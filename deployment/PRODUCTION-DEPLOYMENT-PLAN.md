# Apex Memory System - Production Deployment Plan

**Status:** Ready for Execution
**Timeline:** 4-5 weeks (90-126 hours)
**Target Platform:** Google Cloud Platform (Cloud Run + Managed Services)
**Infrastructure-as-Code:** Pulumi (Python)
**Monthly Cost:** $500-700/month (start), auto-scales to $1,500+ as needed
**Performance Target:** P95 latency <1s, 99.9% uptime, no performance sacrifice

---

## Executive Summary

Deploy Apex Memory System to Google Cloud Platform with production-grade infrastructure, full CI/CD automation, and auto-scaling capabilities. Right-sized for 1-15 users initially with zero performance compromise.

**Key Decisions:**
- ✅ **Pulumi (Python)** - Infrastructure-as-code using same language as application
- ✅ **Cloud Run (Serverless)** - Auto-scaling, pay-per-use, zero cold starts (min-instances=1)
- ✅ **Managed Services** - Cloud SQL, Memorystore, Temporal Cloud (minimize ops overhead)
- ✅ **Auto-Scaling** - Start small ($500/month), auto-scale to production tier ($1,500+) as usage grows
- ✅ **Production-Ready** - Full automation, monitoring, alerting, rollback capabilities

---

## ⚠️ PREREQUISITES - COMPLETE BEFORE STARTING

**CRITICAL:** Before starting Week 1, you MUST complete all items in:

📋 **[DEPLOYMENT-NEEDS.md](DEPLOYMENT-NEEDS.md)** - Complete prerequisite checklist

**Quick checklist:**
- [ ] GCP Account created (with $300 free credit)
- [ ] Temporal Cloud account ($100-150/month)
- [ ] Grafana Cloud Pro ($19/month)
- [ ] OpenAI API key obtained
- [ ] Anthropic API key obtained
- [ ] Docker Desktop licensed (verify if Business license needed)
- [ ] All secrets generated and stored in password manager
- [ ] 2FA enabled on all accounts

**Estimated setup time:** 4-6 hours (spread over 1-2 days)
**Monthly cost:** $149-249/month for first 90 days (with GCP credits), then $411-807/month

**DO NOT PROCEED** until all prerequisites are complete. See [DEPLOYMENT-NEEDS.md](DEPLOYMENT-NEEDS.md) for detailed instructions.

---

## Table of Contents

