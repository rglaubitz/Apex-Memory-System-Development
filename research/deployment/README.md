# Apex Memory System - Production Deployment Documentation

**Purpose:** Complete guide for deploying Apex Memory System from local development to production on Google Cloud Platform (GCP).

**Optimized For:**
- Solo developer / small team
- First production deployment
- Budget: $500-$1,500/month
- GCP infrastructure
- Learning as you go

**Timeline:** 4-6 weeks from start to production

---

## 🚀 Quick Start (First-Time Deployment)

**Start here if this is your first deployment:**

1. **[DEPLOYMENT-CHECKLIST.md](DEPLOYMENT-CHECKLIST.md)** ⭐ START HERE
   - What accounts you need (GCP, Temporal Cloud, GitHub)
   - What credentials to obtain
   - Cost breakdown ($720-950/month estimated)
   - Complete prerequisites checklist
   - **Time:** 2-4 hours

2. **[GCP-DEPLOYMENT-GUIDE.md](GCP-DEPLOYMENT-GUIDE.md)**
   - Step-by-step deployment instructions (8 phases)
   - Every command explained
   - Validation checkpoints at each phase
   - Troubleshooting for common issues
   - **Time:** 8-12 hours (first deployment)

3. **[TESTING-STRATEGY.md](TESTING-STRATEGY.md)**
   - Pre-deployment validation (156 tests)
   - Production smoke tests
   - Performance benchmarks
   - Monitoring & alerting setup
   - **Time:** 2-4 hours

4. **[UPDATE-WORKFLOW.md](UPDATE-WORKFLOW.md)**
   - CI/CD pipeline with Cloud Build
   - How to deploy updates
   - Rollback procedures
   - Hotfix workflow
   - **Time:** 1-2 hours setup

---

## 📚 Complete Documentation Index

### Core Deployment Guides

| Document | Purpose | When to Read | Time Required |
|----------|---------|--------------|---------------|
| **[DEPLOYMENT-CHECKLIST.md](DEPLOYMENT-CHECKLIST.md)** | Prerequisites & account setup | Before starting | 2-4 hours |
| **[GCP-DEPLOYMENT-GUIDE.md](GCP-DEPLOYMENT-GUIDE.md)** | Step-by-step deployment | During deployment | 8-12 hours |
| **[ARCHITECTURE.md](ARCHITECTURE.md)** | Design decisions & rationale | Before deployment | 1-2 hours |
| **[TESTING-STRATEGY.md](TESTING-STRATEGY.md)** | Validation & monitoring | During & after deployment | 2-4 hours |
| **[UPDATE-WORKFLOW.md](UPDATE-WORKFLOW.md)** | CI/CD & iteration | After first deployment | 1-2 hours |

### Supporting Documentation

| Document | Purpose | When to Read |
|----------|---------|--------------|
| **[SECRETS-MANAGEMENT.md](SECRETS-MANAGEMENT.md)** | GCP Secret Manager setup | Before deployment |
| **[COST-OPTIMIZATION.md](COST-OPTIMIZATION.md)** | Budget tracking & alerts | After deployment |

### Infrastructure-as-Code

| Directory | Contents | Usage |
|-----------|----------|-------|
| **[terraform/](terraform/)** | Terraform configurations | Automated deployment |
| **[scripts/](scripts/)** | Deployment automation | Helper scripts |

---

## 🎯 Deployment Phases Overview

### Phase 0: Prerequisites (2-4 hours)
**Status:** ⏺ Not Started

- [ ] GCP account with billing enabled
- [ ] Temporal Cloud account created
- [ ] OpenAI API key obtained
- [ ] GitHub repository set up
- [ ] All secrets documented

**Document:** [DEPLOYMENT-CHECKLIST.md](DEPLOYMENT-CHECKLIST.md)

---

### Phase 1: Foundation (1-2 hours)
**Status:** ⏺ Not Started

- [ ] GCP project created
- [ ] APIs enabled (compute, SQL, Cloud Run, etc.)
- [ ] Budget alerts configured
- [ ] VPC networking configured
- [ ] Secret Manager initialized

