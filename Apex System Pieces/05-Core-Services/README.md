# 05 - Core Services

## 🎯 Purpose

Provides reusable business logic services used throughout the system. These services encapsulate complex operations like document parsing, entity extraction, embeddings generation, and cross-cutting concerns like circuit breaking, distributed locking, and idempotency.

**Why Services Layer?**
- Separation of concerns (business logic vs. API routes)
- Reusability across multiple components
- Easier testing with mocks
- Centralized complex operations

## 🛠 Technical Stack

### Document Processing
- **Docling 2.55.1:** Advanced PDF, DOCX, PPTX parsing
- **pypdf 6.1.1:** PDF text extraction
- **python-docx 1.2.0:** Word document parsing
- **python-pptx 1.0.2:** PowerPoint parsing

### AI & Embeddings
- **OpenAI:** GPT-4o for entity extraction, text-embedding-3-small
- **Sentence-Transformers:** Local embeddings (fallback)
- **Graphiti-core 0.22.0:** Temporal knowledge graph

### Resilience & Reliability
- **Custom circuit breaker:** Fault tolerance
- **Distributed locking (Redis):** Concurrency control
- **Idempotency keys:** Prevent duplicate operations

## 📂 Key Files (14 Services)

### Document Processing Services

**1. document_parser.py** (16,155 bytes)
```python
class DocumentParser:
    """Multi-format document parsing with Docling."""
    def parse(file_path: str) -> ParsedDocument:
        # Handles: PDF, DOCX, PPTX, HTML, Markdown, TXT
```

**2. entity_extractor.py** (15,453 bytes)
```python
class EntityExtractor:
    """Extract entities using OpenAI GPT-4o."""
    def extract(text: str) -> List[Entity]:
        # Returns: Entity name, type, confidence
```

**3. embedding_service.py** (9,017 bytes)
```python
class EmbeddingService:
    """Generate embeddings (OpenAI or Sentence-Transformers)."""
    def generate_embedding(text: str) -> List[float]:
        # Returns: 1536-dimensional vector
```

### Graph & Temporal Services

**4. graphiti_service.py** (40,125 bytes)
```python
class GraphitiService:
    """Temporal knowledge graph integration."""
    def create_episode(text: str, metadata: dict) -> Episode:
        # Creates temporal entity versions
```

**5. graph_analytics_service.py** (19,472 bytes)
```python
class GraphAnalyticsService:
    """Neo4j graph analytics (centrality, communities)."""
    def detect_communities() -> List[Community]:
        # Louvain algorithm for community detection
```

**6. graph_refactoring_service.py** (19,872 bytes)
```python
class GraphRefactoringService:
    """Graph quality maintenance (merge duplicates, prune)."""
    def merge_duplicate_entities() -> int:
        # Similarity-based entity deduplication
```

### Database & Orchestration

**7. database_writer.py** (47,604 bytes)
```python
class DatabaseWriteOrchestrator:
    """Saga pattern multi-DB writes with rollback."""
    def write_document(doc, chunks, entities, embeddings) -> Result:
        # Parallel writes to Neo4j, PostgreSQL, Qdrant, Redis
        # Rollback all on any failure
```

**8. staging_manager.py** (10,573 bytes)
```python
class StagingManager:
    """Local staging lifecycle (/tmp/apex-staging/)."""
    def create_staging(source: str, doc_id: str) -> Path:
        # Creates structured staging directory
```

### Authentication & User Services

**9. auth_service.py** (8,027 bytes)
```python
class AuthService:
    """User authentication and JWT token management."""
    def login(email: str, password: str) -> str:
        # Returns JWT access token
```

**10. conversation_service.py** (18,480 bytes)
```python
class ConversationService:
    """Conversation CRUD and history management."""
    def create_conversation(user_id: UUID, title: str) -> Conversation:
```

**11. achievement_tracker.py** (10,119 bytes)
```python
class AchievementTracker:
    """Minimal gamification tracking."""
    def check_achievements(user_id: UUID) -> List[Achievement]:
        # First query, 10 queries, 100 queries, etc.
```

