#!/usr/bin/env python3
"""
Validation Tests: Cross-Database Synchronization
Purpose: Validate synchronization between PostgreSQL (PRIMARY) and Neo4j (REPLICA)
Run after: Phase 1 and Phase 2 migrations

Usage:
    pytest test_cross_db_sync.py -v
"""

import pytest
import psycopg2
from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configurations
PG_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': os.getenv('POSTGRES_PORT', '5432'),
    'database': os.getenv('POSTGRES_DB', 'apex_memory'),
    'user': os.getenv('POSTGRES_USER', 'apex'),
    'password': os.getenv('POSTGRES_PASSWORD', 'apexmemory2024')
}

NEO4J_CONFIG = {
    'uri': os.getenv('NEO4J_URI', 'bolt://localhost:7687'),
    'user': os.getenv('NEO4J_USER', 'neo4j'),
    'password': os.getenv('NEO4J_PASSWORD', 'apexmemory2024')
}


@pytest.fixture(scope='module')
def pg_conn():
    """PostgreSQL connection fixture"""
    conn = psycopg2.connect(**PG_CONFIG)
    yield conn
    conn.close()


@pytest.fixture(scope='module')
def neo4j_driver():
    """Neo4j driver fixture"""
    driver = GraphDatabase.driver(
        NEO4J_CONFIG['uri'],
        auth=(NEO4J_CONFIG['user'], NEO4J_CONFIG['password'])
    )
    yield driver
    driver.close()


# ==========================
# Entity Count Sync Tests
# ==========================

def test_tractor_count_sync(pg_conn, neo4j_driver):
    """Verify tractor count matches between PostgreSQL and Neo4j"""
    # PostgreSQL count (only current records)
    with pg_conn.cursor() as pg_cur:
        pg_cur.execute("""
            SELECT COUNT(*) FROM hub3_origin.tractors
            WHERE valid_to IS NULL
        """)
        pg_count = pg_cur.fetchone()[0]

    # Neo4j count
    with neo4j_driver.session() as neo4j_session:
        result = neo4j_session.run("MATCH (t:Tractor) RETURN count(t) as count")
        neo4j_count = result.single()['count']

    assert pg_count == neo4j_count, f"Tractor count mismatch: PostgreSQL={pg_count}, Neo4j={neo4j_count}"


def test_driver_count_sync(pg_conn, neo4j_driver):
    """Verify driver count matches between PostgreSQL and Neo4j"""
    # PostgreSQL count (only current records)
    with pg_conn.cursor() as pg_cur:
        pg_cur.execute("""
            SELECT COUNT(*) FROM hub3_origin.drivers
            WHERE valid_to IS NULL
        """)
        pg_count = pg_cur.fetchone()[0]

    # Neo4j count
    with neo4j_driver.session() as neo4j_session:
        result = neo4j_session.run("MATCH (d:Driver) RETURN count(d) as count")
        neo4j_count = result.single()['count']

    assert pg_count == neo4j_count, f"Driver count mismatch: PostgreSQL={pg_count}, Neo4j={neo4j_count}"


# ============================
# Entity Property Sync Tests
# ============================

def test_tractor_properties_sync(pg_conn, neo4j_driver):
    """Verify tractor properties match between databases"""
    # Get sample tractor from PostgreSQL
    with pg_conn.cursor() as pg_cur:
        pg_cur.execute("""
            SELECT unit_number, vin, make, model, status
            FROM hub3_origin.tractors
            WHERE valid_to IS NULL
            LIMIT 1
        """)
        pg_tractor = pg_cur.fetchone()

    if pg_tractor is None:
        pytest.skip("No tractors in PostgreSQL yet")

    unit_number = pg_tractor[0]

    # Get same tractor from Neo4j
    with neo4j_driver.session() as neo4j_session:
        result = neo4j_session.run("""
            MATCH (t:Tractor {unit_number: $unit_number})
            RETURN t.unit_number as unit_number, t.vin as vin,
                   t.make as make, t.model as model, t.status as status
        """, unit_number=unit_number)

        neo4j_tractor = result.single()

    assert neo4j_tractor is not None, f"Tractor {unit_number} not found in Neo4j"

    # Compare properties
    assert neo4j_tractor['unit_number'] == pg_tractor[0]
    if pg_tractor[1]:  # vin
        assert neo4j_tractor['vin'] == pg_tractor[1]
    if pg_tractor[2]:  # make
        assert neo4j_tractor['make'] == pg_tractor[2]
    if pg_tractor[3]:  # model
        assert neo4j_tractor['model'] == pg_tractor[3]
    if pg_tractor[4]:  # status
        assert neo4j_tractor['status'] == pg_tractor[4]


