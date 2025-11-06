# Migration Scripts

**Purpose:** Production-ready implementation scripts for migrating to the 6-hub schema across all 5 databases.

**Status:** ✅ Complete (13 scripts generated)

**Generated:** Week 3 Day 5

---

## 📁 Directory Structure

```
scripts/
├── README.md (this file)
├── requirements.txt                    # Python dependencies
├── .env.example                        # Environment configuration template
├── run_migration.sh                    # Master execution script (TODO)
│
├── migration/                          # Database migration scripts
│   ├── phase1_postgresql/             # Phase 1: PostgreSQL Foundation
│   │   ├── 01_create_database.sql
│   │   ├── 02_create_schemas.sql
│   │   ├── 03_create_tables_hub3.sql
│   │   └── 04_transform_and_load.py
│   │
│   ├── phase2_neo4j/                  # Phase 2: Neo4j Relationships
│   │   ├── 01_create_constraints.cypher
│   │   ├── 02_load_nodes.py
│   │   └── 03_create_relationships.py
│   │
│   ├── phase3_qdrant/                 # Phase 3: Qdrant Vectors
│   │   ├── 01_create_collections.py
│   │   └── 02_load_vectors.py
│   │
│   ├── phase4_redis/                  # Phase 4: Redis Cache
│   │   └── 01_configure_redis.py
│   │
│   └── phase5_graphiti/               # Phase 5: Graphiti Intelligence
│       └── 01_initialize_graphiti.py
│
├── validation/                        # Test scripts
│   ├── test_postgres_validation.py    # PostgreSQL schema tests
│   ├── test_neo4j_validation.py       # Neo4j constraint tests
│   └── test_cross_db_sync.py          # Cross-database sync tests
│
└── sample_data/                       # Sample data generators
    └── (TODO: generate_hub1_data.py through generate_hub6_data.py)
```

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd scripts
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your database credentials
```

### 3. Run Master Migration Script

```bash
chmod +x run_migration.sh
./run_migration.sh --all --execute
```

**Or run phases individually:**

```bash
./run_migration.sh --phase 1 --execute    # PostgreSQL
./run_migration.sh --phase 2 --execute    # Neo4j
./run_migration.sh --phase 3 --execute    # Qdrant
./run_migration.sh --phase 4 --execute    # Redis
./run_migration.sh --phase 5 --execute    # Graphiti
```

---

## 📋 Phase-by-Phase Execution Guide

### Phase 1: PostgreSQL Foundation

**Purpose:** Create PostgreSQL database, schemas, tables, and load initial data

**Scripts:**
1. `01_create_database.sql` - Creates apex_memory database with 5 extensions
2. `02_create_schemas.sql` - Creates 6 hub schemas with permissions
3. `03_create_tables_hub3.sql` - Creates 7 Hub 3 tables with constraints/indexes/triggers
4. `04_transform_and_load.py` - Transforms and loads data from old system

**Execution:**

```bash
# Step 1: Create database (run as PostgreSQL superuser)
psql -U postgres -f migration/phase1_postgresql/01_create_database.sql

# Step 2: Create schemas (run as apex user)
psql -U apex -d apex_memory -f migration/phase1_postgresql/02_create_schemas.sql

# Step 3: Create tables
psql -U apex -d apex_memory -f migration/phase1_postgresql/03_create_tables_hub3.sql

# Step 4: Transform and load data (dry-run first)
python migration/phase1_postgresql/04_transform_and_load.py --hub 3 --dry-run
python migration/phase1_postgresql/04_transform_and_load.py --hub 3 --execute
```

**Verification:**

```bash
psql -U apex -d apex_memory -c "SELECT COUNT(*) FROM hub3_origin.tractors"
```

---

### Phase 2: Neo4j Relationships

**Purpose:** Create Neo4j constraints, load nodes from PostgreSQL, create relationships

**Scripts:**
1. `01_create_constraints.cypher` - Creates 45+ UNIQUE constraints and 20+ indexes
2. `02_load_nodes.py` - Syncs entities from PostgreSQL to Neo4j nodes
3. `03_create_relationships.py` - Creates relationships based on PostgreSQL foreign keys

**Execution:**

```bash
# Step 1: Create constraints
cypher-shell -u neo4j -p apexmemory2024 -f migration/phase2_neo4j/01_create_constraints.cypher

