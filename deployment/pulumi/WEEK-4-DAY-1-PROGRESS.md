# Week 4 Day 1 - Progress Report

**Date:** 2025-11-16
**Status:** 🚧 IN PROGRESS
**Duration So Far:** ~2 hours

---

## 🎯 Week 4 Goal

Deploy Cloud Run services (API + Worker) for the Apex Memory System using Direct VPC Egress for optimal performance and security.

---

## ✅ Completed Today

### 1. Comprehensive Deployment Research (2025-11-16)

**File:** `research/CLOUD-RUN-DEPLOYMENT-RESEARCH.md` (437 lines)

**Key Findings:**
- **Recommendation:** Use Direct VPC Egress (GA since 2024) instead of VPC connectors
- **Architecture:** Two Cloud Run services (API + Worker)
- **Networking:** Gen2 execution environment with Direct VPC Egress
- **Secrets:** Secret Manager with mounted volumes (not env vars)
- **Images:** Google Artifact Registry for container storage

**Major Decision:** Direct VPC Egress vs VPC Connector

| Aspect | Direct VPC Egress | VPC Connector (Legacy) | Decision |
|--------|-------------------|----------------------|----------|
| Performance | Better (Gen2 optimized) | Good | ✅ Direct VPC |
| Complexity | Simpler (no connector) | More complex | ✅ Direct VPC |
| IP Usage | Fewer IPs needed | Requires /28 subnet | ✅ Direct VPC |
| Cost | Lower (no connector) | Higher | ✅ Direct VPC |
| Bandwidth | No limits | Connector bandwidth cap | ✅ Direct VPC |

**Cost Analysis:**
- **Dev Environment:** +$40-60/month for Cloud Run services
- **Updated Dev Total:** $146-181/month (from $116-136 after Week 3)
- **Production:** +$388-575/month for Cloud Run services

---

### 2. Artifact Registry Setup (2025-11-16)

**Created:** `apex-containers` Docker registry
- **Location:** `us-central1`
- **Format:** Docker
- **URL:** `us-central1-docker.pkg.dev/apex-memory-dev/apex-containers`

**Docker Authentication:** Configured via `gcloud auth configure-docker`

---

### 3. Docker Image Builds (2025-11-16)

**Status:** 🚧 Building (in progress)

**Images to Build:**
1. **apex-api:dev** - FastAPI application
   - **Base:** python:3.11-slim
   - **Size:** ~3.25GB (existing image)
   - **Entrypoint:** uvicorn apex_memory.main:app
   - **Port:** 8000
   - **Status:** Building dependencies (shown 50 packages installing)

2. **apex-worker:dev** - Temporal worker
   - **Base:** python:3.11-slim
   - **Entrypoint:** python -m src.apex_memory.temporal.workers.dev_worker
   - **Status:** Queued (will start after API build)

**Build Progress:**
- ✅ Base image pulled (python:3.11-slim)
- ✅ System dependencies installed (build-essential, libpq-dev, curl)
- 🚧 Installing Python dependencies (~140 packages from requirements.txt)
- ⏳ Copy application code
- ⏳ Create non-root user
- ⏳ Set entrypoint

---

## ⏳ In Progress

### 4. Waiting for Docker Builds to Complete

**Current Task:** Installing Python dependencies for API image

**Dependencies Being Installed (sample):**
- aiofiles==24.1.0
- alembic==1.14.0
- anthropic==0.71.0
- asyncpg==0.30.0
- docling==2.55.1
- fastapi==0.118.0
- graphiti-core==0.22.0
- httpx==0.28.1
- langchain==0.3.27
- neo4j==6.0.2
- numpy>=2.1.0
- openai==1.109.1
- pydantic==2.11.10
- ...and ~130 more packages

**Estimated Build Time:**
- API image: ~5-7 minutes (large requirements.txt)
- Worker image: ~4-6 minutes (similar dependencies)
- **Total:** ~10-15 minutes for both builds

---

## 📋 Remaining Tasks for Week 4 Day 1

### 5. Push Docker Images to Artifact Registry

```bash
# After builds complete
docker push us-central1-docker.pkg.dev/apex-memory-dev/apex-containers/apex-api:dev
docker push us-central1-docker.pkg.dev/apex-memory-dev/apex-containers/apex-worker:dev
```

**Estimated Time:** 3-5 minutes (upload ~6GB total)

---

### 6. Create Secret Manager Secrets

**Secrets to Create:**

```bash
# PostgreSQL password (from WEEK-3-DEPLOYMENT-OUTPUTS.txt)
echo -n "V>r8b}e+jBO*<awJw(xlEHSl2u>TC2ds" | \
  gcloud secrets create postgres-password \
  --data-file=- \
  --replication-policy=automatic \
  --project=apex-memory-dev

# Neo4j password (from WEEK-3-DEPLOYMENT-OUTPUTS.txt)
echo -n "{*i-ouY!AZEp1Gf+h0u[A6)R]utvhb#0" | \
  gcloud secrets create neo4j-password \
  --data-file=- \
  --replication-policy=automatic \
  --project=apex-memory-dev

# OpenAI API key (from user environment)
echo -n "$OPENAI_API_KEY" | \
  gcloud secrets create openai-api-key \
  --data-file=- \
  --replication-policy=automatic \
  --project=apex-memory-dev
```

