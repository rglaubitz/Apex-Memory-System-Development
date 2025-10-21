#!/usr/bin/env python3
"""
Tests for basic MCP tools.

Tests the 5 basic memory operations:
- add_memory
- add_conversation
- search_memory
- list_recent_memories
- clear_memories
"""

import pytest
from unittest.mock import patch, AsyncMock


@pytest.mark.asyncio
async def test_add_memory_success():
    """Test adding a memory successfully."""
    from apex_mcp_server.tools.basic_tools import add_memory

    # Mock the API call
    mock_response = {
        "success": True,
        "uuid": "msg-123",
        "entities_extracted": ["Python", "JavaScript"],
        "edges_created": ["User -> PREFERS -> Python"],
        "message": "Memory stored"
    }

    with patch('apex_mcp_server.tools.basic_tools._call_apex_api', new=AsyncMock(return_value=mock_response)):
        result = await add_memory("I prefer Python over JavaScript")

        assert result["success"] is True
        assert result["uuid"] == "msg-123"
        assert "Python" in result["entities_extracted"]
        assert len(result["edges_created"]) > 0


@pytest.mark.asyncio
async def test_add_conversation_success():
    """Test adding a conversation successfully."""
    from apex_mcp_server.tools.basic_tools import add_conversation

    mock_response = {
        "success": True,
        "uuid": "conv-456",
        "entities_extracted": ["Invoice", "ACME Corp"],
        "edges_created": ["Invoice -> BELONGS_TO -> ACME Corp"],
        "message": "Conversation stored"
    }

    messages = [
        {"sender": "user", "content": "I need help with Invoice INV-001"},
        {"sender": "agent", "content": "I see INV-001 for ACME Corp"}
    ]

    with patch('apex_mcp_server.tools.basic_tools._call_apex_api', new=AsyncMock(return_value=mock_response)):
        result = await add_conversation(messages)

        assert result["success"] is True
        assert result["message_count"] == 2
        assert "ACME Corp" in result["entities_extracted"]


@pytest.mark.asyncio
async def test_search_memory_success():
    """Test searching memories successfully."""
    from apex_mcp_server.tools.basic_tools import search_memory

    mock_response = {
        "query": "ACME Corporation",
        "intent": "graph",
        "confidence": 0.94,
        "databases_used": ["neo4j", "qdrant"],
        "results": [{"uuid": "doc-1", "title": "ACME Order"}],
        "result_count": 1,
        "cached": False
    }

    with patch('apex_mcp_server.tools.basic_tools._call_apex_api', new=AsyncMock(return_value=mock_response)):
        result = await search_memory("ACME Corporation")

        assert result["query"] == "ACME Corporation"
        assert result["intent"] == "graph"
        assert result["confidence"] > 0.9
        assert "neo4j" in result["databases_used"]


@pytest.mark.asyncio
async def test_list_recent_memories_success():
    """Test listing recent memories."""
    from apex_mcp_server.tools.basic_tools import list_recent_memories

    mock_response = {
        "results": [
            {"uuid": "ep-1", "name": "Message 1"},
            {"uuid": "ep-2", "name": "Message 2"}
        ],
        "result_count": 2
    }

    with patch('apex_mcp_server.tools.basic_tools._call_apex_api', new=AsyncMock(return_value=mock_response)):
        result = await list_recent_memories(limit=5)

        assert result["count"] == 2
        assert len(result["episodes"]) == 2


@pytest.mark.asyncio
async def test_clear_memories_requires_confirmation():
    """Test clear memories requires confirmation."""
    from apex_mcp_server.tools.basic_tools import clear_memories

    result = await clear_memories("user-123", confirm=False)

    assert result["success"] is False
    assert "confirm" in result["message"].lower()


@pytest.mark.asyncio
async def test_add_memory_with_metadata():
    """Test adding memory with custom metadata."""
    from apex_mcp_server.tools.basic_tools import add_memory

    mock_response = {
        "success": True,
        "uuid": "msg-789",
        "entities_extracted": ["React", "Frontend"],
        "edges_created": [],
        "message": "Memory stored"
    }

    metadata = {"category": "preferences", "priority": "high"}

    with patch('apex_mcp_server.tools.basic_tools._call_apex_api', new=AsyncMock(return_value=mock_response)):
        result = await add_memory("I use React for frontend", metadata=metadata)

        assert result["success"] is True
        assert result["uuid"] == "msg-789"
