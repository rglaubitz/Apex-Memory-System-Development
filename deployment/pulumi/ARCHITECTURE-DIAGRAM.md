# Apex Memory System - GCP Infrastructure Architecture

**Deployment:** Week 1 Day 1 (Complete)
**Tier:** Development (db-f1-micro)
**Status:** ✅ Production-Ready

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           Internet                                       │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             │ HTTPS
                             ▼
                    ┌────────────────┐
                    │  Cloud Run     │
                    │  (Apex API)    │
                    └────────┬───────┘
                             │
                             │ VPC Connector (10.8.0.0/28)
                             │
┌────────────────────────────┴────────────────────────────────────────────┐
│                     VPC: apex-memory-vpc                                 │
│                     (Custom Mode, No Auto-Subnets)                       │
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  Private Subnet: apex-db-subnet (10.0.0.0/24)                   │   │
│  │  Region: us-central1                                             │   │
│  │  Private Google Access: ENABLED                                  │   │
│  │                                                                   │   │
│  │  ┌──────────────────────────────────────────────────────┐       │   │
│  │  │  Cloud SQL PostgreSQL 17                              │       │   │
│  │  │  Instance: apex-postgres-dev                          │       │   │
│  │  │  Private IP: 10.115.5.3                               │       │   │
│  │  │  Database: apex_memory                                │       │   │
│  │  │  User: apex                                           │       │   │
│  │  │                                                        │       │   │
│  │  │  Config:                                              │       │   │
│  │  │  - Tier: db-f1-micro (1 vCPU, 1GB RAM)              │       │   │
│  │  │  - Disk: 10GB SSD                                    │       │   │
│  │  │  - Zone: us-central1-c (ZONAL)                       │       │   │
│  │  │  - Max Connections: 100                              │       │   │
│  │  │  - Shared Buffers: 77MB                              │       │   │
│  │  │                                                        │       │   │
│  │  │  Backups:                                             │       │   │
│  │  │  - Daily at 2:00 AM UTC                              │       │   │
│  │  │  - 7 days retention                                  │       │   │
│  │  └──────────────────────────────────────────────────────┘       │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  Cloud Router: apex-router                                       │   │
│  │  Region: us-central1                                             │   │
│  │                                                                   │   │
│  │  ┌──────────────────────────────────────────────────────┐       │   │
│  │  │  Cloud NAT: apex-nat                                  │       │   │
│  │  │  - Auto-scaling (min/max source IPs)                │       │   │
│  │  │  - Provides outbound internet for private resources │       │   │
│  │  └──────────────────────────────────────────────────────┘       │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  Private Service Connection                                      │   │
│  │  IP Range: apex-private-ip (10.1.0.0/24)                        │   │
│  │  Purpose: VPC_PEERING                                           │   │
│  │  - Connects VPC to servicenetworking.googleapis.com             │   │
│  │  - Enables private Cloud SQL instances                          │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────────────────────────────┘
```

---

## Network Topology

### IP Address Allocation

| Resource | CIDR Range | Purpose | Hosts |
|----------|-----------|---------|-------|
| **Private Subnet** | 10.0.0.0/24 | Databases and services | 254 |
| **VPC Connector** | 10.8.0.0/28 | Cloud Run to VPC bridge | 14 |
| **Private Connection** | 10.1.0.0/24 | Cloud SQL peering | 254 |
| **Cloud SQL Instance** | 10.115.5.3/32 | PostgreSQL private IP | 1 |

**Total IP usage:** ~520 addresses across 3 CIDR blocks

### Traffic Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                      Connection Scenarios                            │
└─────────────────────────────────────────────────────────────────────┘

1. Cloud Run → PostgreSQL
   Cloud Run Container
        ↓ (via VPC Connector 10.8.0.0/28)
   VPC Network (apex-memory-vpc)
        ↓ (private routing)
   Cloud SQL Instance (10.115.5.3:5432)
   Connection: Unix socket (/cloudsql/apex-memory-dev:us-central1:apex-postgres-dev)

2. Local Development → PostgreSQL
   Developer Machine
        ↓ (Cloud SQL Proxy)
   127.0.0.1:5432 (local proxy)
        ↓ (encrypted tunnel to GCP)
   Cloud SQL Instance (10.115.5.3:5432)
   Connection: postgresql://apex:PASSWORD@127.0.0.1:5432/apex_memory

3. GCP Compute (same VPC) → PostgreSQL
   GCP VM in apex-memory-vpc
        ↓ (direct private routing)
   Cloud SQL Instance (10.115.5.3:5432)
   Connection: postgresql://apex:PASSWORD@10.115.5.3:5432/apex_memory

4. Private Resources → Internet (Outbound)
   Cloud SQL Instance / VPC Resources
        ↓ (private routing)
   Cloud Router (apex-router)
        ↓ (NAT translation)
   Cloud NAT (apex-nat)
        ↓ (public internet)
   External Services (package updates, API calls)
```

