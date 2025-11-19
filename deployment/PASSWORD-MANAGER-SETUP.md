# Password Manager Setup Guide

**Date:** 2025-11-15
**Time:** 15-20 minutes
**Cost:** FREE (Bitwarden) or $4.99/month (1Password)

---

## Why a Password Manager?

Your Apex Memory System deployment requires managing **10+ critical credentials:**

- ✅ Temporal Cloud (namespace, API key, connection details)
- ✅ Grafana Cloud (Prometheus credentials, dashboard URLs)
- ✅ OpenAI API key (embeddings, Graphiti)
- ⏳ Anthropic API key (Claude for chat, query rewriting)
- ✅ SECRET_KEY (JWT signing)
- ✅ PostgreSQL password
- ✅ Neo4j password
- ✅ Redis password
- 🔜 GCP service account keys (future production deployment)

**Without a password manager:**
- ❌ Risk losing credentials (no recovery)
- ❌ Weak passwords (easy to guess)
- ❌ Reused passwords across services
- ❌ Credentials in plain text files (security risk)

**With a password manager:**
- ✅ Military-grade encryption (AES-256)
- ✅ Automatic backups and sync
- ✅ Browser integration (auto-fill)
- ✅ Secure sharing with team members
- ✅ 2FA/MFA support
- ✅ Breach monitoring

---

## Option 1: Bitwarden (Recommended - FREE)

**Why Bitwarden:**
- ✅ **FREE forever** (unlimited passwords, devices, sync)
- ✅ Open-source (auditable, transparent)
- ✅ Cross-platform (macOS, Windows, Linux, iOS, Android, browser)
- ✅ Self-hostable (optional)
- ✅ CLI for automation
- ✅ Excellent security track record

**Paid upgrade ($10/year):** TOTP 2FA generator, 1GB encrypted file storage, emergency access

---

### Step 1: Install Bitwarden (5 minutes)

#### Desktop App + CLI

```bash
# Install Bitwarden desktop app
brew install --cask bitwarden

# Install Bitwarden CLI (optional, for automation)
brew install bitwarden-cli

# Launch Bitwarden desktop
open -a Bitwarden
```

#### Browser Extension (Recommended)

**Chrome/Brave/Edge:**
1. Go to: https://chrome.google.com/webstore/detail/bitwarden/nngceckbapebfimnlniiiahkandclblb
2. Click "Add to Chrome"
3. Pin extension to toolbar

**Firefox:**
1. Go to: https://addons.mozilla.org/en-US/firefox/addon/bitwarden-password-manager/
2. Click "Add to Firefox"

---

### Step 2: Create Bitwarden Account (5 minutes)

**Go to:** https://vault.bitwarden.com/#/register

**Account Details:**
- **Email:** Use your primary email (same as GCP, Temporal if possible)
- **Master Password:**
  - **CRITICAL:** This is the ONLY password you need to remember
  - Must be strong (16+ characters, mix of letters, numbers, symbols)
  - **Write it down physically** (store in safe place)
  - **You CANNOT recover this password** - if lost, all data is gone

**Master Password Best Practices:**
```
❌ Bad: password123, mypassword, Company2024
✅ Good: Correct-Horse-Battery-Staple-9247 (Diceware method)
✅ Good: MyD0g!sN@med&Charlie#2019 (personal phrase + numbers/symbols)
```

