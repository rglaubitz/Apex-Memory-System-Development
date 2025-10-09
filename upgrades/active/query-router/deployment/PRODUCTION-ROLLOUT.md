# Production Rollout Guide - Query Router

**Safe 5-stage deployment strategy for all 4 phases**

---

## 📋 Overview

This guide provides a **battle-tested deployment strategy** for activating all query router phases with minimal risk and maximum observability.

**Timeline:** 2-4 weeks from baseline to 100% Phase 4 activation
**Risk Level:** Low (gradual rollout with instant rollback capability)
**Rollback Time:** <1 second (via feature flags)

---

## 🎯 5-Stage Deployment Strategy

```
Stage 1: Baseline (Phases 1-3 Only)           [Day 0-2]
   ↓
Stage 2: Feature Flag Infrastructure          [Day 3-4]
   ↓
Stage 3: Online Learning at 0%                [Day 5-7]
   ↓
Stage 4: Gradual Rollout (5% → 100%)         [Day 8-21]
   ↓
Stage 5: Cleanup & Permanence                 [Day 22-28]
```

---

## 🚀 Stage 1: Baseline (Phases 1-3 Only)

**Goal:** Establish performance baseline with proven features

**Duration:** 2-3 days

**What's Active:**
- ✅ Phase 1: Semantic classification, query rewriting, analytics
- ✅ Phase 2: Adaptive routing, GraphRAG, semantic caching
- ✅ Phase 3: Complexity analysis, multi-router, self-correction
- ❌ Phase 4: Feature flags and online learning (DISABLED)

### Configuration

```python
# router_config.py
from apex_memory.query_router.router import QueryRouter

router = QueryRouter(
    # Database connections
    neo4j_driver=neo4j_driver,
    postgres_conn=postgres_conn,
    qdrant_client=qdrant_client,
    redis_client=redis_client,
    embedding_service=embedding_service,
    graphiti_service=graphiti_service,

    # Phase 1: Foundation
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
    postgres_dsn=os.getenv("POSTGRES_DSN"),
    enable_semantic_classification=True,
    enable_query_rewriting=True,
    enable_analytics=True,

    # Phase 2: Intelligent Routing
    neo4j_uri=os.getenv("NEO4J_URI"),
    neo4j_user=os.getenv("NEO4J_USER"),
    neo4j_password=os.getenv("NEO4J_PASSWORD"),
    enable_adaptive_routing=True,
    enable_graphrag=True,
    enable_semantic_cache=True,
    enable_result_fusion=True,
    bandit_alpha=0.5,
    cache_similarity_threshold=0.95,

    # Phase 3: Agentic Evolution
    enable_complexity_analysis=True,
    enable_multi_router=True,
    enable_self_correction=True,
    enable_query_improvement=True,
    max_correction_retries=2,

    # Phase 4: DISABLED (baseline)
    enable_feature_flags=False,
    enable_online_learning=False
)

await router.initialize()
```

**Full example:** [`examples/router_config_phase3.py`](examples/router_config_phase3.py)

### Metrics to Collect

Monitor these baselines for 2-3 days:

- **Query Latency:**
  - P50: ~200ms
  - P90: ~500ms
  - P99: ~1000ms

- **Accuracy:**
  - Intent classification: 98-99%
  - Cache hit rate: 90%+
  - Routing accuracy: 95-98%

- **Throughput:**
  - Queries per second: ~100 QPS
  - Error rate: <1%

**Action:** Document these baselines. They're your reference for detecting Phase 4 impact.

---

## 🏗️ Stage 2: Feature Flag Infrastructure

