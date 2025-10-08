# Research & Findings

This directory contains technical research following research-first principles for the Apex Memory System project.

## Structure

```
research/
├── documentation/           # Official docs, guides, best practices (Tier 1)
│   ├── neo4j/              # Graph database documentation
│   ├── postgresql/         # PostgreSQL + pgvector
│   ├── qdrant/             # Vector search engine
│   ├── redis/              # Cache layer
│   ├── graphiti/           # Temporal intelligence
│   ├── query-routing/      # Query routing research (2025) ⭐ NEW
│   ├── openai/             # OpenAI API, models
│   ├── fastapi/            # FastAPI framework
│   ├── pydantic/           # Data validation
│   ├── langchain/          # RAG patterns
│   ├── sentence-transformers/ # Embedding models
│   ├── pgvector/           # PostgreSQL vector extension
│   ├── docling/            # Document parsing
│   ├── python-packages/    # Python best practices
│   └── api-specs/          # OpenAPI, standards
├── examples/               # Code samples from high-quality sources (Tier 2)
│   ├── multi-database-rag/ # Parallel database patterns
│   ├── vector-search/      # HNSW implementations
│   ├── temporal-intelligence/ # Bi-temporal tracking
│   ├── document-processing/ # PDF/DOCX parsing
│   ├── fastapi-async/      # Async patterns
│   └── implementation-patterns/ # Best practices
├── architecture-decisions/ # ADRs with research citations
│   ├── ADR-001-multi-database-architecture.md
│   ├── ADR-002-saga-pattern-distributed-writes.md
│   ├── ADR-003-intent-based-query-routing.md
│   ├── ADR-004-bi-temporal-versioning-graphiti.md
│   ├── ADR-005-hnsw-vs-ivfflat-vector-indexing.md
│   └── ADR-006-graphiti-custom-entity-types.md
└── review-board/           # C-suite validation reviews (Phase 3.5)
    └── cio-review.md       # Example CIO review
```

## Source Hierarchy

1. **Official Documentation** - Anthropic docs, Claude docs, Neo4j, PostgreSQL, Qdrant docs
2. **Verified GitHub Repositories** - Minimum 1.5k+ stars for examples
3. **Technical Standards** - RFCs, W3C specs, database best practices
4. **Verified Technical Sources** - Known experts, conference talks
5. **Package Registries** - Official PyPI with verified publishers

## Research Quality Standards

- Documentation must be current (<2 years old OR explicitly verified as still valid)
- GitHub examples must demonstrate the pattern being researched
- All sources must include citations with URLs
- Breaking changes and deprecations must be noted

## Active Research

### Query Routing (October 2025) ⭐

Comprehensive research on state-of-the-art query routing systems for the **Query Router Improvement Plan** (8-week upgrade).

**Location:** `documentation/query-routing/`

**Research Documents:**
- [Semantic Router](documentation/query-routing/semantic-router.md) - 10ms intent classification
- [Query Rewriting](documentation/query-routing/query-rewriting-rag.md) - +21-28 point improvement
- [Agentic RAG 2025](documentation/query-routing/agentic-rag-2025.md) - Autonomous agents paradigm
- [Adaptive Routing](documentation/query-routing/adaptive-routing-learning.md) - Contextual bandits
- [GraphRAG](documentation/query-routing/graphrag-hybrid-search.md) - 99% precision hybrid search

**Expected Impact:**
- 85-95% routing accuracy (vs current 70-75%)
- +21-28 points relevance improvement
- 99% precision on relationship queries
- <500ms P90 latency

📋 **[Query Router Upgrade Plan](../upgrades/query-router/IMPROVEMENT-PLAN.md)**

## References

All research sources should be catalogued in `references.md` with:
- Source URL
- Quality tier (1-5)
- Date accessed
- GitHub star count (if applicable)
- Key findings summary

## Cross-References

- **Upgrades:** See `../upgrades/` for active improvement plans
- **Workflow:** See `../workflow/` for 5-phase development process
- **Review Board:** See `review-board/` for Phase 3.5 validation
- **Agent System:** See `../.claude/agents/` for research team (17 agents)

---

*Created during Phase 2 (Mission)*
*Managed by Research Division and validated by CIO*
