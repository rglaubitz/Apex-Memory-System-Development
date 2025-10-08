# Feature Flags Best Practices 2025

**Date:** January 2025
**Tier:** 1 (Industry Best Practices + Official Documentation)
**Status:** Current

## Overview

Feature flags (feature toggles) enable teams to separate feature deployment from feature activation, allowing instant feature toggling without code redeployment. This document consolidates 2025 best practices for feature flag system design, Redis integration, and gradual rollout strategies.

## Sources

1. **FeatBit - Feature Flag System Design 2025**
   - URL: https://www.featbit.co/articles2025/feature-flag-system-design-2025
   - Focus: Modern architecture patterns, rollout strategies, user targeting

2. **Redis - Feature Rollouts and Error Triaging**
   - URL: https://redis.io/blog/using-redis-to-optimize-feature-rollouts-and-error-triaging/
   - Focus: Redis-specific implementation, performance optimization

3. **Rollout-Redis GitHub**
   - URL: https://github.com/jcagarcia/rollout-redis
   - Focus: Production-ready Redis implementation patterns

---

## Design Principles (2025)

### 1. Flexible Feature Control

**Core Concept:** Separate deployment from activation

**Benefits:**
- Deploy code to production in "dark" mode
- Activate features instantly without redeployment
- Quick rollback by flipping a flag (no code changes)
- Test in production with minimal risk

**Implementation:**
```python
# Traditional (coupled):
if NEW_FEATURE_ENABLED:  # Hardcoded constant
    new_feature()
else:
    old_feature()

# Feature flag (decoupled):
if feature_flags.is_enabled("new_feature", user_id):
    new_feature()
else:
    old_feature()
```

### 2. Gradual Rollouts

**Strategy:** Progressive feature release to increasing user percentages

**Recommended Rollout Stages:**
1. **5%** - Internal beta, monitor closely
2. **25%** - Early adopters, collect feedback
3. **50%** - Majority testing, performance validation
4. **100%** - Full rollout

**Key Metrics to Monitor:**
- Error rates
- Performance (latency, throughput)
- User engagement
- Conversion rates

**Decision Points:**
- If error rate increases >10%, rollback immediately
- If performance degrades >20%, pause at current percentage
- If metrics stable for 24 hours, proceed to next stage

### 3. User Targeting

**Targeting Approaches:**

**Percentage-based (stateless):**
```python
# Consistent hashing ensures same user always gets same experience
user_hash = hash(user_id) % 100
is_enabled = user_hash < rollout_percentage
```

**Attribute-based (stateful):**
```python
# Target specific user segments
if user.location in ["US", "UK"] and user.role == "enterprise":
    enable_feature = True
```

**Whitelist/Blacklist:**
```python
# Explicit inclusion/exclusion
if user_id in feature_whitelist:
    enable_feature = True
elif user_id in feature_blacklist:
    enable_feature = False
```

### 4. Real-Time Monitoring

**Essential Metrics:**
- Flag evaluation rate (requests/sec per flag)
- Flag distribution (% users with feature enabled)
- Feature performance (latency, errors)
- Flag staleness (time since last update)

**Observability Integration:**
```python
# Track flag usage
metrics.increment("feature_flag.evaluated", tags=["flag:new_feature"])
metrics.increment("feature_flag.enabled", tags=["flag:new_feature", "user:123"])

# Alert on anomalies
if error_rate > threshold:
    alert("Feature flag causing errors", flag="new_feature")
```

---

## Redis Integration Patterns

### 1. Data Structure Design

**Flag State Storage:**
```redis
# Global flag state
SET flag:new_feature:enabled "true"

# Rollout percentage
SET flag:new_feature:rollout_pct "25"

# User whitelist
SADD flag:new_feature:whitelist "user123" "user456"

# Metadata
HSET flag:new_feature:meta "created_by" "eng_team" "created_at" "2025-01-01"
```

**Performance Optimization:**
- Use Redis hash structures for metadata (O(1) access)
- Use sets for whitelists/blacklists (O(1) membership check)
- Cache flag state in application memory (reduce Redis calls)

### 2. High Availability

**Redis Enterprise Features:**
- **Conflict-free Replicated Databases (CRDBs)** - Multi-region consistency
- **Active-Active deployments** - Zero downtime
- **Persistence** - Survive restarts

