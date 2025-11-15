# ADR-001: Google Cloud Storage for Cold Storage Archival

**Status:** Accepted
**Date:** 2025-11-14
**Decision Makers:** Richard Glaubitz, Claude Code
**Phase:** Phase 3 (Memory Quality & Importance Management)

---

## Context

Phase 3 Tier 4 (Retention Policies) requires a cold storage solution for long-term archival of low-importance messages that have aged beyond their retention period. The original architecture specified Amazon S3, but the project requirement is to avoid Amazon products entirely.

**Requirements:**
- Long-term archival storage for messages (>1 year old)
- Cost-effective ($0.01-0.02/GB/month)
- API-compatible with modern cloud storage standards
- Reliable, durable (99.999999999% durability)
- No vendor lock-in (ability to migrate if needed)
- **Must NOT be an Amazon product** (AWS S3, Glacier, etc.)

**Storage Architecture:**
```
Hot Storage (Neo4j):     Recent + important messages (~50,000 episodes)
                         ↓ (importance < 0.3, age > 30 days)
Warm Storage (PostgreSQL): Medium-term messages (30 days - 1 year)
                         ↓ (importance < 0.2, age > 365 days)
Cold Storage (???):       Long-term archival (> 1 year)
```

---

## Decision

**We will use Google Cloud Storage (GCS) for cold storage archival.**

---

## Alternatives Considered

### Option 1: Google Cloud Storage (GCS) ⭐ SELECTED

**Pros:**
- ✅ S3-compatible API (easy migration path from S3 documentation)
- ✅ Comparable pricing: $0.020/GB/month (Standard), $0.012/GB/month (Nearline)
- ✅ Excellent Python SDK (`google-cloud-storage`)
- ✅ 99.999999999% durability (11 nines, same as S3)
- ✅ Multi-region replication available
- ✅ No Amazon affiliation (meets project requirement)
- ✅ Strong ecosystem (Google Cloud Platform integration)
- ✅ Lifecycle management policies (automatic archival tiers)
- ✅ Versioning and object lifecycle management
- ✅ Strong security (IAM, encryption at rest, audit logs)

**Cons:**
- ⚠️ Requires Google Cloud account setup
- ⚠️ Slightly different API from S3 (minor learning curve)
- ⚠️ Data egress costs ($0.12/GB if downloading large amounts)

**Cost Estimate (1 year):**
- Archived messages: ~500 GB/year (30% of 1,500 GB total)
- GCS Nearline storage: $0.012/GB × 500 GB = $6/month = $72/year
- Operations: Minimal (few writes, rare reads)
- **Total: ~$75/year**

### Option 2: MinIO (Self-Hosted)

**Pros:**
- ✅ S3-compatible API (100% compatible)
- ✅ Self-hosted (full control, no cloud fees)
- ✅ Open-source (no vendor lock-in)
- ✅ High performance (can exceed cloud providers)
- ✅ On-premise option (data sovereignty)

**Cons:**
- ❌ Requires infrastructure management (servers, disks, networking)
- ❌ Operational complexity (backups, redundancy, disaster recovery)
- ❌ No built-in durability guarantees (need to implement RAID, replication)
- ❌ Team must maintain infrastructure (time cost)
- ❌ Initial setup cost (hardware or VPS rental)
- ❌ Not suitable for MVP/early-stage product

**Cost Estimate (1 year):**
- Server rental: ~$20/month × 12 = $240/year
- Storage: ~$10/month × 12 = $120/year
- Maintenance time: ~4 hours/month × 12 = 48 hours/year
- **Total: ~$360/year + significant time investment**

### Option 3: Local Filesystem + Compression

**Pros:**
- ✅ Simplest implementation (no external dependencies)
- ✅ Zero cloud costs
- ✅ Fast local access
- ✅ Full control

**Cons:**
- ❌ No built-in redundancy (single point of failure)
- ❌ No automatic backup
- ❌ Difficult to scale (disk limits)
- ❌ No disaster recovery
- ❌ Not suitable for production use
- ❌ Requires manual management of disk space

