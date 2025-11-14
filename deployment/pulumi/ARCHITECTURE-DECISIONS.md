# Apex Memory System - Pulumi Architecture Decisions

**Date:** 2025-11-08
**Status:** ✅ Research Complete | 🎯 Ready for Implementation
**Research Base:** 5 comprehensive guides (50+ pages, 38+ sources)

---

## Executive Summary

After comprehensive research across 5 dimensions (fundamentals, GCP patterns, examples, best practices, competitive analysis, trends), we've made clear architectural decisions for deploying Apex Memory System using Pulumi Infrastructure-as-Code.

**Bottom Line:**
- **Language:** Python (same as application)
- **Backend:** Pulumi Cloud free tier (auto state locking)
- **Stack Strategy:** Multi-stack (dev/staging/prod)
- **Package Manager:** uv (100x faster than pip)
- **Secrets:** GCP Secret Manager (defer Pulumi ESC until multi-cloud)
- **CI/CD:** GitHub Actions (PR previews + auto-deploy)
- **Timeline:** 6 weeks to production
- **Cost:** $411-807/month (auto-scales)

---

## Decision Matrix

| # | Decision Area | Choice | Alternative(s) | Rationale | Risk/Mitigation |
|---|--------------|--------|----------------|-----------|-----------------|
| 1 | **Programming Language** | Python | TypeScript, Go, C#, Java | Same language as application code (zero context switching), team expertise, type safety with mypy | Risk: TypeScript is Pulumi's primary SDK<br>Mitigation: Python SDK is first-class (2024-2025 updates prove parity) |
| 2 | **State Backend** | Pulumi Cloud (free tier) | GCS self-hosted, S3, Azure Blob | Automatic state locking, zero setup, free tier sufficient (500 resources), integrated secrets encryption | Risk: Vendor lock-in<br>Mitigation: Can export state and migrate to GCS backend anytime |
| 3 | **Stack Strategy** | Separate stacks per environment (dev/staging/prod) | Separate projects, monorepo with sub-projects | Same code, different configs (Pulumi.{stack}.yaml), easier management, cost isolation | Risk: Config drift between environments<br>Mitigation: Configuration testing in CI/CD |
| 4 | **Python Package Manager** | uv | pip, poetry, pipenv | 100x faster than pip, officially supported by Pulumi (Nov 2024), Rust-based, single tool for everything | Risk: Newer tool (less mature)<br>Mitigation: Fallback to pip is trivial (requirements.txt works with both) |
| 5 | **Secrets Management** | GCP Secret Manager | Pulumi ESC, HashiCorp Vault | Simpler, GCP-native, no additional service, already using for runtime secrets, defer ESC until multi-cloud | Risk: Locked to GCP for secrets<br>Mitigation: Pulumi ESC migration path exists when needed |
| 6 | **CI/CD Platform** | GitHub Actions | GitLab CI, CircleCI, Jenkins | Free, excellent Pulumi integration, PR preview comments, already using GitHub, large community | Risk: GitHub outages<br>Mitigation: Can run `pulumi up` manually from local machine |
| 7 | **Testing Framework** | pytest (unit + integration) | unittest, manual testing | Same framework as application code, extensive mocking support, Pulumi provides test helpers | Risk: Integration tests cost money (real resources)<br>Mitigation: Use unit tests (90%), integration tests (10%) |
| 8 | **Module Organization** | 5 modules (networking, databases, compute, secrets, monitoring) | Monolithic __main__.py, one module per resource type | Separation of concerns, reusability, testability, aligns with research best practices | Risk: Over-engineering<br>Mitigation: Start simple, refactor as needed |
| 9 | **Deployment Pattern** | Blue-green with manual prod approval | Auto-deploy to prod, canary only | Safety for production, allows testing in staging, rollback is instant (traffic shift), manual gate prevents accidents | Risk: Slower deployments<br>Mitigation: Automate dev/staging, manual approval only for prod |
| 10 | **Resource Naming** | Prefix + environment + resource type (apex-prod-postgres) | Random names, resource type only | Cost tracking by environment, easy identification in console, predictable names | Risk: Name collisions<br>Mitigation: Include stack name in prefix |
| 11 | **Multi-Database Approach** | Component Resource pattern | Separate resources, monolithic module | Encapsulation, reusability, single component manages PostgreSQL + Redis + Neo4j + Qdrant | Risk: Complexity<br>Mitigation: Start simple (Week 1), refactor to component (Week 3) |
| 12 | **VPC Strategy** | Single VPC per environment | Shared VPC across environments | Network isolation per environment, simpler security, clear cost attribution | Risk: More expensive<br>Mitigation: VPC is free, only subnet IPs cost money |
| 13 | **Cloud Run Scaling** | Min instances = 1 (prod), 0 (dev) | Always 0, always 1 | No cold starts in production (<50ms), cost savings in dev (scales to zero when unused) | Risk: Higher prod cost (~$30/month per service)<br>Mitigation: Worth it for latency (P95 <1s) |
| 14 | **Database Sizing** | Start small, auto-scale | Fixed large instances | db-f1-micro → auto-upgrade to db-n1-standard-1 when CPU >70%, cost optimization | Risk: Performance issues before auto-scale<br>Mitigation: Monitoring alerts at 60% CPU |
| 15 | **Secret Rotation** | Manual (via Pulumi config) | Automatic rotation | Simplicity, control, scheduled rotation via calendar (quarterly) | Risk: Forgotten rotations<br>Mitigation: Calendar reminders, documentation |

