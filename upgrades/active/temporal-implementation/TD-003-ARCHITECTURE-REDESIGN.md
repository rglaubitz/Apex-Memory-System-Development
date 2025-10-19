# TD-003: Architecture Redesign - Temporal-Orchestrated Ingestion

**Date:** 2025-10-18
**Status:** 🔄 In Design
**Priority:** Critical - Architectural Foundation

---

## Problem Statement

**Original Issue (from TECHNICAL-DEBT.md TD-003):**
> "S3 Staging Area Not Orchestrated by Temporal - The S3 bucket is currently used as a staging area, but Temporal doesn't orchestrate the upload step. External systems push to S3, then Temporal downloads. Wasn't the whole point of Temporal to orchestrate pulling from various sources?"

**Deeper Architectural Issue Discovered:**
1. **Wrong assumption**: S3 staging is needed for all data sources
2. **Wrong assumption**: Structured data can skip parts of the pipeline
3. **Missing orchestration**: Temporal doesn't control the source → staging flow
4. **Wrong staging location**: S3 cloud storage when local folder is sufficient

**User's Critical Correction:**
> "structured data wouldnt feed directly into databases... that skips like half the database architecture. graphitti, embedder models, and the saga pattern thing we built."

---

## Research Summary

### Data Source Types (Official API Documentation)

**1. Document Sources** (require parsing):
- FrontApp email attachments (PDF, DOCX)
- Local file uploads via API
- Carrier EDI file batches

**2. Structured Data Sources** (JSON format):
- **Samsara Fleet Telemetry** (~1,000 events/min):
```json
{
  "data": [{
    "happenedAtTime": "2025-03-10T14:15:06Z",
    "location": {"latitude": 43.94845637, "longitude": -72.53393359},
    "speed": 45.6,
    "odometer": 123456.78
  }]
}
```

- **FrontApp Webhooks** (~1,000/day):
```json
{
  "type": "inbound_received",
  "payload": {
    "id": "msg_123",
    "body": "Customer inquiry message content...",
    "subject": "Re: Shipment #12345",
    "from": {"email": "customer@example.com"}
  }
}
```

- **Turvo TMS** (~500/day):
```json
{
  "shipment_id": "SHIP-12345",
  "status": "in_transit",
  "pickup": {"location": "Chicago, IL", "timestamp": "2025-03-10T08:00:00Z"},
  "delivery": {"location": "Denver, CO", "eta": "2025-03-11T16:00:00Z"}
}
```

### Temporal.io Best Practices (Official Docs)

**Payload Limits:**
- Maximum payload size: **2MB** per workflow/activity
- Recommendation: "Store the actual data in a blob store like AWS S3 and instead passing the URL"
- **Best practice**: Pass references (IDs, URLs, file paths) between activities

**Activity Pattern (from official tutorial):**
```python
@workflow.defn
class DataPipelineWorkflow:
    @workflow.run
    async def run(self, data_id: str) -> dict:
        # Activity 1: Fetch data
        raw_data = await workflow.execute_activity(
            fetch_data_activity,
            data_id,
            start_to_close_timeout=timedelta(minutes=5)
        )

        # Activity 2: Process data
        processed = await workflow.execute_activity(
            process_data_activity,
            raw_data,
            start_to_close_timeout=timedelta(minutes=3)
        )

        # Activity 3: Store results
        result = await workflow.execute_activity(
            store_data_activity,
            processed,
            start_to_close_timeout=timedelta(minutes=2)
        )

        return result
```

**Key Insights:**
- ✅ Each step is a separate activity (retry isolation)
- ✅ Activities chain results to next activity
- ✅ Workflow orchestrates the entire sequence
- ✅ Each activity has independent timeout and retry policy

### Apex Memory Pipeline Architecture

**ALL data (documents AND structured) must flow through:**
1. **Graphiti** - Entity extraction + relationship building
2. **Embedder models** - Vector embeddings generation
3. **Enhanced Saga pattern** - Atomic 4-database writes with rollback

**Critical Rule:** No shortcuts directly to databases (this was the core misunderstanding)

---

## Corrected Architecture Design

### Overview: Two Distinct Workflows

