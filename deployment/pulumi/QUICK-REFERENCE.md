# Pulumi Quick Reference Card

**Last Updated:** 2025-11-08
**Status:** 🟢 Phase 0 Complete | 🔵 Week 1 Ready

---

## 📍 Current State

**✅ What We Have:**
- Pulumi CLI v3.206.0 installed
- gcloud CLI v546.0.0 installed
- Dev stack created: `apex-memory-dev`
- 13 GCP APIs enabled
- State managed via Pulumi Cloud

**🔵 What's Next:**
- Week 1: VPC + Cloud SQL (20-24 hours)
- See NEXT-STEPS.md for details

---

## 🚀 Quick Commands

### Daily Workflow

```bash
# Start session
cd deployment/pulumi
source .venv/bin/activate

# Check status
pulumi stack              # View current stack
pulumi stack output       # View all outputs

# Development cycle
pulumi preview            # Preview changes (dry run)
pulumi up                 # Deploy infrastructure
pulumi logs --follow      # View logs

# Testing
pytest tests/unit/ -v     # Unit tests (fast)
pytest tests/integration/ -v -m integration  # Integration tests (slow)

# Cleanup
pulumi destroy            # Tear down infrastructure (careful!)
```

### Stack Management

```bash
# List stacks
pulumi stack ls

# Switch stacks
pulumi stack select dev
pulumi stack select staging
pulumi stack select production

# Create new stack
pulumi stack init <name>
```

### Configuration

```bash
# View config
pulumi config

# Set config (plain text)
pulumi config set <key> <value>

# Set config (encrypted)
pulumi config set --secret <key> <value>

# Get config
pulumi config get <key>
pulumi config get --show-secrets <key>
```

---

## 📂 Project Structure

```
deployment/pulumi/
├── __main__.py              # Main infrastructure code
├── Pulumi.yaml              # Project config
├── requirements.txt         # Python dependencies
├── .venv/                   # Virtual environment
│
├── modules/                 # Infrastructure modules
│   ├── networking.py        # VPC, subnets, NAT
│   ├── databases.py         # PostgreSQL, Neo4j, Redis
│   ├── compute.py           # Cloud Run services
│   ├── secrets.py           # Secret Manager
│   └── monitoring.py        # Monitoring, dashboards
│
├── tests/                   # Infrastructure tests
│   ├── unit/                # Unit tests (mocked)
│   └── integration/         # Integration tests (real)
│
├── research/                # Research docs (50+ pages)
│   ├── PULUMI-FUNDAMENTALS.md
│   ├── PULUMI-GCP-GUIDE.md
│   └── ...
│
└── docs/                    # Session docs
    ├── README.md            # Master guide
    ├── NEXT-STEPS.md        # Week 1 implementation guide
    ├── SESSION-2025-11-08.md  # Session summary
    └── QUICK-REFERENCE.md   # This file
```

---

## 🎯 6-Week Roadmap

| Week | Goal | Hours | Status |
|------|------|-------|--------|
| **0** | Setup + Research | 4 | ✅ Complete |
| **1** | VPC + Cloud SQL | 20-24 | 🔵 Next |
| **2** | Neo4j + Redis | 16-20 | 📝 Planned |
| **3** | Cloud Run Services | 20-24 | 📝 Planned |
| **4** | Qdrant + Secrets | 16-20 | 📝 Planned |
| **5** | Monitoring + Tests | 20-24 | 📝 Planned |
| **6** | Production Deploy | 16-20 | 📝 Planned |

**Total:** 112-136 hours (6 weeks)

---

## 📚 Documentation Map

**Planning & Overview:**
- README.md - Master guide (743 lines)
- ARCHITECTURE-DECISIONS.md - Decision matrix
- NEXT-STEPS.md - Week 1 implementation guide

**Installation:**
- INSTALLATION.md - Complete installation guide (653 lines)
- check-installation.sh - Verification script
- install-missing-tools.sh - Installation script

**Research:**
- PULUMI-FUNDAMENTALS.md - Core concepts (900+ lines)
- PULUMI-GCP-GUIDE.md - GCP patterns (1,100+ lines)
- PULUMI-EXAMPLES.md - Code examples (8,500+ words)
- PULUMI-BEST-PRACTICES.md - Production patterns
- PULUMI-COMPARISON.md - vs Terraform (38 sources)
- PULUMI-TRENDS-2025.md - Current trends (12,000+ words)

**Session Notes:**
- SESSION-2025-11-08.md - Complete session summary
- QUICK-REFERENCE.md - This file

---

## 🔑 Key Concepts

**Pulumi Basics:**
- **Stack:** Environment (dev/staging/prod)
- **Resource:** GCP infrastructure (VPC, Cloud SQL, etc.)
- **Output:** Exported values (IPs, connection strings)
- **Config:** Stack-specific settings
- **State:** Infrastructure state (managed by Pulumi Cloud)

