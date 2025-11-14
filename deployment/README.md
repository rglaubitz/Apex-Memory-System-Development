# Apex Memory System - Deployment Documentation

**Central hub for all deployment paths, guides, and resources.**

**Last Updated:** 2025-11-07
**Deployment System Status:** 🟢 Operational (1 deployed, 1 production-ready, 1 planned)

---

## 🚀 Getting Started

**New to deployment? Start here:**

1. **📋 Prerequisites** → [DEPLOYMENT-NEEDS.md](DEPLOYMENT-NEEDS.md) - What you need to buy/obtain first (4-6 hours setup)
2. **✅ Verification** → [verification/](verification/) - Verify production readiness (3-4 hours)
3. **🧪 Testing** → [testing/](testing/) - Run comprehensive tests (3-4 hours)
4. **☁️ Deploy** → [production/](production/) - Deploy to GCP (4-6 weeks)

**Total time:** ~5-7 weeks from zero to production
**Total cost:** $411-807/month (or $149-249/month for first 90 days with GCP credits)

---

## 📍 Quick Navigation

**Which deployment guide do I need?**

| I want to... | Go to... | Status |
|-------------|----------|--------|
| **⚠️ See what I need to buy/obtain first** | **[DEPLOYMENT-NEEDS.md](DEPLOYMENT-NEEDS.md)** ⭐ | **📋 START HERE** |
| **Deploy MCP Server to PyPI** | [mcp-server/](mcp-server/) | 🔴 Blocked (Python version issue) |
| **Deploy to Production (GCP)** | [production/](production/) | 📝 Planned |
| **Run Pre-Deployment Verification** | [verification/](verification/) | ✅ Complete |
| **Run Pre-Deployment Testing** | [testing/](testing/) | ✅ Complete |
| **Deploy Query Router** | [components/query-router/](components/query-router/) | ✅ Deployed |
| **Deploy Google Drive Integration** | [components/google-drive-integration/](components/google-drive-integration/) | ✅ Production Ready |

---

## ⚠️ BEFORE YOU DEPLOY - READ THIS FIRST

**📋 Complete prerequisite checklist:** [DEPLOYMENT-NEEDS.md](DEPLOYMENT-NEEDS.md)

**What you need to buy/obtain before starting any deployment:**
- GCP Account ($300 free credit for 90 days)
- Temporal Cloud ($100-150/month)
- Grafana Cloud Pro ($19/month)
- OpenAI API key (~$10-30/month)
- Anthropic API key (~$20-50/month)
- Docker Desktop license verification (may need Business license if org >250 employees)
- Password manager (Bitwarden free or 1Password $5/month)
- Domain name (optional, ~$12-15/year)

**Total monthly cost:** $411-807/month (or $149-249/month for first 90 days with GCP credits)

**Setup time:** 4-6 hours (spread over 1-2 days for account approvals)

**⛔ DO NOT START DEPLOYMENT** until you've completed [DEPLOYMENT-NEEDS.md](DEPLOYMENT-NEEDS.md).

This comprehensive checklist includes:
- Table of all services with costs and signup links
- Step-by-step setup workflow (recommended order)
- Docker Desktop licensing verification
- Secret generation and storage
- 2FA setup for all accounts
- Budget alerts configuration
- Cost optimization tips

**See:** [DEPLOYMENT-NEEDS.md](DEPLOYMENT-NEEDS.md) for complete details.

---

## 🚀 MCP Server Deployment

**Path:** [mcp-server/](mcp-server/)

**What:** Deploy Apex MCP Server to PyPI for npm-style installation (`uvx apex-mcp-server`)

**Status:** 🔴 Blocked (Python version mismatch)

**Blocker:** MCP server not connecting - Python 3.14 vs 3.12 mismatch
- **Issue:** Claude Desktop uses Python 3.14, package installed in Python 3.12
- **Error:** `ModuleNotFoundError: No module named 'apex_mcp_server'`
- **Fix:** Update Claude Desktop config to use Python 3.12 path
- **Details:** [mcp-server/ISSUES-AND-FIXES.md](mcp-server/ISSUES-AND-FIXES.md)

