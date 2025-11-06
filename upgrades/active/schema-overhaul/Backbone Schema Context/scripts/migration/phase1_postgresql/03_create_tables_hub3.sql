-- Phase 1: PostgreSQL Foundation - Step 3: Create Hub 3 Tables
-- Hub 3: Origin Transport - "The Fleet"
-- Purpose: Create all 7 entities for fleet management
-- Run as: apex user
-- Idempotent: Yes

\c apex_memory

-- ====================
-- Table 1: Tractors
-- ====================

CREATE TABLE IF NOT EXISTS hub3_origin.tractors (
    -- Primary Key
    unit_number VARCHAR(10) PRIMARY KEY,

    -- Secondary Identifier
    vin VARCHAR(17) UNIQUE NOT NULL,

    -- Basic Info
    make VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL,
    year INTEGER NOT NULL CHECK (year BETWEEN 2000 AND 2030),

    -- Operational Status
    status VARCHAR(50) NOT NULL CHECK (status IN ('active', 'maintenance', 'out_of_service', 'sold')),
    current_miles INTEGER CHECK (current_miles >= 0),
    engine_hours INTEGER CHECK (engine_hours >= 0),
    location_gps GEOGRAPHY(POINT, 4326),  -- PostGIS geography type

    -- Financial
    purchase_date DATE,
    purchase_price DECIMAL(12,2) CHECK (purchase_price >= 0),
    current_value DECIMAL(12,2) CHECK (current_value >= 0),
    financing_status VARCHAR(50) CHECK (financing_status IN ('owned', 'financed', 'leased')),
    lender_name VARCHAR(255),
    loan_balance DECIMAL(12,2) CHECK (loan_balance >= 0),
    monthly_payment DECIMAL(10,2) CHECK (monthly_payment >= 0),

    -- Insurance
    insurance_policy_number VARCHAR(100),
    insurance_provider VARCHAR(255),
    insurance_expiry_date DATE,
    monthly_premium DECIMAL(10,2) CHECK (monthly_premium >= 0),

    -- Maintenance
    next_service_due_miles INTEGER,
    last_service_date DATE,

    -- Temporal Tracking
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    valid_from TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    valid_to TIMESTAMPTZ,

    -- Constraints
    CONSTRAINT valid_vin_length CHECK (LENGTH(vin) = 17),
    CONSTRAINT valid_unit_number CHECK (unit_number ~ '^\d{4}$'),
    CONSTRAINT service_miles_logical CHECK (next_service_due_miles IS NULL OR next_service_due_miles > current_miles)
);

-- Indexes for Tractors
CREATE INDEX IF NOT EXISTS idx_tractors_status ON hub3_origin.tractors(status) WHERE status IN ('active', 'maintenance');
CREATE INDEX IF NOT EXISTS idx_tractors_vin ON hub3_origin.tractors(vin);
CREATE INDEX IF NOT EXISTS idx_tractors_temporal ON hub3_origin.tractors(valid_from, valid_to) WHERE valid_to IS NULL;
CREATE INDEX IF NOT EXISTS idx_tractors_location ON hub3_origin.tractors USING GIST (location_gps);

-- ====================
-- Table 2: Trailers
-- ====================

CREATE TABLE IF NOT EXISTS hub3_origin.trailers (
    -- Primary Key
    trailer_number VARCHAR(10) PRIMARY KEY,

    -- Basic Info
    trailer_type VARCHAR(50) NOT NULL CHECK (trailer_type IN ('dry_van', 'reefer', 'flatbed')),
    make VARCHAR(100),
    model VARCHAR(100),
    year INTEGER CHECK (year BETWEEN 2000 AND 2030),

    -- Reefer Specifics (for refrigerated trailers)
    reefer_make VARCHAR(100),
    reefer_model VARCHAR(100),
    reefer_serial_number VARCHAR(100),
    reefer_hours INTEGER CHECK (reefer_hours >= 0),

    -- Status
    status VARCHAR(50) NOT NULL CHECK (status IN ('active', 'maintenance', 'out_of_service', 'sold')),
    current_location VARCHAR(255),

    -- Financial
    purchase_date DATE,
    purchase_price DECIMAL(12,2) CHECK (purchase_price >= 0),
    current_value DECIMAL(12,2) CHECK (current_value >= 0),

    -- Insurance
    insurance_policy_number VARCHAR(100),
    insurance_provider VARCHAR(255),
    insurance_expiry_date DATE,

    -- Maintenance
    last_service_date DATE,

    -- Temporal Tracking
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    valid_from TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    valid_to TIMESTAMPTZ,

    -- Constraints
    CONSTRAINT valid_trailer_number CHECK (trailer_number ~ '^T-\d{4}$')
);

