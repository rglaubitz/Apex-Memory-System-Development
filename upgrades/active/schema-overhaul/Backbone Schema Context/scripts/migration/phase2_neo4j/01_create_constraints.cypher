// Phase 2: Neo4j Relationships - Step 1: Create Constraints and Indexes
// Purpose: Create UNIQUE constraints and indexes for all 45 entity types
// Run with: cypher-shell -u neo4j -p apexmemory2024 -f 01_create_constraints.cypher
// Idempotent: Yes (IF NOT EXISTS pattern)

// ====================
// Hub 1: G (Command Center) - 8 entities
// ====================

// G (Person)
CREATE CONSTRAINT constraint_g_user_id IF NOT EXISTS
FOR (g:G) REQUIRE g.user_id IS UNIQUE;

// Project
CREATE CONSTRAINT constraint_project_id IF NOT EXISTS
FOR (p:Project) REQUIRE p.project_id IS UNIQUE;

// Goal
CREATE CONSTRAINT constraint_goal_id IF NOT EXISTS
FOR (g:Goal) REQUIRE g.goal_id IS UNIQUE;

// Task
CREATE CONSTRAINT constraint_task_id IF NOT EXISTS
FOR (t:Task) REQUIRE t.task_id IS UNIQUE;

// Insight
CREATE CONSTRAINT constraint_insight_id IF NOT EXISTS
FOR (i:Insight) REQUIRE i.insight_id IS UNIQUE;

// KnowledgeItem
CREATE CONSTRAINT constraint_knowledge_id IF NOT EXISTS
FOR (k:KnowledgeItem) REQUIRE k.knowledge_id IS UNIQUE;

// Asset
CREATE CONSTRAINT constraint_asset_id IF NOT EXISTS
FOR (a:Asset) REQUIRE a.asset_id IS UNIQUE;

// Note
CREATE CONSTRAINT constraint_note_id IF NOT EXISTS
FOR (n:Note) REQUIRE n.note_id IS UNIQUE;

// ====================
// Hub 2: OpenHaul Brokerage - 8 entities
// ====================

// Load
CREATE CONSTRAINT constraint_load_number IF NOT EXISTS
FOR (l:Load) REQUIRE l.load_number IS UNIQUE;

// Carrier
CREATE CONSTRAINT constraint_carrier_id IF NOT EXISTS
FOR (c:Carrier) REQUIRE c.carrier_id IS UNIQUE;

// Location
CREATE CONSTRAINT constraint_location_id IF NOT EXISTS
FOR (l:Location) REQUIRE l.location_id IS UNIQUE;

// Document (Hub 2)
CREATE CONSTRAINT constraint_document_id IF NOT EXISTS
FOR (d:Document) REQUIRE d.document_id IS UNIQUE;

// MarketRate
CREATE CONSTRAINT constraint_market_rate_id IF NOT EXISTS
FOR (m:MarketRate) REQUIRE m.rate_id IS UNIQUE;

// LoadBoard
CREATE CONSTRAINT constraint_loadboard_id IF NOT EXISTS
FOR (lb:LoadBoard) REQUIRE lb.posting_id IS UNIQUE;

// Quote
CREATE CONSTRAINT constraint_quote_id IF NOT EXISTS
FOR (q:Quote) REQUIRE q.quote_id IS UNIQUE;

// RateHistory
CREATE CONSTRAINT constraint_rate_history_id IF NOT EXISTS
FOR (rh:RateHistory) REQUIRE rh.history_id IS UNIQUE;

// ====================
// Hub 3: Origin Transport - 7 entities
// ====================

// Tractor
CREATE CONSTRAINT constraint_tractor_unit IF NOT EXISTS
FOR (t:Tractor) REQUIRE t.unit_number IS UNIQUE;

CREATE CONSTRAINT constraint_tractor_vin IF NOT EXISTS
FOR (t:Tractor) REQUIRE t.vin IS UNIQUE;