**Quick Start:**
```bash
cd apex-mcp-server
./install-apex-mcp.sh
```

**Key Documents:**
- **[DEPLOYMENT-CHECKLIST.md](mcp-server/DEPLOYMENT-CHECKLIST.md)** - 8-phase rollout plan (70+ tasks)
- **[PUBLISHING.md](mcp-server/PUBLISHING.md)** - PyPI publishing guide
- **[ISSUES-AND-FIXES.md](mcp-server/ISSUES-AND-FIXES.md)** - Current issues and resolutions ⚠️ **NEW**

**Current Phase:** Phase 2 - Manual Testing (blocked by Python version issue)

**Next Steps:**
1. ⚠️ **Fix Python version mismatch** (immediate)
2. Test install script
3. Test Claude Desktop integration
4. Test all 10 MCP tools
5. Publish to TestPyPI
6. Publish to production PyPI

---

## ☁️ Production Deployment (GCP)

**Path:** [pulumi/](pulumi/) (Infrastructure-as-Code) | [production/](production/) (Deployment guide)

**What:** Deploy full Apex Memory System to Google Cloud Platform using Pulumi

**Status:** 🟢 Phase 0 Complete | 🔵 Week 1 Ready (Networking + Cloud SQL)

**Timeline:** 6 weeks (108-132 hours remaining) | **Cost:** $411-807/month

**Last Updated:** 2025-11-08

**Prerequisites:** ⚠️ **MUST complete [DEPLOYMENT-NEEDS.md](DEPLOYMENT-NEEDS.md) first**

**Progress (2025-11-08):**

**✅ Phase 0: Pulumi Setup Complete**
- Installed all CLI tools (Pulumi v3.206.0, gcloud v546.0.0, uv 0.8.12)
- Authenticated with GCP and Pulumi Cloud
- Created `dev` stack in `apex-memory-dev` project
- Deployed 13 GCP APIs (compute, sqladmin, redis, run, secretmanager, etc.)
- Infrastructure state managed via Pulumi Cloud
- View deployment: https://app.pulumi.com/rglaubitz-org/apex-memory-infrastructure/dev/updates/1

**📋 Next: Week 1 Implementation (20-24 hours)**
- Create `modules/networking.py` - VPC with private Google Access
- Create `modules/databases.py` - Cloud SQL PostgreSQL
- See [pulumi/README.md](pulumi/README.md) for detailed plan

**Key Documents:**
- **[DEPLOYMENT-NEEDS.md](DEPLOYMENT-NEEDS.md)** - ⭐ **START HERE** - What to buy/obtain before deploying
- **[pulumi/README.md](pulumi/README.md)** - ⭐ **Pulumi IaC Guide** - Complete setup and implementation guide
- **[PRODUCTION-DEPLOYMENT-PLAN.md](PRODUCTION-DEPLOYMENT-PLAN.md)** - Complete 5-6 week deployment plan
- **[production/README.md](production/README.md)** - Overview and decision framework
- **[production/GCP-DEPLOYMENT-GUIDE.md](production/GCP-DEPLOYMENT-GUIDE.md)** - Step-by-step GCP deployment (8 phases)
- **[production/ARCHITECTURE.md](production/ARCHITECTURE.md)** - Production architecture decisions

**Infrastructure:**
- Cloud Run (serverless containers) - API, Workers, Qdrant
- Cloud SQL PostgreSQL + pgvector (db-n1-standard-1 to start)
- Neo4j on Compute Engine (e2-small to start)
- Qdrant on Cloud Run (containerized)
- Redis Memorystore (Basic 1GB)
- Cloud Load Balancing + SSL
- Temporal Cloud (workflow orchestration)
- Grafana Cloud Pro (monitoring)

**Monthly Cost Breakdown:**
- GCP Services: $261-542/month (auto-scales)
- Temporal Cloud: $100-150/month
- Grafana Cloud: $19/month
- API Keys (OpenAI + Anthropic): $30-80/month
- **Total: $411-807/month**

