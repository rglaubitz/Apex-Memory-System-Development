# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## ⚠️ IMPORTANT RULES - MUST ALWAYS FOLLOW

**These rules are critical and must be followed in every session:**

### Rule 1: Read Key Structural READMEs First

**BEFORE beginning any work with the user**, you MUST read these key structural files:

- `README.md` (root)
- `CLAUDE.md` (project-local, this file)
- `upgrades/README.md`
- `research/README.md`
- `workflow/README.md`
- `upgrades/completed/README.md` (if working with completed upgrades)
- `upgrades/planned/README.md` (if working with planned upgrades)
- `upgrades/active/temporal-implementation/tests/STRUCTURE.md` (if working with Temporal testing)

**Purpose:** Understand project structure, current state, upgrade lifecycle, and test organization before making any changes.

### Rule 2: Read Framework-Specific READMEs Before Implementation

**BEFORE executing any implementation task from a plan**, you MUST read the applicable framework-specific documentation:

**Examples:**
- Implementing Neo4j features → Read `research/documentation/neo4j/README.md`
- Working with PostgreSQL/pgvector → Read `research/documentation/postgresql/README.md` and `research/documentation/pgvector/README.md`
- Query routing implementation → Read `research/documentation/query-routing/README.md`
- Qdrant integration → Read `research/documentation/qdrant/README.md`
- Graphiti temporal features → Read `research/documentation/graphiti/README.md`
- FastAPI endpoints → Read `research/documentation/fastapi/README.md`

**Purpose:** Ensure implementation follows research-backed best practices and uses documented patterns.

**⚠️ DO NOT skip these reads to save tokens. Research-first principles require you to be informed before implementing.**

---

## Project Overview

**Apex Memory System Development** is a research-driven development wrapper for the Apex Memory System project. This directory provides:

- **Research organization** following research-first principles
- **Workflow management** for phased development (Vision → Mission → Execution → Implementation → Testing)
- **Symlinked codebase** at `apex-memory-system/` (actual implementation)

**The main codebase is located at:** `apex-memory-system/` (symlink to `/Users/richardglaubitz/Projects/apex-memory-system`)

## Directory Structure

```
Apex-Memory-System-Development/
├── apex-memory-system/        # Symlink to actual codebase (see apex-memory-system/CLAUDE.md)
│   ├── src/apex_memory/
│   │   ├── api/
│   │   │   └── ingestion.py   # ✅ Temporal-integrated API (Section 9)
│   │   ├── monitoring/
│   │   │   └── metrics.py     # ✅ 27 Temporal metrics (Section 9)
│   │   ├── temporal/          # ✅ Temporal.io integration
│   │   │   ├── activities/
│   │   │   │   └── ingestion.py   # ✅ 5 instrumented activities
│   │   │   ├── workflows/
│   │   │   │   └── ingestion.py   # ✅ DocumentIngestionWorkflow
│   │   │   └── workers/
│   │   │       └── dev_worker.py  # Worker implementation
│   │   └── services/          # Legacy services (still used by activities)
│   ├── monitoring/
│   │   ├── dashboards/
│   │   │   └── temporal-ingestion.json  # ✅ 33-panel dashboard (Section 9)
│   │   └── alerts/
│   │       └── rules.yml      # ✅ 12 Temporal alerts (Section 9)
│   └── scripts/
│       └── temporal/          # ✅ Debugging scripts (Section 9)
│           ├── check-workflow-status.py
│           ├── list-failed-workflows.py
│           ├── compare-metrics.py
│           └── worker-health-check.sh
│
├── research/                  # Research-first organized documentation
│   ├── documentation/         # Official docs (Tier 1 sources)
│   │   ├── query-routing/    # Query routing research (Oct 2025)
│   │   └── temporal/         # Temporal.io research
│   ├── examples/              # Verified code samples (Tier 2 sources)
│   └── architecture-decisions/ # ADRs with research citations
│
├── upgrades/                  # Upgrade tracking system
│   ├── active/
│   │   └── temporal-implementation/  # 🚀 ACTIVE: Sections 1-9 complete (82%)
│   │       ├── PROJECT-STATUS-SNAPSHOT.md      # ⭐ Current project state
│   │       ├── SECTION-9-COMPLETE.md           # ⭐ Section 9 summary
│   │       ├── SECTION-9-IMPLEMENTATION-COMPLETE.md
│   │       ├── HANDOFF-SECTION-9.md
│   │       ├── EXECUTION-ROADMAP.md            # ⭐ Overall plan
│   │       ├── research/                       # RDF documentation
│   │       ├── tests/                          # ⭐ Test artifacts (organized by phase)
│   │       │   ├── STRUCTURE.md               # Complete test organization guide
│   │       │   ├── Phase Tests (Section 11)
│   │       │   │   ├── phase-1-validation/    # ✅ Pre-testing validation (5 fixes)
│   │       │   │   ├── phase-2a-integration/  # ✅ Integration tests (13 fixes, 1/6 tests)
│   │       │   │   ├── phase-2b-saga-baseline/ # Enhanced Saga baseline (121 tests)
│   │       │   │   ├── phase-2c-load-mocked/  # Load tests - mocked DBs (5 tests)
│   │       │   │   ├── phase-2d-load-real/    # Load tests - real DBs (5 tests)
│   │       │   │   ├── phase-2e-metrics/      # Metrics validation (8 tests)
│   │       │   │   └── phase-2f-alerts/       # Alert validation (13 tests)
│   │       │   └── Section Tests (Development)
│   │       │       ├── section-1-preflight/      # ✅ 1 test
│   │       │       ├── section-2-infrastructure/ # ✅ 1 test
│   │       │       ├── section-3-config/         # ✅ 1 test
│   │       │       ├── section-4-worker/         # ✅ 4 tests
│   │       │       ├── section-5-hello-world/    # ✅ 3 tests
│   │       │       ├── section-6-monitoring/     # No tests
│   │       │       ├── section-7-ingestion-activities/ # ✅ 19 tests
│   │       │       └── section-8-ingestion-workflow/   # ✅ 15 tests
│   │       └── examples/                       # Working examples
│   ├── planned/               # Planned upgrades (research phase)
│   └── completed/             # Completed upgrades (archive)
│
├── workflow/                  # Workflow management (phases, approvals)
└── .claude/                   # Claude Code configuration
    ├── agents/                # Custom agent definitions (20 agents)
    └── settings.local.json    # Local settings
```

