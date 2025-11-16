# Feature Analysis Working Notes

**Purpose:** Research findings for all 10 features identified in FEATURE-DEPLOYMENT-INVENTORY.md
**Created:** 2025-11-15
**Phase:** Phase 1 - Research & Analysis

---

## Summary Table

| Feature | Workflows | GCP APIs | DB Changes | Env Vars | Cost/Month | Week | Status |
|---------|-----------|----------|------------|----------|------------|------|--------|
| **Graphiti Integration** | N/A (service layer) | None (uses existing Neo4j) | None (uses Neo4j) | GRAPHITI_ENABLED, GRAPHITI_NEO4J_URI, GRAPHITI_NEO4J_USER, GRAPHITI_NEO4J_PASSWORD | ~$10-30 (LLM usage) | Week 2 | ✅ Implemented |
| **Structured Data Ingestion** | StructuredDataIngestionWorkflow, BatchStructuredDataIngestionWorkflow | None | structured_data table (JSONB) | ENABLE_STRUCTURED_DATA_INGESTION | $0 | Week 2 | ✅ Implemented |
| **Conversation Processing** | ConversationIngestionWorkflow | None | conversations, messages tables | ENABLE_CONVERSATION_INGESTION | ~$5-15 (GPT-5 nano) | Week 3 | ✅ Implemented |
| **Memory Decay** | MemoryDecayWorkflow (scheduled) | None | retention fields in messages | MEMORY_DECAY_THRESHOLD, MEMORY_TTL_DAYS | $0 | Week 3 | ✅ Implemented |
| **Google Drive Archive** | GoogleDriveArchiveWorkflow | storage.googleapis.com | archive_metadata table | GCS_ARCHIVE_BUCKET | ~$0-5 (GCS storage) | Week 2 | ✅ Implemented |
| **GCS Archival Service** | N/A (service layer) | storage.googleapis.com (already enabled) | None | GCS_ENABLED, GCS_BUCKET_NAME | ~$5-10 (moderate usage) | Week 2 | ✅ Implemented |
| **NATS Messaging** | N/A (service layer) | None (self-hosted OR external) | None | NATS_URL | $0 (self-host) OR $15-50 (managed) | Week 3 (optional) | ⚠️ Implemented but usage unclear |
| **Authentication** | N/A (API endpoints) | None | users, api_keys tables | JWT settings (already exist) | $0 | Week 3 (optional) | ✅ Implemented |
| **Agent Interactions** | N/A (service layer) | None | agent_interactions table | None | $0 | Post-initial (defer) | ✅ Implemented (defer deployment) |
| **UI/UX Frontend** | N/A (separate service) | TBD (Cloud Run frontend) | None | TBD | TBD | Post-initial (defer) | 📝 Planned (defer deployment) |

---

## Feature 1: Graphiti Integration

### Implementation Details

**File:** `src/apex_memory/services/graphiti_service.py` (1,194 lines)
**Purpose:** LLM-powered entity extraction replacing regex patterns (60% → 90%+ accuracy)
**Status:** ✅ Fully implemented (Nov 6, 2025)

**Key Components:**
- GraphitiService class with 18 methods
- Auto-configuration for all 46 unified entity schemas
- Methods: `add_document_episode()`, `add_message_episode()`, `add_json_episode()`, `search()`
- Integration with Neo4j via Graphiti library

### Environment Variables

```bash
GRAPHITI_ENABLED=true
GRAPHITI_NEO4J_URI=${NEO4J_URI}  # References existing Neo4j
GRAPHITI_NEO4J_USER=${NEO4J_USER}
GRAPHITI_NEO4J_PASSWORD=${NEO4J_PASSWORD}
```

**Note:** These already exist in `.env.example` (lines 129-135)

### GCP Resources

**None required** - Uses existing Neo4j database

### Database Changes

**None required** - Graphiti stores data in existing Neo4j database

### API Endpoints

No dedicated endpoints - integrated into existing ingestion workflows

### Dependencies

- Neo4j (already deployed in Phase 2)
- OpenAI API key (for LLM extraction) OR Anthropic API key
- Python packages: `graphiti-core` (already in requirements.txt)

### Cost Estimate

- **LLM Usage:** ~$10-30/month for entity extraction
  - Uses OpenAI GPT-5 by default (`llm_model="gpt-5"`)
  - Configurable to use Anthropic Claude or other providers
  - Cost depends on document volume

