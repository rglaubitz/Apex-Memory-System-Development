# Conversational Memory Integration

**Status:** 🟢 Phases 1, 2, 4 Complete - 145/145 Tests Passing
**Priority:** P0 - Critical (enables AI agent brain functionality)
**Completion:** Phase 1 (11/14), Phase 2 (11/14), Phase 4 (11/15)
**Next:** Planning Phase 5 - Human↔Agent Interface (Slack Custom)

---

## 🎯 The Problem

Apex Memory System successfully ingests documents (PDFs, DOCX) into the knowledge graph, but **conversations don't enrich the knowledge graph**. When users teach the system through conversations ("ACME Corp prefers aisle seats"), that knowledge stays trapped in flat PostgreSQL storage.

### Completed Work ✅

**Phase 1:** Multi-Agent Namespacing - 68 tests
**Phase 2:** Conversational Memory Feedback Loop - 43 tests
**Phase 4:** Agent↔Agent Communication - 34 tests
**Total:** 145/145 tests passing

### What's Working Now

- ✅ Document ingestion (PDFs → Graphiti/Neo4j)
- ✅ Conversation storage (PostgreSQL)
- ✅ **Conversational memory feedback loop** (Redis cache + GPT-5 nano extraction)
- ✅ **Agent↔agent communication** (NATS messaging + audit trail)
- ✅ **Automatic knowledge graph updates** from conversations

### Remaining Gap

- ❌ **Human↔Agent Slack interface** - Custom Slack integration for conversational memory
- ❌ **Enhanced entity extraction** - Better accuracy and routing beyond GPT-5 nano baseline

---

## 💡 The Solution

**Implement automatic conversation → knowledge graph ingestion** with:

### Three Core Paths

1. **Human↔Agent (70% traffic):** Slack → PostgreSQL → Background extraction → Neo4j/Graphiti
   - Agent-namespaced Redis caching: `oscar:conversation:123:context`
   - Agent-specific Qdrant collections: `oscar_fleet_knowledge`

2. **Agent↔Agent (30% traffic):** NATS → PostgreSQL → Background extraction → Neo4j/Graphiti
   - Cross-agent knowledge sharing: Oscar ↔ Sarah ↔ Maya
   - Agent-specific Neo4j labels: `:Oscar_Domain`, `:Sarah_Domain`, `:Maya_Domain`

3. **Performance Layer:** Redis caching (60% latency reduction, 5x cost savings)
   - Three agent namespaces: `oscar:*`, `sarah:*`, `maya:*`
   - Shared knowledge: `shared:entity:*`

### Five Degradation Tiers
1. **Pre-ingestion filtering:** Block 30-50% of low-value messages
2. **Importance scoring:** Multi-factor scoring for prioritization
3. **Memory decay:** Exponential decay over time (half-life: 30 days)
4. **Retention policies:** Automatic archival (7 days → 1 year based on tier)
5. **Consolidation:** Deduplicate repeated facts (20-40% reduction)

---

## 📂 Documentation Navigation

### 🏛️ **ARCHITECTURE.md** - **START HERE**
**Complete technical architecture with all final decisions**

Read this first for:
- Final tool decisions (Slack, NATS, PostgreSQL, Redis)
- Complete data flow diagrams
- Redis caching strategy (3 layers)
- 5-tier degradation strategy (with code examples)
- Realistic latency targets (P50/P95/Max)
- Storage architecture (PostgreSQL primary, no migration planned)
- Security, monitoring, scalability analysis

**Link:** [ARCHITECTURE.md](./ARCHITECTURE.md)

---

### 📋 **UPGRADE-PLAN.md** - Historical Planning Doc
**Status:** ⚠️ Superseded by ARCHITECTURE.md (archived to `archive/UPGRADE-PLAN-ORIGINAL.md`)

This document contained early planning notes and has been replaced with finalized architecture.

**For current implementation details:**
- See [ARCHITECTURE.md](./ARCHITECTURE.md) - Finalized technical architecture
- IMPLEMENTATION.md will be created in Phase 1 (Week 1)

**Original planning document:** [archive/UPGRADE-PLAN-ORIGINAL.md](./archive/UPGRADE-PLAN-ORIGINAL.md)

**Link:** [UPGRADE-PLAN.md](./UPGRADE-PLAN.md) (stub with navigation)

---

### 🛠️ **G_Tech_Stack_AI_Workforce.md** - Technology Choices
**Complete tech stack for AI workforce platform**

