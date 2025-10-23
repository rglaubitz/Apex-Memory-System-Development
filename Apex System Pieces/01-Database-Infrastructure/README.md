# 01 - Database Infrastructure

## 🎯 Purpose

Provides persistent storage across 4 specialized databases, each optimized for different query patterns. This is the foundation layer of the Apex Memory System.

**Why 4 databases?**
- Each database excels at specific query types
- Parallel querying across all 4 provides comprehensive answers
- Query Router intelligently routes to optimal database(s) per query

## 🛠 Technical Stack

### PostgreSQL 16 + pgvector
- **Purpose:** Metadata storage + hybrid semantic search
- **Image:** `ankane/pgvector:latest`
- **Features:** Full-text search, pgvector extension for embeddings, JSONB support
- **Port:** 5432

### Neo4j 2025.09.0
- **Purpose:** Graph relationships + entity connections
- **Image:** `neo4j:2025.09.0`
- **Plugins:** APOC (procedures), Graph Data Science (GDS)
- **Memory:** 2GB heap, 1GB page cache
- **Ports:** 7474 (HTTP), 7687 (Bolt)

### Qdrant
- **Purpose:** High-performance vector similarity search
- **Image:** `qdrant/qdrant:latest`
- **Features:** Fast vector indexing, HNSW algorithm
- **Ports:** 6335 (HTTP), 6336 (gRPC)

### Redis 8.2-alpine
- **Purpose:** LRU cache layer for sub-10ms repeat queries
- **Image:** `redis:8.2-alpine`
- **Config:** 1GB max memory, allkeys-lru eviction, AOF persistence
- **Port:** 6379
- **Performance:** 95% cache hit rate in steady state

## 📂 Key Files

### Schema Definitions
- `apex-memory-system/schemas/postgres_schema.sql` (13,375 bytes)
  - Documents, chunks, entities, conversations, users tables
  - pgvector columns for embeddings
  - Full-text search indices

- `apex-memory-system/schemas/neo4j_schema.cypher` (14,084 bytes)
  - Document, Entity, Chunk nodes
  - MENTIONED_IN, RELATED_TO, HAS_CHUNK relationships
  - Indices on UUID, entity names

- `apex-memory-system/schemas/qdrant_schema.py` (18,315 bytes)
  - Collection creation code
  - Vector dimension: 1536 (OpenAI text-embedding-3-small)
  - Distance metric: Cosine similarity

- `apex-memory-system/schemas/redis_schema.md` (12,386 bytes)
  - Cache key patterns
  - TTL strategies
  - Eviction policies

### Infrastructure
- `apex-memory-system/docker/docker-compose.yml` (270 lines)
  - All 4 database containers
  - Health checks
  - Volume persistence
  - Network configuration

### Index Optimization
- `apex-memory-system/schemas/postgres_indices.sql` (17,348 bytes)
  - B-tree indices on UUIDs, timestamps
  - GIN indices for full-text search
  - HNSW indices for pgvector

- `apex-memory-system/schemas/neo4j_indices.cypher` (10,401 bytes)
  - Node property indices
  - Relationship type indices
  - Composite indices

## 🔗 Dependencies

**None** - This is the foundation layer.

All other components depend on Database Infrastructure.

## 🔌 Interfaces

### Consumed By:
1. **Database Writers** (07) - Write operations via drivers:
   - Neo4j: `neo4j==6.0.2` driver
   - PostgreSQL: `psycopg2-binary==2.9.10`, `asyncpg==0.30.0`
   - Qdrant: `qdrant-client==1.15.1`
   - Redis: `redis==6.4.0`

2. **Query Router** (04) - Read operations across all databases

3. **Backend API** (03) - Health checks, metrics queries

4. **Core Services** (05) - Direct database access for specialized operations

### Connection Pooling:
- **PostgreSQL:** Min 2, Max 20 connections (configurable)
- **Neo4j:** Driver manages connection pool automatically
- **Qdrant:** HTTP client with keep-alive
- **Redis:** Max 50 connections with pooling

## ⚙️ Configuration

### Environment Variables (from settings.py)

```python
# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=apex
POSTGRES_PASSWORD=apexmemory2024
POSTGRES_DB=apex_memory
POSTGRES_MIN_POOL_SIZE=2
POSTGRES_MAX_POOL_SIZE=20

# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=apexmemory2024
NEO4J_DATABASE=neo4j

# Qdrant
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_GRPC_PORT=6334
QDRANT_API_KEY=  # Optional, not used in local dev

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=  # Optional, not used in local dev
REDIS_DB=0
```

### Docker Volumes (persistent storage)
```yaml
volumes:
  postgres_data:      # PostgreSQL data directory
  neo4j_data:         # Neo4j graph database
  neo4j_logs:         # Neo4j logs
  qdrant_data:        # Qdrant vector storage
  redis_data:         # Redis AOF persistence
```

## 🚀 Deployment

### Start All Databases

