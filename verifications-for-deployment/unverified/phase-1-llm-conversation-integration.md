# Phase 1: LLM Conversation Integration Architecture

**Status:** UNVERIFIED
**Created:** 2025-10-20
**Researcher:** TBD
**Priority:** BLOCKER

---

## Hypothesis

The Apex Memory System lacks a complete LLM conversation integration architecture. There is no mechanism to:

1. Capture LLM conversations (user messages + assistant responses)
2. Extract entities and relationships from conversations via Graphiti
3. Store conversations in the multi-database system
4. Retrieve conversation context for future queries

**Current State Assumption:**
- Users can upload documents, but cannot capture LLM conversation history
- No conversation ingestion workflow exists
- No API endpoint for conversation submission
- No database schema for storing conversations
- System relies on external tools (like OpenMemory) for conversation capture

**What This Means:**
Without conversation integration, the LLM cannot build operational memory from interactions. This is the core missing piece that prevents the system from being a complete "memory system" for LLMs.

---

## Expected Behavior

### Where it should exist:

**1. API Endpoint:**
- Location: `apex-memory-system/src/apex_memory/api/routes/conversation.py`
- Endpoint: `POST /api/v1/conversation`
- Accepts: `{user_message, assistant_message, session_id, timestamp}`

**2. Temporal Workflow:**
- Location: `apex-memory-system/src/apex_memory/temporal/workflows/conversation.py`
- Workflow: `ConversationIngestionWorkflow`
- Activities:
  - `store_conversation_activity()`
  - `extract_entities_from_conversation_activity()`
  - `generate_conversation_embedding_activity()`
  - `write_conversation_to_databases_activity()`

**3. Database Schema:**
- PostgreSQL table: `conversations`
  ```sql
  CREATE TABLE conversations (
    id UUID PRIMARY KEY,
    user_message TEXT NOT NULL,
    assistant_message TEXT NOT NULL,
    session_id TEXT,
    timestamp TIMESTAMP NOT NULL,
    embedding VECTOR(1536),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
  );
  ```

**4. Service Layer:**
- Location: `apex-memory-system/src/apex_memory/services/conversation_service.py`
- Methods:
  - `ingest_conversation(user_msg, assistant_msg, session_id)`
  - `extract_entities_from_conversation(conversation_text)`
  - `search_conversations(query, limit=10)`

**5. Database Writers:**
- PostgreSQL writer: `write_conversation()` method
- Neo4j writer: Store conversation entities/relationships
- Qdrant writer: Store conversation embeddings
- Redis writer: Cache recent conversations

### How it should work:

**User Flow:**
```
1. User talks to LLM
   User: "ACME Corp ordered 50 brake parts from Supplier Inc."
   LLM: "Noted. I've stored this information in the memory system."

2. LLM client POSTs conversation to Apex Memory API
   POST /api/v1/conversation
   {
     "user_message": "ACME Corp ordered 50 brake parts from Supplier Inc.",
     "assistant_message": "Noted. I've stored this information...",
     "session_id": "session-123",
     "timestamp": "2025-10-20T10:00:00Z"
   }

3. Apex Memory triggers ConversationIngestionWorkflow via Temporal

4. Workflow executes 4 activities in sequence:
   a. Store conversation → PostgreSQL (full text)
   b. Extract entities → Graphiti → Neo4j
   c. Generate embedding → OpenAI → Qdrant
   d. Cache → Redis (for fast retrieval)

5. Workflow completes
   Response: {
     "success": true,
     "conversation_id": "conv-uuid-123",
     "entities_extracted": 2,
     "workflow_id": "ingest-conv-uuid-123"
   }

6. Later, user queries: "Who supplies brake parts?"
   → Query Router: "graph query"
   → Neo4j: MATCH (supplier)-[:SUPPLIES]->(part)
   → LLM: "ACME Corp supplies brake parts (mentioned in conversation 3 days ago)"
```

**System Flow:**
```
ConversationIngestionWorkflow (Temporal)
├── store_conversation_activity()
│   └── PostgreSQL: INSERT INTO conversations (...)
├── extract_entities_from_conversation_activity()
│   └── Graphiti: add_episode(conversation_text)
│       └── Neo4j: CREATE entities + relationships
├── generate_conversation_embedding_activity()
│   └── OpenAI: text-embedding-3-small
│       └── Qdrant: Store vector
└── write_conversation_to_databases_activity()
    └── Redis: Cache recent conversation
```

### Expected Outputs:

**API Response:**
```json
{
  "success": true,
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "workflow_id": "ingest-conv-550e8400",
  "entities_extracted": 2,
  "session_id": "session-123",
  "status": "completed"
}
```

**Database State:**
- PostgreSQL: 1 row in `conversations` table
- Neo4j: 2 entities created (ACME Corp, brake parts), 1 relationship
- Qdrant: 1 vector stored in `conversations` collection
- Redis: 1 cached entry with key `conv:session-123:latest`

---

## Why Important

**Deployment Impact:** BLOCKER

**This is a BLOCKER because:**

1. **Core Value Proposition:** The entire purpose of Apex Memory System is to provide LLMs with operational memory. Without conversation capture, the system cannot fulfill this purpose.