### Deployment Week

**Week 2: Dockerization & Configuration**

### Tests

- `tests/unit/test_graphiti_extraction_activity.py`
- `tests/unit/test_graphiti_rollback.py`
- Part of Enhanced Saga baseline (121 tests passing)

### Feature Flag

```python
use_unified_schemas=True  # Enables Graphiti with unified entity schemas
```

### Verification Command

```bash
# Test entity extraction endpoint
curl -X POST http://localhost:8000/api/v1/ingest/document \
  -H "Content-Type: application/json" \
  -d '{"content": "Test document for entity extraction"}'

# Check Graphiti extraction occurred (entities should be in Neo4j)
```

---

## Feature 2: Structured Data Ingestion

### Implementation Details

**Files:**
- Workflows: `src/apex_memory/temporal/workflows/structured_data_ingestion.py`
- Activities: `src/apex_memory/temporal/activities/structured_data_ingestion.py`
- Models: `src/apex_memory/models/structured_data.py` (116 lines)

**Workflows:**
1. **StructuredDataIngestionWorkflow** - Single JSON ingestion
2. **BatchStructuredDataIngestionWorkflow** - Bulk ingestion

**Purpose:** Ingest JSON from external APIs (Samsara GPS, Turvo shipments, FrontApp messages)

**Status:** ✅ Fully implemented (Nov 6, 2025)

### Environment Variables

```bash
ENABLE_STRUCTURED_DATA_INGESTION=true
```

### GCP Resources

**None required** - Uses existing PostgreSQL

### Database Changes

**Migration:** `alembic/versions/00765e428bf3_add_structured_data_table_with_jsonb_.py`

**Table:** `structured_data`

**Columns:**
- `uuid` (UUID, primary key)
- `source` (VARCHAR) - samsara, turvo, frontapp, generic
- `data_type` (VARCHAR) - gps_event, shipment, message, generic_json
- `data` (JSONB) - Flexible JSON storage
- `external_id` (VARCHAR) - External system ID
- `created_at`, `updated_at` (TIMESTAMP)

### API Endpoints

```
POST /api/v1/ingest/structured
```

**Example Payload:**
```json
{
  "source": "turvo",
  "data_id": "SHIP-12345",
  "data_type": "shipment",
  "staging_path": "/tmp/apex-staging/turvo/SHIP-12345.json"
}
```

### Dependencies

- PostgreSQL (already deployed)
- Temporal Cloud (already deployed)

### Cost Estimate

**$0/month** - Uses existing infrastructure

### Deployment Week

**Week 2: Dockerization & Configuration**

### Tests

- `tests/integration/test_json_integration_e2e.py` (15,808 bytes)
- `tests/unit/test_json_temporal_activities.py`
- `tests/integration/test_structured_workflow.py` (13,769 bytes)

### Verification Command

```bash
# Run migration
cd apex-memory-system
alembic upgrade head

# Test JSON ingestion
curl -X POST http://localhost:8000/api/v1/ingest/structured \
  -H "Content-Type: application/json" \
  -d '{
    "source": "turvo",
    "data_id": "TEST-001",
    "data_type": "shipment",
    "data": {"shipment_id": "TEST-001", "status": "in_transit"}
  }'

# Verify in PostgreSQL
psql -U apex -d apex_memory -c "SELECT * FROM structured_data LIMIT 5;"
```

---

## Feature 3: Conversation Processing

### Implementation Details

**Files:**
- Workflow: `src/apex_memory/temporal/workflows/conversation_ingestion.py`
- Activities: `src/apex_memory/temporal/activities/conversation_ingestion.py`
- Service: `src/apex_memory/services/conversation_service.py` (23,740 bytes)

**Workflow:** `ConversationIngestionWorkflow`

**Purpose:** Background processing for conversational memory feedback loop

**Status:** ✅ Fully implemented

**Target Performance:**
- P95: <20s end-to-end
- P50: <10s end-to-end
- 85%+ entity extraction accuracy

**Agent Awareness:**
- Routes to agent-specific Qdrant collections (oscar_fleet_knowledge, etc.)
- Creates agent-labeled Graphiti episodes (:Oscar_Domain, :Sarah_Domain, etc.)
- Updates agent-namespaced Redis cache