## 🎯 Quick Reference: Temporal Implementation (Current Work)

**Currently Active:** Section 9 just completed! Review these key documents:

### Essential Documentation (Start Here)

1. **[PROJECT-STATUS-SNAPSHOT.md](upgrades/active/temporal-implementation/PROJECT-STATUS-SNAPSHOT.md)**
   - Complete macro view of project
   - Current status: 82% complete (Sections 1-9 done)
   - All 27 metrics documented
   - Test coverage: 162/162 passing
   - Next steps clearly outlined

2. **[SECTION-9-COMPLETE.md](upgrades/active/temporal-implementation/SECTION-9-COMPLETE.md)**
   - Detailed Section 9 implementation summary
   - 6-layer monitoring architecture
   - All deliverables with code examples
   - Success metrics and achievements
   - Handoff to Section 10

3. **[EXECUTION-ROADMAP.md](upgrades/active/temporal-implementation/EXECUTION-ROADMAP.md)**
   - Overall 11-section implementation plan
   - Phase-by-phase breakdown
   - Timeline and dependencies
   - Testing strategy

### Implementation Artifacts

**Code Locations:**
- **Metrics:** `apex-memory-system/src/apex_memory/monitoring/metrics.py` (27 metrics)
- **Activities:** `apex-memory-system/src/apex_memory/temporal/activities/ingestion.py` (5 instrumented)
- **Workflow:** `apex-memory-system/src/apex_memory/temporal/workflows/ingestion.py`
- **API:** `apex-memory-system/src/apex_memory/api/ingestion.py` (Temporal-integrated)
- **Dashboard:** `apex-memory-system/monitoring/dashboards/temporal-ingestion.json` (33 panels)
- **Alerts:** `apex-memory-system/monitoring/alerts/rules.yml` (12 alerts)

**Scripts:**
- `apex-memory-system/scripts/temporal/check-workflow-status.py`
- `apex-memory-system/scripts/temporal/list-failed-workflows.py`
- `apex-memory-system/scripts/temporal/compare-metrics.py`
- `apex-memory-system/scripts/temporal/worker-health-check.sh`

**Test Artifacts:**

⭐ **For complete test organization, see:** `upgrades/active/temporal-implementation/tests/STRUCTURE.md`

