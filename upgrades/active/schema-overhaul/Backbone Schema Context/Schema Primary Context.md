# APEX MEMORY SCHEMA v1.1
**Knowledge Graph Entity Architecture**  
**Date:** November 1, 2025  
**Owner:** G (Richard Glaubitz)  
**Status:** v1.1 - Core Hubs + Subcategories Defined

---

## OVERVIEW

This schema defines the foundational entity architecture for Apex Memory System's multi-database knowledge graph. It establishes 6 independent hub entities that form the backbone of your business knowledge graph.

### Architecture Philosophy
- **Independent Hub Model:** 6 self-contained hub entities with cross-hub relationships
- **Temporal Intelligence:** All entities support bi-temporal tracking (valid_from/valid_to)
- **Multi-Database Mapping:** Entities optimized across Neo4j, PostgreSQL, Qdrant, Redis, Graphiti
- **Rich Relationships:** Connections carry meaningful metadata
- **Scalability:** Designed for growth from 100s to 100,000s of entities

---

## THE 6 INDEPENDENT HUB ENTITIES

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│      G      │     │   OpenHaul   │     │   Origin    │
│  (Command)  │     │  (Brokerage) │     │  (Trucking) │
└─────────────┘     └──────────────┘     └─────────────┘

┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  Contacts   │     │  Financials  │     │  Corporate  │
│    (CRM)    │     │ (Money Flows)│     │Infrastructure│
└─────────────┘     └──────────────┘     └─────────────┘

Each hub is independent and connects to others via relationships
```

---

## HUB 1: G (COMMAND CENTER) 🎯

**Type:** Person (Strategic Hub)  
**Purpose:** Your personal command center - strategic oversight and knowledge base  
**Database Primary:** Neo4j (connections) + PostgreSQL (data) + Qdrant (knowledge search)

### Core Properties
```yaml
entity_type: "person:command_center"
user_id: "g_main" (UNIQUE)
name: "G (Richard Glaubitz)"
email: "richard@origintransport.com"
role: "President | Co-Founder"
location: "Las Vegas, NV"
timezone: "America/Los_Angeles"

# Strategic Attributes
vision: "text" (long-term vision)
current_focus: [] (array of focus areas)
active_goals: [] (array of goal_ids)
decision_framework: {} (JSON - how you make decisions)
communication_style: "direct, action-oriented, high-energy"

# Temporal Tracking
created_at: timestamp
updated_at: timestamp
valid_from: timestamp
valid_to: null (always current)
```

### Subcategories

#### 1. Strategy
**Purpose:** Long-term plans, initiatives, competitive positioning
```yaml
- Business strategies
- Market expansion plans
- Competitive analysis
- Strategic decisions
- Vision documents
```

#### 2. Projects
**Purpose:** Active initiatives and their status
```yaml
- Project definitions
- Milestones and timelines
- Resource allocation
- Project status tracking
- Deliverables
```

#### 3. Insights
**Purpose:** Learnings, patterns, discoveries
```yaml
- AI-generated insights
- Market observations
- Competitive intelligence
- Pattern detection
- Opportunity identification
```

#### 4. Knowledge Hub
**Purpose:** Your personal reference library
```yaml
- Research documents
- Logins/Passwords/Tokens (encrypted)
- Workflows and SOPs
- Templates
- Best practices
- Industry research
```

### Key Relationships (Examples)
```cypher
(G)-[:OWNS]->(OpenHaul)
(G)-[:OWNS]->(Origin)
(G)-[:MANAGES]->(Contact)
(G)-[:SETS]->(Strategy)
(G)-[:TRACKS]->(Project)
(G)-[:LEARNS]->(Insight)
(G)-[:STORES]->(KnowledgeHub)
(G)-[:MAKES]->(Decision)
```

### Database Distribution
- **Neo4j:** Hub node + all ownership/management relationships
- **PostgreSQL:** Personal preferences, goals, strategies, project data
- **Qdrant:** Semantic search on insights, research, knowledge hub
- **Redis:** Current focus, active projects
- **Graphiti:** Evolution of strategies, decision patterns over time

---

## HUB 2: OPENHAUL LOGISTICS 🚚

**Type:** Company (Operating Entity)  
**Purpose:** Asset-light brokerage business  
**Database Primary:** Neo4j (operations) + PostgreSQL (financial data)

### Core Properties
```yaml
entity_type: "company:openhaul"
company_id: "OPENHAUL" (UNIQUE)
legal_name: "OpenHaul Logistics LLC"
dba: "OpenHaul"
entity_structure: "LLC"
founded_date: timestamp
status: "active"

# Business Model
business_type: "freight_brokerage"
asset_type: "asset_light"
specialization: "refrigerated_ltl"

# Operational Metrics
active_customers: count
active_carriers: count
monthly_loads: count
avg_margin: percentage

