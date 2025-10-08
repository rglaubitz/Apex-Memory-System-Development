# Query Routing Research (October 2025)

Comprehensive research on state-of-the-art query routing systems for RAG (Retrieval-Augmented Generation) applications.

## Overview

This collection represents the research foundation for the **Query Router Improvement Plan** (`../../../upgrades/query-router/`), covering the latest advances in query routing, semantic classification, adaptive learning, and hybrid vector-graph search.

**Research Period:** October 2025
**Research Quality:** Tier 1-2 (Official Documentation + Academic Research)
**Total Documents:** 5
**Total Content:** ~47,000 words

## Documents

### 1. Semantic Router

**File:** [semantic-router.md](semantic-router.md)
**Source:** aurelio-labs/semantic-router (GitHub)
**Stars:** High-quality verified repository
**Tier:** 2 (Verified GitHub Repository)

**Key Findings:**
- ✅ **10ms intent classification** vs 100ms keyword matching
- ✅ Embedding-based routing eliminates keyword mismatches
- ✅ 63.64% reduction in misclassification errors
- ✅ Production-ready Python library

**What It Solves:**
- Current Apex Flaw #1: Keyword-based intent classification

**Impact:**
- 90ms faster routing decisions
- Significantly improved accuracy

**Implementation Priority:** ⭐ High (Phase 1)

---

### 2. Query Rewriting for RAG Optimization

**File:** [query-rewriting-rag.md](query-rewriting-rag.md)
**Sources:** Microsoft Azure AI, Academic Papers (arXiv)
**Tier:** 1 (Official Microsoft Documentation + Academic Research)

**Key Findings:**
- ✅ **+21 to +28 points** relevance improvement (Microsoft benchmarks)
- ✅ 10 query rewrites in 147ms
- ✅ HyDE (Hypothetical Document Embeddings): +15-20% improvement
- ✅ RaFe Framework (EMNLP 2024): No manual annotations needed

**What It Solves:**
- Current Apex Flaw #2: No query rewriting

**Techniques Covered:**
- Query normalization (grammar, spelling)
- HyDE (generate hypothetical answers)
- Query decomposition (complex → sub-queries)
- Query expansion (synonyms, related terms)
- Step-back prompting (broader → specific)
- Multi-variation rewriting

**Implementation Priority:** ⭐ High (Phase 1)

---

### 3. Agentic RAG 2025

**File:** [agentic-rag-2025.md](agentic-rag-2025.md)
**Sources:** arXiv 2501.09136, IBM, LangGraph
**Tier:** 1 (Academic Research + Official Documentation)

**Key Findings:**
- ✅ **Paradigm shift:** Static pipelines → Autonomous agents
- ✅ 85-95% accuracy (vs 70-75% static routing)
- ✅ Multi-step reasoning with self-correction
- ✅ Reflection, planning, tool use patterns

**What It Solves:**
- Current Apex Flaw #5: No agentic capabilities
- Current Apex Flaw #7: No self-correction

**Core Patterns:**
- Reflection (agent evaluates own outputs)
- Planning (break complex queries into sub-tasks)
- Tool Use (dynamic database selection)
- Multi-Agent Collaboration (specialized agents)

**Frameworks:**
- LangGraph (agentic workflow graphs)
- LlamaIndex Agents

**Implementation Priority:** Medium (Phase 3)

---

### 4. Adaptive Routing with Learned Weights

**File:** [adaptive-routing-learning.md](adaptive-routing-learning.md)
**Sources:** arXiv 2508.21141, Databricks, Academic Papers
**Tier:** 1 (Academic Research)

**Key Findings:**
- ✅ **+15-30% accuracy improvement** over static weights
- ✅ Contextual bandits (PILOT system) for adaptive routing
- ✅ **8x speedup** in TPC-DS benchmarks (adaptive query execution)
- ✅ Online learning from production feedback

**What It Solves:**
- Current Apex Flaw #3: Static database weights
- Current Apex Flaw #10: No learned adaptation