```
┌─────────────────────────────────────────────────────────────┐
│                   DATA SOURCE ROUTER                         │
│  (Determines which workflow to use based on data type)       │
└─────────────────────────────────────────────────────────────┘
                          │
                          ├──────────────────┬─────────────────┐
                          ▼                  ▼                 ▼
              ┌───────────────────┐ ┌──────────────┐ ┌───────────────┐
              │   PDF / DOCX      │ │  Samsara GPS │ │  Turvo JSON   │
              │   Email Attach    │ │  FrontApp    │ │  Bank Exports │
              └───────────────────┘ └──────────────┘ └───────────────┘
                          │                  │                 │
                          ▼                  ▼                 ▼
              ┌───────────────────┐ ┌──────────────────────────────┐
              │  DOCUMENT         │ │  STRUCTURED DATA             │
              │  INGESTION        │ │  INGESTION                   │
              │  WORKFLOW         │ │  WORKFLOW                    │
              └───────────────────┘ └──────────────────────────────┘
                          │                  │
                          └──────────┬───────┘
                                     ▼
                          ┌──────────────────┐
                          │   GRAPHITI       │
                          │   Entity Extract │
                          └──────────────────┘
                                     ▼
                          ┌──────────────────┐
                          │   EMBEDDINGS     │
                          │   Generation     │
                          └──────────────────┘
                                     ▼
                          ┌──────────────────┐
                          │  ENHANCED SAGA   │
                          │  4-DB Writes     │
                          └──────────────────┘
                                     ▼
              ┌─────────┬──────────┬──────────┬──────────┐
              ▼         ▼          ▼          ▼          ▼
          ┌──────┐ ┌──────┐ ┌──────────┐ ┌────────┐ ┌───────┐
          │Neo4j │ │Qdrant│ │PostgreSQL│ │Graphiti│ │ Redis │
          └──────┘ └──────┘ └──────────┘ └────────┘ └───────┘
```

### Workflow 1: Document Ingestion Workflow

**Purpose:** Handle binary documents (PDF, DOCX, PPTX) requiring parsing

**Local Folder Staging:** `/tmp/apex-staging/{source}/{document_id}/`

**Activities:**

```python
@workflow.defn
class DocumentIngestionWorkflow:
    """
    Orchestrates ingestion of binary documents requiring parsing.

    Flow: Source → Local Staging → Docling Parse → Graphiti → Embeddings → Saga → Databases
    """

    @workflow.run
    async def run(
        self,
        document_id: str,
        source: str,  # "frontapp", "local_upload", "edi_batch"
        source_location: str,  # URL, file path, or API endpoint
    ) -> dict:
        """
        Execute document ingestion workflow.

        Args:
            document_id: Unique document identifier (UUID)
            source: Data source name
            source_location: Where to fetch the document from

        Returns:
            Ingestion result with database write confirmations
        """

        # ========================================
        # ACTIVITY 1: Pull from source → Local staging
        # ========================================
        staging_path = await workflow.execute_activity(
            pull_and_stage_document_activity,
            args=[document_id, source, source_location],
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=RetryPolicy(
                initial_interval=timedelta(seconds=1),
                maximum_interval=timedelta(seconds=10),
                maximum_attempts=3,
            ),
        )
        # Returns: "/tmp/apex-staging/frontapp/doc-uuid-123/document.pdf"

        # ========================================
        # ACTIVITY 2: Parse document with Docling
        # ========================================
        parsed_doc = await workflow.execute_activity(
            docling_parse_activity,
            args=[staging_path],
            start_to_close_timeout=timedelta(minutes=3),
            retry_policy=RetryPolicy(
                initial_interval=timedelta(seconds=2),
                maximum_interval=timedelta(seconds=20),
                maximum_attempts=3,
            ),
        )
        # Returns: ParsedDocument object with text, tables, metadata

        # ========================================
        # ACTIVITY 3: Extract entities with Graphiti
        # ========================================
        entities = await workflow.execute_activity(
            graphiti_extract_entities_activity,
            args=[parsed_doc, source],
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=RetryPolicy(
                initial_interval=timedelta(seconds=2),
                maximum_interval=timedelta(seconds=30),
                maximum_attempts=3,
            ),
        )
        # Returns: List[Entity] with relationships

        # ========================================
        # ACTIVITY 4: Generate embeddings
        # ========================================
        embeddings = await workflow.execute_activity(
            generate_embeddings_activity,
            args=[parsed_doc],
            start_to_close_timeout=timedelta(minutes=3),
            retry_policy=RetryPolicy(
                initial_interval=timedelta(seconds=1),
                maximum_interval=timedelta(seconds=10),
                maximum_attempts=5,  # OpenAI can have transient failures
            ),
        )
        # Returns: List[float] vector embeddings

        # ========================================
        # ACTIVITY 5: Write to databases (Enhanced Saga)
        # ========================================
        saga_result = await workflow.execute_activity(
            saga_write_databases_activity,
            args=[document_id, source, parsed_doc, entities, embeddings],
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=RetryPolicy(
                initial_interval=timedelta(seconds=2),
                maximum_interval=timedelta(seconds=30),
                maximum_attempts=3,
            ),
        )
        # Returns: Dict with write confirmations from all 4 databases

        # ========================================
        # ACTIVITY 6: Cleanup staging directory
        # ========================================
        await workflow.execute_activity(
            cleanup_staging_activity,
            args=[staging_path],
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=RetryPolicy(
                initial_interval=timedelta(seconds=1),
                maximum_interval=timedelta(seconds=5),
                maximum_attempts=3,
            ),
        )

        return {
            "document_id": document_id,
            "source": source,
            "status": "completed",
            "databases_written": saga_result,
            "entities_extracted": len(entities),
            "chunks_created": len(parsed_doc.chunks),
        }
```

