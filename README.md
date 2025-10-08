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

## Quick Start

### View Research Documentation

```bash
# Browse research by framework
cd research/documentation/

# Neo4j, PostgreSQL, Qdrant, Redis, Graphiti
# Query routing, embeddings, vector search
```

### Check Active Upgrades

```bash
# Query Router 8-week improvement plan
cat upgrades/query-router/IMPROVEMENT-PLAN.md

# Expected: +21-28 point relevance, 99% precision, <500ms P90
```

### Explore Agent System

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
│   │   ├── query-routing/         # 2025 RAG research ⭐ NEW
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
│   └── query-router/               # Oct 2025: 8-week upgrade ⭐ ACTIVE
│       ├── IMPROVEMENT-PLAN.md    # Comprehensive 550+ line plan
│       └── README.md              # Quick reference
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

### Query Router Improvement Plan (October 2025)

**Status:** Planning Complete → Ready for Implementation
**Timeline:** 8 weeks (4 phases)
**Priority:** High

Comprehensive upgrade bringing Apex query routing to 2025 standards based on latest RAG research.

**Expected Gains:**
- ✅ **+21-28 points** relevance improvement (Microsoft benchmarks)
- ✅ **99% precision** on relationship queries (GraphRAG)
- ✅ **90ms faster** intent classification (Semantic Router)
- ✅ **15-30% accuracy** improvement (adaptive learning)
- ✅ **90%+ cache hit rate** (semantic caching)

**Research Foundation:**
- [Semantic Router](research/documentation/query-routing/semantic-router.md) - 10ms intent classification
- [Query Rewriting](research/documentation/query-routing/query-rewriting-rag.md) - Microsoft RAG optimization
- [Agentic RAG 2025](research/documentation/query-routing/agentic-rag-2025.md) - Autonomous agents paradigm
- [Adaptive Routing](research/documentation/query-routing/adaptive-routing-learning.md) - Contextual bandits
- [GraphRAG](research/documentation/query-routing/graphrag-hybrid-search.md) - Hybrid vector-graph search

📋 **[Full Plan](upgrades/query-router/IMPROVEMENT-PLAN.md)** | 📊 **[Quick Reference](upgrades/query-router/README.md)**

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

## Documentation

| Resource | Description |
|----------|-------------|
| [CLAUDE.md](CLAUDE.md) | Claude Code integration guide |
| [research/](research/) | Research knowledge base with ADRs |
| [upgrades/](upgrades/) | Active improvement plans |
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