# Financial Overview
ytd_revenue: amount
ytd_profit: amount
target_revenue: amount

# Temporal Tracking
created_at: timestamp
updated_at: timestamp
valid_from: timestamp
valid_to: null
```

### Subcategories

#### 1. Carriers
**Purpose:** Third-party trucking companies that haul OpenHaul freight
```yaml
Properties:
- carrier_id (UNIQUE)
- company_name
- mc_number
- dot_number
- insurance_status
- performance_rating
- preferred_lanes
- payment_terms
- contact_info
```

#### 2. Factoring Companies
**Purpose:** Financial services for quick payment processing
```yaml
Properties:
- factoring_company_id (UNIQUE)
- company_name
- discount_rate
- advance_percentage
- payment_speed
- relationship_status
- volume_ytd
```

#### 3. Sales Orders
**Purpose:** Customer freight orders placed with OpenHaul
```yaml
Properties:
- order_id (UNIQUE)
- customer_id (links to Contacts hub)
- origin/destination
- rate_agreed
- special_instructions
- order_date
- status
```

#### 4. Loads (Brokered)
**Purpose:** Actual freight movements brokered to carriers
```yaml
Properties:
- load_id (UNIQUE)
- order_id (links to Sales Order)
- carrier_id (links to Carrier)
- pickup_date/delivery_date
- rate_to_carrier
- margin
- status (booked/in_transit/delivered)
```

### Key Relationships (Examples)
```cypher
(OpenHaul)-[:BOOKS]->(SalesOrder)
(OpenHaul)-[:BROKERS_TO]->(Carrier)
(OpenHaul)-[:USES_FACTORING]->(FactoringCompany)
(OpenHaul)-[:MANAGES]->(Load:Brokered)
(OpenHaul)-[:SERVES]->(Contact:Customer)
(OpenHaul)-[:GENERATES]->(Revenue)
(OpenHaul)-[:INCURS]->(Expense)
(OpenHaul)-[:OWNED_BY]->(G)
```

### Database Distribution
- **Neo4j:** Company relationships, load flow, carrier network
- **PostgreSQL:** Financial transactions, customer orders, load details
- **Qdrant:** Document search (carrier contracts, rate agreements)
- **Redis:** Real-time load status, active orders
- **Graphiti:** Business evolution, carrier performance trends

---

## HUB 3: ORIGIN TRANSPORT 🚛

**Type:** Company (Operating Entity)  
**Purpose:** Asset-based trucking company  
**Database Primary:** Neo4j (assets) + PostgreSQL (maintenance)

### Core Properties
```yaml
entity_type: "company:origin"
company_id: "ORIGIN" (UNIQUE)
legal_name: "Origin Transport LLC"
dba: "Origin Transport"
entity_structure: "LLC"
founded_date: timestamp
status: "active"

# Business Model
business_type: "trucking_company"
asset_type: "asset_based"
specialization: "refrigerated_transportation"

# Fleet Overview
total_trucks: count
total_trailers: count
total_drivers: count
fleet_utilization: percentage

# Operational Metrics
monthly_miles: count
avg_mpg: number
on_time_delivery: percentage

# Financial Overview
ytd_revenue: amount
ytd_profit: amount
target_revenue: amount

# Temporal Tracking
created_at: timestamp
updated_at: timestamp
valid_from: timestamp
valid_to: null
```

### Subcategories

#### 1. Fleet
**Purpose:** All physical assets (tractors and trailers)

##### 1A. Tractors (PRIMARY ASSET)
**Key Concept:** Unit # is the anchor point for everything

**Example: Unit #6533**
```yaml
Properties:
- unit_number: "6533" (UNIQUE - PRIMARY KEY)
- make: "Kenworth"
- model: "T680"
- year: 2023
- vin: "1XKYDP9X..."
- status: "active"
- purchase_date: timestamp
- current_value: amount

Sub-Entities (all link to unit_number):
├── Insurance
│   ├── policy_number
│   ├── provider
│   ├── coverage_amount
│   ├── expiry_date
│   └── monthly_premium
│
├── Repairs & Maintenance
│   ├── maintenance_id
│   ├── service_date
│   ├── description
│   ├── cost
│   ├── vendor
│   └── next_service_due
│
├── Equipment Specs
│   ├── engine_type
│   ├── transmission
│   ├── axle_configuration
│   ├── fuel_capacity
│   └── weight_rating
│
├── Maintenance Intervals
│   ├── oil_change: "every 15,000 miles"
│   ├── tire_rotation: "every 25,000 miles"
│   ├── dot_inspection: "annual"
│   └── pm_service: "every 30,000 miles"
│
├── Odometer/Miles
│   ├── current_miles: 85000
│   ├── miles_history: [] (array of readings)
│   └── avg_monthly_miles: 8500
│
├── Driver Assignments (TEMPORAL)
│   ├── assignment_id
│   ├── driver_id
│   ├── assigned_date
│   ├── end_date (null if current)
│   └── assignment_type: "primary" | "temporary"
│
└── Load History
    ├── load_id
    ├── date
    ├── miles
    └── revenue