**First 90 Days:** $149-249/month (using GCP $300 free credit)

**Next Steps:**
1. ✅ ~~Complete [DEPLOYMENT-NEEDS.md](DEPLOYMENT-NEEDS.md) prerequisites~~ (partially complete - GCP auth done)
2. 🔵 **CURRENT:** Week 1 Pulumi Implementation - Networking + Cloud SQL (20-24 hours)
3. Week 2: Neo4j + Redis (16-20 hours)
4. Week 3: Cloud Run Services (20-24 hours)
5. Week 4: Qdrant + Secrets (16-20 hours)
6. Week 5: Monitoring + Testing (20-24 hours)
7. Week 6: Production Deployment (16-20 hours)

**See [pulumi/README.md](pulumi/README.md) for detailed 6-week roadmap.**

---

## ✅ Pre-Deployment Verification

**Path:** [verification/](verification/)

**What:** Verify production readiness before deployment

**Status:** ✅ Complete (all verifications passing)

**Timeline:** 3-4 hours

**Key Documents:**
- **[README.md](verification/README.md)** - Verification overview
- **[WORKFLOW-CHECKLIST.md](verification/WORKFLOW-CHECKLIST.md)** - Step-by-step verification workflow

**Verification Categories:**
1. **Core Functionality** (8 tests) - API endpoints, ingestion, search
2. **Database Integrity** (6 tests) - Neo4j, PostgreSQL, Qdrant, Redis
3. **Performance** (4 tests) - Latency, throughput, concurrent users
4. **Error Handling** (3 tests) - Graceful failures, rollback, monitoring
5. **Documentation** (2 tests) - API docs, deployment guides

**Results:** 23/23 verifications passing ✅

---

## 🧪 Pre-Deployment Testing

**Path:** [testing/](testing/)

**What:** Comprehensive pre-deployment testing suite

**Status:** ✅ Complete (all tests passing)

**Timeline:** 3-4 hours

**Key Documents:**
- **[README.md](testing/README.md)** - Testing kit overview
- **[TESTING-KIT.md](testing/TESTING-KIT.md)** - Complete testing guide
- **[IMPLEMENTATION.md](testing/IMPLEMENTATION.md)** - Implementation details
- **[EXECUTION-PLAN.md](testing/EXECUTION-PLAN.md)** - Testing execution plan

**Test Categories:**
1. **Unit Tests** (150+ tests) - Individual components
2. **Integration Tests** (50+ tests) - Multi-component workflows
3. **Load Tests** (10+ tests) - Performance under load
4. **End-to-End Tests** (20+ tests) - Complete user workflows

**Results:** 230+ tests passing ✅

**Quick Run:**
```bash
cd testing
./scripts/run-all-tests.sh
```

---

## 🧩 Component-Specific Deployment

**Path:** [components/](components/)

**What:** Deployment guides for individual components

**Currently Available:**

### Query Router
**Path:** [components/query-router/](components/query-router/)

**Status:** ✅ Deployed (90% accuracy, production-ready)

**Key Documents:**
- **[DEPLOYMENT-GUIDE.md](components/query-router/DEPLOYMENT-GUIDE.md)** - Deployment steps
- **[PRODUCTION-ROLLOUT.md](components/query-router/PRODUCTION-ROLLOUT.md)** - Rollout plan
- **[TESTING.md](components/query-router/TESTING.md)** - Testing guide
- **[TROUBLESHOOTING.md](components/query-router/TROUBLESHOOTING.md)** - Common issues

**Features:**
- Intent-based query classification (7 query types)
- Optimal database routing (Neo4j, PostgreSQL, Qdrant, Redis)
- 90% routing accuracy
- <100ms cache-hit latency

### Google Drive Integration
**Path:** [components/google-drive-integration/](components/google-drive-integration/)

**Status:** ✅ Production Ready (92% test pass rate)

