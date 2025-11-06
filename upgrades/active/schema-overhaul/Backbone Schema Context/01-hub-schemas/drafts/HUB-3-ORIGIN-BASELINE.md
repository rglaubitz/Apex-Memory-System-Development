# HUB 3: ORIGIN TRANSPORT (BASELINE - REFERENCE)

**Status:** ✅ Complete Baseline - Full Detail Documented
**Purpose:** Trucking operations - fleet management, drivers, loads, maintenance
**Company:** Origin Transport LLC
**Primary Key Strategy:** unit_number (e.g., "6520" for tractors), driver_id, load_id

---

## Purpose

Hub 3 serves as the **BASELINE REFERENCE** for schema detail level. All other hubs should match this level of completeness.

**This document is a REFERENCE** - full details are documented in:
1. **[Additional Schema info.md](Additional%20Schema%20info.md)** - Complete schema specification (547 lines)
2. **[example entity connections.md](example%20entity%20connections.md)** - Relationship patterns (805 lines)
3. **[Examples/Example Documents.md](Examples/Example%20Documents.md)** - Real document samples for Unit #6520 (440 lines)

---

## Core Entities (Summary)

**Primary Operational Entities:**
1. **Tractor** - Trucks (18 units: #6501-6533)
   - Primary Key: unit_number (4 digits)
   - Secondary Key: VIN (17 characters)
   - ~30+ properties documented

2. **Trailer** - Trailers
   - Primary Key: unit_number
   - Types: dry van, reefer

3. **Driver** - CDL drivers
   - Primary Key: driver_id
   - Links to Hub 4 (Contacts) for personal info

4. **Load** - Freight movements (when Origin hauls directly for customers)
   - Primary Key: load_id
   - Note: Different from Hub 2 (OpenHaul) loads

**Supporting Entities:**
5. **FuelTransaction** - Individual fuel purchases
   - Links to Tractor via unit_number
   - Links to Driver
   - Challenge: Fleetone invoices don't always include unit_number → matching logic documented

6. **MaintenanceRecord** - Service/repair events
   - Links to Tractor via unit_number or VIN
   - Links to Vendor (Hub 4)
   - Properties: service_date, service_type, description, vendor_name, total_cost

7. **Insurance** - Coverage policies
   - Sub-entity of Tractor
   - Properties: policy_number, provider, coverage_amount, expiry_date, premium

---

## Document Examples (Unit #6520)

**7 Real Documents Documented:**
1. ✅ Fleetone Fuel Invoice (EFS_Statement_2025-10-30.pdf)
2. ✅ Maintenance/Repair Invoice (6520-repair-invoice-2025-10-15.pdf)
3. ✅ Purchase Agreement (6520-purchase-agreement.pdf)
4. ✅ Loan Payoff Statement (6520-loan-payoff-2025-09.pdf)
5. ✅ Insurance Policy (6520-insurance-policy-2025.pdf)
6. ✅ Truck Specifications (kenworth-t680-specs.pdf)
7. ✅ Title/Registration documents

**Extraction patterns defined** for each document type.

---

## Key Relationships

```cypher
// Ownership
(Origin:Company)-[:OPERATES]->(Tractor)

// Driver Assignment (Temporal)
(Driver)-[:ASSIGNED_TO {
  assigned_date: timestamp,
  end_date: timestamp (nullable),
  valid_from: timestamp,
  valid_to: timestamp (nullable)
}]->(Tractor)

// Fuel Consumption
(Tractor)-[:CONSUMES]->(FuelTransaction)
(Driver)-[:PURCHASES]->(FuelTransaction)

// Maintenance
(Tractor)-[:REQUIRES_MAINTENANCE]->(MaintenanceRecord)
(Vendor)-[:PERFORMS]->(MaintenanceRecord)

// Load Hauling
(Tractor)-[:HAULS]->(Load)
(Driver)-[:HAULS]->(Load)

// Financial Flows
(Tractor)-[:GENERATES_REVENUE]->(Revenue)  // Hub 5
(Tractor)-[:INCURS]->(Expense)             // Hub 5
(Loan)-[:SECURES]->(Tractor)               // Hub 5
```

---

## Cross-Hub Links

### Hub 3 → Hub 2 (OpenHaul)
```cypher
// When Origin truck hauls OpenHaul load
(Load {load_number: "OH-321678"})-[:HAULED_BY]->(Carrier {carrier_id: "carr_origin"})
(Load)-[:ASSIGNED_UNIT {unit_number: "6520"}]->(Tractor)
```

### Hub 3 → Hub 4 (Contacts)
```cypher
// Drivers have personal records
(Driver {driver_id: "driver_robert"})-[:PERSON_RECORD]->(Person {person_id: "person_robert"})

// Vendors service trucks
(MaintenanceRecord)-[:PERFORMED_BY]->(Vendor:Company)
(Insurance)-[:PROVIDED_BY]->(Vendor:Company)
```

### Hub 3 → Hub 5 (Financials)
```cypher
// Truck expenses
(Tractor {unit_number: "6520"})-[:INCURS]->(Expense {category: "Maintenance", amount: 2500})
(Tractor)-[:INCURS]->(Expense {category: "Fuel"})

// Truck revenue
(Tractor)-[:GENERATES]->(Revenue)

// Loan secures truck
(Loan)-[:SECURES]->(Tractor)
```

### Hub 3 → Hub 6 (Corporate)
```cypher
// Entity owns fleet
(Origin:LegalEntity)-[:OWNS_FLEET]->(Fleet)
(Origin)-[:OWNS]->(Tractor)

// Trucks operate under DOT
(Tractor)-[:OPERATED_UNDER]->(License {license_type: "DOT"})
```

---

## Database Distribution

### Neo4j (Relationship Memory)
- Tractor nodes
- All relationships (driver → tractor, tractor → load, tractor → maintenance)
- Cross-hub relationships

### PostgreSQL (Factual Memory)
- Complete tractor details (make, model, year, VIN, current_miles)
- Maintenance records
- Fuel transactions
- Driver records

### Qdrant (Semantic Memory)
- PDF embeddings (maintenance invoices, fuel invoices, insurance docs)
- Semantic search for "brake repair" or "tire service"

### Redis (Working Memory)
- Current truck location (GPS from Samsara API - 60s TTL)
- Current driver assignment
- Current status (active, maintenance, idle)

### Graphiti (Temporal Memory)
- Driver assignment history
- Status changes (active → maintenance → active)
- Odometer/miles tracking over time
- Maintenance patterns

---

## Primary Keys & Identity

**Unit #6520 Example Across All Databases:**

```python
# Neo4j
(:Tractor {unit_number: "6520", make: "Kenworth", model: "T680"})

# PostgreSQL
SELECT * FROM tractors WHERE unit_number = '6520'
SELECT * FROM maintenance_records WHERE unit_number = '6520'
SELECT * FROM fuel_transactions WHERE unit_number = '6520'

# Redis
GET truck:6520:location        # Current GPS
GET truck:6520:status          # Current status
GET truck:6520:current_driver  # Current driver_id

# Qdrant
search(query="brake repair", filter={"unit_number": "6520"})

# Graphiti
Tractor(unit_number="6520", make="Kenworth", model="T680")
```

---

## Bi-Temporal Tracking Pattern

**Example: Driver Assignment Changes**

```cypher
// Historical record (ended)
(Robert:Driver)-[:ASSIGNED_TO {
  assigned_date: "2025-01-01",
  end_date: "2025-10-31",
  valid_from: "2025-01-01",
  valid_to: "2025-10-31"
}]->(Tractor {unit_number: "6520"})

// Current record
(Raven:Driver)-[:ASSIGNED_TO {
  assigned_date: "2025-11-01",
  end_date: null,  // Still current
  valid_from: "2025-11-01",
  valid_to: null   // Still current
}]->(Tractor {unit_number: "6520"})
```

**Enables temporal queries:**
- "Who was driving Unit #6520 on October 15, 2025?"
- "Show driver assignment history for Unit #6520"
- "When did Raven start driving #6520?"

---

## Fuel Transaction Matching Challenge

**Problem:** Fleetone fuel invoices list driver_name but NOT unit_number.

**Solution (documented in detail):**
1. Extract driver_name from invoice (e.g., "N-Robert McCullough")
2. Query Samsara API: "Which unit was Robert assigned to on that date?"
3. Cross-reference transaction location + time with truck GPS data
4. Assign with confidence score (high/medium/low/manual_review)
5. Fallback to VIN if available

**This matching logic is implementation (not schema), but schema supports it with:**
- Driver assignment temporal tracking
- GPS location tracking in Redis
- Confidence score property on FuelTransaction

---

## Samsara Integration Pattern

**Real-Time Sync (every 60 seconds):**
```yaml
1. Poll Samsara API: /fleet/vehicles
2. For each truck:
   - Extract: unit_number, vin, current_miles, engine_hours, location, driver_id
   - Update Redis cache (TTL: 60s)
   - If significant change:
     * Update Neo4j node
     * Log in Graphiti (temporal)
     * Create PostgreSQL snapshot (hourly)
3. Check for driver assignment changes:
   - If driver_id changed:
     * End previous ASSIGNED_TO relationship
     * Create new ASSIGNED_TO relationship
     * Log in Graphiti
```

**This workflow is implementation (see Example Implementation Workflows.md), but schema supports it.**

---

## Completion Status

**Hub 3 Baseline:**
- ✅ **Entities Defined:** 7 core entities with complete property lists
- ✅ **Relationships Documented:** 15+ relationship types with properties
- ✅ **Database Distribution:** Clear mapping for all 5 databases
- ✅ **Real Documents:** 7 PDFs for Unit #6520
- ✅ **Extraction Patterns:** Documented for each document type
- ✅ **Cross-Hub Links:** Complete integration with Hubs 2, 4, 5, 6
- ✅ **Temporal Tracking:** Bi-temporal patterns documented
- ✅ **Primary Keys:** unit_number strategy defined and exemplified
- ✅ **Real-World Grounding:** Built from actual business operations

**This is the TARGET LEVEL OF DETAIL for all other hubs.**

---

## For Full Details, See:

1. **[Additional Schema info.md](Additional%20Schema%20info.md)** (547 lines)
   - Section 3: Origin Transport (Origin Trucking) - Hub 3
   - Complete entity definitions
   - All properties with types
   - Example values

2. **[example entity connections.md](example%20entity%20connections.md)** (805 lines)
   - Complete load lifecycle walkthrough
   - All relationship examples with Cypher patterns
   - Temporal tracking examples
   - Cross-hub integration patterns

3. **[Examples/Example Documents.md](Examples/Example%20Documents.md)** (440 lines)
   - Unit #6520 complete document set
   - Extraction patterns for each document type
   - Real-world examples

4. **[Examples/Example Implementation Workflows.md](Examples/Example%20Implementation%20Workflows.md)** (267 lines)
   - Samsara sync workflow
   - Fuel invoice processing
   - Maintenance document processing
   - Driver assignment tracking

---

**Baseline Established:** November 1, 2025
**Schema Version:** v2.0 (Baseline Complete)
**Use This As Template:** Match this detail level for Hubs 1, 2, 4, 5, 6