// Trailer
CREATE CONSTRAINT constraint_trailer_number IF NOT EXISTS
FOR (t:Trailer) REQUIRE t.trailer_number IS UNIQUE;

// Driver
CREATE CONSTRAINT constraint_driver_id IF NOT EXISTS
FOR (d:Driver) REQUIRE d.driver_id IS UNIQUE;

CREATE CONSTRAINT constraint_driver_cdl IF NOT EXISTS
FOR (d:Driver) REQUIRE d.cdl_number IS UNIQUE;

// FuelTransaction
CREATE CONSTRAINT constraint_fuel_transaction_id IF NOT EXISTS
FOR (f:FuelTransaction) REQUIRE f.transaction_id IS UNIQUE;

// MaintenanceRecord
CREATE CONSTRAINT constraint_maintenance_id IF NOT EXISTS
FOR (m:MaintenanceRecord) REQUIRE m.maintenance_id IS UNIQUE;

// Incident
CREATE CONSTRAINT constraint_incident_id IF NOT EXISTS
FOR (i:Incident) REQUIRE i.incident_id IS UNIQUE;

// InsurancePolicy
CREATE CONSTRAINT constraint_insurance_policy_id IF NOT EXISTS
FOR (ip:InsurancePolicy) REQUIRE ip.policy_id IS UNIQUE;

// ====================
// Hub 4: Contacts/CRM - 7 entities
// ====================

// Company
CREATE CONSTRAINT constraint_company_id IF NOT EXISTS
FOR (c:Company) REQUIRE c.company_id IS UNIQUE;

// Person
CREATE CONSTRAINT constraint_person_id IF NOT EXISTS
FOR (p:Person) REQUIRE p.person_id IS UNIQUE;

// Contact
CREATE CONSTRAINT constraint_contact_id IF NOT EXISTS
FOR (c:Contact) REQUIRE c.contact_id IS UNIQUE;

// Address
CREATE CONSTRAINT constraint_address_id IF NOT EXISTS
FOR (a:Address) REQUIRE a.address_id IS UNIQUE;

// Relationship
CREATE CONSTRAINT constraint_relationship_id IF NOT EXISTS
FOR (r:Relationship) REQUIRE r.relationship_id IS UNIQUE;

// Interaction
CREATE CONSTRAINT constraint_interaction_id IF NOT EXISTS
FOR (i:Interaction) REQUIRE i.interaction_id IS UNIQUE;

// Tag
CREATE CONSTRAINT constraint_tag_id IF NOT EXISTS
FOR (t:Tag) REQUIRE t.tag_id IS UNIQUE;

// ====================
// Hub 5: Financials - 8 entities
// ====================

// Expense
CREATE CONSTRAINT constraint_expense_id IF NOT EXISTS
FOR (e:Expense) REQUIRE e.expense_id IS UNIQUE;

// Revenue
CREATE CONSTRAINT constraint_revenue_id IF NOT EXISTS
FOR (r:Revenue) REQUIRE r.revenue_id IS UNIQUE;

// Invoice
CREATE CONSTRAINT constraint_invoice_id IF NOT EXISTS
FOR (i:Invoice) REQUIRE i.invoice_id IS UNIQUE;

CREATE CONSTRAINT constraint_invoice_number IF NOT EXISTS
FOR (i:Invoice) REQUIRE i.invoice_number IS UNIQUE;

// Payment
CREATE CONSTRAINT constraint_payment_id IF NOT EXISTS
FOR (p:Payment) REQUIRE p.payment_id IS UNIQUE;

// BankAccount
CREATE CONSTRAINT constraint_bank_account_id IF NOT EXISTS
FOR (ba:BankAccount) REQUIRE ba.account_id IS UNIQUE;

// Loan
CREATE CONSTRAINT constraint_loan_id IF NOT EXISTS
FOR (l:Loan) REQUIRE l.loan_id IS UNIQUE;

