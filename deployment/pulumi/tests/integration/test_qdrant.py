"""
Integration tests for Qdrant vector database.

Tests Qdrant connectivity, collection operations, and vector search.
These tests require VPC connectivity (Cloud Shell, Compute Engine, or Cloud Run).

⚠️ IMPORTANT: These tests will FAIL when run locally (expected behavior).
   Qdrant is deployed with private IP only (10.0.0.3) for security.

   To run these tests, use Cloud Shell:
   1. gcloud cloud-shell ssh
   2. cd /path/to/deployment/pulumi
   3. source .venv/bin/activate
   4. pytest tests/integration/test_qdrant.py -v
"""

import unittest
import os
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import numpy as np


class TestQdrantConnectivity(unittest.TestCase):
    """Test basic Qdrant connectivity and health."""

    @classmethod
    def setUpClass(cls):
        """Connect to Qdrant instance."""
        # Get Qdrant connection details from pulumi stack outputs
        # Qdrant is at 10.0.0.3:6333 (HTTP) and 10.0.0.3:6334 (gRPC)
        qdrant_host = os.environ.get("QDRANT_HOST", "10.0.0.3")
        qdrant_port = int(os.environ.get("QDRANT_PORT", "6333"))

        cls.client = QdrantClient(host=qdrant_host, port=qdrant_port, timeout=10)

    def test_qdrant_connection(self):
        """Test connection to Qdrant HTTP API."""
        # Health check returns basic info
        health = self.client.get_collections()
        self.assertIsNotNone(health)
        print(f"✅ Qdrant health check passed: {len(health.collections)} collections")

    def test_qdrant_version(self):
        """Test Qdrant version information."""
        # Get cluster info (includes version)
        info = self.client.get_cluster_info()
        self.assertIsNotNone(info)
        print(f"✅ Qdrant cluster info retrieved: {info}")


class TestQdrantCollections(unittest.TestCase):
    """Test Qdrant collection operations."""

    @classmethod
    def setUpClass(cls):
        """Connect to Qdrant instance."""
        qdrant_host = os.environ.get("QDRANT_HOST", "10.0.0.3")
        qdrant_port = int(os.environ.get("QDRANT_PORT", "6333"))
        cls.client = QdrantClient(host=qdrant_host, port=qdrant_port, timeout=10)
        cls.test_collection = "test_collection"

    def tearDown(self):
        """Clean up test collections."""
        try:
            self.client.delete_collection(self.test_collection)
        except Exception:
            pass  # Collection might not exist

    def test_create_collection(self):
        """Test creating a collection with vector config."""
        # Create collection with 128-dimensional vectors
        self.client.create_collection(
            collection_name=self.test_collection,
            vectors_config=VectorParams(size=128, distance=Distance.COSINE),
        )

        # Verify collection exists
        collections = self.client.get_collections()
        collection_names = [c.name for c in collections.collections]
        self.assertIn(self.test_collection, collection_names)
        print(f"✅ Collection '{self.test_collection}' created successfully")

    def test_list_collections(self):
        """Test listing all collections."""
        # Create test collection
        self.client.create_collection(
            collection_name=self.test_collection,
            vectors_config=VectorParams(size=128, distance=Distance.COSINE),
        )

        # List collections
        collections = self.client.get_collections()
        self.assertGreaterEqual(len(collections.collections), 1)
        print(f"✅ Found {len(collections.collections)} collections")

    def test_get_collection_info(self):
        """Test getting collection metadata."""
        # Create test collection
        self.client.create_collection(
            collection_name=self.test_collection,
            vectors_config=VectorParams(size=128, distance=Distance.COSINE),
        )

        # Get collection info
        info = self.client.get_collection(self.test_collection)
        self.assertEqual(info.config.params.vectors.size, 128)
        self.assertEqual(info.config.params.vectors.distance, Distance.COSINE)
        print(f"✅ Collection info retrieved: {info.vectors_count} vectors")

    def test_delete_collection(self):
        """Test deleting a collection."""
        # Create test collection
        self.client.create_collection(
            collection_name=self.test_collection,
            vectors_config=VectorParams(size=128, distance=Distance.COSINE),
        )

        # Delete collection
        result = self.client.delete_collection(self.test_collection)
        self.assertTrue(result)

        # Verify collection no longer exists
        collections = self.client.get_collections()
        collection_names = [c.name for c in collections.collections]
        self.assertNotIn(self.test_collection, collection_names)
        print(f"✅ Collection '{self.test_collection}' deleted successfully")


