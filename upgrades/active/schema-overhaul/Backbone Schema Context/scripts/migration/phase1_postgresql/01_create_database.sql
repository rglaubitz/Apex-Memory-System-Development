-- Phase 1: PostgreSQL Foundation - Step 1: Create Database
-- Purpose: Create apex_memory database with required extensions
-- Run as: postgres superuser
-- Idempotent: Yes (will not error if database exists)

-- Create database
CREATE DATABASE apex_memory
    WITH OWNER = apex
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8'
    TEMPLATE = template0;

-- Connect to new database
\c apex_memory

-- Install required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";      -- UUID generation
CREATE EXTENSION IF NOT EXISTS "pg_trgm";        -- Trigram search (fuzzy matching)
CREATE EXTENSION IF NOT EXISTS "btree_gin";      -- GIN indexes on scalars
CREATE EXTENSION IF NOT EXISTS "pgcrypto";       -- Encryption (for Hub 1 Assets)
CREATE EXTENSION IF NOT EXISTS "postgis";        -- Geography (for truck locations)

-- Verify extensions
SELECT extname, extversion FROM pg_extension
WHERE extname IN ('uuid-ossp', 'pg_trgm', 'btree_gin', 'pgcrypto', 'postgis')
ORDER BY extname;

-- Expected output: 5 rows
-- uuid-ossp, pg_trgm, btree_gin, pgcrypto, postgis

-- Success message
DO $$
BEGIN
    RAISE NOTICE '✅ Database apex_memory created successfully';
    RAISE NOTICE '✅ All 5 required extensions installed';
END $$;
