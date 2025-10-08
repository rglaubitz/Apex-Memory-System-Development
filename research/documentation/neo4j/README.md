# Neo4j Graph Database - Official Documentation

**Tier:** 1 (Official Documentation)
**Date Accessed:** 2025-10-06
**Target Version:** 5.x LTS (Note: Version 6.0.2 database does not exist yet)

## Important Version Note

Based on research, **Neo4j database version 6.0.2 does not currently exist**. The available versions are:
- **Neo4j 5.x** - Current LTS (Long Term Support) version
- **Neo4j 4.4** - Previous LTS version
- **Driver Version 6.x** - Available for Java, Python, and JDBC drivers (not database version)

**Recommendation:** The Apex Memory System should target **Neo4j 5.x LTS** for the database.

## Official Documentation Links

### Main Documentation
- **Neo4j Documentation Hub:** https://neo4j.com/docs/
- **Getting Started Guide:** https://neo4j.com/docs/getting-started/
- **Cypher Query Language Manual:** https://neo4j.com/docs/cypher-manual/current/

### Key Documentation Sections

#### 1. Cypher Query Language Reference
- **Introduction:** https://neo4j.com/docs/cypher-manual/current/introduction/
- **Syntax Reference:** https://neo4j.com/docs/cypher-manual/current/syntax/
- **Basic Queries:** https://neo4j.com/docs/cypher-manual/current/queries/basic/
- **Full Query Reference:** https://neo4j.com/docs/cypher-manual/current/queries/

#### 2. Deployment & Administration
- Neo4j offers multiple deployment options:
  - Neo4j Cloud (managed service)
  - Self-managed installations
  - Docker containers
  - Kubernetes deployments

#### 3. Developer Resources
- **Python Driver (v6.0):** https://neo4j.com/docs/api/python-driver/current/
- **Java Driver Manual:** https://neo4j.com/docs/java-manual/current/
- **API Documentation:** https://neo4j.com/docs/api/python-driver/current/api.html

#### 4. Graph Data Science
- **GDS Library:** Neo4j provides graph algorithms and machine learning capabilities
- **Documentation:** Available through main Neo4j docs portal

## Key Concepts & Architecture

### Core Concepts
1. **Nodes** - Entities in the graph (e.g., users, documents, concepts)
2. **Relationships** - Connections between nodes with direction and type
3. **Properties** - Key-value pairs attached to nodes and relationships
4. **Labels** - Tags for grouping nodes into sets

### Cypher Language Fundamentals

**Creating Nodes:**
```cypher
CREATE (n:Person {name: 'Alice', age: 30})
```

**Creating Relationships:**
```cypher
MATCH (a:Person {name: 'Alice'}), (b:Person {name: 'Bob'})
CREATE (a)-[r:KNOWS]->(b)
RETURN r
```

**Querying:**
```cypher
MATCH (p:Person)-[:KNOWS]->(friend)
WHERE p.name = 'Alice'
RETURN friend.name
```

**Path Queries:**
```cypher
MATCH path = (a:Person)-[:KNOWS*1..3]-(b:Person)
WHERE a.name = 'Alice'
RETURN path
```

## Best Practices

### Performance Optimization
1. **Create Indexes** on frequently queried properties
   ```cypher
   CREATE INDEX FOR (p:Person) ON (p.name)
   ```

2. **Use PROFILE and EXPLAIN** to analyze query performance
   ```cypher
   PROFILE MATCH (p:Person) WHERE p.name = 'Alice' RETURN p
   ```

3. **Limit Result Sets** in development and testing
   ```cypher
   MATCH (n:Person) RETURN n LIMIT 100
   ```

### Data Modeling
1. **Model relationships explicitly** - Don't use properties when relationships are more appropriate
2. **Denormalize when necessary** - Graph databases favor some redundancy for query performance
3. **Use appropriate relationship directions** - Directionality affects traversal performance
4. **Label your nodes** - Labels enable efficient indexing and querying

### Schema Design
1. **Uniqueness Constraints:**
   ```cypher
   CREATE CONSTRAINT FOR (p:Person) REQUIRE p.email IS UNIQUE
   ```

2. **Existence Constraints:**
   ```cypher
   CREATE CONSTRAINT FOR (p:Person) REQUIRE p.name IS NOT NULL
   ```

### Transaction Management
- Use explicit transactions for bulk operations
- Keep transactions short and focused
- Handle connection pooling appropriately in driver code