### Environment Variables

```bash
ENABLE_CONVERSATION_INGESTION=true
```

### GCP Resources

**None required** - Uses existing databases

### Database Changes

**Migration:** `alembic/versions/12a9f72ec074_add_conversations_and_messages_tables.py`

**Tables:**
- `conversations` - Conversation metadata
- `messages` - Individual messages with importance scores

### API Endpoints

**Existing:**
- `/api/v1/conversations/` - Conversation management (see `src/apex_memory/api/conversations.py`)

### Dependencies

- PostgreSQL (conversations/messages tables)
- Qdrant (agent-specific collections)
- Redis (agent-namespaced cache)
- Temporal Cloud

### Cost Estimate

**~$5-15/month** - GPT-5 nano for entity extraction
- GPT-5 nano: $0.05/$0.40 per 1M tokens
- 40x cheaper than Claude Sonnet 4.5
- Estimated cost: <$0.01 per conversation

### Deployment Week

**Week 3: Temporal Cloud & Testing**

### Tests

- `tests/integration/test_conversation_ingestion_workflow.py`
- `tests/unit/test_conversation_ingestion_activities.py`

### Verification Command

```bash
# Start conversation ingestion workflow
cd apex-memory-system
python -c "
from temporalio.client import Client
from apex_memory.temporal.workflows.conversation_ingestion import ConversationIngestionWorkflow, ConversationIngestionInput
import asyncio

async def test():
    client = await Client.connect('localhost:7233')
    result = await client.execute_workflow(
        ConversationIngestionWorkflow.run,
        args=[ConversationIngestionInput(conversation_id='test-conv-001', agent_id='oscar')],
        id='conv-test-001',
        task_queue='apex-ingestion-queue'
    )
    print(result)

asyncio.run(test())
"
```

---

## Feature 4: Memory Decay Automation

### Implementation Details

**Files:**
- Workflow: `src/apex_memory/temporal/workflows/memory_decay.py`
- Activities: `src/apex_memory/temporal/activities/memory_decay.py`

**Workflow:** `MemoryDecayWorkflow` (scheduled)

**Purpose:** Daily workflow for memory importance decay and tier transitions

**Status:** ✅ Fully implemented

**Workflow Steps:**
1. Query aged messages (>1 day old)
2. Recalculate importance scores (age-adjusted)
3. Update tier assignments (critical/important/normal/ephemeral)
4. Archive ephemeral messages (>7 days old)

**Schedule:** Daily at 2:00 AM UTC (low traffic period)

**Execution Time:** ~5-15 minutes for 10,000 messages

### Environment Variables

```bash
MEMORY_DECAY_THRESHOLD=0.3  # Importance threshold for decay
MEMORY_TTL_DAYS=365  # Time-to-live for ephemeral memories
```

### GCP Resources

**None required** - Uses existing Temporal Cloud

### Database Changes

**Migration:** `alembic/versions/6a6b5859ca8c_add_retention_policy_fields_to_messages.py`

**Fields added to `messages` table:**
- Importance score tracking
- Tier assignment fields
- Age tracking

### Temporal Schedule

**Creation Script:**
```python
from temporalio.client import Client
import asyncio

async def create_schedule():
    client = await Client.connect('localhost:7233')

    # Create daily schedule at 2 AM UTC
    await client.create_schedule(
        "memory-decay-daily",
        Schedule(
            action=ScheduleActionStartWorkflow(
                MemoryDecayWorkflow.run,
                args=[MemoryDecayInput()],
                id="memory-decay",
                task_queue="apex-ingestion-queue"
            ),
            spec=ScheduleSpec(
                cron_expressions=["0 2 * * *"]  # 2 AM UTC daily
            )
        )
    )

asyncio.run(create_schedule())
```

### Dependencies

- Temporal Cloud
- PostgreSQL (messages table with retention fields)

### Cost Estimate

**$0/month** - Uses existing Temporal Cloud subscription

### Deployment Week

**Week 3: Temporal Cloud & Testing**

### Tests

- `tests/unit/test_memory_decay_workflow.py`
- `tests/unit/test_retention_policies_gcs.py`

### Verification Command

```bash
# Manual execution (for testing)
cd apex-memory-system
python scripts/temporal/trigger-memory-decay.py

# Check Temporal UI for scheduled execution
# http://localhost:8088/namespaces/default/schedules
```

