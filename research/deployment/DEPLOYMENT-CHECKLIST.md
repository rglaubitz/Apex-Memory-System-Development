# Apex Memory System - Production Deployment Checklist

**Purpose:** Complete checklist of accounts, credentials, and prerequisites needed before deploying to production.

**Timeline:** ~2-4 hours to complete all signups and obtain necessary credentials.

**Budget:** $500-$1,500/month operational costs (detailed breakdown below)

---

## Quick Start Summary

**What You'll Need:**
- [ ] GCP account with billing enabled (~$720-950/month)
- [ ] Temporal Cloud account (~$100-150/month)
- [ ] OpenAI API key (existing - for embeddings)
- [ ] Domain name (optional, ~$12/year)
- [ ] Git provider account (GitHub recommended - free)

**Time Investment:**
- Account setup: 1-2 hours
- Initial deployment: 4-6 hours
- Testing & validation: 2-4 hours

---

## Phase 0: Prerequisites Checklist

### 0.1 Development Environment ✅ (Already Have)

- [x] Local development environment working
- [x] Docker installed and running
- [x] Git repository initialized
- [x] All 156 tests passing locally
- [x] Temporal workflows tested locally

### 0.2 Knowledge Prerequisites 📚

**Recommended Reading (2-3 hours):**
- [ ] GCP Fundamentals: https://cloud.google.com/docs/overview
- [ ] Cloud SQL basics: https://cloud.google.com/sql/docs
- [ ] Temporal Cloud intro: https://docs.temporal.io/cloud
- [ ] Cloud Build basics: https://cloud.google.com/build/docs

**Optional But Helpful:**
- [ ] Terraform basics: https://developer.hashicorp.com/terraform/tutorials/gcp-get-started
- [ ] Docker multi-stage builds: https://docs.docker.com/build/building/multi-stage/

---

## Phase 1: Account Setup

### 1.1 Google Cloud Platform (GCP) Account

**Priority:** 🔴 CRITICAL - Required for all infrastructure

**Steps:**
1. **Sign up:** https://console.cloud.google.com/
   - Use personal Gmail or create new business email
   - Free tier includes $300 credit (90 days)
   - No charges during free trial

2. **Enable billing:**
   - Add credit card (required, not charged during trial)
   - Set up billing account
   - **IMPORTANT:** Set budget alerts (see section 1.8)

3. **Create project:**
   - Project name: `apex-memory-prod`
   - Project ID: `apex-memory-prod-[RANDOM]` (must be globally unique)
   - Note the Project ID - you'll use this everywhere

4. **Enable required APIs:**
   ```bash
   gcloud services enable compute.googleapis.com
   gcloud services enable sqladmin.googleapis.com
   gcloud services enable run.googleapis.com
   gcloud services enable redis.googleapis.com
   gcloud services enable secretmanager.googleapis.com
   gcloud services enable cloudbuild.googleapis.com
   gcloud services enable monitoring.googleapis.com
   ```

**Cost:**
- Free tier: $300 credit (90 days)
- After trial: ~$720-950/month (see detailed breakdown section 2)

**Validation:**
```bash
# Install gcloud CLI
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Initialize and authenticate
gcloud init
gcloud auth login
gcloud config set project apex-memory-prod-[YOUR-ID]

# Verify APIs enabled
gcloud services list --enabled
```

**Resources:**
- GCP Console: https://console.cloud.google.com/
- Documentation: https://cloud.google.com/docs
- Pricing Calculator: https://cloud.google.com/products/calculator

---

### 1.2 Temporal Cloud Account

**Priority:** 🔴 CRITICAL - Required for workflow orchestration

**Steps:**
1. **Sign up:** https://cloud.temporal.io/
   - Use same email as GCP
   - Free trial available
   - No credit card required for trial

2. **Create namespace:**
   - Namespace name: `apex-memory-prod`
   - Region: `us-east-1` or `us-west-2` (choose closest to GCP region)
   - Retention: 7 days (free tier) or 30 days (paid)

3. **Get connection details:**
   - Namespace URL: `apex-memory-prod.abc123.tmprl.cloud:7233`
   - Download certificates (for mTLS authentication)
   - Save certificate files securely

