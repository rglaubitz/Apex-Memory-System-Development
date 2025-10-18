# Temporal Deployment Guide

**Last Updated:** 2025-10-17
**Temporal Version:** >= 1.28.0
**Source:** https://docs.temporal.io/self-hosted-guide

## Quick Start (Development)

### Option 1: Temporal CLI (Fastest)

```bash
# Install Temporal CLI
brew install temporal  # macOS
# OR
curl -sSf https://temporal.download/cli.sh | sh  # Linux/WSL

# Start Temporal Server + UI (all-in-one)
temporal server start-dev

# Access:
# - Temporal Server: localhost:7233
# - Temporal UI: http://localhost:8233
```

**What Gets Started:**
- Temporal Server (in-memory persistence)
- Temporal UI (Web interface)
- SQLite database (ephemeral, resets on restart)

**Use Case:** Quick prototyping, local development, CI/CD tests

---

### Option 2: Docker Compose (Production-Like)

```bash
# Clone Temporal docker-compose repository
git clone https://github.com/temporalio/docker-compose.git temporal-docker
cd temporal-docker

# Start Temporal with PostgreSQL + Elasticsearch + UI
docker-compose -f docker-compose-postgres.yml up -d

# Access:
# - Temporal Server: localhost:7233
# - Temporal UI: http://localhost:8080
# - PostgreSQL: localhost:5432
# - Elasticsearch: localhost:9200
```

**What Gets Started:**
- Temporal Server (4 services: frontend, history, matching, worker)
- Temporal UI
- PostgreSQL (persistent storage)
- Elasticsearch (advanced visibility)
- Prometheus + Grafana (optional monitoring)

**Use Case:** Local development matching production setup, integration testing

---

## Docker Compose Configuration

### Custom docker-compose.yml for Apex Memory System

Create `docker/temporal-compose.yml` in project root:

```yaml
version: '3.8'

services:
  # PostgreSQL for Temporal persistence
  temporal-postgres:
    container_name: temporal-postgres
    image: postgres:16
    restart: always
    environment:
      POSTGRES_USER: temporal
      POSTGRES_PASSWORD: temporal
      POSTGRES_DB: temporal
    ports:
      - "5433:5432"  # Avoid conflict with existing Apex PostgreSQL (5432)
    volumes:
      - temporal-postgres-data:/var/lib/postgresql/data
    networks:
      - apex-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U temporal"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Temporal Server (auto-setup with schema initialization)
  temporal:
    container_name: temporal
    image: temporalio/auto-setup:1.28.0
    restart: always
    depends_on:
      temporal-postgres:
        condition: service_healthy
    environment:
      - DB=postgresql
      - DB_PORT=5432
      - POSTGRES_USER=temporal
      - POSTGRES_PWD=temporal
      - POSTGRES_SEEDS=temporal-postgres
      - DYNAMIC_CONFIG_FILE_PATH=config/dynamicconfig/development.yaml
      - PROMETHEUS_ENDPOINT=0.0.0.0:8000
    ports:
      - "7233:7233"  # Frontend gRPC
      - "8000:8000"  # Prometheus metrics
    volumes:
      - ./temporal-dynamicconfig:/etc/temporal/config/dynamicconfig
    networks:
      - apex-network
    healthcheck:
      test: ["CMD", "tctl", "--address", "localhost:7233", "cluster", "health"]
      interval: 30s
      timeout: 10s
      retries: 5

  # Temporal UI
  temporal-ui:
    container_name: temporal-ui
    image: temporalio/ui:2.38.0
    restart: always
    depends_on:
      temporal:
        condition: service_healthy
    environment:
      - TEMPORAL_ADDRESS=temporal:7233
      - TEMPORAL_CORS_ORIGINS=http://localhost:3000,http://localhost:8080
    ports:
      - "8088:8080"  # Avoid conflict with Apex API (8000)
    networks:
      - apex-network

  # Temporal Admin Tools (for CLI operations)
  temporal-admin-tools:
    container_name: temporal-admin-tools
    image: temporalio/admin-tools:1.28.0
    restart: always
    depends_on:
      temporal:
        condition: service_healthy
    environment:
      - TEMPORAL_CLI_ADDRESS=temporal:7233
    networks:
      - apex-network
    stdin_open: true
    tty: true

volumes:
  temporal-postgres-data:
    driver: local

networks:
  apex-network:
    external: true  # Use existing Apex network
```

**Create dynamic config:**