### Resilience Services

**12. circuit_breaker.py** (7,754 bytes)
```python
class CircuitBreaker:
    """Fault tolerance for external service calls."""
    @circuit_breaker(failure_threshold=5, timeout=60)
    def call_external_api():
        # Opens circuit after 5 failures, prevents cascading failures
```

**13. distributed_lock.py** (8,028 bytes)
```python
class DistributedLock:
    """Redis-based distributed locking."""
    with DistributedLock("resource-id"):
        # Only one worker can execute this block
```

**14. idempotency.py** (11,599 bytes)
```python
class IdempotencyManager:
    """Prevent duplicate operations with idempotency keys."""
    @idempotent(key_generator=lambda doc_id: f"ingest:{doc_id}")
    def ingest_document(doc_id):
        # Same doc_id won't be processed twice
```

## 🔗 Dependencies

### Depends On:
1. **Database Infrastructure** (01) - Direct database access
2. **Data Models** (06) - Pydantic models for validation
3. **Configuration** (11) - Settings for API keys, connection strings

### Optional:
- **Graphiti Service** - Requires `GRAPHITI_ENABLED=true` in config

## 🔌 Interfaces

### Consumed By:
1. **Workflow Orchestration** (02) - Temporal activities use these services
2. **Backend API** (03) - Direct service calls from endpoints
3. **Database Writers** (07) - Uses DatabaseWriteOrchestrator

### Example Usage:

```python
# From a Temporal activity
from apex_memory.services.document_parser import DocumentParser
from apex_memory.services.embedding_service import EmbeddingService

# Parse document
parser = DocumentParser()
parsed = parser.parse("/path/to/document.pdf")

# Generate embeddings
embedding_service = EmbeddingService()
embeddings = [embedding_service.generate_embedding(chunk.text) for chunk in parsed.chunks]
```

## ⚙️ Configuration

### Service Initialization

```python
# From apex-memory-system/src/apex_memory/main.py

# Embedding service (shared between ingestion and query)
embedding_service = EmbeddingService()

# Graphiti service (conditional)
graphiti_service = None
if settings.graphiti_enabled:
    graphiti_service = GraphitiService(
        neo4j_uri=settings.graphiti_uri,
        neo4j_user=settings.graphiti_user,
        neo4j_password=settings.graphiti_password,
        openai_api_key=settings.openai_api_key,
        llm_model=settings.graphiti_llm_model,
    )
```

### Environment Variables

```bash
# OpenAI (required for entity extraction + embeddings)
OPENAI_API_KEY=sk-...

# Graphiti (optional - temporal intelligence)
GRAPHITI_ENABLED=true
GRAPHITI_URI=bolt://localhost:7687
GRAPHITI_USER=neo4j
GRAPHITI_PASSWORD=apexmemory2024
GRAPHITI_LLM_MODEL=gpt-4o
GRAPHITI_SMALL_MODEL=gpt-4o-mini
GRAPHITI_EMBEDDING_MODEL=text-embedding-3-small

# Staging directory (local filesystem)
STAGING_BASE_DIR=/tmp/apex-staging

# Circuit breaker settings
CIRCUIT_BREAKER_FAILURE_THRESHOLD=5
CIRCUIT_BREAKER_TIMEOUT=60

# Distributed lock TTL
DISTRIBUTED_LOCK_TTL=30
```

## 📊 Service Usage Patterns

### Document Parsing Flow

```python
# 1. Parse document
parser = DocumentParser()
parsed_doc = parser.parse(file_path)
# Result: {title, chunks: [...], metadata: {...}}

# 2. Extract entities
extractor = EntityExtractor()
entities = extractor.extract(parsed_doc.full_text)
# Result: [{name: "ACME Corp", type: "Organization", confidence: 0.95}, ...]

# 3. Generate embeddings
embedding_service = EmbeddingService()
chunk_embeddings = [
    embedding_service.generate_embedding(chunk.text)
    for chunk in parsed_doc.chunks
]
# Result: [[0.123, -0.456, ...], ...] (1536 dimensions each)
```

