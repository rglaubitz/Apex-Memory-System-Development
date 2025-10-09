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

### 1. Query Router Improvement Plan

**Status:** 🚀 Active Development | **Priority:** High | **Timeline:** 8 weeks

Comprehensive upgrade bringing Apex query routing to 2025 standards based on latest RAG research.

**Expected Gains:**
- +21-28 point relevance improvement (Microsoft benchmarks)
- 99% precision on relationship queries (GraphRAG)
- 90ms faster intent classification (Semantic Router)
- 15-30% accuracy improvement (adaptive learning)
- 90%+ cache hit rate (semantic caching)

**Research Foundation:**
- Semantic Router - 10ms intent classification
- Query Rewriting - Microsoft +21 point improvement
- Agentic RAG 2025 - Latest paradigm shift
- Adaptive Routing - Learned weights
- GraphRAG - 99% precision hybrid search

**Implementation Phases:**
1. Week 1-2: Foundation (semantic classification, query rewriting, analytics)
2. Week 3-4: Intelligent routing (adaptive weights, GraphRAG, semantic caching)
3. Week 5-6: Agentic evolution (complexity analysis, multi-router, self-correction)
4. Week 7-8: Advanced features (multimodal, real-time adaptation)

📂 **[Full Documentation](query-router/)**

---

### 2. Fine-Tuned Embeddings for Logistics

**Status:** 🚀 Just Started | **Priority:** High | **Timeline:** 1 week

Domain-specific embedding model fine-tuned for freight logistics and query routing on M4 hardware.

**Problem:**
- Generic OpenAI embeddings don't understand freight terminology
- Graph routes collapse on ambiguous queries (43.8% accuracy on medium tier)
- Semantic gap between route definitions and training queries
- Ultra-low learned thresholds cause false positives

**Solution:**
- Fine-tune BAAI/bge-base-en-v1.5 on logistics-specific queries
- Use M4 Neural Engine for fast training (5-10 min)
- Specialize for OpenHaul and Origin Transport business domains
- Close semantic gap at embedding level

**Expected Gains:**
- Medium tier: 67.8% → 85%+ (+17 points)
- Hard tier: 60.0% → 75%+ (+15 points)
- Graph intent: 66.0% → 80%+ (+14 points)
- Overall: 77.9% → 85-90% (+7-12 points)

**M4 Advantage:**
- Only way to fine-tune embeddings (OpenAI doesn't offer this)
- 16-core Neural Engine (38 TOPS)
- Fast iteration cycles (10 minutes per training run)

📂 **[Full Documentation](fine-tuned-embeddings/)**

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
- [Planned Upgrades](../planned/README.md) - Projects in research phase
- [Completed Upgrades](../completed/README.md) - Archived projects

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
- **Query Router** ↔ **Fine-Tuned Embeddings** - Fine-tuned embeddings improve semantic classification accuracy
- **Query Router** ↔ **Saga Pattern** - Consistent data writes enable reliable query routing
- All projects share: `tests/`, `research/documentation/`, and `apex-memory-system/config/training-queries-v7.json`

---

*Last updated: 2025-10-09*