```

##### 1B. Trailers
**Same structure as tractors but for trailers**
```yaml
Properties:
- unit_number: "T-001" (UNIQUE)
- type: "Refrigerated Van"
- reefer_unit_specs
- Insurance
- Maintenance Records
- Assignments (to tractors)
```

#### 2. Fuel
**Purpose:** Fuel consumption tracking per unit
```yaml
Properties:
- fuel_transaction_id (UNIQUE)
- unit_number (links to Tractor)
- transaction_date
- gallons
- price_per_gallon
- total_cost
- location
- odometer_reading
- mpg_calculated
```

#### 3. Drivers
**Purpose:** People who operate the trucks
```yaml
Properties:
- driver_id (UNIQUE)
- name
- cdl_number
- cdl_expiry
- hire_date
- status: "active" | "on_leave" | "terminated"
- current_unit_assignment (links to Tractor unit_number)
- pay_structure
- performance_metrics

Relationships:
- ASSIGNED_TO → Tractor (via unit_number)
- Changes frequently - tracked temporally
```

#### 4. Loads (Owned/Hauled)
**Purpose:** Freight hauled by Origin trucks
```yaml
Properties:
- load_id (UNIQUE)
- unit_number (links to Tractor)
- driver_id (links to Driver)
- customer_id (links to Contacts hub)
- pickup_date/delivery_date
- origin/destination
- rate
- miles
- revenue
- profit
- status

Key Insight: Each load connects to BOTH unit AND driver
```

### Key Relationships (Examples)
```cypher
(Origin)-[:OPERATES]->(Tractor:Unit6533)
(Tractor:Unit6533)-[:HAS_INSURANCE]->(Insurance)
(Tractor:Unit6533)-[:REQUIRES_MAINTENANCE]->(MaintenanceRecord)
(Tractor:Unit6533)-[:CONSUMES]->(FuelTransaction)
(Tractor:Unit6533)-[:ASSIGNED_TO]->(Driver) [temporal]
(Tractor:Unit6533)-[:HAULS]->(Load)
(Driver)-[:OPERATES]->(Tractor:Unit6533)
(Driver)-[:HAULS]->(Load)
(Load)-[:HAULED_BY_UNIT]->(Tractor:Unit6533)
(Load)-[:HAULED_BY_DRIVER]->(Driver)
(Origin)-[:GENERATES]->(Revenue)
(Origin)-[:INCURS]->(Expense)
(Origin)-[:OWNED_BY]->(G)
```

### Database Distribution
- **Neo4j:** Asset relationships, driver-to-unit assignments, load connections
- **PostgreSQL:** Maintenance records, fuel transactions, compliance data
- **Qdrant:** Document search (safety docs, training materials, specs)
- **Redis:** Real-time truck locations, driver status, current assignments
- **Graphiti:** Fleet evolution, asset lifecycle, driver performance over time

---

## HUB 4: CONTACTS (UNIVERSAL CRM) 💰

**Type:** Universal Contact Management  
**Purpose:** All people and companies you do business with  
**Database Primary:** Neo4j (connections) + PostgreSQL (transactions)

### Core Properties
```yaml
entity_type: "contact"
contact_id: "CONT{number}" (UNIQUE)
contact_type: ["customer", "vendor", "bank", "advisor", "personal", "government"]
name: "Company or Person Name"
legal_name: "Legal Entity Name"
status: ["active", "inactive", "prospect", "archived"]

# Classification
primary_role: "customer" (can have multiple roles)
secondary_roles: ["vendor"] (e.g., a customer who also provides services)

# Contact Details
email: "contact@company.com"
phone: "+1-555-555-0100"
address: "full address"

# Business Details (if applicable)
industry: "text"
company_size: ["small", "medium", "large", "enterprise"]

# Temporal Tracking
contact_start: timestamp
created_at: timestamp
updated_at: timestamp
valid_from: timestamp
valid_to: null (unless archived)
```

### Subcategories (Contact Types)

#### 1. Customers
**Purpose:** Revenue-generating relationships
```yaml
Additional Properties:
- revenue_tier: ["tier1", "tier2", "tier3"]
- total_lifetime_value: amount
- ytd_revenue: amount
- avg_monthly_volume: count
- avg_margin: percentage
- credit_rating: ["A", "B", "C", "D"]
- payment_terms: "Net 30"
- credit_limit: amount
- risk_score: 0.0-1.0
- payment_reliability: 0.0-1.0
- account_manager: "person"