**Estimated Time:** 2-3 minutes

---

### 7. Create modules/compute.py

**Purpose:** Pulumi infrastructure module for Cloud Run services

**Key Functions to Implement:**

#### `create_cloud_run_api_service()`
```python
def create_cloud_run_api_service(
    project_id: str,
    region: str,
    network_id: pulumi.Output[str],
    subnet_id: pulumi.Output[str],
    image_uri: str,
    secrets: Dict[str, str],  # Secret Manager secret names
) -> Dict[str, Any]:
    """
    Create Cloud Run API service with Direct VPC Egress.

    Features:
    - Gen2 execution environment
    - Direct VPC Egress to private databases
    - Secret Manager integration (mounted volumes)
    - Autoscaling: 0-10 instances (dev)
    - Health checks via /health endpoint
    """
```

**Configuration:**
- **CPU:** 2 vCPU
- **Memory:** 2 GiB
- **Concurrency:** 80 requests/instance
- **Min Instances:** 0 (scale-to-zero for dev cost savings)
- **Max Instances:** 10
- **Execution Environment:** EXECUTION_ENVIRONMENT_GEN2
- **VPC Egress:** PRIVATE_RANGES_ONLY (Direct VPC)
- **Ingress:** All (public API access)

#### `create_cloud_run_worker_service()`
```python
def create_cloud_run_worker_service(
    project_id: str,
    region: str,
    network_id: pulumi.Output[str],
    subnet_id: pulumi.Output[str],
    image_uri: str,
    secrets: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Create Cloud Run Worker service for Temporal workflows.

    Features:
    - Always-on (min 1 instance for Temporal)
    - Direct VPC Egress
    - Internal ingress only
    """
```

**Configuration:**
- **CPU:** 1 vCPU
- **Memory:** 1 GiB
- **Min Instances:** 1 (always-on for Temporal)
- **Max Instances:** 3
- **Execution Environment:** EXECUTION_ENVIRONMENT_GEN2
- **VPC Egress:** PRIVATE_RANGES_ONLY
- **Ingress:** Internal (no external access)

**Estimated Time:** 1-1.5 hours (complex Pulumi configuration)

---

### 8. Update __main__.py to Deploy Cloud Run Services

```python
# In __main__.py, after Qdrant deployment

# 6. Create Cloud Run API service
api_service = create_cloud_run_api_service(
    project_id=project_id,
    region=region,
    network_id=network["vpc"].id,
    subnet_id=network["subnet"].id,
    image_uri=f"us-central1-docker.pkg.dev/{project_id}/apex-containers/apex-api:dev",
    secrets={
        "postgres_password": "postgres-password",
        "neo4j_password": "neo4j-password",
        "openai_api_key": "openai-api-key",
    },
)

# 7. Create Cloud Run Worker service
worker_service = create_cloud_run_worker_service(
    project_id=project_id,
    region=region,
    network_id=network["vpc"].id,
    subnet_id=network["subnet"].id,
    image_uri=f"us-central1-docker.pkg.dev/{project_id}/apex-containers/apex-worker:dev",
    secrets={
        "postgres_password": "postgres-password",
        "neo4j_password": "neo4j-password",
        "openai_api_key": "openai-api-key",
    },
)
```

**Estimated Time:** 15 minutes

---

### 9. Deploy Cloud Run Services with Pulumi

```bash
pulumi up --yes
```

**Expected Results:**
- 2 new Cloud Run services created
- Direct VPC Egress configured
- Secret Manager volumes mounted
- API service accessible via public URL
- Worker service running internally

**Deployment Time:** ~2-3 minutes

**Estimated Time:** 5 minutes (including verification)

---

### 10. Create Week 4 Day 1 Implementation Summary

**File:** `WEEK-4-DAY-1-IMPLEMENTATION.md`

**Sections:**
- Research findings summary
- Artifact Registry setup
- Docker image build process
- Infrastructure code created
- Deployment results
- Cost analysis update
- Key learnings

**Estimated Time:** 30 minutes

---

## 📊 Week 4 Day 1 Metrics

### Time Breakdown (Estimated)

| Task | Time Spent | Status |
|------|-----------|--------|
| Research Cloud Run deployment | ~1 hour | ✅ Complete |
| Create research document | ~30 min | ✅ Complete |
| Setup Artifact Registry | ~5 min | ✅ Complete |
| Build Docker images | ~15 min | 🚧 In Progress |
| Push Docker images | ~5 min | ⏳ Pending |
| Create Secret Manager secrets | ~3 min | ⏳ Pending |
| Create modules/compute.py | ~1.5 hours | ⏳ Pending |
| Update __main__.py | ~15 min | ⏳ Pending |
| Deploy with Pulumi | ~5 min | ⏳ Pending |
| Create implementation summary | ~30 min | ⏳ Pending |
| **Total Estimated** | **~4-5 hours** | **40% Complete** |

