# Testing Guide - Fine-Tuned Embeddings

**Project:** Fine-Tuned Embeddings for Logistics Query Routing
**Purpose:** Validate that fine-tuned embeddings improve accuracy vs OpenAI baseline

---

## Quick Start

### 1. Train the Model (10 minutes)

```bash
cd /Users/richardglaubitz/Projects/Apex-Memory-System-Development/upgrades/active/fine-tuned-embeddings/training

# Train model (5-10 minutes on M4)
python3 train_embeddings.py \
  --dataset /Users/richardglaubitz/Projects/apex-memory-system/config/training-queries-v7.json \
  --output ../models/apex-logistics-embeddings-v1 \
  --epochs 3

# Verify model exported correctly
python3 export_model.py \
  --input ../models/apex-logistics-embeddings-v1
```

### 2. Enable Custom Embeddings

**Option A: Environment Variable (Recommended)**

```bash
# Add to ~/.zshrc or ~/.bashrc
export CUSTOM_EMBEDDING_MODEL=/Users/richardglaubitz/Projects/Apex-Memory-System-Development/upgrades/active/fine-tuned-embeddings/models/apex-logistics-embeddings-v1

# Reload shell
source ~/.zshrc
```

**Option B: Docker Environment Variable**

```bash
# In docker-compose.yml, add to api service:
environment:
  - CUSTOM_EMBEDDING_MODEL=/app/upgrades/active/fine-tuned-embeddings/models/apex-logistics-embeddings-v1
```

### 3. Run Stratified Test

```bash
cd /Users/richardglaubitz/Projects/apex-memory-system

# Clear query cache
curl -s -X DELETE http://localhost:8000/api/v1/query/cache

# Run full test (250 queries, ~1 hour)
python3 scripts/difficulty_stratified_test.py 2>&1 | tee /tmp/stratified_test_finetuned_v1.txt

# View results
tail -150 /tmp/stratified_test_finetuned_v1.txt
```

---

## Success Criteria

### Minimum Viable (Pass/Fail)

| Metric | Baseline (OpenAI) | Minimum Target | Status |
|--------|------------------|----------------|--------|
| **Medium Tier** | 67.8% | ≥85% | 🎯 Primary goal |
| **Hard Tier** | 60.0% | ≥75% | 🎯 Primary goal |
| **Graph Intent** | 66.0% | ≥80% | 🎯 Primary goal |
| **Inference Latency** | N/A | <100ms | ⚡ Performance req |

### Stretch Goals

| Metric | Baseline (OpenAI) | Stretch Target |
|--------|------------------|----------------|
| Overall Accuracy | 77.9% | ≥90% |
| All Intents | 66-93.4% | ≥85% each |
| Training Time | N/A | <10 minutes |

---

## Validation Process

### Phase 1: Baseline Comparison

**Run with OpenAI embeddings (baseline):**

```bash
# Ensure CUSTOM_EMBEDDING_MODEL is NOT set
unset CUSTOM_EMBEDDING_MODEL

# Run test
python3 scripts/difficulty_stratified_test.py 2>&1 | tee /tmp/stratified_test_openai_baseline.txt
```

**Extract baseline metrics:**

```bash
# Overall accuracy
grep "Overall Accuracy" /tmp/stratified_test_openai_baseline.txt

# Tier accuracy
grep -A 5 "Accuracy by Difficulty" /tmp/stratified_test_openai_baseline.txt

# Intent accuracy
grep -A 6 "Overall Intent Accuracy" /tmp/stratified_test_openai_baseline.txt
```

### Phase 2: Fine-Tuned Model Test

**Run with fine-tuned embeddings:**

```bash
# Set custom model
export CUSTOM_EMBEDDING_MODEL=/Users/richardglaubitz/Projects/Apex-Memory-System-Development/upgrades/active/fine-tuned-embeddings/models/apex-logistics-embeddings-v1

# Clear cache
curl -s -X DELETE http://localhost:8000/api/v1/query/cache

# Run test
python3 scripts/difficulty_stratified_test.py 2>&1 | tee /tmp/stratified_test_finetuned_v1.txt
```

**Extract fine-tuned metrics:**

```bash
# Overall accuracy
grep "Overall Accuracy" /tmp/stratified_test_finetuned_v1.txt

# Tier accuracy
grep -A 5 "Accuracy by Difficulty" /tmp/stratified_test_finetuned_v1.txt

# Intent accuracy
grep -A 6 "Overall Intent Accuracy" /tmp/stratified_test_finetuned_v1.txt
```

### Phase 3: Comparison Analysis

**Create comparison table:**

```bash
# Run comparison script (create if needed)
python3 scripts/compare_test_results.py \
  --baseline /tmp/stratified_test_openai_baseline.txt \
  --finetuned /tmp/stratified_test_finetuned_v1.txt \
  --output /tmp/embedding_comparison.txt
```

**Manual comparison:**

| Metric | OpenAI Baseline | Fine-Tuned | Improvement | Pass? |
|--------|----------------|------------|-------------|-------|
| Medium Tier | 67.8% | ___ % | ___ points | ≥85%? |
| Hard Tier | 60.0% | ___ % | ___ points | ≥75%? |
| Graph Intent | 66.0% | ___ % | ___ points | ≥80%? |
| Overall | 77.9% | ___ % | ___ points | ≥85%? |

---

## Interpreting Results