**Document:** [GCP-DEPLOYMENT-GUIDE.md#phase-1](GCP-DEPLOYMENT-GUIDE.md#phase-1-foundation-setup)

---

### Phase 2: Databases (3-4 hours)
**Status:** ⏺ Not Started

- [ ] Cloud SQL (PostgreSQL + pgvector) deployed
- [ ] Memorystore (Redis) deployed
- [ ] Compute Engine VM (Neo4j) deployed
- [ ] Cloud Run (Qdrant) deployed
- [ ] Database connectivity validated

**Document:** [GCP-DEPLOYMENT-GUIDE.md#phase-2](GCP-DEPLOYMENT-GUIDE.md#phase-2-database-deployment)

---

### Phase 3: Temporal Setup (1-2 hours)
**Status:** ⏺ Not Started

- [ ] Temporal Cloud namespace configured
- [ ] mTLS certificates installed
- [ ] Worker connection tested
- [ ] Sample workflow executed

**Document:** [GCP-DEPLOYMENT-GUIDE.md#phase-3](GCP-DEPLOYMENT-GUIDE.md#phase-3-temporal-setup)

---

### Phase 4: Application Deployment (2-3 hours)
**Status:** ⏺ Not Started

- [ ] Docker image built and pushed
- [ ] Cloud Run service deployed (FastAPI)
- [ ] Environment variables configured
- [ ] Health endpoints validated

**Document:** [GCP-DEPLOYMENT-GUIDE.md#phase-4](GCP-DEPLOYMENT-GUIDE.md#phase-4-application-deployment)

---

### Phase 5: Monitoring & Observability (1-2 hours)
**Status:** ⏺ Not Started

- [ ] GCP Cloud Monitoring configured
- [ ] Prometheus metrics exported
- [ ] Grafana dashboards created (optional)
- [ ] Alert policies defined
- [ ] Log aggregation configured

**Document:** [GCP-DEPLOYMENT-GUIDE.md#phase-5](GCP-DEPLOYMENT-GUIDE.md#phase-5-monitoring-setup)

---

### Phase 6: CI/CD Pipeline (2-3 hours)
**Status:** ⏺ Not Started

- [ ] Cloud Build connected to GitHub
- [ ] Build triggers configured
- [ ] Test pipeline validated
- [ ] Deployment pipeline tested
- [ ] Rollback procedure tested

**Document:** [UPDATE-WORKFLOW.md](UPDATE-WORKFLOW.md)

---

### Phase 7: Production Validation (2-4 hours)
**Status:** ⏺ Not Started

- [ ] All 156 tests passing in production
- [ ] Smoke tests executed
- [ ] Load testing completed
- [ ] Performance benchmarks met
- [ ] Monitoring dashboards validated

**Document:** [TESTING-STRATEGY.md](TESTING-STRATEGY.md)

---

### Phase 8: Go-Live (1-2 hours)
**Status:** ⏺ Not Started

- [ ] Final security review
- [ ] Cost monitoring active
- [ ] Documentation complete
- [ ] Backup/restore tested
- [ ] Production release

**Document:** [GCP-DEPLOYMENT-GUIDE.md#phase-8](GCP-DEPLOYMENT-GUIDE.md#phase-8-production-release)

---

## 💰 Cost Breakdown

**Estimated Monthly Cost: $720-950**

| Service | Monthly Cost | Percentage |
|---------|--------------|------------|
| Cloud SQL (PostgreSQL) | $250-350 | 35% |
| Temporal Cloud | $100-150 | 15% |
| Compute Engine (Neo4j) | $70-90 | 10% |
| Cloud Run (FastAPI + Qdrant) | $90-140 | 15% |
| Memorystore (Redis) | $50-80 | 8% |
| Networking & Storage | $40-80 | 8% |
| Monitoring | $20-40 | 4% |
| Miscellaneous | $30-60 | 5% |

**Free Tier Benefits:**
- $300 GCP credit (90 days)
- Cloud Build: 120 min/day free
- Cloud Monitoring: 150MB logs/month free
- Cloud Storage: 5GB free

**See detailed breakdown:** [COST-OPTIMIZATION.md](COST-OPTIMIZATION.md)

---

## 🏗️ Architecture Overview

**Deployment Architecture:**

```
┌─────────────────────────────────────────────────────────┐
│                    Internet (HTTPS)                     │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│              Cloud Load Balancer (HTTPS)                │
└────────────────────────┬────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
┌───────▼──────┐  ┌──────▼──────┐  ┌─────▼──────┐
│  Cloud Run   │  │  Cloud Run  │  │ Cloud Run  │
│  (FastAPI)   │  │  (FastAPI)  │  │  (Qdrant)  │
│  Instance 1  │  │  Instance 2 │  │  Vector DB │
└───────┬──────┘  └──────┬──────┘  └─────┬──────┘
        │                │                │
        └────────────────┼────────────────┘
                         │
        ┌────────────────┼────────────────────────┐
        │                │                        │
┌───────▼──────┐  ┌──────▼──────┐  ┌────────▼─────────┐
│   Cloud SQL  │  │ Memorystore │  │  Compute Engine  │
│ (PostgreSQL) │  │   (Redis)   │  │     (Neo4j)      │
│  + pgvector  │  │    Cache    │  │   Graph DB       │
└──────────────┘  └─────────────┘  └──────────────────┘
                         │
                ┌────────▼────────┐
                │  Temporal Cloud │
                │   (Workflows)   │
                └─────────────────┘
```

**Key Design Decisions:**
- **Managed services first:** Minimize operational complexity
- **Cloud Run for compute:** Autoscaling, cost-effective for variable loads
- **Temporal Cloud:** Avoid self-hosting Temporal (high complexity)
- **Self-hosted Neo4j:** No managed GCP option in budget
- **PostgreSQL for metadata:** Single source of truth with pgvector

**See full architecture:** [ARCHITECTURE.md](ARCHITECTURE.md)

---

## 🧪 Testing Overview

**156 Total Tests:**
- 40 Unit tests (~2 min)
- 70 Integration tests (~8 min)
- 10 Load tests (~15 min)
- 6 Chaos tests (~10 min)
- 30 Smoke tests (~3 min)

**Testing Phases:**

1. **Pre-Deployment:** All 156 tests pass locally
2. **Post-Deployment:** Smoke tests (30 tests) in production
3. **Validation:** Load tests with real production data
4. **Monitoring:** Continuous validation via health checks

**See testing strategy:** [TESTING-STRATEGY.md](TESTING-STRATEGY.md)

---

## 🔄 Update Workflow (After First Deployment)

**Standard Update Flow:**

1. **Develop locally** → 2. **Push to GitHub** → 3. **Cloud Build triggers** → 4. **Tests run** → 5. **Deploy to production** → 6. **Smoke tests** → 7. **Monitor**

**Rollback Time:** <5 minutes (Cloud Run instant rollback)

**CI/CD Pipeline:**
- Automated tests on every commit
- Build & push Docker images
- Deploy to production (after tests pass)
- Automatic rollback on failure

**See complete workflow:** [UPDATE-WORKFLOW.md](UPDATE-WORKFLOW.md)

---

## 📖 Key Concepts for First-Time Deployers

### What is Cloud Run?
- **Serverless** compute platform
- Runs Docker containers
- **Auto-scales** from 0 to N instances
- Pay only for actual usage
- **Why we use it:** Cost-effective, easy to deploy, no server management

### What is Cloud SQL?
- **Managed PostgreSQL** database
- Automatic backups, updates, scaling
- Built-in high availability
- **Why we use it:** Supports pgvector extension, managed operations

### What is Temporal Cloud?
- **Workflow orchestration** platform
- Ensures reliable execution of multi-step processes
- Automatic retries, state management
- **Why we use it:** Critical for document ingestion pipeline reliability

### What is Secret Manager?
- **Secure storage** for API keys, passwords
- Automatic encryption, access controls
- Version management
- **Why we use it:** Never store secrets in code or env files

---

## 🆘 Troubleshooting Guide

### Common Issues

**Issue:** "gcloud: command not found"
- **Solution:** Install Google Cloud SDK: `curl https://sdk.cloud.google.com | bash`

**Issue:** "API not enabled" errors
- **Solution:** Run `gcloud services enable [API_NAME]` or check GCP Console

**Issue:** "Quota exceeded" errors
- **Solution:** Request quota increase in GCP Console or upgrade billing

**Issue:** Cloud Run deployment fails
- **Solution:** Check logs: `gcloud logs read --service=apex-memory-api --limit=50`

**Issue:** Database connection timeouts
- **Solution:** Check VPC connector configuration, firewall rules

**Issue:** Budget alerts not working
- **Solution:** Verify email in GCP Billing → Budgets & Alerts

**See comprehensive troubleshooting:** [GCP-DEPLOYMENT-GUIDE.md#troubleshooting](GCP-DEPLOYMENT-GUIDE.md#troubleshooting)

---

## 🔗 External Resources

### GCP Documentation
- Cloud SQL: https://cloud.google.com/sql/docs
- Cloud Run: https://cloud.google.com/run/docs
- Memorystore (Redis): https://cloud.google.com/memorystore/docs
- Secret Manager: https://cloud.google.com/secret-manager/docs
- Cloud Build: https://cloud.google.com/build/docs

### Temporal Documentation
- Temporal Cloud: https://docs.temporal.io/cloud
- Temporal SDKs: https://docs.temporal.io/dev-guide/python
- Community Forum: https://community.temporal.io/

### Related Research (Project Documentation)
- **Temporal Integration:** [../documentation/temporal/](../documentation/temporal/)
- **PostgreSQL + pgvector:** [../documentation/postgresql/](../documentation/postgresql/)
- **FastAPI Production:** [../documentation/fastapi/](../documentation/fastapi/)
- **Neo4j Setup:** [../documentation/neo4j/](../documentation/neo4j/)
- **Qdrant Vector DB:** [../documentation/qdrant/](../documentation/qdrant/)

---

## 📋 Status Tracking

**Use this checklist to track your deployment progress:**

- [ ] **Phase 0:** Prerequisites completed ([DEPLOYMENT-CHECKLIST.md](DEPLOYMENT-CHECKLIST.md))
- [ ] **Phase 1:** Foundation setup complete
- [ ] **Phase 2:** All databases deployed
- [ ] **Phase 3:** Temporal configured
- [ ] **Phase 4:** Application deployed
- [ ] **Phase 5:** Monitoring active
- [ ] **Phase 6:** CI/CD pipeline working
- [ ] **Phase 7:** Production validated
- [ ] **Phase 8:** Go-live complete

**Current Status:** Not Started

---

## 🎓 Learning Path for First-Time Deployers

**Recommended Learning Sequence:**

1. **GCP Fundamentals (2-3 hours)**
   - Cloud Console tour
   - Basic concepts (projects, IAM, billing)
   - Resource: https://cloud.google.com/docs/overview

2. **Docker Basics (1-2 hours)** (if needed)
   - Containers vs VMs
   - Dockerfile basics
   - Resource: https://docs.docker.com/get-started/

3. **Cloud Run Quickstart (1 hour)**
   - Deploy "Hello World"
   - Understand autoscaling
   - Resource: https://cloud.google.com/run/docs/quickstarts

4. **Temporal Concepts (2-3 hours)**
   - Workflows vs Activities
   - Durability guarantees
   - Resource: https://docs.temporal.io/concepts

**Total Learning Time:** 6-9 hours (optional, can learn as you deploy)

---

## 🚀 Next Steps

**If you're ready to start:**

1. **Read:** [DEPLOYMENT-CHECKLIST.md](DEPLOYMENT-CHECKLIST.md) (Start here!)
2. **Gather:** All required accounts and credentials
3. **Review:** [ARCHITECTURE.md](ARCHITECTURE.md) to understand design decisions
4. **Deploy:** Follow [GCP-DEPLOYMENT-GUIDE.md](GCP-DEPLOYMENT-GUIDE.md) step-by-step

**If you have questions:**

- Check troubleshooting sections in each guide
- Review GCP/Temporal documentation
- Search community forums
- Document issues for future reference

---

## 📝 Document Versioning

**Current Version:** 1.0.0
**Last Updated:** 2025-01-20
**Maintained By:** Apex Memory System Development Team
**Review Schedule:** Monthly (or after significant architecture changes)

**Change Log:**
- **1.0.0 (2025-01-20):** Initial deployment documentation created
  - Complete 8-phase deployment guide
  - GCP-optimized for $500-1,500/month budget
  - Designed for solo developer first deployment

---

**Questions or Feedback?**

This is your first production deployment - it's normal to have questions! Document your learnings and update these guides as you go. Future you (and future team members) will thank you.

Good luck with your deployment! 🚀