## Integration Patterns

### Python Integration (Driver v6.0)
```python
from neo4j import GraphDatabase

class Neo4jConnection:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def query(self, cypher_query, parameters=None):
        with self.driver.session() as session:
            result = session.run(cypher_query, parameters)
            return [record for record in result]

# Usage
conn = Neo4jConnection("bolt://localhost:7687", "neo4j", "password")
results = conn.query("MATCH (n:Person) RETURN n LIMIT 10")
conn.close()
```

### Temporal Queries (for Apex Memory System)
Neo4j supports temporal data through properties:
```cypher
// Creating temporal nodes
CREATE (e:Event {
  name: 'Meeting',
  start_time: datetime('2025-10-06T10:00:00'),
  end_time: datetime('2025-10-06T11:00:00')
})

// Querying temporal data
MATCH (e:Event)
WHERE e.start_time >= datetime('2025-10-01')
  AND e.start_time < datetime('2025-11-01')
RETURN e
```

## Relevant Documentation for Apex Memory System

### For Temporal Knowledge Graphs
1. **Temporal properties** - Store timestamps on nodes and relationships
2. **Versioning patterns** - Track entity changes over time
3. **Time-based queries** - Filter and aggregate by temporal dimensions
4. **APOC procedures** - Extended library for temporal operations

### For Memory System Integration
1. **Full-text search** - Built-in indexing for text content
2. **Relationship traversal** - Efficient path finding and pattern matching
3. **Graph algorithms** - PageRank, community detection, similarity
4. **Vector integration** - Can store vector embeddings as properties (complement with pgvector/Qdrant)

## Version-Specific Notes

### Neo4j 5.x Features
- Enhanced security with fine-grained access control
- Improved query performance and optimization
- Better cluster management
- Native graph database capabilities
- Production-ready LTS version

### Migration Notes
- If upgrading from 4.x to 5.x, review breaking changes guide
- **Breaking Changes Documentation:** https://neo4j.com/docs/upgrade-migration-guide/current/version-5/migration/breaking-changes/

## Learning Resources

### Official Training
- **GraphAcademy:** Free online courses at https://neo4j.com/graphacademy/
- **Tutorial Guides:** Interactive learning through Neo4j documentation
- **Community Forums:** Support and discussion channels

### Key Topics for Memory System
1. Graph data modeling fundamentals
2. Cypher query optimization
3. Temporal data patterns
4. Integration with external systems
5. Performance tuning and monitoring

## Additional References

- **Supported Versions:** https://neo4j.com/developer/kb/neo4j-supported-versions/
- **Community Support:** Neo4j community forums
- **GitHub Examples:** Official Neo4j example repositories

## Summary

Neo4j is the leading graph database platform with robust support for temporal knowledge graphs, making it ideal for the Apex Memory System. The current production-ready version is **Neo4j 5.x LTS**, with comprehensive documentation, active development, and enterprise support. The Cypher query language provides an intuitive, SQL-like syntax for graph operations, and the platform offers excellent performance for relationship-heavy queries.

**Key Takeaway:** Use Neo4j 5.x LTS (not 6.0.2) with Python Driver 6.0 for optimal compatibility and support.

---

## Related Upgrades

### Query Router Improvement Plan - GraphRAG Hybrid Search

Neo4j is central to the **GraphRAG hybrid search** approach in the Query Router upgrade:

**Current Limitation:**
- Separate queries to Qdrant (vector) and Neo4j (graph)
- 2x latency (150ms → need <80ms)
- Complex merging logic

**Neo4j 5.x Solution:**
- **Vector Index Support** - Native vector embeddings in Neo4j 5.x+
- **Unified Queries** - Single Cypher query combining vector + graph
- **99% Precision** - Graph-aware ranking and relationship context

**Research:** See `../query-routing/graphrag-hybrid-search.md` for implementation details

📋 **[Query Router Upgrade](../../../upgrades/query-router/IMPROVEMENT-PLAN.md)** - Phase 2 (Week 3-4)

---

## Cross-References

- **Research:** `../query-routing/graphrag-hybrid-search.md` - GraphRAG patterns
- **ADRs:** `../../architecture-decisions/ADR-001` - Multi-database architecture
- **Examples:** `../../examples/multi-database-rag/` - GraphRAG implementations
- **Upgrades:** `../../../upgrades/query-router/` - Active improvement plan
