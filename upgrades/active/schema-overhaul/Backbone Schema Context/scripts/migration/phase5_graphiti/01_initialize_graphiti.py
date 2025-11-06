#!/usr/bin/env python3
"""
Phase 5: Graphiti Temporal Intelligence - Step 1: Initialize Graphiti
Purpose: Initialize Graphiti for temporal reasoning and pattern detection
Run after: Phase 1-4 setup

Usage:
    python 01_initialize_graphiti.py --dry-run
    python 01_initialize_graphiti.py --execute
"""

import os
import sys
import logging
import psycopg2
from neo4j import GraphDatabase
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
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


class GraphitiInitializer:
    """Initialize Graphiti for temporal intelligence"""

    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.pg_conn = None
        self.neo4j_driver = None
        self.stats = {
            'initialized': 0,
            'errors': 0
        }

    def connect(self):
        """Connect to databases"""
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

    def create_temporal_indexes(self):
        """Create temporal indexes in Neo4j for Graphiti"""
        logger.info("🔄 Creating temporal indexes...")

        if not self.dry_run:
            with self.neo4j_driver.session() as session:
                try:
                    # Create indexes on temporal properties
                    session.run("""
                        CREATE INDEX index_node_valid_from IF NOT EXISTS
                        FOR (n:TemporalEntity) ON (n.valid_from)
                    """)

                    session.run("""
                        CREATE INDEX index_node_valid_to IF NOT EXISTS
                        FOR (n:TemporalEntity) ON (n.valid_to)
                    """)

                    session.run("""
                        CREATE INDEX index_rel_valid_from IF NOT EXISTS
                        FOR ()-[r:TEMPORAL_RELATIONSHIP]-() ON (r.valid_from)
                    """)

                    session.run("""
                        CREATE INDEX index_rel_valid_to IF NOT EXISTS
                        FOR ()-[r:TEMPORAL_RELATIONSHIP]-() ON (r.valid_to)
                    """)

                    logger.info("✅ Created temporal indexes")
                    self.stats['initialized'] += 1

                except Exception as e:
                    logger.error(f"❌ Error creating temporal indexes: {e}")
                    self.stats['errors'] += 1
        else:
            logger.info("🔍 DRY RUN: Would create temporal indexes")

    def register_entity_types(self):
        """Register entity types with Graphiti"""
        logger.info("🔄 Registering entity types...")

        entity_types = {
            'hub1_command': ['G', 'Project', 'Goal', 'Task', 'Insight', 'KnowledgeItem', 'Asset', 'Note'],
            'hub2_openhaul': ['Load', 'Carrier', 'Location', 'Document', 'MarketRate', 'LoadBoard', 'Quote', 'RateHistory'],
            'hub3_origin': ['Tractor', 'Trailer', 'Driver', 'FuelTransaction', 'MaintenanceRecord', 'Incident', 'InsurancePolicy'],
            'hub4_contacts': ['Company', 'Person', 'Contact', 'Address', 'Relationship', 'Interaction', 'Tag'],
            'hub5_financials': ['Expense', 'Revenue', 'Invoice', 'Payment', 'BankAccount', 'Loan', 'IntercompanyTransfer', 'TaxRecord'],
            'hub6_corporate': ['LegalEntity', 'OwnershipRecord', 'License', 'Filing', 'Compliance']
        }

        if not self.dry_run:
            with self.pg_conn.cursor() as cur:
                try:
                    # Create Graphiti configuration table
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS graphiti_config (
                            config_key VARCHAR(255) PRIMARY KEY,
                            config_value JSONB NOT NULL,
                            created_at TIMESTAMPTZ DEFAULT NOW(),
                            updated_at TIMESTAMPTZ DEFAULT NOW()
                        )
                    """)

                    # Store entity type configuration
                    cur.execute("""
                        INSERT INTO graphiti_config (config_key, config_value)
                        VALUES ('entity_types', %s::jsonb)
                        ON CONFLICT (config_key)
                        DO UPDATE SET
                            config_value = EXCLUDED.config_value,
                            updated_at = NOW()
                    """, (str(entity_types).replace("'", '"'),))

                    self.pg_conn.commit()

                    total_entities = sum(len(types) for types in entity_types.values())
                    logger.info(f"✅ Registered {total_entities} entity types across {len(entity_types)} hubs")
                    self.stats['initialized'] += 1

                except Exception as e:
                    logger.error(f"❌ Error registering entity types: {e}")
                    self.stats['errors'] += 1
        else:
            total_entities = sum(len(types) for types in entity_types.values())
            logger.info(f"🔍 DRY RUN: Would register {total_entities} entity types")

    def initialize_temporal_tracking(self):
        """Initialize temporal tracking for existing entities"""
        logger.info("🔄 Initializing temporal tracking...")

        if not self.dry_run:
            with self.neo4j_driver.session() as session:
                try:
                    # Add TemporalEntity label to all tracked nodes
                    tracked_labels = ['Tractor', 'Driver', 'Company', 'Load']

                    for label in tracked_labels:
                        result = session.run(f"""
                            MATCH (n:{label})
                            WHERE n.valid_from IS NOT NULL
                            SET n:TemporalEntity
                            RETURN count(n) as count
                        """)
                        count = result.single()['count']
                        logger.info(f"   {label}: {count} nodes marked as TemporalEntity")

                    logger.info("✅ Initialized temporal tracking")
                    self.stats['initialized'] += 1

                except Exception as e:
                    logger.error(f"❌ Error initializing temporal tracking: {e}")
                    self.stats['errors'] += 1
        else:
            logger.info("🔍 DRY RUN: Would initialize temporal tracking")

    def create_pattern_detection_config(self):
        """Create configuration for pattern detection"""
        logger.info("🔄 Creating pattern detection configuration...")

        patterns = {
            'recurring_maintenance': {
                'description': 'Detect recurring maintenance patterns',
                'entity_type': 'MaintenanceRecord',
                'temporal_window': 90,  # days
                'min_occurrences': 3
            },
            'driver_reassignment': {
                'description': 'Detect frequent driver reassignments',
                'entity_type': 'Driver',
                'temporal_window': 30,
                'min_occurrences': 2
            },
            'load_frequency': {
                'description': 'Detect load frequency patterns by carrier',
                'entity_type': 'Load',
                'temporal_window': 7,
                'min_occurrences': 5
            },
            'expense_spikes': {
                'description': 'Detect unusual expense patterns',
                'entity_type': 'Expense',
                'temporal_window': 30,
                'threshold_multiplier': 2.0
            }
        }

        if not self.dry_run:
            with self.pg_conn.cursor() as cur:
                try:
                    cur.execute("""
                        INSERT INTO graphiti_config (config_key, config_value)
                        VALUES ('pattern_detection', %s::jsonb)
                        ON CONFLICT (config_key)
                        DO UPDATE SET
                            config_value = EXCLUDED.config_value,
                            updated_at = NOW()
                    """, (str(patterns).replace("'", '"'),))

                    self.pg_conn.commit()

                    logger.info(f"✅ Created {len(patterns)} pattern detection configurations")
                    self.stats['initialized'] += 1

                except Exception as e:
                    logger.error(f"❌ Error creating pattern detection config: {e}")
                    self.stats['errors'] += 1
        else:
            logger.info(f"🔍 DRY RUN: Would create {len(patterns)} pattern detection configs")

    def verify_initialization(self):
        """Verify Graphiti initialization"""
        logger.info("\n" + "="*60)
        logger.info("GRAPHITI INITIALIZATION VERIFICATION")
        logger.info("="*60)

        try:
            # Check PostgreSQL config
            with self.pg_conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM graphiti_config")
                config_count = cur.fetchone()[0]
                logger.info(f"✅ PostgreSQL config entries: {config_count}")

            # Check Neo4j temporal indexes
            with self.neo4j_driver.session() as session:
                result = session.run("SHOW INDEXES")
                indexes = [record for record in result]
                temporal_indexes = [idx for idx in indexes if 'temporal' in str(idx).lower() or 'valid' in str(idx).lower()]
                logger.info(f"✅ Neo4j temporal indexes: {len(temporal_indexes)}")

                # Check TemporalEntity nodes
                result = session.run("MATCH (n:TemporalEntity) RETURN count(n) as count")
                count = result.single()['count']
                logger.info(f"✅ TemporalEntity nodes: {count}")

        except Exception as e:
            logger.error(f"❌ Verification failed: {e}")

        logger.info("="*60)

    def print_stats(self):
        """Print initialization statistics"""
        logger.info("\n" + "="*60)
        logger.info("INITIALIZATION STATISTICS")
        logger.info("="*60)
        logger.info(f"Initialized: {self.stats['initialized']}")
        logger.info(f"Errors:      {self.stats['errors']}")
        logger.info("="*60)


def main():
    """Main execution"""
    parser = argparse.ArgumentParser(description='Initialize Graphiti for temporal intelligence')
    parser.add_argument('--dry-run', action='store_true',
                        help='Preview initialization without writing to databases')
    parser.add_argument('--execute', action='store_true',
                        help='Execute initialization and write to databases')
    parser.add_argument('--verify', action='store_true',
                        help='Verify Graphiti initialization')

    args = parser.parse_args()

    if not args.dry_run and not args.execute and not args.verify:
        logger.error("❌ Must specify either --dry-run, --execute, or --verify")
        sys.exit(1)

    dry_run = args.dry_run

    logger.info("="*60)
    logger.info("GRAPHITI INITIALIZATION")
    logger.info(f"Mode: {'DRY RUN' if dry_run else 'EXECUTE' if args.execute else 'VERIFY'}")
    logger.info("="*60)

    initializer = GraphitiInitializer(dry_run=dry_run)

    try:
        initializer.connect()

        if args.verify:
            initializer.verify_initialization()
        else:
            initializer.create_temporal_indexes()
            initializer.register_entity_types()
            initializer.initialize_temporal_tracking()
            initializer.create_pattern_detection_config()
            initializer.print_stats()

        if dry_run:
            logger.info("\n✅ Dry run complete - no initialization was performed")
        elif args.execute:
            logger.info("\n✅ Initialization complete - Graphiti configured successfully")

    except Exception as e:
        logger.error(f"❌ Initialization failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    finally:
        initializer.disconnect()


if __name__ == "__main__":
    main()