---

## Security Architecture

### Network Security Layers

```
┌─────────────────────────────────────────────────────────────────────┐
│                      Security Layers (Defense in Depth)              │
└─────────────────────────────────────────────────────────────────────┘

Layer 1: Network Isolation
├─ Private IP only (no public internet exposure)
├─ Custom VPC (no auto-created subnets)
└─ Private subnet with controlled routing

Layer 2: Private Google Access
├─ Access Google APIs without public IPs
├─ Cloud SQL, Cloud Storage, etc. via private routes
└─ Reduces attack surface (no internet gateway needed)

Layer 3: VPC Peering
├─ Private Service Connection to servicenetworking.googleapis.com
├─ Dedicated IP range (10.1.0.0/24)
└─ Encrypted traffic between VPC and Cloud SQL

Layer 4: Cloud SQL Security
├─ Private IP only (10.115.5.3)
├─ No authorized networks (not accessible from internet)
├─ SSL: ALLOW_UNENCRYPTED_AND_ENCRYPTED (upgrade to require)
└─ IAM-based authentication available

Layer 5: Access Control
├─ Cloud Run: Service account-based access
├─ Local Development: Cloud SQL Proxy with gcloud auth
├─ Managed credentials (no hardcoded passwords)
└─ Secret Manager integration (recommended for production)

Layer 6: Monitoring & Audit
├─ Cloud SQL audit logs (to enable)
├─ VPC Flow Logs (to enable)
├─ Cloud Monitoring dashboards
└─ Alerting on unusual activity
```

### Current Security Posture

**Implemented ✅:**
- Private IP only (no public internet access)
- Secure password generation (32 characters, base64)
- Private Google Access enabled
- VPC peering for Cloud SQL
- Cloud NAT for controlled outbound access
- Automated daily backups (7 days retention)

**Pending ⏳:**
- Store password in Secret Manager (currently in /tmp)
- Enable Cloud SQL SSL enforcement
- Configure authorized networks (if needed for specific access)
- Enable Cloud SQL audit logs
- Set up IAM conditions for database access
- Review and configure VPC firewall rules
- Enable deletion protection (production only)

---

## Component Details

### VPC Network (apex-memory-vpc)

**Configuration:**
- **Mode:** Custom (no auto-created subnets)
- **Routing Mode:** Regional (us-central1)
- **MTU:** 1460 (standard for GCP)
- **Auto-create firewall rules:** Yes (default allow internal traffic)

**Why Custom Mode?**
- Manual control over subnet creation
- Better security (no unexpected subnets)
- Predictable IP address allocation
- Easier to audit and manage

---

### Private Subnet (apex-db-subnet)

**Configuration:**
- **CIDR:** 10.0.0.0/24 (254 usable addresses)
- **Region:** us-central1
- **Private Google Access:** ENABLED
- **Flow Logs:** Disabled (enable for production)

**Private Google Access Benefits:**
- Access Google APIs (Cloud Storage, Cloud Logging) without public IPs
- Reduces costs (no NAT charges for Google API calls)
- Better security (no internet gateway required)

---

### VPC Connector (apex-vpc-connector)

**Configuration:**
- **CIDR:** 10.8.0.0/28 (14 usable addresses)
- **Machine Type:** e2-micro (0.25 vCPU, 1GB RAM)
- **Min Instances:** 2 (high availability)
- **Max Instances:** 3 (auto-scaling)
- **Region:** us-central1

**Purpose:**
- Connects Cloud Run (serverless) to VPC network
- Enables Cloud Run to access private Cloud SQL instances
- Auto-scales based on traffic

