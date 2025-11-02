# APEX MEMORY SCHEMA v2.0 - CORE BACKBONE
**Engineering Handoff Document**  
**Date:** November 1, 2025  
**Owner:** G (Richard Glaubitz)  
**Purpose:** Foundational schema structure for Apex Memory System

---

## OVERVIEW

This document defines the **CORE BACKBONE** for Apex Memory's multi-database knowledge graph. It provides the essential entity structures, relationships, and database distribution strategy that engineering will build around.

**Fleet Size:**
- 18 active trucks
- 10-15 inactive/sold (historical data)

**Primary Systems:**
- **Samsara:** Real-time tracking (location, odometer, engine hours, driver assignments)
- **Fleetone:** Fuel management (weekly invoices via email)
- **Google Drive:** Document storage
- **Graphiti:** Document extraction & temporal tracking

---

## 1. TRACTOR ENTITY (Core Asset)

### Primary Identifiers
```yaml
unit_number:
  type: string
  pattern: "^\d{4}$"
  example: "6520"
  unique: true
  database: Neo4j (PRIMARY KEY), PostgreSQL, Redis

vin:
  type: string
  pattern: "^[A-HJ-NPR-Z0-9]{17}$"
  unique: true
  database: Neo4j, PostgreSQL
  note: "Secondary identifier - backup for unit_number matching"
```

### Core Properties
```yaml
# Basic Info
make: string (Kenworth, Peterbilt, Freightliner, etc.)
model: string
year: integer (2000-2030)

# Operational Status
status: enum ["active", "maintenance", "out_of_service", "sold"]
current_miles: integer
engine_hours: integer
location_gps: {latitude, longitude, address}

# Financial
purchase_date: date
purchase_price: decimal
current_value: decimal
financing_status: enum ["owned", "financed", "leased"]
lender_name: string (nullable)
loan_balance: decimal (nullable)
monthly_payment: decimal (nullable)

# Insurance
insurance_policy_number: string
insurance_provider: string
insurance_expiry_date: date
monthly_premium: decimal

# Maintenance Tracking
next_service_due_miles: integer
last_service_date: date

# Temporal Tracking
created_at: timestamp
updated_at: timestamp
valid_from: timestamp
valid_to: timestamp (nullable)
```

### Database Distribution
- **Neo4j:** Core node + all relationships
- **PostgreSQL:** Static properties + financial data
- **Redis:** Real-time data (location, current_miles, engine_hours, status)
- **Qdrant:** Document embeddings (specs, manuals)
- **Graphiti:** Temporal changes (status changes, value depreciation)

---

## 2. RELATED ENTITIES

### 2A. FuelTransaction
```yaml
# Links to Tractor via unit_number (primary) or VIN (secondary)

fuel_transaction_id: uuid (auto-generated)
unit_number: string (FOREIGN KEY)
transaction_date: date
fuel_type: enum ["diesel", "reefer", "def", "unleaded"]
location_name: string
location_state: string
gallons: decimal
price_per_gallon: decimal
total_cost: decimal
invoice_number: string
card_last_5: string
driver_name: string
odometer_at_fuel: integer (nullable)
mpg_calculated: decimal (nullable)
pdf_url: string (Google Drive path)

# Database Distribution
- PostgreSQL: PRIMARY (all transaction data)
- Neo4j: Relationship (FuelTransaction)-[:CONSUMED_BY]->(Tractor)
```

**Linking Strategy:**
- Primary: Match unit_number from fuel data
- Backup: Cross-reference driver + Samsara location + time to verify unit
- Fallback: Use VIN if available

### 2B. MaintenanceRecord
```yaml
# Links to Tractor via unit_number (primary) or VIN (secondary)

maintenance_id: uuid (auto-generated)
unit_number: string (FOREIGN KEY)
service_date: date
service_type: enum ["preventive", "repair", "inspection", "oil_change", "brake_service", "other"]
description: text
vendor_name: string
total_cost: decimal
invoice_number: string
odometer_at_service: integer (nullable)
next_service_due_miles: integer (nullable)
pdf_url: string (Google Drive path)

# Database Distribution
- PostgreSQL: PRIMARY (all maintenance data)
- Neo4j: Relationship (MaintenanceRecord)-[:PERFORMED_ON]->(Tractor)
- Qdrant: Document embeddings (for semantic search)
```

### 2C. Insurance
```yaml
# Links to Tractor via unit_number (primary) or VIN (secondary)

insurance_id: uuid (auto-generated)
unit_number: string (FOREIGN KEY)
policy_number: string
insurance_provider: string
coverage_type: array ["liability", "physical_damage", "cargo"]
coverage_amount: decimal
deductible: decimal
monthly_premium: decimal
policy_start_date: date
policy_expiry_date: date
pdf_url: string (Google Drive path)

# Database Distribution
- PostgreSQL: PRIMARY (all insurance data)
- Neo4j: Relationship (Insurance)-[:COVERS]->(Tractor)
- Qdrant: Document embeddings (policy documents)
```

