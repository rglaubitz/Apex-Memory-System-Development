#!/usr/bin/env python3
"""
Phase 2: Neo4j Relationships - Step 3: Create Relationships from PostgreSQL
Purpose: Create relationships between nodes based on PostgreSQL foreign keys
Run after: 01_create_constraints.cypher, 02_load_nodes.py

Usage:
    python 03_create_relationships.py --relationship assigned_to --dry-run
    python 03_create_relationships.py --relationship assigned_to --execute
    python 03_create_relationships.py --all --execute
"""

import os
import sys
import logging
import psycopg2
from neo4j import GraphDatabase
from typing import Dict, List, Any, Optional
from datetime import datetime
from dotenv import load_dotenv
import argparse

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database configuration
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

class Neo4jRelationshipCreator:
    """Create relationships in Neo4j from PostgreSQL foreign keys"""

    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.pg_conn = None
        self.neo4j_driver = None
        self.stats = {
            'created': 0,
            'skipped': 0,
            'errors': 0
        }

    def connect(self):
        """Connect to PostgreSQL and Neo4j"""
        try:
            # Connect to PostgreSQL
            self.pg_conn = psycopg2.connect(**PG_CONFIG)
            logger.info(f"✅ Connected to PostgreSQL: {PG_CONFIG['database']}")

            # Connect to Neo4j
            self.neo4j_driver = GraphDatabase.driver(
                NEO4J_CONFIG['uri'],
                auth=(NEO4J_CONFIG['user'], NEO4J_CONFIG['password'])
            )
            logger.info(f"✅ Connected to Neo4j: {NEO4J_CONFIG['uri']}")

        except Exception as e:
            logger.error(f"❌ Connection failed: {e}")
            sys.exit(1)

    def disconnect(self):
        """Close connections"""
        if self.pg_conn:
            self.pg_conn.close()
        if self.neo4j_driver:
            self.neo4j_driver.close()

    def create_driver_assignments(self) -> int:
        """Create ASSIGNED_TO relationships between Driver and Tractor"""
        logger.info("🔄 Creating Driver → Tractor assignments...")

        with self.pg_conn.cursor() as pg_cur:
            # Get all driver assignments (current assignments only)
            pg_cur.execute("""
                SELECT
                    driver_id,
                    current_unit_assignment,
                    hire_date,
                    created_at,
                    valid_from
                FROM hub3_origin.drivers
                WHERE valid_to IS NULL
                AND current_unit_assignment IS NOT NULL
            """)

            assignments = pg_cur.fetchall()
            logger.info(f"📊 Found {len(assignments)} driver assignments in PostgreSQL")

            if not self.dry_run:
                with self.neo4j_driver.session() as session:
                    for assignment in assignments:
                        try:
                            session.run("""
                                MATCH (d:Driver {driver_id: $driver_id})
                                MATCH (t:Tractor {unit_number: $unit_number})
                                MERGE (d)-[r:ASSIGNED_TO]->(t)
                                SET r.assigned_date = date($hire_date),
                                    r.created_at = datetime($created_at),
                                    r.valid_from = datetime($valid_from)
                            """, {
                                "driver_id": assignment[0],
                                "unit_number": assignment[1],
                                "hire_date": str(assignment[2]) if assignment[2] else None,
                                "created_at": assignment[3].isoformat(),
                                "valid_from": assignment[4].isoformat()
                            })
                            self.stats['created'] += 1

                        except Exception as e:
                            logger.error(f"❌ Error creating assignment {assignment[0]} → {assignment[1]}: {e}")
                            self.stats['errors'] += 1

                logger.info(f"✅ Created {self.stats['created']} ASSIGNED_TO relationships")
            else:
                logger.info(f"🔍 DRY RUN: Would create {len(assignments)} ASSIGNED_TO relationships")
                self.stats['created'] = len(assignments)

            return len(assignments)

    def create_fuel_transaction_relationships(self) -> int:
        """Create FOR_UNIT and BY_DRIVER relationships for fuel transactions"""
        logger.info("🔄 Creating FuelTransaction relationships...")

        with self.pg_conn.cursor() as pg_cur:
            pg_cur.execute("""
                SELECT
                    transaction_id,
                    unit_number,
                    driver_id,
                    transaction_date,
                    created_at
                FROM hub3_origin.fuel_transactions
            """)

            transactions = pg_cur.fetchall()
            logger.info(f"📊 Found {len(transactions)} fuel transactions in PostgreSQL")

            if not self.dry_run:
                with self.neo4j_driver.session() as session:
                    for txn in transactions:
                        try:
                            # Create FuelTransaction → Tractor relationship
                            session.run("""
                                MATCH (f:FuelTransaction {transaction_id: $transaction_id})
                                MATCH (t:Tractor {unit_number: $unit_number})
                                MERGE (f)-[r:FOR_UNIT]->(t)
                                SET r.transaction_date = datetime($transaction_date),
                                    r.created_at = datetime($created_at)
                            """, {
                                "transaction_id": str(txn[0]),
                                "unit_number": txn[1],
                                "transaction_date": txn[3].isoformat(),
                                "created_at": txn[4].isoformat()
                            })

                            # Create FuelTransaction → Driver relationship (if driver exists)
                            if txn[2]:
                                session.run("""
                                    MATCH (f:FuelTransaction {transaction_id: $transaction_id})
                                    MATCH (d:Driver {driver_id: $driver_id})
                                    MERGE (f)-[r:BY_DRIVER]->(d)
                                    SET r.transaction_date = datetime($transaction_date),
                                        r.created_at = datetime($created_at)
                                """, {
                                    "transaction_id": str(txn[0]),
                                    "driver_id": txn[2],
                                    "transaction_date": txn[3].isoformat(),
                                    "created_at": txn[4].isoformat()
                                })

                            self.stats['created'] += 2 if txn[2] else 1

                        except Exception as e:
                            logger.error(f"❌ Error creating fuel transaction relationships {txn[0]}: {e}")
                            self.stats['errors'] += 1

                logger.info(f"✅ Created fuel transaction relationships")
            else:
                logger.info(f"🔍 DRY RUN: Would create ~{len(transactions) * 2} fuel transaction relationships")
                self.stats['created'] = len(transactions) * 2

            return len(transactions)

    def create_maintenance_relationships(self) -> int:
        """Create FOR_UNIT relationships for maintenance records"""
        logger.info("🔄 Creating MaintenanceRecord → Tractor relationships...")

        with self.pg_conn.cursor() as pg_cur:
            pg_cur.execute("""
                SELECT
                    maintenance_id,
                    unit_number,
                    maintenance_date,
                    created_at
                FROM hub3_origin.maintenance_records
            """)

            records = pg_cur.fetchall()
            logger.info(f"📊 Found {len(records)} maintenance records in PostgreSQL")

            if not self.dry_run:
                with self.neo4j_driver.session() as session:
                    for record in records:
                        try:
                            session.run("""
                                MATCH (m:MaintenanceRecord {maintenance_id: $maintenance_id})
                                MATCH (t:Tractor {unit_number: $unit_number})
                                MERGE (m)-[r:FOR_UNIT]->(t)
                                SET r.maintenance_date = date($maintenance_date),
                                    r.created_at = datetime($created_at)
                            """, {
                                "maintenance_id": str(record[0]),
                                "unit_number": record[1],
                                "maintenance_date": str(record[2]),
                                "created_at": record[3].isoformat()
                            })
                            self.stats['created'] += 1

                        except Exception as e:
                            logger.error(f"❌ Error creating maintenance relationship {record[0]}: {e}")
                            self.stats['errors'] += 1

                logger.info(f"✅ Created {self.stats['created']} maintenance relationships")
            else:
                logger.info(f"🔍 DRY RUN: Would create {len(records)} maintenance relationships")
                self.stats['created'] = len(records)

            return len(records)

    def create_incident_relationships(self) -> int:
        """Create INVOLVES_UNIT and INVOLVES_DRIVER relationships for incidents"""
        logger.info("🔄 Creating Incident relationships...")

        with self.pg_conn.cursor() as pg_cur:
            pg_cur.execute("""
                SELECT
                    incident_id,
                    unit_number,
                    driver_id,
                    incident_date,
                    created_at
                FROM hub3_origin.incidents
            """)

            incidents = pg_cur.fetchall()
            logger.info(f"📊 Found {len(incidents)} incidents in PostgreSQL")

            if not self.dry_run:
                with self.neo4j_driver.session() as session:
                    for incident in incidents:
                        try:
                            # Create Incident → Tractor relationship (if unit exists)
                            if incident[1]:
                                session.run("""
                                    MATCH (i:Incident {incident_id: $incident_id})
                                    MATCH (t:Tractor {unit_number: $unit_number})
                                    MERGE (i)-[r:INVOLVES_UNIT]->(t)
                                    SET r.incident_date = datetime($incident_date),
                                        r.created_at = datetime($created_at)
                                """, {
                                    "incident_id": str(incident[0]),
                                    "unit_number": incident[1],
                                    "incident_date": incident[3].isoformat(),
                                    "created_at": incident[4].isoformat()
                                })

                            # Create Incident → Driver relationship (if driver exists)
                            if incident[2]:
                                session.run("""
                                    MATCH (i:Incident {incident_id: $incident_id})
                                    MATCH (d:Driver {driver_id: $driver_id})
                                    MERGE (i)-[r:INVOLVES_DRIVER]->(d)
                                    SET r.incident_date = datetime($incident_date),
                                        r.created_at = datetime($created_at)
                                """, {
                                    "incident_id": str(incident[0]),
                                    "driver_id": incident[2],
                                    "incident_date": incident[3].isoformat(),
                                    "created_at": incident[4].isoformat()
                                })

                            rels_created = (1 if incident[1] else 0) + (1 if incident[2] else 0)
                            self.stats['created'] += rels_created

                        except Exception as e:
                            logger.error(f"❌ Error creating incident relationships {incident[0]}: {e}")
                            self.stats['errors'] += 1

                logger.info(f"✅ Created incident relationships")
            else:
                logger.info(f"🔍 DRY RUN: Would create ~{len(incidents) * 2} incident relationships")
                self.stats['created'] = len(incidents) * 2

            return len(incidents)

    def create_relationship(self, relationship_name: str) -> int:
        """Create specific relationship type"""
        relationship_creators = {
            'assigned_to': self.create_driver_assignments,
            'fuel_transactions': self.create_fuel_transaction_relationships,
            'maintenance': self.create_maintenance_relationships,
            'incidents': self.create_incident_relationships,
        }

        if relationship_name in relationship_creators:
            return relationship_creators[relationship_name]()
        else:
            logger.warning(f"⚠️  Relationship '{relationship_name}' creator not yet implemented")
            return 0

    def create_all(self):
        """Create all implemented relationships"""
        logger.info("🔄 Creating all relationships...")
        self.create_driver_assignments()
        self.create_fuel_transaction_relationships()
        self.create_maintenance_relationships()
        self.create_incident_relationships()
        logger.info("✅ All relationships created")

    def verify_relationships(self):
        """Verify relationship counts"""
        logger.info("\n" + "="*60)
        logger.info("RELATIONSHIP VERIFICATION")
        logger.info("="*60)

        with self.neo4j_driver.session() as session:
            # Check ASSIGNED_TO
            result = session.run("MATCH ()-[r:ASSIGNED_TO]->() RETURN count(r) as count")
            count = result.single()["count"]
            logger.info(f"ASSIGNED_TO relationships: {count}")

            # Check FOR_UNIT (fuel + maintenance)
            result = session.run("MATCH ()-[r:FOR_UNIT]->() RETURN count(r) as count")
            count = result.single()["count"]
            logger.info(f"FOR_UNIT relationships: {count}")

            # Check BY_DRIVER
            result = session.run("MATCH ()-[r:BY_DRIVER]->() RETURN count(r) as count")
            count = result.single()["count"]
            logger.info(f"BY_DRIVER relationships: {count}")

            # Check INVOLVES_UNIT
            result = session.run("MATCH ()-[r:INVOLVES_UNIT]->() RETURN count(r) as count")
            count = result.single()["count"]
            logger.info(f"INVOLVES_UNIT relationships: {count}")

            # Check INVOLVES_DRIVER
            result = session.run("MATCH ()-[r:INVOLVES_DRIVER]->() RETURN count(r) as count")
            count = result.single()["count"]
            logger.info(f"INVOLVES_DRIVER relationships: {count}")

        logger.info("="*60)

    def print_stats(self):
        """Print creation statistics"""
        logger.info("\n" + "="*60)
        logger.info("RELATIONSHIP CREATION STATISTICS")
        logger.info("="*60)
        logger.info(f"Created: {self.stats['created']}")
        logger.info(f"Skipped: {self.stats['skipped']}")
        logger.info(f"Errors:  {self.stats['errors']}")
        logger.info("="*60)