Includes:
- Agent infrastructure (MCP, LangGraph, Slack SDK)
- Apex Memory System overview
- Workflow & orchestration (Temporal.io, NATS)
- Development tools (ruff, uv, pytest)
- Agent deployment strategy (Oscar, Maya, Sarah)

**Link:** [G_Tech_Stack_AI_Workforce.md](./G_Tech_Stack_AI_Workforce.md)

---

### 🏗️ **AGENT_COMMAND_CENTER_CONCEPT.md** - Platform Vision
**Unified command center for human-agent collaboration**

Architecture:
- Slack (human interface layer)
- NATS (real-time agent backbone, <10ms)
- Grafana + Streamlit (observability dashboards)
- 3-layer hybrid architecture
- 6-month implementation timeline

**Link:** [AGENT_COMMAND_CENTER_CONCEPT.md](./AGENT_COMMAND_CENTER_CONCEPT.md)

---

### 🔬 **AGENT_COMMAND_CENTER_INTEGRATION_2025.md** - Research
**Research-backed integration patterns**

50+ sources including:
- Salesforce Agentforce (SlackAgents framework)
- Dust.tt (Temporal workflows)
- GitHub Copilot (session tracking)
- Code examples (LangSmith webhooks, NATS relay, Streamlit dashboards)

**Link:** [AGENT_COMMAND_CENTER_INTEGRATION_2025.md](./AGENT_COMMAND_CENTER_INTEGRATION_2025.md)

---

## 🔑 Key Architecture Decisions

### Tool Stack (Finalized)

| Component | Tool | Why |
|-----------|------|-----|
| Human Interface | Slack Bolt | Native to workflow, proven at scale |
| Agent Communication | NATS | <10ms latency, agent↔agent only (30% traffic) |
| Primary Storage | PostgreSQL | ACID guarantees, 90% implemented |
| Caching | **Redis** | **60% latency reduction, 5x cost savings** |
| Knowledge Graph | Neo4j + Graphiti | Temporal reasoning, entity relationships |
| Background Jobs | Temporal.io | Durable workflows, retry logic |
| Observability | LangSmith + Grafana | Traces + infrastructure monitoring |

### Performance Targets (Realistic)

| Metric | Target (P50) | Target (P95) | Max Acceptable |
|--------|--------------|--------------|----------------|
| **Slack response** | 2s | 3s | 5s |
| **Agent↔Agent (NATS)** | 10ms | 20ms | 50ms |
| **Background ingestion** | 10s | 20s | 60s |
| **Redis cache hit** | <5ms | 10ms | 50ms |

### Scalability Targets

- **Conversation volume:** 1000/hour sustained (10K/hour spikes)
- **Agent messages:** 10,000/min (166/sec)
- **Background processing:** 1000 msgs/hour (16.7/min sustained)
- **Cost:** <$0.05 per conversation (including LLM)

---

## 🤖 Multi-Agent Architecture

### Known Agents

**Active Agents (Phase 1):**
- **Oscar** (`oscar`) - Fleet Manager - Trucks, maintenance, routes, drivers
- **System** (`system`) - Default agent for shared operations

**Planned Agents (Phase 2 - Weeks 9-14):**
- **Sarah** (`sarah`) - CFO / Finance Agent - Invoices, costs, vendor analysis
- **Maya** (`maya`) - Sales / CRM Agent - Customers, quotes, pricing, deals

**Complete documentation:** [agent-registry.md](./agent-registry.md)

### Agent-Specific Data Flow Example

**Scenario:** Oscar (Fleet Manager) processes conversation about Truck 247 maintenance

```
1. User: "Truck 247 needs oil change next week"
         ↓
2. Slack → ConversationService (agent_id="oscar")
         ↓
3. Redis Check (Oscar namespace)
   Key: oscar:conversation:123:context
   Result: CACHE HIT (<5ms) - last 20 messages
         ↓
4. PostgreSQL Write
   Table: core.messages (agent_id="oscar")
         ↓
5. QueryRouter → Oscar's knowledge
   - Redis: oscar:entity:truck247:profile
   - Qdrant: oscar_fleet_knowledge collection
   - Neo4j: MATCH (t:Entity:Oscar_Domain {name: "Truck 247"})
         ↓
6. Claude API (context-aware response)
         ↓
7. Background Ingestion (Temporal)
   - Extract entities: ["Truck 247", "oil change", "next week"]
   - Write to: oscar_fleet_knowledge collection
   - Create Neo4j episode: (:Episode:Oscar_Domain)
```

