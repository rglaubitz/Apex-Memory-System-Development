# Temporal Cloud Setup - Complete Instructions

**Date:** 2025-11-15
**Status:** ✅ Namespace Created | ⏳ Configuration Pending
**Your Namespace:** `quickstart-apex-memory-prod.pnlwy`

---

## ✅ What You've Already Done

Great progress! You've successfully:
- ✅ Created Temporal Cloud account
- ✅ Created namespace: `quickstart-apex-memory-prod.pnlwy`
- ✅ Generated API key
- ✅ Installed Temporal CLI (v1.5.1)

---

## 🎯 What You Need To Do Now

### Step 1: Configure Temporal CLI (2 minutes)

**Run these commands in your terminal:**

```bash
# Configure Temporal Cloud profile
temporal --profile cloud config set --prop address --value "us-east4.gcp.api.temporal.io:7233"

temporal --profile cloud config set --prop namespace --value "quickstart-apex-memory-prod.pnlwy"

temporal --profile cloud config set --prop api_key --value "<YOUR_TEMPORAL_API_KEY>"
```

**Expected output:**
```
Profile: cloud
Namespace: quickstart-apex-memory-prod.pnlwy
Address: us-east4.gcp.api.temporal.io:7233
```

---

### Step 2: Test Connection (2 minutes)

```bash
# Test connection to Temporal Cloud
temporal --profile cloud workflow list

# Expected: Empty list (no workflows yet) or existing workflows if any
```

**If you see "Request unauthorized" error:**
- Wait 1-2 minutes for API key to activate
- Try again

---

### Step 3: Update Apex Memory System .env (5 minutes)

```bash
cd /Users/richardglaubitz/Projects/apex-memory-system

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    cp .env.example .env
fi

# Add Temporal Cloud configuration
cat >> .env << 'EOF'

# ========================================
# Temporal Cloud Configuration
# ========================================
# Namespace
TEMPORAL_NAMESPACE=quickstart-apex-memory-prod.pnlwy

# Address (us-east4 region)
TEMPORAL_ADDRESS=us-east4.gcp.api.temporal.io:7233

# API Key (expires 2025-01-13)
TEMPORAL_API_KEY=<YOUR_TEMPORAL_API_KEY>

# Task Queue
TEMPORAL_TASK_QUEUE=apex-ingestion-queue

# Authentication Method (api_key vs mTLS)
TEMPORAL_AUTH_METHOD=api_key
EOF

echo "✅ Temporal Cloud configuration added to .env"
```

---

### Step 4: Test with Python SDK (5 minutes)

**Test that your application can connect:**

```bash
cd /Users/richardglaubitz/Projects/apex-memory-system
source venv/bin/activate

# Test Temporal Cloud connection with Python
python << 'EOF'
import asyncio
import os
from temporalio.client import Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_connection():
    # Get credentials from environment
    namespace = os.getenv("TEMPORAL_NAMESPACE")
    address = os.getenv("TEMPORAL_ADDRESS")
    api_key = os.getenv("TEMPORAL_API_KEY")

    print(f"Connecting to Temporal Cloud...")
    print(f"  Namespace: {namespace}")
    print(f"  Address: {address}")

    # Connect using API key authentication
    client = await Client.connect(
        address,
        namespace=namespace,
        api_key=api_key,
    )

    print(f"\n✅ Connected successfully to Temporal Cloud!")
    print(f"   Namespace: {client.namespace}")
    print(f"   Identity: {client.identity}")

    # List workflows (should be empty initially)
    workflows = [w async for w in client.list_workflows()]
    print(f"\n   Active workflows: {len(workflows)}")

asyncio.run(test_connection())
EOF
```

**Expected output:**
```
Connecting to Temporal Cloud...
  Namespace: quickstart-apex-memory-prod.pnlwy
  Address: us-east4.gcp.api.temporal.io:7233

✅ Connected successfully to Temporal Cloud!
   Namespace: quickstart-apex-memory-prod.pnlwy
   Identity: apex-memory@...

   Active workflows: 0
```

---

### Step 5: Store Credentials Securely (10 minutes)

#### 5.1 Create Secure Note in Password Manager

**Copy this information to your password manager (Bitwarden, 1Password, etc.):**

```yaml
Title: Temporal Cloud - Apex Memory Production
Type: Secure Note
Category: Development

Connection Details:
  Account ID: pnlwy
  Namespace: quickstart-apex-memory-prod.pnlwy
  Region: us-east4 (GCP)
  Address: us-east4.gcp.api.temporal.io:7233

API Key:
  Key: <YOUR_TEMPORAL_API_KEY>
  Created: 2025-11-15
  Expires: 2025-01-13
  Subject ID: 4dcbce3b83754cd5ac19f74a72c21d1a

Task Queue:
  Name: apex-ingestion-queue

Cost:
  Tier: Essentials
  Monthly: $100-150

Notes:
  - API key authentication (not mTLS)
  - Expires in ~60 days (regenerate before 2025-01-13)
  - Used for document ingestion workflows
  - Region us-east4 nearest to GCP us-central1
```

