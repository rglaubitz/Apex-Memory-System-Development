# Troubleshooting Guide - Query Router

**Comprehensive issue resolution for all 4 phases**

---

## 📋 Quick Diagnosis

**Symptoms → Solutions:**

| Symptom | Likely Cause | Quick Fix |
|---------|--------------|-----------|
| Tests fail with `ImportError` | Missing dependencies | `pip install -r requirements.txt` |
| `Connection refused` errors | Services not running | `docker-compose up -d` |
| `AuthenticationError` | Invalid API keys | Check `.env` file |
| High latency (>2s) | Database overload | Check connection pools |
| Low cache hit rate (<50%) | Cache not working | Check Redis connection |
| Feature flags not working | Redis connection | Verify Redis running |
| Weights not updating | Background task crashed | Check logs, restart |
| Negative rewards | Bad feedback signals | Review reward computation |

---

## 🧪 Test Failures

### ImportError: No module named 'X'

**Error:**
```python
ImportError: No module named 'semantic_router'
ImportError: No module named 'anthropic'
ImportError: No module named 'redis'
```

**Cause:** Python dependencies not installed

**Fix:**
```bash
# Reinstall all dependencies
cd apex-memory-system
pip install -r requirements.txt

# Verify specific package
pip show semantic-router
pip show anthropic

# If package still missing, install directly
pip install semantic-router anthropic redis
```

**Prevention:** Always run `pip install -r requirements.txt` after pulling code

---

### Database Connection Refused

**Error:**
```python
psycopg2.OperationalError: connection to server at "localhost", port 5432 failed: Connection refused
neo4j.exceptions.ServiceUnavailable: Connection to bolt://localhost:7687 failed
```

**Cause:** Database services not running

**Fix:**
```bash
# Start all database services
cd docker && docker-compose up -d

# Wait for services to initialize (30 seconds)
sleep 30

# Verify all services healthy
docker-compose ps

# Check specific service logs
docker-compose logs postgres
docker-compose logs neo4j
docker-compose logs redis
docker-compose logs qdrant

# If service unhealthy, restart it
docker-compose restart postgres
```

**Prevention:** Run `docker-compose up -d` before running tests

---

### API Authentication Errors

**Error:**
```python
openai.AuthenticationError: Incorrect API key provided
anthropic.AuthenticationError: Invalid API key
```

**Cause:** Missing or invalid API keys

**Fix:**
```bash
# Check .env file exists
ls -la .env

# Verify API keys set
cat .env | grep API_KEY

# Test OpenAI key
python -c "
from openai import OpenAI
client = OpenAI()
print('OpenAI: OK' if client.models.list() else 'FAIL')
"

# Test Anthropic key
python -c "
import anthropic
client = anthropic.Anthropic()
print('Anthropic: OK' if client.messages.create(
    model='claude-3-5-sonnet-20241022',
    max_tokens=10,
    messages=[{'role':'user','content':'hi'}]
) else 'FAIL')
"

# If keys invalid, get new keys:
# OpenAI: https://platform.openai.com/api-keys
# Anthropic: https://console.anthropic.com/settings/keys
```

**Prevention:** Keep `.env` file up to date, don't commit keys to Git

---

### AsyncIO Event Loop Errors

**Error:**
```python
RuntimeError: Event loop is closed
RuntimeError: There is no current event loop in thread
```

**Cause:** pytest-asyncio not installed or misconfigured

**Fix:**
```bash
# Install pytest-asyncio
pip install pytest-asyncio

# Verify pytest.ini configuration
cat pytest.ini | grep asyncio_mode
# Should show: asyncio_mode = auto

# If missing, add to pytest.ini:
echo "asyncio_mode = auto" >> pytest.ini
```

**Prevention:** Include `pytest-asyncio` in test dependencies

---

### Timeout Errors

**Error:**
```python
pytest.TimeoutExpired: Test took longer than 300 seconds
```

**Cause:** Tests running too slow or stuck

**Fix:**
```bash
# Increase timeout for specific test
pytest tests/unit/test_slow.py -o addopts="" --timeout=600

# Or edit pytest.ini
# Change: --timeout=300 → --timeout=600

# Check if database services slow
docker stats  # Look for high CPU/memory usage
```

