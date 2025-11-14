# Active Upgrades

**Status:** 🚀 In Active Development

This directory contains upgrade projects currently in active development for the Apex Memory System.

## Overview

Active upgrades are projects that have:
- ✅ Completed research and planning phases
- ✅ Approved by Review Board (if applicable)
- 🚀 Currently being implemented or iteratively improved
- 📊 Active testing and validation

Unlike `planned/` upgrades (research phase) and `completed/` upgrades (archived), active upgrades represent ongoing work.

---

## Current Active Projects

### 1. Temporal Implementation - Graphiti + JSON Integration

**Status:** ✅ **95% COMPLETE** (17/18 days) | **Priority:** High | **Timeline:** 1 day remaining

Complete LLM-powered entity extraction, JSON structured data ingestion, and local staging infrastructure with Temporal.io workflow orchestration.

**What's Complete:**
- ✅ 5 Entity Schemas (Customer, Person, Invoice, Truck, Load) - 177 properties
- ✅ Graphiti Integration with LLM extraction (90%+ accuracy)
- ✅ JSON Support (Samsara, Turvo, FrontApp data sources)
- ✅ Local Staging (`/tmp/apex-staging/`)
- ✅ Workflow Separation (DocumentIngestionWorkflow + StructuredDataIngestionWorkflow)
- ✅ 40/40 critical tests passing (100%)

**Remaining:**
- ⚠️ Load testing (concurrent workflows)
- ⚠️ Performance benchmarks
- ⚠️ Production readiness checklist

📂 **[Full Documentation](temporal-implementation/)**

---

### 2. Multi-Database Schema Overhaul

**Status:** ✅ **Phase 2 Complete** (33% overall) | **Priority:** Critical | **Timeline:** 2-3 weeks (12 days remaining)

Complete redesign of database schemas following research-backed best practices with deep Graphiti integration for temporal knowledge graphs.

**What's Complete (Phase 2):**
- ✅ Neo4j migration system (Alembic-style, 560 lines)
- ✅ PostgreSQL optimizations (HNSW indexes, GIN indices, 40-100x speedup)
- ✅ Qdrant formalization (INT8 quantization, 75% memory reduction)
- ✅ 43 tests passing (100%)

**Next Phase (Phase 3 - Multi-DB Coordination):**
- ⚠️ UUID v7 standardization
- ⚠️ ID mapping table
- ⚠️ Enhanced saga pattern with compensation
- ⚠️ TTL-based caching (>70% hit rate target)

📂 **[Full Documentation](schema-overhaul/)**

---

### 3. Graphiti Domain Configuration

**Status:** ✅ **50% COMPLETE** - Foundation Built | **Priority:** Medium | **Timeline:** 1-2 days remaining

Enhance domain-specific entity extraction for trucking/logistics with additional entity types and validation framework.

**Foundation Complete (Built in Temporal Implementation):**
- ✅ 5 Entity Schemas (88,467 bytes)
- ✅ 177 Tier 2 properties, 67 LLM-extractable fields
- ✅ Helper module (`entity_schema_helpers.py`)
- ✅ Hub-based organization (6 rigid hubs, 45 entity types)

**Remaining Enhancement:**
- ⚠️ 5 more entity types (Vehicle, PartsInvoice, Vendor, BankTransaction, MaintenanceRecord)
- ⚠️ Custom extraction prompt
- ⚠️ 8 relationship types
- ⚠️ Validation framework (10 test documents, 90%+ accuracy)

📂 **[Full Documentation](graphiti-domain-configuration/)**

---

### 4. Conversational Memory Integration ⭐ NEW

**Status:** 🟢 **Architecture Finalized** - Ready for Implementation | **Priority:** P0 - Critical | **Timeline:** 6-8 weeks

Transform Apex into true AI agent brain by enabling automatic conversation → knowledge graph ingestion.

