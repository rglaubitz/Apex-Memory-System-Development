# Query Router Testing Framework

**Location**: `Apex-Memory-System-Development/tests/`
**Purpose**: Comprehensive testing framework for semantic intent classification accuracy

This directory contains test suites, execution results, and analysis tools for validating query router performance across different difficulty levels and intent types.

## Directory Structure

```
tests/
├── README.md                    # This file
├── test-suites/                 # Query test definitions
│   ├── baseline-30-queries.json
│   └── difficulty-stratified-250-queries.json
├── results/                     # Test execution results
│   ├── baseline/
│   │   └── 2025-10-08-baseline-results.json
│   └── stratified/
│       ├── 2025-10-08-stratified-results.json
│       └── 2025-10-08-stratified-summary.txt
└── analysis/                    # Analysis scripts and outputs
    ├── difficulty_stratified_test.py
    ├── confusion_matrix.txt
    └── (future: performance visualizations)
```

## Test Categories

### 1. Test Suites (`test-suites/`)

Test query definitions with expected intent labels and difficulty ratings.

**Baseline Test (30 queries)**
- 7-8 queries per intent type (graph, temporal, semantic, metadata)
- Validates core classification accuracy
- Used for regression testing after changes

**Difficulty-Stratified Test (250 queries)**
- Easy: 100 queries with clear intent signals
- Medium: 100 queries with some ambiguity
- Hard: 50 queries with multiple overlapping intents
- Tests robustness across query complexity

### 2. Results (`results/`)

Raw test execution results and summary reports organized by test type and date.

**Result files contain**:
- Query text and expected intent
- Actual classified intent
- Databases used for routing
- Latency measurements
- Success/failure status
- Timestamp

### 3. Analysis (`analysis/`)

Scripts and outputs for analyzing test results.

**Tools**:
- `difficulty_stratified_test.py` - Main test runner
- `confusion_matrix.txt` - Intent classification confusion analysis
- Performance visualization scripts (future)

## How to Run Tests

### Prerequisites

1. Start all services:
   ```bash
   cd apex-memory-system/docker
   docker-compose up -d
   ```

2. Verify API is running:
   ```bash
   curl http://localhost:8000/health
   ```

### Run Baseline Test (30 queries)

```bash
cd apex-memory-system
python scripts/test_semantic_router.py
```

**Expected results**:
- Overall accuracy: ≥95%
- All intent types: ≥90%
- Latency P50: <500ms

### Run Difficulty-Stratified Test (250 queries)

```bash
cd apex-memory-system
python scripts/difficulty_stratified_test.py
```

**Results location**: `monitoring/stratified/` (will be moved to `tests/results/stratified/`)

**Success criteria**:
- Easy tier: ≥95% accuracy
- Medium tier: ≥85% accuracy
- Hard tier: ≥70% accuracy
- Overall: ≥85% accuracy

## Understanding Test Results

### Intent Types

| Intent | Description | Databases Used |
|--------|-------------|----------------|
| **graph** | Relationships, connections, networks | Neo4j, Graphiti |
| **temporal** | Time-based patterns, history, trends | Graphiti |
| **semantic** | Meaning-based search, similarity | Qdrant, PostgreSQL |
| **metadata** | Structured filters, attributes | PostgreSQL |

### Difficulty Tiers

**Easy**: Clear intent signals with unambiguous terminology
- Example: "which servers are directly connected to database-prod"
- Clear keyword: "connected to" → graph intent

**Medium**: Some ambiguity or overlapping characteristics
- Example: "show dependencies between microservices"
- "dependencies" could mean graph relationships OR semantic topics

**Hard**: Multiple overlapping intents or complex phrasing
- Example: "how have the connections between teams evolved over time"
- Contains graph ("connections"), temporal ("evolved over time"), and semantic ("teams") signals

### Confusion Matrix

Shows which intents are being confused with each other.

**Example**:
```
Graph queries misclassified as:
  - semantic: 11 queries  (e.g., "dependencies" interpreted as topic)
  - temporal: 10 queries  (e.g., "trace path" interpreted as timeline)
  - metadata: 7 queries   (e.g., "filter by" interpreted as attribute)
```

**Common patterns**:
- Graph → Semantic: Relationship terminology misinterpreted as topics
- Temporal → Graph: Timeline queries misinterpreted as sequences
- Metadata → Semantic: Filter keywords misinterpreted as content search

