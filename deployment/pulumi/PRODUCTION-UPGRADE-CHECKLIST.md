# Production Upgrade Checklist

**From:** Development (db-f1-micro) → **To:** Production (db-n1-standard-1+)
**Timeline:** 2-4 hours (mostly waiting for GCP provisioning)
**Downtime:** ~5-10 minutes (instance restart)

---

## Prerequisites

### Before You Begin

- [ ] **Backup Current Data** - Create manual backup before upgrade
  ```bash
  gcloud sql backups create \
    --instance=apex-postgres-dev \
    --project=apex-memory-dev \
    --description="Pre-production-upgrade backup"
  ```

- [ ] **Verify Current State**
  ```bash
  # Instance status
  gcloud sql instances describe apex-postgres-dev --project=apex-memory-dev

  # Database size
  psql -h 127.0.0.1 -U apex -d apex_memory -c "SELECT pg_size_pretty(pg_database_size('apex_memory'));"

  # Connection count
  psql -h 127.0.0.1 -U apex -d apex_memory -c "SELECT count(*) FROM pg_stat_activity;"
  ```

- [ ] **Document Current Configuration**
  ```bash
  # Export current settings
  gcloud sql instances describe apex-postgres-dev \
    --project=apex-memory-dev \
    --format=json > /tmp/apex-postgres-current-config.json
  ```

- [ ] **Notify Stakeholders** - Schedule maintenance window (5-10 minutes downtime)

- [ ] **Test Plan Ready** - Have smoke tests ready to verify after upgrade

---

## Phase 1: Cloud SQL Instance Upgrade (30-45 minutes)

### 1.1 Increase Instance Tier

**Current:** db-f1-micro (1 vCPU, 1GB RAM)
**Target:** db-n1-standard-1 (1 vCPU, 3.75GB RAM)

```bash
# Upgrade instance tier
gcloud sql instances patch apex-postgres-dev \
  --tier=db-n1-standard-1 \
  --project=apex-memory-dev
```

**Expected Duration:** 5-10 minutes
**Downtime:** Yes (~5 minutes)

**Verification:**
```bash
# Check new tier
gcloud sql instances describe apex-postgres-dev \
  --project=apex-memory-dev \
  --format="value(settings.tier)"
```

**Expected Output:** `db-n1-standard-1`

- [ ] Tier upgrade complete
- [ ] Instance status: RUNNABLE
- [ ] Can connect to database

---

### 1.2 Update Database Flags

**Update shared_buffers to use new RAM headroom:**

```bash
gcloud sql instances patch apex-postgres-dev \
  --database-flags=max_connections=250,shared_buffers=262144 \
  --project=apex-memory-dev
```

**Changes:**
- `max_connections`: 100 → 250 (db-n1-standard-1 supports up to 300)
- `shared_buffers`: 78643 KB → 262144 KB (256MB, ~25% of 3.75GB RAM)

**Expected Duration:** 2-3 minutes (no restart needed for these flags)

**Verification:**
```sql
-- Connect via psql
psql -h 127.0.0.1 -U apex -d apex_memory

-- Check flags
SHOW max_connections;  -- Should be 250
SHOW shared_buffers;   -- Should be 256MB
```

- [ ] Database flags updated
- [ ] Values verified in PostgreSQL

---

### 1.3 Increase Disk Size

**Current:** 10GB
**Target:** 50GB (production standard)

```bash
gcloud sql instances patch apex-postgres-dev \
  --storage-size=50 \
  --project=apex-memory-dev
```

**Expected Duration:** Immediate (no restart)

**Note:** Disk size can only be increased, never decreased.

**Verification:**
```bash
gcloud sql instances describe apex-postgres-dev \
  --project=apex-memory-dev \
  --format="value(settings.dataDiskSizeGb)"
```

- [ ] Disk size increased to 50GB
- [ ] No errors during resize

---

### 1.4 Enable High Availability (REGIONAL)

**Current:** ZONAL (single zone)
**Target:** REGIONAL (multi-zone with automatic failover)

```bash
gcloud sql instances patch apex-postgres-dev \
  --availability-type=REGIONAL \
  --project=apex-memory-dev
```

