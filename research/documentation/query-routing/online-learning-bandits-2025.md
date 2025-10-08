# Online Learning & Contextual Bandits 2025

**Date:** January 2025
**Tier:** 1 (Industry Best Practices + Academic Research)
**Status:** Current

## Overview

Online learning with contextual bandits enables systems to continuously improve decision-making through real-time feedback. This document consolidates 2025 best practices for implementing adaptive routing systems that learn from user interactions and optimize performance over time.

## Sources

1. **NumberAnalytics - Contextual Bandits for Online Learning**
   - URL: https://numberanalyt.com/contextual-bandits-for-online-learning/
   - Focus: Theoretical foundations, algorithm design, practical applications

2. **Kameleoon - Real-Time Personalization with Contextual Bandits**
   - URL: https://www.kameleoon.com/en/blog/contextual-bandits
   - Focus: Implementation strategies, feedback collection, continuous adaptation

3. **Rollout.io - Feature Flag Best Practices**
   - URL: https://rollout.io/blog/
   - Focus: Gradual rollout with feedback loops

4. **Li et al. (2010) - "A Contextual-Bandit Approach to Personalized News Article Recommendation"**
   - Classic LinUCB paper
   - Focus: Algorithm design, theoretical guarantees

---

## Core Concepts

### 1. What is Online Learning?

**Definition:** A machine learning paradigm where the model continuously updates as new data arrives, adapting in real-time without requiring batch retraining.

**Key Characteristics:**
- **Incremental learning** - Update model after each observation
- **Real-time adaptation** - No offline retraining required
- **Continuous improvement** - Performance improves over time
- **Resource efficient** - Low memory footprint (no full dataset storage)

**Contrast with Batch Learning:**

| Aspect | Batch Learning | Online Learning |
|--------|----------------|-----------------|
| Training | Full dataset at once | Incremental updates |
| Adaptation | Manual retraining | Automatic real-time |
| Memory | Stores full dataset | Stores only model parameters |
| Latency | Hours to days | Milliseconds |

### 2. Contextual Bandits

**Definition:** A sequential decision-making framework where an agent learns to select optimal actions based on observed context, receiving feedback (rewards) after each decision.

**The Bandit Problem:**
- Agent observes **context** (query features, user attributes)
- Agent selects an **action** (database choice, routing strategy)
- Environment provides **reward** (query success, user satisfaction)
- Agent **updates** policy to maximize cumulative reward

**Why "Contextual"?**

Unlike traditional multi-armed bandits (fixed arm rewards), contextual bandits consider **context** when making decisions:

```python
# Traditional bandit (no context)
action = select_best_arm()  # Same for all queries

# Contextual bandit (context-aware)
action = select_best_arm(context)  # Different for each query
```

**Context Examples:**
- Query embeddings (semantic meaning)
- Query intent (graph, temporal, semantic, metadata)
- User attributes (role, location, history)
- System state (database load, latency)

### 3. Exploration vs Exploitation

**The Fundamental Tradeoff:**

- **Exploitation:** Use current knowledge to maximize immediate reward
- **Exploration:** Try sub-optimal actions to discover better options

**Why Both Matter:**

```python
# Pure exploitation (greedy)
action = argmax(estimated_rewards)
# Problem: Never discovers better actions, stuck at local optimum

# Pure exploration (random)
action = random_choice(actions)
# Problem: Ignores learned knowledge, wastes opportunities

# Balanced approach (contextual bandit)
action = argmax(estimated_rewards + exploration_bonus)
# Solution: Exploit current knowledge, explore uncertain actions
```

**Exploration Strategies:**

1. **ε-greedy** - Exploit with probability (1-ε), explore with probability ε
2. **Upper Confidence Bound (UCB)** - Add confidence bonus to estimates
3. **Thompson Sampling** - Sample from posterior distribution
4. **LinUCB** - UCB for linear contextual models (Apex Memory uses this)

---

## LinUCB Algorithm (Detailed)

### Algorithm Overview

**LinUCB (Linear Upper Confidence Bound)** assumes reward is a linear function of context features.

**Model:**
```
reward(action, context) = θ_action · context + noise
```

Where:
- `θ_action` = weight vector for each action (learned)
- `context` = feature vector (observed)
- `noise` = random error

**Confidence-Based Selection:**
```python
# For each action, compute:
predicted_reward = θ_action · context
uncertainty = sqrt(context^T · A_inverse · context)
ucb_score = predicted_reward + alpha * uncertainty

# Select action with highest UCB score
action = argmax(ucb_score)
```

**Key Parameters:**

- `alpha` - Exploration parameter (higher = more exploration)
  - Typical values: 0.1 to 2.0
  - Apex Memory default: 0.5

### Implementation

