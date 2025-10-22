# Task 2.5.5: Testing and Documentation

**Phase:** 2.5 - Claude Agents SDK Integration
**Status:** ⬜ Not Started
**Estimated Duration:** 3 hours (End of Week 3)
**Assigned To:** (filled during execution)

---

## Overview

Write comprehensive test suite (25 tests total), fix any bugs discovered during testing, and document the streaming/tool use architecture.

---

## Dependencies

**Required Before Starting:**
- Task 2.5.1: Backend Streaming with Tool Use
- Task 2.5.2: Frontend Streaming Hook
- Task 2.5.3: Artifacts Sidebar Component
- Task 2.5.4: ConversationHub Streaming Integration

**Enables After Completion:**
- Phase 3: Apple Minimalist Engagement Layer

---

## Success Criteria

✅ All 10 backend unit tests passing
✅ All 15 integration tests passing
✅ All 10 frontend tests passing (5 hook + 5 component)
✅ Total: 25/25 tests passing (100%)
✅ Bug fixes applied from testing
✅ Architecture documented

---

## Research References

**Technical Documentation:**
- research/documentation/testing-best-practices.md (Lines: 1-150)
  - Key concepts: Mocking AsyncAnthropic, testing streaming, tool execution mocks

**Implementation Guide:**
- TESTING.md (Lines: 1326-1534)
  - Complete test specifications for Phase 2.5

---

## Test Specifications

**Total Tests:** 25
- Backend Unit: 10 tests (`test_tools.py`)
- Integration: 15 tests (`test_streaming_flow.py`)
- Frontend: 10 tests (5 hook + 5 component)

**Coverage Targets:**
- Backend: 85%+ for chat_stream.py
- Frontend: 80%+ for useApexChat and ArtifactSidebar

---

## Implementation Steps

### Subtask 2.5.5.1: Backend Unit Tests

**Duration:** 1 hour
**Status:** ⬜ Not Started

**Files to Create:**
- `apex-memory-system/tests/unit/test_tools.py`

**Steps:**
1. Create test file with fixtures
2. Write TestToolExecutor class with 10 test methods
3. Mock QueryRouter and GraphService
4. Test each of 5 tools with AsyncMock
5. Test unknown tool error handling
6. Test tool input validation
7. Test async tool execution
8. Test tool result formatting
9. Test tool error handling
10. Run tests and verify 100% pass rate

**Code Example:**
```python
# See TESTING.md lines 1334-1411 for complete code
import pytest
from unittest.mock import AsyncMock, Mock

from apex_memory.api.chat_stream import ToolExecutor


class TestToolExecutor:
    """Test tool execution logic."""

    @pytest.mark.asyncio
    async def test_execute_search_knowledge_graph(self):
        """Test search_knowledge_graph tool execution."""
        executor = ToolExecutor()

        # Mock query router
        executor.query_router.route_query = AsyncMock(return_value=[
            {"title": "Doc 1", "content": "Content 1", "score": 0.95}
        ])

        result = await executor.execute_tool(
            "search_knowledge_graph",
            {"query": "test query", "limit": 5}
        )

        assert "results" in result
        assert len(result["results"]) > 0

    # ... 9 more tests
```

**Validation:**
```bash
# Run backend unit tests
pytest tests/unit/test_tools.py -v --cov=apex_memory.api.chat_stream

# Expected: 10/10 tests passing, 85%+ coverage
```

**Expected Result:**
- 10/10 backend unit tests passing
- 85%+ code coverage on ToolExecutor
- All 5 tools tested
- Error handling validated

---

### Subtask 2.5.5.2: Integration Tests

**Duration:** 1 hour
**Status:** ⬜ Not Started

**Files to Create:**
- `apex-memory-system/tests/integration/test_streaming_flow.py`

**Steps:**
1. Create test file with authenticated_headers fixture
2. Write TestStreamingEndpoint class
3. Test basic streaming chat
4. Test streaming with tool use (requires mocking AsyncAnthropic)
5. Test tool result events in stream
6. Test multiple tool executions
7. Test error handling in streaming
8. Test conversation context maintained during streaming
9. Write 15 tests total covering end-to-end flow
10. Run tests and verify 100% pass rate

**Code Example:**
```python
# See TESTING.md lines 1413-1489 for complete code
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock

from apex_memory.main import app

client = TestClient(app)


class TestStreamingEndpoint:
    """Test streaming chat endpoint."""

    def test_stream_chat_basic(self, authenticated_headers):
        """Test basic streaming chat."""
        # Create conversation first
        conv_response = client.post(
            "/api/v1/conversations/",
            json={"title": "Stream Test"},
            headers=authenticated_headers
        )
        conv_uuid = conv_response.json()["uuid"]

        # Mock streaming
        with patch('apex_memory.api.chat_stream.stream_chat_response') as mock_stream:
            async def mock_generator():
                yield 'data: {"type": "text", "text": "Hello"}\n\n'
                yield 'data: {"type": "done"}\n\n'

            mock_stream.return_value = mock_generator()

            # Stream chat
            response = client.post(
                "/api/v1/chat/stream",
                json={
                    "messages": [{"role": "user", "content": "Hello"}],
                    "conversation_uuid": str(conv_uuid)
                },
                headers=authenticated_headers
            )

            assert response.status_code == 200

    # ... 14 more tests
```

