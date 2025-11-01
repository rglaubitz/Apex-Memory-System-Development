"""
Neo4j Migration Manager - Custom Alembic-Style Migration System

Source: neo4j-research.md (Section 3.1 Migration Strategies)
Verified: November 2025

This implementation provides versioned schema migrations for Neo4j,
similar to PostgreSQL's Alembic. Neo4j has no built-in migration system,
so we implement a custom solution with version tracking.

Usage:
    # Apply all pending migrations
    python neo4j-migration-manager.py upgrade

    # Rollback to previous version
    python neo4j-migration-manager.py downgrade

    # Check current version
    python neo4j-migration-manager.py current

    # Create new migration
    python neo4j-migration-manager.py create "add customer indices"
"""

import os
import re
from datetime import datetime
from typing import Optional
from neo4j import GraphDatabase


class Neo4jMigrationManager:
    """
    Custom migration manager for Neo4j schemas.

    Tracks migration versions using a special :SchemaVersion node.
    Migrations are Cypher scripts in migrations/neo4j/ directory.
    """

    def __init__(self, uri: str, user: str, password: str, migrations_dir: str = "migrations/neo4j"):
        """
        Initialize migration manager.

        Args:
            uri: Neo4j connection URI (bolt://localhost:7687)
            user: Neo4j username
            password: Neo4j password
            migrations_dir: Path to migrations directory
        """
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.migrations_dir = migrations_dir

        # Ensure migrations directory exists
        os.makedirs(migrations_dir, exist_ok=True)

        # Initialize schema version tracking
        self._init_schema_version()

    def _init_schema_version(self):
        """Create :SchemaVersion node if it doesn't exist."""
        with self.driver.session() as session:
            session.run("""
                MERGE (v:SchemaVersionTracker {id: 'singleton'})
                ON CREATE SET v.created_at = datetime()
            """)

    def get_current_version(self) -> int:
        """
        Get current schema version from Neo4j.

        Returns:
            Current version number (0 if no migrations applied)
        """
        with self.driver.session() as session:
            result = session.run("""
                MATCH (v:SchemaVersion)
                RETURN v.version AS version
                ORDER BY v.applied_at DESC
                LIMIT 1
            """)
            record = result.single()
            return record["version"] if record else 0

    def get_pending_migrations(self) -> list[tuple[int, str]]:
        """
        Get list of pending migrations that haven't been applied.

        Returns:
            List of (version, filename) tuples
        """
        current_version = self.get_current_version()

        # Find all migration files
        files = sorted([
            f for f in os.listdir(self.migrations_dir)
            if f.endswith('.cypher') and f.startswith('V')
        ])

        # Filter to only pending migrations
        pending = []
        for file in files:
            # Extract version number (V001 -> 1)
            match = re.match(r'V(\d+)__.*\.cypher', file)
            if match:
                version = int(match.group(1))
                if version > current_version:
                    pending.append((version, file))

        return pending

    def run_migration(self, version: int, script_path: str):
        """
        Execute a single migration script.

        Args:
            version: Migration version number
            script_path: Path to migration script
        """
        print(f"Running migration V{version:03d}...")

        # Read migration script
        with open(script_path, 'r') as f:
            cypher = f.read()

        # Execute in transaction
        with self.driver.session() as session:
            with session.begin_transaction() as tx:
                try:
                    # Run migration statements
                    # Split on semicolons to handle multiple statements
                    statements = [s.strip() for s in cypher.split(';') if s.strip()]

                    for statement in statements:
                        tx.run(statement)

                    # Record version
                    tx.run("""
                        CREATE (v:SchemaVersion {
                            version: $version,
                            script: $script,
                            applied_at: datetime()
                        })
                    """, version=version, script=os.path.basename(script_path))

                    tx.commit()
                    print(f"✅ Migration V{version:03d} complete")

                except Exception as e:
                    tx.rollback()
                    print(f"❌ Migration V{version:03d} failed: {e}")
                    raise

    def upgrade(self, target_version: Optional[int] = None):
        """
        Apply all pending migrations up to target version.

        Args:
            target_version: Optional target version (None = apply all)
        """
        pending = self.get_pending_migrations()

        if not pending:
            print("No pending migrations")
            return

        # Filter by target version if specified
        if target_version:
            pending = [(v, f) for v, f in pending if v <= target_version]

        print(f"Found {len(pending)} pending migration(s)")

        for version, filename in pending:
            script_path = os.path.join(self.migrations_dir, filename)
            self.run_migration(version, script_path)

        print(f"✅ All migrations complete - now at version {self.get_current_version()}")

    def rollback(self, target_version: int):
        """
        Rollback to specific version using undo scripts.

        Args:
            target_version: Version to rollback to
        """
        current_version = self.get_current_version()

        if target_version >= current_version:
            print("Target version is current or higher. No rollback needed.")
            return

        # Find rollback scripts (U for "undo")
        files = sorted([
            f for f in os.listdir(self.migrations_dir)
            if f.endswith('.cypher') and f.startswith('U')
        ], reverse=True)

        print(f"Rolling back from V{current_version} to V{target_version}")

        with self.driver.session() as session:
            for file in files:
                # Extract version (U003 -> 3)
                match = re.match(r'U(\d+)__.*\.cypher', file)
                if match:
                    version = int(match.group(1))

                    if version > target_version and version <= current_version:
                        print(f"Rolling back V{version:03d}...")

                        # Execute rollback script
                        script_path = os.path.join(self.migrations_dir, file)
                        with open(script_path, 'r') as f:
                            cypher = f.read()

                        session.run(cypher)

                        # Remove version record
                        session.run("""
                            MATCH (v:SchemaVersion {version: $version})
                            DELETE v
                        """, version=version)

                        print(f"✅ Rollback V{version:03d} complete")

        print(f"✅ Rollback complete - now at version {self.get_current_version()}")

    def create_migration(self, description: str) -> str:
        """
        Create a new migration file with version number and description.

        Args:
            description: Migration description (e.g., "add customer indices")

        Returns:
            Path to created migration file
        """
        current_version = self.get_current_version()
        next_version = current_version + 1

        # Create filename
        # V001__add_customer_indices.cypher
        safe_description = description.lower().replace(' ', '_')
        filename = f"V{next_version:03d}__{safe_description}.cypher"
        filepath = os.path.join(self.migrations_dir, filename)

        # Create template migration file
        template = f"""// Migration V{next_version:03d}: {description}
// Created: {datetime.now().isoformat()}

// ============================================
// CONSTRAINTS
// ============================================

// Add your constraints here
// Example:
// CREATE CONSTRAINT entity_uuid_unique IF NOT EXISTS
// FOR (e:Entity) REQUIRE e.uuid IS UNIQUE;

// ============================================
// INDEXES
// ============================================

// Add your indexes here
// Example:
// CREATE INDEX entity_name_idx IF NOT EXISTS
// FOR (e:Entity) ON (e.name);

// ============================================
// DATA MIGRATIONS
// ============================================

// Add your data migrations here
// Example:
// MATCH (e:Entity) WHERE e.oldProperty IS NOT NULL
// SET e.newProperty = e.oldProperty
// REMOVE e.oldProperty;

// ============================================
// VERIFICATION
// ============================================

// Optional: Add verification queries
// SHOW CONSTRAINTS;
// SHOW INDEXES;
"""

        with open(filepath, 'w') as f:
            f.write(template)

        print(f"✅ Created migration: {filename}")
        print(f"   Edit: {filepath}")
        print(f"   Then run: python neo4j-migration-manager.py upgrade")

        return filepath

    def show_status(self):
        """Show current migration status."""
        current = self.get_current_version()
        pending = self.get_pending_migrations()

        print(f"Current version: V{current:03d}")

        if pending:
            print(f"\nPending migrations ({len(pending)}):")
            for version, filename in pending:
                print(f"  V{version:03d} - {filename}")
        else:
            print("\n✅ All migrations applied")

    def close(self):
        """Close Neo4j driver connection."""
        self.driver.close()


