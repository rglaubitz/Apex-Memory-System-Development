#!/usr/bin/env python3
"""
Basic MCP tools for Apex Memory System.

Provides 5 fundamental memory operations:
- add_memory: Store single memory
- add_conversation: Store multi-turn conversation
- search_memory: Search across knowledge graph
- list_recent_memories: View recent episodes
- clear_memories: Delete user data
"""

import httpx
from typing import Dict, List, Any, Optional

from ..mcp_instance import mcp
from ..config import config


async def _call_apex_api(
    method: str,
    endpoint: str,
    json_data: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Helper to call Apex Memory System API.

    Args:
        method: HTTP method (GET, POST, DELETE)
        endpoint: API endpoint (e.g., "/api/v1/messages/message")
        json_data: JSON body for POST/PUT requests
        params: Query parameters

    Returns:
        API response as dictionary

    Raises:
        httpx.HTTPError: If API request fails
    """
    url = f"{config.apex_api_url}{endpoint}"

    async with httpx.AsyncClient(timeout=config.apex_api_timeout) as client:
        if method == "GET":
            response = await client.get(url, params=params)
        elif method == "POST":
            response = await client.post(url, json=json_data, params=params)
        elif method == "DELETE":
            response = await client.delete(url, params=params)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        response.raise_for_status()
        return response.json()


@mcp.tool()
async def add_memory(
    content: str,
    user_id: str = "default",
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Store a memory in the Apex knowledge graph.

    This triggers:
    - LLM-powered entity extraction (via Graphiti)
    - Automatic relationship inference
    - Storage across 4 databases (Neo4j, PostgreSQL, Qdrant, Redis)
    - Temporal tracking
    - Community detection

    Args:
        content: The memory text to store
        user_id: User identifier (default: "default")
        metadata: Optional additional metadata

    Returns:
        {
            "success": bool,
            "uuid": str,
            "entities_extracted": List[str],
            "edges_created": List[str],
            "message": str
        }

    Example:
        >>> await add_memory("I prefer Python over JavaScript for backend development")
        {
            "success": true,
            "uuid": "msg-123",
            "entities_extracted": ["Python", "JavaScript", "Backend Development"],
            "edges_created": ["User -> PREFERS -> Python"],
            "message": "Memory stored successfully"
        }
    """
    payload = {
        "content": content,
        "sender": user_id,
        "channel": "mcp-claude-desktop",
        "metadata": metadata or {},
    }

    result = await _call_apex_api("POST", "/api/v1/messages/message", json_data=payload)

    return {
        "success": result.get("success", False),
        "uuid": result.get("uuid", ""),
        "entities_extracted": result.get("entities_extracted", []),
        "edges_created": result.get("edges_created", []),
        "message": result.get("message", "Memory stored"),
    }


@mcp.tool()
async def add_conversation(
    messages: List[Dict[str, str]],
    user_id: str = "default",
    participants: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Store a multi-turn conversation in the knowledge graph.

    Processes all messages together to extract entities and relationships
    across the entire conversation context.

    Args:
        messages: List of message dicts with keys: "sender", "content", "timestamp" (optional)
        user_id: User identifier (default: "default")
        participants: Optional list of participant names

    Returns:
        {
            "success": bool,
            "uuid": str,
            "message_count": int,
            "entities_extracted": List[str],
            "edges_created": List[str],
            "message": str
        }

    Example:
        >>> await add_conversation([
        ...     {"sender": "user", "content": "I need help with Invoice INV-001"},
        ...     {"sender": "agent", "content": "I see INV-001 for ACME Corp. How can I help?"}
        ... ])
    """
    payload = {
        "messages": messages,
        "channel": "mcp-claude-desktop",
        "participants": participants,
    }

    result = await _call_apex_api("POST", "/api/v1/messages/conversation", json_data=payload)

    return {
        "success": result.get("success", False),
        "uuid": result.get("uuid", ""),
        "message_count": len(messages),
        "entities_extracted": result.get("entities_extracted", []),
        "edges_created": result.get("edges_created", []),
        "message": result.get("message", "Conversation stored"),
    }


@mcp.tool()
async def search_memory(
    query: str,
    user_id: str = "default",
    limit: int = 10,
    use_cache: bool = True,
) -> Dict[str, Any]:
    """
    Search memories using Apex's intelligent query router.

    The query router automatically:
    - Classifies query intent (semantic, graph, temporal, metadata)
    - Routes to optimal database(s) (Neo4j, PostgreSQL, Qdrant, Redis)
    - Performs hybrid search (semantic + keyword + graph traversal)
    - Aggregates and ranks results
    - Caches for performance

    Args:
        query: Natural language search query
        user_id: User identifier
        limit: Maximum results to return (1-100)
        use_cache: Whether to use semantic caching

    Returns:
        {
            "query": str,
            "intent": str,
            "confidence": float,
            "databases_used": List[str],
            "results": List[Dict],
            "result_count": int,
            "cached": bool
        }

    Example:
        >>> await search_memory("What do I know about ACME Corporation?")
        {
            "query": "What do I know about ACME Corporation?",
            "intent": "graph",
            "confidence": 0.94,
            "databases_used": ["neo4j", "qdrant"],
            "results": [...],
            "result_count": 7,
            "cached": false
        }
    """
    payload = {
        "query": query,
        "limit": limit,
        "use_cache": use_cache,
    }

    result = await _call_apex_api("POST", "/api/v1/query/", json_data=payload)

    return {
        "query": result.get("query", query),
        "intent": result.get("intent", "unknown"),
        "confidence": result.get("confidence", 0.0),
        "routing_method": result.get("routing_method", "unknown"),
        "databases_used": result.get("databases_used", []),
        "results": result.get("results", []),
        "result_count": result.get("result_count", 0),
        "cached": result.get("cached", False),
        "entities_detected": result.get("entities_detected", []),
    }


@mcp.tool()
async def list_recent_memories(
    user_id: str = "default",
    limit: int = 20,
    group_id: str = "default",
) -> Dict[str, Any]:
    """
    List recent memory episodes.

    Shows the most recently added memories with their metadata.

    Args:
        user_id: User identifier
        limit: Maximum episodes to return (1-100)
        group_id: Group/tenant identifier

    Returns:
        {
            "episodes": List[Dict],
            "count": int,
            "user_id": str
        }

    Example:
        >>> await list_recent_memories(limit=5)
        {
            "episodes": [
                {"uuid": "ep-123", "name": "Message msg-456", "created_at": "2025-10-21T..."},
                ...
            ],
            "count": 5
        }
    """
    # Note: This endpoint doesn't exist yet in your API
    # We'll need to add it or use the Graphiti service directly
    # For now, using a search with recent filter

    payload = {
        "query": f"recent memories for {user_id}",
        "limit": limit,
        "use_cache": False,
    }

    result = await _call_apex_api("POST", "/api/v1/query/", json_data=payload)

    return {
        "episodes": result.get("results", []),
        "count": result.get("result_count", 0),
        "user_id": user_id,
    }


@mcp.tool()
async def clear_memories(
    user_id: str,
    confirm: bool = False,
) -> Dict[str, Any]:
    """
    Clear all memories for a user.

    ⚠️  WARNING: This permanently deletes all data for the specified user.

    Args:
        user_id: User identifier to clear
        confirm: Must be True to actually delete (safety check)

    Returns:
        {
            "success": bool,
            "user_id": str,
            "deleted_count": int,
            "message": str
        }

    Example:
        >>> await clear_memories("user-123", confirm=True)
        {
            "success": true,
            "user_id": "user-123",
            "deleted_count": 42,
            "message": "All memories cleared for user-123"
        }
    """
    if not confirm:
        return {
            "success": False,
            "user_id": user_id,
            "deleted_count": 0,
            "message": "Confirmation required. Set confirm=True to delete.",
        }

    # Note: This endpoint needs to be created in your API
    # For now, return a placeholder
    # TODO: Add DELETE /api/v1/maintenance/user-data/{user_id} endpoint

    return {
        "success": False,
        "user_id": user_id,
        "deleted_count": 0,
        "message": "Delete endpoint not yet implemented in Apex API. Please add DELETE /api/v1/maintenance/user-data/{user_id}",
    }