**Completion Date:** November 7, 2025

**Key Documents:**
- **[DEPLOYMENT-CHECKLIST.md](components/google-drive-integration/DEPLOYMENT-CHECKLIST.md)** - 14-item pre-deployment checklist
- **[DEPLOYMENT-GUIDE.md](components/google-drive-integration/DEPLOYMENT-GUIDE.md)** - Complete deployment guide
- **[TROUBLESHOOTING-RUNBOOK.md](components/google-drive-integration/TROUBLESHOOTING-RUNBOOK.md)** - Operational troubleshooting (800 lines)
- **[README.md](components/google-drive-integration/README.md)** - Component overview

**Features:**
- Automated Google Drive folder monitoring (every 15 minutes via Temporal schedule)
- Auto-ingestion of new documents → DocumentIngestionWorkflow
- Auto-archive of processed files → Google Drive archive folder
- Error handling with Dead Letter Queue (retryable vs non-retryable classification)
- 7 Prometheus metrics + 12 alert rules (critical/warning/info)
- PostgreSQL-backed tracking (processed files, permanent failures)

**Test Coverage:**
- 44/48 tests passing (92%)
- 100% coverage for critical paths (fetch, archive, poll, error handling, DLQ)

**Quick Start:**
```bash
# 1. Complete pre-deployment checklist
cat deployment/components/google-drive-integration/DEPLOYMENT-CHECKLIST.md

# 2. Follow deployment guide
cat deployment/components/google-drive-integration/DEPLOYMENT-GUIDE.md

# 3. Deploy and verify
python scripts/temporal/create_monitor_schedule.py
sudo systemctl start apex-temporal-worker
```

---

## 📊 Deployment Decision Tree

**Start here if you're unsure which deployment path to follow:**

```
Do you need to deploy the MCP Server for Claude Desktop?
├─ YES → mcp-server/ (PyPI deployment)
└─ NO
   └─ Do you need to deploy to production cloud infrastructure?
      ├─ YES → production/ (GCP deployment)
      └─ NO
         └─ Do you need to verify production readiness?
            ├─ YES → verification/ (pre-deployment verification)
            └─ NO
               └─ Do you need to run comprehensive tests?
                  ├─ YES → testing/ (pre-deployment testing)
                  └─ NO
                     └─ Do you need to deploy a specific component?
                        └─ YES → components/{component-name}/
```

---

## 🎯 Recommended Deployment Sequence

**For first-time production deployment:**

### Phase 0: Prerequisites (4-6 hours, Days 1-3)
   - **📋 [DEPLOYMENT-NEEDS.md](DEPLOYMENT-NEEDS.md)** - Complete ALL prerequisites first
   - Set up GCP account ($300 free credit)
   - Create Temporal Cloud account ($100-150/month)
   - Create Grafana Cloud Pro account ($19/month)
   - Obtain API keys (OpenAI, Anthropic)
   - Verify Docker Desktop licensing
   - Generate and store all secrets securely
   - Enable 2FA on all accounts
   - **⛔ DO NOT PROCEED without completing this phase**

### Phase 1: Verification (3-4 hours)
   - Run [verification/](verification/) workflow
   - Ensure all 23 verifications pass
   - Document any issues
   - Establish production readiness baseline

### Phase 2: Testing (3-4 hours)
   - Run [testing/](testing/) suite
   - Ensure 230+ tests pass
   - Review performance metrics
   - Validate all critical paths

