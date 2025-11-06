# APEX MEMORY - EXAMPLE ENTITY CONNECTIONS
**Relationship Examples for Engineering Team**  
**Date:** November 1, 2025  
**Purpose:** Reference guide showing how entities connect across all 6 hubs

---

## RELATIONSHIP SYNTAX

```cypher
(SourceEntity)-[RELATIONSHIP_TYPE {properties}]->(TargetEntity)
```

**Property Notation:**
- `{property: value}` = relationship metadata
- `timestamp` = temporal tracking
- `[temporal]` = changes over time tracked with valid_from/valid_to

---

## HUB 1: G (COMMAND CENTER) - OWNERSHIP & OVERSIGHT

### Ownership Relationships

```cypher
// G owns both companies
(G:Person {user_id: "g_main"})-[:OWNS {
  acquisition_date: "2023-01-15",
  ownership_percentage: 100.0,
  role: "founder"
}]->(OpenHaul:Company {company_id: "OPENHAUL"})

(G:Person {user_id: "g_main"})-[:OWNS {
  acquisition_date: "2023-01-15",
  ownership_percentage: 100.0,
  role: "founder"
}]->(Origin:Company {company_id: "ORIGIN"})
```

### Strategic Management

```cypher
// G manages customer relationships
(G:Person)-[:MANAGES {
  since: "2023-01-15",
  capacity: "strategic_oversight"
}]->(SunGlo:Contact {contact_id: "CONT001", contact_type: "customer"})

// G sets financial goals
(G:Person)-[:SETS {
  target_date: "2025-12-31",
  priority: "high",
  reviewed_frequency: "monthly"
}]->(Q4Goal:FinancialGoal {
  goal_id: "GOAL_Q4_2025",
  target_amount: 500000.00,
  goal_type: "revenue"
})

// G tracks projects
(G:Person)-[:TRACKS {
  status: "active",
  check_in_frequency: "weekly"
}]->(ApexImplementation:Project {
  project_id: "PROJ001",
  name: "Apex Memory Implementation"
})
```

### Partnership

```cypher
// Travis Arave is G's business partner
(G:Person {user_id: "g_main"})-[:PARTNERS_WITH {
  since: "2023-01-15",
  partnership_type: "co_founder",
  equity_split: 0.50,
  role: "operations_partner"
}]->(Travis:Contact {
  contact_id: "CONT_TRAVIS",
  contact_type: "personal",
  name: "Travis Arave"
})
```

---

## HUB 2: OPENHAUL (BROKERAGE) - OPERATIONS

### Customer Relationships

```cypher
// Sun-Glo is a customer of OpenHaul
(OpenHaul:Company)-[:SERVES {
  customer_since: "2024-06-01",
  service_type: "refrigerated_ltl_brokerage",
  avg_monthly_loads: 12,
  status: "active"
}]->(SunGlo:Contact {
  contact_id: "CONT001",
  contact_type: "customer",
  name: "Sun-Glo Foods"
})

// Sun-Glo places orders with OpenHaul
(SunGlo:Contact)-[:PLACES {
  order_date: "2025-10-28",
  frequency: "weekly"
}]->(Order123:SalesOrder {
  order_id: "ORD_20251028_001",
  origin: "Phoenix, AZ",
  destination: "Dallas, TX",
  rate_agreed: 2625.00
})
```

### Carrier Network

```cypher
// OpenHaul brokers loads to carriers
(OpenHaul:Company)-[:BROKERS_TO {
  relationship_since: "2024-03-15",
  performance_rating: 4.5,
  preferred_lanes: ["PHX-DAL", "PHX-LAS"],
  status: "approved"
}]->(ABCTrucking:Contact {
  contact_id: "CARR001",
  contact_type: "vendor",
  vendor_type: "carrier",
  mc_number: "MC-123456"
})

// Carrier hauls brokered load
(ABCTrucking:Contact)-[:HAULS {
  assignment_date: "2025-10-28",
  rate_to_carrier: 2200.00,
  margin: 425.00
}]->(BrokeredLoad:Load {
  load_id: "LOAD_BROK_001",
  load_type: "brokered",
  status: "dispatched"
})
```

