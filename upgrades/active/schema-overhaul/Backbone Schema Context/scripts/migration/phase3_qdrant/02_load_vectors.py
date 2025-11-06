#!/usr/bin/env python3
"""
Phase 3: Qdrant Vector Database - Step 2: Load Vectors from PostgreSQL
Purpose: Load document and entity embeddings from PostgreSQL to Qdrant
Run after: 01_create_collections.py

Usage:
    python 02_load_vectors.py --collection document_chunks --dry-run
    python 02_load_vectors.py --collection document_chunks --execute
    python 02_load_vectors.py --all --execute
"""

import os
import sys
import logging
import psycopg2
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Batch
from typing import Dict, List, Any, Optional
from uuid import uuid4
from dotenv import load_dotenv
import argparse
import json

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

QDRANT_CONFIG = {
    'host': os.getenv('QDRANT_HOST', 'localhost'),
    'port': int(os.getenv('QDRANT_PORT', '6333')),
    'grpc_port': int(os.getenv('QDRANT_GRPC_PORT', '6334')),
}

# Batch size for uploads
BATCH_SIZE = 100


class QdrantVectorLoader:
    """Load vectors from PostgreSQL to Qdrant"""

    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.pg_conn = None
        self.qdrant_client = None
        self.stats = {
            'loaded': 0,
            'skipped': 0,
            'errors': 0
        }

    def connect(self):
        """Connect to PostgreSQL and Qdrant"""
        try:
            # Connect to PostgreSQL
            self.pg_conn = psycopg2.connect(**PG_CONFIG)
            logger.info(f"✅ Connected to PostgreSQL: {PG_CONFIG['database']}")

            # Connect to Qdrant
            self.qdrant_client = QdrantClient(
                host=QDRANT_CONFIG['host'],
                port=QDRANT_CONFIG['port'],
                grpc_port=QDRANT_CONFIG['grpc_port'],
                prefer_grpc=True
            )
            logger.info(f"✅ Connected to Qdrant: {QDRANT_CONFIG['host']}:{QDRANT_CONFIG['port']}")

        except Exception as e:
            logger.error(f"❌ Connection failed: {e}")
            sys.exit(1)

    def disconnect(self):
        """Close connections"""
        if self.pg_conn:
            self.pg_conn.close()
        if self.qdrant_client:
            self.qdrant_client.close()

    def load_document_chunks(self) -> int:
        """Load document chunk embeddings to Qdrant"""
        logger.info("🔄 Loading document chunks...")

        with self.pg_conn.cursor() as pg_cur:
            # Query document chunks with embeddings
            # Note: This assumes a documents table with embeddings
            # Adjust table/column names based on actual schema
            pg_cur.execute("""
                SELECT
                    d.document_id,
                    d.chunk_number,
                    d.content,
                    d.embedding,
                    d.metadata,
                    d.created_at
                FROM documents d
                WHERE d.embedding IS NOT NULL
                ORDER BY d.created_at DESC
            """)

            chunks = pg_cur.fetchall()
            logger.info(f"📊 Found {len(chunks)} document chunks with embeddings in PostgreSQL")

            if not self.dry_run:
                points = []
                for chunk in chunks:
                    try:
                        # Parse embedding (stored as array in PostgreSQL)
                        embedding = chunk[3]  # Already a list from pgvector

                        # Extract metadata
                        metadata = json.loads(chunk[4]) if chunk[4] else {}

                        # Create Qdrant point
                        point = PointStruct(
                            id=str(uuid4()),
                            vector=embedding,
                            payload={
                                'document_id': chunk[0],
                                'chunk_number': chunk[1],
                                'text': chunk[2],
                                'hub_name': metadata.get('hub_name', 'unknown'),
                                'entity_type': metadata.get('entity_type', 'document'),
                                'created_at': chunk[5].isoformat() if chunk[5] else None
                            }
                        )
                        points.append(point)

                        # Upload in batches
                        if len(points) >= BATCH_SIZE:
                            self.qdrant_client.upsert(
                                collection_name='document_chunks',
                                points=points
                            )
                            self.stats['loaded'] += len(points)
                            logger.info(f"📤 Uploaded batch of {len(points)} points")
                            points = []

                    except Exception as e:
                        logger.error(f"❌ Error processing chunk {chunk[0]}: {e}")
                        self.stats['errors'] += 1

                # Upload remaining points
                if points:
                    self.qdrant_client.upsert(
                        collection_name='document_chunks',
                        points=points
                    )
                    self.stats['loaded'] += len(points)
                    logger.info(f"📤 Uploaded final batch of {len(points)} points")

                logger.info(f"✅ Loaded {self.stats['loaded']} document chunks to Qdrant")
            else:
                logger.info(f"🔍 DRY RUN: Would load {len(chunks)} document chunks")
                self.stats['loaded'] = len(chunks)

            return len(chunks)

    def load_entity_embeddings(self) -> int:
        """Load entity embeddings to Qdrant"""
        logger.info("🔄 Loading entity embeddings...")

        with self.pg_conn.cursor() as pg_cur:
            # Query entities with embeddings from multiple hubs
            # This is a simplified example - adjust based on actual schema
            pg_cur.execute("""
                SELECT
                    'tractor' as entity_type,
                    unit_number as entity_id,
                    make || ' ' || model as entity_name,
                    status as property,
                    NULL as embedding,  -- Placeholder: would need to generate
                    created_at
                FROM hub3_origin.tractors
                WHERE valid_to IS NULL

                UNION ALL

                SELECT
                    'driver' as entity_type,
                    driver_id as entity_id,
                    name as entity_name,
                    status as property,
                    NULL as embedding,
                    created_at
                FROM hub3_origin.drivers
                WHERE valid_to IS NULL
            """)

            entities = pg_cur.fetchall()
            logger.info(f"📊 Found {len(entities)} entities in PostgreSQL")

            if not self.dry_run:
                logger.info("⚠️  Entity embeddings require generation - skipping for now")
                logger.info("   (Will be generated during actual migration)")
            else:
                logger.info(f"🔍 DRY RUN: Would process {len(entities)} entities")
                self.stats['loaded'] = len(entities)

            return len(entities)

    def load_collection(self, collection_name: str) -> int:
        """Load specific collection"""
        loaders = {
            'document_chunks': self.load_document_chunks,
            'entity_embeddings': self.load_entity_embeddings,
        }

        if collection_name in loaders:
            return loaders[collection_name]()
        else:
            logger.warning(f"⚠️  Collection '{collection_name}' loader not yet implemented")
            return 0

    def load_all(self):
        """Load all implemented collections"""
        logger.info("🔄 Loading all collections...")
        self.load_document_chunks()
        self.load_entity_embeddings()
        logger.info("✅ All collections loaded")

    def verify_vectors(self):
        """Verify vector counts in Qdrant"""
        logger.info("\n" + "="*60)
        logger.info("VECTOR VERIFICATION")
        logger.info("="*60)

        collections = ['document_chunks', 'entity_embeddings', 'query_cache']

        for collection_name in collections:
            try:
                info = self.qdrant_client.get_collection(collection_name)
                logger.info(f"\n📦 {collection_name}:")
                logger.info(f"   Status: {info.status}")
                logger.info(f"   Vectors: {info.vectors_count}")
                logger.info(f"   Points: {info.points_count}")
            except Exception as e:
                logger.warning(f"⚠️  Collection '{collection_name}' not found: {e}")

        logger.info("="*60)

    def print_stats(self):
        """Print loading statistics"""
        logger.info("\n" + "="*60)
        logger.info("VECTOR LOADING STATISTICS")
        logger.info("="*60)
        logger.info(f"Loaded:  {self.stats['loaded']}")
        logger.info(f"Skipped: {self.stats['skipped']}")
        logger.info(f"Errors:  {self.stats['errors']}")
        logger.info("="*60)