**Section 11 Testing (Phase-Based):**
- `tests/phase-1-validation/` - Pre-testing validation (5 critical fixes documented)
- `tests/phase-2a-integration/` - Integration tests (13 critical fixes, 1/6 tests passing)
- `tests/phase-2b-saga-baseline/` - Enhanced Saga baseline verification (121 tests)
- `tests/phase-2c-load-mocked/` - Load tests with mocked DBs (5 tests)
- `tests/phase-2d-load-real/` - Load tests with real DBs (5 tests)
- `tests/phase-2e-metrics/` - Metrics validation (8 tests)
- `tests/phase-2f-alerts/` - Alert validation (13 tests)

**Development Tests (Section-Based):**
- `tests/section-1-preflight/` through `tests/section-8-ingestion-workflow/` (41 tests total)

**Each phase folder contains:**
- `INDEX.md` - Phase overview and achievements
- `PHASE-X-FIXES.md` - Detailed fix documentation (fix-and-document workflow)
- Test files and execution results

### Monitoring Endpoints

- **Grafana Dashboard:** http://localhost:3001/d/temporal-ingestion
- **Temporal UI:** http://localhost:8088
- **Prometheus:** http://localhost:9090
- **API Docs:** http://localhost:8000/docs

---

## Working with This Repository

### Research-First Principle

**All architectural decisions must be grounded in high-quality research:**

1. **Source Hierarchy (highest to lowest priority):**
   - Official Documentation (Anthropic, Neo4j, PostgreSQL, Qdrant, Redis, Graphiti)
   - Verified GitHub Repositories (1.5k+ stars minimum)
   - Technical Standards (RFCs, W3C specs)
   - Verified Technical Sources
   - Package Registries (PyPI, npm)

2. **Research Quality Standards:**
   - Documentation must be current (<2 years old OR explicitly verified)
   - GitHub examples must demonstrate the pattern being researched
   - All sources must include citations with URLs
   - Breaking changes and deprecations must be noted

### Research Organization

**Before implementing features:**

1. Check `research/documentation/` for official guidance
2. Review `research/examples/` for proven patterns
3. Document decisions in `research/architecture-decisions/` as ADRs
4. Reference sources in implementation decisions

**Adding Research:**

```bash
# Official documentation
research/documentation/[framework-name]/[doc-name].md

# Verified examples
research/examples/[pattern-name]/[example-name].md

# Architecture decisions
research/architecture-decisions/ADR-NNN-[title].md
```

## Development Commands

### Working with the Main Codebase

**All development commands run in the symlinked directory:**

```bash
# Navigate to main codebase
cd apex-memory-system

# See full development commands in:
# apex-memory-system/CLAUDE.md
```

### Quick Reference (from apex-memory-system/)

```bash
# Start all services
cd docker && docker-compose up -d

# Run tests
pytest                           # All tests with coverage
pytest tests/unit/ -v            # Unit tests only
pytest tests/integration/ -v     # Integration tests

# Code quality
black src/ tests/                # Format
isort src/ tests/                # Sort imports
flake8 src/ tests/ --max-line-length=100  # Lint
mypy src/                        # Type check

# Start API
python -m uvicorn apex_memory.main:app --reload --port 8000
# API docs: http://localhost:8000/docs
```

## Testing Organization

### Test Structure

All test artifacts are organized under `upgrades/active/temporal-implementation/tests/` with two categories:

**1. Section Tests (Development-Time)**
- Created during feature implementation (Sections 1-8)
- Validate individual components as they're built
- 41 tests total (all passing)
- Located in: `tests/section-*/`

**2. Phase Tests (Production Validation)**
- Created for Section 11 comprehensive testing
- Validate production readiness before deployment
- 194 tests total across 6 phases
- Located in: `tests/phase-*/`

**Complete organization guide:** `tests/STRUCTURE.md`

### Fix-and-Document Workflow

All Phase 2 testing follows this workflow for any test failures:

**1. Document Problem** - Capture error, stack trace, environment context
**2. Root Cause Analysis** - Identify underlying issue (not just symptoms)
**3. Apply Fix** - Implement solution (production code or test code)
**4. Validate Fix** - Confirm test now passes end-to-end
**5. Document Outcome**:
   - What went good (successful aspects of fix)
   - What went bad (challenges, multiple attempts needed)
   - Production impact (was production code affected?)
   - Future considerations

**Documentation Location:** Each phase folder contains `PHASE-X-FIXES.md` with comprehensive fix documentation.