**Activity Implementations:**

```python
# ============================================================================
# ACTIVITY 1: Pull and Stage Document
# ============================================================================
@activity.defn(name="pull_and_stage_document")
async def pull_and_stage_document_activity(
    document_id: str,
    source: str,
    source_location: str,
) -> str:
    """
    Pull document from source and write to local staging folder.

    Handles:
    - FrontApp API downloads (via OAuth)
    - Local file system moves
    - HTTP/HTTPS URL downloads

    Returns:
        Local staging path: "/tmp/apex-staging/{source}/{document_id}/filename.ext"
    """
    staging_dir = f"/tmp/apex-staging/{source}/{document_id}"
    os.makedirs(staging_dir, exist_ok=True)

    if source == "frontapp":
        # Pull via FrontApp API
        attachment = await frontapp_client.get_attachment(source_location)
        file_path = f"{staging_dir}/{attachment.filename}"
        with open(file_path, "wb") as f:
            f.write(attachment.content)

    elif source == "local_upload":
        # Move from temporary upload location
        shutil.copy(source_location, staging_dir)
        file_path = f"{staging_dir}/{os.path.basename(source_location)}"

    elif source.startswith("http"):
        # Download via HTTP
        response = await http_client.get(source_location)
        filename = response.headers.get("Content-Disposition", "document.pdf")
        file_path = f"{staging_dir}/{filename}"
        with open(file_path, "wb") as f:
            f.write(response.content)

    # Emit metric
    metrics.apex_temporal_staging_bytes_written.labels(
        source=source
    ).observe(os.path.getsize(file_path))

    return file_path


# ============================================================================
# ACTIVITY 2: Parse with Docling (REUSE EXISTING)
# ============================================================================
# Already implemented in:
# apex-memory-system/src/apex_memory/temporal/activities/ingestion.py:parse_document_activity


# ============================================================================
# ACTIVITY 3: Extract Entities (REUSE EXISTING)
# ============================================================================
# Already implemented in:
# apex-memory-system/src/apex_memory/temporal/activities/ingestion.py:extract_entities_activity


# ============================================================================
# ACTIVITY 4: Generate Embeddings (REUSE EXISTING)
# ============================================================================
# Already implemented in:
# apex-memory-system/src/apex_memory/temporal/activities/ingestion.py:generate_embeddings_activity


# ============================================================================
# ACTIVITY 5: Saga Write to Databases (REUSE EXISTING)
# ============================================================================
# Already implemented in:
# apex-memory-system/src/apex_memory/temporal/activities/ingestion.py:write_to_databases_activity


# ============================================================================
# ACTIVITY 6: Cleanup Staging
# ============================================================================
@activity.defn(name="cleanup_staging")
async def cleanup_staging_activity(staging_path: str) -> None:
    """
    Remove staging directory after successful ingestion.

    Args:
        staging_path: Path to staging file or directory
    """
    staging_dir = os.path.dirname(staging_path)

    if os.path.exists(staging_dir):
        shutil.rmtree(staging_dir)
        activity.logger.info(f"Cleaned up staging directory: {staging_dir}")

    # Emit metric
    metrics.apex_temporal_staging_cleanups_total.labels(
        status="success"
    ).inc()
```

