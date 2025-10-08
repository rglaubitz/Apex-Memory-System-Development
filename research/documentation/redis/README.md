# Redis 7 - Official Documentation

**Tier:** 1 (Official Documentation)
**Date Accessed:** 2025-10-06
**Target Version:** Redis 7+ (7.2+ recommended)
**Latest Stable:** Redis 7.4

## Official Documentation Links

### Main Documentation
- **Redis Documentation:** https://redis.io/docs/latest/
- **Official Website:** https://redis.io/
- **Downloads:** https://redis.io/downloads/

### Key Documentation Sections

#### 1. Get Started
- **Quick Start:** https://redis.io/docs/latest/
- **Redis Cloud:** Managed Redis service
- **Redis Open Source:** Self-hosted installation
- **GenAI Apps:** Building AI applications with Redis

#### 2. Deploy
- **Deployment Planning:** On-premises and cloud strategies
- **Kubernetes:** Official Kubernetes deployment guides
- **Data Ingestion:** Tools for data loading and synchronization
- **Monitoring:** Prometheus integration

#### 3. Develop
- **Developer Guide:** https://redis.io/docs/latest/develop/
- **Data Structures:** Core Redis data types
- **Commands Reference:** https://redis.io/docs/latest/commands/
- **Client Libraries:** Python, Node.js, Java, Go, C#, PHP, Ruby

#### 4. Redis Products
- **Redis Stack:** Extended modules (JSON, Search, Graph, TimeSeries, Bloom)
- **Redis Enterprise:** Commercial offering with clustering
- **Redis Insight:** Visual database management tool

### Version-Specific Documentation
- **Redis 7.2 Features:** https://redis.io/docs/latest/develop/whats-new/7-2/
- **Redis 7.0 Release:** https://redis.io/blog/redis-7-generally-available/

## Key Concepts & Architecture

### What is Redis?

Redis (Remote Dictionary Server) is an **in-memory data structure store** that can be used as:
- **Database** - Persistent key-value storage
- **Cache** - High-performance caching layer
- **Message Broker** - Pub/Sub messaging
- **Session Store** - Fast session management
- **Real-time Analytics** - Stream processing

### Core Architecture

1. **In-Memory Storage** - Data stored in RAM for microsecond latency
2. **Persistence Options:**
   - **RDB (Redis Database)** - Point-in-time snapshots
   - **AOF (Append-Only File)** - Write-ahead logging
   - **Both** - Hybrid approach
3. **Single-Threaded** - Event loop architecture (with multi-threading for I/O in 6.0+)
4. **Replication** - Master-replica setup for scalability
5. **Clustering** - Sharding for horizontal scaling

## Installation

### Docker (Recommended for Development)
```bash
# Pull official Redis image
docker pull redis:7.4

# Run Redis
docker run --name redis-server -p 6379:6379 -d redis:7.4

# Run with persistence
docker run --name redis-server \
    -v $(pwd)/redis-data:/data \
    -p 6379:6379 \
    -d redis:7.4 redis-server --appendonly yes
```

### Linux/macOS Installation
```bash
# macOS (Homebrew)
brew install redis
brew services start redis

# Ubuntu/Debian
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server

# From source
wget https://download.redis.io/redis-stable.tar.gz
tar -xzvf redis-stable.tar.gz
cd redis-stable
make
sudo make install
```

### Configuration
```bash
# Edit redis.conf
maxmemory 2gb
maxmemory-policy allkeys-lru

# Persistence
appendonly yes
appendfsync everysec

# Security
requirepass your_strong_password
bind 127.0.0.1

# Start with config
redis-server /path/to/redis.conf
```

## Core Data Structures

### 1. Strings
Simple key-value pairs.

```bash
# SET/GET
SET user:1:name "Alice"
GET user:1:name

# Increment/Decrement
SET counter 0
INCR counter          # Returns 1
INCRBY counter 5      # Returns 6
DECR counter          # Returns 5

# Expiration
SETEX session:abc123 3600 "user_data"  # Expires in 1 hour
TTL session:abc123                      # Check time to live

# Atomic operations
SET page:views 0
INCR page:views       # Thread-safe increment
```

