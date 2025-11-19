# Temporal Cloud Setup Guide

**Date:** 2025-11-15
**Estimated Time:** 50-80 minutes
**Cost:** $100-150/month (Essentials tier)
**Status:** 🟡 In Progress

---

## Why Temporal Cloud?

Your Apex Memory System uses Temporal for:
- **Document Ingestion Workflow** - Durable, fault-tolerant document processing
- **Memory Decay Workflow** - Daily automated importance recalculation
- **Conversation Processing** - Background entity extraction
- **Structured Data Ingestion** - JSON/API data ingestion

**Already Implemented:**
- ✅ 5 Temporal activities (parse, extract entities, generate embeddings, write to DBs, staging)
- ✅ DocumentIngestionWorkflow with saga pattern
- ✅ 27 Temporal metrics instrumented
- ✅ API endpoints integrated with Temporal client
- ✅ 162+ tests passing (including Temporal integration tests)

**You need Temporal Cloud to run these workflows in production.**

---

## Step 1: Create Temporal Cloud Account (20 minutes)

### 1.1 Sign Up

Go to: **https://cloud.temporal.io/signup**

**Account Details:**
- Use your primary email (same as GCP if possible)
- Create strong password (store in password manager immediately)
- Verify email address

### 1.2 Choose Plan

**Select: Essentials Tier**
- Cost: $100-150/month
- Includes:
  - 200 actions per second
  - 30-day event history retention
  - mTLS security
  - Multi-region support
  - Standard support

**DO NOT choose:**
- Free tier (limited to 10 actions/sec, not suitable for production)
- Enterprise tier (overkill for initial deployment)

### 1.3 Add Payment Method

- Navigate to: Settings → Billing
- Add credit card
- Set billing email (same as account email recommended)
- **Optional:** Set budget alert at $200/month

**Checklist:**
- [ ] Account created
- [ ] Email verified
- [ ] Payment method added
- [ ] Essentials tier selected

---

## Step 2: Create Namespace (15 minutes)

### 2.1 Create Namespace

In Temporal Cloud console:
1. Click "Create Namespace"
2. Enter namespace details:

**Recommended Configuration:**

```
Namespace Name: apex-memory-prod
(Or: apex-memory-dev for testing first)

Region: us-east-1
(Or choose nearest to your GCP region: us-central1 → us-east-1)

Retention Period: 30 days
(Default, keeps workflow history for 30 days)

Certificate Filter: [Leave empty for now]
(You'll configure mTLS next)
```

### 2.2 Why These Settings?

**Namespace Name:**
- Use `apex-memory-prod` for production
- Use `apex-memory-dev` for development/testing
- You can create multiple namespaces (billed separately)

**Region Selection:**
- **us-east-1** (N. Virginia) - Recommended if GCP region is us-central1
- **us-west-2** (Oregon) - If GCP region is us-west1
- **eu-west-1** (Ireland) - If GCP region is europe-west1

**Retention Period:**
- 30 days = Default (sufficient for most use cases)
- Longer retention = Higher cost
- Can't be changed after namespace creation

**Checklist:**
- [ ] Namespace created
- [ ] Namespace name noted (e.g., `apex-memory-prod`)
- [ ] Region noted (e.g., `us-east-1`)

---

## Step 3: Setup mTLS Authentication (15 minutes)

### 3.1 What is mTLS?

Temporal Cloud uses **mutual TLS (mTLS)** for secure authentication:
- Your application presents a client certificate
- Temporal Cloud verifies the certificate
- No passwords/API keys needed

**You need:**
1. Client certificate (`.pem` file)
2. Private key (`.key` file)
3. CA certificate (optional, usually bundled)

### 3.2 Generate mTLS Certificate

**Option A: Use Temporal Cloud UI (Recommended)**

In your namespace settings:
1. Navigate to: Namespace → Settings → mTLS
2. Click "Generate Certificate"
3. Download both files:
   - `client-cert.pem` (public certificate)
   - `client-key.pem` (private key)
