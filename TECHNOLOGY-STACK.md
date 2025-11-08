# 📊 APEX MEMORY SYSTEM - COMPLETE TECHNOLOGY INVENTORY

**Generated:** 2025-11-07
**Project:** Apex Memory System Development
**Location:** `/Users/richardglaubitz/Projects/Apex-Memory-System-Development/apex-memory-system`
**Purpose:** Comprehensive permanent record of all technologies, tools, libraries, services, and platforms

---

## Table of Contents

- [A. Core Languages & Runtimes](#a-core-languages--runtimes)
- [B. Web Frameworks & APIs](#b-web-frameworks--apis)
- [C. Databases & Storage](#c-databases--storage)
- [D. AI/ML Services & Libraries](#d-aiml-services--libraries)
- [E. Cloud Platform & Infrastructure](#e-cloud-platform--infrastructure)
- [F. Containerization & Orchestration](#f-containerization--orchestration)
- [G. Monitoring & Observability](#g-monitoring--observability)
- [H. CI/CD & Automation](#h-cicd--automation)
- [I. Development Tools](#i-development-tools)
- [J. Testing Framework](#j-testing-framework)
- [K. Code Quality & Security](#k-code-quality--security)
- [L. Document Processing](#l-document-processing)
- [M. External Integrations](#m-external-integrations)
- [N. Workflow Orchestration](#n-workflow-orchestration)
- [O. Networking & Protocols](#o-networking--protocols)
- [P. Build & Package Management](#p-build--package-management)
- [Q. Data Science & Analytics](#q-data-science--analytics)
- [R. Miscellaneous Tools](#r-miscellaneous-tools)
- [S. Summary Statistics](#s-summary-statistics)
- [T. Key Architectural Technologies](#t-key-architectural-technologies)
- [U. Environment Variables](#u-environment-variables)
- [V. Deployment Paths](#v-deployment-paths)

---

## A. Core Languages & Runtimes

| Technology | Version | Purpose | Source |
|------------|---------|---------|--------|
| **Python** | 3.11+ (3.12.4 installed) | Primary programming language | requirements.txt, GitHub Actions |
| **Node.js** | v25.1.0 | MCP server runtime (npx/uvx) | System installed |
| **Shell/Bash** | System default | Scripts, automation, deployment | scripts/*.sh |

---

## B. Web Frameworks & APIs

| Package | Version | Purpose | Source |
|---------|---------|---------|--------|
| **FastAPI** | 0.118.0 | Modern async web framework | requirements.txt |
| **Uvicorn** | 0.37.0 (with standard extras) | ASGI server | requirements.txt |
| **Starlette** | 0.48.0 | ASGI framework (FastAPI dependency) | requirements.txt |
| **python-multipart** | 0.0.20 | Form/file upload support | requirements.txt |
| **httpx** | 0.28.1 | Async HTTP client | requirements.txt |
| **requests** | 2.32.5 | Synchronous HTTP library | requirements.txt |

---

## C. Databases & Storage

### Primary Databases

| Database | Version | Purpose | Source |
|----------|---------|---------|--------|
| **PostgreSQL** | 16+ with pgvector | Relational database + vector search | docker-compose.yml (ankane/pgvector:latest) |
| **Neo4j** | 2025.09.0 | Graph database for relationships | docker-compose.yml |
| **Qdrant** | latest | High-performance vector database | docker-compose.yml (qdrant/qdrant:latest) |
| **Redis** | 8.2-alpine | Cache layer, query caching | docker-compose.yml |

### Database Drivers & Clients

| Package | Version | Purpose | Source |
|---------|---------|---------|--------|
| **neo4j** | 6.0.2 | Neo4j Python driver | requirements.txt |
| **psycopg2-binary** | 2.9.10 | PostgreSQL driver | requirements.txt |
| **asyncpg** | 0.30.0 | Async PostgreSQL driver | requirements.txt |
| **qdrant-client** | 1.15.1 | Qdrant Python client | requirements.txt |
| **redis** | 6.4.0 | Redis Python client | requirements.txt |

### PostgreSQL Extensions

| Extension | Purpose | Source |
|-----------|---------|--------|
| **vector** | pgvector for vector similarity search | schemas/postgres_schema.sql |
| **uuid-ossp** | UUID generation | schemas/postgres_schema.sql |
| **btree_gin** | JSONB optimizations (GIN indices) | schemas/postgres_schema.sql |
| **pg_trgm** | Fuzzy text search | schemas/postgres_schema.sql |

### Neo4j Plugins

| Plugin | Purpose | Source |
|--------|---------|--------|
| **APOC** | Neo4j Awesome Procedures | docker-compose.yml |
| **Graph Data Science** | Graph algorithms | docker-compose.yml |

### Cloud Storage (Local Development)

| Service | Version | Purpose | Source |
|---------|---------|---------|--------|
| **LocalStack** | latest | Local S3 emulation | docker-compose.yml |

---

## D. AI/ML Services & Libraries

### LLM Providers

| Service | Version | Purpose | Source |
|---------|---------|---------|--------|
| **OpenAI API** | openai==1.109.1 | Embeddings (text-embedding-3-small), LLM | requirements.txt, .env.example |
| **Anthropic API** | anthropic==0.71.0 | Claude for query rewriting, conversation | requirements.txt, .env.example |

### AI/ML Libraries

| Package | Version | Purpose | Source |
|---------|---------|---------|--------|
| **graphiti-core** | 0.22.0 | Temporal graph intelligence, LLM-powered entity extraction | requirements.txt |
| **semantic-router** | 0.1.11 | Intent classification for query routing | requirements.txt |
| **sentence-transformers** | 5.1.1 | Local embeddings (all-mpnet-base-v2) | requirements.txt |
| **langchain** | 0.3.27 | RAG orchestration framework | requirements.txt |
| **langchain-community** | 0.3.30 | Community integrations | requirements.txt |
| **numpy** | 1.26.4 | Numerical computing (adaptive routing, result fusion) | requirements.txt |

---

## E. Cloud Platform & Infrastructure

### Google Cloud Platform (GCP)

**Deployment Target:** Production deployment (planned)

| Service | Purpose | Source |
|---------|---------|--------|
| **Cloud Run** | Serverless containers (API, workers, Qdrant) | deployment/production/GCP-DEPLOYMENT-GUIDE.md |
| **Cloud SQL** | Managed PostgreSQL + pgvector | deployment/production/ARCHITECTURE.md |
| **Compute Engine** | Neo4j VM hosting | deployment/production/ARCHITECTURE.md |
| **Memorystore** | Managed Redis cache | deployment/production/ARCHITECTURE.md |
| **VPC** | Private networking | deployment/production/GCP-DEPLOYMENT-GUIDE.md |
| **Secret Manager** | Secrets management | deployment/production/GCP-DEPLOYMENT-GUIDE.md |
| **Cloud Build** | CI/CD builds | deployment/production/GCP-DEPLOYMENT-GUIDE.md |
| **Artifact Registry** | Docker image storage | deployment/production/GCP-DEPLOYMENT-GUIDE.md |
| **Cloud Load Balancer** | SSL/TLS termination, routing | deployment/production/ARCHITECTURE.md |
| **Cloud Armor** | DDoS protection, WAF | deployment/production/ARCHITECTURE.md |

### Managed Services

| Service | Purpose | Source |
|---------|---------|--------|
| **Temporal Cloud** | Managed workflow orchestration (vs. self-hosted) | deployment/production/ARCHITECTURE.md |
| **Grafana Cloud** | Managed monitoring (Pro tier, $19/month) | deployment/PRODUCTION-DEPLOYMENT-PLAN.md |

---

## F. Containerization & Orchestration

### Docker

| Component | Version | Purpose | Source |
|-----------|---------|---------|--------|
| **Docker** | 28.5.1 | Container runtime | System installed |
| **Docker Compose** | Bundled | Multi-container orchestration | docker/docker-compose.yml |

### Container Images

| Image | Version | Purpose | Source |
|-------|---------|---------|--------|
| **python:3.11-slim** | 3.11 | Base image for API & worker | docker/Dockerfile.api, docker/Dockerfile.worker |
| **ankane/pgvector** | latest | PostgreSQL + pgvector | docker-compose.yml |
| **neo4j** | 2025.09.0 | Neo4j graph database | docker-compose.yml |
| **qdrant/qdrant** | latest | Qdrant vector DB | docker-compose.yml |
| **redis** | 8.2-alpine | Redis cache | docker-compose.yml |
| **localstack/localstack** | latest | Local AWS emulation | docker-compose.yml |
| **prom/prometheus** | latest | Metrics collection | docker-compose.yml |
| **grafana/grafana** | latest | Metrics visualization | docker-compose.yml |

### Kubernetes (Planned)

| Component | Status | Purpose | Source |
|-----------|--------|---------|--------|
| **GKE (Google Kubernetes Engine)** | Planned (alternative to Cloud Run) | Container orchestration | deployment/production/ARCHITECTURE.md |

---

## G. Monitoring & Observability

### Monitoring Stack

| Tool | Version | Purpose | Source |
|------|---------|---------|--------|
| **Prometheus** | latest | Metrics collection and storage | docker-compose.yml |
| **Grafana** | latest | Metrics visualization, dashboards | docker-compose.yml |
| **Grafana Cloud** | Pro tier ($19/month) | Managed Prometheus + Grafana | deployment/PRODUCTION-DEPLOYMENT-PLAN.md |
| **prometheus-client** | 0.23.1 | Python Prometheus client | requirements.txt |
| **Sentry** | 2.43.0 | AI-optimized error tracking (150-breadcrumb trail, local variables, exception chains, Temporal integration) | requirements.txt, .env |

### Tracing & Logging

| Package | Version | Purpose | Source |
|---------|---------|---------|--------|
| **opentelemetry-api** | 1.37.0 | Distributed tracing API | requirements.txt |
| **opentelemetry-sdk** | 1.37.0 | OpenTelemetry SDK | requirements.txt |
| **opentelemetry-exporter-jaeger** | 1.21.0 | Jaeger exporter for traces | requirements.txt |
| **Deprecated** | 1.2.18 | Required by Jaeger exporter | requirements.txt |
| **python-json-logger** | 3.3.0 | JSON structured logging | requirements.txt |
| **structlog** | 25.4.0 | Structured logging | requirements.txt |

### Monitoring Configuration

| Asset | Purpose | Source |
|-------|---------|--------|
| **prometheus.yml** | Prometheus scrape config (11 jobs) | docker/prometheus/prometheus.yml |
| **Grafana Dashboards** | 5 dashboards (overview, Graphiti, query router, Temporal, saga) | monitoring/dashboards/*.json |
| **Alert Rules** | 12+ Temporal alerts, critical alerts | monitoring/alerts/rules.yml |

### Metrics Coverage

- **27 Temporal Metrics** - 6-layer monitoring (workflow, activity, data quality, infrastructure, business, logs)
- **5 Grafana Dashboards** - Apex Overview, Graphiti, Query Router, Saga Execution, Temporal Ingestion (33 panels)
- **12+ Alert Rules** - Critical, warning, info severity levels

---

## H. CI/CD & Automation

### GitHub Actions

**Workflows:**

| Workflow | File | Purpose |
|----------|------|---------|
| **CI Pipeline** | .github/workflows/ci.yml | Lint, security, unit tests, integration tests, build |
| **Test Suite** | .github/workflows/test.yml | Unit, integration, performance, security tests |

**Actions Used:**

| Action | Version | Purpose | Source |
|--------|---------|---------|--------|
| **actions/checkout** | v4 | Checkout repository | ci.yml, test.yml |
| **actions/setup-python** | v5 | Setup Python environment | ci.yml, test.yml |
| **actions/cache** | v4 | Cache pip dependencies | ci.yml, test.yml |
| **codecov/codecov-action** | v4 | Upload coverage reports | ci.yml, test.yml |
| **actions/upload-artifact** | v4 | Upload security reports | test.yml |
| **benchmark-action/github-action-benchmark** | v1 | Store performance benchmarks | test.yml |

### CI/CD Services (GitHub Hosted)

| Component | Purpose | Source |
|-----------|---------|--------|
| **Neo4j service** | Integration tests database | .github/workflows/ci.yml (services) |
| **PostgreSQL service** | Integration tests database | .github/workflows/ci.yml (services) |
| **Redis service** | Integration tests cache | .github/workflows/ci.yml (services) |
| **Qdrant service** | Integration tests vector DB | .github/workflows/ci.yml (services) |

### Scripts

**Development Scripts (54 Python scripts):**

| Category | Count | Scripts | Purpose |
|----------|-------|---------|---------|
| **Temporal** | 8 | workflow debugging, health checks, benchmarks, validation | scripts/temporal/ |
| **Query Router** | 16 | performance testing, classification debugging, threshold analysis | scripts/query-router/ |
| **Maintenance** | 2 | Graphiti index building, document reprocessing | scripts/maintenance/ |
| **Setup** | 2 | Sprint verification, Graphiti index initialization | scripts/setup/ |
| **Development** | 2 | Health checks, API runner | scripts/dev/ |
| **Preflight** | 2 | Baseline validation, environment checks | scripts/preflight/ |
| **Migrations** | 1 | Bandit weights table creation | scripts/migrations/ |
| **Debug** | 5 | Qdrant verification, intent testing, Temporal extraction | scripts/debug/ |
| **Neo4j** | 1 | Migration script | scripts/neo4j/ |
| **Qdrant** | 2 | Collection creation, migration | scripts/qdrant/ |
| **Community Detection** | 2 | Graph community detection | scripts/community-detection/ |
| **Training Data** | 11 | Query analysis, version creation | scripts/training-data/ |

**Shell Scripts (7 scripts):**

| Script | Purpose | Source |
|--------|---------|--------|
| **verify_sprint1.sh** | Sprint 1 verification | scripts/setup/ |
| **test_graphiti.sh** | Graphiti testing | scripts/dev/ |
| **start_temporal.sh** | Start Temporal server | scripts/temporal/ |
| **check_temporal_health.sh** | Temporal health check | scripts/temporal/ |
| **stop_temporal.sh** | Stop Temporal server | scripts/temporal/ |
| **worker-health-check.sh** | Worker health monitoring | scripts/temporal/ |
| **health-check-comprehensive.sh** | Comprehensive health check | scripts/temporal/ |

---

## I. Development Tools

### IDEs & Editors

| Tool | Purpose | Source |
|------|---------|--------|
| **Cursor IDE** | Primary IDE (VSCode-based) | ~/.claude/CLAUDE.md |
| **VSCode** | Alternative IDE | ~/.claude/CLAUDE.md |

### CLI Tools

| Tool | Purpose | Source |
|------|---------|--------|
| **Claude Code** | AI-powered CLI (claude.ai/code) | ~/.claude/CLAUDE.md |
| **gcloud CLI** | GCP management | deployment/production/GCP-DEPLOYMENT-GUIDE.md |
| **gh (GitHub CLI)** | GitHub operations | Workflow commands |

### Modern Python Development Tools (2025) ⭐ NEW

**Installed:** November 7, 2025
**Status:** ✅ All configured and operational

| Tool | Version | Purpose | Speed vs Legacy |
|------|---------|---------|-----------------|
| **uv** | 0.8.12 | Ultra-fast package manager | 10-100x faster than pip |
| **ruff** | 0.14.4 | All-in-one linter + formatter | 10-100x faster than flake8/black |
| **pyright** | 1.1.407 | Fast type checker | Faster than mypy |
| **pre-commit** | 4.0.1 | Git hook automation | Prevents bad commits |
| **pip-audit** | 2.9.0 | Official security scanner | Python Packaging Authority |
| **gitleaks** | 8.29.0 | Secret scanner | Prevents API key leaks |
| **semgrep** | 1.142.0 | Advanced security scanning | Complex pattern detection |
| **mkdocs-material** | 9.5.42+ | Modern documentation | Beautiful docs |
| **just** | 1.43.0 | Task runner | Simpler than Make |

**Configuration:**
- **pyproject.toml** - Centralized config for all Python tools (ruff, mypy, pytest, coverage)
- **.pre-commit-config.yaml** - Pre-commit hooks (ruff, mypy, gitleaks, semgrep, pip-audit)
- **justfile** - 40+ common development commands

**Impact:**
- ✅ **Auto-fixed 3,060 code quality issues** (97.8% of 3,132 found)
- ✅ **Formatted 262 files** for consistent style
- ✅ **Pre-commit hooks** run before every commit
- ✅ **Security scanning** (dependencies + secrets + patterns)

**Documentation:** See `DEVELOPMENT-TOOLS.md` for complete guide

**Ruff Replaces:** black, isort, flake8, pyupgrade, pydocstyle, pycodestyle, autoflake (7 tools → 1!)

### MCP (Model Context Protocol) Servers

**Configuration:** `.claude/.mcp.json`

| Server | Package | Purpose |
|--------|---------|---------|
| **memory** | @modelcontextprotocol/server-memory | Persistent memory across sessions |
| **sqlite-knowledge** | mcp-server-sqlite | Shared knowledge database |
| **sequential-thinking** | @modelcontextprotocol/server-sequential-thinking | Step-by-step reasoning |
| **context7** | @context7/mcp-server | Context management |
| **exa** | exa-mcp-server | Web search, code context (EXA_API_KEY required) |
| **firecrawl** | firecrawl-mcp | Web scraping (FIRECRAWL_API_KEY required) |
| **chrome-devtools** | chrome-devtools-mcp@latest | Browser automation, screenshots |
| **mcpdocsearch** | @alizdavoodi/mcpdocsearch | Documentation search |

### Custom Agents (21 agents)

**Location:** `.claude/agents/`

**C-Suite Executives (3):**
- **Chief Information Officer (CIO)** - Research quality validation
- **Chief Technology Officer (CTO)** - Technical architecture review
- **Chief Operations Officer (COO)** - Operational capacity review

**Research Team (17):**
- research-manager, research-coordinator, documentation-expert
- deep-researcher, standards-researcher, company-researcher
- competitive-intelligence-analyst, technical-trend-analyst
- documentation-hunter, api-documentation-specialist
- github-examples-hunter, pattern-implementation-analyst
- citation-manager, technical-validator, code-quality-validator
- memory-system-engineer, agent-testing-engineer

**Specialized Skill (1):**
- penske-receipt-matching (project-specific)

---

## J. Testing Framework

### Core Testing

| Package | Version | Purpose | Source |
|---------|---------|---------|--------|
| **pytest** | 8.3.3 (dev), 8.0.0 (test) | Testing framework | requirements-dev.txt |
| **pytest-asyncio** | 0.24.0 (dev), 0.23.3 (test) | Async test support | requirements-dev.txt |
| **pytest-cov** | 5.0.0 (dev), 4.1.0 (test) | Coverage reporting | requirements-dev.txt |
| **pytest-mock** | 3.14.0 (dev), 3.12.0 (test) | Mocking support | requirements-dev.txt |
| **pytest-timeout** | 2.3.1 (dev), 2.2.0 (test) | Test timeouts | requirements-dev.txt |
| **pytest-xdist** | 3.5.0 | Parallel test execution | requirements-test.txt |

### Advanced Testing

| Package | Version | Purpose | Source |
|---------|---------|---------|--------|
| **hypothesis** | 6.115.2 | Property-based testing | requirements-dev.txt |
| **faker** | 30.8.2 (dev), 22.0.0 (test) | Test data generation | requirements-dev.txt |
| **factory-boy** | 3.3.0 | Test fixture factories | requirements-test.txt |
| **pytest-benchmark** | 4.0.0 | Performance benchmarks | requirements-test.txt |

### Database Testing

| Package | Version | Purpose | Source |
|---------|---------|---------|--------|
| **pytest-postgresql** | 6.1.1 (dev), 5.0.0 (test) | PostgreSQL test utilities | requirements-dev.txt |
| **pytest-redis** | 3.0.2 | Redis test utilities | requirements-test.txt |
| **testcontainers** | 4.8.1 | Docker-based testing | requirements-dev.txt |

### HTTP Testing

| Package | Version | Purpose | Source |
|---------|---------|---------|--------|
| **requests-mock** | 1.11.0 | Mock HTTP requests | requirements-test.txt |

### Load Testing

| Package | Version | Purpose | Source |
|---------|---------|---------|--------|
| **locust** | 2.32.2 (dev), 2.20.0 (test) | Load and performance testing | requirements-dev.txt |

### Coverage

| Package | Version | Purpose | Source |
|---------|---------|---------|--------|
| **coverage[toml]** | 7.4.1 | Coverage measurement | requirements-test.txt |
| **codecov** | 2.1.13 | Coverage reporting to Codecov | requirements-test.txt |

### Test Configuration

| File | Purpose | Source |
|------|---------|--------|
| **pytest.ini** | Pytest configuration (markers, coverage, asyncio) | pytest.ini |

**Test Markers (14):**
- unit, integration, performance, security, chaos
- slow, neo4j, postgres, qdrant, redis
- graphiti, alerts, load, temporal

### Test Organization

**Test Count:** 156+ tests passing (121 Enhanced Saga baseline + 35 Graphiti+JSON tests)

**Test Structure:**
- `tests/unit/` - Unit tests (fast, no external dependencies)
- `tests/integration/` - Integration tests (require databases)
- `tests/load/` - Load and performance tests
- `upgrades/active/temporal-implementation/tests/` - Temporal-specific tests (phase-based + section-based)

---

## K. Code Quality & Security

### Formatters

| Tool | Version | Purpose | Source |
|------|---------|---------|--------|
| **black** | 24.10.0 (dev), 24.1.1 (test) | Code formatter (PEP8) | requirements-dev.txt |
| **isort** | 5.13.2 | Import sorting | requirements-dev.txt |

### Linters

| Tool | Version | Purpose | Source |
|------|---------|---------|--------|
| **flake8** | 7.1.1 (dev), 7.0.0 (test) | Code linter | requirements-dev.txt |
| **flake8-docstrings** | 1.7.0 | Docstring linting | requirements-dev.txt |
| **flake8-bugbear** | 24.8.19 | Bug detection | requirements-dev.txt |
| **pylint** | 3.3.1 | Additional linting | requirements-dev.txt |

### Type Checking

| Tool | Version | Purpose | Source |
|------|---------|---------|--------|
| **mypy** | 1.13.0 (dev), 1.8.0 (test) | Static type checking | requirements-dev.txt |
| **types-requests** | 2.32.4.20250913 | Type stubs for requests | requirements.txt |

### Security Scanning

| Tool | Version | Purpose | Source |
|------|---------|---------|--------|
| **bandit** | 1.7.10 (dev), 1.7.6 (test) | Security linter | requirements-dev.txt |
| **safety** | 3.2.8 (dev), 3.0.1 (test) | Dependency vulnerability scanner | requirements-dev.txt |

### Pre-commit Hooks

| Tool | Version | Purpose | Source |
|------|---------|---------|--------|
| **pre-commit** | 4.0.1 | Git hooks framework | requirements-dev.txt |

**Note:** No `.pre-commit-config.yaml` found (hooks managed manually in CI/CD)

---

## L. Document Processing

### Document Parsing

| Package | Version | Purpose | Source |
|---------|---------|---------|--------|
| **docling** | 2.55.1 | Advanced multi-format parser (PDF, DOCX, PPTX) | requirements.txt |
| **pypdf** | 6.1.1 | PDF parsing | requirements.txt |
| **python-docx** | 1.2.0 | Microsoft Word (DOCX) parsing | requirements.txt |
| **python-pptx** | 1.0.2 | Microsoft PowerPoint (PPTX) parsing | requirements.txt |

**Usage:** `src/apex_memory/services/document_parser.py`

**Supported Formats:**
- PDF (via pypdf and docling)
- Microsoft Word (.docx)
- Microsoft PowerPoint (.pptx)
- HTML
- Markdown
- Plain text

---

## M. External Integrations

### Cloud APIs

| Service | SDK | Version | Purpose | Source |
|---------|-----|---------|---------|--------|
| **Google Drive API** | google-api-python-client | 2.150.0 | Official Python SDK for Google Drive | requirements.txt |
| **Google Auth** | google-auth-httplib2 | 0.2.0 | HTTP library for Google auth | requirements.txt |
| **Google OAuth** | google-auth-oauthlib | 1.2.1 | OAuth flow for Google APIs | requirements.txt |

**Google Drive Integration Features:**
- Automated monitoring (every 15 minutes)
- Document ingestion from Drive
- Archive processed files back to Drive
- Dead Letter Queue for errors
- 7 metrics + 12 alerts
- 48 tests (44/48 passing, 92%)

### Model Context Protocol (MCP)

**Apex MCP Server** (Custom Integration)

| Component | Version | Purpose | Source |
|-----------|---------|---------|--------|
| **apex-mcp-server** | 0.1.0 | MCP server for Claude Desktop integration | apex-mcp-server/pyproject.toml |
| **mcp** | >=1.2.1 | MCP protocol SDK | apex-mcp-server/pyproject.toml |

**Tools Provided (10):**
- `add_memory()`, `add_conversation()`, `search_memory()`, `list_recent_memories()`, `clear_memories()`
- `temporal_search()`, `get_entity_timeline()`, `get_communities()`, `get_graph_stats()`
- `ask_apex()` - Intelligent multi-query orchestration (killer feature)

**Differentiator:** Multi-query orchestration where Claude automatically plans and executes 3-6 queries, then synthesizes coherent narrative answers with insights.

---

## N. Workflow Orchestration

### Temporal.io

| Component | Version | Purpose | Source |
|-----------|---------|---------|--------|
| **temporalio** | 1.11.0 | Temporal.io Python SDK | requirements.txt |
| **Temporal Cloud** | Managed service | Durable workflow orchestration (vs. self-hosted) | deployment/production/ARCHITECTURE.md |

**Implementation:**
- **Workflows:** `src/apex_memory/temporal/workflows/` (DocumentIngestionWorkflow, StructuredDataIngestionWorkflow, GoogleDriveMonitorWorkflow, GoogleDriveArchiveWorkflow)
- **Activities:** `src/apex_memory/temporal/activities/` (5 instrumented activities for ingestion + Google Drive activities)
- **Workers:** `src/apex_memory/temporal/workers/` (dev_worker.py)
- **Metrics:** 27 Temporal metrics across 6 layers
- **Monitoring:** Temporal UI (http://localhost:8088 local, Temporal Cloud UI production)

**Key Features:**
- Durable execution (workflows survive crashes)
- Saga pattern (distributed transactions with compensation)
- Retry logic with exponential backoff
- Observability (27 metrics, 12 alerts)
- Scheduled workflows (Google Drive monitoring every 15 minutes)

---

## O. Networking & Protocols

### Protocols

| Protocol | Implementation | Purpose | Source |
|----------|----------------|---------|--------|
| **HTTP/HTTPS** | FastAPI, httpx, requests | REST API communication | requirements.txt |
| **gRPC** | Qdrant client, Temporal SDK | High-performance RPC | qdrant-client, temporalio |
| **WebSockets** | Starlette (FastAPI) | Real-time communication (if used) | requirements.txt |
| **Bolt** | Neo4j driver | Neo4j binary protocol | neo4j==6.0.2 |

### Networking

| Component | Purpose | Source |
|-----------|---------|--------|
| **Docker bridge network** | apex-network | Container-to-container communication | docker-compose.yml |
| **VPC (GCP)** | apex-network | Private cloud networking | deployment/production/GCP-DEPLOYMENT-GUIDE.md |
| **VPC Connector (GCP)** | apex-connector | Cloud Run <-> Cloud SQL/Redis | deployment/production/GCP-DEPLOYMENT-GUIDE.md |

---

## P. Build & Package Management

### Python Package Management

| Tool | Purpose | Source |
|------|---------|--------|
| **pip** | Python package installer | requirements.txt |
| **venv** | Virtual environment | Development workflow |
| **uv** | Fast Python package installer (recommended) | apex-mcp-server/README.md |

### Build Tools

| Tool | Version | Purpose | Source |
|------|---------|---------|--------|
| **build** | Latest | Python package builder | .github/workflows/ci.yml |
| **wheel** | Latest | Python wheel builder | .github/workflows/ci.yml |
| **hatchling** | Latest | Build backend for apex-mcp-server | apex-mcp-server/pyproject.toml |

### Database Migrations

| Tool | Version | Purpose | Source |
|------|---------|---------|--------|
| **alembic** | 1.14.0 | Database schema migrations | requirements.txt |

**Migration Count:** 7 Alembic migration files

**Migrations:**
1. Initial schema (users, conversations, messages)
2. API keys
3. Structured data (JSONB)
4. Briefings & achievements
5. UUID ordering indices
6. Conversation sharing
7. pgvector + JSONB optimizations

---

## Q. Data Science & Analytics

**Note:** NumPy is used for query routing and result fusion, not full data science stack.

| Package | Version | Purpose | Source |
|---------|---------|---------|--------|
| **numpy** | 1.26.4 | Numerical computing (adaptive routing, result fusion) | requirements.txt |

**No Jupyter notebooks found** in the project (no `.ipynb` files)

**Data Science Tools (Development Only):**

| Package | Version | Purpose | Source |
|---------|---------|---------|--------|
| **IPython** | 8.29.0 | Enhanced Python shell | requirements-dev.txt |
| **jupyter** | 1.1.1 | Notebook environment | requirements-dev.txt |

---

## R. Miscellaneous Tools

### Data Validation

| Package | Version | Purpose | Source |
|---------|---------|---------|--------|
| **pydantic** | 2.11.10 | Data validation, settings management | requirements.txt |
| **pydantic-settings** | 2.11.0 | Settings from environment variables | requirements.txt |
| **email-validator** | 2.2.0 | EmailStr validation | requirements.txt |

### Configuration Management

| Package | Version | Purpose | Source |
|---------|---------|---------|--------|
| **python-dotenv** | 1.1.1 | Environment variables from .env | requirements.txt |

### CLI & Terminal

| Package | Version | Purpose | Source |
|---------|---------|---------|--------|
| **click** | 8.3.0 | CLI framework | requirements.txt |
| **rich** | 14.1.0 | Beautiful terminal output | requirements.txt |
| **httpie** | 3.2.4 | CLI HTTP client | requirements-dev.txt |

### Utilities

| Package | Version | Purpose | Source |
|---------|---------|---------|--------|
| **tenacity** | 9.1.2 | Retry logic with exponential backoff | requirements.txt |
| **python-dateutil** | 2.9.0.post0 | Date parsing utilities | requirements.txt |
| **aiofiles** | 24.1.0 | Async file I/O | requirements.txt |

### Performance & Profiling

| Package | Version | Purpose | Source |
|---------|---------|---------|--------|
| **memory-profiler** | 0.61.0 | Memory profiling | requirements-dev.txt |
| **line-profiler** | 4.1.3 | Line-by-line profiling | requirements-dev.txt |

### Authentication & Security

| Package | Version | Purpose | Source |
|---------|---------|---------|--------|
| **python-jose[cryptography]** | 3.3.0 | JWT token handling | requirements.txt |
| **bcrypt** | 5.0.0 | Password hashing | requirements.txt |

### File System Monitoring

| Package | Version | Purpose | Source |
|---------|---------|---------|--------|
| **watchdog** | 5.0.3 | File system event monitoring | requirements-dev.txt |

### Documentation Generation

| Package | Version | Purpose | Source |
|---------|---------|---------|--------|
| **sphinx** | 8.1.3 | Documentation generator | requirements-dev.txt |
| **sphinx-rtd-theme** | 3.0.1 | Read the Docs theme | requirements-dev.txt |
| **mkdocs** | 1.6.1 | Alternative documentation | requirements-dev.txt |
| **mkdocs-material** | 9.5.42 | Material theme for MkDocs | requirements-dev.txt |

### Configuration Files

**Training Data:**
- 14 JSON files in `config/` for query router training (v2, v3, v3.1-v3.5 iterations)

---

## S. Summary Statistics

### Package Counts

| Category | Count |
|----------|-------|
| **Production Python Packages** | 48 |
| **Development Python Packages** | 28 |
| **Test-Specific Packages** | 20 |
| **Docker Images** | 8 |
| **MCP Servers** | 8 |
| **Custom Agents** | 21 |
| **GitHub Actions Workflows** | 2 |
| **Python Scripts** | 54 |
| **Shell Scripts** | 7 |
| **Grafana Dashboards** | 5 |
| **PostgreSQL Extensions** | 4 |
| **Neo4j Plugins** | 2 |
| **Alembic Migrations** | 7 |
| **Test Markers** | 14 |

### Infrastructure Services

| Environment | Services | Details |
|-------------|----------|---------|
| **Local Development** | 9 services | PostgreSQL, Neo4j, Qdrant, Redis, LocalStack, API, Worker, Prometheus, Grafana |
| **Production (GCP)** | 11+ services | Cloud Run (API, Workers, Qdrant), Cloud SQL, Compute Engine (Neo4j), Memorystore, Temporal Cloud, VPC, Secret Manager, Load Balancer, Cloud Build, Artifact Registry |

### Testing Coverage

| Category | Count/Status |
|----------|--------------|
| **Total Tests** | 156+ passing |
| **Test Markers** | 14 markers |
| **Coverage Target** | 80% minimum |
| **Temporal Tests** | 41 section tests + Phase tests |
| **Enhanced Saga Baseline** | 121 tests |
| **Graphiti+JSON Tests** | 35 tests |
| **Google Drive Tests** | 48 tests (44/48 passing, 92%) |

---

## T. Key Architectural Technologies

### Multi-Database Architecture

**4-Database Parallel System:**

1. **PostgreSQL + pgvector** - Metadata search + hybrid semantic queries
   - Extensions: vector, uuid-ossp, btree_gin, pg_trgm
   - JSONB optimizations for structured data
   - Point-in-time recovery (PITR) via WAL archives

2. **Neo4j** - Graph relationships, entity connections
   - Plugins: APOC, Graph Data Science
   - Community detection (graph clustering)
   - 1-hop to 3-hop traversals

3. **Qdrant** - High-performance vector similarity search
   - <50ms top-10 vector search
   - 100+ queries/second capability
   - Native gRPC protocol

4. **Redis** - Cache layer (<100ms repeat queries)
   - Cache hit rate optimization
   - Query result caching
   - Session storage

### Intelligence Layers

1. **Query Router** - Intent-based classification
   - semantic-router (0.1.11)
   - 90% accuracy
   - Adaptive routing based on performance

2. **Graphiti Integration** - Temporal reasoning
   - LLM-powered entity extraction
   - 90%+ accuracy (vs 60% regex baseline)
   - All 46 entities supported
   - Temporal graph intelligence

3. **Result Fusion** - Multi-database result aggregation
   - NumPy for numerical operations
   - Weighted scoring across databases
   - Deduplication and ranking

4. **Adaptive Routing** - Performance-based optimization
   - Real-time latency monitoring
   - Automatic failover to faster databases
   - Cost-aware routing

### Workflow Orchestration

- **Temporal.io** - Durable workflows, saga pattern
- **5 Instrumented Activities** - Parse, extract, Neo4j write, PostgreSQL write, Qdrant write
- **27 Metrics** - 6-layer monitoring (workflow, activity, data quality, infrastructure, business, logs)
- **12+ Alerts** - Critical, warning, info severity levels

### Entity Extraction

**Graphiti-powered LLM Extraction:**

**46 Entity Types Across 4 Domains:**

**Logistics Domain (18):**
- carrier, driver, trailer, truck, dispatch, shipment
- load, commodity, freight_terms, pickup, delivery
- route, carrier_contract, accessorial_charge, bill_of_lading
- load_board, detention_charge, lumper_fee

**Financial Domain (13):**
- payment, payment_term, invoice, expense, budget
- revenue, cost, profit_margin, tax, factoring_company
- fuel_surcharge, payment_method, financial_report

**Operational Domain (9):**
- inspection, maintenance, fuel_purchase, hours_of_service
- compliance_violation, safety_incident, document
- equipment_lease, regulatory_requirement

**Corporate Domain (6):**
- employee, department, customer, vendor, contract, policy

---

## U. Environment Variables

**Configuration Files:**
- `.env.example` (144 lines) - Development template
- `.env.production.example` (180 lines) - Production template with security notes
- `.env.temporal` - Temporal.io workflow configuration

### Key Environment Groups

**1. Database Connections (4 databases)**
```
NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
DATABASE_URL (PostgreSQL)
QDRANT_HOST, QDRANT_PORT, QDRANT_API_KEY
REDIS_URL
```

**2. AI/ML Services**
```
OPENAI_API_KEY (embeddings)
ANTHROPIC_API_KEY (Claude)
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```

**3. Application Settings**
```
ENVIRONMENT (dev/staging/production)
LOG_LEVEL, LOG_FORMAT, LOG_FILE
API_TIMEOUT, BATCH_SIZE, MAX_WORKERS
```

**4. Monitoring**
```
PROMETHEUS_ENABLED, PROMETHEUS_PORT
GRAFANA_ENABLED, GRAFANA_PORT
ALERT_ENABLED, ALERT_WEBHOOK
```

**5. Security**
```
SECRET_KEY (JWT signing)
CORS_ORIGINS
API_KEY_ENABLED
```

**6. Graphiti**
```
GRAPHITI_ENABLED, GRAPHITI_LLM_MODEL
ENABLE_GRAPHITI_EXTRACTION (feature flag)
```

**7. Google Drive Integration**
```
GOOGLE_DRIVE_ENABLED
GOOGLE_DRIVE_SERVICE_ACCOUNT_KEY
GOOGLE_DRIVE_MONITOR_FOLDER_ID
```

**8. Temporal.io**
```
TEMPORAL_HOST, TEMPORAL_NAMESPACE
TEMPORAL_CLOUD_ENDPOINT, TEMPORAL_CLIENT_CERT_PATH
```

**9. Feature Flags**
```
ENABLE_GRAPHITI_EXTRACTION
ENABLE_QUERY_ROUTER
ENABLE_TEMPORAL_WORKFLOWS
ENABLE_GOOGLE_DRIVE_INTEGRATION
```

---

## V. Deployment Paths

### Available Deployments

| Deployment | Status | Timeline | Cost | Documentation |
|------------|--------|----------|------|---------------|
| **MCP Server (PyPI)** | 82% complete, 🔴 Blocked (Python version mismatch) | 5-6 hours to fix | Free (open source) | deployment/mcp-server/ |
| **Production Cloud (GCP)** | 📝 Planned, 75% ready | 4-5 weeks, 90-126 hours | $500-700/month start, scales to $1,500+ | deployment/PRODUCTION-DEPLOYMENT-PLAN.md |
| **Google Drive Integration** | ✅ Production Ready | Ready to deploy | Included in GCP costs | deployment/components/google-drive-integration/ |
| **Query Router** | ✅ Deployed | Completed Oct 2025 | Included in API | deployment/components/query-router/ |
| **Pre-Deployment Verification** | ✅ Complete | 3-4 hours | N/A | deployment/verification/ |
| **Pre-Deployment Testing** | ✅ Complete | 3-4 hours | N/A | deployment/testing/ |

### Deployment Documentation

**Master Guide:** `deployment/README.md`

**Component-Specific:**
- MCP Server: `deployment/mcp-server/DEPLOYMENT-CHECKLIST.md`, `PUBLISHING.md`
- Production GCP: `deployment/production/GCP-DEPLOYMENT-GUIDE.md`, `ARCHITECTURE.md`
- Google Drive: `deployment/components/google-drive-integration/DEPLOYMENT-GUIDE.md`
- Query Router: `deployment/components/query-router/DEPLOYMENT-GUIDE.md`

**Verification:**
- `deployment/verification/WORKFLOW-CHECKLIST.md` - 23/23 verifications passing
- `deployment/testing/TESTING-KIT.md` - 230+ tests passing

---

## ⚡ Quick Technology Highlights

### Top 10 Most Critical Technologies

1. **FastAPI** - Modern async web framework
2. **Temporal.io** - Workflow orchestration
3. **PostgreSQL + pgvector** - Hybrid database
4. **Neo4j** - Graph relationships
5. **Qdrant** - Vector search
6. **OpenAI** - Embeddings
7. **Graphiti** - Temporal intelligence
8. **Docker** - Containerization
9. **Prometheus + Grafana** - Monitoring
10. **Pytest** - Testing framework

### Unique Differentiators

**Multi-Database Parallel Architecture:**
- 4 databases working in parallel (PostgreSQL, Neo4j, Qdrant, Redis)
- Saga pattern for distributed transactions
- Adaptive routing based on performance
- <1s P95 latency across all databases

**LLM-Powered Intelligence:**
- **Graphiti:** 90%+ entity extraction accuracy (vs 60% regex baseline)
- **Query Router:** 90% intent classification accuracy
- **Apex MCP:** Multi-query orchestration with narrative synthesis

**Production-Grade Observability:**
- **27 Temporal Metrics** across 6 monitoring layers
- **5 Grafana Dashboards** with 33+ panels
- **12+ Alert Rules** with runbook links
- **156+ Tests** with 80%+ coverage

**Developer Experience:**
- **21 Custom Agents** (C-suite executives + research team)
- **8 MCP Servers** for extended capabilities
- **54 Python Scripts** + 7 Shell Scripts for automation
- **Comprehensive Documentation** (31+ README files)

**Workflow Orchestration:**
- **Temporal Cloud** for durable execution
- **Saga Pattern** for distributed transactions
- **4 Workflows:** Document Ingestion, Structured Data Ingestion, Google Drive Monitor, Google Drive Archive
- **Scheduled Execution:** Google Drive monitoring every 15 minutes

---

## 📊 Total Technologies Inventoried

**Total Count:** 200+ distinct tools, libraries, services, and platforms

**Breakdown:**
- **96 Python Packages** (48 production + 28 dev + 20 test)
- **8 Container Images**
- **8 MCP Servers**
- **21 Custom Agents**
- **11 GCP Services**
- **4 Primary Databases** + 6 extensions/plugins
- **6 AI/ML Services**
- **54 Python Scripts** + 7 Shell Scripts
- **14 Test Markers**
- **5 Grafana Dashboards**
- **12+ Alert Rules**
- **7 Alembic Migrations**

---

## 🎯 Technology Selection Philosophy

**Key Principles:**

1. **Best-in-Class** - Choose industry-leading tools for each category
2. **Python-First** - Unified language across stack (Python for app, infrastructure, testing)
3. **Managed Services** - Prefer managed services to minimize ops overhead (Temporal Cloud, Grafana Cloud)
4. **Open Source** - Favor open source with strong communities (FastAPI, Neo4j, Qdrant)
5. **Production-Ready** - All tools battle-tested at scale
6. **Developer Experience** - Tools that enhance productivity (Cursor IDE, Claude Code, MCP)

**Strategic Choices:**

- **FastAPI over Django/Flask** - Modern async, automatic OpenAPI docs, high performance
- **Temporal.io over Celery** - Durable execution, saga pattern, superior observability
- **Multi-database over Single Database** - Parallel specialization (graph, vector, relational, cache)
- **Pulumi over Terraform** - Python IaC (unified language), faster deployments
- **Cloud Run over Kubernetes** - Simpler ops for solo developer, auto-scaling, pay-per-use
- **Grafana Cloud over Datadog** - $19/month vs $79k/year, open source
- **Graphiti over Custom Extraction** - LLM-powered, 90%+ accuracy, temporal reasoning

---

**End of Technology Inventory**

**Document Version:** 1.0
**Last Updated:** 2025-11-07
**Maintained By:** Richard Glaubitz

---

**This inventory provides a complete, permanent record of every technology used in the Apex Memory System project. For deployment planning, see `deployment/PRODUCTION-DEPLOYMENT-PLAN.md`.**