**Expected Duration:** 10-15 minutes
**Downtime:** Yes (~5 minutes for initial setup)

**What Happens:**
- GCP creates standby instance in different zone
- Synchronous replication enabled
- Automatic failover configured (<60 seconds)

**Verification:**
```bash
gcloud sql instances describe apex-postgres-dev \
  --project=apex-memory-dev \
  --format="value(settings.availabilityType)"
```

**Expected Output:** `REGIONAL`

- [ ] HA enabled
- [ ] Standby instance created
- [ ] Replication lag < 1 second

---

## Phase 2: Security Hardening (15-20 minutes)

### 2.1 Enable Deletion Protection

```bash
gcloud sql instances patch apex-postgres-dev \
  --deletion-protection \
  --project=apex-memory-dev
```

**What This Does:**
- Prevents accidental deletion of instance
- Must explicitly disable before destroying
- No performance impact

**Verification:**
```bash
gcloud sql instances describe apex-postgres-dev \
  --project=apex-memory-dev \
  --format="value(settings.deletionProtectionEnabled)"
```

**Expected Output:** `True`

- [ ] Deletion protection enabled

---

### 2.2 Enable SSL Enforcement

**Current:** ALLOW_UNENCRYPTED_AND_ENCRYPTED
**Target:** ENCRYPTED_ONLY

```bash
gcloud sql instances patch apex-postgres-dev \
  --database-flags=ssl_mode=ENCRYPTED_ONLY \
  --project=apex-memory-dev
```

**Note:** This may break connections that don't use SSL. Test first!

**Verification:**
```sql
-- Should fail (no SSL)
psql "host=10.115.5.3 port=5432 dbname=apex_memory user=apex sslmode=disable"

-- Should succeed (SSL required)
psql "host=10.115.5.3 port=5432 dbname=apex_memory user=apex sslmode=require"
```

**Alternative (Recommended for Cloud Run):** Keep `ALLOW_UNENCRYPTED_AND_ENCRYPTED` since Cloud SQL Proxy handles encryption.

- [ ] SSL mode reviewed
- [ ] Decision documented (enforce or allow unencrypted via proxy)

---

### 2.3 Store Password in Secret Manager

**Current:** Password in `/tmp/apex-postgres-password.txt`
**Target:** GCP Secret Manager

```bash
# Create secret
echo -n "dtB6tmTenuNYyXKFwOu/V+OYH4xHN03OPauWJ85Jx88=" | \
  gcloud secrets create db-password \
  --data-file=- \
  --project=apex-memory-dev \
  --replication-policy="automatic"

# Grant Cloud Run access
gcloud secrets add-iam-policy-binding db-password \
  --member="serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor" \
  --project=apex-memory-dev
```

**Verification:**
```bash
# Test secret retrieval
gcloud secrets versions access latest --secret=db-password --project=apex-memory-dev
```

**Expected Output:** Password value

- [ ] Secret created in Secret Manager
- [ ] IAM policy binding configured
- [ ] Secret accessible by Cloud Run service account

---

### 2.4 Enable Cloud SQL Audit Logs

```bash
# Enable audit logs via gcloud (if supported) or GCP Console
# Navigate to: Cloud SQL → apex-postgres-dev → Edit → Flags
# Add: cloudsql.enable_pgaudit = on
```

**Alternative: Via Console**
1. Go to https://console.cloud.google.com/sql/instances/apex-postgres-dev/edit?project=apex-memory-dev
2. Scroll to "Flags"
3. Add flag: `cloudsql.enable_pgaudit = on`
4. Save

**What This Logs:**
- Connection attempts
- Failed authentication
- DDL statements (CREATE, ALTER, DROP)
- DML statements (INSERT, UPDATE, DELETE) - optional

**Verification:**
```bash
# Check logs in Cloud Logging
gcloud logging read "resource.type=cloudsql_database" \
  --project=apex-memory-dev \
  --limit=10
```

- [ ] Audit logs enabled
- [ ] Logs visible in Cloud Logging

---

### 2.5 Rotate Database Password

**Good Practice:** Rotate password during production upgrade

