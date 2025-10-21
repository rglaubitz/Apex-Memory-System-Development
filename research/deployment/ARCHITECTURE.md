# Apex Memory System - Production Architecture

**Purpose:** Explain architectural design decisions, cost tradeoffs, and scaling considerations.

**Audience:** Solo developer deploying first production system.

**Last Updated:** 2025-01-20

---

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Design Decisions](#design-decisions)
- [Component Breakdown](#component-breakdown)
- [Cost Analysis](#cost-analysis)
- [Scaling Strategy](#scaling-strategy)
- [Alternative Architectures](#alternative-architectures)

---

## Architecture Overview

### System Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                       Internet (Users/API Clients)                │
└────────────────────────────┬─────────────────────────────────────┘
                             │ HTTPS
┌────────────────────────────▼─────────────────────────────────────┐
│                    Cloud Load Balancer (GCP)                      │
│                      SSL/TLS Termination                          │
└────────────────────────────┬─────────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
┌───────▼─────────┐  ┌───────▼─────────┐  ┌──────▼────────┐
│   Cloud Run     │  │   Cloud Run     │  │  Cloud Run    │
│   (FastAPI)     │  │   (FastAPI)     │  │   (Qdrant)    │
│   Instance 1    │  │   Instance 2    │  │  Vector DB    │
│  Auto-scaling   │  │  Auto-scaling   │  │   Container   │
└───────┬─────────┘  └───────┬─────────┘  └──────┬────────┘
        │                    │                    │
        └────────────────────┼────────────────────┘
                             │
         ┌───────────────────┼───────────────────────┐
         │                   │                       │
┌────────▼────────┐  ┌───────▼────────┐  ┌─────────▼────────┐
│   Cloud Run     │  │   Cloud SQL    │  │  Memorystore     │
│  (Temporal      │  │  (PostgreSQL   │  │    (Redis)       │
│   Workers)      │  │  + pgvector)   │  │    Cache         │
│  Background     │  │  Managed DB    │  │  Managed Redis   │
└────────┬────────┘  └───────┬────────┘  └─────────┬────────┘
         │                   │                      │
         │           ┌───────▼────────┐             │
         │           │ Compute Engine │             │
         │           │    (Neo4j)     │             │
         │           │   Graph DB VM  │             │
         │           └───────┬────────┘             │
         │                   │                      │
         └───────────────────┼──────────────────────┘
                             │
                    ┌────────▼────────┐
                    │  Temporal Cloud │
                    │   (Workflows)   │
                    │  Hosted Service │
                    └─────────────────┘
```

### Data Flow

**Document Ingestion Flow:**

1. **Client → FastAPI** (Cloud Run)
2. **FastAPI → Temporal Cloud** (Start workflow)
3. **Temporal → Workers** (Execute activities)
4. **Workers → Databases** (Parallel writes):
   - Cloud SQL (PostgreSQL + pgvector): Metadata + vectors
   - Neo4j (Compute Engine): Graph relationships
   - Qdrant (Cloud Run): High-performance vector search
   - Redis (Memorystore): Cache

**Query Flow:**

1. **Client → FastAPI** (Cloud Run)
2. **FastAPI → Redis** (Check cache)
   - Cache hit: Return immediately
   - Cache miss: Continue to databases
3. **FastAPI → Query Router** (Determine optimal database)
4. **Query Router → Database(s)**:
   - Semantic search → Qdrant or PostgreSQL
   - Graph queries → Neo4j
   - Hybrid queries → Multiple databases
5. **Result → Redis** (Cache for future queries)
6. **Result → Client**

---

## Design Decisions

### 1. Why GCP Instead of AWS/Azure?

**Decision:** Google Cloud Platform (GCP)

**Rationale:**
- **Requested by user:** You indicated preference for GCP
- **Cloud Run:** Best serverless container platform (better than AWS Fargate, Azure Container Instances)
- **Managed PostgreSQL:** Cloud SQL has excellent pgvector support
- **Temporal Cloud integration:** Works well with GCP networking
- **Cost-effective:** Competitive pricing for managed services

**Tradeoffs:**
- ✅ **Pros:** Simpler than AWS, better serverless experience, strong Postgres support
- ⚠️ **Cons:** Smaller ecosystem than AWS, fewer third-party integrations

**Alternative:** AWS would be equally valid (more mature), Azure less recommended for this stack.

---

### 2. Why Cloud Run Instead of Kubernetes/Compute Engine?

**Decision:** Cloud Run (serverless containers)

**Rationale:**
- **Simplicity:** No cluster management (vs. GKE/Kubernetes)
- **Cost:** Pay only for actual usage, scale to zero
- **Auto-scaling:** Automatic horizontal scaling (0 to N instances)
- **Deployment:** Simple deploy command, no complex configuration
- **Solo developer friendly:** Minimal ops overhead

**Tradeoffs:**
- ✅ **Pros:** Zero ops, auto-scaling, cost-effective for variable load
- ⚠️ **Cons:** Cold starts (~1-2s), less control than Kubernetes
- ⚠️ **Limitations:** 60-minute max request timeout, stateless only

**Alternative:** Kubernetes (GKE) would give more control but requires significant ops expertise (not recommended for solo developer first deployment).

---

### 3. Why Temporal Cloud Instead of Self-Hosted?

**Decision:** Temporal Cloud (managed service)

**Rationale:**
- **Complexity:** Self-hosted Temporal requires Kubernetes expertise
- **Cost vs. time:** $100-150/month vs. ~40 hours setup + ongoing maintenance
- **Reliability:** 99.9% SLA, automatic failover
- **Focus:** Spend time building product, not managing infrastructure

**Tradeoffs:**
- ✅ **Pros:** Zero ops, battle-tested, instant setup
- ⚠️ **Cons:** $100-150/month cost (vs. $0 for self-hosted infrastructure)
- 📊 **Break-even:** Self-hosting makes sense at $500+/month spend OR if you have Kubernetes expertise

**Alternative:** Self-hosted Temporal on GKE possible but not recommended for first deployment.

---

### 4. Why Cloud SQL Instead of Self-Hosted PostgreSQL?

**Decision:** Cloud SQL (managed PostgreSQL)

**Rationale:**
- **pgvector support:** Native extension support
- **Automatic backups:** Point-in-time recovery included
- **HA built-in:** Multi-AZ deployment option
- **Scaling:** Easy vertical/horizontal scaling
- **Maintenance:** Automatic security patches

**Tradeoffs:**
- ✅ **Pros:** Zero ops, pgvector support, automatic backups
- ⚠️ **Cons:** ~$250-350/month (vs. ~$70/month for self-hosted VM)
- 📊 **ROI:** Worth it for data reliability and time savings

**Alternative:** Self-hosted PostgreSQL on Compute Engine would save ~$200/month but requires DBA expertise.

---

### 5. Why Self-Hosted Neo4j Instead of Managed?

**Decision:** Self-hosted Neo4j on Compute Engine

**Rationale:**
- **No managed option:** Neo4j AuraDB not available in GCP marketplace
- **Cost:** AuraDB Professional starts at ~$200/month (vs. $70-90 for VM)
- **Control:** Full control over Neo4j configuration
- **Budget constraint:** Staying within $500-1,500/month budget

**Tradeoffs:**
- ✅ **Pros:** Cost savings (~$130/month), full control
- ⚠️ **Cons:** Manual backups, no automatic HA, requires management
- 📊 **Upgrade path:** Move to AuraDB when budget allows ($200+/month)

**Alternative:** Neo4j AuraDB (managed) would be better long-term but exceeds current budget.

---

### 6. Why Qdrant on Cloud Run Instead of Managed/Self-Hosted?

**Decision:** Qdrant on Cloud Run (containerized)

**Rationale:**
- **No GCP managed option:** Qdrant Cloud is separate service
- **Cost-effective:** Cloud Run cheaper than dedicated VM
- **Auto-scaling:** Scale to zero when idle
- **Simplicity:** Deploy like application code

**Tradeoffs:**
- ✅ **Pros:** Cost-effective ($40-60/month), auto-scaling, simple deployment
- ⚠️ **Cons:** Cold starts possible, storage limitations
- 📊 **Upgrade path:** Move to Qdrant Cloud or dedicated VM at higher scale

**Alternative:** Qdrant Cloud (~$40/month) or self-hosted VM (~$70/month) both viable.

---

### 7. Why Memorystore (Redis) Instead of Self-Hosted?

**Decision:** Memorystore (managed Redis)

**Rationale:**
- **Low cost:** Basic tier starts at $50/month
- **HA option:** Standard tier for $120/month adds replication
- **Zero ops:** Automatic patching, backups
- **VPC integration:** Native Cloud Run connectivity

**Tradeoffs:**
- ✅ **Pros:** Reliable, low ops, good price for 1GB
- ⚠️ **Cons:** Basic tier has no replication (single point of failure)
- 📊 **Recommendation:** Start Basic, upgrade to Standard if cache becomes critical

**Alternative:** Self-hosted Redis on VM would save ~$30/month but adds ops complexity.

---

## Component Breakdown

### Application Layer (Cloud Run)

**FastAPI Service:**
- **Instances:** Auto-scale 1-10 (configurable)
- **Resources:** 2 vCPU, 2GB RAM per instance
- **Concurrency:** 80 requests per instance
- **Timeout:** 300s (5 minutes)
- **Cost:** ~$50-80/month

**Use Case:** API endpoints, query routing, client-facing logic

**Scaling Triggers:**
- CPU > 60%
- Concurrent requests > 64 (80% of max concurrency)
- Memory > 90%

---

**Temporal Workers (Cloud Run):**
- **Instances:** 2-5 (configurable)
- **Resources:** 1 vCPU, 1GB RAM per instance
- **Purpose:** Execute Temporal activities (ingestion, extraction, embedding)
- **Cost:** ~$30-50/month

**Use Case:** Background processing, workflow execution

**Scaling Triggers:**
- Temporal task queue backlog
- Activity execution latency

---

**Qdrant Vector Database (Cloud Run):**
- **Instances:** 1-3 (configurable)
- **Resources:** 1 vCPU, 2GB RAM per instance
- **Purpose:** High-performance vector similarity search
- **Cost:** ~$40-60/month

**Use Case:** Fast vector search (<100ms P95)

---

### Database Layer

**Cloud SQL (PostgreSQL + pgvector):**
- **Instance Type:** db-n1-standard-2 (2 vCPU, 7.5GB RAM)
- **Storage:** 50GB SSD (auto-expanding to 500GB)
- **Purpose:** Primary metadata store, vector search, full-text search
- **Cost:** ~$250-350/month

**Use Case:**
- Document metadata
- User data
- Hybrid vector + keyword search
- Structured data queries

**Scaling Options:**
- Vertical: Upgrade to db-n1-standard-4 ($500/month)
- Horizontal: Add read replicas ($250/month each)

---

**Memorystore (Redis):**
- **Tier:** Basic (no replication)
- **Size:** 1GB
- **Purpose:** Query result cache, session storage
- **Cost:** ~$50-80/month

**Use Case:**
- Cache frequently accessed queries (>70% hit rate target)
- Reduce database load
- <100ms query responses for cached results

**Scaling Options:**
- Upgrade to Standard tier (with replication): $120/month
- Increase size: 5GB = $250/month

---

**Neo4j (Compute Engine):**
- **Machine Type:** e2-medium (2 vCPU, 4GB RAM)
- **Storage:** 50GB SSD
- **Purpose:** Graph relationships, entity connections
- **Cost:** ~$70-90/month

**Use Case:**
- Entity relationship graphs
- Multi-hop queries
- Temporal relationship tracking

**Scaling Options:**
- Vertical: Upgrade to e2-standard-2 ($130/month)
- Causal Cluster: Add read replicas ($70/month each)

---

**Qdrant (Cloud Run):**
- (See Application Layer)

**Use Case:**
- Ultra-fast vector search
- Large-scale similarity queries
- Real-time recommendations

---

### Workflow Orchestration (Temporal Cloud)

**Temporal Cloud:**
- **Plan:** Essentials tier
- **Namespace:** apex-memory-prod
- **Region:** aws-us-east-1 (or aws-us-west-2)
- **Cost:** ~$100-150/month

**Included:**
- 1M actions/month
- 7-30 day retention
- mTLS authentication
- 99.9% SLA

**Use Case:**
- Document ingestion workflows
- Multi-step data processing
- Reliable execution with retries

**Scaling:**
- Additional actions: $50/million
- Storage: $0.042/GB-hour (active)

---

## Cost Analysis

### Monthly Cost Breakdown

| Component | Spec | Monthly Cost | % of Total |
|-----------|------|--------------|------------|
| **Cloud SQL** | db-n1-standard-2 | $250-350 | 35% |
| **Temporal Cloud** | Essentials tier | $100-150 | 15% |
| **Neo4j VM** | e2-medium | $70-90 | 10% |
| **Cloud Run (API)** | 2 vCPU, 2GB, 1-10 instances | $50-80 | 8% |
| **Memorystore** | Basic 1GB | $50-80 | 8% |
| **Cloud Run (Qdrant)** | 1 vCPU, 2GB, 1-3 instances | $40-60 | 7% |
| **Cloud Run (Workers)** | 1 vCPU, 1GB, 2-5 instances | $30-50 | 5% |
| **Networking** | Egress, VPC connector | $30-50 | 5% |
| **Cloud Monitoring** | Logs, metrics | $10-30 | 3% |
| **Cloud Storage** | 50GB | $1-2 | <1% |
| **Misc** | IPs, snapshots | $10-20 | 2% |
| **TOTAL** | | **$720-950** | 100% |

---

### Cost Optimization Opportunities

**Immediate Savings (First Month):**

1. **Cloud SQL:** Start with db-n1-standard-1 (save ~$120/month)
   - Monitor CPU usage
   - Upgrade if consistently >70%

2. **Cloud Run min-instances:** Set to 0 (save ~$20/month)
   - Accept ~1-2s cold start latency
   - Upgrade to min-instances=1 if cold starts problematic

3. **Neo4j VM:** Use preemptible instance (save ~$50/month)
   - 80% discount
   - May restart occasionally
   - Not for production, but good for staging

**After 3 Months (with usage data):**

4. **Committed Use Discounts (CUDs):**
   - Cloud SQL: 37% savings (1-year commit)
   - Compute Engine: 55% savings (1-year commit)
   - Total potential savings: ~$200-300/month

5. **Rightsizing:**
   - Analyze actual usage patterns
   - Adjust instance sizes (up or down)
   - Remove unused resources

---

### Scaling Costs (Projected)

**At 10x Traffic:**
- API instances: 10-50 (instead of 1-10)
- Workers: 10-20 (instead of 2-5)
- Cloud SQL: db-n1-standard-4 or read replicas
- Redis: 5GB Standard tier
- **Total: ~$2,500-3,500/month**

**At 100x Traffic:**
- Major architecture changes needed:
  - Multi-region deployment
  - Database sharding
  - CDN for static assets
  - Dedicated Qdrant cluster
- **Total: ~$8,000-15,000/month**

---

## Scaling Strategy

### Phase 1: Initial Deployment (0-100 users)

**Current Architecture (as deployed):**
- Single region (us-central1)
- Cloud Run: 1-10 instances
- Cloud SQL: db-n1-standard-2 (no replicas)
- Redis: 1GB Basic tier
- Neo4j: e2-medium (single VM)
- **Capacity:** ~100-500 concurrent users, ~10 docs/sec ingestion

---

### Phase 2: Growth (100-1,000 users)

**When to Scale:**
- API latency P95 > 1s
- Cloud SQL CPU > 70%
- Ingestion backlog > 100 documents

**Scaling Actions:**

1. **Cloud Run:**
   - Increase max-instances: 10 → 20
   - Add more workers: 2-5 → 5-10

2. **Cloud SQL:**
   - Upgrade: db-n1-standard-2 → db-n1-standard-4
   - Or add read replica for query offloading

3. **Redis:**
   - Upgrade: Basic 1GB → Standard 5GB (with replication)

4. **Neo4j:**
   - Upgrade: e2-medium → e2-standard-2
   - Or add read replicas (Causal Cluster)

**Cost Impact:** +$300-500/month

---

### Phase 3: Scale (1,000-10,000 users)

**When to Scale:**
- Multi-region user base
- 100+ docs/sec ingestion
- <50ms latency requirement

**Scaling Actions:**

1. **Multi-Region Deployment:**
   - Deploy to us-central1 + europe-west1 + asia-east1
   - Cloud Load Balancer for geo-routing
   - Replicate databases to each region

2. **Database Sharding:**
   - Shard Cloud SQL by user ID or tenant
   - Neo4j federation
   - Qdrant distributed collections

3. **CDN:**
   - Cloud CDN for static assets
   - Edge caching for API responses

4. **Dedicated Infrastructure:**
   - Move Qdrant to dedicated VM cluster
   - Neo4j Causal Cluster (3-7 nodes)
   - Cloud SQL with 3-5 read replicas

**Cost Impact:** +$5,000-10,000/month

---

## Alternative Architectures

### Option A: All-Managed (Higher Cost, Zero Ops)

**Changes:**
- Neo4j: Use Neo4j AuraDB (+$130/month)
- Qdrant: Use Qdrant Cloud (+$40/month)
- Redis: Upgrade to Standard tier with HA (+$40/month)

**Total Cost:** ~$930-1,160/month (+$210/month)

**Pros:**
- Zero database ops
- All services managed with HA
- Better SLAs

**Cons:**
- 25% higher cost
- Less control over configurations

**Recommendation:** Consider after revenue > $10k/month

---

### Option B: Self-Hosted (Lower Cost, Higher Ops)

**Changes:**
- Temporal: Self-hosted on GKE (save $100/month, add $200 infrastructure)
- Cloud SQL: Self-hosted PostgreSQL on VM (save $200/month)
- Memorystore: Self-hosted Redis (save $50/month)

**Total Cost:** ~$450-600/month (-$250/month)

**Pros:**
- 30% cost savings
- Full control

**Cons:**
- Requires Kubernetes + DBA expertise
- 20-40 hours/month maintenance
- Higher risk (no managed HA)

**Recommendation:** Only if you have strong DevOps background (not recommended for solo developer)

---

### Option C: Serverless-First (Variable Cost)

**Changes:**
- Cloud SQL: Neon (serverless PostgreSQL) instead (save $200/month at low usage)
- Qdrant: Qdrant Cloud (pay per query)
- Redis: Cloud Run + Redis container (save $50/month)

**Total Cost:** ~$300-500/month at low usage, ~$1,000+ at scale

**Pros:**
- Pay only for actual usage
- Scale to zero possible

**Cons:**
- Less predictable costs
- Cold start latencies
- Migration complexity

**Recommendation:** Consider for MVP / pre-launch phase

---

## Summary

**Current Architecture (Recommended for Your Use Case):**

✅ **Right for:**
- Solo developer
- First production deployment
- Budget: $500-1,500/month
- Learning as you go
- Variable traffic (auto-scaling important)

⚠️ **Not optimal for:**
- Multi-region deployment (day 1)
- >1,000 concurrent users (immediately)
- <50ms latency requirements (edge cases)

**Key Strengths:**
1. **Simplicity:** Managed services minimize ops burden
2. **Cost-effective:** Competitive for 0-1,000 user range
3. **Auto-scaling:** Handles traffic spikes automatically
4. **Upgrade path:** Clear scaling strategy when needed

**When to Re-evaluate:**
- Revenue > $10k/month (can afford higher-tier managed services)
- Consistent traffic > 1,000 users (multi-region makes sense)
- Team grows beyond solo developer (can manage more complex infrastructure)

---

**Next Steps:**

1. **Deploy:** Follow [GCP-DEPLOYMENT-GUIDE.md](GCP-DEPLOYMENT-GUIDE.md)
2. **Monitor:** Track costs weekly for first month
3. **Optimize:** Adjust after gathering usage data (30 days)
4. **Scale:** Implement Phase 2 scaling when traffic warrants

---

**Questions?**

- Cost concerns? See [COST-OPTIMIZATION.md](COST-OPTIMIZATION.md)
- Deployment help? See [GCP-DEPLOYMENT-GUIDE.md](GCP-DEPLOYMENT-GUIDE.md)
- Scaling questions? Revisit this document's scaling section

---

**Last Updated:** 2025-01-20
**Version:** 1.0.0
**Author:** Claude Code (Apex Memory System Architecture)
