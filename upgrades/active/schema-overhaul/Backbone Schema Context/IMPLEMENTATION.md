# BACKBONE SCHEMA - IMPLEMENTATION PLAN

**Project:** Apex Memory Backbone Schema Implementation
**Status:** 📝 Phase 1 Complete (Documentation) | 🚀 Phase 2 Ready (Graphiti Entity Types)
**Timeline:** 12-15 hours total (9 phases)
**Owner:** Apex Memory Development Team
**Started:** November 1, 2025

---

## 📋 TABLE OF CONTENTS

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Phase 1: Documentation Organization](#phase-1-documentation-organization-️-complete)
4. [Phase 2: Graphiti Entity Types](#phase-2-graphiti-entity-types-2-3-hours)
5. [Phase 3: Neo4j Schema](#phase-3-neo4j-schema-definition-1-2-hours)
6. [Phase 4: PostgreSQL Schema](#phase-4-postgresql-schema-1-2-hours)
7. [Phase 5: Qdrant Collections](#phase-5-qdrant-collections-30-minutes)
8. [Phase 6: Redis Cache Keys](#phase-6-redis-cache-keys-30-minutes)
9. [Phase 7: Database Integration Layer](#phase-7-database-integration-layer-2-3-hours)
10. [Phase 8: Validation & Testing](#phase-8-validation--testing-2-3-hours)
11. [Phase 9: Documentation Finalization](#phase-9-documentation-finalization-1-hour)
12. [Success Criteria](#success-criteria)
13. [Rollback Plan](#rollback-plan)

---

## OVERVIEW

### What We're Building

The **Backbone Schema** provides the foundational data model for Apex Memory System across 5 databases:

1. **Neo4j** - Relationships and graph queries
2. **PostgreSQL** - Transactional data and structured records
3. **Qdrant** - Document embeddings and semantic search
4. **Redis** - Real-time cache (60s TTL)
5. **Graphiti** - Temporal intelligence and entity evolution

### Why This Matters

- ✅ Document ingestion knows exactly what to extract
- ✅ Query router knows which database to use for each query type
- ✅ Temporal queries can track entity changes over time
- ✅ Multi-database writes maintain consistency via saga pattern
- ✅ All 18 trucks tracked with complete operational history

### Core Design Principles

1. **Tractor as Central Entity** - Everything connects to unit_number
2. **Polyglot Persistence** - Right database for right task
3. **Bi-Temporal Tracking** - Track both when it happened and when we learned about it
4. **Real-World Grounding** - Built from actual business documents
5. **Schema Versioning** - Support evolution without breaking changes

---

## PREREQUISITES

### Environment Setup

```bash
# Navigate to main codebase
cd apex-memory-system

# Activate virtual environment
source venv/bin/activate

# Verify all services running
python scripts/dev/health_check.py -v
```

**Expected Output:**
```
✅ Neo4j: Healthy (neo4j://localhost:7687)
✅ PostgreSQL: Healthy (postgresql://localhost:5432/apex_memory)
✅ Qdrant: Healthy (http://localhost:6333)
✅ Redis: Healthy (redis://localhost:6379)
✅ Temporal: Healthy (http://localhost:7233)
```

### Documentation Review

**Before starting, read these in order:**

1. ✅ [README.md](README.md) - Navigation and overview
2. ✅ [Additional Schema info.md](Additional%20Schema%20info.md) - Complete schema spec
3. ✅ [example entity connections.md](example%20entity%20connections.md) - Relationship patterns
4. ✅ [Examples/Example Documents.md](Examples/Example%20Documents.md) - Real document samples

---

## PHASE 1: Documentation Organization ✅ COMPLETE

**Duration:** 30 minutes
**Status:** ✅ Complete (November 1, 2025)

### Deliverables

- [x] Main README created ([README.md](README.md))
- [x] Cross-reference matrix created (embedded in README)
- [x] Implementation plan created (this document)
- [x] All documentation linked and navigable

### What Was Accomplished

1. **Created comprehensive README** linking all backbone documentation
2. **Mapped document types → entities → databases** in cross-reference sections
3. **Created this IMPLEMENTATION.md** with detailed 9-phase plan
4. **Organized existing documentation** for engineer accessibility

### Next Phase

➡️ **Phase 2: Graphiti Entity Types** - Define Pydantic models for LLM extraction

---

## PHASE 2: Graphiti Entity Types (2-3 hours)

**Goal:** Create custom Pydantic entity types for 90%+ extraction accuracy

### Why This Is Critical

Graphiti uses LLM-powered entity extraction. Without custom entity types:
- ❌ Generic extraction (~60% accuracy)
- ❌ Misses domain-specific entities
- ❌ Incorrect relationship inference

With custom entity types:
- ✅ Domain-specific extraction (90%+ accuracy)
- ✅ Captures trucking-specific entities
- ✅ Correct relationship patterns

### Entity Types to Create

#### 1. Core Asset Types (3 types)

**File:** `schemas/entity_types.py`

```python
from pydantic import BaseModel, Field
from typing import Optional

class Tractor(BaseModel):
    """Truck/tractor entity.

    Primary identifier for all truck-related data. Everything in the fleet
    connects back to unit_number.

    Examples:
        - "Unit #6520 (2023 Kenworth T680, VIN 1XKYDP9X3NJ124351)"
        - "Truck 6531 active, currently in Phoenix, AZ"
        - "2024 Freightliner Cascadia, unit 6533, 45,000 miles"
    """

    unit_number: str = Field(
        ...,
        description="4-digit truck identifier (e.g., '6520')",
        pattern="^\\d{4}$"
    )
    vin: Optional[str] = Field(
        None,
        description="17-character Vehicle Identification Number",
        pattern="^[A-HJ-NPR-Z0-9]{17}$"
    )
    make: Optional[str] = Field(
        None,
        description="Manufacturer: Kenworth, Freightliner, Peterbilt, etc."
    )
    model: Optional[str] = Field(
        None,
        description="Model name: T680, Cascadia, 579, etc."
    )
    year: Optional[int] = Field(
        None,
        description="Model year (2000-2030)",
        ge=2000,
        le=2030
    )
    status: Optional[str] = Field(
        None,
        description="Operational status: active, maintenance, out_of_service, sold"
    )
    current_miles: Optional[int] = Field(
        None,
        description="Current odometer reading",
        ge=0
    )
    engine_hours: Optional[int] = Field(
        None,
        description="Total engine hours",
        ge=0
    )


class Trailer(BaseModel):
    """Trailer entity.

    Examples:
        - "Trailer T-001, 53ft refrigerated van, Thermo King reefer"
        - "Great Dane reefer trailer T-002, active"
    """

    unit_number: str = Field(
        ...,
        description="Trailer identifier (e.g., 'T-001')"
    )
    trailer_type: str = Field(
        ...,
        description="Type: Refrigerated Van, Dry Van, Flatbed, etc."
    )
    make: Optional[str] = Field(
        None,
        description="Trailer manufacturer: Great Dane, Utility, Wabash, etc."
    )
    reefer_make: Optional[str] = Field(
        None,
        description="Refrigeration unit manufacturer: Thermo King, Carrier"
    )
    status: Optional[str] = Field(
        None,
        description="Status: active, in_repair, retired"
    )


class Driver(BaseModel):
    """Driver entity.

    Examples:
        - "Dan Barkow, CDL A, hired 2023-08-01"
        - "Driver Robert McCullough, active, assigned to Unit 6520"
    """

    name: str = Field(..., description="Driver full name")
    driver_id: Optional[str] = Field(
        None,
        description="Unique driver identifier from Samsara or internal system"
    )
    cdl_number: Optional[str] = Field(
        None,
        description="Commercial Driver's License number"
    )
    cdl_class: Optional[str] = Field(
        None,
        description="CDL class: A, B, C"
    )
    status: Optional[str] = Field(
        None,
        description="Employment status: active, on_leave, terminated"
    )
    hire_date: Optional[str] = Field(
        None,
        description="Hire date (YYYY-MM-DD)"
    )
```

#### 2. Operational Types (3 types)

```python
class FuelTransaction(BaseModel):
    """Fuel purchase transaction.

    Extracted from Fleetone weekly invoices. Challenge: Unit number not
    directly listed, must derive from driver assignment + GPS correlation.

    Examples:
        - "Diesel 44.11 gal @ $3.699/gal, Pilot #353, KY"
        - "DEF 5.35 gal, $24.03 total, driver Robert McCullough"
    """

    transaction_date: str = Field(
        ...,
        description="Fuel purchase date (YYYY-MM-DD or MM/DD/YY)"
    )
    fuel_type: str = Field(
        ...,
        description="Fuel type: diesel, reefer, def, unleaded"
    )
    gallons: float = Field(
        ...,
        description="Gallons purchased",
        gt=0
    )
    price_per_gallon: Optional[float] = Field(
        None,
        description="Price per gallon in USD",
        gt=0
    )
    total_cost: float = Field(
        ...,
        description="Total transaction cost in USD",
        gt=0
    )
    location_name: Optional[str] = Field(
        None,
        description="Fuel station name (e.g., 'Pilot 353')"
    )
    location_state: Optional[str] = Field(
        None,
        description="Two-letter state code (e.g., 'KY', 'AZ')"
    )
    driver_name: Optional[str] = Field(
        None,
        description="Driver name from UNIT column in invoice"
    )
    card_last_5: Optional[str] = Field(
        None,
        description="Last 5 digits of fuel card used"
    )


class MaintenanceRecord(BaseModel):
    """Maintenance service record.

    Extracted from shop invoices/receipts. Primary identifier: unit_number.
    Secondary identifier: VIN.

    Examples:
        - "Oil change for Unit #6520, Phoenix Truck Repair, $753.00"
        - "DOT inspection, brake service, Unit 6531, odometer 85,000"
    """

    unit_number: Optional[str] = Field(
        None,
        description="4-digit unit number (primary identifier)",
        pattern="^\\d{4}$"
    )
    vin: Optional[str] = Field(
        None,
        description="17-character VIN (secondary identifier)",
        pattern="^[A-HJ-NPR-Z0-9]{17}$"
    )
    service_date: str = Field(
        ...,
        description="Service date (YYYY-MM-DD or 'Month DD, YYYY')"
    )
    service_type: str = Field(
        ...,
        description="Service type: preventive, repair, inspection, oil_change, brake_service, other"
    )
    description: str = Field(
        ...,
        description="Service description/work performed"
    )
    vendor_name: str = Field(
        ...,
        description="Shop/vendor name"
    )
    total_cost: float = Field(
        ...,
        description="Total service cost in USD",
        ge=0
    )
    odometer: Optional[int] = Field(
        None,
        description="Odometer reading at service",
        ge=0
    )
    invoice_number: Optional[str] = Field(
        None,
        description="Shop invoice/receipt number"
    )
    next_service_due: Optional[int] = Field(
        None,
        description="Next service due at odometer reading",
        ge=0
    )


class Load(BaseModel):
    """Load/shipment entity.

    Examples:
        - "Load #456 from Phoenix, AZ to Dallas, TX, $2,625 revenue"
        - "Shipment for Sun-Glo Foods, delivered 2025-10-29"
    """

    load_number: str = Field(
        ...,
        description="Load identifier/number"
    )
    origin: Optional[str] = Field(
        None,
        description="Origin location (city, state)"
    )
    destination: Optional[str] = Field(
        None,
        description="Destination location (city, state)"
    )
    revenue: Optional[float] = Field(
        None,
        description="Load revenue in USD",
        ge=0
    )
    status: Optional[str] = Field(
        None,
        description="Load status: pending, dispatched, in_transit, delivered, cancelled"
    )
    pickup_date: Optional[str] = Field(
        None,
        description="Pickup date (YYYY-MM-DD)"
    )
    delivery_date: Optional[str] = Field(
        None,
        description="Delivery date (YYYY-MM-DD)"
    )
```

#### 3. Financial Types (3 types)

```python
class Invoice(BaseModel):
    """Invoice entity (AR/AP).

    Examples:
        - "Invoice INV-2025-1029, $2,625.00, due 2025-11-28, Net 30"
        - "Invoice for Sun-Glo Foods, Load #456"
    """

    invoice_number: str = Field(
        ...,
        description="Invoice number"
    )
    amount: float = Field(
        ...,
        description="Invoice amount in USD",
        gt=0
    )
    due_date: Optional[str] = Field(
        None,
        description="Due date (YYYY-MM-DD)"
    )
    status: Optional[str] = Field(
        None,
        description="Invoice status: sent, pending, paid, overdue, cancelled"
    )
    payment_date: Optional[str] = Field(
        None,
        description="Payment date (YYYY-MM-DD)"
    )
    payment_terms: Optional[str] = Field(
        None,
        description="Payment terms: Net 30, Net 60, etc."
    )


class Expense(BaseModel):
    """Expense entity.

    Examples:
        - "Fuel expense $488.25, Unit #6520, tax deductible"
        - "Maintenance expense $753.00, Phoenix Truck Repair"
    """

    amount: float = Field(
        ...,
        description="Expense amount in USD",
        gt=0
    )
    expense_type: str = Field(
        ...,
        description="Expense type: fuel, maintenance, insurance, loan_payment, etc."
    )
    category: Optional[str] = Field(
        None,
        description="Expense category: asset, operational, administrative"
    )
    related_to: Optional[str] = Field(
        None,
        description="Related unit_number or entity"
    )
    tax_deductible: Optional[bool] = Field(
        None,
        description="Whether expense is tax deductible"
    )
    expense_date: str = Field(
        ...,
        description="Expense date (YYYY-MM-DD)"
    )


class Loan(BaseModel):
    """Loan/financing entity.

    Extracted from purchase agreements, loan documents, payoff statements.

    Examples:
        - "Equipment loan $130,000, BMO Financial, 6.5% APR, 60 months"
        - "Truck loan for Unit #6520, paid off 2025-09-15"
    """

    original_amount: float = Field(
        ...,
        description="Original loan amount in USD",
        gt=0
    )
    current_balance: Optional[float] = Field(
        None,
        description="Current remaining balance in USD",
        ge=0
    )
    lender_name: str = Field(
        ...,
        description="Lender/bank name"
    )
    interest_rate: Optional[float] = Field(
        None,
        description="Interest rate as decimal (e.g., 0.065 for 6.5%)",
        ge=0,
        le=1
    )
    monthly_payment: Optional[float] = Field(
        None,
        description="Monthly payment amount in USD",
        gt=0
    )
    loan_term_months: Optional[int] = Field(
        None,
        description="Loan term in months",
        gt=0
    )
    collateral: Optional[str] = Field(
        None,
        description="Collateral description (e.g., 'Unit #6520', VIN)"
    )
    loan_start_date: Optional[str] = Field(
        None,
        description="Loan origination date (YYYY-MM-DD)"
    )
    payoff_date: Optional[str] = Field(
        None,
        description="Loan payoff date if paid off (YYYY-MM-DD)"
    )
```

#### 4. Relationship Types (3 types)

```python
class Customer(BaseModel):
    """Customer entity.

    Examples:
        - "Sun-Glo Foods, credit rating A, Net 30 terms"
        - "Active customer, manufacturing industry, $50k credit limit"
    """

    name: str = Field(..., description="Customer company name")
    credit_rating: Optional[str] = Field(
        None,
        description="Credit rating: A, B, C, D, F"
    )
    payment_terms: Optional[str] = Field(
        None,
        description="Payment terms: Net 30, Net 60, Net 90, Prepaid"
    )
    credit_limit: Optional[float] = Field(
        None,
        description="Credit limit in USD",
        ge=0
    )
    status: Optional[str] = Field(
        None,
        description="Customer status: active, suspended, inactive"
    )
    industry: Optional[str] = Field(
        None,
        description="Industry: manufacturing, retail, construction, etc."
    )


class Vendor(BaseModel):
    """Vendor entity.

    Examples:
        - "Phoenix Truck Repair, maintenance vendor, 4.5 rating"
        - "Triumph Business Capital, factoring company"
    """

    name: str = Field(..., description="Vendor/company name")
    vendor_type: str = Field(
        ...,
        description="Vendor type: maintenance, fuel, parts, insurance, factoring_company, etc."
    )
    rating: Optional[float] = Field(
        None,
        description="Performance rating (1-5)",
        ge=1,
        le=5
    )
    services: Optional[str] = Field(
        None,
        description="Services provided"
    )


class Bank(BaseModel):
    """Bank/lender entity.

    Examples:
        - "BMO Financial, equipment financing, relationship since 2023-06-15"
        - "Commercial Capital Bank, truck loans"
    """

    name: str = Field(..., description="Bank/institution name")
    institution_type: str = Field(
        ...,
        description="Institution type: lender, bank, credit_union"
    )
    relationship_since: Optional[str] = Field(
        None,
        description="Relationship start date (YYYY-MM-DD)"
    )
    total_credit_exposure: Optional[float] = Field(
        None,
        description="Total outstanding credit in USD",
        ge=0
    )
```

#### 5. Entity Types Dictionary

```python
# Entity types dictionary (pass to Graphiti)
ENTITY_TYPES = {
    # Core Assets
    "Tractor": Tractor,
    "Trailer": Trailer,
    "Driver": Driver,

    # Operational
    "FuelTransaction": FuelTransaction,
    "MaintenanceRecord": MaintenanceRecord,
    "Load": Load,

    # Financial
    "Invoice": Invoice,
    "Expense": Expense,
    "Loan": Loan,

    # Relationships
    "Customer": Customer,
    "Vendor": Vendor,
    "Bank": Bank,
}
```

### Implementation Steps

1. **Create file:** `apex-memory-system/schemas/entity_types.py`
2. **Add all 12 entity type classes** (as detailed above)
3. **Create `ENTITY_TYPES` dictionary**
4. **Add helper functions:**
   ```python
   def get_entity_type_names() -> List[str]:
       return list(ENTITY_TYPES.keys())

   def get_entity_type(type_name: str) -> Optional[BaseModel]:
       return ENTITY_TYPES.get(type_name)
   ```
5. **Test imports:**
   ```bash
   cd apex-memory-system
   python -c "from schemas.entity_types import ENTITY_TYPES; print(f'{len(ENTITY_TYPES)} entity types loaded')"
   ```

### Success Criteria

- ✅ 12 Pydantic entity types defined
- ✅ All types have proper Field descriptions for LLM extraction
- ✅ Pattern validation where applicable (unit_number, VIN, etc.)
- ✅ `ENTITY_TYPES` dictionary created
- ✅ Imports work without errors

### Testing

```python
# Test entity type validation
from schemas.entity_types import Tractor

# Valid tractor
valid_tractor = Tractor(
    unit_number="6520",
    vin="1XKYDP9X3NJ124351",
    make="Kenworth",
    model="T680",
    year=2023
)

# Invalid unit_number (should fail validation)
try:
    invalid_tractor = Tractor(unit_number="ABC")
except ValueError as e:
    print(f"Validation caught: {e}")  # Expected
```

---

## PHASE 3: Neo4j Schema Definition (1-2 hours)

**Goal:** Create comprehensive Cypher schema with constraints, indexes, and relationship definitions

### File Location

**File:** `apex-memory-system/schemas/neo4j_backbone_schema.cypher`

### What to Create

#### 1. Constraints (Unique Identifiers)

```cypher
// ============================================================================
// UNIQUE CONSTRAINTS
// ============================================================================

// Tractor constraints
CREATE CONSTRAINT tractor_unit_number IF NOT EXISTS
FOR (t:Tractor) REQUIRE t.unit_number IS UNIQUE;

CREATE CONSTRAINT tractor_vin IF NOT EXISTS
FOR (t:Tractor) REQUIRE t.vin IS UNIQUE;

// Driver constraint
CREATE CONSTRAINT driver_id IF NOT EXISTS
FOR (d:Driver) REQUIRE d.driver_id IS UNIQUE;

// Load constraint
CREATE CONSTRAINT load_id IF NOT EXISTS
FOR (l:Load) REQUIRE l.load_id IS UNIQUE;

// Contact constraints
CREATE CONSTRAINT contact_id IF NOT EXISTS
FOR (c:Contact) REQUIRE c.contact_id IS UNIQUE;
```

#### 2. Indexes (Performance)

```cypher
// ============================================================================
// PERFORMANCE INDEXES
// ============================================================================

// Tractor indexes
CREATE INDEX tractor_status IF NOT EXISTS
FOR (t:Tractor) ON (t.status);

CREATE INDEX tractor_make_model IF NOT EXISTS
FOR (t:Tractor) ON (t.make, t.model);

CREATE INDEX tractor_year IF NOT EXISTS
FOR (t:Tractor) ON (t.year);

// Temporal indexes (for time-based queries)
CREATE INDEX tractor_valid_from IF NOT EXISTS
FOR (t:Tractor) ON (t.valid_from);

CREATE INDEX tractor_valid_to IF NOT EXISTS
FOR (t:Tractor) ON (t.valid_to);

// Driver indexes
CREATE INDEX driver_status IF NOT EXISTS
FOR (d:Driver) ON (d.status);

CREATE INDEX driver_name IF NOT EXISTS
FOR (d:Driver) ON (d.name);

// Load indexes
CREATE INDEX load_status IF NOT EXISTS
FOR (l:Load) ON (l.status);

// Contact indexes
CREATE INDEX contact_type IF NOT EXISTS
FOR (c:Contact) ON (c.contact_type);

CREATE INDEX contact_vendor_type IF NOT EXISTS
FOR (c:Contact) ON (c.vendor_type);
```

#### 3. Node Label Definitions

Document all node labels and their required properties:

```cypher
// ============================================================================
// NODE LABELS & REQUIRED PROPERTIES
// ============================================================================

// :Tractor
// Required: unit_number (unique), vin (unique)
// Optional: make, model, year, status, current_miles, engine_hours, location_gps, etc.

// :Driver
// Required: driver_id (unique), name
// Optional: cdl_number, status, hire_date, etc.

// :Trailer
// Required: unit_number (unique)
// Optional: type, make, reefer_make, status

// :Load
// Required: load_id (unique)
// Optional: origin, destination, revenue, status, pickup_date, delivery_date

// :Contact (universal CRM entity)
// Required: contact_id (unique), contact_type
// contact_type values: customer, vendor, bank, personal
// Optional: name, vendor_type, credit_rating, etc.

// :Company
// Required: company_id (unique), name
// Optional: entity_type, ein, incorporation_state

// :FuelTransaction
// Required: fuel_id (unique), transaction_date, total_cost
// Optional: unit_number, gallons, fuel_type, location, etc.

// :MaintenanceRecord
// Required: maintenance_id (unique), service_date, total_cost
// Optional: unit_number, vin, service_type, vendor_name, etc.

// :Invoice
// Required: invoice_id (unique), invoice_number, amount
// Optional: due_date, status, payment_date, etc.

// :Expense
// Required: expense_id (unique), amount, expense_type
// Optional: category, related_to, tax_deductible, etc.

// :Loan
// Required: loan_id (unique), original_amount, lender_name
// Optional: current_balance, interest_rate, collateral, etc.
```

#### 4. Relationship Types

```cypher
// ============================================================================
// RELATIONSHIP TYPES
// ============================================================================

// Ownership & Operations
// (Company)-[:OPERATES]->(Tractor)
// (Company)-[:OPERATES]->(Trailer)
// (Company)-[:EMPLOYS]->(Driver)

// Driver Assignment (Temporal)
// (Driver)-[:ASSIGNED_TO {
//   assigned_date: timestamp,
//   end_date: timestamp (nullable),
//   assignment_type: "primary" | "temporary",
//   valid_from: timestamp,
//   valid_to: timestamp (nullable)
// }]->(Tractor)

// Fuel Consumption
// (Tractor)-[:CONSUMES]->(FuelTransaction)
// (Driver)-[:PURCHASES]->(FuelTransaction)

// Maintenance
// (Tractor)-[:REQUIRES_MAINTENANCE]->(MaintenanceRecord)
// (MaintenanceRecord)-[:PERFORMED_BY]->(Contact:Vendor)

// Load Hauling
// (Tractor)-[:HAULS]->(Load)
// (Driver)-[:HAULS]->(Load)
// (Trailer)-[:USED_FOR]->(Load)

// Customer Relationships
// (Company)-[:SERVES]->(Contact:Customer)
// (Contact:Customer)-[:PLACES]->(SalesOrder)
// (Load)-[:FULFILLS_ORDER_FOR]->(Contact:Customer)

// Financial Flows
// (Tractor)-[:GENERATES_REVENUE]->(Revenue)
// (Tractor)-[:INCURS]->(Expense)
// (Load)-[:GENERATES]->(Revenue)
// (Invoice)-[:FOR_LOAD]->(Load)
// (Invoice)-[:ISSUED_TO]->(Contact:Customer)

// Financing
// (Contact:Bank)-[:FINANCES]->(Loan)
// (Loan)-[:SECURES]->(Tractor)
// (Company)-[:HOLDS]->(Loan)

// Insurance
// (Contact:Vendor)-[:PROVIDES_INSURANCE]->(Insurance)
// (Insurance)-[:COVERS]->(Tractor)

// Intercompany
// (Company)-[:TRANSACTS_WITH]->(Company)
// (IntercompanyFlow)-[:FROM]->(Company)
// (IntercompanyFlow)-[:TO]->(Company)
```

### Success Criteria

- ✅ All unique constraints created
- ✅ Performance indexes created for common queries
- ✅ All node labels documented with required properties
- ✅ All relationship types documented with properties
- ✅ Schema can be applied to Neo4j without errors

### Testing

```bash
# Apply schema to Neo4j
cd apex-memory-system
cat schemas/neo4j_backbone_schema.cypher | docker exec -i apex-neo4j cypher-shell -u neo4j -p apexmemory2024

# Verify constraints
docker exec -i apex-neo4j cypher-shell -u neo4j -p apexmemory2024 "SHOW CONSTRAINTS"

# Verify indexes
docker exec -i apex-neo4j cypher-shell -u neo4j -p apexmemory2024 "SHOW INDEXES"
```

---

## PHASE 4: PostgreSQL Schema (1-2 hours)

**Goal:** Create transactional database schema with proper foreign keys and validation

### File Location

**File:** `apex-memory-system/schemas/postgres_backbone_schema.sql`

### Tables to Create

#### 1. tractors (Core table)

```sql
CREATE TABLE tractors (
    -- Primary Identifiers
    unit_number VARCHAR(4) PRIMARY KEY CHECK (unit_number ~ '^\d{4}$'),
    vin VARCHAR(17) UNIQUE NOT NULL CHECK (vin ~ '^[A-HJ-NPR-Z0-9]{17}$'),

    -- Basic Info
    make VARCHAR(100),
    model VARCHAR(100),
    year INTEGER CHECK (year >= 2000 AND year <= 2030),

    -- Operational Status
    status VARCHAR(50) CHECK (status IN ('active', 'maintenance', 'out_of_service', 'sold')),
    current_miles INTEGER CHECK (current_miles >= 0),
    engine_hours INTEGER CHECK (engine_hours >= 0),

    -- Location (updated from Samsara)
    location_latitude DECIMAL(10, 8),
    location_longitude DECIMAL(11, 8),
    location_address TEXT,

    -- Financial
    purchase_date DATE,
    purchase_price DECIMAL(12, 2),
    current_value DECIMAL(12, 2),
    financing_status VARCHAR(50) CHECK (financing_status IN ('owned', 'financed', 'leased')),
    lender_name VARCHAR(200),
    loan_balance DECIMAL(12, 2),
    monthly_payment DECIMAL(10, 2),

    -- Insurance
    insurance_policy_number VARCHAR(100),
    insurance_provider VARCHAR(200),
    insurance_expiry_date DATE,
    monthly_premium DECIMAL(10, 2),

    -- Maintenance Tracking
    next_service_due_miles INTEGER,
    last_service_date DATE,

    -- Temporal Tracking
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    valid_from TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    valid_to TIMESTAMP WITH TIME ZONE,

    -- Metadata
    schema_version VARCHAR(10) DEFAULT '2.0'
);

-- Indexes for performance
CREATE INDEX idx_tractors_status ON tractors(status);
CREATE INDEX idx_tractors_make_model ON tractors(make, model);
CREATE INDEX idx_tractors_valid_from ON tractors(valid_from);
CREATE INDEX idx_tractors_valid_to ON tractors(valid_to);
```

#### 2. fuel_transactions

```sql
CREATE TABLE fuel_transactions (
    -- Primary Key
    fuel_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Foreign Key to Tractor
    unit_number VARCHAR(4) NOT NULL,

    -- Transaction Details
    transaction_date DATE NOT NULL,
    fuel_type VARCHAR(20) NOT NULL CHECK (fuel_type IN ('diesel', 'reefer', 'def', 'unleaded')),

    -- Location
    location_name VARCHAR(200),
    location_state VARCHAR(2),

    -- Amounts
    gallons DECIMAL(10, 2) NOT NULL CHECK (gallons > 0),
    price_per_gallon DECIMAL(10, 2) CHECK (price_per_gallon > 0),
    total_cost DECIMAL(10, 2) NOT NULL CHECK (total_cost > 0),

    -- Additional Info
    card_last_5 VARCHAR(5),
    driver_name VARCHAR(200),
    odometer_at_fuel INTEGER,
    mpg_calculated DECIMAL(5, 2),
    invoice_number VARCHAR(100),
    pdf_url TEXT,

    -- Matching Confidence
    match_confidence VARCHAR(20) CHECK (match_confidence IN ('high', 'medium', 'low', 'manual_review')),
    matching_method VARCHAR(50) CHECK (matching_method IN ('samsara_assignment', 'gps_correlation', 'vin_match', 'manual')),

    -- Temporal Tracking
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Foreign Key Constraint
    CONSTRAINT fk_fuel_tractor
        FOREIGN KEY (unit_number)
        REFERENCES tractors(unit_number)
        ON DELETE RESTRICT
);

-- Indexes
CREATE INDEX idx_fuel_unit_number ON fuel_transactions(unit_number);
CREATE INDEX idx_fuel_transaction_date ON fuel_transactions(transaction_date);
CREATE INDEX idx_fuel_fuel_type ON fuel_transactions(fuel_type);
```

#### 3. maintenance_records

```sql
CREATE TABLE maintenance_records (
    -- Primary Key
    maintenance_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Foreign Key to Tractor
    unit_number VARCHAR(4),
    vin VARCHAR(17),

    -- Service Details
    service_date DATE NOT NULL,
    service_type VARCHAR(50) NOT NULL CHECK (service_type IN ('preventive', 'repair', 'inspection', 'oil_change', 'brake_service', 'other')),
    description TEXT NOT NULL,

    -- Vendor Info
    vendor_name VARCHAR(200) NOT NULL,
    invoice_number VARCHAR(100),

    -- Cost
    total_cost DECIMAL(10, 2) NOT NULL CHECK (total_cost >= 0),

    -- Odometer
    odometer_at_service INTEGER,
    next_service_due_miles INTEGER,

    -- Document Reference
    pdf_url TEXT,

    -- Temporal Tracking
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Foreign Key Constraints
    CONSTRAINT fk_maintenance_tractor_unit
        FOREIGN KEY (unit_number)
        REFERENCES tractors(unit_number)
        ON DELETE RESTRICT,

    CONSTRAINT fk_maintenance_tractor_vin
        FOREIGN KEY (vin)
        REFERENCES tractors(vin)
        ON DELETE RESTRICT,

    -- At least one identifier required
    CONSTRAINT check_has_identifier
        CHECK (unit_number IS NOT NULL OR vin IS NOT NULL)
);

-- Indexes
CREATE INDEX idx_maintenance_unit_number ON maintenance_records(unit_number);
CREATE INDEX idx_maintenance_vin ON maintenance_records(vin);
CREATE INDEX idx_maintenance_service_date ON maintenance_records(service_date);
CREATE INDEX idx_maintenance_service_type ON maintenance_records(service_type);
```

#### 4. drivers

```sql
CREATE TABLE drivers (
    -- Primary Key
    driver_id VARCHAR(100) PRIMARY KEY,

    -- Basic Info
    name VARCHAR(200) NOT NULL,
    cdl_number VARCHAR(50),
    cdl_class VARCHAR(10),
    cdl_expiry DATE,

    -- Employment
    hire_date DATE,
    status VARCHAR(50) CHECK (status IN ('active', 'on_leave', 'terminated')),

    -- Current Assignment (denormalized for performance)
    current_unit_assignment VARCHAR(4),

    -- Temporal Tracking
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Foreign Key
    CONSTRAINT fk_driver_current_unit
        FOREIGN KEY (current_unit_assignment)
        REFERENCES tractors(unit_number)
        ON DELETE SET NULL
);

-- Indexes
CREATE INDEX idx_drivers_status ON drivers(status);
CREATE INDEX idx_drivers_current_assignment ON drivers(current_unit_assignment);
```

### Success Criteria

- ✅ All tables created with proper constraints
- ✅ Foreign keys enforce referential integrity
- ✅ Check constraints validate data
- ✅ Indexes created for common queries
- ✅ Temporal tracking columns on all tables

### Testing

```bash
# Apply schema
cd apex-memory-system
PGPASSWORD=apexmemory2024 psql -h localhost -U apex -d apex_memory -f schemas/postgres_backbone_schema.sql

# Verify tables
PGPASSWORD=apexmemory2024 psql -h localhost -U apex -d apex_memory -c "\dt"

# Test constraints
PGPASSWORD=apexmemory2024 psql -h localhost -U apex -d apex_memory -c "
INSERT INTO tractors (unit_number, vin, make, model, year)
VALUES ('6520', '1XKYDP9X3NJ124351', 'Kenworth', 'T680', 2023);
"
```

---

## PHASE 5: Qdrant Collections (30 minutes)

**Goal:** Define vector storage collections for document search

### File Location

**File:** `apex-memory-system/schemas/qdrant_backbone_schema.py`

### Collections to Create

```python
"""Qdrant Collection Definitions for Backbone Schema.

This module defines vector storage collections for semantic document search.
"""

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PayloadSchemaType

# Collection configurations
COLLECTIONS = {
    "documents": {
        "vector_size": 1536,  # OpenAI text-embedding-3-small
        "distance": Distance.COSINE,
        "payload_schema": {
            "unit_number": PayloadSchemaType.KEYWORD,
            "document_type": PayloadSchemaType.KEYWORD,
            "file_path": PayloadSchemaType.KEYWORD,
            "file_name": PayloadSchemaType.KEYWORD,
            "ingestion_date": PayloadSchemaType.DATETIME,
        },
        "hnsw_config": {
            "m": 16,
            "ef_construct": 100,
        },
    },

    "maintenance_docs": {
        "vector_size": 1536,
        "distance": Distance.COSINE,
        "payload_schema": {
            "unit_number": PayloadSchemaType.KEYWORD,
            "vin": PayloadSchemaType.KEYWORD,
            "service_date": PayloadSchemaType.DATETIME,
            "vendor_name": PayloadSchemaType.KEYWORD,
            "service_type": PayloadSchemaType.KEYWORD,
        },
    },

    "fuel_invoices": {
        "vector_size": 1536,
        "distance": Distance.COSINE,
        "payload_schema": {
            "invoice_date": PayloadSchemaType.DATETIME,
            "invoice_number": PayloadSchemaType.KEYWORD,
        },
    },
}


def create_collections(client: QdrantClient):
    """Create all backbone schema collections."""
    for name, config in COLLECTIONS.items():
        client.create_collection(
            collection_name=name,
            vectors_config=VectorParams(
                size=config["vector_size"],
                distance=config["distance"]
            ),
            hnsw_config=config.get("hnsw_config"),
        )

        # Set payload schema
        for field, schema_type in config["payload_schema"].items():
            client.create_payload_index(
                collection_name=name,
                field_name=field,
                field_schema=schema_type
            )
```

---

## PHASE 6: Redis Cache Keys (30 minutes)

**Goal:** Define caching patterns for real-time data

### File Location

**File:** `apex-memory-system/schemas/redis_backbone_schema.md`

### Cache Key Patterns

```markdown
# Redis Cache Patterns - Backbone Schema

## Key Naming Convention

All keys follow pattern: `{entity}:{identifier}:{property}`

## Truck Real-Time Data (60s TTL)

- `truck:{unit_number}:location` - GPS coordinates + address
- `truck:{unit_number}:status` - Current operational status
- `truck:{unit_number}:driver` - Currently assigned driver ID
- `truck:{unit_number}:miles` - Current odometer reading
- `truck:{unit_number}:engine_hours` - Total engine hours
- `truck:{unit_number}:last_update` - Timestamp of last Samsara sync

## Driver Real-Time Data (60s TTL)

- `driver:{driver_id}:unit` - Currently assigned unit_number
- `driver:{driver_id}:location` - Current GPS location
- `driver:{driver_id}:status` - Current status

## Query Result Caching (5min TTL)

- `query:fuel:{unit_number}:ytd` - YTD fuel costs
- `query:maintenance:{unit_number}:ytd` - YTD maintenance costs
- `query:revenue:{unit_number}:ytd` - YTD revenue

## Cache Invalidation Events

- Document update → Invalidate query cache for that unit_number
- Driver assignment change → Invalidate driver + truck cache
- Samsara sync → Update all truck real-time keys
```

---

## PHASE 7: Database Integration Layer (2-3 hours)

**Goal:** Create Python service classes for multi-database operations

### Files to Create

**Directory:** `apex-memory-system/src/apex_memory/services/backbone/`

```
backbone/
├── __init__.py
├── tractor_service.py
├── fuel_service.py
├── maintenance_service.py
└── temporal_query_service.py
```

### Example: TractorService

```python
"""Tractor Service - Multi-database CRUD operations."""

from typing import Dict, Any, Optional
from apex_memory.database.neo4j_writer import Neo4jWriter
from apex_memory.database.postgres_writer import PostgresWriter
from apex_memory.database.redis_writer import RedisWriter
from apex_memory.services.graphiti_service import GraphitiService


class TractorService:
    """Multi-database service for Tractor entities."""

    def __init__(
        self,
        neo4j: Neo4jWriter,
        postgres: PostgresWriter,
        redis: RedisWriter,
        graphiti: GraphitiService
    ):
        self.neo4j = neo4j
        self.postgres = postgres
        self.redis = redis
        self.graphiti = graphiti

    async def create_tractor(self, tractor_data: Dict[str, Any]) -> str:
        """Create tractor across all databases (Saga pattern)."""
        unit_number = tractor_data["unit_number"]

        # Step 1: Create in PostgreSQL (source of truth for static data)
        # Step 2: Create in Neo4j (relationships)
        # Step 3: Cache in Redis (real-time data)
        # Step 4: Add to Graphiti (temporal tracking)

        # Implement saga with compensation logic
        ...

    async def get_tractor(self, unit_number: str) -> Optional[Dict[str, Any]]:
        """Get tractor with data from all databases."""
        # Try Redis cache first
        # Fall back to PostgreSQL + Neo4j
        # Enrich with Graphiti temporal data
        ...
```

---

## PHASE 8: Validation & Testing (2-3 hours)

**Goal:** Test with Unit #6520 real data

### Test File

**File:** `apex-memory-system/tests/integration/test_backbone_schema.py`

### Test Cases

1. **Test Tractor Creation** - Create Unit #6520 across all DBs
2. **Test Fuel Matching** - Match Fleetone invoice to Unit #6520
3. **Test Maintenance Ingestion** - Ingest maintenance PDF
4. **Test Temporal Queries** - Query driver assignment history
5. **Test Performance** - Verify <50ms P90 latency

---

## PHASE 9: Documentation Finalization (1 hour)

**Goal:** Create engineering handoff documentation

### Files to Create

1. **SCHEMA-EVOLUTION-GUIDE.md** - How to add new entity types
2. **QUERY-PATTERN-LIBRARY.md** - Common queries with examples
3. **TROUBLESHOOTING.md** - Common issues + solutions
4. **API-DOCUMENTATION.md** - How to interact with the schema

---

## SUCCESS CRITERIA

### ✅ Schema Quality

- All 12 entity types defined (Pydantic models)
- Neo4j schema with constraints and indexes
- PostgreSQL schema with foreign keys
- Qdrant collections created
- Redis cache patterns documented

### ✅ Performance

- Temporal queries <50ms (P90)
- Multi-DB writes <200ms
- Cache hit rate >70%

### ✅ Operational

- All 18 trucks can be ingested
- Unit #6520 test case passes all queries
- Schema evolution process documented
- Rollback procedures tested

---

## ROLLBACK PLAN

If schema implementation fails:

1. **Database Rollback:**
   - PostgreSQL: `DROP TABLE IF EXISTS fuel_transactions, maintenance_records, drivers, tractors CASCADE;`
   - Neo4j: `MATCH (n) DETACH DELETE n;` (only if testing)
   - Qdrant: `client.delete_collection("documents")`

2. **Code Rollback:**
   - Remove `schemas/entity_types.py`
   - Remove `schemas/*_backbone_schema.*`
   - Remove `src/apex_memory/services/backbone/`

3. **Validation:**
   - Run existing tests to ensure no regression
   - Verify Phase 3 (Multi-DB Coordination) still works

---

## TIMELINE SUMMARY

| Phase | Duration | Status |
|-------|----------|--------|
| Phase 1: Documentation | 30 min | ✅ Complete |
| Phase 2: Graphiti Entity Types | 2-3 hours | 🚀 Next |
| Phase 3: Neo4j Schema | 1-2 hours | Pending |
| Phase 4: PostgreSQL Schema | 1-2 hours | Pending |
| Phase 5: Qdrant Collections | 30 min | Pending |
| Phase 6: Redis Cache Keys | 30 min | Pending |
| Phase 7: Integration Layer | 2-3 hours | Pending |
| Phase 8: Testing | 2-3 hours | Pending |
| Phase 9: Finalization | 1 hour | Pending |
| **TOTAL** | **12-15 hours** | **8% Complete** |

---

## NEXT STEPS

**Tomorrow's Session:**

1. ✅ Pick up right here in IMPLEMENTATION.md
2. ✅ Start Phase 2: Create `schemas/entity_types.py`
3. ✅ All 12 entity types with proper Field descriptions
4. ✅ Test imports and validation
5. ➡️ Move to Phase 3: Neo4j schema

**Resume Command:**
```bash
cd /Users/richardglaubitz/Projects/Apex-Memory-System-Development
git status  # See what was committed
# Start with Phase 2: Create schemas/entity_types.py
```

---

**Last Updated:** November 1, 2025
**Status:** Phase 1 Complete | Phase 2 Ready
**Next Phase:** Create Graphiti Entity Types (2-3 hours)
