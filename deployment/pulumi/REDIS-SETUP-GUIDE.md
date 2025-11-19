# Redis Setup Guide

**Date:** 2025-11-16
**Status:** ✅ Complete
**Instance:** apex-redis-dev

---

## 📋 Overview

This guide covers how to access, manage, and use the Redis Memorystore caching layer deployed in Week 2.

**Instance Details:**
- Name: `apex-redis-dev`
- Private IP: `10.123.172.227`
- Port: `6379`
- Tier: BASIC (1GB)
- Version: Redis 7.0
- Region: us-central1
- Eviction Policy: allkeys-lru (Least Recently Used)

---

## 🔌 Accessing Redis

Redis Memorystore is accessible only from within the VPC network.

### From Cloud Shell (Recommended)

**Step 1: Install redis-cli**
```bash
# Open Cloud Shell: https://shell.cloud.google.com

# Install redis-cli
sudo apt-get update
sudo apt-get install -y redis-tools
```

**Step 2: Connect to Redis**
```bash
# Connect using redis-cli
redis-cli -h 10.123.172.227 -p 6379

# Test connection
127.0.0.1:6379> PING
PONG

# Check server info
127.0.0.1:6379> INFO server
```

---

### From Compute Engine VM

If you have a VM in the same VPC:

```bash
# SSH into VM
gcloud compute ssh <your-vm-name> --zone=us-central1-a

# Install redis-cli
sudo apt-get update
sudo apt-get install -y redis-tools

# Connect
redis-cli -h 10.123.172.227 -p 6379
```

---

### From Python Application

```python
import redis

# Create Redis client
r = redis.Redis(
    host="10.123.172.227",
    port=6379,
    decode_responses=True  # Automatically decode bytes to strings
)

# Test connection
print(r.ping())  # Should print: True

# Basic operations
r.set("key", "value")
print(r.get("key"))  # Should print: value
```

---

## 🔧 CLI Access Examples

### Basic Commands

**String Operations:**
```bash
# Set a key
SET mykey "Hello Redis"

# Get a key
GET mykey

# Set with expiration (60 seconds)
SETEX tempkey 60 "Expires in 60 seconds"

# Check if key exists
EXISTS mykey

# Delete a key
DEL mykey

# Get all keys (use with caution in production)
KEYS *

# Scan keys (better for production)
SCAN 0 MATCH user:* COUNT 100
```

**Numeric Operations:**
```bash
# Increment a counter
SET counter 0
INCR counter
# Returns: 1

INCRBY counter 10
# Returns: 11

DECR counter
# Returns: 10
```

**Expiration:**
```bash
# Set expiration on existing key (seconds)
EXPIRE mykey 300

# Set expiration (milliseconds)
PEXPIRE mykey 300000

# Check time to live
TTL mykey

# Remove expiration
PERSIST mykey
```

---

### Hash Operations (Dictionaries)

**Hash Commands:**
```bash
# Set hash fields
HSET user:1000 name "Alice"
HSET user:1000 email "alice@example.com"
HSET user:1000 age "30"

# Get single field
HGET user:1000 name

# Get all fields
HGETALL user:1000

# Get multiple fields
HMGET user:1000 name email

# Set multiple fields at once
HMSET user:1001 name "Bob" email "bob@example.com" age "25"

# Check if field exists
HEXISTS user:1000 name

# Delete field
HDEL user:1000 age

# Get all field names
HKEYS user:1000

# Get all values
HVALS user:1000

# Increment hash field
HINCRBY user:1000 age 1
```

---

### List Operations (Queues)

**List Commands:**
```bash
# Push to right (append)
RPUSH mylist "item1"
RPUSH mylist "item2" "item3"

# Push to left (prepend)
LPUSH mylist "item0"

# Get list length
LLEN mylist

# Get range of items (0 = first, -1 = last)
LRANGE mylist 0 -1

# Pop from left (queue behavior)
LPOP mylist

# Pop from right (stack behavior)
RPOP mylist

# Get element by index
LINDEX mylist 0

# Set element by index
LSET mylist 0 "new_item"

# Trim list to range
LTRIM mylist 0 9  # Keep only first 10 items

# Blocking pop (wait for item, timeout in seconds)
BLPOP mylist 30
```

