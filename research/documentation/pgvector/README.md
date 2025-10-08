# pgvector - PostgreSQL Vector Extension

**Tier:** 1 (Official Documentation - GitHub Official Project)
**Date Accessed:** 2025-10-06
**Current Version:** 0.8.1 (Latest stable)
**Target Version:** Compatible with PostgreSQL 13+

## Official Documentation Links

### Main Repository
- **GitHub Repository:** https://github.com/pgvector/pgvector
- **Project Status:** 13.7k+ stars, actively maintained
- **License:** Open source

### Installation & Setup
- **Installation Guide:** Available in repository README
- **Compilation:** Source compilation instructions provided
- **Package Managers:** Docker, Homebrew, PGXN, APT, Yum, pkg, conda-forge

## Key Concepts & Features

### Vector Support
pgvector adds vector similarity search capabilities to PostgreSQL, supporting:

1. **Vector Types:**
   - Single-precision (float32) vectors
   - Half-precision (float16) vectors
   - Binary vectors
   - Sparse vectors

2. **Distance Metrics:**
   - **L2 distance** (Euclidean): `<->`
   - **Inner product**: `<#>`
   - **Cosine distance**: `<=>`
   - **L1 distance** (Manhattan): `<+>`
   - **Hamming distance**: `<%>`
   - **Jaccard distance**: `<~>`

3. **Vector Dimensions:**
   - Supports vectors up to **2,000 dimensions**
   - Configurable dimension size per column

### Architecture

pgvector integrates directly with PostgreSQL as an extension:
- Native PostgreSQL data type
- Leverages PostgreSQL's indexing infrastructure
- Uses standard SQL syntax for queries
- Compatible with PostgreSQL transactions and ACID guarantees

## Installation

### From Source (Recommended for Control)
```bash
cd /tmp
git clone --branch v0.8.1 https://github.com/pgvector/pgvector.git
cd pgvector
make
sudo make install
```

### Docker
```bash
docker pull pgvector/pgvector:pg16
docker run -p 5432:5432 -e POSTGRES_PASSWORD=password pgvector/pgvector:pg16
```

### Package Managers
```bash
# Homebrew (macOS)
brew install pgvector

# APT (Debian/Ubuntu)
sudo apt install postgresql-16-pgvector

# Yum (RHEL/CentOS)
sudo yum install pgvector_16
```

## Basic Usage

### 1. Enable Extension
```sql
CREATE EXTENSION vector;
```

### 2. Create Table with Vector Column
```sql
CREATE TABLE items (
    id bigserial PRIMARY KEY,
    embedding vector(3),  -- 3-dimensional vector
    metadata jsonb
);

-- Variable dimension vector (up to 2000)
CREATE TABLE documents (
    id bigserial PRIMARY KEY,
    content text,
    embedding vector(1536),  -- OpenAI embedding dimension
    created_at timestamp DEFAULT now()
);
```

### 3. Insert Vectors
```sql
-- Direct insertion
INSERT INTO items (embedding) VALUES ('[1,2,3]'), ('[4,5,6]');

-- From Python/application (parameterized)
INSERT INTO items (embedding) VALUES ($1);  -- Pass vector as array
```

### 4. Query Nearest Neighbors
```sql
-- Find 5 nearest neighbors using L2 distance
SELECT id, embedding
FROM items
ORDER BY embedding <-> '[3,1,2]'
LIMIT 5;

-- Cosine similarity (1 - cosine distance)
SELECT id, 1 - (embedding <=> '[3,1,2]') AS cosine_similarity
FROM items
ORDER BY embedding <=> '[3,1,2]'
LIMIT 5;

-- Filter with WHERE clause
SELECT id, embedding
FROM items
WHERE metadata->>'category' = 'tech'
ORDER BY embedding <-> '[3,1,2]'
LIMIT 5;
```

## Indexing

### Index Types

#### 1. HNSW (Hierarchical Navigable Small World)
Best for most use cases - excellent recall with fast queries.

```sql
-- Create HNSW index with L2 distance
CREATE INDEX ON items USING hnsw (embedding vector_l2_ops);

-- HNSW with cosine distance
CREATE INDEX ON items USING hnsw (embedding vector_cosine_ops);

-- HNSW with inner product
CREATE INDEX ON items USING hnsw (embedding vector_ip_ops);

-- Tuning parameters
CREATE INDEX ON items USING hnsw (embedding vector_l2_ops)
WITH (m = 16, ef_construction = 64);
```