**Fallback Strategy:**
```python
try:
    is_enabled = redis.get(f"flag:{flag_name}:enabled")
except RedisConnectionError:
    # Fallback to default (conservative)
    is_enabled = False  # Fail closed
    # OR
    is_enabled = True   # Fail open (if feature is stable)
```

### 3. Performance Considerations

**Latency Targets:**
- Flag evaluation: <1ms (in-memory cache)
- Redis lookup: <5ms (local cache miss)
- Total overhead: <10ms per request

**Caching Strategy:**
```python
# Application-level cache (30 second TTL)
@lru_cache(maxsize=1000, ttl=30)
def get_flag_state(flag_name):
    return redis.get(f"flag:{flag_name}:enabled")

# Batch preload on startup
def warmup_flag_cache():
    all_flags = redis.keys("flag:*:enabled")
    for flag in all_flags:
        get_flag_state(flag)  # Prime cache
```

---

## Rollout Strategies

### 1. Canary Deployment

**Process:**
1. Deploy to 1-2% of users (canaries)
2. Monitor for 1-2 hours
3. If metrics healthy, increase to 10%
4. Continue progressive rollout

**Canary Selection:**
- Random sampling (stateless)
- Internal users first (lower risk)
- Geographic segmentation (isolate impact)

### 2. Ring Deployment

**Staged Rollout by Environment:**
```
Development → QA → Staging → Production (5%) → Production (100%)
```

**Benefits:**
- Test in production-like environments first
- Catch issues before wide release
- Build confidence incrementally

### 3. Blue-Green with Flags

**Hybrid Approach:**
```python
# Blue = old version, Green = new version
# Both deployed, flag controls active version
if feature_flags.is_enabled("use_green_version"):
    return green_service.handle(request)
else:
    return blue_service.handle(request)
```

**Instant Rollback:**
- Set flag to 0% → All traffic to blue
- No deployment needed

---

## Best Practices (2025)

### 1. Flag Lifecycle Management

**Stages:**
1. **Creation** - Design, implement, test
2. **Rollout** - Gradual activation (5% → 100%)
3. **Stabilization** - Monitor at 100% for 2-4 weeks
4. **Cleanup** - Remove flag, merge code paths

**Automated Cleanup:**
```python
# Track flag age
if flag.created_at < (now - 90_days) and flag.rollout_pct == 100:
    alert("Flag ready for cleanup", flag=flag.name)
```

**Technical Debt Prevention:**
- Set expiration dates on flags
- Automated reminders for cleanup
- Monthly flag audit

### 2. Naming Conventions

**Pattern:** `{team}_{feature}_{type}`

**Examples:**
- `eng_semantic_routing_rollout`
- `product_new_ui_experiment`
- `ops_performance_optimization_kill_switch`

**Types:**
- `rollout` - Gradual feature release
- `experiment` - A/B test
- `kill_switch` - Emergency off switch
- `ops` - Operational flag

### 3. Access Control

**Role-Based Permissions:**
- **Viewer** - See flag state
- **Editor** - Update rollout percentage
- **Admin** - Create/delete flags
- **Emergency** - Immediate disable (kill switch)

**Audit Trail:**
```python
# Log every flag change
on_flag_change(flag_name, old_value, new_value, user):
    audit_log.write({
        "flag": flag_name,
        "old": old_value,
        "new": new_value,
        "user": user.email,
        "timestamp": datetime.now()
    })
```

### 4. Testing

**Test All Flag States:**
```python
@pytest.mark.parametrize("flag_enabled", [True, False])
def test_feature_with_flag(flag_enabled):
    with feature_flags.override("new_feature", flag_enabled):
        result = handle_request()
        assert result.is_valid
```

**Integration Tests:**
- Test flag enabled + disabled code paths
- Test flag changes during request
- Test cache invalidation
- Test Redis failure scenarios

---

## Common Patterns

### 1. Kill Switch

**Purpose:** Emergency feature disable

```python
class KillSwitch:
    def __init__(self, redis_client):
        self.redis = redis_client

    def is_active(self, feature):
        # Check kill switch (inverted logic)
        killed = self.redis.get(f"kill:{feature}")
        return killed != "true"

    def kill(self, feature, reason):
        self.redis.set(f"kill:{feature}", "true")
        alert(f"Feature killed: {feature}", reason=reason)
```

### 2. Gradual Rollout