4. **CRITICAL:** Save immediately - you won't see the private key again!

**Option B: Use Your Own Certificate (Advanced)**

If you have existing PKI infrastructure:
```bash
# Generate private key
openssl genrsa -out client-key.pem 2048

# Generate certificate signing request
openssl req -new -key client-key.pem -out client.csr \
  -subj "/CN=apex-memory/O=YourOrg"

# Generate self-signed certificate (valid for 1 year)
openssl x509 -req -in client.csr -signkey client-key.pem \
  -out client-cert.pem -days 365

# Upload client-cert.pem to Temporal Cloud
```

### 3.3 Store Certificates Securely

**IMMEDIATELY after download:**

1. **Create secure directory:**
   ```bash
   mkdir -p ~/.temporal/certs/apex-memory-prod
   chmod 700 ~/.temporal/certs
   ```

2. **Move certificates:**
   ```bash
   mv ~/Downloads/client-cert.pem ~/.temporal/certs/apex-memory-prod/
   mv ~/Downloads/client-key.pem ~/.temporal/certs/apex-memory-prod/
   chmod 600 ~/.temporal/certs/apex-memory-prod/*
   ```

3. **Backup to password manager:**
   - Store both files in password manager (Bitwarden, 1Password, etc.)
   - Add note: "Temporal Cloud mTLS certs for apex-memory-prod"

**Checklist:**
- [ ] mTLS certificate generated/downloaded
- [ ] Private key downloaded
- [ ] Both files stored in `~/.temporal/certs/apex-memory-prod/`
- [ ] Permissions set (chmod 600)
- [ ] Backed up to password manager

---

## Step 4: Obtain Connection Details (10 minutes)

### 4.1 Get Namespace Address

In Temporal Cloud console:
1. Navigate to your namespace
2. Copy the **Namespace Address**

**Format:**
```
apex-memory-prod.tmprl.cloud:7233
```

Or for custom region:
```
apex-memory-prod.us-east-1.tmprl.cloud:7233
```

### 4.2 Record All Connection Details

Create a note with these values:

```bash
# Temporal Cloud Connection Details
# Namespace: apex-memory-prod
# Created: 2025-11-15

# Connection
TEMPORAL_NAMESPACE="apex-memory-prod.tmprl.cloud"
TEMPORAL_ADDRESS="apex-memory-prod.tmprl.cloud:7233"

# Certificates
TEMPORAL_CERT_PATH="/Users/[your-username]/.temporal/certs/apex-memory-prod/client-cert.pem"
TEMPORAL_KEY_PATH="/Users/[your-username]/.temporal/certs/apex-memory-prod/client-key.pem"

# Alternative: GCP Secret Manager (for production)
# TEMPORAL_CERT_PATH="gcp:///projects/apex-memory-prod/secrets/temporal-client-cert/versions/latest"
# TEMPORAL_KEY_PATH="gcp:///projects/apex-memory-prod/secrets/temporal-client-key/versions/latest"
```

**Replace `[your-username]`** with your actual macOS username.

### 4.3 Store in Password Manager

Save the above note in your password manager:
- **Title:** "Temporal Cloud - apex-memory-prod"
- **Username:** (namespace name)
- **Password:** (not needed for mTLS)
- **Notes:** (paste the connection details above)
- **Attachments:**
  - `client-cert.pem`
  - `client-key.pem`

**Checklist:**
- [ ] Namespace address copied
- [ ] Connection details documented
- [ ] All details stored in password manager

---

## Step 5: Test Connection (10 minutes)

### 5.1 Install Temporal CLI (if not already installed)

```bash
# macOS
brew install temporal

# Verify installation
temporal --version
```

### 5.2 Test Connection