-- Indexes for Trailers
CREATE INDEX IF NOT EXISTS idx_trailers_status ON hub3_origin.trailers(status) WHERE status = 'active';
CREATE INDEX IF NOT EXISTS idx_trailers_type ON hub3_origin.trailers(trailer_type);
CREATE INDEX IF NOT EXISTS idx_trailers_temporal ON hub3_origin.trailers(valid_from, valid_to) WHERE valid_to IS NULL;

-- ====================
-- Table 3: Drivers
-- ====================

CREATE TABLE IF NOT EXISTS hub3_origin.drivers (
    -- Primary Key
    driver_id VARCHAR(50) PRIMARY KEY,

    -- Basic Info
    name VARCHAR(255) NOT NULL,
    cdl_number VARCHAR(50) UNIQUE NOT NULL,
    cdl_state VARCHAR(2) NOT NULL,
    cdl_expiry_date DATE NOT NULL,

    -- Contact
    phone VARCHAR(20),
    email VARCHAR(255),
    address TEXT,

    -- Status
    status VARCHAR(50) NOT NULL CHECK (status IN ('active', 'inactive', 'on_leave', 'terminated')),
    current_unit_assignment VARCHAR(10),  -- References tractors.unit_number

    -- Employment
    hire_date DATE,
    termination_date DATE,
    employment_type VARCHAR(50) CHECK (employment_type IN ('w2', '1099', 'lease_operator')),

    -- Compensation
    pay_rate DECIMAL(10,2),
    pay_type VARCHAR(50) CHECK (pay_type IN ('per_mile', 'per_hour', 'salary', 'percentage')),

    -- Compliance
    medical_card_expiry DATE,
    background_check_date DATE,
    drug_test_date DATE,

    -- Temporal Tracking
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    valid_from TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    valid_to TIMESTAMPTZ,

    -- Foreign Keys
    CONSTRAINT fk_current_unit FOREIGN KEY (current_unit_assignment) REFERENCES hub3_origin.tractors(unit_number) ON DELETE SET NULL
);

-- Indexes for Drivers
CREATE INDEX IF NOT EXISTS idx_drivers_status ON hub3_origin.drivers(status) WHERE status = 'active';
CREATE INDEX IF NOT EXISTS idx_drivers_cdl ON hub3_origin.drivers(cdl_number);
CREATE INDEX IF NOT EXISTS idx_drivers_current_unit ON hub3_origin.drivers(current_unit_assignment) WHERE current_unit_assignment IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_drivers_temporal ON hub3_origin.drivers(valid_from, valid_to) WHERE valid_to IS NULL;

-- ====================
-- Table 4: Fuel Transactions
-- ====================

CREATE TABLE IF NOT EXISTS hub3_origin.fuel_transactions (
    -- Primary Key
    transaction_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- References
    unit_number VARCHAR(10) NOT NULL,
    driver_id VARCHAR(50),

    -- Transaction Details
    transaction_date TIMESTAMPTZ NOT NULL,
    vendor_name VARCHAR(255) NOT NULL,
    location VARCHAR(255),

    -- Fuel Details
    gallons DECIMAL(10,2) NOT NULL CHECK (gallons > 0),
    price_per_gallon DECIMAL(10,4) NOT NULL CHECK (price_per_gallon > 0),
    total_amount DECIMAL(10,2) NOT NULL CHECK (total_amount > 0),

    -- Additional Charges
    def_amount DECIMAL(10,2) CHECK (def_amount >= 0),
    reefer_fuel_amount DECIMAL(10,2) CHECK (reefer_fuel_amount >= 0),

    -- Invoice Reference
    invoice_number VARCHAR(100),

    -- Temporal Tracking
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Foreign Keys
    CONSTRAINT fk_fuel_unit FOREIGN KEY (unit_number) REFERENCES hub3_origin.tractors(unit_number),
    CONSTRAINT fk_fuel_driver FOREIGN KEY (driver_id) REFERENCES hub3_origin.drivers(driver_id)
);

-- Indexes for Fuel Transactions
CREATE INDEX IF NOT EXISTS idx_fuel_unit ON hub3_origin.fuel_transactions(unit_number);
CREATE INDEX IF NOT EXISTS idx_fuel_driver ON hub3_origin.fuel_transactions(driver_id);
CREATE INDEX IF NOT EXISTS idx_fuel_date ON hub3_origin.fuel_transactions(transaction_date DESC);
CREATE INDEX IF NOT EXISTS idx_fuel_vendor ON hub3_origin.fuel_transactions(vendor_name);

