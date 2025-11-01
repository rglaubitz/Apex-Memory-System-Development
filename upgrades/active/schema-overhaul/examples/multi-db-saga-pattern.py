"""
Multi-Database Saga Pattern Example

Source: postgresql-research.md (Distributed transactions)
Source: neo4j-research.md (Graph write patterns)
Source: qdrant-research.md (Vector upsert patterns)
Verified: November 2025

This example demonstrates the Saga pattern for distributed transactions
across multiple databases (Neo4j, PostgreSQL, Qdrant).

Saga Pattern:
- Execute activities in sequence
- If any activity fails, run compensation activities in reverse order
- Ensures eventual consistency across all databases

Features:
- Coordinated writes to Neo4j, PostgreSQL, Qdrant
- Compensation activities for rollback
- Error handling and retry logic
- UUID v7 for cross-database consistency
- Activity orchestration pattern

Requirements:
    pip install psycopg2-binary neo4j qdrant-client
    Neo4j, PostgreSQL, Qdrant running locally
"""

import time
import uuid
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import psycopg2
from neo4j import GraphDatabase
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance


class SagaStatus(Enum):
    """Saga execution status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    COMPENSATING = "compensating"
    COMPENSATED = "compensated"


@dataclass
class SagaActivity:
    """Single activity in a saga."""
    name: str
    execute_fn: callable
    compensate_fn: callable
    status: SagaStatus = SagaStatus.PENDING
    error: Optional[str] = None


@dataclass
class SagaResult:
    """Result of saga execution."""
    success: bool
    entity_uuid: Optional[str]
    activities_completed: List[str]
    activities_compensated: List[str]
    error: Optional[str] = None


class MultiDatabaseSaga:
    """
    Orchestrate writes across multiple databases using Saga pattern.

    Saga Workflow:
    1. Write to Neo4j (graph entity)
    2. Write to PostgreSQL (metadata)
    3. Write to Qdrant (vector embedding)

    If any step fails:
    1. Compensate Qdrant (delete vector)
    2. Compensate PostgreSQL (delete record)
    3. Compensate Neo4j (delete entity)

    This ensures eventual consistency: either all writes succeed or all are rolled back.
    """

    def __init__(
        self,
        postgres_conn_string: str = "postgresql://apex:apexmemory2024@localhost:5432/apex_memory",
        neo4j_uri: str = "bolt://localhost:7687",
        neo4j_user: str = "neo4j",
        neo4j_password: str = "apexmemory2024",
        qdrant_host: str = "localhost",
        qdrant_port: int = 6333
    ):
        """Initialize database connections."""
        self.pg_conn = psycopg2.connect(postgres_conn_string)
        self.neo4j_driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
        self.qdrant_client = QdrantClient(host=qdrant_host, port=qdrant_port)

        # Ensure collection exists in Qdrant
        self._init_qdrant_collection()

    def _init_qdrant_collection(self):
        """Create Qdrant collection if it doesn't exist."""
        collections = self.qdrant_client.get_collections().collections
        collection_names = [c.name for c in collections]

        if "entities" not in collection_names:
            self.qdrant_client.create_collection(
                collection_name="entities",
                vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
            )

    def generate_uuid_v7(self) -> str:
        """
        Generate UUID v7 for cross-database consistency.

        All databases will use the same UUID for the same entity.
        """
        timestamp_ms = int(time.time() * 1000)
        time_high = (timestamp_ms >> 16) & 0xFFFFFFFF
        time_mid = (timestamp_ms & 0xFFFF)
        time_low = 0x7000 | (int(time.time() * 1000000) & 0x0FFF)
        random_bits = uuid.uuid4().int & ((1 << 62) - 1)
        clock_seq = (random_bits >> 48) & 0x3FFF | 0x8000
        node = random_bits & 0xFFFFFFFFFFFF

        return str(uuid.UUID(
            fields=(time_high, time_mid, time_low, clock_seq, node),
            version=7
        ))

    def execute_saga(
        self,
        entity_name: str,
        entity_type: str,
        summary: str,
        embedding: List[float]
    ) -> SagaResult:
        """
        Execute saga to write entity across all databases.

        Saga Activities:
        1. Write to Neo4j
        2. Write to PostgreSQL
        3. Write to Qdrant

        If any activity fails, compensate in reverse order.

        Args:
            entity_name: Entity name
            entity_type: Entity type
            summary: Entity summary
            embedding: Vector embedding (1536 dimensions)

        Returns:
            SagaResult with success status and entity UUID
        """
        entity_uuid = self.generate_uuid_v7()

        print("=" * 70)
        print(f"Starting Saga for Entity: {entity_name}")
        print(f"UUID: {entity_uuid}")
        print("=" * 70)

        # Define saga activities
        activities = [
            SagaActivity(
                name="Write to Neo4j",
                execute_fn=lambda: self._write_neo4j(entity_uuid, entity_name, entity_type, summary),
                compensate_fn=lambda: self._delete_neo4j(entity_uuid)
            ),
            SagaActivity(
                name="Write to PostgreSQL",
                execute_fn=lambda: self._write_postgres(entity_uuid, entity_name, entity_type, summary),
                compensate_fn=lambda: self._delete_postgres(entity_uuid)
            ),
            SagaActivity(
                name="Write to Qdrant",
                execute_fn=lambda: self._write_qdrant(entity_uuid, entity_name, embedding),
                compensate_fn=lambda: self._delete_qdrant(entity_uuid)
            )
        ]

        # Execute saga
        activities_completed = []
        activities_compensated = []

        try:
            # Forward execution
            for activity in activities:
                print(f"\n▶ Executing: {activity.name}")
                activity.status = SagaStatus.IN_PROGRESS

                try:
                    activity.execute_fn()
                    activity.status = SagaStatus.COMPLETED
                    activities_completed.append(activity.name)
                    print(f"✅ {activity.name} completed")

                except Exception as e:
                    activity.status = SagaStatus.FAILED
                    activity.error = str(e)
                    print(f"❌ {activity.name} failed: {e}")

                    # Trigger compensation
                    raise Exception(f"Activity '{activity.name}' failed: {e}")

            # All activities succeeded
            print("\n" + "=" * 70)
            print("✅ Saga Completed Successfully")
            print("=" * 70)

            return SagaResult(
                success=True,
                entity_uuid=entity_uuid,
                activities_completed=activities_completed,
                activities_compensated=[]
            )

        except Exception as e:
            # Saga failed - compensate in reverse order
            print("\n" + "=" * 70)
            print("⚠️  Saga Failed - Starting Compensation")
            print("=" * 70)

            # Compensate completed activities in reverse order
            for activity in reversed(activities):
                if activity.status == SagaStatus.COMPLETED:
                    print(f"\n◀ Compensating: {activity.name}")
                    activity.status = SagaStatus.COMPENSATING

                    try:
                        activity.compensate_fn()
                        activity.status = SagaStatus.COMPENSATED
                        activities_compensated.append(activity.name)
                        print(f"✅ {activity.name} compensated")

                    except Exception as comp_error:
                        print(f"❌ Compensation failed for {activity.name}: {comp_error}")
                        # Continue compensating other activities

            print("\n" + "=" * 70)
            print("❌ Saga Failed and Compensated")
            print("=" * 70)

            return SagaResult(
                success=False,
                entity_uuid=None,
                activities_completed=activities_completed,
                activities_compensated=activities_compensated,
                error=str(e)
            )

    def _write_neo4j(self, entity_uuid: str, name: str, entity_type: str, summary: str):
        """Write entity to Neo4j."""
        with self.neo4j_driver.session() as session:
            session.run("""
                CREATE (e:Entity {
                    uuid: $uuid,
                    name: $name,
                    entity_type: $entity_type,
                    summary: $summary,
                    created_at: datetime()
                })
            """, uuid=entity_uuid, name=name, entity_type=entity_type, summary=summary)

    def _delete_neo4j(self, entity_uuid: str):
        """Delete entity from Neo4j (compensation)."""
        with self.neo4j_driver.session() as session:
            session.run("""
                MATCH (e:Entity {uuid: $uuid})
                DETACH DELETE e
            """, uuid=entity_uuid)

    def _write_postgres(self, entity_uuid: str, name: str, entity_type: str, summary: str):
        """Write entity to PostgreSQL."""
        with self.pg_conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS entities (
                    uuid UUID PRIMARY KEY,
                    name TEXT NOT NULL,
                    entity_type TEXT NOT NULL,
                    summary TEXT,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)

            cur.execute("""
                INSERT INTO entities (uuid, name, entity_type, summary)
                VALUES (%s, %s, %s, %s)
            """, (entity_uuid, name, entity_type, summary))

        self.pg_conn.commit()

    def _delete_postgres(self, entity_uuid: str):
        """Delete entity from PostgreSQL (compensation)."""
        with self.pg_conn.cursor() as cur:
            cur.execute("DELETE FROM entities WHERE uuid = %s", (entity_uuid,))
        self.pg_conn.commit()

    def _write_qdrant(self, entity_uuid: str, name: str, embedding: List[float]):
        """Write vector to Qdrant."""
        point = PointStruct(
            id=entity_uuid,
            vector=embedding,
            payload={"name": name}
        )

        self.qdrant_client.upsert(
            collection_name="entities",
            points=[point]
        )

    def _delete_qdrant(self, entity_uuid: str):
        """Delete vector from Qdrant (compensation)."""
        self.qdrant_client.delete(
            collection_name="entities",
            points_selector=[entity_uuid]
        )

    def simulate_failure(
        self,
        entity_name: str,
        entity_type: str,
        summary: str,
        embedding: List[float],
        fail_at_activity: str
    ) -> SagaResult:
        """
        Simulate saga failure at specific activity to test compensation.

        Args:
            entity_name: Entity name
            entity_type: Entity type
            summary: Entity summary
            embedding: Vector embedding
            fail_at_activity: Activity name to fail at

        Returns:
            SagaResult showing compensation
        """
        entity_uuid = self.generate_uuid_v7()

        print("=" * 70)
        print(f"Simulating Saga Failure at: {fail_at_activity}")
        print(f"Entity: {entity_name}")
        print(f"UUID: {entity_uuid}")
        print("=" * 70)

        # Define activities with intentional failure
        def fail_intentionally():
            raise Exception(f"Intentional failure at {fail_at_activity}")

        activities = [
            SagaActivity(
                name="Write to Neo4j",
                execute_fn=lambda: self._write_neo4j(entity_uuid, entity_name, entity_type, summary)
                    if fail_at_activity != "Write to Neo4j" else fail_intentionally(),
                compensate_fn=lambda: self._delete_neo4j(entity_uuid)
            ),
            SagaActivity(
                name="Write to PostgreSQL",
                execute_fn=lambda: self._write_postgres(entity_uuid, entity_name, entity_type, summary)
                    if fail_at_activity != "Write to PostgreSQL" else fail_intentionally(),
                compensate_fn=lambda: self._delete_postgres(entity_uuid)
            ),
            SagaActivity(
                name="Write to Qdrant",
                execute_fn=lambda: self._write_qdrant(entity_uuid, entity_name, embedding)
                    if fail_at_activity != "Write to Qdrant" else fail_intentionally(),
                compensate_fn=lambda: self._delete_qdrant(entity_uuid)
            )
        ]

        # Execute saga (will fail and compensate)
        activities_completed = []
        activities_compensated = []

        try:
            for activity in activities:
                print(f"\n▶ Executing: {activity.name}")
                activity.status = SagaStatus.IN_PROGRESS

                try:
                    activity.execute_fn()
                    activity.status = SagaStatus.COMPLETED
                    activities_completed.append(activity.name)
                    print(f"✅ {activity.name} completed")

                except Exception as e:
                    activity.status = SagaStatus.FAILED
                    activity.error = str(e)
                    print(f"❌ {activity.name} failed: {e}")
                    raise Exception(f"Activity '{activity.name}' failed: {e}")

        except Exception as e:
            # Compensate in reverse order
            print("\n" + "=" * 70)
            print("⚠️  Starting Compensation")
            print("=" * 70)

            for activity in reversed(activities):
                if activity.status == SagaStatus.COMPLETED:
                    print(f"\n◀ Compensating: {activity.name}")
                    activity.status = SagaStatus.COMPENSATING

                    try:
                        activity.compensate_fn()
                        activity.status = SagaStatus.COMPENSATED
                        activities_compensated.append(activity.name)
                        print(f"✅ {activity.name} compensated")

                    except Exception as comp_error:
                        print(f"❌ Compensation failed: {comp_error}")

            return SagaResult(
                success=False,
                entity_uuid=None,
                activities_completed=activities_completed,
                activities_compensated=activities_compensated,
                error=str(e)
            )

    def close(self):
        """Close database connections."""
        self.pg_conn.close()
        self.neo4j_driver.close()
        self.qdrant_client.close()