```bash
mkdir -p docker/temporal-dynamicconfig

cat > docker/temporal-dynamicconfig/development.yaml <<EOF
# Temporal dynamic configuration for local development
frontend.enableClientVersionCheck:
  - value: true

limit.maxIDLength:
  - value: 1000

system.forceSearchAttributesCacheRefreshOnRead:
  - value: true

history.maxAutoResetPoints:
  - value: 20
EOF
```

**Start Temporal:**

```bash
# Create network if not exists
docker network create apex-network 2>/dev/null || true

# Start Temporal stack
docker-compose -f docker/temporal-compose.yml up -d

# Verify
docker ps | grep temporal

# Check logs
docker-compose -f docker/temporal-compose.yml logs -f temporal
```

---

## Environment Variables

### For Temporal Server

```bash
# Database connection
DB=postgresql
DB_PORT=5432
POSTGRES_USER=temporal
POSTGRES_PWD=temporal
POSTGRES_SEEDS=temporal-postgres  # Hostname

# Advanced visibility (optional)
ENABLE_ES=true
ES_SEEDS=elasticsearch
ES_VERSION=v7

# Metrics
PROMETHEUS_ENDPOINT=0.0.0.0:8000

# Dynamic config
DYNAMIC_CONFIG_FILE_PATH=config/dynamicconfig/development.yaml
```

### For Python Workers

Create `.env.temporal`:

```bash
# Temporal connection
TEMPORAL_HOST=localhost:7233
TEMPORAL_NAMESPACE=default

# TLS (for production/Temporal Cloud)
# TEMPORAL_TLS_CERT_PATH=/path/to/client-cert.pem
# TEMPORAL_TLS_KEY_PATH=/path/to/client-key.pem
# TEMPORAL_TLS_CA_PATH=/path/to/ca-cert.pem

# Worker configuration
TEMPORAL_TASK_QUEUE=ingestion-queue
TEMPORAL_WORKER_BUILD_ID=local-dev
TEMPORAL_DEPLOYMENT_NAME=ingestion-service

# Observability
TEMPORAL_METRICS_PORT=8077
TEMPORAL_ENABLE_TRACING=true
TEMPORAL_OTEL_ENDPOINT=http://localhost:4318
```

**Load in Python:**

```python
# config/temporal_config.py
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv(".env.temporal")

@dataclass
class TemporalConfig:
    host: str = os.getenv("TEMPORAL_HOST", "localhost:7233")
    namespace: str = os.getenv("TEMPORAL_NAMESPACE", "default")
    task_queue: str = os.getenv("TEMPORAL_TASK_QUEUE", "default-queue")
    build_id: str = os.getenv("TEMPORAL_WORKER_BUILD_ID", "unknown")
    deployment_name: str = os.getenv("TEMPORAL_DEPLOYMENT_NAME", "default-deployment")

    # TLS
    tls_cert_path: str | None = os.getenv("TEMPORAL_TLS_CERT_PATH")
    tls_key_path: str | None = os.getenv("TEMPORAL_TLS_KEY_PATH")
    tls_ca_path: str | None = os.getenv("TEMPORAL_TLS_CA_PATH")

    # Metrics
    metrics_port: int = int(os.getenv("TEMPORAL_METRICS_PORT", "8077"))
    enable_tracing: bool = os.getenv("TEMPORAL_ENABLE_TRACING", "false").lower() == "true"
    otel_endpoint: str = os.getenv("TEMPORAL_OTEL_ENDPOINT", "http://localhost:4318")

config = TemporalConfig()
```

---

## Production Deployment

### Kubernetes (Helm Charts)

```bash
# Add Temporal Helm repository
helm repo add temporalio https://temporal.io/helm
helm repo update

# Create namespace
kubectl create namespace temporal

# Install Temporal (PostgreSQL persistence)
helm install temporal temporalio/temporal \
  --namespace temporal \
  --set server.replicaCount=3 \
  --set server.persistence.default.driver=sql \
  --set server.persistence.default.sql.driver=postgres12 \
  --set server.persistence.default.sql.host=postgres.default.svc.cluster.local \
  --set server.persistence.default.sql.port=5432 \
  --set server.persistence.default.sql.database=temporal \
  --set server.persistence.default.sql.user=temporal \
  --set server.persistence.default.sql.password=temporal \
  --set prometheus.enabled=true \
  --set grafana.enabled=true

# Verify
kubectl get pods -n temporal
```

### Temporal Cloud (Managed Service)

**1. Create Namespace:**

Visit https://cloud.temporal.io → Create Namespace

**2. Generate Certificates:**