```bash
# Generate new password
NEW_PASSWORD=$(openssl rand -base64 32)

# Update password
gcloud sql users set-password apex \
  --instance=apex-postgres-dev \
  --password="$NEW_PASSWORD" \
  --project=apex-memory-dev

# Update Secret Manager
echo -n "$NEW_PASSWORD" | \
  gcloud secrets versions add db-password --data-file=- --project=apex-memory-dev

# Test connection with new password
psql "host=127.0.0.1 port=5432 dbname=apex_memory user=apex password=$NEW_PASSWORD"
```

- [ ] Password rotated
- [ ] Secret Manager updated
- [ ] Connection tested with new password
- [ ] Application configs updated (Cloud Run env vars)

---

## Phase 3: VPC Connector Upgrade (20-30 minutes)

### 3.1 Create Production VPC Connector

**Current:** e2-micro × 2-3 instances
**Target:** e2-standard-4 × 3-10 instances

**Update Pulumi code:**

```python
# modules/networking.py
vpc_connector = gcp.vpcaccess.Connector(
    "apex-vpc-connector-prod",
    name="apex-vpc-connector-prod",
    region=region,
    network=vpc.name,
    ip_cidr_range="10.8.1.0/28",  # Different CIDR
    machine_type="e2-standard-4",  # Upgraded from e2-micro
    min_instances=3,               # Higher min
    max_instances=10,              # Higher max
    project=project_id,
)
```

**Deploy:**
```bash
cd /Users/richardglaubitz/Projects/Apex-Memory-System-Development/deployment/pulumi
source .venv/bin/activate
pulumi up --yes
```

**Expected Duration:** 10-15 minutes (connector creation)

**Verification:**
```bash
gcloud compute networks vpc-access connectors describe apex-vpc-connector-prod \
  --region=us-central1 \
  --project=apex-memory-dev
```

- [ ] Production VPC connector created
- [ ] Status: READY
- [ ] Machine type: e2-standard-4

---

### 3.2 Update Cloud Run to Use New Connector

```bash
# Update Cloud Run service
gcloud run services update apex-memory-api \
  --vpc-connector=apex-vpc-connector-prod \
  --vpc-egress=private-ranges-only \
  --region=us-central1 \
  --project=apex-memory-dev
```

**Verification:**
```bash
gcloud run services describe apex-memory-api \
  --region=us-central1 \
  --project=apex-memory-dev \
  --format="value(spec.template.spec.containers[0].resources.limits.vpcAccess)"
```

- [ ] Cloud Run updated to use production connector
- [ ] Connection to PostgreSQL still works

---

### 3.3 Delete Old VPC Connector (Optional)

**Wait 24-48 hours** to ensure no issues, then delete:

```bash
gcloud compute networks vpc-access connectors delete apex-vpc-connector \
  --region=us-central1 \
  --project=apex-memory-dev
```

- [ ] Old connector deleted (after 24-48 hours)

---

## Phase 4: Monitoring & Alerting (30-45 minutes)

### 4.1 Enable VPC Flow Logs

```bash
gcloud compute networks subnets update apex-db-subnet \
  --region=us-central1 \
  --enable-flow-logs \
  --logging-aggregation-interval=interval-5-sec \
  --logging-flow-sampling=0.5 \
  --project=apex-memory-dev
```

**What This Logs:**
- Network traffic patterns
- Connection attempts
- Bandwidth usage
- Security analysis

**Verification:**
```bash
gcloud logging read "resource.type=gce_subnetwork" \
  --project=apex-memory-dev \
  --limit=5
```

- [ ] VPC Flow Logs enabled
- [ ] Logs visible in Cloud Logging

---

### 4.2 Create Cloud Monitoring Alerts

**Alert 1: CPU Utilization > 80%**

```bash
# Create via gcloud (or use GCP Console)
gcloud alpha monitoring policies create \
  --notification-channels=CHANNEL_ID \
  --display-name="Cloud SQL - High CPU" \
  --condition-display-name="CPU > 80%" \
  --condition-threshold-value=0.8 \
  --condition-threshold-duration=300s \
  --project=apex-memory-dev
```

**Alert 2: Memory Utilization > 80%**

**Alert 3: Disk Utilization > 80%**