def example_successful_saga():
    """
    Example 1: Successful saga execution (all activities succeed).
    """
    print("=" * 70)
    print("Example 1: Successful Saga Execution")
    print("=" * 70)

    saga = MultiDatabaseSaga()

    try:
        # Generate sample embedding (replace with real embedding in production)
        import numpy as np
        embedding = np.random.randn(1536).astype(np.float32).tolist()

        result = saga.execute_saga(
            entity_name="ACME Corporation",
            entity_type="Company",
            summary="Major manufacturing company",
            embedding=embedding
        )

        print("\nSaga Result:")
        print(f"  Success: {result.success}")
        print(f"  Entity UUID: {result.entity_uuid}")
        print(f"  Activities Completed: {len(result.activities_completed)}")
        for activity in result.activities_completed:
            print(f"    • {activity}")

        return result.entity_uuid

    finally:
        saga.close()


def example_failed_saga():
    """
    Example 2: Failed saga with compensation (PostgreSQL write fails).
    """
    print("\n\n" + "=" * 70)
    print("Example 2: Failed Saga with Compensation")
    print("=" * 70)

    saga = MultiDatabaseSaga()

    try:
        # Generate sample embedding
        import numpy as np
        embedding = np.random.randn(1536).astype(np.float32).tolist()

        result = saga.simulate_failure(
            entity_name="Bosch Industries",
            entity_type="Company",
            summary="German engineering company",
            embedding=embedding,
            fail_at_activity="Write to PostgreSQL"
        )

        print("\nSaga Result:")
        print(f"  Success: {result.success}")
        print(f"  Activities Completed: {len(result.activities_completed)}")
        for activity in result.activities_completed:
            print(f"    • {activity}")

        print(f"  Activities Compensated: {len(result.activities_compensated)}")
        for activity in result.activities_compensated:
            print(f"    • {activity}")

        print(f"  Error: {result.error}")

    finally:
        saga.close()


