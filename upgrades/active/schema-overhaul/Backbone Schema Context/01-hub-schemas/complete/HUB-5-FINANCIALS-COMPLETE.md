# HUB 5: FINANCIALS (MONEY FLOWS)

**Status:** ✅ Complete Baseline - Full Detail Documented
**Purpose:** Track where money goes, where it comes from, performance insights, profitability analysis
**Approach:** Operational view (not full accounting) - track performance, spot trends, identify exposure
**Primary Key Strategy:** Invoice/Payment/Expense/Revenue use UUIDs, link to other entities via their keys
**QuickBooks Integration:** ✅ Complete Origin + OpenHaul chart of accounts integrated

---

## Purpose

Hub 5 tracks all financial flows for Origin Transport and OpenHaul Logistics. This is the "backend" of operations - what actually got paid and what actually got received.

**Key Objectives:**
1. **Performance Tracking** - Understand profitability by truck, load, customer, route, driver
2. **Trend Detection** - Spot increasing costs, revenue patterns, seasonal changes, vendor price increases
3. **Exposure Identification** - High vendor concentration, overdue receivables, cash flow gaps, loan covenant risks
4. **Insights Generation** - "Truck #6520 maintenance costs 15% above fleet average", "Sun-Glo pays 5 days faster than average"

**Operational View vs Full Accounting:**
- ✅ **Track expenses by category, vendor, equipment, company** - Full attribution
- ✅ **Track revenue by source, customer, load** - Performance analysis
- ✅ **Link to operational entities** (trucks, loads, vendors, drivers)
- ✅ **QuickBooks alignment** - Categories match existing accounting system
- ❌ **Not Yet:** Full GL accounts, journal entries, tax calculations, depreciation schedules
- 🔮 **Later:** Tax-ready categorization (1099s, deductible vs non-deductible), budget vs actual tracking

**The Multi-Hub Financial Intelligence System:**

Hub 5 doesn't exist in isolation - it's the financial memory layer that gives meaning to operational data:

- **Hub 2 Load** generates Revenue and Expense → Hub 5 tracks profitability
- **Hub 3 Truck** incurs Expenses → Hub 5 tracks total cost of ownership
- **Hub 4 Vendor** receives Payments → Hub 5 tracks vendor spend patterns
- **Hub 6 Legal Entity** owns assets → Hub 5 tracks which company made money

This creates **ONE financial brain** across 5 databases, not separate accounting silos.

---

## Core Entities (7 Entities, 140+ Properties Total)

### 1. **Expense** - Money Going Out

Every expense tracked with **full attribution** - WHO paid WHAT to WHOM for WHY.

**Primary Key:**
- **expense_id** (UUID) - `exp_20251103_001`

**Core Financial Properties (10):**
- amount (Decimal) - `2500.00`
- expense_date (Date) - When expense occurred
- posted_date (Date) - When entered in accounting system
- currency (String) - `USD` (for future multi-currency)
- exchange_rate (Decimal) - `1.0` (for future multi-currency)
- tax_deductible (Boolean) - `True/False`
- payment_status (Enum) - `pending`, `paid`, `overdue`, `cancelled`, `disputed`
- payment_method (Enum) - `check`, `ACH`, `wire`, `credit_card`, `cash`, `factoring_advance`, `fuel_card`
- payment_reference (String) - Check number, ACH trace, wire confirmation
- payment_date (Date) - When actually paid (may differ from expense_date)

**Categorization (QuickBooks Aligned) (5):**
- company_assignment (Enum) - `Origin`, `OpenHaul`, `Primetime`, `G-Personal`
- category (String) - See complete QuickBooks categories below
- subcategory (String) - More specific than main category
- category_code (String) - QuickBooks GL code (for export)
- description (Text) - Human-readable description

**Attribution - WHO/WHAT/WHERE (6):**
- vendor_id (UUID) - Links to Hub 4 Company (who we paid)
- vendor_name (String) - Cached for quick access
- related_to_entity_type (Enum) - `truck`, `load`, `driver`, `company`, `property`, `none`
- related_to_entity_id (String) - `6520`, `OH-321678`, `driver_robert`, etc.
- related_to_secondary_entity_type (Enum) - For multi-attribution (e.g., fuel for specific load AND truck)
- related_to_secondary_entity_id (String)

**Document Linkage (4):**
- invoice_id (UUID) - If expense came from vendor invoice
- document_path (String) - Receipt, invoice PDF path in Qdrant
- document_id (UUID) - Qdrant document ID
- extracted_from_document (Boolean) - Was this auto-extracted or manual entry?

**Approval Workflow (4):**
- requires_approval (Boolean) - For large expenses
- approved_by (String) - User ID who approved
- approved_at (Timestamp)
- approval_notes (Text)

**Recurring Expense Tracking (4):**
- is_recurring (Boolean) - Monthly software subscriptions, insurance
- recurring_frequency (Enum) - `monthly`, `quarterly`, `annually`
- recurring_parent_id (UUID) - Links to RecurringExpenseTemplate
- next_expected_date (Date) - For alerts

**Temporal Tracking (4):**
- created_at (Timestamp)
- updated_at (Timestamp)
- valid_from (Timestamp) - Bi-temporal
- valid_to (Timestamp) - Bi-temporal (nullable)

**Total Expense Properties: 37**

---

**QuickBooks Categories - Origin Transport (17 Expense Categories):**

1. **Accessorial Fees** - Extra charges passed through to customer
   - Examples: Lumper fees, detention, layover
   - Attribution: Usually links to specific load
   - Average: $50-$200 per occurrence

2. **Contract Carriers** - Payments to owner-operators under contract
   - Examples: 1099 driver settlements, lease-purchase payments
   - Attribution: Links to driver AND load
   - Average: $1,500-$3,000 per week per driver

3. **Driver Wages** - W-2 employee driver compensation
   - Examples: Per-mile pay, hourly pay, bonuses, detention pay
   - Attribution: Links to driver AND potentially load
   - Average: $60,000-$80,000 annually per driver
   - Subcategories: Base wages, overtime, bonuses, benefits

4. **Diesel-Truck & DEF** - Fuel and diesel exhaust fluid
   - Examples: Fleetone fuel purchases, DEF refills, fuel cards
   - Attribution: Links to truck (unit_number) AND driver AND potentially load
   - Average: $600-$1,200 per fill-up per truck
   - Subcategories: Diesel fuel, DEF, fuel tax credits

5. **Money Codes** - Cash advances and expense reimbursements to drivers
   - Examples: Advance pay, scale tickets, tolls, expense reimbursement
   - Attribution: Links to driver
   - Average: $50-$500 per transaction

6. **Purchased Transportation** - Brokered freight (when Origin brokers loads)
   - Examples: Carrier payments for brokered loads
   - Attribution: Links to load AND carrier company (Hub 4)
   - Average: $1,500-$3,500 per load

7. **Interest** - Loan interest, line of credit interest
   - Examples: Monthly truck loan interest, LOC interest
   - Attribution: Links to loan AND potentially truck
   - Average: $500-$2,000 per month per loan

8. **Factoring Fees** - Quick-pay financing fees
   - Examples: Triumph factoring fees (2-3% of invoice)
   - Attribution: Links to invoice AND load
   - Average: 2-3% of invoice value

9. **Equipment Lease** - Leased equipment payments
   - Examples: Trailer leases, equipment leases
   - Attribution: Links to trailer or equipment
   - Average: $300-$800 per month per trailer

10. **Repair & Maintenance** - Truck/trailer service and repairs
    - Examples: Oil changes, brake jobs, tire replacement, transmission repair
    - Attribution: Links to truck (unit_number) or trailer
    - Average: $500-$5,000 per service event
    - Subcategories: PM service, tires, brakes, engine, transmission, body, electrical

11. **Parts & Supplies** - Parts purchased separately from service
    - Examples: Bulk tire purchase, spare parts inventory
    - Attribution: Links to truck or inventory
    - Average: $100-$2,000 per purchase

12. **Safety & Compliance** - DOT compliance, drug testing, training
    - Examples: DOT physicals, drug tests, CSA compliance, safety training
    - Attribution: Links to driver or company-wide
    - Average: $100-$500 per item
    - Subcategories: Drug testing, physicals, training, compliance software

13. **Insurance** - Vehicle and liability insurance
    - Examples: Primary liability, physical damage, cargo insurance
    - Attribution: Links to truck or company-wide
    - Average: $1,000-$3,000 per month per truck
    - Subcategories: Primary liability, physical damage, cargo, general liability

14. **Permits and Registration** - State registrations, IFTA, IRP
    - Examples: Truck registration, IFTA quarterly filing, permits
    - Attribution: Links to truck
    - Average: $500-$2,000 per truck annually
    - Subcategories: IFTA, IRP, overweight permits, state registrations

15. **Professional Services** - Legal, accounting, consulting
    - Examples: Accountant fees, attorney fees, consultant fees
    - Attribution: Company-wide or project-specific
    - Average: $200-$2,000 per service

16. **Tax & Licensing** - Business licenses, highway use tax
    - Examples: State business licenses, federal highway use tax (Form 2290)
    - Attribution: Company-wide or truck-specific
    - Average: $100-$1,000 per year

17. **Software & Subscriptions** - Technology and software
    - Examples: Samsara, TMS, QuickBooks, Motive
    - Attribution: Company-wide
    - Average: $50-$1,000 per month per software
    - Subcategories: Fleet management, TMS, accounting, ELD, maintenance

---

**QuickBooks Categories - OpenHaul Logistics (8 Expense Categories):**

1. **Accessorial Fees** - Extra charges for customer loads
   - Examples: Lumper fees, detention, TONU (truck ordered not used)
   - Attribution: Links to load
   - Average: $50-$300 per occurrence

2. **Software & Subscriptions** - Technology stack
   - Examples: TMS (Turvo), QuickBooks, loadboard subscriptions
   - Attribution: Company-wide
   - Average: $100-$1,500 per month
   - Subcategories: TMS, accounting, loadboards, communication

3. **Purchased Transportation** - Carrier payments (primary expense)
   - Examples: Payments to carriers (including Origin when it hauls OpenHaul loads)
   - Attribution: Links to load AND carrier company (Hub 4)
   - Average: $1,500-$4,000 per load

4. **Payroll Wages** - Employee salaries
   - Examples: Office staff, dispatchers, sales team
   - Attribution: Links to employee (Hub 4 Person)
   - Average: $3,000-$6,000 per month per employee

5. **Interest** - Loan interest, line of credit
   - Examples: Business loan interest, LOC interest
   - Attribution: Links to loan
   - Average: $200-$1,000 per month

6. **Office Rent** - Office space rental
   - Examples: Monthly office rent, co-working space
   - Attribution: Company-wide
   - Average: $1,000-$3,000 per month

7. **Travel** - Business travel expenses
   - Examples: Customer visits, trade shows, carrier recruitment
   - Attribution: Links to employee or project
   - Average: $100-$2,000 per trip

8. **Utilities** - Office utilities
   - Examples: Electric, internet, phone
   - Attribution: Company-wide
   - Average: $200-$600 per month

---

**Expense Examples (Category-Specific):**

