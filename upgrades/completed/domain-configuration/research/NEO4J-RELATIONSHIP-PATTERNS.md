# Neo4j Relationship Patterns - Research Summary

**Source:** Official Neo4j Documentation + Graph Modeling Guides
**Date:** 2025-10-20
**Purpose:** Best practices for modeling relationships in Neo4j knowledge graphs

---

## Overview

Neo4j is a graph database that stores data as **nodes** (entities) and **relationships** (edges).

**Official Documentation:** https://neo4j.com/docs/
**Graph Modeling Guide:** https://neo4j.com/developer/guide-data-modeling/

---

## Relationship Fundamentals

### 1. Relationships Are First-Class Citizens

**In Neo4j, relationships are NOT just "links" - they are full entities with:**
- Type (e.g., `BELONGS_TO`, `SUPPLIED_BY`)
- Properties (e.g., `since: "2025-01-01"`, `amount: 820.00`)
- Direction (always directional: source → target)

**Example:**

```cypher
// Create relationship with properties
CREATE (invoice:PartsInvoice {name: "INV-001"})
      -[r:BELONGS_TO {since: "2025-01-01"}]->
       (vehicle:Vehicle {name: "VEH-1234"})
```

---

### 2. Relationship Direction Matters

**Neo4j relationships are always directional:**

```cypher
// Correct: Invoice points to Vehicle
(invoice:PartsInvoice)-[:BELONGS_TO]->(vehicle:Vehicle)

// Incorrect: Bidirectional (not supported)
(invoice:PartsInvoice)<-[:BELONGS_TO]->(vehicle:Vehicle)
```

**Best Practice:** Model relationships in the most natural direction.

**Example:**
- ✅ `(Invoice)-[:BELONGS_TO]->(Vehicle)` - Invoice belongs to Vehicle
- ❌ `(Vehicle)-[:HAS]->(Invoice)` - Less natural

---

### 3. Relationship Type Naming

**Convention:** SCREAMING_SNAKE_CASE (all caps, underscores)

```cypher
// Correct
:BELONGS_TO
:SUPPLIED_BY
:PAID_BY
:ASSIGNED_TO

// Incorrect
:belongs_to   # lowercase
:BelongsTo    # CamelCase
:BELONGS TO   # space
```

**Why?** Neo4j convention + visual distinction from node labels (which use CamelCase).

---

## Common Relationship Patterns

### Pattern 1: Ownership (BELONGS_TO)

**Use Case:** Entity A belongs to or is owned by Entity B

**Examples:**
```cypher
(Invoice)-[:BELONGS_TO]->(Vehicle)
(Driver)-[:BELONGS_TO]->(Customer)
(MaintenanceRecord)-[:BELONGS_TO]->(Vehicle)
```

**Query:**
```cypher
// Find all invoices for VEH-1234
MATCH (invoice:PartsInvoice)-[:BELONGS_TO]->(vehicle:Vehicle {name: "VEH-1234"})
RETURN invoice;
```

---

### Pattern 2: Provenance (SUPPLIED_BY, PAID_BY)

**Use Case:** Entity A was created/supplied/paid by Entity B

**Examples:**
```cypher
(Invoice)-[:SUPPLIED_BY]->(Vendor)
(Invoice)-[:PAID_BY]->(BankTransaction)
(Shipment)-[:ORDERED_BY]->(Customer)
```

**Query:**
```cypher
// Find all invoices from ACME Auto Parts
MATCH (invoice:PartsInvoice)-[:SUPPLIED_BY]->(vendor:Vendor {name: "ACME Auto Parts"})
RETURN invoice;
```

---

### Pattern 3: Assignment (ASSIGNED_TO)

**Use Case:** Entity A is assigned to or allocated to Entity B

**Examples:**
```cypher
(Vehicle)-[:ASSIGNED_TO]->(Driver)
(Shipment)-[:ASSIGNED_TO]->(Driver)
(Route)-[:ASSIGNED_TO]->(Vehicle)
```

**Query:**
```cypher
// Find all vehicles assigned to John Smith
MATCH (vehicle:Vehicle)-[:ASSIGNED_TO]->(driver:Driver {name: "John Smith"})
RETURN vehicle;
```

