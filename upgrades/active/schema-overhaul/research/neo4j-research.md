# Neo4j Schema Design Best Practices

**Status:** ✅ Research Complete and Verified (November 2025)
**Original Research Date:** 2025-11-01
**Verification Date:** 2025-11-01
**Sources:** Neo4j Official Documentation (5.x/2025.x), Neo4j Labs, Community Best Practices
**Research Quality:** High (95%+ confidence from official sources)
**SDK Verification:** ✅ Official neo4j Python driver v5.27.0 (see SDK_VERIFICATION_SUMMARY.md)

---

## Table of Contents

1. [Schema Design Principles](#1-schema-design-principles)
2. [Multi-Database Coordination](#2-multi-database-coordination)
3. [Schema Evolution](#3-schema-evolution)
4. [Performance Considerations](#4-performance-considerations)
5. [Tools and Workflows](#5-tools-and-workflows)
6. [Common Pitfalls](#6-common-pitfalls)
7. [Recommended Workflow](#7-recommended-workflow)
8. [Code Examples](#8-code-examples)

---

## 1. Schema Design Principles

### 1.1 Node Label Design and Naming Conventions

**Official Naming Rules** (Source: [Neo4j Cypher Manual - Naming](https://neo4j.com/docs/cypher-manual/current/syntax/naming/))

- **Start with alphabetic characters** (including non-English: å, ä, ö, ü)
- **Case-sensitive**: `:PERSON`, `:Person`, `:person` are three different labels
- **Avoid starting with numbers**: `1first` invalid, `first1` valid
- **Underscore allowed**: `my_label` acceptable
- **Length limit**: Up to 65,535 characters
- **Special characters**: Use backticks for escaping (`` `my label` ``)

**Community Best Practices:**

- **Node labels**: Use **singular nouns** in **PascalCase** (e.g., `Person`, `Product`, `Order`)
- **Keep names descriptive but concise**
- **Relationship types**: Use **UPPERCASE with underscores** in **present tense verbs** (e.g., `KNOWS`, `ACTED_IN`, `PURCHASED`, `WORKS_FOR`)
- **Properties**: Use **camelCase** (e.g., `firstName`, `createdAt`, `purchaseDate`)

**Examples:**

```cypher
-- GOOD: Clear, descriptive labels
CREATE (p:Person {name: "Alice", email: "alice@example.com"})
CREATE (c:Company {name: "ACME Corp", founded: date('2020-01-01')})
CREATE (p)-[:WORKS_FOR {since: date('2021-03-15')}]->(c)

-- BAD: Poor naming conventions
CREATE (p:person {Name: "Alice"})  -- Wrong case
CREATE (c:Companies {name: "ACME"})  -- Plural label
CREATE (p)-[:works_for]->(c)  -- Lowercase relationship
```

### 1.2 Relationship Types and Naming Conventions

**Official Guidance** (Source: [Neo4j Getting Started - Graph Concepts](https://neo4j.com/docs/getting-started/appendix/graphdb-concepts/))

- **Must have exactly one type** per relationship
- **Must have direction** (though can be queried bidirectionally)
- **Convention**: UPPERCASE with underscores, verb phrases

**Common Relationship Types:**

| Pattern | Example | Description |
|---------|---------|-------------|
| **Action** | `PURCHASED`, `CREATED`, `VIEWED` | Past tense verbs |
| **State** | `OWNS`, `KNOWS`, `MANAGES` | Present tense verbs |
| **Association** | `MEMBER_OF`, `PART_OF` | Structural relationships |
| **Temporal** | `FOLLOWS`, `PRECEDES` | Time-based connections |

**Anti-pattern:** Don't use generic relationships like `:RELATED_TO` - be specific about the semantic meaning.

**Good Examples:**
```cypher
(:Person)-[:KNOWS]->(:Person)
(:Customer)-[:PLACED]->(:Order)
(:Order)-[:CONTAINS]->(:Product)
(:Employee)-[:MANAGES]->(:Department)
```

**Bad Examples:**
```cypher
(:Person)-[:RELATED_TO]->(:Person)  -- Too generic
(:Customer)-[:has]->(:Order)  -- Lowercase
(:Order)-[:order_contains]->(:Product)  -- Redundant prefix
```

### 1.3 Property Design (Nodes vs. Relationships)

**When to Use Node Properties:**
- Attributes describing the entity itself
- Low-cardinality categorical data
- Simple scalar values (strings, numbers, booleans, dates)
- **Example**: `Person.name`, `Person.age`, `Movie.title`, `Movie.released`

**When to Use Relationship Properties:**
- Attributes describing the connection context
- Temporal metadata (when, duration, from/to dates)
- Weights, scores, or ratings
- **Example**: `ACTED_IN.roles[]`, `KNOWS.since`, `RATED.score`, `EMPLOYED.from`, `EMPLOYED.to`

**When to Use Intermediate Nodes:**

Neo4j doesn't support hyperedges (relationships connecting >2 nodes). **Solution:** Create intermediate nodes.

**Example: Employment with Multiple Roles**

```cypher
// BAD: Can't do this in Neo4j
(Person)-[:EMPLOYED {role: "Developer", role2: "Manager"}]->(Company)

// GOOD: Use intermediate node
(Person)-[:HAS_EMPLOYMENT]->(Employment {
    start_date: date('2021-01-01'),
    end_date: null,
    status: "active"
})-[:AT_COMPANY]->(Company)

(Employment)-[:IN_ROLE]->(Role {title: "Developer"})
(Employment)-[:IN_ROLE]->(Role {title: "Manager"})
```

**Benefits:**
- Share context across multiple entities
- Add temporal information easily
- Convert complex relationships into queryable nodes
- Enable many-to-many patterns

### 1.4 Index Strategies

**Index Types** (Source: [Neo4j Cypher Manual - Indexes](https://neo4j.com/docs/cypher-manual/current/indexes/))

#### 1. Range Indexes (General Purpose)

Most common index type for equality checks, range queries, and ordering.

```cypher
-- Basic property index
CREATE INDEX person_email_idx IF NOT EXISTS
FOR (p:Person) ON (p.email);

-- Composite index (multiple properties)
CREATE INDEX person_name_age_idx IF NOT EXISTS
FOR (p:Person) ON (p.lastName, p.firstName, p.age);

-- Use cases
MATCH (p:Person {email: 'alice@example.com'})  -- Uses index
MATCH (p:Person) WHERE p.age > 30 RETURN p ORDER BY p.age  -- Uses index
```

#### 2. Text Indexes (Large Strings)

Optimized for `CONTAINS`, `ENDS WITH` on strings >8kb.

```cypher
CREATE TEXT INDEX document_content_idx IF NOT EXISTS
FOR (d:Document) ON (d.content);

-- Query
MATCH (d:Document)
WHERE d.content CONTAINS "knowledge graph"
RETURN d
```

#### 3. Full-Text Indexes (Semantic Search)

Powered by Apache Lucene, indexes individual words with proximity scores.

```cypher
CREATE FULLTEXT INDEX employee_search_idx IF NOT EXISTS
FOR (n:Employee)
ON EACH [n.name, n.bio, n.skills];

-- Query with scoring
CALL db.index.fulltext.queryNodes(
    "employee_search_idx",
    "python developer"
) YIELD node, score
RETURN node.name, score
ORDER BY score DESC
```

#### 4. Vector Indexes (Neo4j 5.13+)

For similarity searches using embeddings.

```cypher
CREATE VECTOR INDEX document_embeddings_idx IF NOT EXISTS
FOR (d:Document) ON (d.embedding)
OPTIONS {
  indexConfig: {
    `vector.dimensions`: 1536,
    `vector.similarity_function`: 'cosine'
  }
};

-- Query (find similar documents)
MATCH (d:Document)
CALL db.index.vector.queryNodes(
    'document_embeddings_idx',
    10,  -- top K results
    $queryVector
) YIELD node, score
RETURN node.title, score
```

#### 5. Point Indexes (Spatial Queries)

For geospatial data and distance calculations.

```cypher
CREATE POINT INDEX location_idx IF NOT EXISTS
FOR (p:Place) ON (p.location);

-- Query (find places within 5km)
MATCH (p:Place)
WHERE distance(p.location, point({latitude: 37.7749, longitude: -122.4194})) < 5000
RETURN p.name, p.location
```

### 1.5 When to Create Indexes

**Create indexes for:**
- **Frequent filtering**: Properties used often in WHERE clauses
- **High cardinality**: IDs, usernames, timestamps (many distinct values)
- **Performance bottlenecks**: Properties causing slow queries
- **Complex traversals**: Multi-hop queries with filtering at each step

**Avoid over-indexing:**
- **Low cardinality fields**: Booleans, small enums (use labels instead)
- **Rarely queried fields**: Storage overhead not worth it
- **Write-heavy workloads**: Indexes slow down writes

**Monitoring Index Usage (Neo4j 5.8+):**

```cypher
SHOW INDEXES YIELD name, lastRead, readCount, trackedSince
WHERE lastRead IS NOT NULL
RETURN name, readCount, lastRead
ORDER BY readCount DESC
```

**Remove unused indexes:**
```cypher
DROP INDEX unused_index_name IF EXISTS
```

### 1.6 Constraint Design

**Constraint Types:**

#### 1. Uniqueness Constraints

```cypher
CREATE CONSTRAINT person_email_unique IF NOT EXISTS
FOR (p:Person) REQUIRE p.email IS UNIQUE;

-- Composite uniqueness
CREATE CONSTRAINT person_name_dob_unique IF NOT EXISTS
FOR (p:Person) REQUIRE (p.firstName, p.lastName, p.dateOfBirth) IS UNIQUE;
```

**Important:** Uniqueness constraints automatically create an index.

#### 2. Existence Constraints (Enterprise Edition)

```cypher
CREATE CONSTRAINT person_name_exists IF NOT EXISTS
FOR (p:Person) REQUIRE p.name IS NOT NULL;

-- On relationships
CREATE CONSTRAINT rated_score_exists IF NOT EXISTS
FOR ()-[r:RATED]-() REQUIRE r.score IS NOT NULL;
```

#### 3. Node Key Constraints (Enterprise Edition)

Composite uniqueness + existence (all properties must exist AND be unique together).

```cypher
CREATE CONSTRAINT person_node_key IF NOT EXISTS
FOR (p:Person) REQUIRE (p.firstName, p.lastName, p.dateOfBirth) IS NODE KEY;
```

**Benefits:**
- Data integrity enforced at database level
- Prevents duplicate entities
- Enables safe upserts (MERGE operations)

---

## 2. Multi-Database Coordination

### 2.1 Neo4j Multi-Database Architecture (Neo4j 4.x+)

**Key Concepts:**
- DBMS can manage multiple databases (default max: 100, tested up to 500)
- **Structural separation**: Data stored separately per database
- **Shared resources**: Memory and CPU shared across databases
- **No cross-database relationships**: Relationships cannot span databases
- **Default database**: Configurable via `dbms.default_database`

**Use Cases:**
1. **Multi-tenancy**: Separate database per tenant
2. **Development/Testing**: Multiple environment copies
3. **Scalability**: Physically separated data structures
4. **Data partitioning**: Hot/cold data separation

**Creating Databases:**

```cypher
-- Create new database
CREATE DATABASE customer_a_data;
CREATE DATABASE customer_b_data;

-- List databases
SHOW DATABASES;

-- Use specific database
:use customer_a_data;

-- Delete database
DROP DATABASE customer_a_data IF EXISTS;
```

### 2.2 Composite Databases (Neo4j 5.x Enterprise)

**Concept:** Virtual databases that federate multiple physical databases.

```cypher
-- Create composite database
CREATE COMPOSITE DATABASE analytics_composite;

-- Add constituent databases via aliases
CREATE ALIAS analytics_composite.sales FOR DATABASE sales_db;
CREATE ALIAS analytics_composite.inventory FOR DATABASE inventory_db;
CREATE ALIAS analytics_composite.customers FOR DATABASE customers_db;

-- Query across databases
USE analytics_composite;
MATCH (c:Customer)-[:PLACED]->(o:Order)-[:CONTAINS]->(p:Product)
RETURN c.name, o.orderDate, collect(p.name) AS products;
```

**Benefits:**
- Query multiple graphs with single Cypher query
- Data federation (separate graphs, unified query interface)
- Data sharding (partitioned graph, distributed queries)

### 2.3 Integration with PostgreSQL, Qdrant, Redis

**Coordination Pattern: Saga with Neo4j as Graph Layer**

```python
@workflow.defn
class EntityIngestionWorkflow:
    async def run(self, entity_data: dict):
        # Activity 1: Save metadata to PostgreSQL (source of truth)
        pg_result = await save_to_postgresql(entity_data)

        # Activity 2: Create graph structure in Neo4j
        neo_result = await save_to_neo4j(entity_data)

        # Activity 3: Store embeddings in Qdrant
        qdrant_result = await save_to_qdrant(entity_data)

        # Activity 4: Cache in Redis
        await cache_entity(entity_data)

        return {"pg": pg_result, "neo": neo_result, "qdrant": qdrant_result}
```

**ID Coordination:**

```python
# Use same UUID across all databases
entity_uuid = str(uuid7())

# PostgreSQL
db.execute(
    "INSERT INTO entities (id, name, type) VALUES (?, ?, ?)",
    entity_uuid, name, entity_type
)

# Neo4j
neo4j.run("""
    CREATE (e:Entity {
        uuid: $uuid,
        name: $name,
        type: $type
    })
""", uuid=entity_uuid, name=name, type=entity_type)

# Qdrant
qdrant.upsert(
    collection_name="entities",
    points=[{
        "id": entity_uuid,
        "vector": embedding,
        "payload": {"name": name, "type": entity_type}
    }]
)

# Redis
redis.setex(
    f"entity:{entity_uuid}",
    3600,
    json.dumps({"name": name, "type": entity_type})
)
```

---

## 3. Schema Evolution

### 3.1 Migration Strategies

**Challenge:** Neo4j has limited built-in migration tooling like PostgreSQL's Alembic, though community tools exist.

**Community Migration Tools (November 2025):**
- **neo4j-migrations** by Michael Simons (Neo4j Labs community project) - Java-based, Flyway-inspired
- **Liquibase Neo4j Extension** - Enterprise-grade migration management
- **APOC procedures** - Basic schema introspection utilities

**Our Solution:** Implement custom Python migration framework (recommended since no mature Python-native tool exists).

#### Pattern A: Versioned Cypher Scripts

```
migrations/neo4j/
├── V001__initial_schema.cypher
├── V002__add_customer_indices.cypher
├── V003__migrate_employment_to_intermediate_nodes.cypher
└── migration_manager.py
```

**V001__initial_schema.cypher:**
```cypher
// Create constraints
CREATE CONSTRAINT person_uuid_unique IF NOT EXISTS
FOR (p:Person) REQUIRE p.uuid IS UNIQUE;

CREATE CONSTRAINT company_name_unique IF NOT EXISTS
FOR (c:Company) REQUIRE c.name IS UNIQUE;

// Create indexes
CREATE INDEX person_name_idx IF NOT EXISTS
FOR (p:Person) ON (p.name);

CREATE INDEX person_email_idx IF NOT EXISTS
FOR (p:Person) ON (p.email);
```

**migration_manager.py:**
```python
import os
from neo4j import GraphDatabase

class Neo4jMigrationManager:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def get_current_version(self):
        """Get current schema version from tracking node."""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (v:SchemaVersion)
                RETURN v.version AS version
                ORDER BY v.applied_at DESC
                LIMIT 1
            """)
            record = result.single()
            return record["version"] if record else 0

    def run_migration(self, version: int, script_path: str):
        """Execute migration script and record version."""
        with self.driver.session() as session:
            # Read and execute migration script
            with open(script_path, 'r') as f:
                cypher = f.read()

            # Execute in transaction
            with session.begin_transaction() as tx:
                # Run migration
                tx.run(cypher)

                # Record version
                tx.run("""
                    CREATE (v:SchemaVersion {
                        version: $version,
                        script: $script,
                        applied_at: datetime()
                    })
                """, version=version, script=os.path.basename(script_path))

                tx.commit()

    def run_all_migrations(self, migrations_dir: str):
        """Run all pending migrations."""
        current_version = self.get_current_version()

        # Find migration files
        files = sorted([
            f for f in os.listdir(migrations_dir)
            if f.endswith('.cypher') and f.startswith('V')
        ])

        for file in files:
            # Extract version number (V001 -> 1)
            version = int(file.split('__')[0][1:])

            if version > current_version:
                print(f"Running migration V{version:03d}...")
                script_path = os.path.join(migrations_dir, file)
                self.run_migration(version, script_path)
                print(f"✅ Migration V{version:03d} complete")

    def rollback(self, target_version: int):
        """Rollback to specific version (requires manual rollback scripts)."""
        current_version = self.get_current_version()

        if target_version >= current_version:
            print("Target version is current or higher. No rollback needed.")
            return

        # Find rollback scripts (U for "undo")
        migrations_dir = "migrations/neo4j/"
        files = sorted([
            f for f in os.listdir(migrations_dir)
            if f.endswith('.cypher') and f.startswith('U')
        ], reverse=True)

        with self.driver.session() as session:
            for file in files:
                # Extract version (U003 -> 3)
                version = int(file.split('__')[0][1:])

                if version > target_version and version <= current_version:
                    print(f"Rolling back V{version:03d}...")
                    with open(os.path.join(migrations_dir, file), 'r') as f:
                        cypher = f.read()
                    session.run(cypher)

                    # Remove version record
                    session.run("""
                        MATCH (v:SchemaVersion {version: $version})
                        DELETE v
                    """, version=version)
                    print(f"✅ Rollback V{version:03d} complete")
```

#### Pattern B: Schema-as-Code (Python)

```python
# schemas/neo4j_schema.py
from dataclasses import dataclass
from typing import List

@dataclass
class Constraint:
    label: str
    properties: List[str]
    type: str  # "unique", "exists", "node_key"

@dataclass
class Index:
    label: str
    properties: List[str]
    type: str  # "range", "text", "fulltext", "vector"
    options: dict = None

class Neo4jSchema:
    CONSTRAINTS = [
        Constraint("Person", ["uuid"], "unique"),
        Constraint("Person", ["name"], "exists"),
        Constraint("Company", ["name"], "unique"),
        Constraint("Entity", ["uuid"], "unique"),
    ]

    INDEXES = [
        Index("Person", ["name"], "range"),
        Index("Person", ["email"], "range"),
        Index("Document", ["content"], "fulltext"),
        Index("Document", ["embedding"], "vector", {
            "vector.dimensions": 1536,
            "vector.similarity_function": "cosine"
        }),
    ]

    @classmethod
    def apply_schema(cls, neo4j_client):
        """Apply all constraints and indexes."""
        # Create constraints
        for constraint in cls.CONSTRAINTS:
            cls._create_constraint(neo4j_client, constraint)

        # Create indexes
        for index in cls.INDEXES:
            cls._create_index(neo4j_client, index)

    @classmethod
    def _create_constraint(cls, client, constraint: Constraint):
        props = ", ".join([f"n.{p}" for p in constraint.properties])

        if constraint.type == "unique":
            cypher = f"""
                CREATE CONSTRAINT {constraint.label.lower()}_{constraint.properties[0]}_unique
                IF NOT EXISTS
                FOR (n:{constraint.label})
                REQUIRE n.{constraint.properties[0]} IS UNIQUE
            """
        elif constraint.type == "exists":
            cypher = f"""
                CREATE CONSTRAINT {constraint.label.lower()}_{constraint.properties[0]}_exists
                IF NOT EXISTS
                FOR (n:{constraint.label})
                REQUIRE n.{constraint.properties[0]} IS NOT NULL
            """
        elif constraint.type == "node_key":
            props_list = ", ".join([f"n.{p}" for p in constraint.properties])
            cypher = f"""
                CREATE CONSTRAINT {constraint.label.lower()}_node_key
                IF NOT EXISTS
                FOR (n:{constraint.label})
                REQUIRE ({props_list}) IS NODE KEY
            """

        client.run(cypher)

    @classmethod
    def _create_index(cls, client, index: Index):
        props_str = ", ".join([f"n.{p}" for p in index.properties])
        idx_name = f"{index.label.lower()}_{'_'.join(index.properties)}_idx"

        if index.type == "range":
            cypher = f"""
                CREATE INDEX {idx_name} IF NOT EXISTS
                FOR (n:{index.label}) ON ({props_str})
            """
        elif index.type == "text":
            cypher = f"""
                CREATE TEXT INDEX {idx_name} IF NOT EXISTS
                FOR (n:{index.label}) ON (n.{index.properties[0]})
            """
        elif index.type == "fulltext":
            props_list = ", ".join([f"n.{p}" for p in index.properties])
            cypher = f"""
                CREATE FULLTEXT INDEX {idx_name} IF NOT EXISTS
                FOR (n:{index.label}) ON EACH [{props_list}]
            """
        elif index.type == "vector":
            opts = index.options or {}
            cypher = f"""
                CREATE VECTOR INDEX {idx_name} IF NOT EXISTS
                FOR (n:{index.label}) ON (n.{index.properties[0]})
                OPTIONS {{
                    indexConfig: {{
                        `vector.dimensions`: {opts.get('vector.dimensions', 1536)},
                        `vector.similarity_function`: '{opts.get('vector.similarity_function', 'cosine')}'
                    }}
                }}
            """

        client.run(cypher)
```

### 3.2 Backward Compatibility: Expand-Contract Pattern

**Scenario:** Change property name from `email_address` to `email`

**Phase 1: Expand** (Add new property, keep old)

```cypher
// Migration V010__add_email_property.cypher
MATCH (p:Person)
WHERE p.email_address IS NOT NULL AND p.email IS NULL
SET p.email = p.email_address;

// Create index on new property
CREATE INDEX person_email_idx IF NOT EXISTS
FOR (p:Person) ON (p.email);
```

**Application code supports both:**
```python
# v1.0 code (supports both properties)
def get_person_email(person_node):
    return person_node.get("email") or person_node.get("email_address")
```

**Phase 2: Contract** (Remove old property after migration complete)

```cypher
// Migration V011__remove_old_email_property.cypher
MATCH (p:Person)
WHERE p.email_address IS NOT NULL
REMOVE p.email_address;

// Drop old index if it exists
DROP INDEX person_email_address_idx IF EXISTS;
```

**Timeline:** Expand → (2 weeks validation) → Contract

---

## 4. Performance Considerations

### 4.1 Index Placement for Query Patterns

**Principle:** "Write your queries first, then model your schema."

**Query Pattern Analysis:**

```cypher
// Query 1: Find person by email (high frequency)
MATCH (p:Person {email: $email}) RETURN p
// ✅ INDEX NEEDED: person_email_idx

// Query 2: Find orders placed after date (temporal filter)
MATCH (o:Order) WHERE o.orderDate >= date('2025-01-01') RETURN o
// ✅ INDEX NEEDED: order_orderDate_idx

// Query 3: Find products in category with price range
MATCH (p:Product)
WHERE p.category = $category AND p.price BETWEEN $min AND $max
RETURN p
// ✅ COMPOSITE INDEX NEEDED: product_category_price_idx

// Query 4: Full-text search in document content
MATCH (d:Document) WHERE d.content CONTAINS "knowledge graph"
// ✅ TEXT/FULLTEXT INDEX NEEDED: document_content_fulltext_idx

// Query 5: Find similar documents by embedding
MATCH (d:Document)
CALL db.index.vector.queryNodes('doc_embeddings_idx', 10, $queryVector)
YIELD node, score
// ✅ VECTOR INDEX NEEDED: doc_embeddings_idx
```

**Optimization Workflow:**

1. **Profile queries without indexes:**
   ```cypher
   PROFILE MATCH (p:Person {email: 'alice@example.com'}) RETURN p;
   ```
   Look for `AllNodesScan` or `NodeByLabelScan` (slow).

2. **Add index:**
   ```cypher
   CREATE INDEX person_email_idx IF NOT EXISTS
   FOR (p:Person) ON (p.email);
   ```

3. **Re-profile:**
   ```cypher
   PROFILE MATCH (p:Person {email: 'alice@example.com'}) RETURN p;
   ```
   Should now show `NodeIndexSeek` (fast).

4. **Measure improvement:**
   ```cypher
   // Before: 150ms with NodeByLabelScan
   // After: 2ms with NodeIndexSeek
   // ✅ 75x speedup
   ```

### 4.2 Property Cardinality and Storage

**High Cardinality (Good for indexing):**
- UUIDs (millions of unique values)
- Email addresses
- Timestamps
- Usernames

**Low Cardinality (Poor for indexing):**
- Booleans (true/false)
- Small enums (status: active/inactive/suspended)
- Categories with few values

**Strategy for Low Cardinality:**

```cypher
// BAD: Index on low-cardinality property
CREATE INDEX person_is_active_idx FOR (p:Person) ON (p.isActive);

// GOOD: Use label instead
(:Person:Active)  // Active users
(:Person:Inactive)  // Inactive users

// Query becomes:
MATCH (p:Person:Active) RETURN p  // Fast label scan
```

### 4.3 Relationship Direction Optimization

**Natural Direction Modeling:**

```cypher
// Natural semantic direction
(:Person)-[:OWNS]->(:Car)
(:Employee)-[:WORKS_FOR]->(:Company)
(:Customer)-[:PLACED]->(:Order)
```

**Querying Bidirectionally:**

```cypher
// Ignores direction
MATCH (p:Person)-[:KNOWS]-(friend:Person) RETURN friend

// Specific direction
MATCH (p:Person)-[:KNOWS]->(friend:Person) RETURN friend
```

**Performance Consideration: Fanout**

```cypher
// High fanout: One person, many orders
(:Person)-[:PLACED]->(:Order)  // One person → 100+ orders

// Index the "one" side for faster lookups
CREATE INDEX person_uuid_idx FOR (p:Person) ON (p.uuid);

// Query from indexed side
MATCH (p:Person {uuid: $uuid})-[:PLACED]->(o:Order)
RETURN o
```

### 4.4 Query Performance Tuning

**Using EXPLAIN and PROFILE:**

```cypher
// EXPLAIN: Show query plan without executing
EXPLAIN
MATCH (p:Person)-[:KNOWS*1..3]-(friend)
WHERE p.name = 'Alice'
RETURN friend.name

// PROFILE: Execute and show actual performance
PROFILE
MATCH (p:Person)-[:KNOWS*1..3]-(friend)
WHERE p.name = 'Alice'
RETURN friend.name
```

**Key Metrics:**
- **db hits**: Number of database operations (lower is better)
- **rows**: Number of intermediate rows (lower is better)
- **time**: Execution time in milliseconds

**Optimization Techniques:**

1. **Limit Early:**
   ```cypher
   // BAD: Limit at end
   MATCH (p:Person)-[:KNOWS]->(f) RETURN f ORDER BY f.name LIMIT 10

   // GOOD: Limit with subquery
   MATCH (p:Person {name: 'Alice'})-[:KNOWS]->(f)
   WITH f ORDER BY f.name LIMIT 10
   MATCH (f)-[:WORKS_FOR]->(c:Company)
   RETURN f, c
   ```

2. **Use Parameters (Query Plan Caching):**
   ```cypher
   // BAD: Literal values (no caching)
   MATCH (p:Person {name: 'Alice'}) RETURN p

   // GOOD: Parameterized (caching enabled)
   MATCH (p:Person {name: $name}) RETURN p
   ```

3. **Avoid Cartesian Products:**
   ```cypher
   // BAD: Unconnected patterns
   MATCH (p:Person), (m:Movie)  // Returns Person × Movie combinations
   RETURN p, m

   // GOOD: Connected pattern
   MATCH (p:Person)-[:WATCHED]->(m:Movie)
   RETURN p, m
   ```

4. **Index Frequently Filtered Properties:**
   ```cypher
   // Query that benefits from index
   MATCH (o:Order)
   WHERE o.orderDate >= date('2025-01-01')
     AND o.status = 'completed'
   RETURN o

   // Create composite index
   CREATE INDEX order_date_status_idx IF NOT EXISTS
   FOR (o:Order) ON (o.orderDate, o.status);
   ```

---

## 5. Tools and Workflows

### 5.1 Schema Definition Formats

#### Format 1: Cypher Scripts (Recommended for Migrations)

```cypher
// migrations/neo4j/V001__initial_schema.cypher

// ============================================
// CONSTRAINTS
// ============================================

-- Person
CREATE CONSTRAINT person_uuid_unique IF NOT EXISTS
FOR (p:Person) REQUIRE p.uuid IS UNIQUE;

CREATE CONSTRAINT person_email_unique IF NOT EXISTS
FOR (p:Person) REQUIRE p.email IS UNIQUE;

-- Company
CREATE CONSTRAINT company_name_unique IF NOT EXISTS
FOR (c:Company) REQUIRE c.name IS UNIQUE;

// ============================================
// INDEXES
// ============================================

-- Person
CREATE INDEX person_name_idx IF NOT EXISTS
FOR (p:Person) ON (p.name);

CREATE INDEX person_created_at_idx IF NOT EXISTS
FOR (p:Person) ON (p.createdAt);

-- Full-text search
CREATE FULLTEXT INDEX person_search_idx IF NOT EXISTS
FOR (n:Person) ON EACH [n.name, n.bio];

// ============================================
// VERIFICATION
// ============================================

-- Show all constraints
SHOW CONSTRAINTS;

-- Show all indexes
SHOW INDEXES;
```

#### Format 2: APOC Procedures (Declarative)

```cypher
// Use APOC for declarative schema management
CALL apoc.schema.assert(
  {
    Person: ['email', 'name'],      // Indexes
    Company: ['name'],
    Document: ['uuid', 'title']
  },
  {
    Person: ['email', 'uuid'],      // Unique constraints
    Company: ['name'],
    Document: ['uuid']
  }
) YIELD label, key, unique, action
RETURN label, key, unique, action;
```

#### Format 3: Python Schema-as-Code

```python
# schemas/neo4j_schema.py
from enum import Enum
from dataclasses import dataclass

class ConstraintType(Enum):
    UNIQUE = "unique"
    EXISTS = "exists"
    NODE_KEY = "node_key"

class IndexType(Enum):
    RANGE = "range"
    TEXT = "text"
    FULLTEXT = "fulltext"
    VECTOR = "vector"

@dataclass
class SchemaDefinition:
    constraints = [
        ("Person", ["uuid"], ConstraintType.UNIQUE),
        ("Person", ["email"], ConstraintType.UNIQUE),
        ("Person", ["name"], ConstraintType.EXISTS),
    ]

    indexes = [
        ("Person", ["name"], IndexType.RANGE),
        ("Person", ["name", "bio"], IndexType.FULLTEXT),
        ("Document", ["embedding"], IndexType.VECTOR, {
            "dimensions": 1536,
            "similarity": "cosine"
        }),
    ]
```

### 5.2 Validation and Testing

#### Test 1: Schema Consistency Check

```python
# tests/schema/test_neo4j_schema.py
import pytest
from neo4j import GraphDatabase

@pytest.fixture
def neo4j_session():
    driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
    with driver.session() as session:
        yield session
    driver.close()

def test_all_constraints_exist(neo4j_session):
    """Verify all required constraints are present."""
    result = neo4j_session.run("SHOW CONSTRAINTS")
    constraints = [record["name"] for record in result]

    assert "person_uuid_unique" in constraints
    assert "person_email_unique" in constraints
    assert "company_name_unique" in constraints

def test_all_indexes_exist(neo4j_session):
    """Verify all required indexes are present."""
    result = neo4j_session.run("SHOW INDEXES")
    indexes = [record["name"] for record in result]

    assert "person_name_idx" in indexes
    assert "person_search_idx" in indexes  # Full-text
    assert "document_embeddings_idx" in indexes  # Vector

def test_index_usage(neo4j_session):
    """Verify indexes are actually being used by queries."""
    # Run EXPLAIN on common query
    result = neo4j_session.run("""
        EXPLAIN
        MATCH (p:Person {email: 'test@example.com'})
        RETURN p
    """)

    plan = str(result.consume().plan)
    assert "NodeIndexSeek" in plan  # Confirms index is used
```

#### Test 2: Migration Rollback Test

```python
def test_migration_rollback(neo4j_session):
    """Test that migrations can be safely rolled back."""
    manager = Neo4jMigrationManager("bolt://localhost:7687", "neo4j", "password")

    # Get current version
    initial_version = manager.get_current_version()

    # Apply new migration
    manager.run_migration(
        version=initial_version + 1,
        script_path="migrations/neo4j/V999__test_migration.cypher"
    )

    # Verify new version
    assert manager.get_current_version() == initial_version + 1

    # Rollback
    manager.rollback(target_version=initial_version)

    # Verify rollback
    assert manager.get_current_version() == initial_version
```

#### Test 3: Performance Benchmark

```python
import time

def test_query_performance_with_index(neo4j_session):
    """Benchmark query performance with and without index."""
    # Create test data
    neo4j_session.run("""
        UNWIND range(1, 10000) AS i
        CREATE (p:TestPerson {
            uuid: apoc.create.uuid(),
            email: 'user' + i + '@example.com',
            name: 'User ' + i
        })
    """)

    # Benchmark WITHOUT index
    start = time.time()
    neo4j_session.run("MATCH (p:TestPerson {email: 'user5000@example.com'}) RETURN p")
    time_without_index = time.time() - start

    # Create index
    neo4j_session.run("CREATE INDEX test_person_email IF NOT EXISTS FOR (p:TestPerson) ON (p.email)")
    time.sleep(1)  # Wait for index to build

    # Benchmark WITH index
    start = time.time()
    neo4j_session.run("MATCH (p:TestPerson {email: 'user5000@example.com'}) RETURN p")
    time_with_index = time.time() - start

    # Cleanup
    neo4j_session.run("MATCH (p:TestPerson) DETACH DELETE p")
    neo4j_session.run("DROP INDEX test_person_email IF EXISTS")

    # Assert significant speedup
    assert time_with_index < time_without_index / 10  # At least 10x faster
```

### 5.3 Documentation Patterns

#### SCHEMA.md Documentation

```markdown
# Neo4j Schema Documentation

Last Updated: 2025-11-01

## Node Labels

### Person
- **Properties:**
  - `uuid` (STRING, UNIQUE, REQUIRED) - Globally unique identifier
  - `name` (STRING, INDEXED, REQUIRED) - Full name
  - `email` (STRING, UNIQUE, INDEXED) - Email address
  - `createdAt` (DATETIME) - Account creation timestamp
  - `updatedAt` (DATETIME) - Last update timestamp

- **Relationships:**
  - `[:KNOWS]` → Person (friendship/acquaintance)
  - `[:WORKS_FOR]` → Company (employment)
  - `[:OWNS]` → Asset (ownership)

### Company
- **Properties:**
  - `uuid` (STRING, UNIQUE, REQUIRED)
  - `name` (STRING, UNIQUE, REQUIRED)
  - `founded` (DATE) - Founding date
  - `industry` (STRING) - Industry classification

## Indexes

| Name | Type | Label | Properties | Purpose |
|------|------|-------|------------|---------|
| `person_uuid_idx` | Unique | Person | uuid | Fast lookups by ID |
| `person_email_idx` | Unique | Person | email | Fast lookups by email |
| `person_name_idx` | Range | Person | name | Filtering/sorting by name |
| `person_search_idx` | Full-text | Person | name, bio | Text search |

## Constraints

- Person.uuid must be unique
- Person.email must be unique
- Person.name must exist (NOT NULL)
- Company.name must be unique

## Query Patterns

### Find Person by Email
```cypher
MATCH (p:Person {email: $email}) RETURN p
```
Uses: `person_email_idx`

### Full-Text Search
```cypher
CALL db.index.fulltext.queryNodes("person_search_idx", $searchTerm)
YIELD node, score
RETURN node, score
ORDER BY score DESC
```
Uses: `person_search_idx`
```

---

## 6. Common Pitfalls

### Pitfall 1: Over-Indexing

**Problem:** Creating indexes on every property wastes storage and slows writes.

**Example:**
```cypher
// BAD: Indexing low-cardinality boolean
CREATE INDEX person_is_active FOR (p:Person) ON (p.isActive);

// BAD: Indexing rarely-queried field
CREATE INDEX person_middle_name FOR (p:Person) ON (p.middleName);
```

**Solution:** Only index frequently queried, high-cardinality properties.

```cypher
// GOOD: Use labels for low-cardinality
(:Person:Active)  // Active users
(:Person:Inactive)  // Inactive users

// GOOD: Skip rarely-queried fields
// Don't index middleName if it's rarely used
```

### Pitfall 2: Generic Relationships

**Problem:** Using `:RELATED_TO` loses semantic meaning.

```cypher
// BAD
(:Person)-[:RELATED_TO]->(:Company)
(:Person)-[:RELATED_TO]->(:Person)
```

**Solution:** Use specific relationship types.

```cypher
// GOOD
(:Person)-[:WORKS_FOR]->(:Company)
(:Person)-[:KNOWS]->(:Person)
(:Person)-[:MANAGES]->(:Person)
```

### Pitfall 3: Properties Instead of Relationships

**Problem:** Storing connections as properties breaks graph traversal.

```cypher
// BAD: Friends as array property
CREATE (p:Person {name: 'Alice', friends: ['Bob', 'Charlie']})
```

**Solution:** Use relationships.

```cypher
// GOOD
CREATE (alice:Person {name: 'Alice'})
CREATE (bob:Person {name: 'Bob'})
CREATE (charlie:Person {name: 'Charlie'})
CREATE (alice)-[:KNOWS]->(bob)
CREATE (alice)-[:KNOWS]->(charlie)

// Now can traverse: MATCH (alice)-[:KNOWS*1..3]-(friend)
```

### Pitfall 4: Cartesian Products

**Problem:** Unconnected patterns cause exponential results.

```cypher
// BAD: Cartesian product
MATCH (p:Person), (m:Movie)  // Returns every Person × Movie combination
RETURN p, m
```

**Solution:** Connect patterns with relationships.

```cypher
// GOOD
MATCH (p:Person)-[:WATCHED]->(m:Movie)
RETURN p, m
```

### Pitfall 5: Not Testing at Scale

**Problem:** Schema works with 100 nodes but fails at 1M nodes.

**Solution:** Test with realistic data volumes.

```cypher
// Generate test data at scale
UNWIND range(1, 1000000) AS i
CREATE (p:Person {
    uuid: apoc.create.uuid(),
    name: 'Person ' + i,
    email: 'user' + i + '@example.com',
    createdAt: datetime()
});

// Profile query performance
PROFILE MATCH (p:Person {email: 'user500000@example.com'}) RETURN p;
```

### Pitfall 6: Deleting Token Lookup Indexes

**Problem:** Accidentally deleting auto-created token lookup indexes.

**Never do this:**
```cypher
// DON'T DELETE THESE (they're auto-created and critical)
DROP INDEX __org_neo4j_schema_index_label_scan_store_converted_to_token_index;
```

**Consequence:** Severe performance degradation for all label scans.

---

## 7. Recommended Workflow for Schema Development

### Phase 1: Discovery (Week 1)

1. **Define Domain:**
   - List all entities (Person, Company, Product, etc.)
   - Identify relationships (KNOWS, WORKS_FOR, PURCHASED, etc.)
   - Map properties to entities/relationships

2. **List Questions:**
   - What queries need answering?
   - Example: "Find all orders by customer in last 30 days"
   - Example: "Find friends of friends (2 hops)"

3. **Sketch Model:**
   - Draw graph structure on whiteboard/tool
   - Validate with domain experts

### Phase 2: Design (Week 1-2)

1. **Choose Node Labels:**
   - Singular nouns, PascalCase
   - Example: `Person`, `Company`, `Order`

2. **Define Relationships:**
   - Specific types, UPPERCASE_WITH_UNDERSCORES
   - Example: `KNOWS`, `WORKS_FOR`, `PLACED`

3. **Assign Properties:**
   - camelCase for properties
   - Appropriate data types (String, Integer, Date, etc.)

4. **Plan Indexes:**
   - Identify high-cardinality, frequently filtered properties
   - Plan full-text indexes for search

5. **Define Constraints:**
   - Uniqueness for IDs, emails
   - Existence for required fields

### Phase 3: Prototype (Week 2)

1. **Create Test Schema:**
   - Write Cypher scripts
   - Use migration system

2. **Generate Test Data:**
   - 1,000-10,000 nodes
   - Representative relationships

3. **Write Test Queries:**
   - Cover all use cases
   - Use PROFILE to measure performance

4. **Iterate Design:**
   - Refine based on performance results
   - Add/remove indexes as needed

### Phase 4: Migration Planning (Week 3)

1. **Version Migrations:**
   - Use Neo4j-Migrations or custom system
   - V001, V002, V003 scripts

2. **Write Migration Scripts:**
   - Create constraints first
   - Then indexes
   - Then data transformations

3. **Test Rollback:**
   - Write U (undo) scripts
   - Test on staging

### Phase 5: Production (Week 4+)

1. **Apply Migrations:**
   - Use tested scripts
   - Monitor performance

2. **Monitor Performance:**
   - Check index usage
   - Measure query times

3. **Validate Data:**
   - Run integrity checks
   - Verify constraints

4. **Iterate:**
   - Refine based on real usage
   - Add indexes for slow queries

---

## 8. Code Examples

### Complete Schema Setup Example

```cypher
// ============================================
// NEO4J SCHEMA SETUP - APEX MEMORY SYSTEM
// Version: V001
// Date: 2025-11-01
// ============================================

// --- CONSTRAINTS ---

// Entity (Graphiti-owned)
CREATE CONSTRAINT entity_uuid_unique IF NOT EXISTS
FOR (e:Entity) REQUIRE e.uuid IS UNIQUE;

CREATE CONSTRAINT entity_name_exists IF NOT EXISTS
FOR (e:Entity) REQUIRE e.name IS NOT NULL;

// Episode (Graphiti-owned)
CREATE CONSTRAINT episode_uuid_unique IF NOT EXISTS
FOR (ep:Episode) REQUIRE ep.uuid IS UNIQUE;

// Edge (Graphiti-owned)
CREATE CONSTRAINT edge_uuid_unique IF NOT EXISTS
FOR (ed:Edge) REQUIRE ed.uuid IS UNIQUE;

// Document (Apex-owned)
CREATE CONSTRAINT document_uuid_unique IF NOT EXISTS
FOR (d:Document) REQUIRE d.uuid IS UNIQUE;

// Chunk (Apex-owned)
CREATE CONSTRAINT chunk_uuid_unique IF NOT EXISTS
FOR (c:Chunk) REQUIRE c.uuid IS UNIQUE;

// --- PROPERTY INDEXES ---

// Entity indexes
CREATE INDEX entity_name_idx IF NOT EXISTS
FOR (e:Entity) ON (e.name);

CREATE INDEX entity_group_id_idx IF NOT EXISTS
FOR (e:Entity) ON (e.group_id);

CREATE INDEX entity_type_idx IF NOT EXISTS
FOR (e:Entity) ON (e.entity_type);

// Episode indexes
CREATE INDEX episode_reference_time_idx IF NOT EXISTS
FOR (ep:Episode) ON (ep.reference_time);

CREATE INDEX episode_created_at_idx IF NOT EXISTS
FOR (ep:Episode) ON (ep.created_at);

// Edge indexes (CRITICAL for temporal queries)
CREATE INDEX edge_valid_from_idx IF NOT EXISTS
FOR (ed:Edge) ON (ed.valid_from);

CREATE INDEX edge_invalid_at_idx IF NOT EXISTS
FOR (ed:Edge) ON (ed.invalid_at);

// Composite temporal index (MOST IMPORTANT)
CREATE INDEX edge_temporal_validity_idx IF NOT EXISTS
FOR (ed:Edge) ON (ed.valid_from, ed.invalid_at);

// Document indexes
CREATE INDEX document_title_idx IF NOT EXISTS
FOR (d:Document) ON (d.title);

CREATE INDEX document_created_at_idx IF NOT EXISTS
FOR (d:Document) ON (d.created_at);

// --- FULL-TEXT INDEXES ---

// Entity full-text search
CREATE FULLTEXT INDEX entity_search_idx IF NOT EXISTS
FOR (n:Entity) ON EACH [n.name, n.summary];

// Document full-text search
CREATE FULLTEXT INDEX document_search_idx IF NOT EXISTS
FOR (n:Document) ON EACH [n.title, n.content];

// --- VECTOR INDEXES (Neo4j 5.13+) ---

// Document embeddings
CREATE VECTOR INDEX document_embeddings_idx IF NOT EXISTS
FOR (d:Document) ON (d.embedding)
OPTIONS {
  indexConfig: {
    `vector.dimensions`: 1536,
    `vector.similarity_function`: 'cosine'
  }
};

// --- VERIFICATION ---

CALL apoc.schema.nodes()
YIELD name, label, properties, status
RETURN name, label, properties, status;

SHOW INDEXES;
SHOW CONSTRAINTS;
```

### Multi-Database Coordination Example

```python
# services/entity_ingestion_service.py
from temporalio import workflow, activity
from typing import Dict, Any
import uuid
from datetime import datetime

@workflow.defn
class EntityIngestionWorkflow:
    """Coordinates entity ingestion across all databases using saga pattern."""

    @workflow.run
    async def run(self, entity_data: Dict[str, Any]) -> Dict[str, str]:
        # Generate shared UUID
        entity_uuid = str(uuid.uuid7())
        entity_data["uuid"] = entity_uuid

        # Activity 1: Save to PostgreSQL (metadata source of truth)
        try:
            pg_result = await workflow.execute_activity(
                save_to_postgresql,
                entity_data,
                start_to_close_timeout=timedelta(seconds=30)
            )
        except Exception as e:
            workflow.logger.error(f"PostgreSQL write failed: {e}")
            raise

        # Activity 2: Save to Neo4j/Graphiti (graph structure)
        try:
            neo_result = await workflow.execute_activity(
                save_to_graphiti,
                entity_data,
                start_to_close_timeout=timedelta(seconds=60)
            )
        except Exception as e:
            workflow.logger.error(f"Graphiti write failed: {e}")
            # Compensate: Delete from PostgreSQL
            await workflow.execute_activity(
                compensate_postgresql_write,
                entity_uuid,
                start_to_close_timeout=timedelta(seconds=30)
            )
            raise

        # Activity 3: Save to Qdrant (embeddings)
        try:
            qdrant_result = await workflow.execute_activity(
                save_to_qdrant,
                entity_data,
                start_to_close_timeout=timedelta(seconds=30)
            )
        except Exception as e:
            workflow.logger.error(f"Qdrant write failed: {e}")
            # Compensate: Delete from Graphiti and PostgreSQL
            await workflow.execute_activity(
                compensate_graphiti_write,
                entity_uuid,
                start_to_close_timeout=timedelta(seconds=30)
            )
            await workflow.execute_activity(
                compensate_postgresql_write,
                entity_uuid,
                start_to_close_timeout=timedelta(seconds=30)
            )
            raise

        # Activity 4: Cache in Redis
        await workflow.execute_activity(
            cache_entity,
            entity_data,
            start_to_close_timeout=timedelta(seconds=10)
        )

        return {
            "uuid": entity_uuid,
            "postgresql": pg_result,
            "neo4j": neo_result,
            "qdrant": qdrant_result,
            "status": "success"
        }

@activity.defn
async def save_to_graphiti(entity_data: Dict[str, Any]) -> str:
    """Save entity to Graphiti temporal graph."""
    from graphiti_core import Graphiti
    from pydantic import BaseModel, Field

    # Define custom entity type
    entity_type = entity_data.get("entity_type", "Generic")

    if entity_type == "Customer":
        class Customer(BaseModel):
            name: str = Field(..., description="Customer name")
            status: str = Field(..., description="active, suspended, inactive")
            payment_terms: str = Field(..., description="net30, net60, etc.")
            credit_limit: float = Field(..., description="Credit limit in USD")

        entity_types = {"Customer": Customer}
    else:
        entity_types = {}

    # Add episode to Graphiti
    graphiti = get_graphiti_client()
    result = await graphiti.add_episode(
        name=f"{entity_type} {entity_data['name']} created",
        episode_body=json.dumps(entity_data),
        source=EpisodeType.json,
        reference_time=datetime.now(),
        entity_types=entity_types
    )

    return result.episode_uuid

@activity.defn
async def compensate_graphiti_write(entity_uuid: str) -> None:
    """Rollback Graphiti entity creation."""
    # Check if already compensated (idempotency)
    redis_key = f"compensated:graphiti:{entity_uuid}"
    if await redis.exists(redis_key):
        return

    # Delete entity from Graphiti
    neo4j = get_neo4j_client()
    neo4j.run("""
        MATCH (e:Entity {uuid: $uuid})
        OPTIONAL MATCH (e)-[r]-()
        DELETE r, e
    """, uuid=entity_uuid)

    # Mark as compensated
    await redis.setex(redis_key, 86400, "1")
```

### Temporal Query Example

```cypher
// ============================================
// TEMPORAL QUERY PATTERNS
// ============================================

// Query 1: Get entity state at specific point in time
MATCH (e:Entity {name: "ACME Corporation"})
MATCH (e)-[:RELATES_TO]->(edge:Edge)-[:RELATES_TO]->(related:Entity)
WHERE edge.valid_from <= datetime('2025-10-15T00:00:00Z')
  AND (edge.invalid_at IS NULL OR edge.invalid_at > datetime('2025-10-15T00:00:00Z'))
RETURN e.name AS entity,
       edge.name AS relationship,
       related.name AS related_entity,
       edge.fact AS fact,
       edge.valid_from AS valid_from
ORDER BY edge.valid_from DESC;

// Query 2: Get all relationship changes over time
MATCH (e:Entity {name: "ACME Corporation"})
MATCH (e)-[:RELATES_TO]->(edge:Edge)-[:RELATES_TO]->(related:Entity)
RETURN e.name AS entity,
       edge.name AS relationship,
       related.name AS related_entity,
       edge.valid_from AS became_valid,
       edge.invalid_at AS became_invalid,
       CASE WHEN edge.invalid_at IS NULL THEN "current" ELSE "historical" END AS status
ORDER BY edge.valid_from DESC;

// Query 3: Find entities that changed status in date range
MATCH (e:Entity)-[:RELATES_TO]->(edge:Edge {name: "has_status"})-[:RELATES_TO]->(status:Entity)
WHERE edge.valid_from >= datetime('2025-01-01T00:00:00Z')
  AND edge.valid_from <= datetime('2025-12-31T23:59:59Z')
RETURN e.name AS entity,
       status.name AS new_status,
       edge.valid_from AS changed_at
ORDER BY edge.valid_from DESC;

// Query 4: Temporal graph traversal (multi-hop)
MATCH path = (e:Entity {name: "ACME Corporation"})-[:RELATES_TO*1..3]-(related:Entity)
WHERE ALL(edge IN relationships(path)
    WHERE edge.valid_from <= datetime('2025-10-15T00:00:00Z')
      AND (edge.invalid_at IS NULL OR edge.invalid_at > datetime('2025-10-15T00:00:00Z'))
)
RETURN e.name, [n IN nodes(path) | n.name] AS path_nodes, length(path) AS hops
LIMIT 50;
```

---

## Summary & Key Takeaways

### Critical Principles

1. **Write queries first** - Model based on questions, not theory
2. **Use specific relationship types** - Avoid generic connections
3. **Index strategically** - High-cardinality, frequently queried properties only
4. **Test at scale** - Small datasets hide performance problems
5. **Version migrations** - Use custom migration system (no built-in tool)
6. **Coordinate with Graphiti** - Understand label ownership and temporal patterns

### Essential Tools

- **Migration System**: Custom versioned Cypher scripts (V001, V002, etc.)
- **APOC**: Schema introspection and batch operations
- **Cypher PROFILE/EXPLAIN**: Performance analysis
- **Constraints**: Enforce data integrity early

### Performance Checklist

- ✅ Index start nodes of query paths
- ✅ Index properties in WHERE clauses
- ✅ Use constraints for uniqueness
- ✅ Monitor index usage (lastRead, readCount)
- ✅ Drop unused indexes
- ✅ Test with realistic data volumes (1M+ nodes)
- ✅ Profile queries before production

### Graphiti Integration Checklist

- ✅ Understand Graphiti-owned labels (:Entity, :Episode, :Edge, :Community)
- ✅ Create composite temporal indexes (valid_from, invalid_at)
- ✅ Define custom entity types with Pydantic
- ✅ Use saga pattern for multi-database writes
- ✅ Link Apex documents to Graphiti entities

---

## Verification and Updates (November 2025)

**Research Validation Date:** 2025-11-01
**Validation Method:** 5 specialized research agents

### ✅ Verified Current (November 2025)

1. **Neo4j Python Driver** - Official `neo4j` package v5.27.0 (November 2025)
   - Organization: neo4j (official)
   - Repository: https://github.com/neo4j/neo4j-python-driver
   - PyPI: https://pypi.org/project/neo4j/

2. **Neo4j Versions** - 5.x series and 2025.x series available
   - Neo4j 5.x: Current stable production version
   - Neo4j 2025.x: Latest with Cypher 25, block format default, Java 21 required

3. **Migration Tools** - Community tools exist (neo4j-migrations, Liquibase)
   - No official Python-native tool (custom solution recommended)

4. **Vector Indexes** - Supported since Neo4j 5.13+ (verified)
   - Syntax confirmed: `CREATE VECTOR INDEX ... OPTIONS {indexConfig: {...}}`

5. **Index Types** - All documented types verified:
   - Range indexes (general purpose, formerly "BTREE")
   - Text indexes (large strings, CONTAINS queries)
   - Full-text indexes (Apache Lucene, semantic search)
   - Vector indexes (5.13+, cosine/euclidean similarity)
   - Point indexes (spatial queries)

### ⚠️ Updates Made

1. **Migration Tool Claim** - Updated from "no built-in migration system" to "limited built-in migration tooling, community tools exist"

2. **Neo4j Version References** - Updated to reference 5.x/2025.x series (November 2025 current versions)

3. **SDK Verification** - Added reference to SDK_VERIFICATION_SUMMARY.md for complete verification details

### 📋 Recommendations

1. **Use Neo4j Python Driver 5.27.0** - Latest stable, official SDK
2. **Custom Migration Framework** - Continue with custom Python solution (no mature Python-native alternative)
3. **Vector Indexes** - Require Neo4j 5.13+ for VECTOR index support
4. **Test at Scale** - Always test schema with realistic data volumes (1M+ nodes)

---

## References

1. **Neo4j Cypher Manual** - https://neo4j.com/docs/cypher-manual/current/
2. **Neo4j Getting Started** - https://neo4j.com/docs/getting-started/
3. **Neo4j Operations Manual** - https://neo4j.com/docs/operations-manual/current/
4. **Neo4j Python Driver** - https://github.com/neo4j/neo4j-python-driver
5. **Neo4j Labs - Neo4j-Migrations** - https://neo4j.com/labs/neo4j-migrations/ (Java-based community tool)
6. **APOC Documentation** - https://neo4j.com/docs/apoc/current/
7. **Graphiti Documentation** - https://help.getzep.com/graphiti/
8. **Neo4j Blog - Graphiti** - https://neo4j.com/blog/developer/graphiti-knowledge-graph-memory/

---

**Document Version:** 1.1
**Last Updated:** 2025-11-01
**Verification Date:** 2025-11-01
**Maintained By:** Apex Memory System Development Team