### Code Metrics (So Far)

| Category | Lines | Files |
|----------|-------|-------|
| Research Document | 437 | 1 (CLOUD-RUN-DEPLOYMENT-RESEARCH.md) |
| Infrastructure Code | 0 | 0 (modules/compute.py pending) |
| Docker Images | 2 | 2 (Dockerfile.api, Dockerfile.worker - reused) |
| **Total** | **437** | **3 files** |

### Infrastructure Changes

| Resource | Status | Details |
|----------|--------|---------|
| Artifact Registry | ✅ Created | apex-containers (us-central1) |
| Docker Images | 🚧 Building | apex-api:dev + apex-worker:dev |
| Secret Manager Secrets | ⏳ Pending | 3 secrets to create |
| Cloud Run API Service | ⏳ Pending | Awaits modules/compute.py |
| Cloud Run Worker Service | ⏳ Pending | Awaits modules/compute.py |
| **Total New Resources** | **2 deployed, 5 pending** | **7 resources total** |

---

## 🎓 Key Learnings So Far

### 1. Direct VPC Egress is Now the Standard

**Google Recommendation:** Use Direct VPC Egress instead of VPC connectors for Cloud Run

**Benefits Discovered:**
- ✅ No VPC connector resource needed (simpler infrastructure)
- ✅ Better performance with Gen2 execution environment
- ✅ No bandwidth limitations
- ✅ Fewer IP addresses consumed
- ✅ Lower cost (no connector charges)

**Impact:** Simplifies Week 4 deployment significantly

---

### 2. Secret Manager Mounted Volumes > Environment Variables

**Research Finding:** Google recommends mounting secrets as volumes (not env vars)

**Rationale:**
- Environment variables can leak through debug endpoints
- Logs may accidentally capture env vars
- Mounted volumes require file system access (harder to expose)

**Implementation:**
```python
volumes = [
    gcp.cloudrunv2.ServiceTemplateVolumeArgs(
        name="postgres-password",
        secret=gcp.cloudrunv2.ServiceTemplateVolumeSecretArgs(
            secret="postgres-password",
            default_mode=0o444,  # Read-only
            items=[...],
        ),
    ),
]
```

---

### 3. Worker Service Must Stay Always-On

**Challenge:** Should worker service scale to zero like API?

**Decision:** Keep min_instance_count=1 for worker

**Rationale:**
- Temporal workflows require active workers at all times
- Worker cold start ~30 seconds (too slow for workflow execution)
- Cost difference minimal (~$25/month for 1 instance)
- Prevents missed workflow tasks during scale-up

---

### 4. Docker Builds Take Time with Large Dependencies

**Observation:** requirements.txt has ~140 packages

**Impact:**
- API build: ~5-7 minutes
- Worker build: ~4-6 minutes
- Total: ~10-15 minutes for both images

**Optimization Opportunities:**
- Use multi-stage Docker builds
- Cache Python dependencies layer
- Consider using slim base image with pre-built wheels

---

## 🚀 Next Steps

**Immediate (Today):**
1. ✅ Wait for Docker builds to complete (~5 min remaining)
2. ⏳ Push images to Artifact Registry (~5 min)
3. ⏳ Create Secret Manager secrets (~3 min)
4. ⏳ Create modules/compute.py (~1.5 hours)
5. ⏳ Deploy Cloud Run services (~5 min)
6. ⏳ Create implementation summary (~30 min)

**Tomorrow (Week 4 Day 2):**
- Create integration tests for Cloud Run services
- Test API endpoints from public internet
- Test worker Temporal connectivity
- Test Direct VPC Egress database connections
- Verify Secret Manager secret mounting
- Test autoscaling behavior

**Week 4 Days 3-4:**
- Create comprehensive Cloud Run setup guide
- Document monitoring and health checks
- Create Week 4 complete summary
- Update README.md with Week 4 completion

---

## 📂 Files Created Today

1. **research/CLOUD-RUN-DEPLOYMENT-RESEARCH.md** (437 lines)
   - Comprehensive deployment research
   - Options analysis and decision rationale
   - Architecture design for both services

2. **WEEK-4-DAY-1-PROGRESS.md** (this file)
   - Day 1 progress tracking
   - Time estimates and metrics
   - Next steps documentation

**Files Pending:**
- modules/compute.py (~300-400 lines estimated)
- WEEK-4-DAY-1-IMPLEMENTATION.md (~500+ lines estimated)

---

**Last Updated:** 2025-11-16 (Docker builds in progress)
**Status:** 🚧 40% Complete
**Next Task:** Wait for Docker builds → Push images → Create secrets → Build infrastructure code
**Estimated Completion:** ~2-3 hours remaining for Day 1

---

