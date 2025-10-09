# Fine-Tuned Embeddings for Logistics Query Routing

**Status:** 🚀 Active Development | **Priority:** High | **Timeline:** 1 week

Domain-specific embedding model fine-tuned for freight logistics and query intent classification, powered by M4 hardware.

## Project Overview

This project creates a custom embedding model specialized for:
- **Freight logistics domain** (OpenHaul, Origin Transport business operations)
- **Query intent classification** (graph, temporal, semantic, metadata routes)
- **Semantic gap resolution** (ambiguous query disambiguation)

**Key Innovation:** Leverage M4 MacBook's Neural Engine (38 TOPS) to fine-tune embeddings locally - the ONE thing OpenAI doesn't allow you to do via API.

---

## Problem Statement

### Current State (OpenAI text-embedding-3-small)

**Overall Accuracy:** 77.9% (183/235 correct)

| Difficulty | Accuracy | Status |
|------------|----------|--------|
| Easy | 95.9% | ✅ Pass (≥95%) |
| Medium | 67.8% | ❌ Fail (≥85%) |
| Hard | 60.0% | ❌ Fail (≥70%) |

**Intent-Specific Failures:**

| Intent | Accuracy | Correct/Total | Key Issues |
|--------|----------|---------------|------------|
| graph | ❌ 66.0% | 35/53 | **Catastrophic collapse** on ambiguous queries (43.8% medium tier) |
| temporal | ❌ 78.0% | 46/59 | 9 queries misclassified as semantic |
| metadata | ❌ 72.6% | 45/62 | 7 queries confused with temporal |
| semantic | ⚠️ 93.4% | 57/61 | Robust but still has edge cases |

### Root Causes

**1. Semantic Gap Problem**
- Route definitions use clear, unambiguous phrasing (e.g., "show all dependencies between X and Y")
- Training queries use vague, ambiguous phrasing (e.g., "show connections", "find related stuff")
- OpenAI embeddings don't understand they represent the SAME intent
- **Evidence:** Graph accuracy drops 48% from easy → medium tier (91.7% → 43.8%)

**2. Domain Terminology Misunderstanding**
- Generic embeddings don't understand freight logistics context:
  - "show services that use authentication" → misclassified as semantic (should be graph)
  - "find resources assigned to migration" → misclassified as metadata (should be graph)
  - "compare Q1 vs Q2" → misclassified as semantic (should be temporal)

**3. Ultra-Low Learned Thresholds**
- Semantic gap causes fit() to learn overly permissive thresholds:
  - metadata: 0.0202 (94% lower than manual 0.32)
  - temporal: 0.1010 (67% lower than manual 0.30)
- Results in false positives on ambiguous queries

### Example Failures

**Medium Tier (32.2% failure rate):**
```
"show services that use the authentication module"
→ Expected: graph | Actual: semantic
→ Scores: graph: 0.601 | semantic: 0.504
→ Issue: Weaker "use" signal vs explicit "connected to"

"find all resources assigned to the cloud migration"
→ Expected: graph | Actual: metadata
→ Scores: semantic: 0.469 | metadata: 0.440 | graph: 0.410
→ Issue: "assigned" + "resources" triggers filtering
```

**Hard Tier (40.0% failure rate):**
```
"find things related to infrastructure"
→ Expected: graph | Actual: semantic
→ Scores: semantic: 0.453 | graph: 0.368
→ Issue: Ultra-vague "things related" triggers semantic search

"show aligned content"
→ Expected: semantic | Actual: metadata
→ Scores: semantic: 0.376 | metadata: 0.376 (EXACT TIE!)
→ Issue: Metadata wins by chance
```

---

## Solution: Fine-Tune Domain-Specific Embeddings

### Why Fine-Tuning

**Addresses root cause at embedding level:**

1. **Teaches domain terminology** - Model learns that in OUR context:
   - "show services that use X" = graph relationship
   - "find resources assigned to Y" = graph relationship
   - "compare A vs B" = temporal comparison

2. **Closes semantic gap** - Fine-tuned embeddings understand that:
   - "show connections" ≈ "show all dependencies between"
   - "find related stuff" ≈ "find all systems that depend on"
   - "what changed" ≈ "show modifications to X over time"

3. **Learns freight logistics context** - Specializes for:
   - Truck terminology (Freightliner, kingpin, fifth wheel, landing gear)
   - Freight brokerage (detention, accessorials, bill of lading, freight broker authority)
   - Operations (DOT compliance, ELD mandate, FMCSA, route optimization)
   - Business entities (OpenHaul, Origin Transport)

### Technical Approach

