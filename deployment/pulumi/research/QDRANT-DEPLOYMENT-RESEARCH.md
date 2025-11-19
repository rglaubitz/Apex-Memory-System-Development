# Qdrant Deployment Research

**Date:** 2025-11-16
**Status:** ✅ Research Complete
**Decision:** Deploy Qdrant on Compute Engine with Docker (following Neo4j pattern)

---

## 🎯 Research Question

**How should we deploy Qdrant vector database on Google Cloud Platform for the Apex Memory System?**

**Options Considered:**
1. Cloud Run (serverless containers)
2. Compute Engine + Docker (like Neo4j)
3. Google Kubernetes Engine (GKE)
4. Qdrant Cloud (managed service)

---

## 📊 Deployment Options Analysis

### Option 1: Cloud Run ❌ NOT RECOMMENDED

**Pros:**
- Serverless (auto-scaling, pay-per-use)
- Easy deployment from container images
- Integrated with VPC networking

**Cons:**
- ❌ **Stateless architecture** - Cloud Run containers are ephemeral
- ❌ **No persistent disk support** - Only temporary storage during request
- ❌ **Request timeout** - 60 minutes maximum, not suitable for long-running vector operations
- ❌ **Qdrant requires block-level storage** - Cannot use NFS or object storage

**Verdict:** Cloud Run is designed for stateless workloads. Qdrant requires persistent block storage with POSIX file system, making Cloud Run unsuitable.

---

### Option 2: Compute Engine + Docker ✅ RECOMMENDED

**Pros:**
- ✅ **Full control** over VM and storage
- ✅ **Persistent SSD disks** - Exactly what Qdrant requires
- ✅ **Consistent with Neo4j** - Same deployment pattern
- ✅ **Private IP only** - VPC-native security
- ✅ **Cost-effective for dev** - e2-medium (~$24/month)
- ✅ **Simple Startup Script** - Docker install + Qdrant container
- ✅ **Easy to upgrade** - Pull new image, restart container

**Cons:**
- Manual scaling (vs auto-scaling in GKE)
- No built-in HA (single VM)
- Manual backup/restore procedures

**Configuration:**
- **Machine Type:** e2-medium (2 vCPU, 4GB RAM) for dev
- **Disk:** 100GB SSD persistent disk (`/mnt/qdrant`)
- **Docker Image:** `qdrant/qdrant:latest`
- **Ports:** 6333 (HTTP), 6334 (gRPC), 6335 (distributed)
- **Network:** VPC-private only (10.0.0.0/24 subnet)

**Verdict:** Best choice for dev environment. Matches Neo4j pattern, proven infrastructure, cost-effective.

---

### Option 3: Google Kubernetes Engine (GKE) 🔶 FUTURE PRODUCTION

**Pros:**
- ✅ **Production-grade HA** - Multi-zone deployment
- ✅ **Auto-scaling** - Horizontal pod autoscaler
- ✅ **Zero-downtime upgrades** - Rolling updates
- ✅ **Official GCP tutorial** - Well-documented
- ✅ **StatefulSets** - Persistent storage per pod

**Cons:**
- ❌ **Complexity** - Kubernetes learning curve
- ❌ **Cost** - GKE cluster + node pools (~$150-200/month minimum)
- ❌ **Overkill for dev** - More than needed for development/testing

**Verdict:** Defer to production deployment (Week 6). Not needed for initial development environment.

---

### Option 4: Qdrant Cloud 🔶 ALTERNATIVE FOR PRODUCTION

**Pros:**
- ✅ **Fully managed** - Zero infrastructure management
- ✅ **Multi-cloud** - Available on GCP, AWS, Azure
- ✅ **HA built-in** - Replication and failover
- ✅ **Automatic backups** - Point-in-time recovery
- ✅ **Monitoring included** - Metrics and alerts

**Cons:**
- ❌ **Cost** - Premium pricing vs self-hosted
- ❌ **Vendor lock-in** - Tied to Qdrant Cloud platform
- ❌ **Less control** - Cannot customize underlying infrastructure

**Verdict:** Consider for production if team doesn't want to manage Qdrant infrastructure. Compare cost vs GKE during Week 6 planning.

---

## 🔬 Technical Requirements (from Official Docs)

### Persistent Storage

**Requirements:**
- Block-level access to storage devices
- POSIX-compatible file system
- **NOT SUPPORTED:** NFS, S3 object storage
- **RECOMMENDED:** SSD or NVMe drives (for offloaded vectors)

**Qdrant Official Warning:**
> "Using Docker/WSL on Windows with mounts is known to have file system problems causing data loss."

**Our Approach:** Linux VM (Ubuntu 22.04) + ext4 filesystem on SSD persistent disk = fully compatible.

---

### Network Ports

| Port | Purpose | Expose to VPC? |
|------|---------|----------------|
| 6333 | HTTP API + monitoring | ✅ Yes |
| 6334 | gRPC API | ✅ Yes |
| 6335 | Distributed deployment | ❌ No (single node dev) |

**Our Configuration:**
- All ports accessible within VPC (private IP only)
- No external IPs (consistent with Neo4j, Redis, PostgreSQL)

---

### Resource Requirements

**Factors:**
- Vector count (how many documents)
- Vector dimensions (e.g., 1536 for OpenAI embeddings)
- Payload size and indexing
- Replication strategy (dev = single node, no replication)
- Quantization settings

**Dev Environment Estimate:**
- **Vectors:** ~10,000-50,000 (initial testing)
- **Dimensions:** 1536 (OpenAI ada-002)
- **Machine:** e2-medium (2 vCPU, 4GB RAM)
- **Disk:** 100GB SSD