def main():
    """Main execution"""
    parser = argparse.ArgumentParser(description='Create relationships in Neo4j from PostgreSQL')
    parser.add_argument('--relationship', type=str,
                        help='Specific relationship to create (e.g., assigned_to, fuel_transactions)')
    parser.add_argument('--all', action='store_true',
                        help='Create all relationships')
    parser.add_argument('--dry-run', action='store_true',
                        help='Preview relationship creation without writing to Neo4j')
    parser.add_argument('--execute', action='store_true',
                        help='Execute relationship creation and write to Neo4j')
    parser.add_argument('--verify', action='store_true',
                        help='Verify relationships in Neo4j')

    args = parser.parse_args()

    if not args.dry_run and not args.execute and not args.verify:
        logger.error("❌ Must specify either --dry-run, --execute, or --verify")
        sys.exit(1)

    if not args.relationship and not args.all and not args.verify:
        logger.error("❌ Must specify either --relationship, --all, or --verify")
        sys.exit(1)

    dry_run = args.dry_run

    logger.info("="*60)
    logger.info("NEO4J RELATIONSHIP CREATION")
    logger.info(f"Mode: {'DRY RUN' if dry_run else 'EXECUTE' if args.execute else 'VERIFY'}")
    logger.info("="*60)

    creator = Neo4jRelationshipCreator(dry_run=dry_run)

    try:
        creator.connect()

        if args.verify:
            creator.verify_relationships()
        elif args.all:
            creator.create_all()
            creator.print_stats()
        elif args.relationship:
            creator.create_relationship(args.relationship)
            creator.print_stats()

        if dry_run:
            logger.info("\n✅ Dry run complete - no relationships were created")
        elif args.execute:
            logger.info("\n✅ Relationship creation complete - data written to Neo4j")

    except Exception as e:
        logger.error(f"❌ Relationship creation failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    finally:
        creator.disconnect()


if __name__ == "__main__":
    main()