### Factoring

```cypher
// OpenHaul uses factoring for cash flow
(OpenHaul:Company)-[:USES_FACTORING {
  relationship_since: "2024-01-10",
  discount_rate: 0.025,
  advance_percentage: 0.95,
  status: "active"
}]->(TriumphFunding:Contact {
  contact_id: "FACT001",
  contact_type: "vendor",
  vendor_type: "factoring_company",
  name: "Triumph Business Capital"
})
```

---

## HUB 3: ORIGIN TRANSPORT (TRUCKING) - ASSET OPERATIONS

### Fleet Ownership

```cypher
// Origin operates trucks
(Origin:Company)-[:OPERATES {
  acquisition_date: "2023-06-15",
  status: "active",
  primary_use: "refrigerated_freight"
}]->(Unit6531:Tractor {
  unit_number: "6531",
  make: "Kenworth",
  model: "T680",
  year: 2023,
  vin: "1XKYDP9X5PJ123456"
})

(Origin:Company)-[:OPERATES {
  acquisition_date: "2024-02-10",
  status: "active"
}]->(Unit6533:Tractor {
  unit_number: "6533",
  make: "Freightliner",
  model: "Cascadia",
  year: 2024
})
```

### Driver Employment & Assignment

```cypher
// Dan Barkow drives for Origin (employment)
(Origin:Company)-[:EMPLOYS {
  hire_date: "2023-08-01",
  position: "company_driver",
  status: "active",
  pay_type: "per_mile",
  pay_rate: 0.55
}]->(DanBarkow:Driver {
  driver_id: "DRV001",
  name: "Dan Barkow",
  cdl_number: "NV123456789",
  cdl_class: "A"
})

// Dan is assigned to Unit #6531 (temporal - changes over time)
(DanBarkow:Driver)-[:ASSIGNED_TO {
  assigned_date: "2025-10-01",
  end_date: null,
  assignment_type: "primary",
  valid_from: "2025-10-01T00:00:00Z",
  valid_to: null
}]->(Unit6531:Tractor) [temporal]

// Historical: Dan was previously on Unit #6533
(DanBarkow:Driver)-[:ASSIGNED_TO {
  assigned_date: "2023-08-01",
  end_date: "2025-09-30",
  assignment_type: "primary",
  valid_from: "2023-08-01T00:00:00Z",
  valid_to: "2025-09-30T23:59:59Z"
}]->(Unit6533:Tractor) [temporal - historical]
```

### Truck Maintenance & Services

```cypher
// Unit #6531 requires maintenance
(Unit6531:Tractor)-[:REQUIRES_MAINTENANCE {
  service_date: "2025-10-25",
  odometer: 85000,
  downtime_hours: 3.5
}]->(OilChange:MaintenanceRecord {
  maintenance_id: "MAINT_6531_001",
  service_type: "preventive",
  description: "Oil change, filter replacement",
  cost: 450.00
})

// Maintenance performed by vendor
(PhoenixTruckRepair:Contact {
  contact_id: "VEND001",
  contact_type: "vendor",
  vendor_type: "maintenance",
  name: "Phoenix Truck Repair"
})-[:PERFORMS]->(OilChange:MaintenanceRecord)
```

### Fuel Consumption

```cypher
// Unit #6531 consumes fuel
(Unit6531:Tractor)-[:CONSUMES {
  transaction_date: "2025-10-28T14:30:00Z",
  odometer: 85125,
  mpg_calculated: 7.1
}]->(FuelPurchase:FuelTransaction {
  fuel_id: "FUEL_6531_001",
  location: "Pilot Travel Center - Phoenix, AZ",
  gallons: 125.5,
  price_per_gallon: 3.89,
  total_cost: 488.25
})

// Driver purchases fuel (with fuel card)
(DanBarkow:Driver)-[:PURCHASES {
  fuel_card: "FUELCARD001"
}]->(FuelPurchase:FuelTransaction)
```

### Load Hauling