**Key Benefits:**
- **Fast queries:** Oscar's collection only (not all agents)
- **No collisions:** Oscar's Truck 247 ≠ Sarah's invoice mentions
- **Clean monitoring:** Per-agent cache hit rates, query latency
- **Dynamic growth:** Add new agents in 15-30 minutes

### Cross-Agent Query Example (Phase 2)

**Scenario:** "How do maintenance costs (Oscar) affect our margins (Sarah)?"

```
1. Query Router detects cross-agent query
         ↓
2. Query Oscar's data:
   - Collection: oscar_fleet_knowledge
   - Query: "maintenance costs for Q4"
         ↓
3. Query Sarah's data:
   - Collection: sarah_financial_knowledge
   - Query: "profit margins Q4"
         ↓
4. Synthesize insight:
   "High maintenance costs ($50K) in Q4 reduced margins by 8%"
```

**Implementation Details:** See [ARCHITECTURE.md - Multi-Agent Namespacing Strategy](./ARCHITECTURE.md#multi-agent-namespacing-strategy)

---

## 🚀 Implementation Roadmap

### Timeline: 7-9 Weeks (Updated with Multi-Agent Patterns)

**Original:** 6-8 weeks
**With Fluid Mind Patterns:** +1 week → **7-9 weeks**
**Additional work:** Redis namespaces, Qdrant collections, PostgreSQL schema prep

```
✅ Week 0: Project Setup (COMPLETE - 2025-11-14)
     - Folder structure created
     - Documentation framework
     ↓
✅ Phase 1: Multi-Agent Namespacing (COMPLETE - 2025-11-14)
     - VectorService with agent-specific Qdrant collections
     - QueryRouter agent awareness
     - ConversationService agent_id support (already present)
     - 68/68 tests passing
     ↓
✅ Phase 2: Conversational Memory Feedback Loop (COMPLETE - 2025-11-14)
     - Redis conversation context caching
     - ConversationIngestionWorkflow (Temporal)
     - Background entity extraction (GPT-5 nano)
     - Messages API integration
     - 43/43 tests passing
     ↓
✅ Phase 4: Agent↔Agent Communication (COMPLETE - 2025-11-15)
     - NATS integration (pub/sub, request-reply)
     - agent_interactions table + API
     - AgentInteractionService with Graphiti integration
     - Automatic knowledge graph enrichment
     - 34/34 tests passing (26 unit + 8 integration)
     ↓
📍 YOU ARE HERE (145/145 tests passing)
     ↓
→ PLANNING: Phase 5 - Human↔Agent Interface (Slack Custom) ⭐ NEXT
     - Custom Slack integration for conversational memory
     - Enhanced entity extraction and routing
     - Improved accuracy and relevance
     ↓
Week 7: Proactive & Advanced Features
     - Context-triggered suggestions
     - Memory consolidation (synthesis)
     - Temporal pattern detection
     - Community detection
     - 15 tests
     ↓
Week 8: Comprehensive Testing & Validation
     - Integration tests (20 tests)
     - Load tests (5 tests)
     - Enhanced Saga baseline (156 tests preserved)
     - Performance benchmarks
     - Production validation (staging environment)
```

---

## 📊 Success Metrics

### Phase 2: Core Feedback Loop + Redis
- ✅ 100% of conversations auto-queued for ingestion
- ✅ 85%+ entity extraction accuracy
- ✅ **<5ms latency for cached context (Redis)**
- ✅ **95%+ Redis cache hit rate**
- ✅ Background ingestion completes within 20s (P95)

### Phase 3: Memory Quality & Importance
- ✅ 30-50% of low-value messages filtered
- ✅ Importance scores calculated for 100% of messages
- ✅ Daily decay workflow runs successfully
- ✅ **Automatic archival reduces hot storage by 80%**
- ✅ **Duplicate consolidation reduces redundancy by 20-40%**

### Phase 4: Agent↔Agent Communication
- ✅ 100% of agent interactions logged
- ✅ <20ms agent messaging latency (P95)
- ✅ Knowledge graph enriched from agent collaborations

### Phase 5: Proactive Features
- ✅ Proactive suggestions relevant >80% of the time
- ✅ Memory consolidation reduces storage by 20-30%
- ✅ Pattern detection identifies 5+ recurring patterns/user

### Phase 6: Production Validation
- ✅ 156 Enhanced Saga tests pass (100% pass rate)
- ✅ Load tests: 10+ concurrent users, 1000+ messages/hour
- ✅ **Cost: <$0.05 per conversation** (including LLM)
- ✅ **Neo4j storage: <100 GB** (with archival)
- ✅ **Redis: <2 GB memory usage**

---

## 🔄 Storage Architecture

### PostgreSQL Primary ✅
```
Message → PostgreSQL → Temporal → Graphiti
```

**Finalized Decision:**
- PostgreSQL as primary storage (no migration planned)
- NATS for agent↔agent messaging only (30% of traffic)
- Ship to production in 2-3 weeks

**Future Considerations:**
- If traffic exceeds 10,000 msgs/hour, evaluate event sourcing
- See `research/future-enhancements/event-sourcing-migration.md`
- Not planned for MVP

---

## ⚠️ Key Risks & Mitigation

### Technical Risks

**Performance Degradation**
- **Risk:** Latency increases under load
- **Mitigation:** Redis caching (95% load reduction), horizontal scaling
- **Rollback:** Feature flag to disable background ingestion

**Cost Overruns**
- **Risk:** LLM API costs exceed budget
- **Mitigation:** Redis deduplication (5x savings), quality filters (30-50% reduction)
- **Monitoring:** Daily cost alerts, per-message budget tracking

**Database Performance**
- **Risk:** PostgreSQL/Neo4j slow queries
- **Mitigation:** Proper indexing, Redis caching, read replicas
- **Monitoring:** Query latency dashboards, slow query alerts

### Operational Risks

**Breaking Changes**
- **Risk:** Regression in existing functionality
- **Mitigation:** Enhanced Saga baseline (156 tests), feature flags
- **Rollback:** Alembic migration rollback, disable feature flags

**Team Knowledge Gap**
- **Risk:** Team unfamiliar with NATS, event sourcing
- **Mitigation:** Start simple (PostgreSQL), migrate later
- **Training:** Documentation, runbooks, workshops

---

## 💰 Cost Analysis

### Year 1 Costs

**Infrastructure (Monthly):**
- Neo4j: $200/month (with archival, vs $2000 without)
- Redis: $50/month (2 GB instance)
- S3 archival: $50/month (cold storage)
- LLM API: $500-1000/month (with deduplication)
- **Total: $800-1300/month**

**Development (One-Time):**
- 6-8 weeks × 1 developer = **$20,000-30,000**

**Year 1 Total: ~$30,000-$45,000**

### Cost Savings from Architecture

**Redis caching:**
- LLM API duplicate calls: **-$300-1500/month**
- PostgreSQL query load: **-95% fewer queries**

**5-tier degradation:**
- Neo4j storage: **-80% hot storage** ($200 vs $2000/month)
- S3 archival: **10x cheaper** than PostgreSQL for old data

**Net savings: ~$25,000/year** compared to naive implementation

---

## 🎓 Next Steps

### 1. Review & Approve Architecture
- [ ] Read [ARCHITECTURE.md](./ARCHITECTURE.md) (complete technical architecture)
- [ ] Validate tool decisions (Slack, NATS, Redis, PostgreSQL)
- [ ] Approve latency targets (realistic for production)

### 2. Activate Project
- [ ] Move from `upgrades/planned/` → `upgrades/active/`
- [ ] Update `upgrades/active/README.md` with new project

### 3. Begin Phase 1: Research & Documentation
- [ ] Create 5 ADRs (architecture decision records)
- [ ] Design database schemas (retention_tier, importance_score, etc.)
- [ ] Write IMPLEMENTATION.md (step-by-step guide)
- [ ] Write TESTING.md (70+ test specifications)

### 4. Week 2-3: Implement Phase 2 (MVP)
- [ ] Add Redis caching to ConversationService
- [ ] Integrate background Graphiti ingestion
- [ ] Create ConversationIngestionWorkflow (Temporal)
- [ ] Ship to production ✅

---

## 📞 Questions?

**Architecture questions?** See [ARCHITECTURE.md](./ARCHITECTURE.md) - complete technical reference

**Implementation details?** See [UPGRADE-PLAN.md](./UPGRADE-PLAN.md) - phase-by-phase breakdown

**Tool decisions?** See [G_Tech_Stack_AI_Workforce.md](./G_Tech_Stack_AI_Workforce.md) - full tech stack

**Platform vision?** See [AGENT_COMMAND_CENTER_CONCEPT.md](./AGENT_COMMAND_CENTER_CONCEPT.md) - long-term roadmap

---

**Project Status:** ✅ Architecture Finalized
**Last Updated:** 2025-11-14
**Ready for:** Activation → Phase 1 (Research & Documentation)
