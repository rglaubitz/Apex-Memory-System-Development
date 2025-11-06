# 6-HUB IMPLEMENTATION SCHEMAS

**Date:** November 4, 2025
**Purpose:** Production-ready database schemas for all 5 databases
**Status:** ✅ Complete - Ready for implementation
**Version:** v2.0

---

## Document Purpose

This document provides **production-ready implementation code** for all 5 databases:
1. **PostgreSQL** - Complete DDL with indexes and constraints
2. **Neo4j** - Constraints, indexes, and relationship patterns
3. **Qdrant** - Collection configurations and payloads
4. **Redis** - Key patterns and TTL configurations
5. **Graphiti** - Entity tracking configurations

**For complete entity specifications, see:**
- Entity details: `HUB-X-*-COMPLETE.md`
- Cross-reference: `6-HUB-SCHEMA-CROSS-REFERENCE.md`
- Validation: `6-HUB-SCHEMA-VALIDATION-QUERIES.md`

---

## Table of Contents

1. [PostgreSQL Schemas](#postgresql-schemas)
2. [Neo4j Schema](#neo4j-schema)
3. [Qdrant Collections](#qdrant-collections)
4. [Redis Key Patterns](#redis-key-patterns)
5. [Graphiti Entity Tracking](#graphiti-entity-tracking)
6. [Implementation Order](#implementation-order)
7. [Deployment Checklist](#deployment-checklist)

---

## PostgreSQL Schemas

### Core Schema Setup

```sql
-- Create apex_memory database
CREATE DATABASE apex_memory
    WITH
    OWNER = apex
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8'
    TEMPLATE = template0;

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";     -- UUID generation
CREATE EXTENSION IF NOT EXISTS "pg_trgm";       -- Trigram text search
CREATE EXTENSION IF NOT EXISTS "btree_gin";     -- GIN indexes for arrays
CREATE EXTENSION IF NOT EXISTS "pgcrypto";      -- Encryption functions

-- Create schema for each hub
CREATE SCHEMA IF NOT EXISTS hub1_command;       -- G (Command Center)
CREATE SCHEMA IF NOT EXISTS hub2_openhaul;      -- Brokerage Operations
CREATE SCHEMA IF NOT EXISTS hub3_origin;        -- Trucking Operations
CREATE SCHEMA IF NOT EXISTS hub4_contacts;      -- CRM
CREATE SCHEMA IF NOT EXISTS hub5_financials;    -- Money Flows
CREATE SCHEMA IF NOT EXISTS hub6_corporate;     -- Legal Infrastructure

-- Grant permissions
GRANT USAGE ON SCHEMA hub1_command TO apex;
GRANT USAGE ON SCHEMA hub2_openhaul TO apex;
GRANT USAGE ON SCHEMA hub3_origin TO apex;
GRANT USAGE ON SCHEMA hub4_contacts TO apex;
GRANT USAGE ON SCHEMA hub5_financials TO apex;
GRANT USAGE ON SCHEMA hub6_corporate TO apex;
```

---

### Hub 1: G (Command Center)

```sql
-- Table: hub1_command.g_person
CREATE TABLE hub1_command.g_person (
    user_id VARCHAR(50) PRIMARY KEY DEFAULT 'g_main',
    person_id UUID REFERENCES hub4_contacts.people(person_id),
    name VARCHAR(255) NOT NULL,
    display_name VARCHAR(100),

    -- Contact
    email VARCHAR(255) NOT NULL UNIQUE,
    phone VARCHAR(50),
    location VARCHAR(255),
    timezone VARCHAR(100) DEFAULT 'America/Los_Angeles',

    -- Strategic
    role VARCHAR(255),
    vision TEXT,
    current_focus TEXT[],
    decision_framework JSONB,
    communication_style VARCHAR(255),

    -- Preferences
    preferred_meeting_times TEXT[],
    working_hours_start TIME,
    working_hours_end TIME,
    notification_preferences JSONB,

    -- Context
    ownership_stakes JSONB,
    life_stage VARCHAR(100),
    risk_tolerance VARCHAR(50) CHECK (risk_tolerance IN ('conservative', 'moderate', 'aggressive', 'very_aggressive')),
    decision_speed VARCHAR(50) CHECK (decision_speed IN ('deliberate', 'balanced', 'fast', 'instant')),

    -- Temporal
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    valid_from TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    valid_to TIMESTAMPTZ,

    CONSTRAINT only_one_g CHECK (user_id = 'g_main')
);

CREATE INDEX idx_g_person_email ON hub1_command.g_person(email);
CREATE INDEX idx_g_person_temporal ON hub1_command.g_person(valid_from, valid_to) WHERE valid_to IS NULL;


-- Table: hub1_command.projects
CREATE TABLE hub1_command.projects (
    project_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_name VARCHAR(255) NOT NULL,
    project_code VARCHAR(50) UNIQUE,

    -- Classification
    project_type VARCHAR(100) NOT NULL,
    category VARCHAR(100) NOT NULL,
    scope VARCHAR(100) NOT NULL,
    owner_id VARCHAR(50) NOT NULL DEFAULT 'g_main' REFERENCES hub1_command.g_person(user_id),

    -- Status
    status VARCHAR(50) NOT NULL CHECK (status IN ('idea', 'planning', 'active', 'on_hold', 'completed', 'cancelled', 'archived')),
    priority INTEGER CHECK (priority BETWEEN 1 AND 5),
    urgency VARCHAR(50) CHECK (urgency IN ('low', 'medium', 'high', 'critical')),
    visibility VARCHAR(50) CHECK (visibility IN ('private', 'team', 'company', 'public')),

    -- Timeline
    start_date DATE,
    target_completion_date DATE,
    actual_completion_date DATE,
    last_milestone_date DATE,
    next_milestone_date DATE,

    -- Progress
    progress_percentage INTEGER CHECK (progress_percentage BETWEEN 0 AND 100),
    completion_criteria TEXT[],
    blockers TEXT[],

    -- Relationships
    related_to TEXT[],
    related_goals UUID[],
    involved_people UUID[],
    impacted_entities TEXT[],

    -- Content
    description TEXT,
    objective TEXT,
    success_metrics JSONB,

    -- Temporal
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    valid_from TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    valid_to TIMESTAMPTZ
);

CREATE INDEX idx_projects_status ON hub1_command.projects(status) WHERE status IN ('active', 'planning');
CREATE INDEX idx_projects_priority ON hub1_command.projects(priority);
CREATE INDEX idx_projects_owner ON hub1_command.projects(owner_id);
CREATE INDEX idx_projects_temporal ON hub1_command.projects(valid_from, valid_to) WHERE valid_to IS NULL;
CREATE INDEX idx_projects_related_goals ON hub1_command.projects USING GIN (related_goals);


-- Table: hub1_command.goals
CREATE TABLE hub1_command.goals (
    goal_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    goal_title VARCHAR(255) NOT NULL,
    goal_code VARCHAR(50) UNIQUE,

    -- Classification
    goal_type VARCHAR(100) NOT NULL,
    category VARCHAR(100) NOT NULL,
    scope VARCHAR(100) NOT NULL,
    owner_id VARCHAR(50) NOT NULL DEFAULT 'g_main' REFERENCES hub1_command.g_person(user_id),

    -- Status
    status VARCHAR(50) NOT NULL CHECK (status IN ('draft', 'active', 'achieved', 'abandoned', 'deferred')),
    priority INTEGER CHECK (priority BETWEEN 1 AND 5),
    visibility VARCHAR(50) CHECK (visibility IN ('private', 'team', 'company')),

    -- Timeline
    target_date DATE NOT NULL,
    start_tracking_date DATE,
    achieved_date DATE,
    deadline_type VARCHAR(50) CHECK (deadline_type IN ('hard_deadline', 'soft_target', 'aspirational')),

    -- Progress
    progress_percentage INTEGER CHECK (progress_percentage BETWEEN 0 AND 100),
    current_value DECIMAL(15,2),
    target_value DECIMAL(15,2),
    unit_of_measure VARCHAR(100),

    -- Relationships
    related_projects UUID[],
    measured_by_entities TEXT[],
    depends_on_goals UUID[],

    -- Measurement
    metrics JSONB NOT NULL,
    milestone_criteria TEXT[],
    success_definition TEXT,

    -- Content
    description TEXT,
    motivation TEXT,
    obstacles TEXT[],

    -- Temporal
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    valid_from TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    valid_to TIMESTAMPTZ
);

CREATE INDEX idx_goals_status ON hub1_command.goals(status) WHERE status = 'active';
CREATE INDEX idx_goals_target_date ON hub1_command.goals(target_date);
CREATE INDEX idx_goals_type ON hub1_command.goals(goal_type);
CREATE INDEX idx_goals_temporal ON hub1_command.goals(valid_from, valid_to) WHERE valid_to IS NULL;
CREATE INDEX idx_goals_related_projects ON hub1_command.goals USING GIN (related_projects);

-- Additional Hub 1 tables: tasks, knowledge_items, insights, assets, communications
-- (Schemas follow same pattern - see full DDL in deployment scripts)
```

---

### Hub 2: OpenHaul (Brokerage)

```sql
-- Table: hub2_openhaul.loads
CREATE TABLE hub2_openhaul.loads (
    load_number VARCHAR(50) PRIMARY KEY,
    customer_reference VARCHAR(100),

    -- Parties
    customer_id UUID NOT NULL REFERENCES hub4_contacts.companies(company_id),
    carrier_id VARCHAR(100) NOT NULL,  -- Can be UUID or "carr_origin"
    broker_id VARCHAR(100),
    shipper_id UUID REFERENCES hub4_contacts.companies(company_id),
    consignee_id UUID REFERENCES hub4_contacts.companies(company_id),

    -- Locations
    pickup_location_id UUID NOT NULL REFERENCES hub2_openhaul.locations(location_id),
    delivery_location_id UUID NOT NULL REFERENCES hub2_openhaul.locations(location_id),

    -- Dates & Times
    pickup_date DATE NOT NULL,
    pickup_time_window_start TIME,
    pickup_time_window_end TIME,
    pickup_appointment_required BOOLEAN DEFAULT FALSE,
    delivery_date DATE NOT NULL,
    delivery_time_window_start TIME,
    delivery_time_window_end TIME,
    delivery_appointment_required BOOLEAN DEFAULT FALSE,

    -- Equipment & Freight
    equipment_type VARCHAR(50) NOT NULL,
    weight_lbs INTEGER,
    piece_count INTEGER,
    commodity_description TEXT,
    commodity_class VARCHAR(10),
    temperature_range VARCHAR(100),
    special_requirements TEXT[],

    -- Operational Status
    status VARCHAR(50) NOT NULL CHECK (status IN (
        'pending', 'booked', 'dispatched', 'at_pickup', 'loaded',
        'in_transit', 'at_delivery', 'delivered', 'pod_received', 'completed', 'cancelled'
    )),
    current_location_gps POINT,
    eta_delivery TIMESTAMPTZ,
    last_status_update TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Financial
    customer_rate DECIMAL(10,2) NOT NULL,
    carrier_rate DECIMAL(10,2) NOT NULL,
    margin DECIMAL(10,2) GENERATED ALWAYS AS (customer_rate - carrier_rate) STORED,
    accessorial_charges JSONB,

    -- Documents
    sales_order_id UUID REFERENCES hub2_openhaul.sales_orders(sales_order_id),
    rate_con_id UUID REFERENCES hub2_openhaul.rate_confirmations(rate_con_id),
    bol_id UUID REFERENCES hub2_openhaul.bills_of_lading(bol_id),
    pod_id UUID REFERENCES hub2_openhaul.proof_of_deliveries(pod_id),

    -- Temporal
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    booked_date TIMESTAMPTZ,
    completed_date TIMESTAMPTZ,
    valid_from TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    valid_to TIMESTAMPTZ
);

CREATE INDEX idx_loads_customer ON hub2_openhaul.loads(customer_id);
CREATE INDEX idx_loads_carrier ON hub2_openhaul.loads(carrier_id);
CREATE INDEX idx_loads_status ON hub2_openhaul.loads(status) WHERE status NOT IN ('completed', 'cancelled');
CREATE INDEX idx_loads_pickup_date ON hub2_openhaul.loads(pickup_date);
CREATE INDEX idx_loads_delivery_date ON hub2_openhaul.loads(delivery_date);
CREATE INDEX idx_loads_temporal ON hub2_openhaul.loads(valid_from, valid_to) WHERE valid_to IS NULL;
CREATE INDEX idx_loads_location_gps ON hub2_openhaul.loads USING GIST (current_location_gps);

-- Trigger to update margin on rate changes
CREATE OR REPLACE FUNCTION update_load_margin()
RETURNS TRIGGER AS $$
BEGIN
    NEW.margin := NEW.customer_rate - NEW.carrier_rate;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Additional Hub 2 tables: carriers, locations, sales_orders, rate_confirmations, bills_of_lading, etc.
```

---

### Hub 3: Origin Transport (Trucking)

```sql
-- Table: hub3_origin.tractors
CREATE TABLE hub3_origin.tractors (
    unit_number VARCHAR(10) PRIMARY KEY,
    vin VARCHAR(17) UNIQUE,

    -- Basic Info
    make VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL,
    year INTEGER NOT NULL CHECK (year BETWEEN 2000 AND 2030),

    -- Operational Status
    status VARCHAR(50) NOT NULL CHECK (status IN ('active', 'maintenance', 'out_of_service', 'sold')),
    current_miles INTEGER,
    engine_hours INTEGER,
    location_gps POINT,

    -- Financial
    purchase_date DATE,
    purchase_price DECIMAL(12,2),
    current_value DECIMAL(12,2),
    financing_status VARCHAR(50) CHECK (financing_status IN ('owned', 'financed', 'leased')),
    lender_name VARCHAR(255),
    loan_balance DECIMAL(12,2),
    monthly_payment DECIMAL(10,2),

    -- Insurance
    insurance_policy_number VARCHAR(100),
    insurance_provider VARCHAR(255),
    insurance_expiry_date DATE,
    monthly_premium DECIMAL(10,2),

    -- Maintenance
    next_service_due_miles INTEGER,
    last_service_date DATE,

    -- Temporal
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    valid_from TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    valid_to TIMESTAMPTZ,

    CONSTRAINT valid_vin CHECK (LENGTH(vin) = 17),
    CONSTRAINT valid_unit CHECK (unit_number ~ '^\d{4}$')
);

CREATE INDEX idx_tractors_status ON hub3_origin.tractors(status) WHERE status IN ('active', 'maintenance');
CREATE INDEX idx_tractors_vin ON hub3_origin.tractors(vin);
CREATE INDEX idx_tractors_temporal ON hub3_origin.tractors(valid_from, valid_to) WHERE valid_to IS NULL;
CREATE INDEX idx_tractors_location ON hub3_origin.tractors USING GIST (location_gps);
CREATE INDEX idx_tractors_insurance_expiry ON hub3_origin.tractors(insurance_expiry_date) WHERE insurance_expiry_date > CURRENT_DATE;


-- Table: hub3_origin.drivers
CREATE TABLE hub3_origin.drivers (
    driver_id VARCHAR(100) PRIMARY KEY,
    person_id UUID REFERENCES hub4_contacts.people(person_id),

    -- Basic Info
    name VARCHAR(255) NOT NULL,
    cdl_number VARCHAR(50) NOT NULL UNIQUE,
    cdl_expiry DATE NOT NULL,
    hire_date DATE NOT NULL,

    -- Status
    status VARCHAR(50) NOT NULL CHECK (status IN ('active', 'on_leave', 'terminated')),
    current_unit_assignment VARCHAR(10) REFERENCES hub3_origin.tractors(unit_number),

    -- Contact
    phone VARCHAR(50),
    email VARCHAR(255),

    -- Temporal
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    valid_from TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    valid_to TIMESTAMPTZ
);

CREATE INDEX idx_drivers_status ON hub3_origin.drivers(status) WHERE status = 'active';
CREATE INDEX idx_drivers_cdl_expiry ON hub3_origin.drivers(cdl_expiry) WHERE cdl_expiry > CURRENT_DATE;
CREATE INDEX idx_drivers_current_assignment ON hub3_origin.drivers(current_unit_assignment) WHERE current_unit_assignment IS NOT NULL;


-- Table: hub3_origin.fuel_transactions
CREATE TABLE hub3_origin.fuel_transactions (
    fuel_transaction_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    unit_number VARCHAR(10) NOT NULL REFERENCES hub3_origin.tractors(unit_number),
    driver_id VARCHAR(100) REFERENCES hub3_origin.drivers(driver_id),

    -- Transaction Details
    transaction_date DATE NOT NULL,
    fuel_type VARCHAR(50) NOT NULL CHECK (fuel_type IN ('diesel', 'reefer', 'def', 'unleaded')),

    -- Location
    location_name VARCHAR(255),
    location_state VARCHAR(2),

    -- Amounts
    gallons DECIMAL(8,2) NOT NULL,
    price_per_gallon DECIMAL(6,3) NOT NULL,
    total_cost DECIMAL(10,2) NOT NULL,

    -- Reference
    invoice_number VARCHAR(100),
    card_last_5 VARCHAR(5),

    -- Calculated
    odometer_at_fuel INTEGER,
    mpg_calculated DECIMAL(5,2),

    -- Document
    pdf_url VARCHAR(500),

    -- Temporal
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_fuel_unit ON hub3_origin.fuel_transactions(unit_number);
CREATE INDEX idx_fuel_driver ON hub3_origin.fuel_transactions(driver_id);
CREATE INDEX idx_fuel_date ON hub3_origin.fuel_transactions(transaction_date DESC);
CREATE INDEX idx_fuel_invoice ON hub3_origin.fuel_transactions(invoice_number);

-- Additional Hub 3 tables: trailers, maintenance_records, insurance_policies, etc.
```

---

### Hub 4: Contacts (CRM)

```sql
-- Table: hub4_contacts.people
CREATE TABLE hub4_contacts.people (
    person_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Name
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    middle_name VARCHAR(100),
    preferred_name VARCHAR(100),
    suffix VARCHAR(20),

    -- Contact
    email VARCHAR(255),
    phone VARCHAR(50),
    mobile VARCHAR(50),

    -- Professional
    job_title VARCHAR(255),
    linkedin_url VARCHAR(500),

    -- Status
    active_status BOOLEAN DEFAULT TRUE,

    -- Temporal
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    valid_from TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    valid_to TIMESTAMPTZ,

    CONSTRAINT email_or_phone CHECK (email IS NOT NULL OR phone IS NOT NULL)
);

CREATE INDEX idx_people_name ON hub4_contacts.people(last_name, first_name);
CREATE INDEX idx_people_email ON hub4_contacts.people(email) WHERE email IS NOT NULL;
CREATE INDEX idx_people_active ON hub4_contacts.people(active_status) WHERE active_status = TRUE;
CREATE INDEX idx_people_temporal ON hub4_contacts.people(valid_from, valid_to) WHERE valid_to IS NULL;


-- Table: hub4_contacts.companies
CREATE TABLE hub4_contacts.companies (
    company_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Names
    company_name VARCHAR(255) NOT NULL,
    dba_name VARCHAR(255),
    legal_name VARCHAR(255),

    -- Classification
    categories TEXT[] NOT NULL,  -- Multi-category: ["customer", "carrier", "vendor"]
    primary_category VARCHAR(100) NOT NULL,

    -- Related Party
    is_related_party BOOLEAN DEFAULT FALSE,
    related_party_type VARCHAR(100),

    -- Contact
    website VARCHAR(500),
    phone VARCHAR(50),
    email VARCHAR(255),

    -- Status
    active_status BOOLEAN DEFAULT TRUE,

    -- Temporal
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    valid_from TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    valid_to TIMESTAMPTZ,

    CONSTRAINT valid_categories CHECK (array_length(categories, 1) > 0),
    CONSTRAINT primary_in_categories CHECK (primary_category = ANY(categories))
);

CREATE INDEX idx_companies_name ON hub4_contacts.companies(company_name);
CREATE INDEX idx_companies_categories ON hub4_contacts.companies USING GIN (categories);
CREATE INDEX idx_companies_primary_category ON hub4_contacts.companies(primary_category);
CREATE INDEX idx_companies_related_party ON hub4_contacts.companies(is_related_party) WHERE is_related_party = TRUE;
CREATE INDEX idx_companies_active ON hub4_contacts.companies(active_status) WHERE active_status = TRUE;


-- Table: hub4_contacts.addresses
CREATE TABLE hub4_contacts.addresses (
    address_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Address Fields
    address_line1 VARCHAR(255) NOT NULL,
    address_line2 VARCHAR(255),
    city VARCHAR(100) NOT NULL,
    state VARCHAR(50) NOT NULL,
    zip VARCHAR(20) NOT NULL,
    country VARCHAR(100) DEFAULT 'USA',

    -- Geolocation
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    location_point POINT GENERATED ALWAYS AS (POINT(longitude, latitude)) STORED,

    -- Type
    address_type VARCHAR(50),  -- physical, mailing, billing

    -- Temporal
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_addresses_city_state ON hub4_contacts.addresses(city, state);
CREATE INDEX idx_addresses_zip ON hub4_contacts.addresses(zip);
CREATE INDEX idx_addresses_location ON hub4_contacts.addresses USING GIST (location_point);

-- Additional Hub 4 tables: contacts (junction), communication_logs, notes, tags
```

---

### Hub 5: Financials

```sql
-- Table: hub5_financials.expenses
CREATE TABLE hub5_financials.expenses (
    expense_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Amount
    amount DECIMAL(15,2) NOT NULL CHECK (amount > 0),
    expense_date DATE NOT NULL,

    -- Classification
    expense_category VARCHAR(100) NOT NULL,
    subcategory VARCHAR(100),

    -- Parties
    paid_by_entity_id VARCHAR(100) NOT NULL,  -- References hub6 LegalEntity
    paid_to_entity_id VARCHAR(100),

    -- Source
    source_entity_type VARCHAR(100),
    source_load_number VARCHAR(50),
    source_unit_number VARCHAR(10),
    source_entity_id VARCHAR(100),

    -- Related Party Flag
    related_party_transaction BOOLEAN DEFAULT FALSE,

    -- Payment Details
    payment_method VARCHAR(50),
    payment_reference VARCHAR(255),
    invoice_id UUID REFERENCES hub5_financials.invoices(invoice_id),

    -- Description
    description TEXT,
    notes TEXT,

    -- Temporal
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_expenses_date ON hub5_financials.expenses(expense_date DESC);
CREATE INDEX idx_expenses_category ON hub5_financials.expenses(expense_category);
CREATE INDEX idx_expenses_paid_by ON hub5_financials.expenses(paid_by_entity_id);
CREATE INDEX idx_expenses_paid_to ON hub5_financials.expenses(paid_to_entity_id) WHERE paid_to_entity_id IS NOT NULL;
CREATE INDEX idx_expenses_source_load ON hub5_financials.expenses(source_load_number) WHERE source_load_number IS NOT NULL;
CREATE INDEX idx_expenses_source_unit ON hub5_financials.expenses(source_unit_number) WHERE source_unit_number IS NOT NULL;
CREATE INDEX idx_expenses_related_party ON hub5_financials.expenses(related_party_transaction) WHERE related_party_transaction = TRUE;


-- Table: hub5_financials.revenue
CREATE TABLE hub5_financials.revenue (
    revenue_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Amount
    amount DECIMAL(15,2) NOT NULL CHECK (amount > 0),
    revenue_date DATE NOT NULL,

    -- Classification
    revenue_category VARCHAR(100) NOT NULL,
    subcategory VARCHAR(100),

    -- Parties
    received_by_entity_id VARCHAR(100) NOT NULL,  -- References hub6 LegalEntity
    received_from_entity_id VARCHAR(100),

    -- Source
    source_entity_type VARCHAR(100),
    source_load_number VARCHAR(50),
    source_entity_id VARCHAR(100),

    -- Related Party Flag
    related_party_transaction BOOLEAN DEFAULT FALSE,

    -- Payment Details
    payment_method VARCHAR(50),
    payment_reference VARCHAR(255),
    invoice_id UUID REFERENCES hub5_financials.invoices(invoice_id),

    -- Description
    description TEXT,
    notes TEXT,

    -- Temporal
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_revenue_date ON hub5_financials.revenue(revenue_date DESC);
CREATE INDEX idx_revenue_category ON hub5_financials.revenue(revenue_category);
CREATE INDEX idx_revenue_received_by ON hub5_financials.revenue(received_by_entity_id);
CREATE INDEX idx_revenue_received_from ON hub5_financials.revenue(received_from_entity_id) WHERE received_from_entity_id IS NOT NULL;
CREATE INDEX idx_revenue_source_load ON hub5_financials.revenue(source_load_number) WHERE source_load_number IS NOT NULL;


-- Table: hub5_financials.intercompany_transfers
CREATE TABLE hub5_financials.intercompany_transfers (
    transfer_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Amount
    amount DECIMAL(15,2) NOT NULL CHECK (amount > 0),
    transfer_date DATE NOT NULL,

    -- Type
    transfer_type VARCHAR(100) NOT NULL CHECK (transfer_type IN ('loan', 'distribution', 'equity_injection', 'repayment')),

    -- Parties (both must be LegalEntity IDs)
    from_entity_id VARCHAR(100) NOT NULL,
    to_entity_id VARCHAR(100) NOT NULL,

    -- Purpose
    purpose TEXT,
    related_asset VARCHAR(100),

    -- Repayment Terms (for loans)
    repayment_terms JSONB,

    -- Temporal
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT different_entities CHECK (from_entity_id <> to_entity_id)
);

CREATE INDEX idx_transfers_date ON hub5_financials.intercompany_transfers(transfer_date DESC);
CREATE INDEX idx_transfers_type ON hub5_financials.intercompany_transfers(transfer_type);
CREATE INDEX idx_transfers_from ON hub5_financials.intercompany_transfers(from_entity_id);
CREATE INDEX idx_transfers_to ON hub5_financials.intercompany_transfers(to_entity_id);

-- Additional Hub 5 tables: invoices, payments, loans, bank_accounts, payment_terms
```

---

### Hub 6: Corporate (Legal Infrastructure)

```sql
-- Table: hub6_corporate.legal_entities
CREATE TABLE hub6_corporate.legal_entities (
    entity_id VARCHAR(100) PRIMARY KEY,

    -- Names
    legal_name VARCHAR(255) NOT NULL,
    dba_name VARCHAR(255),
    short_name VARCHAR(100),

    -- Entity Type
    entity_type VARCHAR(50) NOT NULL CHECK (entity_type IN ('LLC', 'S_Corp', 'C_Corp', 'partnership', 'sole_proprietorship')),

    -- Formation
    state_of_formation VARCHAR(50) NOT NULL,
    formation_date DATE,
    ein VARCHAR(20) UNIQUE,

    -- Business
    business_purpose TEXT,
    fiscal_year_end VARCHAR(10),
    accounting_method VARCHAR(50) CHECK (accounting_method IN ('cash', 'accrual')),

    -- Status
    status VARCHAR(50) NOT NULL CHECK (status IN ('active', 'dissolved', 'suspended')),
    good_standing BOOLEAN DEFAULT TRUE,

    -- Relationships
    parent_entity_id VARCHAR(100) REFERENCES hub6_corporate.legal_entities(entity_id),

    -- Temporal
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    valid_from TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    valid_to TIMESTAMPTZ,

    CONSTRAINT valid_entity_id CHECK (entity_id ~ '^entity_[a-z_]+$')
);

CREATE INDEX idx_legal_entities_name ON hub6_corporate.legal_entities(legal_name);
CREATE INDEX idx_legal_entities_ein ON hub6_corporate.legal_entities(ein) WHERE ein IS NOT NULL;
CREATE INDEX idx_legal_entities_parent ON hub6_corporate.legal_entities(parent_entity_id) WHERE parent_entity_id IS NOT NULL;
CREATE INDEX idx_legal_entities_status ON hub6_corporate.legal_entities(status) WHERE status = 'active';
CREATE INDEX idx_legal_entities_temporal ON hub6_corporate.legal_entities(valid_from, valid_to) WHERE valid_to IS NULL;


-- Table: hub6_corporate.ownership
CREATE TABLE hub6_corporate.ownership (
    ownership_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Owner (Person OR Entity)
    owner_person_id UUID REFERENCES hub4_contacts.people(person_id),
    owner_entity_id VARCHAR(100) REFERENCES hub6_corporate.legal_entities(entity_id),

    -- Owned Entity
    owned_entity_id VARCHAR(100) NOT NULL REFERENCES hub6_corporate.legal_entities(entity_id),

    -- Ownership Details
    ownership_percentage DECIMAL(5,2) NOT NULL CHECK (ownership_percentage BETWEEN 0.01 AND 100.00),
    acquisition_date DATE NOT NULL,
    cost_basis DECIMAL(15,2),
    voting_rights BOOLEAN DEFAULT TRUE,

    -- Temporal
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    valid_from TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    valid_to TIMESTAMPTZ,

    CONSTRAINT owner_xor CHECK ((owner_person_id IS NOT NULL)::INTEGER + (owner_entity_id IS NOT NULL)::INTEGER = 1)
);

CREATE INDEX idx_ownership_person ON hub6_corporate.ownership(owner_person_id) WHERE owner_person_id IS NOT NULL;
CREATE INDEX idx_ownership_entity_owner ON hub6_corporate.ownership(owner_entity_id) WHERE owner_entity_id IS NOT NULL;
CREATE INDEX idx_ownership_owned ON hub6_corporate.ownership(owned_entity_id);
CREATE INDEX idx_ownership_temporal ON hub6_corporate.ownership(valid_from, valid_to) WHERE valid_to IS NULL;

-- Additional Hub 6 tables: licenses, filings, brand_assets, company_documents, awards
```

---

## Neo4j Schema

### Constraints and Indexes

```cypher
// ============================================
// HUB 1: G (COMMAND CENTER)
// ============================================

// G Person - Unique constraint
CREATE CONSTRAINT constraint_g_user_id IF NOT EXISTS
FOR (g:GPerson) REQUIRE g.user_id IS UNIQUE;

CREATE INDEX index_g_email IF NOT EXISTS
FOR (g:GPerson) ON (g.email);

// Projects
CREATE CONSTRAINT constraint_project_id IF NOT EXISTS
FOR (p:Project) REQUIRE p.project_id IS UNIQUE;

CREATE INDEX index_project_status IF NOT EXISTS
FOR (p:Project) ON (p.status);

CREATE INDEX index_project_owner IF NOT EXISTS
FOR (p:Project) ON (p.owner_id);

// Goals
CREATE CONSTRAINT constraint_goal_id IF NOT EXISTS
FOR (g:Goal) REQUIRE g.goal_id IS UNIQUE;

CREATE INDEX index_goal_status IF NOT EXISTS
FOR (g:Goal) ON (g.status);

// Tasks
CREATE CONSTRAINT constraint_task_id IF NOT EXISTS
FOR (t:Task) REQUIRE t.task_id IS UNIQUE;

// Knowledge Items
CREATE CONSTRAINT constraint_knowledge_id IF NOT EXISTS
FOR (k:KnowledgeItem) REQUIRE k.knowledge_id IS UNIQUE;

// Insights
CREATE CONSTRAINT constraint_insight_id IF NOT EXISTS
FOR (i:Insight) REQUIRE i.insight_id IS UNIQUE;

CREATE INDEX index_insight_type IF NOT EXISTS
FOR (i:Insight) ON (i.insight_type);


// ============================================
// HUB 2: OPENHAUL (BROKERAGE)
// ============================================

// Loads - Unique constraint on load_number
CREATE CONSTRAINT constraint_load_number IF NOT EXISTS
FOR (l:Load) REQUIRE l.load_number IS UNIQUE;

CREATE INDEX index_load_status IF NOT EXISTS
FOR (l:Load) ON (l.status);

CREATE INDEX index_load_customer IF NOT EXISTS
FOR (l:Load) ON (l.customer_id);

CREATE INDEX index_load_carrier IF NOT EXISTS
FOR (l:Load) ON (l.carrier_id);

CREATE INDEX index_load_pickup_date IF NOT EXISTS
FOR (l:Load) ON (l.pickup_date);

// Carriers
CREATE CONSTRAINT constraint_carrier_id IF NOT EXISTS
FOR (c:Carrier) REQUIRE c.carrier_id IS UNIQUE;

CREATE INDEX index_carrier_name IF NOT EXISTS
FOR (c:Carrier) ON (c.carrier_name);

// Locations
CREATE CONSTRAINT constraint_location_id IF NOT EXISTS
FOR (loc:Location) REQUIRE loc.location_id IS UNIQUE;


// ============================================
// HUB 3: ORIGIN TRANSPORT (TRUCKING)
// ============================================

// Tractors - Unique constraint on unit_number
CREATE CONSTRAINT constraint_tractor_unit IF NOT EXISTS
FOR (t:Tractor) REQUIRE t.unit_number IS UNIQUE;

CREATE CONSTRAINT constraint_tractor_vin IF NOT EXISTS
FOR (t:Tractor) REQUIRE t.vin IS UNIQUE;

CREATE INDEX index_tractor_status IF NOT EXISTS
FOR (t:Tractor) ON (t.status);

// Drivers
CREATE CONSTRAINT constraint_driver_id IF NOT EXISTS
FOR (d:Driver) REQUIRE d.driver_id IS UNIQUE;

CREATE INDEX index_driver_status IF NOT EXISTS
FOR (d:Driver) ON (d.status);

// Fuel Transactions
CREATE CONSTRAINT constraint_fuel_transaction_id IF NOT EXISTS
FOR (f:FuelTransaction) REQUIRE f.fuel_transaction_id IS UNIQUE;

// Maintenance Records
CREATE CONSTRAINT constraint_maintenance_id IF NOT EXISTS
FOR (m:MaintenanceRecord) REQUIRE m.maintenance_id IS UNIQUE;


// ============================================
// HUB 4: CONTACTS (CRM)
// ============================================

// People
CREATE CONSTRAINT constraint_person_id IF NOT EXISTS
FOR (p:Person) REQUIRE p.person_id IS UNIQUE;

CREATE INDEX index_person_email IF NOT EXISTS
FOR (p:Person) ON (p.email);

CREATE INDEX index_person_name IF NOT EXISTS
FOR (p:Person) ON (p.last_name, p.first_name);

// Companies
CREATE CONSTRAINT constraint_company_id IF NOT EXISTS
FOR (c:Company) REQUIRE c.company_id IS UNIQUE;

CREATE INDEX index_company_name IF NOT EXISTS
FOR (c:Company) ON (c.company_name);

CREATE INDEX index_company_categories IF NOT EXISTS
FOR (c:Company) ON (c.categories);

// Addresses
CREATE CONSTRAINT constraint_address_id IF NOT EXISTS
FOR (a:Address) REQUIRE a.address_id IS UNIQUE;


// ============================================
// HUB 5: FINANCIALS
// ============================================

// Expenses
CREATE CONSTRAINT constraint_expense_id IF NOT EXISTS
FOR (e:Expense) REQUIRE e.expense_id IS UNIQUE;

CREATE INDEX index_expense_date IF NOT EXISTS
FOR (e:Expense) ON (e.expense_date);

CREATE INDEX index_expense_category IF NOT EXISTS
FOR (e:Expense) ON (e.expense_category);

// Revenue
CREATE CONSTRAINT constraint_revenue_id IF NOT EXISTS
FOR (r:Revenue) REQUIRE r.revenue_id IS UNIQUE;

CREATE INDEX index_revenue_date IF NOT EXISTS
FOR (r:Revenue) ON (r.revenue_date);

// Intercompany Transfers
CREATE CONSTRAINT constraint_transfer_id IF NOT EXISTS
FOR (t:IntercompanyTransfer) REQUIRE t.transfer_id IS UNIQUE;


// ============================================
// HUB 6: CORPORATE (LEGAL INFRASTRUCTURE)
// ============================================

// Legal Entities
CREATE CONSTRAINT constraint_entity_id IF NOT EXISTS
FOR (e:LegalEntity) REQUIRE e.entity_id IS UNIQUE;

CREATE INDEX index_entity_name IF NOT EXISTS
FOR (e:LegalEntity) ON (e.legal_name);

CREATE INDEX index_entity_ein IF NOT EXISTS
FOR (e:LegalEntity) ON (e.ein);

// Ownership
CREATE CONSTRAINT constraint_ownership_id IF NOT EXISTS
FOR (o:Ownership) REQUIRE o.ownership_id IS UNIQUE;

// Licenses
CREATE CONSTRAINT constraint_license_id IF NOT EXISTS
FOR (l:License) REQUIRE l.license_id IS UNIQUE;

CREATE INDEX index_license_type IF NOT EXISTS
FOR (l:License) ON (l.license_type);
```

---

### Key Relationship Patterns

```cypher
// Strategic Relationships (Hub 1)
(:GPerson {user_id: "g_main"})-[:OWNS {percentage: 100}]->(:LegalEntity {entity_id: "entity_primetime"})
(:Project)-[:HAS_TASK]->(:Task)
(:Goal)-[:MEASURED_BY]->(:Revenue | :Expense)
(:Insight)-[:ABOUT]->(:Tractor | :Load | :Company)

// Operational Flow (Hub 2)
(:Load)-[:CUSTOMER]->(:Company)
(:Load)-[:HAULED_BY]->(:Carrier)
(:Load)-[:ASSIGNED_UNIT]->(:Tractor)

// Fleet Operations (Hub 3)
(:Driver)-[:ASSIGNED_TO {
    assigned_date: date,
    end_date: date,
    valid_from: timestamp,
    valid_to: timestamp
}]->(:Tractor)
(:Tractor)-[:CONSUMES]->(:FuelTransaction)
(:Tractor)-[:REQUIRES_MAINTENANCE]->(:MaintenanceRecord)

// CRM Network (Hub 4)
(:Person)-[:WORKS_FOR {role: string}]->(:Company)
(:Person)-[:HAS_ADDRESS]->(:Address)
(:Company)-[:LEGAL_ENTITY]->(:LegalEntity)

// Financial Flows (Hub 5)
(:Expense)-[:SOURCE]->(:Load | :Tractor)
(:Revenue)-[:SOURCE]->(:Load)
(:Expense)-[:PAID_BY]->(:LegalEntity)
(:Revenue)-[:RECEIVED_BY]->(:LegalEntity)

// Legal Structure (Hub 6)
(:LegalEntity)-[:OWNS]->(:Tractor)
(:Person)-[:OWNS {percentage: decimal}]->(:LegalEntity)
(:LegalEntity)-[:OWNS {percentage: decimal}]->(:LegalEntity)
```

---

## Qdrant Collections

### Collection Configurations

```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PayloadSchemaType

client = QdrantClient(host="localhost", port=6333)

# Collection 1: Documents (Hub 2, 3, 6)
client.create_collection(
    collection_name="documents",
    vectors_config=VectorParams(
        size=1536,  # OpenAI text-embedding-3-large
        distance=Distance.COSINE
    )
)

# Add payload indexes for filtering
client.create_payload_index(
    collection_name="documents",
    field_name="document_type",
    field_schema=PayloadSchemaType.KEYWORD
)

client.create_payload_index(
    collection_name="documents",
    field_name="entity_type",
    field_schema=PayloadSchemaType.KEYWORD
)

client.create_payload_index(
    collection_name="documents",
    field_name="date",
    field_schema=PayloadSchemaType.DATETIME
)


# Collection 2: Knowledge Items (Hub 1)
client.create_collection(
    collection_name="knowledge_items",
    vectors_config=VectorParams(
        size=1536,
        distance=Distance.COSINE
    )
)

client.create_payload_index(
    collection_name="knowledge_items",
    field_name="category",
    field_schema=PayloadSchemaType.KEYWORD
)


# Collection 3: Insights (Hub 1)
client.create_collection(
    collection_name="insights",
    vectors_config=VectorParams(
        size=1536,
        distance=Distance.COSINE
    )
)

client.create_payload_index(
    collection_name="insights",
    field_name="insight_type",
    field_schema=PayloadSchemaType.KEYWORD
)


# Example document payload structure
example_payload = {
    "document_id": "doc_12345",
    "document_type": "maintenance_receipt",
    "entity_type": "tractor",
    "entity_id": "6520",
    "date": "2025-11-01T00:00:00Z",
    "total_cost": 2500.00,
    "vendor_name": "Kenworth Las Vegas",
    "pdf_url": "gs://apex-docs/trucks/6520/maintenance/2025-11-01.pdf",
    "hub": 3
}
```

---

## Redis Key Patterns

### Key Naming Conventions and TTLs

```python
# Hub 1: G (Command Center)
redis.setex("g:focus:g_main", 60, json.dumps(["OpenHaul Growth", "Fleet Optimization"]))
redis.setex("g:projects:active", 300, json.dumps([{"project_id": "...", "name": "..."}]))
redis.setex("g:insights:recent", 86400, json.dumps([...]))

# Hub 2: OpenHaul (Brokerage)
redis.setex(f"load:{load_number}:status", 300, status)
redis.setex(f"load:active_list", 300, json.dumps([load_numbers]))
redis.setex(f"carrier:available", 600, json.dumps([carrier_ids]))

# Hub 3: Origin Transport (Trucking) - Real-time Samsara data
redis.setex(f"truck:{unit_number}:location", 60, json.dumps({"lat": 36.1699, "lon": -115.1398}))
redis.setex(f"truck:{unit_number}:status", 60, "active")
redis.setex(f"truck:{unit_number}:current_driver", 300, driver_id)
redis.setex(f"truck:{unit_number}:current_miles", 60, str(odometer))

# Hub 4: Contacts (CRM)
redis.setex("company:active", 3600, json.dumps([company_ids]))
redis.setex("person:contacts:recent", 3600, json.dumps([person_ids]))

# Hub 5: Financials
redis.setex("invoice:unpaid", 3600, json.dumps([invoice_ids]))
redis.setex(f"account:{account_id}:balance", 300, str(balance))

# Hub 6: Corporate (Legal Infrastructure)
redis.setex("license:expiring:30days", 86400, json.dumps([license_ids]))
redis.setex("filing:due:current_quarter", 86400, json.dumps([filing_ids]))
```

---

## Graphiti Entity Tracking

### Entity Tracking Configuration

```python
from graphiti import Graphiti

# Initialize Graphiti
graphiti = Graphiti(api_key="...", storage_backend="postgresql")

# Configure tracked entities
tracked_entities = [
    # Hub 1
    {"entity_type": "GPerson", "id_field": "user_id", "temporal_properties": ["current_focus", "ownership_stakes"]},
    {"entity_type": "Project", "id_field": "project_id", "temporal_properties": ["status", "progress_percentage"]},
    {"entity_type": "Goal", "id_field": "goal_id", "temporal_properties": ["status", "progress_percentage", "current_value"]},

    # Hub 2
    {"entity_type": "Load", "id_field": "load_number", "temporal_properties": ["status", "current_location_gps", "eta_delivery"]},
    {"entity_type": "Carrier", "id_field": "carrier_id", "temporal_properties": ["rating", "on_time_percentage"]},

    # Hub 3
    {"entity_type": "Tractor", "id_field": "unit_number", "temporal_properties": ["status", "current_miles", "current_driver_id", "location_gps"]},
    {"entity_type": "Driver", "id_field": "driver_id", "temporal_properties": ["status", "current_unit_assignment"]},

    # Hub 4
    {"entity_type": "Person", "id_field": "person_id", "temporal_properties": ["job_title", "active_status"]},
    {"entity_type": "Company", "id_field": "company_id", "temporal_properties": ["categories", "active_status"]},

    # Hub 5
    {"entity_type": "Loan", "id_field": "loan_id", "temporal_properties": ["remaining_balance", "payment_status"]},

    # Hub 6
    {"entity_type": "LegalEntity", "id_field": "entity_id", "temporal_properties": ["status", "good_standing"]},
    {"entity_type": "Ownership", "id_field": "ownership_id", "temporal_properties": ["ownership_percentage"]},
    {"entity_type": "License", "id_field": "license_id", "temporal_properties": ["status", "expiration_date"]},
]

# Register entities with Graphiti
for entity_config in tracked_entities:
    graphiti.register_entity_type(**entity_config)
```

---

## Implementation Order

### Phase 1: PostgreSQL Foundation
1. Create database and extensions
2. Create all schemas (hub1-6)
3. Create tables in dependency order:
   - Hub 6 (Legal Entities) first
   - Hub 4 (Contacts) second
   - Hub 3, 2 (Operations) third
   - Hub 5 (Financials) fourth
   - Hub 1 (G) last
4. Create all indexes
5. Create triggers and functions

### Phase 2: Neo4j Relationships
1. Create all constraints
2. Create all indexes
3. Test relationship patterns

### Phase 3: Qdrant Semantic Search
1. Create collections
2. Create payload indexes
3. Test embedding storage

### Phase 4: Redis Cache Layer
1. Test key patterns
2. Validate TTL configurations
3. Test cache invalidation

### Phase 5: Graphiti Temporal Tracking
1. Register entity types
2. Configure temporal properties
3. Test state change logging

---

## Deployment Checklist

- [ ] PostgreSQL database created with all extensions
- [ ] All 6 schemas created (hub1-hub6)
- [ ] All 45 tables created with proper constraints
- [ ] All indexes created and optimized
- [ ] Neo4j constraints created (0 duplicates allowed)
- [ ] Neo4j indexes created for performance
- [ ] Qdrant collections created with vector configs
- [ ] Qdrant payload indexes created
- [ ] Redis key patterns documented
- [ ] Redis TTL configurations validated
- [ ] Graphiti entity types registered
- [ ] Graphiti temporal properties configured
- [ ] Cross-database sync patterns tested
- [ ] Sample data loaded for testing
- [ ] Validation queries passing (see 6-HUB-SCHEMA-VALIDATION-QUERIES.md)
- [ ] Backup and recovery procedures documented
- [ ] Monitoring and alerting configured

---

**Implementation Schemas Complete:** November 4, 2025
**Schema Version:** v2.0 (Production-Ready)
**Next:** Validation Query Suite + Data Migration Guide