---

## Detailed Decision Rationale

### 1. Programming Language: Python

**Research Evidence:**
- PULUMI-TRENDS-2025.md: Python SDK is first-class, 2024 updates prove parity with TypeScript
- PULUMI-COMPARISON.md: Python teams 3-5x more productive when infrastructure matches app language
- PULUMI-FUNDAMENTALS.md: Type safety with mypy/pyright, same as application code

**Decision:** Python for all infrastructure code

**Benefits:**
- Zero context switching between application and infrastructure
- Same testing framework (pytest)
- Same linting/formatting tools (black, isort, flake8)
- Team expertise (no need to learn TypeScript/HCL)
- Type safety with mypy (catch errors before deployment)

**Trade-offs:**
- TypeScript has slightly larger community (but Python is fully supported)
- Some Pulumi examples are in TypeScript (but easily translatable)

**Validation:** 5 migration stories in PULUMI-COMPARISON.md show Python productivity gains

---

### 2. State Backend: Pulumi Cloud (Free Tier)

**Research Evidence:**
- PULUMI-BEST-PRACTICES.md: Pulumi Cloud recommended for teams <10 people
- PULUMI-TRENDS-2025.md: Free tier increased to 500 resources (sufficient for Apex)
- PULUMI-FUNDAMENTALS.md: Automatic state locking, zero setup

**Decision:** Pulumi Cloud backend (not self-hosted GCS)

**Benefits:**
- Automatic state locking (no race conditions)
- Encrypted state at rest (AES-256)
- Zero setup (no buckets to create)
- Free tier: 500 resources, 500 deployment minutes/month
- Integrated secrets encryption
- Web UI for stack visualization