**Prevention:** Monitor test execution times, optimize slow tests

---

## 🚀 Runtime Errors

### Feature Flag Redis Connection Errors

**Error:**
```python
redis.exceptions.ConnectionError: Error 61 connecting to localhost:6379. Connection refused.
```

**Cause:** Redis not running or wrong connection string

**Fix:**
```bash
# Check Redis running
docker-compose ps redis

# If not running, start it
docker-compose up -d redis

# Test connection
redis-cli ping
# Should return: PONG

# Check connection string in .env
cat .env | grep REDIS
# Should be: REDIS_HOST=localhost
#            REDIS_PORT=6379

# Test from Python
python -c "
import redis
r = redis.Redis(host='localhost', port=6379)
print('Redis: OK' if r.ping() else 'FAIL')
"
```

**Prevention:** Always verify Redis running before enabling feature flags

---

### Online Learning Queue Overflow

**Error:**
```python
asyncio.Queue full: queue size exceeded 10000
```

**Cause:** Feedback queue not being processed fast enough

**Fix:**
```python
# Check background task running
stats = router.online_learning_router.get_stats()
print(f"Queue size: {stats['queue_size']}")
print(f"Batch updates: {stats['batch_update_count']}")

# If queue size growing:
# 1. Increase batch size (process more at once)
router = QueryRouter(
    ...,
    online_learning_batch_size=200  # Increase from 100
)

# 2. Increase learning rate (faster processing)
router = QueryRouter(
    ...,
    online_learning_rate=0.02  # Increase from 0.01
)

# 3. Add more worker threads
# (Future enhancement - not yet implemented)
```

**Prevention:** Monitor queue size, alert if >1000

---

### Weight Update Failures

**Error:**
```python
np.linalg.LinAlgError: Singular matrix
```

**Cause:** LinUCB covariance matrix became singular (numerical instability)

**Fix:**
```python
# This is handled automatically in online_learning.py
# Uses pseudoinverse fallback

# If persistent, reduce learning rate
router = QueryRouter(
    ...,
    online_learning_rate=0.005  # Lower from 0.01
)

# Or reset weights
await router.online_learning_router.base_bandit.load_weights()
```

**Prevention:** Use conservative learning rates (0.01 or lower)

---

### Cache Invalidation Issues

**Error:**
```
Cache hit rate dropped from 90% to 30%
```

**Cause:** Cache invalidation too aggressive or Redis memory full

**Fix:**
```bash
# Check Redis memory usage
redis-cli info memory

# If memory usage >90%, increase maxmemory
docker-compose down
# Edit docker-compose.yml:
# redis: command: redis-server --maxmemory 2gb  # Increase from 1gb
docker-compose up -d

# Check cache TTL settings
cat .env | grep CACHE_TTL

# Verify semantic cache working
python -c "
from apex_memory.query_router.semantic_cache import SemanticCache
# Test cache operations
"
```

**Prevention:** Monitor Redis memory, set alerts at 80%

---

## ⚡ Performance Issues

### High Query Latency (>2s)

**Symptoms:** P99 latency >2000ms (should be <1000ms)

**Diagnosis:**
```python
# Check which component is slow
from apex_memory.query_router.analytics import RoutingAnalytics

analytics = RoutingAnalytics(postgres_dsn=...)
await analytics.initialize()

# Get latency breakdown
breakdown = await analytics.get_latency_breakdown()
print(breakdown)
# Example output:
# {
#   'intent_classification': 50ms,
#   'query_rewriting': 200ms,  # ← Slow!
#   'embedding_generation': 100ms,
#   'database_routing': 800ms,
#   'result_aggregation': 50ms
# }
```

**Fixes:**

**If query_rewriting is slow (>500ms):**
```python
# Reduce Claude max_tokens
router = QueryRouter(
    ...,
    anthropic_max_tokens=256  # Reduce from 512
)

# Or disable for simple queries
router = QueryRouter(
    ...,
    enable_query_rewriting=False  # Disable entirely
)
```

**If database_routing is slow (>1000ms):**
```bash
# Check database connection pools
docker stats  # Look for resource constraints

# Increase connection pool size
# Edit .env:
POSTGRES_MAX_POOL_SIZE=30  # Increase from 20
```

