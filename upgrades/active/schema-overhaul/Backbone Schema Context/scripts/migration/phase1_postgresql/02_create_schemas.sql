-- Phase 1: PostgreSQL Foundation - Step 2: Create Hub Schemas
-- Purpose: Create all 6 hub schemas with proper permissions
-- Run as: apex user
-- Idempotent: Yes

\c apex_memory

-- Create all 6 hub schemas
CREATE SCHEMA IF NOT EXISTS hub1_command;
CREATE SCHEMA IF NOT EXISTS hub2_openhaul;
CREATE SCHEMA IF NOT EXISTS hub3_origin;
CREATE SCHEMA IF NOT EXISTS hub4_contacts;
CREATE SCHEMA IF NOT EXISTS hub5_financials;
CREATE SCHEMA IF NOT EXISTS hub6_corporate;

-- Grant permissions to apex user
GRANT USAGE ON SCHEMA hub1_command TO apex;
GRANT USAGE ON SCHEMA hub2_openhaul TO apex;
GRANT USAGE ON SCHEMA hub3_origin TO apex;
GRANT USAGE ON SCHEMA hub4_contacts TO apex;
GRANT USAGE ON SCHEMA hub5_financials TO apex;
GRANT USAGE ON SCHEMA hub6_corporate TO apex;

-- Grant all privileges on all tables in schemas (for future tables)
ALTER DEFAULT PRIVILEGES IN SCHEMA hub1_command GRANT ALL ON TABLES TO apex;
ALTER DEFAULT PRIVILEGES IN SCHEMA hub2_openhaul GRANT ALL ON TABLES TO apex;
ALTER DEFAULT PRIVILEGES IN SCHEMA hub3_origin GRANT ALL ON TABLES TO apex;
ALTER DEFAULT PRIVILEGES IN SCHEMA hub4_contacts GRANT ALL ON TABLES TO apex;
ALTER DEFAULT PRIVILEGES IN SCHEMA hub5_financials GRANT ALL ON TABLES TO apex;
ALTER DEFAULT PRIVILEGES IN SCHEMA hub6_corporate GRANT ALL ON TABLES TO apex;

-- Grant sequence privileges
ALTER DEFAULT PRIVILEGES IN SCHEMA hub1_command GRANT ALL ON SEQUENCES TO apex;
ALTER DEFAULT PRIVILEGES IN SCHEMA hub2_openhaul GRANT ALL ON SEQUENCES TO apex;
ALTER DEFAULT PRIVILEGES IN SCHEMA hub3_origin GRANT ALL ON SEQUENCES TO apex;
ALTER DEFAULT PRIVILEGES IN SCHEMA hub4_contacts GRANT ALL ON SEQUENCES TO apex;
ALTER DEFAULT PRIVILEGES IN SCHEMA hub5_financials GRANT ALL ON SEQUENCES TO apex;
ALTER DEFAULT PRIVILEGES IN SCHEMA hub6_corporate GRANT ALL ON SEQUENCES TO apex;

-- Verify schemas
SELECT schema_name FROM information_schema.schemata
WHERE schema_name LIKE 'hub%'
ORDER BY schema_name;

-- Expected output: 6 rows
-- hub1_command
-- hub2_openhaul
-- hub3_origin
-- hub4_contacts
-- hub5_financials
-- hub6_corporate

-- Success message
DO $$
BEGIN
    RAISE NOTICE '✅ All 6 hub schemas created successfully';
    RAISE NOTICE '✅ Permissions granted to apex user';
END $$;