Sub-Entities:
├── Contacts (decision makers)
├── Locations (shippers/receivers)
├── Orders
├── Invoices
└── Payment History
```

#### 2. Vendors
**Purpose:** Service providers (expense-generating)
```yaml
Additional Properties:
- vendor_type: ["maintenance", "fuel", "insurance", "parts", "technology", "professional_services"]
- payment_terms: "Net 15"
- w9_on_file: boolean
- rating: 1-5 stars
- total_spend_ytd: amount
- preferred: boolean

Sub-Entities:
├── Contacts
├── Purchase Orders
├── Invoices Received
└── Payment History
```

#### 3. Banks & Lenders
**Purpose:** Financial institutions providing capital
```yaml
Additional Properties:
- institution_type: ["bank", "credit_union", "lender", "factoring"]
- relationship_manager: "name"
- total_credit_exposure: amount
- interest_rates: {}
- loan_products: []

Sub-Entities:
├── Loans (links to Financials hub)
├── Credit Lines
├── Banking Accounts
└── Loan Documents
```

#### 4. Advisors
**Purpose:** Professional services (legal, accounting, consulting)
```yaml
Additional Properties:
- advisor_type: ["legal", "accounting", "consulting", "insurance_broker", "other"]
- specialization: "text"
- hourly_rate: amount
- retainer: boolean

Sub-Entities:
├── Contacts
├── Engagements
├── Invoices
└── Documents/Work Product
```

#### 5. Personal Contacts
**Purpose:** Personal network (non-business)
```yaml
Additional Properties:
- relationship_nature: ["family", "friend", "mentor", "networking"]
- notes: "text"
```

#### 6. Government Entities
**Purpose:** Regulatory and compliance contacts
```yaml
Additional Properties:
- agency_type: ["DOT", "IRS", "State_DMV", "EPA", "OSHA"]
- jurisdiction: "Federal" | "State:NV"
- account_number: "if applicable"

Sub-Entities:
├── Filings
├── Licenses
├── Inspections
└── Correspondence
```

### Key Relationships (Examples)
```cypher
(Contact:Customer)-[:DOES_BUSINESS_WITH]->(OpenHaul|Origin)
(Contact:Customer)-[:HAS_DECISION_MAKER]->(Person)
(Contact:Customer)-[:HAS_LOCATION]->(Shipper|Receiver)
(Contact:Customer)-[:PLACES]->(Order)
(Contact:Customer)-[:GENERATES]->(Revenue)
(Contact:Customer)-[:OWES]->(Invoice)

(Contact:Vendor)-[:PROVIDES_SERVICE_TO]->(OpenHaul|Origin)
(Contact:Vendor)-[:RECEIVES]->(Payment)
(Contact:Vendor)-[:GENERATES]->(Expense)

(Contact:Bank)-[:LENDS_TO]->(OpenHaul|Origin)
(Contact:Bank)-[:HOLDS_ACCOUNT_FOR]->(G|OpenHaul|Origin)

(Contact)-[:MANAGED_BY]->(G)
```

### Database Distribution
- **Neo4j:** Contact network mapping, business relationship graph
- **PostgreSQL:** Transaction history, invoices, orders, contact details
- **Qdrant:** Contract/agreement semantic search, communication history
- **Redis:** Active contacts, quick contact lookup
- **Graphiti:** Contact evolution, payment patterns, interaction history

---

## HUB 5: FINANCIALS 💵

**Type:** Abstract Hub (Money Flows)  
**Purpose:** All financial transactions and metrics across all entities  
**Database Primary:** PostgreSQL (transactions) + Neo4j (relationships)

### Core Properties
```yaml
entity_type: "financial_hub"
hub_id: "FINANCIALS" (UNIQUE)

# High-Level Metrics (Aggregated)
total_revenue_ytd: amount
total_expenses_ytd: amount
net_profit_ytd: amount
profit_margin_ytd: percentage
cash_position: amount

# Revenue Streams (by company)
openhaul_revenue: amount
origin_revenue: amount
other_revenue: amount

# Expense Categories
operating_expenses: amount
asset_expenses: amount
administrative_expenses: amount

# Goals & Targets
revenue_target_annual: amount
profit_target_annual: amount
margin_target: percentage