# Example migration files to create in migrations/neo4j/

# V001__initial_schema.cypher
INITIAL_SCHEMA = """
// Migration V001: Initial schema setup
// Created: 2025-11-01

// ============================================
// CONSTRAINTS
// ============================================

// Entity constraints
CREATE CONSTRAINT entity_uuid_unique IF NOT EXISTS
FOR (e:Entity) REQUIRE e.uuid IS UNIQUE;

CREATE CONSTRAINT entity_name_exists IF NOT EXISTS
FOR (e:Entity) REQUIRE e.name IS NOT NULL;

// Episode constraints
CREATE CONSTRAINT episode_uuid_unique IF NOT EXISTS
FOR (ep:Episode) REQUIRE ep.uuid IS UNIQUE;

// Edge constraints (Graphiti temporal edges)
CREATE CONSTRAINT edge_uuid_unique IF NOT EXISTS
FOR (ed:Edge) REQUIRE ed.uuid IS UNIQUE;

// ============================================
// INDEXES
// ============================================

// Entity indexes
CREATE INDEX entity_name_idx IF NOT EXISTS
FOR (e:Entity) ON (e.name);

CREATE INDEX entity_group_id_idx IF NOT EXISTS
FOR (e:Entity) ON (e.group_id);

CREATE INDEX entity_type_idx IF NOT EXISTS
FOR (e:Entity) ON (e.entity_type);

// Episode indexes
CREATE INDEX episode_reference_time_idx IF NOT EXISTS
FOR (ep:Episode) ON (ep.reference_time);

CREATE INDEX episode_created_at_idx IF NOT EXISTS
FOR (ep:Episode) ON (ep.created_at);

// Edge indexes (CRITICAL for temporal queries)
CREATE INDEX edge_valid_from_idx IF NOT EXISTS
FOR (ed:Edge) ON (ed.valid_from);

CREATE INDEX edge_invalid_at_idx IF NOT EXISTS
FOR (ed:Edge) ON (ed.invalid_at);

// Composite temporal index (MOST IMPORTANT)
CREATE INDEX edge_temporal_validity_idx IF NOT EXISTS
FOR (ed:Edge) ON (ed.valid_from, ed.invalid_at);

// ============================================
// FULL-TEXT INDEXES
// ============================================

// Entity full-text search
CREATE FULLTEXT INDEX entity_search_idx IF NOT EXISTS
FOR (n:Entity) ON EACH [n.name, n.summary];

// ============================================
// VERIFICATION
// ============================================

SHOW CONSTRAINTS;
SHOW INDEXES;
"""