### 2D. Driver
```yaml
# Tracked in Samsara, synced to Apex Memory

driver_id: string (unique)
name: string
cdl_number: string
cdl_expiry: date
hire_date: date
status: enum ["active", "on_leave", "terminated"]
current_unit_assignment: string (unit_number) (nullable)

# Database Distribution
- Neo4j: PRIMARY (node + assignment relationships)
- PostgreSQL: Driver details
- Redis: Current assignment (real-time)
- Graphiti: Assignment history (temporal tracking)
```

**Driver-Truck Assignment Relationship:**
```cypher
(Driver)-[:ASSIGNED_TO {
  assigned_date: timestamp,
  end_date: timestamp (nullable),
  assignment_type: "primary" | "temporary"
}]->(Tractor)
```

---

## 3. DATA SOURCES

### 3A. Samsara API (Real-Time)
**Updates:** Every 30-60 seconds  
**Provides:**
- unit_number
- vin
- make, model, year
- current_miles
- engine_hours
- location_gps
- current_driver_id
- status

**Storage:**
- Redis: Real-time cache (60 second TTL)
- PostgreSQL: Hourly snapshots for history

### 3B. Fleetone Invoices (Weekly - Fridays)
**Format:** PDF via email  
**Frequency:** Weekly  
**Contains:** All fuel transactions for all trucks

**Extraction Required:**
- transaction_date
- fuel_type
- location_name, location_state
- gallons
- price_per_gallon
- total_cost
- card_last_5
- driver_name

**Challenge:** Unit number not directly listed
**Solution:** 
1. Extract driver_name from invoice
2. Query Samsara for driver's current/recent assignment
3. Cross-reference transaction location + time with Samsara GPS data
4. Fallback to VIN if available in transaction data

### 3C. Maintenance Documents (Event-Driven)
**Format:** PDF receipts/invoices  
**Trigger:** Uploaded to Google Drive  
**Extraction:** Graphiti

**Key Identifiers to Extract:**
- unit_number (search for "Unit #", "Truck #", "Vehicle #" + 4 digits)
- vin (secondary identifier - 17 characters)
- service_date
- total_cost
- description

### 3D. Purchase/Loan Documents (One-Time)
**Format:** PDFs (purchase agreements, loan docs, title)  
**Extraction:** Graphiti

**Key Data:**
- vin (primary identifier)
- unit_number (if assigned)
- purchase_date
- purchase_price
- lender_name
- loan_amount
- monthly_payment

**Note:** Focus on purchase/loan docs only - no QuickBooks integration yet.

### 3E. Insurance Documents (Annual/Renewal)
**Format:** PDF policies  
**Extraction:** Graphiti

**Key Data:**
- unit_number or vin
- policy_number
- insurance_provider
- coverage_amount
- policy_expiry_date
- monthly_premium

---

## 4. KEY RELATIONSHIPS (Neo4j)

```cypher
# Ownership
(Origin)-[:OPERATES]->(Tractor)

# Driver Assignment (Temporal)
(Driver)-[:ASSIGNED_TO {assigned_date, end_date, assignment_type}]->(Tractor)

# Fuel Consumption
(Tractor)-[:CONSUMES]->(FuelTransaction)

# Maintenance
(Tractor)-[:REQUIRES_MAINTENANCE]->(MaintenanceRecord)
(MaintenanceRecord)-[:PERFORMED_BY]->(Contact:Vendor)

# Insurance
(Tractor)-[:HAS_INSURANCE]->(Insurance)
(Insurance)-[:PROVIDED_BY]->(Contact:Vendor)

# Financing
(Tractor)-[:FINANCED_BY]->(Contact:Lender)

# Operations
(Tractor)-[:HAULS]->(Load)

# Financial Flows
(Tractor)-[:GENERATES]->(Revenue)
(Tractor)-[:INCURS]->(Expense)
```

---

## 5. DATABASE DISTRIBUTION STRATEGY

### Neo4j (Relationships & Graph Queries)
**Purpose:** Relationship mapping, graph traversal, network analysis

**Stores:**
- Core Tractor nodes (unit_number, vin, basic properties)
- All relationships between entities
- Graph-based queries

**Example Queries:**
- "Show all trucks assigned to Driver X"
- "Find all maintenance for Unit #6520"
- "Map complete financial flow for Unit #6520"

### PostgreSQL (Transactional Data)
**Purpose:** Structured records, financial transactions, time-series data

**Stores:**
- Tractor details (static properties)
- FuelTransaction records (PRIMARY)
- MaintenanceRecord records (PRIMARY)
- Insurance records
- Historical snapshots

**Example Queries:**
- "Total fuel cost for Unit #6520 YTD"
- "Maintenance history for Unit #6520"
- "Average MPG by truck"

### Qdrant (Document Search)
**Purpose:** Semantic search across documents

**Stores:**
- PDF document embeddings
- Maintenance receipts
- Insurance policies
- Purchase documents
- Spec sheets