---

### Set Operations (Unique Values)

**Set Commands:**
```bash
# Add members to set
SADD tags "redis" "cache" "database"

# Get all members
SMEMBERS tags

# Check if member exists
SISMEMBER tags "redis"

# Remove member
SREM tags "cache"

# Get set size
SCARD tags

# Pop random member
SPOP tags

# Set operations (union, intersection, difference)
SADD set1 "a" "b" "c"
SADD set2 "b" "c" "d"

SUNION set1 set2      # a, b, c, d
SINTER set1 set2      # b, c
SDIFF set1 set2       # a
```

---

### Sorted Set Operations (Ranked Data)

**Sorted Set Commands:**
```bash
# Add members with scores
ZADD leaderboard 100 "Alice"
ZADD leaderboard 85 "Bob"
ZADD leaderboard 92 "Charlie"

# Get range by rank (lowest to highest)
ZRANGE leaderboard 0 -1 WITHSCORES

# Get range by rank (highest to lowest)
ZREVRANGE leaderboard 0 -1 WITHSCORES

# Get rank of member (0-based)
ZRANK leaderboard "Bob"

# Get score of member
ZSCORE leaderboard "Alice"

# Increment score
ZINCRBY leaderboard 5 "Bob"

# Get members by score range
ZRANGEBYSCORE leaderboard 80 95

# Remove member
ZREM leaderboard "Charlie"

# Get set size
ZCARD leaderboard
```

---

## 💾 Cache Usage Patterns

### Pattern 1: Simple Key-Value Cache

**Use Case:** Cache database query results, API responses

```python
import redis
import json

r = redis.Redis(host="10.123.172.227", port=6379, decode_responses=True)

def get_user_profile(user_id):
    # Try cache first
    cache_key = f"user:{user_id}"
    cached = r.get(cache_key)

    if cached:
        return json.loads(cached)

    # Cache miss - fetch from database
    profile = fetch_from_database(user_id)

    # Store in cache (expire in 5 minutes)
    r.setex(cache_key, 300, json.dumps(profile))

    return profile
```

---

### Pattern 2: Session Storage

**Use Case:** Store user session data

```python
import uuid

def create_session(user_id, user_data):
    session_id = str(uuid.uuid4())
    session_key = f"session:{session_id}"

    # Store session (expire in 1 hour)
    r.hmset(session_key, user_data)
    r.expire(session_key, 3600)

    return session_id

def get_session(session_id):
    session_key = f"session:{session_id}"
    session_data = r.hgetall(session_key)

    # Extend session expiration on access
    r.expire(session_key, 3600)

    return session_data
```

---

### Pattern 3: Rate Limiting

**Use Case:** Limit API requests per user

```python
def check_rate_limit(user_id, max_requests=100, window_seconds=3600):
    key = f"ratelimit:{user_id}"

    # Increment request counter
    current = r.incr(key)

    # Set expiration on first request
    if current == 1:
        r.expire(key, window_seconds)

    # Check if limit exceeded
    if current > max_requests:
        ttl = r.ttl(key)
        raise RateLimitExceeded(f"Try again in {ttl} seconds")

    return current
```

---

### Pattern 4: Leaderboard

**Use Case:** Rankings, high scores, trending content

```python
def add_score(user_id, score):
    r.zadd("leaderboard", {user_id: score})

def get_top_10():
    # Get top 10 users with scores
    return r.zrevrange("leaderboard", 0, 9, withscores=True)

def get_user_rank(user_id):
    # Get user's rank (0-based, lower is better)
    rank = r.zrevrank("leaderboard", user_id)
    return rank + 1 if rank is not None else None

def get_score(user_id):
    return r.zscore("leaderboard", user_id)
```