# Temporal Tracking
created_at: timestamp
updated_at: timestamp
reporting_period: "monthly" | "quarterly" | "annual"
```

### Subcategories

#### 1. Revenue
**Purpose:** All money coming in
```yaml
Properties:
- revenue_id (UNIQUE)
- entity: "openhaul" | "origin" | "g_personal"
- revenue_type: ["freight", "brokerage", "accessorial", "other"]
- amount: decimal
- revenue_date: timestamp
- source: relationship_id (links to Relationships hub)
- related_to: load_id | order_id
- invoice_id: (if invoiced)
- payment_received: boolean
- recognition_status: ["pending", "recognized"]
```

#### 2. Expenses
**Purpose:** All money going out
```yaml
Properties:
- expense_id (UNIQUE)
- entity: "openhaul" | "origin" | "g_personal"
- expense_type: ["fuel", "maintenance", "insurance", "wages", "rent", "technology", "professional_services", "other"]
- category: "operating" | "asset" | "administrative"
- amount: decimal
- expense_date: timestamp
- vendor: relationship_id (links to Relationships hub)
- related_to: unit_number | project_id | general
- payment_status: ["pending", "paid"]
- tax_deductible: boolean
```

#### 3. Loans
**Purpose:** Debt obligations
```yaml
Properties:
- loan_id (UNIQUE)
- entity: "openhaul" | "origin" | "g_personal"
- lender: relationship_id (links to Relationships hub)
- loan_type: ["equipment", "line_of_credit", "term_loan", "sba", "personal"]
- original_amount: decimal
- current_balance: decimal
- interest_rate: percentage
- monthly_payment: decimal
- origination_date: timestamp
- maturity_date: timestamp
- collateral: "unit_number" | "property" | "unsecured"
- status: "active" | "paid_off" | "defaulted"
```

#### 4. Contracts (Recurring Expenses)
**Purpose:** Repeating obligations
```yaml
Properties:
- contract_id (UNIQUE)
- entity: "openhaul" | "origin" | "g_personal"
- contract_type: ["lease", "software_subscription", "insurance_premium", "service_contract"]
- vendor: relationship_id (links to Relationships hub)
- monthly_amount: decimal
- annual_amount: decimal
- start_date: timestamp
- end_date: timestamp
- renewal_terms: "text"
- auto_renew: boolean
- status: "active" | "expired" | "cancelled"
```

#### 5. Assets
**Purpose:** Things we own that have value
```yaml
Properties:
- asset_id (UNIQUE)
- entity: "openhaul" | "origin" | "g_personal"
- asset_type: ["truck", "trailer", "real_estate", "equipment", "intellectual_property"]
- asset_identifier: "unit_number" | "address" | "description"
- purchase_date: timestamp
- purchase_price: decimal
- current_value: decimal
- depreciation_schedule: {}
- financing_status: "owned" | "financed" | "leased"
- related_loan: loan_id (if applicable)
```

#### 6. Credit Scores
**Purpose:** Credit health tracking
```yaml
Properties:
- score_id (UNIQUE)
- entity: "openhaul" | "origin" | "g_personal"
- score_type: "business_credit" | "personal_credit"
- bureau: "Experian" | "Equifax" | "TransUnion" | "Dun & Bradstreet"
- score: number
- score_date: timestamp
- factors: [] (array of score factors)
- trend: "improving" | "declining" | "stable"
```

#### 7. Intercompany Flows ⚡
**Purpose:** Money moving between Origin and OpenHaul
```yaml
Properties:
- transaction_id (UNIQUE)
- from_entity: "openhaul" | "origin"
- to_entity: "openhaul" | "origin"
- transaction_type: ["revenue_share", "expense_allocation", "loan", "equity_contribution", "management_fee"]
- amount: decimal
- transaction_date: timestamp
- reason: "text description"
- accounting_treatment: "text"
- reconciliation_status: "pending" | "reconciled"

Critical: This tracks all money flowing between the two companies
- OpenHaul pays Origin for truck usage
- Origin charges OpenHaul for brokered loads
- Shared expense allocations
- Management fees
```

### Key Relationships (Examples)
```cypher
(Financials)-[:TRACKS]->(Revenue)
(Financials)-[:TRACKS]->(Expense)
(Financials)-[:TRACKS]->(Loan)
(Financials)-[:TRACKS]->(Contract)
(Financials)-[:TRACKS]->(Asset)
(Financials)-[:TRACKS]->(CreditScore)
(Financials)-[:CONTAINS]->(IntercompanyFlow)

(Revenue)-[:GENERATED_BY]->(OpenHaul|Origin)
(Revenue)-[:FROM]->(Relationship:Customer)
(Revenue)-[:RELATED_TO]->(Load|Order)

(Expense)-[:INCURRED_BY]->(OpenHaul|Origin|G)
(Expense)-[:PAID_TO]->(Relationship:Vendor)
(Expense)-[:RELATED_TO]->(Tractor|Project)

(Loan)-[:HELD_BY]->(OpenHaul|Origin|G)
(Loan)-[:FROM]->(Relationship:Bank)

(Asset)-[:OWNED_BY]->(OpenHaul|Origin|G)
(Asset)-[:IS]->(Tractor|Trailer) [if vehicle]

(IntercompanyFlow)-[:FROM]->(OpenHaul|Origin)
(IntercompanyFlow)-[:TO]->(OpenHaul|Origin)

