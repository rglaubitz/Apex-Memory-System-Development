# Cloud Run Deployment Research

**Date:** 2025-11-16
**Status:** Complete
**Purpose:** Research and document Cloud Run deployment strategy for Apex Memory System API and worker services

---

## Executive Summary

**Recommendation:** Deploy two Cloud Run services (API + Worker) using **Direct VPC Egress** (GA since 2024) instead of traditional VPC connectors for optimal performance and simpler configuration.

**Key Benefits:**
- ✅ No VPC connector required (simpler architecture)
- ✅ Better network performance (especially under packet loss)
- ✅ Lower latency for database connections
- ✅ Fewer IP address requirements
- ✅ No connector bandwidth limitations

---

## Deployment Options Analyzed

| Option | Description | Pros | Cons | Decision |
|--------|-------------|------|------|----------|
| **Direct VPC Egress** | Route traffic directly to VPC (no connector) | GA since 2024, better performance, simpler, fewer IPs | Requires Gen2 execution environment | ✅ **SELECTED** |
| **VPC Connector (Legacy)** | Use existing apex-vpc-connector | Already deployed | Extra resource, bandwidth limits, more IPs | ❌ Not needed with Direct VPC |
| **Public Endpoints** | Expose databases with public IPs | Simple | Major security risk, violates VPC-private design | ❌ Rejected |

---

## Cloud Run Architecture Overview

### Two Services to Deploy

#### 1. API Service (`apex-api-dev`)
- **Base Image:** `docker/Dockerfile.api`
- **Entrypoint:** `uvicorn apex_memory.main:app --host 0.0.0.0 --port 8000`
- **Port:** 8000
- **Concurrency:** 80 requests per instance (default)
- **Min Instances:** 0 (scale to zero for dev cost savings)
- **Max Instances:** 10 (dev tier)
- **CPU:** 2 vCPU
- **Memory:** 2 GiB
- **Ingress:** All (public API access)
- **Health Check:** `/health` endpoint

#### 2. Worker Service (`apex-worker-dev`)
- **Base Image:** `docker/Dockerfile.worker`
- **Entrypoint:** `python -m src.apex_memory.temporal.workers.dev_worker`
- **Purpose:** Temporal workflow execution
- **Min Instances:** 1 (keep at least one worker always running)
- **Max Instances:** 3 (dev tier)
- **CPU:** 1 vCPU
- **Memory:** 1 GiB
- **Ingress:** Internal (no external access needed)
- **Health Check:** None (long-running worker process)

---

## Networking Strategy

### Direct VPC Egress Configuration

**VPC Network Routing:**
```python
vpc_access = gcp.cloudrunv2.ServiceTemplateVpcAccessArgs(
    egress="PRIVATE_RANGES_ONLY",  # Only VPC traffic through Direct VPC
    network_interfaces=[
        gcp.cloudrunv2.ServiceTemplateVpcAccessNetworkInterfaceArgs(
            network=network_id,    # apex-memory-vpc
            subnetwork=subnet_id,  # apex-db-subnet
        )
    ],
)
```

**Traffic Routing:**
- ✅ VPC-private traffic (10.0.0.0/24): Routes through Direct VPC Egress
- ✅ Internet traffic (embeddings, APIs): Routes through internet gateway
- ✅ Database connections: PostgreSQL (10.115.5.3), Neo4j (10.0.0.2), Redis (10.123.172.227), Qdrant (10.0.0.3)

### Execution Environment

**Gen2 Execution Environment:**
- Required for Direct VPC Egress performance benefits
- Faster network performance under packet loss
- Better throughput for multi-database workloads

```python
template = gcp.cloudrunv2.ServiceTemplateArgs(
    execution_environment="EXECUTION_ENVIRONMENT_GEN2",
    # ... rest of template config
)
```

---

## Secrets and Environment Variables

### Secret Manager Integration

