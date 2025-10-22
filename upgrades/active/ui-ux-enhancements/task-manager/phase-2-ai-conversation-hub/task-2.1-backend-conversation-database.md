# Task 2.1: Backend Conversation Database and Models

**Phase:** 2 - AI Conversation Hub
**Status:** ⬜ Not Started
**Estimated Duration:** 4 hours
**Assigned To:** (filled during execution)

---

## Overview

Create PostgreSQL database schema for conversations and messages, implement SQLAlchemy models and Pydantic schemas for conversation management.

**Why This Task:**
This establishes the persistence layer for the ChatGPT-like conversation experience. Without this foundation, conversations cannot be saved, retrieved, or managed across sessions.

---

## Dependencies

**Required Before Starting:**
- Phase 1: Authentication Foundation (requires users table and authentication)

**Enables After Completion:**
- Task 2.2: LLM Integration and Conversation Service

---

## Success Criteria

✅ PostgreSQL conversations and messages tables created
✅ Alembic migration applied successfully
✅ ConversationDB and MessageDB SQLAlchemy models functional
✅ Pydantic schemas complete (Conversation, Message, Citation, ConversationCreate, MessageCreate)
✅ Database indexes created on user_uuid and conversation_uuid
✅ CASCADE delete works (deleting conversation deletes messages)

---

## Research References

**Architecture Decisions:**
- ADR-002: Conversation Data Model (Section: JSONB for citations vs. separate table)
  - Why relevant: Chose JSONB for flexible citation storage
  - Key decision: Citations stored as JSONB array in messages table

**Technical Documentation:**
- research/documentation/postgresql/jsonb-patterns.md (Lines: 1-80)
  - Key concepts: JSONB indexing, querying nested structures

**Implementation Guide:**
- IMPLEMENTATION.md (Lines: 1371-1531)
  - Detailed steps for Day 1
  - Complete code examples for schema and models

---

## Test Specifications

**Unit Tests:** (5 tests)
- TESTING.md: Lines 612-699
- File: `tests/unit/test_conversation.py`
- Coverage target: 90%+

**Tests to pass:**
1. Create conversation with title
2. Create conversation without title
3. Get existing conversation
4. Get nonexistent conversation returns None
5. Cannot get other user's conversation (authorization)

**Total Tests:** 5

---

## Implementation Steps

### Subtask 2.1.1: Database Migration

**Duration:** 1.5 hours
**Status:** ⬜ Not Started

**Files to Create:**
- `apex-memory-system/alembic/versions/002_add_conversations.py`

**Steps:**
1. Create Alembic migration for conversations and messages tables
2. Add conversations table (uuid, user_uuid, title, created_at, last_message_at)
3. Add messages table (uuid, conversation_uuid, role, content, citations, created_at)
4. Add foreign key constraints (user_uuid → users, conversation_uuid → conversations)
5. Add indexes on user_uuid and conversation_uuid
6. Add CASCADE delete on messages when conversation deleted
7. Run migration: `alembic upgrade head`

**Code Example:**
```python
# See IMPLEMENTATION.md lines 1385-1431 for complete code
```

**Validation:**
```bash
# Check migration applied
alembic current

# Verify schema
psql -d apex_memory -c "\d conversations"
psql -d apex_memory -c "\d messages"

# Check indexes
psql -d apex_memory -c "\d+ conversations" | grep idx
psql -d apex_memory -c "\d+ messages" | grep idx
```

**Expected Result:**
- conversations and messages tables exist
- Indexes on user_uuid and conversation_uuid
- Foreign key constraints in place

---

### Subtask 2.1.2: SQLAlchemy Models

**Duration:** 1 hour
**Status:** ⬜ Not Started

**Files to Create:**
- `apex-memory-system/src/apex_memory/models/conversation.py`

**Steps:**
1. Create ConversationDB model with UUID primary key
2. Create MessageDB model with UUID primary key
3. Add foreign key relationships (user_uuid, conversation_uuid)
4. Add JSONB column for citations
5. Add timestamps (created_at, last_message_at)

**Code Example:**
```python
# See IMPLEMENTATION.md lines 1435-1473 for complete code
```

**Validation:**
```bash
# Test in Python REPL
python -c "
from apex_memory.models.conversation import ConversationDB, MessageDB
print('ConversationDB table:', ConversationDB.__tablename__)
print('MessageDB table:', MessageDB.__tablename__)
print('ConversationDB columns:', [c.name for c in ConversationDB.__table__.columns])
print('MessageDB columns:', [c.name for c in MessageDB.__table__.columns])
"
```

**Expected Result:**
- Models import successfully
- Tables correctly named
- Columns match schema specification

---

### Subtask 2.1.3: Pydantic Schemas

**Duration:** 1.5 hours
**Status:** ⬜ Not Started

**Files to Modify:**
- `apex-memory-system/src/apex_memory/models/conversation.py` (add schemas)

**Steps:**
1. Create Citation schema (document_uuid, document_title, relevant_excerpt, confidence_score)
2. Create Message schema with citations list
3. Create Conversation schema with messages list
4. Create ConversationCreate input schema
5. Create MessageCreate input schema
6. Create ConversationResponse schema
7. Add validation (confidence_score 0.0-1.0)

**Code Example:**
```python
# See IMPLEMENTATION.md lines 1475-1529 for complete code
```

**Validation:**
```bash
# Test in Python REPL
python -c "
from apex_memory.models.conversation import Citation, Message, Conversation
from uuid import uuid4
from datetime import datetime

# Test Citation validation
c = Citation(
    document_uuid=uuid4(),
    document_title='Test',
    relevant_excerpt='...',
    confidence_score=0.95
)
print('Citation created:', c.document_title)

# Test Message schema
m = Message(
    uuid=uuid4(),
    conversation_uuid=uuid4(),
    role='assistant',
    content='Test response',
    citations=[c],
    created_at=datetime.utcnow()
)
print('Message created:', m.role)
"
```

**Expected Result:**
- All schemas validate correctly
- Citations properly typed
- Confidence score validated to 0.0-1.0 range

---

## Troubleshooting

**Common Issues:**

**Issue 1: Alembic migration fails**
- See TROUBLESHOOTING.md:Lines 200-225
- Solution: Check users table exists (Phase 1 required), verify PostgreSQL connection

**Issue 2: JSONB column errors**
- See TROUBLESHOOTING.md:Lines 250-275
- Solution: Ensure PostgreSQL version 9.4+ supports JSONB, check dialect import

---

## Progress Tracking

**Subtasks:** 0/3 complete (0%)

- [ ] Subtask 2.1.1: Database Migration
- [ ] Subtask 2.1.2: SQLAlchemy Models
- [ ] Subtask 2.1.3: Pydantic Schemas

**Tests:** 0/5 passing (0%)

**Last Updated:** 2025-10-21
