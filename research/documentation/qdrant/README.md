# Qdrant Vector Database

**Tier:** 1 (Official Documentation)
**Date Accessed:** 2025-10-06
**Target Version:** Qdrant 1.12+
**Latest Release:** 1.12.0 (Released October 8, 2024)

## Official Documentation Links

### Main Documentation
- **Qdrant Documentation:** https://qdrant.tech/documentation/
- **Official Website:** https://qdrant.tech/
- **GitHub Repository:** https://github.com/qdrant/qdrant (20k+ stars)

### Key Documentation Sections

#### 1. Getting Started
- **Overview:** https://qdrant.tech/documentation/
- **Local Quickstart:** https://qdrant.tech/documentation/quickstart/
- **Cloud Quickstart:** Managed Qdrant Cloud offering

#### 2. Guides
- **Installation:** https://qdrant.tech/documentation/guides/installation/
- **Configuration:** https://qdrant.tech/documentation/guides/configuration/
- **Distributed Deployment:** https://qdrant.tech/documentation/guides/distributed_deployment/

#### 3. Features & Tutorials
- **Vector Search Basics**
- **Advanced Retrieval**
- **Database Usage**
- **Semantic Search**
- **Recommendation Systems**

#### 4. API Reference
- REST API documentation
- gRPC API support
- Client SDKs for multiple languages

#### 5. Version-Specific
- **Qdrant 1.12 Release:** https://qdrant.tech/blog/qdrant-1.12.x/

## Key Concepts & Architecture

### What is Qdrant?

Qdrant (read: quadrant) is an **AI-native vector database and vector search engine** written in Rust. It provides:
- Fast and scalable vector similarity search
- RESTful API with OpenAPI specification
- gRPC support for high-performance operations
- Extended filtering capabilities
- Production-ready cloud-native architecture

### Core Architecture

1. **Collections** - Named sets of points (vectors) with a defined configuration
2. **Points** - Vectors with associated payloads (metadata)
3. **Vectors** - Dense or sparse numerical representations
4. **Payloads** - JSON-like structures with metadata
5. **Indexes** - Optimized structures for fast retrieval

### Vector Types
- **Dense vectors** - Traditional embeddings (e.g., [0.1, 0.2, 0.3, ...])
- **Sparse vectors** - Efficient for high-dimensional sparse data
- **Named vectors** - Multiple vector types per point
- **Multivector** - Multiple dense vectors per point

## Installation

### Docker (Recommended for Development)
```bash
# Pull latest image
docker pull qdrant/qdrant

# Run Qdrant
docker run -p 6333:6333 -p 6334:6334 \
    -v $(pwd)/qdrant_storage:/qdrant/storage:z \
    qdrant/qdrant
```

### Docker Compose
```yaml
version: '3.8'
services:
  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"  # REST API
      - "6334:6334"  # gRPC API
    volumes:
      - ./qdrant_storage:/qdrant/storage
    environment:
      - QDRANT_ALLOW_RECOVERY_MODE=true
```

### Production Deployment
```bash
# Kubernetes via Helm
helm repo add qdrant https://qdrant.github.io/qdrant-helm
helm install qdrant qdrant/qdrant

# Binary installation (Linux)
wget https://github.com/qdrant/qdrant/releases/download/v1.12.0/qdrant-x86_64-unknown-linux-gnu.tar.gz
tar -xzf qdrant-x86_64-unknown-linux-gnu.tar.gz
./qdrant
```

## Basic Usage

### Python Client Setup
```bash
pip install qdrant-client
```

### Initialize Client
```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

# Local connection
client = QdrantClient(url="http://localhost:6333")

# Cloud connection
client = QdrantClient(
    url="https://xyz.cloud.qdrant.io",
    api_key="your-api-key"
)

# In-memory (for testing)
client = QdrantClient(":memory:")
```

### Create Collection
```python
from qdrant_client.models import Distance, VectorParams

client.create_collection(
    collection_name="documents",
    vectors_config=VectorParams(
        size=1536,  # OpenAI embedding dimension
        distance=Distance.COSINE
    )
)

# With multiple vector types
client.create_collection(
    collection_name="multi_modal",
    vectors_config={
        "text": VectorParams(size=768, distance=Distance.COSINE),
        "image": VectorParams(size=512, distance=Distance.COSINE)
    }
)
```

