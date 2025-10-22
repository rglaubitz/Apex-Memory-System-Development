# Apex Memory System - Update & Iteration Workflow

**Purpose:** Complete guide for deploying updates, fixes, and new features after initial deployment.

**Audience:** Solo developer managing production system.

**Use This When:**
- Adding new features
- Fixing bugs
- Updating dependencies
- Making database changes
- Responding to production incidents

---

## Table of Contents

- [Standard Update Workflow](#standard-update-workflow)
- [Hotfix Workflow](#hotfix-workflow)
- [Database Migration Workflow](#database-migration-workflow)
- [Rollback Procedures](#rollback-procedures)
- [Testing in Production](#testing-in-production)
- [Common Scenarios](#common-scenarios)

---

## Standard Update Workflow

**Use this for:** New features, non-urgent bug fixes, improvements

**Timeline:** 1-4 hours (depending on complexity)

---

### Step 1: Develop Locally

```bash
cd /Users/richardglaubitz/Projects/apex-memory-system

# Create feature branch
git checkout -b feature/new-feature-name

# Make your changes
# ... edit code ...

# Run tests locally (REQUIRED before deploying)
pytest

# Expected: 156/156 tests passing
# If ANY tests fail, fix them before proceeding
```

**Critical:** ALL tests must pass locally before pushing to production.

---

### Step 2: Commit Changes

```bash
# Stage changes
git add .

# Commit with descriptive message
git commit -m "feat: Add new feature description"

# Push to GitHub
git push origin feature/new-feature-name
```

**Commit Message Conventions:**
- `feat:` New feature
- `fix:` Bug fix
- `refactor:` Code refactoring
- `docs:` Documentation changes
- `test:` Test updates
- `chore:` Maintenance tasks

---

### Step 3: Create Pull Request (Optional but Recommended)

**Why PR?** Even as solo developer:
- Review your own changes before merge
- CI/CD runs tests automatically
- History of decisions
- Rollback easier with PR refs

**Process:**
1. Go to GitHub repository
2. Click "Pull Request"
3. Select `feature/new-feature-name` → `main`
4. Review changes yourself
5. Wait for CI/CD to run tests
6. Merge when tests pass

---

### Step 4: Automatic Deployment

**When you merge to `main` (or push directly to `main`):**

1. **Cloud Build Triggers Automatically**
   - Runs all 156 tests
   - Builds Docker image
   - Pushes to Artifact Registry
   - Deploys to Cloud Run

2. **Monitor Build Progress:**
   ```bash
   # Watch builds
   gcloud builds list --limit=5

   # Stream logs for latest build
   BUILD_ID=$(gcloud builds list --limit=1 --format="value(id)")
   gcloud builds log $BUILD_ID --stream
   ```

3. **Build Stages (Typical 10-15 minutes):**
   - Install dependencies: 2-3 min
   - Run tests: 5-8 min
   - Build Docker image: 3-4 min
   - Deploy to Cloud Run: 2-3 min

---

### Step 5: Post-Deployment Validation

**Immediately after deployment completes:**

```bash
# Get API URL
export API_URL=$(gcloud run services describe apex-memory-api \
  --region=us-central1 --format="value(status.url)")

# Test 1: Health check
curl $API_URL/health
# Expected: {"status": "healthy"}

# Test 2: Smoke test (test your new feature)
curl -X POST $API_URL/your-new-endpoint \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'

# Test 3: Check logs for errors
gcloud run services logs read apex-memory-api --region=us-central1 --limit=50 | grep ERROR
# Expected: No errors (or only expected warnings)
```

---

### Step 6: Monitor for 15-30 Minutes

**Watch these metrics in Cloud Console:**

1. **Navigate to:** https://console.cloud.google.com/monitoring
2. **Check:**
   - Error rate (should be <0.1%)
   - Latency P95 (should be <1s)
   - Request count (should be normal)
   - No spike in 5xx errors

**If any issues detected:**
- See [Rollback Procedures](#rollback-procedures)

**If all looks good:**
- Deployment successful! ✅
- Document changes in CHANGELOG.md (optional)

---

## Hotfix Workflow

**Use this for:** Production bugs, urgent fixes, security patches

**Timeline:** 30 minutes - 2 hours

---

### Emergency Hotfix Process

**Step 1: Assess Impact (2-5 minutes)**

```bash
# Check error logs
gcloud run services logs read apex-memory-api --region=us-central1 --limit=100 | grep ERROR

# Check error rate in Monitoring
# Navigate to: https://console.cloud.google.com/monitoring

# Determine:
# - How many users affected?
# - Is system completely down or partial?
# - Is data at risk?
```

**Decision Matrix:**
- 🔴 **System down (5xx errors >50%):** Immediate rollback, then fix
- 🟡 **Partial degradation:** Hotfix deploy (skip PR, fast-track)
- 🟢 **Minor issue (<1% users):** Standard workflow acceptable

---

**Step 2: Quick Fix (15-30 minutes)**

```bash
# Work on main branch directly (emergency only!)
git checkout main
git pull origin main

# Make minimal fix (change only what's necessary)
# ... edit code ...

# Run relevant tests ONLY (not full suite if time-critical)
pytest tests/unit/test_affected_module.py -v

# If tests pass:
git add .
git commit -m "hotfix: Fix critical production bug - [brief description]"
git push origin main

# Cloud Build will auto-deploy (10-15 min)
```

---

**Step 3: Monitor Deployment**

```bash
# Watch build
gcloud builds list --limit=1

BUILD_ID=$(gcloud builds list --limit=1 --format="value(id)")
gcloud builds log $BUILD_ID --stream

# Once deployed, immediately test
curl $API_URL/health
curl $API_URL/affected-endpoint
```

---

**Step 4: Validate Fix**

```bash
# Check if error rate dropped
# Cloud Console → Monitoring → Dashboards

# Check logs for original error
gcloud run services logs read apex-memory-api --region=us-central1 --limit=100 | grep "ORIGINAL_ERROR_MESSAGE"
# Expected: No new occurrences

# Monitor for 30 minutes before declaring success
```

---

**Step 5: Post-Hotfix Cleanup**

```bash
# After fix validated, create proper PR with explanation
git checkout -b hotfix/detailed-fix-description

# Add tests for the bug (prevent regression)
# ... create test cases ...

pytest tests/unit/test_new_regression_tests.py

git add .
git commit -m "test: Add regression tests for hotfix"
git push origin hotfix/detailed-fix-description

# Create PR, document what happened, merge
```

---

## Database Migration Workflow

**Use this for:** Schema changes, new tables/columns, data migrations

**⚠️ CAUTION:** Database changes require extra care.

---

### Safe Migration Process

**Step 1: Create Migration Script**

```bash
# Install Alembic (if not already)
pip install alembic

# Initialize Alembic (first time only)
alembic init alembic

# Create migration
alembic revision -m "Add new_column to documents table"

# Edit generated migration file
# alembic/versions/XXXX_add_new_column_to_documents_table.py
```

**Example Migration:**
```python
from alembic import op
import sqlalchemy as sa

def upgrade():
    # Add column (nullable first for safety)
    op.add_column('documents', sa.Column('new_column', sa.String(), nullable=True))

def downgrade():
    # Rollback
    op.drop_column('documents', 'new_column')
```

---

**Step 2: Test Migration Locally**

```bash
# Run migration on local database
alembic upgrade head

# Verify schema
psql -d apex_memory -c "\d documents"
# Expected: new_column present

# Test rollback
alembic downgrade -1

# Re-run upgrade
alembic upgrade head
```

---

**Step 3: Apply to Production (Zero-Downtime)**

**⚠️ IMPORTANT:** Use expand-migrate-contract pattern for zero downtime.

**Phase 1: Expand (Add new, keep old)**
```bash
# Migration adds NEW column (nullable, with default)
# Old code continues using OLD column
# Deploy migration BEFORE code change

gcloud sql connect apex-postgres --user=postgres

# Once connected:
\c apex_memory

-- Add new column
ALTER TABLE documents ADD COLUMN new_field VARCHAR(255) DEFAULT '';

-- Verify
\d documents

\q
```

**Phase 2: Migrate (Deploy new code)**
```bash
# Update code to write to BOTH old and new columns
# Deploy via standard workflow

git add .
git commit -m "feat: Dual-write to old and new columns"
git push origin main
```

**Phase 3: Backfill (Copy old data to new)**
```bash
# Run backfill script (during low-traffic period)
gcloud sql connect apex-postgres --user=postgres

# Once connected:
\c apex_memory

-- Backfill data
UPDATE documents SET new_field = old_field WHERE new_field IS NULL OR new_field = '';

-- Verify
SELECT COUNT(*) FROM documents WHERE new_field IS NULL OR new_field = '';
-- Expected: 0

\q
```

**Phase 4: Contract (Remove old, keep new)**
```bash
# Update code to read/write ONLY new column
# Deploy via standard workflow

git add .
git commit -m "refactor: Switch to new_field exclusively"
git push origin main

# After validation period (24-48 hours), drop old column
gcloud sql connect apex-postgres --user=postgres

\c apex_memory

-- Drop old column
ALTER TABLE documents DROP COLUMN old_field;

\q
```

---

## Rollback Procedures

**When to rollback:**
- Error rate spike (>5% errors)
- Critical feature broken
- Data corruption detected
- Latency P99 > 5s

**⏱️ Time to rollback:** < 5 minutes

---

### Method 1: Cloud Run Instant Rollback (Recommended)

**Fastest rollback (< 2 minutes):**

```bash
# Step 1: List recent revisions
gcloud run revisions list --service=apex-memory-api --region=us-central1

# Example output:
# NAME                           ACTIVE  SERVICE            DEPLOYED
# apex-memory-api-00005-abc      yes     apex-memory-api    2025-01-20
# apex-memory-api-00004-xyz      no      apex-memory-api    2025-01-19

# Step 2: Rollback to previous revision
gcloud run services update-traffic apex-memory-api \
  --region=us-central1 \
  --to-revisions=apex-memory-api-00004-xyz=100

# Step 3: Validate
curl $API_URL/health
# Expected: {"status": "healthy"}

# Step 4: Check logs
gcloud run services logs read apex-memory-api --region=us-central1 --limit=50
# Expected: No errors
```

**Rollback complete! Traffic now on previous stable version.**

---

### Method 2: Redeploy Previous Docker Image

**Use if need to rollback multiple versions:**

```bash
# Step 1: Find previous good image
gcloud artifacts docker images list \
  us-central1-docker.pkg.dev/$PROJECT_ID/apex-containers/apex-memory-api

# Step 2: Deploy specific image tag
export PREVIOUS_IMAGE="us-central1-docker.pkg.dev/$PROJECT_ID/apex-containers/apex-memory-api:GOOD_TAG"

gcloud run deploy apex-memory-api \
  --image=$PREVIOUS_IMAGE \
  --region=us-central1 \
  --platform=managed

# Step 3: Validate
curl $API_URL/health
```

---

### Method 3: Git Revert + Redeploy

**Use for database migration issues:**

```bash
# Step 1: Revert commit
git revert HEAD  # Reverts last commit
# or
git revert COMMIT_SHA  # Reverts specific commit

# Step 2: Push (triggers auto-deploy)
git push origin main

# Step 3: Wait for Cloud Build (10-15 min)
# Step 4: Validate deployment
```

---

## Testing in Production

**Strategies for safe production testing:**

---

### 1. Feature Flags (Recommended)

**Add to your code:**
```python
# config.py
FEATURE_FLAGS = {
    "enable_new_feature": os.getenv("ENABLE_NEW_FEATURE", "false").lower() == "true"
}

# your_feature.py
from config import FEATURE_FLAGS

if FEATURE_FLAGS["enable_new_feature"]:
    # New feature code
    pass
else:
    # Old code path
    pass
```

**Enable for testing:**
```bash
gcloud run services update apex-memory-api \
  --region=us-central1 \
  --update-env-vars=ENABLE_NEW_FEATURE=true
```

**Disable if issues:**
```bash
gcloud run services update apex-memory-api \
  --region=us-central1 \
  --update-env-vars=ENABLE_NEW_FEATURE=false
```

---

### 2. Canary Deployment (Advanced)

**Gradually roll out to subset of users:**

```bash
# Deploy new version
gcloud run deploy apex-memory-api-canary \
  --image=$NEW_IMAGE \
  --region=us-central1 \
  --tag=canary

# Split traffic: 95% stable, 5% canary
gcloud run services update-traffic apex-memory-api \
  --region=us-central1 \
  --to-revisions=STABLE=95,CANARY=5

# Monitor for 30 minutes

# If good, increase to 50%
gcloud run services update-traffic apex-memory-api \
  --region=us-central1 \
  --to-revisions=STABLE=50,CANARY=50

# If all good, go 100% canary
gcloud run services update-traffic apex-memory-api \
  --region=us-central1 \
  --to-revisions=CANARY=100
```

---

### 3. A/B Testing

**Test two versions simultaneously:**

```bash
# Use Cloud Run tags
gcloud run deploy apex-memory-api \
  --image=$IMAGE_A \
  --tag=version-a

gcloud run deploy apex-memory-api \
  --image=$IMAGE_B \
  --tag=version-b

# Split traffic
gcloud run services update-traffic apex-memory-api \
  --to-tags=version-a=50,version-b=50

# Measure metrics, pick winner
```

---

## Common Scenarios

### Scenario 1: Update Python Dependency

**Example:** Upgrade FastAPI from 0.100.0 to 0.110.0

```bash
# Step 1: Update locally
pip install fastapi==0.110.0
pip freeze > requirements.txt

# Step 2: Test locally
pytest

# Step 3: Deploy
git add requirements.txt
git commit -m "chore: Upgrade FastAPI to 0.110.0"
git push origin main

# Step 4: Monitor deployment (no rollback needed if tests pass)
```

**⚠️ For major updates (e.g., FastAPI 0.x → 1.x):**
- Test extensively locally
- Review breaking changes
- Consider feature flag for rollback option

---

### Scenario 2: Add New API Endpoint

```bash
# Step 1: Develop locally
# ... add new endpoint to src/apex_memory/api/ ...

# Step 2: Add tests
# ... create test_new_endpoint.py ...

pytest tests/integration/test_new_endpoint.py -v

# Step 3: Deploy
git add .
git commit -m "feat: Add /api/new-endpoint for X functionality"
git push origin main

# Step 4: Test in production
curl -X POST $API_URL/api/new-endpoint -d '{"test": "data"}'
```

---

### Scenario 3: Fix Production Bug

```bash
# Step 1: Reproduce locally
# ... identify bug ...

# Step 2: Write regression test FIRST
# ... create test that currently fails ...

pytest tests/unit/test_bug_regression.py -v
# Expected: FAIL (bug reproduces)

# Step 3: Fix bug
# ... implement fix ...

pytest tests/unit/test_bug_regression.py -v
# Expected: PASS

# Step 4: Deploy via hotfix workflow
git add .
git commit -m "fix: Resolve issue with X causing Y"
git push origin main
```

---

### Scenario 4: Update Environment Variable

**Example:** Change Redis connection string

```bash
# Update Secret Manager
gcloud secrets versions add redis-url --data-file=-
# (paste new URL, Ctrl+D)

# Update Cloud Run to use new secret version
gcloud run services update apex-memory-api \
  --region=us-central1 \
  --update-secrets=REDIS_URL=redis-url:latest

# Validate
gcloud run services describe apex-memory-api --region=us-central1 \
  --format="value(spec.template.spec.containers[0].env)"
```

---

### Scenario 5: Scale Resources

**Increase Cloud Run instances:**

```bash
# Increase max instances
gcloud run services update apex-memory-api \
  --region=us-central1 \
  --max-instances=20  # was 10

# Increase memory/CPU
gcloud run services update apex-memory-api \
  --region=us-central1 \
  --memory=4Gi \
  --cpu=4
```

**Upgrade database:**

```bash
# Cloud SQL vertical scaling
gcloud sql instances patch apex-postgres \
  --tier=db-n1-standard-4  # was db-n1-standard-2

# Takes 5-10 minutes, zero downtime
```

---

## Quick Reference

### Common Commands

```bash
# Deploy manually (if Cloud Build fails)
gcloud builds submit --tag us-central1-docker.pkg.dev/$PROJECT_ID/apex-containers/apex-memory-api:manual
gcloud run deploy apex-memory-api --image=us-central1-docker.pkg.dev/$PROJECT_ID/apex-containers/apex-memory-api:manual --region=us-central1

# Rollback instantly
gcloud run services update-traffic apex-memory-api --region=us-central1 --to-revisions=PREVIOUS_REVISION=100

# View logs
gcloud run services logs read apex-memory-api --region=us-central1 --limit=100

# Check service status
gcloud run services describe apex-memory-api --region=us-central1

# List all revisions
gcloud run revisions list --service=apex-memory-api --region=us-central1
```

---

## Summary

**Standard Updates:** Develop → Test → Push → Auto-deploy → Validate (1-4 hours)

**Hotfixes:** Fix → Test (minimal) → Push → Monitor closely → Post-fix cleanup (30 min - 2 hours)

**Database Changes:** Expand → Migrate → Backfill → Contract (days, not hours)

**Rollbacks:** Instant with Cloud Run traffic shifting (<5 minutes)

**Testing:** Feature flags for safe production testing

**Key Principle:** Always test locally first, monitor after deployment, rollback fast if needed.

---

**Next Steps:**

- Bookmark this page for reference
- Practice rollback procedure in staging
- Set up monitoring alerts (see [GCP-DEPLOYMENT-GUIDE.md#phase-5](GCP-DEPLOYMENT-GUIDE.md#phase-5-monitoring-setup))

---

**Last Updated:** 2025-01-20
**Version:** 1.0.0
**Author:** Claude Code (Apex Memory System Update Workflow)
