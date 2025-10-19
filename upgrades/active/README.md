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

### 1. Temporal Workflow Orchestration

**Status:** 🚀 Active Development | **Priority:** High | **Timeline:** 6-8 weeks

Replace custom saga pattern with Temporal.io workflow orchestration for durable, reliable distributed transaction management.

**Expected Gains:**
- 99.9% workflow reliability (Temporal SLA)
- Automatic retries with exponential backoff
- Complete workflow visibility in Temporal UI
- Pause/resume/cancel long-running operations
- Zero custom compensation logic (built-in)

**Research Foundation:**
- [Temporal.io Python SDK](https://docs.temporal.io/develop/python) - Official documentation
- [Temporal Architecture](https://docs.temporal.io/concepts) - Core concepts
- [ARCHITECTURE-ANALYSIS-2025.md](../../ARCHITECTURE-ANALYSIS-2025.md) - Analysis of workflow orchestration benefits

**Implementation Phases:**
1. Week 1-2: Infrastructure setup (Temporal server, Python SDK, workers)
2. Week 3-4: Ingestion workflow migration (with gradual rollout 10% → 100%)
3. Week 5-6: Query workflow migration (including long-running query support)
4. Week 7-8: Monitoring, observability, and Prometheus metrics export

📂 **[Full Documentation](temporal-implementation/)**

---

### 2. OpenAI GPT-5 + graphiti-core 0.22.0 Upgrade

**Status:** 🔴 **CRITICAL - Active (Not Yet Started)** | **Priority:** High | **Timeline:** 3-4 days

Fix critical model name issue: Replace non-existent OpenAI models (`gpt-4.1-mini/nano`) with correct models (`gpt-5-mini/nano`) and upgrade graphiti-core to latest stable version.

**Current Impact:**
- ❌ Using non-existent model names in production code
- ❌ 1 test failing: `test_orphaned_episode_cleanup`
- ❌ False documentation claims about "GPT-4.1 being latest 2025 models"
- ❌ Version mismatch: requirements.txt (0.21.0) vs installed (0.20.4)

**Expected Gains:**
- ✅ 161/161 tests passing (currently 160/161)
- ✅ Correct OpenAI model names (verified via official docs)
- ✅ graphiti-core 0.22.0 with OpenTelemetry support
- ✅ Accurate documentation throughout codebase

**Research Foundation:**
- [OpenAI Platform - Models](https://platform.openai.com/docs/models) - Official model list (screenshot verified)
- [graphiti-core 0.22.0 Release](https://github.com/getzep/graphiti/releases) - Latest stable release
- 20+ files affected across codebase

**Implementation Phases:**
1. Day 1: Model name updates + graphiti-core upgrade
2. Day 2-3: Comprehensive testing (161 tests)
3. Day 3: Integration validation (real documents)
4. Day 3-4: Documentation updates

📂 **[Full Documentation](gpt5-graphiti-upgrade/)**

---

### 3. Saga Pattern Enhancement

**Status:** 📝 Planning | **Priority:** Medium | **Timeline:** TBD

Improve distributed transaction handling across multi-database writes using refined saga patterns.

**Goal:**
- Enhance rollback reliability
- Improve error recovery
- Add compensation logging
- Optimize parallel execution

📂 **[Full Documentation](saga-pattern-enhancement/)**

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

*Last updated: 2025-10-19*
