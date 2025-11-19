# Phase 2: Core Feedback Loop + Redis - Implementation Plan

**Status:** 📝 Ready to Start
**Timeline:** 2 weeks (Weeks 2-3)
**Prerequisites:** ✅ Phase 1 Complete (Multi-Agent Namespacing)
**Target Tests:** 20 tests

---

## 🎯 Phase 2 Overview

**Goal:** Enable automatic conversation → knowledge graph ingestion with Redis caching

**The Feedback Loop:**
```
User Conversation → Immediate Response → Background Processing
                                              ↓
                                    Extract Entities (LLM)
                                              ↓
                                    Update Knowledge Graph
                                              ↓
                              Next Conversation Uses New Knowledge
```

---

## 📋 Implementation Tasks

### Task 1: Redis Conversation Context Caching (4-6 hours)

**Goal:** Cache last 20 messages per conversation for <5ms retrieval

**What to Build:**
1. **Extend CacheService** (`apex-memory-system/src/apex_memory/services/cache_service.py`)
   - Add `cache_conversation_context()` method
   - Add `get_conversation_context()` method
   - Agent-namespaced keys: `{agent_id}:conversation:{conv_id}:context`
   - TTL: 24 hours (conversation context)

2. **Update ConversationService** (`apex-memory-system/src/apex_memory/services/conversation_service.py`)
   - Integrate Redis cache for context retrieval
   - Cache last 20 messages on write
   - Check cache before PostgreSQL query
   - Target: 95%+ cache hit rate

**Files to Modify:**
- `src/apex_memory/services/cache_service.py` (+60 lines)
- `src/apex_memory/services/conversation_service.py` (+40 lines)

**Tests to Create:**
- `tests/unit/test_conversation_context_caching.py` (5 tests)
  - test_cache_conversation_context_agent_namespaced
  - test_get_conversation_context_cache_hit
  - test_get_conversation_context_cache_miss
  - test_cache_eviction_after_ttl
  - test_conversation_context_includes_last_20_messages

**Success Criteria:**
- ✅ Cache hit: <5ms retrieval
- ✅ Cache miss: Falls back to PostgreSQL
- ✅ Agent-namespaced keys (oscar:conversation:*, sarah:conversation:*)
- ✅ Last 20 messages cached per conversation

---

### Task 2: ConversationIngestionWorkflow (Temporal) (6-8 hours)

**Goal:** Background workflow to extract entities from conversations and update knowledge graph

**What to Build:**
1. **Create Temporal Activities** (`src/apex_memory/temporal/activities/conversation_ingestion.py` - NEW)
   ```python
   @activity.defn
   async def fetch_conversation_messages(conversation_id: str, agent_id: str) -> list[dict]:
       """Fetch messages from PostgreSQL for a conversation."""

   @activity.defn
   async def extract_conversation_entities(messages: list[dict], agent_id: str) -> dict:
       """Extract entities from conversation using LLM."""

   @activity.defn
   async def write_entities_to_qdrant(entities: dict, agent_id: str) -> bool:
       """Write extracted entities to agent's Qdrant collection."""

   @activity.defn
   async def create_graphiti_episode(entities: dict, conversation_id: str, agent_id: str) -> str:
       """Create Graphiti episode from conversation."""

   @activity.defn
   async def update_conversation_cache(conversation_id: str, agent_id: str) -> bool:
       """Update Redis cache with new context."""
   ```

2. **Create Workflow** (`src/apex_memory/temporal/workflows/conversation_ingestion.py` - NEW)
   ```python
   @workflow.defn
   class ConversationIngestionWorkflow:
       """Background workflow for conversation → knowledge graph ingestion."""

       @workflow.run
       async def run(self, conversation_id: str, agent_id: str = "system") -> dict:
           # 1. Fetch messages
           messages = await workflow.execute_activity(
               fetch_conversation_messages,
               args=[conversation_id, agent_id],
               start_to_close_timeout=timedelta(seconds=30)
           )

           # 2. Extract entities (LLM)
           entities = await workflow.execute_activity(
               extract_conversation_entities,
               args=[messages, agent_id],
               start_to_close_timeout=timedelta(seconds=60)
           )

           # 3. Write to Qdrant (agent-specific collection)
           await workflow.execute_activity(
               write_entities_to_qdrant,
               args=[entities, agent_id],
               start_to_close_timeout=timedelta(seconds=30)
           )

           # 4. Create Graphiti episode
           episode_id = await workflow.execute_activity(
               create_graphiti_episode,
               args=[entities, conversation_id, agent_id],
               start_to_close_timeout=timedelta(seconds=60)
           )

           # 5. Update cache
           await workflow.execute_activity(
               update_conversation_cache,
               args=[conversation_id, agent_id],
               start_to_close_timeout=timedelta(seconds=10)
           )

           return {
               "conversation_id": conversation_id,
               "agent_id": agent_id,
               "entities_extracted": len(entities),
               "episode_id": episode_id
           }
   ```

