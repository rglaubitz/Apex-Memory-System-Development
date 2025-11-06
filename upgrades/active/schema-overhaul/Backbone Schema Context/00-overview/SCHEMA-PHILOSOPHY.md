# SCHEMA DESIGN PHILOSOPHY

**Document:** Schema Philosophy & Design Principles
**Date:** November 2, 2025
**Owner:** G (Richard Glaubitz)
**Purpose:** Define the foundational principles governing Apex Memory's multi-database schema architecture

---

## THE MULTI-DATABASE MEMORY SYSTEM

### Traditional Approach (What We're NOT Building)

```
Database 1: Neo4j       →  Relationship data silo
Database 2: PostgreSQL  →  Transaction data silo
Database 3: Qdrant      →  Document data silo
Database 4: Redis       →  Cache data silo
Database 5: Graphiti    →  Temporal data silo

Result: 5 disconnected memories, hard to query across, manual integration
```

### Apex Approach (What We ARE Building)

```
                    ┌──────────────────────┐
                    │   UNIFIED MEMORY     │
                    │   SYSTEM (Schema)    │
                    └──────────┬───────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
┌───────▼────────┐    ┌────────▼────────┐    ┌──────▼──────┐
│ Relationship   │    │    Factual      │    │  Semantic   │
│    Memory      │    │    Memory       │    │   Memory    │
│   (Neo4j)      │    │ (PostgreSQL)    │    │  (Qdrant)   │
└────────────────┘    └─────────────────┘    └─────────────┘
        │                      │                      │
        └──────────────────────┼──────────────────────┘
                               │
                ┌──────────────┴─────────────┐
                │                            │
        ┌───────▼────────┐          ┌───────▼────────┐
        │    Working     │          │    Temporal    │
        │    Memory      │          │     Memory     │
        │    (Redis)     │          │   (Graphiti)   │
        └────────────────┘          └────────────────┘

Result: ONE cohesive brain with 5 specialized memory types
```

**Key Principle:** The schema is the "nervous system" connecting all 5 memory types, enabling seamless integration and unified intelligence.

---

## THE FIVE MEMORY TYPES

### 1. Relationship Memory (Neo4j)

**Purpose:** "Who knows whom? What connects to what?"

**Storage Characteristics:**
- Graph nodes and edges
- Fast graph traversal
- Network analysis
- Multi-hop relationship queries

**Example Use Cases:**
- "Show all trucks assigned to Driver X"
- "Find all customers served by OpenHaul"
- "Map complete financial flow for Unit #6520"
- "Who introduced me to this customer?"

**Schema Responsibility:**
- Define node labels (Tractor, Driver, Customer, etc.)
- Define relationship types (ASSIGNED_TO, SERVES, GENERATES)
- Define relationship properties (assigned_date, end_date, etc.)
- Specify indexes for performant traversal

### 2. Factual Memory (PostgreSQL)

**Purpose:** "What happened? When? How much?"

**Storage Characteristics:**
- Relational tables
- ACID transactions
- Complex aggregations
- Historical records

**Example Use Cases:**
- "Total fuel cost for Unit #6520 YTD"
- "Maintenance history for all trucks"
- "Average MPG by truck model"
- "AR aging report for customers"

**Schema Responsibility:**
- Define table structures
- Specify foreign key relationships
- Set up indexes for aggregation performance
- Define constraints (unique, not null, check)

### 3. Semantic Memory (Qdrant)

**Purpose:** "What documents discuss this concept?"

**Storage Characteristics:**
- Vector embeddings
- Semantic similarity search
- Document collections
- Metadata filtering

**Example Use Cases:**
- "Find all maintenance documents mentioning 'brake repair'"
- "Search insurance policies expiring in Q1"
- "Locate contracts with 'Net 30' payment terms"
- "Find emails discussing customer expansion"

**Schema Responsibility:**
- Define collection structures
- Specify metadata fields for filtering
- Map document types to collections
- Define embedding strategies

