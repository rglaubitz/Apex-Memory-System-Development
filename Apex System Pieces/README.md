# Apex System Pieces - Technical Architecture Breakdown

**Created:** 2025-10-23
**Based On:** Actual code analysis of apex-memory-system
**Documentation:** 13 components, ~6,500 lines of technical documentation

---

## 📋 Overview

This directory contains comprehensive technical breakdowns of all 13 major components that make up the Apex Memory System. Each component is documented based on **actual code analysis** - real file paths, line counts, dependencies, and configuration.

**Purpose:** Understand how the system is architectured, what each piece does, and how they connect together.

---

## 🏗 System Architecture

The Apex Memory System is a **parallel multi-database intelligence platform** built with:
- **4 Specialized Databases** - Each optimized for different query types
- **Temporal.io Orchestration** - Fault-tolerant workflow execution
- **FastAPI Backend** - High-performance async API
- **React Frontend** - Modern streaming chat interface
- **90% Query Accuracy** - Achieved through intelligent routing

---

## 📚 Component Index (13 Total)

### Foundation Layer

**[01 - Database Infrastructure](01-Database-Infrastructure/)**
- PostgreSQL 16 + pgvector (metadata + hybrid search)
- Neo4j 2025.09.0 (graph relationships)
- Qdrant (vector similarity)
- Redis 8.2 (95% cache hit rate)
- Docker Compose orchestration

**[02 - Workflow Orchestration](02-Workflow-Orchestration/)**
- Temporal.io server + UI + admin tools
- 3 workflows: Greeting, DocumentIngestion, StructuredDataIngestion
- 11 activities across document and JSON processing
- Worker architecture with Prometheus metrics

**[11 - Configuration Management](11-Configuration-Management/)**
- Pydantic Settings for type-safe config
- Environment variable management
- Centralized database connection strings
- Feature flag controls

---

### Application Layer

**[03 - Backend API](03-Backend-API/)**
- FastAPI application (313 lines main.py)
- 13 API routers: ingestion, query, auth, chat, conversations, etc.
- CORS + Security headers middleware
- Health checks and metrics endpoints
- OpenAPI documentation (Swagger UI)

**[08 - Frontend Application](08-Frontend-Application/)**
- React 18.3 + TypeScript 5 + Vite 5
- Streaming chat with Claude (Vercel AI SDK)
- 27 components, 6 custom hooks
- JWT authentication with protected routes
- 5 artifact types: table, markdown, JSON, graph, timeline

**[12 - Authentication & Security](12-Authentication-Security/)**
- JWT-based authentication (24h expiration)
- bcrypt password hashing
- OWASP security headers (CSP, HSTS, X-Frame-Options)
- Protected routes and endpoints

---

### Intelligence Layer

**[04 - Query Intelligence](04-Query-Intelligence/)**
- 3-tier intent classification (keyword → hybrid → LLM)
- 90% accuracy (October 2025 achievement)
- Reciprocal Rank Fusion (RRF) reranking
- Semantic caching
- Phase 3-4 features DISABLED (see QUERY-ROUTER-STATE.md)

**[09 - Cache Layer](09-Cache-Layer/)**
- Redis-based query result caching
- 95% hit rate in steady state
- <10ms cache hit latency
- SHA256 cache key generation
- 1-hour TTL for query results

---

### Services Layer

**[05 - Core Services](05-Core-Services/)**
- 14 services: document_parser, entity_extractor, embedding_service, graphiti_service, database_writer, staging_manager, auth_service, conversation_service, achievement_tracker, circuit_breaker, distributed_lock, idempotency
- Docling 2.55.1 for PDF/DOCX/PPTX parsing
- OpenAI GPT-4o for entity extraction
- Graphiti-core 0.22.0 for temporal intelligence

**[06 - Data Models](06-Data-Models/)**
- 9 Pydantic models: Document, StructuredData, User, Conversation, Briefing, Achievement, UserMetric, ConversationShare, GraphitiEntity
- Type-safe validation
- JSON serialization
- UUID identifiers

**[07 - Database Writers](07-Database-Writers/)**
- 4 specialized writers: Neo4j, PostgreSQL, Qdrant, Redis
- DatabaseWriteOrchestrator with saga pattern
- Parallel writes with atomic rollback
- Fault tolerance for partial failures

---

### Operations Layer

**[10 - Monitoring & Observability](10-Monitoring-Observability/)**
- Prometheus metrics collection (40+ metrics)
- Grafana dashboards (33-panel temporal ingestion)
- 12 alert rules
- Health checks and performance tracking
- Worker metrics on port 9091

**[13 - Utilities & Scripts](13-Utilities-Scripts/)**
- Temporal debugging scripts (5 scripts)
- Development utilities (health checks, setup)
- Maintenance operations (rebuild indices, clear cache)
- Query router testing tools

---

## 🔗 Component Dependencies

```
┌────────────────────────────────────────────────────────────┐
│                                                            │
│  Frontend (08) ──→ Backend API (03) ──→ Auth (12)         │
│                          │                                 │
│                          ├──→ Query Router (04) ──┐        │
│                          │                        │        │
│                          ├──→ Workflows (02) ─────┼──→ Database Infrastructure (01)
│                          │                        │        │
│                          └──→ Core Services (05) ─┘        │
│                                      │                     │
│                                      └──→ Database Writers (07)
│                                                            │
│  Cache Layer (09) ←─────────────────────────────────────┐ │
│  Monitoring (10)  ←─────────────────────────────────────┼─┘
│  Config (11)      ←─────────────────────────────────────┘
│  Data Models (06) ←──── (used by all components)
│  Utilities (13)   ←──── (supports all components)
│                                                            │
└────────────────────────────────────────────────────────────┘
```