def test_driver_properties_sync(pg_conn, neo4j_driver):
    """Verify driver properties match between databases"""
    # Get sample driver from PostgreSQL
    with pg_conn.cursor() as pg_cur:
        pg_cur.execute("""
            SELECT driver_id, name, cdl_number, status
            FROM hub3_origin.drivers
            WHERE valid_to IS NULL
            LIMIT 1
        """)
        pg_driver = pg_cur.fetchone()

    if pg_driver is None:
        pytest.skip("No drivers in PostgreSQL yet")

    driver_id = pg_driver[0]

    # Get same driver from Neo4j
    with neo4j_driver.session() as neo4j_session:
        result = neo4j_session.run("""
            MATCH (d:Driver {driver_id: $driver_id})
            RETURN d.driver_id as driver_id, d.name as name,
                   d.cdl_number as cdl_number, d.status as status
        """, driver_id=driver_id)

        neo4j_driver_data = result.single()

    assert neo4j_driver_data is not None, f"Driver {driver_id} not found in Neo4j"

    # Compare properties
    assert neo4j_driver_data['driver_id'] == pg_driver[0]
    if pg_driver[1]:  # name
        assert neo4j_driver_data['name'] == pg_driver[1]
    if pg_driver[2]:  # cdl_number
        assert neo4j_driver_data['cdl_number'] == pg_driver[2]
    if pg_driver[3]:  # status
        assert neo4j_driver_data['status'] == pg_driver[3]


# ================================
# Relationship Sync Tests
# ================================

def test_driver_assignment_sync(pg_conn, neo4j_driver):
    """Verify driver assignments match between databases"""
    # Get driver assignments from PostgreSQL
    with pg_conn.cursor() as pg_cur:
        pg_cur.execute("""
            SELECT driver_id, current_unit_assignment
            FROM hub3_origin.drivers
            WHERE valid_to IS NULL
            AND current_unit_assignment IS NOT NULL
        """)
        pg_assignments = {row[0]: row[1] for row in pg_cur.fetchall()}

    # Get driver assignments from Neo4j
    with neo4j_driver.session() as neo4j_session:
        result = neo4j_session.run("""
            MATCH (d:Driver)-[:ASSIGNED_TO]->(t:Tractor)
            RETURN d.driver_id as driver_id, t.unit_number as unit_number
        """)
        neo4j_assignments = {record['driver_id']: record['unit_number'] for record in result}

    # Compare counts
    assert len(pg_assignments) == len(neo4j_assignments), \
        f"Assignment count mismatch: PostgreSQL={len(pg_assignments)}, Neo4j={len(neo4j_assignments)}"

    # Compare individual assignments
    for driver_id, unit_number in pg_assignments.items():
        assert driver_id in neo4j_assignments, f"Driver {driver_id} assignment not found in Neo4j"
        assert neo4j_assignments[driver_id] == unit_number, \
            f"Assignment mismatch for driver {driver_id}: PostgreSQL={unit_number}, Neo4j={neo4j_assignments[driver_id]}"


# ============================
# Temporal Consistency Tests
# ============================

def test_temporal_tracking_sync(pg_conn, neo4j_driver):
    """Verify temporal properties are synchronized"""
    # Get sample tractor with temporal data from PostgreSQL
    with pg_conn.cursor() as pg_cur:
        pg_cur.execute("""
            SELECT unit_number, valid_from, valid_to
            FROM hub3_origin.tractors
            WHERE valid_to IS NULL
            LIMIT 1
        """)
        pg_tractor = pg_cur.fetchone()

    if pg_tractor is None:
        pytest.skip("No tractors in PostgreSQL yet")

    unit_number = pg_tractor[0]

    # Get same tractor from Neo4j
    with neo4j_driver.session() as neo4j_session:
        result = neo4j_session.run("""
            MATCH (t:Tractor {unit_number: $unit_number})
            RETURN t.valid_from as valid_from, t.valid_to as valid_to
        """, unit_number=unit_number)

        neo4j_tractor = result.single()

    assert neo4j_tractor is not None

    # valid_to should be NULL/None in both databases for current records
    assert neo4j_tractor['valid_to'] is None


# ======================
# Summary Test
# ======================

def test_cross_db_sync_summary(pg_conn, neo4j_driver):
    """Overall cross-database synchronization validation"""
    mismatches = []

    # Check tractors
    with pg_conn.cursor() as pg_cur:
        pg_cur.execute("SELECT COUNT(*) FROM hub3_origin.tractors WHERE valid_to IS NULL")
        pg_tractor_count = pg_cur.fetchone()[0]

    with neo4j_driver.session() as neo4j_session:
        result = neo4j_session.run("MATCH (t:Tractor) RETURN count(t) as count")
        neo4j_tractor_count = result.single()['count']

    if pg_tractor_count != neo4j_tractor_count:
        mismatches.append(f"Tractors: PG={pg_tractor_count}, Neo4j={neo4j_tractor_count}")

    # Check drivers
    with pg_conn.cursor() as pg_cur:
        pg_cur.execute("SELECT COUNT(*) FROM hub3_origin.drivers WHERE valid_to IS NULL")
        pg_driver_count = pg_cur.fetchone()[0]

    with neo4j_driver.session() as neo4j_session:
        result = neo4j_session.run("MATCH (d:Driver) RETURN count(d) as count")
        neo4j_driver_count = result.single()['count']

    if pg_driver_count != neo4j_driver_count:
        mismatches.append(f"Drivers: PG={pg_driver_count}, Neo4j={neo4j_driver_count}")

    # Report any mismatches
    if mismatches:
        pytest.fail(f"Cross-database sync mismatches:\n" + "\n".join(mismatches))