**HNSW Parameters:**
- `m` (default: 16) - Number of connections per layer. Higher = better recall, more memory
- `ef_construction` (default: 64) - Size of dynamic candidate list during construction. Higher = better index quality, slower build

**Query-time parameter:**
```sql
SET hnsw.ef_search = 100;  -- Higher = better recall, slower queries
```

#### 2. IVFFlat (Inverted File Flat)
Faster build time, lower memory usage, lower recall.

```sql
-- Create IVFFlat index
CREATE INDEX ON items USING ivfflat (embedding vector_l2_ops)
WITH (lists = 100);

-- Choose lists parameter
-- lists = rows / 1000 for small datasets (< 1M rows)
-- lists = sqrt(rows) for larger datasets
```

**IVFFlat Parameters:**
- `lists` (default: 100) - Number of inverted lists. More lists = faster queries, lower recall

**Query-time parameter:**
```sql
SET ivfflat.probes = 10;  -- Number of lists to search. Higher = better recall, slower queries
```

### Index Selection Guidelines

| Use Case | Index Type | Why |
|----------|------------|-----|
| High recall required | HNSW | Best accuracy |
| Limited memory | IVFFlat | Lower memory footprint |
| Fast inserts | IVFFlat | Faster build time |
| General purpose | HNSW | Best balance |
| Exact search | No index | Brute force scan |

## Best Practices

### Performance Optimization

#### 1. Index After Bulk Load
```sql
-- Load data first
COPY items (embedding) FROM 'vectors.csv' CSV;

-- Then create index
CREATE INDEX ON items USING hnsw (embedding vector_l2_ops);
```

#### 2. Use Appropriate Distance Metric
```sql
-- Normalized vectors (embeddings from OpenAI, etc.) - use cosine or inner product
CREATE INDEX ON embeddings USING hnsw (embedding vector_cosine_ops);

-- Unnormalized vectors - use L2 distance
CREATE INDEX ON features USING hnsw (embedding vector_l2_ops);
```

#### 3. Limit Results
```sql
-- Always use LIMIT for nearest neighbor queries
SELECT * FROM items ORDER BY embedding <-> '[1,2,3]' LIMIT 10;
```

#### 4. Combine with Filters
```sql
-- Filter before vector search when possible
WITH filtered AS (
    SELECT id, embedding
    FROM items
    WHERE category = 'tech' AND created_at > '2025-01-01'
)
SELECT id FROM filtered
ORDER BY embedding <-> '[1,2,3]'
LIMIT 10;
```

### Schema Design

#### 1. Separate Vector and Metadata Tables
```sql
-- Metadata table
CREATE TABLE documents (
    id bigserial PRIMARY KEY,
    title text,
    content text,
    category varchar(50),
    created_at timestamp DEFAULT now()
);

-- Vector table (optimized for similarity search)
CREATE TABLE document_embeddings (
    document_id bigint PRIMARY KEY REFERENCES documents(id),
    embedding vector(1536)
);

CREATE INDEX ON document_embeddings USING hnsw (embedding vector_cosine_ops);
```

#### 2. Partition Large Tables
```sql
-- Partition by category for isolated searches
CREATE TABLE embeddings (
    id bigserial,
    category varchar(50),
    embedding vector(1536),
    PRIMARY KEY (id, category)
) PARTITION BY LIST (category);

CREATE TABLE embeddings_tech PARTITION OF embeddings FOR VALUES IN ('tech');
CREATE TABLE embeddings_science PARTITION OF embeddings FOR VALUES IN ('science');
```

### Memory Management

#### 1. Monitor Index Size
```sql
-- Check index size
SELECT pg_size_pretty(pg_relation_size('items_embedding_idx'));

-- Check table size
SELECT pg_size_pretty(pg_total_relation_size('items'));
```

#### 2. Estimate Memory Requirements
- HNSW index size ≈ `vectors * dimensions * 4 bytes * (m + 1)`
- Example: 1M vectors, 1536 dimensions, m=16
  - ≈ 1,000,000 * 1536 * 4 * 17 ≈ 105 GB