---

### Pattern 4: Location (LOCATED_AT, DELIVERED_TO)

**Use Case:** Entity A is at or delivered to Location B

**Examples:**
```cypher
(Vehicle)-[:LOCATED_AT]->(Location)
(Shipment)-[:DELIVERED_TO]->(Location)
(Warehouse)-[:LOCATED_AT]->(City)
```

**Query:**
```cypher
// Find all vehicles at Chicago Distribution Center
MATCH (vehicle:Vehicle)-[:LOCATED_AT]->(location:Location {name: "Chicago Distribution Center"})
RETURN vehicle;
```

---

### Pattern 5: Billing (BILLED_TO)

**Use Case:** Entity A is billed to Customer B

**Examples:**
```cypher
(Invoice)-[:BILLED_TO]->(Customer)
(Shipment)-[:BILLED_TO]->(Customer)
```

**Query:**
```cypher
// Find all invoices billed to ACME Corporation
MATCH (invoice:PartsInvoice)-[:BILLED_TO]->(customer:Customer {name: "ACME Corporation"})
RETURN invoice;
```

---

### Pattern 6: Action (PERFORMED_ON)

**Use Case:** Action A was performed on Entity B

**Examples:**
```cypher
(MaintenanceRecord)-[:PERFORMED_ON]->(Vehicle)
(Inspection)-[:PERFORMED_ON]->(Vehicle)
```

**Query:**
```cypher
// Find all maintenance performed on VEH-1234
MATCH (record:MaintenanceRecord)-[:PERFORMED_ON]->(vehicle:Vehicle {name: "VEH-1234"})
RETURN record;
```

---

### Pattern 7: Routing (FOLLOWS_ROUTE)

**Use Case:** Entity A follows or uses Route B

**Examples:**
```cypher
(Shipment)-[:FOLLOWS_ROUTE]->(Route)
(Vehicle)-[:FOLLOWS_ROUTE]->(Route)
```

**Query:**
```cypher
// Find all shipments following Route R-100
MATCH (shipment:Shipment)-[:FOLLOWS_ROUTE]->(route:Route {name: "R-100"})
RETURN shipment;
```

---

## Multi-Hop Relationship Patterns

### Pattern 8: Invoice → Vehicle → Driver Chain

**Use Case:** Find driver responsible for vehicle on invoice

```cypher
// Find driver for invoice
MATCH path = (invoice:PartsInvoice)-[:BELONGS_TO]->(vehicle:Vehicle)
                                   -[:ASSIGNED_TO]->(driver:Driver)
WHERE invoice.name = "INV-001"
RETURN invoice, vehicle, driver;
```

**Benefit:** Single query traverses multiple relationships.

---

### Pattern 9: Invoice → Transaction → Payment Verification

**Use Case:** Verify invoice payment

```cypher
// Find unpaid invoices
MATCH (invoice:PartsInvoice)
WHERE NOT (invoice)-[:PAID_BY]->(:BankTransaction)
RETURN invoice;
```

**Benefit:** Quickly identify missing relationships.

---

### Pattern 10: Shipment → Route → Locations

**Use Case:** Find all locations on shipment route

```cypher
// Find route waypoints
MATCH (shipment:Shipment)-[:FOLLOWS_ROUTE]->(route:Route)
                          -[:INCLUDES_LOCATION]->(location:Location)
WHERE shipment.name = "SH-001"
RETURN location
ORDER BY route.sequence;
```

---

## Relationship Properties

### When to Add Properties

**Add properties when:**
- Relationship has metadata (e.g., `since`, `until`, `amount`)
- Need to filter relationships (e.g., `active: true`)
- Need to order relationships (e.g., `sequence: 1, 2, 3`)

**Example:**

```cypher
// Relationship with properties
CREATE (vehicle)-[:ASSIGNED_TO {
  since: "2025-01-01",
  until: "2025-12-31",
  active: true
}]->(driver)
```

**Query with property filter:**

