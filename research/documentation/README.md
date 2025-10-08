# Official Documentation

Store official documentation, guides, and best practices here.

**Source hierarchy priority: HIGHEST (Tier 1)**

## What Goes Here

- Official Anthropic Claude documentation
- Official framework documentation (Neo4j, PostgreSQL, Qdrant, Redis, Graphiti)
- Official Python package documentation (FastAPI, Pydantic, etc.)
- API specifications (OpenAPI, GraphQL schemas)
- Official tutorials and getting-started guides

## Organization

```
documentation/
├── neo4j/                  # Graph database (Cypher, relationships)
├── postgresql/             # PostgreSQL + pgvector extension
├── qdrant/                 # Vector search engine
├── redis/                  # Cache layer, data structures
├── graphiti/               # Temporal intelligence, entity tracking
├── query-routing/          # Query routing research (2025) ⭐ NEW
├── openai/                 # OpenAI API, models, embeddings
├── fastapi/                # FastAPI framework, async patterns
├── pydantic/               # Data validation, models
├── langchain/              # RAG patterns, chains
├── sentence-transformers/  # Embedding models
├── pgvector/               # PostgreSQL vector extension
├── docling/                # Document parsing
├── python-packages/        # Python best practices
└── api-specs/              # OpenAPI specs, standards
```

## Framework Index

| Framework | Purpose | Key Features | Location |
|-----------|---------|--------------|----------|
| **Neo4j** | Graph database | Relationships, Cypher, graph traversal | [neo4j/](neo4j/) |
| **PostgreSQL** | Relational database | Metadata, structured data, ACID | [postgresql/](postgresql/) |
| **Qdrant** | Vector search | Semantic similarity, embeddings, HNSW | [qdrant/](qdrant/) |
| **Redis** | Cache layer | <100ms queries, data structures | [redis/](redis/) |
| **Graphiti** | Temporal intelligence | Bi-temporal tracking, patterns | [graphiti/](graphiti/) |
| **OpenAI** | AI models | GPT-5, embeddings, completions | [openai/](openai/) |
| **FastAPI** | Web framework | Async API, high performance | [fastapi/](fastapi/) |
| **Pydantic** | Data validation | Type checking, models | [pydantic/](pydantic/) |
| **LangChain** | RAG framework | Chains, agents, retrieval | [langchain/](langchain/) |
| **Sentence Transformers** | Embeddings | Text → vectors | [sentence-transformers/](sentence-transformers/) |
| **pgvector** | Vector extension | PostgreSQL vector search | [pgvector/](pgvector/) |
| **Docling** | Document parsing | PDF, DOCX, PPTX | [docling/](docling/) |

## Quality Standards

- Must be from official sources (anthropic.com, neo4j.com, postgresql.org, etc.)
- Include version information
- Note if documentation is for a different version than we're using
- Save local copies for critical docs (PDF or markdown)

## Active Research ⭐

### Query Routing (October 2025)

Comprehensive research on state-of-the-art query routing systems now available in `query-routing/`:

- **[Semantic Router](query-routing/semantic-router.md)** - 10ms intent classification
- **[Query Rewriting](query-routing/query-rewriting-rag.md)** - Microsoft +21-28 point improvement
- **[Agentic RAG 2025](query-routing/agentic-rag-2025.md)** - Autonomous agents paradigm
- **[Adaptive Routing](query-routing/adaptive-routing-learning.md)** - Contextual bandits, learned weights
- **[GraphRAG](query-routing/graphrag-hybrid-search.md)** - 99% precision hybrid search

📋 **[Full Upgrade Plan](../../upgrades/query-router/IMPROVEMENT-PLAN.md)** | 🚀 **[Quick Reference](../../upgrades/query-router/README.md)**

## Cross-References

- **Examples:** See `../examples/` for code implementations
- **ADRs:** See `../architecture-decisions/` for architectural decisions
- **Upgrades:** See `../../upgrades/` for active improvement plans
- **Review Process:** See `../review-board/` for Phase 3.5 validation

---

*Tier 1 sources - Highest priority for architectural decisions*
