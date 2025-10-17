# Project Requirements & Planning

**Project:** Fine-Tuned Embeddings for Logistics Query Routing
**Created:** 2025-10-09
**Status:** 🚀 Active Development
**Owner:** Richard Glaubitz (OpenHaul / Origin Transport)

---

## Executive Summary

**Problem:** Generic OpenAI embeddings don't understand freight logistics terminology, causing 67.8% accuracy on medium-difficulty queries (target: ≥85%).

**Solution:** Fine-tune BAAI/bge-base-en-v1.5 on domain-specific logistics queries using M4 hardware (the ONE capability OpenAI doesn't offer).

**Expected ROI:**
- +17 points medium tier accuracy (67.8% → 85%)
- +15 points hard tier accuracy (60.0% → 75%)
- +14 points graph intent accuracy (66.0% → 80%)
- Zero marginal cost (M4 owned, unlimited iterations)

**Timeline:** 5-6 days from dataset creation to production deployment

---

## Problem Definition

### Current Performance (OpenAI text-embedding-3-small)

| Metric | Current | Target | Gap |
|--------|---------|--------|-----|
| Medium Tier | 67.8% | ≥85% | **-17 points** |
| Hard Tier | 60.0% | ≥70% | -10 points |
| Graph Intent | 66.0% | ≥80% | **-14 points** |
| Overall | 77.9% | ≥85% | -7 points |

### Root Causes

**1. Semantic Gap (Primary Issue)**
- Route definitions: Clear, unambiguous phrasing
- Training queries: Vague, ambiguous phrasing
- OpenAI embeddings: Don't recognize these as same intent
- **Evidence:** Graph accuracy drops 48% from easy → medium tier

**2. Domain Terminology Gap (Secondary Issue)**
- Generic embeddings don't understand:
  - Freight logistics (detention, accessorials, kingpin, fifth wheel)
  - Business context (OpenHaul, Origin Transport operations)
  - Intent disambiguation ("use authentication" = graph, not semantic)

**3. Ultra-Low Learned Thresholds (Symptom)**
- Semantic gap causes fit() to learn permissive thresholds
- metadata: 0.0202 (94% below manual 0.32)
- temporal: 0.1010 (67% below manual 0.30)

---

## Requirements

### Functional Requirements

**FR-1: Domain-Specific Embeddings**
- Model must understand freight logistics terminology
- Must specialize for OpenHaul and Origin Transport business domains
- Must close semantic gap between route definitions and training queries

**FR-2: Intent Classification Accuracy**
- Medium tier ≥85% (currently 67.8%)
- Hard tier ≥75% (currently 60.0%)
- Graph intent ≥80% (currently 66.0%)
- Overall ≥85% (currently 77.9%)

**FR-3: Inference Performance**
- Embedding generation <100ms per query
- Model loading <10 seconds
- Memory footprint <4GB (fits in M4's 48GB unified memory)

**FR-4: Integration Compatibility**
- Must work with semantic-router library (HuggingFaceEncoder)
- Must maintain same API interface as OpenAIEncoder
- Must export in HuggingFace transformer format

### Non-Functional Requirements

**NFR-1: Training Performance**
- Training time <15 minutes per iteration (3 epochs, 314 samples)
- Enable rapid experimentation (train → test → iterate cycle)

**NFR-2: Cost Efficiency**
- Zero marginal cost per training run (M4 hardware owned)
- No API costs (vs OpenAI $0.00002/1k tokens)

**NFR-3: Maintainability**
- Model retraining pipeline documented
- Dataset versioning (v7.0 → v7.1 → ...)
- Reproducible training (fixed random seeds)

---

## Technical Approach

### Base Model Selection

**Chosen: BAAI/bge-base-en-v1.5**

| Criterion | bge-base-en-v1.5 | OpenAI text-embedding-3-small | Winner |
|-----------|------------------|-------------------------------|--------|
| Dimensions | 768 | 1536 | OpenAI (more capacity) |
| MTEB Score | 63.55 | 62.3 | **bge** (better baseline) |
| Fine-tuning | ✅ Supported | ❌ Not available | **bge (ONLY option)** |
| Parameters | 109M | Unknown | bge (known size) |
| M4 Support | ✅ MLX compatible | N/A | **bge** |
| Cost | $0 (local) | $0.00002/1k tokens | **bge (owned)** |

**Verdict:** bge-base-en-v1.5 is the ONLY option for fine-tuning, with comparable baseline performance.

### Training Methodology

**Loss Function: BatchHardTripletLoss**

```
Triplet = (anchor, positive, negative)
- anchor: User query
- positive: Correct route intent
- negative: Wrong route intents

Loss = max(0, distance(anchor, positive) - distance(anchor, negative) + margin)
```

**Why BatchHardTripletLoss:**
- Works with labeled data (our use case)
- Selects hardest negatives in batch (most informative)
- Outperforms softmax loss for similarity tasks
- Standard in sentence-transformers 2024 guides

**Training Configuration:**
```python
{
    "base_model": "BAAI/bge-base-en-v1.5",
    "loss": "BatchHardTripletLoss",
    "epochs": 3,
    "batch_size": 16,
    "learning_rate": 2e-5,
    "warmup_steps": 10,
    "evaluation_steps": 50,
    "margin": 0.5
}
```

### Dataset Architecture

**Logistics Dataset v7.0 (314 total queries)**

**Route Definitions (80 queries):**
- 20 per intent (graph, temporal, semantic, metadata)
- Mixed difficulty: 10 easy + 5 medium + 5 hard per intent
- **Purpose:** Define what each route "looks like"

**Training Data (234 queries):**
- 117 generic queries (keep generalization)
- 117 logistics-specific queries (domain specialization)
- Medium/hard difficulty (close semantic gap)
- **Purpose:** Teach model to generalize and disambiguate

**Logistics Specialization Examples:**
- Graph: "show all equipment owned by OpenHaul"
- Temporal: "track OpenHaul revenue from Q1 to Q4"
- Semantic: "find information about DOT compliance"
- Metadata: "filter trucks where status=available and mileage < 100000"

### Hardware Specifications

**M4 MacBook Pro:**
- GPU: 40-core (parallel matrix operations)
- RAM: 48GB unified (no CPU↔GPU transfer overhead)
- Neural Engine: 16-core, 38 TOPS (transformer-optimized)
- Bandwidth: 500GB/s (fast model loading)

**Expected Performance:**
- Model loading: <10 seconds
- Training (3 epochs, 314 samples): 5-10 minutes
- Inference: 50+ queries/second
- **Total iteration cycle: <15 minutes**

---

## Success Criteria

### Minimum Viable

| Metric | Current | Minimum Target | Status |
|--------|---------|----------------|--------|
| Medium Tier | 67.8% | ≥85% | 🎯 Primary goal |
| Hard Tier | 60.0% | ≥75% | 🎯 Primary goal |
| Graph Intent | 66.0% | ≥80% | 🎯 Primary goal |
| Inference Latency | N/A | <100ms | ⚡ Performance req |

### Stretch Goals

| Metric | Current | Stretch Target |
|--------|---------|----------------|
| Overall Accuracy | 77.9% | ≥90% |
| All Intents | 66-93.4% | ≥85% each |
| Training Time | N/A | <10 minutes |

### Validation Approach

**1. Stratified Test (250 queries)**
- Same test set as OpenAI baseline
- Difficulty tiers: 100 easy + 100 medium + 50 hard
- All 4 intents represented

**2. Confusion Matrix Analysis**
- Compare misclassification patterns vs OpenAI
- Identify remaining failure modes
- Guide dataset v7.1 improvements

**3. Latency Benchmarking**
- Measure embedding generation time
- Ensure <100ms per query (no user-visible slowdown)

---

## Implementation Plan

### Phase 1: Dataset Creation (Day 1)

**Deliverables:**
- `config/training-queries-v7.json` (314 queries)
- 80 route definitions (mixed difficulty)
- 234 training queries (logistics-specialized)

**Tasks:**
- [ ] Define 60 logistics-specific queries (15 per intent)
- [ ] Mix difficulty levels in route definitions
- [ ] Add freight terminology throughout
- [ ] Validate JSON structure

### Phase 2: Training Infrastructure (Day 2)

**Deliverables:**
- `training/train_embeddings.py` (main script)
- `training/export_model.py` (HuggingFace export)
- `training/evaluate.py` (validation utilities)

**Tasks:**
- [ ] Implement triplet data loader
- [ ] Configure BatchHardTripletLoss
- [ ] Add MLX optimization (if available)
- [ ] Create evaluation pipeline

### Phase 3: First Training Run (10 minutes)

**Deliverables:**
- `models/apex-logistics-embeddings-v1/` (trained model)
- Training logs with loss curves
- Validation metrics on held-out set

**Tasks:**
- [ ] Run training (3 epochs, 314 samples)
- [ ] Monitor loss convergence
- [ ] Export model in HuggingFace format

### Phase 4: Integration (2 hours)

**Deliverables:**
- Updated `semantic_classifier.py` with HuggingFaceEncoder support
- Backward compatibility with OpenAIEncoder (config flag)

**Tasks:**
- [ ] Add HuggingFace encoder option
- [ ] Update initialization logic
- [ ] Test end-to-end query flow

### Phase 5: Validation (2 hours)

**Deliverables:**
- Stratified test results (250 queries)
- Comparison report vs OpenAI baseline
- Confusion matrix analysis

**Tasks:**
- [ ] Clear query cache
- [ ] Run full stratified test
- [ ] Generate comparison metrics
- [ ] Identify failure patterns

### Phase 6: Iteration (2-3 days)

**Deliverables:**
- Dataset v7.1 (if needed)
- Retrained model v2 (if needed)
- Production-ready model

**Tasks:**
- [ ] Analyze failure modes
- [ ] Refine dataset based on errors
- [ ] Retrain with updated data
- [ ] Repeat until success criteria met

---

## Resource Requirements

### Hardware

| Resource | Requirement | Available (M4) | Status |
|----------|-------------|----------------|--------|
| GPU Cores | ≥16 | 40 | ✅ |
| RAM | ≥16GB | 48GB | ✅ |
| Storage | ≥10GB | 500GB+ | ✅ |
| Neural Engine | Optional | 16-core (38 TOPS) | ✅ Bonus |

### Software

| Dependency | Version | Purpose |
|------------|---------|---------|
| Python | ≥3.10 | Runtime |
| sentence-transformers | ≥2.2.0 | Fine-tuning framework |
| torch | ≥2.0.0 | ML backend |
| transformers | ≥4.30.0 | Model architecture |
| datasets | ≥2.12.0 | Data loading |
| mlx | latest | M4 optimization (optional) |

### Time Investment

| Phase | Estimated | Actual | Notes |
|-------|-----------|--------|-------|
| Dataset Creation | 1 day | TBD | Manual curation |
| Training Scripts | 1 day | TBD | Mostly boilerplate |
| First Training | 10 min | TBD | M4 fast |
| Integration | 2 hours | TBD | Simple encoder swap |
| Validation | 2 hours | TBD | Automated testing |
| Iteration | 2-3 days | TBD | Depends on first results |
| **TOTAL** | **5-6 days** | TBD | - |

---

## Risks & Mitigation

### Technical Risks

**Risk 1: Overfitting to Logistics Domain**
- **Probability:** Medium
- **Impact:** High (breaks generic queries)
- **Mitigation:** Keep 50% generic queries in training data, validate on generic test set

**Risk 2: Model Size Causes Latency**
- **Probability:** Low
- **Impact:** Medium (user-visible slowdown)
- **Mitigation:** Benchmark inference time, consider distillation if >100ms

**Risk 3: M4 Compatibility Issues**
- **Probability:** Low
- **Impact:** Medium (slower training)
- **Mitigation:** Fallback to standard PyTorch (10-15 min training instead of 5-10 min)

**Risk 4: Insufficient Training Data**
- **Probability:** Medium
- **Impact:** Medium (doesn't hit accuracy targets)
- **Mitigation:** Iterative dataset expansion (v7.0 → v7.1 → v7.2)

### Operational Risks

**Risk 5: API Compatibility Breaking**
- **Probability:** Low
- **Impact:** High (breaks existing queries)
- **Mitigation:** Maintain backward compatibility with OpenAIEncoder via config flag

**Risk 6: Model Deployment Complexity**
- **Probability:** Low
- **Impact:** Medium (manual deployment)
- **Mitigation:** Document model paths, create deployment script

---

## Dependencies

### Upstream Dependencies

- ✅ M4 MacBook Pro (hardware owned)
- ✅ sentence-transformers library (stable, 2024)
- ✅ BAAI/bge-base-en-v1.5 (public, permissive license)
- ✅ Stratified test suite (already implemented)

### Downstream Dependencies

- semantic_classifier.py (requires HuggingFaceEncoder support)
- Query router (depends on semantic_classifier)
- Stratified test script (validation)

---

## Approval Checklist

### Research Complete
- [x] Identified root cause (semantic gap + domain terminology)
- [x] Evaluated alternatives (fine-tuning is ONLY option for OpenAI limitation)
- [x] Researched technical approach (BatchHardTripletLoss, sentence-transformers)
- [x] Validated M4 hardware capabilities (sufficient for training)

### Requirements Defined
- [x] Functional requirements documented (FR-1 through FR-4)
- [x] Non-functional requirements documented (NFR-1 through NFR-3)
- [x] Success criteria defined (minimum + stretch goals)
- [x] Validation approach specified (stratified test + confusion matrix)

### Plan Validated
- [x] Timeline realistic (5-6 days, mostly automated)
- [x] Resources available (M4 hardware, dependencies)
- [x] Risks identified and mitigated
- [x] Dependencies documented

**Approved for implementation:** ✅

---

## Appendix: Research References

**Tier 1 Sources (Official Documentation):**
1. [HuggingFace: Train Sentence Transformers](https://huggingface.co/blog/train-sentence-transformers) - Official 2024 guide
2. [Sentence-Transformers: Loss Functions](https://www.sbert.net/docs/package_reference/sentence_transformer/losses.html) - BatchHardTripletLoss docs
3. [BAAI/bge-base-en-v1.5 Model Card](https://huggingface.co/BAAI/bge-base-en-v1.5) - Base model specifications

**Tier 2 Sources (Research & Examples):**
4. [Fine-tuning Embeddings for Domain-Specific NLP](https://blog.premai.io/fine-tuning-embeddings-for-domain-specific-nlp/) - Domain specialization
5. [Multiple Negatives Ranking Loss](https://www.pinecone.io/learn/series/nlp/fine-tune-sentence-transformers-mnr/) - Advanced triplet loss
6. [NLP and Logistics](https://packagex.io/blog/nlp-and-logistics) - Logistics NLP applications

---

*Last updated: 2025-10-09*
