# Task 2.5: Voice Input and Testing

**Phase:** 2 - AI Conversation Hub
**Status:** ⬜ Not Started
**Estimated Duration:** 6 hours
**Assigned To:** (filled during execution)

---

## Overview

Add voice input feature using Web Speech API, write comprehensive test suite (15 backend tests + 5 frontend tests), and polish UI/UX based on testing feedback.

---

## Dependencies

**Required Before Starting:**
- Task 2.1: Backend Conversation Database (requires models)
- Task 2.2: LLM Integration (requires ConversationService)
- Task 2.3: Conversation API Endpoints (requires API)
- Task 2.4: Frontend Chat Interface (requires ConversationHub)

**Enables After Completion:**
- Phase 2.5: Claude Agents SDK Integration

---

## Success Criteria

✅ VoiceInput component functional with start/stop recording
✅ Speech recognition transcribes to text input
✅ Recording state visible (red pulse animation)
✅ All 15 backend tests passing (conversation service)
✅ All 5 frontend tests passing (ConversationHub)
✅ End-to-end conversation flow tested
✅ Bug fixes applied from testing
✅ Total: 20 tests passing (100%)

---

## Research References

**Technical Documentation:**
- research/documentation/web-speech-api.md (Lines: 1-100)
  - Key concepts: webkitSpeechRecognition, browser compatibility

- research/documentation/testing-best-practices.md (Lines: 1-150)
  - Key concepts: Unit tests, integration tests, mocking

**Implementation Guide:**
- IMPLEMENTATION.md (Lines: 2150-2351)
  - VoiceInput component
  - Complete test suite

---

## Test Specifications

**Backend Unit Tests:** (15 tests)
- TESTING.md: Lines 612-699
- File: `tests/unit/test_conversation.py`

**Frontend Component Tests:** (5 tests)
- TESTING.md: Lines 801-900
- File: `frontend/src/__tests__/components/ConversationHub.test.tsx`

**Integration Tests:** (included in backend tests)
- File: `tests/integration/test_conversations.py`

**Total Tests:** 20

---

## Implementation Steps

### Subtask 2.5.1: Voice Input Component

**Duration:** 2 hours
**Status:** ⬜ Not Started

**Files to Create:**
- `apex-memory-system/frontend/src/components/VoiceInput.tsx`

**Steps:**
1. Create VoiceInput component with onTranscript prop
2. Add state for isRecording
3. Create recognitionRef for SpeechRecognition instance
4. Implement startRecording function
5. Check for webkitSpeechRecognition support
6. Handle onresult event (extract transcript)
7. Handle onerror event
8. Implement stopRecording function
9. Add button with recording state styling (red pulse)

**Code Example:**
```typescript
// See IMPLEMENTATION.md lines 2154-2213 for complete code
```

**Validation:**
```bash
# Test in browser (Chrome/Edge recommended)
# 1. Click microphone button
# 2. Grant microphone permission
# 3. Speak a question
# 4. Verify transcript appears in input field
# 5. Verify recording button pulses red while recording
```

**Expected Result:**
- Microphone button toggles recording state
- Speech transcribed to text accurately
- Text inserted into message input field
- Red pulse animation during recording

---

### Subtask 2.5.2: Backend Unit Tests

**Duration:** 2 hours
**Status:** ⬜ Not Started

**Files to Create:**
- `apex-memory-system/tests/unit/test_conversation.py`

**Steps:**
1. Create test fixtures (db_session, user_uuid, conversation_service)
2. Write TestConversationCreation class (2 tests)
   - test_create_conversation_with_title
   - test_create_conversation_without_title
3. Write TestConversationRetrieval class (3 tests)
   - test_get_existing_conversation
   - test_get_nonexistent_conversation
   - test_cannot_get_other_users_conversation
