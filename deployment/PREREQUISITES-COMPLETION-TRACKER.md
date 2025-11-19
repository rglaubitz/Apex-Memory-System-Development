# Prerequisites Completion Tracker

**Date Started:** 2025-11-15
**Estimated Time:** 4-6 hours
**Status:** 🟡 In Progress

**Purpose:** Track completion of all deployment prerequisites before starting Pulumi infrastructure build (Week 1).

**Reference:** Complete details in [DEPLOYMENT-NEEDS.md](DEPLOYMENT-NEEDS.md)

---

## 🎯 Quick Start

**⭐ NEW: Complete Prerequisites Summary Available!**

📂 **[PREREQUISITES-FINAL-SUMMARY.md](PREREQUISITES-FINAL-SUMMARY.md)** - Complete systematic execution plan with all guides

**All Setup Guides Created:**
- ✅ [ANTHROPIC-API-SETUP.md](ANTHROPIC-API-SETUP.md) - 10-15 min
- ✅ [GRAFANA-CLOUD-SETUP.md](GRAFANA-CLOUD-SETUP.md) - 30-40 min
- ✅ [PASSWORD-MANAGER-SETUP.md](PASSWORD-MANAGER-SETUP.md) - 15-20 min
- ✅ [2FA-ENABLEMENT-CHECKLIST.md](2FA-ENABLEMENT-CHECKLIST.md) - 30-40 min

**Follow the systematic plan in PREREQUISITES-FINAL-SUMMARY.md to complete all remaining prerequisites in ~1.5 hours.**

---

## Quick Status Overview

| Category | Status | Time Remaining |
|----------|--------|----------------|
| **Already Complete** | ✅ 40% | 0 min |
| **Cloud Services** | ✅ 100% (All complete!) | 0 min |
| **API Keys** | ✅ 100% (Both complete!) | 0 min |
| **Security & Secrets** | ✅ 100% (All stored in 1Password!) | 0 min |
| **Development Tools** | ✅ 100% | 0 min |
| **Accounts & 2FA** | ⏳ 0% | 30-40 min |
| **Overall Progress** | **80%** | **~30-40 min** |

---

## ✅ Already Complete (No Action Needed)

### GCP Infrastructure
- ✅ GCP Account created (`apex-memory-dev` project)
- ✅ GCP authenticated (`gcloud auth login` completed)
- ✅ gcloud CLI installed (v546.0.0)
- ✅ Pulumi CLI installed (v3.206.0)
- ✅ Pulumi authenticated (user: `rglaubitz`)
- ✅ Pulumi Phase 0 deployed (13 GCP APIs enabled)
- ✅ Python 3.14.0 + uv 0.8.12 installed

**Time Saved:** ~2 hours (this would normally take 90-120 minutes)

---

## 🟡 Partially Complete (Needs Verification)

### Docker Desktop
- ✅ Docker Desktop installed
- ⏳ **ACTION REQUIRED:** Verify licensing requirements

  **Check if Business license needed:**
  ```bash
  # Option 1: Check Docker Desktop
  # Docker Desktop → Settings → About → License Agreement

  # Option 2: Command line
  docker version
  # Look for "Docker Desktop" license info
  ```

  **Licensing Rules:**
  - ✅ **FREE if:** Personal use OR company <250 employees OR revenue <$10M
  - ⚠️ **Paid ($9/user/month) if:** Company 250+ employees AND revenue >$10M

  **Time:** 10 minutes

- [ ] **Docker licensing verified**

---

## ⏳ Critical Prerequisites (Must Complete)

### 1. Temporal Cloud (COMPLETE ✅)

**Why:** Workflow orchestration (already integrated into codebase)
**Cost:** $100-150/month (Essentials tier)
**Time Spent:** ~50 minutes

**What Was Completed:**
1. ✅ **Account Created** - Temporal Cloud account created
2. ✅ **Namespace Created** - `quickstart-apex-memory-prod.pnlwy` (us-east4 region)
3. ✅ **API Key Generated** - Using API key authentication (not mTLS)
4. ✅ **Temporal CLI Configured** - Successfully tested with `temporal --profile cloud workflow list`
5. ✅ **.env Updated** - Added Temporal Cloud configuration to apex-memory-system/.env
6. ✅ **Connection Verified** - CLI connection successful (Python SDK needs 1-2 min for API key to activate)

**Connection Details:**
```bash
Namespace: quickstart-apex-memory-prod.pnlwy
Address: us-east4.gcp.api.temporal.io:7233
Region: us-east4 (GCP)
Account ID: pnlwy
Task Queue: apex-ingestion-queue
Auth Method: API Key (easier than mTLS!)
```

**⚠️ CRITICAL Security Notes:**
- ⚠️ **API Key EXPOSED in screenshot** - MUST revoke and regenerate ASAP (within 24-48 hours)
- ⚠️ API Key expires: 2025-01-13 (regenerate before expiration)
- ✅ Using API key authentication (simpler than mTLS certificates)