**Cost Estimate (1 year):**
- External HDD (4TB): $100 one-time
- **Total: ~$100/year (but high risk of data loss)**

### Option 4: Azure Blob Storage

**Pros:**
- ✅ Comparable pricing: $0.018/GB/month (Hot), $0.010/GB/month (Cool)
- ✅ Excellent Python SDK (`azure-storage-blob`)
- ✅ 99.999999999% durability (11 nines)
- ✅ No Amazon affiliation
- ✅ Strong enterprise support

**Cons:**
- ⚠️ Requires Microsoft Azure account
- ⚠️ Different API from S3 (learning curve)
- ⚠️ Less ecosystem integration than GCP/AWS
- ⚠️ Data egress costs

**Cost Estimate (1 year):**
- Cool tier: $0.010/GB × 500 GB = $5/month = $60/year
- **Total: ~$65/year**

---

## Rationale

**Google Cloud Storage was selected for the following reasons:**

### 1. **Best Balance of Features and Cost**
- Pricing is competitive with Azure ($72/year vs $65/year for Azure)
- Minimal difference ($7/year = $0.58/month)
- GCS offers better Python ecosystem integration
- GCS has stronger documentation and community support

### 2. **S3-Compatible API (Migration Path)**
- GCS is S3-compatible, meaning code written for S3 can be adapted easily
- Most S3 client libraries work with GCS with minimal changes
- Reduces learning curve for team
- Future migration to other S3-compatible providers is possible

### 3. **Proven Python SDK**
- `google-cloud-storage` is mature, well-documented, and actively maintained
- Official Google SDK (not community-maintained)
- Excellent error handling and retry logic built-in
- Simple authentication (service accounts)

### 4. **Meets Project Requirements**
- ✅ No Amazon products (meets core requirement)
- ✅ Cloud-based (no infrastructure management)
- ✅ Durable (11 nines = 99.999999999%)
- ✅ Cost-effective ($6-12/month depending on tier)
- ✅ Scalable (automatic, no manual intervention)

### 5. **Lifecycle Management**
- GCS supports automatic lifecycle policies (auto-transition to Coldline after X days)
- Reduces manual intervention
- Cost optimization without code changes

### 6. **Strong Security**
- IAM integration (fine-grained permissions)
- Encryption at rest (default)
- Encryption in transit (TLS)
- Audit logs (compliance-friendly)
- Object versioning (data protection)

---

## Implementation Details

### GCS Storage Tiers

We will use **GCS Nearline** for archived messages:

| Tier | Price/GB/month | Use Case | Data Access |
|------|----------------|----------|-------------|
| **Standard** | $0.020 | Hot data (<30 days) | Frequent access |
| **Nearline** ⭐ | $0.012 | Warm data (30-90 days) | Monthly access |
| **Coldline** | $0.004 | Cold data (90+ days) | Quarterly access |
| **Archive** | $0.0012 | Archive (1+ year) | Yearly access |

**Decision:** Start with **Nearline** ($0.012/GB/month)
- Retrieval latency: Milliseconds (same as Standard)
- Minimum storage duration: 30 days
- Data retrieval cost: $0.01/GB
- Best balance for our use case (monthly potential access)

**Lifecycle Policy:**
```json
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "SetStorageClass", "storageClass": "NEARLINE"},
        "condition": {"age": 30}
      },
      {
        "action": {"type": "SetStorageClass", "storageClass": "COLDLINE"},
        "condition": {"age": 90}
      },
      {
        "action": {"type": "SetStorageClass", "storageClass": "ARCHIVE"},
        "condition": {"age": 365}
      }
    ]
  }
}
```

### Python SDK Integration

**Installation:**
```bash
pip install google-cloud-storage
```

**Authentication:**
```bash
# Service account JSON key
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
```

