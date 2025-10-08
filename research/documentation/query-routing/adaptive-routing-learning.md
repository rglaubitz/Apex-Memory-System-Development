# Adaptive Query Routing with Learned Weights

**Sources:** Academic research 2024-2025
**Date:** 2024-2025
**Tier:** 1 (Academic Research Papers)

## Overview

Adaptive query routing uses machine learning and online feedback to dynamically optimize routing decisions and scoring weights, moving from static rules to learned, data-driven strategies.

## Problem with Static Weights

**Current Apex Approach:**
```python
score_weights = {
    "qdrant": 0.4,    # Why 40%?
    "postgres": 0.3,  # Why 30%?
    "neo4j": 0.2,     # Why 20%?
    "graphiti": 0.1,  # Why 10%?
}
```

**Issues:**
- No data-driven justification
- Same weights for all query types
- No adaptation to performance
- Manual tuning required
- Optimal weights unknown

## Solution: Learned Adaptive Weights

### 1. Contextual Bandits for LLM Routing

**Source:** "Adaptive LLM Routing under Budget Constraints" (arXiv 2508.21141)

**Innovation:** PILOT (Preference-prior Informed LinUCB fOr Adaptive RouTing)

**Concept:**
- Treat routing as a contextual bandit problem
- Learn from user feedback (clicks, satisfaction, task completion)
- Balance exploration (try new routes) and exploitation (use best routes)

**Architecture:**
```
Query → Embed → Contextual Bandit → Route Selection → Database
                       ↑                    ↓
                       └──── Feedback ──────┘
```

**Mathematical Foundation:**

LinUCB (Linear Upper Confidence Bound):
```
Score(database, query) = θ_db^T · query_embedding + α · √(query^T · A_db^-1 · query)
                         \_________________/   \___________________________/
                              Expected reward        Uncertainty bonus
```

Where:
- `θ_db`: Learned weight vector for database
- `query_embedding`: Vector representation of query
- `A_db`: Covariance matrix (tracks experience)
- `α`: Exploration parameter

**Advantages:**
- Automatically learns optimal weights
- Adapts to changing data/usage patterns
- Balances exploration vs exploitation
- Online learning (no retraining needed)

**Performance:** 15-30% improvement over static routing

### 2. Matrix Factorization for Scoring

**Source:** "LLM Routing: Optimizing Pathways" (Medium 2024)

**Concept:** Learn scoring function from user feedback

**Process:**
1. Collect triplets: (query, database, score)
   - Score = 1 if user satisfied, 0 if not
2. Factorize into low-rank matrices
   - Query embeddings: Q (n_queries × k)
   - Database embeddings: D (n_databases × k)
3. Score = Q · D^T

**Training:**
```python
from sklearn.decomposition import NMF

# Historical data
queries = [...]  # Query embeddings
databases = [...]  # Database IDs
scores = [...]  # User satisfaction (0 or 1)

# Matrix factorization
model = NMF(n_components=32)
Q = model.fit_transform(query_database_matrix)
D = model.components_

# Predict score for new query
def predict_score(query_embedding, database_id):
    return np.dot(query_embedding, D[database_id])
```

**Advantages:**
- Learns database "affinity" for query types
- Generalizes to unseen queries
- Collaborative filtering effect

### 3. BERT Classifier for Route Prediction

**Concept:** Train classifier to predict best database

**Architecture:**
```
Query Text → BERT Encoder → Classification Head → Database Probabilities
```

**Training Data:**
```python
examples = [
    {
        "query": "What equipment is connected to ACME Corp?",
        "best_database": "neo4j",
        "feedback_score": 0.95
    },
    {
        "query": "Find similar invoices to INV-001",
        "best_database": "qdrant",
        "feedback_score": 0.89
    },
    # ... thousands of examples
]
```

**Inference:**
```python
query = "Show me payment trends over time"
probs = bert_classifier(query)
# probs = {
#     "neo4j": 0.15,
#     "qdrant": 0.25,
#     "postgres": 0.30,
#     "graphiti": 0.30  ← Highest probability
# }
```

**Use Cases:**
- When to use which database
- Multi-database routing (select top-k)
- Confidence-based fallbacks

## Adaptive Query Execution (Database Optimization)

**Source:** "Adaptive Query Execution (AQE)" - Databricks, CelerData

**Concept:** Optimize queries dynamically based on runtime statistics

**Key Techniques:**