---

### Pattern 5: Message Queue

**Use Case:** Background job processing, task queue

```python
def enqueue_task(task_data):
    task_json = json.dumps(task_data)
    r.rpush("task_queue", task_json)

def process_tasks():
    while True:
        # Block for 10 seconds waiting for task
        result = r.blpop("task_queue", timeout=10)

        if result:
            queue_name, task_json = result
            task_data = json.loads(task_json)
            process_task(task_data)
```

---

### Pattern 6: Distributed Lock

**Use Case:** Prevent concurrent execution across multiple servers

```python
import time

def acquire_lock(lock_name, timeout=10):
    lock_key = f"lock:{lock_name}"
    identifier = str(uuid.uuid4())

    # Try to acquire lock
    if r.set(lock_key, identifier, nx=True, ex=timeout):
        return identifier
    return None

def release_lock(lock_name, identifier):
    lock_key = f"lock:{lock_name}"

    # Only release if we own the lock
    if r.get(lock_key) == identifier:
        r.delete(lock_key)
        return True
    return False

# Usage
lock_id = acquire_lock("critical_section")
if lock_id:
    try:
        # Do critical work
        pass
    finally:
        release_lock("critical_section", lock_id)
```

---

## 📊 Monitoring Commands

### Server Information

```bash
# Get server info
INFO

# Specific sections
INFO server
INFO memory
INFO stats
INFO replication
INFO cpu

# Get configuration
CONFIG GET *
CONFIG GET maxmemory*

# Current memory usage
INFO memory | grep used_memory_human

# Connected clients
INFO clients

# Command statistics
INFO commandstats
```

---

### Performance Monitoring

**Monitor Commands in Real-Time:**
```bash
# Watch all commands (debugging only, high overhead)
MONITOR

# Get slow log (commands taking >10ms by default)
SLOWLOG GET 10

# Reset slow log
SLOWLOG RESET
```

**Key Metrics to Watch:**
```bash
# Memory usage
INFO memory | grep -E "used_memory_human|maxmemory_human"

# Hit rate
INFO stats | grep keyspace_hits
INFO stats | grep keyspace_misses

# Evictions (keys removed due to memory pressure)
INFO stats | grep evicted_keys

# Connections
INFO clients | grep connected_clients
```

---

### Database Statistics

```bash
# Get database key counts
INFO keyspace

# Count keys by pattern (use SCAN in production)
EVAL "return #redis.call('keys', 'user:*')" 0

# Sample random key
RANDOMKEY

# Check memory usage of key
MEMORY USAGE mykey

# Get key type
TYPE mykey
```

---

## 🎯 Performance Tuning

### Configuration Check

```bash
# Check current configuration
redis-cli -h 10.123.172.227 -p 6379 CONFIG GET maxmemory-policy

# Should return: allkeys-lru (Least Recently Used eviction)
```

---

### LRU Eviction Policy

**How it works:**
- When memory is full, Redis evicts the least recently used keys
- Ensures cache always has most recent/relevant data
- No manual cleanup needed

**Verify eviction:**
```bash
# Check eviction stats
INFO stats | grep evicted_keys

# Should increase over time as cache fills up
```

---

### Best Practices

**1. Use Appropriate Data Types**
```bash
# Bad: Storing JSON as string
SET user:1000 '{"name":"Alice","age":30}'

# Good: Use hash
HMSET user:1000 name "Alice" age 30
```

**2. Set Expiration on Cache Keys**
```python
# Always set TTL on cached data
r.setex("cache:query:123", 300, data)  # 5 minutes
```

**3. Use SCAN Instead of KEYS**
```bash
# Bad: KEYS * (blocks server)
KEYS user:*

# Good: SCAN (non-blocking)
SCAN 0 MATCH user:* COUNT 100
```

