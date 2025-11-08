# Deployment Prerequisites - Complete Checklist

**Purpose:** Comprehensive list of everything you need to purchase, sign up for, or obtain before starting deployment.

**Status:** Use checkboxes to track progress as you obtain each item.

**Estimated Total Setup Time:** 4-6 hours (spread over 1-2 days for account approvals)

**Estimated Monthly Cost:** $411-793/month (starting at $149-249/month with GCP free credits)

---

## Quick Checklist

- [ ] All Cloud Services configured
- [ ] All API Keys obtained and stored securely
- [ ] Development Tools verified/upgraded
- [ ] Accounts & Credentials created
- [ ] Domain registered (optional for initial deployment)
- [ ] Payment methods configured
- [ ] Budget alerts set up

---

## 1. Cloud Services & Subscriptions

| Service | Cost | Purpose | Where to Get | Prerequisites | Time to Setup | Status |
|---------|------|---------|--------------|---------------|---------------|--------|
| **GCP Account** | $0 first 90 days ($300 credit)<br>Then $261-542/month | Cloud hosting (Cloud Run, Cloud SQL, Memorystore, Compute Engine) | https://console.cloud.google.com/freetrial | - Valid credit card<br>- Gmail or Google Workspace account<br>- Phone number for verification | 30-45 min | [ ] |
| **GCP Billing Enabled** | Included | Required to use paid services after free tier | https://console.cloud.google.com/billing | - GCP account created<br>- Credit card added | 10 min | [ ] |
| **Temporal Cloud** | $100-150/month<br>(Essentials tier) | Workflow orchestration (managed Temporal Server) | https://temporal.io/cloud<br>https://cloud.temporal.io/signup | - Valid email<br>- Credit card | 20-30 min | [ ] |
| **Grafana Cloud Pro** | $19/month | Monitoring dashboards + Prometheus storage | https://grafana.com/auth/sign-up | - Valid email<br>- Credit card (or connect to GCP billing) | 15-20 min | [ ] |

**Subtotal Cloud Services:** $119-169/month (or $19/month for first 90 days with GCP credits)

---

## 2. API Keys & Third-Party Services

| Service | Cost | Purpose | Where to Get | Prerequisites | Time to Setup | Status |
|---------|------|---------|--------------|---------------|---------------|--------|
| **OpenAI API Key** | ~$10-30/month (usage-based)<br>$0.00013/1K tokens (embeddings) | Text embeddings (text-embedding-3-small) | https://platform.openai.com/api-keys | - OpenAI account<br>- Payment method added | 10 min | [ ] |
| **Anthropic API Key** | ~$20-50/month (usage-based)<br>$3/million input tokens (Claude Haiku) | Claude for query rewriting, chat, LLM classification | https://console.anthropic.com/settings/keys | - Anthropic account<br>- Payment method added | 10 min | [ ] |

**Subtotal API Keys:** $30-80/month (usage-based)

---

## 3. Development Tools

| Tool | Cost | Purpose | Where to Get | Prerequisites | Action Needed | Status |
|------|------|---------|--------------|---------------|---------------|--------|
| **Docker Desktop** | **FREE** for personal use<br>**$9/user/month** if org has 250+ employees OR $10M+ revenue | Container runtime for local development and building images | https://www.docker.com/products/docker-desktop/<br>https://www.docker.com/pricing/ | - Check your organization size<br>- Check annual revenue | **ACTION:** Verify if you need Business license (check Docker Desktop settings → About → License) | [ ] |
| **gcloud CLI** | FREE | Google Cloud command-line tool | https://cloud.google.com/sdk/docs/install | - macOS/Linux/Windows | Install via Homebrew: `brew install google-cloud-sdk` | [ ] |
| **Pulumi CLI** | FREE (open source) | Infrastructure-as-Code tool | https://www.pulumi.com/docs/get-started/install/ | - macOS/Linux/Windows | Install via Homebrew: `brew install pulumi` | [ ] |

**Docker Desktop Licensing:**
- ✅ **FREE if:** Small company (<250 employees) OR annual revenue <$10M OR personal/educational use
- ⚠️ **Paid ($9/user/month) if:** Company has 250+ employees AND annual revenue >$10M
- 📋 **How to check:** Docker Desktop → Settings → About → License Agreement

**Subtotal Development Tools:** $0-9/month (depends on Docker licensing)

---

## 4. Accounts & Credentials

| Account | Cost | Purpose | Where to Get | Prerequisites | Time to Setup | Status |
|---------|------|---------|--------------|---------------|---------------|--------|
| **Google Account** (Gmail or Workspace) | FREE (Gmail)<br>$6/user/month (Workspace) | Required for GCP, recommended for all Google services | https://accounts.google.com/signup | - Phone number<br>- Recovery email | 10 min | [ ] |
| **GitHub Account** | FREE (public repos) | Repository hosting, CI/CD via GitHub Actions | https://github.com/signup | - Valid email<br>- 2FA recommended | 10 min | [ ] |
| **Password Manager** | $0-5/user/month<br>(Bitwarden free, 1Password $4.99/mo) | Securely store API keys, passwords, secrets | **Bitwarden:** https://bitwarden.com/<br>**1Password:** https://1password.com/<br>**Pass (GPG):** Built-in on macOS/Linux | - None (choose one) | 20 min | [ ] |