**Example:** Phase 2A documented 13 critical fixes (5 production code, 8 test code) including:
- Temporal SDK API migration (affected production workflow)
- Database configuration for local development
- Test fixture quality improvements

### Running Tests

**Section-specific tests:**
```bash
cd upgrades/active/temporal-implementation/tests/section-X/
./RUN_TESTS.sh
```

**Integration test suite:**
```bash
cd apex-memory-system
pytest tests/integration/test_temporal_ingestion_workflow.py -v -m integration
```

**Load tests:**
```bash
pytest tests/load/ -v -m load
```

**All Enhanced Saga tests (baseline validation):**
```bash
pytest tests/ -v --ignore=tests/load/
```

## Architecture Overview

**The Apex Memory System is a parallel multi-database intelligence platform:**

- **Neo4j** - Graph relationships and entity connections
- **Graphiti** - Temporal reasoning and pattern detection
- **PostgreSQL + pgvector** - Metadata search and hybrid semantic queries
- **Qdrant** - High-performance vector similarity search
- **Redis** - Cache layer for <100ms repeat queries

**Key Components:**

1. **Ingestion Pipeline** (`apex-memory-system/src/apex_memory/services/`)
   - Multi-format parsing (PDF, DOCX, PPTX, HTML, Markdown)
   - Entity extraction and embedding generation
   - Parallel writes to all databases with saga pattern

2. **Query Router** (`apex-memory-system/src/apex_memory/query_router/`)
   - Intent-based query classification
   - Optimal database routing
   - Result aggregation and caching

3. **Temporal Intelligence** (`apex-memory-system/src/apex_memory/temporal/`)
   - Bi-temporal versioning (valid time + transaction time)
   - Pattern detection and trend analysis
   - Graphiti integration for time-aware entity tracking

**For full architecture details, see:** `apex-memory-system/CLAUDE.md`

## Upgrade Tracking System

The `upgrades/` directory tracks the complete upgrade lifecycle with research-backed improvement plans.

**Current Status:** 2 completed ✅ | 1 active 🚀 (82% complete) | 3 planned 📝

---

### 🚀 Active Upgrade: Temporal.io Integration

**Status:** ✅ **Section 9 Complete** (82% overall progress)
**Timeline:** 11 sections total (Sections 1-9 done, 10-11 remaining)
**Priority:** Critical - Production Infrastructure

**Complete Temporal.io workflow orchestration for document ingestion with 6-layer monitoring.**

**Sections Completed (1-9):**
- ✅ Section 1-4: Foundation (Docker, CLI, Worker, Hello World)
- ✅ Section 5: Hello World Workflow (3 tests passing)
- ✅ Section 6: Worker Setup (4 tests passing)
- ✅ Section 7: Ingestion Activities (19 tests passing)
- ✅ Section 8: Document Ingestion Workflow (15 tests passing)
- ✅ **Section 9: Temporal Integration + Monitoring** (JUST COMPLETED)
  - 27 Temporal metrics across 6 layers
  - ALL 5 activities instrumented
  - 100% Temporal API integration
  - 33-panel Grafana dashboard
  - 12 critical alerts
  - 4 debugging scripts

**Key Achievements:**
- 100% Temporal integration (no legacy path)
- Complete observability (workflow → activity → data quality → infrastructure → business → logs)
- Silent failure detection (zero chunks/entities alerts)
- Production-ready monitoring and alerting
- 162 tests passing (Enhanced Saga preserved: 121/121)

**📂 Key Documentation:**
- ⭐ **[PROJECT-STATUS-SNAPSHOT.md](upgrades/active/temporal-implementation/PROJECT-STATUS-SNAPSHOT.md)** - Complete project state
- ⭐ **[SECTION-9-COMPLETE.md](upgrades/active/temporal-implementation/SECTION-9-COMPLETE.md)** - Section 9 detailed summary
- ⭐ **[EXECUTION-ROADMAP.md](upgrades/active/temporal-implementation/EXECUTION-ROADMAP.md)** - Overall implementation plan

**Remaining Sections (10-11):**
- Section 10: Ingestion Testing & Rollout Validation
- Section 11: Production Readiness & Documentation