## Performance Metrics

### Accuracy Metrics

- **Overall Accuracy**: Percentage of correctly classified intents across all queries
- **Per-Intent Accuracy**: Accuracy for each intent type (graph/temporal/semantic/metadata)
- **Per-Difficulty Accuracy**: Accuracy by tier (easy/medium/hard)

### Latency Metrics

- **P50 (median)**: Middle query latency (target: <500ms)
- **P90**: 90th percentile latency (target: <1000ms)
- **P99**: 99th percentile latency (target: <2000ms)
- **Mean**: Average latency across all queries

### Success Criteria

| Metric | Target | Critical Threshold |
|--------|--------|-------------------|
| Overall Accuracy | ≥90% | ≥80% |
| Easy Tier | ≥95% | ≥90% |
| Medium Tier | ≥85% | ≥75% |
| Hard Tier | ≥70% | ≥60% |
| Graph Intent | ≥90% | ≥80% |
| Temporal Intent | ≥90% | ≥85% |
| Semantic Intent | ≥90% | ≥85% |
| Metadata Intent | ≥85% | ≥75% |
| P90 Latency | <1s | <2s |

## Adding New Tests

### Creating a New Test Suite

1. **Create JSON file in `test-suites/`**:
   ```json
   {
     "metadata": {
       "version": "1.0.0",
       "created": "2025-10-08",
       "description": "Test suite description",
       "total_queries": 50
     },
     "queries": [
       {
         "id": 1,
         "query": "example query text",
         "intent": "graph",
         "difficulty": "medium",
         "difficulty_rationale": "Why this is medium difficulty"
       }
     ]
   }
   ```

2. **Run test using test runner**:
   ```bash
   python scripts/difficulty_stratified_test.py \
     --test-file test-suites/your-test-suite.json \
     --output-dir results/your-test-name/
   ```

### Adding Queries to Existing Suite

1. Open test suite JSON file
2. Add query following the format above
3. Update `total_queries` in metadata
4. Re-run test

## Troubleshooting

### Low Accuracy (<80%)

**Check**:
1. Training data quality (`config/training-queries.json`)
2. Semantic router threshold (`semantic_classifier.py`)
3. Confusion matrix to identify problem patterns

**Fix**:
1. Add more training queries for problematic intent
2. Review threshold tuning (current: 0.3 for text-embedding-3-small)
3. Add negative examples to differentiate intents

### High Latency (>2s P90)

**Check**:
1. OpenAI API latency (embedding generation)
2. Database query performance
3. Network latency to services

**Fix**:
1. Enable Redis caching for embeddings
2. Optimize database queries
3. Use semantic caching for similar queries

### Inconsistent Results

**Check**:
1. Non-deterministic behavior in semantic router
2. Temperature settings in LLM calls
3. Cache interference

**Fix**:
1. Set random seed for reproducibility
2. Disable caching during testing
3. Use fixed training data versions

## Current Status

**Last Test Run**: 2025-10-08 18:06:11

**Results**:
- Overall Accuracy: 73.9% ❌ (target: ≥90%)
- Easy Tier: 86.9% ❌ (target: ≥95%)
- Medium Tier: 69.0% ❌ (target: ≥85%)
- Hard Tier: 58.0% ❌ (target: ≥70%)

**Problem Areas**:
- Graph intent: 55.6% accuracy (worst performing)
- Graph queries misclassified as semantic (11), temporal (10), metadata (7)

**Action Items**:
1. ✅ Add 100 graph-specific training queries with diverse relationship terminology
2. ✅ Expand total training data from 160 → 360 queries
3. ⏳ Re-run stratified test with expanded training data
4. ⏳ Target: Graph >90%, Easy >95%, Medium >85%, Hard >70%

## Related Documentation

- **Query Router**: `apex-memory-system/src/apex_memory/query_router/README.md`
- **Semantic Classifier**: `apex-memory-system/src/apex_memory/query_router/semantic_classifier.py`
- **Training Data**: `apex-memory-system/config/training-queries.json`
- **Improvement Plan**: `upgrades/query-router/IMPROVEMENT-PLAN.md`

## Contact

For questions or issues with the testing framework, see:
- **Research Documentation**: `research/documentation/query-routing/`
- **Architecture Decisions**: `research/architecture-decisions/`
- **Workflow**: `workflow/README.md`