### Data Integrity

#### 1. Validate Vector Dimensions
```sql
-- Add check constraint
ALTER TABLE items ADD CONSTRAINT valid_embedding
CHECK (array_length(embedding::float[], 1) = 1536);
```

#### 2. Handle NULL Vectors
```sql
-- Prevent NULL vectors if required
ALTER TABLE items ALTER COLUMN embedding SET NOT NULL;

-- Or filter in queries
SELECT * FROM items
WHERE embedding IS NOT NULL
ORDER BY embedding <-> '[1,2,3]'
LIMIT 10;
```

## Integration Patterns

### Python Integration (psycopg2/psycopg3)

```python
import psycopg2
import numpy as np

# Connect
conn = psycopg2.connect("dbname=apex_memory user=postgres")
cursor = conn.cursor()

# Enable extension
cursor.execute("CREATE EXTENSION IF NOT EXISTS vector")

# Create table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS embeddings (
        id serial PRIMARY KEY,
        embedding vector(3)
    )
""")

# Insert vector
embedding = np.array([1.0, 2.0, 3.0])
cursor.execute(
    "INSERT INTO embeddings (embedding) VALUES (%s)",
    (embedding.tolist(),)
)

# Query nearest neighbors
query_vector = [3.0, 1.0, 2.0]
cursor.execute("""
    SELECT id, embedding
    FROM embeddings
    ORDER BY embedding <-> %s
    LIMIT 5
""", (query_vector,))

results = cursor.fetchall()
for row in results:
    print(f"ID: {row[0]}, Vector: {row[1]}")

conn.commit()
cursor.close()
conn.close()
```

### Using with SQLAlchemy
```python
from sqlalchemy import create_engine, Column, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pgvector.sqlalchemy import Vector

Base = declarative_base()

class Item(Base):
    __tablename__ = 'items'
    id = Column(Integer, primary_key=True)
    embedding = Column(Vector(3))

engine = create_engine('postgresql://user:pass@localhost/dbname')
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

# Insert
item = Item(embedding=[1, 2, 3])
session.add(item)
session.commit()

# Query
from pgvector.sqlalchemy import L2Distance

results = session.query(Item).order_by(
    L2Distance(Item.embedding, [3, 1, 2])
).limit(5).all()
```

### Async Python (asyncpg)
```python
import asyncpg
import numpy as np

async def vector_search():
    conn = await asyncpg.connect('postgresql://user:pass@localhost/dbname')

    # Register vector type
    await conn.execute('CREATE EXTENSION IF NOT EXISTS vector')

    # Insert
    embedding = [1.0, 2.0, 3.0]
    await conn.execute(
        'INSERT INTO items (embedding) VALUES ($1)',
        embedding
    )

    # Query
    query_vector = [3.0, 1.0, 2.0]
    rows = await conn.fetch(
        'SELECT id, embedding FROM items ORDER BY embedding <-> $1 LIMIT 5',
        query_vector
    )

    await conn.close()
    return rows
```

## Version Compatibility

### PostgreSQL Versions
- **Minimum:** PostgreSQL 13
- **Recommended:** PostgreSQL 16 (latest features and performance)
- **Tested:** PostgreSQL 13, 14, 15, 16, 17

### Language Support
- C (native via libpq)
- Python (psycopg2, psycopg3, asyncpg, SQLAlchemy)
- JavaScript/Node.js (node-postgres)
- Ruby (pg gem)
- Java (JDBC)
- Go (pgx)
- Rust (tokio-postgres)
- Any language with PostgreSQL driver

## Relevant Features for Apex Memory System

### Hybrid Search Capabilities
```sql
-- Combine full-text search with vector search
SELECT
    id,
    ts_rank(to_tsvector('english', content), query) AS text_score,
    1 - (embedding <=> $1) AS vector_score
FROM documents,
     to_tsquery('english', 'graph database') AS query
WHERE to_tsvector('english', content) @@ query
ORDER BY (text_score * 0.3 + vector_score * 0.7) DESC
LIMIT 10;
```