(Financials)-[:MANAGED_BY]->(G)
```

### Database Distribution
- **Neo4j:** Financial relationships, money flow paths, entity connections
- **PostgreSQL:** Transaction data, invoice details (PRIMARY), accounting records
- **Qdrant:** Financial document search (contracts, loan docs, reports)
- **Redis:** Real-time P&L, cash position, account balances
- **Graphiti:** Financial trend analysis, pattern detection, credit history

---

## HUB 6: CORPORATE INFRASTRUCTURE 🏢

**Type:** Organizational Foundation  
**Purpose:** Legal, compliance, brand, and strategic documents spanning all entities  
**Database Primary:** PostgreSQL (documents) + Qdrant (semantic search) + Neo4j (relationships)

### Core Properties
```yaml
entity_type: "corporate_infrastructure"
hub_id: "CORPORATE_INFRA" (UNIQUE)

# Organizational Overview
entities_managed: ["openhaul", "origin", "g_personal"]
incorporation_state: "Nevada"
tax_classification: {}

# Status Tracking
compliance_status: "current" | "needs_attention"
licenses_current: boolean
filings_current: boolean

# Temporal Tracking
created_at: timestamp
updated_at: timestamp
```

### Subcategories

#### 1. Legal Documents
**Purpose:** Formation and governance documents
```yaml
Sub-Types:
- Operating Agreements
- Articles of Organization
- Partnership Agreements
- Shareholder Agreements
- Buy-Sell Agreements

Properties:
- document_id (UNIQUE)
- entity: "openhaul" | "origin" | "both"
- document_type: "operating_agreement" | "articles"
- effective_date: timestamp
- last_amended: timestamp
- file_location: "url"
- status: "active" | "superseded" | "archived"
```

#### 2. State Filings
**Purpose:** Government registrations and compliance
```yaml
Sub-Types:
- Business License Renewals
- Annual Reports
- Fictitious Name Statements
- Certificate of Good Standing
- Foreign Qualification (if operating in other states)

Properties:
- filing_id (UNIQUE)
- entity: "openhaul" | "origin"
- filing_type: "annual_report" | "license_renewal"
- jurisdiction: "Nevada" | "Federal" | "State:AZ"
- filing_date: timestamp
- due_date: timestamp
- status: "filed" | "pending" | "overdue"
- confirmation_number: "text"
- file_location: "url"
```

#### 3. Tax Documents
**Purpose:** Tax filings and returns
```yaml
Sub-Types:
- Annual Tax Returns (1120, 1065, 1040)
- Quarterly Estimated Payments
- W-2s / 1099s
- Sales Tax Returns
- IFTA Returns (fuel tax)

Properties:
- tax_document_id (UNIQUE)
- entity: "openhaul" | "origin" | "g_personal"
- document_type: "1120" | "1065" | "1040" | "941" | "ifta"
- tax_year: number
- filing_date: timestamp
- due_date: timestamp
- extended_due_date: timestamp (if applicable)
- filed_by: "accountant_name"
- status: "filed" | "pending" | "amended"
- file_location: "url"
```

#### 4. EIN Letters
**Purpose:** Tax identification documents
```yaml
Properties:
- ein_id (UNIQUE)
- entity: "openhaul" | "origin"
- ein: "XX-XXXXXXX"
- issue_date: timestamp
- file_location: "url"
- notes: "text"
```

#### 5. Branding & Marketing
**Purpose:** Brand assets and marketing materials
```yaml
Sub-Types:
- Logos and Visual Identity
- Brand Guidelines
- Marketing Collateral
- Website Content
- Social Media Guidelines

Properties:
- asset_id (UNIQUE)
- entity: "openhaul" | "origin" | "both"
- asset_type: "logo" | "brand_guide" | "marketing_material"
- file_format: "pdf" | "png" | "svg" | "video"
- version: "v1.2"
- created_date: timestamp
- last_updated: timestamp
- file_location: "url"
- usage_rights: "text"
```

#### 6. Company Voice
**Purpose:** Communication standards and brand voice
```yaml
Properties:
- voice_id (UNIQUE)
- entity: "openhaul" | "origin"
- voice_characteristics: {} (JSON)
  - tone: "professional yet approachable"
  - language_style: "direct, clear"
  - key_phrases: []
  - avoid_phrases: []
- communication_examples: [] (array of examples)
- last_updated: timestamp
```

#### 7. Business Plans
**Purpose:** Strategic planning documents
```yaml
Properties:
- plan_id (UNIQUE)
- entity: "openhaul" | "origin" | "both"
- plan_type: "annual_business_plan" | "expansion_plan" | "strategic_initiative"
- fiscal_year: number
- created_date: timestamp
- last_updated: timestamp
- status: "active" | "archived"
- key_objectives: [] (array)
- financial_projections: {}
- file_location: "url"
```

#### 8. Company Story & Vision
**Purpose:** Narrative and mission
```yaml
Properties:
- story_id (UNIQUE)
- entity: "openhaul" | "origin"
- mission_statement: "text"
- vision_statement: "text"
- origin_story: "text"
- core_values: [] (array)
- competitive_advantages: [] (array)
- target_market: "text"
- version: "v1.0"
- last_updated: timestamp
```

### Key Relationships (Examples)
```cypher
(CorporateInfra)-[:GOVERNS]->(OpenHaul|Origin)
(CorporateInfra)-[:CONTAINS]->(LegalDocument)
(CorporateInfra)-[:REQUIRES]->(StateFiling)
(CorporateInfra)-[:TRACKS]->(TaxDocument)
(CorporateInfra)-[:DEFINES]->(BrandAsset)
(CorporateInfra)-[:ESTABLISHES]->(CompanyVoice)
(CorporateInfra)-[:GUIDES]->(BusinessPlan)
(CorporateInfra)-[:EXPRESSES]->(CompanyStory)