**Subtotal Accounts:** $0-5/month (optional password manager)

---

## 5. Domain & DNS (Optional for Initial Deployment)

| Item | Cost | Purpose | Where to Get | Prerequisites | Time to Setup | Status |
|------|------|---------|--------------|---------------|---------------|--------|
| **Domain Name** | $12-15/year<br>(e.g., apex-memory.com) | Custom domain for production API | **Google Domains:** https://domains.google/ (being sunset)<br>**Cloudflare:** https://www.cloudflare.com/products/registrar/<br>**Namecheap:** https://www.namecheap.com/ | - Credit card | 15-20 min | [ ] |
| **Cloud DNS** | $0.20/month (1 hosted zone) | DNS management for domain | https://console.cloud.google.com/net-services/dns | - GCP account<br>- Domain registered | 10 min | [ ] |
| **SSL Certificate** | FREE (auto-managed by GCP Load Balancer) | HTTPS encryption | Automatic via Cloud Load Balancer | - Domain registered<br>- Load Balancer deployed | 0 min (automatic) | [ ] |

**Note:** You can deploy initially using Cloud Run's auto-generated URL (e.g., `https://apex-api-xxxxx-uc.a.run.app`). Custom domain is optional.

**Subtotal Domain:** $1-2/month (~$15/year amortized)

---

## 6. Security & Secrets Management

| Item | Cost | Purpose | Action Required | Status |
|------|------|---------|-----------------|--------|
| **Generate SECRET_KEY** | FREE | JWT token signing (must be cryptographically secure) | Run: `openssl rand -base64 32` and store in password manager | [ ] |
| **Store all secrets** | Included in password manager | Centralized secret storage | Add to password manager:<br>- GCP service account keys<br>- Temporal Cloud certs<br>- OpenAI API key<br>- Anthropic API key<br>- Database passwords<br>- SECRET_KEY | [ ] |
| **Enable 2FA** | FREE | Two-factor authentication on all accounts | Enable on:<br>- GCP account<br>- GitHub account<br>- OpenAI account<br>- Anthropic account<br>- Temporal Cloud<br>- Grafana Cloud | [ ] |

---

## 📊 Total Monthly Cost Summary

| Category | Low (Minimal Usage) | High (Moderate Usage) | Notes |
|----------|---------------------|----------------------|-------|
| **GCP Services** | $261/month | $542/month | Auto-scales based on traffic |
| **Temporal Cloud** | $100/month | $150/month | Essentials tier |
| **Grafana Cloud** | $19/month | $19/month | Pro tier (10k metrics) |
| **API Keys** (OpenAI + Anthropic) | $30/month | $80/month | Usage-based (embeddings + chat) |
| **Docker Desktop** | $0/month | $9/month | Only if org >250 employees |
| **Domain/DNS** | $1/month | $2/month | ~$15/year amortized |
| **Password Manager** | $0/month | $5/month | Optional (Bitwarden free) |
| **TOTAL** | **$411/month** | **$807/month** | |

**First 90 Days (with GCP $300 free credit):**
- **Out-of-pocket:** $149-249/month (Temporal + Grafana + APIs only)
- **After free credit:** $411-807/month (full cost)

---

## 🎯 Setup Workflow (Recommended Order)

### Day 1: Core Accounts (2-3 hours)