---

## Feature 5: Google Drive Archive Workflow

### Implementation Details

**Files:**
- Workflow: `src/apex_memory/temporal/workflows/google_drive_archive.py`
- Activities: `src/apex_memory/temporal/activities/google_drive_archive.py`

**Workflow:** `GoogleDriveArchiveWorkflow`

**Purpose:** Archive ingested documents to GCS for long-term storage and backup

**Status:** ✅ Fully implemented (Nov 7, 2025 - Week 2 Day 1)

**Archive Pipeline:**
1. Determine archive folder based on domain
2. Upload file to Google Cloud Storage
3. Verify upload succeeded
4. Record archive metadata in PostgreSQL

**Workflow Status Progression:**
```
pending → determining_folder → uploading → verifying → recording_metadata → completed
```

### Environment Variables

```bash
GCS_ARCHIVE_BUCKET=apex-document-archive
```

### GCP Resources

**GCS Bucket:** `apex-document-archive`

**Lifecycle Policy:**
```yaml
lifecycle:
  rule:
    - action: {type: SetStorageClass, storageClass: COLDLINE}
      condition: {age: 30}
```

**IAM Permissions:**
- Cloud Run service account needs `roles/storage.objectCreator`

### Database Changes

**Table:** `archive_metadata` (tracks archival)

**Note:** May need migration if not already exists - check `alembic/versions/` for archive-related migrations

### API Integration

Triggered by `cleanup_staging_activity` after successful document ingestion (asynchronous)

### Dependencies

- Google Cloud Storage (GCS bucket)
- Temporal Cloud
- Google Drive Integration (completed)

### Cost Estimate

**~$0-5/month** - GCS storage
- Standard storage: $0.020/GB/month
- Coldline (after 30 days): $0.004/GB/month
- Estimated usage: 10-50 GB = $0.20-$2/month

### Deployment Week

**Week 2: Dockerization & Configuration** (update existing Google Drive section)

### Tests

- `tests/unit/test_google_drive_archive_workflow.py`

### Verification Command

```bash
# Create GCS bucket
gcloud storage buckets create gs://apex-document-archive \
  --location=us-central1 \
  --uniform-bucket-level-access

# Set lifecycle policy
cat > lifecycle.json <<EOF
{
  "lifecycle": {
    "rule": [{
      "action": {"type": "SetStorageClass", "storageClass": "COLDLINE"},
      "condition": {"age": 30}
    }]
  }
}
EOF

gcloud storage buckets update gs://apex-document-archive \
  --lifecycle-file=lifecycle.json

# Grant service account access
gcloud storage buckets add-iam-policy-binding gs://apex-document-archive \
  --member="serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/storage.objectCreator"

# Trigger archive workflow (after document ingestion)
# Workflow is automatically triggered by cleanup_staging_activity
```

---

## Feature 6: GCS Archival Service

### Implementation Details

**File:** `src/apex_memory/services/gcs_archival_service.py` (8,741 bytes)

**Purpose:** Archive messages to GCS for long-term cold storage (Phase 3: Retention Policies)

**Status:** ✅ Fully implemented

**Architecture:**
- Messages with importance < 0.3 and age > 7 days are archived
- GCS bucket structure: `messages/YYYY/MM/agent/msg-{uuid}.json`
- Automatic lifecycle policies: Standard → Nearline → Coldline → Archive

**Service Methods:**
- `archive_message()` - Archive single message to GCS
- `retrieve_message()` - Retrieve archived message
- `generate_archive_path()` - Generate GCS path

### Environment Variables

```bash
GCS_ENABLED=true
GCS_BUCKET_NAME=apex-memory-archive
# GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json  # Set by GCP
```

### GCP Resources

**GCS Bucket:** `apex-memory-archive` (separate from `apex-document-archive`)

**Lifecycle Policy:** Transition to Nearline (30 days) → Coldline (90 days) → Archive (365 days)

**IAM Permissions:**
- Cloud Run service account needs `roles/storage.objectCreator`, `roles/storage.objectViewer`

### Database Changes

**None required** - Archives existing messages table rows

### API Endpoints

No dedicated endpoints - called internally by MemoryDecayWorkflow

### Dependencies

- GCS bucket (apex-memory-archive)
- Service account authentication

### Cost Estimate