**Backup Master Password:**
1. Write on paper, store in safe/locked drawer
2. Or use offline password hint (don't store online!)

---

### Step 3: Enable 2FA on Bitwarden (5 minutes)

**⚠️ CRITICAL:** Enable 2FA BEFORE storing any production credentials!

**In Bitwarden:**
1. Navigate to: **Settings → Security → Two-step Login**
2. Choose method:
   - **Authenticator App** (recommended) - Use Authy, Google Authenticator, or Microsoft Authenticator
   - **Email** (backup only) - Less secure but better than nothing
3. Follow setup wizard
4. **Save recovery codes** - Store in safe place (physical paper)

**Why 2FA is critical:**
- Even if master password is compromised, attacker can't access vault
- Required for production deployment best practices
- Many compliance frameworks require it

---

### Step 4: Store Apex Memory Credentials (10 minutes)

**Create organized folder structure:**

1. **In Bitwarden:** Create folder "Apex Memory System"
2. **Create the following secure notes:**

---

#### Secure Note 1: Temporal Cloud

```yaml
Title: Temporal Cloud - Apex Memory
Type: Secure Note
Folder: Apex Memory System
Category: Cloud Services

Namespace: quickstart-apex-memory-prod.pnlwy
Address: us-east4.gcp.api.temporal.io:7233
Account ID: pnlwy
Region: us-east4 (GCP)
Task Queue: apex-ingestion-queue

API Key: <YOUR_TEMPORAL_API_KEY>
API Key Expires: 2025-01-13
Auth Method: API Key (not mTLS)

Console: https://cloud.temporal.io
UI: http://localhost:8088 (local development)

Cost: $100-150/month (Essentials tier)

⚠️ Security Notes:
- API key was exposed in screenshot - REGENERATE within 24-48 hours
- API key has 60-day expiration (2025-01-13) - regenerate before expiry
- Use temporal CLI profile: "cloud"

Notes:
- Namespace created: 2025-11-15
- 27 Temporal metrics already instrumented in codebase
- Local development via Docker: docker-compose up temporal
```

---

#### Secure Note 2: Application Secrets

```yaml
Title: Apex Memory - Application Secrets
Type: Secure Note
Folder: Apex Memory System
Category: Development

SECRET_KEY (JWT): Vs/+L290LTyKhPIxxDRkpWyz1Isvg2fxnF1kQ9d9f3Y=
Generated: 2025-11-15
Purpose: JWT token signing for authentication
Length: 256 bits (32 bytes, base64-encoded)

PostgreSQL Password: zvzl8fnKdcIv6AA+5xKlIoYDpHnMeRam
User: apex
Database: apex_memory
Port: 5432

Neo4j Password: 41O4Sf955Z3frfw9PTQRRubhtijUWNQd
User: neo4j
Port: 7687

Redis Password: Wb7NPoIAJ4so21u9t1vwZf4Ux08EKLMF
Port: 6379

Notes:
- All passwords: 24-byte (192-bit) base64-encoded
- PostgreSQL and Neo4j passwords required
- Redis password optional (can run without auth in private network)
- Rotate SECRET_KEY every 90-180 days
- DO NOT commit to git (.env is in .gitignore)
```

---

#### Secure Note 3: OpenAI API

```yaml
Title: OpenAI API - Apex Memory
Type: Secure Note
Folder: Apex Memory System
Category: API Keys

API Key: [YOUR_OPENAI_API_KEY_HERE]
Created: [DATE]
Monthly Limit: $50 (recommended)
Usage Alerts: $25 (50%), $40 (80%)

Default Model: text-embedding-3-small
Purpose:
  - Text embeddings ($0.00013/1K tokens)
  - Graphiti entity extraction (90%+ accuracy)
  - GPT-4 for conversation processing (optional)

Cost Estimate: $10-30/month (usage-based)
Pricing:
  - text-embedding-3-small: $0.00013/1K tokens
  - text-embedding-3-large: $0.00013/1K tokens
  - GPT-4: $30/$60 per 1M tokens (input/output)

Console: https://platform.openai.com
Billing: https://platform.openai.com/account/billing
API Keys: https://platform.openai.com/api-keys

Notes:
  - Set $50/month usage limit
  - Email alerts at $25 and $40
  - Key format: sk-...
```

---

#### Secure Note 4: Anthropic API

```yaml
Title: Anthropic API - Apex Memory
Type: Secure Note
Folder: Apex Memory System
Category: API Keys

API Key: [YOUR_ANTHROPIC_API_KEY_WHEN_YOU_GET_IT]
Created: [DATE]
Monthly Limit: $50
Usage Alerts: $25 (50%), $40 (80%)

Default Model: claude-3-haiku-20240307
Purpose:
  - Query rewriting (natural language → database queries)
  - Chat responses
  - LLM classification
  - Alternative to OpenAI for Graphiti entity extraction

Cost Estimate: $20-50/month (usage-based)
Pricing:
  - Haiku: $3/$15 per 1M tokens (input/output)
  - Sonnet: $15/$75 per 1M tokens (input/output)

Console: https://console.anthropic.com
Billing: https://console.anthropic.com/settings/billing
API Keys: https://console.anthropic.com/settings/keys

Notes:
  - Set $50/month usage limit
  - Email alerts at $25 and $40
  - Key format: sk-ant-api03-...
```

---

#### Secure Note 5: Grafana Cloud

```yaml
Title: Grafana Cloud - Apex Memory
Type: Secure Note
Folder: Apex Memory System
Category: Monitoring

Stack Details:
  Stack Name: apex-memory-prod
  Region: us-east-1
  Plan: Pro ($19/month)

Grafana Instance:
  URL: https://apex-memory-prod.grafana.net
  Username: [your-email]
  Password: [your-password]

Prometheus Remote Write:
  URL: https://prometheus-prod-xx-xxx-xx.grafana.net/api/prom/push
  User (Instance ID): [instance-id]
  Token: glc_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
  Created: 2025-11-15

Dashboard:
  URL: https://apex-memory-prod.grafana.net/d/temporal-ingestion
  Panels: 33 (workflow, activity, data quality, infrastructure, business, logs)

Alerts:
  Total: 12 critical alerts
  Contact: email-alerts
  Email: [your-email]

Cost: $19/month (fixed)
Metrics Limit: 10,000 series
Retention: 13 months

Notes:
  - 27 Temporal metrics already instrumented
  - Dashboard JSON imported from monitoring/dashboards/
  - Alert rules from monitoring/alerts/rules.yml
  - Metrics push every 15 seconds via remote write
```

---

### Step 5: Backup Your Vault (5 minutes)

**Option 1: Cloud Sync (Automatic)**
- Bitwarden automatically syncs to cloud (encrypted)
- Access from any device
- **Free tier includes unlimited sync**

**Option 2: Export Backup (Recommended for critical systems)**

```bash
# Export encrypted vault
# In Bitwarden: Tools → Export Vault → File Format: .json (Encrypted)
# Save to secure location (external USB drive, offline storage)
```

**Backup checklist:**
- [ ] Encrypted vault export stored offline
- [ ] Master password written on paper (stored securely)
- [ ] 2FA recovery codes saved separately
- [ ] Backup location documented

---

## Option 2: 1Password (Paid - $4.99/month)

**Why 1Password:**
- ✅ Premium UX/UI (most polished interface)
- ✅ Excellent browser integration
- ✅ Family plan ($4.99/month for 5 users)
- ✅ Travel Mode (hide sensitive vaults when crossing borders)
- ✅ Watchtower (breach monitoring)
- ✅ 1GB document storage included

**Cost:** $4.99/month individual, $7.99/month family (5 users)

---

### Quick Setup

1. **Sign Up:** https://1password.com/sign-up
2. **Install Desktop:** https://1password.com/downloads
3. **Install Browser Extension:** (auto-prompted during signup)
4. **Enable 2FA:** Settings → Security → Two-Factor Authentication
5. **Create Vault:** "Apex Memory System"
6. **Add Items:** Same structure as Bitwarden (use Secure Notes)

**Templates:** Use the same YAML formats from Bitwarden section above.

---

## Option 3: pass (FREE - GPG-based, Advanced Users)

**Why pass:**
- ✅ 100% FREE and open-source
- ✅ Command-line based (for automation)
- ✅ GPG encryption (military-grade)
- ✅ Git integration (version control)
- ✅ No cloud dependency (fully local)

**Cons:**
- ❌ Requires GPG knowledge
- ❌ No browser integration (unless using browser-pass)
- ❌ Manual sync required
- ❌ Steeper learning curve

---

### Quick Setup

```bash
# Install pass
brew install pass

# Generate GPG key (if you don't have one)
gpg --full-generate-key
# Choose: (1) RSA and RSA, 4096 bits, no expiration

# Initialize pass with your GPG key ID
gpg --list-keys  # Find your key ID (long hex string)
pass init YOUR_GPG_KEY_ID

# Add credentials
pass insert apex-memory/temporal-cloud-api-key
pass insert apex-memory/secret-key
pass insert apex-memory/postgres-password

# Retrieve credentials
pass apex-memory/temporal-cloud-api-key

# Optional: Enable Git tracking
pass git init
pass git remote add origin git@github.com:yourusername/password-store.git
```

**Templates:** Store as multi-line passwords:

```bash
pass insert -m apex-memory/temporal-cloud

# Paste:
Namespace: quickstart-apex-memory-prod.pnlwy
Address: us-east4.gcp.api.temporal.io:7233
API Key: eyJhbGci...
# Ctrl+D to save
```

---

## ✅ Password Manager Setup Complete!

### What You've Accomplished

- ✅ Password manager installed (Bitwarden, 1Password, or pass)
- ✅ Master password created and backed up
- ✅ 2FA enabled on password manager
- ✅ All Apex Memory credentials stored securely:
  - Temporal Cloud (namespace, API key, connection details)
  - Application secrets (SECRET_KEY, database passwords)
  - OpenAI API key
  - Anthropic API key (when you get it)
  - Grafana Cloud (when you set it up)
- ✅ Vault backup created

### Security Best Practices

**DO ✅:**
- Use unique master password (never reuse elsewhere)
- Enable 2FA on password manager
- Backup vault regularly (encrypted export)
- Store master password offline (paper in safe)
- Review stored credentials quarterly
- Enable breach monitoring (if available)

**DON'T ❌:**
- Share master password with anyone
- Store master password digitally
- Disable 2FA for convenience
- Use weak master password
- Store credentials in plain text (delete GENERATED-SECRETS.md!)

---

## 🎯 Next Steps

**Delete Secrets File (CRITICAL!):**
```bash
# ONLY run this AFTER you've stored all secrets in password manager!
rm /Users/richardglaubitz/Projects/Apex-Memory-System-Development/deployment/GENERATED-SECRETS.md

echo "✅ Secrets file deleted (safely stored in password manager)"
```

**Update Prerequisites Tracker:**
- Mark "Password Manager" as complete in `PREREQUISITES-COMPLETION-TRACKER.md`

**Continue Prerequisites:**
- Next: Enable 2FA on all accounts (30-40 minutes)
- Then: Final verification and you're done!

---

## Troubleshooting

### "Can't remember master password"

**Problem:** Forgot Bitwarden/1Password master password

**Solution:**
- **Bitwarden:** No recovery possible - all data is lost (this is by design for security)
- **1Password:** Emergency Kit might help (if you printed it during signup)
- **Prevention:** Write master password on paper, store in safe

### "2FA device lost"

**Problem:** Lost phone with authenticator app

**Solution:**
- Use recovery codes you saved during 2FA setup
- Contact password manager support (may require identity verification)
- **Prevention:** Save recovery codes when enabling 2FA

### "Vault won't sync"

**Problem:** Changes not appearing on other devices

**Solution:**
- Check internet connection
- Force sync: Settings → Sync → Sync Vault Now
- Re-login to account on device
- Check subscription status (for 1Password)

---

**Setup Complete!** 🎉

You now have military-grade encrypted storage for all production credentials. All secrets are backed up and accessible from any device.

**Next:** Enable 2FA on all accounts, then final verification.
