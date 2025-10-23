# 09 - Cache Layer (Redis)

## 🎯 Purpose

Provides sub-10ms response times for repeat queries through intelligent caching. Achieves 95% cache hit rate in steady state for dramatic performance improvement.

## 🛠 Technical Stack

- **Redis 8.2-alpine:** In-memory cache
- **LRU Eviction:** Least Recently Used policy
- **AOF Persistence:** Append-Only File for durability
- **SHA256 Hashing:** Cache key generation

## 📂 Key Files

**1. query_cache.py** (Located in `apex-memory-system/src/apex_memory/cache/`)

```python
class QueryCache:
    """Redis-based query result caching."""
    
    def get(query: str, filters: dict = None) -> Optional[Any]:
        """Get cached result (sub-10ms if hit)."""
        
    def set(query: str, result: Any, ttl: int = 3600):
        """Cache result with 1-hour TTL."""
        
    def invalidate(query: str):
        """Remove cached result."""
        
    def stats() -> CacheStats:
        """Return hit rate, size, total queries."""
```

## Cache Strategy

### Key Generation
```python
# SHA256 hash for consistent keys
key_data = {"query": query, "filters": filters or {}}
key_string = json.dumps(key_data, sort_keys=True)
cache_key = f"query:{hashlib.sha256(key_string.encode()).hexdigest()}"
```

### TTL Strategy
- **Query Results:** 1 hour (3600s)
- **Conversations:** 5 minutes (300s)
- **User Profiles:** 1 hour (3600s)

### Eviction Policy
- **Max Memory:** 1GB
- **Policy:** allkeys-lru (evict least recently used)
- **Result:** Automatic cleanup when memory full

## Performance

### Cache Hit Rate
- **Steady State:** 95%
- **Cold Start:** 0% (gradually increases)
- **After 100 queries:** 70-80%

### Latency
- **Cache Hit:** <10ms (P99)
- **Cache Miss:** 600ms-2.5s (query execution time)

## Configuration

```bash
# Redis Connection
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Cache TTL (seconds)
CACHE_TTL_CONVERSATION=300      # 5 minutes
CACHE_TTL_PROFILE=3600          # 1 hour
CACHE_TTL_SEARCH=600            # 10 minutes
```

## Example Usage

```python
from apex_memory.cache.query_cache import QueryCache

cache = QueryCache()

# Check cache before querying
cached_result = cache.get(query="What is ACME Corp?")
if cached_result:
    return cached_result  # <10ms

# Execute query if cache miss
result = execute_query(query)

# Store in cache for future requests
cache.set(query="What is ACME Corp?", result=result, ttl=3600)
```

---

**Previous Component:** [08-Frontend-Application](../08-Frontend-Application/README.md)
**Next Component:** [10-Monitoring-Observability](../10-Monitoring-Observability/README.md)
