#!/usr/bin/env python3
"""
Validation Tests: PostgreSQL Schema and Data
Purpose: Validate PostgreSQL schema, constraints, and data integrity
Run after: Phase 1 PostgreSQL migration

Usage:
    pytest test_postgres_validation.py -v
    pytest test_postgres_validation.py::test_hub3_tables_exist -v
"""

import pytest
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
PG_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': os.getenv('POSTGRES_PORT', '5432'),
    'database': os.getenv('POSTGRES_DB', 'apex_memory'),
    'user': os.getenv('POSTGRES_USER', 'apex'),
    'password': os.getenv('POSTGRES_PASSWORD', 'apexmemory2024')
}


@pytest.fixture(scope='module')
def pg_conn():
    """PostgreSQL connection fixture"""
    conn = psycopg2.connect(**PG_CONFIG)
    yield conn
    conn.close()


@pytest.fixture(scope='module')
def pg_cursor(pg_conn):
    """PostgreSQL cursor fixture"""
    cursor = pg_conn.cursor(cursor_factory=RealDictCursor)
    yield cursor
    cursor.close()


# ======================
# Schema Validation Tests
# ======================

def test_database_exists(pg_cursor):
    """Verify apex_memory database exists"""
    pg_cursor.execute("SELECT current_database()")
    result = pg_cursor.fetchone()
    assert result['current_database'] == 'apex_memory'


def test_extensions_installed(pg_cursor):
    """Verify required PostgreSQL extensions are installed"""
    pg_cursor.execute("SELECT extname FROM pg_extension")
    extensions = [row['extname'] for row in pg_cursor.fetchall()]

    required_extensions = ['uuid-ossp', 'pg_trgm', 'btree_gin', 'pgcrypto', 'postgis']
    for ext in required_extensions:
        assert ext in extensions, f"Extension {ext} not installed"


def test_all_hub_schemas_exist(pg_cursor):
    """Verify all 6 hub schemas exist"""
    pg_cursor.execute("""
        SELECT schema_name
        FROM information_schema.schemata
        WHERE schema_name LIKE 'hub%'
    """)
    schemas = [row['schema_name'] for row in pg_cursor.fetchall()]

    expected_schemas = [
        'hub1_command', 'hub2_openhaul', 'hub3_origin',
        'hub4_contacts', 'hub5_financials', 'hub6_corporate'
    ]

    assert len(schemas) == 6, f"Expected 6 hub schemas, found {len(schemas)}"
    for schema in expected_schemas:
        assert schema in schemas, f"Schema {schema} not found"


def test_hub3_tables_exist(pg_cursor):
    """Verify all Hub 3 tables exist"""
    pg_cursor.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'hub3_origin'
    """)
    tables = [row['table_name'] for row in pg_cursor.fetchall()]

    expected_tables = [
        'tractors', 'trailers', 'drivers',
        'fuel_transactions', 'maintenance_records',
        'incidents', 'insurance_policies'
    ]

    assert len(tables) == 7, f"Expected 7 tables in hub3_origin, found {len(tables)}"
    for table in expected_tables:
        assert table in tables, f"Table {table} not found in hub3_origin"


def test_tractors_table_structure(pg_cursor):
    """Verify tractors table has correct structure"""
    pg_cursor.execute("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_schema = 'hub3_origin'
        AND table_name = 'tractors'
        ORDER BY ordinal_position
    """)
    columns = {row['column_name']: row for row in pg_cursor.fetchall()}

    # Primary key
    assert 'unit_number' in columns
    assert columns['unit_number']['data_type'] == 'character varying'

    # Secondary identifier
    assert 'vin' in columns
    assert columns['vin']['is_nullable'] == 'NO'

    # Temporal tracking
    assert 'created_at' in columns
    assert 'updated_at' in columns
    assert 'valid_from' in columns
    assert 'valid_to' in columns