**Base Model:** BAAI/bge-base-en-v1.5
- 768 dimensions (vs OpenAI's 1536)
- 109M parameters
- MTEB score: 63.55 (vs OpenAI's 62.3)
- **Designed for fine-tuning** (used in most SOTA fine-tuned models)

**Training Method:** Triplet Loss with BatchHardTripletLoss
- Anchor: User query
- Positive: Correct route intent
- Negative: Wrong route intents
- Loss function: Maximize distance between positive and negatives

**Dataset:** Logistics v7.0 (314 total queries)
- 80 route definitions (20 per intent, mixed difficulty)
- 234 training queries (medium/hard, logistics-specialized)
- Freight-specific terminology throughout

**Hardware:** M4 MacBook Pro
- 40-core GPU
- 48GB unified memory
- 16-core Neural Engine (38 TOPS)
- 500GB/s memory bandwidth
- **Training time:** 5-10 minutes for 3 epochs

---

## Expected Improvements

### Accuracy Gains

| Metric | Current | Target | Improvement |
|--------|---------|--------|-------------|
| **Medium Tier** | 67.8% | 85%+ | +17 points |
| **Hard Tier** | 60.0% | 75%+ | +15 points |
| **Graph Intent** | 66.0% | 80%+ | +14 points |
| **Overall** | 77.9% | 85-90% | +7-12 points |

### Intent-Specific Improvements

**Graph Routes** (biggest improvement):
- Current: 66.0% (35/53 correct)
- Target: 80%+ (42+/53 correct)
- **+14 points** - Disambiguates relationship queries

**Temporal Routes**:
- Current: 78.0% (46/59 correct)
- Target: 85%+ (50+/59 correct)
- **+7 points** - Reduces semantic confusion

**Metadata Routes**:
- Current: 72.6% (45/62 correct)
- Target: 80%+ (50+/62 correct)
- **+7 points** - Better filtering vs temporal distinction

**Semantic Routes** (already strong):
- Current: 93.4% (57/61 correct)
- Target: 95%+ (58+/61 correct)
- **+2 points** - Eliminates edge cases

### Research Support

**Tier 1 Evidence (HuggingFace Documentation):**
- bge-base-en-v1.5 supports contrastive fine-tuning
- Sentence-transformers library provides fine-tuning API
- Triplet loss with positive/negative pairs is standard

**Tier 1 Evidence (Sentence-Transformers 2024):**
- BatchHardTripletLoss for labeled data (our use case)
- Multiple Negatives Ranking (MNR) extends triplet loss
- Models trained with MNR outperform softmax loss

**Tier 2 Evidence (Logistics NLP Research):**
- Domain-specific fine-tuning improves accuracy 10-20% for specialized terminology
- Freight logistics has unique vocabulary requiring specialized embeddings

---

## M4 Hardware Advantage

### Why Local Fine-Tuning Matters

**The ONE thing OpenAI doesn't offer:**
- OpenAI API: Cannot fine-tune text-embedding-3-small (not available)
- HuggingFace embeddings: CAN be fine-tuned locally
- **This is the unique value of M4 hardware**

### M4 Neural Engine Specifications

| Spec | Value | Advantage |
|------|-------|-----------|
| GPU Cores | 40-core | Parallel matrix operations |
| RAM | 48GB unified | No CPU↔GPU memory transfer overhead |
| Bandwidth | 500GB/s | Fast model loading and training |
| Neural Engine | 16-core (38 TOPS) | Optimized for transformer operations |

### Training Performance

**Expected with MLX (Apple's ML framework):**
- Model loading: <10 seconds
- Training 3 epochs (314 samples): 5-10 minutes
- Inference speed: 50+ queries/second
- Total iteration cycle: **<15 minutes start to finish**

**Compare to alternatives:**
- Google Colab (free tier): 30-45 min + queue wait
- Cloud GPU (AWS p3.2xlarge): $3/hour + setup overhead
- OpenAI fine-tuning: **Not available** for embeddings

### Cost Analysis

| Approach | Hardware | Cost per Iteration | Limitation |
|----------|----------|-------------------|------------|
| **M4 Local** | Owned | $0 | None |
| Google Colab | Cloud (T4 GPU) | $0 (w/ queue) or $10/month | 30-45 min + limited hours |
| AWS SageMaker | Cloud (ml.g4dn.xlarge) | $0.526/hour | Setup complexity |
| OpenAI API | Cloud | N/A | **Not offered** |

**Bottom line:** M4 enables **unlimited experimentation at zero marginal cost** for the ONE capability OpenAI won't provide.

---

## Quick Start

### 1. Install Dependencies

```bash
# Install sentence-transformers with MLX support
pip install sentence-transformers torch datasets mlx

# Verify installation
python -c "import sentence_transformers; print(f'✅ Version: {sentence_transformers.__version__}')"
```

### 2. Train the Model

```bash
# From project root
cd upgrades/active/fine-tuned-embeddings/

# Run training (5-10 minutes on M4)
python training/train_embeddings.py \
  --dataset ../../config/training-queries-v7.json \
  --base-model BAAI/bge-base-en-v1.5 \
  --output models/apex-logistics-embeddings-v1 \
  --epochs 3 \
  --batch-size 16
```

### 3. Export for Semantic-Router

```bash
# Export model in HuggingFace format
python training/export_model.py \
  --input models/apex-logistics-embeddings-v1 \
  --output models/apex-logistics-embeddings-v1-export
```

### 4. Integrate with Query Router

Update `apex-memory-system/src/apex_memory/query_router/semantic_classifier.py`:

```python
from semantic_router.encoders import HuggingFaceEncoder

# Replace OpenAIEncoder with custom model
self.encoder = HuggingFaceEncoder(
    name='/Users/richardglaubitz/Projects/Apex-Memory-System-Development/upgrades/active/fine-tuned-embeddings/models/apex-logistics-embeddings-v1'
)
```

### 5. Run Stratified Test

```bash
# Clear cache and test
cd /Users/richardglaubitz/Projects/apex-memory-system
curl -s -X DELETE http://localhost:8000/api/v1/query/cache

# Run full stratified test (250 queries)
python3 scripts/difficulty_stratified_test.py 2>&1 | tee /tmp/stratified_test_finetuned_v1.txt

# View results
tail -100 /tmp/stratified_test_finetuned_v1.txt
```

---

## Project Structure

```
fine-tuned-embeddings/
├── README.md                    # This file
├── PRP.md                       # Project Requirements & Planning
├── training/
│   ├── train_embeddings.py      # Main training script
│   ├── export_model.py          # Export for semantic-router
│   └── evaluate.py              # Evaluation utilities
└── models/
    └── apex-logistics-embeddings-v1/  # Trained model output
        ├── config.json
        ├── pytorch_model.bin
        └── tokenizer/
```

---

## Success Criteria

**Minimum viable:**
- ✅ Medium tier ≥85% (current: 67.8%)
- ✅ Hard tier ≥75% (current: 60.0%)
- ✅ Graph intent ≥80% (current: 66.0%)

**Stretch goals:**
- ⭐ Overall ≥90% (current: 77.9%)
- ⭐ All intents ≥85%
- ⭐ <100ms inference latency

**Validation:**
- Run full stratified test (250 queries)
- Compare confusion matrix vs OpenAI baseline
- Measure latency (should be <100ms for embedding generation)

---

## Cross-References

**Related Projects:**
- [Query Router Improvement Plan](../query-router/) - Broader query routing enhancements
- [Saga Pattern Enhancement](../saga-pattern-enhancement/) - Transaction reliability

**Research Foundation:**
- [HuggingFace: Train Sentence Transformers](https://huggingface.co/blog/train-sentence-transformers) - Official guide (2024)
- [Sentence-Transformers: Triplet Loss](https://www.sbert.net/docs/package_reference/sentence_transformer/losses.html#tripletloss) - Loss function docs
- [Fine-tuning Embeddings for Domain-Specific NLP](https://blog.premai.io/fine-tuning-embeddings-for-domain-specific-nlp/) - Domain specialization research

**Datasets:**
- [Logistics Dataset v7.0](../../config/training-queries-v7.json) - Training data
- [Stratified Test Queries](../../config/difficulty-stratified-queries.json) - Validation set

---

## Timeline

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| **Phase 1: Dataset Creation** | 1 day | Logistics v7.0 with 314 queries |
| **Phase 2: Training Script** | 1 day | train_embeddings.py with triplet loss |
| **Phase 3: Model Training** | 10 min | First trained model |
| **Phase 4: Integration** | 2 hours | semantic_classifier.py updated |
| **Phase 5: Testing** | 2 hours | Stratified test comparison |
| **Phase 6: Iteration** | 2-3 days | Refinement based on results |

**Total:** 5-6 days from start to production-ready model

---

## Next Steps

**Immediate (this session):**
1. ✅ Create project structure
2. ✅ Write README (this document)
3. 🚀 Write PRP.md
4. 🚀 Create logistics dataset v7.0
5. 🚀 Write training scripts

**Next session:**
1. Run first training pass
2. Integrate with semantic_classifier
3. Run stratified test
4. Compare results vs OpenAI baseline

---

*Last updated: 2025-10-09*