class TestQdrantVectors(unittest.TestCase):
    """Test Qdrant vector operations."""

    @classmethod
    def setUpClass(cls):
        """Connect to Qdrant and create test collection."""
        qdrant_host = os.environ.get("QDRANT_HOST", "10.0.0.3")
        qdrant_port = int(os.environ.get("QDRANT_PORT", "6333"))
        cls.client = QdrantClient(host=qdrant_host, port=qdrant_port, timeout=10)
        cls.test_collection = "test_vectors"

        # Create collection with 128-dimensional vectors
        cls.client.create_collection(
            collection_name=cls.test_collection,
            vectors_config=VectorParams(size=128, distance=Distance.COSINE),
        )

    @classmethod
    def tearDownClass(cls):
        """Clean up test collection."""
        try:
            cls.client.delete_collection(cls.test_collection)
        except Exception:
            pass

    def test_insert_vector(self):
        """Test inserting a single vector."""
        # Generate random 128-dimensional vector
        vector = np.random.rand(128).tolist()

        # Insert vector with payload
        self.client.upsert(
            collection_name=self.test_collection,
            points=[
                PointStruct(
                    id=1,
                    vector=vector,
                    payload={"text": "test document", "category": "test"},
                )
            ],
        )

        # Retrieve vector
        point = self.client.retrieve(
            collection_name=self.test_collection,
            ids=[1],
        )
        self.assertEqual(len(point), 1)
        self.assertEqual(point[0].id, 1)
        self.assertEqual(point[0].payload["text"], "test document")
        print("✅ Vector inserted and retrieved successfully")

    def test_batch_insert_vectors(self):
        """Test inserting multiple vectors in batch."""
        # Generate 10 random vectors
        points = [
            PointStruct(
                id=i,
                vector=np.random.rand(128).tolist(),
                payload={"text": f"document {i}", "index": i},
            )
            for i in range(10)
        ]

        # Batch insert
        self.client.upsert(
            collection_name=self.test_collection,
            points=points,
        )

        # Verify all vectors inserted
        info = self.client.get_collection(self.test_collection)
        self.assertEqual(info.vectors_count, 10)
        print("✅ Batch insert of 10 vectors successful")

    def test_vector_search(self):
        """Test similarity search for nearest vectors."""
        # Insert test vectors
        points = [
            PointStruct(
                id=i,
                vector=np.random.rand(128).tolist(),
                payload={"text": f"document {i}", "index": i},
            )
            for i in range(10)
        ]
        self.client.upsert(
            collection_name=self.test_collection,
            points=points,
        )

        # Search for similar vectors
        query_vector = np.random.rand(128).tolist()
        results = self.client.search(
            collection_name=self.test_collection,
            query_vector=query_vector,
            limit=5,
        )

        # Verify search results
        self.assertEqual(len(results), 5)
        self.assertIsNotNone(results[0].score)
        self.assertIsNotNone(results[0].payload)
        print(f"✅ Vector search returned {len(results)} results")
        print(f"   Top result score: {results[0].score:.4f}")

    def test_filtered_search(self):
        """Test vector search with payload filters."""
        # Insert vectors with different categories
        points = [
            PointStruct(
                id=i,
                vector=np.random.rand(128).tolist(),
                payload={"text": f"document {i}", "category": "A" if i < 5 else "B"},
            )
            for i in range(10)
        ]
        self.client.upsert(
            collection_name=self.test_collection,
            points=points,
        )

        # Search with filter for category A
        query_vector = np.random.rand(128).tolist()
        results = self.client.search(
            collection_name=self.test_collection,
            query_vector=query_vector,
            query_filter={"must": [{"key": "category", "match": {"value": "A"}}]},
            limit=10,
        )

        # Verify all results are category A
        self.assertLessEqual(len(results), 5)  # Max 5 category A documents
        for result in results:
            self.assertEqual(result.payload["category"], "A")
        print(f"✅ Filtered search returned {len(results)} category A results")

    def test_update_vector(self):
        """Test updating an existing vector."""
        # Insert initial vector
        vector1 = np.random.rand(128).tolist()
        self.client.upsert(
            collection_name=self.test_collection,
            points=[
                PointStruct(
                    id=1,
                    vector=vector1,
                    payload={"text": "original", "version": 1},
                )
            ],
        )

        # Update vector with new embedding and payload
        vector2 = np.random.rand(128).tolist()
        self.client.upsert(
            collection_name=self.test_collection,
            points=[
                PointStruct(
                    id=1,
                    vector=vector2,
                    payload={"text": "updated", "version": 2},
                )
            ],
        )

        # Retrieve and verify update
        point = self.client.retrieve(
            collection_name=self.test_collection,
            ids=[1],
        )
        self.assertEqual(point[0].payload["text"], "updated")
        self.assertEqual(point[0].payload["version"], 2)
        print("✅ Vector updated successfully")

    def test_delete_vector(self):
        """Test deleting individual vectors."""
        # Insert vectors
        points = [
            PointStruct(
                id=i,
                vector=np.random.rand(128).tolist(),
                payload={"text": f"document {i}"},
            )
            for i in range(5)
        ]
        self.client.upsert(
            collection_name=self.test_collection,
            points=points,
        )

        # Delete vector with id=2
        self.client.delete(
            collection_name=self.test_collection,
            points_selector=[2],
        )

        # Verify deletion
        info = self.client.get_collection(self.test_collection)
        self.assertEqual(info.vectors_count, 4)  # 5 - 1 = 4

        # Verify id=2 no longer exists
        remaining = self.client.retrieve(
            collection_name=self.test_collection,
            ids=[2],
        )
        self.assertEqual(len(remaining), 0)
        print("✅ Vector deleted successfully")