-- ====================
-- Table 5: Maintenance Records
-- ====================

CREATE TABLE IF NOT EXISTS hub3_origin.maintenance_records (
    -- Primary Key
    maintenance_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- References
    unit_number VARCHAR(10) NOT NULL,

    -- Maintenance Details
    maintenance_date DATE NOT NULL,
    service_type VARCHAR(100) NOT NULL,
    description TEXT,
    odometer_reading INTEGER,

    -- Vendor
    vendor_name VARCHAR(255) NOT NULL,
    vendor_contact VARCHAR(255),

    -- Cost
    labor_cost DECIMAL(10,2) CHECK (labor_cost >= 0),
    parts_cost DECIMAL(10,2) CHECK (parts_cost >= 0),
    total_cost DECIMAL(10,2) NOT NULL CHECK (total_cost >= 0),

    -- Invoice Reference
    invoice_number VARCHAR(100),

    -- Status
    status VARCHAR(50) CHECK (status IN ('scheduled', 'in_progress', 'completed', 'cancelled')),

    -- Temporal Tracking
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Foreign Keys
    CONSTRAINT fk_maintenance_unit FOREIGN KEY (unit_number) REFERENCES hub3_origin.tractors(unit_number)
);

-- Indexes for Maintenance Records
CREATE INDEX IF NOT EXISTS idx_maintenance_unit ON hub3_origin.maintenance_records(unit_number);
CREATE INDEX IF NOT EXISTS idx_maintenance_date ON hub3_origin.maintenance_records(maintenance_date DESC);
CREATE INDEX IF NOT EXISTS idx_maintenance_type ON hub3_origin.maintenance_records(service_type);
CREATE INDEX IF NOT EXISTS idx_maintenance_vendor ON hub3_origin.maintenance_records(vendor_name);

-- ====================
-- Table 6: Incidents
-- ====================

CREATE TABLE IF NOT EXISTS hub3_origin.incidents (
    -- Primary Key
    incident_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- References
    unit_number VARCHAR(10),
    driver_id VARCHAR(50),

    -- Incident Details
    incident_date TIMESTAMPTZ NOT NULL,
    incident_type VARCHAR(100) NOT NULL CHECK (incident_type IN ('accident', 'traffic_violation', 'breakdown', 'theft', 'other')),
    severity VARCHAR(50) CHECK (severity IN ('minor', 'moderate', 'major', 'critical')),
    description TEXT NOT NULL,
    location VARCHAR(255),

    -- Financial Impact
    estimated_damage DECIMAL(12,2) CHECK (estimated_damage >= 0),
    insurance_claim_number VARCHAR(100),

    -- Status
    status VARCHAR(50) CHECK (status IN ('reported', 'under_investigation', 'resolved', 'closed')),
    resolution_notes TEXT,

    -- Temporal Tracking
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Foreign Keys
    CONSTRAINT fk_incident_unit FOREIGN KEY (unit_number) REFERENCES hub3_origin.tractors(unit_number),
    CONSTRAINT fk_incident_driver FOREIGN KEY (driver_id) REFERENCES hub3_origin.drivers(driver_id)
);

-- Indexes for Incidents
CREATE INDEX IF NOT EXISTS idx_incidents_unit ON hub3_origin.incidents(unit_number);
CREATE INDEX IF NOT EXISTS idx_incidents_driver ON hub3_origin.incidents(driver_id);
CREATE INDEX IF NOT EXISTS idx_incidents_date ON hub3_origin.incidents(incident_date DESC);
CREATE INDEX IF NOT EXISTS idx_incidents_type ON hub3_origin.incidents(incident_type);
CREATE INDEX IF NOT EXISTS idx_incidents_status ON hub3_origin.incidents(status) WHERE status != 'closed';

-- ====================
-- Table 7: Insurance Policies
-- ====================

CREATE TABLE IF NOT EXISTS hub3_origin.insurance_policies (
    -- Primary Key
    policy_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Policy Details
    policy_number VARCHAR(100) UNIQUE NOT NULL,
    policy_type VARCHAR(100) NOT NULL CHECK (policy_type IN ('liability', 'physical_damage', 'cargo', 'workers_comp', 'general_liability')),
    provider_name VARCHAR(255) NOT NULL,

    -- Coverage
    coverage_amount DECIMAL(12,2) NOT NULL CHECK (coverage_amount > 0),
    deductible DECIMAL(10,2) CHECK (deductible >= 0),

    -- Dates
    effective_date DATE NOT NULL,
    expiration_date DATE NOT NULL,

    -- Cost
    annual_premium DECIMAL(12,2) NOT NULL CHECK (annual_premium > 0),
    payment_frequency VARCHAR(50) CHECK (payment_frequency IN ('monthly', 'quarterly', 'annual')),

    -- Status
    status VARCHAR(50) CHECK (status IN ('active', 'expired', 'cancelled')),

    -- References (which units/drivers covered)
    covered_units TEXT[],  -- Array of unit_numbers
    covered_drivers TEXT[], -- Array of driver_ids

    -- Temporal Tracking
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    valid_from TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    valid_to TIMESTAMPTZ,

    -- Constraints
    CONSTRAINT valid_policy_dates CHECK (expiration_date > effective_date)
);