```bash
# Set environment variables
export TEMPORAL_NAMESPACE="apex-memory-prod.tmprl.cloud"
export TEMPORAL_ADDRESS="apex-memory-prod.tmprl.cloud:7233"
export TEMPORAL_CERT_PATH="$HOME/.temporal/certs/apex-memory-prod/client-cert.pem"
export TEMPORAL_KEY_PATH="$HOME/.temporal/certs/apex-memory-prod/client-key.pem"

# Test connection
temporal workflow list \
  --address "$TEMPORAL_ADDRESS" \
  --namespace "$TEMPORAL_NAMESPACE" \
  --tls-cert-path "$TEMPORAL_CERT_PATH" \
  --tls-key-path "$TEMPORAL_KEY_PATH"
```

**Expected output:**
```
No workflows found (or list of existing workflows if any)
```

**If you see connection errors:**
- Check certificate paths are correct
- Verify namespace name matches exactly
- Ensure certificates have correct permissions (chmod 600)
- Check firewall/VPN isn't blocking port 7233

### 5.3 Test with Python SDK (Optional)

```bash
cd apex-memory-system

# Activate virtual environment
source venv/bin/activate

# Test Temporal connection
python -c "
import asyncio
from temporalio.client import Client, TLSConfig

async def test_connection():
    with open('$TEMPORAL_CERT_PATH', 'rb') as f:
        client_cert = f.read()
    with open('$TEMPORAL_KEY_PATH', 'rb') as f:
        client_key = f.read()

    client = await Client.connect(
        '$TEMPORAL_ADDRESS',
        namespace='$TEMPORAL_NAMESPACE',
        tls=TLSConfig(
            client_cert=client_cert,
            client_private_key=client_key,
        )
    )
    print('✅ Connected successfully to Temporal Cloud!')
    print(f'Namespace: {client.namespace}')

asyncio.run(test_connection())
"
```

**Expected output:**
```
✅ Connected successfully to Temporal Cloud!
Namespace: apex-memory-prod.tmprl.cloud
```

**Checklist:**
- [ ] Temporal CLI installed
- [ ] Connection test successful (CLI)
- [ ] Python SDK connection test successful (optional)

---

## Step 6: Update Application Configuration (10 minutes)

### 6.1 Update .env File

```bash
cd apex-memory-system

# Create .env file if it doesn't exist
cp .env.example .env

# Add Temporal Cloud configuration
cat >> .env << 'EOF'

# Temporal Cloud Configuration
TEMPORAL_NAMESPACE=apex-memory-prod.tmprl.cloud
TEMPORAL_ADDRESS=apex-memory-prod.tmprl.cloud:7233
TEMPORAL_CERT_PATH=/Users/[your-username]/.temporal/certs/apex-memory-prod/client-cert.pem
TEMPORAL_KEY_PATH=/Users/[your-username]/.temporal/certs/apex-memory-prod/client-key.pem

# Temporal Task Queue (used by workers and workflows)
TEMPORAL_TASK_QUEUE=apex-ingestion-queue
EOF
```

**Replace `[your-username]`** with your actual username.

### 6.2 Update Production Environment Template

```bash
# Update .env.production.example
cat >> .env.production.example << 'EOF'

# Temporal Cloud Configuration (Production)
TEMPORAL_NAMESPACE=apex-memory-prod.tmprl.cloud
TEMPORAL_ADDRESS=apex-memory-prod.tmprl.cloud:7233
TEMPORAL_CERT_PATH=gcp:///projects/apex-memory-prod/secrets/temporal-client-cert/versions/latest
TEMPORAL_KEY_PATH=gcp:///projects/apex-memory-prod/secrets/temporal-client-key/versions/latest
TEMPORAL_TASK_QUEUE=apex-ingestion-queue
EOF
```

**Note:** Production uses GCP Secret Manager paths (will configure in Week 4).

**Checklist:**
- [ ] `.env` updated with Temporal Cloud configuration
- [ ] `.env.production.example` updated
- [ ] Paths verified (no typos)

---

## Step 7: Enable 2FA (5 minutes)

