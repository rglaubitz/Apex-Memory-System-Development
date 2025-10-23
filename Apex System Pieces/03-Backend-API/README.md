# 03 - Backend API (FastAPI)

## 🎯 Purpose

Provides RESTful HTTP API for all system functionality: document ingestion, intelligent querying, streaming chat, authentication, and administrative operations. Built with FastAPI for high performance and automatic OpenAPI documentation.

**Why FastAPI?**
- Async/await support for high concurrency
- Automatic OpenAPI (Swagger) documentation
- Pydantic data validation
- Built-in dependency injection
- Native SSE (Server-Sent Events) support

## 🛠 Technical Stack

### Core Framework
- **FastAPI:** Modern async web framework
- **Uvicorn:** ASGI server (production-grade)
- **Pydantic:** Data validation and serialization
- **Python 3.11+:** Type hints and performance

### Key Libraries
- **Anthropic SDK:** Claude streaming chat integration
- **python-multipart:** File upload support
- **python-jose:** JWT token handling
- **passlib:** Password hashing (bcrypt)

## 📂 Key Files

### Main Application
- `apex-memory-system/src/apex_memory/main.py` (313 lines)
  - FastAPI app initialization
  - All router includes
  - CORS + Security headers middleware
  - Embedded service initialization (QueryRouter, GraphitiService)
  - Health and metrics endpoints

### API Routers (13 total)

#### Core Functionality
- `api/ingestion.py` (30,466 bytes)
  - `POST /api/v1/ingest` - Upload and ingest documents
  - `GET /api/v1/document/{uuid}` - Retrieve document metadata
  - `DELETE /api/v1/document/{uuid}` - Delete document
  - Triggers Temporal workflows

- `api/query.py` (25,602 bytes)
  - `POST /api/v1/query/` - Execute intelligent queries
  - `GET /api/v1/query/explain` - Explain query routing decision
  - `GET /api/v1/query/cache/stats` - Cache statistics
  - `DELETE /api/v1/query/cache` - Invalidate cache

- `api/chat_stream.py` (11,908 bytes)
  - `POST /api/v1/chat/stream` - Streaming chat with Claude (SSE)
  - 5 Claude tools: search_knowledge_graph, get_entity_relationships, get_temporal_timeline, find_similar_documents, get_graph_statistics
  - Progressive artifact rendering

#### Authentication & Users
- `api/auth.py` (4,141 bytes)
  - `POST /api/v1/auth/register` - User registration
  - `POST /api/v1/auth/login` - JWT token generation
  - `GET /api/v1/auth/me` - Current user profile
  - `POST /api/v1/auth/refresh` - Token refresh

- `api/conversations.py` (9,841 bytes)
  - `GET /api/v1/conversations` - List user conversations
  - `POST /api/v1/conversations` - Create conversation
  - `GET /api/v1/conversations/{id}` - Get conversation history
  - `DELETE /api/v1/conversations/{id}` - Delete conversation

#### AI Features
- `api/briefings.py` (5,294 bytes)
  - `GET /api/v1/briefings/daily` - Generate AI daily briefing
  - `POST /api/v1/briefings/mark-read` - Mark briefing as read

- `api/achievements.py` (3,473 bytes)
  - `GET /api/v1/achievements` - Get user achievements (minimal gamification)

#### Data Operations
- `api/messages.py` (12,532 bytes)
  - `POST /api/v1/messages` - Ingest message episodes
  - `GET /api/v1/messages/{uuid}` - Retrieve message
  - Message-specific ingestion pipeline

- `api/patterns.py` (15,667 bytes)
  - `GET /api/v1/patterns/temporal` - Detect temporal patterns
  - `GET /api/v1/patterns/communities` - Entity community detection
  - GraphRAG community analysis

- `api/graph.py` (16,669 bytes)
  - `GET /api/v1/graph/entity/{name}` - Entity graph neighborhood
  - `GET /api/v1/graph/path/{from}/{to}` - Shortest path between entities
  - `GET /api/v1/graph/stats` - Graph statistics

- `api/analytics.py` (22,026 bytes)
  - `GET /api/v1/analytics/overview` - System analytics
  - `GET /api/v1/analytics/query-performance` - Query performance stats
  - `GET /api/v1/analytics/ingestion-stats` - Ingestion metrics

#### Administration
- `api/maintenance.py` (27,089 bytes)
  - `POST /api/v1/maintenance/rebuild-index` - Rebuild search indices
  - `POST /api/v1/maintenance/clear-cache` - Clear all caches
  - `GET /api/v1/maintenance/health` - Detailed health check