**Implementation:**
```python
class GradualRollout:
    def is_enabled(self, flag, user_id):
        # Check whitelist first
        if self.redis.sismember(f"flag:{flag}:whitelist", user_id):
            return True

        # Check percentage
        rollout_pct = float(self.redis.get(f"flag:{flag}:rollout_pct") or 0)
        user_hash = hash(user_id) % 100
        return user_hash < rollout_pct
```

### 3. A/B Testing

**Variant Assignment:**
```python
class ABTest:
    def get_variant(self, experiment, user_id):
        # Consistent variant assignment
        user_hash = hash(f"{experiment}:{user_id}") % 100

        # Example: 50/50 split
        if user_hash < 50:
            return "control"
        else:
            return "treatment"
```

---

## Monitoring & Alerting

### Key Metrics

**Flag Health:**
- Evaluation rate (calls/sec)
- Error rate
- Cache hit rate
- Redis latency

**Feature Health:**
- Feature usage (% requests using feature)
- Feature errors (errors from feature code)
- Feature performance (latency delta)

### Alert Thresholds

```python
# Alert rules
alerts = {
    "flag_error_rate": {
        "threshold": 0.01,  # 1% errors
        "action": "rollback"
    },
    "flag_latency_p99": {
        "threshold": 100,  # 100ms
        "action": "investigate"
    },
    "flag_stale": {
        "threshold": 300,  # 5 minutes
        "action": "notify"
    }
}
```

---

## Production Checklist

✅ **Before Launch:**
- [ ] Flag naming follows convention
- [ ] Default state is safe (fail-closed or fail-open decided)
- [ ] Rollout plan documented (5% → 25% → 50% → 100%)
- [ ] Monitoring dashboards created
- [ ] Alert thresholds configured
- [ ] Rollback procedure tested
- [ ] Team trained on flag usage
- [ ] Cleanup date set (flag expiration)

✅ **During Rollout:**
- [ ] Monitor error rates at each stage
- [ ] Check performance metrics (latency, throughput)
- [ ] Collect user feedback
- [ ] Pause if anomalies detected
- [ ] Document issues and resolutions

✅ **After 100% Rollout:**
- [ ] Monitor for 2-4 weeks
- [ ] Verify feature stability
- [ ] Schedule flag cleanup
- [ ] Remove flag code
- [ ] Archive flag history

---

## Anti-Patterns (Avoid These)

❌ **Long-Lived Flags**
- Flags should be temporary (weeks to months, not years)
- Set expiration dates
- Automate cleanup

❌ **Nested Flags**
```python
# BAD: Complex flag dependencies
if flag_a and not flag_b and (flag_c or flag_d):
    complex_feature()
```

❌ **No Monitoring**
- Always track flag usage and impact
- Set up alerts for anomalies

❌ **Hardcoded Defaults**
```python
# BAD: No fallback strategy
is_enabled = redis.get("flag")  # What if Redis is down?

# GOOD: Safe default
is_enabled = redis.get("flag") or False  # Fail closed
```

❌ **Testing Only One State**
- Test both enabled and disabled code paths
- Test transitions (flag changes mid-request)

---

## Tools & Libraries (2025)

**Open Source:**
- **Unleash** - Self-hosted, feature-rich
- **Flagsmith** - Open-source, API-first
- **Rollout-Redis** - Lightweight Ruby/Python
- **GrowthBook** - A/B testing focus

**Commercial:**
- **LaunchDarkly** - Enterprise-grade, extensive SDKs
- **Split.io** - Feature delivery platform
- **Optimizely** - Experimentation focus
- **ConfigCat** - Simple, affordable

**For Apex Memory System:**
- Use custom Redis-based implementation (lightweight, full control)
- Integrate with existing Redis infrastructure
- Minimal dependencies

---

## References

1. **FeatBit: Feature Flag System Design 2025**
   - https://www.featbit.co/articles2025/feature-flag-system-design-2025

2. **Redis: Using Redis to Optimize Feature Rollouts**
   - https://redis.io/blog/using-redis-to-optimize-feature-rollouts-and-error-triaging/

3. **GitHub: rollout-redis**
   - https://github.com/jcagarcia/rollout-redis

4. **Martin Fowler: Feature Toggles (Feature Flags)**
   - https://martinfowler.com/articles/feature-toggles.html

5. **LaunchDarkly: Feature Flag Best Practices**
   - https://launchdarkly.com/blog/feature-flag-best-practices/

---

**Document Version:** 1.0
**Last Updated:** January 2025
**Next Review:** July 2025
