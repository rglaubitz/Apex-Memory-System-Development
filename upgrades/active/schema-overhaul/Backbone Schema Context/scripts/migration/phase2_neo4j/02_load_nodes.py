#!/usr/bin/env python3
"""
Phase 2: Neo4j Relationships - Step 2: Load Nodes from PostgreSQL
Purpose: Sync all current entities from PostgreSQL to Neo4j as nodes
Run after: 01_create_constraints.cypher

Usage:
    python 02_load_nodes.py --entity tractors --dry-run
    python 02_load_nodes.py --entity tractors --execute
    python 02_load_nodes.py --all --execute
"""

import os
import sys
import logging
import psycopg2
from neo4j import GraphDatabase
from typing import Dict, List, Any
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

class Neo4jNodeLoader:
    """Load nodes from PostgreSQL to Neo4j"""

    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.pg_conn = None
        self.neo4j_driver = None
        self.stats = {
            'loaded': 0,
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

    def load_tractors(self) -> int:
        """Load tractors from PostgreSQL to Neo4j"""
        logger.info("🔄 Loading tractors...")

        with self.pg_conn.cursor() as pg_cur:
            # Get all current tractors (valid_to IS NULL)
            pg_cur.execute("""
                SELECT
                    unit_number, vin, make, model, year, status,
                    current_miles, engine_hours,
                    ST_Y(location_gps::geometry) as lat,
                    ST_X(location_gps::geometry) as lon,
                    purchase_date, purchase_price, current_value,
                    financing_status, lender_name, loan_balance,
                    insurance_policy_number, insurance_provider, insurance_expiry_date,
                    created_at, updated_at, valid_from, valid_to
                FROM hub3_origin.tractors
                WHERE valid_to IS NULL
            """)

            tractors = pg_cur.fetchall()
            logger.info(f"📊 Found {len(tractors)} current tractors in PostgreSQL")

            if not self.dry_run:
                with self.neo4j_driver.session() as session:
                    for tractor in tractors:
                        try:
                            session.run("""
                                MERGE (t:Tractor {unit_number: $unit_number})
                                SET t.vin = $vin,
                                    t.make = $make,
                                    t.model = $model,
                                    t.year = $year,
                                    t.status = $status,
                                    t.current_miles = $current_miles,
                                    t.engine_hours = $engine_hours,
                                    t.location_lat = $lat,
                                    t.location_lon = $lon,
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
                                "lat": tractor[8],
                                "lon": tractor[9],
                                "purchase_date": str(tractor[10]) if tractor[10] else None,
                                "purchase_price": float(tractor[11]) if tractor[11] else None,
                                "current_value": float(tractor[12]) if tractor[12] else None,
                                "financing_status": tractor[13],
                                "lender_name": tractor[14],
                                "loan_balance": float(tractor[15]) if tractor[15] else None,
                                "insurance_policy_number": tractor[16],
                                "insurance_provider": tractor[17],
                                "insurance_expiry_date": str(tractor[18]) if tractor[18] else None,
                                "created_at": tractor[19].isoformat(),
                                "updated_at": tractor[20].isoformat(),
                                "valid_from": tractor[21].isoformat(),
                                "valid_to": tractor[22].isoformat() if tractor[22] else None
                            })
                            self.stats['loaded'] += 1

                        except Exception as e:
                            logger.error(f"❌ Error loading tractor {tractor[0]}: {e}")
                            self.stats['errors'] += 1

                logger.info(f"✅ Loaded {self.stats['loaded']} tractors to Neo4j")
            else:
                logger.info(f"🔍 DRY RUN: Would load {len(tractors)} tractors")
                self.stats['loaded'] = len(tractors)

            return len(tractors)

    def load_drivers(self) -> int:
        """Load drivers from PostgreSQL to Neo4j"""
        logger.info("🔄 Loading drivers...")

        with self.pg_conn.cursor() as pg_cur:
            pg_cur.execute("""
                SELECT
                    driver_id, name, cdl_number, cdl_state, cdl_expiry_date,
                    phone, email, status, current_unit_assignment,
                    hire_date, employment_type, pay_rate, pay_type,
                    created_at, updated_at, valid_from, valid_to
                FROM hub3_origin.drivers
                WHERE valid_to IS NULL
            """)

            drivers = pg_cur.fetchall()
            logger.info(f"📊 Found {len(drivers)} current drivers in PostgreSQL")

            if not self.dry_run:
                with self.neo4j_driver.session() as session:
                    for driver in drivers:
                        try:
                            session.run("""
                                MERGE (d:Driver {driver_id: $driver_id})
                                SET d.name = $name,
                                    d.cdl_number = $cdl_number,
                                    d.cdl_state = $cdl_state,
                                    d.cdl_expiry_date = date($cdl_expiry_date),
                                    d.phone = $phone,
                                    d.email = $email,
                                    d.status = $status,
                                    d.current_unit_assignment = $current_unit_assignment,
                                    d.hire_date = date($hire_date),
                                    d.employment_type = $employment_type,
                                    d.pay_rate = $pay_rate,
                                    d.pay_type = $pay_type,
                                    d.created_at = datetime($created_at),
                                    d.updated_at = datetime($updated_at),
                                    d.valid_from = datetime($valid_from),
                                    d.valid_to = datetime($valid_to)
                            """, {
                                "driver_id": driver[0],
                                "name": driver[1],
                                "cdl_number": driver[2],
                                "cdl_state": driver[3],
                                "cdl_expiry_date": str(driver[4]) if driver[4] else None,
                                "phone": driver[5],
                                "email": driver[6],
                                "status": driver[7],
                                "current_unit_assignment": driver[8],
                                "hire_date": str(driver[9]) if driver[9] else None,
                                "employment_type": driver[10],
                                "pay_rate": float(driver[11]) if driver[11] else None,
                                "pay_type": driver[12],
                                "created_at": driver[13].isoformat(),
                                "updated_at": driver[14].isoformat(),
                                "valid_from": driver[15].isoformat(),
                                "valid_to": driver[16].isoformat() if driver[16] else None
                            })
                            self.stats['loaded'] += 1

                        except Exception as e:
                            logger.error(f"❌ Error loading driver {driver[0]}: {e}")
                            self.stats['errors'] += 1

                logger.info(f"✅ Loaded {self.stats['loaded']} drivers to Neo4j")
            else:
                logger.info(f"🔍 DRY RUN: Would load {len(drivers)} drivers")
                self.stats['loaded'] = len(drivers)

            return len(drivers)

    def load_entity(self, entity_name: str) -> int:
        """Load specific entity type"""
        entity_loaders = {
            'tractors': self.load_tractors,
            'drivers': self.load_drivers,
            # Add more entity loaders here:
            # 'trailers': self.load_trailers,
            # 'loads': self.load_loads,
            # etc.
        }

        if entity_name in entity_loaders:
            return entity_loaders[entity_name]()
        else:
            logger.warning(f"⚠️  Entity '{entity_name}' loader not yet implemented")
            return 0

    def load_all(self):
        """Load all implemented entities"""
        logger.info("🔄 Loading all entities...")
        self.load_tractors()
        self.load_drivers()
        # Add more entity loads here
        logger.info("✅ All entities loaded")

    def verify_sync(self):
        """Verify PostgreSQL and Neo4j have matching counts"""
        logger.info("\n" + "="*60)
        logger.info("SYNC VERIFICATION")
        logger.info("="*60)

        with self.pg_conn.cursor() as pg_cur, self.neo4j_driver.session() as neo4j_session:
            # Check tractors
            pg_cur.execute("SELECT COUNT(*) FROM hub3_origin.tractors WHERE valid_to IS NULL")
            pg_count = pg_cur.fetchone()[0]

            neo4j_result = neo4j_session.run("MATCH (t:Tractor) RETURN count(t) as count")
            neo4j_count = neo4j_result.single()["count"]

            logger.info(f"Tractors: PostgreSQL={pg_count}, Neo4j={neo4j_count} {'✅' if pg_count == neo4j_count else '❌'}")

            # Check drivers
            pg_cur.execute("SELECT COUNT(*) FROM hub3_origin.drivers WHERE valid_to IS NULL")
            pg_count = pg_cur.fetchone()[0]

            neo4j_result = neo4j_session.run("MATCH (d:Driver) RETURN count(d) as count")
            neo4j_count = neo4j_result.single()["count"]

            logger.info(f"Drivers: PostgreSQL={pg_count}, Neo4j={neo4j_count} {'✅' if pg_count == neo4j_count else '❌'}")

        logger.info("="*60)

    def print_stats(self):
        """Print loading statistics"""
        logger.info("\n" + "="*60)
        logger.info("LOADING STATISTICS")
        logger.info("="*60)
        logger.info(f"Loaded:  {self.stats['loaded']}")
        logger.info(f"Skipped: {self.stats['skipped']}")
        logger.info(f"Errors:  {self.stats['errors']}")
        logger.info("="*60)


def main():
    """Main execution"""
    parser = argparse.ArgumentParser(description='Load nodes from PostgreSQL to Neo4j')
    parser.add_argument('--entity', type=str,
                        help='Specific entity to load (e.g., tractors, drivers)')
    parser.add_argument('--all', action='store_true',
                        help='Load all entities')
    parser.add_argument('--dry-run', action='store_true',
                        help='Preview loading without writing to Neo4j')
    parser.add_argument('--execute', action='store_true',
                        help='Execute loading and write to Neo4j')
    parser.add_argument('--verify', action='store_true',
                        help='Verify sync between PostgreSQL and Neo4j')

    args = parser.parse_args()

    if not args.dry_run and not args.execute and not args.verify:
        logger.error("❌ Must specify either --dry-run, --execute, or --verify")
        sys.exit(1)

    if not args.entity and not args.all and not args.verify:
        logger.error("❌ Must specify either --entity, --all, or --verify")
        sys.exit(1)

    dry_run = args.dry_run

    logger.info("="*60)
    logger.info("NEO4J NODE LOADING")
    logger.info(f"Mode: {'DRY RUN' if dry_run else 'EXECUTE' if args.execute else 'VERIFY'}")
    logger.info("="*60)

    loader = Neo4jNodeLoader(dry_run=dry_run)

    try:
        loader.connect()

        if args.verify:
            loader.verify_sync()
        elif args.all:
            loader.load_all()
            loader.print_stats()
        elif args.entity:
            loader.load_entity(args.entity)
            loader.print_stats()

        if dry_run:
            logger.info("\n✅ Dry run complete - no data was written")
        elif args.execute:
            logger.info("\n✅ Loading complete - data written to Neo4j")

    except Exception as e:
        logger.error(f"❌ Loading failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    finally:
        loader.disconnect()


if __name__ == "__main__":
    main()