```python
# Origin - Diesel Fuel
Expense(
    expense_id="exp_20251103_001",
    amount=987.45,
    expense_date="2025-11-03",
    posted_date="2025-11-03",
    company_assignment="Origin",
    category="Diesel-Truck & DEF",
    subcategory="Diesel Fuel",
    description="Fleetone fuel purchase - TA Truck Stop, Exit 45 I-80",
    vendor_id="company_fleetone",
    vendor_name="Fleetone",
    related_to_entity_type="truck",
    related_to_entity_id="6520",
    related_to_secondary_entity_type="driver",
    related_to_secondary_entity_id="driver_robert",
    payment_method="fuel_card",
    payment_status="paid",
    payment_reference="FLEET-123456789",
    tax_deductible=True,
    extracted_from_document=True,
    document_path="qdrant://invoices/fleetone-statement-2025-11-03.pdf"
)

# Origin - Truck Maintenance
Expense(
    expense_id="exp_20251103_002",
    amount=2847.50,
    expense_date="2025-11-01",
    posted_date="2025-11-02",
    payment_date="2025-11-10",
    company_assignment="Origin",
    category="Repair & Maintenance",
    subcategory="Tires",
    description="4 new drive tires - Michelin XZA3+ 11R22.5",
    vendor_id="company_bosch",
    vendor_name="Bosch Service Center",
    related_to_entity_type="truck",
    related_to_entity_id="6520",
    payment_method="check",
    payment_status="paid",
    payment_reference="CHECK-1547",
    tax_deductible=True,
    invoice_id="inv_vendor_001",
    extracted_from_document=True,
    document_path="qdrant://invoices/bosch-invoice-789456.pdf"
)

# Origin - Driver Settlement
Expense(
    expense_id="exp_20251103_003",
    amount=2340.00,
    expense_date="2025-11-01",
    posted_date="2025-11-01",
    company_assignment="Origin",
    category="Contract Carriers",
    subcategory="1099 Driver Settlement",
    description="Weekly settlement - Robert McCullough - 1,300 miles @ $1.80/mile",
    vendor_id="person_robert_mccullough",
    vendor_name="Robert McCullough",
    related_to_entity_type="driver",
    related_to_entity_id="driver_robert",
    related_to_secondary_entity_type="truck",
    related_to_secondary_entity_id="6520",
    payment_method="ACH",
    payment_status="paid",
    payment_reference="ACH-SETTLE-20251101",
    tax_deductible=True
)

# Origin - Insurance (Recurring)
Expense(
    expense_id="exp_20251103_004",
    amount=2150.00,
    expense_date="2025-11-01",
    posted_date="2025-11-01",
    company_assignment="Origin",
    category="Insurance",
    subcategory="Primary Liability",
    description="Monthly primary liability insurance - 18 units",
    vendor_id="company_progressive",
    vendor_name="Progressive Commercial",
    related_to_entity_type="company",
    related_to_entity_id="company_origin",
    payment_method="ACH",
    payment_status="paid",
    payment_reference="ACH-INS-20251101",
    is_recurring=True,
    recurring_frequency="monthly",
    next_expected_date="2025-12-01",
    tax_deductible=True
)

# OpenHaul - Carrier Payment
Expense(
    expense_id="exp_20251103_005",
    amount=1850.00,
    expense_date="2025-11-03",
    posted_date="2025-11-04",
    payment_date="2025-11-10",
    company_assignment="OpenHaul",
    category="Purchased Transportation",
    description="Carrier payment - Load OH-321678 - Sun-Glo pickup to delivery",
    vendor_id="company_origin",  # Origin as carrier
    vendor_name="Origin Transport LLC",
    related_to_entity_type="load",
    related_to_entity_id="OH-321678",
    related_to_secondary_entity_type="truck",
    related_to_secondary_entity_id="6520",  # Origin's truck that hauled it
    payment_method="ACH",
    payment_status="pending",
    invoice_id="inv_carrier_001",
    tax_deductible=True
)

# OpenHaul - Software Subscription (Recurring)
Expense(
    expense_id="exp_20251103_006",
    amount=499.00,
    expense_date="2025-11-01",
    posted_date="2025-11-01",
    company_assignment="OpenHaul",
    category="Software & Subscriptions",
    subcategory="TMS",
    description="Turvo TMS monthly subscription",
    vendor_id="company_turvo",
    vendor_name="Turvo Inc",
    related_to_entity_type="company",
    related_to_entity_id="company_openhaul",
    payment_method="credit_card",
    payment_status="paid",
    payment_reference="CC-TURVO-20251101",
    is_recurring=True,
    recurring_frequency="monthly",
    next_expected_date="2025-12-01",
    tax_deductible=True
)

# OpenHaul - Office Rent (Recurring)
Expense(
    expense_id="exp_20251103_007",
    amount=1200.00,
    expense_date="2025-11-01",
    posted_date="2025-11-01",
    company_assignment="OpenHaul",
    category="Office Rent",
    description="Monthly office rent - 800 sq ft",
    vendor_id="company_landlord_xyz",
    vendor_name="XYZ Property Management",
    related_to_entity_type="company",
    related_to_entity_id="company_openhaul",
    payment_method="check",
    payment_status="paid",
    payment_reference="CHECK-2001",
    is_recurring=True,
    recurring_frequency="monthly",
    next_expected_date="2025-12-01",
    tax_deductible=True
)
```

---

### 2. **Revenue** - Money Coming In

Every revenue source tracked with **full attribution** - WHO paid us WHAT for WHY.

**Primary Key:**
- **revenue_id** (UUID) - `rev_20251103_001`

**Core Financial Properties (10):**
- amount (Decimal) - `2500.00`
- revenue_date (Date) - When revenue earned
- posted_date (Date) - When entered in accounting system
- payment_received_date (Date) - When actually received (may differ)
- currency (String) - `USD`
- exchange_rate (Decimal) - `1.0`
- payment_status (Enum) - `pending`, `received`, `partial`, `overdue`, `factored`, `cancelled`
- payment_method (Enum) - `ACH`, `wire`, `check`, `factoring_advance`, `credit_card`
- payment_reference (String) - ACH trace, wire confirmation
- net_terms (Integer) - `0`, `15`, `30`, `60` (days)

**Categorization (QuickBooks Aligned) (5):**
- company_assignment (Enum) - `Origin`, `OpenHaul`
- category (String) - See complete QuickBooks categories below
- subcategory (String) - More specific than main category
- category_code (String) - QuickBooks GL code
- description (Text)

**Attribution - WHO/WHAT/WHERE (5):**
- customer_id (UUID) - Links to Hub 4 Company (who paid us)
- customer_name (String) - Cached for quick access
- source_entity_type (Enum) - `load`, `truck`, `service`, `lease`, `none`
- source_entity_id (String) - `OH-321678`, `6520`, etc.
- source_secondary_entity_id (String) - For multi-attribution

**Document Linkage (4):**
- invoice_id (UUID) - Customer invoice that generated this revenue
- document_path (String) - Invoice PDF, rate confirmation PDF
- document_id (UUID) - Qdrant document ID
- extracted_from_document (Boolean)

**Factoring (4):**
- factored (Boolean) - Was this invoice factored?
- factor_id (UUID) - Links to Factor entity (Hub 2) or Company (Hub 4)
- factored_date (Date)
- factoring_fee (Decimal) - Amount paid to factor

**Temporal Tracking (4):**
- created_at (Timestamp)
- updated_at (Timestamp)
- valid_from (Timestamp)
- valid_to (Timestamp)

**Total Revenue Properties: 32**

---

**QuickBooks Categories - Origin Transport (2 Revenue Categories):**

1. **Line Haul Income** - Primary freight revenue
   - Examples: Customer payments for hauling freight
   - Attribution: Links to load (when brokered) or truck (when dedicated/spot)
   - Average: $2,000-$5,000 per load
   - Subcategories: Spot freight, dedicated lanes, intermodal

2. **Equipment Lease Income** - Trailer/equipment rental income
   - Examples: Trailer leases to other carriers, equipment rentals
   - Attribution: Links to trailer or equipment
   - Average: $300-$800 per month per trailer

---

**QuickBooks Categories - OpenHaul Logistics (2 Revenue Categories):**

1. **LineHaul Income** - Primary brokerage revenue (customer charges)
   - Examples: Customer payments for brokered loads
   - Attribution: Links to load
   - Average: $2,200-$5,500 per load
   - Subcategories: Brokerage, direct freight, customer-specific lanes

2. **Accessorial Income** - Extra charges passed to customer
   - Examples: Lumper fees, detention, layover, TONU, fuel surcharge
   - Attribution: Links to load
   - Average: $50-$500 per occurrence
   - Subcategories: Detention, lumper, fuel surcharge, TONU, layover

---

**Revenue Examples (Category-Specific):**

```python
# OpenHaul - Brokerage Revenue (Load)
Revenue(
    revenue_id="rev_20251103_001",
    amount=2375.00,
    revenue_date="2025-11-03",
    posted_date="2025-11-04",
    payment_received_date="2025-11-18",  # net-15
    company_assignment="OpenHaul",
    category="LineHaul Income",
    subcategory="Brokerage",
    description="Load OH-321678 - Sun-Glo Nurseries pickup to delivery",
    customer_id="company_sunglo",
    customer_name="Sun-Glo Nurseries",
    source_entity_type="load",
    source_entity_id="OH-321678",
    payment_method="ACH",
    payment_status="pending",
    net_terms=15,
    invoice_id="inv_customer_001",
    factored=True,
    factor_id="company_triumph",
    factored_date="2025-11-05",
    factoring_fee=59.38,  # 2.5% of $2,375
    extracted_from_document=True,
    document_path="qdrant://invoices/openhaul-invoice-OH-321678.pdf"
)

# OpenHaul - Accessorial Revenue (Detention)
Revenue(
    revenue_id="rev_20251103_002",
    amount=150.00,
    revenue_date="2025-11-03",
    posted_date="2025-11-04",
    company_assignment="OpenHaul",
    category="Accessorial Income",
    subcategory="Detention",
    description="Detention charge - Load OH-321678 - 3 hours @ $50/hr",
    customer_id="company_sunglo",
    customer_name="Sun-Glo Nurseries",
    source_entity_type="load",
    source_entity_id="OH-321678",
    payment_status="pending",
    net_terms=15,
    factored=True,
    factor_id="company_triumph",
    factored_date="2025-11-05",
    factoring_fee=3.75  # 2.5% of $150
)

# Origin - Freight Revenue (Dedicated Lane)
Revenue(
    revenue_id="rev_20251103_003",
    amount=3200.00,
    revenue_date="2025-11-01",
    posted_date="2025-11-01",
    payment_received_date="2025-11-30",  # net-30
    company_assignment="Origin",
    category="Line Haul Income",
    subcategory="Dedicated Lanes",
    description="Weekly dedicated run - Customer ABC Corp - Unit #6520",
    customer_id="company_abc",
    customer_name="ABC Corporation",
    source_entity_type="truck",
    source_entity_id="6520",
    source_secondary_entity_id="driver_robert",
    payment_method="ACH",
    payment_status="pending",
    net_terms=30
)

# Origin - Equipment Lease Revenue
Revenue(
    revenue_id="rev_20251103_004",
    amount=650.00,
    revenue_date="2025-11-01",
    posted_date="2025-11-01",
    payment_received_date="2025-11-05",
    company_assignment="Origin",
    category="Equipment Lease Income",
    description="Monthly trailer lease - 53' dry van #T-4501",
    customer_id="company_xyz_carrier",
    customer_name="XYZ Carrier LLC",
    source_entity_type="trailer",
    source_entity_id="T-4501",
    payment_method="ACH",
    payment_status="received"
)
```

---

### 3. **Invoice** - Bills Sent/Received

Tracks both **customer invoices (AR)** and **vendor invoices (AP)**.

**Primary Key:**
- **invoice_id** (UUID)

**Core Properties (20):**
- invoice_number (String) - Vendor's or our invoice number (e.g., "OH-INV-2025-11-001")
- invoice_type (Enum) - `customer`, `vendor`
- invoice_date (Date)
- due_date (Date)
- amount (Decimal) - Total invoice amount
- amount_paid (Decimal) - Amount paid so far
- amount_outstanding (Decimal) - Remaining balance
- status (Enum) - `open`, `partial`, `paid`, `overdue`, `void`, `disputed`, `factored`
- company_assignment (Enum) - `Origin`, `OpenHaul`, `Primetime`
- customer_id (UUID) - If customer invoice (who we bill)
- vendor_id (UUID) - If vendor invoice (who billed us)
- related_to_entity_type (Enum) - `load`, `truck`, `service`, `multiple`, `none`
- related_to_entity_id (String)
- document_path (String) - Invoice PDF
- payment_ids (Array[UUID]) - Payments that paid this invoice
- factored_by_id (UUID) - If factored (links to Factor or Company)
- factoring_date (Date)
- factoring_advance_amount (Decimal)
- created_at, updated_at, valid_from, valid_to (Timestamps)

**Invoice Line Items:**

Many invoices have multiple line items. These can be modeled as a sub-entity or as separate Expense/Revenue records linked to the same invoice_id.

**Approach:** Store line items in PostgreSQL JSON field for complex invoices, create separate Expense/Revenue for each line item.

**Examples:**