**Cost:** ~$10-12/month (2-3 e2-micro instances running 24/7)

**Why e2-micro?**
- Development tier sufficient for database connections
- Can upgrade to e2-standard-4 for production (higher throughput)

---

### Cloud Router + Cloud NAT

**Cloud Router (apex-router):**
- **Purpose:** Dynamic routing for VPC
- **Region:** us-central1
- **ASN:** Auto-assigned by GCP

**Cloud NAT (apex-nat):**
- **Purpose:** Outbound internet access for private resources
- **Configuration:** Auto-scaling (automatic source IP allocation)
- **Logging:** Disabled (enable for production debugging)

**Use Cases:**
- Cloud SQL downloads package updates
- API calls to external services
- Webhook notifications

**Cost:** ~$0.50-2/month (minimal usage in dev)

---

### Cloud SQL PostgreSQL 17

**Instance Configuration:**
- **Name:** apex-postgres-dev
- **Version:** PostgreSQL 17
- **Tier:** db-f1-micro (1 vCPU, 1GB RAM)
- **Disk:** 10GB SSD (auto-storage increase disabled)
- **Zone:** us-central1-c (ZONAL availability)
- **Connection Name:** apex-memory-dev:us-central1:apex-postgres-dev

**Database Flags:**
```
max_connections: 100
shared_buffers: 78643 KB (~77MB, max for db-f1-micro)
```

**Backup Configuration:**
- **Enabled:** Yes
- **Start Time:** 02:00 UTC (6 PM PST / 7 PM PDT)
- **Retention:** 7 days
- **Transaction Logs:** 7 days
- **Point-in-time Recovery:** Available

**Maintenance Window:**
- **Day:** Any day (GCP chooses)
- **Hour:** Any hour (GCP chooses)
- **Update Track:** Production (stable updates only)

**Deletion Protection:** Disabled (dev only - enable for production)

**Cost:** ~$15-20/month (db-f1-micro tier)

---

## Upgrade Paths

### Development → Staging

**Cloud SQL Tier:**
```
db-f1-micro (1 vCPU, 1GB RAM)
    ↓
db-n1-standard-1 (1 vCPU, 3.75GB RAM)
```

**Changes:**
- Increase shared_buffers to 256MB (more headroom)
- Increase max_connections to 250
- Enable High Availability (REGIONAL)
- Enable point-in-time recovery
- Add read replicas (optional)

**Cost Increase:** +$85-100/month

---

### Staging → Production

**Cloud SQL Tier:**
```
db-n1-standard-1 (1 vCPU, 3.75GB RAM)
    ↓
db-n1-standard-2 (2 vCPU, 7.5GB RAM)
or
db-n1-standard-4 (4 vCPU, 15GB RAM)
```

**Additional Changes:**
- Enable deletion protection
- Enable Cloud SQL audit logs
- Enable VPC Flow Logs
- Configure alerts (CPU > 80%, connections > 80%)
- Set up Cloud Armor (DDoS protection)
- Enable SSL enforcement (require SSL connections)
- Configure authorized networks (if needed)
- Add monitoring dashboards
- Set up automated testing

**Cost Increase:** +$100-300/month (depending on tier)

---

### VPC Connector Scaling

**Development:**
```
e2-micro (0.25 vCPU, 1GB RAM) × 2-3 instances
```

**Production:**
```
e2-standard-4 (4 vCPU, 16GB RAM) × 3-10 instances
```

**Why Upgrade?**
- Higher throughput (more concurrent Cloud Run connections)
- Better performance under load
- Handles traffic spikes

**Cost Increase:** +$100-200/month

---

## Connection Patterns

### Cloud Run (Production Pattern)

```python
import sqlalchemy
from google.cloud.sql.connector import Connector

# Initialize Cloud SQL Python Connector
connector = Connector()

def getconn():
    conn = connector.connect(
        "apex-memory-dev:us-central1:apex-postgres-dev",
        "pg8000",
        user="apex",
        password=os.environ["DB_PASSWORD"],  # From Secret Manager
        db="apex_memory",
    )
    return conn

# Create SQLAlchemy engine using connector
engine = sqlalchemy.create_engine(
    "postgresql+pg8000://",
    creator=getconn,
    pool_size=2,           # Small for Cloud Run (serverless)
    max_overflow=1,
    pool_timeout=10,
    pool_recycle=600,      # 10 minutes
    pool_pre_ping=True,
)

# Use engine
with engine.connect() as conn:
    result = conn.execute(sqlalchemy.text("SELECT version();"))
    print(result.fetchone())
```

