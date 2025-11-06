#!/usr/bin/env python3
"""
Phase 3: Qdrant Vector Database - Step 1: Create Collections
Purpose: Create Qdrant collections for different embedding types
Run after: Phase 1 PostgreSQL setup

Usage:
    python 01_create_collections.py --collection document_chunks --dry-run
    python 01_create_collections.py --collection document_chunks --execute
    python 01_create_collections.py --all --execute
"""

import os
import sys
import logging
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct,
    CollectionInfo, HnswConfigDiff
)
from typing import Dict, List, Any, Optional
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

# Qdrant configuration
QDRANT_CONFIG = {
    'host': os.getenv('QDRANT_HOST', 'localhost'),
    'port': int(os.getenv('QDRANT_PORT', '6333')),
    'grpc_port': int(os.getenv('QDRANT_GRPC_PORT', '6334')),
}

# Collection configurations
# OpenAI text-embedding-3-small: 1536 dimensions
# OpenAI text-embedding-3-large: 3072 dimensions
EMBEDDING_DIMENSION = int(os.getenv('EMBEDDING_DIMENSION', '1536'))

COLLECTIONS = {
    'document_chunks': {
        'description': 'Document chunk embeddings from all 6 hubs',
        'vector_size': EMBEDDING_DIMENSION,
        'distance': Distance.COSINE,
        'hnsw_config': {
            'm': 16,  # Number of edges per node
            'ef_construct': 100,  # Size of the dynamic candidate list
        },
        'payload_schema': {
            'document_id': 'keyword',
            'chunk_number': 'integer',
            'hub_name': 'keyword',
            'entity_type': 'keyword',
            'text': 'text',
            'created_at': 'datetime'
        }
    },
    'entity_embeddings': {
        'description': 'Entity embeddings (tractors, drivers, companies, etc.)',
        'vector_size': EMBEDDING_DIMENSION,
        'distance': Distance.COSINE,
        'hnsw_config': {
            'm': 16,
            'ef_construct': 100,
        },
        'payload_schema': {
            'entity_id': 'keyword',
            'entity_type': 'keyword',
            'hub_name': 'keyword',
            'entity_name': 'text',
            'properties': 'text',
            'created_at': 'datetime'
        }
    },
    'query_cache': {
        'description': 'Cached query embeddings for semantic search',
        'vector_size': EMBEDDING_DIMENSION,
        'distance': Distance.COSINE,
        'hnsw_config': {
            'm': 8,  # Smaller graph for cache
            'ef_construct': 50,
        },
        'payload_schema': {
            'query_text': 'text',
            'query_hash': 'keyword',
            'result_ids': 'keyword',
            'created_at': 'datetime',
            'access_count': 'integer'
        }
    }
}