```cypher
// Find active assignments
MATCH (vehicle:Vehicle)-[r:ASSIGNED_TO]->(driver:Driver)
WHERE r.active = true
RETURN vehicle, driver;
```

---

### Common Relationship Properties

**Temporal Properties:**
- `since` / `from` - Start date
- `until` / `to` - End date
- `created_at` - Creation timestamp

**Status Properties:**
- `active` - Boolean (true/false)
- `status` - Enum (active, inactive, pending)

**Metadata Properties:**
- `amount` - Monetary value
- `quantity` - Numeric value
- `sequence` - Ordering

---

## Performance Optimization

### Optimization 1: Index Relationship Types

**Neo4j automatically indexes relationship types** - no action needed.

**Fast:**
```cypher
MATCH ()-[r:BELONGS_TO]->()
RETURN COUNT(r);  # Fast (indexed)
```

---

### Optimization 2: Avoid Relationship Property Scans

**Slow:**
```cypher
// Scans all ASSIGNED_TO relationships
MATCH (vehicle:Vehicle)-[r:ASSIGNED_TO]->(driver:Driver)
WHERE r.since > "2025-01-01"
RETURN vehicle, driver;
```

**Faster:**
```cypher
// Index vehicle nodes first
MATCH (vehicle:Vehicle)-[r:ASSIGNED_TO]->(driver:Driver)
WHERE vehicle.active = true AND r.since > "2025-01-01"
RETURN vehicle, driver;
```

---

### Optimization 3: Limit Relationship Hops

**Slow:**
```cypher
// Unlimited hops (expensive)
MATCH path = (invoice:PartsInvoice)-[*]->(location:Location)
RETURN path;
```

**Faster:**
```cypher
// Limit to 3 hops
MATCH path = (invoice:PartsInvoice)-[*1..3]->(location:Location)
RETURN path;
```

---

## Validation Patterns

### Validation 1: Check Relationship Exists

```cypher
// Verify invoice has payment
MATCH (invoice:PartsInvoice {name: "INV-001"})
OPTIONAL MATCH (invoice)-[:PAID_BY]->(transaction:BankTransaction)
RETURN invoice, transaction IS NOT NULL AS is_paid;
```

---

### Validation 2: Count Relationships

```cypher
// Count invoices per vehicle
MATCH (vehicle:Vehicle)<-[:BELONGS_TO]-(invoice:PartsInvoice)
RETURN vehicle.name, COUNT(invoice) AS invoice_count
ORDER BY invoice_count DESC;
```

---

### Validation 3: Find Orphaned Nodes

```cypher
// Find invoices with no vehicle
MATCH (invoice:PartsInvoice)
WHERE NOT (invoice)-[:BELONGS_TO]->(:Vehicle)
RETURN invoice;
```

---

## Best Practices Summary

1. ✅ **Use Directional Relationships:** Always source → target
2. ✅ **Semantic Naming:** Use descriptive relationship types (BELONGS_TO vs. HAS)
3. ✅ **Consistent Naming:** SCREAMING_SNAKE_CASE for relationship types
4. ✅ **Add Properties When Needed:** Timestamp, status, metadata
5. ✅ **Limit Relationship Hops:** Avoid `*` (unlimited), use `*1..3` (limited)
6. ✅ **Validate Relationships:** Check existence, count, find orphans
7. ✅ **Index Node Properties:** Not relationship properties (slow)

---

## Research Sources

**Official Documentation:**
- Neo4j Graph Modeling: https://neo4j.com/developer/guide-data-modeling/
- Neo4j Relationship Documentation: https://neo4j.com/docs/getting-started/current/cypher-intro/relationships/
- Cypher Manual: https://neo4j.com/docs/cypher-manual/current/

**Books:**
- Graph Databases (Robinson, Webber, Eifrem) - Neo4j patterns
- Learning Neo4j (Baton) - Relationship modeling

**Industry Examples:**
- LinkedIn Knowledge Graph - Professional relationships
- Airbnb Knowledge Graph - Booking relationships
- Uber Knowledge Graph - Logistics relationships

---

**Key Takeaway:** Neo4j relationships are powerful - use semantic naming, directional modeling, and properties to create queryable knowledge graphs.
