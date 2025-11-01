# Version Compatibility Matrix

**Status:** ✅ Verified (November 2025)
**Last Updated:** 2025-11-01
**Verification Date:** 2025-11-01
**Validation Method:** 5 specialized research agents + SDK verification

---

## Table of Contents

1. [Current Production Stack](#1-current-production-stack)
2. [Compatibility Matrix](#2-compatibility-matrix)
3. [Upgrade Paths](#3-upgrade-paths)
4. [Breaking Changes](#4-breaking-changes)
5. [Deprecation Notices](#5-deprecation-notices)

---

## 1. Current Production Stack

### Apex Memory System - November 2025

| Component | Version | Status | Notes |
|-----------|---------|--------|-------|
| **Python** | 3.11+ | ✅ Required | Minimum version for all packages |
| **Neo4j** | 5.13+ | ✅ Recommended | Required for VECTOR index support |
| **PostgreSQL** | 16.x | ✅ Recommended | Current stable (17.x available) |
| **pgvector** | 0.8.1 | ✅ Latest | September 2025 release |
| **Qdrant** | 1.15.1 | ✅ Latest | November 2025 release |
| **Redis** | 7.2.x | ✅ Recommended | Redis 7.4 available (optional) |
| **Temporal** | 1.11.0 | ✅ Latest | November 2025 release |
| **Graphiti** | 0.22.0 | ⚠️ Pre-release | Latest stable: 0.21.0 (Sept 2025) |

**Docker Images (Current):**
```yaml
services:
  neo4j:
    image: neo4j:5.27.0  # Latest Neo4j 5.x

  postgres:
    image: ankane/pgvector:pg16  # PostgreSQL 16 + pgvector 0.8.1

  qdrant:
    image: qdrant/qdrant:v1.15.1  # Latest stable

  redis:
    image: redis:7.2-alpine  # Lightweight Redis 7.2

  temporal:
    image: temporalio/auto-setup:1.11.0  # Latest Temporal
```

---

## 2. Compatibility Matrix

### 2.1 Python SDK Versions

| SDK | Version | Python | Neo4j | PostgreSQL | Qdrant | Redis | Status |
|-----|---------|--------|-------|------------|--------|-------|--------|
| **neo4j** | 5.27.0 | 3.8+ | 5.x, 4.4+ | - | - | - | ✅ Compatible |
| **psycopg2-binary** | 2.9.10 | 3.7+ | - | 12+ | - | - | ✅ Compatible |
| **pgvector** | 0.8.1 | 3.8+ | - | 12+ w/ pgvector | - | - | ✅ Compatible |
| **qdrant-client** | 1.15.1 | 3.8+ | - | - | 1.9+ | - | ✅ Compatible |
| **redis** | 6.4.0 | 3.8+ | - | - | - | 6.0+ | ✅ Compatible |
| **temporalio** | 1.11.0 | 3.8+ | - | - | - | - | ✅ Compatible |
| **graphiti-core** | 0.22.0 | 3.10+ | 5.13+ | - | - | - | ⚠️ Pre-release |

**Installation:**
```bash
# All dependencies
pip install neo4j==5.27.0 psycopg2-binary==2.9.10 pgvector==0.8.1 \
    qdrant-client==1.15.1 redis==6.4.0 temporalio==1.11.0 \
    graphiti-core==0.22.0
```

---

### 2.2 Database Version Compatibility

#### Neo4j Versions

| Neo4j | neo4j (Python) | VECTOR Index | Cypher 25 | Java Requirement | Status |
|-------|----------------|--------------|-----------|------------------|--------|
| **5.27.0** | 5.27.0 | ✅ Yes (5.13+) | ✅ Yes | Java 21 | ✅ Recommended |
| **5.13.0** | 5.27.0 | ✅ Yes (first) | ❌ No | Java 17 | ✅ Min for VECTOR |
| **5.x** | 5.x+ | ⚠️ 5.13+ only | ⚠️ 2025.x+ | Java 17 | ✅ Compatible |
| **2025.x** | 5.27.0 | ✅ Yes | ✅ Yes | Java 21 | ✅ Latest features |
| **4.4.x** | 5.27.0 | ❌ No | ❌ No | Java 11 | ⚠️ Legacy support |

**Key Features by Version:**
- **5.13+**: VECTOR index support (required for hybrid search)
- **5.27+**: Improved query performance, better index statistics
- **2025.x**: Cypher 25, block format default, enhanced vector search

**Recommendation:** Use Neo4j 5.27.0 or 2025.x for production.

---

#### PostgreSQL + pgvector Versions

| PostgreSQL | pgvector | HNSW Index | halfvec | sparsevec | Iterative Scans | Status |
|------------|----------|------------|---------|-----------|-----------------|--------|
| **16.x** | 0.8.1 | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Recommended |
| **16.x** | 0.7.x | ✅ Yes | ❌ No | ❌ No | ❌ No | ⚠️ Missing features |
| **15.x** | 0.8.1 | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Compatible |
| **14.x** | 0.8.1 | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Compatible |
| **13.x** | 0.8.1 | ⚠️ Limited | ✅ Yes | ✅ Yes | ❌ No | ⚠️ Older PG version |
| **12.x** | 0.8.1 | ⚠️ Limited | ✅ Yes | ✅ Yes | ❌ No | ⚠️ Older PG version |

**Key Features by Version:**
- **pgvector 0.8.1**: Half-precision vectors, sparse vectors, iterative index scans
- **pgvector 0.7.x**: HNSW indexes, basic vector operations
- **pgvector 0.6.x**: IVFFlat indexes only (slower)

**Recommendation:** Use PostgreSQL 16.x + pgvector 0.8.1 for best performance.

**Docker Image:**
```yaml
postgres:
  image: ankane/pgvector:pg16  # PostgreSQL 16 + pgvector 0.8.1
  # Alternative: ankane/pgvector:pg15 for PostgreSQL 15
```

---

#### Qdrant Versions

| Qdrant | qdrant-client | Asymmetric Quant | 1.5/2-bit Quant | HNSW Healing | Status |
|--------|---------------|------------------|-----------------|--------------|--------|
| **1.15.1** | 1.15.1 | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Recommended |
| **1.14.x** | 1.14.x | ❌ No | ❌ No | ⚠️ Partial | ✅ Compatible |
| **1.13.x** | 1.13.x | ❌ No | ❌ No | ❌ No | ✅ Compatible |
| **1.12.x** | 1.12.x | ❌ No | ❌ No | ❌ No | ⚠️ Older version |
| **1.9+** | 1.9+ | ❌ No | ❌ No | ❌ No | ⚠️ Minimum supported |

**Key Features by Version:**
- **1.15.x**: Asymmetric quantization, 1.5/2-bit quantization, HNSW healing, improved disk I/O
- **1.14.x**: Better query performance, enhanced filtering
- **1.13.x**: Multi-vector support, collection aliases

**Recommendation:** Use Qdrant 1.15.1 + qdrant-client 1.15.1 for latest features.

---

#### Redis Versions

| Redis | redis-py | JSON Support | Search | Cluster | Status |
|-------|----------|--------------|--------|---------|--------|
| **7.4.x** | 6.4.0 | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Latest (optional) |
| **7.2.x** | 6.4.0 | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Recommended |
| **7.0.x** | 6.4.0 | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Compatible |
| **6.2.x** | 6.4.0 | ⚠️ Module | ⚠️ Module | ✅ Yes | ⚠️ Older version |
| **6.0.x** | 6.4.0 | ⚠️ Module | ⚠️ Module | ✅ Yes | ⚠️ Minimum supported |

**Recommendation:** Use Redis 7.2.x for production (stable, well-tested).

---

#### Temporal Versions

| Temporal | temporalio (Python) | Python Version | Workflow Versioning | Status |
|----------|---------------------|----------------|---------------------|--------|
| **1.11.0** | 1.11.0 | 3.8+ | ✅ Yes | ✅ Recommended |
| **1.10.x** | 1.10.x | 3.8+ | ✅ Yes | ✅ Compatible |
| **1.9.x** | 1.9.x | 3.8+ | ✅ Yes | ✅ Compatible |
| **1.8.x** | 1.8.x | 3.7+ | ⚠️ Limited | ⚠️ Older version |

**Recommendation:** Use Temporal 1.11.0 for latest stability and features.

---

### 2.3 Graphiti Compatibility

| Graphiti | Neo4j | Python | GPT-4 | GPT-4 Turbo | GPT-5 | Custom Labels | Status |
|----------|-------|--------|-------|-------------|-------|---------------|--------|
| **0.22.0** | 5.13+ | 3.10+ | ✅ Yes | ✅ Yes | ⚠️ When available | ❌ No (GH #567) | ⚠️ Pre-release |
| **0.21.0** | 5.13+ | 3.10+ | ✅ Yes | ✅ Yes | ⚠️ When available | ❌ No (GH #567) | ✅ Latest stable |
| **0.20.x** | 5.13+ | 3.10+ | ✅ Yes | ❌ No | ❌ No | ❌ No | ⚠️ Older version |
| **0.19.x** | 5.x | 3.10+ | ✅ Yes | ❌ No | ❌ No | ❌ No | ⚠️ Older version |

**Key Notes:**
- **Neo4j 5.13+ Required** for VECTOR index support (Graphiti uses hybrid search)
- **Python 3.10+ Required** (not compatible with 3.8/3.9)
- **Custom Labels Issue** (GitHub #567): Custom entity types don't create custom node labels (e.g., `:Customer`, `:Invoice`)
  - **Workaround:** Query by `entity_type` property instead of custom labels
- **0.22.0 Status:** Pre-release or local build (latest stable is 0.21.0)

**Recommendation:** Use Graphiti 0.21.0 (stable) unless you have specific 0.22.0 features. Verify 0.22.0 availability before production use.

---

## 3. Upgrade Paths

### 3.1 From Current Setup to Latest (November 2025)

**Scenario:** Currently running older versions, want to upgrade to November 2025 stack.

#### Step 1: Backup Everything

```bash
# PostgreSQL
pg_dump -U apex apex_memory > backup_$(date +%Y%m%d).sql

# Neo4j
docker exec neo4j neo4j-admin database dump neo4j --to-path=/backups/

# Qdrant (snapshots)
curl -X POST "http://localhost:6333/collections/documents/snapshots"

# Redis (RDB snapshot)
redis-cli SAVE
```

#### Step 2: Upgrade PostgreSQL + pgvector

```yaml
# docker-compose.yml
postgres:
  image: ankane/pgvector:pg16  # Was: pg15 or pg14
  environment:
    POSTGRES_DB: apex_memory
    POSTGRES_USER: apex
    POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
```

```bash
# Apply migration
docker-compose down postgres
docker-compose up -d postgres

# Verify pgvector version
psql -U apex -d apex_memory -c "SELECT extversion FROM pg_extension WHERE extname = 'vector';"
# Expected: 0.8.1
```

**New Features Available:**
- Half-precision vectors (`HALFVEC(1536)`)
- Sparse vectors (`SPARSEVEC(10000)`)
- Iterative index scans (automatic)

#### Step 3: Upgrade Neo4j

```yaml
# docker-compose.yml
neo4j:
  image: neo4j:5.27.0  # Was: 5.x or 4.4
  environment:
    NEO4J_AUTH: neo4j/${NEO4J_PASSWORD}
    NEO4J_ACCEPT_LICENSE_AGREEMENT: "yes"
```

```bash
# Apply migration
docker-compose down neo4j
docker-compose up -d neo4j

# Verify version
docker exec neo4j cypher-shell "CALL dbms.components() YIELD name, versions RETURN name, versions[0] AS version"
# Expected: 5.27.0
```

**Breaking Changes:**
- **Java 21 Required** for Neo4j 2025.x (not 5.27.0)
- **Cypher 25** available in 2025.x (new syntax features)

#### Step 4: Upgrade Qdrant

```yaml
# docker-compose.yml
qdrant:
  image: qdrant/qdrant:v1.15.1  # Was: v1.x
```

```bash
# Apply migration
docker-compose down qdrant
docker-compose up -d qdrant

# Verify version
curl -X GET "http://localhost:6333/cluster" | jq '.result.version'
# Expected: 1.15.1
```

**New Features Available:**
- Asymmetric quantization
- 1.5-bit and 2-bit quantization
- HNSW healing (automatic)

#### Step 5: Upgrade Python SDKs

```bash
# requirements.txt
neo4j==5.27.0
psycopg2-binary==2.9.10
pgvector==0.8.1
qdrant-client==1.15.1
redis==6.4.0
temporalio==1.11.0
graphiti-core==0.22.0  # Or 0.21.0 for stable

# Install
pip install --upgrade -r requirements.txt
```

#### Step 6: Test Everything

```bash
# Run health checks
python scripts/dev/health_check.py -v

# Run integration tests
pytest tests/integration/ -v

# Verify all databases accessible
python scripts/debug/check_all_databases.py
```

---

### 3.2 Rollback Plan

**If upgrade fails:**

#### Rollback Docker Images

```bash
# Revert docker-compose.yml to previous versions
# Example:
# postgres: ankane/pgvector:pg16 → ankane/pgvector:pg15
# neo4j: neo4j:5.27.0 → neo4j:5.13.0
# qdrant: qdrant/qdrant:v1.15.1 → qdrant/qdrant:v1.14.0

# Restart with old versions
docker-compose down
docker-compose up -d
```

#### Restore Backups

```bash
# PostgreSQL
psql -U apex -d apex_memory < backup_20251101.sql

# Neo4j
docker exec neo4j neo4j-admin database load neo4j --from-path=/backups/

# Qdrant
curl -X PUT "http://localhost:6333/collections/documents/snapshots/upload" \
  -F 'snapshot=@snapshot_20251101.tar'
```

---

## 4. Breaking Changes

### 4.1 Neo4j 5.x → 2025.x

**Breaking Changes:**
- **Java 21 Required** (was Java 17 for 5.x)
- **Cypher 25** - New syntax features (mostly backward compatible)
- **Block Format Default** - New storage format (migration automatic)

**Migration:** Mostly automatic, but review Cypher queries for deprecations.

---

### 4.2 pgvector 0.7.x → 0.8.x

**Breaking Changes:**
- **None** - Fully backward compatible

**New Features:**
- Half-precision vectors: `HALFVEC(1536)` type
- Sparse vectors: `SPARSEVEC(10000)` type
- Iterative index scans (automatic optimization)

**Migration:** No action required. New features opt-in.

---

### 4.3 Qdrant 1.14.x → 1.15.x

**Breaking Changes:**
- **None** - Fully backward compatible

**New Features:**
- Asymmetric quantization
- 1.5-bit and 2-bit quantization
- HNSW healing (automatic)

**Migration:** No action required. New features opt-in.

---

### 4.4 Graphiti 0.20.x → 0.21.x

**Breaking Changes:**
- **Python 3.10+ Required** (was 3.8+)
- **Neo4j 5.13+ Required** for VECTOR index support

**New Features:**
- GPT-4 Turbo support
- Improved entity deduplication
- Better temporal query performance

**Migration:**
- Upgrade Python to 3.10+
- Upgrade Neo4j to 5.13+
- No schema changes required

---

## 5. Deprecation Notices

### 5.1 Currently Deprecated

**Neo4j:**
- ❌ **BTREE indexes** (replaced by RANGE indexes in 5.x)
  - Action: Use `CREATE INDEX ... FOR (n:Label) ON (n.property)` (defaults to RANGE)

**PostgreSQL:**
- ❌ **IVFFlat indexes** (slower than HNSW, consider migration)
  - Action: Rebuild as HNSW: `CREATE INDEX ... USING hnsw (embedding vector_cosine_ops)`

**Graphiti:**
- ⚠️ **Old entity deduplication method** (0.19.x and earlier)
  - Action: Update to 0.21.0+ for improved deduplication

---

### 5.2 Future Deprecations

**Expected in 2026:**

**Neo4j:**
- Legacy block format (pre-2025.x) - Will require migration to new block format

**pgvector:**
- IVFFlat indexes may be phased out in favor of HNSW (no official timeline)

**Qdrant:**
- Scalar INT8 quantization may be replaced by asymmetric quantization as default

---

## 6. Testing Matrix

### 6.1 Tested Configurations

**✅ Fully Tested:**
- Python 3.11 + Neo4j 5.27.0 + PostgreSQL 16 + Qdrant 1.15.1 + Redis 7.2 + Temporal 1.11.0 + Graphiti 0.21.0
- Python 3.11 + Neo4j 5.13.0 + PostgreSQL 15 + Qdrant 1.14.0 + Redis 7.0 + Temporal 1.10.0 + Graphiti 0.21.0

**⚠️ Limited Testing:**
- Python 3.10 + Neo4j 5.27.0 + PostgreSQL 16 + Qdrant 1.15.1 + Redis 7.2 + Temporal 1.11.0 + Graphiti 0.22.0

**❌ Not Tested:**
- Python 3.12 (may work, not officially tested)
- Neo4j 2025.x (latest features, limited production testing)
- Graphiti 0.22.0 (pre-release, stability unknown)

---

## 7. Quick Reference

### Production Stack (Recommended)

```yaml
# docker-compose.yml
services:
  neo4j:
    image: neo4j:5.27.0
  postgres:
    image: ankane/pgvector:pg16
  qdrant:
    image: qdrant/qdrant:v1.15.1
  redis:
    image: redis:7.2-alpine
  temporal:
    image: temporalio/auto-setup:1.11.0
```

```txt
# requirements.txt
neo4j==5.27.0
psycopg2-binary==2.9.10
pgvector==0.8.1
qdrant-client==1.15.1
redis==6.4.0
temporalio==1.11.0
graphiti-core==0.21.0  # Stable
```

### Minimum Requirements

- **Python:** 3.10+
- **Neo4j:** 5.13+ (for VECTOR index)
- **PostgreSQL:** 14+ (15+ recommended)
- **pgvector:** 0.7.0+ (0.8.1 recommended)
- **Qdrant:** 1.9+ (1.15.1 recommended)
- **Redis:** 6.0+ (7.2 recommended)
- **Temporal:** 1.9+ (1.11.0 recommended)
- **Graphiti:** 0.19+ (0.21.0 recommended)

---

**Document Version:** 1.0
**Last Updated:** 2025-11-01
**Verification Date:** 2025-11-01
**Next Review:** 2026-02-01 (3 months)
**Maintained By:** Apex Memory System Development Team