```cypher
// Origin hauls loads for OpenHaul (intercompany)
(Origin:Company)-[:HAULS_FOR {
  service_type: "truck_rental",
  rate_per_mile: 2.00,
  relationship_type: "intercompany"
}]->(OpenHaul:Company)

// Specific load example
(Unit6531:Tractor)-[:HAULS {
  pickup_date: "2025-10-28T08:00:00Z",
  delivery_date: "2025-10-29T14:00:00Z",
  miles: 1050,
  revenue: 2625.00
}]->(Load456:Load {
  load_id: "LOAD_OWN_456",
  load_type: "owned",
  status: "delivered"
})

(DanBarkow:Driver)-[:HAULS {
  pickup_date: "2025-10-28T08:00:00Z",
  delivery_date: "2025-10-29T14:00:00Z"
}]->(Load456:Load)

// Load is for customer
(Load456:Load)-[:FULFILLS_ORDER_FOR]->(SunGlo:Contact)
```

### Trailer Operations

```cypher
// Origin operates trailers
(Origin:Company)-[:OPERATES {
  acquisition_date: "2022-11-20",
  status: "active"
}]->(TrailerT001:Trailer {
  unit_number: "T-001",
  type: "Refrigerated Van",
  make: "Great Dane",
  reefer_make: "Thermo King"
})

// Unit #6531 pulls Trailer T-001
(Unit6531:Tractor)-[:PULLS {
  assigned_date: "2025-10-28",
  end_date: null
}]->(TrailerT001:Trailer) [temporal]
```

---

## HUB 4: CONTACTS (UNIVERSAL CRM)

### Customer Sub-Entities

```cypher
// Sun-Glo has decision maker
(SunGlo:Contact {contact_type: "customer"})-[:HAS_DECISION_MAKER {
  role: "VP of Logistics",
  decision_authority: "high"
}]->(SarahJohnson:Person {
  person_id: "PER_SJ001",
  name: "Sarah Johnson",
  email: "sjohnson@sunglofoods.com",
  title: "VP of Logistics"
})

// Sun-Glo has shipping locations
(SunGlo:Contact)-[:HAS_LOCATION {
  location_type: "shipper",
  primary: true
}]->(PhoenixWarehouse:Location {
  location_id: "LOC_SG_PHX",
  name: "Sun-Glo Phoenix Warehouse",
  city: "Phoenix",
  state: "AZ",
  dock_type: "refrigerated"
})

(SunGlo:Contact)-[:HAS_LOCATION {
  location_type: "receiver",
  primary: true
}]->(DallasDistribution:Location {
  location_id: "LOC_SG_DAL",
  name: "Sun-Glo Dallas Distribution",
  city: "Dallas",
  state: "TX"
})
```

### Vendor Relationships

```cypher
// Phoenix Truck Repair provides maintenance services
(PhoenixTruckRepair:Contact {
  contact_type: "vendor",
  vendor_type: "maintenance"
})-[:PROVIDES_SERVICE_TO {
  since: "2023-07-15",
  preferred: true,
  rating: 4.5,
  avg_response_time: "2 hours"
}]->(Origin:Company)
```

### Bank/Lender Relationships

```cypher
// BMO Financial provides equipment financing
(BMOFinancial:Contact {
  contact_id: "BANK001",
  contact_type: "bank",
  institution_type: "lender",
  name: "BMO Financial"
})-[:LENDS_TO {
  relationship_since: "2023-06-15",
  total_credit_exposure: 285000.00
}]->(Origin:Company)

// Specific loan for Unit #6531
(BMOFinancial:Contact)-[:FINANCES {
  loan_origination_date: "2023-06-15",
  interest_rate: 0.065,
  monthly_payment: 2500.00
}]->(TruckLoan:Loan {
  loan_id: "LOAN_6531",
  original_amount: 130000.00,
  current_balance: 85000.00,
  collateral: "Unit #6531"
})

(TruckLoan:Loan)-[:SECURES]->(Unit6531:Tractor)
```

---

## HUB 5: FINANCIALS (MONEY FLOWS)

### Revenue Generation

