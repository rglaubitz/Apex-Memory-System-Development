# Apex Memory System - Pulumi Infrastructure

**Status:** 🟢 Phase 0 Complete | 🔵 Ready for Week 1 Implementation
**Timeline:** 6 weeks to production deployment (Week 1 starts next)
**Cost:** $411-807/month (auto-scales based on usage)
**Last Updated:** 2025-11-08

---

## 🎯 Current Progress

### ✅ Phase 0: Setup Complete (2025-11-08)

**What We Accomplished:**
- ✅ Installed Pulumi CLI v3.206.0
- ✅ Installed gcloud CLI v546.0.0
- ✅ Installed Python 3.14.0 + uv 0.8.12
- ✅ Authenticated with GCP (project: `apex-memory-dev`)
- ✅ Authenticated with Pulumi Cloud (user: `rglaubitz`)
- ✅ Created virtual environment (.venv) using uv
- ✅ Installed Python dependencies (15 packages in 19ms!)
- ✅ Created `dev` stack
- ✅ Deployed initial infrastructure (13 GCP APIs enabled)

**Infrastructure Deployed:**
- 12 GCP API services enabled (compute, sqladmin, redis, run, secretmanager, monitoring, logging, etc.)
- Stack: `dev` | Project: `apex-memory-dev` | Region: `us-central1`
- Pulumi Cloud state management configured
- Deployment took 25 seconds

**View Deployment:**
https://app.pulumi.com/rglaubitz-org/apex-memory-infrastructure/dev/updates/1

### 📋 Next Steps

**Immediate Next: Week 1 Implementation (20-24 hours)**

Create `modules/networking.py` with:
- VPC network with private Google Access
- Private service connection for Cloud SQL
- Cloud SQL PostgreSQL instance (db-f1-micro for dev)
- Cloud NAT for outbound internet access
- VPC connector for Cloud Run

**Command to Start:**
```bash
cd deployment/pulumi
source .venv/bin/activate
# Create modules/networking.py (see Week 1 section below)
```

---

## 📚 Table of Contents