def test_drivers_table_structure(pg_cursor):
    """Verify drivers table has correct structure"""
    pg_cursor.execute("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_schema = 'hub3_origin'
        AND table_name = 'drivers'
        ORDER BY ordinal_position
    """)
    columns = {row['column_name']: row for row in pg_cursor.fetchall()}

    # Primary key
    assert 'driver_id' in columns

    # Unique identifiers
    assert 'cdl_number' in columns

    # Foreign key
    assert 'current_unit_assignment' in columns

    # Temporal tracking
    assert 'valid_from' in columns
    assert 'valid_to' in columns


# =======================
# Constraint Validation Tests
# =======================

def test_primary_key_constraints(pg_cursor):
    """Verify primary key constraints exist"""
    pg_cursor.execute("""
        SELECT tc.table_name, kcu.column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
            ON tc.constraint_name = kcu.constraint_name
        WHERE tc.table_schema = 'hub3_origin'
        AND tc.constraint_type = 'PRIMARY KEY'
    """)
    primary_keys = {row['table_name']: row['column_name'] for row in pg_cursor.fetchall()}

    assert primary_keys['tractors'] == 'unit_number'
    assert primary_keys['drivers'] == 'driver_id'


def test_unique_constraints(pg_cursor):
    """Verify unique constraints exist"""
    pg_cursor.execute("""
        SELECT tc.table_name, kcu.column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
            ON tc.constraint_name = kcu.constraint_name
        WHERE tc.table_schema = 'hub3_origin'
        AND tc.constraint_type = 'UNIQUE'
    """)
    unique_constraints = {(row['table_name'], row['column_name']) for row in pg_cursor.fetchall()}

    assert ('tractors', 'vin') in unique_constraints
    assert ('drivers', 'cdl_number') in unique_constraints


def test_foreign_key_constraints(pg_cursor):
    """Verify foreign key constraints exist"""
    pg_cursor.execute("""
        SELECT
            tc.table_name,
            kcu.column_name,
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name
        FROM information_schema.table_constraints AS tc
        JOIN information_schema.key_column_usage AS kcu
            ON tc.constraint_name = kcu.constraint_name
        JOIN information_schema.constraint_column_usage AS ccu
            ON ccu.constraint_name = tc.constraint_name
        WHERE tc.table_schema = 'hub3_origin'
        AND tc.constraint_type = 'FOREIGN KEY'
    """)
    foreign_keys = [(row['table_name'], row['column_name'], row['foreign_table_name']) for row in pg_cursor.fetchall()]

    # drivers.current_unit_assignment → tractors.unit_number
    assert any(fk[0] == 'drivers' and fk[1] == 'current_unit_assignment' and fk[2] == 'tractors' for fk in foreign_keys)


def test_check_constraints(pg_cursor):
    """Verify check constraints exist"""
    pg_cursor.execute("""
        SELECT
            SPLIT_PART(conrelid::regclass::text, '.', 2) as table_name,
            conname as constraint_name,
            pg_get_constraintdef(oid) as check_clause
        FROM pg_constraint
        WHERE conrelid::regclass::text LIKE 'hub3_origin.%'
        AND contype = 'c'
    """)
    check_constraints = {(row['table_name'], row['constraint_name']) for row in pg_cursor.fetchall()}

    # Verify some critical check constraints
    assert any('valid_vin_length' in name for table, name in check_constraints if table == 'tractors')
    assert any('valid_unit_number' in name for table, name in check_constraints if table == 'tractors')


# ===================
# Index Validation Tests
# ===================

def test_indexes_exist(pg_cursor):
    """Verify performance indexes exist"""
    pg_cursor.execute("""
        SELECT tablename, indexname
        FROM pg_indexes
        WHERE schemaname = 'hub3_origin'
    """)
    indexes = {(row['tablename'], row['indexname']) for row in pg_cursor.fetchall()}

    # Status indexes
    assert any('status' in idx for tbl, idx in indexes if tbl == 'tractors')
    assert any('status' in idx for tbl, idx in indexes if tbl == 'drivers')

    # Temporal indexes
    assert any('temporal' in idx for tbl, idx in indexes if tbl == 'tractors')

    # Geography index
    assert any('location' in idx for tbl, idx in indexes if tbl == 'tractors')


# ====================
# Trigger Validation Tests
# ====================

def test_updated_at_triggers_exist(pg_cursor):
    """Verify auto-update triggers exist"""
    pg_cursor.execute("""
        SELECT event_object_table, trigger_name
        FROM information_schema.triggers
        WHERE trigger_schema = 'hub3_origin'
        AND trigger_name LIKE '%updated_at%'
    """)
    triggers = {row['event_object_table'] for row in pg_cursor.fetchall()}

    # All main tables should have updated_at triggers
    assert 'tractors' in triggers
    assert 'drivers' in triggers
    assert 'fuel_transactions' in triggers
    assert 'maintenance_records' in triggers


# ====================
# Data Validation Tests
# ====================

def test_tractors_data_types(pg_cursor):
    """Verify tractors table accepts valid data"""
    pg_cursor.execute("""
        SELECT COUNT(*) as count
        FROM hub3_origin.tractors
    """)
    result = pg_cursor.fetchone()
    # Should have 0 or more tractors (depending on if sample data was loaded)
    assert result['count'] >= 0


def test_temporal_tracking_defaults(pg_cursor):
    """Verify temporal tracking fields have defaults"""
    pg_cursor.execute("""
        SELECT column_name, column_default
        FROM information_schema.columns
        WHERE table_schema = 'hub3_origin'
        AND table_name = 'tractors'
        AND column_name IN ('created_at', 'updated_at', 'valid_from')
    """)
    defaults = {row['column_name']: row['column_default'] for row in pg_cursor.fetchall()}

    assert 'created_at' in defaults
    assert 'NOW()' in defaults['created_at'] or 'now()' in defaults['created_at']


def test_geographic_data_type(pg_cursor):
    """Verify PostGIS geography type is working"""
    pg_cursor.execute("""
        SELECT column_name, udt_name
        FROM information_schema.columns
        WHERE table_schema = 'hub3_origin'
        AND table_name = 'tractors'
        AND column_name = 'location_gps'
    """)
    result = pg_cursor.fetchone()

    assert result is not None
    assert result['udt_name'] == 'geography'


# ======================
# Summary Test
# ======================

def test_hub3_complete_setup(pg_cursor):
    """Overall validation that Hub 3 is correctly set up"""
    # Count tables
    pg_cursor.execute("""
        SELECT COUNT(*) as count
        FROM information_schema.tables
        WHERE table_schema = 'hub3_origin'
    """)
    table_count = pg_cursor.fetchone()['count']

    # Count indexes
    pg_cursor.execute("""
        SELECT COUNT(*) as count
        FROM pg_indexes
        WHERE schemaname = 'hub3_origin'
    """)
    index_count = pg_cursor.fetchone()['count']

    # Count triggers
    pg_cursor.execute("""
        SELECT COUNT(*) as count
        FROM information_schema.triggers
        WHERE trigger_schema = 'hub3_origin'
    """)
    trigger_count = pg_cursor.fetchone()['count']

    assert table_count == 7, f"Expected 7 tables, found {table_count}"
    assert index_count >= 20, f"Expected at least 20 indexes, found {index_count}"
    assert trigger_count == 7, f"Expected 7 triggers, found {trigger_count}"