```cypher
// Load generates revenue
(Load456:Load)-[:GENERATES {
  revenue_date: "2025-10-29",
  revenue_type: "freight",
  recognition_status: "recognized"
}]->(Revenue2625:Revenue {
  revenue_id: "REV_20251029_001",
  entity: "origin",
  amount: 2625.00,
  source: "CONT001"
})

// Revenue from customer
(SunGlo:Contact)-[:GENERATES_REVENUE_FOR {
  ytd_revenue: 125000.00,
  avg_monthly: 10400.00
}]->(Origin:Company)

// Truck generates revenue
(Unit6531:Tractor)-[:GENERATES_REVENUE {
  ytd_total: 185000.00,
  avg_per_load: 2500.00
}]->(Revenue:FinancialHub)
```

### Expense Tracking

```cypher
// Maintenance generates expense
(OilChange:MaintenanceRecord)-[:GENERATES_EXPENSE]->(MaintenanceExpense:Expense {
  expense_id: "EXP_20251025_001",
  entity: "origin",
  expense_type: "maintenance",
  category: "asset",
  amount: 450.00,
  related_to: "6531",
  tax_deductible: true
})

// Fuel generates expense
(FuelPurchase:FuelTransaction)-[:GENERATES_EXPENSE]->(FuelExpense:Expense {
  expense_id: "EXP_20251028_002",
  entity: "origin",
  expense_type: "fuel",
  amount: 488.25,
  related_to: "6531"
})

// Vendor receives payment
(PhoenixTruckRepair:Contact)-[:RECEIVES {
  payment_date: "2025-10-26",
  payment_method: "ach"
}]->(Payment450:Payment {
  payment_id: "PAY_001",
  amount: 450.00
})
```

### Intercompany Flows âš¡

```cypher
// OpenHaul pays Origin for truck usage
(OpenHaul:Company)-[:TRANSACTS_WITH {
  transaction_date: "2025-10-29",
  transaction_type: "revenue_share",
  reconciliation_status: "reconciled"
}]->(IntercompanyTx:IntercompanyFlow {
  transaction_id: "IC_20251029_001",
  from_entity: "openhaul",
  to_entity: "origin",
  amount: 2100.00,
  reason: "Truck rental - Unit #6531 - Load #456"
})

(IntercompanyTx:IntercompanyFlow)-[:FROM]->(OpenHaul:Company)
(IntercompanyTx:IntercompanyFlow)-[:TO]->(Origin:Company)
(IntercompanyTx:IntercompanyFlow)-[:FOR_LOAD]->(Load456:Load)
```

### Invoicing

```cypher
// Invoice issued to customer
(Origin:Company)-[:ISSUES {
  invoice_date: "2025-10-29",
  due_date: "2025-11-28",
  payment_terms: "Net 30"
}]->(Invoice2625:Invoice {
  invoice_id: "INV_20251029_001",
  invoice_number: "INV-2025-1029",
  invoice_type: "accounts_receivable",
  amount: 2625.00,
  status: "sent"
})

(Invoice2625:Invoice)-[:ISSUED_TO]->(SunGlo:Contact)
(Invoice2625:Invoice)-[:FOR_LOAD]->(Load456:Load)
```

### Loan Tracking

```cypher
// Loan held by Origin
(Origin:Company)-[:HOLDS {
  loan_status: "active",
  payment_schedule: "monthly"
}]->(TruckLoan:Loan)

// Loan from bank
(TruckLoan:Loan)-[:FROM {
  lender_name: "BMO Financial"
}]->(BMOFinancial:Contact)

// Loan secures asset
(TruckLoan:Loan)-[:SECURES {
  collateral_type: "truck",
  collateral_value: 145000.00
}]->(Unit6531:Tractor)
```

---

## HUB 6: CORPORATE INFRASTRUCTURE

### Legal & Governance

```cypher
// Operating agreement governs company
(OperatingAgreement:LegalDocument {
  document_id: "DOC_OA_ORIGIN",
  document_type: "operating_agreement",
  effective_date: "2023-01-15",
  status: "active"
})-[:GOVERNS]->(Origin:Company)

// G signs documents
(G:Person)-[:SIGNS {
  signature_date: "2023-01-15",
  capacity: "managing_member"
}]->(OperatingAgreement:LegalDocument)
```

### State Filings