### 2. Hashes
Maps between string fields and values (like objects).

```bash
# HSET/HGET
HSET user:1 name "Alice" email "alice@example.com" age 30
HGET user:1 name          # Returns "Alice"
HGETALL user:1            # Returns all fields

# Multiple fields
HMSET user:2 name "Bob" email "bob@example.com"
HMGET user:2 name email

# Increment field
HINCRBY user:1 age 1      # Increment age by 1

# Check existence
HEXISTS user:1 name       # Returns 1 (true)
```

### 3. Lists
Ordered collections of strings (linked lists).

```bash
# LPUSH/RPUSH (left/right push)
LPUSH messages "msg1"
RPUSH messages "msg2" "msg3"

# LPOP/RPOP
LPOP messages            # Remove and return first element
RPOP messages            # Remove and return last element

# Range
LRANGE messages 0 -1     # Get all elements
LRANGE messages 0 9      # Get first 10 elements

# Length
LLEN messages

# Use case: Job queues
LPUSH job:queue "job1"
BRPOP job:queue 0        # Blocking pop (wait for element)
```

### 4. Sets
Unordered collections of unique strings.

```bash
# SADD/SMEMBERS
SADD tags:1 "redis" "database" "cache"
SMEMBERS tags:1

# Check membership
SISMEMBER tags:1 "redis"   # Returns 1 (true)

# Set operations
SADD set1 "a" "b" "c"
SADD set2 "b" "c" "d"
SINTER set1 set2           # Intersection: b, c
SUNION set1 set2           # Union: a, b, c, d
SDIFF set1 set2            # Difference: a

# Random element (useful for sampling)
SRANDMEMBER tags:1
```

### 5. Sorted Sets (ZSets)
Sets ordered by score.

```bash
# ZADD
ZADD leaderboard 100 "player1" 200 "player2" 150 "player3"

# Range by rank
ZRANGE leaderboard 0 -1 WITHSCORES    # All, ascending
ZREVRANGE leaderboard 0 9 WITHSCORES  # Top 10, descending

# Range by score
ZRANGEBYSCORE leaderboard 100 200

# Rank
ZRANK leaderboard "player1"           # Position (0-indexed)

# Increment score
ZINCRBY leaderboard 50 "player1"

# Use case: Time-series data
ZADD events 1696598400 "event1" 1696598500 "event2"
ZRANGEBYSCORE events 1696598000 1696599000  # Events in time range
```

### 6. JSON (Redis Stack)
Native JSON support with JSONPath queries.

```bash
# JSON.SET
JSON.SET user:1 $ '{"name":"Alice","age":30,"tags":["redis","db"]}'

# JSON.GET
JSON.GET user:1 $.name     # Returns "Alice"
JSON.GET user:1 $          # Returns full document

# Update nested fields
JSON.SET user:1 $.age 31
JSON.ARRAPPEND user:1 $.tags '"cache"'

# Query
JSON.GET user:1 $..name    # JSONPath query
```

### 7. Streams
Append-only log structure for event streaming.

```bash
# Add to stream
XADD events:stream * user "alice" action "login" timestamp "2025-10-06T10:00:00Z"

# Read from stream
XREAD COUNT 10 STREAMS events:stream 0

# Consumer groups
XGROUP CREATE events:stream mygroup 0
XREADGROUP GROUP mygroup consumer1 STREAMS events:stream >
```

## Redis 7 Specific Features

### Redis 7.0 Features
1. **Redis Functions** - User-defined functions in Lua
2. **ACL v2** - Enhanced access control
3. **Command Introspection** - Better debugging
4. **Sharded Pub/Sub** - Scalable messaging

### Redis 7.2 New Features

#### 1. Improved Geospatial Queries
```bash
# Polygon search
GEOSEARCH locations FROMLONLAT -73.9 40.7 BYBOX 10 10 km WITHCOORD
```