2. **Current Gap:** Users currently rely on external tools (OpenMemory) for conversation capture. Apex should have this built-in.

3. **System Completeness:** The system can ingest documents and structured data, but cannot capture the most important data source: LLM conversations themselves.

4. **User Experience:** Without conversation integration:
   - Users must manually copy conversation snippets into document uploads
   - No automatic knowledge graph building from conversations
   - No temporal tracking of conversation topics
   - LLM cannot reference past conversations contextually

5. **Competitive Differentiation:** Conversation → Entity Extraction → Multi-DB Storage is what differentiates Apex from simple conversation stores like OpenMemory.

**Without this feature, the system is incomplete and cannot deliver on its core promise.**

---

## Research Plan

### Files to Check:

**API Layer:**
```bash
# Search for conversation endpoints
grep -r "conversation" apex-memory-system/src/apex_memory/api/

# Check for conversation routes
ls apex-memory-system/src/apex_memory/api/routes/ | grep conversation

# Search for conversation API classes
grep -r "class Conversation" apex-memory-system/src/apex_memory/api/
```

**Temporal Workflows:**
```bash
# Search for ConversationIngestionWorkflow
grep -r "ConversationIngestionWorkflow" apex-memory-system/src/apex_memory/temporal/workflows/

# Search for conversation workflow files
ls apex-memory-system/src/apex_memory/temporal/workflows/ | grep conversation

# Search for conversation activities
grep -r "conversation_activity" apex-memory-system/src/apex_memory/temporal/activities/
```

**Services:**
```bash
# Search for ConversationService
grep -r "class ConversationService" apex-memory-system/src/apex_memory/services/

# Search for conversation service files
ls apex-memory-system/src/apex_memory/services/ | grep conversation

# Search for conversation methods
grep -r "ingest_conversation" apex-memory-system/src/apex_memory/services/
```

**Database Layer:**
```bash
# Check for conversations table in PostgreSQL
PGPASSWORD=apexmemory2024 psql -h localhost -U apex -d apex_memory -c "\dt" | grep conversation

# Search for conversation database writers
grep -r "write_conversation" apex-memory-system/src/apex_memory/database/

# Check for conversation models
grep -r "class Conversation" apex-memory-system/src/apex_memory/models/
```

### Tests to Run:

**Unit Tests:**
```bash
# Search for conversation test files
find apex-memory-system/tests/unit/ -name "*conversation*"

# Run conversation service tests
pytest apex-memory-system/tests/unit/test_conversation_service.py -v

# Run conversation activity tests
pytest apex-memory-system/tests/unit/test_conversation_activities.py -v
```

**Integration Tests:**
```bash
# Search for conversation integration tests
find apex-memory-system/tests/integration/ -name "*conversation*"

# Run conversation workflow tests
pytest apex-memory-system/tests/integration/test_conversation_workflow.py -v -m integration
```

**API Tests:**
```bash
# Test conversation API endpoint
curl -X POST http://localhost:8000/api/v1/conversation \
  -H "Content-Type: application/json" \
  -d '{
    "user_message": "Test message",
    "assistant_message": "Test response",
    "session_id": "test-session",
    "timestamp": "2025-10-20T10:00:00Z"
  }'
```

### Evidence Needed:

**To prove IMPLEMENTED:**
- [ ] API endpoint `/api/v1/conversation` exists and returns 200
- [ ] `ConversationIngestionWorkflow` class defined
- [ ] All 4 activities implemented (store, extract, embed, write)
- [ ] PostgreSQL `conversations` table exists
- [ ] Tests exist and pass (unit + integration)
- [ ] Documentation exists

**To prove MISSING:**
- [ ] No API endpoint found
- [ ] No workflow class defined
- [ ] No activities found
- [ ] No database table exists
- [ ] No tests found
- [ ] No documentation

### Success Criteria:

**Feature is IMPLEMENTED if:**
1. API endpoint responds correctly
2. Workflow executes successfully
3. Conversation stored in PostgreSQL
4. Entities extracted to Neo4j
5. Embedding stored in Qdrant
6. All tests passing

**Feature is MISSING if:**
1. No API endpoint exists, OR
2. No workflow defined, OR
3. No database schema, OR
4. Tests missing or failing

---

## Research Log

**Link:** `research-logs/phase-1-llm-conversation-integration-research.md`

---

## Verification Decision

**Status:** PENDING

**Decision Date:** TBD
**Verified By:** TBD

**Evidence:**
[To be filled after research]

**Next Steps:**
- If IMPLEMENTED: Move to `verified/implemented/` and document architecture
- If MISSING: Move to `verified/missing/` and create upgrade plan in `upgrades/active/llm-conversation-integration/`

---

**Expected Outcome:** MISSING (based on initial assessment)

**Reason:** No evidence in testing-kit documents or recent codebase reviews of conversation-specific workflows or APIs. Document ingestion exists, but conversation capture appears to be a gap.

**If MISSING, Auto-Trigger:**
- Create `upgrades/active/llm-conversation-integration/`
- Priority: BLOCKER
- Timeline: 1-2 weeks for MVP
- Deliverables:
  - ConversationIngestionWorkflow
  - API endpoint
  - Database schema
  - Tests (10+ tests)
