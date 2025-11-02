# APEX MEMORY - EXAMPLE WORKFLOWS
**Supporting Document for Schema v2.0**  
**Date:** November 1, 2025

---

## WORKFLOW 1: Samsara Real-Time Sync

**Frequency:** Every 60 seconds  
**Purpose:** Keep truck data current

```yaml
Trigger: Scheduled (cron job every 60 seconds)

Steps:
  1. Poll Samsara API: /fleet/vehicles
  2. For each vehicle:
     - Extract: unit_number, vin, current_miles, engine_hours, location, driver_id
     - Update Redis cache (TTL: 60 seconds)
     - If significant change detected:
       * Update Neo4j node
       * Log change in Graphiti (temporal tracking)
       * Create PostgreSQL snapshot (if hourly)
  
  3. Check for driver assignment changes:
     - If driver_id changed:
       * End previous assignment relationship (set end_date)
       * Create new assignment relationship
       * Log in Graphiti

Success: All 18 trucks updated in <5 seconds
```

---

## WORKFLOW 2: Fleetone Invoice Processing

**Frequency:** Weekly (Fridays)  
**Purpose:** Extract all fuel transactions

```yaml
Trigger: Email arrives with PDF attachment

Steps:
  1. Email received: EFS_Statement_[date].pdf
  2. Save to Google Drive: /Fuel-Invoices/2025/
  3. Graphiti extracts PDF:
     - Parse all transaction rows
     - Extract: date, fuel_type, gallons, cost, driver_name, location, card
  
  4. For each transaction:
     - Extract driver_name (e.g., "N-Robert McCullough")
     - Query Samsara: "Find driver named Robert McCullough"
     - Get driver's current/recent unit assignment
     - Cross-reference:
       * Transaction location matches truck GPS location?
       * Transaction time matches when driver had that truck?
     - If match confirmed:
       * Create FuelTransaction entity
       * Link: (FuelTransaction)-[:CONSUMED_BY]->(Tractor)
       * Create Expense record
  
  5. Update aggregated metrics:
     - Recalculate Tractor.avg_mpg (if odometer captured)
     - Update Tractor.ytd_fuel_cost

Success: All transactions linked to correct trucks
```

**Fallback Logic:**
```
If unit_number match fails:
  1. Try matching by VIN
  2. Try matching by card_last_5 → driver mapping
  3. Flag for manual review
```

---

## WORKFLOW 3: Maintenance Document Processing

**Frequency:** Event-driven (when document uploaded)  
**Purpose:** Auto-populate maintenance records

```yaml
Trigger: New file in /Trucks/Unit-XXXX/Maintenance/

Steps:
  1. Document uploaded: 2025-11-01-oil-change.pdf
  2. Graphiti extracts PDF:
     - Search for unit_number patterns: "6520", "Unit #6520", "Truck 6520"
     - Search for VIN: 17-character alphanumeric
     - Extract: service_date, description, total_cost, vendor_name
  
  3. Entity Matching:
     - If unit_number found → Match to Tractor
     - Else if VIN found → Match to Tractor
     - Else → Flag for manual unit assignment
  
  4. Create MaintenanceRecord entity:
     - Link: (MaintenanceRecord)-[:PERFORMED_ON]->(Tractor)
     - Link: (MaintenanceRecord)-[:PERFORMED_BY]->(Vendor)
     - Create Expense record
  
  5. Update Tractor:
     - Set Tractor.next_service_due_miles
     - Set Tractor.last_service_date

Success: Maintenance auto-logged without manual entry
```

---

## WORKFLOW 4: Purchase Document Processing

**Frequency:** One-time per truck  
**Purpose:** Populate initial truck data

