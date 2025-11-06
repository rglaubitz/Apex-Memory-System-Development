#!/usr/bin/env python3
"""
Phase 1: PostgreSQL Foundation - Step 4: Data Transformation and Loading
Purpose: Transform data from old system and load into new 6-hub schema
Run after: 01_create_database.sql, 02_create_schemas.sql, 03_create_tables_hub3.sql

Usage:
    python 04_transform_and_load.py --hub 3 --dry-run
    python 04_transform_and_load.py --hub 3 --execute
"""

import os
import sys
import logging
import psycopg2
from psycopg2.extras import execute_batch
from typing import Dict, List, Tuple, Optional
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
DB_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': os.getenv('POSTGRES_PORT', '5432'),
    'database': os.getenv('POSTGRES_DB', 'apex_memory'),
    'user': os.getenv('POSTGRES_USER', 'apex'),
    'password': os.getenv('POSTGRES_PASSWORD', 'apexmemory2024')
}

class DataTransformer:
    """Transforms data from old schema to new 6-hub schema"""

    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.conn = None
        self.old_conn = None
        self.stats = {
            'transformed': 0,
            'skipped': 0,
            'errors': 0
        }

    def connect(self):
        """Connect to PostgreSQL databases"""
        try:
            # Connect to new database
            self.conn = psycopg2.connect(**DB_CONFIG)
            logger.info(f"✅ Connected to new database: {DB_CONFIG['database']}")

            # Connect to old database (if exists)
            old_db_config = DB_CONFIG.copy()
            old_db_config['database'] = os.getenv('OLD_POSTGRES_DB', 'apex_memory_old')
            try:
                self.old_conn = psycopg2.connect(**old_db_config)
                logger.info(f"✅ Connected to old database: {old_db_config['database']}")
            except psycopg2.OperationalError:
                logger.warning("⚠️  Old database not found - will use sample data instead")
                self.old_conn = None

        except psycopg2.Error as e:
            logger.error(f"❌ Database connection failed: {e}")
            sys.exit(1)

    def disconnect(self):
        """Close database connections"""
        if self.conn:
            self.conn.close()
        if self.old_conn:
            self.old_conn.close()

    def format_unit_number(self, old_id: str) -> str:
        """
        Transform old truck ID to new unit_number format
        Example: "TRUCK-6520" -> "6520"
        """
        if old_id.startswith("TRUCK-"):
            return old_id.replace("TRUCK-", "")
        # If already in correct format, return as-is
        if old_id.isdigit() and len(old_id) == 4:
            return old_id
        # Otherwise, try to extract 4 digits
        import re
        match = re.search(r'\d{4}', old_id)
        if match:
            return match.group()
        # Fallback: pad with zeros
        return old_id.zfill(4)

    def geocode_location(self, location_text: str) -> Optional[Tuple[float, float]]:
        """
        Convert location text to GPS coordinates
        In production, use actual geocoding API (Google Maps, Mapbox, etc.)
        """
        # Simple lookup table for demo
        locations = {
            "Las Vegas, NV": (36.1699, -115.1398),
            "Los Angeles, CA": (34.0522, -118.2437),
            "Phoenix, AZ": (33.4484, -112.0740),
            "Salt Lake City, UT": (40.7608, -111.8910)
        }
        coords = locations.get(location_text)
        if coords:
            return coords
        logger.warning(f"⚠️  Unknown location: {location_text}, using default (0, 0)")
        return (0.0, 0.0)

    def transform_tractors(self) -> int:
        """Transform trucks from old schema to hub3_origin.tractors"""
        logger.info("🔄 Transforming tractors...")

        if not self.old_conn:
            logger.info("📝 No old database - generating sample data")
            return self._generate_sample_tractors()

        with self.old_conn.cursor() as old_cur, self.conn.cursor() as new_cur:
            # Extract from old system
            old_cur.execute("""
                SELECT
                    truck_id, vin, make, model, year, status,
                    current_miles, location,
                    purchase_date, purchase_price, current_value,
                    insurance_policy_number, insurance_provider, insurance_expiry_date,
                    created_at, updated_at
                FROM trucks
                WHERE active = true
            """)

            trucks = old_cur.fetchall()
            logger.info(f"📊 Found {len(trucks)} tractors in old system")

            batch_data = []
            for truck in trucks:
                # Transform data
                unit_number = self.format_unit_number(truck[0])
                location_coords = self.geocode_location(truck[7]) if truck[7] else None

                batch_data.append((
                    unit_number,  # unit_number
                    truck[1],     # vin
                    truck[2],     # make
                    truck[3],     # model
                    truck[4],     # year
                    truck[5],     # status
                    truck[6],     # current_miles
                    f"POINT({location_coords[1]} {location_coords[0]})" if location_coords else None,  # location_gps
                    truck[8],     # purchase_date
                    truck[9],     # purchase_price
                    truck[10],    # current_value
                    truck[11],    # insurance_policy_number
                    truck[12],    # insurance_provider
                    truck[13],    # insurance_expiry_date
                    truck[14],    # created_at
                    truck[15],    # updated_at
                    truck[14]     # valid_from (same as created_at)
                ))

            if not self.dry_run:
                # Batch insert
                execute_batch(new_cur, """
                    INSERT INTO hub3_origin.tractors (
                        unit_number, vin, make, model, year, status,
                        current_miles, location_gps,
                        purchase_date, purchase_price, current_value,
                        insurance_policy_number, insurance_provider, insurance_expiry_date,
                        created_at, updated_at, valid_from
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s,
                        %s, ST_GeogFromText(%s),
                        %s, %s, %s,
                        %s, %s, %s,
                        %s, %s, %s
                    )
                    ON CONFLICT (unit_number) DO NOTHING
                """, batch_data)

                self.conn.commit()
                logger.info(f"✅ Transformed {len(batch_data)} tractors")
            else:
                logger.info(f"🔍 DRY RUN: Would transform {len(batch_data)} tractors")

            self.stats['transformed'] += len(batch_data)
            return len(batch_data)

    def _generate_sample_tractors(self) -> int:
        """Generate sample tractor data for testing"""
        logger.info("📝 Generating sample tractor data...")

        sample_tractors = [
            ('6520', '1XKYDP9X3LJ123456', 'Kenworth', 'T680', 2020, 'active', 450000,
             'POINT(-115.1398 36.1699)', '2020-01-15', 185000, 120000,
             'POL-123456', 'Progressive', '2026-01-15'),
            ('6533', '1XKYDP9X5MJ234567', 'Kenworth', 'T680', 2021, 'active', 380000,
             'POINT(-118.2437 34.0522)', '2021-03-20', 190000, 130000,
             'POL-234567', 'Progressive', '2026-03-20'),
            ('6540', '1XKYDP9X7NJ345678', 'Freightliner', 'Cascadia', 2022, 'active', 250000,
             'POINT(-112.0740 33.4484)', '2022-06-10', 195000, 150000,
             'POL-345678', 'Progressive', '2026-06-10'),
        ]

        if not self.dry_run:
            with self.conn.cursor() as cur:
                for tractor in sample_tractors:
                    cur.execute("""
                        INSERT INTO hub3_origin.tractors (
                            unit_number, vin, make, model, year, status, current_miles,
                            location_gps, purchase_date, purchase_price, current_value,
                            insurance_policy_number, insurance_provider, insurance_expiry_date
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s,
                            ST_GeogFromText(%s), %s, %s, %s,
                            %s, %s, %s
                        )
                        ON CONFLICT (unit_number) DO NOTHING
                    """, tractor)
                self.conn.commit()
            logger.info(f"✅ Generated {len(sample_tractors)} sample tractors")
        else:
            logger.info(f"🔍 DRY RUN: Would generate {len(sample_tractors)} sample tractors")

        self.stats['transformed'] += len(sample_tractors)
        return len(sample_tractors)

    def transform_hub(self, hub_number: int):
        """Transform data for specific hub"""
        if hub_number == 3:
            self.transform_tractors()
            # Add more entity transformations here:
            # self.transform_trailers()
            # self.transform_drivers()
            # etc.
        else:
            logger.warning(f"⚠️  Hub {hub_number} transformation not yet implemented")

    def print_stats(self):
        """Print transformation statistics"""
        logger.info("\n" + "="*60)
        logger.info("TRANSFORMATION STATISTICS")
        logger.info("="*60)
        logger.info(f"Transformed: {self.stats['transformed']}")
        logger.info(f"Skipped:     {self.stats['skipped']}")
        logger.info(f"Errors:      {self.stats['errors']}")
        logger.info("="*60)


