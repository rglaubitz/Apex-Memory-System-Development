#!/usr/bin/env python3
"""
Phase 4: Redis Cache - Step 1: Configure Redis
Purpose: Configure Redis for Apex Memory System caching
Run after: Phase 1-3 setup

Usage:
    python 01_configure_redis.py --dry-run
    python 01_configure_redis.py --execute
"""

import os
import sys
import logging
import redis
from typing import Dict, List, Any, Optional
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

# Redis configuration
REDIS_CONFIG = {
    'host': os.getenv('REDIS_HOST', 'localhost'),
    'port': int(os.getenv('REDIS_PORT', '6379')),
    'db': int(os.getenv('REDIS_DB', '0')),
    'password': os.getenv('REDIS_PASSWORD', None),
    'decode_responses': True
}

# Cache configuration
CACHE_CONFIG = {
    'query_results': {
        'prefix': 'apex:query:',
        'ttl': 3600,  # 1 hour
        'description': 'Cached query results for repeat queries'
    },
    'embeddings': {
        'prefix': 'apex:embedding:',
        'ttl': 86400,  # 24 hours
        'description': 'Cached embeddings for common texts'
    },
    'entity_cache': {
        'prefix': 'apex:entity:',
        'ttl': 1800,  # 30 minutes
        'description': 'Cached entity data for quick lookups'
    },
    'graph_patterns': {
        'prefix': 'apex:pattern:',
        'ttl': 7200,  # 2 hours
        'description': 'Cached graph patterns and traversals'
    }
}


class RedisConfigurator:
    """Configure Redis for Apex Memory System"""

    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.client = None
        self.stats = {
            'configured': 0,
            'errors': 0
        }

    def connect(self):
        """Connect to Redis"""
        try:
            self.client = redis.Redis(**REDIS_CONFIG)

            # Test connection
            self.client.ping()

            info = self.client.info()
            logger.info(f"✅ Connected to Redis: {REDIS_CONFIG['host']}:{REDIS_CONFIG['port']}")
            logger.info(f"📊 Redis version: {info['redis_version']}")
            logger.info(f"📊 Used memory: {info['used_memory_human']}")
            logger.info(f"📊 Connected clients: {info['connected_clients']}")

        except Exception as e:
            logger.error(f"❌ Connection failed: {e}")
            sys.exit(1)

    def disconnect(self):
        """Close Redis connection"""
        if self.client:
            self.client.close()

    def configure_cache_namespaces(self):
        """Set up cache namespace configuration"""
        logger.info("🔄 Configuring cache namespaces...")

        config_key = "apex:config:cache_namespaces"

        if not self.dry_run:
            try:
                # Store cache configuration
                self.client.set(
                    config_key,
                    json.dumps(CACHE_CONFIG),
                    ex=None  # No expiration for config
                )

                logger.info(f"✅ Configured {len(CACHE_CONFIG)} cache namespaces")
                for namespace, config in CACHE_CONFIG.items():
                    logger.info(f"   {namespace}: {config['description']} (TTL: {config['ttl']}s)")

                self.stats['configured'] += 1

            except Exception as e:
                logger.error(f"❌ Error configuring namespaces: {e}")
                self.stats['errors'] += 1
        else:
            logger.info(f"🔍 DRY RUN: Would configure {len(CACHE_CONFIG)} cache namespaces")
            self.stats['configured'] = len(CACHE_CONFIG)

    def set_memory_policy(self):
        """Configure Redis memory policy"""
        logger.info("🔄 Configuring memory policy...")

        if not self.dry_run:
            try:
                # Set maxmemory policy to LRU (Least Recently Used)
                # This ensures old cache entries are evicted when memory is full
                self.client.config_set('maxmemory-policy', 'allkeys-lru')

                # Set maxmemory (example: 1GB)
                # Adjust based on your server capacity
                max_memory = os.getenv('REDIS_MAX_MEMORY', '1gb')
                self.client.config_set('maxmemory', max_memory)

                logger.info(f"✅ Memory policy: allkeys-lru")
                logger.info(f"✅ Max memory: {max_memory}")
                self.stats['configured'] += 1

            except Exception as e:
                logger.error(f"❌ Error setting memory policy: {e}")
                self.stats['errors'] += 1
        else:
            logger.info("🔍 DRY RUN: Would configure memory policy (allkeys-lru)")

    def create_indexes(self):
        """Create RediSearch indexes for advanced querying"""
        logger.info("🔄 Creating RediSearch indexes...")

        if not self.dry_run:
            try:
                # Check if RediSearch module is loaded
                modules = self.client.module_list()
                has_search = any('search' in str(module).lower() for module in modules)

                if has_search:
                    logger.info("✅ RediSearch module detected")
                    # In production, create FT.CREATE indexes here
                    # Example: self.client.execute_command('FT.CREATE', 'idx:queries', ...)
                else:
                    logger.warning("⚠️  RediSearch module not loaded - skipping index creation")
                    logger.info("   (Basic key-value caching will still work)")

            except Exception as e:
                logger.warning(f"⚠️  Error checking for RediSearch: {e}")
        else:
            logger.info("🔍 DRY RUN: Would create RediSearch indexes (if module available)")

    def populate_warm_cache(self):
        """Pre-populate cache with frequently accessed data"""
        logger.info("🔄 Pre-populating warm cache...")

        if not self.dry_run:
            try:
                # Example: Cache common entity types
                common_entities = {
                    'entity_types': ['tractor', 'driver', 'trailer', 'load', 'company'],
                    'statuses': ['active', 'inactive', 'maintenance', 'available'],
                    'hubs': ['hub1_command', 'hub2_openhaul', 'hub3_origin',
                            'hub4_contacts', 'hub5_financials', 'hub6_corporate']
                }

                for key, values in common_entities.items():
                    cache_key = f"apex:config:{key}"
                    self.client.set(cache_key, json.dumps(values), ex=None)
                    logger.info(f"   Cached {key}: {len(values)} items")

                self.stats['configured'] += len(common_entities)
                logger.info(f"✅ Pre-populated warm cache with {len(common_entities)} config items")

            except Exception as e:
                logger.error(f"❌ Error populating warm cache: {e}")
                self.stats['errors'] += 1
        else:
            logger.info("🔍 DRY RUN: Would pre-populate warm cache")

    def verify_configuration(self):
        """Verify Redis configuration"""
        logger.info("\n" + "="*60)
        logger.info("REDIS CONFIGURATION VERIFICATION")
        logger.info("="*60)

        try:
            # Check connection
            self.client.ping()
            logger.info("✅ Connection: OK")

            # Check memory policy
            policy = self.client.config_get('maxmemory-policy')
            max_mem = self.client.config_get('maxmemory')
            logger.info(f"✅ Memory policy: {policy.get('maxmemory-policy', 'N/A')}")
            logger.info(f"✅ Max memory: {max_mem.get('maxmemory', 'N/A')}")

            # Check configured keys
            config_keys = self.client.keys('apex:config:*')
            logger.info(f"✅ Configuration keys: {len(config_keys)}")

            # Check Redis info
            info = self.client.info()
            logger.info(f"📊 Used memory: {info['used_memory_human']}")
            logger.info(f"📊 Total keys: {info['db0']['keys'] if 'db0' in info else 0}")

        except Exception as e:
            logger.error(f"❌ Verification failed: {e}")

        logger.info("="*60)

    def print_stats(self):
        """Print configuration statistics"""
        logger.info("\n" + "="*60)
        logger.info("CONFIGURATION STATISTICS")
        logger.info("="*60)
        logger.info(f"Configured: {self.stats['configured']}")
        logger.info(f"Errors:     {self.stats['errors']}")
        logger.info("="*60)