**Goal:** Enable feature flag system (but don't use it yet)

**Duration:** 1-2 days

**What's Active:**
- ✅ Phase 1-3: All active (same as Stage 1)
- ✅ Phase 4: Feature flags ENABLED (infrastructure only)
- ❌ Phase 4: Online learning DISABLED

### Configuration

```python
router = QueryRouter(
    # ... same as Stage 1 ...

    # Phase 4: Enable feature flags
    enable_feature_flags=True,     # ← NEW
    enable_online_learning=False   # Still disabled
)

await router.initialize()
```

**Full example:** See [`examples/feature_flag_setup.py`](examples/feature_flag_setup.py)

### Verification

```python
# Verify feature flag manager initialized
assert router.feature_flags is not None

# Check feature flag stats
stats = await router.feature_flags.get_stats()
print(f"Total flags: {stats['total_flags']}")
print(f"Cache size: {stats['cache_size']}")
```

### Metrics to Watch

- **No regression:** All baseline metrics should remain stable
- **Feature flag latency:** <1ms for flag evaluation
- **Redis connections:** Monitor connection pool usage

**Red Flags:**
- ❌ Latency increase >10%
- ❌ Redis connection errors
- ❌ Feature flag evaluation >5ms

**Action:** If metrics stable for 24 hours, proceed to Stage 3.

---

## 🧪 Stage 3: Online Learning at 0%

**Goal:** Enable online learning but don't activate it (0% rollout)

**Duration:** 2-3 days

**What's Active:**
- ✅ Phase 1-3: All active
- ✅ Phase 4: Feature flags active
- ✅ Phase 4: Online learning ENABLED but at 0% rollout
  - Background task running
  - Feedback queue active
  - No user traffic affected yet

### Configuration

```python
router = QueryRouter(
    # ... same as Stage 2 ...

    # Phase 4: Enable both
    enable_feature_flags=True,
    enable_online_learning=True,    # ← NEW
    online_learning_batch_size=100,
    online_learning_rate=0.01       # Conservative learning rate
)

await router.initialize()

# Create feature flag at 0% (no one gets Phase 4 yet)
await router.feature_flags.create_flag(
    "phase4_online_learning",
    description="Enable Phase 4 online learning router",
    default_enabled=False,
    rollout_percentage=0  # ← 0% = disabled for all users
)
```

**Full example:** [`examples/online_learning_setup.py`](examples/online_learning_setup.py)

### Verification

```python
# Verify online learning initialized
assert router.online_learning_router is not None

# Check background task running
stats = router.online_learning_router.get_stats()
print(f"Feedback count: {stats['feedback_count']}")
print(f"Queue size: {stats['queue_size']}")

# Verify flag at 0%
flag_state = await router.feature_flags.get_flag("phase4_online_learning")
assert flag_state.rollout_percentage == 0
```

### Metrics to Watch

- **No regression:** Baseline metrics still stable
- **Background task:** Should be running without errors
- **Memory usage:** Monitor for leaks from feedback queue
- **Learning rate:** Should be 0 (no feedback yet)

**Red Flags:**
- ❌ Memory leak (growing unbounded)
- ❌ Background task crashed
- ❌ Error rate increase

**Action:** If metrics stable for 48 hours, proceed to Stage 4 (the big one!).

---

## 🎢 Stage 4: Gradual Rollout (5% → 100%)

**Goal:** Gradually activate Phase 4 online learning with close monitoring

**Duration:** ~2 weeks (4 rollout stages)

**Timeline:**
```
Day 8:  5% rollout   → Internal team
Day 11: 25% rollout  → Early adopters
Day 15: 50% rollout  → Majority
Day 21: 100% rollout → Everyone
```

### Sub-Stage 4.1: 5% Rollout (Day 8-10)

**Target:** Internal team / canary users

```python
# Increase to 5%
await router.feature_flags.set_rollout_percentage("phase4_online_learning", 5)

# Add internal team to whitelist (always enabled)
internal_users = ["user_alice", "user_bob", "user_charlie"]
for user_id in internal_users:
    await router.feature_flags.add_to_whitelist("phase4_online_learning", user_id)
```

**Metrics to Watch (Monitor Every Hour):**
- Query latency (should stay <1s P99)
- Error rate (should stay <1%)
- Online learning:
  - Feedback count (should be increasing)
  - Average reward (target: 0.5-0.8)
  - Queue size (should stay <500)

**Success Criteria (After 2-3 Days):**
- ✅ No latency regression (P99 <1s)
- ✅ Error rate stable (<1%)
- ✅ Average reward >0.5
- ✅ No crash or memory leak

**If Success → Proceed to 25%**
**If Failure → Rollback to 0%**

### Sub-Stage 4.2: 25% Rollout (Day 11-14)

**Target:** Early adopters

```python
# Increase to 25%
await router.feature_flags.set_rollout_percentage("phase4_online_learning", 25)
```

**Metrics to Watch (Monitor Every 6 Hours):**
- Same as 5% but expect:
  - 5× more feedback
  - Avg reward should be trending up
  - Weight updates should be happening

**Success Criteria (After 3-4 Days):**
- ✅ Metrics stable at 25%
- ✅ Average reward ≥0.6 (improving)
- ✅ Cache hit rate maintaining ≥70%
- ✅ No user complaints

**If Success → Proceed to 50%**
**If Failure → Rollback to 5% or 0%**

### Sub-Stage 4.3: 50% Rollout (Day 15-20)

**Target:** Majority of users

```python
# Increase to 50%
await router.feature_flags.set_rollout_percentage("phase4_online_learning", 50)
```

**Metrics to Watch (Monitor Daily):**
- Same as 25% but expect:
  - 2× more feedback
  - Weight convergence visible
  - Accuracy improvements measurable

**Success Criteria (After 5-6 Days):**
- ✅ Metrics stable at 50%
- ✅ Average reward ≥0.65
- ✅ Routing accuracy improvement visible (98% → 98.5%)
- ✅ No performance degradation

**If Success → Proceed to 100%**
**If Failure → Rollback to 25%**

### Sub-Stage 4.4: 100% Rollout (Day 21+)

**Target:** Everyone

```python
# Increase to 100%
await router.feature_flags.set_rollout_percentage("phase4_online_learning", 100)
```

**Metrics to Watch (Monitor Daily for 1 Week):**
- All metrics stabilized
- Average reward ≥0.7
- Long-term accuracy trend positive
- User satisfaction stable

**Success Criteria (After 1 Week at 100%):**
- ✅ All metrics stable
- ✅ No user complaints
- ✅ Observable accuracy improvement
- ✅ System behaving normally

**If Success → Proceed to Stage 5 (Cleanup)**
**If Failure → Rollback to 50%**

---

## 🧹 Stage 5: Cleanup & Permanence

**Goal:** Remove training wheels, make Phase 4 permanent

**Duration:** 1 week

**When:** After 2-4 weeks at 100% rollout with no issues

### Actions

1. **Remove Feature Flag**
   ```python
   # Flag has been at 100% for 4 weeks, make it permanent
   await router.feature_flags.delete_flag("phase4_online_learning")
   ```

2. **Update Configuration** (remove flags)
   ```python
   # router_config.py
   router = QueryRouter(
       # ... all phases enabled ...
       # No feature flags needed anymore
       enable_feature_flags=False,      # ← Can disable now
       enable_online_learning=True      # ← Permanent
   )
   ```

3. **Archive Documentation**
   - Move rollout logs to `docs/deployments/phase4-rollout-2025-10.md`
   - Document lessons learned
   - Update runbooks

4. **Celebrate!** 🎉
   - All 4 phases active
   - 99%+ accuracy achieved
   - Continuous learning operational

---

## 📊 Monitoring Dashboard

### Key Metrics by Stage

| Metric | Stage 1 | Stage 2 | Stage 3 | Stage 4 (5%) | Stage 4 (100%) |
|--------|---------|---------|---------|--------------|----------------|
| Latency P99 | 1000ms | 1000ms | 1000ms | 1000ms | 1000ms |
| Error Rate | <1% | <1% | <1% | <1% | <1% |
| Cache Hit Rate | 90%+ | 90%+ | 90%+ | 90%+ | 90%+ |
| Feedback Count | 0 | 0 | 0 | ~50/day | ~1000/day |
| Avg Reward | N/A | N/A | N/A | 0.5-0.6 | 0.65-0.75 |
| Learning Active | No | No | No | Yes (5%) | Yes (100%) |

### Grafana Dashboards

**Access:** http://localhost:3001 (admin/apexmemory2024)

**Dashboards to create:**
1. **Query Router Overview** - Latency, throughput, error rate
2. **Phase 4 Monitoring** - Feedback count, avg reward, queue size
3. **Database Health** - Connection pool, query latency per DB
4. **Feature Flags** - Rollout percentage, evaluation latency

**Setup:** See [`examples/monitoring_setup.py`](examples/monitoring_setup.py)

---

## 🚨 Rollback Procedures

### Emergency Rollback (<1 Second)

```python
# Instant disable via feature flag
await router.feature_flags.set_rollout_percentage("phase4_online_learning", 0)
```

**When to Use:**
- Error rate spike >5%
- Latency spike >2× baseline
- System crash or severe bug
- Data corruption detected

### Graceful Rollback (Gradual Decrease)

```python
# Step down gradually
await router.feature_flags.set_rollout_percentage("phase4_online_learning", 50)
# Monitor for 1 day...
await router.feature_flags.set_rollout_percentage("phase4_online_learning", 25)
# Monitor for 1 day...
await router.feature_flags.set_rollout_percentage("phase4_online_learning", 0)
```

**When to Use:**
- Minor performance degradation
- User feedback concerns
- Unclear if issue is Phase 4 related

### Code Rollback (Git Revert)

```bash
# Revert Phase 4 commit
git revert 69cdd35

# Redeploy
git push
# ... deployment process ...
```

**When to Use:**
- Critical bug in Phase 4 code
- Feature flag rollback insufficient
- Need to remove Phase 4 entirely

---

## ✅ Pre-Deployment Checklist

**Before Stage 1:**
- [ ] All 223 tests passing
- [ ] Database services healthy
- [ ] Monitoring dashboards configured
- [ ] Baseline metrics documented
- [ ] Rollback procedure tested
- [ ] On-call engineer assigned
- [ ] Stakeholders notified

**Before Stage 4 (Gradual Rollout):**
- [ ] Stages 1-3 completed successfully
- [ ] Feature flags working correctly
- [ ] Online learning background task running
- [ ] Monitoring alerts configured
- [ ] Rollback procedure documented
- [ ] Team trained on metrics

**Before Stage 5 (Cleanup):**
- [ ] 100% rollout stable for 2-4 weeks
- [ ] No user complaints
- [ ] Metrics showing improvement
- [ ] Documentation updated
- [ ] Lessons learned documented

---

## 📞 Escalation Path

**If Issues Arise:**

1. **Check monitoring dashboards** (Grafana)
2. **Review logs** (`logs/apex-memory.log`)
3. **Check TROUBLESHOOTING.md** for known issues
4. **If unsure → Rollback to previous stage**
5. **Document issue for investigation**

**Severity Levels:**

- **P0 (Critical):** Immediate rollback, page on-call
- **P1 (High):** Pause rollout, investigate within 4 hours
- **P2 (Medium):** Continue monitoring, investigate within 24 hours
- **P3 (Low):** Note for next iteration

---

## 🎓 Lessons Learned Template

After deployment, document:

```markdown
# Phase 4 Deployment Post-Mortem

## Timeline
- Stage 1: [dates]
- Stage 2: [dates]
- Stage 3: [dates]
- Stage 4: [dates]
- Stage 5: [dates]

## What Went Well
- [bullet points]

## What Went Wrong
- [bullet points]

## Unexpected Issues
- [bullet points]

## Metrics Impact
- Latency: [before/after]
- Accuracy: [before/after]
- User satisfaction: [before/after]

## Recommendations for Next Time
- [bullet points]
```

---

**Production Rollout Guide v1.0**
**Last Updated:** 2025-10-07
**Next Review:** 2025-11-07