**Code Example:**
```python
from google.cloud import storage

class GCSArchiveService:
    def __init__(self, bucket_name: str):
        self.client = storage.Client()
        self.bucket = self.client.bucket(bucket_name)

    async def archive_message(self, message_id: str, content: str):
        """Upload message to GCS Nearline storage"""
        blob = self.bucket.blob(f"messages/{message_id}.json")
        blob.upload_from_string(
            content,
            content_type="application/json"
        )
        # Set storage class to Nearline
        blob.update_storage_class("NEARLINE")

    async def retrieve_message(self, message_id: str) -> str:
        """Retrieve message from GCS"""
        blob = self.bucket.blob(f"messages/{message_id}.json")
        return blob.download_as_text()
```

### Bucket Structure

```
apex-memory-archive/              # GCS bucket name
├── messages/
│   ├── 2025/
│   │   ├── 01/                  # January
│   │   │   ├── oscar/           # Agent-specific
│   │   │   │   └── msg-uuid.json
│   │   │   ├── sarah/
│   │   │   └── system/
│   │   └── 02/                  # February
│   └── 2026/
└── episodes/                    # Graphiti episodes (if needed)
    └── 2025/
        └── 01/
            └── episode-uuid.json
```

### Cost Projections

**Year 1 (Low Volume):**
- Messages/year: ~365,000 (1,000/day)
- Archived (30% low-importance): ~110,000 messages
- Average message size: ~2 KB
- Total storage: 110,000 × 2 KB = 220 MB = 0.22 GB
- **Cost: $0.22 × $0.012 = $0.0026/month = $0.03/year** (negligible)

**Year 2-3 (Growth):**
- Storage: ~1.5 GB (cumulative)
- **Cost: 1.5 × $0.012 = $0.018/month = $0.22/year**

**Year 5 (Mature Product):**
- Storage: ~5 GB (cumulative)
- **Cost: 5 × $0.012 = $0.06/month = $0.72/year**

**Conclusion:** GCS costs are **negligible** even at scale (<$1/year for 5 years of data).

---

## Configuration Changes

### Settings (`src/apex_memory/config/settings.py`)

```python
# Google Cloud Storage Configuration
gcs_enabled: bool = Field(
    default=True,
    description="Enable Google Cloud Storage for cold archival"
)
gcs_bucket_name: str = Field(
    default="apex-memory-archive",
    description="GCS bucket name for archived messages"
)
gcs_service_account_file: str | None = Field(
    default=None,
    description="Path to GCS service account JSON key file"
)
gcs_archive_base_path: str = Field(
    default="messages",
    description="Base path within GCS bucket for archived messages"
)
```

### Environment Variables (`.env`)

```bash
# Google Cloud Storage
GCS_ENABLED=true
GCS_BUCKET_NAME=apex-memory-archive
GCS_SERVICE_ACCOUNT_FILE=/path/to/service-account-key.json
GCS_ARCHIVE_BASE_PATH=messages
```

---

## Migration Path

### From S3 to GCS (If Needed Later)

GCS is S3-compatible, so most S3 code can be adapted with minimal changes:

**S3 (boto3):**
```python
import boto3
s3 = boto3.client('s3')
s3.upload_file('file.txt', 'bucket-name', 'key')
```

**GCS (google-cloud-storage):**
```python
from google.cloud import storage
client = storage.Client()
bucket = client.bucket('bucket-name')
blob = bucket.blob('key')
blob.upload_from_filename('file.txt')
```

**Interoperability:**
- GCS supports S3-compatible XML API (can use boto3 with endpoint override)
- gsutil command-line tool supports `rsync` with S3 (migration tool)

---

## Consequences

### Positive

- ✅ No Amazon products (meets core requirement)
- ✅ Cost-effective ($0.012/GB/month Nearline, <$1/year even at scale)
- ✅ Durable (99.999999999% durability)
- ✅ Simple Python SDK integration (`google-cloud-storage`)
- ✅ Automatic lifecycle management (transition to Coldline/Archive)
- ✅ S3-compatible (easy migration if needed)
- ✅ Strong security (IAM, encryption, audit logs)
- ✅ No infrastructure management required
- ✅ Scales automatically without code changes