def main():
    """Main execution"""
    parser = argparse.ArgumentParser(description='Configure Redis for Apex Memory System')
    parser.add_argument('--dry-run', action='store_true',
                        help='Preview configuration without writing to Redis')
    parser.add_argument('--execute', action='store_true',
                        help='Execute configuration and write to Redis')
    parser.add_argument('--verify', action='store_true',
                        help='Verify Redis configuration')

    args = parser.parse_args()

    if not args.dry_run and not args.execute and not args.verify:
        logger.error("❌ Must specify either --dry-run, --execute, or --verify")
        sys.exit(1)

    dry_run = args.dry_run

    logger.info("="*60)
    logger.info("REDIS CONFIGURATION")
    logger.info(f"Mode: {'DRY RUN' if dry_run else 'EXECUTE' if args.execute else 'VERIFY'}")
    logger.info("="*60)

    configurator = RedisConfigurator(dry_run=dry_run)

    try:
        configurator.connect()

        if args.verify:
            configurator.verify_configuration()
        else:
            configurator.configure_cache_namespaces()
            configurator.set_memory_policy()
            configurator.create_indexes()
            configurator.populate_warm_cache()
            configurator.print_stats()

        if dry_run:
            logger.info("\n✅ Dry run complete - no configuration was written")
        elif args.execute:
            logger.info("\n✅ Configuration complete - Redis configured successfully")

    except Exception as e:
        logger.error(f"❌ Configuration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    finally:
        configurator.disconnect()


if __name__ == "__main__":
    main()
