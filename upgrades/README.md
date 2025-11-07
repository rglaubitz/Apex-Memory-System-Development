# Upgrades & Improvement Plans

This directory tracks active and planned upgrades to the Apex Memory System, each backed by comprehensive research and phased implementation plans.

## Purpose

The `upgrades/` directory serves as:

1. **Planning Hub** - Detailed improvement plans with research citations
2. **Progress Tracking** - Implementation status and phase tracking
3. **Knowledge Base** - Research summaries and decision rationale
4. **Reference Archive** - Historical upgrades and lessons learned

## Structure

```
upgrades/
├── README.md              # This file
├── active/                # Active upgrades (implementation)
│   ├── README.md         # Active upgrades index
│   ├── temporal-implementation/    # 🚀 Active: Workflow orchestration
│   └── query-router-enhancement/   # 📝 Planned: search_memory routing fix
├── planned/               # Planned upgrades (research phase)
│   ├── README.md         # Planned upgrades index
│   ├── fine-tuned-embeddings/     # 📝 Planning (domain-specific embeddings)
│   └── api-connections/            # 📝 Planning (FrontApp integration)
├── completed/             # Completed upgrades (historical)
│   ├── README.md         # Completed upgrades index
│   ├── query-router/              # ✅ Oct 2025
│   ├── documentation-system/      # ✅ Oct 2025
│   └── cross-reference-system/    # ✅ Oct 2025
└── [future-upgrade]/      # Template for new upgrades
    ├── README.md
    └── IMPROVEMENT-PLAN.md
```

## Active Upgrades

### Temporal Workflow Orchestration

**Status:** 🚀 Active Implementation
**Priority:** High
**Timeline:** 6-8 weeks (4 phases)
**Research Progress:** 40% (architecture analysis complete)

**Location:** [`active/temporal-implementation/`](active/temporal-implementation/)

**TL;DR:**
Replace custom saga pattern with Temporal.io workflow orchestration for durable, reliable distributed transaction management with automatic retries, compensation, and complete observability.

**Expected Gains:**
- ✅ 99.9% workflow reliability (Temporal SLA)
- ✅ Automatic retries with exponential backoff
- ✅ Complete workflow visibility in Temporal UI
- ✅ Pause/resume/cancel long-running operations
- ✅ Zero custom compensation logic (built-in)