**Data Structures:**

```python
# Per-action state (stored in PostgreSQL)
A_action = np.eye(d)  # d × d covariance matrix
b_action = np.zeros(d)  # d-dimensional reward vector
θ_action = np.zeros(d)  # d-dimensional weight vector

# Update after each observation
A_action += context · context^T
b_action += reward · context
θ_action = A_action^(-1) · b_action
```

**Selection Logic:**

```python
def select_action(context, actions, alpha=0.5):
    scores = {}
    for action in actions:
        # Predicted reward
        theta = load_weights(action)
        predicted = np.dot(theta, context)

        # Uncertainty bonus
        A_inv = load_covariance_inverse(action)
        uncertainty = np.sqrt(context.T @ A_inv @ context)

        # UCB score
        scores[action] = predicted + alpha * uncertainty

    return max(scores, key=scores.get)
```

**Update Logic:**

```python
def update_weights(action, context, reward):
    # Load current state
    A = load_covariance(action)
    b = load_reward_vector(action)

    # Update covariance
    A += np.outer(context, context)

    # Update reward vector
    b += reward * context

    # Compute new weights
    theta = np.linalg.solve(A, b)

    # Store updated state
    save_weights(action, theta, A, b)
```

### Extensions for Online Learning

**1. Windowed Updates (Forget Old Data)**

```python
# Exponential decay
A_action = decay * A_action + context · context^T
b_action = decay * b_action + reward · context

# Typical decay: 0.99 (forget ~1% per update)
```

**2. Mini-Batch Updates (Efficiency)**

```python
# Accumulate feedback
feedback_queue = Queue()

# Process in batches
async def batch_update_task():
    while True:
        batch = await collect_batch(feedback_queue, size=100)
        for action, context, reward in batch:
            update_weights(action, context, reward)
```

**3. Warm Start (Initialize with Prior Knowledge)**

```python
# Initialize with Phase 2 static weights
A_action = np.eye(d) * prior_confidence
b_action = static_weights * prior_confidence
```

---

## Real-Time Adaptation

### 1. Feedback Collection

**Feedback Signals:**

| Signal | Measurement | Reward Formula |
|--------|-------------|----------------|
| **Click-through** | User clicked result | 1.0 if clicked, 0.0 otherwise |
| **Dwell time** | Time viewing result | normalized(seconds) ∈ [0, 1] |
| **Explicit rating** | User satisfaction | rating / max_rating |
| **Query refinement** | User re-queried | -0.5 (negative reward) |
| **Result count** | Results returned | min(count / target, 1.0) |
| **Latency** | Query response time | 1 - min(latency / timeout, 1) |

**Multi-Signal Aggregation:**

```python
def compute_reward(feedback):
    weights = {
        'clicked': 0.4,
        'dwell_time': 0.3,
        'explicit': 0.2,
        'latency': 0.1
    }

    reward = sum(
        weights[signal] * normalize(feedback[signal])
        for signal in weights
    )

    return reward  # ∈ [0, 1]
```

### 2. Asynchronous Learning

**Architecture:**

```
Query Request → Router Selection → Execute Query
                     ↓
                Store Context
                     ↓
                     ⏱️ (wait for feedback)
                     ↓
User Feedback → Feedback Queue → Background Learner
                                        ↓
                                Update Weights
                                        ↓
                                Store to DB
```

**Implementation:**

```python
class OnlineLearningRouter:
    def __init__(self, base_router, feedback_queue):
        self.base_router = base_router
        self.feedback_queue = feedback_queue
        self.pending_contexts = {}  # query_id → (action, context)

    async def route(self, query, context):
        # Select action using LinUCB
        action = self.select_action(context)

        # Execute query
        result = await self.base_router.route(query, action)

        # Store context for later feedback
        query_id = generate_id()
        self.pending_contexts[query_id] = (action, context)

        return result, query_id

    async def record_feedback(self, query_id, feedback):
        # Retrieve stored context
        action, context = self.pending_contexts.pop(query_id)

        # Compute reward
        reward = self.compute_reward(feedback)

        # Add to queue (async processing)
        await self.feedback_queue.put((action, context, reward))
```

### 3. Background Learning Task

**Batch Processing:**

```python
async def background_learning_task(feedback_queue, batch_size=100):
    """Background task for weight updates."""
    batch = []

    while True:
        try:
            # Collect batch
            while len(batch) < batch_size:
                item = await asyncio.wait_for(
                    feedback_queue.get(),
                    timeout=10.0
                )
                batch.append(item)

            # Process batch
            await process_batch(batch)
            batch.clear()

        except asyncio.TimeoutError:
            # Process partial batch if timeout
            if batch:
                await process_batch(batch)
                batch.clear()

async def process_batch(batch):
    """Update weights for a batch of feedback."""
    for action, context, reward in batch:
        update_weights(action, context, reward)

    logger.info(f"Processed batch of {len(batch)} updates")
```

