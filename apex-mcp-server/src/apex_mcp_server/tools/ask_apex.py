#!/usr/bin/env python3
"""
ask_apex() - Intelligent multi-query orchestration and narrative synthesis.

THE KILLER FEATURE of Apex MCP.

This tool uses an LLM to:
1. Understand complex user questions
2. Plan optimal query strategy across Apex's APIs
3. Execute queries in dependency order
4. Synthesize results into narrative answers
5. Suggest relevant follow-ups

Examples:
- "Tell me everything about ACME Corporation"
  → Orchestrates: search → graph → temporal → patterns → communities
  → Synthesizes: Multi-paragraph narrative with insights

- "What changed in my knowledge graph this week?"
  → Orchestrates: temporal search → analytics → pattern detection
  → Synthesizes: Summary of changes + detected patterns

- "How are X and Y connected?"
  → Orchestrates: search both → get relationship path → temporal context
  → Synthesizes: Explanation of connection + evolution over time
"""

import json
import httpx
from typing import Dict, List, Any, Optional
from datetime import datetime
from anthropic import Anthropic

from ..mcp_instance import mcp
from ..config import config

# Initialize Anthropic client
anthropic_client = None

if config.anthropic_api_key:
    anthropic_client = Anthropic(api_key=config.anthropic_api_key)