4. Write TestMessageProcessing class (5 tests)
   - test_process_message_saves_user_message
   - test_process_message_calls_llm
   - test_process_message_saves_assistant_message
   - test_process_message_extracts_citations
   - test_process_message_updates_last_message_at
5. Write TestConversationManagement class (5 tests)
   - test_list_conversations
   - test_delete_conversation
   - test_conversation_history_maintained
   - test_message_with_context
   - test_authorization_enforced

**Code Example:**
```python
# See IMPLEMENTATION.md lines 2223-2343 and TESTING.md lines 622-699 for complete code
```

**Validation:**
```bash
# Run backend tests
pytest tests/unit/test_conversation.py -v --cov=apex_memory.services.conversation_service

# Expected output: 15/15 tests passing, 90%+ coverage
```

**Expected Result:**
- All 15 unit tests passing
- 90%+ code coverage on ConversationService
- All edge cases tested (authorization, errors)

---

### Subtask 2.5.3: Frontend Component Tests

**Duration:** 1.5 hours
**Status:** ⬜ Not Started

**Files to Create:**
- `apex-memory-system/frontend/src/__tests__/components/ConversationHub.test.tsx`

**Steps:**
1. Set up test environment (React Testing Library, mock axios)
2. Write test: ConversationHub renders empty state
3. Write test: Load conversations on mount
4. Write test: Create new conversation
5. Write test: Send message updates conversation
6. Write test: Citations display correctly
7. Mock AuthContext and API responses

**Code Example:**
```typescript
// See TESTING.md lines 801-900 for complete code (not in IMPLEMENTATION.md excerpt)
```

**Validation:**
```bash
# Run frontend tests
cd frontend
npm test -- ConversationHub.test.tsx --coverage

# Expected output: 5/5 tests passing, 85%+ coverage
```

**Expected Result:**
- All 5 frontend tests passing
- 85%+ code coverage on ConversationHub
- API mocking works correctly

---

### Subtask 2.5.4: Integration Tests and Bug Fixes

**Duration:** 0.5 hours
**Status:** ⬜ Not Started

**Files to Create:**
- `apex-memory-system/tests/integration/test_conversations.py`

**Steps:**
1. Write end-to-end conversation flow test
2. Test: create → send message → verify response → verify citations
3. Test: conversation history maintained across multiple messages
4. Run all tests and identify bugs
5. Fix any bugs discovered during testing
6. Add error handling improvements
7. Polish loading states and error messages

**Code Example:**
```python
# See IMPLEMENTATION.md lines 2270-2343 for integration test examples
```

**Validation:**
```bash
# Run all tests
pytest tests/ -v --cov

# Check coverage report
pytest --cov-report=html
open htmlcov/index.html

# Frontend tests
cd frontend && npm test -- --coverage
```

**Expected Result:**
- All 20 tests passing (15 backend + 5 frontend)
- 90%+ backend coverage, 85%+ frontend coverage
- No critical bugs remaining
- Error handling polished

---

## Troubleshooting

**Common Issues:**

**Issue 1: Speech recognition not supported**
- See TROUBLESHOOTING.md:Lines 650-675
- Solution: Use Chrome/Edge, add browser compatibility check, show fallback UI

**Issue 2: Tests fail due to async timing**
- See TROUBLESHOOTING.md:Lines 700-725
- Solution: Use waitFor from React Testing Library, await async operations

**Issue 3: Mock data not matching real API**
- See TROUBLESHOOTING.md:Lines 750-775
- Solution: Align mock responses with actual API schemas, use factories

---

## Progress Tracking

**Subtasks:** 0/4 complete (0%)

- [ ] Subtask 2.5.1: Voice Input Component
- [ ] Subtask 2.5.2: Backend Unit Tests (15 tests)
- [ ] Subtask 2.5.3: Frontend Component Tests (5 tests)
- [ ] Subtask 2.5.4: Integration Tests and Bug Fixes

**Tests:** 0/20 passing (0%)

**Last Updated:** 2025-10-21