#### 2. JSON Enhancements
```bash
# JSON.MERGE - Merge JSON values
JSON.MERGE user:1 $.stats '{"views":100,"likes":50}'

# JSON.MSET - Set multiple JSON values atomically
JSON.MSET user:1 $.name '"Alice"' user:2 $.name '"Bob"'
```

#### 3. Performance Improvements
- Sorted sets performance: **30-100% faster**
- Enhanced stream consumer tracking
- Optimized `SORT BY` operations

#### 4. TLS Improvements
- SNI (Server Name Indication) support
- Better replication over TLS

## Best Practices

### Caching Strategies

#### 1. Cache Eviction Policies
```bash
# Configuration
CONFIG SET maxmemory 2gb
CONFIG SET maxmemory-policy allkeys-lru

# Policies:
# allkeys-lru    - Evict least recently used keys
# volatile-lru   - Evict LRU among keys with expiration
# allkeys-lfu    - Evict least frequently used (Redis 4.0+)
# volatile-ttl   - Evict keys closest to expiration
# noeviction     - Return errors when memory limit reached
```

#### 2. TTL Management
```bash
# Set expiration
EXPIRE key 3600                # Expire in 1 hour
EXPIREAT key 1696598400       # Expire at Unix timestamp
PEXPIRE key 60000             # Expire in milliseconds

# Check TTL
TTL key                        # Returns seconds
PTTL key                       # Returns milliseconds

# Remove expiration
PERSIST key
```

#### 3. Cache-Aside Pattern
```python
import redis
import json

r = redis.Redis(host='localhost', port=6379, db=0)

def get_user(user_id):
    # Try cache first
    cached = r.get(f"user:{user_id}")
    if cached:
        return json.loads(cached)

    # Cache miss - fetch from database
    user = fetch_from_database(user_id)

    # Store in cache with TTL
    r.setex(f"user:{user_id}", 3600, json.dumps(user))
    return user
```

### Performance Optimization

#### 1. Pipelining
Batch multiple commands to reduce network round trips.

```python
import redis

r = redis.Redis()

# Without pipelining (3 round trips)
r.set('key1', 'value1')
r.set('key2', 'value2')
r.set('key3', 'value3')

# With pipelining (1 round trip)
pipe = r.pipeline()
pipe.set('key1', 'value1')
pipe.set('key2', 'value2')
pipe.set('key3', 'value3')
pipe.execute()
```

#### 2. Lua Scripts (Atomicity)
Execute multiple operations atomically.

```python
# Register script
script = r.register_script("""
local current = redis.call('GET', KEYS[1])
if current then
    return redis.call('INCR', KEYS[1])
else
    redis.call('SET', KEYS[1], ARGV[1])
    return tonumber(ARGV[1])
end
""")

# Execute
result = script(keys=['counter'], args=[0])
```

#### 3. Connection Pooling
```python
import redis

# Create connection pool
pool = redis.ConnectionPool(
    host='localhost',
    port=6379,
    db=0,
    max_connections=50
)

# Use pool
r = redis.Redis(connection_pool=pool)
```

### Data Modeling

#### 1. Key Naming Conventions
```bash
# Use hierarchical naming with colons
user:1:profile
user:1:sessions
user:1:preferences

# Include type in key name
user:1:hash       # Hash type
user:1:list       # List type
cache:page:123    # Cache data
```

#### 2. Avoid Large Keys
```bash
# Bad: Single large hash
HSET user:1:all field1 val1 field2 val2 ... field1000 val1000

# Good: Split into smaller hashes
HSET user:1:profile name "Alice" email "alice@example.com"
HSET user:1:settings theme "dark" lang "en"
```

#### 3. Use Appropriate Data Types
```bash
# Counters - Use strings with INCR
SET page:views:123 0
INCR page:views:123

# Unique items - Use sets
SADD post:123:likes user:1 user:2

# Ordered data - Use sorted sets
ZADD trending:posts 100 "post:1" 200 "post:2"

# Key-value pairs - Use hashes
HSET session:abc123 user_id 1 created_at 1696598400
```

### Security