1. [Quick Start](#quick-start)
2. [Project Overview](#project-overview)
3. [Research Findings](#research-findings-5-comprehensive-guides)
4. [Architecture Decisions](#architecture-decisions)
5. [Implementation Roadmap](#implementation-roadmap-6-weeks)
6. [Folder Structure](#folder-structure)
7. [Development Workflow](#development-workflow)
8. [Testing Strategy](#testing-strategy)
9. [Deployment Guide](#deployment-guide)
10. [Troubleshooting](#troubleshooting)

---

## 🚀 Quick Start

### Prerequisites

```bash
# Install Pulumi CLI
brew install pulumi

# Install uv (100x faster than pip)
brew install uv

# Install Python 3.11+
python --version  # Ensure 3.11+
```

### Initial Setup

```bash
# Navigate to Pulumi directory
cd deployment/pulumi

# Create virtual environment with uv
uv venv

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# Install dependencies
uv pip install -r requirements.txt

# Login to Pulumi Cloud (free tier)
pulumi login

# Select/create stack
pulumi stack init dev
# or
pulumi stack select dev

# Configure GCP project
pulumi config set gcp:project apex-memory-dev
pulumi config set gcp:region us-central1

# Preview infrastructure
pulumi preview

# Deploy infrastructure
pulumi up
```

### Verify Deployment

```bash
# View outputs
pulumi stack output

# Check resource status
pulumi stack

# View logs
pulumi logs --follow
```

---

## 📖 Project Overview

**Goal:** Deploy Apex Memory System to Google Cloud Platform using Infrastructure-as-Code

**What We're Deploying:**
- **VPC Networking** - Private Google Access, Cloud NAT
- **Cloud SQL PostgreSQL** - Multi-zone HA with pgvector
- **Neo4j Graph Database** - Compute Engine e2-small
- **Redis Memorystore** - 1GB Basic tier
- **Qdrant Vector Database** - Containerized on Cloud Run
- **Cloud Run Services** - API Gateway, Ingestion Workers
- **Secret Manager** - Centralized secret storage
- **Cloud Monitoring** - Metrics, dashboards, alerts

**Architecture Highlights:**
- **Multi-Database Parallel Writes** - Saga pattern with compensation
- **Serverless Cloud Run** - Auto-scaling API and workers
- **Private Networking** - Databases not exposed to internet
- **Temporal Cloud** - Workflow orchestration (external)

---

## 🔬 Research Findings (5 Comprehensive Guides)

We conducted exhaustive research across 5 dimensions. All research is in `research/` directory:

### 1. **PULUMI-FUNDAMENTALS.md** (900+ lines)
**What:** Core Pulumi concepts, architecture, state management

**Key Learnings:**
- Pulumi uses declarative infrastructure with imperative programming languages
- State management with automatic locking (Pulumi Cloud)
- Resources, Inputs, Outputs, and dependency tracking
- Stack concept for multi-environment management (dev/staging/prod)
- Secrets management with encryption at rest

**Read this if:** New to Pulumi or need to understand how it works

---

### 2. **PULUMI-GCP-GUIDE.md** (1,100+ lines)
**What:** GCP provider deep dive with production examples

**Key Learnings:**
- Complete Cloud Run + Cloud SQL private IP integration
- VPC networking setup for multi-database architecture
- Service account creation with least privilege IAM
- 20+ working code examples
- **400 lines of production-ready Apex Memory infrastructure**

**Read this if:** Implementing GCP resources with Pulumi

---

### 3. **PULUMI-EXAMPLES.md** (8,500+ words)
**What:** Production-grade code patterns from official Pulumi examples (21k+ stars)

**Key Learnings:**
- Multi-database component resource pattern (PostgreSQL + Redis + Neo4j + Qdrant)
- Reusable CloudRunService component with auto database injection
- Multi-environment configuration (same code, different configs)
- 15+ complete, copy-paste-ready examples

**Read this if:** Need code patterns to copy/adapt

---

### 4. **PULUMI-BEST-PRACTICES.md** (Comprehensive production guide)
**What:** Industry best practices for production Pulumi deployments

**Key Learnings:**
- Micro-stacks pattern for lifecycle separation
- State management (Pulumi Cloud vs GCS backend)
- Security best practices (secrets, IAM, network isolation)
- Testing strategies (unit, property, integration)
- Deployment patterns (blue-green, canary, rollback)
- Cost optimization (tagging, right-sizing, auto-scaling)
- **9 common anti-patterns to avoid**

**Read this if:** Planning production deployment architecture

---

### 5. **PULUMI-COMPARISON.md** (38-source analysis)
**What:** Competitive analysis of Pulumi vs alternatives

**Key Learnings:**
- **Pulumi wins** for Apex Memory (Python-native, type safety, testing)
- 112x faster than Terraform (Starburst case study)
- Full GCP API coverage with same-day updates
- Multi-cloud ready (no new DSL if we expand to AWS/Azure)
- **What we're giving up:** Smaller community than Terraform (5,631 providers vs 292 packages)
- **Mitigation:** Pulumi can bridge ANY Terraform provider

**Read this if:** Need to justify Pulumi choice to stakeholders

---

### 6. **PULUMI-TRENDS-2025.md** (12,000+ words)
**What:** Current Pulumi trends and emerging patterns (2024-2025)

**Key Learnings:**
- Python SDK is first-class (full type hints, uv integration, 100x faster)
- Pulumi ESC (secrets) is GA (Sept 2024) but defer until multi-cloud needed
- GitHub Actions is industry standard for Pulumi CI/CD
- Pulumi Cloud free tier is recommended backend (auto state locking)
- **Immediate recommendations:** Python + uv + GitHub Actions + Pulumi Cloud
- **Defer:** ESC, Pulumi Neo (too new), Automation API (later)

**Read this if:** Want to know what's current and what's emerging

---

## 🎯 Architecture Decisions

Based on research, here are our key architectural choices:

### Decision Matrix

| Decision | Choice | Alternative | Why This Choice |
|----------|--------|-------------|-----------------|
| **Language** | Python | TypeScript, Go | Same language as application (zero context switching) |
| **Backend** | Pulumi Cloud (free) | GCS self-hosted | Automatic state locking, free tier sufficient, zero setup |
| **Stack Strategy** | Separate stacks (dev/staging/prod) | Separate projects | Same code, different configs, easier management |
| **Package Manager** | uv | pip, poetry | 100x faster than pip, Pulumi officially supports |
| **Secrets** | GCP Secret Manager | Pulumi ESC | Simpler, GCP-native, defer ESC until multi-cloud |
| **CI/CD** | GitHub Actions | GitLab, CircleCI | Free, excellent Pulumi integration, PR previews |
| **Testing** | pytest + mocking | Manual testing | Same framework as application, automate everything |
| **Module Organization** | 5 modules (networking, databases, compute, secrets, monitoring) | Monolithic __main__.py | Reusability, testability, separation of concerns |
| **Deployment Pattern** | Blue-green with manual prod approval | Auto-deploy to prod | Safety for production, canary testing in staging |

### Key Principles

1. **Python-First** - Use Python for everything (infrastructure + application)
2. **Type Safety** - mypy/pyright integration to catch errors before deployment
3. **Testing** - pytest for infrastructure code (same as application)
4. **Simplicity** - Start with GCP Secret Manager (defer ESC until needed)
5. **Automation** - GitHub Actions for CI/CD (PR previews + auto-deploy)
6. **Security** - Least privilege IAM, private networking, no hardcoded secrets

---

## 📅 Implementation Roadmap (6 Weeks)

### Week 1: Networking + Cloud SQL (20-24 hours)
**Goal:** VPC with private Google Access + Cloud SQL PostgreSQL

**Deliverables:**
- `modules/networking.py` - VPC, subnets, VPC connector, Cloud NAT
- `modules/databases.py` - Cloud SQL PostgreSQL (db-f1-micro, auto-scaling to db-n1-standard-1)
- Tests: 5 unit tests, 2 integration tests

**Validation:**
- `pulumi preview` shows VPC + Cloud SQL
- `pulumi up` creates resources
- PostgreSQL accessible via private IP only

---

### Week 2: Neo4j + Redis (16-20 hours)
**Goal:** Neo4j on Compute Engine + Redis Memorystore

**Deliverables:**
- Add Neo4j to `modules/databases.py` - e2-small VM with Neo4j Community
- Add Redis to `modules/databases.py` - Memorystore Basic 1GB
- Service account for Neo4j VM
- Tests: 4 unit tests, 2 integration tests

**Validation:**
- Neo4j accessible via private IP
- Redis accessible from Cloud Run via VPC connector
- Both integrated with application services

---

### Week 3: Cloud Run Services (20-24 hours)
**Goal:** Deploy API Gateway + Ingestion Worker

**Deliverables:**
- `modules/compute.py` - Reusable CloudRunService component
- Deploy API Gateway service
- Deploy Ingestion Worker service
- Auto-inject database connection strings
- Tests: 6 unit tests, 3 integration tests

**Validation:**
- API Gateway accessible via public URL
- Ingestion Worker processes documents
- Both services connect to all 4 databases

---

### Week 4: Qdrant + Secrets (16-20 hours)
**Goal:** Qdrant vector database + Secret Manager

**Deliverables:**
- Add Qdrant to `modules/compute.py` - Containerized on Cloud Run
- `modules/secrets.py` - GCP Secret Manager integration
- Migrate all secrets from env vars to Secret Manager
- Tests: 5 unit tests, 2 integration tests

**Validation:**
- Qdrant accessible from Cloud Run services
- All secrets stored in Secret Manager (zero hardcoded)
- Services retrieve secrets at runtime

---

### Week 5: Monitoring + Testing (20-24 hours)
**Goal:** Complete monitoring stack + comprehensive testing

**Deliverables:**
- `modules/monitoring.py` - Cloud Monitoring dashboards + alerts
- Grafana Cloud integration (if using)
- Complete test suite (30+ tests total)
- CI/CD pipeline (GitHub Actions)

**Validation:**
- All 27 Temporal metrics flowing
- 12+ alert rules configured
- Grafana dashboards displaying metrics
- CI/CD pipeline deploys to dev on PR merge

---

### Week 6: Production Deployment + Validation (16-20 hours)
**Goal:** Deploy to production stack + validation

**Deliverables:**
- Production stack configuration
- Blue-green deployment setup
- Rollback procedures
- Operational runbooks
- Complete documentation

**Validation:**
- Production stack deployed successfully
- Smoke tests passed (4 critical paths)
- Load tests passed (10 concurrent users, P95 <1s)
- Monitoring and alerts functional
- Rollback tested and documented

---

**Total Timeline:** 6 weeks (108-132 hours)

**Cost:**
- Dev: $50-100/month (auto-scales to zero)
- Staging: $100-200/month (always-on, smaller instances)
- Production: $411-807/month (auto-scales based on usage)

---

## 📂 Folder Structure

```
deployment/pulumi/
├── README.md                    # This file
├── Pulumi.yaml                  # Project configuration
├── requirements.txt             # Python dependencies
├── .gitignore                   # Git ignore rules
├── __main__.py                  # Main Pulumi program
│
├── modules/                     # Reusable infrastructure modules
│   ├── __init__.py
│   ├── networking.py            # VPC, subnets, load balancer
│   ├── databases.py             # PostgreSQL, Neo4j, Redis, Qdrant
│   ├── compute.py               # Cloud Run services
│   ├── secrets.py               # Secret Manager
│   └── monitoring.py            # Cloud Monitoring, Grafana
│
├── research/                    # Comprehensive research guides
│   ├── PULUMI-FUNDAMENTALS.md  # Core concepts (900+ lines)
│   ├── PULUMI-GCP-GUIDE.md     # GCP patterns (1,100+ lines)
│   ├── PULUMI-EXAMPLES.md      # Code examples (8,500+ words)
│   ├── PULUMI-BEST-PRACTICES.md # Production best practices
│   ├── PULUMI-COMPARISON.md    # vs Terraform, etc. (38 sources)
│   └── PULUMI-TRENDS-2025.md   # Current trends (12,000+ words)
│
├── examples/                    # Reference implementations
│   ├── simple-cloud-run/        # Minimal Cloud Run example
│   ├── multi-database/          # Multi-DB cluster example
│   └── full-stack/              # Complete app example
│
├── tests/                       # Infrastructure tests
│   ├── unit/                    # Unit tests (mocked resources)
│   ├── integration/             # Integration tests (real resources)
│   └── policy/                  # CrossGuard policy tests
│
└── .github/                     # GitHub Actions CI/CD
    └── workflows/
        └── pulumi.yml           # PR preview + merge deploy
```

---

## 🔧 Development Workflow

### Day-to-Day Development

**1. Create Feature Branch**
```bash
git checkout -b feature/add-qdrant-database
```

**2. Make Infrastructure Changes**
```bash
# Edit modules/databases.py to add Qdrant
code modules/databases.py

# Preview changes
pulumi preview

# Deploy to dev stack
pulumi up
```

**3. Test Changes**
```bash
# Run unit tests
pytest tests/unit/ -v

# Run integration tests (creates real resources)
pytest tests/integration/ -v

# Verify deployment
pulumi stack output
```

**4. Create Pull Request**
- GitHub Actions runs `pulumi preview` automatically
- Comment on PR with preview results
- Team reviews infrastructure changes

**5. Merge to Main**
- GitHub Actions automatically deploys to `dev` stack
- Manual approval required for `staging` and `production`

---

### Multi-Environment Management

**Switch between environments:**
```bash
# Development
pulumi stack select dev
pulumi up

# Staging
pulumi stack select staging
pulumi up

# Production (manual approval required)
pulumi stack select production
pulumi up  # Requires manual confirmation
```

**Environment-specific configuration:**
```bash
# Dev: Smaller instances, auto-scale to zero
pulumi config set --stack dev database-tier db-f1-micro
pulumi config set --stack dev min-instances 0

# Production: Larger instances, always-on
pulumi config set --stack production database-tier db-n1-standard-1
pulumi config set --stack production min-instances 1
```

---

## 🧪 Testing Strategy

### Test Pyramid

**60% Unit Tests** - Fast, mocked resources
```python
# tests/unit/test_networking.py
def test_vpc_creation():
    with pulumi.runtime.mocks.Mocks():
        vpc = create_vpc(...)
        assert vpc.name == "apex-memory-vpc"
        assert vpc.auto_create_subnetworks == False
```

**30% Property Tests** - Policy validation (CrossGuard)
```python
# tests/policy/test_security_policies.py
def test_cloud_sql_requires_private_ip():
    # Policy: Cloud SQL must not have public IP
    assert policy.validate(cloud_sql_instance)
```

**10% Integration Tests** - Real resources (expensive)
```python
# tests/integration/test_database_cluster.py
def test_postgres_connectivity():
    # Deploy real PostgreSQL, test connection
    result = pulumi.automation.LocalWorkspace.create_or_select_stack(...)
    result.up()
    assert can_connect_to_postgres()
    result.destroy()
```

### Running Tests

```bash
# All tests
pytest

# Unit tests only (fast)
pytest tests/unit/ -v

# Integration tests (slow, creates real resources)
pytest tests/integration/ -v -m integration

# Policy tests
pytest tests/policy/ -v

# Coverage report
pytest --cov=modules --cov-report=html
```

---

## 🚀 Deployment Guide

### Prerequisites Checklist

Before deploying, complete [deployment/DEPLOYMENT-NEEDS.md](../DEPLOYMENT-NEEDS.md):

- [ ] GCP Account created ($300 free credit)
- [ ] Temporal Cloud account ($100-150/month)
- [ ] Grafana Cloud Pro ($19/month)
- [ ] OpenAI API key obtained
- [ ] Anthropic API key obtained
- [ ] Docker Desktop licensed
- [ ] All secrets generated (openssl rand -base64 32)
- [ ] 2FA enabled on all accounts
- [ ] Budget alerts configured ($700/month threshold)

**Total monthly cost:** $149-249/month for first 90 days (with GCP credits), then $411-807/month

---

### Step-by-Step Deployment

**1. Initial Setup**
```bash
cd deployment/pulumi

# Create virtual environment
uv venv
source venv/bin/activate

# Install dependencies
uv pip install -r requirements.txt

# Login to Pulumi Cloud (free tier)
pulumi login

# Create dev stack
pulumi stack init dev
pulumi config set gcp:project apex-memory-dev
pulumi config set gcp:region us-central1
```

**2. Configure Secrets**
```bash
# Generate secrets (DO NOT commit these!)
openssl rand -base64 32  # JWT secret key
openssl rand -base64 32  # PostgreSQL password
openssl rand -base64 32  # Neo4j password

# Set secrets (encrypted by Pulumi)
pulumi config set --secret jwt-secret-key <generated-secret>
pulumi config set --secret postgres-password <generated-secret>
pulumi config set --secret neo4j-password <generated-secret>

# Add API keys
pulumi config set --secret openai-api-key sk-...
pulumi config set --secret anthropic-api-key sk-ant-...
```

**3. Deploy Infrastructure**
```bash
# Preview changes (dry run)
pulumi preview

# Deploy to dev
pulumi up

# Verify outputs
pulumi stack output

# Expected outputs:
# - project_id: apex-memory-dev
# - region: us-central1
# - api_url: https://apex-api-xxxxx-uc.a.run.app
# - postgres_connection: apex-memory-dev:us-central1:postgres
```

**4. Validate Deployment**
```bash
# Check API health
curl https://$(pulumi stack output api_url)/health

# Run smoke tests
pytest tests/integration/test_smoke.py -v

# View logs
pulumi logs --follow
```

**5. Promote to Staging/Production**
```bash
# Create staging stack
pulumi stack init staging
pulumi config set gcp:project apex-memory-staging
# ... configure secrets ...
pulumi up

# Create production stack (requires manual approval)
pulumi stack init production
pulumi config set gcp:project apex-memory-prod
# ... configure secrets ...
pulumi up  # Manual confirmation required
```

---

## 🔍 Troubleshooting

### Common Issues

**Issue 1: `pulumi up` fails with "quota exceeded"**

**Cause:** GCP project quota limits

**Solution:**
```bash
# Check quota usage
gcloud compute project-info describe --project=apex-memory-dev

# Request quota increase
# Navigate to: https://console.cloud.google.com/iam-admin/quotas
# Search for: Cloud SQL instances
# Request increase to 10 instances
```

---

**Issue 2: Cloud Run service won't start**

**Cause:** Container fails to start, database not accessible

**Solution:**
```bash
# View Cloud Run logs
pulumi logs --resource apex-api --follow

# Common errors:
# - ModuleNotFoundError → Fix Dockerfile PYTHONPATH
# - Connection refused → Check VPC connector, database private IP
# - Permission denied → Check service account IAM roles

# Fix VPC connector
pulumi config set vpc-connector apex-vpc-connector
pulumi up
```

---

**Issue 3: State file conflicts**

**Cause:** Multiple team members running `pulumi up` simultaneously

**Solution:**
```bash
# Pulumi Cloud automatically handles locking (no action needed)

# If using GCS backend:
pulumi config set backend.url gs://apex-pulumi-state
pulumi up  # Pulumi will wait for lock to be released
```

---

**Issue 4: Secrets not decrypting**

**Cause:** Wrong Pulumi stack selected

**Solution:**
```bash
# Verify current stack
pulumi stack

# Select correct stack
pulumi stack select dev

# Verify secrets are encrypted
pulumi config get --show-secrets jwt-secret-key
```

---

### Getting Help

**Resources:**
- Official Pulumi docs: https://www.pulumi.com/docs/
- Pulumi Slack: https://pulumi.io/slack
- GCP support: https://cloud.google.com/support
- Research guides: `research/` directory in this repo

**Debugging Commands:**
```bash
# Show detailed stack information
pulumi stack --show-ids --show-urns

# Export stack to JSON
pulumi stack export > stack-backup.json

# Refresh state (sync with actual resources)
pulumi refresh

# View resource dependencies
pulumi stack graph > dependency-graph.dot
dot -Tpng dependency-graph.dot -o dependencies.png
```

---

## 🎉 Summary

**What You Have Now:**
- ✅ Complete Pulumi project structure
- ✅ 5 comprehensive research guides (50+ pages combined)
- ✅ Starter files (Pulumi.yaml, __main__.py, requirements.txt)
- ✅ Architecture decisions documented
- ✅ 6-week implementation roadmap
- ✅ Testing strategy defined
- ✅ CI/CD plan ready

**Next Steps:**
1. Review research guides in `research/` directory (2-3 hours)
2. Make final architecture decisions (1 hour)
3. Implement Week 1: Networking + Cloud SQL (20-24 hours)
4. Follow 6-week roadmap to production

**Total Time to Production:** 6 weeks (108-132 hours)

**Total Cost:** $411-807/month (auto-scales based on usage)

---

**Ready to start implementation?** Begin with Week 1: Networking + Cloud SQL!