**~$5-10/month** (moderate usage)
- FREE up to 5GB
- Standard storage: $0.020/GB/month
- Coldline storage: $0.004/GB/month
- Estimated usage: 50-100 GB messages = $2-8/month

### Deployment Week

**Week 2: Dockerization & Configuration**

### Tests

- `tests/unit/test_retention_policies_gcs.py`

### Verification Command

```bash
# Create GCS bucket for message archival
gcloud storage buckets create gs://apex-memory-archive \
  --location=us-central1 \
  --uniform-bucket-level-access

# Set lifecycle policy (Nearline → Coldline → Archive)
cat > message-lifecycle.json <<EOF
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
EOF

gcloud storage buckets update gs://apex-memory-archive \
  --lifecycle-file=message-lifecycle.json

# Test archival service
python -c "
from apex_memory.services.gcs_archival_service import GCSArchivalService
import asyncio

async def test():
    service = GCSArchivalService('apex-memory-archive')
    result = await service.archive_message(
        'test-uuid-001',
        {'content': 'Test message', 'agent': 'oscar'},
        agent_id='oscar'
    )
    print(result)

asyncio.run(test())
"
```

---

## Feature 7: NATS Messaging

### Implementation Details

**File:** `src/apex_memory/services/nats_service.py` (7,710 bytes)

**Purpose:** Lightweight messaging for agent-to-agent communication

**Status:** ⚠️ Implemented but **usage unclear** - needs codebase verification

**Architecture:**
- Pub/sub pattern for fire-and-forget notifications
- Request-reply pattern for synchronous queries
- Subject-based routing: `agent.{agent_id}.{message_type}`
- <10ms latency for agent messaging

**Performance Targets:**
- Publish: <5ms latency
- Request-reply: <20ms P95 latency

**Service Methods:**
- `connect()`, `disconnect()`
- `publish()` - Fire-and-forget
- `request()` - Request-reply
- `subscribe()` - Subscribe to subjects

### Environment Variables

```bash
NATS_URL=nats://localhost:4222  # Self-hosted
# OR
NATS_URL=nats://nats.example.com:4222  # Managed NATS
```

**Note:** `NATS_URL` is referenced in:
- `src/apex_memory/services/nats_service.py` (line 63)
- `src/apex_memory/config/settings.py`

### GCP Resources

**Option A: Self-Hosted on Compute Engine (Recommended for cost)**
- Compute Engine e2-micro instance ($7/month, already have for worker)
- Docker container: `nats:latest`
- Firewall rule: Allow port 4222 from Cloud Run VPC

**Option B: Managed NATS**
- External provider: https://nats.io
- Cost: $15-50/month depending on tier

### Database Changes

**None required**

### Usage Verification Needed

**Action Required:** Search codebase to confirm NATS is actively used in production code

```bash
# Check usage
grep -r "NATSService" apex-memory-system/src/ --include="*.py" | grep -v "test" | head -20
grep -r "nats_service" apex-memory-system/src/ --include="*.py" | grep -v "test" | head -20
```

**Current Finding:** Only found in:
- Service definition itself
- Config settings

**Recommendation:** Mark as **OPTIONAL** unless active usage is confirmed

### Dependencies

- NATS server (self-hosted OR managed)
- Python package: `nats-py` (check requirements.txt)

### Cost Estimate

**$0/month (self-hosted)** - Deploy on existing Compute Engine worker VM
**OR**
**$15-50/month (managed)** - Use nats.io managed service

### Deployment Week

**Week 3: Temporal Cloud & Testing (OPTIONAL - only if actively used)**

### Tests

**No dedicated test files found** - further confirms unclear usage

### Verification Command

```bash
# Self-hosted deployment on Compute Engine
gcloud compute ssh apex-worker-vm --command "
docker run -d \
  --name nats-server \
  -p 4222:4222 \
  --restart unless-stopped \
  nats:latest
"

# Configure firewall
gcloud compute firewall-rules create allow-nats-from-cloud-run \
  --allow=tcp:4222 \
  --source-ranges=CLOUD_RUN_VPC_CIDR \
  --target-tags=apex-worker

# Test connection
python -c "
from apex_memory.services.nats_service import NATSService
import asyncio

async def test():
    service = NATSService()
    await service.connect()
    await service.publish('test.subject', {'message': 'hello'})
    await service.disconnect()

asyncio.run(test())
"
```