---

### Workflow 2: Structured Data Ingestion Workflow

**Purpose:** Handle JSON data from APIs/webhooks (Samsara, Turvo, FrontApp messages)

**No staging needed** - JSON data passed directly (under 2MB limit)

**Activities:**

```python
@workflow.defn
class StructuredDataIngestionWorkflow:
    """
    Orchestrates ingestion of structured JSON data.

    Flow: Source API → Graphiti → Embeddings → Saga → Databases

    No Docling parsing needed (already structured).
    No staging needed (JSON fits in 2MB payload limit).
    """

    @workflow.run
    async def run(
        self,
        data_id: str,
        source: str,  # "samsara", "turvo", "frontapp_webhook"
        source_endpoint: str,  # API endpoint or webhook payload
        data_type: str,  # "gps_event", "shipment", "message"
    ) -> dict:
        """
        Execute structured data ingestion workflow.

        Args:
            data_id: Unique data identifier (UUID or external ID)
            source: Data source name
            source_endpoint: API endpoint to fetch from
            data_type: Type of structured data

        Returns:
            Ingestion result with database write confirmations
        """

        # ========================================
        # ACTIVITY 1: Fetch structured data from source
        # ========================================
        raw_json = await workflow.execute_activity(
            fetch_structured_data_activity,
            args=[data_id, source, source_endpoint, data_type],
            start_to_close_timeout=timedelta(minutes=2),
            retry_policy=RetryPolicy(
                initial_interval=timedelta(seconds=1),
                maximum_interval=timedelta(seconds=10),
                maximum_attempts=5,  # External APIs can be flaky
            ),
        )
        # Returns: Dict with raw JSON from API

        # ========================================
        # ACTIVITY 2: Extract entities with Graphiti
        # ========================================
        entities = await workflow.execute_activity(
            graphiti_extract_from_json_activity,
            args=[raw_json, source, data_type],
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=RetryPolicy(
                initial_interval=timedelta(seconds=2),
                maximum_interval=timedelta(seconds=30),
                maximum_attempts=3,
            ),
        )
        # Returns: List[Entity] with relationships

        # ========================================
        # ACTIVITY 3: Generate embeddings
        # ========================================
        embeddings = await workflow.execute_activity(
            generate_embeddings_from_json_activity,
            args=[raw_json, data_type],
            start_to_close_timeout=timedelta(minutes=3),
            retry_policy=RetryPolicy(
                initial_interval=timedelta(seconds=1),
                maximum_interval=timedelta(seconds=10),
                maximum_attempts=5,
            ),
        )
        # Returns: List[float] vector embeddings

        # ========================================
        # ACTIVITY 4: Write to databases (Enhanced Saga)
        # ========================================
        saga_result = await workflow.execute_activity(
            saga_write_structured_data_activity,
            args=[data_id, source, data_type, raw_json, entities, embeddings],
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=RetryPolicy(
                initial_interval=timedelta(seconds=2),
                maximum_interval=timedelta(seconds=30),
                maximum_attempts=3,
            ),
        )
        # Returns: Dict with write confirmations from all 4 databases

        return {
            "data_id": data_id,
            "source": source,
            "data_type": data_type,
            "status": "completed",
            "databases_written": saga_result,
            "entities_extracted": len(entities),
        }
```

**Activity Implementations:**