### Negative

- ⚠️ Requires Google Cloud account setup (one-time effort)
- ⚠️ Data egress costs if downloading large amounts ($0.12/GB)
- ⚠️ Vendor lock-in risk (mitigated by S3 compatibility)
- ⚠️ Service account key management (credentials security)

### Neutral

- ℹ️ Monthly GCS billing (vs self-hosted one-time cost)
- ℹ️ API learning curve (minor, well-documented)
- ℹ️ Dependency on Google Cloud Platform uptime (99.95% SLA)

---

## Risks and Mitigation

### Risk 1: GCS Unavailability

**Impact:** Cannot archive or retrieve old messages
**Probability:** Low (99.95% SLA = ~4 hours/year downtime)
**Mitigation:**
- Graceful degradation: Keep messages in PostgreSQL if GCS unavailable
- Retry logic with exponential backoff
- Queue failed archival attempts for later retry

### Risk 2: Data Egress Costs

**Impact:** High costs if downloading large amounts of data
**Probability:** Low (archival is write-heavy, read-rare)
**Mitigation:**
- Monitor egress metrics (Grafana dashboard)
- Alert on egress >100 GB/month
- Use lifecycle policies to minimize manual retrieval
- Cache frequently accessed archived data in PostgreSQL

### Risk 3: Service Account Key Exposure

**Impact:** Unauthorized access to GCS bucket
**Probability:** Low (if following security best practices)
**Mitigation:**
- Store key in secure secrets manager (Google Secret Manager)
- Use IAM roles with least privilege (read/write only apex-memory-archive bucket)
- Rotate service account keys quarterly
- Enable audit logging on bucket
- Use encryption at rest (enabled by default)

### Risk 4: Vendor Lock-In

**Impact:** Difficult to migrate away from GCS if needed
**Probability:** Low (S3 compatibility provides migration path)
**Mitigation:**
- Use S3-compatible API wrapper (boto3 with GCS endpoint)
- Document migration path in ADR
- Test migration to MinIO annually (disaster recovery drill)

---

## Alternatives Not Considered

### Backblaze B2
- **Reason:** Less mature ecosystem, smaller community support
- **Cost:** $0.005/GB/month (half of GCS), but $0.01/GB egress
- **Verdict:** Marginally cheaper but less reliable for production use

### Wasabi
- **Reason:** No egress fees, but smaller provider with less reliability track record
- **Cost:** $0.0059/GB/month (flat, no egress fees)
- **Verdict:** Interesting for read-heavy workloads, but less proven

### Cloudflare R2
- **Reason:** Zero egress fees, S3-compatible
- **Cost:** $0.015/GB/month, $0/GB egress
- **Verdict:** Strong option, but newer service with limited track record

**Decision:** GCS is the safest, most proven option for production use.

---

## References

**Official Documentation:**
- Google Cloud Storage: https://cloud.google.com/storage/docs
- Python SDK: https://googleapis.dev/python/storage/latest/index.html
- Pricing: https://cloud.google.com/storage/pricing
- Lifecycle Management: https://cloud.google.com/storage/docs/lifecycle

**Comparison Articles:**
- GCS vs S3: https://cloud.google.com/docs/compare/aws/storage
- Storage pricing comparison: https://www.cloudwards.net/comparison/

**Implementation Guides:**
- Service Account Authentication: https://cloud.google.com/docs/authentication/getting-started
- Python Quickstart: https://cloud.google.com/storage/docs/reference/libraries#client-libraries-install-python

---

## Approval

**Approved By:** Richard Glaubitz
**Approval Date:** 2025-11-14
**Implementation Target:** Phase 3, Week 2 (Days 8-10)

---

## Changelog

- **2025-11-14:** ADR created, GCS selected as cold storage solution