---

## Integration with Existing Systems

### 1. Building on Phase 2 Adaptive Weights

**Phase 2 (Static LinUCB):**
- Weights learned offline from historical data
- Stored in PostgreSQL, loaded at startup
- No real-time updates

**Phase 4 (Online Learning):**
- Weights updated continuously from live feedback
- Same LinUCB algorithm, different update frequency
- Backward compatible (warm start from Phase 2 weights)

**Migration Path:**

```python
# Initialize with Phase 2 weights
online_router = OnlineLearningRouter(
    base_router=adaptive_router,
    initial_weights=adaptive_router.get_current_weights(),
    learning_rate=0.01  # Slow adaptation, trust prior
)

# Gradually increase learning rate as data accumulates
if online_router.feedback_count > 1000:
    online_router.learning_rate = 0.1  # Faster adaptation
```

### 2. Wrapper Pattern

**Design:** OnlineLearningRouter wraps any existing router

```python
# Wrap Phase 3 multi-router
online_router = OnlineLearningRouter(
    base_router=meta_router,  # Phase 3 multi-router
    feedback_queue=feedback_queue,
    update_interval=100  # Batch size
)

# Wrap Phase 2 adaptive router
online_router = OnlineLearningRouter(
    base_router=adaptive_router,  # Phase 2 adaptive router
    feedback_queue=feedback_queue,
    update_interval=100
)
```

**Benefits:**
- No changes to existing routers
- Opt-in via configuration flag
- Easy A/B testing (online vs static)

---

## Best Practices (2025)

### 1. Reward Design

**Principles:**
- **Immediate feedback is best** - Update within seconds of query
- **Multi-signal rewards** - Combine multiple feedback types
- **Normalize scales** - All rewards ∈ [0, 1]
- **Avoid sparse rewards** - Always provide some signal

**Anti-Patterns:**

❌ **Binary rewards only** (clicked / not clicked)
- Problem: Ignores partial success

✅ **Multi-signal rewards** (click + dwell + relevance)
- Solution: Captures nuanced feedback

❌ **Delayed feedback** (wait hours for batch processing)
- Problem: Slow adaptation, outdated policies

✅ **Real-time feedback** (update within seconds)
- Solution: Fast adaptation, up-to-date policies

### 2. Exploration Management

**Dynamic Exploration:**

```python
# Reduce exploration as confidence grows
def adaptive_alpha(num_observations):
    if num_observations < 100:
        return 2.0  # High exploration (uncertain)
    elif num_observations < 1000:
        return 0.5  # Medium exploration
    else:
        return 0.1  # Low exploration (confident)
```

**Context-Specific Exploration:**

```python
# Explore more for rare contexts
def context_alpha(context, base_alpha=0.5):
    context_count = get_observation_count(context)
    if context_count < 10:
        return base_alpha * 2  # Double exploration
    return base_alpha
```

### 3. Monitoring

**Key Metrics:**

- **Regret** - Difference from optimal policy
  - Formula: `regret = sum(optimal_reward - actual_reward)`
  - Target: Sublinear growth (diminishing over time)

- **Cumulative Reward** - Total reward over time
  - Target: Monotonic increase

- **Exploration Rate** - % of exploratory actions
  - Target: Decreasing over time (10% → 1%)

- **Weight Stability** - Change in θ per update
  - Target: Decreasing over time (converging)

**Alerts:**

```python
# Alert if performance degrades
if recent_avg_reward < historical_avg_reward * 0.9:
    alert("Online learning performance drop")

# Alert if weights diverge
if weight_change > threshold:
    alert("Weight instability detected")
```

### 4. Fallback Strategy

**Safety Net:**

```python
# If online learning fails, fall back to Phase 2 static weights
try:
    action = online_router.select_action(context)
except Exception as e:
    logger.error(f"Online learning failed: {e}")
    action = static_router.select_action(context)  # Fallback
```

**Automatic Rollback:**

```python
# Monitor performance, rollback if degraded
if online_performance < static_performance * 0.95:
    logger.warning("Online learning underperforming, rolling back")
    disable_online_learning()
    use_static_weights()
```

---

## Performance Expectations

### Accuracy Improvement

**Timeline:**
- **Day 1:** 0% improvement (cold start, same as Phase 2)
- **Week 1:** 2-5% improvement (initial learning)
- **Month 1:** 5-10% improvement (stabilizing)
- **Month 3+:** 10-15% improvement (converged)

**Factors:**
- Query distribution (stable = faster learning)
- Feedback quality (accurate = better learning)
- Initial weights (good prior = faster convergence)