def main():
    """Main execution"""
    parser = argparse.ArgumentParser(description='Load vectors from PostgreSQL to Qdrant')
    parser.add_argument('--collection', type=str,
                        help='Specific collection to load (document_chunks, entity_embeddings)')
    parser.add_argument('--all', action='store_true',
                        help='Load all collections')
    parser.add_argument('--dry-run', action='store_true',
                        help='Preview loading without writing to Qdrant')
    parser.add_argument('--execute', action='store_true',
                        help='Execute loading and write to Qdrant')
    parser.add_argument('--verify', action='store_true',
                        help='Verify vectors in Qdrant')

    args = parser.parse_args()

    if not args.dry_run and not args.execute and not args.verify:
        logger.error("❌ Must specify either --dry-run, --execute, or --verify")
        sys.exit(1)

    if not args.collection and not args.all and not args.verify:
        logger.error("❌ Must specify either --collection, --all, or --verify")
        sys.exit(1)

    dry_run = args.dry_run

    logger.info("="*60)
    logger.info("QDRANT VECTOR LOADING")
    logger.info(f"Mode: {'DRY RUN' if dry_run else 'EXECUTE' if args.execute else 'VERIFY'}")
    logger.info(f"Batch size: {BATCH_SIZE}")
    logger.info("="*60)

    loader = QdrantVectorLoader(dry_run=dry_run)

    try:
        loader.connect()

        if args.verify:
            loader.verify_vectors()
        elif args.all:
            loader.load_all()
            loader.print_stats()
        elif args.collection:
            loader.load_collection(args.collection)
            loader.print_stats()

        if dry_run:
            logger.info("\n✅ Dry run complete - no vectors were loaded")
        elif args.execute:
            logger.info("\n✅ Vector loading complete - data written to Qdrant")

    except Exception as e:
        logger.error(f"❌ Vector loading failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    finally:
        loader.disconnect()


if __name__ == "__main__":
    main()