4. **Create API key** (optional, for CI/CD):
   - Navigate to Settings → API Keys
   - Create new API key
   - Save key securely (can't retrieve later)

**Cost:**
- Free trial: 14 days
- Essentials plan: ~$100-150/month for your workload
  - 1M actions included
  - Additional: $50/million actions
  - Storage: ~$15-30/month

**Validation:**
```bash
# Test connection (after getting certificates)
tctl --namespace apex-memory-prod namespace describe
```

**Resources:**
- Temporal Cloud Console: https://cloud.temporal.io/
- Documentation: https://docs.temporal.io/cloud
- Pricing: https://temporal.io/pricing

**Alternative:** Self-hosted Temporal (cost: $0, complexity: HIGH)
- Not recommended for first deployment
- Requires Kubernetes expertise
- Consider after 6-12 months if cost becomes issue

---

### 1.3 GitHub Account (for CI/CD)

**Priority:** 🟡 HIGH - Required for automated deployments

**Steps:**
1. **Sign up:** https://github.com/ (if you don't have)
   - Free tier sufficient

2. **Create repository:**
   - Repository name: `apex-memory-system`
   - Private or Public (your choice)
   - Initialize with README

3. **Push your code:**
   ```bash
   git remote add origin https://github.com/[USERNAME]/apex-memory-system.git
   git push -u origin main
   ```

4. **Create Personal Access Token** (for Cloud Build):
   - Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Select scopes: `repo` (all), `admin:repo_hook`
   - Save token securely

**Cost:** Free (for private repos up to 2,000 CI/CD minutes/month)

**Validation:**
```bash
git push origin main  # Should succeed
```

**Alternative:** GitLab or Bitbucket (supported by Cloud Build)

---

### 1.4 OpenAI API Access

**Priority:** 🔴 CRITICAL - Required for embeddings

**Steps:**
1. **Already have:** ✅ (confirmed from your setup)
2. **Verify quota:**
   - Check usage: https://platform.openai.com/usage
   - Recommended tier: Pay-as-you-go (Tier 2+)
   - Rate limit needed: 100 RPM (requests per minute)

3. **Cost estimation:**
   - Embedding model: `text-embedding-3-small`
   - Cost: $0.02 per 1M tokens
   - Your workload: ~1,000 docs/day = 50M tokens/month ≈ $1/month

4. **Rotate key for production:**
   - Create new API key specifically for production
   - Name: "apex-memory-production"
   - Save in GCP Secret Manager (don't use .env in prod)

**Cost:** ~$1-5/month (embedding costs)

**Validation:**
```bash
# Test API key
curl https://api.openai.com/v1/embeddings \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "test",
    "model": "text-embedding-3-small"
  }'
```

---

### 1.5 Domain Name (Optional But Recommended)

**Priority:** 🟢 OPTIONAL - Improves production polish

**Steps:**
1. **Purchase domain:**
   - Registrar: Google Domains, Namecheap, Cloudflare
   - Example: `apexmemory.com` or `[yourname]-apex.com`
   - Cost: $10-15/year

2. **DNS configuration:**
   - Point A record to Cloud Run IP (after deployment)
   - Configure SSL certificate (Cloud Run handles automatically)

**Cost:** $10-15/year

**Alternative:** Use Cloud Run default URL
- Format: `https://apex-memory-[hash]-uc.a.run.app`
- Works fine, just less professional

---

### 1.6 Monitoring & Observability

**Priority:** 🟡 HIGH - Critical for production operations

**Option A: GCP Cloud Monitoring (Recommended for Budget)**
- **Cost:** Included in GCP (first 150MB logs/month free)
- **Pros:** Native integration, simple setup
- **Cons:** Basic dashboards, limited alerting

**Option B: Grafana Cloud (Better Dashboards)**
- **Sign up:** https://grafana.com/
- **Free tier:** 10K metrics, 50GB logs, 14-day retention
- **Cost:** Free tier likely sufficient, paid $29/month if needed
- **Pros:** Beautiful dashboards, better alerting
- **Cons:** Extra integration work

**Recommendation:** Start with GCP Cloud Monitoring (included), upgrade to Grafana Cloud if needed.

**Steps (GCP Cloud Monitoring):**
1. Already enabled with GCP project
2. No additional setup required
3. Access: https://console.cloud.google.com/monitoring

**Steps (Grafana Cloud - if chosen):**
1. Sign up: https://grafana.com/auth/sign-up
2. Create stack (free tier)
3. Get Prometheus endpoint and API key
4. Configure in application (see UPDATE-WORKFLOW.md)

---

### 1.7 Email/Alerting (For Production Incidents)

**Priority:** 🟡 HIGH - You need to know when things break

**Options:**

**Option A: Email Alerts (Free, Simple)**
- Use your existing email
- Configure in GCP Alerting Policies
- **Pros:** Free, immediate
- **Cons:** Can get noisy, no on-call management

**Option B: PagerDuty (Recommended for Serious Production)**
- **Sign up:** https://www.pagerduty.com/
- **Free tier:** 1 user, limited integrations
- **Paid:** $19/month for Professional tier
- **Pros:** Proper incident management, escalation policies, mobile app
- **Cons:** Additional cost

**Option C: Slack Integration (Middle Ground)**
- **Free:** Use existing Slack workspace
- **Setup:** GCP → Pub/Sub → Slack webhook
- **Pros:** Team visibility, free
- **Cons:** Not designed for critical alerts

**Recommendation:** Start with Email (free), upgrade to PagerDuty after first month if needed.

---

### 1.8 Budget Alerts (CRITICAL - Protect Yourself)

**Priority:** 🔴 CRITICAL - Prevent unexpected bills

**Steps:**
1. **Navigate to:** https://console.cloud.google.com/billing/budgets
2. **Create budget:**
   - Name: "Apex Memory Production Budget"
   - Amount: $1,500/month (your max budget)
   - Alerts at: 50%, 80%, 90%, 100%
   - Send to: Your email

3. **Set up quota monitoring:**
   - Monitor: Cloud SQL, Cloud Run, Compute Engine
   - Alert if approaching limits

4. **Enable cost breakdown:**
   - Export billing to BigQuery (for detailed analysis)
   - Optional: Set up cost anomaly detection

**Validation:**
- You'll receive test email confirming budget alert setup

**IMPORTANT:** GCP can exceed budget limits. Budget alerts don't stop spending, they only notify you. Monitor weekly!

---

## Phase 2: Cost Breakdown & Budget Planning

### 2.1 Estimated Monthly Costs (Production)

**Total: $720-950/month (well within $1,500 budget)**

| Service | Spec | Monthly Cost | Notes |
|---------|------|--------------|-------|
| **Cloud SQL (PostgreSQL)** | db-n1-standard-2 (2 vCPU, 7.5GB RAM) | $250-350 | Managed PostgreSQL + pgvector |
| **Memorystore Redis** | Basic tier, 1GB | $50-80 | Managed Redis cache |
| **Compute Engine (Neo4j)** | e2-medium (2 vCPU, 4GB RAM) | $70-90 | Self-hosted Neo4j VM |
| **Cloud Run (Qdrant)** | 1 vCPU, 2GB RAM | $40-60 | Containerized vector DB |
| **Cloud Run (FastAPI)** | 1 vCPU, 2GB RAM, autoscale 0-3 | $50-80 | Main application |
| **Temporal Cloud** | Essentials tier | $100-150 | Workflow orchestration |
| **Cloud Storage** | 50GB standard class | $1-2 | Document storage, backups |
| **Cloud Build** | Free tier (120 min/day) | $0-10 | CI/CD (rarely exceeds free tier) |
| **Networking** | Data egress, Load Balancer | $30-50 | Network costs |
| **Cloud Monitoring** | Logs, metrics (under free tier) | $0-20 | Observability |
| **Cloud Secret Manager** | ~20 secrets | $1-2 | Secrets storage |
| **Misc** | IPs, snapshots, etc. | $10-30 | Miscellaneous |

**Free Tier Benefits (First 90 Days):**
- $300 GCP credit
- Effectively free for first 3 months
- Use time to validate product-market fit

**Scaling Costs:**
- At 10x traffic: ~$2,500-3,500/month
- At 100x traffic: ~$8,000-15,000/month (need architecture changes)

---

### 2.2 Cost Optimization Opportunities

**Immediate Savings (Do on Day 1):**
1. **Use Committed Use Discounts (CUDs):**
   - Save 37% on Cloud SQL (1-year commit)
   - Save 55% on Compute Engine (1-year commit)
   - Recommendation: Wait 1 month to validate workload, then commit

2. **Rightsize instances:**
   - Start with smaller instances
   - Monitor for 1 week
   - Scale up if needed (scale down harder)

3. **Enable autoscaling:**
   - Cloud Run: Scale to zero when idle
   - Cloud SQL: Use read replicas only when needed

4. **Use cheaper storage classes:**
   - Nearline storage for old documents (>30 days)
   - Archive storage for backups

**After 3 Months:**
- Re-evaluate Temporal Cloud vs self-hosted
  - Break-even point: ~$200/month (if you have K8s expertise)
  - Your workload: Not worth self-hosting (complexity >> savings)

---

### 2.3 Free Tier Maximization

**GCP Free Tier (Always Free):**
- Cloud Functions: 2M invocations/month
- Cloud Storage: 5GB standard storage
- Cloud Build: 120 build-minutes/day
- Cloud Monitoring: 150MB logs/month
- Pub/Sub: 10GB messages/month

**Recommendations:**
- Use Cloud Functions for async tasks (ingestion triggers)
- Keep CI/CD under 120 min/day (optimize build times)
- Aggregate logs before sending to monitoring

**Temporal Cloud Free Trial:**
- 14 days free
- After trial: $100-150/month (no free tier)
- Worth it for simplicity (don't self-host to save money)

---

## Phase 3: Credentials & Secrets Inventory

### 3.1 Required Credentials Checklist

**Collect These Before Deployment:**

- [ ] **GCP Project ID:** `apex-memory-prod-[RANDOM]`
- [ ] **GCP Service Account Key:** (JSON file, for Terraform)
- [ ] **Temporal Namespace:** `apex-memory-prod`
- [ ] **Temporal Certificates:** `client.pem`, `client.key`, `ca.pem`
- [ ] **OpenAI API Key:** `sk-proj-...` (production key)
- [ ] **GitHub Personal Access Token:** `ghp_...` (for Cloud Build)
- [ ] **PostgreSQL Password:** (will be generated during setup)
- [ ] **Neo4j Password:** (will be set during setup)
- [ ] **Redis Password:** (optional, auto-generated if enabled)

**Storage Location:**
- **Development:** `.env` file (gitignored)
- **Production:** GCP Secret Manager (NEVER in git, NEVER in env vars)

---

### 3.2 Secrets Setup (GCP Secret Manager)

**Create these secrets BEFORE first deployment:**

```bash
# Authenticate
gcloud auth login
gcloud config set project apex-memory-prod-[YOUR-ID]

# Create secrets
echo -n "YOUR_OPENAI_KEY" | gcloud secrets create openai-api-key --data-file=-
echo -n "YOUR_POSTGRES_PASSWORD" | gcloud secrets create postgres-password --data-file=-
echo -n "YOUR_NEO4J_PASSWORD" | gcloud secrets create neo4j-password --data-file=-

# Upload Temporal certificates
gcloud secrets create temporal-client-cert --data-file=client.pem
gcloud secrets create temporal-client-key --data-file=client.key

# Grant Cloud Run access to secrets
gcloud secrets add-iam-policy-binding openai-api-key \
  --member=serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com \
  --role=roles/secretmanager.secretAccessor
```

**Validation:**
```bash
# List secrets
gcloud secrets list

# Test access
gcloud secrets versions access latest --secret=openai-api-key
```

---

## Phase 4: Pre-Deployment Validation

### 4.1 Local Testing (Run Before Deploying)

**All tests must pass:**
```bash
cd apex-memory-system

# Unit tests
pytest tests/unit/ -v
# Expected: 40/40 passing

# Integration tests
pytest tests/integration/ -v
# Expected: 70/70 passing

# Load tests (mocked DBs)
pytest tests/load/ -v -m load
# Expected: 10/10 passing

# Total: 156/156 tests passing
```

**If any tests fail:** Do NOT deploy. Fix locally first.

---

### 4.2 Temporal Workflow Validation

**Test Temporal workflows locally:**
```bash
# Start local Temporal server
docker compose -f docker/docker-compose.temporal.yml up -d

# Run temporal integration tests
pytest tests/integration/test_temporal_ingestion_workflow.py -v

# Expected: All workflows complete successfully
```

**Validation criteria:**
- Workflows complete (no timeouts)
- Activities execute correctly
- Compensation logic works (test failure scenarios)
- Metrics collected (check Prometheus)

---

### 4.3 Docker Build Validation

**Build production Docker images:**
```bash
# FastAPI application
docker build -t apex-memory-api:test -f Dockerfile .

# Run locally
docker run -p 8000:8000 apex-memory-api:test

# Test health endpoint
curl http://localhost:8000/health
# Expected: {"status": "healthy"}
```

**Check image size:**
```bash
docker images apex-memory-api:test
# Expected: <500MB (if larger, optimize Dockerfile)
```

---

## Phase 5: Deployment Readiness Checklist

### 5.1 Final Pre-Flight Checklist

**Before running first deployment:**

- [ ] All GCP APIs enabled
- [ ] Billing enabled with budget alerts
- [ ] Temporal Cloud namespace created
- [ ] All secrets stored in Secret Manager
- [ ] GitHub repository set up
- [ ] 156/156 tests passing locally
- [ ] Docker images build successfully
- [ ] Domain name purchased (optional)
- [ ] Monitoring configured
- [ ] Cost estimates reviewed and accepted
- [ ] Backup plan documented (see UPDATE-WORKFLOW.md)
- [ ] Rollback procedure understood

---

### 5.2 Go/No-Go Decision Criteria

**GO if:**
- ✅ All above checklist items complete
- ✅ Budget approved ($720-950/month)
- ✅ Free trial credits active (or billing enabled)
- ✅ Tests passing (156/156)
- ✅ Comfortable with rollback plan

**NO-GO if:**
- ❌ Budget uncertainty
- ❌ Tests failing (>5% failure rate)
- ❌ Missing critical credentials
- ❌ Haven't read deployment guide
- ❌ No monitoring plan

---

## Phase 6: Estimated Timeline

### 6.1 First-Time Deployment Schedule

**Week 1: Setup (6-10 hours)**
- Day 1-2: Account creation (2 hours)
- Day 3-4: Secrets setup (2 hours)
- Day 5: Local validation (2-3 hours)
- Day 6-7: Review documentation (2-3 hours)

**Week 2: Initial Deployment (8-12 hours)**
- Day 1-2: Database deployment (4-6 hours)
- Day 3: Application deployment (2-3 hours)
- Day 4: Testing & validation (2-3 hours)
- Day 5: Monitoring setup (1-2 hours)

**Week 3: Validation & Optimization (4-6 hours)**
- Day 1-3: Production soak testing (24-48 hours)
- Day 4: Cost optimization review
- Day 5: Documentation updates

**Week 4: Production Release (2-4 hours)**
- Day 1: Final validation
- Day 2: Go-live
- Day 3-7: Monitoring & iteration

**Total Time Investment:** 20-32 hours over 4 weeks

---

## Quick Reference: All Account Links

**Primary Services:**
- GCP Console: https://console.cloud.google.com/
- Temporal Cloud: https://cloud.temporal.io/
- OpenAI Platform: https://platform.openai.com/
- GitHub: https://github.com/

**Monitoring:**
- GCP Monitoring: https://console.cloud.google.com/monitoring
- GCP Logging: https://console.cloud.google.com/logs

**Billing:**
- GCP Billing: https://console.cloud.google.com/billing
- Budget Alerts: https://console.cloud.google.com/billing/budgets

**Documentation:**
- GCP Docs: https://cloud.google.com/docs
- Temporal Docs: https://docs.temporal.io/
- Cloud SQL Docs: https://cloud.google.com/sql/docs

---

## Next Steps

After completing this checklist:

1. **Read next:** `GCP-DEPLOYMENT-GUIDE.md` - Step-by-step deployment instructions
2. **Review:** `ARCHITECTURE.md` - Understand design decisions
3. **Prepare:** `SECRETS-MANAGEMENT.md` - Secure credentials handling

---

**Questions or Issues?**

- Check troubleshooting sections in deployment guide
- Review GCP documentation
- Consult Temporal community forum: https://community.temporal.io/

---

**Last Updated:** 2025-01-20
**Author:** Claude Code (Apex Memory System Deployment Documentation)
**Version:** 1.0.0