```python
# ============================================================================
# ACTIVITY 1: Fetch Structured Data
# ============================================================================
@activity.defn(name="fetch_structured_data")
async def fetch_structured_data_activity(
    data_id: str,
    source: str,
    source_endpoint: str,
    data_type: str,
) -> dict:
    """
    Fetch structured JSON data from external API.

    Handles:
    - Samsara GPS telemetry (via REST API)
    - Turvo shipment data (via REST API)
    - FrontApp webhook payloads (already in memory)

    Returns:
        Raw JSON dictionary from source
    """
    if source == "samsara":
        # Fetch via Samsara API
        response = await samsara_client.get_vehicle_location(data_id)
        return response.json()

    elif source == "turvo":
        # Fetch via Turvo API
        response = await turvo_client.get_shipment(data_id)
        return response.json()

    elif source == "frontapp_webhook":
        # Webhook payload already provided via source_endpoint (JSON string)
        return json.loads(source_endpoint)

    # Emit metric
    metrics.apex_temporal_structured_data_fetched_total.labels(
        source=source,
        data_type=data_type,
    ).inc()


# ============================================================================
# ACTIVITY 2: Extract Entities from JSON
# ============================================================================
@activity.defn(name="graphiti_extract_from_json")
async def graphiti_extract_from_json_activity(
    raw_json: dict,
    source: str,
    data_type: str,
) -> List[Entity]:
    """
    Extract entities and relationships from structured JSON data.

    Uses Graphiti's JSON parsing capabilities:
    - Automatically extracts entities from nested JSON
    - Builds relationships based on data structure
    - Handles temporal aspects (timestamps, event sequences)

    Args:
        raw_json: Raw JSON dictionary
        source: Data source name
        data_type: Type of data (for context)

    Returns:
        List of Entity objects with relationships
    """
    # Use existing Graphiti service (adjust for JSON input)
    entities = await graphiti_service.extract_entities_from_json(
        data=raw_json,
        source=source,
        data_type=data_type,
    )

    # Emit metrics
    metrics.apex_temporal_entities_per_json_bucket.labels(
        source=source,
        data_type=data_type,
    ).observe(len(entities))

    return entities


# ============================================================================
# ACTIVITY 3: Generate Embeddings from JSON
# ============================================================================
@activity.defn(name="generate_embeddings_from_json")
async def generate_embeddings_from_json_activity(
    raw_json: dict,
    data_type: str,
) -> List[float]:
    """
    Generate vector embeddings from JSON data.

    Converts JSON to text representation, then embeds:
    - GPS events: "Vehicle at (lat, lon) traveling speed mph on timestamp"
    - Shipments: "Shipment from origin to destination, status, ETA"
    - Messages: Use message body directly

    Args:
        raw_json: Raw JSON dictionary
        data_type: Type of data (determines text conversion)

    Returns:
        Vector embeddings (1536-dimensional for OpenAI)
    """
    # Convert JSON to natural language text
    if data_type == "gps_event":
        text = f"Vehicle at ({raw_json['location']['latitude']}, {raw_json['location']['longitude']}) traveling {raw_json.get('speed', 0)} mph on {raw_json['happenedAtTime']}"

    elif data_type == "shipment":
        text = f"Shipment {raw_json['shipment_id']} from {raw_json['pickup']['location']} to {raw_json['delivery']['location']}, status: {raw_json['status']}, ETA: {raw_json['delivery']['eta']}"

    elif data_type == "message":
        text = f"{raw_json['payload']['subject']}: {raw_json['payload']['body']}"

    # Generate embeddings (reuse existing service)
    embeddings = await embedder_service.generate_embeddings(text)

    # Emit metrics
    metrics.apex_temporal_embeddings_generated_total.labels(
        source="json",
        data_type=data_type,
    ).inc()

    return embeddings


# ============================================================================
# ACTIVITY 4: Saga Write (Structured Data Variant)
# ============================================================================
@activity.defn(name="saga_write_structured_data")
async def saga_write_structured_data_activity(
    data_id: str,
    source: str,
    data_type: str,
    raw_json: dict,
    entities: List[Entity],
    embeddings: List[float],
) -> dict:
    """
    Write structured data to all 4 databases using Enhanced Saga pattern.

    Similar to document saga, but:
    - No chunks (JSON is already structured)
    - Different metadata schema
    - Same rollback guarantees

    Args:
        data_id: Unique data identifier
        source: Data source name
        data_type: Type of data
        raw_json: Raw JSON dictionary
        entities: Extracted entities
        embeddings: Vector embeddings

    Returns:
        Dict with write confirmations from all databases
    """
    # Reuse existing Enhanced Saga implementation
    # (see apex-memory-system/src/apex_memory/temporal/activities/ingestion.py)

    result = await saga_service.write_structured_data(
        data_id=data_id,
        source=source,
        data_type=data_type,
        raw_json=raw_json,
        entities=entities,
        embeddings=embeddings,
    )

    # Emit metrics
    metrics.apex_temporal_databases_written.labels(
        source=source,
        data_type=data_type,
        database="all",
        status="success" if result["all_successful"] else "failed",
    ).inc()

    return result
```