```bash
# Generate private key
openssl genrsa -out client.key 2048

# Generate CSR
openssl req -new -key client.key -out client.csr \
  -subj "/C=US/ST=CA/L=San Francisco/O=Apex/CN=apex-worker"

# Upload CSR to Temporal Cloud → Get signed certificate
```

**3. Connect Worker:**

```python
from temporalio.client import Client
from temporalio.worker import Worker
import ssl

async def main():
    # Load TLS certificates
    ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    ssl_context.load_cert_chain(
        certfile="client.pem",
        keyfile="client.key"
    )

    # Connect to Temporal Cloud
    client = await Client.connect(
        target_host="apex.a2dd6.tmprl.cloud:7233",  # Your namespace.account.tmprl.cloud
        namespace="apex.a2dd6",  # Your namespace
        tls=ssl_context
    )

    worker = Worker(
        client,
        task_queue="ingestion-queue",
        workflows=[...],
        activities=[...]
    )

    await worker.run()
```

---

## Resource Requirements

### Development (Temporal CLI)

| Component | CPU | Memory | Disk |
|-----------|-----|--------|------|
| Temporal Server | 0.5 cores | 512 MB | 1 GB (SQLite) |
| **Total** | 0.5 cores | 512 MB | 1 GB |

### Local Docker Compose (PostgreSQL)

| Component | CPU | Memory | Disk |
|-----------|-----|--------|------|
| Temporal Server (4 services) | 2 cores | 2 GB | - |
| PostgreSQL | 0.5 cores | 512 MB | 10 GB |
| Temporal UI | 0.25 cores | 256 MB | - |
| Elasticsearch (optional) | 1 core | 2 GB | 10 GB |
| **Total** | 3.75 cores | 4.75 GB | 20 GB |

### Production (Kubernetes)

| Component | Replicas | CPU/replica | Memory/replica | Total CPU | Total Memory |
|-----------|----------|-------------|----------------|-----------|--------------|
| Frontend | 3 | 1 core | 1 GB | 3 cores | 3 GB |
| History | 3 | 2 cores | 2 GB | 6 cores | 6 GB |
| Matching | 3 | 1 core | 1 GB | 3 cores | 3 GB |
| Worker | 3 | 1 core | 1 GB | 3 cores | 3 GB |
| PostgreSQL | 3 (HA) | 2 cores | 4 GB | 6 cores | 12 GB |
| **Total** | - | - | - | **21 cores** | **27 GB** |

**Recommendations:**
- Use dedicated PostgreSQL cluster (Amazon RDS, Google Cloud SQL)
- Enable Elasticsearch for advanced visibility
- Configure Prometheus + Grafana for observability
- Set up distributed tracing (OpenTelemetry)

---

## Database Schema

### PostgreSQL Setup (Manual)

```sql
-- Create databases
CREATE DATABASE temporal;
CREATE DATABASE temporal_visibility;

-- Create user
CREATE USER temporal WITH PASSWORD 'temporal';

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE temporal TO temporal;
GRANT ALL PRIVILEGES ON DATABASE temporal_visibility TO temporal;
```

**Initialize schema:**

```bash
# Download temporal-sql-tool
docker run --rm temporalio/admin-tools:1.28.0 \
  temporal-sql-tool create-database -database temporal

# Apply schema
docker run --rm \
  -e SQL_PLUGIN=postgres12 \
  -e SQL_HOST=host.docker.internal \
  -e SQL_PORT=5432 \
  -e SQL_USER=temporal \
  -e SQL_PASSWORD=temporal \
  temporalio/admin-tools:1.28.0 \
  sh -c "temporal-sql-tool --database temporal setup-schema -v 0.0 && \
         temporal-sql-tool --database temporal update -schema-dir /etc/temporal/schema/postgresql/v12/temporal/versioned"
```

**Verify:**

```bash
# Check tables
PGPASSWORD=temporal psql -h localhost -U temporal -d temporal -c "\dt"

# Expected tables:
# - executions
# - activity_info_maps
# - timer_info_maps
# - workflow_executions
# - ... (50+ tables)
```

---

## Health Checks

### Temporal Server

```bash
# Docker
docker exec temporal tctl cluster health

# Kubernetes
kubectl exec -n temporal temporal-frontend-0 -- tctl cluster health

# Expected output:
# SERVING: Frontend service is healthy
# SERVING: History service is healthy
# SERVING: Matching service is healthy
# SERVING: Worker service is healthy
```

### PostgreSQL

