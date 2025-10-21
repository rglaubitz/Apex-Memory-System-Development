# Domain Modeling Best Practices - Research Summary

**Source:** Domain-Driven Design + Knowledge Graph Research
**Date:** 2025-10-20
**Purpose:** Best practices for modeling trucking/logistics domain for knowledge graphs

---

## Overview

Domain modeling is the process of identifying entities, relationships, and constraints for a specific business domain (e.g., trucking/logistics).

---

## Core Principles

### 1. Entity Identification

**Definition:** An entity is a "thing" that has identity and significance in the domain.

**Good Entities:**
- Have unique identifiers (Vehicle: VEH-1234, Invoice: INV-001)
- Have properties (Vehicle: make, model, year)
- Persist over time (Vehicle exists for years)

**Bad Entities:**
- Temporary states (e.g., "Loading" as an entity → should be a property)
- Actions/verbs (e.g., "Delivering" → should be a relationship or event)

---

### 2. Entity Granularity

**Goldilocks Principle:** Not too generic, not too specific.

**Example: Trucking Domain**

**Too Generic:**
```
❌ Document (could be invoice, shipment, contract, maintenance record)
❌ Person (could be driver, customer contact, vendor contact)
```

**Too Specific:**
```
❌ BrakePadsInvoice (too narrow - should be PartsInvoice)
❌ OilChangeMaintenanceRecord (too narrow - should be MaintenanceRecord)
```

**Just Right:**
```
✅ PartsInvoice (specific enough, covers all parts invoices)
✅ Vehicle (specific enough, covers trucks and trailers)
✅ Driver (specific role in domain)
```

---

### 3. Entity Type Hierarchy

**Use hierarchies when natural groupings exist:**

```
Vehicle (parent)
├── Truck (child)
└── Trailer (child)

Vendor (parent)
├── PartsVendor (child)
├── FuelVendor (child)
└── ServiceVendor (child)
```

**When to use hierarchies:**
- Shared properties (all Vehicles have VIN, make, model)
- Shared behavior (all Vendors have name, contact info)
- Polymorphic queries (find all Vehicles regardless of type)

**When NOT to use hierarchies:**
- Only 1-2 subtypes (not worth the complexity)
- No shared properties/behavior

---

### 4. Relationship Identification

**Definition:** A relationship connects two entities with semantic meaning.

**Good Relationships:**
- Semantic (BELONGS_TO vs. generic RELATED_TO)
- Directional (Invoice → Vehicle, not bidirectional)
- Verifiable (can confirm relationship exists)

**Bad Relationships:**
- Generic (RELATED_TO, MENTIONS - no semantic meaning)
- Ambiguous (HAS - has what? has how?)

---

### 5. Relationship Naming Conventions

**Convention:** VERB_PREPOSITION format (all caps, snake case)

**Examples:**
```
✅ BELONGS_TO (Invoice BELONGS_TO Vehicle)
✅ SUPPLIED_BY (Invoice SUPPLIED_BY Vendor)
✅ PAID_BY (Invoice PAID_BY BankTransaction)
✅ ASSIGNED_TO (Vehicle ASSIGNED_TO Driver)
✅ DELIVERED_TO (Shipment DELIVERED_TO Location)
```

**Why all caps?** Neo4j convention for relationship types.

---

## Domain Modeling Process

### Step 1: Identify Core Entities

**Technique:** Noun extraction from domain documents.

**Example: Parts Invoice Document**

```
"Invoice INV-2025-001 for $820.00 from ACME Auto Parts for brake pads for Truck VEH-1234. Paid via ACH transfer TX-5678."

Nouns:
- Invoice (→ PartsInvoice entity)
- ACME Auto Parts (→ Vendor entity)
- Truck (→ Vehicle entity)
- ACH transfer (→ BankTransaction entity)
```

**Result:** 4 core entities identified.

---

### Step 2: Define Entity Schemas

**For each entity, define:**
1. **Required attributes** (must have)
2. **Optional attributes** (nice to have)
3. **Examples** (for validation)

**Example: Vehicle Entity**

```yaml
type: Vehicle
description: A truck, trailer, or other vehicle in the fleet
required_attributes:
  - vehicle_id  # Unique identifier (e.g., VEH-1234)
  - type        # Truck or Trailer
optional_attributes:
  - make        # Freightliner, Kenworth, Volvo
  - model       # Cascadia, T680, VNL
  - year        # 2022, 2023
  - vin         # Vehicle Identification Number
  - license_plate
examples:
  - "Truck VEH-1234"
  - "2022 Freightliner Cascadia VIN ABC123"
  - "Trailer #5678"
```

---

### Step 3: Identify Relationships

**Technique:** Verb extraction + semantic analysis.

**Example: Same Invoice Document**