(LegalDocument)-[:APPLIES_TO]->(OpenHaul|Origin)
(StateFiling)-[:FILED_BY]->(OpenHaul|Origin)
(TaxDocument)-[:FILED_BY]->(OpenHaul|Origin|G)
(BrandAsset)-[:BELONGS_TO]->(OpenHaul|Origin)

(CorporateInfra)-[:MANAGED_BY]->(G)
```

### Database Distribution
- **Neo4j:** Relationships between documents and entities
- **PostgreSQL:** Document metadata, filing records, dates and deadlines
- **Qdrant:** Full-text search across all corporate documents (PRIMARY for search)
- **Redis:** Upcoming filing deadlines, compliance alerts
- **Graphiti:** Corporate evolution, document versioning, filing history

---

## CROSS-HUB RELATIONSHIPS

## CROSS-HUB RELATIONSHIPS

### How the 6 Core Hubs Connect

```cypher
# Ownership & Governance
(G)-[:OWNS]->(OpenHaul)
(G)-[:OWNS]->(Origin)
(G)-[:MANAGES]->(Contact)
(G)-[:OVERSEES]->(Financials)
(G)-[:GOVERNS]->(CorporateInfra)

# Business Operations
(OpenHaul)-[:SERVES]->(Contact:Customer)
(OpenHaul)-[:USES]->(Contact:Carrier)
(OpenHaul)-[:BROKERS]->(Load:Brokered)
(Origin)-[:SERVES]->(Contact:Customer)
(Origin)-[:OPERATES]->(Tractor|Trailer)
(Origin)-[:EMPLOYS]->(Driver)
(Origin)-[:HAULS]->(Load:Owned)

# Financial Flows
(OpenHaul)-[:GENERATES]->(Revenue)
(OpenHaul)-[:INCURS]->(Expense)
(OpenHaul)-[:TRANSACTS_WITH]->(Origin) [via IntercompanyFlow]
(Origin)-[:GENERATES]->(Revenue)
(Origin)-[:INCURS]->(Expense)
(Origin)-[:TRANSACTS_WITH]->(OpenHaul) [via IntercompanyFlow]
(Contact:Customer)-[:GENERATES_REVENUE_FOR]->(OpenHaul|Origin)
(Contact:Vendor)-[:GENERATES_EXPENSE_FOR]->(OpenHaul|Origin)
(Contact:Bank)-[:LENDS_TO]->(OpenHaul|Origin)

# Corporate Infrastructure
(CorporateInfra)-[:GOVERNS]->(OpenHaul|Origin)
(CorporateInfra)-[:DEFINES_BRAND_FOR]->(OpenHaul|Origin)
(CorporateInfra)-[:CONTAINS_FILINGS_FOR]->(OpenHaul|Origin|G)

# Asset Tracking
(Tractor:Unit6533)-[:OWNED_BY]->(Origin)
(Tractor:Unit6533)-[:ASSIGNED_TO]->(Driver)
(Tractor:Unit6533)-[:HAULS]->(Load)
(Tractor:Unit6533)-[:CONSUMES]->(FuelTransaction)
(Tractor:Unit6533)-[:GENERATES]->(Revenue)
(Tractor:Unit6533)-[:INCURS]->(Expense)