#### 1. Authentication
```bash
# Set password in redis.conf
requirepass your_strong_password

# Connect with password
redis-cli -a your_strong_password

# Or authenticate after connection
AUTH your_strong_password
```

#### 2. ACL (Access Control Lists) - Redis 6.0+
```bash
# Create user with limited permissions
ACL SETUSER alice on >password ~cached:* +get +set

# List users
ACL LIST

# Check current user
ACL WHOAMI
```

#### 3. Network Security
```bash
# Bind to specific interface (redis.conf)
bind 127.0.0.1

# Enable SSL/TLS (redis.conf)
tls-port 6379
port 0
tls-cert-file /path/to/cert.pem
tls-key-file /path/to/key.pem
```

### Persistence

#### 1. RDB Snapshots
```bash
# redis.conf
save 900 1      # Save if 1 key changed in 900 seconds
save 300 10     # Save if 10 keys changed in 300 seconds
save 60 10000   # Save if 10000 keys changed in 60 seconds

# Manual snapshot
BGSAVE           # Background save
SAVE             # Blocking save (avoid in production)
```

#### 2. AOF (Append-Only File)
```bash
# redis.conf
appendonly yes
appendfsync everysec   # fsync every second (balanced)
# appendfsync always   # fsync on every write (slow, safe)
# appendfsync no       # Let OS decide (fast, risky)

# AOF rewrite
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb
```

#### 3. Hybrid Persistence (Recommended)
```bash
# Enable both RDB and AOF
save 900 1
appendonly yes
appendfsync everysec
```

## Integration Patterns

### Python (redis-py)

```python
import redis
from redis.sentinel import Sentinel

# Basic connection
r = redis.Redis(
    host='localhost',
    port=6379,
    db=0,
    decode_responses=True  # Return strings instead of bytes
)

# Set and get
r.set('key', 'value', ex=3600)  # With expiration
value = r.get('key')

# Hash operations
r.hset('user:1', mapping={'name': 'Alice', 'age': 30})
user = r.hgetall('user:1')

# List operations
r.lpush('queue', 'job1', 'job2')
job = r.brpop('queue', timeout=5)  # Blocking pop with timeout

# Sorted set
r.zadd('leaderboard', {'player1': 100, 'player2': 200})
top_players = r.zrevrange('leaderboard', 0, 9, withscores=True)

# Pub/Sub
pubsub = r.pubsub()
pubsub.subscribe('channel1')
for message in pubsub.listen():
    print(message)

# Pipeline
pipe = r.pipeline()
pipe.set('key1', 'value1')
pipe.set('key2', 'value2')
pipe.execute()

# Transaction with WATCH
with r.pipeline() as pipe:
    while True:
        try:
            pipe.watch('key')
            current = pipe.get('key')
            pipe.multi()
            pipe.set('key', int(current) + 1)
            pipe.execute()
            break
        except redis.WatchError:
            continue
```

### Async Python (redis-py with asyncio)
```python
import redis.asyncio as redis

async def main():
    r = await redis.Redis(host='localhost', port=6379)
    await r.set('key', 'value')
    value = await r.get('key')
    await r.close()
```

### High Availability with Sentinel
```python
from redis.sentinel import Sentinel

sentinel = Sentinel([
    ('localhost', 26379),
    ('localhost', 26380)
], socket_timeout=0.1)

# Discover master
master = sentinel.discover_master('mymaster')

# Get Redis connection
r = sentinel.master_for('mymaster', socket_timeout=0.1)
r.set('key', 'value')

# Get slave connection (for reads)
slave = sentinel.slave_for('mymaster', socket_timeout=0.1)
value = slave.get('key')
```

## Relevant Features for Apex Memory System

### 1. Session Management
```python
import redis
import json

r = redis.Redis()

def store_session(session_id, data, ttl=3600):
    """Store session data with automatic expiration."""
    r.setex(f"session:{session_id}", ttl, json.dumps(data))

def get_session(session_id):
    """Retrieve session data."""
    data = r.get(f"session:{session_id}")
    return json.loads(data) if data else None
```