### 4. Working Memory (Redis)

**Purpose:** "What's happening RIGHT NOW?"

**Storage Characteristics:**
- Key-value pairs
- <1 second access time
- Automatic expiration (TTL)
- Real-time state

**Example Use Cases:**
- "Current location of Unit #6520"
- "Active loads in transit right now"
- "Today's dashboard metrics"
- "Current driver assignments"

**Schema Responsibility:**
- Define key naming patterns
- Specify TTL durations
- Map real-time data sources
- Define cache invalidation rules

### 5. Temporal Memory (Graphiti)

**Purpose:** "How has this changed over time?"

**Storage Characteristics:**
- Bi-temporal tracking
- Pattern detection
- Relationship evolution
- Time-based queries

**Example Use Cases:**
- "Who was driving Unit #6520 on October 15?"
- "When did Unit #6520 enter maintenance status?"
- "Show odometer progression over time"
- "Track customer payment reliability trend"

**Schema Responsibility:**
- Define temporal entity types
- Specify valid_from/valid_to fields
- Map entities for temporal tracking
- Define pattern detection targets

---

## SCHEMA DESIGN PRINCIPLES

### Principle 1: Define Structure, Not Logic

**Schema Defines:**
- ✅ Hubs (G, OpenHaul, Origin, Contacts, Financials, Corporate)
- ✅ Entities (Tractor, Driver, FuelTransaction, Customer, Invoice)
- ✅ Sub-Entities (Insurance belongs to Tractor, MaintenanceRecord belongs to Tractor)
- ✅ Properties (unit_number, make, model, service_date, total_cost)
- ✅ Relationships (Driver ASSIGNED_TO Tractor, Load GENERATES Revenue)
- ✅ Relationship Properties (assigned_date, end_date, assignment_type)
- ✅ Database Distribution (Tractor → Neo4j + PostgreSQL + Redis + Graphiti)
- ✅ Primary Keys (unit_number for tractors, contact_id for contacts)

**Schema Does NOT Define:**
- ❌ How to extract data from PDFs (Temporal workflows handle this)
- ❌ How to calculate profitability (Agent runtime logic)
- ❌ How to detect patterns (Application features using Graphiti queries)
- ❌ Alert thresholds (Monitoring system configuration)
- ❌ Dashboard layouts (UI/UX design)
- ❌ API endpoints (FastAPI route definitions)

**Why This Matters:**
- Schema is the STRUCTURE that enables logic
- Logic is implemented ON TOP OF the schema
- Separating concerns enables independent evolution

### Principle 2: Unified Entity Identity