---

## Comparison: Before vs. After

### Before (Current Broken Architecture)

```
┌──────────────┐
│  FrontApp    │ ──┐
│  Turvo       │   │ External systems push to S3
│  Samsara     │   │ (NO TEMPORAL ORCHESTRATION!)
└──────────────┘   │
                   ▼
              ┌─────────┐
              │   S3    │ Cloud staging (expensive, unnecessary)
              │ Staging │
              └─────────┘
                   ▼
         ┌──────────────────┐
         │ Temporal Workflow│ Downloads from S3
         │ (download only)  │
         └──────────────────┘
                   ▼
              ┌─────────┐
              │ Docling │ Parses everything (even JSON!)
              └─────────┘
                   ▼
         ┌──────────────────┐
         │    Databases     │ Direct writes (no saga?)
         └──────────────────┘
```

**Problems:**
- ❌ S3 upload not orchestrated by Temporal (defeats the purpose)
- ❌ Expensive cloud storage for temporary staging
- ❌ All data forced through Docling (JSON doesn't need parsing)
- ❌ Unclear if saga pattern is used for all data types
- ❌ No distinction between document vs. structured data flows

### After (Corrected Architecture)

```
┌──────────────────────────────────────────────────┐
│            TEMPORAL ORCHESTRATES EVERYTHING       │
└──────────────────────────────────────────────────┘

┌──────────────┐
│  FrontApp    │ ──┐
│  Turvo       │   │ Temporal fetches on demand
│  Samsara     │   │ (Activity 1 pulls data)
└──────────────┘   │
                   ▼
         ┌──────────────────┐
         │ Temporal Workflow│ Routes by data type
         └──────────────────┘
                   │
       ┌───────────┴───────────┐
       ▼                       ▼
┌────────────┐        ┌──────────────┐
│ Documents  │        │ Structured   │
│ (PDF/DOCX) │        │ (JSON)       │
└────────────┘        └──────────────┘
       │                       │
       ▼                       │
┌─────────────┐                │
│Local Staging│                │
│/tmp/apex/   │                │
└─────────────┘                │
       │                       │
       ▼                       │
┌─────────────┐                │
│  Docling    │                │
│  Parsing    │                │
└─────────────┘                │
       │                       │
       └───────────┬───────────┘
                   ▼
         ┌──────────────────┐
         │    GRAPHITI      │ Entity extraction
         │  (ALL DATA!)     │
         └──────────────────┘
                   ▼
         ┌──────────────────┐
         │   EMBEDDINGS     │ Vector generation
         │  (ALL DATA!)     │
         └──────────────────┘
                   ▼
         ┌──────────────────┐
         │ ENHANCED SAGA    │ Atomic 4-DB writes
         │  (ALL DATA!)     │ with rollback
         └──────────────────┘
                   ▼
    ┌────┬────┬────┬────────┐
    ▼    ▼    ▼    ▼        ▼
  Neo4j Qdrant PG Graphiti Redis
```

**Improvements:**
- ✅ Temporal orchestrates the entire flow (source → databases)
- ✅ Local folder staging (fast, free, ephemeral)
- ✅ Two workflows optimized for data type
- ✅ ALL data flows through Graphiti + embeddings + saga
- ✅ Activity-based design (retry isolation, observability)
- ✅ Based on official Temporal tutorial pattern

---

## Implementation Plan

### Phase 1: Create New Activities (Week 1)

**New activities to implement:**

1. **pull_and_stage_document_activity** (replaces download_from_s3_activity)
   - Location: `apex-memory-system/src/apex_memory/temporal/activities/ingestion.py`
   - Handles: FrontApp API, local uploads, HTTP downloads
   - Output: Local staging path

2. **cleanup_staging_activity** (new)
   - Location: `apex-memory-system/src/apex_memory/temporal/activities/ingestion.py`
   - Handles: Cleanup `/tmp/apex-staging/` after successful ingestion

3. **fetch_structured_data_activity** (new)
   - Location: `apex-memory-system/src/apex_memory/temporal/activities/ingestion.py`
   - Handles: Samsara, Turvo, FrontApp webhook JSON fetching

4. **graphiti_extract_from_json_activity** (new variant)
   - Location: `apex-memory-system/src/apex_memory/temporal/activities/ingestion.py`
   - Adapts existing Graphiti service for JSON input

5. **generate_embeddings_from_json_activity** (new variant)
   - Location: `apex-memory-system/src/apex_memory/temporal/activities/ingestion.py`
   - Converts JSON to text, then embeds

6. **saga_write_structured_data_activity** (new variant)
   - Location: `apex-memory-system/src/apex_memory/temporal/activities/ingestion.py`
   - Saga pattern for JSON data (no chunks)

**Testing:**
- Unit tests for each activity (mock external APIs)
- Integration tests with real staging folder
- Saga rollback tests for structured data

### Phase 2: Update Workflows (Week 2)

**Modify existing DocumentIngestionWorkflow:**
- Replace `download_from_s3_activity` → `pull_and_stage_document_activity`
- Add `cleanup_staging_activity` at end
- Update workflow to accept `source_location` instead of `s3_bucket`
- Keep all existing activities (parse, extract, embed, saga write)

**Create new StructuredDataIngestionWorkflow:**
- New workflow class in `apex-memory-system/src/apex_memory/temporal/workflows/ingestion.py`
- Chain: fetch → graphiti → embeddings → saga
- No staging, no Docling

**Testing:**
- Workflow unit tests (mock activities)
- Integration tests with mocked databases
- End-to-end tests with real databases

### Phase 3: Update API Routes (Week 2)

**Modify /ingest endpoint:**
- Remove S3 upload logic
- Determine data type (document vs. structured)
- Route to appropriate workflow
- Pass source location (file path, URL, or API endpoint)

**Create new endpoints:**
- `POST /ingest/webhook/frontapp` - FrontApp webhook receiver
- `POST /ingest/webhook/turvo` - Turvo webhook receiver
- `POST /ingest/scheduled/samsara` - Samsara polling trigger (cron)

**Testing:**
- API integration tests
- Webhook payload validation tests
- End-to-end ingestion tests

### Phase 4: Update Worker Configuration (Week 3)

**Worker must register new activities:**
```python
worker = Worker(
    client,
    task_queue="apex-ingestion-queue",
    workflows=[
        DocumentIngestionWorkflow,
        StructuredDataIngestionWorkflow,  # NEW
    ],
    activities=[
        # Document activities
        pull_and_stage_document_activity,  # REPLACES download_from_s3_activity
        parse_document_activity,
        extract_entities_activity,
        generate_embeddings_activity,
        write_to_databases_activity,
        cleanup_staging_activity,  # NEW

        # Structured data activities
        fetch_structured_data_activity,  # NEW
        graphiti_extract_from_json_activity,  # NEW
        generate_embeddings_from_json_activity,  # NEW
        saga_write_structured_data_activity,  # NEW
    ],
)
```

**Testing:**
- Worker registration tests
- Concurrent workflow execution tests
- Load testing (100+ parallel workflows)

### Phase 5: Monitoring Updates (Week 3)

**New metrics to add:**

```python
# Staging metrics
apex_temporal_staging_bytes_written = Histogram(
    "apex_temporal_staging_bytes_written",
    "Bytes written to local staging",
    ["source"],
    buckets=[1024, 10240, 102400, 1048576, 10485760],  # 1KB to 10MB
)

apex_temporal_staging_cleanups_total = Counter(
    "apex_temporal_staging_cleanups_total",
    "Total staging directory cleanups",
    ["status"],  # success, failed
)

# Structured data metrics
apex_temporal_structured_data_fetched_total = Counter(
    "apex_temporal_structured_data_fetched_total",
    "Total structured data records fetched",
    ["source", "data_type"],
)

apex_temporal_entities_per_json_bucket = Histogram(
    "apex_temporal_entities_per_json_bucket",
    "Entities extracted per JSON record",
    ["source", "data_type"],
    buckets=[0, 1, 5, 10, 20, 50],
)
```

**Dashboard updates:**
- Add "Structured Data Ingestion" row to Grafana dashboard
- Add "Staging Operations" panel (bytes written, cleanup rate)
- Update workflow panel to show both workflow types

**Alerts:**
- Alert on staging cleanup failures (disk space leak)
- Alert on structured data fetch failures (API down)

### Phase 6: Migration & Rollout (Week 4)

**Migration steps:**

1. **Deploy new code (both workflows available)**
   - Document workflow: Uses local staging
   - Structured workflow: Available but not routed yet

2. **Route new uploads to local staging**
   - Update API to use `pull_and_stage_document_activity`
   - Keep S3 as fallback (read-only)

3. **Enable webhook endpoints**
   - FrontApp webhooks → StructuredDataIngestionWorkflow
   - Turvo webhooks → StructuredDataIngestionWorkflow

4. **Monitor for 1 week**
   - Validate staging cleanup (no disk leaks)
   - Validate structured data pipeline (Graphiti, embeddings, saga)

5. **Deprecate S3 staging**
   - Remove S3 upload logic from API
   - Remove `download_from_s3_activity`
   - Archive S3 bucket (historical data only)

**Rollback plan:**
- If issues, revert API to S3 staging
- Local staging is additive (doesn't break existing)

---

## Success Criteria

**Functional Requirements:**
- ✅ Temporal orchestrates 100% of data source pulls (no external S3 pushes)
- ✅ Documents use local folder staging (`/tmp/apex-staging/`)
- ✅ Structured data flows through full pipeline (Graphiti + embeddings + saga)
- ✅ Both workflows pass integration tests with real databases
- ✅ Staging cleanup prevents disk leaks (<1GB staging footprint)

**Performance Requirements:**
- ✅ Document workflow: <30s end-to-end (matches current performance)
- ✅ Structured data workflow: <10s end-to-end (no parsing overhead)
- ✅ Staging I/O: <500ms for typical document (5MB PDF)
- ✅ Concurrent workflows: Support 100+ parallel executions

**Observability Requirements:**
- ✅ All new activities emit metrics (start, complete, retry, failed)
- ✅ Grafana dashboard shows both workflow types
- ✅ Alerts cover staging failures and structured data fetch failures
- ✅ Temporal UI shows clear workflow differentiation

**Quality Requirements:**
- ✅ Unit test coverage: >80% for new activities
- ✅ Integration tests: Both workflows end-to-end
- ✅ Saga rollback tests: Structured data variant works correctly
- ✅ Load tests: 1,000 workflows/day (Samsara volume)

---

## Open Questions

1. **Staging folder lifecycle:**
   - How long to keep failed ingestion staging folders? (for debugging)
   - Should staging cleanup be asynchronous activity or synchronous?

2. **Samsara streaming:**
   - Should we batch GPS events (100 events/workflow) or individual workflows?
   - How to handle 1,000 events/min without overwhelming Temporal?

3. **FrontApp attachments:**
   - Are attachments always accessible via API, or do they expire?
   - Need OAuth refresh token handling?

4. **Graphiti JSON support:**
   - Does Graphiti already handle JSON entity extraction?
   - Need custom JSON-to-text conversion logic?

5. **Saga pattern for structured data:**
   - Does existing saga service handle JSON (no chunks)?
   - Need separate saga implementation or just adapter?

---

## References

**Official Documentation:**
- Temporal.io Data Pipeline Tutorial: https://learn.temporal.io/tutorials/python/build-a-data-pipeline/
- Temporal Payload Limits: https://docs.temporal.io/develop/python/data-converters
- Samsara REST API: https://developers.samsara.com/reference
- FrontApp Webhooks: https://dev.frontapp.com/docs/webhooks
- Turvo API: https://api.turvo.com/docs

**Internal Documentation:**
- ADR-003: Temporal Orchestration Decision
- TECHNICAL-DEBT.md TD-003: S3 Staging Issue
- Enhanced Saga Pattern: `apex-memory-system/src/apex_memory/services/saga_orchestrator.py`
- Existing Activities: `apex-memory-system/src/apex_memory/temporal/activities/ingestion.py`

---

**Status:** 🔄 **Ready for Review**
**Next Step:** Get user feedback on architecture design, then proceed to Phase 1 implementation.

---

**Last Updated:** 2025-10-18
**Author:** Claude Code (based on user corrections and official Temporal.io documentation)
