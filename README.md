# Apex Memory System - Development Workspace

> **Research-driven development wrapper** for the Apex Memory System with phased workflow management, comprehensive research documentation, and specialized agent orchestration.

[![Research-First](https://img.shields.io/badge/methodology-research--first-blue)](research/)
[![Phased Workflow](https://img.shields.io/badge/workflow-5--phase-green)](workflow/)
[![Agents](https://img.shields.io/badge/agents-20-orange)](.claude/agents/)

## What is This Repository?

This is the **development coordination layer** for the Apex Memory System project. It provides:

- **Research Organization** - Tier 1-5 source hierarchy with citations and validation
- **Workflow Management** - 5-phase development (Vision → Mission → Planning → Implementation → Testing)
- **Agent Orchestration** - 20 specialized agents including C-suite executives and research team
- **Upgrade Tracking** - Active improvement plans with research backing

**The actual codebase** is maintained separately at [`apex-memory-system/`](https://github.com/rglaubitz/apex-memory-system) and linked here as a symlink for local development.

## 📁 Directory Structure

```
Apex-Memory-System-Development/
├── README.md                    # This file
├── CLAUDE.md                    # Claude Code instructions
│
├── docs/                        # 📚 Documentation & Guides
│   ├── guides/                  # Implementation guides
│   ├── research/                # Research papers & notes
│   └── system/                  # System manuals & diagrams
│
├── session-logs/                # 📅 Day-by-day development logs
│   ├── 2025-10-09/             # Days 1-3 completion
│   ├── 2025-10-23/             # Day 2 implementation
│   └── 2025-10-24/             # MCP testing
│
├── media/                       # 📸 Screenshots & images
│
├── testing/                     # 🧪 Test suites (consolidated)
│   ├── integration/            # Integration tests
│   ├── verification/           # Pre-deployment checks
│   └── manual/                 # Manual test procedures
│
├── research/                    # 🔬 Research-first documentation
│   ├── documentation/          # Tier 1 sources (official docs)
│   ├── examples/               # Tier 2 sources (verified code)
│   └── architecture-decisions/ # ADRs with citations
│
├── upgrades/                    # 🚀 Active improvement plans
│   ├── active/                 # Current implementations
│   ├── planned/                # Research phase
│   └── completed/              # Archived upgrades
│
├── deployment/                  # 🌐 Deployment guides
│   ├── mcp-server/             # PyPI deployment
│   ├── production/             # GCP deployment
│   └── verification/           # Pre-deployment checks
│
├── workflow/                    # 📋 5-phase development workflow
├── apex-mcp-server/            # MCP server implementation
└── apex-memory-system/         # ⭐ Main codebase (symlink)
```

## Quick Start

### 📚 Browse Documentation

```bash
# View all guides
ls docs/guides/

# Read system manual
open docs/system/SYSTEM-MANUAL.html
```

### 🚀 Check Active Upgrades

```bash
# Query Router Enhancement (COMPLETED Oct 25, 2025)
cat upgrades/active/query-router-enhancement/IMPLEMENTATION-SUMMARY.md

# Grade: B- → A- (+22 points)
# Fixes: Temporal endpoint, Qdrant content, Metadata bias
```

### 📅 Review Session Logs

```bash
# Latest session
cat session-logs/2025-10-24/apex-mcp-testing-results.md

# All Day 2 sessions
ls session-logs/2025-10-23/
```

### 🔬 Explore Research

```bash
# Browse research by framework
cd research/documentation/

# Neo4j, PostgreSQL, Qdrant, Redis, Graphiti
# Query routing, embeddings, vector search
```

### 🤖 Agent System

```bash
# 20 specialized agents
ls .claude/agents/

# C-Suite: CIO, CTO, COO (Review Board)
# Research: documentation-hunter, github-examples-hunter, etc.
```

## Directory Structure

```
Apex-Memory-System-Development/
├── README.md                       # You are here
├── CLAUDE.md                       # Claude Code integration guide
│
├── apex-memory-system/             # Symlink to main codebase (not committed)
│
├── research/                       # Research-first knowledge base
│   ├── documentation/              # Official docs (Tier 1 sources)
│   │   ├── neo4j/                 # Graph database docs
│   │   ├── postgresql/            # PostgreSQL + pgvector
│   │   ├── qdrant/                # Vector search
│   │   ├── graphiti/              # Temporal intelligence
│   │   ├── temporal/              # Temporal.io workflow orchestration
│   │   └── ...
│   ├── examples/                   # Verified code samples (Tier 2)
│   │   ├── multi-database-rag/    # Parallel database patterns
│   │   ├── vector-search/         # HNSW implementations
│   │   ├── temporal-intelligence/ # Bi-temporal tracking
│   │   └── ...
│   ├── architecture-decisions/     # ADRs with research citations
│   │   ├── ADR-001-multi-database-architecture.md
│   │   ├── ADR-002-saga-pattern-distributed-writes.md
│   │   ├── ADR-003-intent-based-query-routing.md
│   │   ├── ADR-004-bi-temporal-versioning-graphiti.md
│   │   ├── ADR-005-hnsw-vs-ivfflat-vector-indexing.md
│   │   └── ...
│   ├── review-board/               # C-suite validation reviews
│   └── references.md               # Source index with quality ratings
│
├── upgrades/                       # Active improvement plans
│   ├── active/
│   │   └── temporal-implementation/ # Oct 2025: Sections 1-9 complete ⭐ ACTIVE
│   │       ├── README.md           # Project overview (updated Oct 18)
│   │       ├── EXECUTION-ROADMAP.md
│   │       ├── PROJECT-STATUS-SNAPSHOT.md
│   │       ├── TECHNICAL-DEBT.md
│   │       ├── guides/             # Implementation guides
│   │       │   ├── IMPLEMENTATION-GUIDE.md (3,110 lines)
│   │       │   ├── PREFLIGHT-CHECKLIST.md
│   │       │   └── VALIDATION-PROCEDURES.md
│   │       ├── handoffs/           # Section handoff docs
│   │       │   └── HANDOFF-SECTION-6 through 9.md
│   │       ├── section-summaries/  # Detailed section completion docs
│   │       │   ├── SECTION-9-COMPLETE.md
│   │       │   └── SECTION-10-COMPLETE.md
│   │       ├── research/           # RDF documentation
│   │       ├── tests/              # Test artifacts (organized by phase)
│   │       │   ├── STRUCTURE.md   # Complete test organization guide
│   │       │   ├── phase-1-validation/      # Pre-testing validation
│   │       │   ├── phase-2a-integration/    # Integration tests (1/6 complete)
│   │       │   ├── phase-2b through 2f/     # Load, metrics, alerts
│   │       │   └── section-1 through 8/     # Development tests (41 tests)
│   │       └── examples/           # Working code examples
│   ├── planned/                    # Future upgrades
│   └── completed/                  # Completed upgrades
│
├── deployment/                     # All deployment documentation ⭐ NEW
│   ├── README.md                  # Master deployment guide
│   ├── mcp-server/                # MCP Server PyPI deployment (82% complete)
│   │   ├── DEPLOYMENT-CHECKLIST.md
│   │   └── PUBLISHING.md
│   ├── production/                # Production cloud deployment (planned)
│   │   ├── README.md
│   │   ├── GCP-DEPLOYMENT-GUIDE.md
│   │   ├── ARCHITECTURE.md
│   │   ├── scripts/               # Deployment automation
│   │   └── terraform/             # Infrastructure as code
│   ├── verification/              # Pre-deployment verification (complete)
│   │   ├── README.md
│   │   ├── WORKFLOW-CHECKLIST.md
│   │   └── verified/              # Verification results
│   ├── testing/                   # Pre-deployment testing (complete)
│   │   ├── README.md
│   │   ├── TESTING-KIT.md
│   │   └── scripts/               # Test automation
│   └── components/                # Component-specific deployment
│       └── query-router/          # Query router deployment (complete)
│           ├── DEPLOYMENT-GUIDE.md
│           ├── PRODUCTION-ROLLOUT.md
│           ├── TESTING.md
│           └── TROUBLESHOOTING.md
│
├── workflow/                       # 5-phase development process
│   └── README.md                  # Workflow documentation
│
└── .claude/                        # Claude Code configuration
    ├── agents/                     # 20 specialized agents
    │   ├── CIO.md                 # Chief Information Officer
    │   ├── CTO.md                 # Chief Technology Officer
    │   ├── COO.md                 # Chief Operations Officer
    │   ├── research-manager.md
    │   ├── documentation-hunter.md
    │   └── ... (17 more)
    ├── .mcp.json                  # MCP server configuration
    └── README.md                  # Agent system overview
```

## Active Upgrades

### Temporal.io Integration (October 2025)

**Status:** Section 11 Testing - Phase 2A Complete (82% overall progress)
**Timeline:** 11 sections (Sections 1-9 done, 10-11 remaining)
**Priority:** Critical - Production Infrastructure

Complete Temporal.io workflow orchestration for document ingestion with 6-layer monitoring.

**Sections Completed (1-9):**
- ✅ Sections 1-4: Foundation (Docker, CLI, Worker, Hello World)
- ✅ Section 5-8: Implementation (Activities, Workflows, Integration)
- ✅ **Section 9: Monitoring** - 27 metrics, 33-panel dashboard, 12 alerts

**Section 11 Testing Progress:**
- ✅ **Phase 1:** Pre-testing validation (5 critical fixes)
- ✅ **Phase 2A:** Integration tests (13 critical fixes, 1/6 tests passing)
- 🔄 **Phase 2B:** Enhanced Saga baseline verification (121 tests)
- 📝 **Phase 2C-2F:** Load tests, metrics, alerts (pending)

**Key Achievements:**
- 100% Temporal integration (no legacy path)
- Complete observability (6-layer monitoring)
- Silent failure detection
- 194 test suite (42 passing, 152 pending)

**Test Organization:**
- All test artifacts organized in `upgrades/active/temporal-implementation/tests/`
- Phase-based structure with fix-and-document workflow
- Complete documentation in `tests/STRUCTURE.md`

📋 **[Execution Roadmap](upgrades/active/temporal-implementation/EXECUTION-ROADMAP.md)** | 📊 **[Project Status](upgrades/active/temporal-implementation/PROJECT-STATUS-SNAPSHOT.md)** | 🧪 **[Test Structure](upgrades/active/temporal-implementation/tests/STRUCTURE.md)**

## Research-First Philosophy

All architectural decisions must be grounded in high-quality research following our source hierarchy:

### Source Hierarchy (Priority Order)

1. **Tier 1:** Official Documentation - Anthropic, Neo4j, PostgreSQL, Qdrant, Redis, Graphiti
2. **Tier 2:** Verified GitHub Repositories - Minimum 1.5k+ stars, active maintenance
3. **Tier 3:** Technical Standards - RFCs, W3C specs, academic papers (peer-reviewed)
4. **Tier 4:** Verified Technical Sources - Known experts, conference talks
5. **Tier 5:** Package Registries - Official PyPI, npm with verified publishers

### Research Quality Standards

- ✅ Documentation must be current (<2 years old OR explicitly verified)
- ✅ GitHub examples must demonstrate the pattern being researched
- ✅ All sources must include citations with URLs
- ✅ Breaking changes and deprecations must be noted

**Enforcement:** CIO validates research quality during Phase 3.5 Review Board

## Workflow System

5-phase development process with quality gates:

1. **Phase 1: Vision** - Strategic goals and success criteria
2. **Phase 2: Mission** - Research and technical approach
3. **Phase 3: Execution Planning** - Detailed implementation plan
4. **Phase 3.5: Review Board** - C-suite validation (COO, CIO, CTO) ⭐
5. **Phase 4: Implementation** - Execute approved plan
6. **Phase 5: Testing** - Validate against requirements

**Quality Gate:** All 3 executives must approve before Phase 4 begins.

📋 **[Workflow Details](workflow/README.md)**

### Session Continuity & Handoffs

**Handoff Workflow Format** - Zero context loss across multi-day/multi-week development

**Key Features:**
- ✅ Complete session-to-session continuity (What Was Accomplished, What's Next)
- ✅ Copy-paste "Start Command" for instant continuation
- ✅ Architectural decisions documented (WHY not just WHAT)
- ✅ Implementation patterns (reusable code templates)
- ✅ Baseline test preservation tracking

**Components:**
1. **Handoff Documents** - Complete work summaries with file locations, line numbers
2. **Quick Reference** - Fast pattern/command lookup
3. **Progress Tracking** - Updated after each day (current vs. expected)
4. **Handoff Index** - Chronological progression

**Example:** Week 3 Staging Lifecycle handoff enabled instant continuation with 11 tests (100% pass), ~1,017 lines of code, zero context loss.

📖 **[Handoff Format Guide](workflow/HANDOFF-WORKFLOW-FORMAT.md)** | 📂 **[Current Handoffs](upgrades/active/temporal-implementation/handoffs/INDEX.md)**

## Agent System

20 specialized agents for development coordination:

### C-Suite Executives (Review Board)
- **CIO** - Research quality, documentation completeness
- **CTO** - Technical architecture, implementation feasibility
- **COO** - Operational capacity, goal achievement

### Research Team (17 Agents)
- **Core:** research-manager, research-coordinator, documentation-expert
- **Hunters:** documentation-hunter, github-examples-hunter, api-documentation-specialist
- **Analysts:** deep-researcher, standards-researcher, competitive-intelligence-analyst
- **Validators:** technical-validator, citation-manager, code-quality-validator
- **Engineers:** memory-system-engineer, agent-testing-engineer

🤖 **[Agent Index](.claude/agents/README.md)** | ⚙️ **[System Overview](.claude/README.md)**

## Testing Workflow

### Test Organization

All tests are organized in `upgrades/active/temporal-implementation/tests/` with two categories:

**Section Tests (Development-Time):**
- 41 tests created during Sections 1-8 implementation
- Validate individual components as they're built
- Located in `tests/section-*/`

**Phase Tests (Production Validation):**
- 194 tests for Section 11 comprehensive testing
- Validate production readiness before deployment
- Located in `tests/phase-*/` with fix-and-document workflow

📘 **[Complete Test Structure](upgrades/active/temporal-implementation/tests/STRUCTURE.md)**

### Pre-Deployment Testing Kit ⭐ NEW

**Comprehensive validation suite** before moving to production:

- **Testing Kit** - Complete pre-deployment validation in 3-4 hours
- **6 Architectural Layers** - Database writers → Services → Activities → Workflows → API → Query Router
- **Bottom-Up Testing** - Validate foundation before higher layers
- **GO/NO-GO Decision** - Clear deployment criteria based on test results

🧪 **[Testing Kit Guide](testing-kit/)** | 📋 **[Implementation Steps](testing-kit/IMPLEMENTATION.md)** | 📊 **[Results Template](testing-kit/results/RESULTS-TEMPLATE.md)**

**What You'll Know After Testing:**
- ✅/❌ System health at all 6 layers
- ✅/❌ Integration points working correctly
- ✅/❌ Performance metrics vs. targets (throughput, latency, cache hit rate)
- ✅/❌ Production readiness (enhanced saga 121/121, metrics recording, zero critical errors)

### Fix-and-Document Workflow

All Phase 2 testing follows this 5-step workflow for test failures:

1. **Document Problem** - Capture error, stack trace, environment
2. **Root Cause Analysis** - Identify underlying issue (not symptoms)
3. **Apply Fix** - Implement solution (production or test code)
4. **Validate Fix** - Confirm test passes end-to-end
5. **Document Outcome** - What went good/bad, production impact

**Results:** Each phase folder contains detailed `PHASE-X-FIXES.md` documentation.

**Example:** Phase 2A discovered 13 critical issues:
- 5 production code fixes (Temporal SDK, database config)
- 8 test code improvements (fixtures, mocking, validation)
- All documented with production impact assessment

## Main Codebase

The actual implementation is maintained at:

🔗 **https://github.com/rglaubitz/apex-memory-system**

**Symlink:** `apex-memory-system/` (local development only, not committed)

### Architecture Overview

**Parallel multi-database intelligence platform:**

- **Neo4j** - Graph relationships and entity connections
- **Graphiti** - Temporal reasoning and pattern detection
- **PostgreSQL + pgvector** - Metadata search and hybrid semantic queries
- **Qdrant** - High-performance vector similarity search
- **Redis** - Cache layer for <100ms repeat queries

### Quick Commands (from apex-memory-system/)

```bash
# Start all services
cd docker && docker-compose up -d

# Run tests
pytest                          # All tests with coverage
pytest tests/integration/ -v    # Integration tests

# Start API
python -m uvicorn apex_memory.main:app --reload --port 8000
# API docs: http://localhost:8000/docs
```

📖 **[Full Development Guide](apex-memory-system/CLAUDE.md)**

## MCP Server (Claude Desktop Integration)

**Apex MCP Server** enables Claude Desktop to interact directly with your Apex Memory System through conversational memory.

🔗 **[apex-mcp-server/](apex-mcp-server/)** - Complete MCP server implementation

### Key Features

- **🧠 Intelligent Orchestration** - `ask_apex()` orchestrates 3-6 queries and synthesizes narrative answers
- **5 Basic Memory Operations** - Add, search, list, and manage memories with LLM entity extraction
- **4 Advanced Features** - Temporal search, entity timelines, community detection, graph analytics
- **Multi-Database Integration** - Seamless access to Neo4j, PostgreSQL, Qdrant, Redis through unified API

### Quick Start

```bash
# Install and configure
cd apex-mcp-server
./install-apex-mcp.sh

# Restart Claude Desktop
# Start talking: "Remember that I prefer Python for backend development"
```

### What Makes It Different

Unlike OpenMemory (simple storage) or Graphiti MCP (single database), Apex MCP provides:

- ✅ **Multi-query orchestration** - Claude plans and executes 3-6 queries automatically
- ✅ **Narrative synthesis** - Transforms JSON data into coherent stories with insights
- ✅ **4-database intelligence** - Routes queries to optimal database (Neo4j, Qdrant, PostgreSQL, Redis)
- ✅ **Bi-temporal tracking** - Query your knowledge graph as it existed at any point in time
- ✅ **Pattern detection** - Discovers trends, communities, and relationships automatically

**Example conversation:**
```
You: "Tell me everything about ACME Corporation"

Claude: [Orchestrates 6 queries across graph, temporal layer, communities]

       I've analyzed ACME Corporation across your entire knowledge graph.
       Here's what I found:

       📊 OVERVIEW: 12 documents, 8 connected entities, 3 months tracked
       🔗 KEY RELATIONSHIPS: Primary supplier Bosch (83% of orders)
       📈 PATTERNS: Recurring orders every 3-4 weeks (89% consistency)
       📍 TEMPORAL: Added Brembo in March (supplier diversification)
       💡 INSIGHT: Stable customer with strategic risk management
```

📚 **Documentation:** [INSTALLATION.md](apex-mcp-server/INSTALLATION.md) | [EXAMPLES.md](apex-mcp-server/EXAMPLES.md) | [TROUBLESHOOTING.md](apex-mcp-server/TROUBLESHOOTING.md)

## Documentation

| Resource | Description |
|----------|-------------|
| [CLAUDE.md](CLAUDE.md) | Claude Code integration guide |
| [testing-kit/](testing-kit/) ⭐ NEW | Pre-deployment testing kit (3-4 hours comprehensive validation) |
| [research/](research/) | Research knowledge base with ADRs |
| [upgrades/](upgrades/) | Active improvement plans |
| [upgrades/active/temporal-implementation/tests/STRUCTURE.md](upgrades/active/temporal-implementation/tests/STRUCTURE.md) | Complete test organization guide |
| [workflow/](workflow/) | 5-phase development process |
| [.claude/agents/](.claude/agents/) | 20 specialized agents |

## Performance Targets

- **Query Latency:** <1s for 90% of queries (P90)
- **Cache Hit Rate:** >70% for repeat queries (target: 90%+)
- **Ingestion Throughput:** 10+ documents/second parallel processing
- **Test Coverage:** 80% minimum code coverage

## Getting Help

**For development questions:**
1. Check [research/documentation/](research/documentation/) for official docs
2. Review [research/architecture-decisions/](research/architecture-decisions/) for design rationale
3. See [apex-memory-system/CLAUDE.md](apex-memory-system/CLAUDE.md) for implementation guide
4. Consult [upgrades/](upgrades/) for active improvement plans

## License

MIT License - See main codebase repository for details.

---

**Maintained by:** Richard Glaubitz
**Research Methodology:** Research-first with source validation
**Quality Gate:** C-suite Review Board (Phase 3.5)
**Agent System:** 20 specialized agents for development coordination