**Validation:**
```bash
# Run integration tests
pytest tests/integration/test_streaming_flow.py -v -m integration

# Expected: 15/15 tests passing
```

**Expected Result:**
- 15/15 integration tests passing
- Streaming flow validated end-to-end
- Tool execution verified
- Error cases covered

---

### Subtask 2.5.5.3: Frontend Tests

**Duration:** 0.5 hours
**Status:** ⬜ Not Started

**Files to Create:**
- `apex-memory-system/frontend/src/__tests__/hooks/useApexChat.test.ts` (5 tests)
- `apex-memory-system/frontend/src/__tests__/components/ArtifactSidebar.test.tsx` (5 tests)

**Steps:**
1. Create useApexChat test file
2. Mock 'ai/react' useChat hook
3. Test hook initialization
4. Test tool execution tracking
5. Test onFinish callback
6. Create ArtifactSidebar test file
7. Test sidebar rendering
8. Test each visualization component (SearchResultsView, RelationshipsView, TimelineView, SimilarDocsView, StatisticsView)
9. Run frontend tests
10. Verify 10/10 passing

**Code Example:**
```typescript
// See TESTING.md lines 1491-1534 for complete code
import { renderHook, act, waitFor } from '@testing-library/react';
import { useApexChat } from '../../hooks/useApexChat';

// Mock ai/react
jest.mock('ai/react', () => ({
  useChat: jest.fn(() => ({
    messages: [],
    input: '',
    handleInputChange: jest.fn(),
    handleSubmit: jest.fn(),
    isLoading: false,
  })),
}));

describe('useApexChat Hook', () => {
  test('initializes with empty messages', () => {
    const { result } = renderHook(() => useApexChat('conv-123'));

    expect(result.current.messages).toEqual([]);
    expect(result.current.toolExecutions).toEqual([]);
  });

  // ... 4 more tests
});
```

**Validation:**
```bash
# Run frontend tests
cd frontend
npm test -- --coverage

# Expected: 10/10 tests passing, 80%+ coverage
```

**Expected Result:**
- 5/5 hook tests passing
- 5/5 component tests passing
- 80%+ frontend coverage
- Tool execution tracking validated

---

### Subtask 2.5.5.4: Bug Fixes and Documentation

**Duration:** 0.5 hours
**Status:** ⬜ Not Started

**Files to Create:**
- `apex-memory-system/docs/streaming-architecture.md` (architecture documentation)

**Steps:**
1. Run all tests and identify any failures
2. Fix bugs discovered during testing
3. Re-run tests to verify fixes
4. Document streaming architecture
5. Document tool use pattern
6. Document artifact visualization
7. Add inline code comments for complex sections
8. Update API documentation with streaming endpoint

**Code Example:**
```markdown
# Streaming Architecture

## Overview

The streaming chat system uses Server-Sent Events (SSE) to provide real-time responses with tool use visualization.

## Components

1. **Backend Streaming Endpoint** (`chat_stream.py`)
   - AsyncAnthropic client with tool use
   - ToolExecutor for executing 5 Apex tools
   - SSE streaming generator

2. **Frontend Hook** (`useApexChat.ts`)
   - Vercel AI SDK useChat hook
   - Tool execution tracking
   - EventSource handling

3. **Artifacts Sidebar** (`ArtifactSidebar.tsx`)
   - 5 visualization components
   - Sheet animation pattern

## Flow

1. User sends message
2. Backend streams response with tool_use blocks
3. ToolExecutor executes tools
4. Frontend receives tool results via SSE
5. Artifacts sidebar displays visualizations
```

**Validation:**
```bash
# Final test run
pytest tests/ -v --cov
cd frontend && npm test -- --coverage

# Expected: 25/25 tests passing (100%)
```

**Expected Result:**
- All bugs fixed
- 25/25 tests passing
- Documentation complete
- Architecture clearly explained

---

## Troubleshooting

**Common Issues:**

**Issue 1: AsyncAnthropic mocking fails**
- See TROUBLESHOOTING.md:Lines 1400-1425
- Solution: Use AsyncMock for async methods, patch at correct module path

**Issue 2: Frontend tests timeout**
- See TROUBLESHOOTING.md:Lines 1450-1475
- Solution: Use waitFor for async updates, increase timeout for streaming tests

**Issue 3: Integration tests fail intermittently**
- See TROUBLESHOOTING.md:Lines 1500-1525
- Solution: Mock external dependencies (Anthropic API, QueryRouter), use transactions for database tests

---

## Progress Tracking

**Subtasks:** 0/4 complete (0%)

- [ ] Subtask 2.5.5.1: Backend Unit Tests (10 tests)
- [ ] Subtask 2.5.5.2: Integration Tests (15 tests)
- [ ] Subtask 2.5.5.3: Frontend Tests (10 tests)
- [ ] Subtask 2.5.5.4: Bug Fixes and Documentation

**Tests:** 0/25 passing (0%)

**Last Updated:** 2025-10-21