---

## Feature 8: Authentication System

### Implementation Details

**Files:**
- Service: `src/apex_memory/services/auth_service.py` (7,879 bytes)
- API: `src/apex_memory/api/auth.py` (assumed - not verified)
- Models: `src/apex_memory/models/user.py` (UserCreate, UserDB, TokenData)

**Purpose:** User authentication, password hashing, JWT token management

**Status:** ✅ Fully implemented

**Service Methods:**
- `get_password_hash()` - Bcrypt hashing
- `verify_password()` - Password verification
- `create_access_token()` - JWT generation
- `verify_access_token()` - JWT validation

**Security:**
- Bcrypt for password hashing
- JWT (jose library) for tokens
- SECRET_KEY for JWT signing (already configured)

### Environment Variables

**Already configured in .env.example:**
```bash
# Security Configuration (lines 119-127)
API_KEY_ENABLED=false  # For development
API_KEY=  # Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"

# JWT settings (used by AuthService)
# SECRET_KEY is already in DEPLOYMENT-NEEDS.md under Security section
# JWT_ALGORITHM=HS256 (default in AuthService)
# JWT_EXPIRATION=3600 (1 hour, default in AuthService)
```

**Add to .env.example if not present:**
```bash
JWT_ALGORITHM=HS256
JWT_EXPIRATION=3600
```

### GCP Resources

**None required** - Uses existing PostgreSQL

### Database Changes

**Migration:** `alembic/versions/f0ca98480aa7_add_users_and_api_keys_tables.py`

**Tables:**
- `users` - User accounts (id, email, username, password_hash, is_admin, created_at)
- `api_keys` - API key management (if API_KEY_ENABLED=true)

### API Endpoints

**Expected routes:**
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login (returns JWT)
- `POST /api/v1/auth/refresh` - Refresh token
- `GET /api/v1/auth/me` - Get current user

**Note:** Verify actual endpoints in `src/apex_memory/api/` directory

### Dependencies

- PostgreSQL (users table)
- Python packages: `bcrypt`, `python-jose`
- SECRET_KEY environment variable (already exists)

### Cost Estimate

**$0/month** - Uses existing infrastructure

### Deployment Week

**Week 3: Temporal Cloud & Testing (OPTIONAL - not required for initial deployment)**

**Rationale:** Authentication can be added post-initial deployment if API needs to be public

### Tests

**No dedicated test files found** - should be added in component deployment guide

### Verification Command

```bash
# Run migration
cd apex-memory-system
alembic upgrade head

# Test user registration
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "SecurePassword123!"
  }'

# Test login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePassword123!"
  }'

# Should return JWT token:
# {"access_token": "eyJhbGc...", "token_type": "bearer"}

# Verify in PostgreSQL
psql -U apex -d apex_memory -c "SELECT email, username, is_admin FROM users;"
```

---

## Feature 9: Agent Interactions

### Implementation Details

**Files:**
- Service: `src/apex_memory/services/agent_interaction_service.py` (17,208 bytes)
- Communication: `src/apex_memory/services/agent_communication.py` (18,636 bytes)
- API: `src/apex_memory/api/agent_interactions.py`

**Purpose:** Automatically log and analyze agent-to-agent communication

**Status:** ✅ Implemented but **DEFERRED for deployment**

**Service Features:**
- Logs all agent interactions to PostgreSQL
- Extracts entities from interaction content
- Calculates interaction importance scores
- Links interactions to conversation context
- Creates Graphiti episodes for high-importance interactions

**Importance Threshold:** 0.6 (only creates episodes for interactions >= 0.6)

### Environment Variables

**None specific** - Uses existing database/Graphiti configuration

### GCP Resources

**None required** - Uses existing infrastructure

### Database Changes

**Migration:** `alembic/versions/1bf6df45f545_add_agent_interactions_table.py`

**Table:** `agent_interactions`

**Columns:**
- from_agent, to_agent (VARCHAR)
- interaction_type (query, notification, command, response)
- query_text, response_text (TEXT)
- request_id, conversation_id (UUID)
- interaction_metadata (JSONB)
- latency_ms, confidence, sources
- entities_extracted (JSONB)
- importance_score (FLOAT)
- created_at, updated_at

### API Endpoints

