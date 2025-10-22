# Task 2.3: Conversation API Endpoints

**Phase:** 2 - AI Conversation Hub
**Status:** ⬜ Not Started
**Estimated Duration:** 3 hours
**Assigned To:** (filled during execution)

---

## Overview

Create FastAPI REST endpoints for conversation management: create conversation, list conversations, get conversation, send message, and delete conversation.

---

## Dependencies

**Required Before Starting:**
- Task 2.2: LLM Integration and Conversation Service (requires ConversationService)

**Enables After Completion:**
- Task 2.4: Frontend Chat Interface

---

## Success Criteria

✅ API router created with /api/v1/conversations prefix
✅ POST / endpoint creates conversation
✅ GET / endpoint lists user's conversations
✅ GET /{uuid} endpoint retrieves specific conversation
✅ POST /{uuid}/messages endpoint sends message and gets AI response
✅ DELETE /{uuid} endpoint deletes conversation
✅ All endpoints protected by authentication
✅ OpenAPI docs updated at /docs

---

## Research References

**Technical Documentation:**
- research/documentation/fastapi/async-endpoints.md (Lines: 1-100)
  - Key concepts: Async route handlers, dependency injection

- research/documentation/fastapi/error-handling.md (Lines: 1-80)
  - Key concepts: HTTPException, 404/401/403 responses

**Implementation Guide:**
- IMPLEMENTATION.md (Lines: 1797-1923)
  - Complete API endpoint implementations

---

## Test Specifications

**Integration Tests:** (5 tests)
- TESTING.md: Lines 700-800
- File: `tests/integration/test_conversation_api.py`

**Tests to pass:**
1. POST /conversations creates new conversation
2. GET /conversations lists user conversations
3. POST /conversations/{uuid}/messages sends message
4. DELETE /conversations/{uuid} deletes conversation
5. GET /conversations/{uuid} returns 404 for nonexistent

**Total Tests:** 5

---

## Implementation Steps

### Subtask 2.3.1: Create Conversation Router

**Duration:** 1.5 hours
**Status:** ⬜ Not Started

**Files to Create:**
- `apex-memory-system/src/apex_memory/api/conversations.py`

**Steps:**
1. Create APIRouter with prefix /api/v1/conversations
2. Import dependencies (get_db, get_current_user, ConversationService)
3. Import schemas (Conversation, ConversationCreate, MessageCreate, ConversationResponse)
4. Implement POST / endpoint (create conversation)
5. Implement GET / endpoint (list conversations with pagination)
6. Implement GET /{conversation_uuid} endpoint (get specific conversation)
7. Add authentication dependency to all endpoints
8. Add proper error handling (404, 401)

**Code Example:**
```python
# See IMPLEMENTATION.md lines 1799-1862 for complete code
```

**Validation:**
```bash
# Start server
python -m uvicorn apex_memory.main:app --reload

# Test with curl
TOKEN="your-test-token"

# Create conversation
curl -X POST http://localhost:8000/api/v1/conversations/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Conversation"}'

# List conversations
curl -X GET http://localhost:8000/api/v1/conversations/ \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Result:**
- POST / returns created conversation with UUID
- GET / returns list of user's conversations
- GET /{uuid} returns conversation with messages
- 401 if not authenticated

---

### Subtask 2.3.2: Message Sending Endpoint

**Duration:** 1 hour
**Status:** ⬜ Not Started

**Files to Modify:**
- `apex-memory-system/src/apex_memory/api/conversations.py` (add send_message endpoint)

**Steps:**
1. Implement POST /{conversation_uuid}/messages endpoint
2. Verify conversation exists and belongs to user (404 if not)
3. Call ConversationService.process_message (async)
4. Return ConversationResponse (message + updated conversation)
5. Handle errors from LLM gracefully

**Code Example:**
```python
# See IMPLEMENTATION.md lines 1864-1895 for complete code
```

**Validation:**
```bash
# Send message
curl -X POST http://localhost:8000/api/v1/conversations/{UUID}/messages \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content": "What is Apex Memory?"}'

# Response should include:
# - message: AI response with citations
# - conversation: updated conversation object
```

**Expected Result:**
- User message saved immediately
- AI response generated with context
- Citations included in response
- Conversation returned with all messages

---

### Subtask 2.3.3: Delete Endpoint and Router Registration

**Duration:** 0.5 hours
**Status:** ⬜ Not Started

**Files to Modify:**
- `apex-memory-system/src/apex_memory/api/conversations.py` (add delete endpoint)
- `apex-memory-system/src/apex_memory/main.py` (register router)

**Steps:**
1. Implement DELETE /{conversation_uuid} endpoint
2. Call ConversationService.delete_conversation
3. Return 204 No Content on success
4. Return 404 if conversation not found
5. Register router in main.py
6. Verify OpenAPI docs updated at /docs

**Code Example:**
```python
# See IMPLEMENTATION.md lines 1898-1922 for complete code
```

**Validation:**
```bash
# Delete conversation
curl -X DELETE http://localhost:8000/api/v1/conversations/{UUID} \
  -H "Authorization: Bearer $TOKEN"

# Should return 204 No Content

# Verify deleted
curl -X GET http://localhost:8000/api/v1/conversations/{UUID} \
  -H "Authorization: Bearer $TOKEN"
# Should return 404 Not Found

# Check OpenAPI docs
open http://localhost:8000/docs
# Verify /conversations endpoints listed
```

**Expected Result:**
- DELETE returns 204 on success
- Conversation and messages deleted from database
- 404 if trying to delete nonexistent conversation
- OpenAPI docs show all endpoints

---

## Troubleshooting

**Common Issues:**

**Issue 1: Router not registered**
- See TROUBLESHOOTING.md:Lines 450-475
- Solution: Verify app.include_router(conversations.router) in main.py

**Issue 2: Async endpoint errors**
- See TROUBLESHOOTING.md:Lines 500-525
- Solution: Use async def for endpoints calling async methods, await service calls

---

## Progress Tracking

**Subtasks:** 0/3 complete (0%)

- [ ] Subtask 2.3.1: Create Conversation Router
- [ ] Subtask 2.3.2: Message Sending Endpoint
- [ ] Subtask 2.3.3: Delete Endpoint and Router Registration

**Tests:** 0/5 passing (0%)

**Last Updated:** 2025-10-21