class QdrantCollectionManager:
    """Manage Qdrant collections for Apex Memory System"""

    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.client = None
        self.stats = {
            'created': 0,
            'skipped': 0,
            'errors': 0
        }

    def connect(self):
        """Connect to Qdrant"""
        try:
            self.client = QdrantClient(
                host=QDRANT_CONFIG['host'],
                port=QDRANT_CONFIG['port'],
                grpc_port=QDRANT_CONFIG['grpc_port'],
                prefer_grpc=True  # Use gRPC for better performance
            )

            # Test connection
            collections = self.client.get_collections()
            logger.info(f"✅ Connected to Qdrant: {QDRANT_CONFIG['host']}:{QDRANT_CONFIG['port']}")
            logger.info(f"📊 Found {len(collections.collections)} existing collections")

        except Exception as e:
            logger.error(f"❌ Connection failed: {e}")
            sys.exit(1)

    def disconnect(self):
        """Close Qdrant connection"""
        if self.client:
            self.client.close()

    def create_collection(self, collection_name: str) -> bool:
        """Create a specific collection"""
        if collection_name not in COLLECTIONS:
            logger.error(f"❌ Unknown collection: {collection_name}")
            return False

        config = COLLECTIONS[collection_name]
        logger.info(f"🔄 Creating collection: {collection_name}")
        logger.info(f"   Description: {config['description']}")
        logger.info(f"   Vector size: {config['vector_size']}")
        logger.info(f"   Distance: {config['distance']}")

        if not self.dry_run:
            try:
                # Check if collection already exists
                existing_collections = self.client.get_collections()
                if any(c.name == collection_name for c in existing_collections.collections):
                    logger.info(f"⚠️  Collection '{collection_name}' already exists, skipping")
                    self.stats['skipped'] += 1
                    return True

                # Create collection
                self.client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(
                        size=config['vector_size'],
                        distance=config['distance']
                    ),
                    hnsw_config=HnswConfigDiff(
                        m=config['hnsw_config']['m'],
                        ef_construct=config['hnsw_config']['ef_construct']
                    )
                )

                # Create payload indexes for efficient filtering
                for field_name, field_type in config['payload_schema'].items():
                    self.client.create_payload_index(
                        collection_name=collection_name,
                        field_name=field_name,
                        field_schema=field_type
                    )

                self.stats['created'] += 1
                logger.info(f"✅ Created collection: {collection_name}")
                return True

            except Exception as e:
                logger.error(f"❌ Error creating collection {collection_name}: {e}")
                self.stats['errors'] += 1
                return False
        else:
            logger.info(f"🔍 DRY RUN: Would create collection {collection_name}")
            self.stats['created'] += 1
            return True

    def create_all_collections(self):
        """Create all defined collections"""
        logger.info("🔄 Creating all collections...")
        for collection_name in COLLECTIONS:
            self.create_collection(collection_name)
        logger.info("✅ All collections created")

    def verify_collections(self):
        """Verify collections exist and show info"""
        logger.info("\n" + "="*60)
        logger.info("COLLECTION VERIFICATION")
        logger.info("="*60)

        try:
            collections_response = self.client.get_collections()
            collections = collections_response.collections

            for collection in collections:
                info = self.client.get_collection(collection.name)
                logger.info(f"\n📦 {collection.name}:")
                logger.info(f"   Status: {info.status}")
                logger.info(f"   Vectors: {info.vectors_count}")
                logger.info(f"   Points: {info.points_count}")
                if hasattr(info.config, 'params'):
                    logger.info(f"   Vector size: {info.config.params.vectors.size}")
                    logger.info(f"   Distance: {info.config.params.vectors.distance}")

            if not collections:
                logger.warning("⚠️  No collections found in Qdrant")

        except Exception as e:
            logger.error(f"❌ Error verifying collections: {e}")

        logger.info("="*60)

    def print_stats(self):
        """Print creation statistics"""
        logger.info("\n" + "="*60)
        logger.info("COLLECTION CREATION STATISTICS")
        logger.info("="*60)
        logger.info(f"Created: {self.stats['created']}")
        logger.info(f"Skipped: {self.stats['skipped']}")
        logger.info(f"Errors:  {self.stats['errors']}")
        logger.info("="*60)


def main():
    """Main execution"""
    parser = argparse.ArgumentParser(description='Create Qdrant collections')
    parser.add_argument('--collection', type=str,
                        help='Specific collection to create (document_chunks, entity_embeddings, query_cache)')
    parser.add_argument('--all', action='store_true',
                        help='Create all collections')
    parser.add_argument('--dry-run', action='store_true',
                        help='Preview collection creation without creating in Qdrant')
    parser.add_argument('--execute', action='store_true',
                        help='Execute collection creation and write to Qdrant')
    parser.add_argument('--verify', action='store_true',
                        help='Verify collections in Qdrant')

    args = parser.parse_args()

    if not args.dry_run and not args.execute and not args.verify:
        logger.error("❌ Must specify either --dry-run, --execute, or --verify")
        sys.exit(1)

    if not args.collection and not args.all and not args.verify:
        logger.error("❌ Must specify either --collection, --all, or --verify")
        sys.exit(1)

    dry_run = args.dry_run

    logger.info("="*60)
    logger.info("QDRANT COLLECTION CREATION")
    logger.info(f"Mode: {'DRY RUN' if dry_run else 'EXECUTE' if args.execute else 'VERIFY'}")
    logger.info(f"Embedding dimension: {EMBEDDING_DIMENSION}")
    logger.info("="*60)

    manager = QdrantCollectionManager(dry_run=dry_run)

    try:
        manager.connect()

        if args.verify:
            manager.verify_collections()
        elif args.all:
            manager.create_all_collections()
            manager.print_stats()
        elif args.collection:
            manager.create_collection(args.collection)
            manager.print_stats()

        if dry_run:
            logger.info("\n✅ Dry run complete - no collections were created")
        elif args.execute:
            logger.info("\n✅ Collection creation complete - collections created in Qdrant")

    except Exception as e:
        logger.error(f"❌ Collection creation failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    finally:
        manager.disconnect()


if __name__ == "__main__":
    main()