**GCP Resources:**
- **VPC:** Virtual Private Cloud network
- **Cloud SQL:** Managed PostgreSQL
- **Cloud Run:** Serverless containers
- **Secret Manager:** Centralized secrets
- **Compute Engine:** Virtual machines (for Neo4j)

**Module Pattern:**
- Each module exports a function
- Function returns dict of resources
- Main file imports and calls modules
- Promotes reusability and testing

---

## 🛠️ Common Tasks

### Add New Resource

```python
# In appropriate module file
new_resource = gcp.compute.Instance(
    "my-instance",
    machine_type="e2-micro",
    zone="us-central1-a",
    # ... other config ...
)

return {
    # ... existing resources ...
    "new_resource": new_resource,
}
```

### Export Output

```python
# In __main__.py
pulumi.export("output_name", resource.property)

# View outputs
pulumi stack output
pulumi stack output output_name
```

### Update Configuration

```bash
# Set non-secret config
pulumi config set database-tier db-f1-micro

# Set secret config
pulumi config set --secret postgres-password <password>

# Use in code
config = pulumi.Config()
db_tier = config.get("database-tier") or "db-f1-micro"
db_password = config.require_secret("postgres-password")
```

### Run Tests

```bash
# Unit tests (fast, mocked)
pytest tests/unit/ -v

# Integration tests (slow, real resources)
pytest tests/integration/ -v -m integration

# Specific test file
pytest tests/unit/test_networking.py -v

# With coverage
pytest --cov=modules --cov-report=html
```

---

## 📊 Cost Estimate

**Dev Stack (current):**
- API enablement: $0/month
- VPC networking: $0/month (basic)
- Cloud SQL (db-f1-micro): $7-15/month
- **Total:** ~$10-20/month

**Production Stack (Week 6):**
- VPC + Load Balancer: $30-50/month
- Cloud SQL (db-n1-standard-1): $80-120/month
- Neo4j (e2-small): $25-40/month
- Redis (1GB Basic): $40-60/month
- Qdrant (Cloud Run): $20-40/month
- Cloud Run (API + Workers): $50-150/month
- Temporal Cloud: $100-150/month
- Grafana Cloud: $19/month
- **Total:** $411-807/month

**With GCP $300 credit:** $149-249/month for first 90 days

---

## 🔗 Important Links

**Pulumi Cloud:**
- Dashboard: https://app.pulumi.com/rglaubitz-org
- Current stack: https://app.pulumi.com/rglaubitz-org/apex-memory-infrastructure/dev

**Official Docs:**
- Pulumi: https://www.pulumi.com/docs/
- Pulumi GCP: https://www.pulumi.com/registry/packages/gcp/
- GCP: https://cloud.google.com/docs

**GCP Console:**
- Project: https://console.cloud.google.com/home/dashboard?project=apex-memory-dev
- APIs: https://console.cloud.google.com/apis/dashboard?project=apex-memory-dev

---

## 🆘 Troubleshooting

**Issue: `pulumi up` fails**
```bash
# View detailed error
pulumi up --debug

# Refresh state
pulumi refresh

# Cancel pending operations
pulumi cancel
```

**Issue: Resource stuck in creating state**
```bash
# Check GCP console for actual status
# May need to import existing resource
pulumi import <resource-type> <resource-name> <resource-id>
```

**Issue: Config not found**
```bash
# Ensure correct stack selected
pulumi stack select dev

# List all config
pulumi config

# Set missing config
pulumi config set <key> <value>
```

**Issue: Authentication expired**
```bash
# Re-authenticate GCP
gcloud auth login
gcloud auth application-default login

# Re-authenticate Pulumi
pulumi login
```

---

## 💡 Pro Tips

**Speed up development:**
- Use `pulumi preview` frequently (free, instant)
- Test modules independently before integrating
- Use `pulumi.Output.all()` for complex dependencies
- Export everything you might need later

**Save money:**
- Destroy dev stack when not using: `pulumi destroy`
- Use smallest instance sizes for dev (db-f1-micro, e2-micro)
- Set `min_instances: 0` for Cloud Run in dev
- Monitor costs in GCP console

**Avoid mistakes:**
- Never use `--yes` flag in production
- Always review `pulumi preview` before `pulumi up`
- Use secrets for sensitive data: `--secret` flag
- Test rollback procedures before production deployment

**Maintain quality:**
- Write tests for every module
- Document all architecture decisions
- Keep README.md updated with progress
- Create session summaries for continuity

---

## 🎯 Next Session

**Start here:**
```bash
cd deployment/pulumi
source .venv/bin/activate
pulumi stack
cat NEXT-STEPS.md  # Read Week 1 implementation guide
```

**Week 1 Goal:** VPC + Cloud SQL PostgreSQL (20-24 hours)

**See NEXT-STEPS.md for complete implementation guide.**

---

**Last Updated:** 2025-11-08
**Pulumi Version:** v3.206.0
**GCP Project:** apex-memory-dev
**Stack:** dev