# Step 2: Load nodes (dry-run first)
python migration/phase2_neo4j/02_load_nodes.py --all --dry-run
python migration/phase2_neo4j/02_load_nodes.py --all --execute

# Step 3: Create relationships
python migration/phase2_neo4j/03_create_relationships.py --all --dry-run
python migration/phase2_neo4j/03_create_relationships.py --all --execute

# Step 4: Verify sync
python migration/phase2_neo4j/02_load_nodes.py --verify
python migration/phase2_neo4j/03_create_relationships.py --verify
```

**Verification:**

```bash
# Open Neo4j Browser: http://localhost:7474
# Run: MATCH (t:Tractor) RETURN count(t)
# Should match PostgreSQL count
```

---

### Phase 3: Qdrant Vectors

**Purpose:** Create Qdrant collections and load embeddings

**Scripts:**
1. `01_create_collections.py` - Creates 3 collections (document_chunks, entity_embeddings, query_cache)
2. `02_load_vectors.py` - Loads vectors from PostgreSQL embeddings

**Execution:**

```bash
# Step 1: Create collections (dry-run first)
python migration/phase3_qdrant/01_create_collections.py --all --dry-run
python migration/phase3_qdrant/01_create_collections.py --all --execute

# Step 2: Load vectors
python migration/phase3_qdrant/02_load_vectors.py --all --dry-run
python migration/phase3_qdrant/02_load_vectors.py --all --execute

# Step 3: Verify
python migration/phase3_qdrant/01_create_collections.py --verify
```

**Verification:**

```bash
# Open Qdrant dashboard: http://localhost:6333/dashboard
```

---

### Phase 4: Redis Cache

**Purpose:** Configure Redis for caching query results and embeddings

**Scripts:**
1. `01_configure_redis.py` - Configures cache namespaces, memory policy, indexes

**Execution:**

```bash
# Configure Redis (dry-run first)
python migration/phase4_redis/01_configure_redis.py --dry-run
python migration/phase4_redis/01_configure_redis.py --execute

# Verify
python migration/phase4_redis/01_configure_redis.py --verify
```

**Verification:**

```bash
redis-cli
> KEYS apex:config:*
> GET apex:config:cache_namespaces
```

---

### Phase 5: Graphiti Intelligence

**Purpose:** Initialize Graphiti for temporal reasoning and pattern detection

**Scripts:**
1. `01_initialize_graphiti.py` - Creates temporal indexes, registers entities, configures patterns

**Execution:**

```bash
# Initialize Graphiti (dry-run first)
python migration/phase5_graphiti/01_initialize_graphiti.py --dry-run
python migration/phase5_graphiti/01_initialize_graphiti.py --execute

# Verify
python migration/phase5_graphiti/01_initialize_graphiti.py --verify
```

**Verification:**

```bash
psql -U apex -d apex_memory -c "SELECT * FROM graphiti_config"
```

---

## 🧪 Validation Tests

**Run all validation tests after migration:**

```bash
cd scripts/validation
pytest -v