**Why This Pattern?**
- Automatic IAM authentication (no password needed)
- Connection pooling optimized for serverless
- Built-in retry logic
- Supports Cloud SQL Proxy under the hood

---

### Local Development (Cloud SQL Proxy)

```bash
# Terminal 1: Start proxy
cloud-sql-proxy apex-memory-dev:us-central1:apex-postgres-dev

# Terminal 2: Connect
psql "host=127.0.0.1 port=5432 dbname=apex_memory user=apex password=$(cat /tmp/apex-postgres-password.txt)"
```

```python
# Python (SQLAlchemy)
from sqlalchemy import create_engine

engine = create_engine(
    "postgresql://apex:PASSWORD@127.0.0.1:5432/apex_memory",
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
)
```

**Why This Pattern?**
- Encrypted connection to Cloud SQL
- Works from any network (home, coffee shop, etc.)
- Uses your gcloud credentials (no password needed)
- Same connection interface as direct connection

---

## Monitoring & Observability

### GCP Console Views

**Cloud SQL Instance:**
https://console.cloud.google.com/sql/instances/apex-postgres-dev?project=apex-memory-dev

**Key Metrics:**
- CPU utilization (should be < 80%)
- Memory usage (should be < 80%)
- Disk usage (should be < 80%)
- Connections (should be < 80 for db-f1-micro)
- Replication lag (if HA enabled)

**VPC Network:**
https://console.cloud.google.com/networking/networks/details/apex-memory-vpc?project=apex-memory-dev

**Cloud NAT:**
https://console.cloud.google.com/net-services/nat/list?project=apex-memory-dev

---

### Monitoring Queries

```sql
-- Check current connections
SELECT count(*) as total_connections
FROM pg_stat_activity;

-- Connections by state
SELECT state, count(*)
FROM pg_stat_activity
GROUP BY state;

-- Long-running queries (> 5 minutes)
SELECT pid,
       now() - pg_stat_activity.query_start AS duration,
       query
FROM pg_stat_activity
WHERE state = 'active'
AND now() - pg_stat_activity.query_start > interval '5 minutes'
ORDER BY duration DESC;

-- Database size
SELECT pg_size_pretty(pg_database_size('apex_memory')) as db_size;

-- Table sizes
SELECT schemaname,
       tablename,
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

---

## Disaster Recovery

### Backup Strategy

**Automated Backups:**
- **Frequency:** Daily at 2:00 AM UTC
- **Retention:** 7 days (168 hours)
- **Type:** Full database backup
- **Point-in-time Recovery:** Available (transaction logs retained)

**Recovery Scenarios:**

**Scenario 1: Accidental Data Deletion (< 7 days ago)**
```bash
# Restore to point-in-time (5 days ago)
gcloud sql backups restore BACKUP_ID \
  --instance=apex-postgres-dev \
  --project=apex-memory-dev
```

**Scenario 2: Database Corruption**
```bash
# Clone to new instance from backup
gcloud sql instances clone apex-postgres-dev apex-postgres-recovery \
  --point-in-time='2025-11-10T12:00:00Z' \
  --project=apex-memory-dev
```

**Scenario 3: Instance Deletion (deletion protection disabled)**
- Manual backup to Cloud Storage (recommended before major changes)
- Export to SQL file: `gcloud sql export sql`

---

### High Availability Upgrade

**Current:** ZONAL (single zone, us-central1-c)

**Production Upgrade:** REGIONAL (multi-zone, automatic failover)

```bash
# Enable HA (requires restart)
gcloud sql instances patch apex-postgres-dev \
  --availability-type=REGIONAL \
  --project=apex-memory-dev
