# Task 2.2: LLM Integration and Conversation Service

**Phase:** 2 - AI Conversation Hub
**Status:** ⬜ Not Started
**Estimated Duration:** 6 hours
**Assigned To:** (filled during execution)

---

## Overview

Implement ConversationService with Claude API integration, Apex Memory context retrieval, conversation history management, and citation extraction.

---

## Dependencies

**Required Before Starting:**
- Task 2.1: Backend Conversation Database and Models (requires schemas)
- Query Router functional (from existing system)

**Enables After Completion:**
- Task 2.3: Frontend Chat Interface

---

## Success Criteria

✅ ConversationService class functional with all methods
✅ Claude API integration working (anthropic SDK)
✅ Query router retrieves top 5 relevant documents
✅ Conversation history maintained (last 10 messages)
✅ Citations extracted from context and attached to messages
✅ System prompt built with retrieved context
✅ All backend unit tests passing (10 tests)

---

## Research References

**Technical Documentation:**
- research/documentation/claude-api/messages-api.md (Lines: 1-150)
  - Key concepts: Message format, system prompts, streaming

- research/documentation/query-routing/context-retrieval.md (Lines: 1-100)
  - Key concepts: Query router integration, result formatting

**Implementation Guide:**
- IMPLEMENTATION.md (Lines: 1535-1923)
  - Detailed steps for Day 2
  - Complete service implementation

---

## Test Specifications

**Backend Unit Tests:** (10 tests)
- TESTING.md: Lines 662-699
- File: `tests/unit/test_conversation.py`
- Coverage target: 90%+

**Tests to pass:**
1. Create conversation service instance
2. Process message retrieves context
3. Process message calls Claude API
4. Process message saves user and assistant messages
5. Process message extracts citations
6. Process message updates last_message_at
7. Conversation history retrieval (last 10 messages)
8. List conversations for user
9. Delete conversation
10. Authorization: Cannot delete other user's conversation

**Total Tests:** 10

---

## Implementation Steps

### Subtask 2.2.1: Conversation Service Core Methods

**Duration:** 2 hours
**Status:** ⬜ Not Started

**Files to Create:**
- `apex-memory-system/src/apex_memory/services/conversation_service.py`

**Files to Modify:**
- `apex-memory-system/src/apex_memory/config.py` (add ANTHROPIC_API_KEY)

**Steps:**
1. Install anthropic SDK: `pip install anthropic`
2. Add ANTHROPIC_API_KEY to .env and config.py
3. Create ConversationService class with __init__(db: Session)
4. Initialize Anthropic client and QueryRouter
5. Implement create_conversation method
6. Implement get_conversation method (with message loading)
7. Implement list_conversations method (ordered by last_message_at)
8. Implement delete_conversation method

**Code Example:**
```python
# See IMPLEMENTATION.md lines 1539-1795 for complete code
```

**Validation:**
```bash
# Test in Python REPL
python -c "
from apex_memory.services.conversation_service import ConversationService
from apex_memory.models.conversation import ConversationCreate
from uuid import uuid4

# Test conversation creation (requires db session)
print('ConversationService imported successfully')
"
```

**Expected Result:**
- Service initializes with db session
- CRUD methods functional
- Authorization checks enforce user ownership

---

### Subtask 2.2.2: Context Retrieval Integration

**Duration:** 2 hours
**Status:** ⬜ Not Started

**Files to Modify:**
- `apex-memory-system/src/apex_memory/services/conversation_service.py` (add _retrieve_context)

**Steps:**
1. Implement _retrieve_context async method
2. Call query router with user's message
3. Format top 5 results for LLM context
4. Extract title, content, score, uuid from each result
5. Handle empty results gracefully

**Code Example:**
```python
# See IMPLEMENTATION.md lines 1664-1679 for complete code
```

**Validation:**
```bash
# Test context retrieval (requires query router and sample data)
pytest tests/unit/test_conversation.py::TestContextRetrieval -v
```

**Expected Result:**
- Top 5 most relevant documents retrieved
- Results formatted for LLM consumption
- Scores included for citation confidence

---

### Subtask 2.2.3: Claude API Integration

**Duration:** 2 hours
**Status:** ⬜ Not Started

**Files to Modify:**
- `apex-memory-system/src/apex_memory/services/conversation_service.py` (add _generate_response, _build_system_prompt)

**Steps:**
1. Implement _build_system_prompt method (inject context)
2. Format context as numbered documents with excerpts
3. Add instructions for citation and knowledge usage
4. Implement _generate_response async method
5. Build conversation history for Claude
6. Call anthropic.messages.create with claude-3-5-sonnet
7. Extract response text
8. Build citations list from context
9. Return (response_text, citations) tuple

**Code Example:**
```python
# See IMPLEMENTATION.md lines 1701-1759 for complete code
```

**Validation:**
```bash
# Test Claude API integration
python -c "
import asyncio
from apex_memory.services.conversation_service import ConversationService

# Mock test (requires API key and db)
print('Claude integration ready')
"

# Test with actual API call
pytest tests/integration/test_claude_integration.py -v
```

**Expected Result:**
- System prompt includes retrieved context
- Claude generates relevant responses
- Citations extracted from context used

---

### Subtask 2.2.4: Message Processing Pipeline

**Duration:** 2 hours (overlaps with above)
**Status:** ⬜ Not Started

**Files to Modify:**
- `apex-memory-system/src/apex_memory/services/conversation_service.py` (add process_message, _get_conversation_history)

**Steps:**
1. Implement _get_conversation_history method (last 10 messages)
2. Reverse chronological order for context
3. Implement process_message async method
4. Save user message to database
5. Retrieve context from Apex Memory
6. Get conversation history
7. Generate AI response with Claude
8. Save assistant message with citations
9. Update conversation.last_message_at timestamp
10. Return assistant message

**Code Example:**
```python
# See IMPLEMENTATION.md lines 1620-1662, 1681-1700 for complete code
```

**Validation:**
```bash
# Test full message processing pipeline
pytest tests/integration/test_conversations.py::test_process_message -v
pytest tests/integration/test_conversations.py::test_message_with_context -v
```

**Expected Result:**
- User message saved immediately
- Context retrieved from knowledge graph
- AI response generated with citations
- Both messages persisted to database
- last_message_at timestamp updated

---

## Troubleshooting

**Common Issues:**

**Issue 1: Claude API rate limits**
- See TROUBLESHOOTING.md:Lines 300-325
- Solution: Implement exponential backoff, handle 429 errors

**Issue 2: Context retrieval empty**
- See TROUBLESHOOTING.md:Lines 350-375
- Solution: Verify query router functional, check document ingestion

**Issue 3: Citations not appearing**
- See TROUBLESHOOTING.md:Lines 400-425
- Solution: Verify context has 'uuid' field, check JSONB serialization

---

## Progress Tracking

**Subtasks:** 0/4 complete (0%)

- [ ] Subtask 2.2.1: Conversation Service Core Methods
- [ ] Subtask 2.2.2: Context Retrieval Integration
- [ ] Subtask 2.2.3: Claude API Integration
- [ ] Subtask 2.2.4: Message Processing Pipeline

**Tests:** 0/10 passing (0%)

**Last Updated:** 2025-10-21
