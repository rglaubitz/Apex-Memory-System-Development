# Quick Start - After GCP Authentication

**Status:** Waiting for GCP auth completion
**Next Step:** Re-run Pulumi deployment

---

## ✅ What's Already Complete

**Infrastructure Code (100%):**
- ✅ `modules/networking.py` - VPC networking (137 lines)
- ✅ `modules/databases.py` - Cloud SQL PostgreSQL (126 lines)
- ✅ `__main__.py` - Module orchestration
- ✅ Pulumi preview successful (11 resources ready)

**Tests Created:**
- ✅ `tests/unit/test_networking.py` - 3 unit tests
- ✅ `tests/unit/test_databases.py` - 2 unit tests

**Blocked By:**
- ⏳ GCP application default credentials need refresh

---

## 🔑 Step 1: Complete GCP Authentication

**In your terminal, run ONE of these commands:**

### Option A: Application Default Credentials (Recommended)
```bash
gcloud auth application-default login
```

### Option B: User Credentials with ADC Update
```bash
gcloud auth login --update-adc
```

**This will:**
1. Open your browser
2. Ask you to sign in to Google
3. Grant permissions to gcloud
4. Save new credentials locally

---

## 🚀 Step 2: Retry Pulumi Deployment

**After authentication completes, run:**

```bash
cd /Users/richardglaubitz/Projects/Apex-Memory-System-Development/deployment/pulumi
source .venv/bin/activate
pulumi up --yes
```

**Expected timeline:**
- Fast resources (1-2 min): VPC, subnet, router, NAT, password
- VPC connector (~5-10 min): Takes time to provision
- Cloud SQL (~10-15 min): Longest wait
- **Total: ~15-20 minutes**

---

## 📊 What Will Be Created

**11 GCP Resources:**
1. VPC network (apex-memory-vpc)
2. Private subnet (10.0.0.0/24)
3. VPC connector for Cloud Run (e2-micro, 2-3 instances)
4. Cloud Router
5. Cloud NAT
6. Global Address for private IP range
7. Private service connection
8. Random PostgreSQL password
9. Cloud SQL PostgreSQL 17 instance
10. PostgreSQL database (apex_memory)
11. PostgreSQL user (apex)

**Cost:** ~$25-35/month (dev tier)

---

## ✅ Step 3: Verify Deployment

**After deployment completes:**

```bash
# View all outputs
pulumi stack output

# Get PostgreSQL private IP (should start with 10.)
pulumi stack output postgres_private_ip

# Get PostgreSQL password (secret)
pulumi stack output postgres_password --show-secrets

# View deployment in browser
# URL will be shown in output
```

---

## 🧪 Step 4: Run Tests (Optional)

```bash
# Run unit tests (fast, mocked)
pytest tests/unit/ -v

# Run all tests
pytest tests/ -v
```

---

## 📝 After Deployment Success

**Next tasks:**
1. Update WEEK-1-DAY-1-DEPLOYMENT.md with completion status
2. Test PostgreSQL connectivity
3. Create integration tests (Week 1 Day 2)
4. Document learnings and gotchas

---

## 🔧 Troubleshooting

### If deployment fails again:

**Check GCP authentication:**
```bash
gcloud auth list
gcloud auth application-default print-access-token
```

**Check Pulumi state:**
```bash
pulumi stack
pulumi refresh
```

**Retry deployment:**
```bash
pulumi up --yes
```

### If you want to start fresh:

**Destroy all resources:**
```bash
pulumi destroy --yes
```

**Then re-deploy:**
```bash
pulumi up --yes
```

---

## 💡 Pro Tips

1. **Watch deployment in browser** - Pulumi shows live URL
2. **VPC connector is slow** - Don't worry if it takes 10 minutes
3. **Cloud SQL is slowest** - Expected to take 10-15 minutes
4. **Check cost** - Resources start charging immediately
5. **Save outputs** - PostgreSQL password only shown once without `--show-secrets`

---

## 🎯 Success Criteria

**Deployment is successful when you see:**

```
Outputs:
  + vpc_id: "projects/apex-memory-dev/global/networks/apex-memory-vpc-XXXXX"
  + subnet_id: "projects/apex-memory-dev/regions/us-central1/subnetworks/apex-db-subnet-XXXXX"
  + vpc_connector_id: "projects/apex-memory-dev/locations/us-central1/connectors/apex-vpc-connector"
  + postgres_private_ip: "10.1.0.X"
  + postgres_connection_name: "apex-memory-dev:us-central1:apex-postgres-dev"
  + database_name: "apex_memory"
  + postgres_user: "apex"

Resources:
    + 11 created
    13 unchanged
```

---

**Once deployed, Week 1 Day 1 is COMPLETE! 🎉**

Total Day 1 time: ~4-5 hours (including prerequisite setup)
Week 1 remaining: Days 2-4 (16-20 hours for tests and documentation)