```cypher
// Annual report filed for Origin
(NevadaAnnualReport:StateFiling {
  filing_id: "FILE_NV_2025",
  filing_type: "annual_report",
  jurisdiction: "Nevada",
  filing_date: "2025-01-31",
  status: "filed"
})-[:FILED_BY]->(Origin:Company)

// Filing stored in Corporate Infrastructure
(CorporateInfra:CorporateInfrastructure)-[:TRACKS]->(NevadaAnnualReport:StateFiling)
```

### Brand Assets

```cypher
// Origin has brand guidelines
(OriginBrandGuide:BrandAsset {
  asset_id: "BRAND_ORIGIN_001",
  asset_type: "brand_guide",
  version: "v1.2",
  created_date: "2023-03-01"
})-[:BELONGS_TO]->(Origin:Company)

// Corporate Infrastructure manages brand
(CorporateInfra:CorporateInfrastructure)-[:DEFINES {
  brand_consistency: "high",
  update_frequency: "quarterly"
}]->(OriginBrandGuide:BrandAsset)
```

---

## COMPLETE LOAD LIFECYCLE EXAMPLE

### THE FULL STORY OF LOAD #456

```cypher
// 1. Customer places order
(SunGlo:Contact)-[:PLACES]->(Order123:SalesOrder)

// 2. OpenHaul books the load
(OpenHaul:Company)-[:BOOKS]->(Order123:SalesOrder)

// 3. OpenHaul contracts with Origin to haul
(OpenHaul:Company)-[:CONTRACTS_WITH {rate: 2100.00}]->(Origin:Company)

// 4. Origin assigns truck and driver
(Origin:Company)-[:DISPATCHES]->(Load456:Load)
(Load456:Load)-[:ASSIGNED_TO_UNIT]->(Unit6531:Tractor)
(Load456:Load)-[:ASSIGNED_TO_DRIVER]->(DanBarkow:Driver)
(Load456:Load)-[:USES_TRAILER]->(TrailerT001:Trailer)

// 5. Pickup and delivery locations
(Load456:Load)-[:PICKS_UP_AT]->(PhoenixWarehouse:Location)
(Load456:Load)-[:DELIVERS_TO]->(DallasDistribution:Location)

// 6. Fuel consumed during trip
(Unit6531:Tractor)-[:CONSUMES]->(FuelPurchase:FuelTransaction)
(FuelPurchase:FuelTransaction)-[:GENERATES_EXPENSE]->(FuelExpense:Expense)

// 7. Revenue generation
(Load456:Load)-[:GENERATES]->(Revenue2625:Revenue)
(Revenue2625:Revenue)-[:FROM]->(SunGlo:Contact)

// 8. Invoicing
(Origin:Company)-[:ISSUES]->(Invoice2625:Invoice)
(Invoice2625:Invoice)-[:FOR_LOAD]->(Load456:Load)
(Invoice2625:Invoice)-[:ISSUED_TO]->(SunGlo:Contact)

// 9. Intercompany settlement
(OpenHaul:Company)-[:PAYS {amount: 2100.00}]->(Origin:Company)

// 10. G tracks performance
(G:Person)-[:MONITORS]->(Load456:Load)
(G:Person)-[:ANALYZES {metric: "profitability", margin: 0.42}]->(Revenue2625:Revenue)
```

---

## COMPLEX QUERY EXAMPLES

### Fleet Profitability Analysis

```cypher
// How profitable is Unit #6531?

MATCH (Unit6531:Tractor {unit_number: "6531"})
  -[:GENERATES_REVENUE]->(rev:Revenue)
MATCH (Unit6531)-[:INCURS]->(exp:Expense)
MATCH (Unit6531)-[:FINANCED_BY]->(loan:Loan)

RETURN 
  Unit6531.unit_number,
  SUM(rev.amount) as total_revenue,
  SUM(exp.amount) as total_expenses,
  loan.monthly_payment * 12 as annual_loan_payment,
  (SUM(rev.amount) - SUM(exp.amount) - loan.monthly_payment * 12) as net_profit
```

### Customer Relationship Health

