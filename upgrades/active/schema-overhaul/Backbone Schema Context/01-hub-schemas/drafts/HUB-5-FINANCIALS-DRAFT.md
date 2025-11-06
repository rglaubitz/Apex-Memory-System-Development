# HUB 5: FINANCIALS (MONEY FLOWS)

**Status:** 📝 Draft - Rough Structure
**Purpose:** Track where money goes, where it comes from, performance insights, profitability analysis
**Approach:** Operational view (not full accounting) - track performance, spot trends, identify exposure
**Primary Key Strategy:** Invoice/Payment/Expense/Revenue use UUIDs, link to other entities via their keys

---

## Purpose

Hub 5 tracks all financial flows for Origin Transport and OpenHaul. This is the "backend" of operations - what actually got paid and what actually got received.

**Key Objectives:**
1. **Performance Tracking** - Understand profitability by truck, load, customer, route
2. **Trend Detection** - Spot increasing costs, revenue patterns, seasonal changes
3. **Exposure Identification** - High vendor concentration, overdue receivables, cash flow gaps
4. **Insights Generation** - "Truck #6520 maintenance costs 15% above average"

**Operational View vs Full Accounting:**
- **Yes:** Track expenses by category, vendor, equipment, company
- **Yes:** Track revenue by source, customer, load
- **Yes:** Link to operational entities (trucks, loads, vendors)
- **Not Yet:** Full GL accounts, journal entries, tax calculations
- **Later:** Tax-ready categorization (1099s, deductible vs non-deductible)

---

## Core Entities

### 1. **Expense** - Money Going Out
Every expense tracked with full attribution.

**Core Properties:**
- **expense_id** (PRIMARY KEY - UUID)
- amount
- expense_date
- category (from QuickBooks chart of accounts - TO BE PROVIDED)
- description
- company_assignment (Origin, OpenHaul, Primetime, Personal)
- vendor_id (who we paid - links to Hub 4)
- payment_method (check, ACH, credit_card, cash)
- payment_status (pending, paid, overdue)
- tax_deductible (boolean - for future tax tracking)

**Attribution (What/Where):**
- related_to_entity_type (truck, load, company, person, none)
- related_to_entity_id (unit_number, load_number, company_id, etc.)
- subcategory (more specific than main category)

**Document Linkage:**
- invoice_id (if this expense came from an invoice)
- document_path (receipt, invoice PDF)

**Temporal:**
- created_at, updated_at, valid_from, valid_to

**Examples:**
```python
# Truck Maintenance Expense
Expense(
    expense_id="exp_001",
    amount=2500.00,
    expense_date="2025-11-01",
    category="Maintenance & Repairs",
    subcategory="Tires",
    description="4 new drive tires for Unit #6520",
    company_assignment="Origin",
    vendor_id="company_bosch",  # Hub 4
    related_to_entity_type="truck",
    related_to_entity_id="6520",
    payment_status="paid",
    tax_deductible=True
)

# Software Subscription Expense
Expense(
    expense_id="exp_002",
    amount=500.00,
    expense_date="2025-11-01",
    category="Software & Technology",
    subcategory="TMS",
    description="Turvo monthly payment",
    company_assignment="OpenHaul",
    vendor_id="company_turvo",
    related_to_entity_type="company",
    related_to_entity_id="company_openhaul",
    payment_status="paid"
)

# Carrier Payment Expense (from load)
Expense(
    expense_id="exp_003",
    amount=2000.00,
    expense_date="2025-11-05",
    category="Carrier Payments",
    description="Carrier payment for load OH-321678",
    company_assignment="OpenHaul",
    vendor_id="company_origin",  # Origin as carrier
    related_to_entity_type="load",
    related_to_entity_id="OH-321678",  # Hub 2
    payment_status="paid"
)
```

---

### 2. **Revenue** - Money Coming In
Every revenue source tracked.

**Core Properties:**
- **revenue_id** (PRIMARY KEY - UUID)
- amount
- revenue_date
- category (from QuickBooks chart of accounts - TO BE PROVIDED)
- description
- company_assignment (Origin, OpenHaul)
- customer_id (who paid us - links to Hub 4)
- payment_method (ACH, check, wire, factoring)
- payment_status (pending, received, overdue)

**Source Attribution:**
- source_entity_type (load, truck, service, none)
- source_entity_id (load_number, unit_number, etc.)

**Document Linkage:**
- invoice_id (customer invoice that generated this revenue)
- document_path (payment confirmation, remittance advice)