def main():
    """Main execution"""
    parser = argparse.ArgumentParser(description='Transform and load data into 6-hub schema')
    parser.add_argument('--hub', type=int, required=True, choices=range(1, 7),
                        help='Hub number to transform (1-6)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Preview transformation without writing to database')
    parser.add_argument('--execute', action='store_true',
                        help='Execute transformation and write to database')

    args = parser.parse_args()

    if not args.dry_run and not args.execute:
        logger.error("❌ Must specify either --dry-run or --execute")
        sys.exit(1)

    dry_run = args.dry_run

    logger.info("="*60)
    logger.info(f"DATA TRANSFORMATION - HUB {args.hub}")
    logger.info(f"Mode: {'DRY RUN' if dry_run else 'EXECUTE'}")
    logger.info("="*60)

    transformer = DataTransformer(dry_run=dry_run)

    try:
        transformer.connect()
        transformer.transform_hub(args.hub)
        transformer.print_stats()

        if dry_run:
            logger.info("\n✅ Dry run complete - no data was written")
        else:
            logger.info("\n✅ Transformation complete - data written to database")

    except Exception as e:
        logger.error(f"❌ Transformation failed: {e}")
        sys.exit(1)

    finally:
        transformer.disconnect()


if __name__ == "__main__":
    main()