```bash
# Check connection
PGPASSWORD=temporal psql -h localhost -p 5433 -U temporal -d temporal -c "SELECT 1"

# Check Temporal schema version
PGPASSWORD=temporal psql -h localhost -p 5433 -U temporal -d temporal \
  -c "SELECT * FROM schema_version ORDER BY version_partition, db_version DESC LIMIT 1"
```

### Temporal UI

```bash
# Check UI accessibility
curl -I http://localhost:8088

# Expected: HTTP/1.1 200 OK
```

---

## Troubleshooting

### Issue: Temporal Server Not Starting

**Symptoms:**
- `docker ps` shows temporal container restarting
- Logs show database connection errors

**Solution:**
```bash
# Check PostgreSQL is healthy
docker-compose -f docker/temporal-compose.yml ps temporal-postgres

# Check logs
docker-compose -f docker/temporal-compose.yml logs temporal-postgres
docker-compose -f docker/temporal-compose.yml logs temporal

# Verify PostgreSQL connection
docker exec temporal-postgres pg_isready -U temporal

# Restart stack
docker-compose -f docker/temporal-compose.yml down
docker-compose -f docker/temporal-compose.yml up -d
```

### Issue: Worker Can't Connect

**Symptoms:**
- Worker logs show connection refused
- Activities not executing

**Solution:**
```python
# Verify Temporal Server address
client = await Client.connect("localhost:7233")  # Correct
# NOT: client = await Client.connect("temporal:7233")  # Wrong (unless running in Docker)

# Check network
import socket
socket.getaddrinfo("localhost", 7233)  # Should resolve

# Test connection
from temporalio.client import Client
client = await Client.connect("localhost:7233")
await client.list_workflows("WorkflowType='*'")
```

### Issue: Workflows Not Visible in UI

**Symptoms:**
- Workflows executing but not showing in Temporal UI
- Search returns no results

**Solution:**
```bash
# Check Elasticsearch (if enabled)
curl http://localhost:9200/_cluster/health

# Rebuild visibility index
docker exec temporal-admin-tools tctl admin cluster add-search-attributes \
  --name CustomKeyword --type Keyword

# Restart Temporal UI
docker-compose -f docker/temporal-compose.yml restart temporal-ui
```

---

## Monitoring

### Prometheus Metrics

```bash
# Temporal Server metrics
curl http://localhost:8000/metrics

# Key metrics:
# - temporal_request_latency
# - temporal_activity_execution_latency
# - temporal_workflow_success_count
# - temporal_workflow_failed_count
```

### Grafana Dashboards

```bash
# Import community dashboards
# 1. Go to http://localhost:3000 (if Grafana enabled)
# 2. Import dashboard: https://github.com/temporalio/dashboards
# 3. Select: temporal-server.json, temporal-sdk.json
```

---

## Backup & Recovery

### PostgreSQL Backup

```bash
# Backup all Temporal databases
docker exec temporal-postgres pg_dumpall -U temporal > temporal-backup-$(date +%Y%m%d).sql

# Restore
docker exec -i temporal-postgres psql -U temporal < temporal-backup-20251017.sql
```

### Workflow History Export

```bash
# Export specific workflow
tctl workflow show \
  --workflow_id my-workflow-id \
  --output_filename workflow-history.json

# Replay workflow
python -m temporalio.testing replay --workflow MyWorkflow workflow-history.json
```

---

## Upgrading Temporal

### Docker Compose Upgrade

```bash
# 1. Backup database
docker exec temporal-postgres pg_dumpall -U temporal > backup.sql

# 2. Stop Temporal (keep PostgreSQL running)
docker-compose -f docker/temporal-compose.yml stop temporal temporal-ui

# 3. Update image version in docker-compose.yml
# temporalio/auto-setup:1.28.0 → temporalio/auto-setup:1.29.0

# 4. Pull new image
docker-compose -f docker/temporal-compose.yml pull

# 5. Start Temporal (auto-setup will migrate schema)
docker-compose -f docker/temporal-compose.yml up -d

# 6. Verify
docker-compose -f docker/temporal-compose.yml logs temporal | grep "schema update"
```

---

## Related Documentation

- [Temporal.io Overview](temporal-io-overview.md)
- [Python SDK Guide](python-sdk-guide.md)
- [Monitoring & Observability](monitoring-observability.md)
- [Integration Patterns](integration-patterns.md)

## Resources

- Official Deployment Guide: https://docs.temporal.io/self-hosted-guide
- Docker Compose Repository: https://github.com/temporalio/docker-compose
- Helm Charts: https://github.com/temporalio/helm-charts
- Temporal Cloud: https://cloud.temporal.io