**If embedding_generation is slow (>500ms):**
```python
# Use smaller embedding model
# Edit .env:
OPENAI_EMBEDDING_MODEL=text-embedding-3-small  # Faster than large
OPENAI_EMBEDDING_DIMENSIONS=1536  # Reduce if using large
```

**Prevention:** Monitor latency per component, set alerts

---

### Low Cache Hit Rate (<70%)

**Symptoms:** Cache hit rate dropped below 70% (target: 90%+)

**Diagnosis:**
```python
# Check cache stats
stats = await router.semantic_cache.get_stats()
print(f"Hit rate: {stats['hit_rate']:.1%}")
print(f"Total queries: {stats['total_queries']}")
print(f"Cache hits: {stats['cache_hits']}")
```

**Fixes:**

**If similarity threshold too high:**
```python
# Lower threshold (more lenient matching)
router = QueryRouter(
    ...,
    cache_similarity_threshold=0.90  # Lower from 0.95
)
```

**If cache TTL too short:**
```bash
# Increase cache TTL
# Edit .env:
CACHE_TTL_SEARCH=1200  # Increase from 600 (10 min → 20 min)
```

**If query diversity too high:**
```python
# This is expected if users asking very different questions
# Monitor trend, not absolute value
```

**Prevention:** Track cache hit rate daily, investigate drops >10%

---

### Memory Leaks

**Symptoms:** Memory usage growing unbounded

**Diagnosis:**
```bash
# Monitor memory usage
docker stats

# Check Python process memory
ps aux | grep python

# Use memory profiler
pip install memory-profiler
python -m memory_profiler script.py
```

**Fixes:**

**If feedback queue growing:**
```python
# Check queue size
stats = router.online_learning_router.get_stats()
if stats['queue_size'] > 1000:
    print("Queue overflow - increase batch size")
```

**If pending_contexts dict growing:**
```python
# Old query contexts not being cleaned up
# Check size
print(f"Pending: {len(router.online_learning_router.pending_contexts)}")

# Implement cleanup (add to online_learning.py)
# Remove contexts older than 1 hour
```

**Prevention:** Monitor memory usage, set alerts at 80%

---

## 🚩 Feature Flag Issues

### Inconsistent User Experience (Flickering)

**Symptoms:** User gets different experience on each request

**Cause:** Not using consistent hashing correctly

**Diagnosis:**
```python
# Test same user multiple times
user_id = "test_user_123"
results = []
for i in range(10):
    eval = await router.feature_flags.is_enabled("phase4_online_learning", user_id)
    results.append(eval.enabled)

print(f"Consistency: {len(set(results)) == 1}")  # Should be True
```

**Fix:**
```python
# Feature flags use consistent hashing by default
# If flickering, ensure user_id is consistent

# BAD: Different user_id each time
eval = await router.feature_flags.is_enabled("flag", str(uuid.uuid4()))

# GOOD: Same user_id for same user
eval = await router.feature_flags.is_enabled("flag", request.user_id)
```

**Prevention:** Always pass consistent user_id

---

### Rollout Percentage Not Working

**Symptoms:** 50% rollout but seeing 90% enabled

**Diagnosis:**
```python
# Check flag state
flag_state = await router.feature_flags.get_flag("phase4_online_learning")
print(f"Rollout: {flag_state.rollout_percentage}%")
print(f"Whitelist: {len(flag_state.whitelist)} users")
print(f"Blacklist: {len(flag_state.blacklist)} users")

# Whitelist overrides percentage!
```

**Fix:**
```python
# Clear whitelist if testing percentage rollout
whitelist_users = await router.feature_flags.get_flag("phase4").whitelist
for user_id in whitelist_users:
    # Remove from whitelist
    await router.redis.srem("flag:phase4:whitelist", user_id)
```

**Prevention:** Document which users are whitelisted

---

## 🤖 Online Learning Issues

### Weights Not Updating

**Symptoms:** Feedback being recorded but weights not changing

**Diagnosis:**
```python
# Check if background task running
assert router.online_learning_router.learning_task is not None
assert not router.online_learning_router.learning_task.done()

# Check batch count
stats = router.online_learning_router.get_stats()
print(f"Batch updates: {stats['batch_update_count']}")  # Should be increasing

# Check feedback queue
print(f"Queue size: {stats['queue_size']}")  # Should be processing (not growing)
```