### ✅ Success Indicators

**Accuracy improvements:**
- Medium tier +17 points or more (67.8% → 85%+)
- Hard tier +15 points or more (60.0% → 75%+)
- Graph intent +14 points or more (66.0% → 80%+)

**Confusion matrix improvements:**
- Fewer graph → semantic errors
- Fewer temporal → semantic errors
- Better disambiguation on vague queries

**Example success patterns:**
- "show services that use authentication" → graph ✅ (was semantic ❌)
- "find resources assigned to migration" → graph ✅ (was metadata ❌)
- "compare Q1 vs Q2" → temporal ✅ (was semantic ❌)

### ⚠️ Warning Signs

**Minimal improvement (<5 points):**
- Dataset may need more logistics queries
- Epochs may need adjustment (try 5 epochs)
- Training may have converged too quickly

**Regression (accuracy decreases):**
- Model may be overfitting to logistics domain
- Need more generic queries in training data
- Consider reducing epochs to 2

**High inference latency (>100ms):**
- HuggingFace encoder may be slower than OpenAI
- Consider model distillation or quantization

### ❌ Failure Modes

**If medium tier <85%:**
1. Check confusion matrix - which intents are failing?
2. Add more training examples for failing intents
3. Try dataset v7.1 with intent-specific improvements

**If graph intent <80%:**
1. Add more relationship-specific queries
2. Include more freight-specific relationships (truck-driver, vendor-service)
3. Train for 5 epochs instead of 3

**If latency >100ms:**
1. Profile inference time with test query
2. Consider switching to quantized model
3. Fall back to OpenAI if speed is critical

---

## Troubleshooting

### Model Not Loading

```bash
# Check model path exists
ls -la /Users/richardglaubitz/Projects/Apex-Memory-System-Development/upgrades/active/fine-tuned-embeddings/models/apex-logistics-embeddings-v1

# Check model files
ls -la /Users/richardglaubitz/Projects/Apex-Memory-System-Development/upgrades/active/fine-tuned-embeddings/models/apex-logistics-embeddings-v1/0_Transformer/

# Test loading directly
python3 -c "from sentence_transformers import SentenceTransformer; m = SentenceTransformer('/Users/richardglaubitz/Projects/Apex-Memory-System-Development/upgrades/active/fine-tuned-embeddings/models/apex-logistics-embeddings-v1'); print('✅ Model loaded')"
```

### API Not Using Custom Model

```bash
# Check environment variable set
echo $CUSTOM_EMBEDDING_MODEL

# Check logs for "Using custom embedding model"
docker logs apex-memory-system_api_1 | grep "custom embedding"

# Restart API to pick up environment variable
cd /Users/richardglaubitz/Projects/apex-memory-system/docker
docker-compose restart api
```

### Training Fails

```bash
# Check dependencies installed
pip list | grep sentence-transformers
pip list | grep torch

# Install if missing
pip install sentence-transformers torch datasets

# Check dataset format
python3 -c "import json; data = json.load(open('/Users/richardglaubitz/Projects/apex-memory-system/config/training-queries-v7.json')); print(f'✅ {len(data[\"training_data\"][\"queries\"])} queries loaded')"
```

---

## Performance Benchmarking

### Inference Latency Test

```python
# Create benchmark script: benchmarks/embedding_latency.py
from sentence_transformers import SentenceTransformer
import time

model_path = "/Users/richardglaubitz/Projects/Apex-Memory-System-Development/upgrades/active/fine-tuned-embeddings/models/apex-logistics-embeddings-v1"
model = SentenceTransformer(model_path)

test_queries = [
    "show all trucks owned by OpenHaul",
    "track OpenHaul revenue from Q1 to Q4",
    "find information about DOT compliance",
    "filter trucks where status = available"
]

# Warm-up
_ = model.encode(test_queries[0])

# Benchmark
times = []
for query in test_queries * 25:  # 100 total queries
    start = time.time()
    _ = model.encode(query)
    times.append((time.time() - start) * 1000)  # Convert to ms

print(f"Mean latency: {sum(times)/len(times):.2f}ms")
print(f"P50 latency: {sorted(times)[len(times)//2]:.2f}ms")
print(f"P90 latency: {sorted(times)[int(len(times)*0.9)]:.2f}ms")
print(f"P99 latency: {sorted(times)[int(len(times)*0.99)]:.2f}ms")
```

**Target:** <100ms per query (P90)

---

## Next Steps After Testing

### If Tests Pass ✅

1. **Deploy to production:**
   - Set CUSTOM_EMBEDDING_MODEL in .env
   - Restart API
   - Monitor accuracy in production

2. **Document results:**
   - Update README.md with actual improvements
   - Add before/after comparison charts
   - Archive test results

3. **Iterate:**
   - Try dataset v7.1 with more logistics queries
   - Experiment with 5 epochs
   - Test on real user queries

### If Tests Fail ❌

1. **Analyze failures:**
   - Review confusion matrix
   - Identify specific failing patterns
   - Check if logistics specialization hurts generic queries

2. **Refine dataset:**
   - Create v7.1 with fixes
   - Add more examples for failing intents
   - Balance logistics vs generic queries

3. **Retrain:**
   - Adjust hyperparameters (epochs, batch size)
   - Try different base models (bge-large, etc.)
   - Monitor training loss curves

---

*Last updated: 2025-10-09*
