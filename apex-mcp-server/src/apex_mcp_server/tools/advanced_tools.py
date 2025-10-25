#!/usr/bin/env python3
"""
Advanced MCP tools for Apex Memory System.

Provides 4 advanced features:
- temporal_search: Point-in-time queries
- get_entity_timeline: Entity evolution tracking
- get_communities: Knowledge cluster discovery
- get_graph_stats: Analytics and metrics
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


@mcp.tool()
async def temporal_search(
    query: str,
    reference_time: Optional[str] = None,
    time_window_days: int = 90,
    limit: int = 10,
) -> Dict[str, Any]:
    """
    Execute temporal queries using Graphiti's bi-temporal tracking.

    Query the knowledge graph as it existed at a specific point in time,
    or search for patterns within a time window.

    Args:
        query: Natural language temporal query
        reference_time: Point in time for query (ISO format: "2025-10-01T00:00:00Z")
                       If None, uses current time
        time_window_days: Time window in days for pattern/history queries (1-365)
        limit: Maximum results to return (1-100)

    Returns:
        {
            "query": str,
            "query_type": str,
            "results": List[Dict],
            "result_count": int,
            "temporal_context": Dict,
            "search_time_ms": float
        }

    Examples:
        >>> # Point-in-time query
        >>> await temporal_search(
        ...     "What was ACME's supplier in January?",
        ...     reference_time="2025-01-31T23:59:59Z"
        ... )

        >>> # Pattern detection
        >>> await temporal_search(
        ...     "How did ACME's relationships evolve?",
        ...     time_window_days=90
        ... )
    """
    payload = {
        "query": query,
        "reference_time": reference_time,
        "time_window_days": time_window_days,
        "limit": limit,
    }

    result = await _call_apex_api("POST", "/api/v1/query/temporal", json_data=payload)

    return {
        "query": result.get("query", query),
        "query_type": result.get("query_type", "temporal"),
        "results": result.get("results", []),
        "result_count": result.get("result_count", 0),
        "temporal_context": result.get("temporal_context", {}),
        "search_time_ms": result.get("search_time_ms", 0.0),
    }


@mcp.tool()
async def get_entity_timeline(
    entity_uuid: str,
    time_window_days: int = 180,
) -> Dict[str, Any]:
    """
    Get complete timeline of events for an entity.

    Shows all state changes, relationship changes, and episodes
    associated with an entity over time.

    Args:
        entity_uuid: UUID of the entity
        time_window_days: How far back to look (1-730 days)

    Returns:
        {
            "entity_uuid": str,
            "entity_name": str,
            "events": List[{
                "timestamp": str,
                "event_type": str,
                "fact": str,
                "source": str,
                "target": str,
                "valid_from": str,
                "valid_to": str
            }],
            "event_count": int,
            "first_seen": str,
            "last_updated": str
        }

    Example:
        >>> await get_entity_timeline("entity-uuid-123", time_window_days=90)
        {
            "entity_uuid": "entity-uuid-123",
            "entity_name": "ACME Corporation",
            "events": [
                {
                    "timestamp": "2025-01-15T10:00:00Z",
                    "event_type": "relationship_created",
                    "fact": "ACME -> ORDERED_FROM -> Bosch",
                    ...
                },
                ...
            ],
            "event_count": 15
        }
    """
    params = {
        "time_window_days": time_window_days,
    }

    result = await _call_apex_api(
        "GET",
        f"/api/v1/query/entity/{entity_uuid}/timeline",
        params=params
    )

    return {
        "entity_uuid": result.get("entity_uuid", entity_uuid),
        "entity_name": result.get("entity_name", ""),
        "events": result.get("events", []),
        "event_count": result.get("event_count", 0),
        "first_seen": result.get("first_seen"),
        "last_updated": result.get("last_updated"),
    }


@mcp.tool()
async def get_communities(
    entity_uuid: Optional[str] = None,
    group_id: str = "default",
    limit: int = 10,
) -> Dict[str, Any]:
    """
    Get knowledge graph communities (clusters of related entities).

    Graphiti automatically detects communities using the Leiden algorithm.
    Communities represent thematic clusters like "Work", "Projects", "People", etc.

    Args:
        entity_uuid: If provided, returns communities this entity belongs to.
                    If None, returns all communities.
        group_id: Group/tenant identifier
        limit: Maximum communities to return (1-100)

    Returns:
        If entity_uuid provided:
        {
            "entity_uuid": str,
            "communities": List[{
                "community_id": str,
                "name": str,
                "member_count": int,
                "summary": str
            }],
            "community_count": int
        }

        If entity_uuid is None:
        {
            "communities": List[{
                "community_id": str,
                "name": str,
                "member_count": int,
                "summary": str
            }],
            "total_communities": int
        }

    Examples:
        >>> # Get all communities
        >>> await get_communities(limit=5)

        >>> # Get communities for specific entity
        >>> await get_communities(entity_uuid="entity-123")
    """
    if entity_uuid:
        # Get communities for specific entity
        params = {"group_id": group_id}
        result = await _call_apex_api(
            "GET",
            f"/api/v1/query/entity/{entity_uuid}/communities",
            params=params
        )

        return {
            "entity_uuid": result.get("entity_uuid", entity_uuid),
            "communities": result.get("communities", []),
            "community_count": result.get("community_count", 0),
        }
    else:
        # Get all communities
        params = {"group_id": group_id, "limit": limit}
        result = await _call_apex_api(
            "GET",
            "/api/v1/analytics/communities",
            params=params
        )

        return {
            "communities": result.get("top_communities", []),
            "total_communities": result.get("community_count", 0),
            "avg_community_size": result.get("avg_community_size", 0.0),
        }


@mcp.tool()
async def get_graph_stats(
    metric_type: str = "overview",
    group_id: str = "default",
    limit: int = 10,
) -> Dict[str, Any]:
    """
    Get knowledge graph statistics and analytics.

    Args:
        metric_type: Type of metrics to retrieve:
                    - "overview": General graph statistics
                    - "entities": Entity-level metrics
                    - "relationships": Relationship metrics
                    - "communities": Community metrics
                    - "health": Graph health score
        group_id: Group/tenant identifier
        limit: For top-N queries (e.g., most connected entities)

    Returns:
        Depends on metric_type:

        "overview":
        {
            "total_entities": int,
            "total_relationships": int,
            "total_communities": int,
            "graph_density": float,
            "avg_relationships_per_entity": float
        }

        "entities":
        {
            "entity_count": int,
            "type_distribution": Dict[str, int],
            "top_entities": List[Dict],
            "orphaned_count": int
        }

        "relationships":
        {
            "relationship_count": int,
            "type_distribution": Dict[str, int],
            "top_relationships": List[Dict]
        }

    Example:
        >>> await get_graph_stats("overview")
        {
            "total_entities": 1247,
            "total_relationships": 3891,
            "total_communities": 23,
            "graph_density": 0.42
        }
    """
    params = {"group_id": group_id, "limit": limit}

    endpoint_map = {
        "overview": "/api/v1/analytics/dashboard",
        "entities": "/api/v1/analytics/entities",
        "relationships": "/api/v1/analytics/relationships",
        "communities": "/api/v1/analytics/communities",
        "health": "/api/v1/analytics/graph-health",
    }

    endpoint = endpoint_map.get(metric_type, "/api/v1/analytics/dashboard")
    result = await _call_apex_api("GET", endpoint, params=params)

    return result