### Insert Points (Vectors)
```python
from qdrant_client.models import PointStruct

# Insert single point
client.upsert(
    collection_name="documents",
    points=[
        PointStruct(
            id=1,
            vector=[0.1, 0.2, 0.3, ...],  # 1536 dimensions
            payload={
                "title": "Introduction to Vector Databases",
                "category": "tech",
                "timestamp": "2025-10-06T10:00:00Z"
            }
        )
    ]
)

# Batch insert
points = [
    PointStruct(id=i, vector=vector, payload=metadata)
    for i, (vector, metadata) in enumerate(data)
]
client.upsert(collection_name="documents", points=points)
```

### Search (Query)
```python
# Basic vector search
results = client.query_points(
    collection_name="documents",
    query=[0.2, 0.1, 0.9, ...],  # Query vector
    limit=10
)

# With filtering
from qdrant_client.models import Filter, FieldCondition, MatchValue

results = client.query_points(
    collection_name="documents",
    query=[0.2, 0.1, 0.9, ...],
    query_filter=Filter(
        must=[
            FieldCondition(
                key="category",
                match=MatchValue(value="tech")
            )
        ]
    ),
    limit=10
)

# With score threshold
results = client.query_points(
    collection_name="documents",
    query=[0.2, 0.1, 0.9, ...],
    score_threshold=0.8,
    limit=10
)
```

### Update & Delete
```python
# Update point payload
client.set_payload(
    collection_name="documents",
    payload={"views": 100},
    points=[1, 2, 3]
)

# Delete points
client.delete(
    collection_name="documents",
    points_selector=[1, 2, 3]
)

# Delete with filter
from qdrant_client.models import FilterSelector

client.delete(
    collection_name="documents",
    points_selector=FilterSelector(
        filter=Filter(
            must=[
                FieldCondition(key="category", match=MatchValue(value="old"))
            ]
        )
    )
)
```

## Qdrant 1.12 New Features

### 1. Distance Matrix API
Calculate pairwise distances between multiple vectors efficiently.

```python
from qdrant_client.models import DistanceMatrixRequest

# Calculate distances between points
response = client.distance_matrix(
    collection_name="documents",
    sample=[1, 2, 3, 4],  # Point IDs
    limit=10
)

# Output formats
# "Pairs": Simple representation [(id1, id2, distance), ...]
# "Offsets": CSR sparse matrix format for advanced use
```

**Use Cases:**
- Clustering analysis
- Dimensionality reduction preparation
- Data exploration and visualization
- Similarity matrix computation

### 2. Facet API (Faceted Search)
Count and aggregate unique values in payload fields.

```python
from qdrant_client.models import FacetRequest, FacetParams

# Count unique values in category field
facets = client.facet(
    collection_name="documents",
    request=FacetRequest(
        key="category",
        limit=100
    )
)

# With filtering
facets = client.facet(
    collection_name="documents",
    request=FacetRequest(
        key="category",
        filter=Filter(
            must=[
                FieldCondition(key="year", range={"gte": 2024})
            ]
        )
    )
)
```

**Use Cases:**
- E-commerce filtering (show available categories, brands)
- Analytics dashboards
- Dynamic UI generation
- Data distribution analysis

### 3. On-Disk Indexing

#### Text Index on Disk
Reduce memory usage for text indexes.

```python
# Enable on-disk text index
client.create_collection(
    collection_name="documents",
    vectors_config=VectorParams(size=768, distance=Distance.COSINE),
    on_disk_payload=True
)

# Or update existing collection
client.update_collection(
    collection_name="documents",
    on_disk_payload=True
)
```

#### Geo Index on Disk
Store geographic indexes on disk instead of memory.

```python
# Create collection with geo field
client.upsert(
    collection_name="locations",
    points=[
        PointStruct(
            id=1,
            vector=[...],
            payload={
                "location": {"lat": 40.7128, "lon": -74.0060},
                "name": "New York"
            }
        )
    ]
)

# Configure geo index on disk
# Set in collection configuration
```

**Benefits:**
- Lower memory footprint
- Handle larger datasets
- Cost optimization for memory-intensive deployments

## Advanced Features

