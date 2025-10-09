# Query Router Improvement Plan - Quick Reference

**Status:** ✅ Planning Complete → 🚀 Ready for Implementation
**Priority:** High
**Timeline:** 8 weeks (4 phases)
**Last Updated:** October 2025

## TL;DR

Comprehensive upgrade bringing Apex query routing from current keyword-based approach to 2025 standards with semantic classification, adaptive learning, agentic reasoning, and GraphRAG hybrid search.

## Expected Gains

| Metric | Current | Target | Gain |
|--------|---------|--------|------|
| **Routing Accuracy** | 70-75% | 85-92% | +15-20% |
| **Relevance Score** | 0.72 | 0.85-0.93 | +21-28 points |
| **Intent Classification** | 100ms (keyword) | 10ms (semantic) | 90ms faster |
| **Cache Hit Rate** | 75% (exact match) | 90%+ (semantic) | +15%+ |
| **Precision (Relationships)** | 70-75% | 99% | +24-29% |
| **P90 Latency** | 800ms | <500ms | -37.5% |

## Current Problems (10 Critical Flaws)

1. ❌ **Keyword-based intent classification** (63.64% misclassification rate)
2. ❌ **No query rewriting** (missing +21-28 point gains)
3. ❌ **Static database weights** (no adaptation)
4. ❌ **No GraphRAG hybrid search** (missing 99% precision)
5. ❌ **No agentic capabilities** (no self-correction, reflection)
6. ❌ **No complexity analysis** (same routing for all queries)
7. ❌ **No out-of-scope detection** (wasted resources)
8. ❌ **Exact-match-only caching** (75% vs 90%+ possible)
9. ❌ **No confidence scores** (can't assess quality)
10. ❌ **No learned adaptation** (fixed rules forever)

## Research Foundation

| Document | Key Finding | Impact |
|----------|-------------|--------|
| [Semantic Router](../../research/documentation/query-routing/semantic-router.md) | 10ms intent classification with embeddings | 90ms faster routing |
| [Query Rewriting](../../research/documentation/query-routing/query-rewriting-rag.md) | Microsoft: +21-28 points relevance | Massive quality boost |
| [Agentic RAG 2025](../../research/documentation/query-routing/agentic-rag-2025.md) | Autonomous agents, 85-95% accuracy | New paradigm |
| [Adaptive Routing](../../research/documentation/query-routing/adaptive-routing-learning.md) | Contextual bandits, learned weights | +15-30% accuracy |
| [GraphRAG](../../research/documentation/query-routing/graphrag-hybrid-search.md) | Unified vector+graph, 99% precision | Best-in-class |

📚 **[Complete Research Documentation](../../research/documentation/query-routing/)** - 11 research documents covering all aspects of modern RAG query routing

## Testing & Validation

**Test Framework:** [`../../tests/`](../../tests/)

Comprehensive testing framework with 250-query difficulty-stratified test suite validating semantic intent classification accuracy across easy/medium/hard queries.

**Key Test Files:**
- **Test Suite:** [`tests/test-suites/difficulty-stratified-250-queries.json`](../../tests/test-suites/difficulty-stratified-250-queries.json) - 250 queries across 3 difficulty tiers
- **Test Runner:** [`tests/analysis/difficulty_stratified_test.py`](../../tests/analysis/difficulty_stratified_test.py) - Main test execution script
- **Results:** [`tests/results/stratified/`](../../tests/results/stratified/) - Historical test results and analysis
- **Confusion Matrix:** [`tests/analysis/confusion_matrix.txt`](../../tests/analysis/confusion_matrix.txt) - Intent classification error patterns

**Latest Test Results (2025-10-08):**
- Overall: 77.9% (target: ≥85%)
- Easy: 95.9% ✅ | Medium: 67.8% ❌ | Hard: 60.0% ❌
- Graph intent: 66.0% (catastrophic collapse on medium tier → 43.8%)

## Training Data & Configuration

**Primary Dataset:** [`../../apex-memory-system/config/training-queries-v7.json`](../../apex-memory-system/config/training-queries-v7.json)

Latest logistics-specialized training dataset (314 queries):
- 80 route definitions (mixed difficulty: 10 easy + 5 medium + 5 hard per intent)
- 234 training queries (50% freight logistics + 50% generic)
- Specialized for OpenHaul and Origin Transport business operations

**Related Datasets:**
- `training-queries.json` - Base dataset (split from v7)
- `training-queries-split.json` - Train/test split version
- `difficulty-stratified-queries.json` - 250-query test suite

**See Also:** [Fine-Tuned Embeddings Project](../fine-tuned-embeddings/) - Leverages v7 dataset to train domain-specific embeddings for improved accuracy

## Implementation Phases

### Phase 1: Foundation (Week 1-2)
**Goal:** Replace keyword matching with semantic classification

**Deliverables:**
- ✅ Semantic Router integration (10ms intent classification)
- ✅ Query normalization and rewriting
- ✅ Analytics and logging infrastructure

**Code:** Lines 180-350 in IMPROVEMENT-PLAN.md

---

### Phase 2: Intelligent Routing (Week 3-4)
**Goal:** Add adaptive learning and GraphRAG

**Deliverables:**
- ✅ Contextual bandit for adaptive weights
- ✅ GraphRAG hybrid search (Neo4j vector index)
- ✅ Semantic caching (90%+ hit rate)

**Code:** Lines 352-520 in IMPROVEMENT-PLAN.md

---

### Phase 3: Agentic Evolution (Week 5-6)
**Goal:** Add autonomous decision-making

**Deliverables:**
- ✅ Complexity-based routing
- ✅ Multi-router architecture
- ✅ Self-correction loops

**Code:** Lines 522-690 in IMPROVEMENT-PLAN.md

---

### Phase 4: Advanced Features (Week 7-8)
**Goal:** Production optimization

**Deliverables:**
- ✅ Multimodal query support
- ✅ Real-time adaptation
- ✅ Production monitoring

**Code:** Lines 692-850 in IMPROVEMENT-PLAN.md

## Quick Wins (Immediate Implementation)

Can be implemented today without dependencies:

1. **Add Confidence Scores** (10 min)
   - Add confidence threshold to intent classification
   - Return confidence with results

2. **Comprehensive Logging** (20 min)
   - Log all routing decisions
   - Track query types and latencies

3. **Out-of-Scope Detection** (30 min)
   - Detect irrelevant queries
   - Return early with helpful message

4. **Query Normalization** (15 min)
   - Grammar correction
   - Spelling fixes
   - Standardization

5. **Timing Metrics** (15 min)
   - Track per-database latencies
   - Identify bottlenecks

**Total Time:** ~90 minutes
**Impact:** Better observability, immediate quality improvements

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Semantic Router latency | Benchmark first, fallback to keywords if >50ms |
| Neo4j vector performance | A/B test, keep Qdrant as primary |
| Adaptive weights instability | Gradual updates, min/max bounds |
| Query rewriting quality | Validation loop, user feedback |

## Success Metrics

### Week 2 (Phase 1 Complete)
- ✅ <10ms intent classification
- ✅ 80%+ routing accuracy
- ✅ Query normalization working

### Week 4 (Phase 2 Complete)
- ✅ 85%+ routing accuracy
- ✅ 90%+ cache hit rate
- ✅ GraphRAG working for relationship queries

### Week 6 (Phase 3 Complete)
- ✅ 90%+ routing accuracy
- ✅ Self-correction loops reducing errors
- ✅ Complexity analysis improving latency

### Week 8 (Phase 4 Complete)
- ✅ 85-92% routing accuracy
- ✅ <500ms P90 latency
- ✅ Production ready with monitoring

## Full Documentation

📋 **[Complete IMPROVEMENT-PLAN.md](IMPROVEMENT-PLAN.md)** (550+ lines)
- Executive summary
- All 10 critical flaws with code references
- Comprehensive code examples for each phase
- Performance benchmarks and comparisons
- References to all research documents

## Implementation Priority

**Start with:** Phase 1 (Foundation) - Highest impact, no dependencies

**Next:** Phase 2 (Intelligent Routing) - Builds on Phase 1

**Then:** Phase 3 (Agentic Evolution) - Requires Phase 1+2

**Finally:** Phase 4 (Advanced Features) - Polish and production readiness

---

**Ready to Begin:** ✅ All research complete, plan approved
**Next Step:** Create implementation branch, begin Phase 1
**Estimated Completion:** 8 weeks from start date
