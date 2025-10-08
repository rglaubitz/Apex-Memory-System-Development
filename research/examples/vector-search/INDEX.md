# Vector Search Implementation Patterns - Index

**Directory:** `/research/examples/vector-search/`
**Last Updated:** October 6, 2025
**Research Agent:** github-examples-hunter

---

## Quick Reference

### Repository Summary

| Repository | Stars | Status | License | Primary Use |
|------------|-------|--------|---------|-------------|
| [Qdrant](https://github.com/qdrant/qdrant) | 26.4k | Active (Oct 2025) | Apache 2.0 | High-performance vector DB |
| [pgvector](https://github.com/pgvector/pgvector) | 17.8k | Active (v0.8.1) | PostgreSQL | Hybrid SQL + vector |
| [Milvus](https://github.com/milvus-io/milvus) | 36.3k | Active (v2.6) | Apache 2.0 | Cloud-native vector DB |
| [LlamaIndex](https://github.com/run-llama/llama_index) | 44.6k | Very Active | MIT | LLM application framework |
| [LangChain](https://github.com/langchain-ai/langchain) | 65k+ | Very Active | MIT | RAG orchestration |

### Key Patterns Documented

1. **HNSW Indexing** (Qdrant, pgvector, Milvus)
   - Parameter tuning: `m`, `ef_construction`, `ef_search`
   - Performance: <10ms P90 latency achievable
   - Trade-offs: HNSW vs IVFFlat

2. **Hybrid Search** (LangChain, Haystack)
   - Vector + keyword combination
   - 15-30% recall improvement
   - Ensemble retrieval patterns

3. **Semantic Caching** (LangChain)
   - Redis-backed caching
   - <100ms for repeat queries
   - 0.95 similarity threshold

4. **Embedding Pipelines** (LlamaIndex)
   - Batch processing (10+ docs/sec)
   - Parallel database writes
   - Progress tracking

5. **Multi-Database Routing** (LlamaIndex)
   - Query type classification
   - Optimal database selection
   - Result aggregation

---

## File Structure

```
vector-search/
├── INDEX.md           # This file - Quick reference and navigation
└── README.md          # Full research report with detailed analysis
```

---

## Relevance to Apex Memory System

### Direct Integrations (Current Architecture)

**Qdrant:**
- High-performance vector similarity search
- HNSW indexing for <10ms P90 latency
- Payload filtering for hybrid queries
- Current status: Integrated in Apex

**pgvector:**
- Hybrid SQL + vector queries
- HNSW and IVFFlat index support
- Bi-temporal metadata + semantic search
- Current status: Integrated in Apex

### Framework Patterns (Implementation Reference)

**LlamaIndex:**
- Multi-database orchestration patterns
- VectorStoreIndex abstraction
- Embedding pipeline optimization
- Evaluation frameworks

**LangChain:**
- Hybrid search (ensemble retrieval)
- Semantic caching strategies
- Query routing patterns
- Observability integration

**Milvus:**
- Multi-index strategies (reference only)
- Quantization techniques
- GPU acceleration patterns
- Not currently integrated, but useful for future scaling

---

## Quick Access: Performance Benchmarks

### Latency Targets (P90)

- **Qdrant HNSW:** <10ms (vector similarity)
- **pgvector Hybrid:** <50ms (SQL + vector)
- **Redis Cache:** <100ms (repeat queries)
- **Full RAG Pipeline:** <1s (with re-ranking)

### Throughput Targets

- **Embedding Generation:** 10+ docs/second (batch processing)
- **Cache Hit Rate:** >70% (semantic caching)
- **Parallel Ingestion:** Multiple databases (saga pattern)

### Memory Optimization

- **Quantization:** 4x reduction (int8 vs float32)
- **IVFFlat vs HNSW:** 2-3x memory reduction
- **Milvus v2.6:** 72% memory reduction (reference)

---

## Implementation Checklist

### Phase 1: Foundational (Current)
- [x] Qdrant integration with HNSW
- [x] pgvector with HNSW and IVFFlat
- [ ] Tune HNSW parameters for production

### Phase 2: Performance Optimization
- [ ] Implement hybrid search (Qdrant + PostgreSQL FTS)
- [ ] Add semantic caching (Redis, 0.95 threshold)
- [ ] Optimize embedding pipeline (batch + async)

### Phase 3: Advanced Features
- [ ] Maximum Marginal Relevance (diversity)
- [ ] Cross-encoder re-ranking
- [ ] Enhanced query router (multi-database)

### Phase 4: Monitoring
- [ ] Cache hit rate tracking (>70% target)
- [ ] Retrieval metrics (hit rate, MRR, NDCG)
- [ ] Latency monitoring (P90, P99 per DB)

---

## Key Takeaways

1. **HNSW is production-ready** - Use for Qdrant and pgvector (better than IVFFlat for most cases)
2. **Hybrid search improves recall** - Combine vector + keyword for 15-30% improvement
3. **Semantic caching hits target** - <100ms for repeat queries (aligns with Apex goal)
4. **Batch processing scales** - 10+ docs/second achievable with proper pipeline
5. **Multi-database patterns proven** - LlamaIndex/LangChain validate Apex architecture

---

## Related Research

- **Official Documentation:** `/research/documentation/qdrant/`, `/research/documentation/pgvector/`
- **Architecture Decisions:** `/research/architecture-decisions/` (ADRs referencing these patterns)
- **Performance Benchmarks:** See "Performance Optimization Summary" in README.md

---

## Contact & Updates

**Research Agent:** github-examples-hunter
**Review Board:** CIO (documentation quality), CTO (technical feasibility)
**Last Review:** October 6, 2025
**Next Review:** When implementing Phase 2 optimizations

---

**Quick Links:**
- [Full Research Report](./README.md)
- [Apex Memory System Main Docs](/apex-memory-system/CLAUDE.md)
- [Research Standards](/research/documentation/README.md)