**Best Practices:**
1. ✅ Pin secrets to specific versions (don't use `latest`)
2. ✅ Use Secret Manager API directly in code (not env vars)
3. ✅ Avoid exposing secrets via env vars (leak risk)
4. ✅ Use IAM conditions for secret-level access control
5. ✅ Rotate secrets periodically

**Secrets to Create:**
- `postgres-password` (from Week 1 output)
- `neo4j-password` (from Week 2 output)
- `openai-api-key` (for embeddings)

**Environment Variables (Non-Sensitive):**
```python
env_vars = [
    # Database connections (private IPs)
    gcp.cloudrunv2.ServiceTemplateContainerEnvArgs(
        name="POSTGRES_HOST", value="10.115.5.3"
    ),
    gcp.cloudrunv2.ServiceTemplateContainerEnvArgs(
        name="POSTGRES_DB", value="apex_memory"
    ),
    gcp.cloudrunv2.ServiceTemplateContainerEnvArgs(
        name="NEO4J_URI", value="bolt://10.0.0.2:7687"
    ),
    gcp.cloudrunv2.ServiceTemplateContainerEnvArgs(
        name="REDIS_HOST", value="10.123.172.227"
    ),
    gcp.cloudrunv2.ServiceTemplateContainerEnvArgs(
        name="QDRANT_HOST", value="10.0.0.3"
    ),
    # Sensitive values use Secret Manager (mounted as files)
]
```

**Secrets (Mounted as Volumes):**
```python
volumes = [
    gcp.cloudrunv2.ServiceTemplateVolumeArgs(
        name="postgres-password",
        secret=gcp.cloudrunv2.ServiceTemplateVolumeSecretArgs(
            secret="postgres-password",
            default_mode=0o444,  # Read-only
            items=[
                gcp.cloudrunv2.ServiceTemplateVolumeSecretItemArgs(
                    version="1",  # Pin to version 1
                    path="postgres-password",
                )
            ],
        ),
    ),
]

volume_mounts = [
    gcp.cloudrunv2.ServiceTemplateContainerVolumeMountArgs(
        name="postgres-password",
        mount_path="/secrets/postgres",
    ),
]
```

---

## Container Image Strategy

### Google Artifact Registry

**Registry Configuration:**
- **Name:** `apex-containers`
- **Location:** `us-central1`
- **Format:** Docker
- **Repository URL:** `us-central1-docker.pkg.dev/apex-memory-dev/apex-containers`

**Images to Build and Push:**
1. `apex-api:dev` - FastAPI application (built from `docker/Dockerfile.api`)
2. `apex-worker:dev` - Temporal worker (built from `docker/Dockerfile.worker`)

**Build and Push Process:**
```bash
# Authenticate with Artifact Registry
gcloud auth configure-docker us-central1-docker.pkg.dev

# Build API image
docker build -f docker/Dockerfile.api -t us-central1-docker.pkg.dev/apex-memory-dev/apex-containers/apex-api:dev .

# Build Worker image
docker build -f docker/Dockerfile.worker -t us-central1-docker.pkg.dev/apex-memory-dev/apex-containers/apex-worker:dev .

# Push images
docker push us-central1-docker.pkg.dev/apex-memory-dev/apex-containers/apex-api:dev
docker push us-central1-docker.pkg.dev/apex-memory-dev/apex-containers/apex-worker:dev
```

---

## Service-to-Service Authentication

### IAM-Based Authentication

**API Service → Temporal Service:**
- Temporal UI/Server runs on Compute Engine (10.0.0.4 - placeholder for future deployment)
- No authentication needed for internal VPC communication
- Alternative: Use VPC firewall rules to restrict access

**Worker Service → Databases:**
- Direct VPC egress allows private IP connections
- No Cloud SQL Auth Proxy needed (reduces quota issues)
- Neo4j: Standard bolt authentication
- Redis: Standard password authentication
- Qdrant: HTTP API (no auth in dev)

---

## Cost Analysis

### Development Environment (Monthly)

**Cloud Run Costs:**
| Resource | Configuration | Estimated Cost |
|----------|---------------|----------------|
| API Service | 2 vCPU, 2GiB RAM, scale-to-zero | ~$15-25/month |
| Worker Service | 1 vCPU, 1GiB RAM, min 1 instance | ~$25-35/month |
| Artifact Registry | 2 Docker images (~1GB total) | ~$0.10/month |
| Secret Manager | 3 secrets, pinned versions | ~$0.18/month |
| **Total Cloud Run** | | **~$40-60/month** |

**Updated Infrastructure Total:**
| Service | Week 3 Cost | Week 4 Cost (Added) |
|---------|-------------|---------------------|
| PostgreSQL | ~$15-20 | ~$15-20 |
| VPC Connector | ~$10-15 | ~~$10-15~~ (removed with Direct VPC) |
| Neo4j | ~$20-25 | ~$20-25 |
| Redis | ~$30-35 | ~$30-35 |
| Qdrant | ~$41 | ~$41 |
| **Cloud Run** | N/A | **~$40-60** |
| **Total** | **~$116-136** | **~$146-181** |

**Cost Increase:** +$30-45/month for Cloud Run services (net savings from VPC connector removal)

### Production Environment (Monthly)

**Cloud Run Production Costs:**
| Resource | Configuration | Estimated Cost |
|----------|---------------|----------------|
| API Service | 4 vCPU, 4GiB RAM, min 2 instances | ~$200-300/month |
| Worker Service | 2 vCPU, 2GiB RAM, min 3 instances | ~$150-200/month |
| Load Balancer | Global HTTPS LB | ~$18-25/month |
| CDN (optional) | Static assets caching | ~$20-50/month |
| **Total Cloud Run** | | **~$388-575/month** |

**Updated Production Total:** ~$1,004-1,345/month (databases + Cloud Run)

---

## Autoscaling Configuration

### API Service Autoscaling

**Scale-to-Zero (Dev):**
```python
scaling = gcp.cloudrunv2.ServiceTemplateScalingArgs(
    min_instance_count=0,   # Save costs when idle
    max_instance_count=10,  # Cap at 10 instances
)
```

**Always-On (Production):**
```python
scaling = gcp.cloudrunv2.ServiceTemplateScalingArgs(
    min_instance_count=2,   # Always 2 instances for HA
    max_instance_count=100, # Scale up to 100
)
```

**Autoscaling Triggers:**
- CPU utilization > 60%
- Request concurrency > 80 per instance
- Request latency > 1000ms

### Worker Service Autoscaling

**Dev:**
```python
scaling = gcp.cloudrunv2.ServiceTemplateScalingArgs(
    min_instance_count=1,   # Always 1 worker running
    max_instance_count=3,   # Max 3 workers for dev
)
```

**Production:**
```python
scaling = gcp.cloudrunv2.ServiceTemplateScalingArgs(
    min_instance_count=3,   # Always 3 workers (HA)
    max_instance_count=20,  # Scale up to 20 workers
)
```

---

## Monitoring and Health Checks

### API Service Health Check

**Endpoint:** `/health`

**Configuration:**
```python
health_check = gcp.cloudrunv2.ServiceTemplateContainerStartupProbeArgs(
    http_get=gcp.cloudrunv2.ServiceTemplateContainerStartupProbeHttpGetArgs(
        path="/health",
        port=8000,
    ),
    initial_delay_seconds=10,
    timeout_seconds=5,
    period_seconds=30,
    failure_threshold=3,
)
```

**Health Response:**
```json
{
    "status": "healthy",
    "databases": {
        "postgres": "connected",
        "neo4j": "connected",
        "redis": "connected",
        "qdrant": "connected"
    },
    "timestamp": "2025-11-16T12:00:00Z"
}
```

### Worker Service Monitoring

**No Health Checks:** Workers are long-running Temporal processes that self-report to Temporal server

**Monitoring via Temporal UI:**
- Worker status: http://localhost:8088/workers
- Workflow execution stats
- Activity completion rates

---

## Key Learnings and Decisions

### 1. Direct VPC Egress Replaces VPC Connector

**Challenge:** Traditional VPC connector adds complexity, costs, and bandwidth limits.

**Solution:** Use Direct VPC Egress (GA since 2024) for simpler, faster networking.

**Benefits:**
- ✅ No dedicated /28 subnet required
- ✅ No connector bandwidth limits
- ✅ Better performance with Gen2 execution environment
- ✅ Fewer IP addresses consumed
- ✅ Simpler Pulumi code (no connector resource)

---

### 2. Secret Manager vs Environment Variables

**Challenge:** How to securely pass database passwords to Cloud Run?

**Decision:** Use Secret Manager with **mounted volumes** (not env vars)

**Rationale:**
- Environment variables can leak through debug endpoints
- Mounted secrets are harder to accidentally expose
- Secret Manager provides versioning and rotation
- IAM conditions enable fine-grained access control

**Implementation:**
```python
# Read secret from mounted volume in application code
with open("/secrets/postgres/postgres-password") as f:
    postgres_password = f.read().strip()
```

---

### 3. Artifact Registry for Container Images

**Challenge:** Where to store Docker images for Cloud Run deployment?

**Decision:** Use Google Artifact Registry (not Docker Hub or GCR legacy)

**Rationale:**
- Integrated with GCP IAM
- Regional storage (us-central1) reduces latency
- Vulnerability scanning built-in
- Cheaper than Docker Hub for private images
- GCR is being sunset (Artifact Registry is replacement)

---

### 4. Worker Service Always-On in Dev

**Challenge:** Should worker service scale to zero like API?

**Decision:** Keep min_instance_count=1 for worker (not 0)

**Rationale:**
- Temporal workflows require active workers
- Cold start for worker ~30 seconds (too slow for workflows)
- Cost difference minimal (~$25/month for 1 instance)
- Avoids missed workflow tasks during scale-up

---

### 5. Gen2 Execution Environment Required

**Challenge:** Gen1 vs Gen2 execution environment?

**Decision:** Use Gen2 for all services

**Rationale:**
- Required for Direct VPC Egress performance benefits
- Better network throughput (critical for multi-database workload)
- Improved packet loss handling
- Gen1 will eventually be deprecated
- No downside to using Gen2

---

## Implementation Checklist

### Week 4 Day 1: Container Registry and Images

- [ ] Create Artifact Registry repository
- [ ] Build apex-api:dev Docker image
- [ ] Build apex-worker:dev Docker image
- [ ] Push images to Artifact Registry
- [ ] Verify images accessible from Pulumi

### Week 4 Day 2: Secret Manager Setup

- [ ] Create Secret Manager secrets (postgres-password, neo4j-password, openai-api-key)
- [ ] Pin secrets to version 1
- [ ] Create IAM bindings for Cloud Run service accounts
- [ ] Document secret access patterns

### Week 4 Day 3: Cloud Run Services Deployment

- [ ] Create modules/compute.py with Cloud Run functions
- [ ] Deploy API service with Direct VPC Egress
- [ ] Deploy Worker service with Direct VPC Egress
- [ ] Test database connectivity from both services
- [ ] Verify health checks passing

### Week 4 Day 4: Integration Testing

- [ ] Create integration tests for API endpoints
- [ ] Create integration tests for Worker workflows
- [ ] Test autoscaling behavior
- [ ] Test Direct VPC Egress database connectivity
- [ ] Create Week 4 summary documentation

---

## References

**Official Documentation:**
- [Direct VPC Egress | Cloud Run](https://cloud.google.com/run/docs/configuring/vpc-direct-vpc)
- [Secrets in Cloud Run | Secret Manager](https://cloud.google.com/run/docs/configuring/services/secrets)
- [Artifact Registry Overview](https://cloud.google.com/artifact-registry/docs/overview)
- [Cloud Run Best Practices](https://cloud.google.com/run/docs/configuring/networking-best-practices)

**Research Sources:**
- VPC Connectors vs Direct VPC Egress comparison (Google Cloud docs)
- Secret Manager best practices (Google Cloud docs)
- Gen2 execution environment performance benchmarks

---

**Last Updated:** 2025-11-16
**Status:** ✅ Research Complete
**Next Phase:** Implementation (modules/compute.py)