### 2. Rate Limiting
```python
def is_rate_limited(user_id, max_requests=100, window=60):
    """Rate limit user requests (100 per minute)."""
    key = f"rate_limit:{user_id}"
    current = r.incr(key)

    if current == 1:
        r.expire(key, window)

    return current > max_requests
```

### 3. Caching Query Results
```python
def cache_query_result(query_hash, result, ttl=300):
    """Cache database query results."""
    r.setex(f"query:cache:{query_hash}", ttl, json.dumps(result))

def get_cached_query(query_hash):
    """Retrieve cached query result."""
    cached = r.get(f"query:cache:{query_hash}")
    return json.loads(cached) if cached else None
```

### 4. Distributed Locks
```python
import uuid

def acquire_lock(resource, timeout=10):
    """Acquire distributed lock."""
    lock_id = str(uuid.uuid4())
    acquired = r.set(
        f"lock:{resource}",
        lock_id,
        nx=True,
        ex=timeout
    )
    return lock_id if acquired else None

def release_lock(resource, lock_id):
    """Release lock only if we own it."""
    script = """
    if redis.call("get", KEYS[1]) == ARGV[1] then
        return redis.call("del", KEYS[1])
    else
        return 0
    end
    """
    return r.eval(script, 1, f"lock:{resource}", lock_id)
```

### 5. Temporary Data Storage
```python
def store_temp_data(key, data, ttl=3600):
    """Store temporary data (e.g., processing results)."""
    r.setex(f"temp:{key}", ttl, json.dumps(data))
```

## Monitoring & Maintenance

### Monitoring Commands
```bash
# Server info
INFO

# Specific section
INFO stats
INFO memory
INFO replication

# Monitor all commands (debugging only)
MONITOR

# Slow log
SLOWLOG GET 10
CONFIG SET slowlog-log-slower-than 10000  # 10ms

# Client connections
CLIENT LIST
CLIENT KILL <ip:port>

# Memory usage
MEMORY USAGE key
MEMORY STATS

# Key space
DBSIZE
KEYS pattern  # Use SCAN instead in production
```

### Maintenance
```bash
# Database cleanup
FLUSHDB   # Clear current database
FLUSHALL  # Clear all databases (dangerous!)

# Scan keys safely
SCAN 0 MATCH user:* COUNT 100

# Background operations
BGSAVE       # Background RDB save
BGREWRITEAOF # Rewrite AOF file
```

## Learning Resources

### Official Resources
- **Redis Documentation:** Comprehensive guides
- **Redis University:** Free online courses
- **Redis CLI:** Interactive learning tool
- **Redis Insight:** Visual management tool

### Key Topics for Memory System
1. Caching strategies and eviction policies
2. Data structure selection
3. Performance optimization (pipelining, Lua scripts)
4. High availability (Sentinel, Cluster)
5. Persistence configuration
6. Security and ACLs

## Summary

Redis 7 is a battle-tested, high-performance in-memory data structure store ideal for caching, session management, and real-time data operations. Its sub-millisecond latency, rich data structures, and extensive language support make it perfect for the Apex Memory System's caching layer.

**Key Strengths for Apex Memory:**
- **Extreme performance** - Microsecond latencies
- **Rich data structures** - Beyond simple key-value
- **Flexible persistence** - RDB, AOF, or hybrid
- **Pub/Sub messaging** - Real-time event notifications
- **Lua scripting** - Atomic operations
- **JSON support** - Native JSON in Redis Stack
- **Mature ecosystem** - Extensive client libraries
- **High availability** - Sentinel and Cluster modes

**Recommended Setup:**
- Redis 7.2+ for latest features
- AOF with `everysec` fsync for balanced durability
- Connection pooling in application code
- `allkeys-lru` eviction policy for cache
- Sentinel for high availability in production
- Redis Insight for monitoring and debugging

**Primary Use Cases in Apex Memory:**
- Query result caching (reduce database load)
- Session state management
- Rate limiting and throttling
- Temporary data storage (processing intermediate results)
- Distributed locks for coordination
- Real-time notifications via Pub/Sub