**Research Foundation:**
- [Temporal.io Python SDK](https://docs.temporal.io/develop/python) - Official documentation
- [Temporal Architecture](https://docs.temporal.io/concepts) - Core concepts
- [ARCHITECTURE-ANALYSIS-2025.md](ARCHITECTURE-ANALYSIS-2025.md) - Analysis of workflow orchestration benefits

**Implementation Phases:**
1. **Week 1-2:** Infrastructure setup (Temporal server, Python SDK, workers)
2. **Week 3-4:** Ingestion workflow migration (with gradual rollout 10% → 100%)
3. **Week 5-6:** Query workflow migration (including long-running query support)
4. **Week 7-8:** Monitoring, observability, and Prometheus metrics export

📋 **[Full Plan](active/temporal-implementation/README.md)**

---

### Query Router Enhancement - search_memory Routing Improvement

**Status:** 📝 Planned (not blocking PyPI deployment)
**Priority:** Medium
**Timeline:** 2 hours (1 hour pattern detection + 1 hour dedicated endpoint)
**Created:** 2025-10-24

**Location:** [`active/query-router-enhancement/`](active/query-router-enhancement/)

**TL;DR:**
Fix MCP `search_memory()` tool routing to graph databases instead of PostgreSQL document storage. Add pattern-based query detection and dedicated `/api/v1/memory/search` endpoint.

**Problem:**
- Current: `search_memory("What do you know about X?")` → metadata (PostgreSQL) → old documents ❌
- Expected: `search_memory("What do you know about X?")` → graph (Neo4j/Graphiti) → recent memories ✅

**Solution (2-phase hybrid approach):**
1. **Phase 1 (1 hour):** Add MEMORY_PATTERNS regex detection before hybrid classifier
2. **Phase 2 (1 hour):** Create dedicated `/memory/search` endpoint that always routes to graph

**Expected Gains:**
- ✅ Correct routing for memory queries ("What do you know about X?")
- ✅ Backward compatibility (document search unchanged)
- ✅ No performance impact (<10ms pattern matching overhead)
- ✅ Clean API semantics (documents vs memories)

**Research Foundation:**
- [PHASE-2-FIX-SUMMARY.md](../apex-mcp-server/PHASE-2-FIX-SUMMARY.md) - Root cause analysis
- [PHASE-2-TESTING-RESULTS.md](../apex-mcp-server/PHASE-2-TESTING-RESULTS.md) - Testing evidence

**Workaround (Immediate):**
Use `temporal_search()` instead of `search_memory()` for recent memory queries.

📋 **[Full Plan](active/query-router-enhancement/README.md)** | 📝 **[Implementation Guide](active/query-router-enhancement/IMPLEMENTATION.md)** | 🧪 **[Testing Specs](active/query-router-enhancement/TESTING.md)**

---

## Completed Upgrades ✅

### Domain Configuration (November 2025)

**Completed:** 2025-11-07
**Impact:** ⭐⭐⭐⭐ Major Enhancement - Business-Context Entity Extraction
**Timeline:** 4 phases (completed in 1 day with research foundation)

**Achievement:** Complete Domain Configuration system for business-context customization of knowledge graph entity extraction with logistics-domain specialization.

**Results:**
- ✅ **85-90% accuracy** with logistics domain (vs 75-80% unified schemas)
- ✅ **46 entity types** + 30 edge types for freight logistics
- ✅ **13 few-shot examples** across 5 categories (truck, load, invoice, carrier, network)
- ✅ **7 validation rules** catching 70-80% of data quality issues
- ✅ **88 tests** passing (27 + 23 + 38 unit tests, 8 integration tests)
- ✅ **End-to-end integration** API → Workflow → Activity → GraphitiService
- ✅ **Zero breaking changes** (optional parameter, graceful fallback)

**Key Deliverables:**
- **Phase 1 - Foundation:** `domain_config.py`, `logistics_domain.py`, `logistics_glossary.py` (1,110 lines)
- **Phase 2 - Few-Shot Examples:** `logistics_examples.py` with 13 comprehensive examples (328 lines)
- **Phase 3 - Validation:** `logistics_rules.py` with 7 critical validation rules (507 lines)
- **Phase 4 - Integration:** API + Workflow + Activity modifications (135 lines across 3 files)

**Technical Highlights:**
- Optional domain parameter at all levels (backward compatible)
- Graceful fallback to unified schemas on errors
- Domain loading in activity layer (keeps Temporal payloads small)
- Three-tier validation severity (ERROR/WARNING/INFO)
- Extensible design for adding new domains

**API Usage:**
```bash
# Domain-specific extraction (logistics)
POST /ingest?domain_name=logistics

# Standard extraction (unified schemas)
POST /ingest
```

📂 **[Full Documentation](completed/domain-configuration/)**

---

### Temporal Implementation (November 2025)

**Completed:** 2025-11-06
**Impact:** ⭐⭐⭐⭐⭐ Critical Infrastructure - Production Workflow Orchestration
**Timeline:** 11 sections (7 weeks as planned)

**Achievement:** Complete Temporal.io workflow orchestration replacing custom saga patterns with enterprise-grade reliability, 6-layer monitoring, and production-ready documentation.

**Results:**
- ✅ **99.9%+ reliability** with automatic retries and compensation
- ✅ **94 tests** passing (integration, unit, load tests)
- ✅ **6-layer monitoring** (workflow, activity, data quality, infrastructure, business, logs)
- ✅ **7 Grafana dashboards** including 33-panel primary dashboard
- ✅ **12 Prometheus alerts** (critical + warning)
- ✅ **Production guides** (12,000+ words deployment guide, 10,000+ words runbook)
- ✅ **12 operational scripts** for debugging and validation
- ✅ **Enhanced Saga pattern** (121 baseline tests preserved at 100%)

**Key Deliverables:**
- **Workflow Orchestration:** DocumentIngestionWorkflow + StructuredDataIngestionWorkflow
- **27 Temporal Metrics:** Across 6 layers (workflow, activity, data quality, infrastructure, business, logs)
- **Monitoring Stack:** 7 dashboards (temporal-ingestion.json with 33 panels), 12 alerts (rules.yml 19KB)
- **Operational Tools:** 12 scripts including validate-deployment.py (17KB), benchmark-ingestion.py (13KB)
- **Documentation:** PRODUCTION-DEPLOYMENT-GUIDE.md (12K words), PRODUCTION-RUNBOOK.md (10K words)

**Technical Highlights:**
- Temporal SDK 1.5.0+ integration
- Worker concurrency: 100 workflows, 50 activities per worker
- Multi-DB saga pattern (Neo4j, PostgreSQL, Qdrant, Redis)
- Throughput: 10+ docs/sec, <5s average latency
- Complete observability via Temporal UI

📂 **[Full Documentation](completed/temporal-implementation/)**

---

### Graphiti + JSON Integration (November 2025)

**Completed:** 2025-11-06
**Impact:** ⭐⭐⭐⭐⭐ Critical Architecture Enhancement
**Timeline:** 4 weeks + bonus Phase 5 (as planned)

**Achievement:** Complete LLM-powered entity extraction, structured data ingestion, local staging infrastructure, and dual workflow architecture delivering 90%+ entity extraction accuracy.

**Results:**
- ✅ **90%+ accuracy** entity extraction (vs 60% regex baseline)
- ✅ **All 46 entities** wired into Graphiti dynamically
- ✅ **Local staging** production-ready at `/tmp/apex-staging/`
- ✅ **Dual workflows** (DocumentIngestion + StructuredDataIngestion)
- ✅ **BONUS Phase 5** perfect workflow separation
- ✅ **35+ tests** created (100% pass rate)
- ✅ **Zero breaking changes** (feature flag enabled)

**Key Deliverables:**
- **Graphiti Integration:** 1,194-line GraphitiService with 18 methods
- **JSON Support:** StructuredData models + PostgreSQL JSONB storage
- **Local Staging:** Complete StagingManager with TTL cleanup (9 tests)
- **Workflow Separation:** Dedicated modules for document vs JSON paths
- **Test Coverage:** 5 test files (60+ KB total)

**Technical Highlights:**
- Auto-configuration via `use_unified_schemas=True`
- 24 entities/sec (all 46), 346 entities/sec (selective)
- Feature flag: `ENABLE_GRAPHITI_EXTRACTION`
- Complete handoff documentation for continuation

📂 **[Full Documentation](completed/graphiti-json-integration/)**

---

### Phase 2: Schema Overhaul (November 2025)

**Completed:** 2025-11-01
**Impact:** ⭐⭐⭐⭐⭐ Critical Infrastructure Upgrade
**Timeline:** 8 days (as planned)

**Achievement:** Comprehensive schema optimization across 3 databases (Neo4j, PostgreSQL, Qdrant) with production-ready migration scripts, comprehensive testing, and verified performance improvements.

**Results:**
- ✅ **40-100x** vector search speedup (IVFFlat → HNSW)
- ✅ **75%** memory reduction (INT8 quantization verified)
- ✅ **50x** JSONB query speedup (GIN indices)
- ✅ **3 databases** optimized (Neo4j, PostgreSQL, Qdrant)
- ✅ **43 unit tests** (100% pass rate)
- ✅ **Zero-downtime** migration patterns implemented

**Key Deliverables:**
- **Neo4j:** Custom migration framework (560 lines) + version tracking system
- **PostgreSQL:** HNSW indices + GIN indices + structured_data.embedding column (254 lines)
- **Qdrant:** Collection creation + batch migration scripts (1,020 lines)
- **Tests:** Comprehensive unit test suite (43 tests, 100% pass rate)
- **Documentation:** Complete phase summary (2,500+ lines)

**Database Improvements:**

| Database | Optimization | Impact |
|----------|-------------|---------|
| **Neo4j** | Alembic-style migrations | Version tracking + rollback support |
| **PostgreSQL** | HNSW + GIN indices | 40-100x vector, 50x JSONB speedup |
| **Qdrant** | INT8 quantization | 75% memory savings |

**Technical Highlights:**
- Matching HNSW parameters across databases (m=16, ef_construct=64)
- Production-ready batch migration (1,000+ points/second)
- Comprehensive error handling with retry logic
- Idempotent operations for safe re-runs

📂 **[Full Documentation](../PHASE-2-SCHEMA-OVERHAUL-COMPLETE.md)**

---

### Query Router Improvement Plan (October 2025)

**Completed:** 2025-10-16
**Impact:** ⭐⭐⭐⭐⭐ Major System Enhancement

**Achievement:** Comprehensive upgrade bringing Apex query routing to 2025 standards with semantic classification, adaptive learning, and intelligent routing.

**Results:**
- ✅ Implemented Semantic Router for 10ms intent classification
- ✅ Query rewriting system based on Microsoft research
- ✅ Adaptive routing with learned weights
- ✅ GraphRAG hybrid search integration
- ✅ 90%+ cache hit rate with semantic caching
- ✅ Complete deployment guide and monitoring

**Key Deliverables:**
- Semantic classification layer
- Query rewriting engine
- Adaptive weight learning
- Comprehensive test suite (250+ queries)
- Production deployment guides
- Monitoring and observability

📂 **[Full Documentation](completed/query-router/)**

---

### Documentation System (October 2025)

**Completed:** 2025-10-07
**Impact:** ⭐⭐⭐⭐⭐ Critical Infrastructure

**Achievement:** Created comprehensive documentation system with 31 professional README files covering entire project structure.

**Results:**
- ✅ 31 READMEs created (from 0)
- ✅ 100% documentation coverage
- ✅ Professional GitHub landing page
- ✅ 34,000+ lines committed and organized
- ✅ Clear navigation and onboarding path

**Key Deliverables:**
- Root landing page with badges
- Agent system documentation (20 agents)
- Workflow phase documentation
- Research organization structure
- Upgrade tracking system

📂 **[Full Documentation](completed/documentation-system/)**

---

### Cross-Reference System (October 2025)

**Completed:** 2025-10-07
**Impact:** ⭐⭐⭐⭐⭐ Major Usability Improvement

**Achievement:** Enhanced documentation with comprehensive bidirectional cross-references creating complete knowledge graph.

**Results:**
- ✅ 385 insertions across 14 files
- ✅ Bidirectional navigation between all docs
- ✅ Query Router fully integrated with research
- ✅ 1-click access to related topics
- ✅ Complete knowledge network

**Key Features:**
- "Related Upgrades" sections in all framework docs
- Cross-references connecting research ↔ examples ↔ ADRs
- Updated directory structures (100% accurate)
- Query Router links from 11 different documents

📂 **[Full Documentation](completed/cross-reference-system/)**

---

## Planned Upgrades 📝

For detailed planning and research tracking, see **[`planned/`](planned/)** directory.

### Ingestion Pipeline v2

**Status:** 📝 Research Phase
**Priority:** Medium
**Timeline:** TBD
**Research Progress:** 0%

**Goal:** Improve document parsing quality, add multi-modal support, optimize parallel processing

**Key Improvements:**
- 95%+ format preservation (PDF, DOCX, PPTX)
- Multi-modal support (images, tables, diagrams)
- Consistent 10+ docs/second throughput
- 90%+ entity extraction accuracy

📂 **[Full Planning](planned/ingestion-pipeline-v2/)**

---

### Temporal Intelligence Enhancement

**Status:** 📝 Research Phase
**Priority:** Medium
**Timeline:** TBD
**Research Progress:** 0%

**Goal:** Enhance Graphiti integration, improve pattern detection, add time-series forecasting

**Key Features:**
- Pattern detection (recurring themes, trends)
- Community detection (GraphRAG approach)
- Time-series forecasting
- Query router integration

📂 **[Full Planning](planned/temporal-intelligence-enhancement/)**

---

### Multi-Modal RAG

**Status:** 📝 Research Phase
**Priority:** Low
**Timeline:** TBD
**Research Progress:** 0%

**Goal:** Support images, tables, audio in retrieval and generation

**Capabilities:**
- Image ingestion and search
- Table structure preservation
- Audio/video transcription
- Cross-modal retrieval (text → images)

📂 **[Full Planning](planned/multi-modal-rag/)**

---

## Upgrade Workflow

### 1. Research Phase

**Objective:** Gather high-quality research following source hierarchy

**Activities:**
- Use research team agents to find documentation
- Document findings in `research/documentation/`
- Collect code examples in `research/examples/`
- Track sources in `research/references.md`

**Quality Gate:** CIO validates research quality

### 2. Planning Phase

**Objective:** Create comprehensive improvement plan

**Activities:**
- Identify current flaws and gaps
- Propose phased implementation approach
- Define expected gains and metrics
- Reference research documents
- Create upgrade directory with README + IMPROVEMENT-PLAN.md

**Quality Gate:** Review Board (Phase 3.5) validates plan

### 3. Implementation Phase

**Objective:** Execute approved plan

**Activities:**
- Follow phased implementation
- Track progress with TodoWrite
- Update upgrade README with status
- Create ADRs for significant decisions

**Quality Gate:** COO validates execution feasibility

### 4. Testing Phase

**Objective:** Validate improvements against targets

**Activities:**
- Run benchmarks and performance tests
- Compare against expected gains
- Document actual results
- Create test reports

**Quality Gate:** CTO validates technical achievement

### 5. Completion Phase

**Objective:** Preserve knowledge for future reference

**Activities:**
- Move to `completed/` with completion date
- Document lessons learned
- Update metrics and benchmarks
- Create summary for future upgrades
- Add to completed upgrades index

---

## Creating New Upgrades

### Directory Structure

```
upgrades/[upgrade-name]/
├── README.md              # Quick reference (TL;DR)
├── IMPROVEMENT-PLAN.md    # Comprehensive plan
├── RESEARCH.md            # Research summary (optional)
├── PROGRESS.md            # Implementation tracking (optional)
└── RESULTS.md             # Post-implementation results (optional)
```

### README.md Template

```markdown
# [Upgrade Name]

**Status:** [Planning/Implementation/Testing/Complete]
**Priority:** [High/Medium/Low]
**Timeline:** [X weeks/months]

## TL;DR
[One paragraph summary]

## Expected Gains
- Metric 1: X% improvement
- Metric 2: Y reduction

## Research Foundation
- [Link to research doc 1]
- [Link to research doc 2]

## Implementation Phases
1. Phase 1: [Description]
2. Phase 2: [Description]

[Full Plan](IMPROVEMENT-PLAN.md)
```

### IMPROVEMENT-PLAN.md Template

```markdown
# [Upgrade Name] - Comprehensive Improvement Plan

## Executive Summary
[High-level overview]

## Current State Analysis
[Identify problems and gaps]

## Research Summary
[Reference research documents]

## Proposed Solution
[Detailed approach]

## Implementation Phases
### Phase 1: [Name] (Week X-Y)
[Detailed tasks and code examples]

### Phase 2: [Name] (Week Z-W)
[Detailed tasks and code examples]

## Expected Outcomes
[Metrics and benchmarks]

## Risk Mitigation
[Potential issues and solutions]

## References
[Research citations]
```

---

## Metrics Tracking

All upgrades should define and track:

1. **Performance Metrics**
   - Latency (P50, P90, P99)
   - Throughput
   - Resource utilization

2. **Quality Metrics**
   - Accuracy/Precision/Recall
   - Error rates
   - User satisfaction

3. **Business Metrics**
   - Cost reduction
   - Time saved
   - User adoption

4. **Technical Metrics**
   - Code coverage
   - Code quality scores
   - Test pass rate

---

## Quality Standards

All upgrades must adhere to:

- ✅ **Research-First Principle** - Backed by Tier 1-5 sources
- ✅ **Phased Implementation** - No "big bang" changes
- ✅ **Review Board Approval** - Phase 3.5 validation
- ✅ **Metrics-Driven** - Define success criteria upfront
- ✅ **Documented** - Comprehensive plans and progress tracking
- ✅ **Tested** - Benchmarks validate expected gains

---

## References

- **Research Directory:** `../research/`
- **ADRs:** `../research/architecture-decisions/`
- **Workflow:** `../workflow/README.md`
- **Review Board:** `.claude/agents/` (CIO, CTO, COO)

---

**Last Updated:** November 2025
**Completed Upgrades:** 5 (Temporal Implementation, Graphiti+JSON, Schema Overhaul, Query Router, Documentation System)
**Active Upgrades:** 2 (Schema Overhaul Entity Phase, Graphiti Domain Configuration)
**Planned Upgrades:** 2 (Fine-Tuned Embeddings, API Connections)
