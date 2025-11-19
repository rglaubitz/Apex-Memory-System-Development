# Qdrant Setup Guide

**Qdrant Instance:** apex-qdrant-dev
**Private IP:** 10.0.0.3
**HTTP API:** http://10.0.0.3:6333
**gRPC API:** http://10.0.0.3:6334
**Status:** ✅ RUNNING

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Accessing Qdrant](#accessing-qdrant)
3. [Python Client Examples](#python-client-examples)
4. [Collection Management](#collection-management)
5. [Vector Operations](#vector-operations)
6. [Search Strategies](#search-strategies)
7. [Performance Tuning](#performance-tuning)
8. [Backup and Restore](#backup-and-restore)
9. [Monitoring](#monitoring)
10. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Connection Details

| Property | Value |
|----------|-------|
| Instance Name | apex-qdrant-dev |
| Private IP | 10.0.0.3 |
| HTTP API Port | 6333 |
| gRPC API Port | 6334 |
| Network | apex-memory-vpc (VPC-private) |
| Data Path | /mnt/qdrant (100GB SSD) |
| Docker Image | qdrant/qdrant:latest |

### Prerequisites

```bash
# Install Qdrant Python client
pip install qdrant-client

# Or add to requirements.txt
echo "qdrant-client>=1.7.0" >> requirements.txt
pip install -r requirements.txt
```

---

## Accessing Qdrant

### From Cloud Shell

```bash
# 1. SSH to Cloud Shell
gcloud cloud-shell ssh

# 2. Install Python client
pip install qdrant-client

# 3. Test connection
python3 << EOF
from qdrant_client import QdrantClient

client = QdrantClient(host="10.0.0.3", port=6333)
print(client.get_collections())
EOF
```

### From Compute Engine VM

```bash
# If VM is in same VPC (apex-memory-vpc)
from qdrant_client import QdrantClient

client = QdrantClient(host="10.0.0.3", port=6333)
```

### From Cloud Run

```python
# Cloud Run services with VPC connector can access Qdrant
import os
from qdrant_client import QdrantClient

qdrant_host = os.environ.get("QDRANT_HOST", "10.0.0.3")
qdrant_port = int(os.environ.get("QDRANT_PORT", "6333"))

client = QdrantClient(host=qdrant_host, port=qdrant_port)
```

### ⚠️ Local Access (Will Fail)

```python
# This will timeout - Qdrant has no external IP
client = QdrantClient(host="10.0.0.3", port=6333)
# ConnectionError: Qdrant is VPC-private only
```

**Why it fails:** Qdrant is deployed with private IP only (10.0.0.3) for security. No external access allowed.

---

## Python Client Examples

### Basic Connection

```python
from qdrant_client import QdrantClient

# Connect to Qdrant
client = QdrantClient(host="10.0.0.3", port=6333, timeout=10)

# Health check
collections = client.get_collections()
print(f"Connected! Found {len(collections.collections)} collections")
```

### Using gRPC (Faster)

```python
# gRPC is faster than HTTP for bulk operations
client = QdrantClient(host="10.0.0.3", port=6334, prefer_grpc=True)
```

### Connection with Retry Logic

```python
import time
from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import UnexpectedResponse

def connect_with_retry(max_retries=3):
    for attempt in range(max_retries):
        try:
            client = QdrantClient(host="10.0.0.3", port=6333, timeout=10)
            client.get_collections()  # Test connection
            print(f"Connected to Qdrant on attempt {attempt + 1}")
            return client
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Connection failed, retrying... ({e})")
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                raise

client = connect_with_retry()
```

---

## Collection Management

### Create Collection

```python
from qdrant_client.models import Distance, VectorParams

# Create collection with cosine similarity
client.create_collection(
    collection_name="my_collection",
    vectors_config=VectorParams(
        size=1536,  # OpenAI ada-002 embedding size
        distance=Distance.COSINE,  # COSINE, EUCLID, or DOT
    ),
)
```

### Distance Metrics

| Metric | Use Case | Range |
|--------|----------|-------|
| COSINE | Text embeddings (OpenAI, HuggingFace) | -1 to 1 |
| EUCLID | Image embeddings, general purpose | 0 to ∞ |
| DOT | Pre-normalized vectors | -∞ to ∞ |

### List Collections

```python
# Get all collections
collections = client.get_collections()

for collection in collections.collections:
    print(f"- {collection.name}")
```

### Get Collection Info

```python
# Detailed collection metadata
info = client.get_collection("my_collection")

print(f"Name: {info.config.params.vectors.size}")
print(f"Vector size: {info.config.params.vectors.size}")
print(f"Distance metric: {info.config.params.vectors.distance}")
print(f"Vectors count: {info.vectors_count}")
print(f"Points count: {info.points_count}")
```

### Update Collection

```python
# Update collection parameters
client.update_collection(
    collection_name="my_collection",
    optimizers_config={
        "indexing_threshold": 20000,  # Start indexing after 20k vectors
    },
)
```

### Delete Collection

```python
# Delete entire collection
client.delete_collection("my_collection")
```

---

## Vector Operations

### Insert Single Vector

```python
from qdrant_client.models import PointStruct

# Insert vector with payload
client.upsert(
    collection_name="my_collection",
    points=[
        PointStruct(
            id=1,
            vector=[0.1, 0.2, 0.3, ...],  # 1536-dimensional vector
            payload={
                "text": "This is a document about AI",
                "source": "blog_post",
                "timestamp": "2025-11-16T10:00:00Z",
            },
        )
    ],
)
```

### Batch Insert Vectors

```python
# Insert multiple vectors efficiently
points = [
    PointStruct(
        id=i,
        vector=[...],  # Your embedding vector
        payload={"text": f"Document {i}", "index": i},
    )
    for i in range(1000)
]

client.upsert(
    collection_name="my_collection",
    points=points,
    wait=True,  # Wait for indexing to complete
)
```

### Retrieve Vectors

```python
# Get vectors by ID
points = client.retrieve(
    collection_name="my_collection",
    ids=[1, 2, 3],
    with_vectors=True,  # Include vector data
    with_payload=True,  # Include payload
)

for point in points:
    print(f"ID: {point.id}")
    print(f"Payload: {point.payload}")
```

### Update Vector

```python
# Update existing vector (upsert replaces)
client.upsert(
    collection_name="my_collection",
    points=[
        PointStruct(
            id=1,
            vector=[...],  # New embedding
            payload={"text": "Updated document", "version": 2},
        )
    ],
)
```

### Delete Vectors

```python
# Delete by ID
client.delete(
    collection_name="my_collection",
    points_selector=[1, 2, 3],  # List of IDs
)

# Delete by filter
client.delete(
    collection_name="my_collection",
    points_selector={
        "filter": {
            "must": [{"key": "source", "match": {"value": "old_data"}}]
        }
    },
)
```

---

## Search Strategies

### Basic Similarity Search

```python
# Search for nearest vectors
results = client.search(
    collection_name="my_collection",
    query_vector=[0.1, 0.2, 0.3, ...],  # Query embedding
    limit=10,  # Top 10 results
)

for result in results:
    print(f"Score: {result.score:.4f}")
    print(f"Payload: {result.payload}")
```

### Filtered Search

```python
# Search with payload filters
results = client.search(
    collection_name="my_collection",
    query_vector=[...],
    query_filter={
        "must": [
            {"key": "source", "match": {"value": "blog_post"}},
            {"key": "timestamp", "range": {"gte": "2025-01-01"}},
        ]
    },
    limit=10,
)
```

### Search with Scoring Threshold

```python
# Only return results above similarity threshold
results = client.search(
    collection_name="my_collection",
    query_vector=[...],
    score_threshold=0.8,  # Cosine similarity > 0.8
    limit=10,
)
```

### Batch Search

```python
# Search multiple queries at once
search_queries = [
    {
        "vector": [0.1, 0.2, ...],
        "limit": 5,
        "filter": {"must": [{"key": "category", "match": {"value": "tech"}}]},
    },
    {
        "vector": [0.3, 0.4, ...],
        "limit": 5,
        "filter": {"must": [{"key": "category", "match": {"value": "science"}}]},
    },
]

batch_results = client.search_batch(
    collection_name="my_collection",
    requests=search_queries,
)
```

### Recommendation Search

```python
# Find similar items based on positive/negative examples
results = client.recommend(
    collection_name="my_collection",
    positive=[1, 2, 3],  # IDs of items to be similar to
    negative=[4, 5],  # IDs of items to be different from
    limit=10,
)
```

---

## Performance Tuning

### Indexing Configuration

```python
# Configure indexing for better search performance
client.update_collection(
    collection_name="my_collection",
    optimizers_config={
        "indexing_threshold": 20000,  # Start indexing after 20k vectors
        "memmap_threshold": 50000,  # Use memory mapping after 50k vectors
    },
    hnsw_config={
        "m": 16,  # Number of edges per node (higher = more accurate, slower)
        "ef_construct": 100,  # Construction time (higher = better index quality)
    },
)
```

### Search Performance

```python
# Adjust search parameters for speed vs accuracy
results = client.search(
    collection_name="my_collection",
    query_vector=[...],
    limit=10,
    search_params={
        "hnsw_ef": 128,  # Higher = more accurate, slower (default: 128)
        "exact": False,  # Use approximate search (faster)
    },
)
```

### Quantization (Memory Optimization)

```python
# Use scalar quantization to reduce memory usage
client.update_collection(
    collection_name="my_collection",
    quantization_config={
        "scalar": {
            "type": "int8",  # Compress float32 to int8 (4x memory reduction)
            "quantile": 0.99,
        }
    },
)
```

---

## Backup and Restore

### Create Snapshot

```bash
# SSH to Qdrant VM
gcloud compute ssh apex-qdrant-dev --zone=us-central1-a

# Create snapshot via API
curl -X POST 'http://localhost:6333/collections/my_collection/snapshots'

# List snapshots
curl 'http://localhost:6333/collections/my_collection/snapshots'

# Download snapshot
curl 'http://localhost:6333/collections/my_collection/snapshots/snapshot_name' --output snapshot.dat
```

### Manual Backup (Data Directory)

```bash
# SSH to VM
gcloud compute ssh apex-qdrant-dev --zone=us-central1-a

# Stop Docker container
docker stop qdrant

# Backup data directory
sudo tar -czf /tmp/qdrant-backup-$(date +%Y%m%d).tar.gz -C /mnt/qdrant .

# Copy to Cloud Storage
gsutil cp /tmp/qdrant-backup-*.tar.gz gs://your-backup-bucket/

# Restart container
docker start qdrant
```

### Restore from Backup

```bash
# Stop Qdrant
docker stop qdrant

# Restore data
gsutil cp gs://your-backup-bucket/qdrant-backup-20251116.tar.gz /tmp/
sudo tar -xzf /tmp/qdrant-backup-20251116.tar.gz -C /mnt/qdrant

# Restart Qdrant
docker start qdrant

# Verify
curl http://localhost:6333/collections
```

---

## Monitoring

### Health Check

```python
# Check Qdrant health
try:
    collections = client.get_collections()
    print(f"✅ Qdrant healthy: {len(collections.collections)} collections")
except Exception as e:
    print(f"❌ Qdrant unhealthy: {e}")
```

### Collection Metrics

```python
# Get collection statistics
info = client.get_collection("my_collection")

print(f"Vectors: {info.vectors_count:,}")
print(f"Points: {info.points_count:,}")
print(f"Indexed vectors: {info.indexed_vectors_count:,}")
print(f"Segments: {info.segments_count}")
```

### HTTP Health Endpoint

```bash
# From Cloud Shell or Compute Engine in VPC
curl http://10.0.0.3:6333/health
# Returns: {"title":"qdrant - vector search engine","version":"..."}
```

### Docker Logs

```bash
# SSH to VM
gcloud compute ssh apex-qdrant-dev --zone=us-central1-a

# View logs
docker logs qdrant

# Follow logs
docker logs -f qdrant

# Last 100 lines
docker logs --tail 100 qdrant
```

### Container Status

```bash
# Check if Qdrant container is running
docker ps | grep qdrant

# Restart if needed
docker restart qdrant

# Check resource usage
docker stats qdrant --no-stream
```

---

## Troubleshooting

### Connection Timeout

**Problem:** `ConnectionError: Connection timeout`

**Solutions:**
```bash
# 1. Verify you're in VPC (Cloud Shell, Compute Engine, or Cloud Run)
# Local connections will ALWAYS fail

# 2. Check VM is running
gcloud compute instances describe apex-qdrant-dev --zone=us-central1-a --format="value(status)"
# Should return: RUNNING

# 3. Check Docker container is running
gcloud compute ssh apex-qdrant-dev --zone=us-central1-a --command="docker ps | grep qdrant"

# 4. Restart Docker container if needed
gcloud compute ssh apex-qdrant-dev --zone=us-central1-a --command="docker restart qdrant"
```

### Qdrant Not Starting

**Problem:** Docker container crashes or won't start

**Solutions:**
```bash
# SSH to VM
gcloud compute ssh apex-qdrant-dev --zone=us-central1-a

# Check Docker logs for errors
docker logs qdrant

# Check disk space
df -h /mnt/qdrant

# Check permissions
ls -la /mnt/qdrant

# Restart container
docker restart qdrant

# If still failing, recreate container
docker rm qdrant
docker run -d \
  --name qdrant \
  --restart always \
  -p 6333:6333 \
  -p 6334:6334 \
  -v /mnt/qdrant:/qdrant/storage \
  qdrant/qdrant:latest
```

### Slow Search Performance

**Problem:** Search queries are taking too long

**Solutions:**
```python
# 1. Check if indexing is complete
info = client.get_collection("my_collection")
print(f"Indexed: {info.indexed_vectors_count} / {info.vectors_count}")

# 2. Adjust HNSW parameters
client.update_collection(
    collection_name="my_collection",
    hnsw_config={
        "m": 16,  # Reduce for faster search (less accurate)
        "ef_construct": 100,
    },
)

# 3. Use quantization
client.update_collection(
    collection_name="my_collection",
    quantization_config={"scalar": {"type": "int8", "quantile": 0.99}},
)

# 4. Reduce search ef parameter
results = client.search(
    collection_name="my_collection",
    query_vector=[...],
    limit=10,
    search_params={"hnsw_ef": 64},  # Lower = faster (less accurate)
)
```

### Out of Memory

**Problem:** Qdrant crashes with OOM errors

**Solutions:**
```bash
# 1. Check memory usage
gcloud compute ssh apex-qdrant-dev --zone=us-central1-a --command="free -h"

# 2. Enable quantization (4x memory reduction)
# See Performance Tuning > Quantization section

# 3. Enable memory mapping for large collections
# See Performance Tuning > Indexing Configuration section

# 4. Upgrade VM to larger machine type (production)
# e2-medium (4GB) → e2-standard-4 (16GB)
```

### Data Corruption

**Problem:** Collection is corrupt or data is missing

**Solutions:**
```bash
# 1. Restore from snapshot
# See Backup and Restore section

# 2. Rebuild collection from source
# Delete collection and re-ingest all vectors

# 3. Check disk integrity
gcloud compute ssh apex-qdrant-dev --zone=us-central1-a
sudo fsck -n /dev/sdb
```

---

## Advanced Features

### Named Vectors (Multi-Modal)

```python
# Create collection with multiple vector types
from qdrant_client.models import VectorParams

client.create_collection(
    collection_name="multi_modal",
    vectors_config={
        "text": VectorParams(size=1536, distance=Distance.COSINE),
        "image": VectorParams(size=512, distance=Distance.COSINE),
    },
)

# Insert point with multiple vectors
client.upsert(
    collection_name="multi_modal",
    points=[
        PointStruct(
            id=1,
            vector={"text": [...], "image": [...]},
            payload={"title": "AI Article with Image"},
        )
    ],
)

# Search specific vector type
results = client.search(
    collection_name="multi_modal",
    query_vector=("text", [...]),  # Specify vector name
    limit=10,
)
```

### Payload Indexing

```python
# Create index on payload field for faster filtering
client.create_payload_index(
    collection_name="my_collection",
    field_name="category",
    field_schema="keyword",  # keyword, integer, float, geo, text
)
```

### Scroll API (Iterate All Vectors)

```python
# Iterate through all vectors in collection
offset = None
all_points = []

while True:
    batch, offset = client.scroll(
        collection_name="my_collection",
        limit=100,
        offset=offset,
        with_payload=True,
        with_vectors=False,
    )
    all_points.extend(batch)
    if offset is None:
        break

print(f"Retrieved {len(all_points)} total vectors")
```

---

## Quick Reference

### Common Commands

```python
# Connect
from qdrant_client import QdrantClient
client = QdrantClient(host="10.0.0.3", port=6333)

# Create collection
from qdrant_client.models import Distance, VectorParams
client.create_collection("my_collection", vectors_config=VectorParams(size=1536, distance=Distance.COSINE))

# Insert vector
from qdrant_client.models import PointStruct
client.upsert("my_collection", points=[PointStruct(id=1, vector=[...], payload={"text": "..."})])

# Search
results = client.search("my_collection", query_vector=[...], limit=10)

# Delete collection
client.delete_collection("my_collection")
```

### Useful URLs

- **HTTP API:** http://10.0.0.3:6333
- **Health Check:** http://10.0.0.3:6333/health
- **Collections:** http://10.0.0.3:6333/collections
- **Official Docs:** https://qdrant.tech/documentation/

---

**Last Updated:** 2025-11-16
**Status:** ✅ Complete
**Qdrant Version:** latest (Docker image)