```python
# Customer Invoice (OpenHaul → Sun-Glo)
Invoice(
    invoice_id="inv_customer_001",
    invoice_type="customer",
    invoice_number="OH-INV-2025-11-001",
    invoice_date="2025-11-04",
    due_date="2025-11-19",  # net-15
    amount=2525.00,  # $2,375 linehaul + $150 detention
    amount_paid=0,
    amount_outstanding=2525.00,
    status="factored",
    company_assignment="OpenHaul",
    customer_id="company_sunglo",
    related_to_entity_type="load",
    related_to_entity_id="OH-321678",
    document_path="qdrant://invoices/openhaul-invoice-OH-321678.pdf",
    factored_by_id="company_triumph",
    factoring_date="2025-11-05",
    factoring_advance_amount=2399.75,  # 95% of $2,525
    payment_ids=["pay_20251105_001"]  # Factoring advance payment
)

# Vendor Invoice (Bosch → Origin)
Invoice(
    invoice_id="inv_vendor_001",
    invoice_type="vendor",
    invoice_number="BOSCH-789456",  # Vendor's invoice number
    invoice_date="2025-11-01",
    due_date="2025-11-16",  # net-15
    amount=2847.50,
    amount_paid=2847.50,
    amount_outstanding=0,
    status="paid",
    company_assignment="Origin",
    vendor_id="company_bosch",
    related_to_entity_type="truck",
    related_to_entity_id="6520",
    document_path="qdrant://invoices/bosch-invoice-789456.pdf",
    payment_ids=["pay_20251110_001"]
)

# Vendor Invoice - Fuel Statement (Fleetone → Origin)
Invoice(
    invoice_id="inv_vendor_002",
    invoice_type="vendor",
    invoice_number="FLEETONE-202511-MONTHLY",
    invoice_date="2025-11-01",
    due_date="2025-11-15",
    amount=18450.00,  # Monthly fuel total for all trucks
    amount_paid=18450.00,
    amount_outstanding=0,
    status="paid",
    company_assignment="Origin",
    vendor_id="company_fleetone",
    related_to_entity_type="multiple",  # Multiple trucks
    related_to_entity_id="fleet",
    document_path="qdrant://invoices/fleetone-statement-2025-11.pdf",
    payment_ids=["pay_20251115_001"]
)
```

---

### 4. **Payment** - Actual Money Transfers

Records of money actually changing hands.

**Primary Key:**
- **payment_id** (UUID)

**Core Properties (18):**
- amount (Decimal)
- payment_date (Date)
- payment_method (Enum) - `check`, `ACH`, `wire`, `credit_card`, `cash`, `factoring_advance`, `fuel_card`
- payment_direction (Enum) - `inbound`, `outbound`
- company_assignment (Enum) - `Origin`, `OpenHaul`, `Primetime`
- from_company_id (UUID) - Who sent money
- to_company_id (UUID) - Who received money
- invoice_id (UUID) - Which invoice this payment applies to (nullable for non-invoice payments)
- partial_payment (Boolean)
- bank_account_id (UUID) - Which bank account
- transaction_reference (String) - Check number, ACH trace, wire confirmation
- memo (Text) - Payment description
- reconciled (Boolean) - Matched to bank statement
- reconciled_date (Date)
- created_at, updated_at, valid_from, valid_to (Timestamps)

**Examples:**

```python
# Customer Payment (Sun-Glo → OpenHaul via Factoring Advance)
Payment(
    payment_id="pay_20251105_001",
    amount=2399.75,  # 95% advance
    payment_date="2025-11-05",
    payment_method="factoring_advance",
    payment_direction="inbound",
    company_assignment="OpenHaul",
    from_company_id="company_triumph",  # Factor advances money
    to_company_id="company_openhaul",
    invoice_id="inv_customer_001",
    partial_payment=True,  # Remaining 5% comes later
    bank_account_id="bank_openhaul_checking",
    transaction_reference="TRIUMPH-ADV-20251105",
    memo="Factoring advance for invoice OH-INV-2025-11-001",
    reconciled=True,
    reconciled_date="2025-11-06"
)

# Factoring Fee Payment (OpenHaul → Triumph)
Payment(
    payment_id="pay_20251118_001",
    amount=125.25,  # Remaining 5% minus fee
    payment_date="2025-11-18",
    payment_method="ACH",
    payment_direction="outbound",
    company_assignment="OpenHaul",
    from_company_id="company_openhaul",
    to_company_id="company_triumph",
    memo="Factoring fee settlement - Invoice OH-INV-2025-11-001 - Net paid by customer",
    reconciled=True,
    reconciled_date="2025-11-19"
)

# Vendor Payment (Origin → Bosch)
Payment(
    payment_id="pay_20251110_001",
    amount=2847.50,
    payment_date="2025-11-10",
    payment_method="check",
    payment_direction="outbound",
    company_assignment="Origin",
    from_company_id="company_origin",
    to_company_id="company_bosch",
    invoice_id="inv_vendor_001",
    partial_payment=False,
    bank_account_id="bank_origin_checking",
    transaction_reference="CHECK-1547",
    memo="Payment for tire service - Unit #6520",
    reconciled=True,
    reconciled_date="2025-11-15"
)

# Driver Settlement (Origin → Robert)
Payment(
    payment_id="pay_20251101_001",
    amount=2340.00,
    payment_date="2025-11-01",
    payment_method="ACH",
    payment_direction="outbound",
    company_assignment="Origin",
    from_company_id="company_origin",
    to_company_id="person_robert_mccullough",
    invoice_id=None,  # No formal invoice for driver settlements
    bank_account_id="bank_origin_checking",
    transaction_reference="ACH-SETTLE-20251101",
    memo="Weekly settlement - Robert McCullough - Week ending 2025-10-31",
    reconciled=True,
    reconciled_date="2025-11-02"
)
```

---

### 5. **Loan** - Debt Obligations

Truck loans, lines of credit, equipment financing.

**Primary Key:**
- **loan_id** (UUID)

**Core Properties (22):**
- loan_type (Enum) - `equipment`, `line_of_credit`, `term_loan`, `SBA`, `personal_guarantee`
- lender_id (UUID) - Bank/lender (Hub 4)
- lender_name (String) - Cached
- loan_number (String) - Lender's account/loan number
- original_amount (Decimal)
- current_balance (Decimal)
- interest_rate (Decimal) - Annual percentage
- monthly_payment (Decimal)
- start_date (Date)
- maturity_date (Date)
- next_payment_date (Date)
- payment_day_of_month (Integer) - 1-31
- collateral_entity_type (Enum) - `truck`, `trailer`, `equipment`, `property`, `none`
- collateral_entity_id (String) - Links to Hub 3 Truck/Trailer
- company_assignment (Enum) - `Origin`, `OpenHaul`, `Primetime`, `G-Personal`
- status (Enum) - `active`, `paid_off`, `defaulted`, `refinanced`
- auto_payment (Boolean)
- payment_source_account_id (UUID) - Bank account for auto-pay
- created_at, updated_at, valid_from, valid_to (Timestamps)

**Examples:**

```python
# Truck Loan (Origin - Unit #6520)
Loan(
    loan_id="loan_001",
    loan_type="equipment",
    lender_id="company_bank_of_america",
    lender_name="Bank of America",
    loan_number="LOAN-445566778",
    original_amount=120000.00,
    current_balance=78450.00,
    interest_rate=5.75,  # 5.75% APR
    monthly_payment=2389.00,
    start_date="2023-01-15",
    maturity_date="2028-01-15",  # 5-year term
    next_payment_date="2025-12-15",
    payment_day_of_month=15,
    collateral_entity_type="truck",
    collateral_entity_id="6520",
    company_assignment="Origin",
    status="active",
    auto_payment=True,
    payment_source_account_id="bank_origin_checking"
)

# Line of Credit (OpenHaul)
Loan(
    loan_id="loan_002",
    loan_type="line_of_credit",
    lender_id="company_bank_of_america",
    lender_name="Bank of America",
    loan_number="LOC-998877665",
    original_amount=50000.00,  # Credit limit
    current_balance=12000.00,  # Current draw
    interest_rate=7.25,
    monthly_payment=0,  # Interest-only, variable
    start_date="2024-06-01",
    maturity_date="2026-06-01",  # 2-year revolving
    next_payment_date="2025-12-01",
    payment_day_of_month=1,
    collateral_entity_type="none",  # Unsecured
    company_assignment="OpenHaul",
    status="active",
    auto_payment=False
)
```

---

### 6. **BankAccount** - Where Money Lives

Bank accounts for each company.

**Primary Key:**
- **bank_account_id** (UUID)