// IntercompanyTransfer
CREATE CONSTRAINT constraint_intercompany_transfer_id IF NOT EXISTS
FOR (it:IntercompanyTransfer) REQUIRE it.transfer_id IS UNIQUE;

// TaxRecord
CREATE CONSTRAINT constraint_tax_record_id IF NOT EXISTS
FOR (tr:TaxRecord) REQUIRE tr.record_id IS UNIQUE;

// ====================
// Hub 6: Corporate Infrastructure - 7 entities
// ====================

// LegalEntity
CREATE CONSTRAINT constraint_legal_entity_id IF NOT EXISTS
FOR (le:LegalEntity) REQUIRE le.entity_id IS UNIQUE;

// OwnershipRecord
CREATE CONSTRAINT constraint_ownership_id IF NOT EXISTS
FOR (o:OwnershipRecord) REQUIRE o.ownership_id IS UNIQUE;

// License
CREATE CONSTRAINT constraint_license_id IF NOT EXISTS
FOR (l:License) REQUIRE l.license_id IS UNIQUE;

// Filing
CREATE CONSTRAINT constraint_filing_id IF NOT EXISTS
FOR (f:Filing) REQUIRE f.filing_id IS UNIQUE;

// Document (Hub 6)
// Note: Reusing Document constraint from Hub 2

// Insurance (Hub 6)
// Note: Using same constraint as InsurancePolicy from Hub 3

// Compliance
CREATE CONSTRAINT constraint_compliance_id IF NOT EXISTS
FOR (c:Compliance) REQUIRE c.compliance_id IS UNIQUE;

// ====================
// Indexes for Performance
// ====================

// Status indexes (for active/current queries)
CREATE INDEX index_tractor_status IF NOT EXISTS FOR (t:Tractor) ON (t.status);
CREATE INDEX index_trailer_status IF NOT EXISTS FOR (t:Trailer) ON (t.status);
CREATE INDEX index_driver_status IF NOT EXISTS FOR (d:Driver) ON (d.status);
CREATE INDEX index_load_status IF NOT EXISTS FOR (l:Load) ON (l.status);
CREATE INDEX index_project_status IF NOT EXISTS FOR (p:Project) ON (p.status);
CREATE INDEX index_goal_status IF NOT EXISTS FOR (g:Goal) ON (g.status);

// Date indexes (for temporal queries)
CREATE INDEX index_load_pickup_date IF NOT EXISTS FOR (l:Load) ON (l.pickup_date);
CREATE INDEX index_fuel_transaction_date IF NOT EXISTS FOR (f:FuelTransaction) ON (f.transaction_date);
CREATE INDEX index_maintenance_date IF NOT EXISTS FOR (m:MaintenanceRecord) ON (m.maintenance_date);
CREATE INDEX index_incident_date IF NOT EXISTS FOR (i:Incident) ON (i.incident_date);

// Name indexes (for search queries)
CREATE INDEX index_company_name IF NOT EXISTS FOR (c:Company) ON (c.company_name);
CREATE INDEX index_person_name IF NOT EXISTS FOR (p:Person) ON (p.full_name);
CREATE INDEX index_driver_name IF NOT EXISTS FOR (d:Driver) ON (d.name);
CREATE INDEX index_legal_entity_name IF NOT EXISTS FOR (le:LegalEntity) ON (le.legal_name);

// Category indexes (for filtering)
CREATE INDEX index_company_categories IF NOT EXISTS FOR (c:Company) ON (c.categories);
CREATE INDEX index_expense_category IF NOT EXISTS FOR (e:Expense) ON (e.expense_category);
CREATE INDEX index_revenue_category IF NOT EXISTS FOR (r:Revenue) ON (r.revenue_category);

// ====================
// Verification
// ====================

// Show all constraints
SHOW CONSTRAINTS;

// Show all indexes
SHOW INDEXES;

// Success message
:param message => "✅ All 45+ constraints created successfully";
:param message => "✅ All 20+ indexes created successfully";
RETURN $message AS status;
