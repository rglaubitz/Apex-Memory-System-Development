#!/usr/bin/env python3
"""
Tests for advanced MCP tools.

Tests the 4 advanced features:
- temporal_search
- get_entity_timeline
- get_communities
- get_graph_stats
"""

import pytest
from unittest.mock import patch, AsyncMock


@pytest.mark.asyncio
async def test_temporal_search_point_in_time():
    """Test temporal search at specific point in time."""
    from apex_mcp_server.tools.advanced_tools import temporal_search

    mock_response = {
        "query": "What was ACME's supplier in January?",
        "query_type": "temporal",
        "results": [{"supplier": "Bosch", "valid_from": "2024-12-01"}],
        "result_count": 1,
        "temporal_context": {"reference_time": "2025-01-31T23:59:59Z"},
        "search_time_ms": 45.2
    }

    with patch('apex_mcp_server.tools.advanced_tools._call_apex_api', new=AsyncMock(return_value=mock_response)):
        result = await temporal_search(
            "What was ACME's supplier in January?",
            reference_time="2025-01-31T23:59:59Z"
        )

        assert result["query_type"] == "temporal"
        assert result["result_count"] == 1
        assert result["search_time_ms"] > 0


@pytest.mark.asyncio
async def test_get_entity_timeline():
    """Test getting entity timeline."""
    from apex_mcp_server.tools.advanced_tools import get_entity_timeline

    mock_response = {
        "entity_uuid": "entity-123",
        "entity_name": "ACME Corporation",
        "events": [
            {
                "timestamp": "2025-01-15T10:00:00Z",
                "event_type": "relationship_created",
                "fact": "ACME -> ORDERED_FROM -> Bosch"
            },
            {
                "timestamp": "2025-03-01T14:00:00Z",
                "event_type": "relationship_created",
                "fact": "ACME -> ORDERED_FROM -> Brembo"
            }
        ],
        "event_count": 2,
        "first_seen": "2024-12-01T00:00:00Z",
        "last_updated": "2025-03-01T14:00:00Z"
    }

    with patch('apex_mcp_server.tools.advanced_tools._call_apex_api', new=AsyncMock(return_value=mock_response)):
        result = await get_entity_timeline("entity-123")

        assert result["entity_uuid"] == "entity-123"
        assert result["entity_name"] == "ACME Corporation"
        assert result["event_count"] == 2
        assert len(result["events"]) == 2


@pytest.mark.asyncio
async def test_get_communities_all():
    """Test getting all communities."""
    from apex_mcp_server.tools.advanced_tools import get_communities

    mock_response = {
        "largest_communities": [
            {"community_id": "comm-1", "name": "Work", "member_count": 48},
            {"community_id": "comm-2", "name": "Projects", "member_count": 35}
        ],
        "community_count": 2,
        "avg_community_size": 41.5
    }

    with patch('apex_mcp_server.tools.advanced_tools._call_apex_api', new=AsyncMock(return_value=mock_response)):
        result = await get_communities(limit=5)

        assert result["total_communities"] == 2
        assert len(result["communities"]) == 2
        assert result["communities"][0]["name"] == "Work"


@pytest.mark.asyncio
async def test_get_communities_for_entity():
    """Test getting communities for specific entity."""
    from apex_mcp_server.tools.advanced_tools import get_communities

    mock_response = {
        "entity_uuid": "entity-456",
        "communities": [
            {"community_id": "comm-1", "name": "Work", "member_count": 48}
        ],
        "community_count": 1
    }

    with patch('apex_mcp_server.tools.advanced_tools._call_apex_api', new=AsyncMock(return_value=mock_response)):
        result = await get_communities(entity_uuid="entity-456")

        assert result["entity_uuid"] == "entity-456"
        assert result["community_count"] == 1


@pytest.mark.asyncio
async def test_get_graph_stats_overview():
    """Test getting graph overview statistics."""
    from apex_mcp_server.tools.advanced_tools import get_graph_stats

    mock_response = {
        "total_entities": 1247,
        "total_relationships": 3891,
        "total_communities": 23,
        "graph_density": 0.42,
        "avg_relationships_per_entity": 3.1
    }

    with patch('apex_mcp_server.tools.advanced_tools._call_apex_api', new=AsyncMock(return_value=mock_response)):
        result = await get_graph_stats("overview")

        assert result["total_entities"] == 1247
        assert result["total_relationships"] == 3891
        assert result["graph_density"] == 0.42


@pytest.mark.asyncio
async def test_get_graph_stats_entities():
    """Test getting entity-level statistics."""
    from apex_mcp_server.tools.advanced_tools import get_graph_stats

    mock_response = {
        "entity_count": 1247,
        "type_distribution": {
            "Person": 450,
            "Organization": 320,
            "Document": 477
        },
        "top_entities": [
            {"name": "ACME Corp", "degree": 45}
        ],
        "orphaned_count": 5
    }

    with patch('apex_mcp_server.tools.advanced_tools._call_apex_api', new=AsyncMock(return_value=mock_response)):
        result = await get_graph_stats("entities")

        assert result["entity_count"] == 1247
        assert "Organization" in result["type_distribution"]
        assert result["orphaned_count"] == 5