### 7.1 Enable Two-Factor Authentication

In Temporal Cloud console:
1. Navigate to: Settings → Security
2. Click "Enable 2FA"
3. Scan QR code with authenticator app (Google Authenticator, Authy, 1Password)
4. Enter verification code
5. **Save recovery codes** in password manager

**Checklist:**
- [ ] 2FA enabled on Temporal Cloud account
- [ ] Recovery codes saved in password manager

---

## ✅ Temporal Cloud Setup Complete!

### What You've Accomplished

- ✅ Temporal Cloud account created (Essentials tier, $100-150/month)
- ✅ Namespace created (`apex-memory-prod` or `apex-memory-dev`)
- ✅ mTLS certificates generated and stored securely
- ✅ Connection tested successfully
- ✅ Application configured with Temporal Cloud credentials
- ✅ 2FA enabled for account security

### Next Steps

**Update Prerequisites Tracker:**
- Mark "Temporal Cloud" section as complete in `PREREQUISITES-COMPLETION-TRACKER.md`

**Continue Prerequisites Setup:**
- Next: Grafana Cloud Pro (30-40 minutes)
- Then: API Keys (OpenAI + Anthropic) (20-30 minutes)
- Then: Security & Secrets (30-45 minutes)

**Or: Test Temporal Integration Immediately:**
```bash
cd apex-memory-system
source venv/bin/activate

# Start Temporal worker
python src/apex_memory/temporal/workers/dev_worker.py

# In another terminal, test workflow
python -c "
import asyncio
from temporalio.client import Client, TLSConfig
from apex_memory.temporal.workflows.ingestion import DocumentIngestionWorkflow

async def test_workflow():
    # Connect to Temporal Cloud
    with open('$TEMPORAL_CERT_PATH', 'rb') as f:
        client_cert = f.read()
    with open('$TEMPORAL_KEY_PATH', 'rb') as f:
        client_key = f.read()

    client = await Client.connect(
        '$TEMPORAL_ADDRESS',
        namespace='$TEMPORAL_NAMESPACE',
        tls=TLSConfig(
            client_cert=client_cert,
            client_private_key=client_key,
        )
    )

    # Start test workflow
    result = await client.execute_workflow(
        DocumentIngestionWorkflow.run,
        {'test': 'Hello from Temporal Cloud!'},
        id='test-workflow-1',
        task_queue='apex-ingestion-queue',
    )
    print(f'✅ Workflow completed: {result}')

asyncio.run(test_workflow())
"
```

---

## Troubleshooting

### Connection Refused Error

**Problem:** `temporal workflow list` returns "connection refused"

**Solutions:**
1. Check namespace address is correct (include `:7233` port)
2. Verify firewall/VPN isn't blocking outbound connections
3. Try with `--tls-server-name` flag:
   ```bash
   temporal workflow list \
     --address "$TEMPORAL_ADDRESS" \
     --namespace "$TEMPORAL_NAMESPACE" \
     --tls-cert-path "$TEMPORAL_CERT_PATH" \
     --tls-key-path "$TEMPORAL_KEY_PATH" \
     --tls-server-name "apex-memory-prod.tmprl.cloud"
   ```

### Certificate Verification Failed

**Problem:** "certificate signed by unknown authority"

**Solutions:**
1. Verify you downloaded BOTH certificate and private key
2. Check file permissions: `chmod 600 ~/.temporal/certs/apex-memory-prod/*`
3. Re-download certificates from Temporal Cloud UI

### Namespace Not Found

**Problem:** "namespace not found" error

**Solutions:**
1. Verify namespace name matches exactly (case-sensitive)
2. Check namespace address includes `.tmprl.cloud` domain
3. Wait 2-3 minutes after namespace creation (propagation delay)

---

**Setup Complete!** 🎉

You're now ready to run Temporal workflows in production on Temporal Cloud.

**Next:** Continue with Grafana Cloud setup (30-40 minutes)