# Strategic Oversight
(G)-[:SETS_STRATEGY_FOR]->(OpenHaul|Origin)
(G)-[:MONITORS]->(Financials)
(G)-[:TRACKS]->(Project)
(G)-[:LEARNS]->(Insight)
```

---

## DATABASE MAPPING STRATEGY

### Entity Distribution Across Apex Memory Databases

| Hub | Neo4j | PostgreSQL | Qdrant | Redis | Graphiti |
|-----|-------|-----------|--------|-------|----------|
| **G** | ✅ Ownership + Oversight | ✅ Strategies + Goals | ✅ Knowledge Hub | ✅ Current Focus | ✅ Decision Evolution |
| **OpenHaul** | ✅ Operations Network | ✅ Orders + Transactions | ✅ Contracts | ✅ Active Loads | ✅ Business Trends |
| **Origin** | ✅ Asset Relationships | ✅ Maintenance + Fuel | ✅ Safety Docs | ✅ Real-time Status | ✅ Fleet Lifecycle |
| **Contacts** | ✅ Network Mapping | ✅ Transactions + Contact Details | ✅ Communications | ✅ Active Accounts | ✅ Contact Patterns |
| **Financials** | ✅ Money Flow Paths | ✅ Transactions* (PRIMARY) | ✅ Financial Docs | ✅ Real-time P&L | ✅ Trend Analysis |
| **Corporate Infra** | ✅ Entity Connections | ✅ Filings + Metadata | ✅ Document Search* (PRIMARY) | ✅ Deadlines | ✅ Filing History |

**Key Database Roles:**
- **Neo4j:** Relationship mapping, graph traversal, network analysis
- **PostgreSQL:** Transactional data, structured records (PRIMARY for financial transactions)
- **Qdrant:** Semantic document search (PRIMARY for corporate documents)
- **Redis:** Real-time data, caching, quick lookups
- **Graphiti:** Temporal analysis, pattern detection, evolution tracking

---

## TEMPORAL INTELLIGENCE

### Bi-Temporal Tracking (Graphiti Integration)

Every entity supports two time dimensions:

1. **Valid Time** (Business Reality)
   - `valid_from`: When this data became true in the real world
   - `valid_to`: When this data stopped being true (null = still valid)

2. **Transaction Time** (System Knowledge)
   - `created_at`: When we learned this information
   - `updated_at`: When we last modified this information

### Example Temporal Queries

```cypher
// How has customer ACME changed over time?
MATCH (c:Customer {customer_id: "CUST001"})
RETURN c.credit_rating, c.valid_from, c.valid_to
ORDER BY c.valid_from DESC;

// What was Origin's fleet size in Q1 2025?
MATCH (o:Origin)
WHERE o.valid_from <= datetime("2025-03-31") 
  AND (o.valid_to IS NULL OR o.valid_to > datetime("2025-01-01"))
RETURN o.total_trucks;
```

---

## QUERY ROUTER OPTIMIZATION

### How Apex Routes Queries for These Hubs

| Query Pattern | Primary Database | Secondary | Why |
|--------------|-----------------|-----------|-----|
| "What does G own?" | Neo4j | - | Graph traversal |
| "OpenHaul revenue last month" | PostgreSQL | Redis | Time-series financial data |
| "Origin truck #6533 maintenance history" | PostgreSQL | Neo4j | Structured maintenance records |
| "Find similar customers to ACME" | Qdrant | Neo4j | Semantic similarity |
| "Origin truck locations right now" | Redis | Neo4j | Real-time data |
| "Financial trends Q1-Q4" | Graphiti | PostgreSQL | Temporal patterns |
| "When is Nevada annual report due?" | PostgreSQL | Redis | Filing deadlines |
| "Find all contracts with vendor XYZ" | Qdrant | PostgreSQL | Document semantic search |
| "Intercompany transactions last quarter" | PostgreSQL | Neo4j | Financial query with relationships |
| "Driver assignment history for Unit #6533" | Graphiti | Neo4j | Temporal relationship tracking |

---

## SCHEMA SUMMARY

### What We've Defined

**6 Independent Hub Entities:**
1. **G** (Command Center) - Strategy, Projects, Insights, Knowledge Hub
2. **OpenHaul** (Brokerage) - Carriers, Factoring, Sales Orders, Loads
3. **Origin** (Trucking) - Fleet (Tractors/Trailers by Unit #), Fuel, Drivers, Loads
4. **Relationships** (Universal CRM) - Customers, Vendors, Banks, Advisors, Personal, Government
5. **Financials** (Money Flows) - Revenue, Expenses, Loans, Contracts, Assets, Credit, Intercompany Flows
6. **Corporate Infrastructure** (Foundation) - Legal, Filings, Tax, Brand, Vision

### Key Design Decisions

**✅ Unit # as Primary Key:** Every truck (e.g., Unit #6533) is the anchor for insurance, maintenance, fuel, driver assignments, and loads.

**✅ Universal CRM:** "Relationships" hub handles all contact types (customers, vendors, banks, etc.) with shared structure.

**✅ Intercompany Tracking:** Dedicated subcategory under Financials for Origin ↔ OpenHaul money flows.

**✅ Temporal Intelligence:** All entities support bi-temporal tracking (valid_from/valid_to + created_at/updated_at).

**✅ Multi-Database Optimization:** Each hub strategically distributed across Neo4j, PostgreSQL, Qdrant, Redis, and Graphiti.

### Next Iteration: Implementation

**Phase 1:** Create Neo4j constraints and indexes for all 6 hubs
**Phase 2:** Define PostgreSQL schemas for transaction data
**Phase 3:** Configure Qdrant collections for document search
**Phase 4:** Set up Redis cache patterns
**Phase 5:** Initialize Graphiti temporal tracking
**Phase 6:** Build data ingestion pipelines

---

**Schema v1.1 Complete** ✅