**The Problem:**
If the same entity (e.g., Unit #6520) has different identifiers across databases, LLMs/agents can't connect the dots.

**The Solution:**
Use consistent primary keys across all databases.

**Example: Unit #6520 (Tractor)**

```python
# Neo4j
(:Tractor {unit_number: "6520", make: "Kenworth", model: "T680"})

# PostgreSQL
tractors.unit_number = '6520'
maintenance_records.unit_number = '6520'  # Foreign key

# Redis
truck:6520:location = "{lat: 36.1699, lon: -115.1398}"
truck:6520:status = "active"

# Qdrant
metadata = {"unit_number": "6520", "make": "Kenworth"}

# Graphiti
Tractor(unit_number="6520", make="Kenworth", model="T680")
```

**Result:** LLMs/agents can ask "Show me everything about Unit #6520" and seamlessly query across all 5 databases using the same identifier.

### Principle 3: Query Patterns Drive Structure

**Schema design must consider:**
- **Common queries** - What questions are asked frequently?
- **Performance requirements** - What needs <1s response time?
- **Cache strategy** - What data is accessed repeatedly?

**Example:**

**Query:** "Show me all financial flows for Unit #6520"

**Optimization:**
1. **Neo4j Index:** Create index on `Tractor.unit_number` for fast node lookup
2. **PostgreSQL Index:** Create index on `fuel_transactions.unit_number` for aggregation
3. **Redis Cache:** Store `truck:6520:ytd_fuel_cost` with daily refresh
4. **Query Router:** Recognize this is a multi-database query requiring Neo4j + PostgreSQL coordination

**Schema captures this in:**
- Index definitions
- Cache key patterns
- Database distribution map

### Principle 4: Balance Normalization vs Performance

Different databases have different optimization strategies:

**PostgreSQL (Relational):**
- Normalize for data integrity
- Foreign keys enforce relationships
- Avoid redundancy

**Neo4j (Graph):**
- Denormalize for traversal speed
- Store frequently-accessed properties on nodes
- Accept some redundancy for performance

**Redis (Cache):**
- Completely flatten for <1s access
- Pre-calculate aggregations
- Heavy redundancy acceptable (TTL handles staleness)

**Schema Alignment Strategy:**
- Use consistent primary keys (unit_number)
- Accept different optimization approaches per database
- Document data flow patterns

### Principle 5: Temporal Tracking Scope

**Not all entities need temporal tracking** - only those that change meaningfully over time.

**Temporal Tracking Required:**
- ✅ Driver assignments (changes frequently)
- ✅ Truck status (active → maintenance → active)
- ✅ Customer credit rating (improves/degrades over time)
- ✅ Pricing terms (contracts change, need historical record)

**Temporal Tracking NOT Required:**
- ❌ Truck VIN (never changes)
- ❌ Company EIN (static)
- ❌ Document create_date (point-in-time event)

**Schema Responsibility:**
- Define which entities get `valid_from`/`valid_to` fields
- Specify which relationships are temporal
- Map entities to Graphiti for temporal queries

### Principle 6: Hub Independence with Cross-Hub Relationships

**Hubs are organizational concepts, not technical silos.**

**Hub Structure:**
```
Hub 1: G (Command) - Strategy, projects, insights, knowledge
Hub 2: OpenHaul (Brokerage) - Sales orders, carriers, factoring
Hub 3: Origin (Transport) - Fleet, drivers, fuel, loads
Hub 4: Contacts (CRM) - Customers, vendors, banks, personal network
Hub 5: Financials (Money Flows) - Revenue, expenses, loans, credit lines
Hub 6: Corporate (Infrastructure) - Legal, filings, brand, compliance
```

**Key Principle:** Hubs help organize thinking, but relationships cross hubs freely.

**Examples:**
```cypher
// Hub 3 (Origin) → Hub 4 (Contacts)
(Tractor:Origin)-[:REQUIRES_MAINTENANCE]->(MaintenanceRecord:Origin)
(MaintenanceRecord:Origin)-[:PERFORMED_BY]->(Vendor:Contacts)

// Hub 2 (OpenHaul) → Hub 5 (Financials)
(Load:OpenHaul)-[:GENERATES]->(Revenue:Financials)

// Hub 1 (G) → Hub 4 (Contacts)
(G:Person)-[:MANAGES]->(Customer:Contacts)
```

**Schema Responsibility:**
- Define entities within logical hubs
- Allow relationships to cross hubs seamlessly
- Document common cross-hub traversal patterns

---

## WHAT SCHEMA PHASE DELIVERS

### 1. Entity Catalog

**Complete hierarchical list:**

```
Hub 1: G (Command Center)
├── Entity: Strategy
│   ├── Property: strategy_id (uuid)
│   ├── Property: title (string)
│   └── Property: description (text)
├── Entity: Project
├── Entity: Insight
└── Entity: KnowledgeItem

Hub 2: OpenHaul (Brokerage)
├── Entity: SalesOrder
├── Entity: Carrier
├── Entity: FactoringTransaction
└── Entity: Load (Brokered)

Hub 3: Origin (Transport)
├── Entity: Tractor
│   ├── Sub-Entity: Insurance
│   ├── Sub-Entity: MaintenanceRecord
│   └── Sub-Entity: EquipmentSpecs
├── Entity: Trailer
├── Entity: Driver
├── Entity: FuelTransaction
└── Entity: Load (Owned)

... (continue for all 6 hubs)
```

**Deliverable:** Complete entity list with properties, data types, constraints

### 2. Property Definitions

**For each entity property:**
- Data type (string, integer, decimal, timestamp, array, JSON)
- Constraints (required/optional, unique, pattern, min/max)
- Description (what this property represents)
- Example values

**Example:**
```yaml
Tractor:
  unit_number:
    type: string
    pattern: "^\d{4}$"
    required: true
    unique: true
    example: "6520"
    description: "4-digit truck identifier used across all systems"

  make:
    type: string
    required: true
    example: "Kenworth"
    description: "Manufacturer name"

  current_miles:
    type: integer
    required: false
    min: 0
    example: 127893
    description: "Current odometer reading from Samsara API"
```

### 3. Relationship Map

**All relationship types between entities:**

```cypher
// Driver ↔ Tractor
(Driver)-[:ASSIGNED_TO {assigned_date, end_date, assignment_type}]->(Tractor)

// Tractor ↔ Fuel
(Tractor)-[:CONSUMES {transaction_date, gallons, mpg}]->(FuelTransaction)

// Load ↔ Revenue
(Load)-[:GENERATES {revenue_date, amount}]->(Revenue)

... (complete relationship catalog)
```

**Deliverable:** Complete relationship catalog with properties and cardinality

### 4. Database Distribution

**For each entity, specify:**
- Primary database (authoritative source)
- Secondary databases (copies for optimization)
- Properties per database (what gets stored where)

**Example: Tractor Entity**

```yaml
Tractor:
  Neo4j: (PRIMARY for relationships)
    - unit_number (node identifier)
    - make, model, year (basic properties)
    - All relationships (ASSIGNED_TO, CONSUMES, HAULS, etc.)

  PostgreSQL: (PRIMARY for static data)
    - unit_number (primary key)
    - All properties (complete record)
    - Foreign keys to maintenance_records, fuel_transactions

  Redis: (Working memory - 60s TTL)
    - truck:6520:location (GPS)
    - truck:6520:status (active/maintenance)
    - truck:6520:current_driver (driver_id)

  Graphiti: (Temporal tracking)
    - unit_number, make, model
    - Status changes over time
    - Value depreciation over time

  Qdrant: (Optional - only if documents reference truck)
    - Metadata: unit_number, make, model
```

**Deliverable:** Complete database distribution map for all entities

### 5. Primary Key Strategy

**How to identify entities across databases:**

```
Tractor:          unit_number (string, 4 digits)
Driver:           driver_id (string, unique)
Customer:         contact_id (string, "CONT{number}")
FuelTransaction:  fuel_transaction_id (uuid)
Load:             load_id (string, "LOAD_{type}_{number}")
Invoice:          invoice_id (uuid)
Revenue:          revenue_id (uuid)
```

**Deliverable:** Primary key definitions for all entities

### 6. Query Pattern Documentation

**Common queries that inform indexes:**

**Query:** "Total fuel cost for Unit #6520 YTD"
- Database: PostgreSQL
- Index needed: `fuel_transactions (unit_number, transaction_date)`
- Cache: `truck:6520:ytd_fuel_cost` (Redis, daily refresh)

**Query:** "Show all customers served by OpenHaul"
- Database: Neo4j
- Index needed: `Customer` node label, `SERVES` relationship type
- Traversal: `(OpenHaul:Company)-[:SERVES]->(Customer)`

**Deliverable:** Query pattern catalog with index/cache recommendations

---

## WHAT SCHEMA PHASE DOES NOT DELIVER

### 1. PDF Extraction Logic

**NOT Schema:**
```python
# This is IMPLEMENTATION, not schema
def extract_maintenance_record(pdf_path):
    parsed = docling.parse(pdf_path)
    entities = graphiti.extract(parsed, entity_types=[MaintenanceRecord])
    return entities
```

**Schema defines:**
```yaml
MaintenanceRecord:
  unit_number: string (links to Tractor)
  service_date: date
  total_cost: decimal
  description: text
```

### 2. Metric Calculation Formulas

**NOT Schema:**
```python
# This is RUNTIME LOGIC, not schema
def calculate_truck_profitability(unit_number):
    revenue = sum_revenue_for_truck(unit_number)
    fuel_cost = sum_fuel_cost_for_truck(unit_number)
    maintenance_cost = sum_maintenance_cost_for_truck(unit_number)
    return revenue - fuel_cost - maintenance_cost
```

**Schema defines:**
```yaml
Revenue:
  amount: decimal
  revenue_date: date
  related_to_unit: string (foreign key to Tractor)

Expense:
  amount: decimal
  expense_type: string
  related_to_unit: string
```

### 3. Pattern Detection Algorithms

**NOT Schema:**
```python
# This is APPLICATION LOGIC, not schema
def detect_growth_opportunity(carrier_id):
    # Check if carrier could become customer
    on_time_rate = get_carrier_on_time_rate(carrier_id)
    volume = get_carrier_volume(carrier_id)
    if on_time_rate > 0.95 and volume > 10:
        return {"opportunity": "carrier_to_customer", "confidence": "high"}
```

**Schema defines:**
```yaml
Carrier:
  carrier_id: string
  performance_rating: decimal
  monthly_volume: integer
```

### 4. Alert Thresholds

**NOT Schema:**
```yaml
# This is MONITORING CONFIG, not schema
alerts:
  - name: "intercompany_credit_imbalance"
    threshold: 15000
    condition: "abs(origin_owes_openhaul) > threshold"
    action: "notify_g"
```

**Schema defines:**
```yaml
IntercompanyFlow:
  from_entity: string
  to_entity: string
  amount: decimal
  transaction_date: timestamp
```

---

## SCHEMA VS IMPLEMENTATION BOUNDARY

### Schema Design (This Phase)

**Timeframe:** Current phase
**Deliverables:**
- Entity catalog (hubs, entities, sub-entities, properties)
- Relationship map
- Database distribution
- Primary key strategy
- Query patterns

**Tools Used:**
- Documentation (markdown files)
- Schema diagrams
- Property definitions (YAML/JSON)

### Implementation (Future Phases)

**Timeframe:** After schema is complete
**Deliverables:**
- Temporal workflows (PDF extraction pipelines)
- Graphiti entity types (Pydantic models)
- Neo4j constraints/indexes (Cypher DDL)
- PostgreSQL tables (SQL DDL)
- Qdrant collections (API calls)
- Redis cache patterns (key naming conventions)
- FastAPI endpoints (route handlers)
- LLM agent logic (runtime calculations)

**Tools Used:**
- Python (Temporal, FastAPI)
- Cypher (Neo4j)
- SQL (PostgreSQL)
- Redis CLI
- Graphiti SDK

---

## SUCCESS CRITERIA FOR SCHEMA PHASE

**Schema design is complete when:**

✅ All 6 hubs have entities defined with equal detail
✅ All entities have properties with data types and constraints
✅ All relationships are documented with properties
✅ Database distribution is specified for every entity
✅ Primary keys are defined for cross-database identity
✅ Common query patterns are documented
✅ Index and cache strategies are identified
✅ Example documents validate entity definitions
✅ Cross-hub relationship patterns are clear
✅ Implementation team can start building without ambiguity

---

## EXAMPLE: COMPLETE ENTITY DEFINITION

### Tractor Entity (Full Schema Definition)

```yaml
Entity: Tractor
Hub: Origin Transport (Hub 3)
Description: Commercial truck/tractor unit operated by Origin Transport

Properties:
  # Primary Identifiers
  unit_number:
    type: string
    pattern: "^\d{4}$"
    required: true
    unique: true
    example: "6520"
    description: "4-digit truck identifier (human-readable, primary key)"
    databases: [Neo4j, PostgreSQL, Redis, Qdrant, Graphiti]

  vin:
    type: string
    pattern: "^[A-HJ-NPR-Z0-9]{17}$"
    required: true
    unique: true
    example: "1XKYDP9X3NJ124351"
    description: "17-character Vehicle Identification Number (secondary identifier)"
    databases: [Neo4j, PostgreSQL, Graphiti]

  # Basic Info
  make:
    type: string
    required: true
    example: "Kenworth"
    databases: [Neo4j, PostgreSQL, Graphiti]

  model:
    type: string
    required: true
    example: "T680"
    databases: [Neo4j, PostgreSQL, Graphiti]

  year:
    type: integer
    required: true
    min: 2000
    max: 2030
    example: 2023
    databases: [Neo4j, PostgreSQL]

  # Operational Status
  status:
    type: enum
    values: ["active", "maintenance", "out_of_service", "sold"]
    required: true
    default: "active"
    databases: [Neo4j, PostgreSQL, Redis, Graphiti]
    temporal_tracking: true

  current_miles:
    type: integer
    required: false
    min: 0
    example: 127893
    databases: [PostgreSQL, Redis, Graphiti]
    source: "Samsara API"
    update_frequency: "60 seconds"

  # ... (continue for all properties)

Sub-Entities:
  - Insurance
  - MaintenanceRecord
  - EquipmentSpecs

Relationships:
  - (Origin:Company)-[:OPERATES]->(Tractor)
  - (Driver)-[:ASSIGNED_TO {assigned_date, end_date}]->(Tractor)
  - (Tractor)-[:CONSUMES]->(FuelTransaction)
  - (Tractor)-[:REQUIRES_MAINTENANCE]->(MaintenanceRecord)
  - (Tractor)-[:HAULS]->(Load)
  - (Tractor)-[:GENERATES_REVENUE]->(Revenue)
  - (Tractor)-[:INCURS]->(Expense)
  - (Loan)-[:SECURES]->(Tractor)

Database Distribution:
  Neo4j:
    role: "Primary for relationships"
    stores:
      - unit_number (node identifier)
      - make, model, year (basic properties)
      - All relationships
    indexes:
      - unit_number (unique)
      - status
      - make, model (composite)

  PostgreSQL:
    role: "Primary for static data"
    stores:
      - All properties (complete record)
    indexes:
      - unit_number (primary key)
      - vin (unique)
      - status
    foreign_keys:
      - maintenance_records.unit_number → tractors.unit_number
      - fuel_transactions.unit_number → tractors.unit_number

  Redis:
    role: "Working memory (real-time state)"
    stores:
      - truck:{unit_number}:location (GPS coordinates)
      - truck:{unit_number}:status (current status)
      - truck:{unit_number}:current_driver (driver_id)
      - truck:{unit_number}:current_miles (odometer)
    ttl: 60 seconds
    source: "Samsara API sync"

  Graphiti:
    role: "Temporal memory"
    stores:
      - unit_number, make, model (identifiers)
      - Status changes over time
      - Odometer progression
      - Value depreciation
    temporal_tracking:
      - status (valid_from, valid_to)
      - current_miles (progression over time)

  Qdrant:
    role: "Optional (only if documents reference truck)"
    stores:
      - Metadata: unit_number, make, model
    collections:
      - truck_documents
      - maintenance_documents

Query Patterns:
  - "Get all trucks" (Neo4j: MATCH (t:Tractor) RETURN t)
  - "Total maintenance cost for Unit #6520" (PostgreSQL: SUM maintenance_records WHERE unit_number = '6520')
  - "Current location of Unit #6520" (Redis: GET truck:6520:location)
  - "Driver assignment history for Unit #6520" (Graphiti: temporal query)
  - "Find maintenance docs for Unit #6520" (Qdrant: search with filter)
```

---

**Last Updated:** November 2, 2025
**Schema Version:** 2.0
**Status:** Philosophy defined, entity definitions in progress