#### 5.2 IMPORTANT: Revoke the Exposed API Key

Since you shared the API key publicly in the screenshot, you should revoke it and generate a new one:

**To revoke and regenerate:**

1. Go to Temporal Cloud console: https://cloud.temporal.io
2. Navigate to: Settings → API Keys
3. Find the key that starts with `GzbFFLK0B9lbfvQt6z7bXFteNjPfSsZD`
4. Click "Revoke"
5. Generate new API key
6. Update `.env` file with new key
7. Run Step 4 again to test with new key

**⚠️ CRITICAL:** Do this within 24-48 hours to prevent unauthorized access.

---

### Step 6: Update Production Configuration Template (5 minutes)

```bash
cd /Users/richardglaubitz/Projects/apex-memory-system

# Update .env.production.example for future reference
cat >> .env.production.example << 'EOF'

# ========================================
# Temporal Cloud Configuration (Production)
# ========================================
# Option 1: Direct API Key (for Cloud Run)
TEMPORAL_NAMESPACE=quickstart-apex-memory-prod.pnlwy
TEMPORAL_ADDRESS=us-east4.gcp.api.temporal.io:7233
TEMPORAL_API_KEY=<YOUR_TEMPORAL_API_KEY>
TEMPORAL_TASK_QUEUE=apex-ingestion-queue
TEMPORAL_AUTH_METHOD=api_key

# Option 2: GCP Secret Manager (recommended for production)
# TEMPORAL_API_KEY=gcp:///projects/apex-memory-prod/secrets/temporal-api-key/versions/latest
EOF

echo "✅ Production template updated"
```

---

## ✅ Temporal Cloud Setup Complete!

### What You've Accomplished

- ✅ Temporal Cloud account created (Essentials tier, $100-150/month)
- ✅ Namespace created (`quickstart-apex-memory-prod.pnlwy`)
- ✅ API key generated (easier than mTLS!)
- ✅ Temporal CLI configured
- ✅ Connection tested successfully
- ✅ Application `.env` configured
- ✅ Credentials stored in password manager

---

## 🎯 Next Steps

### Immediate (Security)
1. ⚠️ **Revoke the exposed API key** (do this within 24-48 hours)
2. ✅ Generate new API key
3. ✅ Update `.env` with new key

### Next Prerequisites
4. **Grafana Cloud Pro** (30-40 minutes) - Monitoring dashboards
5. **API Keys** (20-30 minutes) - OpenAI + Anthropic
6. **Secrets Generation** (30-45 minutes) - SECRET_KEY, DB passwords

---

## 🧪 Optional: Test a Workflow Now

If you want to test immediately:

```bash
cd /Users/richardglaubitz/Projects/apex-memory-system
source venv/bin/activate

# Start Temporal worker (in one terminal)
export TEMPORAL_NAMESPACE="quickstart-apex-memory-prod.pnlwy"
export TEMPORAL_ADDRESS="us-east4.gcp.api.temporal.io:7233"
export TEMPORAL_API_KEY="<YOUR_TEMPORAL_API_KEY>"

python src/apex_memory/temporal/workers/dev_worker.py
```

Then you can view workflows at: https://cloud.temporal.io/namespaces/quickstart-apex-memory-prod.pnlwy/workflows

---

## 📊 Connection Details Reference

**For quick reference:**

```bash
# Temporal Cloud
Namespace: quickstart-apex-memory-prod.pnlwy
Address: us-east4.gcp.api.temporal.io:7233
Region: us-east4 (GCP)
Account ID: pnlwy

# Task Queue
apex-ingestion-queue

# Web UI
https://cloud.temporal.io/namespaces/quickstart-apex-memory-prod.pnlwy
```

---

## Troubleshooting

### "Request unauthorized" Error

**Problem:** API key not activated yet

**Solution:**
- Wait 1-2 minutes
- Try connection test again
- If persists, check API key copied correctly

### "Namespace not found" Error

**Problem:** Namespace name typo

**Solution:**
- Verify exact namespace: `quickstart-apex-memory-prod.pnlwy`
- Check capitalization (case-sensitive)

### Python SDK Connection Fails

**Problem:** Missing or incorrect API key in `.env`

**Solution:**
```bash
# Check if API key is set
cd /Users/richardglaubitz/Projects/apex-memory-system
grep TEMPORAL_API_KEY .env

# If missing, re-run Step 3
```

---

**Setup Complete!** 🎉

You're now ready to run Temporal workflows in production on Temporal Cloud.

**Next:** Continue with Grafana Cloud setup (30-40 minutes) or regenerate API key for security.