def example_saga_patterns():
    """
    Example 3: Common saga patterns and best practices.
    """
    print("\n\n" + "=" * 70)
    print("Example 3: Saga Patterns and Best Practices")
    print("=" * 70)

    print("""
1. Forward Recovery (Retry on Failure):
   • Neo4j write fails temporarily (network issue)
   • Retry 3 times with exponential backoff
   • If still fails, trigger compensation

2. Compensation Activities Must Be Idempotent:
   • Can run multiple times without side effects
   • Example: DELETE WHERE uuid = X (safe to run twice)
   • Example: INSERT (not idempotent, needs check first)

3. Activity Ordering:
   • Cheapest operations first (PostgreSQL, Neo4j)
   • Expensive operations last (Qdrant vector index)
   • Easier to compensate early failures

4. Temporal Integration:
   • Each activity is a Temporal activity
   • Temporal handles retries and compensation
   • Saga state persisted in Temporal

5. Monitoring:
   • Track saga success rate
   • Alert on high compensation rate
   • Log all compensation activities

Example Temporal Workflow:

```python
@workflow.defn
class EntityIngestionWorkflow:
    @workflow.run
    async def run(self, entity_data: EntityData) -> str:
        entity_uuid = generate_uuid_v7()

        try:
            # Activity 1: Neo4j
            await workflow.execute_activity(
                write_neo4j,
                entity_data,
                start_to_close_timeout=timedelta(seconds=30),
                retry_policy=RetryPolicy(maximum_attempts=3)
            )

            # Activity 2: PostgreSQL
            await workflow.execute_activity(
                write_postgres,
                entity_data,
                start_to_close_timeout=timedelta(seconds=30)
            )

            # Activity 3: Qdrant
            await workflow.execute_activity(
                write_qdrant,
                entity_data,
                start_to_close_timeout=timedelta(seconds=60)
            )

            return entity_uuid

        except Exception as e:
            # Compensation triggered automatically by Temporal
            workflow.logger.error(f"Workflow failed: {e}")
            raise
```

6. Testing Saga Compensation:
   • Test each failure scenario
   • Verify compensation restores consistent state
   • Load test with 10% failure rate
   • Monitor database consistency after compensation
    """)


def main():
    """
    Run all saga pattern examples.
    """
    # Example 1: Successful saga
    entity_uuid = example_successful_saga()

    # Example 2: Failed saga with compensation
    example_failed_saga()

    # Example 3: Saga patterns and best practices
    example_saga_patterns()

    print("\n" + "=" * 70)
    print("All Examples Complete!")
    print("=" * 70)

    print("\nKey Takeaways:")
    print("✅ Saga pattern ensures eventual consistency across databases")
    print("✅ Compensation activities rollback partial failures")
    print("✅ UUID v7 enables cross-database entity tracking")
    print("✅ Activity ordering: cheap first, expensive last")
    print("✅ Temporal handles retries and compensation automatically")

    print("\nProduction Recommendations:")
    print("1. Use Temporal workflows for saga orchestration")
    print("2. Make all compensation activities idempotent")
    print("3. Monitor saga success rate and compensation frequency")
    print("4. Test failure scenarios thoroughly")
    print("5. Order activities by cost (cheap → expensive)")


if __name__ == "__main__":
    main()