class TestQdrantPersistence(unittest.TestCase):
    """Test Qdrant data persistence across Docker container restarts."""

    @classmethod
    def setUpClass(cls):
        """Connect to Qdrant instance."""
        qdrant_host = os.environ.get("QDRANT_HOST", "10.0.0.3")
        qdrant_port = int(os.environ.get("QDRANT_PORT", "6333"))
        cls.client = QdrantClient(host=qdrant_host, port=qdrant_port, timeout=10)
        cls.test_collection = "persistence_test"

    @classmethod
    def tearDownClass(cls):
        """Clean up test collection."""
        try:
            cls.client.delete_collection(cls.test_collection)
        except Exception:
            pass

    def test_data_persistence(self):
        """
        Test that data persists across container restarts.

        Note: This test requires manual container restart between runs.
        First run: Creates collection and inserts data
        Second run (after restart): Verifies data still exists
        """
        try:
            # Try to get existing collection
            info = self.client.get_collection(self.test_collection)
            print(f"✅ Collection persisted! Found {info.vectors_count} vectors after restart")

            # Clean up for next test
            self.client.delete_collection(self.test_collection)
        except Exception:
            # Collection doesn't exist, create it
            self.client.create_collection(
                collection_name=self.test_collection,
                vectors_config=VectorParams(size=128, distance=Distance.COSINE),
            )

            # Insert test data
            points = [
                PointStruct(
                    id=i,
                    vector=np.random.rand(128).tolist(),
                    payload={"text": f"persistent doc {i}"},
                )
                for i in range(5)
            ]
            self.client.upsert(
                collection_name=self.test_collection,
                points=points,
            )

            print("✅ Test data created. Restart Docker container and run test again.")
            print("   SSH to VM: gcloud compute ssh apex-qdrant-dev --zone=us-central1-a")
            print("   Restart: docker restart qdrant")


if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2)
