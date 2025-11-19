"""
Integration tests for Neo4j and Redis connectivity.

Tests database connections from the VPC to verify private networking
and basic operations.

These tests require actual GCP infrastructure to be deployed.
"""

import pytest
from neo4j import GraphDatabase
import redis


# Connection details from Pulumi stack outputs
NEO4J_URI = "bolt://10.0.0.2:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "{*i-ouY!AZEp1Gf+h0u[A6)R]utvhb#0"

REDIS_HOST = "10.123.172.227"
REDIS_PORT = 6379


@pytest.mark.integration
class TestNeo4jConnectivity:
    """Test Neo4j graph database connectivity and operations."""

    def test_neo4j_connection(self):
        """Test basic Neo4j connectivity via Bolt protocol."""
        driver = None
        try:
            # Create Neo4j driver
            driver = GraphDatabase.driver(
                NEO4J_URI,
                auth=(NEO4J_USER, NEO4J_PASSWORD)
            )

            # Verify connection with simple query
            with driver.session() as session:
                result = session.run("RETURN 1 AS num")
                record = result.single()
                assert record["num"] == 1

        finally:
            if driver:
                driver.close()

    def test_neo4j_create_node(self):
        """Test creating and retrieving a node in Neo4j."""
        driver = None
        try:
            driver = GraphDatabase.driver(
                NEO4J_URI,
                auth=(NEO4J_USER, NEO4J_PASSWORD)
            )

            with driver.session() as session:
                # Create a test node
                result = session.run(
                    "CREATE (n:TestNode {name: $name, timestamp: $timestamp}) RETURN n",
                    name="integration_test",
                    timestamp="2025-11-16"
                )
                node = result.single()["n"]
                assert node["name"] == "integration_test"

                # Retrieve the node
                result = session.run(
                    "MATCH (n:TestNode {name: $name}) RETURN n",
                    name="integration_test"
                )
                retrieved_node = result.single()["n"]
                assert retrieved_node["name"] == "integration_test"
                assert retrieved_node["timestamp"] == "2025-11-16"

                # Cleanup: Delete the test node
                session.run(
                    "MATCH (n:TestNode {name: $name}) DELETE n",
                    name="integration_test"
                )

        finally:
            if driver:
                driver.close()

    def test_neo4j_relationship(self):
        """Test creating and querying relationships in Neo4j."""
        driver = None
        try:
            driver = GraphDatabase.driver(
                NEO4J_URI,
                auth=(NEO4J_USER, NEO4J_PASSWORD)
            )

            with driver.session() as session:
                # Create two nodes with a relationship
                session.run("""
                    CREATE (a:Person {name: 'Alice'})
                    CREATE (b:Person {name: 'Bob'})
                    CREATE (a)-[:KNOWS {since: '2025'}]->(b)
                """)

                # Query the relationship
                result = session.run("""
                    MATCH (a:Person {name: 'Alice'})-[r:KNOWS]->(b:Person {name: 'Bob'})
                    RETURN a.name as from, b.name as to, r.since as since
                """)
                record = result.single()
                assert record["from"] == "Alice"
                assert record["to"] == "Bob"
                assert record["since"] == "2025"

                # Cleanup
                session.run("MATCH (n:Person) DETACH DELETE n")

        finally:
            if driver:
                driver.close()

    def test_neo4j_persistence(self):
        """Test data persistence across connections."""
        driver = None
        try:
            driver = GraphDatabase.driver(
                NEO4J_URI,
                auth=(NEO4J_USER, NEO4J_PASSWORD)
            )

            # Create node in first session
            with driver.session() as session:
                session.run(
                    "CREATE (n:PersistenceTest {id: $id})",
                    id="test-123"
                )

            # Close driver to simulate disconnect
            driver.close()

            # Reconnect and verify node still exists
            driver = GraphDatabase.driver(
                NEO4J_URI,
                auth=(NEO4J_USER, NEO4J_PASSWORD)
            )

            with driver.session() as session:
                result = session.run(
                    "MATCH (n:PersistenceTest {id: $id}) RETURN n",
                    id="test-123"
                )
                node = result.single()
                assert node is not None
                assert node["n"]["id"] == "test-123"

                # Cleanup
                session.run("MATCH (n:PersistenceTest) DELETE n")

        finally:
            if driver:
                driver.close()


@pytest.mark.integration
class TestRedisConnectivity:
    """Test Redis Memorystore connectivity and operations."""

    def test_redis_connection(self):
        """Test basic Redis connectivity."""
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

        # Test ping
        assert r.ping() is True

    def test_redis_set_get(self):
        """Test basic Redis set/get operations."""
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

        try:
            # Set a key
            r.set("test_key", "test_value")

            # Get the key
            value = r.get("test_key")
            assert value == "test_value"

        finally:
            # Cleanup
            r.delete("test_key")

    def test_redis_expiration(self):
        """Test Redis key expiration."""
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

        try:
            # Set key with 2 second TTL
            r.setex("expire_test", 2, "will_expire")

            # Verify key exists
            assert r.exists("expire_test") == 1

            # Check TTL
            ttl = r.ttl("expire_test")
            assert 0 < ttl <= 2

            # Verify value
            assert r.get("expire_test") == "will_expire"

        finally:
            # Cleanup (in case test fails before expiration)
            r.delete("expire_test")

    def test_redis_hash_operations(self):
        """Test Redis hash (dictionary) operations."""
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

        try:
            # Set hash fields
            r.hset("user:123", mapping={
                "name": "Alice",
                "email": "alice@example.com",
                "age": "30"
            })

            # Get single field
            name = r.hget("user:123", "name")
            assert name == "Alice"

            # Get all fields
            user = r.hgetall("user:123")
            assert user["name"] == "Alice"
            assert user["email"] == "alice@example.com"
            assert user["age"] == "30"

        finally:
            # Cleanup
            r.delete("user:123")

    def test_redis_list_operations(self):
        """Test Redis list operations."""
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

        try:
            # Push items to list
            r.rpush("queue", "item1", "item2", "item3")

            # Get list length
            length = r.llen("queue")
            assert length == 3

            # Pop from list
            item = r.lpop("queue")
            assert item == "item1"

            # Check new length
            assert r.llen("queue") == 2

        finally:
            # Cleanup
            r.delete("queue")

    def test_redis_lru_eviction(self):
        """Test that Redis is configured with LRU eviction policy."""
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

        # Check maxmemory-policy configuration
        config = r.config_get("maxmemory-policy")
        assert config["maxmemory-policy"] == "allkeys-lru"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