### 1. Runtime Statistics Collection
```python
def execute_query(query):
    plan = create_initial_plan(query)

    # Execute first stage
    intermediate_results = execute_stage_1(plan)

    # Collect runtime stats
    stats = {
        "row_count": len(intermediate_results),
        "data_size": intermediate_results.nbytes,
        "execution_time": stage_1_time,
        "cache_hit_rate": cache_stats.hit_rate
    }

    # Adjust plan based on stats
    adjusted_plan = optimize_plan(plan, stats)

    # Execute remaining stages with adjusted plan
    return execute_remaining(adjusted_plan, intermediate_results)
```

### 2. Dynamic Weight Adjustment

**Approach:** Adjust database weights based on observed performance

```python
class AdaptiveWeightManager:
    def __init__(self):
        self.weights = {
            "qdrant": 0.25,
            "postgres": 0.25,
            "neo4j": 0.25,
            "graphiti": 0.25
        }
        self.performance_history = defaultdict(list)

    def update_weights(self, query_type, database, performance_score):
        # Track performance
        self.performance_history[database].append(performance_score)

        # Update weights based on moving average
        if len(self.performance_history[database]) >= 100:
            avg_performance = np.mean(self.performance_history[database][-100:])

            # Adjust weight proportionally to performance
            self.weights[database] = avg_performance / sum(avg_performance for all DBs)

    def get_weights(self, query_type):
        # Return type-specific weights
        return self.weights
```

**Performance:** 8x speedup in TPC-DS benchmarks

### 3. Feedback-Driven Optimization

**Sources:**
1. "Adaptive Querying for Reward Learning" (arXiv 2412.07990)
2. "QuARI: Query Adaptive Retrieval Improvement" (arXiv 2505.21647)

**Concept:** Use retrieval performance as reward signal

**Implementation:**
```python
class FeedbackDrivenRouter:
    def __init__(self):
        self.router_model = LinearBandit()

    def route(self, query):
        # Get current best route
        route = self.router_model.predict(query)

        # Execute and measure
        results, metrics = execute_and_measure(route, query)

        # Compute reward
        reward = compute_reward(results, metrics)
        # Reward factors:
        # - User satisfaction (clicks, dwell time)
        # - Result relevance (reranker score)
        # - Latency (faster = higher reward)
        # - Coverage (more relevant docs found)

        # Update model with feedback
        self.router_model.update(query, route, reward)

        return results

    def compute_reward(self, results, metrics):
        reward = 0.0

        # Relevance component (0-1)
        reward += metrics['avg_relevance'] * 0.5

        # Latency component (0-1, inverse)
        reward += (1.0 - min(metrics['latency_ms'] / 1000, 1.0)) * 0.3

        # Coverage component (0-1)
        reward += (metrics['docs_found'] / metrics['docs_needed']) * 0.2

        return reward
```

## Reinforcement Learning for Query Optimization

**Source:** "Simple Adaptive Query Processing vs. Learned Query Optimizers" (VLDB 2025)

**Key Insight:** RL-based optimizers use pre-trained models, adaptive approaches use runtime statistics

**Comparison:**

| Approach | Training | Adaptation | Performance |
|----------|----------|------------|-------------|
| Static Rules | None | None | Baseline |
| Adaptive (Runtime) | None | Real-time | +50-100% |
| RL (Pre-trained) | Offline | Limited | +100-200% |
| Hybrid (RL + Adaptive) | Offline + Online | Real-time | +200-300% |

**Hybrid Approach:**
```python
class HybridOptimizer:
    def __init__(self):
        self.rl_model = load_pretrained_model()  # Offline trained
        self.adaptive_adjuster = AdaptiveAdjuster()  # Online learning

    def optimize_query(self, query):
        # Get RL model's suggestion
        rl_plan = self.rl_model.suggest_plan(query)

        # Execute with runtime monitoring
        results, runtime_stats = execute_with_monitoring(rl_plan, query)

        # Adaptive adjustment based on actual performance
        if runtime_stats.is_suboptimal():
            adjusted_plan = self.adaptive_adjuster.adjust(rl_plan, runtime_stats)
            results = execute(adjusted_plan, query)

        # Update both models
        self.rl_model.update(query, results)
        self.adaptive_adjuster.update(runtime_stats)

        return results
```

## Deep Reinforcement Learning for Network Routing

**Source:** "An adaptive intelligent routing algorithm based on deep reinforcement learning" (ScienceDirect 2024)