### Phase 3: Infrastructure-as-Code (40-60 hours, Weeks 1-2)
   - **Critical blocker:** Create Pulumi IaC (doesn't exist yet)
   - Define all GCP resources (VPC, Cloud Run, databases)
   - Test deployment locally
   - Document IaC patterns
   - **Cannot deploy without this**

### Phase 4: Production Deployment (88-128 hours, Weeks 3-5)
   - Follow [production/GCP-DEPLOYMENT-GUIDE.md](production/GCP-DEPLOYMENT-GUIDE.md)
   - Deploy databases (PostgreSQL, Neo4j, Qdrant, Redis)
   - Deploy application (Cloud Run services)
   - Configure monitoring and alerts
   - Run production validation
   - Monitor for 1 week before full cutover

### Phase 5: MCP Server (Optional, 1-2 weeks)
   - Follow [mcp-server/](mcp-server/) guide
   - Fix Python version issue first
   - Publish to PyPI
   - Enable npm-style installation (`uvx apex-mcp-server`)

---

## 📚 Additional Resources

**Main Documentation:**
- **[Project README](../README.md)** - Project overview
- **[CLAUDE.md](../CLAUDE.md)** - Development guide
- **[apex-memory-system/CLAUDE.md](../apex-memory-system/CLAUDE.md)** - Main codebase guide

**Research:**
- **[research/](../research/)** - Architecture decisions, documentation

**Upgrades:**
- **[upgrades/](../upgrades/)** - Feature implementation tracking

---

## 🚨 Before You Deploy - Critical Checklist

**⛔ STOP - Complete these before any deployment:**

### Prerequisites (Phase 0)
- [ ] **[DEPLOYMENT-NEEDS.md](DEPLOYMENT-NEEDS.md) 100% complete** - All items checked
- [ ] GCP account created with $300 free credit
- [ ] Temporal Cloud account created ($100-150/month)
- [ ] Grafana Cloud Pro account created ($19/month)
- [ ] OpenAI API key obtained and stored in password manager
- [ ] Anthropic API key obtained and stored in password manager
- [ ] Docker Desktop licensed correctly (verify if Business license needed)
- [ ] All secrets generated (SECRET_KEY, DB passwords) and stored securely
- [ ] 2FA enabled on all cloud accounts
- [ ] Password manager configured with all credentials

### Verification (Phase 1)
- [ ] All 230+ tests passing
- [ ] All 23 verifications passing
- [ ] Production readiness confirmed

### Infrastructure Preparation (Phase 3)
- [ ] Pulumi Infrastructure-as-Code created (40-60 hours)
- [ ] IaC tested locally
- [ ] All GCP resources defined

### Deployment Readiness (Phase 4)
- [ ] Documentation reviewed and up-to-date
- [ ] Environment variables configured
- [ ] Database backups created
- [ ] Rollback plan documented
- [ ] Monitoring and alerting configured
- [ ] Budget alerts set ($700/month threshold)

**Estimated total prep time before first deployment:** 50-70 hours (Phases 0-3)

---

## 📞 Support

**Issues?**
- Check component-specific TROUBLESHOOTING.md files
- Review [verification/](verification/) results
- Check [testing/](testing/) results
- Create GitHub issue with reproduction steps

---

## 💡 Key Insights from Deployment Readiness Analysis

**Current State:** 72% production-ready with clear path to deployment

**Strengths:**
- ✅ Excellent codebase (39,499 lines, 477 tests)
- ✅ Production monitoring ready (27 metrics, 5 dashboards, 12+ alerts)
- ✅ Complete database schemas (7 Alembic migrations + Neo4j + Qdrant)
- ✅ Comprehensive documentation (1,755-line deployment guide)

**Critical Gaps:**
- 🔴 No Infrastructure-as-Code (40-60 hours to create)
- 🔴 3 critical bugs to fix (Dockerfile, SECRET_KEY, .dockerignore) - 1 hour total
- ⚠️ No deployment automation

**Realistic Timeline:** 5-6 weeks (128-170 hours)
**Realistic Cost:** $411-807/month (or $149-249/month for first 90 days)

**See:** [DEPLOYMENT-NEEDS.md](DEPLOYMENT-NEEDS.md) for complete prerequisites and cost breakdown.

---

**Last Updated:** 2025-11-08
**Deployment System Status:** 🟢 Operational (1 deployed, 1 production-ready, 1 in-progress)
**Documentation Status:** ✅ Complete with prerequisites checklist
**Pulumi Status:** 🟢 Phase 0 Complete | 🔵 Week 1 Ready
