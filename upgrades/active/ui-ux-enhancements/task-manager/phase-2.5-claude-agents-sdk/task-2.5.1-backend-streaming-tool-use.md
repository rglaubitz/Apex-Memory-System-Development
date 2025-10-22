# Task 2.5.1: Backend Streaming with Tool Use

**Phase:** 2.5 - Claude Agents SDK Integration
**Status:** ⬜ Not Started
**Estimated Duration:** 8 hours (Days 1-2)
**Assigned To:** (filled during execution)

---

## Overview

Implement backend streaming chat endpoint with Claude tool use integration, 5 Apex-specific tools, and ToolExecutor class for executing tool calls.

---

## Dependencies

**Required Before Starting:**
- Task 2.2: LLM Integration and Conversation Service (requires ConversationService)
- Task 2.3: Conversation API Endpoints (requires API structure)

**Enables After Completion:**
- Task 2.5.2: Frontend Streaming Hook

---

## Success Criteria

✅ Vercel AI SDK (Anthropic package) installed
✅ 5 Apex tools defined with proper schemas
✅ ToolExecutor class functional with all 5 tools
✅ Streaming endpoint returns Server-Sent Events (SSE)
✅ Tool execution integrated into streaming flow
✅ Chat router registered in main app

---

## Research References

**Technical Documentation:**
- research/documentation/tool-use-api.md (Lines: 1-200)
  - Key concepts: Tool schemas, tool_use blocks, tool_result pattern

- research/documentation/streaming-api.md (Lines: 1-150)
  - Key concepts: SSE format, content_block_delta events

**Implementation Guide:**
- IMPLEMENTATION.md (Lines: 2367-2617)
  - Complete backend streaming implementation
  - Tool definitions and ToolExecutor

---

## Test Specifications

**Backend Unit Tests:** (10 tests)
- TESTING.md: Lines 1332-1411
- File: `tests/unit/test_tools.py`

**Tests to pass:**
1. Execute search_knowledge_graph tool
2. Execute get_entity_relationships tool
3. Execute get_temporal_timeline tool
4. Execute find_similar_documents tool
5. Execute get_graph_statistics tool
6. Unknown tool returns error
7. Tool input validation
8. Async tool execution
9. Tool result formatting
10. Tool error handling

**Total Tests:** 10

---

## Implementation Steps

### Subtask 2.5.1.1: Install Vercel AI SDK

**Duration:** 0.5 hours
**Status:** ⬜ Not Started

**Files to Modify:**
- `apex-memory-system/requirements.txt`
- `apex-memory-system/src/apex_memory/config.py` (verify ANTHROPIC_API_KEY)

**Steps:**
1. Install anthropic SDK (already installed from Phase 2)
2. Verify Anthropic client initialization
3. Test async client creation

**Code Example:**
```bash
# Verify installation
cd apex-memory-system
pip list | grep anthropic

# Test import
python -c "from anthropic import AsyncAnthropic; print('✓ AsyncAnthropic available')"
```

**Validation:**
```bash
# Verify API key loaded
python -c "
from apex_memory.config import settings
assert settings.ANTHROPIC_API_KEY, 'ANTHROPIC_API_KEY missing'
print('✓ API key configured')
"
```

**Expected Result:**
- Anthropic SDK available
- AsyncAnthropic client can be instantiated
- API key configured in settings

---

### Subtask 2.5.1.2: Define 5 Apex Tools

**Duration:** 2 hours
**Status:** ⬜ Not Started

**Files to Create:**
- `apex-memory-system/src/apex_memory/api/chat_stream.py` (tool definitions)

**Steps:**
1. Create chat_stream.py module
2. Define APEX_TOOLS list with 5 tool schemas
3. Each tool has: name, description, input_schema (JSON Schema)
4. Tools:
   - search_knowledge_graph (query, limit)
   - get_entity_relationships (entity_name, max_depth)
   - get_temporal_timeline (entity_name, start_date, end_date)
   - find_similar_documents (document_uuid, limit)
   - get_graph_statistics (include_metrics)
5. Add comprehensive descriptions for Claude to understand tool usage

**Code Example:**
```python
# See IMPLEMENTATION.md lines 2403-2498 for complete code
APEX_TOOLS = [
    {
        "name": "search_knowledge_graph",
        "description": "Search across all databases (Neo4j, Qdrant, PostgreSQL) for relevant information",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The search query"},
                "limit": {"type": "integer", "description": "Maximum number of results", "default": 5}
            },
            "required": ["query"]
        }
    },
    # ... 4 more tools
]
```

**Validation:**
```bash
# Validate tool schemas
python -c "
from apex_memory.api.chat_stream import APEX_TOOLS
assert len(APEX_TOOLS) == 5, 'Expected 5 tools'
for tool in APEX_TOOLS:
    assert 'name' in tool
    assert 'description' in tool
    assert 'input_schema' in tool
print('✓ All 5 tools defined with valid schemas')
"
```

**Expected Result:**
- 5 tools defined with complete JSON schemas
- Tool descriptions clear and actionable
- Input schemas include types, descriptions, required fields

---

### Subtask 2.5.1.3: Implement ToolExecutor Class