**Files to Create:**
- `src/apex_memory/temporal/activities/conversation_ingestion.py` (~300 lines)
- `src/apex_memory/temporal/workflows/conversation_ingestion.py` (~150 lines)

**Tests to Create:**
- `tests/unit/test_conversation_ingestion_activities.py` (5 tests)
  - test_fetch_conversation_messages
  - test_extract_conversation_entities_accuracy
  - test_write_entities_to_qdrant_agent_collection
  - test_create_graphiti_episode_with_agent_label
  - test_update_conversation_cache

- `tests/integration/test_conversation_ingestion_workflow.py` (5 tests)
  - test_conversation_ingestion_workflow_end_to_end
  - test_workflow_writes_to_correct_agent_collection
  - test_workflow_handles_llm_failures
  - test_workflow_creates_graphiti_episode
  - test_workflow_updates_cache

**Success Criteria:**
- ✅ Workflow completes in <20s (P95)
- ✅ 85%+ entity extraction accuracy
- ✅ Writes to agent-specific Qdrant collection
- ✅ Creates Graphiti episode with agent label (:Oscar_Domain, etc.)
- ✅ Retries on failure (Temporal handles this)

---

### Task 3: Integrate Messages API with Background Ingestion (3-4 hours)

**Goal:** Trigger ConversationIngestionWorkflow when messages are added