**Alert 4: Connection Count > 200 (80% of 250)**

**Alert 5: Replication Lag > 10 seconds**

**Recommended Tool:** Use GCP Console for easier alert creation
- Navigate to: https://console.cloud.google.com/monitoring/alerting?project=apex-memory-dev

- [ ] CPU utilization alert configured
- [ ] Memory utilization alert configured
- [ ] Disk utilization alert configured
- [ ] Connection count alert configured
- [ ] Replication lag alert configured (if HA enabled)

---

### 4.3 Create Monitoring Dashboard

**Recommended:** Use Grafana or GCP Cloud Monitoring

**Key Metrics:**
- CPU utilization (%)
- Memory utilization (%)
- Disk utilization (%)
- Active connections
- Queries per second
- Replication lag (if HA)
- Backup success/failure

**GCP Console:**
https://console.cloud.google.com/monitoring/dashboards/create?project=apex-memory-dev

- [ ] Monitoring dashboard created
- [ ] All key metrics visible

---

## Phase 5: Production Validation (30-60 minutes)

### 5.1 Performance Testing

**Test 1: Connection Pooling**
```python
# Test script: test_connection_pool.py
from sqlalchemy import create_engine, text
import time

engine = create_engine(
    "postgresql://apex:PASSWORD@127.0.0.1:5432/apex_memory",
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
)

# Test 50 concurrent connections
for i in range(50):
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print(f"Connection {i}: {result.fetchone()}")
```

**Expected:** All connections succeed, no "too many connections" errors

- [ ] Connection pooling test passed
- [ ] No connection errors under load

---

**Test 2: Query Performance**
```sql
-- Create test data
CREATE TABLE test_performance (
    id SERIAL PRIMARY KEY,
    data TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

INSERT INTO test_performance (data)
SELECT 'test data ' || generate_series(1, 100000);

-- Test query performance
EXPLAIN ANALYZE SELECT * FROM test_performance WHERE id < 10000;
```

**Expected:** Faster than db-f1-micro (more RAM for caching)

- [ ] Query performance improved
- [ ] Explain plans show efficient execution

---

### 5.2 Backup Testing

**Test Full Backup:**
```bash
# Trigger on-demand backup
gcloud sql backups create \
  --instance=apex-postgres-dev \
  --description="Production validation backup" \
  --project=apex-memory-dev
```

**Test Point-in-Time Recovery:**
```bash
# Clone instance to 1 hour ago
gcloud sql instances clone apex-postgres-dev apex-postgres-test \
  --point-in-time="$(date -u -d '1 hour ago' '+%Y-%m-%dT%H:%M:%SZ')" \
  --project=apex-memory-dev
```

**Verify:**
```bash
# Connect to clone
psql "host=CLONE_IP port=5432 dbname=apex_memory user=apex"

# Check data
SELECT count(*) FROM your_table;
```

**Cleanup:**
```bash
gcloud sql instances delete apex-postgres-test --project=apex-memory-dev
```

- [ ] On-demand backup successful
- [ ] Point-in-time recovery tested
- [ ] Clone verified
- [ ] Test instance deleted

---

### 5.3 Failover Testing (REGIONAL only)

**Trigger Manual Failover:**
```bash
gcloud sql instances failover apex-postgres-dev --project=apex-memory-dev
```

**What Happens:**
- Primary instance becomes standby
- Standby instance becomes primary
- Downtime: < 60 seconds
- Connections drop and reconnect

**Monitor:**
```bash
# Watch instance status
watch -n 2 'gcloud sql instances describe apex-postgres-dev --project=apex-memory-dev --format="value(state)"'
```

**Verify:**
```bash
# Check replication lag after failover
# Should return to < 1 second quickly
```

- [ ] Manual failover successful
- [ ] Downtime < 60 seconds
- [ ] Replication recovered
- [ ] Application reconnected

---

## Phase 6: Cost Optimization (15-30 minutes)

### 6.1 Review and Enable Committed Use Discounts

**Current:** On-demand pricing
**Target:** Committed use (1-year or 3-year)

**Savings:**
- 1-year commitment: 37% discount
- 3-year commitment: 55% discount