**Duration:** 2.5 hours
**Status:** ⬜ Not Started

**Files to Modify:**
- `apex-memory-system/src/apex_memory/api/chat_stream.py` (add ToolExecutor)

**Steps:**
1. Create ToolExecutor class with __init__
2. Initialize QueryRouter and GraphService instances
3. Implement execute_tool async method with tool_name and tool_input
4. Add handlers for each of the 5 tools
5. Call appropriate service methods (query_router.route_query, graph_service.get_entity_relationships, etc.)
6. Return structured results as dicts
7. Handle unknown tools with error response
8. Add error handling for service failures

**Code Example:**
```python
# See IMPLEMENTATION.md lines 2501-2547 for complete code
class ToolExecutor:
    """Executes Apex tool calls."""

    def __init__(self):
        self.query_router = QueryRouter()
        self.graph_service = GraphService()

    async def execute_tool(self, tool_name: str, tool_input: dict) -> dict:
        """Execute a tool and return results."""
        if tool_name == "search_knowledge_graph":
            results = await self.query_router.route_query(
                tool_input["query"],
                limit=tool_input.get("limit", 5)
            )
            return {"results": results}
        # ... handle other 4 tools
        else:
            return {"error": f"Unknown tool: {tool_name}"}
```

**Validation:**
```bash
# Test ToolExecutor
python -c "
import asyncio
from apex_memory.api.chat_stream import ToolExecutor

async def test():
    executor = ToolExecutor()
    # Test unknown tool
    result = await executor.execute_tool('unknown_tool', {})
    assert 'error' in result
    print('✓ ToolExecutor handles unknown tools')

asyncio.run(test())
"
```

**Expected Result:**
- ToolExecutor class instantiates successfully
- Each tool handler calls correct service method
- Unknown tools return error dict
- Results formatted consistently

---

### Subtask 2.5.1.4: Create Streaming Endpoint

**Duration:** 3 hours
**Status:** ⬜ Not Started

**Files to Modify:**
- `apex-memory-system/src/apex_memory/api/chat_stream.py` (add stream_chat_response, router)
- `apex-memory-system/src/apex_memory/main.py` (register router)

**Steps:**
1. Create ChatRequest Pydantic model (messages, conversation_uuid)
2. Implement stream_chat_response async generator
3. Call anthropic.messages.create with tools=APEX_TOOLS, stream=True
4. Handle streaming events:
   - content_block_start (tool_use type) → yield tool_start event
   - content_block_delta (text) → yield text event
   - content_block_stop (tool_use) → execute tool, yield tool_result event
   - message_stop → yield done event
5. Yield Server-Sent Events format: `data: {json}\n\n`
6. Create POST /api/v1/chat/stream endpoint
7. Return StreamingResponse with media_type="text/event-stream"
8. Register router in main.py

**Code Example:**
```python
# See IMPLEMENTATION.md lines 2549-2615 for complete code
async def stream_chat_response(
    messages: list[dict],
    user: User,
) -> AsyncGenerator[str, None]:
    """Stream chat response with tool use."""
    anthropic = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
    tool_executor = ToolExecutor()

    response = await anthropic.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=4096,
        tools=APEX_TOOLS,
        messages=messages,
        stream=True,
    )

    async for event in response:
        if event.type == "content_block_start":
            if event.content_block.type == "tool_use":
                yield f'data: {{"type": "tool_start", "tool_name": "{event.content_block.name}"}}\n\n'
        # ... handle other event types
```

**Validation:**
```bash
# Start server
python -m uvicorn apex_memory.main:app --reload --port 8000 &

# Test streaming endpoint
TOKEN="your-test-token"
CONV_UUID="test-conversation-uuid"

curl -X POST http://localhost:8000/api/v1/chat/stream \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Search for ACME"}],
    "conversation_uuid": "'$CONV_UUID'"
  }'

# Should see SSE stream with tool events
```

**Expected Result:**
- Streaming endpoint returns SSE format
- Tool use events appear in stream (tool_start, tool_execute, tool_result)
- Text content streams progressively
- Stream ends with "done" event
- Router registered in main app

---

## Troubleshooting

**Common Issues:**

**Issue 1: Streaming response not formatted correctly**
- See TROUBLESHOOTING.md:Lines 800-825
- Solution: Ensure `data: {json}\n\n` format (data prefix, double newline), use text/event-stream media type

**Issue 2: Tool execution errors**
- See TROUBLESHOOTING.md:Lines 850-875
- Solution: Check GraphService and QueryRouter are initialized, mock services in tests

**Issue 3: AsyncAnthropic streaming API changes**
- See TROUBLESHOOTING.md:Lines 900-925
- Solution: Check Anthropic SDK version (>=0.18.0), review streaming API documentation

---

## Progress Tracking

**Subtasks:** 0/4 complete (0%)

- [ ] Subtask 2.5.1.1: Install Vercel AI SDK
- [ ] Subtask 2.5.1.2: Define 5 Apex Tools
- [ ] Subtask 2.5.1.3: Implement ToolExecutor Class
- [ ] Subtask 2.5.1.4: Create Streaming Endpoint

**Tests:** 0/10 passing (0%)

**Last Updated:** 2025-10-21