**Techniques:**
- LinUCB (Linear Upper Confidence Bound)
- Matrix factorization for scoring
- BERT classifier for route prediction
- Runtime statistics collection
- Feedback-driven optimization

**Implementation Priority:** ⭐ High (Phase 2)

---

### 5. GraphRAG and Hybrid Vector-Graph Search

**File:** [graphrag-hybrid-search.md](graphrag-hybrid-search.md)
**Sources:** Neo4j Blog, FalkorDB, Industry Research
**Tier:** 1 (Official Documentation + Industry Implementations)

**Key Findings:**
- ✅ **99% precision** on relationship queries
- ✅ Single unified query (vs 2 separate queries)
- ✅ 2x latency reduction (150ms → 80ms)
- ✅ Neo4j 5.x native vector index support

**What It Solves:**
- Current Apex Flaw #4: No GraphRAG hybrid search

**Approaches:**
1. **Option 1:** Add Neo4j vector index (unified)
2. **Option 2:** Keep Qdrant + Neo4j with intelligent merging
3. **Option 3:** Migrate to unified GraphRAG DB (FalkorDB)

**Graph-Aware Reranking:**
- Boost results based on graph centrality
- Relationship context enrichment
- Cross-database verification

**Implementation Priority:** ⭐ High (Phase 2)

---

## Research Summary Table

| Document | Size | Tier | Key Metric | Impact |
|----------|------|------|------------|--------|
| Semantic Router | 3,867 words | 2 | 10ms classification | 90ms faster |
| Query Rewriting | 7,336 words | 1 | +21-28 points | Massive quality boost |
| Agentic RAG 2025 | 10,885 words | 1 | 85-95% accuracy | Paradigm shift |
| Adaptive Routing | 13,469 words | 1 | +15-30% accuracy | Learn & improve |
| GraphRAG | 11,611 words | 1 | 99% precision | Best-in-class |
| **TOTAL** | **47,168 words** | - | - | Revolutionary |

## Implementation Mapping

### Phase 1: Foundation (Week 1-2)
**Uses:**
- Semantic Router → Replace keyword matching
- Query Rewriting → Normalization, HyDE

**Expected Gain:** +21-28 points relevance, 90ms faster

---

### Phase 2: Intelligent Routing (Week 3-4)
**Uses:**
- Adaptive Routing → Contextual bandits, learned weights
- GraphRAG → Neo4j vector index, hybrid search
- Query Rewriting → Semantic caching

**Expected Gain:** +15-30% accuracy, 99% precision on relationships

---

### Phase 3: Agentic Evolution (Week 5-6)
**Uses:**
- Agentic RAG → Multi-router, self-correction
- Adaptive Routing → Complexity analysis

**Expected Gain:** 85-95% overall accuracy, autonomous improvement

---

### Phase 4: Advanced Features (Week 7-8)
**Uses:**
- All research combined for production optimization

**Expected Gain:** Production-ready, monitored, adaptive system

---

## Research Quality Validation

**CIO Validation Criteria:**
- ✅ Sources follow Tier 1-2 hierarchy
- ✅ All documents include citations with URLs
- ✅ Documentation is current (2024-2025)
- ✅ GitHub repos verified (high-quality)
- ✅ Academic papers from reputable sources (arXiv, EMNLP)
- ✅ Official vendor documentation (Microsoft, Neo4j, IBM)

**Pass Rate:** 100% (All criteria met)

## Cross-References

**Improvement Plan:** `../../../upgrades/query-router/IMPROVEMENT-PLAN.md`
**Quick Reference:** `../../../upgrades/query-router/README.md`
**Review Board:** `../../review-board/`
**ADRs:** `../../architecture-decisions/`

## References

All research documents contain full citations and URLs to source material. See individual files for detailed references.

---

**Research Conducted:** October 2025
**Research Team:** documentation-hunter, github-examples-hunter, deep-researcher, standards-researcher
**Validated By:** CIO (Research Quality)
**Purpose:** Foundation for Query Router Improvement Plan (8-week upgrade)