**Core Properties (14):**
- account_name (String) - "Origin Operating Account"
- bank_name (String) - "Bank of America"
- account_type (Enum) - `checking`, `savings`, `credit_card`, `money_market`
- account_number_last_4 (String) - "1234" (security - don't store full number)
- routing_number_last_4 (String) - "7890" (partial only)
- company_assignment (Enum) - `Origin`, `OpenHaul`, `Primetime`, `G-Personal`
- current_balance (Decimal) - Updated periodically
- available_balance (Decimal) - After pending transactions
- currency (String) - `USD`
- active_status (Boolean)
- primary_account (Boolean) - Is this the main operating account?
- created_at, updated_at, valid_from, valid_to (Timestamps)

**Examples:**

```python
# Origin - Primary Checking
BankAccount(
    bank_account_id="bank_origin_checking",
    account_name="Origin Transport Operating Account",
    bank_name="Bank of America",
    account_type="checking",
    account_number_last_4="1234",
    routing_number_last_4="7890",
    company_assignment="Origin",
    current_balance=52340.00,
    available_balance=48750.00,  # $3,590 in pending checks
    currency="USD",
    active_status=True,
    primary_account=True
)

# OpenHaul - Primary Checking
BankAccount(
    bank_account_id="bank_openhaul_checking",
    account_name="OpenHaul Logistics Operating Account",
    bank_name="Bank of America",
    account_type="checking",
    account_number_last_4="5678",
    company_assignment="OpenHaul",
    current_balance=18750.00,
    available_balance=15200.00,
    currency="USD",
    active_status=True,
    primary_account=True
)

# Origin - Savings
BankAccount(
    bank_account_id="bank_origin_savings",
    account_name="Origin Transport Reserve Account",
    bank_name="Bank of America",
    account_type="savings",
    account_number_last_4="9012",
    company_assignment="Origin",
    current_balance=75000.00,
    available_balance=75000.00,
    currency="USD",
    active_status=True,
    primary_account=False
)
```

---

### 7. **IntercompanyTransfer** - Money Between Companies

Transfers between Origin, OpenHaul, Primetime that are **NOT load-related**.

**Primary Key:**
- **transfer_id** (UUID)

**Core Properties (14):**
- amount (Decimal)
- transfer_date (Date)
- from_company_id (UUID)
- to_company_id (UUID)
- transfer_type (Enum) - `credit_line`, `bill_coverage`, `loan`, `capital_contribution`, `distribution`, `reimbursement`
- description (Text)
- repayment_terms (String) - "Net-30, no interest", "Net-60, 5% APR", "No repayment expected"
- repayment_due_date (Date)
- repayment_status (Enum) - `pending`, `paid`, `partial`, `overdue`, `forgiven`
- amount_repaid (Decimal)
- status (Enum) - `pending`, `completed`, `cancelled`
- created_at, updated_at, valid_from, valid_to (Timestamps)

**Key Distinction:** This is NOT a load payment. Load payments (Origin hauls for OpenHaul) flow through normal Expense/Revenue tracking in Hub 2 → Hub 5 link.

**Examples:**

```python
# Credit Line Extension (Origin → OpenHaul)
IntercompanyTransfer(
    transfer_id="trans_001",
    amount=10000.00,
    transfer_date="2025-11-01",
    from_company_id="company_origin",
    to_company_id="company_openhaul",
    transfer_type="credit_line",
    description="Origin extends $10k credit line to OpenHaul for Q4 cash flow",
    repayment_terms="Net-90, no interest",
    repayment_due_date="2026-02-01",
    repayment_status="pending",
    amount_repaid=0,
    status="completed"
)

# Bill Coverage (Primetime → Origin)
IntercompanyTransfer(
    transfer_id="trans_002",
    amount=5000.00,
    transfer_date="2025-10-15",
    from_company_id="company_primetime",
    to_company_id="company_origin",
    transfer_type="bill_coverage",
    description="Primetime covers Origin insurance bill",
    repayment_terms="Repay when cash flow improves",
    repayment_status="paid",
    amount_repaid=5000.00,
    status="completed"
)

# Capital Contribution (G-Personal → OpenHaul)
IntercompanyTransfer(
    transfer_id="trans_003",
    amount=25000.00,
    transfer_date="2025-01-15",
    from_company_id="person_g",
    to_company_id="company_openhaul",
    transfer_type="capital_contribution",
    description="G invests $25k to launch OpenHaul",
    repayment_terms="No repayment expected - equity contribution",
    repayment_status="forgiven",
    status="completed"
)
```

---

## Primary Relationships

### Expense Attribution
```cypher
// Expense to vendor
(Expense {expense_id: "exp_001"})-[:PAID_TO]->(Vendor:Company {company_id: "company_bosch"})

// Expense assigned to company
(Expense)-[:ASSIGNED_TO]->(Origin:Company)

// Expense relates to equipment
(Expense)-[:RELATES_TO {type: "equipment", attribution: "primary"}]->(Tractor {unit_number: "6520"})

// Expense relates to load (multi-attribution)
(Expense)-[:RELATES_TO {type: "load", attribution: "secondary"}]->(Load {load_number: "OH-321678"})

// Expense relates to driver
(Expense {category: "Driver Wages"})-[:PAID_TO]->(Driver {driver_id: "driver_robert"})

// Expense categorization
(Expense)-[:CATEGORIZED_AS]->(ExpenseCategory {name: "Repair & Maintenance", subcategory: "Tires"})

// Recurring expense template
(Expense {is_recurring: true})-[:INSTANCE_OF]->(RecurringExpenseTemplate)
```

### Revenue Attribution
```cypher
// Revenue from customer
(Revenue {revenue_id: "rev_001"})-[:RECEIVED_FROM]->(Customer:Company {company_id: "company_sunglo"})

// Revenue earned by company
(Revenue)-[:EARNED_BY]->(OpenHaul:Company)

// Revenue generated by load
(Revenue)-[:GENERATED_BY]->(Load {load_number: "OH-321678"})

// Revenue generated by truck
(Revenue)-[:GENERATED_BY]->(Tractor {unit_number: "6520"})

// Revenue categorization
(Revenue)-[:CATEGORIZED_AS]->(RevenueCategory {name: "LineHaul Income", subcategory: "Brokerage"})

// Factored revenue
(Revenue {factored: true})-[:FACTORED_BY]->(Factor:Company {company_id: "company_triumph"})
```

### Invoice-Payment Chain
```cypher
// Customer invoice
(Invoice {type: "customer"})-[:BILLED_TO]->(Customer:Company)
(Invoice)-[:FOR_LOAD]->(Load)

// Vendor invoice
(Invoice {type: "vendor"})-[:RECEIVED_FROM]->(Vendor:Company)
(Invoice)-[:FOR_SERVICE]->(MaintenanceRecord)  // Hub 3

// Payment applies to invoice
(Payment)-[:APPLIES_TO]->(Invoice)
(Payment)-[:FROM]->(FromCompany:Company)
(Payment)-[:TO]->(ToCompany:Company)

// Invoice generates expense/revenue
(Invoice {type: "vendor"})-[:CREATES]->(Expense)
(Invoice {type: "customer"})-[:CREATES]->(Revenue)

// Factored invoice
(Invoice {factored: true})-[:FACTORED_BY]->(Factor:Company)
(Payment {payment_method: "factoring_advance"})-[:ADVANCES]->(Invoice)
```

### Loan Relationships
```cypher
// Loan from lender
(Loan)-[:FROM_LENDER]->(Bank:Company)

// Loan secures asset
(Loan)-[:SECURES]->(Tractor {unit_number: "6520"})

// Loan payment is expense
(Loan)-[:MONTHLY_PAYMENT_CREATES]->(Expense {category: "Interest"})

// Payment pays loan
(Payment)-[:PAYS_LOAN]->(Loan)
```

### Bank Account Relationships
```cypher
// Company owns account
(Company)-[:HAS_ACCOUNT]->(BankAccount)

// Payment from/to account
(Payment)-[:FROM_ACCOUNT]->(BankAccount)
(Payment)-[:TO_ACCOUNT]->(BankAccount)

// Loan auto-payment
(Loan {auto_payment: true})-[:PAYS_FROM]->(BankAccount)
```

### Intercompany Transfer Relationships
```cypher
// Transfer between companies
(IntercompanyTransfer)-[:FROM]->(OriginCompany:LegalEntity)
(IntercompanyTransfer)-[:TO]->(OpenHaulCompany:LegalEntity)

// Transfer creates payment
(IntercompanyTransfer)-[:CREATES]->(Payment)
```

---

## Cross-Hub Relationships

### Hub 5 → Hub 2 (OpenHaul)

**Load Financial Tracking:**
```cypher
// Load generates revenue
(Load {load_number: "OH-321678"})-[:GENERATES]->(Revenue {
    amount: 2375.00,
    category: "LineHaul Income",
    customer_id: "company_sunglo"
})

// Load incurs carrier expense
(Load {load_number: "OH-321678"})-[:INCURS]->(Expense {
    amount: 1850.00,
    category: "Purchased Transportation",
    vendor_id: "company_origin"
})

// Load margin calculation
(Load)-[:HAS_MARGIN {
    revenue: 2375.00,
    expense: 1850.00,
    gross_profit: 525.00,
    margin_percent: 22.1
}]

// Invoice links to load
(Invoice {type: "customer"})-[:FOR_LOAD]->(Load)

// Factoring links to load
(Factor)-[:ADVANCES_FOR]->(Load)
```

---

### Hub 5 → Hub 3 (Origin)

**Truck Financial Tracking:**
```cypher
// Truck incurs expenses
(Tractor {unit_number: "6520"})-[:INCURS]->(Expense {
    category: "Diesel-Truck & DEF",
    amount: 987.45
})
(Tractor)-[:INCURS]->(Expense {
    category: "Repair & Maintenance",
    amount: 2847.50
})
(Tractor)-[:INCURS]->(Expense {
    category: "Insurance",
    amount: 2150.00
})

// Truck generates revenue
(Tractor {unit_number: "6520"})-[:GENERATES]->(Revenue {
    category: "Line Haul Income",
    amount: 3200.00
})

// Truck profitability over time
(Tractor)-[:HAS_FINANCIAL_PERFORMANCE {
    time_period: "2025-11",
    total_revenue: 12800.00,
    total_expenses: 9850.00,
    net_profit: 2950.00,
    profit_margin_percent: 23.0
}]

// Loan secures truck
(Loan {loan_number: "LOAN-445566778"})-[:SECURES]->(Tractor {unit_number: "6520"})
(Loan)-[:MONTHLY_PAYMENT {
    amount: 2389.00,
    payment_date: "2025-11-15"
}]->(Expense {category: "Interest"})

// Maintenance record generates expense
(MaintenanceRecord {service_date: "2025-11-01"})-[:CREATES]->(Expense {
    category: "Repair & Maintenance",
    amount: 2847.50
})

// Fuel transaction generates expense
(FuelTransaction {transaction_date: "2025-11-03"})-[:CREATES]->(Expense {
    category: "Diesel-Truck & DEF",
    amount: 987.45
})
```

---

### Hub 5 → Hub 4 (Contacts)

**Vendor/Customer Financial Relationships:**
```cypher
// Expenses paid to vendors
(Expense)-[:PAID_TO]->(Vendor:Company {company_id: "company_bosch"})

// Revenue from customers
(Revenue)-[:RECEIVED_FROM]->(Customer:Company {company_id: "company_sunglo"})

// Invoices
(Invoice {type: "customer"})-[:BILLED_TO]->(Customer)
(Invoice {type: "vendor"})-[:RECEIVED_FROM]->(Vendor)

// Payments
(Payment)-[:FROM]->(FromCompany)
(Payment)-[:TO]->(ToCompany)

// Loans from banks
(Loan)-[:FROM_LENDER]->(Bank:Company {company_id: "company_bank_of_america"})

// Vendor spend analysis
(Vendor)-[:RECEIVED_TOTAL {
    time_period: "2025-11",
    total_amount: 15450.00,
    transaction_count: 8,
    average_transaction: 1931.25
}]

// Customer payment behavior
(Customer)-[:PAYMENT_PATTERN {
    average_days_to_pay: 18,
    on_time_percentage: 92,
    total_revenue_ytd: 45000.00
}]

// Driver as expense recipient (1099 contractors)
(Driver:Person)-[:RECEIVES_SETTLEMENT]->(Expense {
    category: "Contract Carriers",
    amount: 2340.00
})
```

---

### Hub 5 → Hub 6 (Corporate)

**Legal Entity Financial Assignment:**
```cypher
// Expenses assigned to legal entities
(Expense)-[:ASSIGNED_TO]->(Origin:LegalEntity)
(Expense)-[:ASSIGNED_TO]->(OpenHaul:LegalEntity)

// Revenue earned by legal entities
(Revenue)-[:EARNED_BY]->(OpenHaul:LegalEntity)

// Company profitability
(Origin:LegalEntity)-[:HAS_FINANCIAL_PERFORMANCE {
    time_period: "2025-11",
    total_revenue: 125000.00,
    total_expenses: 98000.00,
    net_profit: 27000.00,
    profit_margin: 21.6
}]

// Intercompany transfers between legal entities
(IntercompanyTransfer)-[:FROM]->(Origin:LegalEntity)
(IntercompanyTransfer)-[:TO]->(OpenHaul:LegalEntity)

// Loan obligations by entity
(Origin:LegalEntity)-[:OWES]->(Loan {current_balance: 78450.00})

// Bank accounts by entity
(Origin:LegalEntity)-[:HAS_ACCOUNT]->(BankAccount {current_balance: 52340.00})

// Entity ownership impacts financials
(Primetime:LegalEntity)-[:OWNS {percentage: 100}]->(Origin:LegalEntity)
// Consolidate Origin financials into Primetime
```

---

### Hub 5 → Hub 1 (G - Command Center)

**Goal/Project Financial Tracking:**
```cypher
// Goals measured by financials
(Goal {title: "Grow OpenHaul Revenue"})-[:MEASURED_BY]->(Revenue {
    company_assignment: "OpenHaul",
    time_period: "2025-Q4"
})
(Goal {title: "Reduce Truck Operating Costs"})-[:MEASURED_BY]->(Expense {
    company_assignment: "Origin",
    category: "Diesel-Truck & DEF"
})

// Projects impact financials
(Project {title: "Fleet Expansion"})-[:RESULTS_IN]->(Revenue {
    increase_expected: 50000.00
})
(Project)-[:REQUIRES]->(Expense {
    category: "Equipment Lease",
    amount: 15000.00
})

// Insights about financial patterns
(Insight {
    content: "Unit #6520 maintenance costs 15% above fleet average",
    generated_date: "2025-11-10"
})-[:ABOUT]->(Expense {
    related_to_entity_id: "6520",
    category: "Repair & Maintenance"
})

// G personal tracking
(G:Person)-[:MONITORS]->(BankAccount {company_assignment: "Origin"})
(G)-[:REVIEWS]->(Expense {amount_gt: 5000})  // Large expense alerts
```

---

## Database Distribution

### Neo4j (Relationship Memory)

**Stores:**
- Basic expense/revenue/invoice/payment/loan/bankaccount nodes (lightweight)
- All attribution relationships:
  - `(Expense)-[:PAID_TO]->(Vendor)`
  - `(Revenue)-[:RECEIVED_FROM]->(Customer)`
  - `(Expense)-[:RELATES_TO]->(Tractor)`
  - `(Revenue)-[:GENERATED_BY]->(Load)`
  - `(Invoice)-[:APPLIES_TO]->(Payment)`
  - `(Loan)-[:SECURES]->(Tractor)`
- Cross-hub links
- Financial performance relationships (truck profitability, vendor spend, customer payment patterns)

**Why:**
- Graph traversal queries:
  - "Show all expenses for Unit #6520"
  - "Track invoice → payment chain"
  - "Find all revenue from Sun-Glo"
  - "Show vendor spend across all companies"
  - "Trace intercompany financial flows"
- Pattern detection:
  - Vendor concentration risk (one vendor = 40% of spend)
  - Customer dependency (one customer = 60% of revenue)
  - Cross-hub attribution (expense → truck → load → customer)

**Node Properties (Minimal):**
```cypher
(:Expense {
    expense_id: "exp_001",
    amount: 2500.00,
    expense_date: "2025-11-01",
    category: "Repair & Maintenance",
    company_assignment: "Origin"
})
```

---

### PostgreSQL (Factual Memory)

**Stores:**
- **Complete financial records** (all properties)
- Expense table (37 properties)
- Revenue table (32 properties)
- Invoice table (20+ properties)
- Payment table (18 properties)
- Loan table (22 properties)
- BankAccount table (14 properties)
- IntercompanyTransfer table (14 properties)

**Why:**
- Structured queries:
  - "Total expenses by category YTD"
  - "Outstanding invoices by customer"
  - "Loan payment schedule for all trucks"
  - "Bank account balances as of date"
  - "Intercompany transfer history with repayment status"
- Aggregations:
  - Sum, average, count by category/vendor/customer
  - Date range filtering (expense_date BETWEEN)
  - Status filtering (payment_status = 'pending')
- Reporting:
  - P&L by company
  - Cash flow projections
  - Vendor aging report
  - Customer AR aging

**Schema Example (PostgreSQL):**
```sql
CREATE TABLE expenses (
    expense_id UUID PRIMARY KEY,
    amount NUMERIC(12, 2) NOT NULL,
    expense_date DATE NOT NULL,
    posted_date DATE,
    payment_date DATE,
    currency VARCHAR(3) DEFAULT 'USD',
    payment_status VARCHAR(20),
    payment_method VARCHAR(50),
    payment_reference VARCHAR(255),
    company_assignment VARCHAR(50) NOT NULL,
    category VARCHAR(100) NOT NULL,
    subcategory VARCHAR(100),
    category_code VARCHAR(50),
    description TEXT,
    vendor_id UUID,
    vendor_name VARCHAR(255),
    related_to_entity_type VARCHAR(50),
    related_to_entity_id VARCHAR(100),
    related_to_secondary_entity_type VARCHAR(50),
    related_to_secondary_entity_id VARCHAR(100),
    invoice_id UUID,
    document_path VARCHAR(500),
    document_id UUID,
    extracted_from_document BOOLEAN DEFAULT FALSE,
    requires_approval BOOLEAN DEFAULT FALSE,
    approved_by VARCHAR(100),
    approved_at TIMESTAMP,
    approval_notes TEXT,
    is_recurring BOOLEAN DEFAULT FALSE,
    recurring_frequency VARCHAR(20),
    recurring_parent_id UUID,
    next_expected_date DATE,
    tax_deductible BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    valid_from TIMESTAMP DEFAULT NOW(),
    valid_to TIMESTAMP
);

CREATE INDEX idx_expenses_company ON expenses(company_assignment);
CREATE INDEX idx_expenses_category ON expenses(category);
CREATE INDEX idx_expenses_vendor ON expenses(vendor_id);
CREATE INDEX idx_expenses_entity ON expenses(related_to_entity_type, related_to_entity_id);
CREATE INDEX idx_expenses_date ON expenses(expense_date);
CREATE INDEX idx_expenses_status ON expenses(payment_status);
```

---

### Qdrant (Semantic Memory)

**Stores:**
- Invoice document embeddings (PDFs)
  - Customer invoices
  - Vendor invoices
  - Fuel statements
  - Maintenance invoices
- Expense receipt embeddings
- Payment confirmation embeddings
- Bank statement embeddings
- Loan statement embeddings
- Expense/revenue description embeddings

**Why:**
- Semantic search:
  - "Find all maintenance expenses mentioning 'transmission'"
  - "Search invoices from similar vendors"
  - "Find fuel purchases with 'DEF' mentioned"
  - "Locate loan documents with refinancing terms"
- Document retrieval:
  - Original PDFs for audit/verification
  - Invoice images
  - Receipt scans
- Similarity queries:
  - "Find expenses similar to this maintenance record"
  - "Group vendors by invoice format similarity"

**Vector Fields:**
```python
{
    "id": "exp_001",
    "vector": [0.234, 0.567, ...],  # 1536-dim OpenAI embedding
    "payload": {
        "expense_id": "exp_001",
        "type": "expense",
        "category": "Repair & Maintenance",
        "amount": 2500.00,
        "vendor_name": "Bosch Service Center",
        "description": "4 new drive tires - Michelin XZA3+",
        "related_to_entity_id": "6520",
        "document_path": "s3://apex-docs/invoices/bosch-invoice-789456.pdf",
        "full_text": "...complete invoice text..."
    }
}
```

---

### Redis (Working Memory)

**Stores:**
- Recent transactions (last 7-30 days) - fast access
- Outstanding invoice totals by customer (for dashboard)
- Current bank account balances (refreshed hourly)
- Overdue payments alert list
- Upcoming loan payments (next 30 days)
- Daily/weekly expense totals (running totals)
- Cash flow summary (last updated timestamp)

**Why:**
- Fast dashboard access (<100ms):
  - "What's our AR balance right now?"
  - "Today's expenses total?"
  - "Outstanding invoices from Sun-Glo?"
  - "Next loan payment due date?"
- Real-time alerts:
  - Invoice overdue notifications
  - Large expense approval needed
  - Low bank balance warnings
- Cache expiration:
  - Recent transactions: 30-day TTL
  - Account balances: 1-hour TTL
  - Outstanding invoices: 15-minute TTL

**Redis Keys:**
```python
# Recent expenses (last 7 days)
SET expense:recent:2025-11-03 "[exp_001, exp_002, exp_003]" EX 604800  # 7 days

# Outstanding invoices by customer
SET invoices:outstanding:company_sunglo "2525.00" EX 900  # 15 minutes

# Bank account balance
SET bank:balance:bank_origin_checking "52340.00" EX 3600  # 1 hour

# Today's expense total
SET expense:total:today:Origin "15450.00" EX 86400  # 1 day

# Overdue payments
ZADD payments:overdue 1730854800 "inv_customer_003"  # Score = due_date timestamp

# Next loan payments
SET loan:next_payment:loan_001 "2025-12-15|2389.00" EX 2592000  # 30 days
```

---

### Graphiti (Temporal Memory)

**Stores:**
- Expense trend tracking:
  - "Maintenance costs for Unit #6520 over 12 months"
  - "Fuel costs per truck over time"
  - "Insurance premium changes"
- Revenue pattern detection:
  - "Sun-Glo ships more in Q4 (seasonal pattern)"
  - "Dedicated lane revenue consistency"
- Payment behavior tracking:
  - "Sun-Glo pays in 18 days on average"
  - "Vendor payment patterns"
- Budget vs actual over time
- Loan balance reduction tracking
- Bank account balance trends

**Why:**
- Temporal queries:
  - "How have maintenance costs changed for #6520 over 6 months?"
  - "Detect expense spikes"
  - "Track revenue seasonality"
  - "Show loan paydown progress"
- Pattern detection:
  - Recurring expenses missed (should have been charged)
  - Vendor price increases detected
  - Customer payment delays trending
- Forecasting:
  - Predict next month's fuel costs
  - Estimate annual maintenance per truck
  - Project cash flow 90 days out

**Graphiti Episode Example:**
```python
Episode(
    name="Unit #6520 Maintenance Trend - October 2025",
    episode_type="financial_trend",
    content="Unit #6520 incurred $8,450 in maintenance costs during October 2025, consisting of 4 new drive tires ($2,847), brake service ($3,200), oil change ($450), and inspection ($1,953). This is 35% higher than the fleet average of $6,250 per truck for October.",
    source_description="Expense records for Unit #6520, category 'Repair & Maintenance', October 2025",
    created_at="2025-11-01T08:00:00Z",
    valid_at="2025-10-31T23:59:59Z",
    entities=[
        Entity(name="Unit #6520", entity_type="truck"),
        Entity(name="Maintenance Expenses", entity_type="expense_category")
    ],
    edges=[
        Edge(
            source_entity="Unit #6520",
            target_entity="Maintenance Expenses",
            edge_name="INCURRED_ABOVE_AVERAGE",
            fact="Unit #6520 maintenance costs 35% above fleet average in October 2025"
        )
    ]
)
```

---

## Primary Keys & Cross-Database Identity

**Financial entities use UUIDs:**

```python
# Neo4j
(:Expense {
    expense_id: "exp_20251103_001",
    category: "Repair & Maintenance",
    amount: 2500.00,
    related_to_entity_id: "6520"
})

# PostgreSQL
SELECT * FROM expenses WHERE expense_id = 'exp_20251103_001'
SELECT * FROM expenses WHERE related_to_entity_id = '6520'

# Qdrant (for related documents)
search(
    query="brake repair",
    filter={
        "expense_id": "exp_20251103_001"
    }
)

# Redis (recent expense cache)
GET expense:detail:exp_20251103_001
ZADD expense:by_truck:6520 1730649600 "exp_20251103_001"  # Score = timestamp

# Graphiti
Episode(
    name="Truck #6520 Maintenance - November 2025",
    entities=[Entity(name="Unit #6520", entity_type="truck")],
    edges=[Edge(
        source_entity="Unit #6520",
        target_entity="Maintenance Expense",
        fact="$2,500 tire replacement on 2025-11-03"
    )]
)
```

**Link to other entities via THEIR keys:**

```python
# Expense links to truck (Hub 3)
Expense(
    expense_id="exp_001",
    related_to_entity_type="truck",
    related_to_entity_id="6520"  # Truck's unit_number
)

# Revenue links to load (Hub 2)
Revenue(
    revenue_id="rev_001",
    source_entity_type="load",
    source_entity_id="OH-321678"  # Load's load_number
)

# Expense links to vendor (Hub 4)
Expense(
    expense_id="exp_001",
    vendor_id="company_bosch"  # Company's company_id UUID
)

# Loan links to truck (Hub 3)
Loan(
    loan_id="loan_001",
    collateral_entity_type="truck",
    collateral_entity_id="6520"
)
```

---

## Bi-Temporal Tracking Pattern

**Financial records require bi-temporal tracking for audit compliance and historical accuracy.**

### Why Bi-Temporal for Financials?

1. **Transaction Time** - When did we LEARN about this expense/revenue?
2. **Valid Time** - When did this expense/revenue ACTUALLY occur?

**Example: Late Invoice Entry**

```cypher
// Vendor invoice from October entered in November
(:Expense {
    expense_id: "exp_late_001",
    amount: 1500.00,
    expense_date: "2025-10-15",  // VALID TIME - when expense occurred
    posted_date: "2025-11-05",   // TRANSACTION TIME - when we recorded it
    category: "Repair & Maintenance",
    related_to_entity_id: "6520",
    created_at: "2025-11-05T09:00:00Z",  // Transaction time
    valid_from: "2025-10-15T00:00:00Z",  // Valid time
    valid_to: null  // Still current
})

// Query: "What were Unit #6520 expenses in October AS WE KNOW THEM TODAY?"
// Returns: Includes this expense

// Query: "What were Unit #6520 expenses in October AS WE KNEW THEM ON NOVEMBER 1?"
// Returns: Does NOT include this expense (not yet recorded)
```

### Correction Pattern

```cypher
// Original (incorrect) expense
(:Expense {
    expense_id: "exp_001_v1",
    amount: 2000.00,
    expense_date: "2025-11-01",
    created_at: "2025-11-01T08:00:00Z",
    valid_from: "2025-11-01T00:00:00Z",
    valid_to: "2025-11-05T14:00:00Z"  // Invalidated
})

// Corrected expense
(:Expense {
    expense_id: "exp_001_v2",
    amount: 2500.00,  // Corrected amount
    expense_date: "2025-11-01",
    created_at: "2025-11-05T14:00:00Z",  // When correction made
    valid_from: "2025-11-01T00:00:00Z",  // Valid from original date
    valid_to: null  // Current version
})

// Link
(exp_001_v2)-[:SUPERSEDES]->(exp_001_v1)
```

### Invoice Factoring Timeline

```cypher
// Invoice created
(:Invoice {
    invoice_id: "inv_001",
    status: "open",
    amount: 2525.00,
    created_at: "2025-11-04T10:00:00Z",
    valid_from: "2025-11-04T00:00:00Z"
})

// Invoice factored (status change)
(:Invoice {
    invoice_id: "inv_001",
    status: "factored",
    amount: 2525.00,
    created_at: "2025-11-04T10:00:00Z",  // Original creation
    updated_at: "2025-11-05T15:00:00Z",  // Status change time
    valid_from: "2025-11-04T00:00:00Z"
})

// Factoring advance payment
(:Payment {
    payment_id: "pay_001",
    amount: 2399.75,
    payment_date: "2025-11-05",
    created_at: "2025-11-05T15:30:00Z",
    valid_from: "2025-11-05T15:30:00Z"
})
```

---

## Query Pattern Examples

### Performance Tracking Queries

**1. Truck Profitability (Unit #6520)**
```cypher
// Neo4j - Graph traversal
MATCH (t:Tractor {unit_number: "6520"})
MATCH (t)-[:GENERATES]->(rev:Revenue)
WHERE rev.revenue_date >= date("2025-11-01")
  AND rev.revenue_date <= date("2025-11-30")
MATCH (t)-[:INCURS]->(exp:Expense)
WHERE exp.expense_date >= date("2025-11-01")
  AND exp.expense_date <= date("2025-11-30")
RETURN
  t.unit_number as truck,
  sum(rev.amount) as total_revenue,
  sum(exp.amount) as total_expenses,
  sum(rev.amount) - sum(exp.amount) as net_profit,
  round(((sum(rev.amount) - sum(exp.amount)) / sum(rev.amount)) * 100, 2) as profit_margin_percent
```

```sql
-- PostgreSQL - Structured query with detailed breakdown
SELECT
    '6520' as unit_number,
    SUM(r.amount) as total_revenue,
    SUM(CASE WHEN r.category = 'Line Haul Income' THEN r.amount ELSE 0 END) as linehaul_revenue,
    SUM(e.amount) as total_expenses,
    SUM(CASE WHEN e.category = 'Diesel-Truck & DEF' THEN e.amount ELSE 0 END) as fuel_costs,
    SUM(CASE WHEN e.category = 'Repair & Maintenance' THEN e.amount ELSE 0 END) as maintenance_costs,
    SUM(CASE WHEN e.category = 'Driver Wages' THEN e.amount ELSE 0 END) as driver_wages,
    SUM(r.amount) - SUM(e.amount) as net_profit,
    ROUND(((SUM(r.amount) - SUM(e.amount)) / SUM(r.amount)) * 100, 2) as profit_margin_percent
FROM
    revenue r
    FULL OUTER JOIN expenses e ON r.source_entity_id = e.related_to_entity_id
        AND r.source_entity_type = 'truck'
        AND e.related_to_entity_type = 'truck'
WHERE
    (r.source_entity_id = '6520' OR e.related_to_entity_id = '6520')
    AND (r.revenue_date BETWEEN '2025-11-01' AND '2025-11-30'
         OR e.expense_date BETWEEN '2025-11-01' AND '2025-11-30')
GROUP BY unit_number;
```

**2. Load Margin Analysis (Load OH-321678)**
```cypher
// Neo4j
MATCH (l:Load {load_number: "OH-321678"})
MATCH (l)-[:GENERATES]->(rev:Revenue)
MATCH (l)-[:INCURS]->(exp:Expense)
RETURN
  l.load_number as load,
  sum(rev.amount) as total_revenue,
  sum(exp.amount) as total_expense,
  sum(rev.amount) - sum(exp.amount) as gross_profit,
  round(((sum(rev.amount) - sum(exp.amount)) / sum(rev.amount)) * 100, 2) as margin_percent
```

```sql
-- PostgreSQL
SELECT
    'OH-321678' as load_number,
    SUM(r.amount) as customer_charge,
    SUM(CASE WHEN r.category = 'LineHaul Income' THEN r.amount ELSE 0 END) as linehaul_charge,
    SUM(CASE WHEN r.category = 'Accessorial Income' THEN r.amount ELSE 0 END) as accessorial_charge,
    SUM(e.amount) as carrier_cost,
    SUM(CASE WHEN e.category = 'Purchased Transportation' THEN e.amount ELSE 0 END) as carrier_payment,
    SUM(CASE WHEN e.category = 'Accessorial Fees' THEN e.amount ELSE 0 END) as accessorial_cost,
    SUM(r.amount) - SUM(e.amount) as gross_profit,
    ROUND(((SUM(r.amount) - SUM(e.amount)) / SUM(r.amount)) * 100, 2) as margin_percent
FROM
    revenue r
    FULL OUTER JOIN expenses e ON r.source_entity_id = e.related_to_entity_id
WHERE
    r.source_entity_id = 'OH-321678' OR e.related_to_entity_id = 'OH-321678'
GROUP BY load_number;
```

**3. Vendor Spend Analysis**
```cypher
// Neo4j - Vendor concentration risk
MATCH (exp:Expense)-[:PAID_TO]->(v:Company)
WHERE exp.company_assignment = "Origin"
  AND exp.expense_date >= date("2025-01-01")
WITH v, sum(exp.amount) as total_spend, count(exp) as transaction_count
WITH sum(total_spend) as grand_total,
     collect({vendor: v, spend: total_spend, transactions: transaction_count}) as vendors
UNWIND vendors as vendor_data
RETURN
  vendor_data.vendor.company_name as vendor,
  vendor_data.spend as total_spend,
  round((vendor_data.spend / grand_total) * 100, 2) as spend_percentage,
  vendor_data.transactions as transaction_count
ORDER BY total_spend DESC
LIMIT 10
```

```sql
-- PostgreSQL - Detailed vendor analysis with categories
SELECT
    v.company_name as vendor,
    e.category as expense_category,
    COUNT(*) as transaction_count,
    SUM(e.amount) as total_spend,
    ROUND(AVG(e.amount), 2) as average_transaction,
    MIN(e.expense_date) as first_transaction,
    MAX(e.expense_date) as last_transaction
FROM
    expenses e
    JOIN companies v ON e.vendor_id = v.company_id
WHERE
    e.company_assignment = 'Origin'
    AND e.expense_date >= '2025-01-01'
GROUP BY v.company_name, e.category
ORDER BY total_spend DESC;
```

**4. Customer Payment Behavior**
```sql
-- PostgreSQL - Average days to pay by customer
SELECT
    c.company_name as customer,
    COUNT(DISTINCT i.invoice_id) as invoice_count,
    SUM(i.amount) as total_invoiced,
    SUM(p.amount) as total_paid,
    ROUND(AVG(EXTRACT(DAY FROM (p.payment_date - i.invoice_date))), 1) as avg_days_to_pay,
    SUM(CASE WHEN p.payment_date <= i.due_date THEN 1 ELSE 0 END)::FLOAT / COUNT(*) * 100 as on_time_percentage
FROM
    invoices i
    JOIN payments p ON p.invoice_id = i.invoice_id
    JOIN companies c ON i.customer_id = c.company_id
WHERE
    i.invoice_type = 'customer'
    AND i.company_assignment = 'OpenHaul'
    AND i.invoice_date >= '2025-01-01'
GROUP BY c.company_name
ORDER BY total_invoiced DESC;
```

**5. Expense Trend Detection (Graphiti)**
```python
# Query Graphiti for expense patterns
query = "Show maintenance cost trends for Unit #6520 over the last 6 months"

# Graphiti returns temporal pattern
result = graphiti.search(
    query=query,
    filter={"entity_name": "Unit #6520", "entity_type": "truck"}
)

# Returns episodes like:
# "Unit #6520 maintenance costs increased 35% in October 2025"
# "Tire replacements for Unit #6520 every 4 months (pattern detected)"
# "Brake service overdue - last service 8 months ago"
```

---

## Real-World Financial Example: Load OH-321678

This example shows ONE load flowing through the complete financial system across all 5 databases.

**Load Details (Hub 2):**
- Load Number: OH-321678
- Customer: Sun-Glo Nurseries
- Carrier: Origin Transport (Unit #6520, Driver Robert)
- Pickup: 2025-11-01
- Delivery: 2025-11-03

**Financial Flow:**

### Step 1: Customer Invoice Created (2025-11-04)

**Hub 5 → Invoice Created:**
```python
Invoice(
    invoice_id="inv_oh321678",
    invoice_number="OH-INV-2025-11-001",
    invoice_type="customer",
    invoice_date="2025-11-04",
    due_date="2025-11-19",  # net-15
    amount=2525.00,  # $2,375 linehaul + $150 detention
    amount_paid=0,
    amount_outstanding=2525.00,
    status="open",
    company_assignment="OpenHaul",
    customer_id="company_sunglo",
    related_to_entity_type="load",
    related_to_entity_id="OH-321678"
)
```

**Stored Across Databases:**
- **Neo4j:** `(Invoice)-[:BILLED_TO]->(Sun-Glo)`, `(Invoice)-[:FOR_LOAD]->(Load:OH-321678)`
- **PostgreSQL:** Complete invoice record in `invoices` table
- **Qdrant:** Invoice PDF embedded for semantic search
- **Redis:** `SET invoices:outstanding:company_sunglo "2525.00"`
- **Graphiti:** Episode: "Invoice OH-INV-2025-11-001 created for Sun-Glo on 2025-11-04"

### Step 2: Revenue Records Created (2025-11-04)

**Hub 5 → Revenue:**
```python
# Linehaul revenue
Revenue(
    revenue_id="rev_oh321678_linehaul",
    amount=2375.00,
    revenue_date="2025-11-03",  # When load delivered
    posted_date="2025-11-04",
    company_assignment="OpenHaul",
    category="LineHaul Income",
    subcategory="Brokerage",
    customer_id="company_sunglo",
    source_entity_type="load",
    source_entity_id="OH-321678",
    payment_status="pending",
    invoice_id="inv_oh321678"
)

# Accessorial revenue
Revenue(
    revenue_id="rev_oh321678_detention",
    amount=150.00,
    revenue_date="2025-11-03",
    posted_date="2025-11-04",
    company_assignment="OpenHaul",
    category="Accessorial Income",
    subcategory="Detention",
    customer_id="company_sunglo",
    source_entity_type="load",
    source_entity_id="OH-321678",
    payment_status="pending",
    invoice_id="inv_oh321678"
)
```

**Stored Across Databases:**
- **Neo4j:** `(Revenue)-[:RECEIVED_FROM]->(Sun-Glo)`, `(Revenue)-[:GENERATED_BY]->(Load:OH-321678)`, `(Revenue)-[:EARNED_BY]->(OpenHaul)`
- **PostgreSQL:** 2 revenue records in `revenue` table
- **Redis:** `INCRBYFLOAT revenue:total:today:OpenHaul 2525.00`
- **Graphiti:** Episode: "Load OH-321678 generated $2,525 revenue for OpenHaul"

### Step 3: Invoice Factored (2025-11-05)

**Hub 5 → Invoice Status Update + Payment:**
```python
# Invoice status changed
Invoice.status = "factored"
Invoice.factored_by_id = "company_triumph"
Invoice.factoring_date = "2025-11-05"
Invoice.updated_at = "2025-11-05T15:00:00Z"

# Factoring advance payment
Payment(
    payment_id="pay_oh321678_factor_advance",
    amount=2399.75,  # 95% of $2,525
    payment_date="2025-11-05",
    payment_method="factoring_advance",
    payment_direction="inbound",
    company_assignment="OpenHaul",
    from_company_id="company_triumph",
    to_company_id="company_openhaul",
    invoice_id="inv_oh321678",
    partial_payment=True,
    bank_account_id="bank_openhaul_checking",
    transaction_reference="TRIUMPH-ADV-20251105"
)

# Revenue status updated
Revenue.payment_status = "factored"
Revenue.factored = True
Revenue.factor_id = "company_triumph"
Revenue.factored_date = "2025-11-05"
Revenue.factoring_fee = 62.63  # 2.5% of $2,525
```

**Stored Across Databases:**
- **Neo4j:** `(Invoice)-[:FACTORED_BY]->(Triumph)`, `(Payment)-[:ADVANCES]->(Invoice)`
- **PostgreSQL:** Invoice and payment records updated, revenue records updated
- **Redis:** `INCRBYFLOAT bank:balance:bank_openhaul_checking 2399.75`
- **Graphiti:** Episode: "Invoice OH-INV-2025-11-001 factored to Triumph on 2025-11-05"

### Step 4: Carrier Payment (OpenHaul → Origin) (2025-11-05)

**Hub 5 → Expense Created:**
```python
# Carrier payment expense (OpenHaul pays Origin)
Expense(
    expense_id="exp_oh321678_carrier",
    amount=1850.00,
    expense_date="2025-11-05",
    posted_date="2025-11-05",
    payment_date="2025-11-10",  # Will pay in 5 days
    company_assignment="OpenHaul",
    category="Purchased Transportation",
    description="Carrier payment - Load OH-321678",
    vendor_id="company_origin",  # Origin is the carrier
    vendor_name="Origin Transport LLC",
    related_to_entity_type="load",
    related_to_entity_id="OH-321678",
    related_to_secondary_entity_type="truck",
    related_to_secondary_entity_id="6520",
    payment_method="ACH",
    payment_status="scheduled"
)

# Corresponding revenue for Origin
Revenue(
    revenue_id="rev_origin_load_oh321678",
    amount=1850.00,
    revenue_date="2025-11-03",
    posted_date="2025-11-05",
    payment_received_date="2025-11-10",  # Expects payment
    company_assignment="Origin",
    category="Line Haul Income",
    subcategory="Brokerage",
    customer_id="company_openhaul",  # OpenHaul is customer
    source_entity_type="truck",
    source_entity_id="6520",
    source_secondary_entity_id="OH-321678",
    payment_status="pending"
)
```

**Cross-Hub Link (Hub 2 → Hub 5):**
```cypher
(Load:OH-321678)-[:GENERATES]->(Revenue:rev_oh321678_linehaul)
(Load)-[:GENERATES]->(Revenue:rev_oh321678_detention)
(Load)-[:INCURS]->(Expense:exp_oh321678_carrier)

// Margin calculation
(Load)-[:HAS_MARGIN {
    customer_charge: 2525.00,
    carrier_cost: 1850.00,
    gross_profit: 675.00,
    margin_percent: 26.7,
    factoring_fee: 62.63,
    net_profit: 612.37,
    net_margin_percent: 24.3
}]
```

### Step 5: Carrier Payment Executed (2025-11-10)

**Hub 5 → Payment Created:**
```python
Payment(
    payment_id="pay_oh321678_carrier",
    amount=1850.00,
    payment_date="2025-11-10",
    payment_method="ACH",
    payment_direction="outbound",
    company_assignment="OpenHaul",
    from_company_id="company_openhaul",
    to_company_id="company_origin",
    invoice_id=None,  # No formal invoice for this
    bank_account_id="bank_openhaul_checking",
    transaction_reference="ACH-CARRIER-20251110"
)

# Expense status updated
Expense.payment_status = "paid"

# Origin revenue status updated
Revenue.payment_status = "received"
Revenue.payment_received_date = "2025-11-10"
```

**Stored Across Databases:**
- **Neo4j:** `(Payment)-[:FROM]->(OpenHaul)`, `(Payment)-[:TO]->(Origin)`, `(Payment)-[:PAYS]->(Expense)`
- **PostgreSQL:** Payment record created, expense and revenue updated
- **Redis:** `DECRBYFLOAT bank:balance:bank_openhaul_checking 1850.00`, `INCRBYFLOAT bank:balance:bank_origin_checking 1850.00`
- **Graphiti:** Episode: "OpenHaul paid Origin $1,850 for Load OH-321678 on 2025-11-10"

### Step 6: Customer Pays Factor (2025-11-18)

**Hub 5 → Final Settlement:**
```python
# Sun-Glo pays Triumph (full amount)
Payment(
    payment_id="pay_oh321678_customer_to_factor",
    amount=2525.00,
    payment_date="2025-11-18",
    payment_method="ACH",
    payment_direction="inbound",
    company_assignment="OpenHaul",  # For tracking purposes
    from_company_id="company_sunglo",
    to_company_id="company_triumph",
    invoice_id="inv_oh321678",
    memo="Customer payment to factor for invoice OH-INV-2025-11-001"
)

# Triumph settles remaining balance minus fee with OpenHaul
Payment(
    payment_id="pay_oh321678_factor_final",
    amount=125.37,  # $2,525 - $2,399.75 (advance) - $0 (no additional fee, already deducted)
    payment_date="2025-11-18",
    payment_method="ACH",
    payment_direction="inbound",
    company_assignment="OpenHaul",
    from_company_id="company_triumph",
    to_company_id="company_openhaul",
    invoice_id="inv_oh321678",
    bank_account_id="bank_openhaul_checking",
    transaction_reference="TRIUMPH-FINAL-20251118"
)

# Invoice fully paid
Invoice.amount_paid = 2525.00
Invoice.amount_outstanding = 0
Invoice.status = "paid"

# Revenue fully received
Revenue.payment_status = "received"
```

**Complete Financial Flow Summary:**

**OpenHaul (Brokerage):**
- Customer charge: $2,525.00
- Factoring advance (95%): $2,399.75 (received 2025-11-05)
- Factoring fee (2.5%): $62.63
- Carrier cost: $1,850.00 (paid 2025-11-10)
- Final settlement: $125.37 (received 2025-11-18)
- **Net Profit: $612.37 (24.3% margin)**

**Origin (Carrier):**
- Revenue from OpenHaul: $1,850.00 (received 2025-11-10)
- Truck expenses (fuel, driver, maintenance): ~$1,200 (estimated)
- **Net Profit: ~$650 (35% margin)**

**Cross-Database Tracking:**

| Database | What's Stored | Query Example |
|----------|---------------|---------------|
| **Neo4j** | Relationships: Load → Revenue, Load → Expense, Invoice → Payment | "Show complete financial flow for Load OH-321678" |
| **PostgreSQL** | Complete financial records | "Calculate margin for all loads delivered in November" |
| **Qdrant** | Invoice PDF, rate confirmation PDF | "Find similar loads by invoice description" |
| **Redis** | Real-time balances, recent transactions | "Current outstanding invoices from Sun-Glo?" |
| **Graphiti** | Temporal patterns | "Sun-Glo payment behavior over 12 months" |

---

## Document Examples

Hub 5 requires **7 document types** matching Hub 3's baseline standard.

### 1. Customer Invoice (AR)

**Document:** `openhaul-invoice-OH-321678.pdf`
**Type:** Customer Invoice
**Company:** OpenHaul Logistics
**Customer:** Sun-Glo Nurseries

**Extraction Pattern:**
```python
{
    "invoice_type": "customer",
    "invoice_number": "OH-INV-2025-11-001",
    "invoice_date": "2025-11-04",
    "due_date": "2025-11-19",
    "customer_name": "Sun-Glo Nurseries",
    "customer_id": "company_sunglo",  # Match from Hub 4
    "line_items": [
        {
            "description": "Freight - Load OH-321678",
            "category": "LineHaul Income",
            "quantity": 1,
            "rate": 2375.00,
            "amount": 2375.00
        },
        {
            "description": "Detention - 3 hours @ $50/hr",
            "category": "Accessorial Income",
            "subcategory": "Detention",
            "quantity": 3,
            "rate": 50.00,
            "amount": 150.00
        }
    ],
    "total_amount": 2525.00,
    "payment_terms": "Net 15",
    "related_to_entity_type": "load",
    "related_to_entity_id": "OH-321678"
}
```

---

### 2. Vendor Invoice (AP) - Maintenance

**Document:** `bosch-invoice-789456.pdf`
**Type:** Vendor Invoice
**Vendor:** Bosch Service Center
**Company:** Origin Transport

**Extraction Pattern:**
```python
{
    "invoice_type": "vendor",
    "invoice_number": "BOSCH-789456",
    "invoice_date": "2025-11-01",
    "due_date": "2025-11-16",
    "vendor_name": "Bosch Service Center",
    "vendor_id": "company_bosch",  # Match from Hub 4
    "line_items": [
        {
            "description": "4 new drive tires - Michelin XZA3+ 11R22.5",
            "category": "Repair & Maintenance",
            "subcategory": "Tires",
            "quantity": 4,
            "unit_price": 650.00,
            "amount": 2600.00
        },
        {
            "description": "Tire mount & balance",
            "category": "Repair & Maintenance",
            "subcategory": "Labor",
            "quantity": 1,
            "amount": 247.50
        }
    ],
    "total_amount": 2847.50,
    "payment_terms": "Net 15",
    "related_to_entity_type": "truck",
    "related_to_entity_id": "6520"  # Match from Hub 3
}
```

---

### 3. Fuel Invoice - Monthly Statement

**Document:** `fleetone-statement-2025-11.pdf`
**Type:** Vendor Invoice (Bulk Fuel Statement)
**Vendor:** Fleetone
**Company:** Origin Transport

**Extraction Pattern:**
```python
{
    "invoice_type": "vendor",
    "invoice_number": "FLEETONE-202511-MONTHLY",
    "invoice_date": "2025-11-01",
    "due_date": "2025-11-15",
    "vendor_name": "Fleetone",
    "vendor_id": "company_fleetone",
    "line_items": [
        {
            "transaction_date": "2025-11-01",
            "driver_name": "Robert McCullough",
            "driver_id": "driver_robert",  # Matched via Hub 3 temporal assignment
            "truck": "6520",  # Matched via Samsara API cross-reference
            "location": "TA Truck Stop - Exit 45 I-80",
            "gallons": 150.2,
            "price_per_gallon": 3.45,
            "amount": 518.19,
            "category": "Diesel-Truck & DEF",
            "subcategory": "Diesel Fuel"
        },
        {
            "transaction_date": "2025-11-03",
            "driver_name": "Robert McCullough",
            "driver_id": "driver_robert",
            "truck": "6520",
            "location": "Loves - Exit 123 I-70",
            "gallons": 145.8,
            "price_per_gallon": 3.52,
            "amount": 513.22,
            "category": "Diesel-Truck & DEF",
            "subcategory": "Diesel Fuel"
        }
        # ... (50+ transactions)
    ],
    "total_amount": 18450.00,
    "related_to_entity_type": "multiple",  # Multiple trucks
    "related_to_entity_id": "fleet"
}
```

**Challenge:** Fleetone invoices list driver name but NOT unit_number directly.

**Matching Logic (same as Hub 3):**
1. Extract driver_name from invoice
2. Query Samsara API: "Which unit was this driver assigned to on that date?" (Hub 3 temporal tracking)
3. Cross-reference transaction location + time with truck GPS data (Redis cache)
4. Assign with confidence score (high/medium/low/manual_review)
5. Create separate Expense record for each transaction linked to truck + driver

---

### 4. Bank Statement

**Document:** `bank-statement-origin-2025-11.pdf`
**Type:** Bank Statement
**Company:** Origin Transport
**Bank:** Bank of America

**Extraction Pattern:**
```python
{
    "bank_name": "Bank of America",
    "account_name": "Origin Transport Operating Account",
    "account_number_last_4": "1234",
    "statement_period": "2025-11-01 to 2025-11-30",
    "beginning_balance": 48750.00,
    "ending_balance": 52340.00,
    "transactions": [
        {
            "date": "2025-11-10",
            "description": "ACH DEBIT - Bosch Service Center",
            "amount": -2847.50,
            "transaction_type": "debit",
            "matched_payment_id": "pay_20251110_001"  # Match to Payment record
        },
        {
            "date": "2025-11-10",
            "description": "ACH CREDIT - OpenHaul Logistics",
            "amount": 1850.00,
            "transaction_type": "credit",
            "matched_payment_id": "pay_oh321678_carrier"
        },
        # ... (100+ transactions)
    ],
    "total_debits": 98450.00,
    "total_credits": 102040.00,
    "service_charges": 25.00
}
```

**Reconciliation Process:**
- Match bank transactions to Payment records via amount + date + description
- Flag unmatched transactions for manual review
- Update Payment.reconciled = True when matched

---

### 5. Loan Statement

**Document:** `bank-of-america-loan-statement-2025-11.pdf`
**Type:** Loan Statement
**Lender:** Bank of America
**Loan:** Truck Loan - Unit #6520

**Extraction Pattern:**
```python
{
    "lender_name": "Bank of America",
    "loan_number": "LOAN-445566778",
    "statement_date": "2025-11-15",
    "borrower": "Origin Transport LLC",
    "collateral": "2023 Kenworth T680 - VIN 1XKWDB9X5NJ123456",
    "original_amount": 120000.00,
    "current_balance": 78450.00,
    "principal_paid_this_month": 1950.00,
    "interest_paid_this_month": 439.00,
    "total_payment": 2389.00,
    "next_payment_due": "2025-12-15",
    "interest_rate": 5.75,
    "remaining_term": "32 months",
    "payoff_amount": 79120.00,  # If paid today
    "related_to_entity_type": "truck",
    "related_to_entity_id": "6520"  # Match from Hub 3 via VIN lookup
}
```

---

### 6. Payment Confirmation

**Document:** `ach-confirmation-triumph-20251105.pdf`
**Type:** Payment Confirmation
**From:** Triumph Business Capital (Factor)
**To:** OpenHaul Logistics
**Type:** Factoring Advance

**Extraction Pattern:**
```python
{
    "payment_type": "factoring_advance",
    "payment_date": "2025-11-05",
    "payment_method": "ACH",
    "amount": 2399.75,
    "from_company": "Triumph Business Capital",
    "from_company_id": "company_triumph",
    "to_company": "OpenHaul Logistics",
    "to_company_id": "company_openhaul",
    "to_account_last_4": "5678",
    "transaction_reference": "TRIUMPH-ADV-20251105",
    "memo": "Factoring advance for invoice OH-INV-2025-11-001",
    "related_invoice_number": "OH-INV-2025-11-001",
    "related_invoice_id": "inv_oh321678"
}
```

---

### 7. Factoring Agreement / Invoice Submission

**Document:** `triumph-invoice-submission-oh321678.pdf`
**Type:** Factoring Submission
**Factor:** Triumph Business Capital
**Company:** OpenHaul Logistics

**Extraction Pattern:**
```python
{
    "submission_type": "factoring",
    "submission_date": "2025-11-05",
    "factor_name": "Triumph Business Capital",
    "factor_id": "company_triumph",
    "invoice_number": "OH-INV-2025-11-001",
    "invoice_id": "inv_oh321678",
    "invoice_amount": 2525.00,
    "advance_rate": 95,  # percent
    "advance_amount": 2399.75,
    "factoring_fee_rate": 2.5,  # percent
    "factoring_fee": 62.63,
    "reserve_amount": 125.25,  # Held until customer pays
    "expected_payment_date": "2025-11-19",  # Invoice due date
    "recourse": False,  # Non-recourse factoring
    "customer_name": "Sun-Glo Nurseries",
    "customer_id": "company_sunglo"
}
```

---

## TODO - Information Still Needed

### Clarifications Needed

- [x] **QuickBooks Chart of Accounts** - ✅ COMPLETE (Origin + OpenHaul categories provided)
- [ ] **Payment Terms Standard:** Typical net-15, net-30, net-60 for different customer types?
- [ ] **Factoring Process Details:** Complete workflow from invoice submission to final settlement
- [ ] **Loan Covenant Details:** Are there loan covenants (e.g., debt-to-equity ratio) that need tracking?
- [ ] **Budget Tracking:** Should we add Budget entities to track planned vs actual?

### Attribution Rules Needed

- [ ] **Expense Attribution Decision Tree:**
  - When to link expense to truck only?
  - When to link to both truck AND load?
  - When to link to driver?
  - When no attribution (company-wide expenses)?

- [ ] **Multi-Attribution:** Can one expense relate to BOTH truck AND load simultaneously? (e.g., fuel for specific load)

### Document Examples Still Needed

- [ ] Sample factoring agreement (full contract)
- [ ] Sample loan agreement
- [ ] Sample intercompany transfer documentation
- [ ] Sample driver settlement statement (1099 contractor)
- [ ] Sample equipment lease agreement

### Integration Details

- [ ] **Factoring Flow:** Complete workflow documentation (invoice → submission → advance → customer payment → final settlement)
- [ ] **Intercompany Accounting:** How to track running balances between companies? Reconciliation process?
- [ ] **Recurring Expense Management:** Template system for monthly subscriptions (TMS, insurance, software)?
- [ ] **Invoice Approval Workflow:** Threshold amounts requiring approval? Approval hierarchy?

### Cross-Hub Workflow Clarifications

- [ ] Should every Hub 2 Load automatically create Revenue and Expense records? Or manual entry?
- [ ] Should every Hub 3 MaintenanceRecord automatically create an Expense? Or linked later?
- [ ] Should every Hub 3 FuelTransaction automatically create an Expense?
- [ ] How to handle cash transactions with no invoice? (e.g., truck stop purchases)

---

## Financial Insight Patterns (Advanced Queries)

### 1. Vendor Concentration Risk

```cypher
// Neo4j - Detect vendor concentration
MATCH (exp:Expense)-[:PAID_TO]->(v:Company)
WHERE exp.company_assignment = "Origin"
  AND exp.expense_date >= date("2025-01-01")
WITH sum(exp.amount) as grand_total
MATCH (exp2:Expense)-[:PAID_TO]->(v2:Company)
WHERE exp2.company_assignment = "Origin"
  AND exp2.expense_date >= date("2025-01-01")
WITH v2, sum(exp2.amount) as vendor_total, grand_total
WHERE vendor_total / grand_total > 0.20  // >20% concentration
RETURN
  v2.company_name as vendor,
  vendor_total as total_spend,
  round((vendor_total / grand_total) * 100, 2) as concentration_percent,
  "HIGH CONCENTRATION RISK" as alert
ORDER BY concentration_percent DESC
```

### 2. Customer Payment Trending

```sql
-- PostgreSQL - Detect payment delays
WITH payment_trends AS (
    SELECT
        c.company_name as customer,
        DATE_TRUNC('month', i.invoice_date) as month,
        AVG(EXTRACT(DAY FROM (p.payment_date - i.invoice_date))) as avg_days_to_pay
    FROM
        invoices i
        JOIN payments p ON p.invoice_id = i.invoice_id
        JOIN companies c ON i.customer_id = c.company_id
    WHERE
        i.invoice_type = 'customer'
        AND i.invoice_date >= CURRENT_DATE - INTERVAL '6 months'
    GROUP BY c.company_name, DATE_TRUNC('month', i.invoice_date)
)
SELECT
    customer,
    MAX(CASE WHEN month = DATE_TRUNC('month', CURRENT_DATE - INTERVAL '5 months') THEN avg_days_to_pay END) as month_1,
    MAX(CASE WHEN month = DATE_TRUNC('month', CURRENT_DATE - INTERVAL '4 months') THEN avg_days_to_pay END) as month_2,
    MAX(CASE WHEN month = DATE_TRUNC('month', CURRENT_DATE - INTERVAL '3 months') THEN avg_days_to_pay END) as month_3,
    MAX(CASE WHEN month = DATE_TRUNC('month', CURRENT_DATE - INTERVAL '2 months') THEN avg_days_to_pay END) as month_4,
    MAX(CASE WHEN month = DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month') THEN avg_days_to_pay END) as month_5,
    MAX(CASE WHEN month = DATE_TRUNC('month', CURRENT_DATE) THEN avg_days_to_pay END) as month_6,
    CASE
        WHEN MAX(CASE WHEN month = DATE_TRUNC('month', CURRENT_DATE) THEN avg_days_to_pay END) >
             MAX(CASE WHEN month = DATE_TRUNC('month', CURRENT_DATE - INTERVAL '3 months') THEN avg_days_to_pay END) + 5
        THEN 'PAYMENT DELAY DETECTED'
        ELSE 'Normal'
    END as trend_alert
FROM payment_trends
GROUP BY customer
ORDER BY month_6 DESC;
```

### 3. Truck Cost per Mile

```sql
-- PostgreSQL - Calculate cost per mile by truck
SELECT
    t.unit_number,
    t.make || ' ' || t.model as truck,
    COALESCE(SUM(e.amount), 0) as total_expenses,
    t.current_miles - t.beginning_miles_for_period as miles_driven,
    ROUND(COALESCE(SUM(e.amount), 0) / NULLIF(t.current_miles - t.beginning_miles_for_period, 0), 2) as cost_per_mile,
    ROUND(AVG(fleet_avg.cost_per_mile), 2) as fleet_average_cpm,
    ROUND((COALESCE(SUM(e.amount), 0) / NULLIF(t.current_miles - t.beginning_miles_for_period, 0)) - AVG(fleet_avg.cost_per_mile), 2) as variance_from_fleet_avg
FROM
    tractors t
    LEFT JOIN expenses e ON e.related_to_entity_id = t.unit_number
        AND e.related_to_entity_type = 'truck'
        AND e.expense_date >= '2025-11-01'
    CROSS JOIN (
        SELECT
            AVG(total_expenses / NULLIF(miles_driven, 0)) as cost_per_mile
        FROM (
            SELECT
                t2.unit_number,
                SUM(e2.amount) as total_expenses,
                t2.current_miles - t2.beginning_miles_for_period as miles_driven
            FROM
                tractors t2
                LEFT JOIN expenses e2 ON e2.related_to_entity_id = t2.unit_number
            WHERE e2.expense_date >= '2025-11-01'
            GROUP BY t2.unit_number, t2.current_miles, t2.beginning_miles_for_period
        ) subq
    ) fleet_avg
WHERE t.unit_number IS NOT NULL
GROUP BY t.unit_number, t.make, t.model, t.current_miles, t.beginning_miles_for_period
ORDER BY cost_per_mile DESC;
```

### 4. Load Margin Distribution

```cypher
// Neo4j - Analyze load margin distribution
MATCH (l:Load)-[:GENERATES]->(rev:Revenue)
MATCH (l)-[:INCURS]->(exp:Expense)
WHERE l.delivery_date >= date("2025-11-01")
WITH l, sum(rev.amount) as total_rev, sum(exp.amount) as total_exp
WITH l, total_rev, total_exp,
     round(((total_rev - total_exp) / total_rev) * 100, 2) as margin_percent
WITH
    CASE
        WHEN margin_percent < 10 THEN '0-10%'
        WHEN margin_percent < 20 THEN '10-20%'
        WHEN margin_percent < 30 THEN '20-30%'
        WHEN margin_percent < 40 THEN '30-40%'
        ELSE '40%+'
    END as margin_bucket,
    count(l) as load_count,
    avg(margin_percent) as avg_margin
RETURN
    margin_bucket,
    load_count,
    round(avg_margin, 2) as average_margin_in_bucket
ORDER BY margin_bucket
```

### 5. Cash Flow Projection (30 days)

```sql
-- PostgreSQL - Project cash flow
WITH upcoming_receivables AS (
    SELECT
        'Receivable' as type,
        i.due_date as date,
        SUM(i.amount_outstanding) as amount
    FROM invoices i
    WHERE i.invoice_type = 'customer'
        AND i.status IN ('open', 'partial')
        AND i.due_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '30 days'
    GROUP BY i.due_date
),
upcoming_payables AS (
    SELECT
        'Payable' as type,
        i.due_date as date,
        -SUM(i.amount_outstanding) as amount
    FROM invoices i
    WHERE i.invoice_type = 'vendor'
        AND i.status IN ('open', 'partial')
        AND i.due_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '30 days'
    GROUP BY i.due_date
),
upcoming_loans AS (
    SELECT
        'Loan Payment' as type,
        l.next_payment_date as date,
        -l.monthly_payment as amount
    FROM loans l
    WHERE l.status = 'active'
        AND l.next_payment_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '30 days'
),
all_flows AS (
    SELECT * FROM upcoming_receivables
    UNION ALL
    SELECT * FROM upcoming_payables
    UNION ALL
    SELECT * FROM upcoming_loans
)
SELECT
    date,
    SUM(CASE WHEN type = 'Receivable' THEN amount ELSE 0 END) as receivables,
    SUM(CASE WHEN type = 'Payable' THEN amount ELSE 0 END) as payables,
    SUM(CASE WHEN type = 'Loan Payment' THEN amount ELSE 0 END) as loan_payments,
    SUM(amount) as net_flow,
    SUM(SUM(amount)) OVER (ORDER BY date) + (SELECT current_balance FROM bankaccounts WHERE primary_account = TRUE LIMIT 1) as projected_balance
FROM all_flows
GROUP BY date
ORDER BY date;
```

---

## Next Steps

1. **✅ QuickBooks Categories Integrated** - Origin + OpenHaul complete
2. **Clarify Attribution Rules** - Decision tree for expense/revenue attribution
3. **Review Document Extraction Patterns** - Validate 7 document types
4. **Define Factoring Workflow** - Complete end-to-end process documentation
5. **Implement Recurring Expense Templates** - Monthly subscription management
6. **Add Budget Tracking** (Optional) - Planned vs actual comparisons
7. **Cross-Hub Workflow Validation** - Automatic vs manual financial record creation
8. **Create Sample Financial Dashboard Queries** - Real-time performance metrics

---

**Completion Status:** ✅ 95% Complete (QuickBooks integrated, full property definitions, 7 document types, cross-hub links, query patterns, real-world example complete)

**Match to Hub 3 Baseline:**
- ✅ **Entities Defined:** 7 core entities with complete property lists (140+ properties total)
- ✅ **Relationships Documented:** 25+ relationship types with properties
- ✅ **Database Distribution:** Clear mapping for all 5 databases
- ✅ **Document Examples:** 7 document types with extraction patterns
- ✅ **QuickBooks Integration:** Complete Origin (17 expense + 2 revenue) + OpenHaul (8 expense + 2 revenue) categories
- ✅ **Cross-Hub Links:** Complete integration with Hubs 1, 2, 3, 4, 6
- ✅ **Temporal Tracking:** Bi-temporal patterns documented (expense corrections, invoice status changes, payment flows)
- ✅ **Primary Keys:** UUID strategy defined and exemplified across all databases
- ✅ **Real-World Example:** Complete Load OH-321678 financial flow across all 5 databases
- ✅ **Query Patterns:** 10+ advanced query examples (truck profitability, load margin, vendor risk, customer behavior, cash flow projection)
- 🔲 **Attribution Rules:** Need decision tree clarification
- 🔲 **Some TODOs:** Factoring workflow details, recurring expense templates, budget tracking

**This matches Hub 3 baseline detail level.** Ready for Phase 2 deep dive on remaining hubs (Hub 4, Hub 2, Hub 6, Hub 1).

---

**Baseline Established:** November 4, 2025
**Schema Version:** v2.0 (Baseline Complete)
**QuickBooks Integration:** ✅ Complete