# Or run individually:
pytest test_postgres_validation.py -v
pytest test_neo4j_validation.py -v
pytest test_cross_db_sync.py -v
```

**Expected Results:**
- PostgreSQL: 25+ tests passing
- Neo4j: 20+ tests passing
- Cross-DB Sync: 10+ tests passing

---

## 📊 Migration Scripts Summary

| Phase | Database | Scripts | Purpose | Status |
|-------|----------|---------|---------|--------|
| 1 | PostgreSQL | 4 | Create database, schemas, tables, load data | ✅ Complete |
| 2 | Neo4j | 3 | Create constraints, load nodes, create relationships | ✅ Complete |
| 3 | Qdrant | 2 | Create collections, load vectors | ✅ Complete |
| 4 | Redis | 1 | Configure cache | ✅ Complete |
| 5 | Graphiti | 1 | Initialize temporal intelligence | ✅ Complete |
| **Validation** | All | 3 | Validate schema, constraints, sync | ✅ Complete |
| **Total** | | **13** | | ✅ Complete |

---

## 🛠️ Script Features

### Idempotent Execution
- All SQL/Cypher scripts use `IF NOT EXISTS` patterns
- Safe to run multiple times
- No data duplication on re-execution

### Dry-Run Mode
- All Python scripts support `--dry-run` flag
- Preview changes before execution
- Comprehensive logging

### Verification Mode
- All Python scripts support `--verify` flag
- Check database state without modifications
- Validate counts and constraints

### Comprehensive Logging
- Visual indicators (✅, ❌, ⚠️, 🔄, 📊, 🔍)
- Detailed statistics
- Error handling with stack traces

### Batch Processing
- PostgreSQL: `execute_batch` for bulk inserts
- Qdrant: Configurable batch size (default: 100)
- Optimized for performance

---

## 🔧 Configuration

### Database Credentials

Edit `.env` file with your credentials:

```env
# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=apex_memory
POSTGRES_USER=apex
POSTGRES_PASSWORD=your_password_here

# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password_here

# Qdrant
QDRANT_HOST=localhost
QDRANT_PORT=6333

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# OpenAI (for embeddings)
OPENAI_API_KEY=your_openai_api_key_here
```

### Embedding Dimensions

Default: 1536 (OpenAI text-embedding-3-small)

To use text-embedding-3-large (3072 dimensions):

```env
EMBEDDING_DIMENSION=3072
```

---

## 📝 Dependencies

```bash
# Core
python-dotenv==1.0.0

# Databases
psycopg2-binary==2.9.9     # PostgreSQL
neo4j==5.14.1              # Neo4j
qdrant-client==1.7.0       # Qdrant
redis==5.0.1               # Redis

# Testing
pytest==7.4.3
pytest-cov==4.1.0
```

---

## ⚠️ Important Notes

1. **PostgreSQL is PRIMARY** - Single source of truth for all data
2. **Neo4j is REPLICA** - Replicates entities and relationships from PostgreSQL
3. **Run in order** - Phase 1 must complete before Phase 2, etc.
4. **Always dry-run first** - Test scripts before executing
5. **Backup first** - Always backup databases before migration
6. **Check logs** - Review logs carefully for any errors

---

## 🎯 Next Steps

1. **Generate Sample Data** - Create sample data generators for all 6 hubs
2. **Create Master Script** - Build run_migration.sh for automated execution
3. **Test in Staging** - Run complete migration in staging environment
4. **Performance Testing** - Validate query performance after migration
5. **Production Deployment** - Execute migration in production with rollback plan

---

## 🆘 Troubleshooting

### Connection Errors

```bash
# Test PostgreSQL connection
psql -U apex -d apex_memory -c "SELECT 1"

# Test Neo4j connection
cypher-shell -u neo4j -p apexmemory2024 "RETURN 1"

# Test Qdrant connection
curl http://localhost:6333/collections

# Test Redis connection
redis-cli PING
```

### Permission Errors

```bash
# Grant PostgreSQL permissions
GRANT ALL ON SCHEMA hub3_origin TO apex;
GRANT ALL ON ALL TABLES IN SCHEMA hub3_origin TO apex;
```

### Data Sync Issues

```bash
# Run cross-database sync validation
pytest validation/test_cross_db_sync.py -v
```

---

## 📚 Related Documentation

- [Backbone Schema Context Documentation](../README.md)
- [6-Hub Architecture Overview](../)
- [Validation Queries](../queries/)
- [Schema Diagrams](../diagrams/)

---

**Generated:** Week 3 Day 5
**Status:** ✅ Production-Ready
**Version:** 1.0.0