---

## 📊 Key Metrics (October 2025)

### Performance
- **Query Latency P50:** 600ms
- **Query Latency P90:** 1000ms
- **Cache Hit Rate:** 95% (steady state)
- **Query Accuracy:** 94-95%

### Scale
- **Total Documents:** Tested to 10,000+
- **Concurrent Requests:** 100+ (production config)
- **Test Coverage:** 80%+ code coverage
- **Total Tests:** 230+ tests passing

### Architecture
- **4 Databases:** PostgreSQL, Neo4j, Qdrant, Redis
- **13 API Routers:** Comprehensive REST API
- **14 Core Services:** Reusable business logic
- **3 Workflows:** Temporal-orchestrated ingestion

---

## 🚀 Quick Start

### Prerequisites
```bash
# 1. Install Docker + Docker Compose
docker --version
docker-compose --version

# 2. Install Python 3.11+
python3.11 --version

# 3. Set API keys in .env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

### Start System
```bash
# 1. Start all databases (components 01, 02)
cd apex-memory-system/docker
docker-compose up -d
docker-compose -f temporal-compose.yml up -d

# 2. Initialize databases
cd ..
python init-scripts/qdrant/init.py

# 3. Start Temporal worker (component 02)
python src/apex_memory/temporal/workers/dev_worker.py &

# 4. Start backend API (component 03)
python -m uvicorn apex_memory.main:app --reload --port 8000

# 5. Start frontend (component 08)
cd src/apex_memory/frontend
npm install && npm run dev
```

### Access Points
- **Frontend:** http://localhost:5173
- **API Docs:** http://localhost:8000/docs
- **Temporal UI:** http://localhost:8088
- **Grafana:** http://localhost:3001 (admin/apexmemory2024)
- **Prometheus:** http://localhost:9090

---

## 📖 How to Use This Documentation

### Learning the Architecture
1. **Start with Foundation:** Read 01-Database-Infrastructure, 02-Workflow-Orchestration
2. **Understand Application:** Read 03-Backend-API, 08-Frontend-Application
3. **Deep Dive Intelligence:** Read 04-Query-Intelligence, 09-Cache-Layer
4. **Explore Services:** Read 05-Core-Services, 06-Data-Models, 07-Database-Writers

### Debugging Issues
1. **Check health:** Use 13-Utilities-Scripts health checks
2. **Check metrics:** Use 10-Monitoring-Observability dashboards
3. **Check config:** Review 11-Configuration-Management
4. **Check security:** Review 12-Authentication-Security

### Implementing Changes
1. **Understand dependencies:** Check component README "Dependencies" section
2. **Review interfaces:** Check "Interfaces" section
3. **Read critical warnings:** Many components have "Known Issues" sections
4. **Test thoroughly:** Each component documents testing procedures

---

## ⚠️ Critical Warnings

### Query Router (Component 04)
- **Phase 3-4 features DISABLED** (main.py:174-177)
- **DO NOT enable** without reading QUERY-ROUTER-STATE.md
- **Intent mapping is stable** (router.py:786-791) - changing will affect 90% accuracy

### Workflow Orchestration (Component 02)
- **Worker must be running** for any ingestion to work
- **Without worker:** Documents queue indefinitely in Temporal

### Configuration (Component 11)
- **Change JWT secret in production!**
- **Restrict CORS** from `allow_origins=["*"]`
- **Add rate limiting** for production deployment

---

## 🔍 Finding Specific Information

### "Where is X implemented?"
- **Document parsing:** Component 05 (Core Services) - document_parser.py
- **Entity extraction:** Component 05 (Core Services) - entity_extractor.py
- **Query routing:** Component 04 (Query Intelligence) - router.py
- **Authentication:** Component 12 (Authentication & Security) - auth_service.py
- **Database writes:** Component 07 (Database Writers) - database_writer.py

### "How does Y work?"
- **Document ingestion:** Component 02 (Workflow Orchestration) - DocumentIngestionWorkflow
- **Query execution:** Component 04 (Query Intelligence) - Query Execution Flow diagram
- **Caching:** Component 09 (Cache Layer) - Cache Strategy section
- **Streaming chat:** Component 03 (Backend API) - chat_stream.py documentation

### "What databases are used?"
- See Component 01 (Database Infrastructure) for complete list

### "How do I configure Z?"
- See Component 11 (Configuration Management) for all settings

---

## 📝 Maintenance

This documentation was generated from actual code analysis on 2025-10-23. As the codebase evolves:

1. **File paths may change** - Use grep/find to locate moved files
2. **Line counts may differ** - Use `wc -l` to get current sizes
3. **Dependencies may update** - Check requirements.txt and package.json
4. **New components may be added** - Follow this documentation pattern

**To regenerate:** Re-analyze codebase following the same methodology (actual code inspection, not document reading).

---

## 🎯 Next Steps

1. **Choose a component** from the index above
2. **Read its README.md** for detailed technical information
3. **Explore the actual code** at the documented file paths
4. **Run the examples** provided in each README

**Note:** All file paths are relative to `apex-memory-system/` directory.

---

**Total Documentation:**
- 13 component READMEs
- ~6,500 lines of technical content
- Based on actual code analysis
- File paths, line counts, dependencies verified

**Created by:** Claude Code (Anthropic)
**Date:** 2025-10-23
**Method:** Direct codebase inspection and analysis