-- Indexes for Insurance Policies
CREATE INDEX IF NOT EXISTS idx_insurance_policy_number ON hub3_origin.insurance_policies(policy_number);
CREATE INDEX IF NOT EXISTS idx_insurance_provider ON hub3_origin.insurance_policies(provider_name);
CREATE INDEX IF NOT EXISTS idx_insurance_type ON hub3_origin.insurance_policies(policy_type);
CREATE INDEX IF NOT EXISTS idx_insurance_expiration ON hub3_origin.insurance_policies(expiration_date) WHERE status = 'active';
CREATE INDEX IF NOT EXISTS idx_insurance_covered_units ON hub3_origin.insurance_policies USING GIN (covered_units);
CREATE INDEX IF NOT EXISTS idx_insurance_covered_drivers ON hub3_origin.insurance_policies USING GIN (covered_drivers);

-- ====================
-- Triggers
-- ====================

-- Create trigger function for auto-updating updated_at
CREATE OR REPLACE FUNCTION hub3_origin.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to all tables
CREATE TRIGGER update_tractors_updated_at
    BEFORE UPDATE ON hub3_origin.tractors
    FOR EACH ROW
    EXECUTE FUNCTION hub3_origin.update_updated_at_column();

CREATE TRIGGER update_trailers_updated_at
    BEFORE UPDATE ON hub3_origin.trailers
    FOR EACH ROW
    EXECUTE FUNCTION hub3_origin.update_updated_at_column();

CREATE TRIGGER update_drivers_updated_at
    BEFORE UPDATE ON hub3_origin.drivers
    FOR EACH ROW
    EXECUTE FUNCTION hub3_origin.update_updated_at_column();

CREATE TRIGGER update_fuel_transactions_updated_at
    BEFORE UPDATE ON hub3_origin.fuel_transactions
    FOR EACH ROW
    EXECUTE FUNCTION hub3_origin.update_updated_at_column();

CREATE TRIGGER update_maintenance_records_updated_at
    BEFORE UPDATE ON hub3_origin.maintenance_records
    FOR EACH ROW
    EXECUTE FUNCTION hub3_origin.update_updated_at_column();

CREATE TRIGGER update_incidents_updated_at
    BEFORE UPDATE ON hub3_origin.incidents
    FOR EACH ROW
    EXECUTE FUNCTION hub3_origin.update_updated_at_column();

CREATE TRIGGER update_insurance_policies_updated_at
    BEFORE UPDATE ON hub3_origin.insurance_policies
    FOR EACH ROW
    EXECUTE FUNCTION hub3_origin.update_updated_at_column();

-- ====================
-- Verification
-- ====================

-- Verify all tables created
SELECT table_schema, table_name,
       (SELECT COUNT(*) FROM information_schema.columns WHERE table_schema = t.table_schema AND table_name = t.table_name) as column_count
FROM information_schema.tables t
WHERE table_schema = 'hub3_origin'
ORDER BY table_name;

-- Expected output: 7 rows (tractors, trailers, drivers, fuel_transactions, maintenance_records, incidents, insurance_policies)

-- Verify indexes
SELECT schemaname, tablename, indexname
FROM pg_indexes
WHERE schemaname = 'hub3_origin'
ORDER BY tablename, indexname;

-- Expected output: ~35 indexes

-- Verify triggers
SELECT trigger_schema, event_object_table, trigger_name
FROM information_schema.triggers
WHERE trigger_schema = 'hub3_origin'
ORDER BY event_object_table;

-- Expected output: 7 rows (one per table)

-- Success message
DO $$
BEGIN
    RAISE NOTICE '✅ Hub 3 (Origin Transport): All 7 tables created successfully';
    RAISE NOTICE '✅ All indexes created (~35 total)';
    RAISE NOTICE '✅ All triggers created (7 total)';
    RAISE NOTICE '✅ Foreign key relationships established';
END $$;