```yaml
Trigger: Purchase docs uploaded to /Trucks/Unit-XXXX/Purchase/

Steps:
  1. Documents uploaded:
     - purchase-agreement.pdf
     - loan-documents.pdf
     - title.pdf
  
  2. Graphiti extracts from all docs:
     - VIN (primary identifier)
     - make, model, year
     - purchase_date, purchase_price
     - lender_name, loan_amount, monthly_payment
  
  3. Create or update Tractor entity:
     - If VIN exists → Update
     - Else → Create new truck
     - Assign unit_number (if not already assigned)
  
  4. Create relationships:
     - (Tractor)-[:FINANCED_BY]->(Lender)
     - (Tractor)-[:OWNED_BY]->(Origin)

Success: Truck fully documented in system
```

---

## WORKFLOW 5: Insurance Policy Processing

**Frequency:** Annual/renewal  
**Purpose:** Track insurance coverage

```yaml
Trigger: Insurance doc uploaded to /Trucks/Unit-XXXX/Insurance/

Steps:
  1. Document uploaded: policy-2025.pdf
  2. Graphiti extracts:
     - Search for unit_number or VIN
     - Extract: policy_number, provider, coverage_amount, expiry_date, premium
  
  3. Create Insurance entity:
     - Link: (Insurance)-[:COVERS]->(Tractor)
     - Link: (Insurance)-[:PROVIDED_BY]->(Vendor:InsuranceProvider)
  
  4. Set expiry alert:
     - If expiry_date < 60 days → Flag for renewal

Success: Insurance tracked, renewal alerts set
```

---

## WORKFLOW 6: Driver Assignment Change

**Frequency:** Real-time (when detected in Samsara)  
**Purpose:** Maintain accurate driver-truck assignments

```yaml
Trigger: Samsara shows new driver for truck

Steps:
  1. Samsara sync detects: Unit #6520 driver changed from Robert → Raven
  2. Query Graphiti: Get current assignment
     - Current: (Robert)-[:ASSIGNED_TO {assigned_date: "2025-10-01"}]->(Unit6520)
  
  3. End previous assignment:
     - Set end_date: "2025-11-01"
     - Update Graphiti (temporal tracking)
  
  4. Create new assignment:
     - (Raven)-[:ASSIGNED_TO {assigned_date: "2025-11-01", assignment_type: "primary"}]->(Unit6520)
     - Update Redis: Tractor.current_driver_id = "raven-id"
  
  5. Update future fuel transaction mapping:
     - All subsequent fuel transactions for card associated with this truck
       will now link to Raven

Success: Complete assignment history maintained
```

---

## WORKFLOW 7: Status Change Tracking

**Frequency:** Real-time (when detected)  
**Purpose:** Track truck operational status

```yaml
Trigger: Status change detected (active → maintenance)

Steps:
  1. Status change detected:
     - Unit #6520: active → maintenance
  
  2. Update current state:
     - Set Tractor.status = "maintenance"
     - Set Tractor.valid_to = "2025-11-01" (for previous status)
     - Create new state: Tractor.valid_from = "2025-11-01"
  
  3. Log in Graphiti:
     - Temporal tracking: status changed at timestamp
  
  4. Trigger downstream actions:
     - If maintenance → Look for recent MaintenanceRecord
     - Link status change to maintenance event
     - Calculate downtime when returned to active

Success: Complete status history with timestamps
```

---

## WORKFLOW 8: Aggregated Metrics Calculation

**Frequency:** Hourly/Daily  
**Purpose:** Keep calculated metrics current

```yaml
Trigger: Scheduled (daily at midnight)

Calculations:
  1. Tractor.avg_mpg:
     - Query all FuelTransactions for truck
     - Calculate: total_miles_driven / total_gallons
  
  2. Tractor.ytd_fuel_cost:
     - Sum all FuelTransaction.total_cost WHERE year = current_year
  
  3. Tractor.ytd_maintenance_cost:
     - Sum all MaintenanceRecord.total_cost WHERE year = current_year
  
  4. Tractor.total_cost_per_mile:
     - (ytd_fuel_cost + ytd_maintenance_cost) / miles_driven_ytd
  
  5. Fleet-wide metrics:
     - Total fleet fuel cost
     - Average MPG across fleet
     - Most expensive truck to operate

Success: Dashboard metrics updated
```

---

**END OF EXAMPLE WORKFLOWS** ✅