**The Problem:**
- Conversations stored in PostgreSQL but NOT extracted into knowledge graph
- System can't learn from user interactions or agent collaborations
- Missing 70% of potential knowledge (document ingestion works, conversation ingestion doesn't)

**The Solution:**
- ✅ **Architecture finalized** (Slack + NATS + PostgreSQL + Redis + Neo4j/Graphiti)
- ✅ **3 core paths:** Human↔Agent (70%), Agent↔Agent (30%), Redis caching
- ✅ **5-tier degradation:** Filter, score, decay, archive, consolidate
- ✅ **Realistic performance targets:** 2-3s Slack, <20ms NATS, 10-20s background
- ✅ **Migration path:** PostgreSQL → Event Sourcing (when ready)

**Implementation Phases (6-8 weeks):**
- Week 1: Research & Documentation (ADRs, schemas, IMPLEMENTATION.md)
- Week 2-3: Core Feedback Loop + Redis (automatic ingestion, caching)
- Week 3-4: Memory Quality (importance scoring, archival, consolidation)
- Week 5-6: Agent↔Agent Communication (NATS integration)
- Week 7: Proactive Features (suggestions, patterns, communities)
- Week 8: Comprehensive Testing (156 Enhanced Saga baseline + 70 new tests)

**Key Benefits:**
- Agents learn from every conversation automatically
- 60% latency reduction (Redis caching)
- 5x cost savings (LLM deduplication)
- 80% storage reduction (5-tier degradation)
- <$0.05 per conversation (including LLM costs)

📂 **[Full Documentation](conversational-memory-integration/)**

---

## Development Workflow

**Active projects follow this cycle:**

1. **Implementation** - Code changes, new features
2. **Testing** - Validation against success criteria
3. **Iteration** - Refine based on test results
4. **Documentation** - Update READMEs, ADRs, guides
5. **Deployment** - Merge to main codebase when stable

**Moving between stages:**
- `planned/` → `active/` - After Phase 3 Review Board approval
- `active/` → `completed/` - After successful deployment and validation
- `active/` → `planned/` - If project needs additional research

---

## Adding a New Active Project

When moving a project from `planned/` to `active/`:

1. **Ensure prerequisites:**
   - ✅ Research complete
   - ✅ PRP.md (Project Requirements & Planning) written
   - ✅ Review Board approved (if required)
   - ✅ Success criteria defined

2. **Move directory:**
   ```bash
   mv upgrades/planned/project-name upgrades/active/
   ```

3. **Update this README:**
   - Add project to "Current Active Projects" section
   - Include status, priority, timeline
   - Link to project directory

4. **Begin implementation:**
   - Create implementation branches
   - Track progress with todos
   - Run tests regularly

---

## Project Structure Template

Each active project should maintain:

```
project-name/
├── README.md              # Project overview, status, goals
├── PRP.md                 # Project Requirements & Planning
├── IMPLEMENTATION.md      # Implementation notes, decisions
├── research/              # Supporting research (if applicable)
├── scripts/               # Training scripts, utilities
└── tests/                 # Project-specific tests
```

---

## Cross-References

**Related Documentation:**
- [Upgrades Overview](../README.md) - Complete upgrade tracking system
- [Planned Upgrades](../planned/README.md) - Projects in research phase (Fine-Tuned Embeddings, API Connections)
- [Completed Upgrades](../completed/README.md) - Archived projects (Query Router, Documentation System, Cross-Reference System)

**Research Foundation:**
- [Query Routing Research](../../research/documentation/query-routing/) - 11 research documents (Semantic Router, GraphRAG, Query Rewriting, Agentic RAG, Adaptive Learning)
- [Sentence Transformers](../../research/documentation/sentence-transformers/) - Fine-tuning framework documentation
- [Architecture Decisions](../../research/architecture-decisions/) - ADRs for key architectural decisions
  - [ADR-002: Saga Pattern](../../research/architecture-decisions/ADR-002-saga-pattern-distributed-writes.md) - Distributed transaction management

**Testing & Validation:**
- [Test Framework](../../tests/) - Comprehensive testing infrastructure
  - [Difficulty-Stratified Test Suite](../../tests/test-suites/difficulty-stratified-250-queries.json) - 250 queries across 3 difficulty tiers
  - [Test Runner](../../tests/analysis/difficulty_stratified_test.py) - Main test execution script
  - [Confusion Matrix](../../tests/analysis/confusion_matrix.txt) - Intent classification error analysis
  - [Historical Results](../../tests/results/stratified/) - Test execution results over time

**Training Data & Configuration:**
- [Training Queries v7](../../apex-memory-system/config/training-queries-v7.json) - Logistics-specialized dataset (314 queries)
  - 80 route definitions (mixed difficulty)
  - 234 training queries (OpenHaul/Origin Transport specialized)
  - Closes semantic gap, enables fine-tuning

**Implementation References:**
- [Transaction Manager](../../apex-memory-system/src/apex_memory/services/transaction_manager.py) - Current saga pattern implementation
- [Semantic Classifier](../../apex-memory-system/src/apex_memory/query_router/semantic_classifier.py) - Query intent classification with semantic-router

**Project Interconnections:**
- **Temporal Workflow** ↔ **Saga Pattern** - Temporal replaces custom saga implementation
- All projects share: `tests/`, `research/documentation/`, and database infrastructure

---

*Last updated: 2025-11-06 (after directory reorganization)*