**Fixes:**

**If background task crashed:**
```python
# Check logs for errors
# Restart online learning
await router.online_learning_router.close()
router.online_learning_router = OnlineLearningRouter(...)
await router.online_learning_router.initialize()
```

**If batch size too large:**
```python
# Reduce batch size for faster updates
router = QueryRouter(
    ...,
    online_learning_batch_size=50  # Reduce from 100
)
```

**Prevention:** Monitor batch update count, alert if not increasing

---

### Negative Average Reward

**Symptoms:** Average reward <0.3 (should be 0.5-0.8)

**Cause:** Bad reward computation or poor routing decisions

**Diagnosis:**
```python
# Check per-database rewards
stats = router.online_learning_router.get_stats()
for db, db_stats in stats['databases'].items():
    print(f"{db}: {db_stats['avg_reward']:.3f}")
```

**Fixes:**

**If all databases have low rewards:**
```python
# Review reward computation weights
router.online_learning_router.reward_weights = {
    'clicked': 0.5,        # Increase click weight
    'dwell_time': 0.3,     # Keep same
    'explicit_rating': 0.2, # Keep same
    'latency': 0.0         # Remove latency penalty temporarily
}
```

**If specific database has low rewards:**
```python
# That database might be performing poorly
# Investigate why users unhappy with results from that DB
```

**Prevention:** Monitor per-database rewards, investigate drops

---

### Learning Rate Too Aggressive

**Symptoms:** Weights oscillating, performance unstable

**Diagnosis:**
```python
# Check weight change magnitude
# (Add monitoring to online_learning.py)
weight_changes = []
# Track |theta_new - theta_old| per update
```

**Fix:**
```python
# Reduce learning rate
router.online_learning_router.adjust_learning_rate(0.005)  # Lower from 0.01

# Or disable online learning temporarily
await router.feature_flags.set_rollout_percentage("phase4_online_learning", 0)
```

**Prevention:** Start with conservative learning rate (0.01)

---

## 🔥 Emergency Procedures

### Complete System Failure

**Symptoms:** Everything broken, can't route queries

**Emergency Rollback:**
```bash
# 1. Rollback Phase 4 instantly
python -c "
import asyncio
from apex_memory.query_router.router import QueryRouter

async def rollback():
    router = QueryRouter(...)  # Initialize
    await router.feature_flags.set_rollout_percentage('phase4_online_learning', 0)
    print('Phase 4 disabled')

asyncio.run(rollback())
"

# 2. Restart all services
cd docker && docker-compose restart

# 3. Check service health
docker-compose ps

# 4. Tail logs for errors
docker-compose logs -f --tail=100
```

---

### Data Corruption

**Symptoms:** Weights corrupted, wrong results

**Fix:**
```bash
# 1. Stop online learning
await router.online_learning_router.close()

# 2. Reset weights to Phase 2 baseline
DELETE FROM bandit_weights WHERE updated_at > '2025-10-08';

# 3. Reload weights
await router.online_learning_router.base_bandit.load_weights()

# 4. Restart with clean state
await router.online_learning_router.initialize()
```

---

## 📞 Getting Help

**Escalation Path:**

1. **Check this troubleshooting guide**
2. **Search logs:** `grep -r "ERROR" logs/apex-memory.log`
3. **Check database health:** `docker-compose ps`
4. **Review recent changes:** `git log --oneline -10`
5. **If still stuck:** Document issue, rollback, investigate later

**Log Locations:**
- Application: `logs/apex-memory.log`
- PostgreSQL: `docker-compose logs postgres`
- Neo4j: `docker-compose logs neo4j`
- Redis: `docker-compose logs redis`
- Qdrant: `docker-compose logs qdrant`

**Useful Commands:**
```bash
# View all logs
docker-compose logs -f --tail=100

# Search for errors
grep -i error logs/*.log

# Check resource usage
docker stats

# Restart everything
docker-compose down && docker-compose up -d
```

---

**Troubleshooting Guide v1.0**
**Last Updated:** 2025-10-07
**Next Review:** 2025-11-07