**Modified Files (Section 9):**
- `apex-memory-system/src/apex_memory/monitoring/metrics.py` (+450 lines)
- `apex-memory-system/src/apex_memory/temporal/activities/ingestion.py` (+300 lines)
- `apex-memory-system/src/apex_memory/api/ingestion.py` (rewritten for Temporal)
- `apex-memory-system/monitoring/dashboards/temporal-ingestion.json` (NEW)
- `apex-memory-system/monitoring/alerts/rules.yml` (+12 alerts)
- `apex-memory-system/scripts/temporal/*.py` (4 new scripts)

---

### Completed Upgrades ✅

#### Documentation System (October 2025)

**Completed:** 2025-10-07
**Impact:** ⭐⭐⭐⭐⭐ Critical Infrastructure

Created comprehensive documentation system with 31 professional README files covering entire project structure.

**Results:**
- ✅ 31 READMEs created (from 0)
- ✅ 100% documentation coverage
- ✅ Professional GitHub landing page
- ✅ 34,000+ lines committed and organized

📂 **[Full Documentation](upgrades/completed/documentation-system/)**

---

#### Cross-Reference System (October 2025)

**Completed:** 2025-10-07
**Impact:** ⭐⭐⭐⭐⭐ Major Usability Improvement

Enhanced documentation with comprehensive bidirectional cross-references creating complete knowledge graph.

**Results:**
- ✅ 385 insertions across 14 files
- ✅ Bidirectional navigation between all docs
- ✅ Query Router fully integrated with research
- ✅ 1-click access to related topics

📂 **[Full Documentation](upgrades/completed/cross-reference-system/)**

---

### Planned Upgrades 📝

#### Ingestion Pipeline v2

**Priority:** Medium | **Research Progress:** 0%

**Goal:** Improve document parsing quality, add multi-modal support, optimize parallel processing

**Key Improvements:**
- 95%+ format preservation (PDF, DOCX, PPTX)
- Multi-modal support (images, tables, diagrams)
- Consistent 10+ docs/second throughput
- 90%+ entity extraction accuracy

📂 **[Full Planning](upgrades/planned/ingestion-pipeline-v2/)**

---

#### Temporal Intelligence Enhancement

**Priority:** Medium | **Research Progress:** 0%

**Goal:** Enhance Graphiti integration, improve pattern detection, add time-series forecasting

**Key Features:**
- Pattern detection (recurring themes, trends)
- Community detection (GraphRAG approach)
- Time-series forecasting
- Query router integration

📂 **[Full Planning](upgrades/planned/temporal-intelligence-enhancement/)**

---

#### Multi-Modal RAG

**Priority:** Low | **Research Progress:** 0%

**Goal:** Support images, tables, audio in retrieval and generation

**Capabilities:**
- Image ingestion and search
- Table structure preservation
- Audio/video transcription
- Cross-modal retrieval (text → images)

📂 **[Full Planning](upgrades/planned/multi-modal-rag/)**

---

**For complete upgrade workflow and lifecycle, see:** [`upgrades/README.md`](upgrades/README.md)

## Research Management

### Adding Official Documentation

```bash
# Example: Adding Neo4j documentation
mkdir -p research/documentation/neo4j
# Save documentation as markdown or PDF
# Reference in ADRs and implementation decisions
```

### Creating Architecture Decision Records

```bash
# Use the template in research/architecture-decisions/README.md
# Example ADR structure:
# - Context: What problem are we solving?
# - Options Considered: Research-backed alternatives
# - Decision: Chosen option with rationale
# - Research Support: Citations to Tier 1-3 sources
# - Consequences: Positive, negative, mitigation
```

### Example ADR Citation

```markdown
## Research Support

**Official Documentation (Tier 1):**
- Neo4j Graph Database Guide: research/documentation/neo4j/graph-guide.md
- PostgreSQL pgvector Extension: research/documentation/postgres/pgvector.md

**Verified Examples (Tier 2):**
- Multi-database RAG: research/examples/lettria-case-study.md (>1.5k stars)

**Technical Standards (Tier 3):**
- Saga Pattern: research/documentation/saga-pattern-microsoft.md
```

## Workflow Integration

**This repository supports a phased development workflow:**

1. **Phase 1: Vision** - Strategic goals and success criteria
2. **Phase 2: Mission** - Research and technical approach
3. **Phase 3: Execution Planning** - Detailed implementation plan
4. **Phase 3.5: Review Board** - C-suite validation (COO, CIO, CTO)
5. **Phase 4: Implementation** - Execute approved plan
6. **Phase 5: Testing** - Validate against requirements

**Workflow commands are managed through Claude Code slash commands.**

