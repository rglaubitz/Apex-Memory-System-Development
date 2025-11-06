# 6-Hub Schema Data Migration Guide

**Document Status:** Production-Ready
**Last Updated:** 2025-11-04
**Phase:** Phase 3 (Final Integration) - Week 3 Days 3-4

---

## Purpose

This guide provides a comprehensive, step-by-step migration strategy for deploying the 6-hub unified memory system across all 5 databases (PostgreSQL, Neo4j, Qdrant, Redis, Graphiti). It includes:

- **Phased Migration Strategy** - Low-risk deployment in 6 phases
- **Data Transformation Logic** - Converting existing data to new schema
- **Rollback Procedures** - Safe rollback at any phase
- **Testing & Validation** - Comprehensive validation at each step
- **Production Timeline** - Realistic timeline with dependencies

**Target Audience:** DevOps engineers, database administrators, implementation team

---

## Quick Navigation

- [Migration Strategy Overview](#migration-strategy-overview)
- [Pre-Migration Checklist](#pre-migration-checklist)
- [Phase 1: PostgreSQL Foundation](#phase-1-postgresql-foundation)
- [Phase 2: Neo4j Relationships](#phase-2-neo4j-relationships)
- [Phase 3: Qdrant Semantic Search](#phase-3-qdrant-semantic-search)
- [Phase 4: Redis Cache Layer](#phase-4-redis-cache-layer)
- [Phase 5: Graphiti Temporal Tracking](#phase-5-graphiti-temporal-tracking)
- [Phase 6: Production Cutover](#phase-6-production-cutover)
- [Rollback Procedures](#rollback-procedures)
- [Testing & Validation](#testing--validation)
- [Production Timeline](#production-timeline)

---

## Migration Strategy Overview

### High-Level Approach

**Strategy:** Phased migration with parallel old/new systems during transition

**Key Principles:**
- ✅ **Zero downtime** - Old system remains operational during migration
- ✅ **Incremental validation** - Validate each phase before proceeding
- ✅ **Safe rollback** - Can rollback at any phase with no data loss
- ✅ **Dual-write period** - Write to both old and new systems during transition
- ✅ **Read migration** - Gradually shift reads from old to new system

**Timeline:** 4-6 weeks for complete migration

---

### Migration Phases

| Phase | Focus | Duration | Risk | Rollback |
|-------|-------|----------|------|----------|
| **Phase 1** | PostgreSQL Foundation | 1 week | Low | Easy |
| **Phase 2** | Neo4j Relationships | 1 week | Medium | Easy |
| **Phase 3** | Qdrant Semantic Search | 1 week | Low | Easy |
| **Phase 4** | Redis Cache Layer | 3 days | Low | Easy |
| **Phase 5** | Graphiti Temporal Tracking | 4 days | Medium | Easy |
| **Phase 6** | Production Cutover | 1 week | High | Difficult |

**Total:** 4-6 weeks (with buffer for testing and validation)

---

### Data Flow During Migration

**Phase 1-5: Dual-Write Period**
```
Application
├─> Old System (PostgreSQL)      [PRIMARY - 100% reads, 100% writes]
└─> New System (6-hub schema)    [SHADOW - 0% reads, 100% writes, validation only]
```

**Phase 6: Gradual Read Migration**
```
Week 1: Application
        ├─> Old System [PRIMARY - 90% reads, 100% writes]
        └─> New System [10% reads (canary), 100% writes]

Week 2: Application
        ├─> Old System [PRIMARY - 50% reads, 100% writes]
        └─> New System [50% reads, 100% writes]

Week 3: Application
        ├─> Old System [10% reads (fallback), 100% writes]
        └─> New System [PRIMARY - 90% reads, 100% writes]

Week 4: Application
        └─> New System [PRIMARY - 100% reads, 100% writes]
```

---

## Pre-Migration Checklist

### Infrastructure Requirements

**Compute Resources:**
- [ ] PostgreSQL 15+ with sufficient storage (estimate: current size × 1.5)
- [ ] Neo4j 5.14+ with 32GB+ RAM for graph processing
- [ ] Qdrant cluster with 1536-dim vector storage
- [ ] Redis 7+ with sufficient memory for cache (estimate: 10-20% of hot data)
- [ ] Dedicated Graphiti instance (Neo4j-backed)

**Networking:**
- [ ] All databases accessible from application servers
- [ ] Firewall rules configured for database ports
- [ ] SSL/TLS certificates for secure connections

**Backup Infrastructure:**
- [ ] Automated PostgreSQL backups (daily full, hourly incremental)
- [ ] Neo4j backup solution configured
- [ ] Qdrant snapshot strategy
- [ ] Redis persistence (AOF + RDB)

---

### Data Preparation

**Data Audit:**
- [ ] Complete inventory of existing data (tables, row counts, sizes)
- [ ] Identify data quality issues (NULL values, orphaned records, constraint violations)
- [ ] Document data transformations needed
- [ ] Identify test datasets for validation

**Schema Mapping:**
- [ ] Map old schema to new 6-hub schema (entity-by-entity)
- [ ] Document property name changes
- [ ] Identify new required fields (provide defaults)
- [ ] Document data type conversions

**Example Mapping:**

| Old Table | Old Column | New Hub/Table | New Column | Transformation |
|-----------|------------|---------------|------------|----------------|
| `trucks` | `truck_id` | `hub3_origin.tractors` | `unit_number` | Format: "6520" |
| `trucks` | `location` | `hub3_origin.tractors` | `location_gps` | Convert to PostGIS POINT |
| `trucks` | `driver` | Neo4j relationship | `ASSIGNED_TO` | Create relationship |

---

### Team Preparation

**Roles & Responsibilities:**
- [ ] **Migration Lead:** Overall coordination, go/no-go decisions
- [ ] **Database Admin:** Execute DDL, monitor performance
- [ ] **Backend Engineer:** Dual-write implementation, API updates
- [ ] **QA Engineer:** Validation testing, data quality checks
- [ ] **DevOps:** Infrastructure, monitoring, rollback procedures

**Communication Plan:**
- [ ] Daily standups during migration
- [ ] Slack channel for real-time updates
- [ ] Runbook with escalation procedures
- [ ] Post-migration retrospective

---

### Monitoring Setup

**Alerts:**
- [ ] Database replication lag (PostgreSQL → Neo4j sync)
- [ ] Query performance degradation
- [ ] Error rate spikes
- [ ] Disk space utilization
- [ ] Data discrepancy alerts (old vs new system)

**Dashboards:**
- [ ] Migration progress dashboard (records migrated per table)
- [ ] Data quality dashboard (validation query results)
- [ ] Performance dashboard (query latency, throughput)
- [ ] Dual-write dashboard (write success rate to both systems)

---

## Phase 1: PostgreSQL Foundation

**Duration:** 1 week
**Objective:** Create all 6 hub schemas, tables, indexes, constraints in PostgreSQL

---

### Step 1.1: Create Database and Extensions

**Script:** `scripts/migration/phase1_01_create_database.sql`

```sql
-- Create database (if not exists)
-- Note: Run as postgres superuser
CREATE DATABASE apex_memory
    WITH OWNER = apex
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8'
    TEMPLATE = template0;

\c apex_memory

-- Install required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";      -- UUID generation
CREATE EXTENSION IF NOT EXISTS "pg_trgm";        -- Trigram search
CREATE EXTENSION IF NOT EXISTS "btree_gin";      -- GIN indexes on scalars
CREATE EXTENSION IF NOT EXISTS "pgcrypto";       -- Encryption (for Hub 1 Assets)
CREATE EXTENSION IF NOT EXISTS "postgis";        -- Geography (for truck locations)

-- Verify extensions
SELECT extname, extversion FROM pg_extension;
```

**Validation:**
```sql
-- Expected output: uuid-ossp, pg_trgm, btree_gin, pgcrypto, postgis
SELECT extname FROM pg_extension WHERE extname IN ('uuid-ossp', 'pg_trgm', 'btree_gin', 'pgcrypto', 'postgis');
-- Should return 5 rows
```

---

### Step 1.2: Create Hub Schemas

**Script:** `scripts/migration/phase1_02_create_schemas.sql`

```sql
-- Create all 6 hub schemas
CREATE SCHEMA IF NOT EXISTS hub1_command;
CREATE SCHEMA IF NOT EXISTS hub2_openhaul;
CREATE SCHEMA IF NOT EXISTS hub3_origin;
CREATE SCHEMA IF NOT EXISTS hub4_contacts;
CREATE SCHEMA IF NOT EXISTS hub5_financials;
CREATE SCHEMA IF NOT EXISTS hub6_corporate;

-- Grant permissions
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
```

**Validation:**
```sql
SELECT schema_name FROM information_schema.schemata
WHERE schema_name LIKE 'hub%'
ORDER BY schema_name;
-- Should return 6 rows
```

---

### Step 1.3: Create Tables (Hub-by-Hub)

**Approach:** Create tables hub-by-hub to allow incremental validation

**Script:** `scripts/migration/phase1_03_create_tables_hub1.sql`

```sql
-- Hub 1: G (Command Center)

-- Table: g_persons
CREATE TABLE hub1_command.g_persons (
    user_id VARCHAR(50) PRIMARY KEY,
    person_id VARCHAR(50) NOT NULL,  -- Links to hub4_contacts.persons
    name VARCHAR(255) NOT NULL,
    display_name VARCHAR(100),

    -- Contact
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(20),
    location VARCHAR(255),
    timezone VARCHAR(50),

    -- Strategic Properties
    role VARCHAR(255),
    vision TEXT,
    current_focus TEXT[],
    decision_framework JSONB,
    communication_style VARCHAR(100),

    -- Temporal
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    valid_from TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    valid_to TIMESTAMPTZ,

    CONSTRAINT fk_person FOREIGN KEY (person_id) REFERENCES hub4_contacts.persons(person_id)
);

-- Indexes
CREATE INDEX idx_g_persons_person_id ON hub1_command.g_persons(person_id);
CREATE INDEX idx_g_persons_email ON hub1_command.g_persons(email);
CREATE INDEX idx_g_persons_temporal ON hub1_command.g_persons(valid_from, valid_to) WHERE valid_to IS NULL;

-- Trigger for auto-update updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_g_persons_updated_at
BEFORE UPDATE ON hub1_command.g_persons
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Table: projects
CREATE TABLE hub1_command.projects (
    project_id VARCHAR(50) PRIMARY KEY,
    project_name VARCHAR(255) NOT NULL,
    project_code VARCHAR(50) UNIQUE,
    project_type VARCHAR(100),
    category VARCHAR(100),

    -- Status
    status VARCHAR(50) NOT NULL CHECK (status IN ('planned', 'active', 'on_hold', 'completed', 'cancelled')),
    priority INTEGER CHECK (priority BETWEEN 1 AND 5),
    progress_percentage DECIMAL(5,2) CHECK (progress_percentage BETWEEN 0 AND 100),

    -- Details
    description TEXT,
    completion_criteria TEXT[],
    success_metrics JSONB,

    -- Dates
    start_date DATE,
    target_completion_date DATE,
    actual_completion_date DATE,

    -- Relationships
    related_goals TEXT[],  -- Array of goal_ids

    -- Temporal
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    valid_from TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    valid_to TIMESTAMPTZ
);

-- Indexes
CREATE INDEX idx_projects_status ON hub1_command.projects(status) WHERE status IN ('active', 'planned');
CREATE INDEX idx_projects_category ON hub1_command.projects(category);
CREATE INDEX idx_projects_related_goals ON hub1_command.projects USING GIN (related_goals);
CREATE INDEX idx_projects_temporal ON hub1_command.projects(valid_from, valid_to) WHERE valid_to IS NULL;

-- Trigger
CREATE TRIGGER update_projects_updated_at
BEFORE UPDATE ON hub1_command.projects
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Continue for all 8 Hub 1 entities...
-- (goals, tasks, insights, knowledge_items, assets, notes)
```

**Validation:**
```sql
-- Verify table creation
SELECT table_schema, table_name, table_type
FROM information_schema.tables
WHERE table_schema = 'hub1_command'
ORDER BY table_name;
-- Should return 8 rows (8 entities in Hub 1)

-- Verify indexes
SELECT schemaname, tablename, indexname
FROM pg_indexes
WHERE schemaname = 'hub1_command'
ORDER BY tablename, indexname;
-- Should return ~24 indexes (3 per table average)

-- Verify triggers
SELECT trigger_schema, event_object_table, trigger_name
FROM information_schema.triggers
WHERE trigger_schema = 'hub1_command';
-- Should return 8 rows (1 per table)
```

**Repeat for Hub 2-6:**
- `phase1_03_create_tables_hub2.sql` (8 entities)
- `phase1_03_create_tables_hub3.sql` (7 entities)
- `phase1_03_create_tables_hub4.sql` (7 entities)
- `phase1_03_create_tables_hub5.sql` (8 entities)
- `phase1_03_create_tables_hub6.sql` (7 entities)

---

### Step 1.4: Data Transformation and Load

**Approach:** Extract from old system → Transform → Load into new 6-hub schema

**Script:** `scripts/migration/phase1_04_transform_hub3_tractors.py`

```python
import psycopg2
from datetime import datetime

# Connect to old and new databases
old_conn = psycopg2.connect(
    host="localhost",
    database="apex_memory_old",
    user="apex",
    password="apexmemory2024"
)

new_conn = psycopg2.connect(
    host="localhost",
    database="apex_memory",
    user="apex",
    password="apexmemory2024"
)

def transform_tractors():
    """Transform trucks from old schema to hub3_origin.tractors"""

    with old_conn.cursor() as old_cur, new_conn.cursor() as new_cur:
        # Extract from old system
        old_cur.execute("""
            SELECT
                truck_id,
                vin,
                make,
                model,
                year,
                status,
                current_miles,
                location,  -- Text: "Las Vegas, NV"
                purchase_date,
                purchase_price,
                current_value,
                insurance_policy_number,
                insurance_provider,
                insurance_expiry_date,
                created_at,
                updated_at
            FROM trucks
            WHERE active = true
        """)

        trucks = old_cur.fetchall()

        transformed_count = 0
        for truck in trucks:
            # Transform data
            unit_number = format_unit_number(truck[0])  # "6520" format
            location_gps = geocode_location(truck[7])  # Convert to PostGIS POINT

            # Insert into new schema
            new_cur.execute("""
                INSERT INTO hub3_origin.tractors (
                    unit_number, vin, make, model, year, status,
                    current_miles, location_gps,
                    purchase_date, purchase_price, current_value,
                    insurance_policy_number, insurance_provider, insurance_expiry_date,
                    created_at, updated_at, valid_from, valid_to
                ) VALUES (
                    %s, %s, %s, %s, %s, %s,
                    %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326),
                    %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s, NULL
                )
                ON CONFLICT (unit_number) DO NOTHING
            """, (
                unit_number, truck[1], truck[2], truck[3], truck[4], truck[5],
                truck[6], location_gps['lon'], location_gps['lat'],
                truck[8], truck[9], truck[10],
                truck[11], truck[12], truck[13],
                truck[14], truck[15], truck[14]  # valid_from = created_at
            ))

            transformed_count += 1

        new_conn.commit()
        print(f"✅ Transformed {transformed_count} tractors")

def format_unit_number(truck_id):
    """Convert old truck_id to new unit_number format"""
    # Example: "TRUCK-6520" -> "6520"
    return truck_id.replace("TRUCK-", "")

def geocode_location(location_text):
    """Convert location text to GPS coordinates"""
    # Simple lookup (in production, use geocoding API)
    locations = {
        "Las Vegas, NV": {"lat": 36.1699, "lon": -115.1398},
        "Los Angeles, CA": {"lat": 34.0522, "lon": -118.2437}
    }
    return locations.get(location_text, {"lat": 0.0, "lon": 0.0})

if __name__ == "__main__":
    transform_tractors()
```

**Validation:**
```sql
-- Compare row counts (old vs new)
SELECT 'Old System' as source, COUNT(*) as tractor_count FROM apex_memory_old.trucks WHERE active = true
UNION ALL
SELECT 'New System' as source, COUNT(*) as tractor_count FROM hub3_origin.tractors WHERE valid_to IS NULL;
-- Row counts should match

-- Sample data comparison
SELECT unit_number, make, model, year FROM hub3_origin.tractors LIMIT 5;
-- Verify data looks correct
```

**Repeat for all 45 entities across 6 hubs**

---

### Step 1.5: Phase 1 Validation

**Run all Phase 1 validation queries** from `6-HUB-SCHEMA-VALIDATION-QUERIES.md`:

```bash
# Execute validation script
python scripts/migration/phase1_validate.py

# Expected output:
# ✅ Q1.1: G Person Entity Integrity - 0 issues
# ✅ Q1.2: Project → Goal Relationships - 0 issues
# ...
# ✅ All Phase 1 validation queries passed
```

**Go/No-Go Decision:**
- ✅ All tables created (45 entities)
- ✅ All indexes created (~135 indexes)
- ✅ All triggers created (45 triggers)
- ✅ All data loaded (compare row counts)
- ✅ All validation queries passed (0 critical issues)
- ✅ Performance acceptable (query latency < 1s)

**If Go:** Proceed to Phase 2
**If No-Go:** Rollback Phase 1 (see [Rollback Procedures](#rollback-procedures))

---

## Phase 2: Neo4j Relationships

**Duration:** 1 week
**Objective:** Create all nodes and relationships in Neo4j as REPLICA of PostgreSQL

---

### Step 2.1: Create Neo4j Constraints

**Script:** `scripts/migration/phase2_01_create_constraints.cypher`

```cypher
// Tractors
CREATE CONSTRAINT constraint_tractor_unit IF NOT EXISTS
FOR (t:Tractor) REQUIRE t.unit_number IS UNIQUE;

CREATE CONSTRAINT constraint_tractor_vin IF NOT EXISTS
FOR (t:Tractor) REQUIRE t.vin IS UNIQUE;

// Trailers
CREATE CONSTRAINT constraint_trailer_number IF NOT EXISTS
FOR (t:Trailer) REQUIRE t.trailer_number IS UNIQUE;

// Drivers
CREATE CONSTRAINT constraint_driver_id IF NOT EXISTS
FOR (d:Driver) REQUIRE d.driver_id IS UNIQUE;

// Loads
CREATE CONSTRAINT constraint_load_number IF NOT EXISTS
FOR (l:Load) REQUIRE l.load_number IS UNIQUE;

// Companies
CREATE CONSTRAINT constraint_company_id IF NOT EXISTS
FOR (c:Company) REQUIRE c.company_id IS UNIQUE;

// Persons
CREATE CONSTRAINT constraint_person_id IF NOT EXISTS
FOR (p:Person) REQUIRE p.person_id IS UNIQUE;

// Legal Entities
CREATE CONSTRAINT constraint_entity_id IF NOT EXISTS
FOR (e:LegalEntity) REQUIRE e.entity_id IS UNIQUE;

// Goals
CREATE CONSTRAINT constraint_goal_id IF NOT EXISTS
FOR (g:Goal) REQUIRE g.goal_id IS UNIQUE;

// Projects
CREATE CONSTRAINT constraint_project_id IF NOT EXISTS
FOR (p:Project) REQUIRE p.project_id IS UNIQUE;

// Continue for all 45 entity types...
```

**Validation:**
```cypher
// Verify constraints
SHOW CONSTRAINTS;
// Should return 45 UNIQUE constraints (1 per entity type)
```

---

### Step 2.2: Load Nodes from PostgreSQL

**Script:** `scripts/migration/phase2_02_load_nodes.py`

```python
import psycopg2
from neo4j import GraphDatabase

# Connect to PostgreSQL
pg_conn = psycopg2.connect(
    host="localhost",
    database="apex_memory",
    user="apex",
    password="apexmemory2024"
)

# Connect to Neo4j
neo4j_driver = GraphDatabase.driver(
    "bolt://localhost:7687",
    auth=("neo4j", "apexmemory2024")
)

def load_tractors_to_neo4j():
    """Load tractors from PostgreSQL to Neo4j"""

    with pg_conn.cursor() as pg_cur, neo4j_driver.session() as neo4j_session:
        # Extract from PostgreSQL
        pg_cur.execute("""
            SELECT
                unit_number, vin, make, model, year, status,
                current_miles, engine_hours,
                purchase_date, purchase_price, current_value,
                financing_status, lender_name, loan_balance,
                insurance_policy_number, insurance_provider, insurance_expiry_date,
                created_at, updated_at, valid_from, valid_to
            FROM hub3_origin.tractors
            WHERE valid_to IS NULL  -- Only current records
        """)

        tractors = pg_cur.fetchall()

        # Load into Neo4j
        for tractor in tractors:
            neo4j_session.run("""
                MERGE (t:Tractor {unit_number: $unit_number})
                SET t.vin = $vin,
                    t.make = $make,
                    t.model = $model,
                    t.year = $year,
                    t.status = $status,
                    t.current_miles = $current_miles,
                    t.engine_hours = $engine_hours,
                    t.purchase_date = date($purchase_date),
                    t.purchase_price = $purchase_price,
                    t.current_value = $current_value,
                    t.financing_status = $financing_status,
                    t.lender_name = $lender_name,
                    t.loan_balance = $loan_balance,
                    t.insurance_policy_number = $insurance_policy_number,
                    t.insurance_provider = $insurance_provider,
                    t.insurance_expiry_date = date($insurance_expiry_date),
                    t.created_at = datetime($created_at),
                    t.updated_at = datetime($updated_at),
                    t.valid_from = datetime($valid_from),
                    t.valid_to = datetime($valid_to)
            """, {
                "unit_number": tractor[0],
                "vin": tractor[1],
                "make": tractor[2],
                "model": tractor[3],
                "year": tractor[4],
                "status": tractor[5],
                "current_miles": tractor[6],
                "engine_hours": tractor[7],
                "purchase_date": str(tractor[8]) if tractor[8] else None,
                "purchase_price": float(tractor[9]) if tractor[9] else None,
                "current_value": float(tractor[10]) if tractor[10] else None,
                "financing_status": tractor[11],
                "lender_name": tractor[12],
                "loan_balance": float(tractor[13]) if tractor[13] else None,
                "insurance_policy_number": tractor[14],
                "insurance_provider": tractor[15],
                "insurance_expiry_date": str(tractor[16]) if tractor[16] else None,
                "created_at": tractor[17].isoformat(),
                "updated_at": tractor[18].isoformat(),
                "valid_from": tractor[19].isoformat(),
                "valid_to": tractor[20].isoformat() if tractor[20] else None
            })

        print(f"✅ Loaded {len(tractors)} tractors to Neo4j")

if __name__ == "__main__":
    load_tractors_to_neo4j()
    # Repeat for all 45 entity types...
```

**Validation:**
```cypher
// Compare node counts (PostgreSQL vs Neo4j)
MATCH (n:Tractor)
RETURN count(n) as neo4j_tractor_count;
// Should match PostgreSQL count
```

---

### Step 2.3: Create Relationships

**Script:** `scripts/migration/phase2_03_create_relationships.py`

```python
def create_driver_tractor_assignments():
    """Create ASSIGNED_TO relationships between drivers and tractors"""

    with pg_conn.cursor() as pg_cur, neo4j_driver.session() as neo4j_session:
        # Get current assignments from PostgreSQL
        pg_cur.execute("""
            SELECT
                driver_id,
                current_unit_assignment,
                -- Assuming assignment_history table exists
                ah.assigned_date,
                ah.end_date
            FROM hub3_origin.drivers d
            LEFT JOIN hub3_origin.assignment_history ah
                ON d.driver_id = ah.driver_id
                AND ah.end_date IS NULL
            WHERE d.current_unit_assignment IS NOT NULL
        """)

        assignments = pg_cur.fetchall()

        for assignment in assignments:
            driver_id, unit_number, assigned_date, end_date = assignment

            # Create relationship
            neo4j_session.run("""
                MATCH (d:Driver {driver_id: $driver_id})
                MATCH (t:Tractor {unit_number: $unit_number})
                MERGE (d)-[a:ASSIGNED_TO]->(t)
                SET a.assigned_date = date($assigned_date),
                    a.end_date = date($end_date),
                    a.valid_from = datetime($assigned_date),
                    a.valid_to = datetime($end_date)
            """, {
                "driver_id": driver_id,
                "unit_number": unit_number,
                "assigned_date": str(assigned_date) if assigned_date else None,
                "end_date": str(end_date) if end_date else None
            })

        print(f"✅ Created {len(assignments)} ASSIGNED_TO relationships")

def create_load_relationships():
    """Create load-related relationships"""

    with pg_conn.cursor() as pg_cur, neo4j_driver.session() as neo4j_session:
        # Get loads with relationships
        pg_cur.execute("""
            SELECT
                load_number,
                carrier_id,
                customer_id,
                shipper_id,
                assigned_unit,
                pickup_location_id,
                delivery_location_id
            FROM hub2_openhaul.loads
            WHERE valid_to IS NULL
        """)

        loads = pg_cur.fetchall()

        for load in loads:
            load_number, carrier_id, customer_id, shipper_id, assigned_unit, pickup_id, delivery_id = load

            # Create HAULED_BY relationship
            if carrier_id:
                neo4j_session.run("""
                    MATCH (l:Load {load_number: $load_number})
                    MATCH (c:Carrier {carrier_id: $carrier_id})
                    MERGE (l)-[:HAULED_BY]->(c)
                """, {"load_number": load_number, "carrier_id": carrier_id})

            # Create FOR_CUSTOMER relationship
            if customer_id:
                neo4j_session.run("""
                    MATCH (l:Load {load_number: $load_number})
                    MATCH (c:Company {company_id: $customer_id})
                    MERGE (l)-[:FOR_CUSTOMER]->(c)
                """, {"load_number": load_number, "customer_id": customer_id})

            # Create ASSIGNED_UNIT relationship
            if assigned_unit:
                neo4j_session.run("""
                    MATCH (l:Load {load_number: $load_number})
                    MATCH (t:Tractor {unit_number: $assigned_unit})
                    MERGE (l)-[:ASSIGNED_UNIT]->(t)
                """, {"load_number": load_number, "assigned_unit": assigned_unit})

            # Create PICKUP_AT and DELIVERY_AT relationships
            # (similar pattern)

        print(f"✅ Created load relationships for {len(loads)} loads")

# Create all relationship types:
# - Hub 1: Project -[:DRIVES]-> Load, Goal -[:MEASURED_BY]-> Revenue/Expense
# - Hub 2: Load -[:HAULED_BY]-> Carrier, Load -[:FOR_CUSTOMER]-> Company
# - Hub 3: Driver -[:ASSIGNED_TO]-> Tractor, FuelTransaction -[:FOR_UNIT]-> Tractor
# - Hub 4: Person -[:WORKS_FOR]-> Company, Person -[:KNOWS]-> Person
# - Hub 5: Expense -[:PAID_BY]-> LegalEntity, Revenue -[:RECEIVED_BY]-> LegalEntity
# - Hub 6: LegalEntity -[:OWNS]-> LegalEntity, Document -[:RELATED_TO]-> LegalEntity
```

**Validation:**
```cypher
// Verify relationship counts
MATCH ()-[r:ASSIGNED_TO]->()
RETURN count(r) as assigned_to_count;
// Should match expected assignment count

// Verify load relationships
MATCH (l:Load)-[:HAULED_BY]->(c:Carrier)
RETURN count(l) as loads_with_carrier;
// Should match PostgreSQL load count
```

---

### Step 2.4: Phase 2 Validation

**Run all Phase 2 Neo4j validation queries** from `6-HUB-SCHEMA-VALIDATION-QUERIES.md`:

```bash
# Execute validation script
python scripts/migration/phase2_validate.py

# Expected output:
# ✅ N1: Node Count Consistency - 0 mismatches
# ✅ N2: Relationship Integrity - 0 orphaned relationships
# ✅ N3: Driver → Tractor Assignment Consistency - 0 issues
# ...
# ✅ All Phase 2 validation queries passed
```

**Go/No-Go Decision:**
- ✅ All nodes created (45 entity types)
- ✅ All relationships created (150+ relationship types)
- ✅ Node counts match PostgreSQL
- ✅ Relationship integrity validated
- ✅ Temporal queries working

**If Go:** Proceed to Phase 3
**If No-Go:** Rollback Phase 2

---

## Phase 3: Qdrant Semantic Search

**Duration:** 1 week
**Objective:** Create Qdrant collections and load embeddings for semantic search

---

### Step 3.1: Create Qdrant Collections

**Script:** `scripts/migration/phase3_01_create_collections.py`

```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PayloadSchemaType

client = QdrantClient(host="localhost", port=6333)

def create_collections():
    """Create all Qdrant collections"""

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
        field_name="hub",
        field_schema=PayloadSchemaType.KEYWORD
    )

    print("✅ Created 'documents' collection with 3 payload indexes")

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

    print("✅ Created 'knowledge_items' collection")

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
        field_name="insight_category",
        field_schema=PayloadSchemaType.KEYWORD
    )

    print("✅ Created 'insights' collection")

if __name__ == "__main__":
    create_collections()
```

**Validation:**
```python
# Verify collections
collections = client.get_collections()
print(f"Collections: {[c.name for c in collections.collections]}")
# Expected: ['documents', 'knowledge_items', 'insights']
```

---

### Step 3.2: Generate and Load Embeddings

**Script:** `scripts/migration/phase3_02_load_embeddings.py`

```python
import psycopg2
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
import openai
import uuid

# Configuration
openai.api_key = "YOUR_OPENAI_API_KEY"
qdrant_client = QdrantClient(host="localhost", port=6333)

pg_conn = psycopg2.connect(
    host="localhost",
    database="apex_memory",
    user="apex",
    password="apexmemory2024"
)

def generate_embedding(text):
    """Generate embedding using OpenAI"""
    response = openai.embeddings.create(
        model="text-embedding-3-large",
        input=text
    )
    return response.data[0].embedding

def load_documents():
    """Load documents from PostgreSQL to Qdrant"""

    with pg_conn.cursor() as cur:
        # Get all documents from Hub 6
        cur.execute("""
            SELECT
                document_id,
                document_name,
                document_type,
                content_text,  -- Assuming extracted text
                related_entity_id,
                metadata
            FROM hub6_corporate.documents
            WHERE valid_to IS NULL
              AND content_text IS NOT NULL
        """)

        documents = cur.fetchall()

        points = []
        for doc in documents:
            document_id, name, doc_type, content, entity_id, metadata = doc

            # Generate embedding
            embedding = generate_embedding(content[:8000])  # Truncate to 8K chars

            # Create point
            point = PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload={
                    "document_id": document_id,
                    "document_name": name,
                    "document_type": doc_type,
                    "entity_type": "Document",
                    "hub": "hub6_corporate",
                    "related_entity_id": entity_id,
                    "content_preview": content[:500],  # First 500 chars
                    "metadata": metadata
                }
            )
            points.append(point)

            # Batch upload every 100 documents
            if len(points) >= 100:
                qdrant_client.upsert(
                    collection_name="documents",
                    points=points
                )
                print(f"✅ Uploaded {len(points)} document embeddings")
                points = []

        # Upload remaining
        if points:
            qdrant_client.upsert(
                collection_name="documents",
                points=points
            )
            print(f"✅ Uploaded final {len(points)} document embeddings")

        print(f"✅ Total: {len(documents)} documents embedded")

def load_knowledge_items():
    """Load knowledge items from Hub 1 to Qdrant"""

    with pg_conn.cursor() as cur:
        cur.execute("""
            SELECT
                knowledge_id,
                title,
                category,
                content,
                tags
            FROM hub1_command.knowledge_items
            WHERE valid_to IS NULL
        """)

        items = cur.fetchall()

        points = []
        for item in items:
            knowledge_id, title, category, content, tags = item

            # Generate embedding (title + content)
            text = f"{title}\n\n{content}"
            embedding = generate_embedding(text[:8000])

            point = PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload={
                    "knowledge_id": knowledge_id,
                    "title": title,
                    "category": category,
                    "tags": tags,
                    "content_preview": content[:500]
                }
            )
            points.append(point)

        qdrant_client.upsert(
            collection_name="knowledge_items",
            points=points
        )
        print(f"✅ Uploaded {len(items)} knowledge items")

if __name__ == "__main__":
    load_documents()
    load_knowledge_items()
    # Continue for insights...
```

**Validation:**
```python
# Verify point counts
docs_info = qdrant_client.get_collection("documents")
print(f"Documents: {docs_info.points_count} points")

knowledge_info = qdrant_client.get_collection("knowledge_items")
print(f"Knowledge Items: {knowledge_info.points_count} points")

# Test semantic search
results = qdrant_client.search(
    collection_name="documents",
    query_vector=generate_embedding("maintenance records for Unit #6520"),
    limit=5
)
print(f"✅ Semantic search working: {len(results)} results")
```

---

### Step 3.3: Phase 3 Validation

**Run cross-database sync validation** from `6-HUB-SCHEMA-VALIDATION-QUERIES.md`:

```bash
python scripts/migration/phase3_validate.py

# Expected output:
# ✅ C2: PostgreSQL ↔ Qdrant Vector Sync - 0% mismatch
# ✅ Semantic search functional
# ✅ All Phase 3 validation queries passed
```

**Go/No-Go Decision:**
- ✅ All collections created (3 collections)
- ✅ All embeddings loaded (compare counts with PostgreSQL)
- ✅ Semantic search functional
- ✅ Query latency acceptable (<1s)

**If Go:** Proceed to Phase 4
**If No-Go:** Rollback Phase 3

---

## Phase 4: Redis Cache Layer

**Duration:** 3 days
**Objective:** Configure Redis cache layer for real-time data and query caching

---

### Step 4.1: Configure Redis Key Patterns

**Script:** `scripts/migration/phase4_01_redis_setup.sh`

```bash
#!/bin/bash

# Connect to Redis
redis-cli -h localhost -p 6379 <<EOF

# Set maxmemory policy (evict least recently used when full)
CONFIG SET maxmemory-policy allkeys-lru
CONFIG SET maxmemory 4gb

# Enable keyspace notifications (for cache invalidation)
CONFIG SET notify-keyspace-events Ex

# Save configuration
CONFIG REWRITE

EOF

echo "✅ Redis configured"
```

---

### Step 4.2: Populate Redis Cache

**Script:** `scripts/migration/phase4_02_populate_cache.py`

```python
import redis
import psycopg2
import json

redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

pg_conn = psycopg2.connect(
    host="localhost",
    database="apex_memory",
    user="apex",
    password="apexmemory2024"
)

def populate_truck_cache():
    """Populate real-time truck data in Redis"""

    with pg_conn.cursor() as cur:
        # Get all active trucks
        cur.execute("""
            SELECT
                unit_number,
                ST_Y(location_gps) as lat,
                ST_X(location_gps) as lon,
                status,
                current_miles,
                current_driver_id
            FROM hub3_origin.tractors
            WHERE status = 'active'
              AND valid_to IS NULL
        """)

        trucks = cur.fetchall()

        for truck in trucks:
            unit_number, lat, lon, status, miles, driver_id = truck

            # Cache location (TTL: 60 seconds - refreshed by Samsara)
            redis_client.setex(
                f"truck:{unit_number}:location",
                60,
                json.dumps({"lat": lat, "lon": lon})
            )

            # Cache status (TTL: 60 seconds)
            redis_client.setex(
                f"truck:{unit_number}:status",
                60,
                status
            )

            # Cache current driver (TTL: 5 minutes)
            if driver_id:
                redis_client.setex(
                    f"truck:{unit_number}:current_driver",
                    300,
                    driver_id
                )

            # Cache current miles (TTL: 60 seconds)
            redis_client.setex(
                f"truck:{unit_number}:current_miles",
                60,
                str(miles)
            )

        print(f"✅ Cached data for {len(trucks)} trucks")

def populate_hot_query_cache():
    """Pre-warm cache with hot queries"""

    # Example: Cache company summary for OpenHaul
    with pg_conn.cursor() as cur:
        cur.execute("""
            SELECT
                company_id,
                company_name,
                categories,
                primary_contact_id
            FROM hub4_contacts.companies
            WHERE company_id = 'company_openhaul'
        """)

        company = cur.fetchone()

        if company:
            redis_client.setex(
                "company:company_openhaul:summary",
                3600,  # 1 hour TTL
                json.dumps({
                    "company_id": company[0],
                    "company_name": company[1],
                    "categories": company[2],
                    "primary_contact_id": company[3]
                })
            )
            print("✅ Cached OpenHaul company summary")

if __name__ == "__main__":
    populate_truck_cache()
    populate_hot_query_cache()
```

**Validation:**
```python
# Verify cache entries
truck_location = redis_client.get("truck:6520:location")
print(f"Cached truck location: {truck_location}")

# Verify TTL
ttl = redis_client.ttl("truck:6520:location")
print(f"TTL: {ttl} seconds")  # Should be ~60

# Verify keyspace
keys = redis_client.keys("truck:*")
print(f"✅ {len(keys)} truck-related keys in cache")
```

---

### Step 4.3: Phase 4 Validation

```bash
python scripts/migration/phase4_validate.py

# Expected output:
# ✅ Redis maxmemory configured
# ✅ Cache populated for 15 active trucks
# ✅ Hot queries cached
# ✅ TTLs configured correctly
# ✅ All Phase 4 validation passed
```

**Go/No-Go Decision:**
- ✅ Redis configured (maxmemory, eviction policy)
- ✅ Cache populated (truck data, hot queries)
- ✅ TTLs working correctly
- ✅ Cache hit rate >70% (after warm-up)

**If Go:** Proceed to Phase 5
**If No-Go:** Rollback Phase 4

---

## Phase 5: Graphiti Temporal Tracking

**Duration:** 4 days
**Objective:** Configure Graphiti for temporal entity tracking and pattern detection

---

### Step 5.1: Initialize Graphiti

**Script:** `scripts/migration/phase5_01_init_graphiti.py`

```python
from graphiti_core import Graphiti

# Initialize Graphiti
graphiti = Graphiti(
    neo4j_uri="bolt://localhost:7687",
    neo4j_user="neo4j",
    neo4j_password="apexmemory2024"
)

# Initialize schema
graphiti.initialize()

print("✅ Graphiti initialized")
```

---

### Step 5.2: Register Entity Types

**Script:** `scripts/migration/phase5_02_register_entities.py`

```python
tracked_entities = [
    # Hub 1: Command Center
    {"entity_type": "Goal", "id_field": "goal_id", "temporal_properties": ["status", "progress_percentage", "current_value"]},
    {"entity_type": "Project", "id_field": "project_id", "temporal_properties": ["status", "progress_percentage"]},

    # Hub 2: OpenHaul
    {"entity_type": "Load", "id_field": "load_number", "temporal_properties": ["status", "location", "assigned_driver"]},

    # Hub 3: Origin
    {"entity_type": "Tractor", "id_field": "unit_number", "temporal_properties": ["status", "current_miles", "current_driver_id", "location_gps"]},
    {"entity_type": "Driver", "id_field": "driver_id", "temporal_properties": ["status", "current_unit_assignment"]},

    # Hub 4: Contacts
    {"entity_type": "Company", "id_field": "company_id", "temporal_properties": ["categories", "primary_contact_id"]},

    # Hub 5: Financials
    {"entity_type": "Revenue", "id_field": "revenue_id", "temporal_properties": ["amount", "status"]},
    {"entity_type": "Expense", "id_field": "expense_id", "temporal_properties": ["amount", "status"]},

    # Hub 6: Corporate
    {"entity_type": "LegalEntity", "id_field": "entity_id", "temporal_properties": ["status", "owner_entity_id"]},
    {"entity_type": "License", "id_field": "license_id", "temporal_properties": ["status", "expiration_date"]},
]

for entity_config in tracked_entities:
    graphiti.register_entity_type(**entity_config)
    print(f"✅ Registered {entity_config['entity_type']} for temporal tracking")

print(f"✅ Total: {len(tracked_entities)} entity types registered")
```

---

### Step 5.3: Load Historical Timeline

**Script:** `scripts/migration/phase5_03_load_timeline.py`

```python
import psycopg2
from graphiti_core import Graphiti

graphiti = Graphiti(
    neo4j_uri="bolt://localhost:7687",
    neo4j_user="neo4j",
    neo4j_password="apexmemory2024"
)

pg_conn = psycopg2.connect(
    host="localhost",
    database="apex_memory",
    user="apex",
    password="apexmemory2024"
)

def load_goal_timeline():
    """Load goal progress timeline into Graphiti"""

    with pg_conn.cursor() as cur:
        # Get goal history from audit table
        cur.execute("""
            SELECT
                goal_id,
                progress_percentage,
                current_value,
                status,
                updated_at
            FROM hub1_command.goal_audit_log
            ORDER BY goal_id, updated_at
        """)

        events = cur.fetchall()

        for event in events:
            goal_id, progress, current_value, status, timestamp = event

            # Add temporal event to Graphiti
            graphiti.add_state_change(
                entity_type="Goal",
                entity_id=goal_id,
                timestamp=timestamp,
                properties={
                    "progress_percentage": progress,
                    "current_value": current_value,
                    "status": status
                }
            )

        print(f"✅ Loaded {len(events)} goal timeline events")

def load_driver_assignment_history():
    """Load driver assignment history"""

    with pg_conn.cursor() as cur:
        cur.execute("""
            SELECT
                driver_id,
                unit_number,
                assigned_date,
                end_date
            FROM hub3_origin.assignment_history
            ORDER BY driver_id, assigned_date
        """)

        assignments = cur.fetchall()

        for assignment in assignments:
            driver_id, unit_number, start_date, end_date = assignment

            # Add assignment start event
            graphiti.add_state_change(
                entity_type="Driver",
                entity_id=driver_id,
                timestamp=start_date,
                properties={
                    "current_unit_assignment": unit_number,
                    "status": "assigned"
                }
            )

            # Add assignment end event (if exists)
            if end_date:
                graphiti.add_state_change(
                    entity_type="Driver",
                    entity_id=driver_id,
                    timestamp=end_date,
                    properties={
                        "current_unit_assignment": None,
                        "status": "available"
                    }
                )

        print(f"✅ Loaded {len(assignments)} driver assignment events")

if __name__ == "__main__":
    load_goal_timeline()
    load_driver_assignment_history()
    # Continue for other entity types...
```

**Validation:**
```python
# Test temporal query
timeline = graphiti.get_entity_timeline(
    entity_type="Goal",
    entity_id="goal_openhaul_revenue_2025",
    property="progress_percentage"
)

print(f"✅ Goal timeline: {len(timeline)} events")
print(f"   Latest progress: {timeline[-1][1]}%")

# Test driver assignment query
driver_timeline = graphiti.get_entity_timeline(
    entity_type="Driver",
    entity_id="driver_robert",
    property="current_unit_assignment"
)

print(f"✅ Driver assignment history: {len(driver_timeline)} events")
```

---

### Step 5.4: Phase 5 Validation

```bash
python scripts/migration/phase5_validate.py

# Expected output:
# ✅ Graphiti initialized
# ✅ 16 entity types registered
# ✅ Goal timeline: 120 events loaded
# ✅ Driver assignment history: 45 events loaded
# ✅ Temporal queries working
# ✅ All Phase 5 validation passed
```

**Go/No-Go Decision:**
- ✅ Graphiti initialized
- ✅ All entity types registered (16 types)
- ✅ Historical timeline loaded
- ✅ Temporal queries working
- ✅ Pattern detection functional

**If Go:** Proceed to Phase 6 (Production Cutover)
**If No-Go:** Rollback Phase 5

---

## Phase 6: Production Cutover

**Duration:** 1 week (gradual rollout)
**Objective:** Gradually migrate reads from old system to new 6-hub system

---

### Step 6.1: Enable Dual-Write Mode

**Code Change:** `src/apex_memory/services/entity_service.py`

```python
import os

DUAL_WRITE_ENABLED = os.getenv("DUAL_WRITE_ENABLED", "true").lower() == "true"
NEW_SYSTEM_READ_PERCENTAGE = int(os.getenv("NEW_SYSTEM_READ_PERCENTAGE", "0"))

class EntityService:
    def create_tractor(self, tractor_data):
        """Create tractor in both old and new systems"""

        # Write to old system (always)
        old_tractor_id = self.old_db.create_truck(tractor_data)

        # Write to new system (if dual-write enabled)
        if DUAL_WRITE_ENABLED:
            try:
                new_tractor_id = self.new_db.create_tractor(tractor_data)

                # Validate writes match
                if not self._validate_tractor_consistency(old_tractor_id, new_tractor_id):
                    logger.error(f"Inconsistency detected: old={old_tractor_id}, new={new_tractor_id}")
                    # Optionally raise alert
            except Exception as e:
                logger.error(f"Dual-write to new system failed: {e}")
                # Don't fail the request - old system is PRIMARY

        return old_tractor_id

    def get_tractor(self, unit_number):
        """Get tractor from old or new system based on canary percentage"""

        # Determine which system to read from
        import random
        use_new_system = random.randint(0, 99) < NEW_SYSTEM_READ_PERCENTAGE

        if use_new_system:
            try:
                tractor = self.new_db.get_tractor(unit_number)
                logger.info(f"Read from NEW system: {unit_number}")
                return tractor
            except Exception as e:
                logger.error(f"New system read failed: {e}, falling back to old")
                # Fallback to old system

        # Read from old system
        tractor = self.old_db.get_truck(unit_number)
        logger.info(f"Read from OLD system: {unit_number}")
        return tractor
```

**Environment Configuration:**
```bash
# Week 1: 10% canary
export DUAL_WRITE_ENABLED=true
export NEW_SYSTEM_READ_PERCENTAGE=10

# Week 2: 50% split
export NEW_SYSTEM_READ_PERCENTAGE=50

# Week 3: 90% new system
export NEW_SYSTEM_READ_PERCENTAGE=90

# Week 4: 100% new system
export NEW_SYSTEM_READ_PERCENTAGE=100
```

---

### Step 6.2: Week 1 - 10% Canary

**Objective:** Route 10% of reads to new system, monitor for issues

**Monitoring Checklist:**
- [ ] Query latency (P50, P90, P99) - should be <1s
- [ ] Error rate - should be <0.1%
- [ ] Data consistency - old vs new system should match 100%
- [ ] Cache hit rate - should be >70%
- [ ] Database CPU/memory - should be <80%

**Daily Validation:**
```bash
# Run data consistency checks
python scripts/migration/phase6_validate_consistency.py

# Expected output:
# ✅ Tractor data: 100% consistent (0 mismatches out of 1,250 reads)
# ✅ Load data: 100% consistent (0 mismatches out of 3,450 reads)
# ✅ Revenue data: 100% consistent (0 mismatches out of 890 reads)
```

**Rollback Trigger:**
- Error rate >1%
- Query latency P99 >5s
- Data inconsistency >0.1%

---

### Step 6.3: Week 2 - 50% Traffic Split

**Objective:** Route 50% of reads to new system, increase confidence

**Configuration:**
```bash
export NEW_SYSTEM_READ_PERCENTAGE=50
```

**Additional Monitoring:**
- [ ] Compare query patterns (old vs new system)
- [ ] Validate cross-database joins work correctly
- [ ] Check Neo4j relationship query performance
- [ ] Verify Qdrant semantic search accuracy

---

### Step 6.4: Week 3 - 90% New System

**Objective:** Route 90% of reads to new system, old system becomes fallback

**Configuration:**
```bash
export NEW_SYSTEM_READ_PERCENTAGE=90
```

**Validation:**
- [ ] No fallback to old system in 24 hours
- [ ] All validation queries passing
- [ ] Performance within SLA (<1s P90)
- [ ] Zero critical errors

---

### Step 6.5: Week 4 - 100% New System (Cutover Complete)

**Objective:** Route 100% of reads to new system, decommission old system (after backup)

**Configuration:**
```bash
export NEW_SYSTEM_READ_PERCENTAGE=100
export DUAL_WRITE_ENABLED=false  # Stop writing to old system
```

**Final Validation:**
```bash
# Run complete validation suite
python scripts/migration/phase6_final_validation.py

# Expected output:
# ✅ All PostgreSQL validation queries passed (25/25)
# ✅ All Neo4j validation queries passed (10/10)
# ✅ All cross-database sync checks passed (4/4)
# ✅ All temporal queries working (5/5)
# ✅ All automated tests passing (150/150)
# ✅ Performance within SLA (P90: 0.8s, P99: 2.1s)
# ✅ Zero critical errors in 7 days
#
# 🎉 Migration Complete - New 6-hub system is PRIMARY
```

**Decommissioning Old System:**
1. [ ] Create final backup of old system
2. [ ] Archive old system (read-only for 90 days)
3. [ ] Update monitoring dashboards (remove old system metrics)
4. [ ] Update documentation
5. [ ] Schedule old system shutdown (after 90-day archive period)

---

## Rollback Procedures

### Rollback Triggers

**Automatic Rollback Triggers:**
- Error rate >5% for 10 minutes
- Query latency P99 >10s for 10 minutes
- Database disk >95% full
- Data corruption detected

**Manual Rollback Triggers:**
- Critical bug discovered
- Data inconsistency >1%
- Performance degradation unresolved for 4 hours
- Go/No-Go decision: NO-GO

---

### Phase 1 Rollback: PostgreSQL Foundation

**Impact:** Low (no production traffic yet)

**Steps:**
```bash
# 1. Drop all tables
psql -U apex -d apex_memory -c "DROP SCHEMA hub1_command CASCADE;"
psql -U apex -d apex_memory -c "DROP SCHEMA hub2_openhaul CASCADE;"
psql -U apex -d apex_memory -c "DROP SCHEMA hub3_origin CASCADE;"
psql -U apex -d apex_memory -c "DROP SCHEMA hub4_contacts CASCADE;"
psql -U apex -d apex_memory -c "DROP SCHEMA hub5_financials CASCADE;"
psql -U apex -d apex_memory -c "DROP SCHEMA hub6_corporate CASCADE;"

# 2. Drop extensions (if no longer needed)
psql -U apex -d apex_memory -c "DROP EXTENSION IF EXISTS postgis CASCADE;"

# 3. Restore from backup (if needed)
psql -U apex -d apex_memory < backup/pre_phase1_backup.sql

echo "✅ Phase 1 rolled back"
```

**Validation:**
```bash
# Verify old system still operational
psql -U apex -d apex_memory -c "SELECT COUNT(*) FROM trucks;"
# Should return correct count
```

---

### Phase 2 Rollback: Neo4j Relationships

**Impact:** Low (no production traffic yet)

**Steps:**
```cypher
// 1. Delete all nodes and relationships
MATCH (n)
DETACH DELETE n;

// 2. Drop all constraints
SHOW CONSTRAINTS;
// Manually drop each constraint
DROP CONSTRAINT constraint_tractor_unit IF EXISTS;
// Repeat for all 45 constraints

// 3. Verify clean state
MATCH (n)
RETURN count(n) as node_count;
// Should return 0
```

---

### Phase 3 Rollback: Qdrant Semantic Search

**Impact:** Low (no production traffic yet)

**Steps:**
```python
from qdrant_client import QdrantClient

client = QdrantClient(host="localhost", port=6333)

# 1. Delete all collections
client.delete_collection("documents")
client.delete_collection("knowledge_items")
client.delete_collection("insights")

# 2. Verify clean state
collections = client.get_collections()
print(f"Collections: {len(collections.collections)}")  # Should be 0
```

---

### Phase 4 Rollback: Redis Cache Layer

**Impact:** Low (cache miss just reads from old system)

**Steps:**
```bash
# 1. Flush all Redis keys
redis-cli FLUSHALL

# 2. Reset configuration
redis-cli CONFIG SET maxmemory-policy noeviction

echo "✅ Phase 4 rolled back"
```

---

### Phase 5 Rollback: Graphiti Temporal Tracking

**Impact:** Low (temporal queries can fall back to PostgreSQL)

**Steps:**
```python
from graphiti_core import Graphiti

graphiti = Graphiti(
    neo4j_uri="bolt://localhost:7687",
    neo4j_user="neo4j",
    neo4j_password="apexmemory2024"
)

# 1. Unregister all entity types
graphiti.unregister_all_entity_types()

# 2. Delete timeline data
graphiti.delete_all_timeline_data()

print("✅ Phase 5 rolled back")
```

---

### Phase 6 Rollback: Production Cutover

**Impact:** HIGH (production traffic affected)

**Emergency Rollback (within minutes):**

```bash
# 1. Immediately disable new system reads
export NEW_SYSTEM_READ_PERCENTAGE=0

# 2. Restart application to pick up environment change
kubectl rollout restart deployment/apex-memory-api
# OR
systemctl restart apex-memory-api

# 3. Verify old system is serving 100% of traffic
curl http://localhost:8000/health/system-status
# Should show: "primary_system": "old"

echo "✅ Emergency rollback complete - old system is PRIMARY"
```

**Validation:**
```bash
# Monitor for 15 minutes
watch -n 30 'curl -s http://localhost:8000/metrics | grep system_read_percentage'
# Should show: system_read_percentage{system="old"} 100.0

# Check error rate
curl -s http://localhost:8000/metrics | grep error_rate
# Should be <0.1%
```

**Planned Rollback (with analysis):**

1. [ ] Disable new system reads (set to 0%)
2. [ ] Wait 24 hours to verify stability
3. [ ] Analyze root cause of rollback
4. [ ] Create fix plan with timeline
5. [ ] Re-attempt migration after fixes

---

## Testing & Validation

### Pre-Migration Testing (Staging Environment)

**Duration:** 1 week before production migration

**Test Scenarios:**
1. **Data Consistency Test**
   - Migrate staging database
   - Run all validation queries
   - Compare old vs new system results (should be 100% match)

2. **Performance Test**
   - Simulate production load (10,000 requests/minute)
   - Measure query latency (P50, P90, P99)
   - Target: P90 <1s, P99 <2s

3. **Failover Test**
   - Simulate database failures
   - Verify graceful degradation
   - Verify automatic recovery

4. **Rollback Test**
   - Execute rollback procedures for each phase
   - Verify old system restores correctly
   - Measure rollback time (target: <5 minutes)

---

### Post-Migration Validation

**Daily (First 30 Days):**
- [ ] Run data consistency checks (old vs new)
- [ ] Review error logs for anomalies
- [ ] Check query performance metrics
- [ ] Verify backup jobs successful

**Weekly (First 90 Days):**
- [ ] Review monitoring dashboards
- [ ] Analyze cache hit rates
- [ ] Check database disk growth
- [ ] Review slow query logs

**Monthly (First Year):**
- [ ] Review system capacity
- [ ] Optimize indexes based on query patterns
- [ ] Update documentation with learnings
- [ ] Plan for old system decommissioning

---

## Production Timeline

### Complete Migration Timeline (6 Weeks)

| Week | Phase | Activities | Risk | Go/No-Go Gate |
|------|-------|------------|------|---------------|
| **Week 1** | Phase 1: PostgreSQL | Schema creation, data load, validation | Low | All tables created, data loaded, 0 critical validation issues |
| **Week 2** | Phase 2: Neo4j | Node/relationship creation, sync validation | Medium | Node counts match PostgreSQL, relationships valid, temporal queries working |
| **Week 3** | Phase 3: Qdrant | Collection creation, embedding generation | Low | Collections created, embeddings loaded, semantic search working |
| **Week 4** | Phase 4-5: Redis + Graphiti | Cache setup, temporal tracking | Low | Cache populated, temporal queries validated |
| **Week 5** | Phase 6 (Week 1-2): 10% → 50% canary | Gradual read migration | Medium | Error rate <0.1%, consistency 100%, latency <1s P90 |
| **Week 6** | Phase 6 (Week 3-4): 90% → 100% | Complete cutover | High | 7 days at 100% with zero critical errors |

**Total Duration:** 6 weeks from start to complete cutover

---

### Detailed Day-by-Day Schedule (Week 1 Example)

| Day | Activities | Duration | Owner |
|-----|------------|----------|-------|
| **Mon** | Phase 1.1-1.2: Database + schemas | 4 hours | DBA |
| **Tue** | Phase 1.3: Create tables (Hub 1-3) | 6 hours | DBA |
| **Wed** | Phase 1.3: Create tables (Hub 4-6) | 6 hours | DBA |
| **Thu** | Phase 1.4: Data transformation + load | 8 hours | Backend Engineer |
| **Fri** | Phase 1.5: Validation + Go/No-Go | 4 hours | QA + Team Lead |

**Buffer:** 10 hours for unexpected issues

---

## Risk Mitigation

### High-Risk Areas

**Risk 1: Data Inconsistency During Dual-Write**

**Mitigation:**
- Real-time consistency monitoring (alert on >0.1% mismatch)
- Automatic reconciliation jobs (hourly)
- Write ordering guarantees (old system first, then new system)

**Risk 2: Performance Degradation**

**Mitigation:**
- Gradual rollout (10% → 50% → 90% → 100%)
- Automatic rollback on P99 latency >5s
- Query optimization before cutover
- Database connection pooling tuned

**Risk 3: Downtime During Cutover**

**Mitigation:**
- Zero-downtime strategy (dual-write period)
- Canary deployments
- Instant rollback capability (<5 minutes)

**Risk 4: Data Loss**

**Mitigation:**
- Hourly incremental backups during migration
- Point-in-time recovery enabled
- 90-day archive of old system
- Transaction logs retained

---

## Summary

This migration guide provides a comprehensive 6-phase strategy for deploying the 6-hub unified memory system:

- ✅ **Phase 1: PostgreSQL Foundation** (1 week) - 45 entities, 1,086 properties
- ✅ **Phase 2: Neo4j Relationships** (1 week) - 150+ relationship types
- ✅ **Phase 3: Qdrant Semantic Search** (1 week) - 3 collections, embeddings
- ✅ **Phase 4: Redis Cache Layer** (3 days) - Real-time data caching
- ✅ **Phase 5: Graphiti Temporal Tracking** (4 days) - 16 entity types
- ✅ **Phase 6: Production Cutover** (1 week) - Gradual read migration

**Key Success Factors:**
- Zero downtime during migration
- Safe rollback at any phase
- Comprehensive validation at each step
- Gradual traffic migration (10% → 100%)
- Complete monitoring and alerting

**Expected Outcome:** Production-ready 6-hub system with 100% data consistency, <1s query latency, and zero critical errors.

---

**Next Steps:** Execute Phase 1 (PostgreSQL Foundation) and proceed phase-by-phase with Go/No-Go gates.