```

**Benefits:**
- Automatic failover to standby instance (< 60 seconds)
- Zero downtime maintenance
- 99.95% SLA (vs. 99.5% for zonal)

**Cost:** Included in tier (no additional charge)

---

## Troubleshooting

### Common Issues

**Issue 1: Connection Refused (Cloud SQL Proxy)**
```
Error: could not connect to server: Connection refused
```

**Solutions:**
1. Check proxy is running: `ps aux | grep cloud-sql-proxy`
2. Start proxy: `cloud-sql-proxy apex-memory-dev:us-central1:apex-postgres-dev &`
3. Verify instance is RUNNABLE: `gcloud sql instances describe apex-postgres-dev`

---

**Issue 2: Too Many Connections**
```
FATAL: sorry, too many clients already
```

**Solutions:**
1. Check current connections:
   ```sql
   SELECT count(*) FROM pg_stat_activity;
   ```

2. Kill idle connections:
   ```sql
   SELECT pg_terminate_backend(pid)
   FROM pg_stat_activity
   WHERE state = 'idle'
   AND state_change < NOW() - INTERVAL '5 minutes';
   ```

3. Reduce connection pool sizes in applications
4. Upgrade to db-n1-standard-1 (250 max connections)

---

**Issue 3: Slow Queries**

**Solutions:**
1. Check query plan: `EXPLAIN ANALYZE SELECT ...;`
2. Add indexes for frequently queried columns
3. Monitor with pg_stat_statements:
   ```sql
   SELECT * FROM pg_stat_statements
   ORDER BY total_exec_time DESC
   LIMIT 10;
   ```
4. Consider upgrading instance tier

---

## Cost Analysis

### Monthly Costs (Development Tier)

| Service | Configuration | Monthly Cost | Notes |
|---------|--------------|--------------|-------|
| Cloud SQL PostgreSQL | db-f1-micro, 10GB, ZONAL | $15-20 | 1 vCPU, 1GB RAM |
| VPC Connector | e2-micro × 2-3 instances | $10-12 | Auto-scaling |
| Cloud NAT | Auto-scaling, minimal usage | $0.50-2 | Outbound internet |
| Network Egress | Varies by traffic | $1-5 | To internet |
| **Total** | | **$25-35** | **Development** |

---

### Monthly Costs (Production Tier)

| Service | Configuration | Monthly Cost | Notes |
|---------|--------------|--------------|-------|
| Cloud SQL PostgreSQL | db-n1-standard-1, 50GB, REGIONAL | $100-150 | 1 vCPU, 3.75GB RAM, HA |
| VPC Connector | e2-standard-4 × 3-10 instances | $150-250 | Higher throughput |
| Cloud NAT | Auto-scaling, higher usage | $5-15 | More outbound traffic |
| Network Egress | Higher traffic | $10-30 | Production traffic |
| Cloud Armor | DDoS protection | $20-50 | Security |
| **Total** | | **$285-495** | **Production** |

---

### Cost Optimization Tips

**Development:**
- Use db-f1-micro (smallest tier)
- Disable deletion protection (faster iteration)
- Use ZONAL availability (no HA needed)
- Keep backup retention at 7 days
- Use minimal VPC connector instances (2)

**Production:**
- Right-size instance tier (monitor CPU/RAM usage)
- Enable committed use discounts (1-year: 37% off, 3-year: 55% off)
- Use Cloud CDN for static content (reduce egress)
- Optimize connection pooling (reduce instance size needs)
- Consider read replicas instead of scaling primary
- Use Cloud Scheduler to stop dev instances at night (save 50%)

---

## References

**Official Documentation:**
- Cloud SQL PostgreSQL: https://cloud.google.com/sql/docs/postgres
- VPC Networks: https://cloud.google.com/vpc/docs
- Cloud NAT: https://cloud.google.com/nat/docs
- VPC Connector: https://cloud.google.com/vpc/docs/configure-serverless-vpc-access
- Cloud SQL Proxy: https://cloud.google.com/sql/docs/postgres/connect-instance-auth-proxy

**Pulumi Documentation:**
- GCP Provider: https://www.pulumi.com/registry/packages/gcp/
- Pulumi State Management: https://www.pulumi.com/docs/concepts/state/

**GCP Console:**
- Project Dashboard: https://console.cloud.google.com/home/dashboard?project=apex-memory-dev
- Cloud SQL: https://console.cloud.google.com/sql/instances?project=apex-memory-dev
- VPC Networks: https://console.cloud.google.com/networking/networks/list?project=apex-memory-dev

---

**Last Updated:** 2025-11-15
**Architecture Version:** 1.0
**Deployment Status:** ✅ Production-Ready (Development Tier)