async def _call_apex_api(
    method: str,
    endpoint: str,
    json_data: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Helper to call Apex Memory System API."""
    url = f"{config.apex_api_url}{endpoint}"

    async with httpx.AsyncClient(timeout=config.apex_api_timeout) as client:
        if method == "GET":
            response = await client.get(url, params=params)
        elif method == "POST":
            response = await client.post(url, json=json_data, params=params)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        response.raise_for_status()
        return response.json()


async def plan_query_strategy(question: str, max_queries: int = 6) -> List[Dict[str, Any]]:
    """
    Use LLM to plan optimal query strategy for a question.

    Args:
        question: User's question
        max_queries: Maximum queries to plan

    Returns:
        List of query steps with dependencies:
        [
            {
                "step": 1,
                "type": "search",
                "endpoint": "/api/v1/query",
                "method": "POST",
                "payload": {"query": "...", "limit": 10},
                "description": "Search for ACME Corporation",
                "extract": "entity_uuid"  # Extract this from response
            },
            {
                "step": 2,
                "type": "graph",
                "endpoint": "/api/v1/graph/document/{uuid}",
                "method": "GET",
                "depends_on": 1,  # Depends on step 1
                "use_extracted": "entity_uuid",  # Use extracted UUID
                "description": "Get ACME's knowledge graph"
            },
            ...
        ]
    """
    if not anthropic_client:
        raise ValueError("Anthropic API key not configured. Cannot use ask_apex().")

    planning_prompt = f"""You are a query planning assistant for the Apex Memory System.

The user asked: "{question}"

Your task: Plan the optimal sequence of API queries to answer this question comprehensively.

Available Apex API endpoints:
1. POST /api/v1/query - General search (semantic routing, hybrid search)
2. POST /api/v1/query/temporal - Temporal queries (point-in-time, patterns)
3. GET /api/v1/query/entity-timeline/{{uuid}} - Entity evolution timeline
4. GET /api/v1/query/entity-communities/{{uuid}} - Entity's communities
5. GET /api/v1/analytics/entities - Entity metrics
6. GET /api/v1/analytics/relationships - Relationship metrics
7. GET /api/v1/analytics/communities - Community metrics
8. GET /api/v1/analytics/dashboard - Overall graph stats
9. POST /api/v1/patterns/aggregation/change-frequency - Pattern detection

Create a query plan (max {max_queries} queries) as a JSON array.

Each query step should have:
- step: int (1, 2, 3, ...)
- type: str (descriptive type like "search", "graph", "temporal", "analytics")
- endpoint: str (the API endpoint)
- method: str ("GET" or "POST")
- payload: dict (for POST requests, the JSON body)
- params: dict (for GET requests, query parameters)
- depends_on: int | null (step number this depends on, or null if independent)
- use_extracted: str | null (field to extract from previous step, e.g., "uuid", "entity_uuid")
- description: str (what this query does)

Example for "Tell me about ACME Corporation":
[
  {{
    "step": 1,
    "type": "search",
    "endpoint": "/api/v1/query",
    "method": "POST",
    "payload": {{"query": "ACME Corporation", "limit": 10}},
    "depends_on": null,
    "use_extracted": null,
    "description": "Search for ACME Corporation to find entity UUID"
  }},
  {{
    "step": 2,
    "type": "temporal_context",
    "endpoint": "/api/v1/query/temporal",
    "method": "POST",
    "payload": {{"query": "ACME Corporation evolution", "time_window_days": 90}},
    "depends_on": null,
    "use_extracted": null,
    "description": "Get temporal evolution of ACME"
  }},
  {{
    "step": 3,
    "type": "analytics",
    "endpoint": "/api/v1/analytics/dashboard",
    "method": "GET",
    "params": {{"group_id": "default"}},
    "depends_on": null,
    "use_extracted": null,
    "description": "Get overall graph context"
  }}
]

Now plan queries for: "{question}"

Return ONLY valid JSON array, no explanation.
"""

    response = anthropic_client.messages.create(
        model=config.anthropic_model,
        max_tokens=2000,
        messages=[{"role": "user", "content": planning_prompt}]
    )

    # Extract JSON from response
    content = response.content[0].text.strip()

    # Remove markdown code blocks if present
    if content.startswith("```json"):
        content = content[7:]
    if content.startswith("```"):
        content = content[3:]
    if content.endswith("```"):
        content = content[:-3]

    strategy = json.loads(content.strip())
    return strategy[:max_queries]  # Enforce max limit


async def execute_query_strategy(strategy: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Execute query strategy steps in dependency order.

    Args:
        strategy: Query plan from plan_query_strategy()

    Returns:
        List of query results with metadata:
        [
            {
                "step": 1,
                "type": "search",
                "description": "...",
                "endpoint": "...",
                "result": {...},
                "extracted": {"entity_uuid": "..."}
            },
            ...
        ]
    """
    results = []
    extracted_data = {}  # Store extracted fields for later steps

    for step_config in strategy:
        step_num = step_config["step"]

        # Check dependencies
        if step_config.get("depends_on"):
            dep_step = step_config["depends_on"]
            # Wait for dependency (in our case, they're already completed since we process sequentially)
            if dep_step not in [r["step"] for r in results]:
                raise ValueError(f"Step {step_num} depends on step {dep_step} which hasn't completed")

            # Use extracted data if needed
            if step_config.get("use_extracted"):
                extract_key = step_config["use_extracted"]
                if extract_key in extracted_data:
                    # Replace placeholder in endpoint
                    endpoint = step_config["endpoint"].replace(
                        f"{{{extract_key}}}",
                        extracted_data[extract_key]
                    )
                    step_config["endpoint"] = endpoint

        # Execute query
        try:
            if step_config["method"] == "POST":
                result = await _call_apex_api(
                    "POST",
                    step_config["endpoint"],
                    json_data=step_config.get("payload", {})
                )
            else:  # GET
                result = await _call_apex_api(
                    "GET",
                    step_config["endpoint"],
                    params=step_config.get("params", {})
                )

            # Extract data for future steps
            if "extract" in step_config:
                extract_key = step_config["extract"]
                if extract_key in result:
                    extracted_data[extract_key] = result[extract_key]

            # Also try common UUID fields
            for uuid_field in ["uuid", "entity_uuid", "document_uuid"]:
                if uuid_field in result:
                    extracted_data[uuid_field] = result[uuid_field]

            # Store result
            results.append({
                "step": step_num,
                "type": step_config["type"],
                "description": step_config.get("description", ""),
                "endpoint": step_config["endpoint"],
                "result": result,
                "extracted": {k: v for k, v in extracted_data.items() if k in step_config.get("extract", [])}
            })

        except Exception as e:
            # Log error but continue with other queries
            results.append({
                "step": step_num,
                "type": step_config["type"],
                "description": step_config.get("description", ""),
                "endpoint": step_config["endpoint"],
                "result": {"error": str(e)},
                "extracted": {}
            })

    return results


async def synthesize_narrative(
    question: str,
    query_results: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Use LLM to synthesize query results into narrative answer.

    Args:
        question: Original user question
        query_results: Results from execute_query_strategy()

    Returns:
        {
            "narrative": str,  # Multi-paragraph answer
            "key_insights": List[str],  # Bullet points
            "entities_mentioned": List[str],  # Entities in answer
            "follow_up_questions": List[str],  # Suggested next questions
            "confidence": float  # 0-1 confidence score
        }
    """
    if not anthropic_client:
        raise ValueError("Anthropic API key not configured")

    # Prepare query results summary
    results_summary = json.dumps(query_results, indent=2, default=str)

    synthesis_prompt = f"""You are a narrative synthesis assistant for the Apex Memory System.

The user asked: "{question}"

I executed {len(query_results)} queries to answer this question. Here are the results:

{results_summary}

Your task: Synthesize these results into a comprehensive, narrative answer.

Guidelines:
1. Write 2-4 paragraphs explaining what you found
2. Be specific - mention entities, relationships, patterns
3. Explain temporal evolution if relevant
4. Highlight important insights with ✨ emoji
5. Use conversational tone
6. If data is limited, acknowledge it honestly

Then provide:
- key_insights: 3-5 bullet points (start with ✨)
- entities_mentioned: List of key entities
- follow_up_questions: 2-3 relevant next questions
- confidence: 0-1 score (how complete is this answer?)

Return as JSON:
{{
  "narrative": "Multi-paragraph answer here...",
  "key_insights": ["✨ Insight 1", "✨ Insight 2", ...],
  "entities_mentioned": ["Entity1", "Entity2", ...],
  "follow_up_questions": ["Question 1?", "Question 2?", ...],
  "confidence": 0.85
}}

Return ONLY valid JSON, no explanation.
"""

    response = anthropic_client.messages.create(
        model=config.anthropic_model,
        max_tokens=config.ask_apex_max_synthesis_tokens,
        messages=[{"role": "user", "content": synthesis_prompt}]
    )

    # Extract JSON
    content = response.content[0].text.strip()
    if content.startswith("```json"):
        content = content[7:]
    if content.startswith("```"):
        content = content[3:]
    if content.endswith("```"):
        content = content[:-3]

    synthesis = json.loads(content.strip())
    return synthesis


@mcp.tool()
async def ask_apex(
    question: str,
    user_id: str = "default",
    include_raw_data: bool = False,
    max_queries: int = 6,
) -> Dict[str, Any]:
    """
    Ask Apex any question - intelligent multi-query orchestration with narrative synthesis.

    🌟 THE KILLER FEATURE 🌟

    Unlike basic memory tools, ask_apex() uses an LLM to:
    1. Understand your complex question
    2. Plan the optimal query strategy (which APIs to call, in what order)
    3. Execute queries across Apex's 4-database architecture
    4. Synthesize results into a narrative answer
    5. Suggest relevant follow-up questions

    This unlocks Apex's full power without requiring you to know the API.

    Args:
        question: Any natural language question about your knowledge graph
        user_id: User identifier
        include_raw_data: Include full query results in response (default: False)
        max_queries: Maximum queries to orchestrate (1-10, default: 6)

    Returns:
        {
            "question": str,
            "answer": str,  # Narrative answer (2-4 paragraphs)
            "key_insights": List[str],  # Bullet points with ✨
            "entities_mentioned": List[str],
            "data_sources_used": List[str],  # Which endpoints were queried
            "query_count": int,
            "follow_up_questions": List[str],  # Suggested next questions
            "confidence": float,  # 0-1 confidence score
            "raw_data": List[Dict] | None  # Full query results (if include_raw_data=True)
        }

    Examples:
        >>> # Comprehensive entity exploration
        >>> result = await ask_apex("Tell me everything about ACME Corporation")
        >>> print(result["answer"])
        "ACME Corporation is a key entity in your knowledge graph with 12 associated
        documents and 8 connected entities tracked over 3 months...

        [Multi-paragraph narrative explaining relationships, patterns, temporal evolution]"

        >>> # Temporal analysis
        >>> result = await ask_apex("What changed in my knowledge graph this week?")
        >>> print(result["key_insights"])
        [
            "✨ 5 new entities added (3 organizations, 2 people)",
            "✨ ACME Corporation changed suppliers (Bosch → Brembo)",
            "✨ 2 new communities detected (Projects, Suppliers)"
        ]

        >>> # Relationship exploration
        >>> result = await ask_apex("How are ACME and Bosch connected?")
        >>> print(result["follow_up_questions"])
        [
            "Why did ACME switch from Bosch to Brembo?",
            "What other customers use Bosch?",
            "Show me ACME's complete supplier history"
        ]
    """
    if not anthropic_client:
        return {
            "question": question,
            "answer": "❌ ask_apex() requires Anthropic API key. Please configure ANTHROPIC_API_KEY in your environment.",
            "key_insights": [],
            "entities_mentioned": [],
            "data_sources_used": [],
            "query_count": 0,
            "follow_up_questions": [],
            "confidence": 0.0,
            "raw_data": None
        }

    try:
        # Stage 1: Plan query strategy
        strategy = await plan_query_strategy(question, max_queries=max_queries)

        # Stage 2: Execute queries
        query_results = await execute_query_strategy(strategy)

        # Stage 3: Synthesize narrative
        synthesis = await synthesize_narrative(question, query_results)

        # Build response
        return {
            "question": question,
            "answer": synthesis.get("narrative", ""),
            "key_insights": synthesis.get("key_insights", []),
            "entities_mentioned": synthesis.get("entities_mentioned", []),
            "data_sources_used": [r["endpoint"] for r in query_results],
            "query_count": len(query_results),
            "follow_up_questions": synthesis.get("follow_up_questions", []),
            "confidence": synthesis.get("confidence", 0.0),
            "raw_data": query_results if include_raw_data else None,
        }

    except Exception as e:
        return {
            "question": question,
            "answer": f"❌ Error orchestrating query: {str(e)}",
            "key_insights": [],
            "entities_mentioned": [],
            "data_sources_used": [],
            "query_count": 0,
            "follow_up_questions": [],
            "confidence": 0.0,
            "raw_data": None
        }