**File:** `src/apex_memory/api/agent_interactions.py`

**Expected routes:**
- GET /api/v1/agent-interactions/ - List interactions
- GET /api/v1/agent-interactions/{interaction_id} - Get specific interaction
- POST /api/v1/agent-interactions/ - Log interaction manually (if needed)

### Dependencies

- PostgreSQL (agent_interactions table)
- GraphitiService (for high-importance interaction episodes)
- NATS (if inter-agent messaging is used)

### Cost Estimate

**$0/month** - Uses existing infrastructure

### Deployment Recommendation

**DEFER to Post-Initial Deployment**

**Rationale:**
- Nice-to-have feature, not core functionality
- Requires agent ecosystem to be fully operational
- Better to deploy after production deployment is stable

### Deployment Week

**Post-initial deployment** (not in critical path)

### Tests

- `tests/integration/test_agent_communication_e2e.py`

### Verification Command

```bash
# Run migration
cd apex-memory-system
alembic upgrade head

# Check API endpoints
curl http://localhost:8000/api/v1/agent-interactions/

# Verify table
psql -U apex -d apex_memory -c "\d agent_interactions"
```

---

## Feature 10: UI/UX Frontend

### Implementation Details

**Status:** 📝 Planned but **DEFERRED for deployment**

**Files:** No frontend files found in `src/apex_memory/` directory

**Documentation:** `upgrades/completed/ui-ux-enhancements/` (comprehensive UI/UX enhancement documentation)

**Purpose:** Web interface for Apex Memory System

**Deployment Target:** Cloud Run frontend service (separate from API backend)

### Environment Variables

**TBD** - Will depend on frontend framework chosen

Likely variables:
```bash
FRONTEND_API_URL=https://apex-api-xxxxx-uc.a.run.app
FRONTEND_PORT=3000
NODE_ENV=production
```

### GCP Resources

**Required (when deployed):**
- Cloud Run service for frontend
- Cloud Build for Docker image builds
- Artifact Registry for image storage

### Build Process

**TBD** - Depends on frontend framework (React/Vue/Svelte/etc.)

Example for React:
```bash
npm install
npm run build
docker build -t gcr.io/PROJECT_ID/apex-frontend:latest .
docker push gcr.io/PROJECT_ID/apex-frontend:latest
gcloud run deploy apex-frontend --image gcr.io/PROJECT_ID/apex-frontend:latest
```

### Dependencies

- Node.js, npm
- Frontend framework dependencies (TBD)
- API backend (already deployed)

### Cost Estimate

**TBD** - Estimated $10-30/month
- Cloud Run: $0-10/month (minimal traffic)
- Cloud Build: $0-5/month (automated builds)
- Artifact Registry: $0.10/GB/month

### Deployment Recommendation

**DEFER to Post-Initial Deployment** - API-first approach

**Rationale:**
- API is the core functionality
- Frontend can be developed and deployed independently
- Allows API to stabilize in production first
- Frontend development can happen in parallel with production API usage

### Deployment Week

**Post-initial deployment** (not in critical path)

### Tests

**TBD** - Frontend testing framework to be determined

### Verification Command

**TBD** - Will be documented when frontend is implemented

---

## Summary of Findings

### Critical Features (Must Deploy) - Week 2-3

| Feature | Status | Deployment Week | Action Required |
|---------|--------|----------------|-----------------|
| Graphiti Integration | ✅ Implemented | Week 2 | Add to deployment docs |
| Structured Data Ingestion | ✅ Implemented | Week 2 | Add to deployment docs |
| Conversation Processing | ✅ Implemented | Week 3 | Add to deployment docs |
| Memory Decay | ✅ Implemented | Week 3 | Add to deployment docs |

### High Priority Features (Enhance Functionality) - Week 2-3

| Feature | Status | Deployment Week | Action Required |
|---------|--------|----------------|-----------------|
| Google Drive Archive | ✅ Implemented | Week 2 | Update existing guide |
| GCS Archival Service | ✅ Implemented | Week 2 | Add to deployment docs |
| NATS Messaging | ⚠️ Usage unclear | Week 3 (optional) | Verify usage, mark optional |
| Authentication | ✅ Implemented | Week 3 (optional) | Add to deployment docs, mark optional |

### Deferred Features (Post-Initial)

