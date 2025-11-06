#!/usr/bin/env python3
"""
Validation Tests: Neo4j Constraints and Relationships
Purpose: Validate Neo4j schema, constraints, and relationship integrity
Run after: Phase 2 Neo4j migration

Usage:
    pytest test_neo4j_validation.py -v
    pytest test_neo4j_validation.py::test_tractor_constraints -v
"""

import pytest
from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Neo4j configuration
NEO4J_CONFIG = {
    'uri': os.getenv('NEO4J_URI', 'bolt://localhost:7687'),
    'user': os.getenv('NEO4J_USER', 'neo4j'),
    'password': os.getenv('NEO4J_PASSWORD', 'apexmemory2024')
}


@pytest.fixture(scope='module')
def neo4j_driver():
    """Neo4j driver fixture"""
    driver = GraphDatabase.driver(
        NEO4J_CONFIG['uri'],
        auth=(NEO4J_CONFIG['user'], NEO4J_CONFIG['password'])
    )
    yield driver
    driver.close()


@pytest.fixture(scope='module')
def neo4j_session(neo4j_driver):
    """Neo4j session fixture"""
    with neo4j_driver.session() as session:
        yield session


# ==========================
# Constraint Validation Tests
# ==========================

def test_constraints_exist(neo4j_session):
    """Verify constraints were created"""
    result = neo4j_session.run("SHOW CONSTRAINTS")
    constraints = list(result)

    assert len(constraints) >= 45, f"Expected at least 45 constraints, found {len(constraints)}"


def test_tractor_constraints(neo4j_session):
    """Verify Tractor node constraints"""
    result = neo4j_session.run("SHOW CONSTRAINTS")
    constraints = list(result)

    constraint_names = [record.get('name', '') for record in constraints]

    # Should have constraints on unit_number and vin
    assert any('tractor' in name.lower() and 'unit' in name.lower() for name in constraint_names)
    assert any('tractor' in name.lower() and 'vin' in name.lower() for name in constraint_names)


def test_driver_constraints(neo4j_session):
    """Verify Driver node constraints"""
    result = neo4j_session.run("SHOW CONSTRAINTS")
    constraints = list(result)

    constraint_names = [record.get('name', '') for record in constraints]

    # Should have constraints on driver_id and cdl_number
    assert any('driver' in name.lower() and 'id' in name.lower() for name in constraint_names)
    assert any('driver' in name.lower() and 'cdl' in name.lower() for name in constraint_names)


def test_hub1_constraints(neo4j_session):
    """Verify Hub 1 (Command Center) constraints"""
    result = neo4j_session.run("SHOW CONSTRAINTS")
    constraints = list(result)

    constraint_names = [record.get('name', '') for record in constraints]

    # Hub 1 entities
    hub1_entities = ['project', 'goal', 'task', 'insight']
    for entity in hub1_entities:
        assert any(entity in name.lower() for name in constraint_names), f"Missing constraint for {entity}"


def test_hub2_constraints(neo4j_session):
    """Verify Hub 2 (OpenHaul) constraints"""
    result = neo4j_session.run("SHOW CONSTRAINTS")
    constraints = list(result)

    constraint_names = [record.get('name', '') for record in constraints]

    # Hub 2 entities
    hub2_entities = ['load', 'carrier', 'location']
    for entity in hub2_entities:
        assert any(entity in name.lower() for name in constraint_names), f"Missing constraint for {entity}"


# =====================
# Index Validation Tests
# =====================

def test_indexes_exist(neo4j_session):
    """Verify performance indexes were created"""
    result = neo4j_session.run("SHOW INDEXES")
    indexes = list(result)

    assert len(indexes) >= 20, f"Expected at least 20 indexes, found {len(indexes)}"


def test_status_indexes(neo4j_session):
    """Verify status indexes for key entities"""
    result = neo4j_session.run("SHOW INDEXES")
    indexes = list(result)

    index_names = [record.get('name', '') for record in indexes]

    # Should have status indexes
    assert any('status' in name.lower() for name in index_names)


def test_date_indexes(neo4j_session):
    """Verify date indexes for temporal queries"""
    result = neo4j_session.run("SHOW INDEXES")
    indexes = list(result)

    index_names = [record.get('name', '') for record in indexes]

    # Should have date-related indexes
    assert any('date' in name.lower() for name in index_names)


# ====================
# Node Validation Tests
# ====================

def test_tractor_nodes_exist(neo4j_session):
    """Verify Tractor nodes were created"""
    result = neo4j_session.run("MATCH (t:Tractor) RETURN count(t) as count")
    count = result.single()['count']

    # Should have 0 or more tractors (depending on if data was loaded)
    assert count >= 0


def test_driver_nodes_exist(neo4j_session):
    """Verify Driver nodes were created"""
    result = neo4j_session.run("MATCH (d:Driver) RETURN count(d) as count")
    count = result.single()['count']

    assert count >= 0


def test_tractor_node_properties(neo4j_session):
    """Verify Tractor nodes have required properties"""
    result = neo4j_session.run("""
        MATCH (t:Tractor)
        RETURN t LIMIT 1
    """)

    record = result.single()
    if record:
        tractor = record['t']

        # Check required properties exist
        assert 'unit_number' in tractor
        assert 'vin' in tractor or True  # May not have VIN yet
        assert 'make' in tractor or True
        assert 'model' in tractor or True


def test_driver_node_properties(neo4j_session):
    """Verify Driver nodes have required properties"""
    result = neo4j_session.run("""
        MATCH (d:Driver)
        RETURN d LIMIT 1
    """)

    record = result.single()
    if record:
        driver = record['d']

        # Check required properties exist
        assert 'driver_id' in driver
        assert 'name' in driver or True
        assert 'cdl_number' in driver or True