### Temporal Vector Search
```sql
-- Time-aware vector search
SELECT id, content, created_at
FROM documents
WHERE created_at >= '2025-01-01'
ORDER BY embedding <-> $1
LIMIT 10;

-- Decay by time
SELECT
    id,
    (1 - (embedding <=> $1)) *
    (1 / (1 + EXTRACT(EPOCH FROM (now() - created_at)) / 86400)) AS score
FROM documents
ORDER BY score DESC
LIMIT 10;
```

### Multi-vector Search
```sql
-- Store multiple embeddings per entity
CREATE TABLE multi_embeddings (
    id bigserial PRIMARY KEY,
    title_embedding vector(768),
    content_embedding vector(1536),
    metadata jsonb
);

-- Search across multiple embeddings
WITH title_matches AS (
    SELECT id, title_embedding <=> $1 AS distance
    FROM multi_embeddings
    ORDER BY distance LIMIT 20
),
content_matches AS (
    SELECT id, content_embedding <=> $2 AS distance
    FROM multi_embeddings
    ORDER BY distance LIMIT 20
)
SELECT COALESCE(t.id, c.id) AS id
FROM title_matches t
FULL OUTER JOIN content_matches c ON t.id = c.id
ORDER BY COALESCE(t.distance, 999) + COALESCE(c.distance, 999)
LIMIT 10;
```

## Monitoring & Maintenance

### Query Performance
```sql
-- Explain vector query
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM items
ORDER BY embedding <-> '[1,2,3]'
LIMIT 10;

-- Check index usage
SELECT schemaname, tablename, indexname, idx_scan
FROM pg_stat_user_indexes
WHERE indexname LIKE '%embedding%';
```

### Index Maintenance
```sql
-- Rebuild index if needed
REINDEX INDEX items_embedding_idx;

-- Analyze table statistics
ANALYZE items;
```

### Performance Tuning
```sql
-- Adjust work_mem for index creation
SET work_mem = '2GB';
CREATE INDEX ON items USING hnsw (embedding vector_l2_ops);
RESET work_mem;

-- Tune HNSW search
SET hnsw.ef_search = 200;  -- Higher = better recall, slower

-- Tune IVFFlat search
SET ivfflat.probes = 20;  -- More probes = better recall
```

## Common Issues & Solutions

### Issue: Slow Queries
**Solution:**
1. Create appropriate index (HNSW for accuracy, IVFFlat for speed)
2. Increase `hnsw.ef_search` or `ivfflat.probes`
3. Use LIMIT on queries
4. Ensure vectors are normalized for cosine distance

### Issue: Large Index Size
**Solution:**
1. Reduce `m` parameter in HNSW (lower accuracy tradeoff)
2. Use IVFFlat instead of HNSW
3. Use half-precision vectors if precision allows
4. Partition tables by category/timeframe

### Issue: Slow Inserts
**Solution:**
1. Batch inserts with COPY or INSERT multi-row
2. Create indexes after bulk load
3. Use IVFFlat for faster index updates
4. Consider disabling indexes during bulk operations

## Learning Resources

### Official Resources
- **GitHub README:** Comprehensive guide and examples
- **GitHub Issues:** Active community support and discussions
- **Release Notes:** Version-specific changes and improvements

### Community Resources
- Supabase pgvector guide
- PostgreSQL extension documentation
- Various blog posts and tutorials (verify recency)

## Summary

pgvector is a mature, production-ready extension that adds vector similarity search to PostgreSQL. It integrates seamlessly with PostgreSQL's ecosystem, supports multiple distance metrics and indexing strategies, and scales well for real-world applications. For the Apex Memory System, pgvector provides the vector search capabilities needed for semantic retrieval while leveraging PostgreSQL's robust transaction and data management features.

**Key Strengths:**
- Native PostgreSQL integration
- Multiple indexing options (HNSW, IVFFlat)
- Supports various distance metrics
- Excellent Python ecosystem support
- Production-proven with large deployments
- Open source and actively maintained
- Combines well with PostgreSQL's relational and full-text search features

**Recommended Setup for Apex Memory:**
- PostgreSQL 16 + pgvector 0.8.1+
- HNSW indexes for high-recall semantic search
- Cosine distance for normalized embeddings (OpenAI, etc.)
- Separate tables for vectors and metadata for optimal performance