**Trade-offs:**
- Vendor lock-in (mitigated by export/import capability)
- Internet dependency (can't deploy offline)

**Cost:** $0/month (free tier sufficient)

**Migration Path:** Can export state and switch to GCS backend anytime:
```bash
pulumi stack export > state.json
pulumi login gs://apex-pulumi-state
pulumi stack import < state.json
```

---

### 3. Stack Strategy: Multi-Stack (dev/staging/prod)

**Research Evidence:**
- PULUMI-BEST-PRACTICES.md: Micro-stacks pattern for lifecycle separation
- PULUMI-EXAMPLES.md: 90% of production teams use separate stacks per environment

**Decision:** 3 stacks (dev, staging, production) in single project

**Structure:**
```
apex-memory-infrastructure/
├── Pulumi.yaml              # Base configuration
├── Pulumi.dev.yaml          # Dev overrides (small instances)
├── Pulumi.staging.yaml      # Staging overrides (medium instances)
├── Pulumi.production.yaml   # Production overrides (large instances)
└── __main__.py              # Shared code
```

**Benefits:**
- Same code for all environments (DRY principle)
- Environment-specific configuration (Pulumi.{stack}.yaml)
- Cost isolation (dev scales to zero, prod always-on)
- Clear promotion path (dev → staging → production)

**Configuration Examples:**
```yaml
# Pulumi.dev.yaml
config:
  apex:database-tier: db-f1-micro
  apex:min-instances: 0
  apex:auto-scale: true

# Pulumi.production.yaml
config:
  apex:database-tier: db-n1-standard-1
  apex:min-instances: 1
  apex:auto-scale: true
```

---

### 4. Python Package Manager: uv

**Research Evidence:**
- PULUMI-TRENDS-2025.md: uv integration announced Nov 2024
- Performance: 100x faster than pip (Rust-based)
- Official Pulumi support in runtime config

**Decision:** uv as primary package manager (fallback to pip)

**Benefits:**
- 100x faster package installation
- Single tool (replaces pip + pip-tools + virtualenv)
- Lockfile support (reproducible builds)
- Officially supported by Pulumi (Pulumi.yaml runtime.options.toolchain: uv)

**Setup:**
```bash
# Install uv
brew install uv

# Create venv
uv venv

# Install dependencies
uv pip install -r requirements.txt

# Pulumi automatically uses uv if available
```

**Fallback:** If uv causes issues, `requirements.txt` works with pip (zero changes needed)

---

### 5. Secrets Management: GCP Secret Manager

**Research Evidence:**
- PULUMI-TRENDS-2025.md: Pulumi ESC is GA but not required for single-cloud
- PULUMI-GCP-GUIDE.md: GCP Secret Manager native integration patterns
- PULUMI-BEST-PRACTICES.md: Start simple, add complexity when needed

**Decision:** GCP Secret Manager for runtime secrets, Pulumi config for deployment secrets

**Architecture:**
```
Deployment Secrets (Pulumi)          Runtime Secrets (GCP Secret Manager)
├── API keys (OpenAI, Anthropic)     ├── Database passwords
├── GCP service account keys         ├── JWT secret key
└── Temporal Cloud certificates      └── Third-party API tokens
```

**Benefits:**
- GCP-native (already using for runtime)
- Simple integration (no additional service)
- IAM-based access control
- Automatic encryption (KMS)
- Free tier: 10,000 secret versions

**Cost:** $0/month (free tier sufficient)

**Defer Pulumi ESC Until:**
- Multi-cloud deployment (AWS/Azure)
- >50 secrets to manage
- Need centralized secret management UI
- Team >10 people

---

### 6. CI/CD Platform: GitHub Actions

**Research Evidence:**
- PULUMI-TRENDS-2025.md: GitHub Actions is industry standard for Pulumi
- PULUMI-EXAMPLES.md: 80% of production repos use GitHub Actions
- Official Pulumi GitHub Action supports PR previews

**Decision:** GitHub Actions for CI/CD

**Workflow:**
```yaml
# .github/workflows/pulumi.yml
on:
  pull_request:
    paths:
      - 'deployment/pulumi/**'
  push:
    branches: [main]

jobs:
  preview:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: pulumi/actions@v4
        with:
          command: preview
          comment-on-pr: true  # Auto-comment on PR

  deploy-dev:
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: pulumi/actions@v4
        with:
          command: up
          stack-name: dev

  deploy-production:
    needs: deploy-dev
    environment: production  # Manual approval required
    runs-on: ubuntu-latest
    steps:
      - uses: pulumi/actions@v4
        with:
          command: up
          stack-name: production
```

**Benefits:**
- Free for public/private repos
- Excellent Pulumi integration (official action)
- PR preview comments (team visibility)
- Manual approval for production
- Secrets management (GitHub Secrets)

**Cost:** $0/month (free tier sufficient)

---

### 7. Testing Framework: pytest

**Research Evidence:**
- PULUMI-BEST-PRACTICES.md: Testing pyramid (60% unit, 30% property, 10% integration)
- PULUMI-FUNDAMENTALS.md: Python SDK provides test mocking helpers

**Decision:** pytest for all infrastructure tests

**Test Types:**

**1. Unit Tests (60%)** - Fast, mocked resources
```python
# tests/unit/test_networking.py
import pulumi
from modules.networking import create_vpc

@pulumi.runtime.test
def test_vpc_creation():
    def check_vpc(args):
        name, auto_create = args
        assert name == "apex-memory-vpc"
        assert auto_create is False

    pulumi.runtime.set_mocks(pulumi.runtime.Mocks())
    vpc = create_vpc(...)
    return pulumi.Output.all(vpc.name, vpc.auto_create_subnetworks).apply(check_vpc)
```

**2. Property Tests (30%)** - Policy validation (CrossGuard)
```python
# tests/policy/test_security.py
from pulumi_policy import PolicyPack, ResourceValidationPolicy

def cloud_sql_no_public_ip(args, report_violation):
    if args.resource_type == "gcp:sql/databaseInstance:DatabaseInstance":
        if args.props.get("settings", {}).get("ipConfiguration", {}).get("ipv4Enabled"):
            report_violation("Cloud SQL must not have public IP")

PolicyPack(
    name="security-policies",
    policies=[
        ResourceValidationPolicy("cloud-sql-no-public-ip", cloud_sql_no_public_ip),
    ],
)
```

**3. Integration Tests (10%)** - Real resources
```python
# tests/integration/test_database_cluster.py
import pulumi.automation as auto

def test_postgres_connectivity():
    stack = auto.create_or_select_stack(stack_name="test", work_dir=".")
    up_res = stack.up()

    # Test database connection
    assert can_connect_to_postgres(up_res.outputs["postgres_connection"])

    # Cleanup
    stack.destroy()
```

**Running Tests:**
```bash
pytest                       # All tests
pytest tests/unit/ -v        # Unit tests only (fast)
pytest tests/integration/    # Integration tests (slow, $$)
pytest --cov=modules         # Coverage report
```

**Benefits:**
- Same framework as application testing
- Pulumi provides mocking helpers
- Fast feedback (unit tests <1s)
- Catch errors before deployment

**Cost:** ~$5-10/month for integration test infrastructure (ephemeral resources)

---

### 8-15. Additional Decisions

(See Decision Matrix table above for quick reference)

---

## Implementation Checklist

Use this checklist as you implement the infrastructure:

### Pre-Implementation
- [ ] Review all 5 research guides (2-3 hours)
- [ ] Validate architectural decisions with team
- [ ] Complete prerequisites ([DEPLOYMENT-NEEDS.md](../DEPLOYMENT-NEEDS.md))
- [ ] Set up Pulumi Cloud account (free tier)
- [ ] Install uv package manager

### Week 1: Foundation
- [ ] Create `modules/networking.py`
- [ ] Create `modules/databases.py` (PostgreSQL only)
- [ ] Write 5 unit tests
- [ ] Deploy to dev stack
- [ ] Verify PostgreSQL connectivity

### Week 2: Multi-Database
- [ ] Add Neo4j to `modules/databases.py`
- [ ] Add Redis to `modules/databases.py`
- [ ] Write 4 unit tests
- [ ] Deploy to dev stack
- [ ] Verify all databases accessible

### Week 3: Cloud Run
- [ ] Create `modules/compute.py`
- [ ] Deploy API Gateway service
- [ ] Deploy Ingestion Worker service
- [ ] Write 6 unit tests
- [ ] Verify services connect to databases

### Week 4: Secrets & Qdrant
- [ ] Create `modules/secrets.py`
- [ ] Add Qdrant to `modules/compute.py`
- [ ] Migrate secrets to Secret Manager
- [ ] Write 5 unit tests
- [ ] Verify zero hardcoded secrets

### Week 5: Monitoring & CI/CD
- [ ] Create `modules/monitoring.py`
- [ ] Set up GitHub Actions workflow
- [ ] Complete test suite (30+ tests)
- [ ] Deploy to staging stack
- [ ] Verify monitoring dashboards

### Week 6: Production
- [ ] Deploy to production stack
- [ ] Run smoke tests
- [ ] Run load tests (10 concurrent users)
- [ ] Document rollback procedures
- [ ] Create operational runbooks

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| State file corruption | Low | High | Pulumi Cloud automatic backups, export state weekly |
| Cost overruns | Medium | Medium | Budget alerts at $700/month, auto-scaling caps |
| Deployment failures | Medium | Medium | Blue-green deployment, instant rollback via traffic shift |
| Secret exposure | Low | Critical | Never commit secrets, encrypted config, Secret Manager |
| Team knowledge gap | Medium | Low | Comprehensive documentation, 5 research guides |
| Vendor lock-in (Pulumi) | Low | Medium | Can export state and migrate to GCS backend |
| Python SDK limitations | Very Low | Low | Python SDK is first-class (2024-2025 validation) |

---

## Success Metrics

**Deployment Success:**
- [ ] All resources deployed successfully (0 failures)
- [ ] All tests passing (30+ unit, 5+ integration)
- [ ] API responds in <1s (P95 latency)
- [ ] Zero hardcoded secrets
- [ ] Monitoring dashboards displaying metrics

**Cost Success:**
- [ ] Monthly cost within budget ($411-807/month)
- [ ] Budget alerts configured
- [ ] Cost tracking by environment (dev/staging/prod)

**Team Success:**
- [ ] Team can deploy without Claude Code assistance
- [ ] Documentation complete and up-to-date
- [ ] Rollback procedures tested
- [ ] On-call runbooks created

---

## References

All decisions are based on comprehensive research:

1. **PULUMI-FUNDAMENTALS.md** - Core concepts, state management, Python SDK
2. **PULUMI-GCP-GUIDE.md** - GCP provider patterns, Cloud Run + Cloud SQL integration
3. **PULUMI-EXAMPLES.md** - Production code patterns, multi-database component
4. **PULUMI-BEST-PRACTICES.md** - Security, testing, deployment, cost optimization
5. **PULUMI-COMPARISON.md** - Pulumi vs Terraform, validation of choice
6. **PULUMI-TRENDS-2025.md** - Python SDK status, uv integration, GitHub Actions

**Total Research:** 50+ pages, 38+ sources, 2,000+ lines of code examples

---

## Next Steps

1. **Review this document** with team (1 hour)
2. **Make any final decision changes** (30 minutes)
3. **Begin Week 1 implementation** (20-24 hours)
4. **Follow 6-week roadmap** to production

**Questions?** Review research guides in `research/` directory or ask in team chat.

---

**Last Updated:** 2025-11-08
**Status:** ✅ Ready for Implementation
**Review Date:** Before Week 1 starts