- `api/export.py` (2,287 bytes)
  - `GET /api/v1/export/conversation/{id}` - Export as Markdown/PDF

### Middleware
- `SecurityHeadersMiddleware` (main.py:48-94)
  - Content Security Policy (CSP)
  - HTTP Strict Transport Security (HSTS)
  - X-Frame-Options, X-Content-Type-Options
  - Referrer Policy, Permissions Policy

## 🔗 Dependencies

### Depends On:
1. **Database Infrastructure** (01) - All database connections
2. **Workflow Orchestration** (02) - Triggers Temporal workflows
3. **Query Intelligence** (04) - QueryRouter instance
4. **Core Services** (05) - EmbeddingService, GraphitiService
5. **Database Writers** (07) - DatabaseWriteOrchestrator
6. **Data Models** (06) - Pydantic request/response models
7. **Cache Layer** (09) - QueryCache for results
8. **Authentication** (12) - JWT validation, user management

## 🔌 Interfaces

### Provides:
- **HTTP REST API** - Port 8000 (default)
- **OpenAPI Documentation** - http://localhost:8000/docs (Swagger UI)
- **ReDoc** - http://localhost:8000/redoc (Alternative docs)
- **Prometheus Metrics** - http://localhost:8000/metrics

### Consumed By:
1. **Frontend Application** (08) - React SPA makes API calls
2. **MCP Server** (external) - Claude Desktop integration
3. **External Clients** - Any HTTP client (curl, Postman, etc.)

## ⚙️ Configuration

### Server Settings

```python
# From src/apex_memory/main.py

app = FastAPI(
    title="Apex Memory System",
    description="Multi-database intelligence platform for sub-second answers to complex business questions",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)
```

### CORS Configuration

```python
# Allow frontend on different port (development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Environment Variables

```bash
APP_ENV=development
APP_HOST=0.0.0.0
APP_PORT=8000
APP_DEBUG=true
LOG_LEVEL=INFO

# API Keys (required)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# All database connection strings (see 01-Database-Infrastructure)
```

## 🚀 Deployment

### Development Server

```bash
# Activate virtual environment
cd apex-memory-system
source venv/bin/activate

# Start with auto-reload (for development)
python -m uvicorn apex_memory.main:app --reload --port 8000

# API available at:
# - Main: http://localhost:8000
# - Docs: http://localhost:8000/docs
# - ReDoc: http://localhost:8000/redoc
# - Metrics: http://localhost:8000/metrics
```

### Production Server

```bash
# Use Uvicorn with workers (production)
uvicorn apex_memory.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \
  --loop uvloop \
  --log-level info

# Or with Gunicorn + Uvicorn workers
gunicorn apex_memory.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

### Docker Deployment

```bash
# Using docker-compose
cd apex-memory-system/docker
docker-compose up -d api

# API container includes:
# - Uvicorn server
# - All dependencies
# - Volume mount for hot reload (development)
```

## 📊 API Endpoint Catalog

### Document Ingestion

```bash
# Upload document (triggers Temporal workflow)
POST /api/v1/ingest
Content-Type: multipart/form-data
Body: file (PDF/DOCX/PPTX/HTML/MD/TXT), source (string)
Response: 202 Accepted, {workflow_id, document_id}

# Get document metadata
GET /api/v1/document/{uuid}
Response: 200 OK, {uuid, title, chunks, entities, created_at}

# Delete document
DELETE /api/v1/document/{uuid}
Response: 204 No Content
```

### Intelligent Querying

```bash
# Execute query (routes to optimal DB)
POST /api/v1/query/
Content-Type: application/json
Body: {query: "Find all suppliers for ACME Corp", limit: 10}
Response: 200 OK, {results: [...], metadata: {intent, databases_used, cache_hit}}

# Explain routing decision
GET /api/v1/query/explain?query=How%20has%20ACME%20changed
Response: 200 OK, {intent: "temporal", databases: ["graphiti", "neo4j"], reasoning: "..."}

# Cache statistics
GET /api/v1/query/cache/stats
Response: 200 OK, {hit_rate: 0.95, total_queries: 1000, cache_size_bytes: 5242880}
```

### Streaming Chat

```bash
# Start streaming chat with Claude
POST /api/v1/chat/stream
Content-Type: application/json
Body: {
  "conversation_id": "uuid",
  "messages": [{"role": "user", "content": "Summarize ACME Corp"}]
}
Response: 200 OK (text/event-stream)

# SSE Events:
# event: message_start
# event: content_block_start (type: text | tool_use)
# event: content_block_delta (delta: {text: "..."})
# event: tool_use (name: "search_knowledge_graph", input: {...})
# event: message_stop
```

