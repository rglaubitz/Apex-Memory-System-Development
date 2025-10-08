# API Specifications & Standards

**Research Phase:** Standards & Query Languages Collection
**Created:** 2025-10-06
**Quality Tier:** Tier 1 (Official Specifications)

---

## Table of Contents

1. [REST API Standards](#rest-api-standards)
2. [Query Language Specifications](#query-language-specifications)
3. [Data Format Standards](#data-format-standards)
4. [Vector Search Standards](#vector-search-standards)

---

## REST API Standards

### OpenAPI 3.0.3 Specification

**Official Specification:** https://spec.openapis.org/oas/v3.0.3.html
**Latest Version:** OpenAPI 3.1.0 (https://spec.openapis.org/oas/v3.1.0.html)
**Maintainer:** OpenAPI Initiative (https://www.openapis.org/)
**Status:** Industry standard for REST API documentation

#### Key Features

- **Purpose:** Defines a standard, language-agnostic interface to RESTful APIs
- **Format:** JSON or YAML-based API description
- **Validation:** Enables automated testing and code generation

#### Core Components

1. **Info Object**
   - API title, version, description
   - Contact and license information

2. **Paths Object**
   - API endpoints and operations
   - HTTP methods (GET, POST, PUT, DELETE, PATCH)
   - Path templating support

3. **Components Object**
   - Reusable schemas
   - Parameters, responses, examples
   - Security schemes

4. **Parameters**
   - Location: path, query, header, cookie
   - Schema definitions
   - Validation rules

5. **Request Bodies**
   - Content type definitions
   - Schema references
   - Required field specifications

6. **Responses**
   - HTTP status code mappings
   - Response schemas
   - Headers and links

7. **Security Schemes**
   - API keys
   - OAuth2
   - OpenID Connect
   - HTTP authentication

#### Best Practices

**Source:** https://learn.openapis.org/best-practices.html

- **Design-First Approach:** Write API specification before implementation
- **Reusable Components:** Use `$ref` for schemas, parameters, responses
- **Meaningful Examples:** Include realistic examples for all operations
- **Versioning:** Include version in info object and consider URL versioning
- **Consistent Naming:** Use kebab-case for paths, camelCase for properties
- **Error Responses:** Document all possible error responses with examples

#### Adoption

- **Industry Usage:** De facto standard for REST APIs
- **Tools:** Swagger UI, ReDoc, Postman, API clients generators
- **Integration:** Native support in FastAPI, Django REST, Express.js

---

### Richardson Maturity Model

**Original Article:** https://martinfowler.com/articles/richardsonMaturityModel.html
**Author:** Martin Fowler (based on Leonard Richardson's work)
**Status:** Authoritative REST API design framework

#### The Four Levels

**Level 0: The Swamp of POX**
- Single endpoint for all operations
- HTTP as transport tunnel
- No resource concept
- Example: SOAP, XML-RPC

**Level 1: Resources**
- Multiple endpoints representing resources
- URIs identify individual resources
- Still limited HTTP verb usage
- Example: `/users`, `/products/{id}`

**Level 2: HTTP Verbs**
- Proper use of HTTP methods:
  - `GET` - Retrieve resource (idempotent, safe)
  - `POST` - Create new resource
  - `PUT` - Update/replace resource (idempotent)
  - `PATCH` - Partial update
  - `DELETE` - Remove resource (idempotent)
- HTTP status codes communicate results:
  - `200 OK` - Success
  - `201 Created` - Resource created
  - `204 No Content` - Success with no body
  - `400 Bad Request` - Client error
  - `404 Not Found` - Resource doesn't exist
  - `500 Internal Server Error` - Server error

**Level 3: Hypermedia Controls (HATEOAS)**
- Responses include links to related resources
- Self-describing API
- Clients discover capabilities dynamically
- Example: HAL, JSON:API, Siren formats

#### REST Compliance Note

**Important:** Roy Fielding (REST creator) emphasizes that Level 3 is a **pre-condition** for true REST, not the final goal. The RMM is a useful thinking tool but not a complete REST definition.

#### Best Practices

- **Target Level 2** for most practical APIs
- **Use Level 3** when client discovery is valuable
- **Consistent HTTP semantics** across all endpoints
- **Idempotent operations** for PUT and DELETE

---

### HTTP Method Semantics

**Specification:** RFC 7231 (HTTP/1.1 Semantics and Content)
**URL:** https://tools.ietf.org/html/rfc7231

#### Safe Methods (Read-Only)

- `GET` - Retrieve representation
- `HEAD` - Get headers only
- `OPTIONS` - Describe communication options

#### Idempotent Methods

- `PUT` - Multiple identical requests have same effect as single request
- `DELETE` - Deleting already-deleted resource is safe
- `GET`, `HEAD`, `OPTIONS` - Also idempotent

#### Non-Idempotent Methods

- `POST` - May create multiple resources if called multiple times
- `PATCH` - Depends on implementation

#### Method Selection Guide

| Operation | Method | Idempotent | Safe |
|-----------|--------|------------|------|
| List all | GET | Yes | Yes |
| Get one | GET | Yes | Yes |
| Create | POST | No | No |
| Update (full) | PUT | Yes | No |
| Update (partial) | PATCH | Depends | No |
| Delete | DELETE | Yes | No |
| Replace or create | PUT | Yes | No |

---

## Query Language Specifications

### Cypher Query Language (Neo4j)

**Official Manual:** https://neo4j.com/docs/cypher-manual/current/
**Version:** Cypher 5 (current), Cypher 25 (future development)
**Standard:** ISO/IEC 39075:2024 GQL-conformant
**Maintainer:** Neo4j, openCypher initiative

#### Overview

Cypher is Neo4j's declarative query language for property graph databases. It provides an intuitive, SQL-like syntax for graph traversal and pattern matching.

#### Key Concepts

**Nodes:** Represented with parentheses `(n)`
- Labels: `(p:Person)`
- Properties: `(p:Person {name: 'Alice'})`

**Relationships:** Represented with brackets `[r]`
- Direction: `(a)-[r]->(b)` or `(a)<-[r]-(b)` or `(a)-[r]-(b)`
- Type: `[r:KNOWS]`
- Properties: `[r:KNOWS {since: 2020}]`

**Patterns:** Combine nodes and relationships
```cypher
(alice:Person)-[:KNOWS]->(bob:Person)
```

#### Core Operations

**MATCH** - Find patterns
```cypher
MATCH (p:Person {name: 'Alice'})
RETURN p
```

**CREATE** - Create nodes and relationships
```cypher
CREATE (p:Person {name: 'Bob', age: 30})
```

**WHERE** - Filter results
```cypher
MATCH (p:Person)
WHERE p.age > 25
RETURN p.name
```

**RETURN** - Specify output
```cypher
MATCH (p:Person)
RETURN p.name, p.age
ORDER BY p.age DESC
LIMIT 10
```

**MERGE** - Create if not exists (upsert)
```cypher
MERGE (p:Person {email: 'alice@example.com'})
ON CREATE SET p.created = timestamp()
ON MATCH SET p.lastSeen = timestamp()
```

**DELETE** - Remove nodes/relationships
```cypher
MATCH (p:Person {name: 'Bob'})
DELETE p
```

**SET** - Update properties
```cypher
MATCH (p:Person {name: 'Alice'})
SET p.age = 31
```

#### Advanced Features

- **Path traversal:** `(a)-[*1..5]->(b)` (1 to 5 hops)
- **Aggregation:** `COUNT()`, `SUM()`, `AVG()`, `COLLECT()`
- **Functions:** `size()`, `length()`, `nodes()`, `relationships()`
- **Procedures:** `CALL db.labels()` (system procedures)

#### openCypher Standard

**Project:** https://opencypher.org/
**Goal:** Open specification for graph query language
**Adoption:** Multiple graph databases support Cypher variants

#### GQL (Graph Query Language) Standard

**Specification:** ISO/IEC 39075:2024
**Published:** April 12, 2024
**Significance:** First new ISO database language standard since SQL (1986)
**Length:** 628 pages
**Cost:** 217 CHF
**URL:** https://www.iso.org/standard/76120.html

**Key Details:**
- Based on openCypher and Cypher
- Industry-wide collaboration (Neo4j, Oracle, TigerGraph, etc.)
- Property graph query capabilities
- Data definition and manipulation
- Graph creation, querying, maintenance, and control

---

### PostgreSQL + pgvector SQL Syntax

**Official Repo:** https://github.com/pgvector/pgvector
**GitHub Stars:** 15k+ (Tier 2 quality)
**Maintainer:** Andrew Kane
**PostgreSQL Version:** 12+

#### Installation

```sql
CREATE EXTENSION vector;
```

#### Vector Data Type

**Syntax:** `vector(dimensions)`

```sql
CREATE TABLE documents (
    id BIGSERIAL PRIMARY KEY,
    content TEXT,
    embedding vector(1536)  -- OpenAI ada-002 dimension
);
```

#### Vector Operations

**Distance Operators:**
- `<->` - Euclidean distance (L2)
- `<#>` - Negative inner product
- `<=>` - Cosine distance

**Similarity Operators:**
- `<->` returns smaller values for closer vectors
- `<#>` optimized for maximum inner product search
- `<=>` measures cosine similarity (0 = identical, 2 = opposite)

#### Vector Search Queries

**Nearest Neighbor Search:**
```sql
SELECT id, content, embedding <-> '[0.1, 0.2, ..., 0.8]' AS distance
FROM documents
ORDER BY embedding <-> '[0.1, 0.2, ..., 0.8]'
LIMIT 10;
```

**Similarity Threshold:**
```sql
SELECT id, content
FROM documents
WHERE embedding <=> '[0.1, 0.2, ..., 0.8]' < 0.3
ORDER BY embedding <=> '[0.1, 0.2, ..., 0.8]'
LIMIT 10;
```

#### Index Types

**IVFFlat (Inverted File Index):**
```sql
CREATE INDEX ON documents USING ivfflat (embedding vector_l2_ops)
WITH (lists = 100);
```

**HNSW (Hierarchical Navigable Small World):**
```sql
CREATE INDEX ON documents USING hnsw (embedding vector_l2_ops);
-- OR for cosine distance:
CREATE INDEX ON documents USING hnsw (embedding vector_cosine_ops);
```

**Index Parameters:**
- `lists` - Number of clusters for IVFFlat (rule of thumb: rows/1000)
- `m` - Max connections per layer in HNSW (default: 16)
- `ef_construction` - HNSW build quality (default: 64)

**Query Tuning:**
```sql
SET ivfflat.probes = 10;  -- Number of lists to search
SET hnsw.ef_search = 40;  -- HNSW search quality
```

#### Best Practices

- **Index selection:** HNSW for better recall, IVFFlat for larger datasets
- **Dimension limits:** Max 16,000 dimensions per vector
- **Batch inserts:** Disable indexes during bulk loading
- **Query planning:** Use `EXPLAIN ANALYZE` to verify index usage

---

### PromQL (Prometheus Query Language)

**Official Documentation:** https://prometheus.io/docs/prometheus/latest/querying/
**Project:** Prometheus (CNCF Graduated)
**Status:** De facto standard for metrics querying
**Use Case:** Time-series data, monitoring, alerting

#### Overview

PromQL is a functional query language for selecting and aggregating time series data in real-time.

#### Data Types

1. **Instant Vector** - Set of time series with single sample per series
2. **Range Vector** - Set of time series with multiple samples over time
3. **Scalar** - Simple numeric floating point value
4. **String** - String value (currently unused)

#### Basic Queries

**Select by metric name:**
```promql
http_requests_total
```

**Filter by labels:**
```promql
http_requests_total{job="api-server", method="GET"}
```

**Range selector:**
```promql
http_requests_total[5m]  # Last 5 minutes
```

#### Operators

**Arithmetic:** `+`, `-`, `*`, `/`, `%`, `^`

**Comparison:** `==`, `!=`, `>`, `<`, `>=`, `<=`

**Logical:** `and`, `or`, `unless`

#### Aggregation Functions

```promql
sum(http_requests_total)                    # Total requests
avg(http_requests_total)                    # Average
max(http_requests_total)                    # Maximum
min(http_requests_total)                    # Minimum
count(http_requests_total)                  # Count
rate(http_requests_total[5m])              # Per-second rate
increase(http_requests_total[1h])          # Increase over 1 hour
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
```

#### Grouping

**By labels:**
```promql
sum by (job) (http_requests_total)
```

**Without specific labels:**
```promql
sum without (instance) (http_requests_total)
```

#### Common Patterns

**Request rate:**
```promql
rate(http_requests_total[5m])
```

**Error ratio:**
```promql
rate(http_requests_total{status=~"5.."}[5m]) /
rate(http_requests_total[5m])
```

**95th percentile latency:**
```promql
histogram_quantile(0.95,
  rate(http_request_duration_seconds_bucket[5m])
)
```

#### Functions Reference

**Rate/Increase:**
- `rate()` - Per-second rate over time window
- `irate()` - Instant rate (last 2 points)
- `increase()` - Total increase over time window

**Aggregation over time:**
- `avg_over_time()`
- `max_over_time()`
- `min_over_time()`
- `sum_over_time()`

**Prediction:**
- `predict_linear()` - Linear extrapolation

#### Best Practices

- Use `rate()` for counters, not raw values
- Choose appropriate time windows (4x scrape interval minimum)
- Use recording rules for complex queries
- Label cardinality matters for performance

---

### Redis Commands

**Official Documentation:** https://redis.io/docs/latest/commands/
**Version:** Redis 7.x
**License:** BSD 3-Clause (open source)
**Status:** Industry-standard in-memory data store

#### Command Categories

**Key-Value Operations:**
- `SET key value` - Set string value
- `GET key` - Get string value
- `DEL key [key ...]` - Delete keys
- `EXISTS key [key ...]` - Check key existence
- `EXPIRE key seconds` - Set expiration
- `TTL key` - Get time to live

**Data Structures:**

**Strings:**
```redis
SET user:1000:name "Alice"
GET user:1000:name
INCR user:1000:visits
```

**Hashes:**
```redis
HSET user:1000 name "Alice" age 30
HGET user:1000 name
HGETALL user:1000
```

**Lists:**
```redis
LPUSH queue:tasks "task1"
RPOP queue:tasks
LRANGE queue:tasks 0 -1
```

**Sets:**
```redis
SADD tags:article:1 "python" "redis"
SMEMBERS tags:article:1
SINTER tags:article:1 tags:article:2
```

**Sorted Sets:**
```redis
ZADD leaderboard 100 "player1" 200 "player2"
ZRANGE leaderboard 0 9 WITHSCORES
ZRANK leaderboard "player1"
```

#### Caching Patterns

**Cache-Aside (Lazy Loading):**
```python
def get_user(user_id):
    # Try cache first
    cached = redis.get(f"user:{user_id}")
    if cached:
        return json.loads(cached)

    # Cache miss - fetch from DB
    user = db.query("SELECT * FROM users WHERE id = ?", user_id)

    # Store in cache
    redis.setex(f"user:{user_id}", 3600, json.dumps(user))
    return user
```

**Write-Through:**
```python
def update_user(user_id, data):
    # Update database
    db.update("users", user_id, data)

    # Update cache immediately
    redis.setex(f"user:{user_id}", 3600, json.dumps(data))
```

**Write-Behind:**
```python
def update_user(user_id, data):
    # Update cache immediately
    redis.setex(f"user:{user_id}", 3600, json.dumps(data))

    # Queue for async DB update
    redis.lpush("write_queue", json.dumps({"id": user_id, "data": data}))
```

#### Performance Best Practices

**Avoid blocking commands:**
- Use `SCAN` instead of `KEYS`
- Use `UNLINK` instead of `DEL` for large keys
- Avoid `FLUSHDB`/`FLUSHALL` in production

**Pipeline operations:**
```python
pipe = redis.pipeline()
pipe.set("key1", "value1")
pipe.set("key2", "value2")
pipe.execute()
```

**Connection pooling:**
```python
pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
redis_client = redis.Redis(connection_pool=pool)
```

#### Key Naming Conventions

**Hierarchical structure:**
```
object-type:id:field
user:1000:profile
session:abc123:data
cache:article:5000
```

**Namespacing:**
```
{environment}:{service}:{resource}:{id}
prod:api:user:1000
dev:worker:job:queue
```

---

## Data Format Standards

### JSON (JavaScript Object Notation)

**Specification:** RFC 8259
**URL:** https://tools.ietf.org/html/rfc8259
**Status:** IETF Standard (STD 90)
**Use Case:** API payloads, configuration, data exchange

#### Key Features

- Human-readable text format
- Language-independent
- Lightweight data interchange
- Native JavaScript support

#### Data Types

- **Object:** `{"key": "value"}`
- **Array:** `[1, 2, 3]`
- **String:** `"text"`
- **Number:** `123`, `45.67`
- **Boolean:** `true`, `false`
- **Null:** `null`

#### Best Practices

- Use UTF-8 encoding
- Keep structure flat when possible
- Use consistent naming (camelCase or snake_case)
- Validate against JSON Schema
- Avoid deeply nested structures

---

### JSON Schema

**Specification:** https://json-schema.org/
**Latest Version:** Draft 2020-12
**Status:** IETF Internet-Draft
**Use Case:** JSON validation, documentation, code generation

#### Purpose

- Validate JSON document structure
- Document expected format
- Enable code generation
- API contract definition

#### Example Schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://example.com/user.schema.json",
  "title": "User",
  "type": "object",
  "properties": {
    "id": {
      "type": "integer",
      "minimum": 1
    },
    "name": {
      "type": "string",
      "minLength": 1,
      "maxLength": 100
    },
    "email": {
      "type": "string",
      "format": "email"
    },
    "age": {
      "type": "integer",
      "minimum": 0,
      "maximum": 150
    }
  },
  "required": ["id", "name", "email"]
}
```

#### Integration

- OpenAPI uses JSON Schema for request/response validation
- Pydantic generates JSON Schema from Python models
- FastAPI automatically exposes JSON Schema in documentation

---

## Vector Search Standards

### HNSW (Hierarchical Navigable Small World)

**Original Paper:** "Efficient and robust approximate nearest neighbor search using Hierarchical Navigable Small World graphs"
**Authors:** Yu. A. Malkov, D. A. Yashunin
**Published:** arXiv:1603.09320 (2016)
**URL:** https://arxiv.org/abs/1603.09320

#### Overview

HNSW is a graph-based algorithm for approximate k-nearest neighbor (k-NN) search in high-dimensional vector spaces.

#### Key Characteristics

- **Fully graph-based:** No additional search structures needed
- **Multi-layer structure:** Hierarchical proximity graphs
- **Logarithmic complexity:** Scales efficiently even in high dimensions
- **Incremental construction:** Add elements one at a time
- **Parameter tuning:** Trade-off between speed and accuracy

#### Algorithm Properties

**Construction:**
- Elements inserted with exponentially decaying layer probability
- Each element connects to `M` nearest neighbors per layer
- Top layers have fewer elements (skip-list structure)

**Search:**
- Start from top layer
- Greedily navigate to nearest neighbors
- Descend layers when local minimum found
- Return k-nearest from bottom layer

#### Parameters

**M (max connections):**
- Default: 16
- Higher M = better recall, more memory
- Typical range: 5-48

**ef_construction (build quality):**
- Default: 64
- Higher value = better graph quality, slower build
- Typical range: 100-500

**ef_search (query quality):**
- Runtime parameter
- Higher value = better recall, slower search
- Typical range: 100-500

#### Performance

- **Search complexity:** O(log N) expected
- **Memory:** O(M * N)
- **Recall:** 95%+ achievable with proper parameters
- **Speed:** Orders of magnitude faster than brute force

#### Adoption

- **pgvector:** PostgreSQL extension
- **Qdrant:** Native HNSW implementation
- **FAISS:** Facebook's similarity search library
- **Milvus:** Vector database
- **Annoy:** Spotify's library (similar approach)

---

### Vector Similarity Metrics

**Reference:** Common standards across vector databases

#### Euclidean Distance (L2)

**Formula:** $d(p, q) = \sqrt{\sum_{i=1}^n (p_i - q_i)^2}$

**Properties:**
- Measures absolute distance between points
- Sensitive to magnitude
- Range: [0, ∞)
- Smaller = more similar

**Use Cases:**
- When magnitude matters
- Image embeddings
- Audio features

**SQL (pgvector):** `embedding <-> '[0.1, 0.2, ...]'`

---

#### Cosine Similarity / Cosine Distance

**Formula:** $similarity = \frac{p \cdot q}{||p|| \cdot ||q||}$

**Cosine Distance:** $distance = 1 - similarity$

**Properties:**
- Measures angle between vectors
- Magnitude-independent
- Range: [0, 2] for distance, [-1, 1] for similarity
- Smaller distance = more similar

**Use Cases:**
- Text embeddings (word2vec, BERT, GPT)
- Document similarity
- When direction matters more than magnitude

**SQL (pgvector):** `embedding <=> '[0.1, 0.2, ...]'`

**Most common for LLM embeddings**

---

#### Inner Product (Dot Product)

**Formula:** $p \cdot q = \sum_{i=1}^n p_i \times q_i$

**Properties:**
- Considers both angle and magnitude
- Not a true distance metric
- Range: (-∞, ∞)
- Higher = more similar

**Use Cases:**
- Maximum inner product search (MIPS)
- Recommendation systems
- When magnitude conveys importance

**SQL (pgvector):** `embedding <#> '[0.1, 0.2, ...]'` (negative inner product)

---

#### Metric Selection Guide

| Metric | Magnitude Sensitive | Normalized Required | Typical Use |
|--------|-------------------|-------------------|-------------|
| L2 Distance | Yes | No | Images, audio |
| Cosine Distance | No | No | Text, NLP |
| Inner Product | Yes | Yes | Recommendations |

**Best Practice:** Match metric to embedding model training
- OpenAI embeddings: Cosine similarity
- Sentence Transformers: Cosine similarity (default)
- Custom embeddings: Check model documentation

---

## Adoption & Industry Standards

### API Standards Adoption

- **OpenAPI:** Used by Google, Microsoft, AWS, IBM, Stripe, GitHub
- **REST Level 2:** Majority of public APIs (GitHub, Twitter, Stripe)
- **REST Level 3 (HATEOAS):** Less common (HAL, JSON:API formats)

### Query Language Adoption

- **Cypher/GQL:** Neo4j (primary), AWS Neptune, Memgraph, RedisGraph
- **SQL:** Universal relational database standard
- **PromQL:** Prometheus, Grafana, many observability platforms
- **Redis:** Used by Twitter, GitHub, Stack Overflow, Airbnb

### Vector Search Adoption

- **HNSW:** Dominant algorithm in production vector databases
- **Cosine Similarity:** Standard for text embeddings (OpenAI, Anthropic)
- **pgvector:** 15k+ GitHub stars, PostgreSQL ecosystem integration

---

## References & Further Reading

### Official Specifications

1. **OpenAPI 3.0.3:** https://spec.openapis.org/oas/v3.0.3.html
2. **ISO GQL:** https://www.iso.org/standard/76120.html
3. **RFC 8259 (JSON):** https://tools.ietf.org/html/rfc8259
4. **RFC 7231 (HTTP):** https://tools.ietf.org/html/rfc7231
5. **HNSW Paper:** https://arxiv.org/abs/1603.09320

### Official Documentation

1. **Neo4j Cypher Manual:** https://neo4j.com/docs/cypher-manual/current/
2. **openCypher:** https://opencypher.org/
3. **pgvector:** https://github.com/pgvector/pgvector
4. **Prometheus PromQL:** https://prometheus.io/docs/prometheus/latest/querying/
5. **Redis Commands:** https://redis.io/docs/latest/commands/
6. **OpenAPI Best Practices:** https://learn.openapis.org/best-practices.html

### Authoritative Articles

1. **Richardson Maturity Model:** https://martinfowler.com/articles/richardsonMaturityModel.html (Martin Fowler)
2. **JSON Schema:** https://json-schema.org/
3. **GQL Standard Overview:** https://www.gqlstandards.org/

---

**Last Updated:** 2025-10-06
**Research Quality:** Tier 1 (Official sources only)
**Next Review:** As standards evolve
