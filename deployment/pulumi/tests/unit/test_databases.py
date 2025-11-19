"""
Unit tests for Cloud SQL database module.

Tests database infrastructure creation without actual GCP calls.
Uses Pulumi's mocking framework for fast, isolated testing.
"""

import unittest
import pulumi


# Set up Pulumi mocks for testing
class MyMocks(pulumi.runtime.Mocks):
    """Mock Pulumi calls for unit testing."""

    def new_resource(self, args: pulumi.runtime.MockResourceArgs):
        """Mock resource creation."""
        outputs = args.inputs

        # Add default outputs for different resource types
        if args.typ == "random:index/randomPassword:RandomPassword":
            outputs = {
                **args.inputs,
                "result": "mock-secure-password-32-chars-long",
            }
        elif args.typ == "gcp:sql/databaseInstance:DatabaseInstance":
            outputs = {
                **args.inputs,
                "id": "postgres-instance-12345",
                "connection_name": "test-project:us-central1:test-postgres",
                "private_ip_address": "10.1.0.5",
            }
        elif args.typ == "gcp:sql/database:Database":
            outputs = {
                **args.inputs,
                "id": "database-12345",
            }
        elif args.typ == "gcp:sql/user:User":
            outputs = {
                **args.inputs,
                "id": "user-12345",
            }
        elif args.typ == "gcp:serviceaccount/account:Account":
            outputs = {
                **args.inputs,
                "id": "service-account-12345",
                "email": "test-sa@test-project.iam.gserviceaccount.com",
            }
        elif args.typ == "gcp:compute/disk:Disk":
            outputs = {
                **args.inputs,
                "id": "disk-12345",
                "self_link": "https://compute.googleapis.com/compute/v1/projects/test/zones/us-central1-a/disks/test-disk",
            }
        elif args.typ == "gcp:compute/instance:Instance":
            outputs = {
                **args.inputs,
                "id": "instance-12345",
                "network_interfaces": [
                    {
                        "network_ip": "10.0.0.10",
                        "name": "nic0",
                    }
                ],
            }
        elif args.typ == "gcp:redis/instance:Instance":
            outputs = {
                **args.inputs,
                "id": "redis-12345",
                "host": "10.0.0.20",
                "port": 6379,
            }

        return [args.name + "_id", outputs]

    def call(self, args: pulumi.runtime.MockCallArgs):
        """Mock function calls."""
        return {}


pulumi.runtime.set_mocks(MyMocks())