1. [Prerequisites](#prerequisites---complete-before-starting)
2. [Current State Assessment](#current-state-assessment)
3. [Deployment Architecture](#deployment-architecture)
4. [Week-by-Week Plan](#week-by-week-plan)
5. [Cost Analysis](#cost-analysis)
6. [Performance Targets](#performance-targets)
7. [Risk Mitigation](#risk-mitigation)
8. [Success Criteria](#success-criteria)
9. [Post-Deployment](#post-deployment)

---

## Current State Assessment

### ✅ Strong Foundation (75% Ready)

**What Exists Today:**
- ✅ **Excellent Documentation** - Comprehensive deployment guide (1,755 lines), architecture (632 lines), checklists
- ✅ **Mature Testing** - 477 tests (156+ passing baseline), >80% coverage likely
- ✅ **Production Monitoring** - 27 Temporal metrics, 12+ alerts, 5 Grafana dashboards
- ✅ **Database Migrations** - 7 Alembic migrations, complete schema files for all 4 databases
- ✅ **Docker Configs** - Multi-stage builds, non-root users, health checks
- ✅ **CI/CD Pipeline** - GitHub Actions with lint, security scan, unit tests, integration tests
- ✅ **Environment Management** - Complete `.env.example` and `.env.production.example`

### 🔴 Critical Gaps (Must Fix Before Deployment)

**What's Missing:**
1. ❌ **No Infrastructure-as-Code** - Manual `gcloud` commands, not reproducible
2. ❌ **Dockerfile Path Error** - `src.apex_memory.main` should be `apex_memory.main` (line 48)
3. ❌ **Hardcoded Secret** - Default `SECRET_KEY` in `config/settings.py:41`
4. ⚠️ **No Production Configs** - Missing Prometheus/Grafana/Nginx production configs
5. ⚠️ **No Deployment Automation** - CI/CD only tests, doesn't deploy

**Estimated Effort to Address:** 90-126 hours (4-5 weeks)

---

## Deployment Architecture

### High-Level Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                   Internet (Users/API Clients)                    │
└────────────────────────────┬─────────────────────────────────────┘
                             │ HTTPS (TLS)
┌────────────────────────────▼─────────────────────────────────────┐
│               Cloud Load Balancer (GCP Global)                    │
│                 SSL Certificate (auto-renewal)                    │
│                   Cloud Armor (DDoS protection)                   │
└────────────────────────────┬─────────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
┌───────▼──────────┐  ┌──────▼──────────┐  ┌─────▼───────────┐
│   Cloud Run      │  │   Cloud Run     │  │   Cloud Run     │
│   FastAPI API    │  │   Temporal      │  │    Qdrant       │
│   (min=1, max=10)│  │   Workers       │  │  Vector Search  │
│   2GB RAM/2 vCPU │  │   (min=1, max=5)│  │   (min=1, max=3)│
└───────┬──────────┘  └──────┬──────────┘  └─────┬───────────┘
        │                    │                    │
        └────────────────────┼────────────────────┘
                             │
              ┌──────────────┴──────────────┐
              │    VPC Connector             │
              │  (Private networking)        │
              └──────────────┬───────────────┘
                             │
    ┌────────────────────────┼────────────────────────┐
    │                        │                        │
┌───▼─────────────┐  ┌───────▼────────┐  ┌──────────▼──────────┐
│  Cloud SQL      │  │  Memorystore   │  │  Compute Engine     │
│  PostgreSQL     │  │  Redis Cache   │  │  Neo4j Graph DB     │
│  + pgvector     │  │  (Basic 1GB)   │  │  (e2-small 2GB)     │
│  (db-f1-micro)  │  │  Auto-scale    │  │  Auto-upgrade       │
└─────────────────┘  └────────────────┘  └─────────────────────┘
        │                                          │
        │     ┌──────────────────────────────┐    │
        └────▶│    GCP Secret Manager        │◀───┘
              │   (All credentials)          │
              └──────────────────────────────┘
                             │
              ┌──────────────▼───────────────┐
              │    Temporal Cloud            │
              │   (Workflow orchestration)   │
              │   Essentials tier            │
              └──────────────────────────────┘
                             │
              ┌──────────────▼───────────────┐
              │  Grafana Cloud Pro           │
              │  (Metrics & monitoring)      │
              │  $19/month                   │
              └──────────────────────────────┘
```

### Technology Stack

**Compute:**
- Cloud Run (API, Temporal Workers, Qdrant)
- Compute Engine (Neo4j VM)

**Databases:**
- Cloud SQL: PostgreSQL 15 + pgvector (db-f1-micro → db-n1-standard-1)
- Memorystore: Redis 7 (Basic 1GB)
- Neo4j: Community Edition on e2-small VM
- Qdrant: Containerized on Cloud Run

**Orchestration:**
- Temporal Cloud (Essentials tier, $100-150/month)

**Monitoring:**
- Prometheus (Cloud Run)
- Grafana Cloud Pro ($19/month)
- Cloud Monitoring (GCP native)

**Security:**
- GCP Secret Manager
- Cloud Armor (DDoS protection)
- Cloud Load Balancer (SSL/TLS termination)

**Infrastructure-as-Code:**
- Pulumi (Python)

**CI/CD:**
- GitHub Actions

---

## Week-by-Week Plan

### Week 1: Foundation & Quick Wins (24-32 hours)

#### Day 1-2: Infrastructure Setup & Quick Fixes (6 hours)

**Quick Wins (2 hours):**

1. **Fix Dockerfile API Path Error** (30 min)
   - File: `docker/Dockerfile.api:48`
   - Change: `CMD ["uvicorn", "src.apex_memory.main:app", ...]` → `CMD ["uvicorn", "apex_memory.main:app", ...]`
   - Impact: Prevents container startup failure

2. **Remove Hardcoded SECRET_KEY** (30 min)
   - File: `src/apex_memory/config/settings.py:41`
   - Change: Remove default `"CHANGE_THIS_SECRET_KEY_IN_PRODUCTION"`
   - Add: Validation to raise error if `SECRET_KEY` not provided in production
   - Impact: Prevents critical security vulnerability

3. **Create .dockerignore** (15 min)
   - File: `docker/.dockerignore`
   - Content: Exclude `.git/`, `tests/`, `venv/`, `*.pyc`, `.env`, `__pycache__/`
   - Impact: Reduces Docker image size by ~50%

4. **Run Security Scan** (15 min)
   - Command: `safety check`
   - Fix: Update any vulnerable dependencies
   - Document: Record vulnerabilities found and fixes applied

5. **Verify Test Baseline** (30 min)
   - Command: `cd apex-memory-system && pytest --co -q`
   - Verify: 477 tests collected
   - Run: Full test suite to establish baseline

**GCP Project Setup (4 hours):**

6. **Create Production GCP Project**
   - Project ID: `apex-memory-prod`
   - Organization: (your GCP organization)
   - Billing account: Link production billing account
   - Budget alert: $700/month threshold (email notification)

7. **Enable Required APIs**
   ```bash
   gcloud services enable \
     cloudrun.googleapis.com \
     sql-component.googleapis.com \
     sqladmin.googleapis.com \
     redis.googleapis.com \
     compute.googleapis.com \
     secretmanager.googleapis.com \
     cloudresourcemanager.googleapis.com \
     iam.googleapis.com \
     container.googleapis.com \
     logging.googleapis.com \
     monitoring.googleapis.com
   ```

8. **Configure VPC Network**
   - Create VPC: `apex-vpc`
   - Subnet: `apex-subnet-us-central1` (10.0.0.0/24)
   - Create Cloud Run VPC Connector: `apex-vpc-connector`
   - Purpose: Allow Cloud Run to access Cloud SQL/Memorystore privately

9. **Set Up IAM Service Accounts**
   - `apex-api@apex-memory-prod.iam.gserviceaccount.com` - API service account
   - `apex-worker@apex-memory-prod.iam.gserviceaccount.com` - Worker service account
   - Permissions: Secret Manager read, Cloud SQL client, Memorystore client

#### Day 3-5: Secret Manager & Pulumi Setup (18-26 hours)

**Secret Manager Setup (6 hours):**

10. **Create Secrets in GCP Secret Manager**
    ```bash
    # Database credentials
    echo -n "your-secret-key" | gcloud secrets create apex-secret-key --data-file=-
    echo -n "postgres-password" | gcloud secrets create apex-postgres-password --data-file=-
    echo -n "neo4j-password" | gcloud secrets create apex-neo4j-password --data-file=-

    # API keys
    echo -n "sk-..." | gcloud secrets create apex-openai-api-key --data-file=-
    echo -n "sk-ant-..." | gcloud secrets create apex-anthropic-api-key --data-file=-

    # Temporal Cloud
    echo -n "temporal-cert" | gcloud secrets create apex-temporal-cert --data-file=-
    echo -n "temporal-key" | gcloud secrets create apex-temporal-key --data-file=-
    ```

11. **Implement Secret Manager Client**
    - File: `src/apex_memory/config/secrets.py` (NEW)
    - Class: `SecretManagerClient` with `get_secret(secret_id)` method
    - Integration: Uses Google Cloud Secret Manager SDK

12. **Update Settings Class**
    - File: `src/apex_memory/config/settings.py`
    - Change: Use `SecretManagerClient` in production (`ENVIRONMENT == "production"`)
    - Fallback: Use environment variables in development
    - Validation: Raise `ValueError` if required secrets missing in production

13. **Test Locally**
    - Set `GOOGLE_APPLICATION_CREDENTIALS` to service account key
    - Run: `python -c "from apex_memory.config import settings; print(settings.SECRET_KEY)"`
    - Verify: Secret fetched from Secret Manager

**Pulumi Infrastructure Code (12-20 hours):**

14. **Initialize Pulumi Project**
    ```bash
    cd /Users/richardglaubitz/Projects/Apex-Memory-System-Development
    mkdir infrastructure
    cd infrastructure
    pulumi new gcp-python --name apex-memory --description "Apex Memory System Infrastructure"
    ```

15. **Create Project Structure**
    ```
    infrastructure/
    ├── pulumi/
    │   ├── __main__.py           # Main Pulumi program
    │   ├── Pulumi.yaml           # Project config
    │   ├── Pulumi.dev.yaml       # Dev stack config
    │   ├── Pulumi.staging.yaml   # Staging stack config
    │   ├── Pulumi.production.yaml # Production stack config
    │   ├── requirements.txt      # Pulumi dependencies
    │   └── modules/
    │       ├── __init__.py
    │       ├── databases.py      # Cloud SQL, Redis, Neo4j, Qdrant
    │       ├── networking.py     # VPC, Load Balancer, Cloud Armor
    │       ├── compute.py        # Cloud Run services
    │       ├── secrets.py        # Secret Manager integration
    │       └── monitoring.py     # Cloud Monitoring, log sinks
    ```

16. **Create Databases Module (`modules/databases.py`)**
    - Cloud SQL PostgreSQL (pgvector extension)
    - Memorystore Redis
    - Neo4j VM (Compute Engine)
    - Qdrant Cloud Run service
    - Auto-scaling configurations

17. **Create Networking Module (`modules/networking.py`)**
    - VPC and subnets
    - Cloud Run VPC Connector
    - Cloud Load Balancer
    - Cloud Armor DDoS protection
    - SSL certificate (auto-renewal)

18. **Create Compute Module (`modules/compute.py`)**
    - Cloud Run API service
    - Cloud Run Temporal Worker service
    - Container registry (GCR)
    - IAM bindings

19. **Create Secrets Module (`modules/secrets.py`)**
    - Secret Manager secrets
    - IAM bindings for service accounts
    - Secret versioning

20. **Create Monitoring Module (`modules/monitoring.py`)**
    - Cloud Monitoring workspaces
    - Uptime checks (every 1 minute)
    - Log sinks to Cloud Storage
    - Alert policies

21. **Create Main Pulumi Program (`__main__.py`)**
    - Import all modules
    - Configure stack-specific settings (dev/staging/production)
    - Export outputs (API URL, database endpoints, etc.)

22. **Test Pulumi Preview**
    ```bash
    pulumi stack init dev
    pulumi preview
    ```
    - Verify: All resources plan correctly
    - Fix: Any configuration errors

---

### Week 2: Dockerization & Configuration (24-30 hours)

#### Day 1-2: Production Dockerfiles (10-14 hours)

**Create Production-Hardened Dockerfiles:**

23. **Dockerfile.api.production** (NEW)
    ```dockerfile
    # Build stage
    FROM python:3.11-slim AS builder

    WORKDIR /build

    # Install build dependencies
    RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
        g++ \
        libpq-dev \
        && rm -rf /var/lib/apt/lists/*

    # Copy requirements and install
    COPY requirements.txt .
    RUN pip install --no-cache-dir --user -r requirements.txt

    # Runtime stage
    FROM python:3.11-slim

    # Install runtime dependencies only
    RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq5 \
        curl \
        && rm -rf /var/lib/apt/lists/*

    # Create non-root user
    RUN useradd -m -u 1000 -s /bin/bash apex && \
        mkdir -p /app /tmp/apex-staging && \
        chown -R apex:apex /app /tmp/apex-staging

    WORKDIR /app

    # Copy Python packages from builder
    COPY --from=builder /root/.local /home/apex/.local

    # Copy application code
    COPY --chown=apex:apex src/ ./src/
    COPY --chown=apex:apex alembic/ ./alembic/
    COPY --chown=apex:apex alembic.ini .

    # Switch to non-root user
    USER apex

    # Add Python packages to PATH
    ENV PATH=/home/apex/.local/bin:$PATH
    ENV PYTHONPATH=/app/src:$PYTHONPATH

    # Resource limits (configured in Cloud Run)
    # CPU: 2 cores, Memory: 2GB

    # Health check
    HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
        CMD curl -f http://localhost:8000/api/v1/health || exit 1

    # Expose port
    EXPOSE 8000

    # Run with Gunicorn + Uvicorn workers
    CMD ["gunicorn", "apex_memory.main:app", \
         "--workers", "4", \
         "--worker-class", "uvicorn.workers.UvicornWorker", \
         "--bind", "0.0.0.0:8000", \
         "--timeout", "300", \
         "--max-requests", "1000", \
         "--max-requests-jitter", "50", \
         "--access-logfile", "-", \
         "--error-logfile", "-", \
         "--log-level", "info"]
    ```

24. **Dockerfile.worker.production** (NEW)
    ```dockerfile
    # Build stage
    FROM python:3.11-slim AS builder

    WORKDIR /build

    RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
        g++ \
        libpq-dev \
        && rm -rf /var/lib/apt/lists/*

    COPY requirements.txt .
    RUN pip install --no-cache-dir --user -r requirements.txt

    # Runtime stage
    FROM python:3.11-slim

    RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq5 \
        && rm -rf /var/lib/apt/lists/*

    RUN useradd -m -u 1000 -s /bin/bash apex && \
        mkdir -p /app /tmp/apex-staging && \
        chown -R apex:apex /app /tmp/apex-staging

    WORKDIR /app

    COPY --from=builder /root/.local /home/apex/.local
    COPY --chown=apex:apex src/ ./src/

    USER apex

    ENV PATH=/home/apex/.local/bin:$PATH
    ENV PYTHONPATH=/app/src:$PYTHONPATH

    # Graceful shutdown handler for Temporal worker
    STOPSIGNAL SIGTERM

    # Resource limits (configured in Cloud Run)
    # CPU: 1 core, Memory: 1GB

    # Run Temporal worker
    CMD ["python", "-m", "apex_memory.temporal.workers.dev_worker"]
    ```

25. **Update .dockerignore**
    ```
    .git/
    .github/
    tests/
    venv/
    .env
    .env.*
    *.pyc
    __pycache__/
    .pytest_cache/
    .coverage
    htmlcov/
    *.log
    .DS_Store
    *.md
    docs/
    media/
    session-logs/
    research/
    upgrades/
    workflow/
    deployment/
    ```

26. **Test Docker Builds Locally**
    ```bash
    cd apex-memory-system

    # Build API
    docker build -f docker/Dockerfile.api.production -t apex-api:latest .

    # Build Worker
    docker build -f docker/Dockerfile.worker.production -t apex-worker:latest .

    # Test API
    docker run -p 8000:8000 --env-file .env apex-api:latest
    # Verify: http://localhost:8000/docs

    # Test Worker
    docker run --env-file .env.temporal apex-worker:latest
    ```

27. **Optimize Image Size**
    - Verify: Multi-stage builds reduce size by ~50%
    - Check: `docker images | grep apex`
    - Target: API <500MB, Worker <400MB

#### Day 3-4: Production Configuration Files (10-12 hours)

**Prometheus Production Config:**

28. **monitoring/prometheus.production.yml** (NEW)
    ```yaml
    global:
      scrape_interval: 15s
      evaluation_interval: 15s
      external_labels:
        cluster: 'apex-memory-prod'
        environment: 'production'

    # Remote write to Grafana Cloud
    remote_write:
      - url: https://prometheus-prod-XX-XXXX.grafana.net/api/prom/push
        basic_auth:
          username: <grafana-cloud-user-id>
          password: <grafana-cloud-api-key>

    scrape_configs:
      - job_name: 'apex-api'
        static_configs:
          - targets: ['apex-api:8000']
        metrics_path: '/metrics'
        scheme: http

      - job_name: 'apex-worker'
        static_configs:
          - targets: ['apex-worker:8080']
        metrics_path: '/metrics'
        scheme: http

      - job_name: 'temporal-metrics'
        static_configs:
          - targets: ['temporal.cloud:443']
        scheme: https
        tls_config:
          insecure_skip_verify: false

      - job_name: 'postgres'
        static_configs:
          - targets: ['postgres-exporter:9187']

      - job_name: 'redis'
        static_configs:
          - targets: ['redis-exporter:9121']
    ```

**Grafana Provisioning:**

29. **monitoring/grafana/provisioning/datasources/production.yml** (NEW)
    ```yaml
    apiVersion: 1

    datasources:
      - name: Prometheus
        type: prometheus
        access: proxy
        url: http://prometheus:9090
        isDefault: true
        editable: false

      - name: Cloud Logging
        type: stackdriver
        access: proxy
        jsonData:
          authenticationType: gce
          defaultProject: apex-memory-prod
        editable: false
    ```

30. **monitoring/grafana/provisioning/dashboards/default.yml** (NEW)
    ```yaml
    apiVersion: 1

    providers:
      - name: 'Apex Dashboards'
        orgId: 1
        folder: ''
        type: file
        disableDeletion: false
        updateIntervalSeconds: 10
        allowUiUpdates: true
        options:
          path: /etc/grafana/provisioning/dashboards
    ```

31. **monitoring/grafana/provisioning/notifiers/production.yml** (NEW)
    ```yaml
    notifiers:
      - name: Email
        type: email
        uid: email-notifier
        org_id: 1
        is_default: true
        settings:
          addresses: alerts@yourdomain.com

      - name: Slack
        type: slack
        uid: slack-notifier
        org_id: 1
        settings:
          url: https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
          username: Apex Memory Alerts
          icon_emoji: ":warning:"
    ```

**Nginx/Load Balancer Config:**

32. **infrastructure/nginx/nginx.conf** (NEW)
    ```nginx
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=100r/m;
    limit_req_status 429;

    upstream apex_api {
        server apex-api:8000;
    }

    server {
        listen 443 ssl http2;
        server_name api.apexmemory.com;

        # SSL Configuration (managed by GCP Load Balancer)
        ssl_certificate /etc/ssl/certs/apex-cert.pem;
        ssl_certificate_key /etc/ssl/private/apex-key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;

        # Security headers
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;

        # Rate limiting
        location /api/ {
            limit_req zone=api_limit burst=20 nodelay;
            proxy_pass http://apex_api;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Health check (no rate limiting)
        location /api/v1/health {
            proxy_pass http://apex_api;
            access_log off;
        }
    }
    ```

#### Day 5: API Versioning (4-6 hours)

33. **Add API Versioning to FastAPI**
    - File: `src/apex_memory/main.py`
    - Change: Prefix all routes with `/api/v1/`
    - Example: `/query` → `/api/v1/query`
    - Update: All router includes to use prefix

34. **Update API Documentation**
    - File: `apex-memory-system/README.md`
    - Document: API versioning strategy
    - Add: Deprecation policy (v1 supported for 12 months after v2 release)

35. **Update Client Examples**
    - Files: Any documentation with API endpoint examples
    - Change: Update URLs to include `/api/v1/` prefix

36. **Test API Versioning**
    ```bash
    # Start API locally
    uvicorn apex_memory.main:app --reload

    # Test endpoints
    curl http://localhost:8000/api/v1/health
    curl -X POST http://localhost:8000/api/v1/query -H "Content-Type: application/json" -d '{"query": "test"}'

    # Verify OpenAPI docs
    # http://localhost:8000/docs (should show /api/v1/ prefix)
    ```

---

### Week 3: Temporal Cloud & Testing (26-32 hours)

#### Day 1-2: Temporal Cloud Setup (8-10 hours)

**Temporal Cloud Namespace:**

37. **Create Temporal Cloud Account**
    - Sign up: https://temporal.io/cloud
    - Plan: Essentials tier ($100-150/month)
    - Features: 1M actions/month, 7-30 day retention, 99.9% SLA

38. **Create Namespace**
    - Namespace: `apex-memory-prod`
    - Region: `us-central1` (same as GCP)
    - Retention: 30 days

39. **Generate mTLS Certificates**
    ```bash
    # Generate CA certificate
    openssl req -x509 -newkey rsa:4096 -keyout ca.key -out ca.pem -days 3650 -nodes

    # Generate client certificate
    openssl req -newkey rsa:4096 -keyout client.key -out client.csr -nodes
    openssl x509 -req -in client.csr -CA ca.pem -CAkey ca.key -CAcreateserial -out client.pem -days 3650

    # Upload to Temporal Cloud
    # (via Temporal Cloud UI: Settings → Certificates)
    ```

40. **Store Certificates in Secret Manager**
    ```bash
    gcloud secrets create apex-temporal-cert --data-file=client.pem
    gcloud secrets create apex-temporal-key --data-file=client.key
    gcloud secrets create apex-temporal-ca --data-file=ca.pem
    ```

41. **Update Environment Variables**
    - File: `.env.production.example`
    - Add:
      ```
      TEMPORAL_CLOUD_ENDPOINT=apex-memory-prod.tmprl.cloud:7233
      TEMPORAL_NAMESPACE=apex-memory-prod
      TEMPORAL_CLIENT_CERT_PATH=/secrets/temporal-cert
      TEMPORAL_CLIENT_KEY_PATH=/secrets/temporal-key
      ```

**Worker Deployment on Cloud Run:**

42. **Update Worker to Use Temporal Cloud**
    - File: `src/apex_memory/temporal/workers/dev_worker.py`
    - Change: Connect to Temporal Cloud endpoint
    - Add: mTLS certificate loading
    - Test: Connection locally first

43. **Deploy Worker to Cloud Run** (via Pulumi)
    - Update: `modules/compute.py` to include worker service
    - Configure: Min instances=1, max instances=5
    - Mount: Secrets from Secret Manager as environment variables

44. **Test Workflow Execution**
    ```python
    # Test script: scripts/temporal/test-cloud-connection.py
    from temporalio.client import Client
    from apex_memory.temporal.workflows.ingestion import DocumentIngestionWorkflow

    async def test():
        client = await Client.connect(
            "apex-memory-prod.tmprl.cloud:7233",
            namespace="apex-memory-prod",
            tls=True,  # Load certs from environment
        )

        result = await client.execute_workflow(
            DocumentIngestionWorkflow.run,
            args=["test-doc-id"],
            id="test-workflow-1",
            task_queue="apex-ingestion-tasks",
        )
        print(f"Workflow result: {result}")

    if __name__ == "__main__":
        import asyncio
        asyncio.run(test())
    ```

#### Day 3-4: Staging Deployment & Testing (12-16 hours)

**Deploy to Staging:**

45. **Create Staging Stack**
    ```bash
    cd infrastructure/pulumi
    pulumi stack init staging
    pulumi config set gcp:project apex-memory-staging
    pulumi config set gcp:region us-central1
    ```

46. **Deploy Infrastructure**
    ```bash
    pulumi up --stack staging
    ```
    - Verify: All resources created (Cloud SQL, Memorystore, Neo4j VM, Cloud Run services)
    - Note: Endpoint URLs for API, worker

47. **Run Database Migrations**
    ```bash
    # Connect to Cloud SQL instance
    gcloud sql connect apex-postgres-staging --user=postgres

    # Run Alembic migrations
    cd apex-memory-system
    alembic upgrade head
    ```

48. **Deploy Application Containers**
    ```bash
    # Build and push API
    docker build -f docker/Dockerfile.api.production -t gcr.io/apex-memory-staging/apex-api:latest .
    docker push gcr.io/apex-memory-staging/apex-api:latest

    # Build and push Worker
    docker build -f docker/Dockerfile.worker.production -t gcr.io/apex-memory-staging/apex-worker:latest .
    docker push gcr.io/apex-memory-staging/apex-worker:latest

    # Deploy via Cloud Run (or Pulumi updates)
    gcloud run deploy apex-api --image gcr.io/apex-memory-staging/apex-api:latest --region us-central1
    gcloud run deploy apex-worker --image gcr.io/apex-memory-staging/apex-worker:latest --region us-central1
    ```

**Validation Testing:**

49. **Smoke Tests (4 Critical Paths)**
    ```bash
    # 1. Health Check
    curl https://apex-api-staging-xxxxx-uc.a.run.app/api/v1/health

    # 2. Authentication
    curl -X POST https://apex-api-staging-xxxxx-uc.a.run.app/api/v1/auth/login \
      -H "Content-Type: application/json" \
      -d '{"username": "test", "password": "test"}'

    # 3. Document Ingestion
    curl -X POST https://apex-api-staging-xxxxx-uc.a.run.app/api/v1/ingest \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer <token>" \
      -d '{"document": "test content"}'

    # 4. Query
    curl -X POST https://apex-api-staging-xxxxx-uc.a.run.app/api/v1/query \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer <token>" \
      -d '{"query": "test query"}'
    ```

50. **Load Tests (Locust)**
    ```python
    # tests/load/locustfile.py
    from locust import HttpUser, task, between

    class ApexMemoryUser(HttpUser):
        wait_time = between(1, 3)

        @task(3)
        def query(self):
            self.client.post("/api/v1/query", json={"query": "test"})

        @task(1)
        def ingest(self):
            self.client.post("/api/v1/ingest", json={"document": "test"})
    ```

    Run:
    ```bash
    locust -f tests/load/locustfile.py --host https://apex-api-staging-xxxxx-uc.a.run.app --users 10 --spawn-rate 1 --run-time 10m
    ```

51. **Integration Tests (Full Suite)**
    ```bash
    # Set staging environment variables
    export API_URL=https://apex-api-staging-xxxxx-uc.a.run.app
    export DATABASE_URL=<staging-db-url>

    # Run all integration tests
    cd apex-memory-system
    pytest tests/integration/ -v --tb=short

    # Verify: All tests pass
    ```

52. **Performance Validation**
    - Metric: P95 latency <1s for API requests
    - Tool: Grafana dashboard (Apex Overview)
    - Check: Query router latency, database response times
    - Document: Baseline metrics for production comparison

#### Day 5: Monitoring Validation (6 hours)

53. **Verify Grafana Dashboards**
    - Navigate: https://grafana.com (Grafana Cloud)
    - Import: 5 existing dashboards (Apex Overview, Graphiti, Query Router, Saga, Temporal Ingestion)
    - Verify: Metrics flowing from staging environment
    - Check: All 27 Temporal metrics visible

54. **Test Alert Rules**
    - Simulate: High error rate (send bad requests to API)
    - Verify: Alert fires in Grafana
    - Check: Notification sent to Slack/email
    - Document: Alert response time

55. **Configure Alert Notification Channels**
    - Email: alerts@yourdomain.com
    - Slack: #apex-alerts channel webhook
    - PagerDuty: (optional) for critical alerts

56. **Create Operational Runbook**
    - File: `deployment/OPERATIONAL-RUNBOOK.md`
    - Content: Incident response, escalation paths, common issues
    - Include: Alert descriptions, remediation steps

---

### Week 4: Automation & Production Deployment (28-36 hours)

#### Day 1-2: CI/CD Automation (12-16 hours)

**GitHub Actions Deployment Workflow:**

57. **Create `.github/workflows/deploy-production.yml`**
    ```yaml
    name: Deploy to Production

    on:
      push:
        branches: [main]
      workflow_dispatch:  # Manual trigger

    env:
      GCP_PROJECT: apex-memory-prod
      GCP_REGION: us-central1

    jobs:
      test:
        runs-on: ubuntu-latest
        services:
          postgres:
            image: pgvector/pgvector:pg15
            env:
              POSTGRES_PASSWORD: test
            ports: ['5432:5432']
          redis:
            image: redis:7-alpine
            ports: ['6379:6379']
          qdrant:
            image: qdrant/qdrant:latest
            ports: ['6333:6333']
          neo4j:
            image: neo4j:5.15-community
            env:
              NEO4J_AUTH: neo4j/test
            ports: ['7687:7687']

        steps:
          - uses: actions/checkout@v3

          - name: Set up Python 3.11
            uses: actions/setup-python@v4
            with:
              python-version: '3.11'

          - name: Install dependencies
            run: |
              cd apex-memory-system
              pip install -r requirements-dev.txt

          - name: Run linters
            run: |
              cd apex-memory-system
              black --check src/ tests/
              isort --check-only src/ tests/
              flake8 src/ tests/ --max-line-length=100

          - name: Run security scans
            run: |
              cd apex-memory-system
              bandit -r src/
              safety check

          - name: Run tests
            env:
              DATABASE_URL: postgresql://postgres:test@localhost:5432/test
              REDIS_URL: redis://localhost:6379
              QDRANT_HOST: localhost
              QDRANT_PORT: 6333
              NEO4J_URI: bolt://localhost:7687
              NEO4J_USER: neo4j
              NEO4J_PASSWORD: test
            run: |
              cd apex-memory-system
              pytest --cov=src --cov-report=xml --cov-report=term

          - name: Upload coverage
            uses: codecov/codecov-action@v3
            with:
              file: ./apex-memory-system/coverage.xml

      build-and-push:
        needs: test
        if: github.ref == 'refs/heads/main'
        runs-on: ubuntu-latest

        steps:
          - uses: actions/checkout@v3

          - name: Set up Cloud SDK
            uses: google-github-actions/setup-gcloud@v1
            with:
              service_account_key: ${{ secrets.GCP_SA_KEY }}
              project_id: ${{ env.GCP_PROJECT }}

          - name: Configure Docker for GCR
            run: gcloud auth configure-docker

          - name: Build Docker images
            run: |
              cd apex-memory-system
              docker build -f docker/Dockerfile.api.production -t gcr.io/${{ env.GCP_PROJECT }}/apex-api:${{ github.sha }} .
              docker build -f docker/Dockerfile.api.production -t gcr.io/${{ env.GCP_PROJECT }}/apex-api:latest .
              docker build -f docker/Dockerfile.worker.production -t gcr.io/${{ env.GCP_PROJECT }}/apex-worker:${{ github.sha }} .
              docker build -f docker/Dockerfile.worker.production -t gcr.io/${{ env.GCP_PROJECT }}/apex-worker:latest .

          - name: Push Docker images
            run: |
              docker push gcr.io/${{ env.GCP_PROJECT }}/apex-api:${{ github.sha }}
              docker push gcr.io/${{ env.GCP_PROJECT }}/apex-api:latest
              docker push gcr.io/${{ env.GCP_PROJECT }}/apex-worker:${{ github.sha }}
              docker push gcr.io/${{ env.GCP_PROJECT }}/apex-worker:latest

      deploy-staging:
        needs: build-and-push
        runs-on: ubuntu-latest
        environment:
          name: staging
          url: https://apex-api-staging.run.app

        steps:
          - uses: actions/checkout@v3

          - name: Set up Cloud SDK
            uses: google-github-actions/setup-gcloud@v1
            with:
              service_account_key: ${{ secrets.GCP_SA_KEY }}
              project_id: apex-memory-staging

          - name: Deploy to Cloud Run (Staging)
            run: |
              gcloud run deploy apex-api \
                --image gcr.io/${{ env.GCP_PROJECT }}/apex-api:${{ github.sha }} \
                --region ${{ env.GCP_REGION }} \
                --platform managed \
                --allow-unauthenticated \
                --set-env-vars="ENVIRONMENT=staging"

              gcloud run deploy apex-worker \
                --image gcr.io/${{ env.GCP_PROJECT }}/apex-worker:${{ github.sha }} \
                --region ${{ env.GCP_REGION }} \
                --platform managed \
                --no-allow-unauthenticated \
                --set-env-vars="ENVIRONMENT=staging"

          - name: Run smoke tests
            run: |
              curl -f https://apex-api-staging.run.app/api/v1/health || exit 1

      deploy-production:
        needs: deploy-staging
        runs-on: ubuntu-latest
        environment:
          name: production
          url: https://api.apexmemory.com

        steps:
          - uses: actions/checkout@v3

          - name: Set up Cloud SDK
            uses: google-github-actions/setup-gcloud@v1
            with:
              service_account_key: ${{ secrets.GCP_SA_KEY }}
              project_id: ${{ env.GCP_PROJECT }}

          - name: Deploy to Cloud Run (Production)
            run: |
              # Deploy with traffic split (blue-green)
              gcloud run deploy apex-api \
                --image gcr.io/${{ env.GCP_PROJECT }}/apex-api:${{ github.sha }} \
                --region ${{ env.GCP_REGION }} \
                --platform managed \
                --allow-unauthenticated \
                --set-env-vars="ENVIRONMENT=production" \
                --no-traffic  # Deploy new revision without traffic

              # Get new revision name
              NEW_REVISION=$(gcloud run revisions list --service apex-api --region ${{ env.GCP_REGION }} --format="value(name)" --limit=1)

              # Gradually shift traffic (canary deployment)
              gcloud run services update-traffic apex-api \
                --region ${{ env.GCP_REGION }} \
                --to-revisions=$NEW_REVISION=10  # 10% traffic to new revision

              # Wait 5 minutes, monitor error rate
              sleep 300

              # If error rate OK, shift 100% traffic
              gcloud run services update-traffic apex-api \
                --region ${{ env.GCP_REGION }} \
                --to-latest

          - name: Verify deployment
            run: |
              curl -f https://api.apexmemory.com/api/v1/health || exit 1

          - name: Rollback on failure
            if: failure()
            run: |
              # Rollback to previous revision
              PREVIOUS_REVISION=$(gcloud run revisions list --service apex-api --region ${{ env.GCP_REGION }} --format="value(name)" --limit=2 | tail -n 1)
              gcloud run services update-traffic apex-api \
                --region ${{ env.GCP_REGION }} \
                --to-revisions=$PREVIOUS_REVISION=100
    ```

58. **Configure GitHub Environments**
    - GitHub repo → Settings → Environments
    - Create: `staging` (auto-deploy)
    - Create: `production` (manual approval required)
    - Add: Protection rules for production (require approval from 1 reviewer)

59. **Add GitHub Secrets**
    - `GCP_SA_KEY` - Service account key JSON for deployment
    - `GCP_PROJECT_ID` - apex-memory-prod
    - `CODECOV_TOKEN` - For coverage uploads

60. **Test CI/CD Pipeline**
    - Push: Small change to `main` branch
    - Verify: Workflow runs, tests pass, deploys to staging
    - Approve: Production deployment
    - Verify: Deploys to production with canary (10% → 100%)

#### Day 3-4: Production Deployment (12-16 hours)

**Pre-Deployment Checklist:**

61. **Run Full Test Suite**
    ```bash
    cd apex-memory-system
    pytest --cov=src --cov-report=term
    ```
    - Verify: All 477 tests pass
    - Verify: Coverage >80%

62. **Security Scan**
    ```bash
    bandit -r src/
    safety check
    ```
    - Verify: No critical vulnerabilities
    - Fix: Any medium/high severity issues

63. **Database Migrations Tested**
    - Verify: All migrations run successfully in staging
    - Backup: Create snapshot of staging database
    - Test: Rollback migration (ensure reversibility)

64. **Secrets Validated**
    - Verify: All secrets exist in GCP Secret Manager
    - Test: Secret retrieval works from production service accounts
    - Rotate: Any default/test credentials

**Deploy to Production:**

65. **Run Pulumi Deployment**
    ```bash
    cd infrastructure/pulumi
    pulumi stack select production
    pulumi up
    ```
    - Review: Resource plan (databases, networking, compute, monitoring)
    - Approve: Create all resources
    - Note: Endpoint URLs, database IPs

66. **Deploy Application via GitHub Actions**
    - Push: Tag with version `v1.0.0`
    - Trigger: GitHub Actions workflow
    - Monitor: Workflow execution
    - Approve: Production deployment step

67. **Run Production Smoke Tests**
    ```bash
    # 1. Health check
    curl https://api.apexmemory.com/api/v1/health

    # 2. Authentication
    curl -X POST https://api.apexmemory.com/api/v1/auth/register \
      -H "Content-Type: application/json" \
      -d '{"email": "test@example.com", "password": "securepassword"}'

    # 3. Ingestion
    curl -X POST https://api.apexmemory.com/api/v1/ingest \
      -H "Authorization: Bearer <token>" \
      -H "Content-Type: application/json" \
      -d '{"content": "Test document"}'

    # 4. Query
    curl -X POST https://api.apexmemory.com/api/v1/query \
      -H "Authorization: Bearer <token>" \
      -H "Content-Type: application/json" \
      -d '{"query": "test"}'
    ```

68. **Monitor for 2 Hours**
    - Dashboard: https://grafana.com (Grafana Cloud)
    - Check: Error rate, latency (P50, P95, P99), throughput
    - Verify: All metrics within baseline
    - Alert: Verify no critical alerts fired

#### Day 5: Post-Deployment Validation (4 hours)

69. **Verify All Services Healthy**
    - Cloud Run: API and Worker both running
    - Cloud SQL: Connection pool healthy
    - Neo4j: Graph database accessible
    - Qdrant: Vector search responding
    - Redis: Cache hit rate >0%
    - Temporal: Workers connected, workflows executing

70. **Run End-to-End Tests in Production**
    ```bash
    # Set production environment
    export API_URL=https://api.apexmemory.com
    export API_KEY=<production-api-key>

    # Run E2E tests
    pytest tests/e2e/ -v --tb=short
    ```

71. **Load Test with 5 Concurrent Users**
    ```bash
    locust -f tests/load/locustfile.py \
      --host https://api.apexmemory.com \
      --users 5 \
      --spawn-rate 1 \
      --run-time 30m
    ```
    - Verify: P95 latency <1s
    - Verify: No errors
    - Document: Performance metrics

72. **Create Operational Runbook**
    - File: `deployment/OPERATIONAL-RUNBOOK.md`
    - Sections:
      - Incident Response (on-call procedures)
      - Scaling (when to upgrade resources)
      - Rollback (how to revert deployment)
      - Common Issues (troubleshooting guide)
      - Emergency Contacts

---

### Week 5: Optimization & Documentation (12-16 hours)

#### Day 1-2: Cost Optimization (6-8 hours)

73. **Analyze Actual Resource Usage**
    - Navigate: GCP Console → Billing → Reports
    - Check: CPU, memory, network usage for each service
    - Identify: Over-provisioned resources (CPU <30%, Memory <50%)
    - Identify: Under-provisioned resources (CPU >80%, Memory >90%)

74. **Right-Size Databases**
    - Cloud SQL: Upgrade if CPU consistently >70%
    - Neo4j VM: Downgrade if memory <40% utilized
    - Redis: Adjust size based on cache hit rate

75. **Set Up Committed Use Discounts (if usage stable)**
    - Navigate: GCP Console → Billing → Committed Use Discounts
    - Purchase: 1-year commit for Cloud SQL, Compute Engine
    - Savings: ~30-40% for stable resources

76. **Document Cost Optimization Opportunities**
    - File: `deployment/COST-OPTIMIZATION.md`
    - Sections:
      - Current spend breakdown
      - Optimization recommendations
      - Potential savings (monthly)
      - Action items with timelines

#### Day 3-4: Documentation & Handoff (6-8 hours)

77. **Update Deployment Documentation**
    - File: `deployment/production/GCP-DEPLOYMENT-GUIDE.md`
    - Add: Pulumi-specific instructions
    - Add: Actual learnings from deployment
    - Update: Cost estimates with actual spend
    - Add: Screenshots of Grafana dashboards

78. **Create Runbooks**
    - **Incident Response Runbook** (`deployment/runbooks/INCIDENT-RESPONSE.md`)
      - Alert definitions
      - Triage steps
      - Escalation paths
      - Remediation procedures

    - **Scaling Runbook** (`deployment/runbooks/SCALING.md`)
      - When to scale (CPU, memory, latency thresholds)
      - How to scale each service
      - Cost implications
      - Rollback if issues

    - **Rollback Runbook** (`deployment/runbooks/ROLLBACK.md`)
      - When to rollback
      - How to rollback (GitHub Actions, manual)
      - Database rollback (migration revert)
      - Verification steps

79. **Document Monitoring/Alerting Thresholds**
    - File: `deployment/MONITORING-THRESHOLDS.md`
    - List: All 12+ alert rules
    - For each: Threshold, severity, notification channel, runbook link

80. **Create Disaster Recovery Plan**
    - File: `deployment/DISASTER-RECOVERY.md`
    - Sections:
      - Backup strategy (daily Cloud SQL, weekly Neo4j)
      - Recovery Time Objective (RTO): 30 minutes
      - Recovery Point Objective (RPO): <1 hour
      - Multi-region failover (future Phase 3)
      - Restore procedures (step-by-step)

---

## Cost Analysis

### Starting Monthly Cost: $500-700/month (1-15 Users)

| Service | Configuration | Monthly Cost | Notes |
|---------|--------------|--------------|-------|
| **Cloud SQL (PostgreSQL)** | db-f1-micro (0.6GB RAM, 10GB storage) | $40 | Auto-upgrade to db-n1-standard-1 ($180) if CPU >70% |
| **Neo4j VM** | e2-small (2 vCPU, 2GB RAM, 20GB SSD) | $35 | Self-hosted, manual backups |
| **Redis (Memorystore Basic)** | 1GB | $50 | No replication (cache can rebuild) |
| **Qdrant (Cloud Run)** | 1 instance, 1 vCPU, 1GB RAM | $30 | Auto-scale to 3 instances if needed |
| **Cloud Run API** | 1-3 instances, 2 vCPU, 2GB RAM each | $60 | Min-instances=1 (no cold starts) |
| **Cloud Run Worker** | 1-2 instances, 1 vCPU, 1GB RAM each | $35 | Min-instances=1 |
| **Temporal Cloud** | Essentials tier (1M actions/month) | $100 | 99.9% SLA, managed service |
| **Grafana Cloud** | Pro tier (10k metrics, 50GB logs) | $19 | Managed Prometheus + Grafana |
| **Networking** | Load Balancer, Cloud NAT, egress | $40 | ~100GB egress/month estimated |
| **Storage (GCS)** | 50GB backups | $10 | Standard storage class |
| **Cloud Logging** | 10GB logs/month | $5 | Beyond free tier |
| **Misc** | Monitoring, IPs, snapshots | $15 | Miscellaneous GCP services |
| **TOTAL (Start)** | | **$439/month** | |

### Auto-Scaling Thresholds

**When to Upgrade (Automatic or Manual):**

1. **Cloud SQL → db-n1-standard-1 ($180/month)**
   - Trigger: CPU >70% for 5 minutes
   - Action: Auto-upgrade (Pulumi alerts, manual approval)
   - Impact: +$140/month, 10x performance improvement

2. **Neo4j VM → e2-medium ($70/month)**
   - Trigger: Memory >80% for 10 minutes
   - Action: Manual upgrade (restart required)
   - Impact: +$35/month, 2x RAM (4GB)

3. **Redis → Memorystore Standard 5GB ($250/month)**
   - Trigger: Cache hit rate <50% OR evictions >100/sec
   - Action: Upgrade to Standard tier (adds replication)
   - Impact: +$200/month, high availability + 5x capacity

4. **Cloud Run API → Max Instances 10**
   - Trigger: Request queue backlog >10 OR CPU >80%
   - Action: Auto-scale (Cloud Run native)
   - Impact: +$20-40/month per additional instance

### Cost at 15 Active Users: $700-900/month

**Estimated Resource Usage:**
- Cloud SQL: db-n1-standard-1 ($180) - likely needed
- Neo4j: e2-medium ($70) - likely needed
- Redis: Basic 1GB ($50) - sufficient
- Cloud Run API: 3-5 instances ($90-150) - during peak hours
- Cloud Run Worker: 2-3 instances ($50-70)
- All other services: Same ($204)
- **Total: $714-894/month**

### Cost at 100 Active Users: $1,500-2,000/month

**Production Tier:**
- Cloud SQL: db-n1-standard-4 + read replica ($700)
- Neo4j: e2-standard-2 ($130) - 8GB RAM
- Redis: Memorystore Standard 5GB ($250)
- Cloud Run API: 10-15 instances ($300-450)
- Cloud Run Worker: 5-8 instances ($100-160)
- Temporal Cloud: Growth plan ($500) - higher action limit
- All other services: $204
- **Total: $2,184-2,694/month**

### Cost Optimization Strategies

1. **Committed Use Discounts (after 3 months)**
   - Cloud SQL: 37% savings (1-year commit)
   - Compute Engine (Neo4j): 55% savings (1-year commit)
   - **Potential savings:** $200-300/month

2. **Cloud Run min-instances Tuning**
   - Start: min-instances=1 (no cold starts, ~$30/month/service)
   - Optimize: Set min-instances=0 for worker if cold starts acceptable
   - **Potential savings:** $35/month (worker)

3. **Database Storage Optimization**
   - Enable auto-delete for old logs (>30 days)
   - Compress backups in Cloud Storage
   - **Potential savings:** $10-20/month

4. **Networking Optimization**
   - Use VPC Peering instead of VPN
   - Optimize egress traffic (compress responses)
   - **Potential savings:** $10-15/month

---

## Performance Targets

### Latency Goals

**API Response Times:**
- **P50 (Median):** <200ms
- **P95:** <1s (contractual SLA if needed)
- **P99:** <2s
- **Health Check:** <50ms

**Database Query Times:**
- **PostgreSQL (metadata):** <50ms for simple queries, <500ms for complex
- **Neo4j (graph):** <100ms for 1-hop, <500ms for 3-hop traversal
- **Qdrant (vector search):** <50ms for top-10 results
- **Redis (cache):** <10ms for cache hits

**Workflow Execution:**
- **Document Ingestion:** <30s for 10-page document
- **Entity Extraction:** <10s (Graphiti LLM-powered)
- **Vector Embedding:** <5s per document

### Throughput Goals

**API Requests:**
- **Sustained:** 10 requests/second
- **Burst:** 100 requests/second (with auto-scaling)

**Document Ingestion:**
- **Sustained:** 10 documents/second
- **Daily:** 100,000 documents/day

**Vector Search:**
- **Queries/second:** 100+ (Qdrant can handle 1000+)

### Availability Goals

**Uptime:**
- **Target:** 99.9% uptime (43 minutes downtime/month)
- **Cloud Run SLA:** 99.95% (GCP guarantee)
- **Temporal Cloud SLA:** 99.9%

**Recovery:**
- **RTO (Recovery Time Objective):** 30 minutes
- **RPO (Recovery Point Objective):** <1 hour (via PITR)

---

## Risk Mitigation

### Risk 1: Temporal Cloud Connection Issues ⚠️ MEDIUM

**Issue:** mTLS certificate configuration is complex, connection failures can block all workflows.

**Mitigation:**
1. Test Temporal Cloud connection in staging thoroughly
2. Keep local Temporal server as fallback (docker-compose)
3. Monitor worker connection status (alert if disconnected >1 minute)
4. Document rollback to local Temporal (emergency)

**Testing:**
- Test mTLS certificate renewal (expires after 1 year)
- Test worker reconnection after network interruption
- Test workflow execution under high load

---

### Risk 2: Multi-Database Sync Failures ⚠️ MEDIUM

**Issue:** Saga pattern can fail if one database is down, leaving partial writes.

**Mitigation:**
1. Comprehensive saga rollback tests (121 tests baseline)
2. Monitor saga execution dashboard (Grafana)
3. Alert on saga failures (>5% failure rate)
4. Manual reconciliation runbook for data inconsistency

**Testing:**
- Chaos engineering: Kill each database, verify rollback
- Verify compensation steps (undo writes)
- Test at scale (100 concurrent ingestions)

---

### Risk 3: Cost Overruns 🟢 LOW-MEDIUM

**Issue:** Auto-scaling could spike costs unexpectedly.

**Mitigation:**
1. Budget alerts at $500, $700, $900, $1,200
2. Daily cost review for first 2 weeks
3. Max instances cap on Cloud Run (prevent runaway scaling)
4. Resource quotas on GCP project level

**Monitoring:**
- Real-time cost dashboard (GCP Billing Reports)
- Weekly cost review meetings
- Alert if daily spend >$30 (expect $15-20/day)

---

### Risk 4: Neo4j Self-Hosted (Single Point of Failure) 🟢 LOW

**Issue:** Neo4j runs on single VM, no automatic high availability.

**Mitigation:**
1. Daily automated backups to GCS
2. Test restore procedure monthly
3. Monitor Neo4j health (uptime check every 1 minute)
4. Upgrade path to Neo4j AuraDB documented (if budget allows)

**Backup Strategy:**
```bash
# Daily cron job
0 3 * * * neo4j-admin backup --to=/backup/neo4j && gsutil cp -r /backup/neo4j gs://apex-backups/neo4j/$(date +\%Y\%m\%d)
```

**Restore Procedure:**
```bash
# Stop Neo4j
sudo systemctl stop neo4j

# Download backup
gsutil cp -r gs://apex-backups/neo4j/20250115 /restore/neo4j

# Restore
neo4j-admin restore --from=/restore/neo4j/20250115

# Start Neo4j
sudo systemctl start neo4j
```

---

### Risk 5: Cold Starts (Cloud Run) ✅ MITIGATED

**Issue:** Cloud Run can have 1-2 second cold start latency if min-instances=0.

**Mitigation:**
1. Set min-instances=1 for API and Worker (prevent cold starts)
2. Monitor cold start rate (Cloud Run metrics)
3. Accept higher cost (~$30/month/service) for zero cold starts

**Performance:**
- With min-instances=1: <50ms response time (container already warm)
- With min-instances=0: 1-2s first request, then <50ms

---

## Success Criteria

### Phase 1: Infrastructure Deployed ✅

- [ ] Pulumi infrastructure code created (5 modules)
- [ ] All GCP resources deployed (Cloud SQL, Memorystore, Neo4j VM, Cloud Run, Load Balancer)
- [ ] Secrets stored in Secret Manager (all 10+ secrets)
- [ ] VPC networking configured (private access to databases)
- [ ] Monitoring infrastructure deployed (Prometheus, Grafana Cloud)

### Phase 2: Application Deployed ✅

- [ ] Production Dockerfiles created (API, Worker)
- [ ] Containers built and pushed to GCR
- [ ] Cloud Run services deployed (API, Worker, Qdrant)
- [ ] Database migrations run successfully
- [ ] Temporal Cloud connected (workers executing workflows)

### Phase 3: Testing Passed ✅

- [ ] All 477 tests passing
- [ ] Smoke tests passed (4 critical paths)
- [ ] Load tests passed (10 concurrent users, 10 minutes, P95 <1s)
- [ ] Integration tests passed (all databases connected)
- [ ] Performance validation (P95 latency <1s)

### Phase 4: Monitoring Configured ✅

- [ ] 5 Grafana dashboards displaying metrics
- [ ] 12+ alert rules configured (critical, warning, info)
- [ ] Alert notifications working (Slack, email)
- [ ] Uptime checks running (every 1 minute)
- [ ] Log aggregation configured (Cloud Logging)

### Phase 5: Automation Complete ✅

- [ ] GitHub Actions CI/CD pipeline configured
- [ ] Auto-deploy to staging on push to main
- [ ] Manual approval for production deployment
- [ ] Blue-green deployment (canary: 10% → 100%)
- [ ] Automatic rollback on failure

### Phase 6: Production Validated ✅

- [ ] All services healthy (Cloud Run, databases, Temporal)
- [ ] End-to-end tests passed in production
- [ ] Load tests passed (5 concurrent users, 30 minutes)
- [ ] No critical alerts fired
- [ ] Operational runbooks created

### Phase 7: Documentation Complete ✅

- [ ] Deployment guide updated with Pulumi instructions
- [ ] Operational runbooks created (incident, scaling, rollback)
- [ ] Monitoring thresholds documented
- [ ] Disaster recovery plan created
- [ ] Cost optimization guide created

---

## Post-Deployment

### Week 1 After Deployment

**Daily Tasks:**
1. **Check Metrics** (15 min/day)
   - Error rate, latency, throughput
   - Database performance
   - Cost (actual vs. budget)

2. **Review Logs** (30 min/day)
   - Any ERROR or CRITICAL level logs
   - Unusual patterns
   - Slow queries

3. **Alert Triage** (as needed)
   - Respond to any alerts within 15 minutes
   - Document false positives
   - Adjust thresholds if needed

**Weekly Tasks:**
4. **Performance Review** (1 hour/week)
   - Compare actual vs. target latency
   - Identify slow endpoints
   - Database query optimization

5. **Cost Review** (1 hour/week)
   - Actual spend vs. budget
   - Resource utilization (CPU, memory)
   - Optimization opportunities

6. **Backup Verification** (30 min/week)
   - Verify backups completed successfully
   - Test restore (sample)
   - Document any issues

### Month 1-3: Optimization Phase

**Goals:**
1. **Right-Size Resources** (Week 4-6)
   - Analyze 4 weeks of usage data
   - Upgrade under-provisioned resources (CPU >80%)
   - Downgrade over-provisioned resources (CPU <30%)

2. **Apply Committed Use Discounts** (Week 8-10)
   - Identify stable resources (Cloud SQL, Neo4j VM)
   - Purchase 1-year commit (30-40% savings)
   - Estimated savings: $200-300/month

3. **Fine-Tune Monitoring** (Week 6-8)
   - Adjust alert thresholds (reduce false positives)
   - Add missing metrics
   - Create custom dashboards

4. **Security Hardening** (Week 10-12)
   - Security audit (internal or external)
   - Penetration testing (if budget allows)
   - Fix any vulnerabilities
   - Implement WAF rules (Cloud Armor)

### Month 4-6: Scale Preparation

**Goals:**
1. **Multi-Region Planning** (if user base grows internationally)
   - Deploy to europe-west1 and asia-east1
   - Configure global load balancing
   - Multi-region database replication

2. **Advanced Features** (if needed)
   - Blue-green deployments (already have canary)
   - Feature flags system
   - A/B testing infrastructure

3. **Backup & DR Enhancement**
   - Automated restore testing
   - Cross-region backups
   - Multi-region failover

---

## Appendix A: Quick Reference Commands

### Pulumi Commands

```bash
# Initialize new stack
pulumi stack init <stack-name>

# Preview changes
pulumi preview

# Deploy infrastructure
pulumi up

# Destroy infrastructure
pulumi destroy

# View outputs
pulumi stack output

# View current stack
pulumi stack
```

### Docker Commands

```bash
# Build API
docker build -f docker/Dockerfile.api.production -t gcr.io/apex-memory-prod/apex-api:latest .

# Build Worker
docker build -f docker/Dockerfile.worker.production -t gcr.io/apex-memory-prod/apex-worker:latest .

# Push to GCR
docker push gcr.io/apex-memory-prod/apex-api:latest
docker push gcr.io/apex-memory-prod/apex-worker:latest

# Run locally
docker run -p 8000:8000 --env-file .env gcr.io/apex-memory-prod/apex-api:latest
```

### GCloud Commands

```bash
# Deploy to Cloud Run
gcloud run deploy apex-api \
  --image gcr.io/apex-memory-prod/apex-api:latest \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated

# View logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=apex-api" --limit 50

# Connect to Cloud SQL
gcloud sql connect apex-postgres-prod --user=postgres

# List secrets
gcloud secrets list

# Access secret
gcloud secrets versions access latest --secret=apex-secret-key
```

### Database Commands

```bash
# Run Alembic migrations
cd apex-memory-system
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "description"

# Rollback migration
alembic downgrade -1

# Neo4j backup
neo4j-admin backup --to=/backup/neo4j/$(date +%Y%m%d)

# Neo4j restore
neo4j-admin restore --from=/backup/neo4j/20250115
```

### Monitoring Commands

```bash
# View Grafana dashboards
# https://grafana.com

# Query Prometheus
curl http://prometheus:9090/api/v1/query?query=up

# View Cloud Logging
gcloud logging read "severity>=ERROR" --limit 50

# View uptime checks
gcloud monitoring uptime-check-configs list
```

---

## Appendix B: Troubleshooting Common Issues

### Issue 1: Cloud Run Service Won't Start

**Symptoms:**
- Cloud Run deployment succeeds but service shows "Unhealthy"
- Logs show "Error: Failed to start server"

**Diagnosis:**
```bash
# View logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=apex-api" --limit 50

# Common errors:
# - ModuleNotFoundError (incorrect PYTHONPATH)
# - ImportError (missing dependency)
# - Connection refused (database not accessible)
```

**Solutions:**
1. **Incorrect PYTHONPATH:** Update Dockerfile to set `PYTHONPATH=/app/src`
2. **Missing dependency:** Add to `requirements.txt`, rebuild Docker image
3. **Database not accessible:** Verify VPC Connector configured, database allows connections from Cloud Run

---

### Issue 2: Temporal Worker Not Connecting

**Symptoms:**
- Worker logs show "Failed to connect to Temporal Cloud"
- Workflows stuck in "Running" state

**Diagnosis:**
```bash
# View worker logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=apex-worker" --limit 50

# Common errors:
# - tls: failed to verify certificate
# - connection refused
# - context deadline exceeded
```

**Solutions:**
1. **Certificate error:** Verify mTLS certificates uploaded to Temporal Cloud, not expired
2. **Connection refused:** Check Temporal Cloud endpoint (should be `<namespace>.tmprl.cloud:7233`)
3. **Timeout:** Check network egress from Cloud Run (may need Cloud NAT)

---

### Issue 3: High Cloud SQL CPU Usage

**Symptoms:**
- Cloud SQL CPU >80% for >5 minutes
- API latency >1s

**Diagnosis:**
```bash
# Connect to Cloud SQL
gcloud sql connect apex-postgres-prod --user=postgres

# Find slow queries
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

**Solutions:**
1. **Missing index:** Create index on frequently queried columns
2. **Inefficient query:** Optimize query (use EXPLAIN ANALYZE)
3. **Under-provisioned:** Upgrade to larger instance (db-n1-standard-2)

---

### Issue 4: Qdrant Out of Memory

**Symptoms:**
- Qdrant container restarting frequently
- Logs show "OOMKilled"

**Diagnosis:**
```bash
# View Qdrant logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=qdrant" --limit 50

# Check memory usage
# (Cloud Run Metrics dashboard)
```

**Solutions:**
1. **Too many vectors:** Increase Cloud Run memory limit (1GB → 2GB)
2. **Large vector dimension:** Optimize embedding model (reduce dimensions)
3. **Memory leak:** Restart container, upgrade Qdrant version

---

## Appendix C: Rollback Procedures

### Rollback Scenario 1: Bad API Deployment

**When:**
- New API deployment causes high error rate (>5%)
- Critical bug discovered in production

**Procedure:**
```bash
# 1. Identify previous revision
gcloud run revisions list --service apex-api --region us-central1

# 2. Rollback to previous revision
PREVIOUS_REVISION=$(gcloud run revisions list --service apex-api --region us-central1 --format="value(name)" --limit=2 | tail -n 1)

gcloud run services update-traffic apex-api \
  --region us-central1 \
  --to-revisions=$PREVIOUS_REVISION=100

# 3. Verify rollback
curl https://api.apexmemory.com/api/v1/health

# 4. Monitor error rate (should drop to <1%)
```

**Timeline:** 2-5 minutes

---

### Rollback Scenario 2: Database Migration Failure

**When:**
- Alembic migration fails mid-execution
- Data corruption detected

**Procedure:**
```bash
# 1. Stop application (prevent further writes)
gcloud run services update apex-api --region us-central1 --no-traffic

# 2. Rollback migration
cd apex-memory-system
alembic downgrade -1

# 3. Verify data integrity
psql -h <cloud-sql-ip> -U postgres -d apex_memory -c "SELECT COUNT(*) FROM documents;"

# 4. Restore from backup (if corruption)
gcloud sql backups restore <backup-id> --backup-instance=apex-postgres-prod

# 5. Re-enable traffic
gcloud run services update apex-api --region us-central1 --to-latest
```

**Timeline:** 30 minutes - 2 hours (depends on restore)

---

### Rollback Scenario 3: Infrastructure Change (Pulumi)

**When:**
- Pulumi update causes resource deletion or misconfiguration
- Database connection lost

**Procedure:**
```bash
# 1. View Pulumi history
pulumi stack history

# 2. Rollback to previous state
pulumi stack select production
pulumi cancel  # Cancel current update if running
pulumi refresh  # Sync state with actual resources

# 3. Revert to previous version
git checkout <previous-commit>
pulumi up  # Re-apply previous configuration

# 4. Verify all resources healthy
pulumi stack output
gcloud run services list
gcloud sql instances list
```

**Timeline:** 10-30 minutes

---

## Appendix D: Contact Information

### Escalation Path

**Level 1: Self-Service** (0-15 minutes)
- Check monitoring dashboards (Grafana)
- Review logs (Cloud Logging)
- Consult runbooks (this document)

**Level 2: On-Call Engineer** (15-60 minutes)
- Your email: [your-email@example.com]
- Your phone: [your-phone-number]
- Response time: <30 minutes

**Level 3: External Support** (60+ minutes)
- GCP Support: https://cloud.google.com/support (depends on support tier)
- Temporal Support: https://temporal.io/support (Essentials tier: email only)
- Community: Temporal Slack, Neo4j Discord

### Vendor Support Contacts

**GCP Support:**
- Portal: https://console.cloud.google.com/support
- Phone: 1-877-355-5787 (US)
- SLA: Depends on support tier (Basic/Development/Production/Critical)

**Temporal Cloud Support:**
- Email: support@temporal.io
- Slack: https://temporal.io/slack
- Docs: https://docs.temporal.io

**Neo4j Support:**
- Community: https://community.neo4j.com
- Discord: https://discord.gg/neo4j
- Commercial: https://neo4j.com/support (if using AuraDB)

---

## Document Revision History

| Date | Version | Author | Changes |
|------|---------|--------|---------|
| 2025-01-15 | 1.0 | Claude | Initial deployment plan created |

---

**End of Production Deployment Plan**