```bash
cd apex-memory-system/docker
docker-compose up -d

# Wait 30-60s for health checks to pass
docker-compose ps  # Verify all healthy
```

### Initialize Databases

```bash
# PostgreSQL schema auto-loads from docker-entrypoint-initdb.d/
# (postgres_schema.sql, postgres_indices.sql, postgres_dlq.sql)

# Qdrant collections must be initialized
cd apex-memory-system
python init-scripts/qdrant/init.py

# Neo4j schema can be applied via browser or cypher-shell
# (Optional - schema is created dynamically by first write)
```

### Access Interfaces

| Service | URL | Credentials |
|---------|-----|-------------|
| **Neo4j Browser** | http://localhost:7474 | neo4j / apexmemory2024 |
| **PostgreSQL** | localhost:5432 | apex / apexmemory2024 |
| **Qdrant Dashboard** | http://localhost:6335/dashboard | (no auth) |
| **Redis CLI** | `redis-cli` | (no auth) |

### Health Checks

```bash
# PostgreSQL
PGPASSWORD=apexmemory2024 psql -h localhost -U apex -d apex_memory -c "SELECT 1"

# Neo4j
echo "RETURN 1" | cypher-shell -u neo4j -p apexmemory2024

# Qdrant
curl http://localhost:6335/health

# Redis
redis-cli ping
```

## 📊 Metrics & Monitoring

### Database Health Metrics (Prometheus)

```python
# From apex-memory-system/src/apex_memory/monitoring/metrics.py

db_connections_active = Gauge(
    "apex_db_connections_active",
    "Number of active database connections",
    ["database"]  # neo4j, postgres, qdrant, redis
)

db_query_duration_seconds = Histogram(
    "apex_db_query_duration_seconds",
    "Database query execution time",
    ["database", "operation"]
)

db_errors_total = Counter(
    "apex_db_errors_total",
    "Total database errors",
    ["database", "error_type"]
)

db_connection_pool_usage = Gauge(
    "apex_db_connection_pool_usage",
    "Database connection pool usage (0.0 to 1.0)",
    ["database"]
)
```

### Performance Targets

- **PostgreSQL:** <50ms for metadata queries, <100ms for vector hybrid search
- **Neo4j:** <100ms for 2-hop graph traversals, <500ms for complex patterns
- **Qdrant:** <50ms for vector similarity (top 10), <200ms for large result sets
- **Redis:** <10ms for cache hits (99.9% of queries)

## 🔧 Maintenance Operations

### Backup

```bash
# PostgreSQL
pg_dump -h localhost -U apex apex_memory > backup.sql

# Neo4j (stop container first)
docker stop apex-neo4j
cp -r /var/lib/docker/volumes/docker_neo4j_data/_data /backups/neo4j
docker start apex-neo4j

# Qdrant (snapshot via API)
curl -X POST http://localhost:6335/collections/documents/snapshots/create

# Redis (AOF persistence enabled - automatic)
redis-cli BGSAVE
```

### Database Reset (Development Only)

```bash
# WARNING: Destroys all data!
cd apex-memory-system/docker
docker-compose down -v  # -v removes volumes
docker-compose up -d
python ../init-scripts/qdrant/init.py
```

## 📈 Storage Estimates

**Typical document (10 pages, 5,000 words):**

- **PostgreSQL:** ~50KB metadata + ~200 chunks × 2KB = ~450KB
- **Neo4j:** ~10 entity nodes × 1KB + ~20 relationships × 500B = ~20KB
- **Qdrant:** ~200 vectors × 6KB (1536 dims × 4 bytes) = ~1.2MB
- **Redis:** ~5KB cached query result (TTL: 1 hour)

**Total per document:** ~1.67MB across all databases

**1,000 documents:** ~1.67GB
**10,000 documents:** ~16.7GB
**100,000 documents:** ~167GB

## 🚨 Known Limitations

1. **Qdrant health check disabled** - Container lacks curl/wget, monitored via application
2. **Neo4j cold start** - First query after restart takes 5-10s (page cache warming)
3. **PostgreSQL connection limit** - Max 100 concurrent connections (default config)
4. **Redis memory eviction** - 1GB limit with LRU eviction (oldest keys dropped)

## 🔍 Troubleshooting

### "Database connection refused"
```bash
# Check containers are running
docker ps | grep apex

# Check logs
docker logs apex-postgres
docker logs apex-neo4j
docker logs apex-qdrant
docker logs apex-redis

# Wait for health checks (30-60s after docker-compose up)
docker-compose ps
```

### "Qdrant collection not found"
```bash
# Initialize collections
python apex-memory-system/init-scripts/qdrant/init.py
```

### "PostgreSQL schema missing"
```bash
# Manually apply schema
PGPASSWORD=apexmemory2024 psql -h localhost -U apex -d apex_memory < apex-memory-system/schemas/postgres_schema.sql
```

---

**Next Component:** [02-Workflow-Orchestration](../02-Workflow-Orchestration/README.md)