### Executive Suite (Review Board)

The project includes three C-suite executive agents for quality validation during Phase 3.5:

**Chief Information Officer (CIO)**

- Validates research quality and documentation completeness
- Enforces source hierarchy standards (official docs, 1.5k+ star repos)
- Reviews dependencies, references, and code examples
- **Tools:** Read, Grep, Glob, WebSearch, WebFetch, Write
- **Location:** `.claude/agents/CIO.md`

**Chief Technology Officer (CTO)**

- Reviews technical architecture and implementation feasibility
- Validates technology stack, API design, and data architecture
- Ensures code quality standards and security considerations
- **Tools:** Read, Grep, Glob, WebSearch, WebFetch, Write
- **Location:** `.claude/agents/CTO.md`

**Chief Operations Officer (COO)**

- Reviews operational capacity and goal achievement
- Validates execution feasibility, resource adequacy, and timeline realism
- Ensures UX quality, aesthetic polish, and user adoption likelihood
- **Tools:** Read, Grep, Glob, Write, TodoWrite
- **Location:** `.claude/agents/COO.md`

**Review Board Process:**

- All 3 executives must approve before Phase 4 (Implementation) begins
- Each provides scored rubric (0-100) and verdict (APPROVED/APPROVED_WITH_CONCERNS/REJECTED)
- Reviews validate alignment with research-first principles
- Agents have **veto power** for quality gate enforcement

### Research Team

The project includes 17 specialized research agents for continuous knowledge acquisition:

**Core Research Leadership:**

- **research-manager** - Coordinates research efforts, monitors documentation, manages knowledge base
- **research-coordinator** - Orchestrates multi-agent research tasks, delegates specialized research
- **documentation-expert** - Maintains documentation quality, creates guides and references

**Specialized Researchers:**

- **deep-researcher** - In-depth technical research, complex problem analysis
- **standards-researcher** - Industry standards, best practices, compliance research
- **company-researcher** - Company-specific research, vendor analysis
- **competitive-intelligence-analyst** - Competitor analysis, market intelligence
- **technical-trend-analyst** - Technology trends, emerging patterns

**Documentation Specialists:**

- **documentation-hunter** - Finds official documentation, API references
- **api-documentation-specialist** - API documentation, endpoint analysis
- **github-examples-hunter** - Finds high-quality code examples (1.5k+ stars)
- **pattern-implementation-analyst** - Analyzes implementation patterns

**Quality & Validation:**

- **citation-manager** - Manages research citations, ensures source quality
- **technical-validator** - Validates technical accuracy of research
- **code-quality-validator** - Reviews code examples for quality standards

**Specialized Engineers:**

- **memory-system-engineer** - Memory systems, knowledge graphs, persistence
- **agent-testing-engineer** - Agent testing, validation, quality assurance

**All research agents located in:** `.claude/agents/`

## Important Notes

1. **Main codebase is symlinked** - All source code lives in `apex-memory-system/`
2. **Research is local** - Documentation and ADRs live in `research/`
3. **Settings are local** - `.claude/settings.local.json` is gitignored
4. **Always research first** - Check `research/` before implementation
5. **Cite your sources** - All decisions must reference research

## Configuration

### Environment Variables

**Configured in:** `apex-memory-system/.env` (copy from `.env.example`)

**Key variables:**
- `OPENAI_API_KEY` - OpenAI API key (required for embeddings)
- Database connection strings (Neo4j, PostgreSQL, Qdrant, Redis)
- Performance tuning parameters

### Database Access

| Service | URL | Credentials |
|---------|-----|-------------|
| Neo4j Browser | http://localhost:7474 | neo4j / apexmemory2024 |
| Grafana | http://localhost:3000 | admin / apexmemory2024 |
| Prometheus | http://localhost:9090 | (no auth) |
| API Docs | http://localhost:8000/docs | (no auth) |

## Performance Targets

- **Query latency:** <1s for 90% of queries (P90)
- **Cache hit rate:** >70% for repeat queries
- **Ingestion throughput:** 10+ documents/second parallel processing
- **Test coverage:** 80% minimum code coverage

## Getting Help

**For development questions, check:**
1. `apex-memory-system/CLAUDE.md` - Full development guide
2. `apex-memory-system/README.md` - Project overview and quick start
3. `research/documentation/` - Official documentation
4. `research/architecture-decisions/` - ADRs explaining design choices
