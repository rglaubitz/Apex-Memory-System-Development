# Neo4j Cypher Query Language - Official Documentation Reference

**Source Type:** Tier 1 - Official Documentation
**URL:** https://neo4j.com/docs/cypher-manual/current/
**Date Retrieved:** 2025-10-06
**Status:** Current (Neo4j 2025.06+, Cypher 25)

## Overview

Cypher is Neo4j's declarative graph query language, created in 2011 by Neo4j engineers as an SQL-equivalent language for graph databases. It is GQL conformant and available as open source via The openCypher project.

## Main Documentation URLs

### Primary References

1. **Cypher Manual (Main Reference)**
   - URL: https://neo4j.com/docs/cypher-manual/current/
   - Comprehensive reference for all Cypher features
   - Target audience: Developers, administrators, and researchers

2. **Cypher Queries Section**
   - URL: https://neo4j.com/docs/cypher-manual/current/queries/
   - Core query concepts and patterns
   - All major clauses and operations

3. **Cypher Cheat Sheet**
   - URL: https://neo4j.com/docs/cypher-cheat-sheet/5/all/
   - Quick reference for all Cypher features
   - Version-specific (Cypher 25 for Neo4j 2025.06+)

4. **Getting Started with Cypher**
   - URL: https://neo4j.com/docs/getting-started/cypher/
   - Beginner-friendly introduction
   - Basic concepts and examples

## Documentation Structure

### 1. Introduction
- Overview of Cypher
- Cypher and Neo4j integration
- Cypher and Aura (cloud) considerations

### 2. Queries
**Core Concepts:**
- Nodes, Relationships, and Paths
- Query Composition
- Cypher Versioning

**Query Types:**
- Basic Queries
- Combined Queries (UNION)
- Subqueries

### 3. Key Clauses

**Reading Data:**
- `MATCH` - Pattern matching for graph queries
- `OPTIONAL MATCH` - Optional pattern matching (returns null if no match)
- `WHERE` - Filter results based on conditions
- `RETURN` - Specify what to return from query
- `WITH` - Chain query parts together and process intermediate results

**Writing Data:**
- `CREATE` - Create nodes and relationships
- `MERGE` - Match existing or create new nodes/relationships
- `DELETE` - Delete nodes and relationships
- `REMOVE` - Remove properties or labels
- `SET` - Set properties or labels

**Result Processing:**
- `ORDER BY` - Sort results
- `LIMIT` - Limit number of results
- `SKIP` - Skip results (for pagination)
- `UNWIND` - Transform lists into rows

**New in Cypher 25:**
- `WHEN` - Conditional queries
- `NEXT` - Sequential queries

### 4. Subqueries
- Existential subqueries
- COUNT subqueries
- CALL subqueries
- COLLECT subqueries

### 5. Patterns
- Pattern matching techniques
- Fixed-length patterns
- Variable-length patterns
- Shortest path algorithms

### 6. Values and Types
**Data Types:**
- Temporal values (Date, Time, DateTime, Duration)
- Spatial values (Point, geometry)
- Lists and collections
- Maps and structured data
- Primitive types (String, Integer, Float, Boolean)

### 7. Expressions
**Expression Types:**
- Predicates (boolean conditions)
- Operators (comparison, mathematical, string)
- Mathematical expressions
- Conditional expressions
- Pattern expressions

### 8. Functions

**Function Categories:**
- Aggregating functions (COUNT, SUM, AVG, MAX, MIN, COLLECT)
- Mathematical functions (abs, ceil, floor, round, sqrt, etc.)
- String functions (substring, replace, split, toLower, toUpper)
- Temporal functions (date, time, datetime, duration operations)
- Spatial functions (distance, point operations)
- List functions (size, head, tail, range, reduce)
- Predicate functions (exists, isEmpty, all, any, none)
- Scalar functions (coalesce, properties, type, id)

### 9. Indexes and Constraints

**Index Types:**
- Range indexes
- Text indexes
- Point indexes
- Full-text indexes
- Vector indexes

**Constraint Types:**
- Uniqueness constraints
- Node property existence constraints
- Relationship property existence constraints
- Node key constraints

### 10. Execution Plans and Query Tuning
- Query profiling
- EXPLAIN and PROFILE commands
- Query optimization techniques
- Performance tuning

### 11. Administration
- Database management via Cypher
- User and role management
- Security administration

### 12. Syntax Guidelines
- Naming conventions
- Case sensitivity
- Reserved keywords
- Whitespace and formatting

### 13. Appendix
- Cypher style guide
- GQL conformance documentation
- Tutorials and examples
- Migration guides

## Key Features Highlighted

### Declarative Language
Cypher is declarative, meaning you specify WHAT you want to find, not HOW to find it (unlike imperative languages).

### Pattern Matching
Core strength is ASCII-art style pattern matching:
```cypher
MATCH (person:Person)-[:KNOWS]->(friend)
WHERE person.name = 'Alice'
RETURN friend.name
```

### Graph-Optimized
- Built specifically for graph databases
- Natural representation of nodes and relationships
- Efficient traversal operations

### GQL Conformant
- Adheres to Graph Query Language (GQL) standard
- Industry-standard query language for graph databases

## Version Information

- **Current Version:** Cypher 5 (default)
- **Latest Features:** Cypher 25 (Neo4j 2025.06+)
- **Compatibility:** Backwards compatible with previous versions
- **Version Selection:** Can specify Cypher version in queries

## Use Cases for Apex Memory System

### Relevant Sections for Project

1. **Pattern Matching** - For entity relationship traversal
2. **Temporal Functions** - For bi-temporal versioning
3. **Indexes** - For performance optimization
4. **Subqueries** - For complex entity retrieval
5. **Aggregation Functions** - For analytics and statistics
6. **Variable-Length Patterns** - For multi-hop relationship queries

### Query Types Needed

- Entity relationship traversal (MATCH with patterns)
- Entity creation and updates (CREATE, MERGE)
- Temporal queries (WHERE with date/time filters)
- Aggregation queries (COUNT, COLLECT for statistics)
- Path finding (shortestPath, allShortestPaths)

## Quality Assessment

**Source Quality:** Tier 1 (Official Documentation)
**Currency:** Current (2025)
**Completeness:** Comprehensive
**Technical Accuracy:** Authoritative (maintained by Neo4j)
**Recommended Use:** Primary reference for all Cypher development

## Related Resources

- openCypher Project: https://www.opencypher.org/
- Neo4j Graph Academy: https://graphacademy.neo4j.com/
- Neo4j Community Forum: https://community.neo4j.com/
- Neo4j GitHub: https://github.com/neo4j/neo4j

---

**Research Agent:** documentation-hunter
**Validated By:** documentation-expert
**Status:** Active Reference
**Next Review:** 2026-01-06 (quarterly review)