1. **Create GCP Account** (30-45 min)
   - Go to https://console.cloud.google.com/freetrial
   - Use Gmail or create Google Workspace account
   - Add credit card ($300 free credit, won't charge until you opt-in)
   - Verify phone number
   - Complete billing profile

2. **Enable GCP Billing** (10 min)
   - Navigate to Billing → Link Billing Account
   - Set up budget alerts ($700/month threshold)

3. **Create GitHub Account** (10 min) - if you don't have one
   - Go to https://github.com/signup
   - Enable 2FA

4. **Install Development Tools** (20-30 min)
   ```bash
   # Install gcloud CLI
   brew install google-cloud-sdk

   # Install Pulumi CLI
   brew install pulumi

   # Verify Docker Desktop
   docker --version
   # Check licensing: Docker Desktop → Settings → About
   ```

5. **Set up Password Manager** (20 min)
   - Choose Bitwarden (free) or 1Password ($4.99/mo)
   - Create master password (write it down!)
   - Install browser extension
   - Install CLI tool (optional)

### Day 2: API Keys & Cloud Services (1-2 hours)

6. **Get OpenAI API Key** (10 min)
   - Go to https://platform.openai.com/api-keys
   - Create account if needed
   - Add payment method
   - Create API key
   - **IMMEDIATELY:** Copy to password manager (you can't see it again)

7. **Get Anthropic API Key** (10 min)
   - Go to https://console.anthropic.com/
   - Create account
   - Add payment method
   - Create API key
   - Store in password manager

8. **Set up Temporal Cloud** (20-30 min)
   - Go to https://cloud.temporal.io/signup
   - Create account (Essentials tier)
   - Create namespace: `apex-memory-prod`
   - Download mTLS certificates
   - Store certificates in password manager

9. **Set up Grafana Cloud** (15-20 min)
   - Go to https://grafana.com/auth/sign-up
   - Choose Pro tier ($19/month)
   - Connect to GCP billing (optional)
   - Note Prometheus endpoint URL
   - Store API key in password manager

### Day 3: Security & Credentials (30-60 min)

10. **Generate Secrets** (15 min)
    ```bash
    # Generate SECRET_KEY for JWT
    openssl rand -base64 32
    # Output: (example) 3xK8n2Lm9Qp1Rz7Ws4Yv6Bt0Hd5Jf8Gc

    # Generate PostgreSQL password
    openssl rand -base64 32

    # Generate Neo4j password
    openssl rand -base64 32
    ```
    **Store ALL of these in password manager immediately**

11. **Enable 2FA Everywhere** (15-30 min)
    - GCP: https://myaccount.google.com/security
    - GitHub: Settings → Password and authentication
    - OpenAI: https://platform.openai.com/account/security
    - Anthropic: Account settings
    - Temporal Cloud: Account settings
    - Grafana Cloud: Profile → Security

12. **Create Deployment Checklist** (10 min)
    - Copy this file to your password manager notes
    - Check off items as you complete them
    - Store all credentials securely

---

## 💡 Cost Optimization Tips

**Free Tier Maximization:**
- ✅ GCP $300 credit lasts 90 days (use it!)
- ✅ Cloud Run: 2M requests/month free
- ✅ Cloud Storage: 5GB free
- ✅ Cloud Build: 120 build-minutes/day free

**Minimize Initial Costs:**
1. Start with smallest GCP instance sizes (db-f1-micro, e2-small)
2. Use Cloud Run min-instances=0 initially (accept cold starts)
3. Use Memorystore Basic tier (no HA/replication)
4. Skip custom domain initially (use Cloud Run URL)

**After 3 Months (when usage is stable):**
1. Apply GCP Committed Use Discounts (30-55% savings)
   - Cloud SQL: 37% off with 1-year commit
   - Compute Engine: 55% off with 1-year commit
2. Potential savings: $200-300/month
3. Net cost after discounts: $600-700/month (moderate usage)

---

## ⚠️ Common Pitfalls to Avoid

### GCP Account Setup
- ❌ **Don't:** Skip budget alerts (can rack up unexpected costs)
- ✅ **Do:** Set budget alerts at $500, $700, $900, $1,200

### API Keys
- ❌ **Don't:** Leave API keys in `.env` files committed to Git
- ✅ **Do:** Use `.env.example` templates, gitignore `.env`

### Docker Desktop
- ❌ **Don't:** Assume it's free for commercial use without checking
- ✅ **Do:** Verify your organization size and licensing requirements

### Secrets Management
- ❌ **Don't:** Use weak passwords or reuse passwords
- ✅ **Do:** Use password manager to generate strong, unique passwords

### Temporal Cloud
- ❌ **Don't:** Lose your mTLS certificates (can't regenerate exact same ones)
- ✅ **Do:** Store certificates in password manager + backup to encrypted USB

---

## 📋 Pre-Deployment Verification

**Before starting actual deployment, verify:**

- [ ] GCP account has $300 free credit active
- [ ] Budget alerts configured in GCP Billing
- [ ] All API keys stored in password manager
- [ ] 2FA enabled on all accounts
- [ ] Docker Desktop licensed correctly for your use case
- [ ] gcloud CLI installed and authenticated (`gcloud auth login`)
- [ ] Pulumi CLI installed (`pulumi version`)
- [ ] All secrets generated and stored securely
- [ ] Password manager backed up
- [ ] You have at least 5-6 weeks available for deployment (20-28 hrs/week)

**Once all checkboxes above are checked, you're ready to start deployment!**

---

## 🔗 Quick Links

**Cloud Consoles:**
- GCP: https://console.cloud.google.com/
- Temporal Cloud: https://cloud.temporal.io/
- Grafana Cloud: https://grafana.com/
- OpenAI: https://platform.openai.com/
- Anthropic: https://console.anthropic.com/

**Billing/Usage:**
- GCP Billing: https://console.cloud.google.com/billing
- OpenAI Usage: https://platform.openai.com/usage
- Anthropic Usage: https://console.anthropic.com/settings/usage

**Documentation:**
- GCP Free Tier: https://cloud.google.com/free
- Temporal Pricing: https://temporal.io/pricing
- Grafana Pricing: https://grafana.com/pricing
- OpenAI Pricing: https://openai.com/api/pricing/
- Anthropic Pricing: https://www.anthropic.com/pricing

---

**Last Updated:** 2025-11-07
**Status:** Complete prerequisite checklist
**Next Step:** After completing all items above, proceed to `deployment/PRODUCTION-DEPLOYMENT-PLAN.md`