# V002__add_document_indices.cypher
ADD_DOCUMENT_INDICES = """
// Migration V002: Add document-specific indices
// Created: 2025-11-01

// ============================================
// CONSTRAINTS
// ============================================

// Document constraints
CREATE CONSTRAINT document_uuid_unique IF NOT EXISTS
FOR (d:Document) REQUIRE d.uuid IS UNIQUE;

// ============================================
// INDEXES
// ============================================

// Document indexes
CREATE INDEX document_title_idx IF NOT EXISTS
FOR (d:Document) ON (d.title);

CREATE INDEX document_created_at_idx IF NOT EXISTS
FOR (d:Document) ON (d.created_at);

CREATE INDEX document_doc_type_idx IF NOT EXISTS
FOR (d:Document) ON (d.doc_type);

// Full-text search on documents
CREATE FULLTEXT INDEX document_search_idx IF NOT EXISTS
FOR (n:Document) ON EACH [n.title, n.content];

// ============================================
// VERIFICATION
// ============================================

SHOW INDEXES WHERE name CONTAINS 'document';
"""


# CLI Entry Point
if __name__ == "__main__":
    import sys

    # Configuration (load from env in production)
    NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "apexmemory2024")

    manager = Neo4jMigrationManager(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)

    try:
        if len(sys.argv) < 2:
            print("Usage: python neo4j-migration-manager.py <command>")
            print("\nCommands:")
            print("  upgrade            - Apply all pending migrations")
            print("  downgrade <version> - Rollback to specific version")
            print("  current            - Show current version")
            print("  status             - Show migration status")
            print('  create "<description>" - Create new migration file')
            sys.exit(1)

        command = sys.argv[1]

        if command == "upgrade":
            manager.upgrade()

        elif command == "downgrade":
            if len(sys.argv) < 3:
                print("Error: downgrade requires target version")
                print("Usage: python neo4j-migration-manager.py downgrade <version>")
                sys.exit(1)
            target = int(sys.argv[2])
            manager.rollback(target)

        elif command == "current":
            version = manager.get_current_version()
            print(f"Current version: V{version:03d}")

        elif command == "status":
            manager.show_status()

        elif command == "create":
            if len(sys.argv) < 3:
                print("Error: create requires description")
                print('Usage: python neo4j-migration-manager.py create "add customer indices"')
                sys.exit(1)
            description = sys.argv[2]
            manager.create_migration(description)

        else:
            print(f"Unknown command: {command}")
            sys.exit(1)

    finally:
        manager.close()