**4. Pipeline Multiple Commands**
```python
# Bad: Multiple round trips
r.set("key1", "value1")
r.set("key2", "value2")
r.set("key3", "value3")

# Good: Pipeline (one round trip)
pipe = r.pipeline()
pipe.set("key1", "value1")
pipe.set("key2", "value2")
pipe.set("key3", "value3")
pipe.execute()
```

---

## 🔍 Troubleshooting

### Connection Refused

**Error:**
```
redis.exceptions.ConnectionError: Error 111 connecting to 10.123.172.227:6379. Connection refused.
```

**Causes:**
1. Not in VPC (cannot access private IP)
2. Redis instance not ready
3. Firewall rules blocking port

**Solutions:**
- Connect from Cloud Shell or Compute Engine VM in VPC
- Check instance status: `gcloud redis instances describe apex-redis-dev --region=us-central1`
- Verify instance is READY state

---

### Memory Issues

**Check Memory Usage:**
```bash
# Get current memory usage
redis-cli -h 10.123.172.227 -p 6379 INFO memory | grep used_memory_human

# Check if evictions are happening
redis-cli -h 10.123.172.227 -p 6379 INFO stats | grep evicted_keys
```

**Solutions:**
- Evictions are NORMAL with LRU policy (expected behavior)
- If eviction rate is too high, consider upgrading to 2GB or 5GB tier
- Review TTL settings on keys (shorter TTL = less memory pressure)

---

### Slow Performance

**Check Hit Rate:**
```bash
# Get hit/miss statistics
redis-cli -h 10.123.172.227 -p 6379 INFO stats | grep keyspace

# Calculate hit rate:
# hit_rate = hits / (hits + misses)
# Target: >80% hit rate for cache
```

**Solutions:**
- Low hit rate: Review caching strategy (are you caching the right data?)
- Network latency: Ensure application is in same VPC/region
- Use pipelining for multiple commands

---

### Data Loss After Instance Restart

**Behavior:**
- BASIC tier Redis has **no persistence** (data is in-memory only)
- All data is lost on instance restart or failure

**Solutions:**
- This is expected for cache workloads (cache can rebuild)
- For persistent data, use PostgreSQL or Neo4j instead
- To enable persistence, upgrade to STANDARD_HA tier (adds RDB snapshots)

---

## 📚 Learning Resources

**Official Documentation:**
- Redis Commands: https://redis.io/commands/
- Redis Data Types: https://redis.io/docs/data-types/
- Redis Best Practices: https://redis.io/docs/management/optimization/

**Interactive Learning:**
- Try Redis: https://try.redis.io/
- Redis University: https://university.redis.com/

**Python Client:**
- redis-py Documentation: https://redis-py.readthedocs.io/

---

## 🚀 Next Steps

1. ✅ **Connect from Cloud Shell** - Install redis-cli and test connection
2. ✅ **Try CLI Commands** - Practice string, hash, list operations
3. ✅ **Test Python Client** - Run example code from CONNECTION-PATTERNS.md
4. ✅ **Implement Cache Pattern** - Choose pattern from Cache Usage Patterns section
5. ✅ **Monitor Performance** - Track hit rate and memory usage
6. 🔜 **Integrate with Application** - Connect from Cloud Run service

---

## 🔗 Integration with Application

**Example Cloud Run Configuration:**
```python
# In your FastAPI or Flask application
import os
import redis

REDIS_HOST = os.getenv("REDIS_HOST", "10.123.172.227")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

# Create global Redis client
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True,
    socket_connect_timeout=5,
    socket_timeout=5,
    retry_on_timeout=True,
    health_check_interval=30
)

# Health check endpoint
@app.get("/health/redis")
async def redis_health():
    try:
        redis_client.ping()
        return {"status": "healthy"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
```

**Environment Variables in Cloud Run:**
```bash
gcloud run services update apex-api \
  --set-env-vars REDIS_HOST=10.123.172.227,REDIS_PORT=6379 \
  --region us-central1
```

---

**Last Updated:** 2025-11-16
**Status:** ✅ Complete
**Next:** Week 2 Completion Summary