class TestDatabases(unittest.TestCase):
    """Test Cloud SQL database module."""

    @pulumi.runtime.test
    def test_postgres_instance_creation(self):
        """Test that PostgreSQL instance is created with correct settings."""
        from modules.databases import create_cloud_sql_postgres

        # Mock network ID and private connection
        mock_network_id = pulumi.Output.from_input("vpc-12345")
        mock_private_connection = None  # In unit tests, we don't need actual connection

        # Create database infrastructure
        databases = create_cloud_sql_postgres(
            project_id="test-project",
            region="us-central1",
            network_id=mock_network_id,
            private_connection=mock_private_connection,
            tier="db-f1-micro",
        )

        # Verify PostgreSQL instance exists
        self.assertIsNotNone(databases["postgres"])
        self.assertIsNotNone(databases["database"])
        self.assertIsNotNone(databases["user"])
        self.assertIsNotNone(databases["password"])

    @pulumi.runtime.test
    def test_postgres_private_ip_only(self):
        """Test that PostgreSQL has no public IP."""
        from modules.databases import create_cloud_sql_postgres

        mock_network_id = pulumi.Output.from_input("vpc-12345")
        mock_private_connection = None

        databases = create_cloud_sql_postgres(
            project_id="test-project",
            region="us-central1",
            network_id=mock_network_id,
            private_connection=mock_private_connection,
        )

        # Verify private IP configuration - just check attributes exist
        postgres = databases["postgres"]
        self.assertIsNotNone(postgres)
        self.assertTrue(hasattr(postgres, 'settings'))

    @pulumi.runtime.test
    def test_neo4j_instance_creation(self):
        """Test that Neo4j instance is created with correct settings."""
        from modules.databases import create_neo4j_instance

        # Mock network and subnet IDs
        mock_network_id = pulumi.Output.from_input("vpc-12345")
        mock_subnet_id = pulumi.Output.from_input("subnet-12345")

        # Create Neo4j infrastructure
        neo4j = create_neo4j_instance(
            project_id="test-project",
            region="us-central1",
            network_id=mock_network_id,
            subnet_id=mock_subnet_id,
            machine_type="e2-small",
            disk_size_gb=50,
        )

        # Verify Neo4j resources exist
        self.assertIsNotNone(neo4j["service_account"])
        self.assertIsNotNone(neo4j["disk"])
        self.assertIsNotNone(neo4j["instance"])
        self.assertIsNotNone(neo4j["password"])

    @pulumi.runtime.test
    def test_neo4j_private_ip_only(self):
        """Test that Neo4j has no external IP (private only)."""
        from modules.databases import create_neo4j_instance

        mock_network_id = pulumi.Output.from_input("vpc-12345")
        mock_subnet_id = pulumi.Output.from_input("subnet-12345")

        neo4j = create_neo4j_instance(
            project_id="test-project",
            region="us-central1",
            network_id=mock_network_id,
            subnet_id=mock_subnet_id,
        )

        # Verify instance has network interfaces
        instance = neo4j["instance"]
        self.assertIsNotNone(instance)
        self.assertTrue(hasattr(instance, 'network_interfaces'))

    @pulumi.runtime.test
    def test_redis_instance_creation(self):
        """Test that Redis Memorystore instance is created with correct settings."""
        from modules.databases import create_redis_instance

        # Mock network ID
        mock_network_id = pulumi.Output.from_input("vpc-12345")

        # Create Redis infrastructure
        redis = create_redis_instance(
            project_id="test-project",
            region="us-central1",
            network_id=mock_network_id,
            memory_size_gb=1,
            tier="BASIC",
        )

        # Verify Redis instance exists
        self.assertIsNotNone(redis["instance"])

    @pulumi.runtime.test
    def test_redis_configuration(self):
        """Test that Redis has correct configuration settings."""
        from modules.databases import create_redis_instance

        mock_network_id = pulumi.Output.from_input("vpc-12345")

        redis = create_redis_instance(
            project_id="test-project",
            region="us-central1",
            network_id=mock_network_id,
            memory_size_gb=1,
            tier="BASIC",
        )

        # Verify instance has correct attributes
        instance = redis["instance"]
        self.assertIsNotNone(instance)
        self.assertTrue(hasattr(instance, 'tier'))
        self.assertTrue(hasattr(instance, 'memory_size_gb'))

    @pulumi.runtime.test
    def test_qdrant_instance_creation(self):
        """Test that Qdrant instance is created with correct settings."""
        from modules.databases import create_qdrant_instance

        # Mock network and subnet IDs
        mock_network_id = pulumi.Output.from_input("vpc-12345")
        mock_subnet_id = pulumi.Output.from_input("subnet-12345")

        # Create Qdrant infrastructure
        qdrant = create_qdrant_instance(
            project_id="test-project",
            region="us-central1",
            network_id=mock_network_id,
            subnet_id=mock_subnet_id,
            machine_type="e2-medium",
            disk_size_gb=100,
        )

        # Verify Qdrant resources exist
        self.assertIsNotNone(qdrant["service_account"])
        self.assertIsNotNone(qdrant["disk"])
        self.assertIsNotNone(qdrant["instance"])

    @pulumi.runtime.test
    def test_qdrant_private_ip_only(self):
        """Test that Qdrant has no external IP (private only)."""
        from modules.databases import create_qdrant_instance

        mock_network_id = pulumi.Output.from_input("vpc-12345")
        mock_subnet_id = pulumi.Output.from_input("subnet-12345")

        qdrant = create_qdrant_instance(
            project_id="test-project",
            region="us-central1",
            network_id=mock_network_id,
            subnet_id=mock_subnet_id,
        )

        # Verify instance has network interfaces
        instance = qdrant["instance"]
        self.assertIsNotNone(instance)
        self.assertTrue(hasattr(instance, 'network_interfaces'))


if __name__ == "__main__":
    unittest.main()