### Saga Pattern (Database Writer)

```python
# Atomic multi-DB write with rollback
orchestrator = DatabaseWriteOrchestrator(neo4j, postgres, qdrant, redis)

result = orchestrator.write_document(
    document=doc,
    chunks=chunks,
    entities=entities,
    embeddings=embeddings
)

# If any database write fails:
# 1. Rolls back all previous writes
# 2. Returns failure status
# 3. Logs error details

if result.success:
    print(f"Document {result.document_id} written to all databases")
else:
    print(f"Rollback performed: {result.error}")
```

### Circuit Breaker Pattern

```python
# Protect against external service failures
breaker = CircuitBreaker(failure_threshold=5, timeout=60)

@breaker.protected
def call_openai_api(text: str):
    # If OpenAI fails 5 times in a row:
    # - Circuit opens (stops calling OpenAI)
    # - Returns cached/fallback response
    # - Retries after 60 seconds
    return openai.Completion.create(...)

# Manual circuit check
if breaker.is_open():
    return cached_response
else:
    return call_openai_api(text)
```

## 🔧 Testing

### Unit Tests

```bash
# Test individual services
pytest tests/unit/test_document_parser.py -v
pytest tests/unit/test_entity_extractor.py -v
pytest tests/unit/test_embedding_service.py -v
pytest tests/unit/test_graphiti_service.py -v

# Test resilience patterns
pytest tests/unit/test_circuit_breaker.py -v
pytest tests/unit/test_distributed_lock.py -v
pytest tests/unit/test_idempotency.py -v
```

### Integration Tests

```bash
# Test services with real databases
pytest tests/integration/test_database_writer.py -v
pytest tests/integration/test_staging_manager.py -v

# Test end-to-end service orchestration
pytest tests/integration/test_document_ingestion_services.py -v
```

## 📈 Performance Characteristics

### Service Latency (Typical Document)

| Service | Latency | Notes |
|---------|---------|-------|
| **DocumentParser** | 2-10s | Depends on page count |
| **EntityExtractor** | 1-3s | OpenAI API call |
| **EmbeddingService** | 500ms-2s | Batch size dependent |
| **GraphitiService** | 500ms-1s | Episode creation |
| **DatabaseWriteOrchestrator** | 1-3s | Parallel writes |
| **StagingManager** | 50-100ms | Local filesystem ops |
| **CircuitBreaker** | <1ms | Overhead negligible |

### Resource Usage

- **Memory:** 200-500MB per service (embedding models in memory)
- **CPU:** Spikes during parsing, entity extraction
- **Disk:** Staging uses ~2MB per document (temporary)

## 🚨 Known Limitations

1. **OpenAI Dependency** - Entity extraction requires OpenAI API key
2. **Graphiti Optional** - System works without it (fallback to Neo4j only)
3. **Circuit Breaker State** - Not persisted across restarts (in-memory)
4. **Distributed Lock** - Requires Redis (single point of failure)
5. **Staging Cleanup** - Manual cleanup if workflow fails before cleanup activity

## 🔍 Troubleshooting

### "OpenAI rate limit exceeded"

```python
# Circuit breaker will open after 5 failures
# Implement exponential backoff or request rate increase from OpenAI

# Fallback: Use Sentence-Transformers for embeddings
# (Entity extraction has no local fallback currently)
```

### "Graphiti initialization failed"

```bash
# Check Neo4j connection
cypher-shell -u neo4j -p apexmemory2024 "RETURN 1"

# Disable Graphiti if not needed
export GRAPHITI_ENABLED=false
```

### "Staging directory full"

```bash
# Check disk space
df -h /tmp

# Clean old staging directories
rm -rf /tmp/apex-staging/*/
```

---

**Previous Component:** [04-Query-Intelligence](../04-Query-Intelligence/README.md)
**Next Component:** [06-Data-Models](../06-Data-Models/README.md)