```cypher
// How is Sun-Glo performing?

MATCH (SunGlo:Contact {name: "Sun-Glo Foods"})
  -[:GENERATES_REVENUE_FOR]->(company)
MATCH (SunGlo)-[:OWES]->(invoice:Invoice)
MATCH (invoice)-[:PAID_BY]->(payment:Payment)

WITH SunGlo,
  SUM(payment.amount) as total_paid,
  AVG(duration.between(invoice.invoice_date, payment.payment_date).days) as avg_days_to_pay

RETURN
  SunGlo.name,
  SunGlo.ytd_revenue,
  total_paid,
  avg_days_to_pay,
  CASE 
    WHEN avg_days_to_pay <= 30 THEN "excellent"
    WHEN avg_days_to_pay <= 45 THEN "good"
    ELSE "needs_attention"
  END as payment_health
```

---

## TEMPORAL RELATIONSHIP EXAMPLES

### Driver Assignment History

```cypher
// Current assignment (valid_to = null)
(DanBarkow:Driver)-[:ASSIGNED_TO {
  assigned_date: "2025-10-01",
  end_date: null,
  valid_from: "2025-10-01T00:00:00Z",
  valid_to: null,
  assignment_type: "primary"
}]->(Unit6531:Tractor)

// Historical assignment (valid_to populated)
(DanBarkow:Driver)-[:ASSIGNED_TO {
  assigned_date: "2024-05-01",
  end_date: "2025-09-30",
  valid_from: "2024-05-01T00:00:00Z",
  valid_to: "2025-09-30T23:59:59Z",
  assignment_type: "primary"
}]->(Unit6533:Tractor)
```

### Customer Credit Status Changes

```cypher
// Current credit rating (valid_to = null)
(SunGlo:Contact)-[:HAS_CREDIT_RATING {
  credit_rating: "A",
  credit_limit: 50000.00,
  valid_from: "2025-01-01T00:00:00Z",
  valid_to: null,
  reason: "consistent_payment_history"
}]

// Historical - Previous rating (valid_to populated)
(SunGlo:Contact)-[:HAS_CREDIT_RATING {
  credit_rating: "B",
  credit_limit: 30000.00,
  valid_from: "2024-06-01T00:00:00Z",
  valid_to: "2024-12-31T23:59:59Z",
  reason: "new_customer_evaluation"
}]
```

---

## KEY INSIGHTS FOR ENGINEERING TEAM

### 1. Unit # is the Universal Identifier
Every truck-related entity links via `unit_number`:
- Maintenance → Unit #
- Fuel → Unit #
- Driver Assignment → Unit #
- Loads → Unit #
- Insurance → Unit #
- Revenue → Unit #
- Expenses → Unit #

### 2. Temporal Relationships Are Critical
Use `valid_from` / `valid_to` for relationships that change:
- Driver assignments
- Credit ratings
- Equipment status
- Partnership terms
- Contract renewals

### 3. Intercompany Flows Are Unique
Origin ↔ OpenHaul transactions require special tracking:
- Separate entity: `IntercompanyFlow`
- Both `FROM` and `TO` relationships
- Reconciliation status tracking
- Accounting treatment documentation

### 4. Multi-Hub Traversal Patterns
Common query patterns span multiple hubs:
- Load → Truck → Driver → Customer → Invoice → Payment
- Truck → Loan → Bank → Payment Schedule
- Customer → Orders → Loads → Revenue → Financials → G (oversight)

### 5. Contact Hub Is Universal
All external entities route through Contacts hub:
- Customers
- Vendors (maintenance, fuel, parts)
- Banks / Lenders
- Carriers
- Factoring companies
- Advisors
- Personal network

### 6. G Connects to Everything
Every major entity has path back to G:
- G → owns → Companies
- G → manages → Customers
- G → sets → Goals
- G → tracks → Projects
- G → monitors → Financials
- G → learns → Insights

---

## NEXT STEPS FOR IMPLEMENTATION

1. **Create Neo4j Constraints** - Enforce unique identifiers
2. **Build Sample Dataset** - Use these examples as seed data
3. **Test Query Performance** - Verify multi-hop traversals work
4. **Validate Temporal Logic** - Test time-based queries
5. **Document Edge Cases** - Handle unusual relationship scenarios

---

**END OF EXAMPLE CONNECTIONS DOCUMENT** ✅