**How to Revoke/Regenerate:**
1. Go to: https://cloud.temporal.io/settings/api-keys
2. Delete old API key
3. Generate new API key
4. Update .env with new key
5. Test connection: `temporal --profile cloud workflow list`

**Reference:** Complete setup guide at `deployment/TEMPORAL-CLOUD-COMPLETE-SETUP.md`

**Checklist:**
- [x] Temporal Cloud account created
- [x] Namespace created
- [x] API key generated
- [x] Temporal CLI configured
- [x] Connection tested successfully
- [x] .env file updated
- [ ] Credentials stored in password manager (NEXT STEP)
- [ ] Exposed API key revoked and new one generated (SECURITY - DO WITHIN 24-48 HRS)

---

### 2. Grafana Cloud Pro (30-40 minutes)

**Why:** Monitoring dashboards + Prometheus storage (27 Temporal metrics)
**Cost:** $19/month (Pro tier)

**Steps:**
1. **Create Account** (15 min)
   - Go to: https://grafana.com/auth/sign-up
   - Sign up with email
   - Choose "Cloud Pro" plan
   - Add payment method

2. **Create Prometheus Instance** (10 min)
   - Navigate to: Connections → Add data source → Prometheus
   - Note the Remote Write endpoint URL
   - Generate API key for Prometheus remote write

3. **Obtain Connection Details** (5 min)
   ```bash
   # Save these values:
   GRAFANA_CLOUD_PROMETHEUS_URL="https://prometheus-prod-xx-xxx-xxx.grafana.net/api/prom/push"
   GRAFANA_CLOUD_PROMETHEUS_USER="<instance-id>"
   GRAFANA_CLOUD_API_KEY="<generated-api-key>"
   ```

**Reference:** https://grafana.com/docs/grafana-cloud/

**Checklist:**
- [ ] Grafana Cloud account created
- [ ] Prometheus instance created
- [ ] API key generated
- [ ] Connection details stored in password manager

---

### 3. API Keys (20-30 minutes)

**Why:** Embeddings, LLM classification, entity extraction
**Cost:** $40-110/month (usage-based)

#### OpenAI API Key
**Purpose:**
- Text embeddings (text-embedding-3-small) - $0.00013/1K tokens
- Graphiti entity extraction (90%+ accuracy)
- GPT-5 Nano for conversation processing (optional)

**Steps:**
1. **Obtain API Key** (10 min)
   - Go to: https://platform.openai.com/api-keys
   - Sign in or create account
   - Click "Create new secret key"
   - Copy key (starts with `sk-...`)
   - **⚠️ WARNING:** Key only shown once - copy immediately

2. **Add Payment Method** (5 min)
   - Navigate to: Billing → Payment methods
   - Add credit card
   - Set usage limits: $50/month (recommended)

**Checklist:**
- [ ] OpenAI account created
- [ ] API key generated and stored in password manager
- [ ] Payment method added
- [ ] Usage limits set

#### Anthropic API Key ✅ COMPLETE
**Purpose:**
- Claude for query rewriting, chat, LLM classification
- Alternative to OpenAI for Graphiti (can use either)

**✅ Status:** API key obtained and tested successfully!

**API Key:** `<YOUR_ANTHROPIC_API_KEY>`

**Configured:**
- ✅ .env file updated with ANTHROPIC_API_KEY
- ✅ Default model: claude-3-haiku-20240307
- ✅ API key tested and working (response received)

**⚠️ Remaining Tasks:**
- [ ] Add payment method in Anthropic console
- [ ] Set $50/month usage limit
- [ ] Store API key in password manager (see PASSWORD-MANAGER-SETUP.md)

**Checklist:**
- [x] Anthropic account created
- [x] API key generated
- [x] API key added to .env
- [x] API key tested successfully
- [ ] Payment method added (do this soon!)
- [ ] Usage limits set ($50/month)
- [ ] Stored in password manager

---

### 4. Security & Secrets (30-45 minutes)

**Why:** Secure application secrets, JWT signing, database passwords

#### Generate SECRET_KEY (5 min)
```bash
# Generate cryptographically secure secret (32 bytes, base64-encoded)
openssl rand -base64 32

# Example output: Xg8K7n3mPz2vQ9wR5jL1dT6hS4bN8cM0fV7yU2xA1e=
```

**Checklist:**
- [ ] SECRET_KEY generated
- [ ] Stored in password manager

#### Generate Database Passwords (10 min)
```bash
# PostgreSQL password
openssl rand -base64 24
# Example: rK9mN3pL7jQ2wV5xS8cT4bH6fY1

# Neo4j password
openssl rand -base64 24
# Example: tB2nM9pJ4qW8xL1cH5vS7rF3kY6

# Redis password (optional, Redis can run without auth in private network)
openssl rand -base64 24
# Example: jH4mP7qN2wX9kL5cT8vB1rF6sY3
```

