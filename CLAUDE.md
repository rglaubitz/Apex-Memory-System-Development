# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

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
├── research/                  # Research-first organized documentation
│   ├── documentation/         # Official docs (Tier 1 sources)
│   │   └── query-routing/    # Query routing research (Oct 2025)
│   ├── examples/              # Verified code samples (Tier 2 sources)
│   └── architecture-decisions/ # ADRs with research citations
├── upgrades/                  # Active improvement plans
│   └── query-router/          # Query router upgrade (8-week plan)
├── workflow/                  # Workflow management (phases, approvals)
└── .claude/                   # Claude Code configuration
    ├── agents/                # Custom agent definitions
    └── settings.local.json    # Local settings
```

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

## Active Upgrades

### Query Router Improvement Plan (October 2025)

**Status:** Planning → Implementation Ready
**Timeline:** 8 weeks (4 phases)
**Priority:** High

We've completed comprehensive research on state-of-the-art query routing systems and identified 10 critical flaws in the current implementation. The improvement plan brings Apex to 2025 standards with:

**Expected Gains:**
- +21-28 point relevance improvement
- 90ms faster routing decisions
- 15-30% accuracy improvement
- 99% precision on relationship queries
- 90%+ cache hit rate

**Plan Location:** [`upgrades/query-router/IMPROVEMENT-PLAN.md`](upgrades/query-router/IMPROVEMENT-PLAN.md)

**Research Foundation:**
- [Semantic Router](research/documentation/query-routing/semantic-router.md) - 10ms intent classification
- [Query Rewriting](research/documentation/query-routing/query-rewriting-rag.md) - Microsoft +21 point improvement
- [Agentic RAG 2025](research/documentation/query-routing/agentic-rag-2025.md) - Latest paradigm shift
- [Adaptive Routing](research/documentation/query-routing/adaptive-routing-learning.md) - Learned weights
- [GraphRAG](research/documentation/query-routing/graphrag-hybrid-search.md) - 99% precision hybrid search

**Implementation Phases:**
1. **Week 1-2:** Foundation (semantic classification, query rewriting, analytics)
2. **Week 3-4:** Intelligent routing (adaptive weights, GraphRAG, semantic caching)
3. **Week 5-6:** Agentic evolution (complexity analysis, multi-router, self-correction)
4. **Week 7-8:** Advanced features (multimodal, real-time adaptation)

**Quick Wins Available:** 5 immediate improvements that can be implemented today (confidence scores, logging, OOS detection, normalization, timing tracking)

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