**Examples:**
```python
# Load Revenue
Revenue(
    revenue_id="rev_001",
    amount=2500.00,
    revenue_date="2025-11-10",
    category="Freight Revenue",
    subcategory="Brokerage",
    description="Load OH-321678 payment from Sun-Glo",
    company_assignment="OpenHaul",
    customer_id="company_sunglo",  # Hub 4
    source_entity_type="load",
    source_entity_id="OH-321678",  # Hub 2
    payment_status="received"
)

# Dedicated Lane Revenue
Revenue(
    revenue_id="rev_002",
    amount=3500.00,
    revenue_date="2025-11-08",
    category="Freight Revenue",
    subcategory="Dedicated Lanes",
    description="Weekly dedicated run - Customer XYZ",
    company_assignment="Origin",
    customer_id="company_xyz",
    source_entity_type="truck",
    source_entity_id="6520",  # This truck ran the dedicated lane
    payment_status="received"
)
```

---

### 3. **Invoice** - Bills Sent/Received
Tracks both customer invoices (AR) and vendor invoices (AP).

**Core Properties:**
- **invoice_id** (PRIMARY KEY - UUID)
- invoice_number (vendor's or our invoice number)
- invoice_type (customer, vendor)
- invoice_date
- due_date
- amount
- amount_paid
- amount_outstanding
- status (open, partial, paid, overdue, void)
- company_assignment (Origin, OpenHaul)

**Parties:**
- customer_id (if customer invoice - who we bill)
- vendor_id (if vendor invoice - who billed us)

**Linkage:**
- related_to_entity_type (load, truck, service, etc.)
- related_to_entity_id
- document_path (invoice PDF)

**Payment Tracking:**
- payment_ids [] (array of Payment IDs that paid this invoice)
- factored_by_id (if factored - links to Factor in Hub 2)

**Examples:**
```python
# Customer Invoice
Invoice(
    invoice_type="customer",
    invoice_number="OH-INV-2025-11-001",
    invoice_date="2025-11-05",
    due_date="2025-12-05",  # net-30
    amount=2500.00,
    amount_paid=0,
    amount_outstanding=2500.00,
    status="open",
    company_assignment="OpenHaul",
    customer_id="company_sunglo",
    related_to_entity_type="load",
    related_to_entity_id="OH-321678"
)

# Vendor Invoice
Invoice(
    invoice_type="vendor",
    invoice_number="BOSCH-789456",  # Vendor's invoice number
    invoice_date="2025-11-01",
    due_date="2025-11-16",  # net-15
    amount=2500.00,
    amount_paid=2500.00,
    amount_outstanding=0,
    status="paid",
    company_assignment="Origin",
    vendor_id="company_bosch",
    related_to_entity_type="truck",
    related_to_entity_id="6520"
)
```

---

### 4. **Payment** - Actual Money Transfers
Records of money actually changing hands.

**Core Properties:**
- **payment_id** (PRIMARY KEY - UUID)
- amount
- payment_date
- payment_method (check, ACH, wire, credit_card, cash, factoring_advance)
- payment_direction (inbound, outbound)
- company_assignment (Origin, OpenHaul)

**Parties:**
- from_company_id (who sent money)
- to_company_id (who received money)

**Invoice Linkage:**
- invoice_id (which invoice this payment applies to)
- partial_payment (boolean - is this a partial payment?)

**Bank/Account:**
- bank_account_id (which account money came from / went to)
- transaction_reference (check number, ACH trace, wire confirmation)

**Examples:**
```python
# Customer Payment
Payment(
    amount=2500.00,
    payment_date="2025-11-15",
    payment_method="ACH",
    payment_direction="inbound",
    company_assignment="OpenHaul",
    from_company_id="company_sunglo",
    to_company_id="company_openhaul",
    invoice_id="inv_customer_001",
    bank_account_id="bank_openhaul_checking"
)

# Vendor Payment
Payment(
    amount=2500.00,
    payment_date="2025-11-10",
    payment_method="ACH",
    payment_direction="outbound",
    company_assignment="Origin",
    from_company_id="company_origin",
    to_company_id="company_bosch",
    invoice_id="inv_vendor_001",
    bank_account_id="bank_origin_checking"
)
```

---

### 5. **Loan** - Debt Obligations
Truck loans, lines of credit, equipment financing.

**Core Properties:**
- **loan_id** (PRIMARY KEY - UUID)
- loan_type (equipment, line_of_credit, term_loan)
- lender_id (bank/lender - links to Hub 4)
- original_amount
- current_balance
- interest_rate
- monthly_payment
- start_date, maturity_date
- collateral_entity_type (truck, equipment, none)
- collateral_entity_id (unit_number if truck loan)
- company_assignment (Origin, OpenHaul, Primetime)
- status (active, paid_off, defaulted)

**Examples:**
```python
# Truck Loan
Loan(
    loan_type="equipment",
    lender_id="company_bank_of_america",
    original_amount=120000.00,
    current_balance=85000.00,
    interest_rate=5.5,  # percent
    monthly_payment=2500.00,
    start_date="2023-01-15",
    maturity_date="2028-01-15",  # 5-year term
    collateral_entity_type="truck",
    collateral_entity_id="6520",
    company_assignment="Origin",
    status="active"
)
```

---

### 6. **BankAccount** - Where Money Lives
Bank accounts for each company.

**Core Properties:**
- **bank_account_id** (PRIMARY KEY - UUID)
- account_name
- bank_name
- account_number_last_4 (security - don't store full number)
- account_type (checking, savings, credit_card)
- company_assignment (Origin, OpenHaul, Primetime, G-Personal)
- current_balance (updated periodically)
- currency (USD)
- active_status

**Examples:**
```python
BankAccount(
    account_name="Origin Operating Account",
    bank_name="Bank of America",
    account_number_last_4="1234",
    account_type="checking",
    company_assignment="Origin",
    current_balance=45000.00,
    active_status=True
)
```

---

### 7. **IntercompanyTransfer** - Money Between Companies
Transfers between Origin, OpenHaul, Primetime that are NOT load-related.

**Core Properties:**
- **transfer_id** (PRIMARY KEY - UUID)
- amount
- transfer_date
- from_company_id
- to_company_id
- transfer_type (credit_line, bill_coverage, loan, capital_contribution, distribution)
- description
- repayment_terms (if applicable)
- status (pending, completed, cancelled)

**Examples:**
```python
# Credit Line Extension
IntercompanyTransfer(
    amount=10000.00,
    transfer_date="2025-11-01",
    from_company_id="company_origin",
    to_company_id="company_openhaul",
    transfer_type="credit_line",
    description="Origin extends $10k credit line to OpenHaul for cash flow",
    repayment_terms="Net-30, no interest",
    status="completed"
)
```

**Key Distinction:** This is NOT a load payment. Load payments (Origin hauls for OpenHaul) flow through normal Expense/Revenue tracking in Hub 2 → Hub 5 link.

---

## Primary Relationships

### Expense Attribution
```cypher
// Expense to vendor
(Expense)-[:PAID_TO]->(Vendor:Company)  // Hub 4

// Expense assigned to company
(Expense)-[:ASSIGNED_TO]->(Origin:Company)  // Hub 4 or Hub 6

// Expense relates to equipment
(Expense)-[:RELATES_TO {type: "equipment"}]->(Tractor {unit_number: "6520"})  // Hub 3

// Expense relates to load
(Expense)-[:RELATES_TO {type: "load"}]->(Load {load_number: "OH-321678"})  // Hub 2

// Expense categorization
(Expense)-[:CATEGORIZED_AS]->(Category {name: "Maintenance & Repairs"})
```

### Revenue Attribution
```cypher
// Revenue from customer
(Revenue)-[:RECEIVED_FROM]->(Customer:Company)  // Hub 4

// Revenue earned by company
(Revenue)-[:EARNED_BY]->(OpenHaul:Company)

// Revenue generated by load
(Revenue)-[:GENERATED_BY]->(Load)  // Hub 2

// Revenue generated by truck
(Revenue)-[:GENERATED_BY]->(Tractor)  // Hub 3
```

### Invoice-Payment Chain
```cypher
// Invoice to customer/vendor
(Invoice {type: "customer"})-[:BILLED_TO]->(Customer)  // Hub 4
(Invoice {type: "vendor"})-[:RECEIVED_FROM]->(Vendor)  // Hub 4

// Payment applies to invoice
(Payment)-[:APPLIES_TO]->(Invoice)

// Invoice generates expense/revenue
(Invoice {type: "vendor"})-[:CREATES]->(Expense)
(Invoice {type: "customer"})-[:CREATES]->(Revenue)
```

### Loan Relationships
```cypher
// Loan from lender
(Loan)-[:FROM_LENDER]->(Bank:Company)  // Hub 4

// Loan secures asset
(Loan)-[:SECURES]->(Tractor)  // Hub 3

// Loan payment is expense
(Loan)-[:MONTHLY_PAYMENT_IS]->(Expense {category: "Loan Payment"})
```

---

## Cross-Hub Relationships

### Hub 5 → Hub 2 (OpenHaul)
```cypher
// Load generates revenue and expense
(Load {load_number: "OH-321678"})-[:GENERATES]->(Revenue {amount: 2500})
(Load)-[:INCURS]->(Expense {amount: 2000, category: "Carrier Payment"})

// Invoice links to load
(Invoice)-[:FOR_LOAD]->(Load)
```

### Hub 5 → Hub 3 (Origin)
```cypher
// Truck incurs expenses
(Tractor {unit_number: "6520"})-[:INCURS]->(Expense {category: "Maintenance"})
(Tractor)-[:INCURS]->(Expense {category: "Fuel"})

// Truck generates revenue
(Tractor)-[:GENERATES]->(Revenue {category: "Freight Revenue"})

// Loan secures truck
(Loan)-[:SECURES]->(Tractor)
```

### Hub 5 → Hub 4 (Contacts)
```cypher
// Expenses paid to vendors
(Expense)-[:PAID_TO]->(Vendor:Company)

// Revenue from customers
(Revenue)-[:RECEIVED_FROM]->(Customer:Company)

// Invoices bill/received from companies
(Invoice)-[:BILLED_TO]->(Customer)
(Invoice)-[:RECEIVED_FROM]->(Vendor)

// Loans from banks
(Loan)-[:FROM_LENDER]->(Bank:Company)
```

### Hub 5 → Hub 6 (Corporate)
```cypher
// Expenses/revenue assigned to legal entities
(Expense)-[:ASSIGNED_TO]->(Origin:LegalEntity)
(Revenue)-[:EARNED_BY]->(OpenHaul:LegalEntity)

// Intercompany transfers between legal entities
(IntercompanyTransfer)-[:FROM]->(Origin:LegalEntity)
(IntercompanyTransfer)-[:TO]->(OpenHaul:LegalEntity)
```

### Hub 5 → Hub 1 (G)
```cypher
// Goals measure financial performance
(Goal {title: "Grow Revenue"})-[:MEASURED_BY]->(Revenue)
(Goal {title: "Reduce Costs"})-[:MEASURED_BY]->(Expense)

// Projects impact financials
(Project)-[:RESULTS_IN]->(Revenue)
(Project)-[:REQUIRES]->(Expense)

// Insights about financial patterns
(Insight)-[:ABOUT]->(Expense {category: "Maintenance"})
```

---

## Database Distribution

### Neo4j (Relationship Memory)
**Stores:**
- Basic expense/revenue/invoice/payment nodes
- All attribution relationships (expense → vendor, revenue → customer, invoice → load)
- Cross-hub links (expense → truck, revenue → load)

**Why:** Graph traversal - "Show all expenses for Unit #6520", "Track invoice → payment chain", "Find all revenue from Sun-Glo"

---

### PostgreSQL (Factual Memory)
**Stores:**
- Complete financial records (amounts, dates, descriptions, categories)
- Invoice details (due dates, amounts, payment status)
- Payment details (methods, dates, transaction references)
- Loan schedules and balances
- Bank account information

**Why:** Structured queries - "Total expenses by category YTD", "Outstanding invoices by customer", "Loan payment schedule"

---

### Qdrant (Semantic Memory)
**Stores:**
- Invoice document embeddings (PDFs)
- Expense receipt embeddings
- Payment confirmation embeddings
- Expense/revenue description embeddings

**Why:** Semantic search - "Find all maintenance expenses mentioning 'transmission'", "Search invoices from similar vendors"

---

### Redis (Working Memory)
**Stores:**
- Recent transactions (last 7 days)
- Outstanding invoice totals (for dashboard)
- Current account balances (refreshed hourly)

**Why:** Fast dashboard access - "What's our AR balance right now?", "Recent expenses today"

---

### Graphiti (Temporal Memory)
**Stores:**
- Expense trend tracking (maintenance costs increasing for Unit #6520)
- Revenue pattern detection (Sun-Glo ships more in Q4)
- Payment behavior (vendor payment patterns)
- Budget vs actual over time

**Why:** Temporal queries - "How have maintenance costs changed for #6520 over 6 months?", "Detect expense spikes", "Track revenue seasonality"

---

## Primary Keys & Cross-Database Identity

**Expense/Revenue/Invoice/Payment use UUIDs:**
```python
# Neo4j
(:Expense {expense_id: "exp_001", category: "Maintenance", amount: 2500})

# PostgreSQL
SELECT * FROM expenses WHERE expense_id = 'exp_001'

# Qdrant (for related documents)
filter={"expense_id": "exp_001"}

# Graphiti
Expense(expense_id="exp_001", category="Maintenance", amount=2500, ...)
```

**Link to other entities via THEIR keys:**
```python
# Expense links to truck
Expense(expense_id="exp_001", related_to_entity_id="6520", related_to_entity_type="truck")

# Revenue links to load
Revenue(revenue_id="rev_001", source_entity_id="OH-321678", source_entity_type="load")
```

---

## TODO - Information Needed

### ⭐ CRITICAL: QuickBooks Chart of Accounts
- [ ] **Expense Categories** - Complete list from Origin QuickBooks
- [ ] **Expense Categories** - Complete list from OpenHaul QuickBooks
- [ ] **Revenue Categories** - Complete list from Origin QuickBooks
- [ ] **Revenue Categories** - Complete list from OpenHaul QuickBooks

**User will provide these lists to ensure alignment with existing accounting.**

### Missing Details
- [ ] **Payment Methods:** Complete enumeration (check, ACH, wire, credit_card, cash, factoring, etc.)
- [ ] **Loan Types:** All types tracked (equipment, line_of_credit, term_loan, SBA, personal_guarantee, etc.)
- [ ] **Invoice Status Values:** Complete list (open, partial, paid, overdue, void, disputed, etc.)
- [ ] **Intercompany Transfer Types:** All types (credit_line, bill_coverage, loan, capital_contribution, distribution, etc.)

### Attribution Patterns
- [ ] **Expense Attribution Rules:** When to link to truck vs load vs company vs none?
- [ ] **Revenue Attribution Rules:** When to link to load vs truck vs customer vs service?
- [ ] **Multi-Attribution:** Can one expense relate to BOTH truck AND load? (e.g., fuel for specific load)

### Document Examples
- [ ] Sample customer invoice (AR)
- [ ] Sample vendor invoice (AP)
- [ ] Sample payment confirmation
- [ ] Sample bank statement
- [ ] Sample loan statement

### Integration Questions
- [ ] **Factoring Flow:** Detailed workflow for factoring (invoice → factor → advance → payment → fee)
- [ ] **Intercompany Accounting:** How to track intercompany balances? Reconciliation process?
- [ ] **Budget Tracking:** Should we add Budget entities to compare actual vs planned?
- [ ] **Recurring Expenses:** How to model recurring subscriptions (TMS, insurance, etc.)?

### Cross-Hub Clarifications
- [ ] Should every Hub 2 Load automatically create Revenue and Expense records?
- [ ] Should every Hub 3 MaintenanceRecord automatically create an Expense?
- [ ] How to handle cash transactions with no invoice?

---

## Financial Insight Patterns

**Performance Tracking:**
```cypher
// Truck profitability
MATCH (t:Tractor {unit_number: "6520"})
MATCH (t)-[:GENERATES]->(rev:Revenue)
MATCH (t)-[:INCURS]->(exp:Expense)
RETURN t.unit_number,
       sum(rev.amount) as total_revenue,
       sum(exp.amount) as total_expenses,
       sum(rev.amount) - sum(exp.amount) as net_profit

// Load margin analysis
MATCH (l:Load {load_number: "OH-321678"})
MATCH (l)-[:GENERATES]->(rev:Revenue)
MATCH (l)-[:INCURS]->(exp:Expense)
RETURN l.load_number,
       sum(rev.amount) - sum(exp.amount) as margin

// Vendor spend analysis
MATCH (exp:Expense)-[:PAID_TO]->(v:Company)
WHERE exp.company_assignment = "Origin"
RETURN v.company_name,
       sum(exp.amount) as total_spend,
       count(exp) as transaction_count
ORDER BY total_spend DESC
```

---

## Next Steps

1. **Get QuickBooks chart of accounts** ⭐ CRITICAL - Categories must align
2. **Review this draft** - Does the operational view approach make sense?
3. **Define attribution rules** - When to link expenses to trucks vs loads vs neither?
4. **Clarify factoring flow** - Detailed workflow documentation
5. **Get document examples** - Sample invoices, payments, statements
6. **Deep dive** - Expand to full detail matching Hub 3 baseline

---

**Draft Created:** November 3, 2025
**Schema Version:** v2.0 (Draft)
**Completion Status:** ~30% (structure defined, categories needed from QuickBooks)