### Authentication

```bash
# Register new user
POST /api/v1/auth/register
Body: {email, password, full_name}
Response: 201 Created, {user_id, access_token}

# Login (get JWT)
POST /api/v1/auth/login
Body: {email, password}
Response: 200 OK, {access_token, token_type: "bearer"}

# Get current user
GET /api/v1/auth/me
Headers: Authorization: Bearer <token>
Response: 200 OK, {user_id, email, full_name}
```

### Analytics

```bash
# System overview
GET /api/v1/analytics/overview
Response: 200 OK, {
  total_documents: 1500,
  total_entities: 8000,
  total_queries: 10000,
  cache_hit_rate: 0.95,
  avg_query_latency_ms: 650
}

# Query performance breakdown
GET /api/v1/analytics/query-performance
Response: 200 OK, {
  by_intent: {...},
  by_database: {...},
  latency_percentiles: {p50: 600, p90: 1000, p99: 2500}
}
```

## 📈 Performance Characteristics

### Latency (P50/P90/P99)

| Endpoint | P50 | P90 | P99 |
|----------|-----|-----|-----|
| `POST /ingest` | 50ms | 100ms | 300ms |
| `POST /query/` (cache hit) | 10ms | 20ms | 50ms |
| `POST /query/` (cache miss) | 600ms | 1000ms | 2500ms |
| `POST /chat/stream` (first token) | 800ms | 1500ms | 3000ms |
| `GET /auth/me` | 5ms | 10ms | 20ms |
| `GET /health` | 2ms | 5ms | 10ms |

### Concurrency

- **Development:** Single Uvicorn worker (1 concurrent request)
- **Production:** 4-8 workers (supports 100+ concurrent requests)
- **Rate Limiting:** Not implemented (add via middleware for production)

## 🔧 Testing

### API Testing

```bash
# Run API integration tests
cd apex-memory-system
pytest tests/integration/test_api_*.py -v

# Test specific router
pytest tests/integration/test_ingestion_api.py -v
pytest tests/integration/test_query_api.py -v
pytest tests/integration/test_chat_stream.py -v

# Load testing with Locust
locust -f tests/load/locustfile.py --host=http://localhost:8000
```

### Manual Testing (curl)

```bash
# Health check
curl http://localhost:8000/health

# Register user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123","full_name":"Test User"}'

# Upload document (with token)
curl -X POST http://localhost:8000/api/v1/ingest \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@test.pdf" \
  -F "source=local_upload"

# Query (with token)
curl -X POST http://localhost:8000/api/v1/query/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"What is ACME Corporation?","limit":10}'
```

## 🚨 Known Issues & Limitations

### Current State (from QUERY-ROUTER-STATE.md)

**Phase 3-4 Features DISABLED** (main.py:174-177):
```python
# Phase 3: Agentic Evolution (TEMPORARILY DISABLED)
enable_complexity_analysis=False,
enable_multi_router=False,
enable_self_correction=False,
enable_query_improvement=False,
```

**Reason:** 500 errors with query rewriting. See QUERY-ROUTER-STATE.md before re-enabling.

### Security Notes

1. **CORS:** Currently set to `allow_origins=["*"]` - Configure for production!
2. **JWT Secret:** Change default secret in production (settings.py)
3. **Rate Limiting:** Not implemented - add middleware for production
4. **File Upload Limits:** No size limit enforced - add validation
5. **HTTPS:** Required for HSTS headers to activate

## 🔍 Troubleshooting

### "500 Internal Server Error"

```bash
# Check server logs
# (View terminal where uvicorn is running)

# Check database connections
curl http://localhost:8000/api/v1/maintenance/health

# Restart server with debug
LOG_LEVEL=DEBUG python -m uvicorn apex_memory.main:app --reload
```

### "Workflow not executing" (ingestion)

```bash
# Verify Temporal worker is running
ps aux | grep dev_worker

# Check Temporal UI
open http://localhost:8088

# View workflow status
docker exec temporal-admin-tools tctl workflow list
```

### "401 Unauthorized"

```bash
# Verify JWT token is valid
# Token expires after 24 hours (default)

# Re-login to get new token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'
```

---

**Previous Component:** [02-Workflow-Orchestration](../02-Workflow-Orchestration/README.md)
**Next Component:** [04-Query-Intelligence](../04-Query-Intelligence/README.md)