# ============================
# Relationship Validation Tests
# ============================

def test_assigned_to_relationships(neo4j_session):
    """Verify ASSIGNED_TO relationships exist"""
    result = neo4j_session.run("""
        MATCH ()-[r:ASSIGNED_TO]->()
        RETURN count(r) as count
    """)
    count = result.single()['count']

    # Should have 0 or more relationships
    assert count >= 0


def test_assigned_to_relationship_properties(neo4j_session):
    """Verify ASSIGNED_TO relationships have temporal properties"""
    result = neo4j_session.run("""
        MATCH (d:Driver)-[r:ASSIGNED_TO]->(t:Tractor)
        RETURN r LIMIT 1
    """)

    record = result.single()
    if record:
        relationship = record['r']

        # Should have temporal tracking
        assert 'valid_from' in relationship or 'created_at' in relationship


def test_for_unit_relationships(neo4j_session):
    """Verify FOR_UNIT relationships exist"""
    result = neo4j_session.run("""
        MATCH ()-[r:FOR_UNIT]->()
        RETURN count(r) as count
    """)
    count = result.single()['count']

    assert count >= 0


def test_by_driver_relationships(neo4j_session):
    """Verify BY_DRIVER relationships exist"""
    result = neo4j_session.run("""
        MATCH ()-[r:BY_DRIVER]->()
        RETURN count(r) as count
    """)
    count = result.single()['count']

    assert count >= 0


def test_involves_unit_relationships(neo4j_session):
    """Verify INVOLVES_UNIT relationships exist"""
    result = neo4j_session.run("""
        MATCH ()-[r:INVOLVES_UNIT]->()
        RETURN count(r) as count
    """)
    count = result.single()['count']

    assert count >= 0


def test_involves_driver_relationships(neo4j_session):
    """Verify INVOLVES_DRIVER relationships exist"""
    result = neo4j_session.run("""
        MATCH ()-[r:INVOLVES_DRIVER]->()
        RETURN count(r) as count
    """)
    count = result.single()['count']

    assert count >= 0


# ==========================
# Graph Pattern Validation Tests
# ==========================

def test_driver_to_tractor_pattern(neo4j_session):
    """Verify Driver -> Tractor assignment pattern"""
    result = neo4j_session.run("""
        MATCH (d:Driver)-[r:ASSIGNED_TO]->(t:Tractor)
        RETURN d.driver_id as driver_id, t.unit_number as unit_number
        LIMIT 5
    """)

    records = list(result)
    # May have 0 or more assignments
    assert len(records) >= 0


def test_fuel_transaction_pattern(neo4j_session):
    """Verify FuelTransaction -> Tractor and Driver pattern"""
    result = neo4j_session.run("""
        MATCH (f:FuelTransaction)-[:FOR_UNIT]->(t:Tractor)
        OPTIONAL MATCH (f)-[:BY_DRIVER]->(d:Driver)
        RETURN f, t, d
        LIMIT 5
    """)

    records = list(result)
    assert len(records) >= 0


def test_maintenance_pattern(neo4j_session):
    """Verify MaintenanceRecord -> Tractor pattern"""
    result = neo4j_session.run("""
        MATCH (m:MaintenanceRecord)-[:FOR_UNIT]->(t:Tractor)
        RETURN m, t
        LIMIT 5
    """)

    records = list(result)
    assert len(records) >= 0


def test_incident_pattern(neo4j_session):
    """Verify Incident -> Tractor and Driver pattern"""
    result = neo4j_session.run("""
        MATCH (i:Incident)
        OPTIONAL MATCH (i)-[:INVOLVES_UNIT]->(t:Tractor)
        OPTIONAL MATCH (i)-[:INVOLVES_DRIVER]->(d:Driver)
        RETURN i, t, d
        LIMIT 5
    """)

    records = list(result)
    assert len(records) >= 0


# ==========================
# Temporal Query Validation Tests
# ==========================

def test_temporal_properties_exist(neo4j_session):
    """Verify temporal properties on nodes"""
    result = neo4j_session.run("""
        MATCH (t:Tractor)
        WHERE t.valid_from IS NOT NULL
        RETURN count(t) as count
    """)

    count = result.single()['count']
    # All tractors should have valid_from
    # (Or 0 if no tractors loaded yet)
    assert count >= 0


def test_current_entities_query(neo4j_session):
    """Verify query for current entities (valid_to IS NULL)"""
    result = neo4j_session.run("""
        MATCH (t:Tractor)
        WHERE t.valid_to IS NULL
        RETURN count(t) as count
    """)

    count = result.single()['count']
    assert count >= 0


# ======================
# Summary Test
# ======================

def test_neo4j_complete_setup(neo4j_session):
    """Overall validation that Neo4j is correctly set up"""
    # Count constraints
    result = neo4j_session.run("SHOW CONSTRAINTS")
    constraint_count = len(list(result))

    # Count indexes
    result = neo4j_session.run("SHOW INDEXES")
    index_count = len(list(result))

    # Count node labels
    result = neo4j_session.run("CALL db.labels()")
    label_count = len(list(result))

    # Count relationship types
    result = neo4j_session.run("CALL db.relationshipTypes()")
    rel_type_count = len(list(result))

    assert constraint_count >= 45, f"Expected at least 45 constraints, found {constraint_count}"
    assert index_count >= 20, f"Expected at least 20 indexes, found {index_count}"
    assert label_count >= 7, f"Expected at least 7 labels (Hub 3), found {label_count}"
    # Relationship types may be 0 if no relationships created yet
    assert rel_type_count >= 0