**Calculate Savings:**
```
Monthly cost (on-demand): ~$100-150
1-year commitment: ~$63-95/month (save ~$37-55/month)
3-year commitment: ~$45-68/month (save ~$55-82/month)
```

**Enable:**
https://console.cloud.google.com/compute/commitments/create?project=apex-memory-dev

- [ ] Committed use discount reviewed
- [ ] Decision documented (on-demand vs. committed)

---

### 6.2 Optimize Backup Retention

**Current:** 7 days
**Consider:** Longer retention for production

**Options:**
- 7 days: Minimal cost, sufficient for most cases
- 30 days: Recommended for production (+$5-10/month)
- 90 days: Compliance requirements (+$15-25/month)

```bash
# Update retention (if desired)
gcloud sql instances patch apex-postgres-dev \
  --backup-start-time=02:00 \
  --retained-backups-count=30 \
  --project=apex-memory-dev
```

- [ ] Backup retention reviewed
- [ ] Retention policy updated (if needed)

---

### 6.3 Review Network Egress Costs

**Monitor:**
- Network egress to internet (most expensive)
- Egress to other GCP regions (cheaper)
- Egress within same region (cheapest)

**Optimize:**
- Use Cloud CDN for static content
- Keep services in same region
- Use VPC for internal communication

- [ ] Network egress reviewed
- [ ] Optimization opportunities documented

---

## Phase 7: Documentation Update (15-20 minutes)

### 7.1 Update Infrastructure Documentation

**Files to Update:**
- `deployment/pulumi/DEPLOYMENT-COMPLETE.md` - Update tier, costs
- `deployment/pulumi/DEVELOPER-CONNECTION-GUIDE.md` - Update connection examples
- `deployment/pulumi/ARCHITECTURE-DIAGRAM.md` - Update tier, HA status

```bash
# Update tier references
# db-f1-micro → db-n1-standard-1
# ZONAL → REGIONAL
# $25-35/month → $110-165/month
```

- [ ] DEPLOYMENT-COMPLETE.md updated
- [ ] DEVELOPER-CONNECTION-GUIDE.md updated
- [ ] ARCHITECTURE-DIAGRAM.md updated

---

### 7.2 Update Pulumi Code

**Files to Update:**
- `modules/databases.py` - Tier, HA, flags
- `modules/networking.py` - VPC connector
- `__main__.py` - Outputs

```python
# modules/databases.py
tier="db-n1-standard-1",  # Updated from db-f1-micro
availability_type="REGIONAL",  # Updated from ZONAL
deletion_protection=True,  # Updated from False

database_flags=[
    gcp.sql.DatabaseInstanceSettingsDatabaseFlagArgs(
        name="max_connections",
        value="250",  # Updated from 100
    ),
    gcp.sql.DatabaseInstanceSettingsDatabaseFlagArgs(
        name="shared_buffers",
        value="262144",  # Updated from 78643
    ),
]
```

- [ ] Pulumi code updated
- [ ] Changes committed to git

---

### 7.3 Create Production Runbook

**Create:** `deployment/pulumi/PRODUCTION-RUNBOOK.md`

**Contents:**
- Connection details (with Secret Manager references)
- Backup procedures
- Restore procedures
- Failover procedures
- Monitoring dashboards
- Alert contacts
- Escalation procedures
- Common issues and solutions

- [ ] Production runbook created

---

## Phase 8: Final Verification (10-15 minutes)

### 8.1 End-to-End Smoke Test

**Test Flow:**
1. API call → Cloud Run
2. Cloud Run → Cloud SQL (via VPC connector)
3. Query execution
4. Response returned

```bash
# Test API endpoint
curl -X POST https://YOUR_CLOUD_RUN_URL/api/v1/documents \
  -H "Content-Type: application/json" \
  -d '{"content": "Test document", "metadata": {}}'

# Verify in database
psql -h 127.0.0.1 -U apex -d apex_memory -c "SELECT * FROM documents ORDER BY created_at DESC LIMIT 1;"
```

- [ ] End-to-end test successful
- [ ] API → Database → Response working

---

### 8.2 Verify All Metrics