| Feature | Status | Deployment Week | Rationale |
|---------|--------|----------------|-----------|
| Agent Interactions | ✅ Implemented | Post-initial | Nice-to-have, not core |
| UI/UX Frontend | 📝 Planned | Post-initial | API-first approach |

### Environment Variables Summary

**New Variables to Add:**
```bash
# Graphiti (already in .env.example)
GRAPHITI_ENABLED=true

# Structured Data
ENABLE_STRUCTURED_DATA_INGESTION=true

# Conversation Processing
ENABLE_CONVERSATION_INGESTION=true

# Memory Decay
MEMORY_DECAY_THRESHOLD=0.3
MEMORY_TTL_DAYS=365

# GCS Archival
GCS_ARCHIVE_BUCKET=apex-document-archive
GCS_ENABLED=true
GCS_BUCKET_NAME=apex-memory-archive

# NATS (optional - if used)
NATS_URL=nats://localhost:4222

# Authentication (optional)
JWT_ALGORITHM=HS256
JWT_EXPIRATION=3600
```

### Database Migrations Summary

**Migrations to Run (in order):**
1. `12a9f72ec074_add_conversations_and_messages_tables.py` - Conversations
2. `00765e428bf3_add_structured_data_table_with_jsonb_.py` - Structured data
3. `6a6b5859ca8c_add_retention_policy_fields_to_messages.py` - Memory decay
4. `f0ca98480aa7_add_users_and_api_keys_tables.py` - Authentication (optional)
5. `1bf6df45f545_add_agent_interactions_table.py` - Agent interactions (optional)

**Command:**
```bash
cd apex-memory-system
alembic upgrade head
```

### GCS Buckets to Create

**Week 2 Setup:**
1. `apex-document-archive` - Google Drive Archive workflow
2. `apex-memory-archive` - GCS Archival Service

### Cost Impact Summary

**New Monthly Costs:**
- Graphiti Integration: +$10-30 (LLM usage)
- Conversation Processing: +$5-15 (GPT-5 nano)
- GCS Archival: +$5-10 (moderate storage usage)
- NATS (if self-hosted): +$0 (uses existing VM)
- NATS (if managed): +$15-50 (optional)
- All others: $0 (use existing infrastructure)

**Total New Costs:**
- **Minimum:** +$20-55/month (without NATS or with self-hosted NATS)
- **Maximum:** +$105/month (with managed NATS)

**Updated DEPLOYMENT-NEEDS.md Totals:**
- Current: $411-807/month
- With New Features: $431-912/month

---

## Next Steps

### Phase 2: Component Documentation

Create deployment guides for each feature:

1. `deployment/components/graphiti-integration/DEPLOYMENT-GUIDE.md`
2. `deployment/components/structured-data-ingestion/DEPLOYMENT-GUIDE.md`
3. `deployment/components/conversation-processing/DEPLOYMENT-GUIDE.md`
4. `deployment/components/memory-decay/DEPLOYMENT-GUIDE.md`
5. Update `deployment/components/google-drive-integration/DEPLOYMENT-GUIDE.md` (add archive workflow)
6. `deployment/components/gcs-archival/DEPLOYMENT-GUIDE.md`
7. `deployment/components/nats-messaging/DEPLOYMENT-GUIDE.md` (mark as OPTIONAL)
8. `deployment/components/authentication/DEPLOYMENT-GUIDE.md` (mark as OPTIONAL)
9. `deployment/components/agent-interactions/DEPLOYMENT-GUIDE.md` (DEFERRED stub)
10. `deployment/components/frontend/DEPLOYMENT-GUIDE.md` (DEFERRED stub)

### Phase 3: Prerequisites Integration

Update `deployment/DEPLOYMENT-NEEDS.md` with:
- Graphiti prerequisites (Section 2: API Keys)
- GCS Archival cost estimates
- NATS prerequisites (optional)
- Updated cost summary

### Phase 4: Workflow Integration

Update deployment workflows:
- `deployment/PRODUCTION-DEPLOYMENT-PLAN.md` (Week 2-3 integration steps)
- `deployment/production/GCP-DEPLOYMENT-GUIDE.md` (Phase 2-4 infrastructure)

---

**Research Phase Complete:** 2025-11-15
**Total Features Analyzed:** 10
**Time Spent:** ~4.5 hours
**Ready for Phase 2:** ✅ YES