**What to Build:**
1. **Update Messages API** (`src/apex_memory/api/messages.py`)
   - Add Temporal client initialization
   - Trigger workflow after message ingestion
   - Pass agent_id to workflow
   - Fire-and-forget (don't block response)

2. **Update ConversationService** (`src/apex_memory/services/conversation_service.py`)
   - Add method to trigger ingestion workflow
   - Integration with Temporal client

**Files to Modify:**
- `src/apex_memory/api/messages.py` (+30 lines)
- `src/apex_memory/services/conversation_service.py` (+50 lines)

**Tests to Create:**
- `tests/integration/test_messages_api_background_ingestion.py` (5 tests)
  - test_message_ingest_triggers_workflow
  - test_workflow_uses_correct_agent_id
  - test_message_response_not_blocked_by_workflow
  - test_workflow_triggered_for_conversation_endpoint
  - test_workflow_triggered_for_json_endpoint

**Success Criteria:**
- ✅ Workflow triggered automatically after message ingestion
- ✅ Response not blocked (<2s P50, <3s P95)
- ✅ Correct agent_id passed to workflow
- ✅ Works for all message types (single, conversation, JSON)

---

### Task 4: Entity Extraction with LLM (4-5 hours)

**Goal:** Extract entities from conversation messages with 85%+ accuracy

**What to Build:**
1. **Create ConversationEntityExtractor** (`src/apex_memory/services/conversation_entity_extractor.py` - NEW)
   ```python
   class ConversationEntityExtractor:
       """Extract entities from conversation messages using LLM."""

       def __init__(self, openai_api_key: str, agent_id: str = "system"):
           self.client = openai.Client(api_key=openai_api_key)
           self.agent_id = agent_id

       async def extract_entities(self, messages: list[dict]) -> dict:
           """Extract entities from conversation messages."""
           # Build prompt with agent context
           prompt = self._build_extraction_prompt(messages, self.agent_id)

           # Call OpenAI
           response = await self.client.chat.completions.create(
               model="gpt-4o-mini",
               messages=[{"role": "user", "content": prompt}],
               temperature=0.0
           )

           # Parse entities
           entities = self._parse_entities(response.choices[0].message.content)

           return entities

       def _build_extraction_prompt(self, messages: list[dict], agent_id: str) -> str:
           """Build agent-specific extraction prompt."""
           # Agent context (Oscar = fleet, Sarah = finance, Maya = sales)
           agent_context = self._get_agent_context(agent_id)

           return f"""
           You are extracting entities from a conversation for {agent_context}.

           Extract:
           - Entities (people, places, things)
           - Relationships (X relates to Y how?)
           - Temporal facts (when did X happen?)

           Conversation:
           {self._format_messages(messages)}

           Return JSON:
           {{
               "entities": [
                   {{"name": "Truck 247", "type": "vehicle", "domain": "fleet"}},
                   ...
               ],
               "relationships": [
                   {{"source": "Truck 247", "relation": "NEEDS", "target": "Oil Change"}},
                   ...
               ],
               "facts": [
                   {{"fact": "Truck 247 scheduled for oil change", "valid_from": "now", "valid_to": "next_week"}},
                   ...
               ]
           }}
           """
   ```

**Files to Create:**
- `src/apex_memory/services/conversation_entity_extractor.py` (~250 lines)

**Tests to Create:**
- `tests/unit/test_conversation_entity_extractor.py` (5 tests)
  - test_extract_entities_from_simple_conversation
  - test_extract_entities_agent_specific_context
  - test_extract_relationships
  - test_extract_temporal_facts
  - test_extraction_accuracy_benchmark (85%+ accuracy)

**Success Criteria:**
- ✅ 85%+ entity extraction accuracy
- ✅ Agent-specific extraction (Oscar focuses on fleet, Sarah on finance)
- ✅ Extracts entities, relationships, temporal facts
- ✅ Returns structured JSON
- ✅ <30s extraction time (P95)

---

## 📊 Success Metrics

**Phase 2 Complete When:**
- ✅ 100% of conversations auto-queued for ingestion
- ✅ 85%+ entity extraction accuracy
- ✅ <5ms latency for cached context (Redis)
- ✅ 95%+ Redis cache hit rate
- ✅ Background ingestion completes within 20s (P95)
- ✅ 20/20 tests passing

---

## 🧪 Testing Strategy

**Unit Tests (15 tests):**
- Conversation context caching (5)
- Conversation ingestion activities (5)
- Conversation entity extractor (5)

**Integration Tests (5 tests):**
- Conversation ingestion workflow end-to-end (5)

**Total: 20 tests**

---

## 📁 Files Summary

**New Files (5):**
1. `src/apex_memory/temporal/activities/conversation_ingestion.py` (~300 lines)
2. `src/apex_memory/temporal/workflows/conversation_ingestion.py` (~150 lines)
3. `src/apex_memory/services/conversation_entity_extractor.py` (~250 lines)
4. `tests/unit/test_conversation_context_caching.py` (5 tests)
5. `tests/unit/test_conversation_entity_extractor.py` (5 tests)

**Modified Files (3):**
1. `src/apex_memory/services/cache_service.py` (+60 lines)
2. `src/apex_memory/services/conversation_service.py` (+90 lines)
3. `src/apex_memory/api/messages.py` (+30 lines)

**Test Files (3):**
1. `tests/unit/test_conversation_ingestion_activities.py` (5 tests)
2. `tests/integration/test_conversation_ingestion_workflow.py` (5 tests)
3. `tests/integration/test_messages_api_background_ingestion.py` (5 tests)

**Total New Lines:** ~1,000 lines of production code, ~600 lines of test code

---

## 🔄 Implementation Order

**Recommended sequence:**

1. **Start with Redis Caching** (Task 1) - Foundation for performance
   - Fastest to implement
   - Immediate performance benefit
   - No external dependencies

2. **Build Entity Extractor** (Task 4) - Core logic
   - Can test independently
   - Critical for accuracy validation
   - Needed by Temporal activities

3. **Create Temporal Workflow** (Task 2) - Background processing
   - Uses entity extractor
   - Integrates with Phase 1 VectorService
   - Most complex component

4. **Integrate with Messages API** (Task 3) - Wire everything together
   - Final integration point
   - End-to-end testing
   - Production-ready

---

## 🚀 Ready to Start?

**Next step:** Begin Task 1 (Redis Conversation Context Caching)

**Estimated time to Phase 2 completion:** 2 weeks (17-23 hours of implementation)

---

**Last Updated:** 2025-11-14
**Status:** Ready to start implementation
**Prerequisites:** ✅ Phase 1 complete (60/60 tests passing)