```
"Invoice INV-2025-001 for $820.00 from ACME Auto Parts for brake pads for Truck VEH-1234. Paid via ACH transfer TX-5678."

Relationships:
- Invoice "for" Truck → BELONGS_TO
- Invoice "from" Vendor → SUPPLIED_BY
- Invoice "paid via" Transaction → PAID_BY
```

**Result:** 3 relationships identified.

---

### Step 4: Define Relationship Schemas

**For each relationship, define:**
1. **Source entity type** (where relationship starts)
2. **Target entity type** (where relationship ends)
3. **Semantic meaning** (what does relationship represent?)
4. **Examples** (for validation)

**Example: BELONGS_TO Relationship**

```yaml
type: BELONGS_TO
description: Entity belongs to or is owned by another entity
source_entity: PartsInvoice
target_entity: Vehicle
examples:
  - "Invoice INV-001 BELONGS_TO Vehicle VEH-1234"
  - "Driver John Smith BELONGS_TO Customer ACME Corp"
```

---

### Step 5: Validate with Sample Documents

**Validation Process:**

1. **Create 10 sample documents** representing common scenarios
2. **Manually extract entities** (expected output)
3. **Test LLM extraction** (actual output)
4. **Compare expected vs. actual** (accuracy calculation)
5. **Iterate on schemas** if accuracy < 90%

**Iteration Example:**

```
Initial Schema: "Document" entity (too generic)
Accuracy: 65% (LLM confused by generic type)

Updated Schema: "PartsInvoice" entity (specific)
Accuracy: 92% (LLM recognizes specific type)
```

---

## Trucking/Logistics Domain Model

### Identified Entity Types (10)

1. **Vehicle** - Trucks, trailers, fleet vehicles
2. **PartsInvoice** - Invoices for parts, repairs, services
3. **Vendor** - Suppliers of parts, services, fuel
4. **BankTransaction** - Payments, transfers, financial records
5. **Driver** - Employed or contracted drivers
6. **Shipment** - Deliveries, loads, cargo
7. **Location** - Warehouses, terminals, customer sites
8. **Customer** - Clients receiving services
9. **MaintenanceRecord** - Maintenance/repair records
10. **Route** - Delivery routes or paths

---

### Identified Relationship Types (8)

1. **BELONGS_TO** - Invoice → Vehicle, Driver → Customer
2. **SUPPLIED_BY** - Invoice → Vendor
3. **PAID_BY** - Invoice → BankTransaction
4. **ASSIGNED_TO** - Vehicle → Driver, Shipment → Driver
5. **DELIVERED_TO** - Shipment → Location
6. **BILLED_TO** - Invoice → Customer
7. **LOCATED_AT** - Vehicle → Location
8. **PERFORMED_ON** - MaintenanceRecord → Vehicle

---

## Common Pitfalls

### Pitfall 1: Too Many Entity Types

**Problem:** 50+ entity types → complexity explosion

**Solution:** Start with 10-15 core entity types, add more as needed.

---

### Pitfall 2: Generic Relationship Types

**Problem:** Everything uses "RELATED_TO" → no semantic meaning

**Solution:** Define specific relationships (BELONGS_TO, SUPPLIED_BY, etc.)

---

### Pitfall 3: Entity/Relationship Confusion

**Problem:** Modeling relationships as entities (e.g., "Assignment" entity instead of ASSIGNED_TO relationship)

**Solution:** Ask: "Does this have properties beyond source and target?" If no → relationship. If yes → entity.

---

### Pitfall 4: Over-Engineering

**Problem:** Modeling every possible attribute upfront

**Solution:** Start with required attributes only, add optional attributes as needed.

---

## Best Practices Summary

1. ✅ **Start Small:** 10-15 entity types, 8-10 relationships
2. ✅ **Be Specific:** Domain-specific types (PartsInvoice) over generic (Document)
3. ✅ **Use Examples:** Include 3+ examples per entity type
4. ✅ **Iterate:** Validate with real documents, refine schemas
5. ✅ **Document:** Write clear descriptions for each entity/relationship
6. ✅ **Consistent Naming:** CamelCase for entities, CAPS_SNAKE for relationships

---

## Research Sources

**Books:**
- Domain-Driven Design (Eric Evans) - Entity/relationship modeling
- Knowledge Graphs (Aidan Hogan et al.) - Knowledge graph design patterns

**Papers:**
- "Knowledge Graph Refinement: A Survey of Approaches and Evaluation Methods" (Paulheim, 2017)
- "A Survey on Knowledge Graphs: Representation, Acquisition and Applications" (Ji et al., 2021)

**Industry Examples:**
- Google Knowledge Graph - Entity modeling at scale
- Uber's Knowledge Graph - Logistics domain modeling

---

**Key Takeaway:** Domain modeling is iterative. Start with core entities and relationships, validate with real data, refine based on accuracy metrics.