**Checklist:**
- [ ] PostgreSQL password generated and stored
- [ ] Neo4j password generated and stored
- [ ] Redis password generated (optional) and stored

#### Setup Password Manager (15 min)

**Recommended: Bitwarden (FREE)**
```bash
# Option 1: Install Bitwarden CLI
brew install bitwarden-cli

# Option 2: Use Bitwarden web vault
# https://vault.bitwarden.com/
```

**Alternative: 1Password ($4.99/month)**
- https://1password.com/

**Alternative: pass (FREE, GPG-based, macOS/Linux)**
```bash
# Install pass
brew install pass

# Initialize (requires GPG key)
pass init <gpg-key-id>
```

**Items to Store:**
1. Temporal Cloud mTLS certificates
2. Grafana Cloud API keys
3. OpenAI API key
4. Anthropic API key
5. SECRET_KEY
6. PostgreSQL password
7. Neo4j password
8. Redis password (optional)
9. GCP service account keys (future)

**Checklist:**
- [ ] Password manager installed
- [ ] All secrets stored securely
- [ ] Backup/recovery configured

#### Enable 2FA on All Accounts (10 min)

**Accounts requiring 2FA:**
1. GCP account
2. GitHub account
3. OpenAI account
4. Anthropic account
5. Temporal Cloud account
6. Grafana Cloud account
7. Password manager account

**Checklist:**
- [ ] GCP 2FA enabled
- [ ] GitHub 2FA enabled
- [ ] OpenAI 2FA enabled
- [ ] Anthropic 2FA enabled
- [ ] Temporal Cloud 2FA enabled
- [ ] Grafana Cloud 2FA enabled
- [ ] Password manager 2FA enabled

---

## 🔵 Optional Prerequisites (Can Skip for Now)

### Google Drive Integration (45 minutes)
- **Status:** Optional (can deploy after initial production launch)
- **Cost:** FREE (Google Drive API) + $5-15/month (GCS archival)
- **When to do:** After Week 3-4 deployment, if needed
- **Guide:** `deployment/components/google-drive-integration/DEPLOYMENT-GUIDE.md`

### NATS Messaging (30-45 minutes)
- **Status:** Optional (verify usage first)
- **Cost:** $0/month (self-hosted) or $15-50/month (managed)
- **When to do:** Only if actively used in production code (verify first)
- **Guide:** `deployment/components/nats-messaging/DEPLOYMENT-GUIDE.md`

### Domain Name ($12-15/year)
- **Status:** Optional (Cloud Run provides auto-generated URL)
- **When to do:** After initial production deployment (Week 4-5)
- **Providers:** Cloudflare, Namecheap, Google Domains

---

## 📋 Final Verification Checklist

Before proceeding to Pulumi Week 1, verify ALL of the following:

### Critical (Must Have)
- [ ] GCP account with billing enabled
- [ ] Temporal Cloud namespace created with mTLS certs
- [ ] Grafana Cloud Pro instance created with API keys
- [ ] OpenAI API key obtained and stored
- [ ] Anthropic API key obtained and stored
- [ ] SECRET_KEY generated and stored
- [ ] Database passwords generated and stored
- [ ] All secrets stored in password manager
- [ ] 2FA enabled on all accounts

### Development Tools
- [ ] gcloud CLI installed and authenticated
- [ ] Pulumi CLI installed and authenticated
- [ ] Docker Desktop licensed correctly
- [ ] Python 3.11+ installed
- [ ] uv package manager installed

### Security
- [ ] Password manager configured
- [ ] All API keys have usage limits set
- [ ] GCP budget alerts configured ($700/month threshold)
- [ ] All secrets backed up

---

## 🎯 Ready for Next Step

Once ALL critical items are checked, you're ready to proceed to:

**Pulumi Week 1: Networking + Cloud SQL** (20-24 hours)
- `deployment/pulumi/README.md` - Full Pulumi guide
- Week 1 deliverables: VPC, Cloud SQL PostgreSQL, tests

**Or: Manual Deployment (Fast Track)** (16-24 hours)
- `deployment/production/GCP-DEPLOYMENT-GUIDE.md` - Step-by-step manual deployment

---

## 💰 Cost Tracking

**Monthly Costs After Prerequisites Complete:**

| Service | Cost |
|---------|------|
| GCP Services | $261-542/month (auto-scales) |
| Temporal Cloud | $100-150/month |
| Grafana Cloud | $19/month |
| OpenAI API | $10-30/month (usage-based) |
| Anthropic API | $20-50/month (usage-based) |
| Graphiti | Included in OpenAI costs |
| GCS Archival | $5-15/month (optional) |
| **TOTAL** | **$415-806/month** |

**First 90 Days (GCP $300 free credit):**
- **Out-of-pocket:** $154-264/month (Temporal + Grafana + APIs only)
- **After credit expires:** $415-806/month (full cost)

---

**Last Updated:** 2025-11-15
**Next Review:** After all critical prerequisites complete
