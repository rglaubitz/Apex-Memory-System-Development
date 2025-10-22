# Apex Memory System - Deployment Documentation

**Central hub for all deployment paths, guides, and resources.**

---

## 📍 Quick Navigation

**Which deployment guide do I need?**

| I want to... | Go to... | Status |
|-------------|----------|--------|
| **Deploy MCP Server to PyPI** | [mcp-server/](mcp-server/) | 🟡 Pre-Production (82% complete) |
| **Deploy to Production (GCP)** | [production/](production/) | 📝 Planned |
| **Run Pre-Deployment Verification** | [verification/](verification/) | ✅ Complete |
| **Run Pre-Deployment Testing** | [testing/](testing/) | ✅ Complete |
| **Deploy Query Router** | [components/query-router/](components/query-router/) | ✅ Deployed |

---

## 🚀 MCP Server Deployment

**Path:** [mcp-server/](mcp-server/)

**What:** Deploy Apex MCP Server to PyPI for npm-style installation (`uvx apex-mcp-server`)

**Status:** 🟡 Pre-Production (Phase 1 complete - awaiting manual testing)

**Quick Start:**
```bash
cd apex-mcp-server
./install-apex-mcp.sh
```

**Key Documents:**
- **[DEPLOYMENT-CHECKLIST.md](mcp-server/DEPLOYMENT-CHECKLIST.md)** - 8-phase rollout plan (70+ tasks)
- **[PUBLISHING.md](mcp-server/PUBLISHING.md)** - PyPI publishing guide

**Current Phase:** Phase 2 - Manual Testing (requires user testing before PyPI publish)

**Next Steps:**
1. Test install script
2. Test Claude Desktop integration
3. Test all 10 MCP tools
4. Publish to TestPyPI
5. Publish to production PyPI

---

## ☁️ Production Deployment (GCP)

**Path:** [production/](production/)

**What:** Deploy full Apex Memory System to Google Cloud Platform

**Status:** 📝 Planned (architecture complete, not yet deployed)

**Timeline:** 4-6 weeks | **Cost:** $500-$1,500/month

**Key Documents:**
- **[README.md](production/README.md)** - Overview and decision framework
- **[GCP-DEPLOYMENT-GUIDE.md](production/GCP-DEPLOYMENT-GUIDE.md)** - Step-by-step GCP deployment
- **[ARCHITECTURE.md](production/ARCHITECTURE.md)** - Production architecture
- **[DEPLOYMENT-CHECKLIST.md](production/DEPLOYMENT-CHECKLIST.md)** - Production deployment tasks
- **[UPDATE-WORKFLOW.md](production/UPDATE-WORKFLOW.md)** - Zero-downtime updates

**Infrastructure:**
- GKE cluster (3 nodes: 4 vCPU, 16GB each)
- Cloud SQL PostgreSQL + pgvector
- Neo4j Aura database
- Qdrant Cloud vector search
- Redis Memorystore
- Cloud Load Balancing + CDN
- Cloud Armor (DDoS protection)

**Next Steps:**
1. Create GCP project and enable billing
2. Configure Terraform backend
3. Review and customize terraform variables
4. Deploy infrastructure
5. Deploy application

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

1. **Verification** (3-4 hours)
   - Run [verification/](verification/) workflow
   - Ensure all 23 verifications pass
   - Document any issues

2. **Testing** (3-4 hours)
   - Run [testing/](testing/) suite
   - Ensure 230+ tests pass
   - Review performance metrics

3. **Component Deployment** (1 week per component)
   - Deploy components individually
   - Start with [components/query-router/](components/query-router/)
   - Validate each component before next

4. **Production Deployment** (4-6 weeks)
   - Follow [production/](production/) guide
   - Deploy to GCP infrastructure
   - Monitor for 1 week before full cutover

5. **MCP Server** (1-2 weeks)
   - Follow [mcp-server/](mcp-server/) guide
   - Publish to PyPI
   - Enable npm-style installation

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

## 🚨 Before You Deploy

**Pre-flight checklist:**

- [ ] All tests passing (230+ tests)
- [ ] All verifications passing (23 verifications)
- [ ] Documentation reviewed and up-to-date
- [ ] Environment variables configured
- [ ] Database backups created
- [ ] Rollback plan documented
- [ ] Monitoring and alerting configured
- [ ] Team notified of deployment window

---

## 📞 Support

**Issues?**
- Check component-specific TROUBLESHOOTING.md files
- Review [verification/](verification/) results
- Check [testing/](testing/) results
- Create GitHub issue with reproduction steps

---

**Last Updated:** 2025-10-21
**Deployment System Status:** 🟢 Operational (1 deployed, 1 pre-production, 1 planned)