### Hybrid Search (Combining Multiple Vectors)
```python
# Search with multiple vectors
from qdrant_client.models import Prefetch, Query

results = client.query_points(
    collection_name="multi_modal",
    prefetch=[
        Prefetch(query=[...], using="text", limit=20),
        Prefetch(query=[...], using="image", limit=20)
    ],
    query=Query(fusion="rrf")  # Reciprocal Rank Fusion
)
```

### Multitenancy with Payloads
```python
# Isolate data by tenant
client.upsert(
    collection_name="shared_documents",
    points=[
        PointStruct(
            id=1,
            vector=[...],
            payload={"tenant_id": "tenant-a", "content": "..."}
        )
    ]
)

# Query with tenant isolation
results = client.query_points(
    collection_name="shared_documents",
    query=[...],
    query_filter=Filter(
        must=[FieldCondition(key="tenant_id", match=MatchValue(value="tenant-a"))]
    )
)
```

### Snapshots & Backups
```python
# Create snapshot
snapshot = client.create_snapshot(collection_name="documents")

# List snapshots
snapshots = client.list_snapshots(collection_name="documents")

# Restore from snapshot
client.recover_snapshot(
    collection_name="documents",
    snapshot_name="snapshot-2025-10-06"
)
```

### Vector Quantization
Reduce memory usage and improve performance with quantization.

```python
from qdrant_client.models import ScalarQuantization, ScalarType

client.update_collection(
    collection_name="documents",
    quantization_config=ScalarQuantization(
        type=ScalarType.INT8,
        quantile=0.99,
        always_ram=True
    )
)
```

## Best Practices

### Performance Optimization

#### 1. Choose Appropriate Distance Metric
```python
# For normalized vectors (embeddings) - use Cosine or Dot product
Distance.COSINE  # Range: [0, 2]
Distance.DOT     # Faster, use for normalized vectors

# For unnormalized vectors
Distance.EUCLID  # L2 distance
Distance.MANHATTAN  # L1 distance
```

#### 2. Indexing Strategy
```python
from qdrant_client.models import HnswConfigDiff

# HNSW index tuning
client.update_collection(
    collection_name="documents",
    hnsw_config=HnswConfigDiff(
        m=16,              # Number of edges per node (default: 16)
        ef_construct=100,  # Construction time accuracy (default: 100)
    )
)

# At search time
results = client.query_points(
    collection_name="documents",
    query=[...],
    search_params={"hnsw_ef": 128},  # Search time accuracy
    limit=10
)
```

#### 3. Payload Indexing
```python
# Create index on frequently filtered fields
client.create_payload_index(
    collection_name="documents",
    field_name="category",
    field_schema="keyword"
)

# Index types
# "keyword" - exact matching
# "integer" - numerical range queries
# "float" - floating point ranges
# "geo" - geographic filtering
# "text" - full-text search
```

#### 4. Batch Operations
```python
# Batch upsert for better performance
batch_size = 100
for i in range(0, len(points), batch_size):
    batch = points[i:i+batch_size]
    client.upsert(collection_name="documents", points=batch)
```

### Scaling & High Availability

#### Distributed Deployment
```python
# Configure cluster
# In qdrant config.yaml:
"""
cluster:
  enabled: true
  p2p:
    port: 6335
  consensus:
    tick_period_ms: 100
"""
```

#### Replication
```python
# Set replication factor
client.update_collection(
    collection_name="documents",
    replication_factor=3  # 3 replicas
)
```

### Monitoring

```python
# Collection info
info = client.get_collection(collection_name="documents")
print(f"Points count: {info.points_count}")
print(f"Vectors count: {info.vectors_count}")
print(f"Indexed vectors: {info.indexed_vectors_count}")

# Health check
health = client.health()
print(health)
```

## Integration Patterns

### With LangChain
```python
from langchain.vectorstores import Qdrant
from langchain.embeddings import OpenAIEmbeddings

embeddings = OpenAIEmbeddings()
vectorstore = Qdrant(
    client=client,
    collection_name="documents",
    embeddings=embeddings
)

# Add documents
vectorstore.add_texts(
    texts=["Text 1", "Text 2"],
    metadatas=[{"source": "doc1"}, {"source": "doc2"}]
)

# Search
results = vectorstore.similarity_search("query text", k=5)
```

### With LlamaIndex
```python
from llama_index.vector_stores import QdrantVectorStore
from llama_index import VectorStoreIndex, Document

vector_store = QdrantVectorStore(
    client=client,
    collection_name="documents"
)

documents = [Document(text="...", metadata={...})]
index = VectorStoreIndex.from_documents(
    documents,
    vector_store=vector_store
)
```