```bash
# CPU utilization < 50% (plenty of headroom)
# Memory utilization < 50%
# Disk utilization < 20% (40GB free out of 50GB)
# Active connections < 50 (200 headroom)
# Replication lag < 1 second (if HA)
```

- [ ] All metrics in healthy range

---

### 8.3 Verify Monitoring & Alerts

- [ ] CPU alert firing threshold tested (optional: load test)
- [ ] Alerts sent to correct channels
- [ ] Dashboard shows all metrics
- [ ] Logs flowing to Cloud Logging

---

## Rollback Plan

### If Issues Encountered

**Option 1: Restore from Backup (Data Loss Possible)**
```bash
# Restore to backup taken before upgrade
gcloud sql backups restore BACKUP_ID \
  --instance=apex-postgres-dev \
  --project=apex-memory-dev
```

**Option 2: Clone to Previous Point-in-Time**
```bash
# Clone to just before upgrade started
gcloud sql instances clone apex-postgres-dev apex-postgres-rollback \
  --point-in-time="2025-11-15T14:00:00Z" \
  --project=apex-memory-dev
```

**Option 3: Downgrade Tier (Not Recommended)**
- Cannot downgrade to smaller tier directly
- Must export data, recreate instance, re-import

---

## Post-Upgrade Monitoring

### First 24 Hours

**Monitor Closely:**
- [ ] CPU utilization trends
- [ ] Memory utilization trends
- [ ] Connection count patterns
- [ ] Query performance metrics
- [ ] Replication lag (if HA)
- [ ] Backup success
- [ ] Error rates

### First Week

**Review:**
- [ ] Cost actual vs. estimated
- [ ] Performance improvements documented
- [ ] Any unexpected issues documented
- [ ] Team feedback collected

### First Month

**Optimize:**
- [ ] Right-size instance tier (if needed)
- [ ] Adjust connection pools
- [ ] Fine-tune database flags
- [ ] Optimize backup schedule
- [ ] Review committed use discounts

---

## Summary Checklist

### Phase 1: Cloud SQL Upgrade
- [ ] Instance tier upgraded (db-n1-standard-1)
- [ ] Database flags updated (max_connections: 250, shared_buffers: 256MB)
- [ ] Disk size increased (50GB)
- [ ] High availability enabled (REGIONAL)

### Phase 2: Security Hardening
- [ ] Deletion protection enabled
- [ ] SSL enforcement reviewed
- [ ] Password stored in Secret Manager
- [ ] Cloud SQL audit logs enabled
- [ ] Password rotated

### Phase 3: VPC Connector Upgrade
- [ ] Production VPC connector created (e2-standard-4)
- [ ] Cloud Run updated to use new connector
- [ ] Old connector deleted (after 24-48 hours)

### Phase 4: Monitoring & Alerting
- [ ] VPC Flow Logs enabled
- [ ] Cloud Monitoring alerts configured (5 alerts)
- [ ] Monitoring dashboard created

### Phase 5: Production Validation
- [ ] Connection pooling tested
- [ ] Query performance tested
- [ ] Backup tested
- [ ] Failover tested (if HA enabled)

### Phase 6: Cost Optimization
- [ ] Committed use discounts reviewed
- [ ] Backup retention reviewed
- [ ] Network egress reviewed

### Phase 7: Documentation Update
- [ ] Infrastructure documentation updated
- [ ] Pulumi code updated
- [ ] Production runbook created

### Phase 8: Final Verification
- [ ] End-to-end smoke test passed
- [ ] All metrics healthy
- [ ] Monitoring and alerts verified

---

**Upgrade Complete! 🎉**

**New Configuration:**
- Instance: db-n1-standard-1 (1 vCPU, 3.75GB RAM)
- Availability: REGIONAL (HA enabled)
- Disk: 50GB SSD
- Max Connections: 250
- Shared Buffers: 256MB
- Deletion Protection: Enabled
- Cost: ~$110-165/month (vs. $25-35/month dev)

**Next Steps:**
- Monitor for 24-48 hours
- Collect performance metrics
- Document any issues
- Schedule next review (1 week)

---

**Last Updated:** 2025-11-15
**Upgrade Version:** 1.0 (Development → Production)
