#!/usr/bin/env python3
"""
Apex MCP Server - Main server entry point.

Starts the Model Context Protocol server with all Apex Memory tools.
"""

import asyncio
import logging
from mcp.server.stdio import stdio_server

# Import shared mcp instance
from .mcp_instance import mcp

# Import all tools to register them (importing registers decorators)
from .tools import (
    # Basic tools
    add_memory,
    add_conversation,
    search_memory,
    list_recent_memories,
    clear_memories,
    # Advanced tools
    temporal_search,
    get_entity_timeline,
    get_communities,
    get_graph_stats,
    # Intelligence
    ask_apex,
)

from .config import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Add resources
@mcp.resource("apex://knowledge-graph-snapshot")
async def get_knowledge_graph_snapshot() -> str:
    """
    Get a snapshot of the current knowledge graph state.

    Returns JSON with:
    - Entity count
    - Relationship count
    - Community count
    - Top entities
    - Recent changes
    """
    import httpx
    import json

    try:
        async with httpx.AsyncClient(timeout=config.apex_api_timeout) as client:
            response = await client.get(
                f"{config.apex_api_url}/api/v1/analytics/dashboard",
                params={"group_id": config.default_group_id}
            )
            response.raise_for_status()
            data = response.json()

            # Format as readable text
            snapshot = f"""# Knowledge Graph Snapshot
Generated: {data.get('timestamp', 'unknown')}

## Overview
- Total Entities: {data.get('total_entities', 0)}
- Total Relationships: {data.get('total_relationships', 0)}
- Total Communities: {data.get('total_communities', 0)}
- Graph Density: {data.get('graph_density', 0.0):.2f}

## Entity Distribution
{json.dumps(data.get('entity_type_distribution', {}), indent=2)}

## Relationship Distribution
{json.dumps(data.get('relationship_type_distribution', {}), indent=2)}

## Health Metrics
- Orphaned Entities: {data.get('orphaned_entities', 0)}
- Average Relationships per Entity: {data.get('avg_relationships_per_entity', 0.0):.1f}
"""
            return snapshot

    except Exception as e:
        return f"# Knowledge Graph Snapshot\n\nError: {str(e)}"


@mcp.resource("apex://recent-patterns")
async def get_recent_patterns() -> str:
    """
    Get recently detected patterns in the knowledge graph.

    Returns text summary of:
    - Trending entities
    - Emerging relationships
    - Community changes
    """
    import httpx

    try:
        async with httpx.AsyncClient(timeout=config.apex_api_timeout) as client:
            # Get recent analytics
            response = await client.get(
                f"{config.apex_api_url}/api/v1/analytics/entities",
                params={"group_id": config.default_group_id, "limit": 10}
            )
            response.raise_for_status()
            data = response.json()

            patterns = f"""# Recent Patterns
Detected in knowledge graph

## Top Connected Entities
{chr(10).join([f"- {entity.get('name', 'Unknown')} ({entity.get('degree', 0)} connections)" for entity in data.get('top_entities', [])[:5]])}

## Entity Activity
- New Entities (last 7 days): Check temporal queries
- Modified Entities: Check entity timelines
- New Relationships: Check relationship analytics

Use `ask_apex("What changed recently?")` for detailed analysis.
"""
            return patterns

    except Exception as e:
        return f"# Recent Patterns\n\nError: {str(e)}"


# Add prompts
@mcp.prompt()
async def summarize_conversations(timeframe: str = "24h") -> str:
    """
    Generate prompt for conversation summarization.

    Args:
        timeframe: Time window (e.g., "24h", "7d", "30d")

    Returns:
        Prompt template for Claude
    """
    return f"""Based on the Apex Memory knowledge graph, summarize key conversations from the last {timeframe}.

Focus on:
- **Key Decisions Made**: Important choices and their rationale
- **Action Items Identified**: Tasks, follow-ups, commitments
- **Important Entities Mentioned**: People, organizations, projects
- **Relationship Changes**: New or modified connections

Use ask_apex() to gather the data, then provide a concise executive summary.
"""


@mcp.prompt()
async def extract_key_facts(topic: str) -> str:
    """
    Generate prompt for fact extraction about a topic.

    Args:
        topic: Topic to extract facts about

    Returns:
        Prompt template for Claude
    """
    return f"""Analyze the Apex Memory knowledge graph and extract key facts about: {topic}

Include:
- **Core Entities** related to the topic
- **Relationships** between entities
- **Temporal Evolution** - how facts changed over time
- **Confidence Levels** based on:
  - Number of sources mentioning the fact
  - Consistency across episodes
  - Recency of information

Use ask_apex("{topic}") to gather comprehensive data, then structure your findings.
"""


def main():
    """Main entry point for the MCP server."""
    logger.info("Starting Apex MCP Server...")
    logger.info(f"Apex API URL: {config.apex_api_url}")
    logger.info(f"Anthropic model: {config.anthropic_model}")

    # Register all tools (already registered via decorators)
    logger.info("Tools registered:")
    logger.info("  - Basic: add_memory, add_conversation, search_memory, list_recent_memories, clear_memories")
    logger.info("  - Advanced: temporal_search, get_entity_timeline, get_communities, get_graph_stats")
    logger.info("  - Intelligence: ask_apex")

    logger.info("Resources registered:")
    logger.info("  - apex://knowledge-graph-snapshot")
    logger.info("  - apex://recent-patterns")

    logger.info("Prompts registered:")
    logger.info("  - summarize_conversations")
    logger.info("  - extract_key_facts")

    # Run the server with stdio transport
    mcp.run("stdio")


if __name__ == "__main__":
    main()