**Production Estimate:**
- **Vectors:** 1M-10M
- **Machine:** e2-standard-4 (4 vCPU, 16GB RAM) or GKE cluster
- **Disk:** 500GB-1TB SSD

---

### Docker Deployment Commands

**Basic Deployment:**
```bash
docker run -d \
  --name qdrant \
  --restart always \
  -p 6333:6333 \
  -p 6334:6334 \
  -v /mnt/qdrant:/qdrant/storage \
  qdrant/qdrant:latest
```

**With Custom Configuration:**
```bash
docker run -d \
  --name qdrant \
  --restart always \
  -p 6333:6333 \
  -p 6334:6334 \
  -v /mnt/qdrant:/qdrant/storage \
  -v /path/to/config.yaml:/qdrant/config/production.yaml \
  qdrant/qdrant:latest
```

**Health Check:**
```bash
curl http://localhost:6333/health
# Should return: {"title":"qdrant - vector search engine","version":"..."}
```

---

## 🏗️ Implementation Plan

### Week 3 Day 1: Compute Engine + Docker Deployment

**Step 1: Create Qdrant Infrastructure Module**

Add to `modules/databases.py`:
```python
def create_qdrant_instance(
    project_id: str,
    region: str,
    network_id: pulumi.Output[str],
    subnet_id: pulumi.Output[str],
    machine_type: str = "e2-medium",
    disk_size_gb: int = 100,
) -> Dict[str, Any]:
    """Create Qdrant vector database on Compute Engine."""

    # Service account for Qdrant VM
    # Persistent SSD disk for vector storage
    # Startup script: Docker + Qdrant container
    # Private IP only (no external IP)
    # Tags: qdrant, database
```

**Step 2: Startup Script**
```bash
#!/bin/bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
sleep 10

# Format and mount data disk
mkfs.ext4 -F /dev/sdb
mkdir -p /mnt/qdrant
mount /dev/sdb /mnt/qdrant
echo '/dev/sdb /mnt/qdrant ext4 defaults,nofail 0 2' >> /etc/fstab

# Run Qdrant container
docker run -d \
  --name qdrant \
  --restart always \
  -p 6333:6333 \
  -p 6334:6334 \
  -v /mnt/qdrant:/qdrant/storage \
  qdrant/qdrant:latest
```

**Step 3: Unit Tests**
- Test VM creation
- Test disk attachment
- Test private IP configuration
- Test startup script syntax

**Step 4: Integration Tests**
- Test HTTP API (port 6333)
- Test collection creation
- Test vector insertion
- Test vector search
- Test data persistence

---

## 💰 Cost Analysis

### Development Environment (Monthly)

| Service | Configuration | Cost |
|---------|---------------|------|
| Compute Engine | e2-medium (2 vCPU, 4GB) | ~$24 |
| Persistent Disk | 100GB SSD (pd-ssd) | ~$17 |
| **Total Qdrant** | | **~$41/month** |

**Updated Total Dev Cost:**
- PostgreSQL: ~$15-20
- VPC Connector: ~$10-15
- Neo4j: ~$20-25
- Redis: ~$30-35
- **Qdrant: ~$41**
- **TOTAL: ~$116-136/month** (from ~$75-95)

### Production Environment (Monthly)

| Service | Configuration | Cost |
|---------|---------------|------|
| Compute Engine | e2-standard-4 (4 vCPU, 16GB) | ~$120 |
| Persistent Disk | 500GB SSD | ~$85 |
| **Total Qdrant** | | **~$205/month** |

**Alternative: GKE Cluster**
- 3-node cluster (e2-standard-4 per node): ~$360
- Persistent disks (3x 500GB SSD): ~$255
- **TOTAL: ~$615/month** (HA, auto-scaling)

**Alternative: Qdrant Cloud**
- Pricing varies (contact sales for enterprise)
- Typically $200-500/month for production workloads

---

## ✅ Decision Summary

**Selected Approach:** Compute Engine + Docker (Option 2)

**Rationale:**
1. **Consistent with existing infrastructure** - Matches Neo4j deployment pattern
2. **Meets all technical requirements** - Block storage, POSIX filesystem, SSD
3. **Cost-effective for dev** - ~$41/month vs ~$615/month for GKE
4. **Simple to implement** - Reuse Neo4j startup script pattern
5. **VPC-private security** - No external exposure, same as other databases
6. **Proven approach** - Docker-based Qdrant is officially supported for production

**Future Production Options:**
- Week 6: Evaluate GKE vs Qdrant Cloud vs larger Compute Engine
- Decision criteria: Cost, HA requirements, team expertise, auto-scaling needs

---

## 📚 References

**Official Documentation:**
- Qdrant Installation Guide: https://qdrant.tech/documentation/guides/installation/
- GCP GKE Tutorial: https://cloud.google.com/kubernetes-engine/docs/tutorials/deploy-qdrant
- Qdrant Hybrid Cloud: https://qdrant.tech/documentation/hybrid-cloud/

**Best Practices:**
- Self-hosting with Docker on Ubuntu: https://sliplane.io/blog/self-hosting-qdrant-with-docker-on-ubuntu-server
- Qdrant Data Persistence: https://stackoverflow.com/questions/77412601/how-to-configure-qdrant-data-persistence-and-reload

**Community Examples:**
- Medium: Mastering Qdrant (Oct 2025): https://medium.com/@david-koh/part-2-mastering-qdrant-a-deep-dive-into-vector-storage-and-dense-search
- Azure Samples (similar pattern): https://github.com/Azure-Samples/qdrant-azure

---

**Last Updated:** 2025-11-16
**Status:** ✅ Research Complete
**Next Step:** Implement Qdrant infrastructure code in `modules/databases.py`