### Async Python Client
```python
from qdrant_client import AsyncQdrantClient

async def search():
    client = AsyncQdrantClient(url="http://localhost:6333")

    results = await client.query_points(
        collection_name="documents",
        query=[...],
        limit=10
    )

    await client.close()
    return results
```

## Relevant Features for Apex Memory System

### Temporal Search
```python
# Time-aware search with payload filtering
from datetime import datetime, timedelta

recent_threshold = (datetime.now() - timedelta(days=7)).isoformat()

results = client.query_points(
    collection_name="documents",
    query=[...],
    query_filter=Filter(
        must=[
            FieldCondition(
                key="timestamp",
                range={"gte": recent_threshold}
            )
        ]
    ),
    limit=10
)
```

### Multi-modal Search
```python
# Store and search multiple vector types
client.create_collection(
    collection_name="multi_modal_docs",
    vectors_config={
        "title": VectorParams(size=768, distance=Distance.COSINE),
        "content": VectorParams(size=1536, distance=Distance.COSINE),
        "summary": VectorParams(size=384, distance=Distance.COSINE)
    }
)

# Search across multiple vectors with fusion
results = client.query_points(
    collection_name="multi_modal_docs",
    prefetch=[
        Prefetch(query=title_vector, using="title", limit=20),
        Prefetch(query=content_vector, using="content", limit=20)
    ],
    query=Query(fusion="rrf"),
    limit=10
)
```

### Recommendation System
```python
# Recommend similar items based on positive/negative examples
from qdrant_client.models import RecommendStrategy

results = client.recommend(
    collection_name="documents",
    positive=[1, 2, 3],  # Similar to these
    negative=[99],       # But not like this
    limit=10,
    strategy=RecommendStrategy.AVERAGE_VECTOR
)
```

## Configuration

### Server Configuration (config.yaml)
```yaml
service:
  host: 0.0.0.0
  http_port: 6333
  grpc_port: 6334

storage:
  storage_path: ./storage
  on_disk_payload: true

# Performance tuning
performance:
  max_search_threads: 0  # Auto-detect

# Optimization
optimizers:
  deleted_threshold: 0.2
  vacuum_min_vector_number: 1000

# Logging
log_level: INFO
```

## Monitoring & Maintenance

### Metrics & Telemetry
```python
# Collection metrics
collection_info = client.get_collection("documents")
print(f"Segments: {collection_info.segments_count}")
print(f"Status: {collection_info.status}")

# Point count
count = client.count(collection_name="documents")
print(f"Total points: {count.count}")
```

### Optimization
```python
# Trigger optimization manually
client.update_collection(
    collection_name="documents",
    optimizer_config={
        "deleted_threshold": 0.2,
        "vacuum_min_vector_number": 1000,
        "max_segment_size": 200000
    }
)
```

## Learning Resources

### Official Resources
- **Documentation:** https://qdrant.tech/documentation/
- **Blog:** https://qdrant.tech/blog/ (tutorials, case studies)
- **GitHub:** https://github.com/qdrant/qdrant (source code, examples)
- **Discord Community:** Active support channel

### Key Topics for Memory System
1. Collection design and management
2. Filter optimization for temporal queries
3. Multi-vector search patterns
4. Payload indexing strategies
5. Distributed deployment
6. Performance tuning

## Summary

Qdrant is a modern, purpose-built vector database with excellent performance, scalability, and developer experience. Version 1.12+ introduces powerful features like Distance Matrix API, Faceting, and on-disk indexing that make it ideal for production AI applications.

**Key Strengths for Apex Memory:**
- Purpose-built for vector search (vs. extension like pgvector)
- Excellent filtering capabilities for temporal queries
- Multi-vector support for hybrid search
- Built-in clustering and replication
- Active development and modern architecture
- Cloud-native with Kubernetes support
- Rich API with gRPC for performance
- On-disk indexing for cost optimization (v1.12+)
- Faceting API for analytics (v1.12+)

**Recommended Setup:**
- Qdrant 1.12+ (latest features)
- Docker deployment for development
- Kubernetes/distributed for production
- HNSW indexes with cosine distance for embeddings
- Payload indexes on temporal and category fields
- Replication factor 3 for high availability