**Transferable Concepts:**
- State representation: Query features, database states
- Action space: Route selections
- Reward function: Latency, accuracy, cost
- Policy network: Neural network mapping states → actions

**Architecture:**
```
Query State → Neural Network → Route Probabilities → Sample Action
     ↑                                                      ↓
     └────────────── Reward Feedback ──────────────────────┘
```

## Implementation Roadmap for Apex

### Phase 1: Data Collection (Week 1)
```python
class RoutingLogger:
    """Log all routing decisions and outcomes."""

    def log_decision(self, query, intent, databases_used, results, metrics):
        record = {
            "timestamp": datetime.now(),
            "query": query,
            "intent": intent.query_type.value,
            "databases": list(databases_used),
            "num_results": len(results),
            "avg_relevance": metrics.get("avg_relevance", 0.0),
            "latency_ms": metrics.get("latency_ms", 0),
            "cache_hit": metrics.get("cached", False),
            "user_clicked": None,  # Fill in from user feedback
            "user_satisfaction": None  # Fill in from user feedback
        }

        self.save_to_analytics_db(record)
```

### Phase 2: Offline Analysis (Week 2)
```python
# Analyze historical data
data = load_routing_logs()

# Train initial models
bandit_model = train_contextual_bandit(data)
classifier_model = train_bert_classifier(data)

# Evaluate performance
baseline_accuracy = evaluate_static_routing(data)
bandit_accuracy = evaluate_bandit_routing(data, bandit_model)
classifier_accuracy = evaluate_classifier_routing(data, classifier_model)
```

### Phase 3: A/B Testing (Week 3-4)
```python
class ABTestRouter:
    def __init__(self, test_percentage=0.1):
        self.static_router = StaticRouter()  # Current approach
        self.learned_router = LearnedRouter()  # New approach
        self.test_percentage = test_percentage

    def route(self, query):
        if random.random() < self.test_percentage:
            # Test group: use learned router
            return self.learned_router.route(query), "learned"
        else:
            # Control group: use static router
            return self.static_router.route(query), "static"
```

### Phase 4: Gradual Rollout (Week 5-6)
```python
# Increase learned router usage based on performance
if learned_router.accuracy > static_router.accuracy + 0.05:
    test_percentage = min(test_percentage + 0.1, 1.0)
```

### Phase 5: Continuous Learning (Week 7+)
```python
# Online learning from production feedback
def online_update(query, route, feedback):
    # Update bandit model
    bandit_model.partial_fit(query, route, feedback)

    # Periodically retrain classifier
    if num_samples % 1000 == 0:
        classifier_model.retrain(recent_samples)
```

## Key Metrics to Track

1. **Routing Accuracy:** % of queries routed to optimal database
2. **Latency:** P50, P95, P99 latency by route
3. **Relevance:** Average relevance score of results
4. **Cost:** Compute cost per database
5. **User Satisfaction:** Click-through rate, dwell time
6. **Exploration Rate:** % of exploratory decisions
7. **Weight Stability:** How much weights fluctuate

## Expected Improvements

Based on research:

| Metric | Static | Adaptive | Gain |
|--------|--------|----------|------|
| Routing Accuracy | 70-75% | 85-92% | +15-20% |
| Avg Latency | 800ms | 600ms | -25% |
| Relevance Score | 0.72 | 0.85 | +18% |
| Cost Efficiency | Baseline | -30% | 30% savings |

## References

1. Adaptive LLM Routing under Budget Constraints (arXiv 2508.21141)
   https://arxiv.org/html/2508.21141

2. Adaptive Querying for Reward Learning (arXiv 2412.07990)
   https://arxiv.org/html/2412.07990v1

3. Simple Adaptive Query Processing vs. Learned Query Optimizers (VLDB 2025)
   https://link.springer.com/article/10.1007/s00778-025-00936-6

4. Adaptive Query Execution (Databricks 2020)
   https://www.databricks.com/blog/2020/05/29/adaptive-query-execution-speeding-up-spark-sql-at-runtime.html

5. QuARI: Query Adaptive Retrieval Improvement (arXiv 2505.21647)
   https://arxiv.org/html/2505.21647v1

6. An adaptive intelligent routing algorithm based on deep reinforcement learning
   https://www.sciencedirect.com/science/article/abs/pii/S0140366423004826

7. LLM Routing: Optimizing Pathways in Language Processing
   https://medium.com/accredian/llm-routing-optimizing-pathways-in-language-processing-c52c2adf7c4e