### Latency Impact

**Overhead:**
- **Selection:** +1-2ms (LinUCB computation)
- **Feedback recording:** <1ms (async queue)
- **Weight updates:** 0ms (background task)

**Total:** <5ms additional latency (negligible)

### Resource Usage

**Memory:**
- Per-action state: ~1KB (d=100 dimensions)
- 4 actions × 1KB = 4KB total
- Feedback queue: ~100 items × 200 bytes = 20KB

**CPU:**
- Selection: O(d²) matrix multiplication (~0.1ms for d=100)
- Update: O(d²) matrix inverse (~1ms for d=100)
- Batch update (100 items): ~100ms every 10 seconds = 1% CPU

**Database:**
- Weight updates: 100 writes/minute (batch updates)
- Minimal impact on PostgreSQL

---

## Implementation Checklist

### Phase 4 Online Learning

✅ **Before Implementation:**
- [ ] Define feedback signals (clicks, dwell time, ratings)
- [ ] Implement reward computation function
- [ ] Set up async feedback queue (asyncio.Queue)
- [ ] Configure batch size (default: 100)
- [ ] Set initial exploration parameter (alpha=0.5)

✅ **During Implementation:**
- [ ] Implement OnlineLearningRouter wrapper
- [ ] Add background learning task
- [ ] Store pending contexts (query_id → context)
- [ ] Implement feedback recording endpoint
- [ ] Add monitoring (regret, cumulative reward)

✅ **After Implementation:**
- [ ] A/B test vs Phase 2 static weights (50/50 split)
- [ ] Monitor performance for 1 week
- [ ] Tune alpha parameter if needed
- [ ] Set up alerts for performance degradation
- [ ] Document learned weights for future reference

---

## Example: End-to-End Flow

```python
# 1. User submits query
query = "find ACME Corp invoices from last quarter"
context = generate_context(query)  # embedding + intent + metadata

# 2. Router selects action using LinUCB
action, query_id = await online_router.route(query, context)
# action = "neo4j" (selected based on context + uncertainty)

# 3. Execute query
results = await execute_query(query, action)

# 4. Return results to user
return {"results": results, "query_id": query_id}

# 5. User interacts with results
# - Clicks on 3rd result
# - Views for 15 seconds
# - Provides explicit rating: 4/5

# 6. Record feedback
feedback = {
    "clicked": True,
    "click_position": 3,
    "dwell_time": 15,
    "rating": 4
}
await online_router.record_feedback(query_id, feedback)

# 7. Background task processes feedback
# - Computes reward: 0.85 (weighted combination)
# - Updates weights for "neo4j" action
# - Stores updated weights to PostgreSQL

# 8. Next similar query uses updated weights
# - Higher confidence in "neo4j" for similar contexts
# - Reduced exploration (uncertainty decreased)
```

---

## Research Citations

1. **Li, L., Chu, W., Langford, J., & Schapire, R. E. (2010)**
   - "A Contextual-Bandit Approach to Personalized News Article Recommendation"
   - WWW '10: Proceedings of the 19th International Conference on World Wide Web
   - DOI: 10.1145/1772690.1772758

2. **Agrawal, S., & Goyal, N. (2013)**
   - "Thompson Sampling for Contextual Bandits with Linear Payoffs"
   - ICML '13: Proceedings of the 30th International Conference on Machine Learning

3. **Chu, W., Li, L., Reyzin, L., & Schapire, R. E. (2011)**
   - "Contextual Bandits with Linear Payoff Functions"
   - AISTATS '11: Proceedings of the 14th International Conference on AI and Statistics

4. **NumberAnalytics - Contextual Bandits for Online Learning (2025)**
   - https://numberanalyt.com/contextual-bandits-for-online-learning/

5. **Kameleoon - Real-Time Personalization with Contextual Bandits (2025)**
   - https://www.kameleoon.com/en/blog/contextual-bandits

---

## Glossary

**Action**: A decision made by the router (e.g., database selection)

**Context**: Observable features used for decision-making (query embedding, intent)

**Reward**: Feedback signal indicating action quality (0.0 to 1.0)

**Regret**: Cumulative difference from optimal policy

**Exploration**: Trying sub-optimal actions to gather information

**Exploitation**: Using current knowledge to maximize immediate reward

**LinUCB**: Linear Upper Confidence Bound algorithm for contextual bandits

**Alpha (α)**: Exploration parameter (higher = more exploration)

**Theta (θ)**: Learned weight vector for each action

**Covariance Matrix (A)**: Confidence in weight estimates

**Warm Start**: Initializing online learning with prior knowledge

---

**Document Version:** 1.0
**Last Updated:** January 2025
**Next Review:** July 2025
