# Google Drive Integration - Architecture Diagrams

**Author:** Apex Infrastructure Team
**Created:** November 7, 2025 (Week 4 Day 2)
**Version:** 1.0

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Workflow Orchestration](#workflow-orchestration)
3. [Monitoring Pipeline](#monitoring-pipeline)
4. [Error Handling Flow](#error-handling-flow)
5. [Archive Workflow](#archive-workflow)
6. [Component Interaction](#component-interaction)
7. [Database Schema](#database-schema)

---

## System Overview

### High-Level Architecture

```mermaid
graph TB
    subgraph "Google Drive"
        GD[Google Drive Folder]
    end

    subgraph "Temporal Orchestration"
        TS[Temporal Schedule<br/>Every 15 min]
        MW[GoogleDriveMonitorWorkflow]
        IW[DocumentIngestionWorkflow]
        AW[GoogleDriveArchiveWorkflow]
    end

    subgraph "Activities"
        POLL[poll_google_drive_folder_activity]
        MARK[mark_file_as_processed_activity]
        DLQ[add_to_dead_letter_queue_activity]
        INGEST[Ingestion Activities<br/>parse, extract, embed, write]
        ARCHIVE[Archive Activities<br/>upload, verify, record]
    end

    subgraph "Data Stores"
        PG[(PostgreSQL<br/>Processed Files + DLQ)]
        NEO[(Neo4j<br/>Entities + Relationships)]
        QDRANT[(Qdrant<br/>Vector Embeddings)]
        REDIS[(Redis<br/>Cache)]
    end

    subgraph "Monitoring"
        PROM[Prometheus<br/>Metrics]
        ALERT[Alertmanager<br/>Alerts]
        GRAF[Grafana<br/>Dashboards]
    end

    TS -->|Triggers| MW
    MW -->|Polls| POLL
    POLL -->|List Files| GD
    POLL -->|Query| PG
    MW -->|New File| IW
    IW -->|Process| INGEST
    INGEST -->|Write| NEO
    INGEST -->|Write| QDRANT
    INGEST -->|Write| REDIS
    MW -->|Success| MARK
    MARK -->|Insert| PG
    MW -->|Failure| DLQ
    DLQ -->|Track| PG
    IW -->|Cleanup| AW
    AW -->|Archive| ARCHIVE
    ARCHIVE -->|Upload| GD

    MW -->|Metrics| PROM
    IW -->|Metrics| PROM
    PROM -->|Alerts| ALERT
    PROM -->|Query| GRAF

    style MW fill:#4A90E2
    style IW fill:#4A90E2
    style AW fill:#4A90E2
    style PROM fill:#E85D75
    style ALERT fill:#E85D75
```

**Key Components:**

- **Temporal Schedule:** Triggers monitor workflow every 15 minutes
- **GoogleDriveMonitorWorkflow:** Orchestrates file detection and ingestion
- **DocumentIngestionWorkflow:** Processes each detected file
- **GoogleDriveArchiveWorkflow:** Archives processed files (async)
- **Monitoring Stack:** Prometheus + Alertmanager + Grafana for observability

---

## Workflow Orchestration

### GoogleDriveMonitorWorkflow Flow

```mermaid
flowchart TD
    START([Temporal Schedule<br/>Every 15 min]) --> INIT[Initialize Workflow<br/>folder_id, max_results=100]
    INIT --> POLL[Execute: poll_google_drive_folder_activity<br/>30s timeout, 3 retries]

    POLL --> CHECK_NEW{New files<br/>detected?}

    CHECK_NEW -->|No| EARLY[Record Metrics:<br/>- poll success<br/>- 0 files detected<br/>- workflow duration]
    EARLY --> END_SUCCESS([Return: status=success<br/>files_processed=0])

    CHECK_NEW -->|Yes| PROCESS[For each new file]

    PROCESS --> CHILD[Execute Child Workflow:<br/>DocumentIngestionWorkflow<br/>10min timeout, 3 retries]

    CHILD --> ING_CHECK{Ingestion<br/>succeeded?}

    ING_CHECK -->|Yes| MARK_PROC[Execute: mark_file_as_processed_activity<br/>10s timeout, 3 retries]
    MARK_PROC --> METRIC_SUCCESS[Record Metrics:<br/>- file processed<br/>- processed file count++]
    METRIC_SUCCESS --> MORE{More files<br/>to process?}

    ING_CHECK -->|No| CLASSIFY[Classify Error:<br/>GoogleDriveErrorClassifier]

    CLASSIFY --> RETRYABLE{Error<br/>retryable?}

    RETRYABLE -->|Yes| METRIC_FAIL[Record Metrics:<br/>- file failed<br/>- error_category]
    METRIC_FAIL --> MORE

    RETRYABLE -->|No| ADD_DLQ[Execute: add_to_dead_letter_queue_activity<br/>10s timeout, 3 retries]
    ADD_DLQ --> METRIC_FAIL

    MORE -->|Yes| PROCESS
    MORE -->|No| FINAL[Record Metrics:<br/>- workflow duration<br/>- final status]

    FINAL --> STATUS{Determine<br/>status}

    STATUS -->|All succeeded| END_SUCCESS2([Return: status=success<br/>files_processed=N, files_failed=0])
    STATUS -->|Some failed| END_PARTIAL([Return: status=partial<br/>files_processed=N, files_failed=M])
    STATUS -->|All failed| END_FAILED([Return: status=failed<br/>files_processed=0, files_failed=N])

    style INIT fill:#D4E6F1
    style CHILD fill:#4A90E2
    style ADD_DLQ fill:#E85D75
    style END_SUCCESS fill:#58D68D
    style END_SUCCESS2 fill:#58D68D
    style END_PARTIAL fill:#F39C12
    style END_FAILED fill:#E74C3C
```

**State Persistence (Temporal):**
- `folder_id`, `current_status`, `last_poll_timestamp`
- `files_processed_count`, `files_failed_count`
- `new_files`, `error_message`

**Key Features:**
- Early return if no new files (efficient)
- Child workflow pattern (wait for completion)
- Error classification before DLQ routing
- Partial success reporting

---

### DocumentIngestionWorkflow Integration

```mermaid
flowchart LR
    MW[GoogleDriveMonitorWorkflow]
    MW --> |For each new file| CHILD[execute_child_workflow<br/>DocumentIngestionWorkflow]

    CHILD --> STAGE[pull_and_stage_document_activity<br/>Download from Google Drive]
    STAGE --> PARSE[parse_document_activity<br/>Docling parser]
    PARSE --> EXTRACT[extract_entities_activity<br/>OpenAI extraction]
    EXTRACT --> EMBED[generate_embeddings_activity<br/>OpenAI embeddings]
    EMBED --> WRITE[write_to_databases_activity<br/>Neo4j, PostgreSQL, Qdrant, Redis]
    WRITE --> CLEANUP[cleanup_staging_activity<br/>Remove staging + trigger archive]
    CLEANUP --> RETURN[Return: status, chunks, entities]

    RETURN --> MW

    style CHILD fill:#4A90E2
    style RETURN fill:#58D68D
```

**Ingestion Duration:** Typical 10-30 seconds per file
**Timeout:** 10 minutes per file
**Retries:** 3 attempts with exponential backoff

---

## Monitoring Pipeline

### Metrics Collection Architecture

```mermaid
graph TB
    subgraph "Workflow Layer"
        WF[GoogleDriveMonitorWorkflow<br/>+ DocumentIngestionWorkflow]
    end

    subgraph "Metrics Recording"
        M1[Poll Metrics<br/>polls_total, files_detected]
        M2[Processing Metrics<br/>files_processed, files_failed]
        M3[Duration Metrics<br/>monitor_duration, ingestion_duration]
        M4[DLQ Metrics<br/>Implicit via files_failed by error_type]
    end

    subgraph "Prometheus"
        SCRAPE[Scrape Endpoint<br/>:8000/metrics<br/>Every 15s]
        STORE[Time Series DB<br/>Retention: 15d]
    end

    subgraph "Alerting"
        RULES[Alert Rules<br/>12 alerts:<br/>3 critical, 5 warning, 4 info]
        EVAL[Alert Evaluation<br/>Every 30s]
        AM[Alertmanager<br/>Routing + Grouping]
    end

    subgraph "Visualization"
        GRAF[Grafana Dashboards<br/>Real-time monitoring]
    end

    subgraph "Notification Channels"
        EMAIL[Email<br/>team@company.com]
        SLACK[Slack<br/>#apex-alerts]
        PD[PagerDuty<br/>Critical only]
    end

    WF --> M1
    WF --> M2
    WF --> M3
    WF --> M4

    M1 --> SCRAPE
    M2 --> SCRAPE
    M3 --> SCRAPE
    M4 --> SCRAPE

    SCRAPE --> STORE
    STORE --> RULES
    RULES --> EVAL
    EVAL --> AM

    STORE --> GRAF

    AM --> EMAIL
    AM --> SLACK
    AM --> PD

    style WF fill:#4A90E2
    style SCRAPE fill:#E85D75
    style AM fill:#E85D75
    style PD fill:#E74C3C
```

**7 Prometheus Metrics:**
1. `apex_google_drive_monitor_polls_total` (Counter) - Poll success/failure
2. `apex_google_drive_files_detected_total` (Counter) - New files per poll
3. `apex_google_drive_files_processed_total` (Counter) - Successful ingestions
4. `apex_google_drive_files_failed_total` (Counter) - Failed ingestions by error_type
5. `apex_google_drive_monitor_duration_seconds` (Histogram) - Workflow duration
6. `apex_google_drive_processed_files_count` (Gauge) - Cumulative processed count
7. (Implicit) Error type distribution via labels on files_failed_total

**12 Alert Rules:**
- **3 Critical:** Workflow down, workflow failing, high failure rate (>50%)
- **5 Warning:** Moderate failure rate, slow workflow, DLQ growing, high poll duration, error spike
- **4 Info:** No new files, low throughput

---

## Error Handling Flow

### Error Classification and DLQ Routing

```mermaid
flowchart TD
    START([File Processing Failed]) --> CATCH[Catch Exception]

    CATCH --> CLASSIFY[GoogleDriveErrorClassifier<br/>.is_retryable]

    CLASSIFY --> CHECK_KEYWORDS{Check Error<br/>Keywords}

    CHECK_KEYWORDS -->|"rate limit"<br/>"timeout"<br/>"network"<br/>"temporary"| RETRYABLE[is_retryable = True<br/>error_category = "rate_limit" etc.]

    CHECK_KEYWORDS -->|"not found"<br/>"permission denied"<br/>"invalid"<br/>"deleted"| NON_RETRYABLE[is_retryable = False<br/>error_category = "not_found" etc.]

    CHECK_KEYWORDS -->|Unknown error| DEFAULT[is_retryable = True<br/>error_category = "unknown"<br/>Safer default]

    RETRYABLE --> LOG_RETRY[Log: Retryable error<br/>error_category in extra]
    NON_RETRYABLE --> LOG_NON[Log: Non-retryable error<br/>Adding to DLQ]
    DEFAULT --> LOG_RETRY

    LOG_RETRY --> METRIC_RETRY[Record Metric:<br/>files_failed_total{error_category}]
    LOG_NON --> METRIC_NON[Record Metric:<br/>files_failed_total{error_category}]

    METRIC_RETRY --> TEMPORAL_RETRY[Temporal retries<br/>per RetryPolicy<br/>max 3 attempts]
    METRIC_NON --> ADD_DLQ[Execute Activity:<br/>add_to_dead_letter_queue_activity]

    TEMPORAL_RETRY --> MAX_ATTEMPTS{Max attempts<br/>reached?}

    MAX_ATTEMPTS -->|No| BACKOFF[Exponential backoff<br/>Wait and retry]
    BACKOFF --> START

    MAX_ATTEMPTS -->|Yes| EVENTUAL_DLQ[Consider adding to DLQ<br/>after exhausting retries]

    ADD_DLQ --> DLQ_TABLE[(PostgreSQL<br/>google_drive_dead_letter_queue)]

    DLQ_TABLE --> INVESTIGATION[Manual Investigation<br/>Via troubleshooting runbook]

    INVESTIGATION --> REPROCESS{Can<br/>reprocess?}

    REPROCESS -->|Yes| MANUAL[Manual Reprocessing<br/>Trigger DocumentIngestionWorkflow]
    REPROCESS -->|No| MARK_DONE[Mark as reprocessed<br/>to prevent future alerts]

    MANUAL --> SUCCESS{Reprocessing<br/>succeeded?}

    SUCCESS -->|Yes| MARK_REPROCESSED[Execute Activity:<br/>mark_dlq_file_reprocessed_activity]
    SUCCESS -->|No| BACK_DLQ[Remains in DLQ<br/>for further investigation]

    style NON_RETRYABLE fill:#E85D75
    style ADD_DLQ fill:#E85D75
    style DLQ_TABLE fill:#F39C12
    style MARK_REPROCESSED fill:#58D68D
    style BACK_DLQ fill:#E74C3C
```

**Error Categories:**
- **Retryable:** rate_limit, timeout, network_error, unknown
- **Non-Retryable:** not_found, permission_denied, invalid_request

**DLQ Schema:**
- file_id, file_name, folder_id, error_message, error_type
- retry_count, metadata (JSONB), failed_at
- reprocessed (BOOLEAN), reprocessed_at

---

## Archive Workflow

### GoogleDriveArchiveWorkflow (Async)

```mermaid
flowchart TD
    START([cleanup_staging_activity<br/>completes]) --> TRIGGER[Start Child Workflow:<br/>GoogleDriveArchiveWorkflow<br/>Async, non-blocking]

    TRIGGER --> DETERMINE[Execute: determine_archive_folder_activity<br/>Calculate archive path<br/>Example: Archive/2025/11/]

    DETERMINE --> CREATE{Archive<br/>folder exists?}

    CREATE -->|No| CREATE_FOLDER[Create folder via<br/>Google Drive API]
    CREATE_FOLDER --> UPLOAD
    CREATE -->|Yes| UPLOAD[Execute: upload_to_google_drive_activity<br/>Upload file to archive folder<br/>30s timeout, 3 retries]

    UPLOAD --> VERIFY[Execute: verify_upload_activity<br/>Check file exists in archive<br/>10s timeout, 3 retries]

    VERIFY --> VERIFY_CHECK{Upload<br/>verified?}

    VERIFY_CHECK -->|Yes| RECORD[Execute: record_archive_metadata_activity<br/>Save: archive_folder_id, archive_file_id<br/>10s timeout, 3 retries]

    VERIFY_CHECK -->|No| RETRY_ARCHIVE{Retry<br/>attempts<br/>remaining?}

    RETRY_ARCHIVE -->|Yes| UPLOAD
    RETRY_ARCHIVE -->|No| FAIL[Archive failed<br/>File remains in staging<br/>Log error for investigation]

    RECORD --> DELETE[Optional: Delete from<br/>monitored folder<br/>Only if archive verified]

    DELETE --> SUCCESS([Archive Complete<br/>Return: status=success<br/>archive_file_id])

    FAIL --> FAIL_RETURN([Return: status=failed<br/>error message])

    style TRIGGER fill:#4A90E2
    style RECORD fill:#58D68D
    style SUCCESS fill:#58D68D
    style FAIL fill:#E74C3C
    style FAIL_RETURN fill:#E74C3C
```

**Key Design:**
- **Async trigger:** DocumentIngestionWorkflow doesn't wait for archive
- **Idempotent:** Can retry safely (checks if file already archived)
- **Verification:** Ensures file exists in archive before deleting from monitored folder
- **Metadata tracking:** Records archive location for audit trail

**Archive Folder Structure:**
```
Google Drive Archive/
├── 2025/
│   ├── 11/
│   │   ├── contract-001.pdf (archived Nov 2025)
│   │   └── contract-002.pdf
│   └── 12/
│       └── contract-003.pdf (archived Dec 2025)
└── 2026/
    └── 01/
        └── contract-004.pdf
```

---

## Component Interaction

### Activity-Level Interactions

```mermaid
graph TB
    subgraph "External Services"
        GD[Google Drive API<br/>www.googleapis.com]
        OPENAI[OpenAI API<br/>embeddings + extraction]
    end

    subgraph "Temporal Activities"
        subgraph "Monitoring Activities"
            POLL[poll_google_drive_folder_activity]
            MARK[mark_file_as_processed_activity]
            DLQ[add_to_dead_letter_queue_activity]
        end

        subgraph "Ingestion Activities"
            STAGE[pull_and_stage_document_activity]
            PARSE[parse_document_activity]
            EXTRACT[extract_entities_activity]
            EMBED[generate_embeddings_activity]
            WRITE[write_to_databases_activity]
            CLEANUP[cleanup_staging_activity]
        end

        subgraph "Archive Activities"
            DETERMINE[determine_archive_folder_activity]
            UPLOAD[upload_to_google_drive_activity]
            VERIFY[verify_upload_activity]
            RECORD[record_archive_metadata_activity]
        end
    end

    subgraph "Data Stores"
        PG[(PostgreSQL<br/>Processed Files<br/>DLQ)]
        NEO[(Neo4j<br/>Graph)]
        QDRANT[(Qdrant<br/>Vectors)]
        REDIS[(Redis<br/>Cache)]
        FS[Local Filesystem<br/>/tmp/apex-staging/]
    end

    subgraph "Services"
        GDS[GoogleDriveService<br/>Official SDK]
        DOCLING[Docling Parser<br/>Multi-format]
        ENTITY[EntityExtractor<br/>OpenAI GPT]
        EMBSVC[EmbeddingService<br/>OpenAI]
        WRITER[DatabaseWriteOrchestrator<br/>Saga Pattern]
    end

    POLL --> GDS
    GDS --> GD
    POLL --> PG

    MARK --> PG
    DLQ --> PG

    STAGE --> GDS
    STAGE --> FS

    PARSE --> FS
    PARSE --> DOCLING

    EXTRACT --> ENTITY
    ENTITY --> OPENAI

    EMBED --> EMBSVC
    EMBSVC --> OPENAI

    WRITE --> WRITER
    WRITER --> NEO
    WRITER --> QDRANT
    WRITER --> REDIS
    WRITER --> PG

    DETERMINE --> GDS
    UPLOAD --> GDS
    VERIFY --> GDS
    RECORD --> PG

    style POLL fill:#D4E6F1
    style STAGE fill:#D4E6F1
    style EXTRACT fill:#D4E6F1
    style WRITER fill:#58D68D
    style DLQ fill:#E85D75
```

**Service Dependencies:**
- **GoogleDriveService:** Official Python SDK (`google-api-python-client`)
- **Docling:** Multi-format parser (PDF, DOCX, PPTX, HTML, Markdown)
- **OpenAI:** GPT-4 for entity extraction, text-embedding-3-small for embeddings
- **DatabaseWriteOrchestrator:** Saga pattern for transactional writes

---

## Database Schema

### PostgreSQL Tables

```mermaid
erDiagram
    GOOGLE_DRIVE_PROCESSED_FILES {
        int id PK
        varchar file_id UK "Google Drive file ID"
        varchar file_name
        timestamp modified_time "Last modified in Drive"
        timestamp processed_at "When ingested by Apex"
        varchar document_id "Apex document ID"
        timestamp created_at
    }

    GOOGLE_DRIVE_DEAD_LETTER_QUEUE {
        int id PK
        varchar file_id "Google Drive file ID"
        varchar file_name
        varchar folder_id "Source folder"
        text error_message "Full error message"
        varchar error_type "Category: not_found, permission_denied, etc."
        int retry_count "Number of retry attempts"
        jsonb metadata "File metadata: mime_type, size, etc."
        timestamp failed_at "When permanently failed"
        boolean reprocessed "Has been reprocessed?"
        timestamp reprocessed_at "When reprocessed"
        timestamp created_at
    }

    GOOGLE_DRIVE_PROCESSED_FILES ||--o{ GOOGLE_DRIVE_DEAD_LETTER_QUEUE : "file_id (reference)"
```

**Indexes:**

```sql
-- google_drive_processed_files
CREATE INDEX idx_processed_files_file_id ON google_drive_processed_files(file_id);

-- google_drive_dead_letter_queue
CREATE INDEX idx_dlq_file_id ON google_drive_dead_letter_queue(file_id);
CREATE INDEX idx_dlq_error_type ON google_drive_dead_letter_queue(error_type);
CREATE INDEX idx_dlq_reprocessed ON google_drive_dead_letter_queue(reprocessed);
```

**Unique Constraints:**

```sql
-- google_drive_processed_files
ALTER TABLE google_drive_processed_files ADD CONSTRAINT unique_file_id UNIQUE (file_id);

-- google_drive_dead_letter_queue
ALTER TABLE google_drive_dead_letter_queue
ADD CONSTRAINT unique_file_id_failed_at UNIQUE (file_id, failed_at);
```

**Rationale:**
- `file_id` uniqueness prevents duplicate tracking
- `(file_id, failed_at)` allows same file to fail multiple times (different timestamps)
- JSONB `metadata` stores flexible file attributes (mime_type, size, etc.)

---

## Sequence Diagrams

### End-to-End File Processing

```mermaid
sequenceDiagram
    participant Schedule as Temporal Schedule
    participant Monitor as GoogleDriveMonitorWorkflow
    participant Poll as poll_google_drive_folder_activity
    participant Drive as Google Drive API
    participant DB as PostgreSQL
    participant Ingest as DocumentIngestionWorkflow
    participant Writer as DatabaseWriteOrchestrator
    participant Archive as GoogleDriveArchiveWorkflow
    participant Metrics as Prometheus

    Schedule->>Monitor: Trigger (every 15 min)
    Monitor->>Poll: Execute activity
    Poll->>Drive: List files in folder
    Drive-->>Poll: Return files list
    Poll->>DB: Query processed files
    DB-->>Poll: Return processed file IDs
    Poll->>Poll: Filter new files
    Poll-->>Monitor: Return new_files list
    Monitor->>Metrics: Record poll metrics

    loop For each new file
        Monitor->>Ingest: Execute child workflow
        Ingest->>Drive: Download file
        Ingest->>Writer: Write to databases
        Writer->>Metrics: Record ingestion metrics
        Writer-->>Ingest: Return success
        Ingest->>Archive: Start archive workflow (async)
        Ingest-->>Monitor: Return success
        Monitor->>DB: Mark file as processed
        Monitor->>Metrics: Record file processed
    end

    Monitor->>Metrics: Record workflow duration
    Monitor-->>Schedule: Return summary

    Note over Archive: Archive workflow runs independently
    Archive->>Drive: Upload to archive folder
    Archive->>DB: Record archive metadata
```

---

## Summary

This architecture provides:

✅ **Scalability:** Temporal schedules, parallel workflow execution
✅ **Reliability:** Retry policies, error classification, Dead Letter Queue
✅ **Observability:** Prometheus metrics, Grafana dashboards, 12 alerts
✅ **Maintainability:** Clear component separation, documented flows
✅ **Auditability:** Complete tracking in PostgreSQL (processed + DLQ)

**Key Architectural Decisions:**
1. **Temporal orchestration** - Durable workflows with automatic retries
2. **Child workflow pattern** - Wait for ingestion before marking processed
3. **Error classification** - Prevent retry storms for permanent failures
4. **Dead Letter Queue** - PostgreSQL for durability and queryability
5. **Async archive** - Non-blocking archive workflow
6. **Metrics-first** - 7 metrics + 12 alerts for complete observability

---

**Architecture Version:** 1.0
**Last Updated:** November 7, 2025