**Example Queries:**
- "Find all maintenance documents mentioning 'brake repair'"
- "Search insurance policies expiring in Q1"
- "Locate spec sheet for Kenworth T680"

### Redis (Real-Time Cache)
**Purpose:** Fast access to current state

**Stores:**
- Current truck locations (GPS)
- Current odometer readings
- Current driver assignments
- Current status
- Real-time metrics

**TTL:** 60 seconds (sync with Samsara)

### Graphiti (Temporal Intelligence)
**Purpose:** Track how things change over time

**Stores:**
- Driver assignment history
- Status changes (active → maintenance → active)
- Odometer progression
- Value depreciation
- All entity state changes

**Example Queries:**
- "Who was driving Unit #6520 on October 15?"
- "When did Unit #6520 enter maintenance status?"
- "Show odometer progression for Unit #6520"

---

## 6. GOOGLE DRIVE STRUCTURE

```
/Apex-Memory-Documents/
  
  /Trucks/
    /Unit-6520/
      /Purchase/
      /Insurance/
      /Maintenance/
      /Specs/
    
    /Unit-6521/
      # Same structure
    
    # Repeat for all 18 trucks
  
  /Fuel-Invoices/
    /2024/
    /2025/
```

---

## 7. GRAPHITI EXTRACTION HINTS

### Fuel Invoices
```yaml
linking_identifier: "unit_number"
extraction_hints:
  - "Driver name in UNIT column"
  - "Cross-reference with Samsara driver assignments"
  - "Use transaction location + time to verify unit"
  - "VIN as fallback identifier"
```

### Maintenance Documents
```yaml
linking_identifier: "unit_number" (primary) OR "vin" (secondary)
extraction_hints:
  - "Look for 'Unit #', 'Truck #', 'Vehicle #' followed by 4 digits"
  - "VIN is 17-character alphanumeric"
  - "Unit number typically appears in vehicle identification section"
```

### Purchase/Loan Documents
```yaml
linking_identifier: "vin" (primary) OR "unit_number" (secondary)
extraction_hints:
  - "VIN in vehicle identification section"
  - "Look for 'VIN:', 'Vehicle Identification Number'"
  - "Extract make, model, year from description"
```

### Insurance Documents
```yaml
linking_identifier: "unit_number" OR "vin"
extraction_hints:
  - "Check vehicle schedule section"
  - "VIN often listed per vehicle"
  - "Unit number may be in internal reference fields"
```

---

## 8. TEMPORAL TRACKING

All entities support **bi-temporal tracking:**

**Valid Time** (Business Reality)
- `valid_from`: When this became true in real world
- `valid_to`: When this stopped being true (null = current)

**Transaction Time** (System Knowledge)
- `created_at`: When system learned this
- `updated_at`: When last modified

**Example:**
```cypher
// Truck 6520 was financed, now owned
(Tractor:Unit6520 {
  financing_status: "financed",
  valid_from: "2023-06-15",
  valid_to: "2025-09-01"
})

(Tractor:Unit6520 {
  financing_status: "owned",
  valid_from: "2025-09-01",
  valid_to: null  // Current state
})
```

---

## 9. IMPLEMENTATION PRIORITIES

### Phase 1: Core Infrastructure
- Samsara API integration
- Tractor entity creation (18 trucks)
- Driver entity sync
- Real-time data flow (Redis cache)

### Phase 2: Document Processing
- Google Drive setup
- Graphiti configuration
- Document classification
- Entity extraction

### Phase 3: Fuel Automation
- Fleetone invoice processing
- Unit matching logic
- FuelTransaction entity creation
- Cost aggregation

### Phase 4: Maintenance Tracking
- Maintenance document ingestion
- MaintenanceRecord creation
- Service due tracking

### Phase 5: Validation
- Test with Unit #6520
- Verify all queries work
- Scale to remaining trucks

---

## 10. SUCCESS CRITERIA

✅ All 18 trucks in Neo4j with core properties  
✅ Real-time Samsara data syncing  
✅ Driver assignments tracked temporally  
✅ Fuel transactions linked to correct trucks  
✅ Maintenance records searchable  
✅ Documents organized in Google Drive  
✅ Query router correctly routes to optimal database  

---

## APPENDIX: TEST CASE

**Primary Test Vehicle:** Unit #6520 (G's favorite, oldest truck)

**Test Data Required:**
1. Samsara data (current state)
2. Last 2 Fleetone invoices
3. Last 5 maintenance receipts
4. Purchase/loan documents
5. Insurance policy
6. Spec sheet

**Validation Queries:**
- Neo4j: Get all relationships for Unit #6520
- PostgreSQL: Total maintenance cost for Unit #6520
- Qdrant: Find maintenance docs for Unit #6520
- Redis: Current location of Unit #6520
- Graphiti: Driver assignment history for Unit #6520

---

**END OF CORE BACKBONE SCHEMA v2.0** ✅
