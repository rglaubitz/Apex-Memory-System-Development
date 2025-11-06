# Temporal Implementation - Execution Roadmap

**Status:** Ready for Execution
**Command:** `/execute` (for each section)
**Total Sections:** 17
**Estimated Time:** 40-55 hours

---

## How to Use This Roadmap

1. **Execute sections sequentially** - Each section builds on previous work
2. **Use `/execute` command** - Triggers the 10-step implementation pattern
3. **Context compact between sections** - Required to prevent context overflow
4. **Track progress** - Check off sections as you complete them

---

## Section 1: Pre-Flight & Setup ⚙️

**Status:** ☐ Not Started | ☐ In Progress | ☐ Complete

**Reference:** IMPLEMENTATION-GUIDE.md lines 42-135
**Timeline:** 1 hour
**Prerequisites:** None (first section)

### Deliverables
- [ ] Environment validation scripts (PostgreSQL, Docker, Python)
- [ ] `requirements.txt` updated with `temporalio==1.11.0`
- [ ] Pre-flight verification documentation
- [ ] Apex infrastructure baseline tests (121/121 Saga tests passing)

### Expected Tests
- `test_postgres_version()` - Verify PostgreSQL 12+
- `test_docker_version()` - Verify Docker 20.10+
- `test_python_version()` - Verify Python 3.11+
- `test_apex_databases_running()` - Verify 4 databases up
- `test_saga_baseline()` - Verify 121/121 tests passing

### Success Criteria
✅ All validation scripts pass
✅ Temporal SDK installed and importable
✅ Baseline Saga tests still passing

**Next Section:** Section 2 (Docker Compose Infrastructure)

---

## Section 2: Phase 1.1 - Docker Compose Infrastructure 🐳

**Status:** ☐ Not Started | ☐ In Progress | ☐ Complete

**Reference:** IMPLEMENTATION-GUIDE.md lines 142-318
**Timeline:** 2-3 hours
**Prerequisites:** Section 1 complete

### Deliverables
- [ ] `apex-memory-system/docker/temporal-compose.yml` (4 services)
  - `temporal-postgres` (port 5433)
  - `temporal` (port 7233, 8077)
  - `temporal-ui` (port 8088)
  - `temporal-admin-tools`
- [ ] `apex-memory-system/docker/temporal-dynamicconfig/development.yaml`
- [ ] Health check scripts
- [ ] Network integration with `apex-network`

### Expected Tests (10 tests)
- `test_temporal_compose_valid()` - Validate YAML syntax
- `test_temporal_postgres_starts()` - Verify postgres container starts
- `test_temporal_server_starts()` - Verify temporal container starts
- `test_temporal_ui_accessible()` - Verify UI at localhost:8088
- `test_admin_tools_accessible()` - Verify admin tools container
- `test_health_checks_pass()` - All healthchecks green
- `test_prometheus_metrics_available()` - Metrics at localhost:8077
- `test_postgres_persistence()` - Data survives restart
- `test_network_connectivity()` - Apex network integration
- `test_dynamic_config_loaded()` - Config file applied

### Success Criteria
✅ All 4 containers running and healthy
✅ Temporal UI accessible at http://localhost:8088
✅ PostgreSQL persistence working (port 5433)
✅ No port conflicts with Apex infrastructure

**Next Section:** Section 3 (Python SDK & Configuration)

---

## Section 3: Phase 1.2 - Python SDK & Configuration ⚙️

**Status:** ☐ Not Started | ☐ In Progress | ☐ Complete

**Reference:** IMPLEMENTATION-GUIDE.md lines 321-421
**Timeline:** 2 hours
**Prerequisites:** Section 2 complete

### Deliverables
- [ ] `src/apex_memory/config/temporal_config.py`
  - `TemporalConfig` dataclass
  - Environment variable loading
  - Feature flags (rollout percentage)
- [ ] `.env.temporal` (gitignored)
  - Connection config (host, namespace)
  - Worker config (task_queue, build_id)
  - Observability config (metrics, tracing)
  - Migration flags (TEMPORAL_ROLLOUT)
- [ ] Update `src/apex_memory/main.py` to load `.env.temporal`

### Expected Tests (5 tests)
- `test_config_loads_from_env()` - Environment variables parsed
- `test_config_defaults()` - Default values applied
- `test_rollout_percentage_validation()` - 0-100 range enforced
- `test_use_temporal_property()` - Feature flag logic
- `test_env_temporal_gitignored()` - .env.temporal in .gitignore

### Success Criteria
✅ `TemporalConfig` loads all environment variables
✅ Feature flags working (TEMPORAL_ROLLOUT=0 disables)
✅ `.env.temporal` in .gitignore
✅ Config importable from `main.py`

**Next Section:** Section 4 (Worker Infrastructure)

---

## Section 4: Phase 1.3 - Worker Infrastructure 👷

**Status:** ☐ Not Started | ☐ In Progress | ☐ Complete

**Reference:** IMPLEMENTATION-GUIDE.md lines 424-594
**Timeline:** 2-3 hours
**Prerequisites:** Section 3 complete

### Deliverables
- [ ] Directory structure:
  ```
  src/apex_memory/temporal/
  ├── __init__.py
  ├── workflows/__init__.py
  ├── activities/__init__.py
  └── workers/__init__.py
  ```
- [ ] `src/apex_memory/temporal/workers/base_worker.py`
  - `ApexTemporalWorker` class
  - Connection management
  - Graceful shutdown (SIGINT, SIGTERM)
  - Configurable concurrency

### Expected Tests (15 tests)
- `test_worker_initialization()` - Worker instance created
- `test_worker_connects_to_server()` - Connection succeeds
- `test_worker_polls_task_queue()` - Task queue polling works
- `test_worker_handles_sigint()` - SIGINT shutdown graceful
- `test_worker_handles_sigterm()` - SIGTERM shutdown graceful
- `test_worker_concurrent_workflow_tasks()` - Concurrency config works
- `test_worker_concurrent_activities()` - Activity concurrency works
- `test_worker_connection_retry()` - Reconnect on failure
- `test_worker_task_queue_config()` - Task queue from config
- `test_worker_namespace_config()` - Namespace from config
- `test_worker_logs_startup()` - Logging configured
- `test_worker_closes_client()` - Client cleanup on shutdown
- `test_worker_multiple_workflows()` - Multiple workflows registered
- `test_worker_multiple_activities()` - Multiple activities registered
- `test_worker_startup_failure_handling()` - Startup errors logged

### Success Criteria
✅ Worker connects to Temporal Server (localhost:7233)
✅ Graceful shutdown handlers working
✅ All tests passing (15/15)
✅ Worker logs startup/shutdown events

**Next Section:** Section 5 (Hello World Validation)

---

## Section 5: Phase 1.4 - Hello World Validation 👋

**Status:** ☐ Not Started | ☐ In Progress | ☐ Complete

**Reference:** IMPLEMENTATION-GUIDE.md lines 597-809
**Timeline:** 2-3 hours
**Prerequisites:** Section 4 complete

### Deliverables
- [ ] `src/apex_memory/temporal/workflows/hello_world.py`
  - `GreetingWorkflow` class
  - Activity execution with retry policy
- [ ] `src/apex_memory/temporal/activities/hello_world.py`
  - `greet_activity` function
- [ ] `src/apex_memory/temporal/workers/dev_worker.py`
  - Development worker script
  - Signal handler setup
- [ ] `scripts/test_hello_world.py`
  - Workflow execution test script

### Expected Tests (10 tests)
- `test_greeting_workflow_executes()` - Workflow completes successfully
- `test_greeting_workflow_with_name()` - Correct greeting returned
- `test_greet_activity_isolated()` - Activity works independently
- `test_workflow_retry_policy()` - Retry policy configured
- `test_workflow_timeout()` - Timeout enforced
- `test_workflow_logs()` - Logging works
- `test_dev_worker_starts()` - Worker script runs
- `test_workflow_in_temporal_ui()` - Workflow visible in UI
- `test_workflow_event_history()` - Event history complete
- `test_empty_name_handling()` - Empty string handled

### Expected Examples
- `examples/hello-world-basic.py` - Minimal workflow execution
- `examples/hello-world-with-retry.py` - Retry policy demonstration
- `examples/hello-world-query-status.py` - Query workflow status

### Success Criteria
✅ Hello World workflow executes end-to-end
✅ Activity logs "Hello, {name}!" message
✅ Workflow visible in Temporal UI (http://localhost:8088)
✅ Event history shows all steps
✅ All tests passing (10/10)

**Next Section:** Section 6 (Monitoring & Testing)

---

## Section 6: Phase 1.5 - Monitoring & Testing 📊

**Status:** ☐ Not Started | ☐ In Progress | ☐ Complete

**Reference:** IMPLEMENTATION-GUIDE.md lines 812-1092
**Timeline:** 3 hours
**Prerequisites:** Section 5 complete

### Deliverables
- [ ] `docker/prometheus/temporal.yml`
  - Scrape config for Temporal Server (port 8077)
  - Scrape config for Python SDK (port 8078)
- [ ] Grafana dashboards (2 files):
  - `docker/grafana/dashboards/temporal/temporal-server.json`
  - `docker/grafana/dashboards/temporal/temporal-sdk.json`
- [ ] `tests/integration/test_temporal_integration.py` (4 tests)
  - Connection test
  - Hello World workflow test
  - Activity execution test
  - Invalid input handling test
- [ ] `tests/integration/test_temporal_smoke.py` (5 tests)
  - Server reachable test
  - UI reachable test
  - Config loaded test
  - Workflows importable test
  - Activities importable test
- [ ] Phase 1 validation script

### Expected Tests (9 tests total)
**Integration Tests (4):**
- `test_temporal_server_connection()` - Can connect to server
- `test_hello_world_workflow()` - Full workflow execution
- `test_activity_execution()` - Activity runs independently
- `test_workflow_with_invalid_input()` - Error handling

**Smoke Tests (5):**
- `test_temporal_server_reachable()` - Server health check
- `test_temporal_ui_reachable()` - UI accessible
- `test_temporal_config_loaded()` - Config imported
- `test_worker_can_import_workflows()` - Workflows importable
- `test_worker_can_import_activities()` - Activities importable

### Expected Examples
- `examples/monitoring/check-prometheus-metrics.py` - Query Prometheus
- `examples/monitoring/import-grafana-dashboard.py` - Automate import

### Success Criteria
✅ Prometheus scraping Temporal metrics (2 jobs)
✅ Grafana dashboards imported and showing data
✅ Integration tests passing (4/4)
✅ Smoke tests passing (5/5)
✅ Saga baseline tests still passing (121/121)

**Phase 1 Complete!** 🎉

**Next Section:** Section 7 (Ingestion Activities)

---

## Section 7: Phase 2.1 - Ingestion Activities 📥

**Status:** ☐ Not Started | ☐ In Progress | ☐ Complete

**Reference:** IMPLEMENTATION-GUIDE.md lines 1100-1316
**Timeline:** 3 hours
**Prerequisites:** Section 6 complete (Phase 1 done)

### Deliverables
- [ ] `src/apex_memory/temporal/activities/ingestion.py` (4 activities):
  - `parse_document_activity` - Parse document from storage
  - `extract_entities_activity` - Extract entities
  - `generate_embeddings_activity` - Generate embeddings
  - `write_to_databases_activity` - Delegate to Enhanced Saga

### Expected Tests (20 tests)
**Parse Activity (5 tests):**
- `test_parse_document_activity()` - Parse succeeds
- `test_parse_activity_with_heartbeat()` - Heartbeats sent
- `test_parse_activity_retry()` - Retry on failure
- `test_parse_activity_invalid_document()` - ValidationError raised
- `test_parse_activity_serializable_output()` - Output is dict

**Extract Entities Activity (4 tests):**
- `test_extract_entities_activity()` - Entities extracted
- `test_extract_entities_empty_content()` - Empty content handled
- `test_extract_entities_logging()` - Logs entity count
- `test_extract_entities_output_format()` - Output format valid

**Generate Embeddings Activity (4 tests):**
- `test_generate_embeddings_activity()` - Embeddings generated
- `test_generate_embeddings_chunk_count()` - Chunk embeddings match
- `test_generate_embeddings_dimension()` - Correct embedding dimension
- `test_generate_embeddings_retry()` - Retry on OpenAI failure

**Write Databases Activity (7 tests):**
- `test_write_to_databases_activity()` - Write succeeds
- `test_write_to_databases_saga_integration()` - Enhanced Saga called
- `test_write_to_databases_all_success()` - All DBs written
- `test_write_to_databases_rollback()` - Rollback on failure
- `test_write_to_databases_partial_failure()` - Partial failure handling
- `test_write_to_databases_idempotency()` - Idempotent retries
- `test_write_to_databases_circuit_breaker()` - Circuit breaker active

### Expected Examples
- `examples/activities/parse-document-standalone.py` - Parse in isolation
- `examples/activities/write-databases-with-saga.py` - Saga integration demo

### Success Criteria
✅ All 4 activities implemented
✅ Enhanced Saga integration preserved (121/121 tests passing)
✅ Idempotency and circuit breakers working
✅ All tests passing (20/20)

**Next Section:** Section 8 (Ingestion Workflow)

---

## Section 8: Phase 2.2 - Ingestion Workflow 🔄

**Status:** ☐ Not Started | ☐ In Progress | ☐ Complete

**Reference:** IMPLEMENTATION-GUIDE.md lines 1318-1451
**Timeline:** 2-3 hours
**Prerequisites:** Section 7 complete

### Deliverables
- [ ] `src/apex_memory/temporal/workflows/ingestion.py`
  - `DocumentIngestionWorkflow` class
  - 4-step orchestration (parse → entities → embeddings → write)
  - Status tracking (`pending`, `parsed`, `entities_extracted`, `completed`)
  - Workflow query (`get_status`)
  - Retry policies per activity

### Expected Tests (15 tests)
**Workflow Execution (5 tests):**
- `test_ingestion_workflow_executes()` - Full workflow completes
- `test_ingestion_workflow_status_tracking()` - Status updates correctly
- `test_ingestion_workflow_with_source()` - Source parameter tracked
- `test_ingestion_workflow_retry_on_parse_failure()` - Parse retry works
- `test_ingestion_workflow_retry_on_write_failure()` - Write retry works

**Workflow Queries (3 tests):**
- `test_get_status_pending()` - Status query before execution
- `test_get_status_in_progress()` - Status query during execution
- `test_get_status_completed()` - Status query after completion

**Error Handling (4 tests):**
- `test_workflow_validation_error_no_retry()` - ValidationError non-retryable
- `test_workflow_saga_rollback()` - Saga rollback on write failure
- `test_workflow_activity_timeout()` - Activity timeout enforced
- `test_workflow_openai_retry()` - OpenAI retry (5 attempts)

**Integration (3 tests):**
- `test_workflow_with_real_saga()` - End-to-end with Enhanced Saga
- `test_workflow_logs_all_steps()` - Logging complete
- `test_workflow_in_temporal_ui()` - Visible in UI with event history

### Expected Examples
- `examples/workflows/ingest-document-basic.py` - Basic ingestion
- `examples/workflows/ingest-with-query-status.py` - Status queries
- `examples/workflows/ingest-with-retry.py` - Retry demonstration

### Success Criteria
✅ DocumentIngestionWorkflow orchestrates all 4 steps
✅ Status tracking working (`get_status` query)
✅ Retry policies configured per activity
✅ Enhanced Saga integration preserved
✅ All tests passing (15/15)

**Next Section:** Section 9 (Gradual Rollout)

---

## Section 9: Phase 2.3 - Gradual Rollout 🚦

**Status:** ☐ Not Started | ☐ In Progress | ☐ Complete

**Reference:** IMPLEMENTATION-GUIDE.md lines 1454-1655
**Timeline:** 2-3 hours
**Prerequisites:** Section 8 complete

### Deliverables
- [ ] `src/apex_memory/temporal/migration/rollout_coordinator.py`
  - `RolloutCoordinator` class
  - Deterministic hash-based routing
  - Feature flag percentage (0%, 10%, 50%, 100%)
- [ ] Update `src/apex_memory/api/endpoints/documents.py`
  - `ingest_via_temporal()` function
  - `ingest_via_legacy()` function
  - Routing logic based on rollout percentage
- [ ] Feature flag environment variable (`TEMPORAL_ROLLOUT`)

### Expected Tests (10 tests)
**RolloutCoordinator (6 tests):**
- `test_rollout_0_percent()` - All traffic to legacy
- `test_rollout_100_percent()` - All traffic to Temporal
- `test_rollout_50_percent_distribution()` - ~50% split
- `test_rollout_deterministic_hashing()` - Same doc → same path
- `test_rollout_coordinator_logging()` - Routing decisions logged
- `test_rollout_from_config()` - Percentage from environment variable

**API Endpoint (4 tests):**
- `test_ingest_routes_to_temporal()` - Temporal path chosen
- `test_ingest_routes_to_legacy()` - Legacy path chosen
- `test_ingest_temporal_path()` - Temporal workflow executes
- `test_ingest_legacy_path()` - Legacy Saga executes

### Expected Examples
- `examples/rollout/test-rollout-10-percent.py` - 10% traffic test
- `examples/rollout/verify-deterministic-routing.py` - Routing consistency

### Success Criteria
✅ RolloutCoordinator implemented with hash-based routing
✅ API endpoint routing to Temporal or legacy based on flag
✅ Deterministic routing (same doc always same path)
✅ All tests passing (10/10)
✅ Zero-downtime migration capability

**Next Section:** Section 10 (Ingestion Testing & Rollout)

---

## Section 10: Phase 2.4 - Ingestion Testing & Rollout 🧪

**Status:** ☐ Not Started | ☐ In Progress | ☐ Complete

**Reference:** IMPLEMENTATION-GUIDE.md lines 1658-1921
**Timeline:** 3-4 hours
**Prerequisites:** Section 9 complete

### Deliverables
- [ ] `tests/integration/test_ingestion_workflow.py` (3 tests)
  - Full ingestion workflow test
  - Rollback on failure test
  - Query status test
- [ ] `tests/load/test_concurrent_ingestion.py` (100 concurrent)
- [ ] Rollout monitoring scripts:
  - `scripts/rollout/set-rollout-percentage.sh`
  - `scripts/rollout/monitor-rollout.sh`
  - `scripts/rollout/compare-error-rates.sh`
- [ ] Rollout execution plan (10% → 50% → 100%)

### Expected Tests (8 tests)
**Integration Tests (3):**
- `test_full_ingestion_workflow()` - End-to-end with all activities
- `test_ingestion_rollback_on_failure()` - Saga rollback works
- `test_ingestion_query_status()` - Status queries during execution

**Load Tests (5):**
- `test_100_concurrent_workflows()` - 100 workflows in parallel
- `test_concurrent_workflow_success_rate()` - All workflows succeed
- `test_concurrent_workflow_latency()` - P99 latency acceptable
- `test_worker_task_queue_handling()` - Queue doesn't overflow
- `test_saga_under_load()` - Enhanced Saga stable under load

### Rollout Plan
**Week 3 (10% traffic):**
- [ ] Set `TEMPORAL_ROLLOUT=10`
- [ ] Monitor for 48 hours
- [ ] Compare error rates (Temporal vs legacy)
- [ ] Verify P99 latency < 5× legacy
- [ ] Check Temporal UI for failures

**Week 4 (50% → 100% traffic):**
- [ ] Set `TEMPORAL_ROLLOUT=50`
- [ ] Monitor for 24 hours
- [ ] Set `TEMPORAL_ROLLOUT=100`
- [ ] Monitor for 48 hours
- [ ] Remove legacy code (after 2-week safety window)

### Success Criteria
✅ All integration tests passing (3/3)
✅ Load tests passing (100 concurrent workflows)
✅ 10% rollout validated (error rate < 2× legacy)
✅ 50% rollout validated
✅ 100% rollout running (full migration)
✅ Saga baseline still passing (121/121)

**Phase 2 Complete!** 🎉

**Next Section:** Section 11 (Webhook Workflows)

---

## Section 11: Phase 3.1 - Webhook Workflows 🪝

**Status:** ☐ Not Started | ☐ In Progress | ☐ Complete

**Reference:** IMPLEMENTATION-GUIDE.md lines 1947-2187
**Timeline:** 3-4 hours
**Prerequisites:** Section 10 complete (Phase 2 done)

### Deliverables
- [ ] `src/apex_memory/temporal/workflows/webhook_ingestion.py`
  - `WebhookIngestionWorkflow` class
  - Signature validation step
  - Deduplication check
  - Child workflow routing to `DocumentIngestionWorkflow`
- [ ] `src/apex_memory/temporal/activities/webhook.py`
  - `validate_webhook_signature` activity
  - `parse_webhook_payload` activity
  - Source-specific parsers (FrontApp, Turvo, Sonar)

### Expected Tests (20 tests)
**Webhook Workflow (6 tests):**
- `test_webhook_workflow_executes()` - Full webhook processing
- `test_webhook_signature_validation()` - Signature checked
- `test_webhook_invalid_signature()` - Invalid signature rejected
- `test_webhook_deduplication()` - Duplicate events skipped
- `test_webhook_child_workflow_spawned()` - Child workflow created
- `test_webhook_status_query()` - Status tracking works

**Webhook Activities (14 tests):**
- `test_validate_webhook_signature_valid()` - Valid signature passes
- `test_validate_webhook_signature_invalid()` - Invalid signature fails
- `test_validate_webhook_missing_secret()` - Missing secret handled
- `test_parse_webhook_frontapp()` - FrontApp payload parsed
- `test_parse_webhook_turvo()` - Turvo payload parsed
- `test_parse_webhook_sonar()` - Sonar payload parsed
- `test_parse_webhook_unsupported_source()` - Unsupported source rejected
- `test_parse_webhook_frontapp_metadata()` - Metadata extracted
- `test_parse_webhook_turvo_metadata()` - Metadata extracted
- `test_parse_webhook_sonar_metadata()` - Metadata extracted
- `test_webhook_secret_from_env()` - Secrets loaded from environment
- `test_webhook_signature_hmac_sha256()` - HMAC SHA256 algorithm
- `test_webhook_logging()` - Logging configured
- `test_webhook_activity_retry()` - Activity retries on failure

### Expected Examples
- `examples/webhooks/frontapp-webhook-example.py` - FrontApp integration
- `examples/webhooks/turvo-webhook-example.py` - Turvo integration
- `examples/webhooks/webhook-signature-validation.py` - Signature demo

### Success Criteria
✅ Webhook workflow processing all 3 sources (FrontApp, Turvo, Sonar)
✅ Signature validation working (HMAC SHA256)
✅ Deduplication preventing duplicate events
✅ Child workflow routing to DocumentIngestionWorkflow
✅ All tests passing (20/20)

**Next Section:** Section 12 (Polling Workflows)

---

## Section 12: Phase 3.2 - Polling Workflows 🔄

**Status:** ☐ Not Started | ☐ In Progress | ☐ Complete

**Reference:** IMPLEMENTATION-GUIDE.md lines 2192-2339
**Timeline:** 2-3 hours
**Prerequisites:** Section 11 complete

### Deliverables
- [ ] `src/apex_memory/temporal/workflows/polling.py`
  - `PollingWorkflow` class
  - Periodic polling (15-minute intervals)
  - Continue-as-new pattern (every 100 iterations)
  - Child workflow spawning per record
- [ ] `src/apex_memory/temporal/activities/polling.py`
  - `fetch_new_records` activity
  - Source-specific polling (Plaid, CRM, Financial)

### Expected Tests (15 tests)
**Polling Workflow (7 tests):**
- `test_polling_workflow_executes()` - Polling loop works
- `test_polling_workflow_interval()` - 15-minute sleep works
- `test_polling_workflow_spawns_child_workflows()` - Child workflows created
- `test_polling_workflow_continue_as_new()` - Continue-as-new at 100 iterations
- `test_polling_workflow_stats_query()` - Stats query works
- `test_polling_workflow_no_records()` - Empty result handled
- `test_polling_workflow_logging()` - Logging configured

**Polling Activities (8 tests):**
- `test_fetch_new_records_plaid()` - Plaid API called
- `test_fetch_new_records_crm()` - CRM API called
- `test_fetch_new_records_financial()` - Financial API called
- `test_fetch_new_records_unsupported()` - Unsupported source rejected
- `test_fetch_new_records_empty()` - Empty list handled
- `test_fetch_new_records_retry()` - Retry on API failure
- `test_fetch_new_records_logging()` - Record count logged
- `test_fetch_new_records_activity_heartbeat()` - Heartbeat sent

### Expected Examples
- `examples/polling/plaid-polling-example.py` - Plaid integration
- `examples/polling/continue-as-new-demo.py` - Continue-as-new pattern

### Success Criteria
✅ Polling workflow running indefinitely
✅ Continue-as-new preventing history growth
✅ Child workflows spawned for each record
✅ All 3 sources supported (Plaid, CRM, Financial)
✅ All tests passing (15/15)

**Next Section:** Section 13 (Streaming & Batch Workflows)

---

## Section 13: Phase 3.3 - Streaming & Batch Workflows 🌊

**Status:** ☐ Not Started | ☐ In Progress | ☐ Complete

**Reference:** IMPLEMENTATION-GUIDE.md lines 2343-2546
**Timeline:** 3-4 hours
**Prerequisites:** Section 12 complete

### Deliverables
- [ ] `src/apex_memory/temporal/workflows/streaming.py`
  - `StreamIngestionWorkflow` class
  - Batch collection (100 events/batch)
  - Parallel child workflow processing
  - High-volume handling (1,000 events/min)
- [ ] `src/apex_memory/temporal/workflows/batch.py`
  - `BatchProcessingWorkflow` class
  - Multi-file processing
  - Carrier EDI support
- [ ] `src/apex_memory/temporal/activities/streaming.py`
  - `collect_stream_batch` activity
- [ ] `src/apex_memory/temporal/activities/batch.py`
  - `fetch_batch_files` activity
  - `parse_batch_file` activity

### Expected Tests (20 tests)
**Streaming Workflow (8 tests):**
- `test_streaming_workflow_executes()` - Streaming works
- `test_streaming_batch_collection()` - Batch collection works
- `test_streaming_batch_size_100()` - Batch size enforced
- `test_streaming_parallel_processing()` - Parallel child workflows
- `test_streaming_empty_batch()` - Empty batch handled
- `test_streaming_high_volume()` - 1,000 events/min sustained
- `test_streaming_heartbeat()` - Activity heartbeats sent
- `test_streaming_stats_tracking()` - Total processed tracked

**Batch Workflow (6 tests):**
- `test_batch_workflow_executes()` - Batch processing works
- `test_batch_multi_file_processing()` - Multiple files processed
- `test_batch_file_parsing()` - EDI files parsed correctly
- `test_batch_parallel_records()` - Records processed in parallel
- `test_batch_summary()` - Summary stats returned
- `test_batch_error_handling()` - File errors handled

**Activities (6 tests):**
- `test_collect_stream_batch()` - Batch collection works
- `test_fetch_batch_files()` - Files fetched from storage
- `test_parse_batch_file_edi()` - EDI parsing works
- `test_parse_batch_file_csv()` - CSV parsing works
- `test_activity_timeout()` - Long operations timeout
- `test_activity_retry()` - Activities retry on failure

### Expected Examples
- `examples/streaming/samsara-stream-example.py` - Samsara integration
- `examples/batch/carrier-edi-example.py` - EDI batch processing

### Success Criteria
✅ Streaming workflow handling 1,000 events/min
✅ Batch workflow processing multiple files
✅ Parallel child workflow execution working
✅ All tests passing (20/20)

**Phase 3 Complete!** 🎉

**Next Section:** Section 14 (Temporal UI & Search)

---

## Section 14: Phase 4.1 - Temporal UI & Search 🔍

**Status:** ☐ Not Started | ☐ In Progress | ☐ Complete

**Reference:** IMPLEMENTATION-GUIDE.md lines 2554-2588
**Timeline:** 2 hours
**Prerequisites:** Section 13 complete (Phase 3 done)

### Deliverables
- [ ] Search attribute configuration script
  - `scripts/temporal/configure-search-attributes.sh`
  - Add: Source, Priority, DocumentId, Status
- [ ] Update workflow start options to include search attributes
  - Modify all workflow executions in API endpoints
- [ ] Search attribute query examples

### Expected Tests (10 tests)
- `test_search_attributes_configured()` - Attributes registered
- `test_workflow_with_source_attribute()` - Source searchable
- `test_workflow_with_priority_attribute()` - Priority searchable
- `test_workflow_with_document_id_attribute()` - DocumentId searchable
- `test_workflow_with_status_attribute()` - Status searchable
- `test_search_by_source()` - Can find workflows by source
- `test_search_by_document_id()` - Can find workflows by document
- `test_search_combined_attributes()` - Multiple attribute search
- `test_search_attribute_update()` - Attributes updatable
- `test_temporal_ui_search()` - UI search works

### Expected Examples
- `examples/ui/search-workflows-by-source.py` - Source filtering
- `examples/ui/search-workflows-by-status.py` - Status filtering

### Success Criteria
✅ 4 search attributes configured (Source, Priority, DocumentId, Status)
✅ All workflows tagged with search attributes
✅ Temporal UI search working
✅ All tests passing (10/10)

**Next Section:** Section 15 (Prometheus & Grafana)

---

## Section 15: Phase 4.2 - Prometheus & Grafana 📈

**Status:** ☐ Not Started | ☐ In Progress | ☐ Complete

**Reference:** IMPLEMENTATION-GUIDE.md lines 2592-2651
**Timeline:** 2-3 hours
**Prerequisites:** Section 14 complete

### Deliverables
- [ ] `docker/grafana/dashboards/apex-temporal.json`
  - 4 custom panels:
    1. Workflow Success Rate
    2. Workflow Latency (P99)
    3. Activity Execution Rate
    4. Worker Task Queue Depth
- [ ] Prometheus query validation scripts
- [ ] Dashboard import automation

### Expected Tests (8 tests)
- `test_prometheus_temporal_server_metrics()` - Server metrics available
- `test_prometheus_sdk_metrics()` - SDK metrics available
- `test_grafana_dashboard_import()` - Dashboard imports successfully
- `test_workflow_success_rate_panel()` - Success rate panel configured
- `test_workflow_latency_panel()` - Latency panel configured
- `test_activity_execution_rate_panel()` - Activity rate panel configured
- `test_task_queue_depth_panel()` - Queue depth panel configured
- `test_dashboard_queries_valid()` - All Prometheus queries valid

### Expected Examples
- `examples/monitoring/query-prometheus.py` - Query Prometheus metrics
- `examples/monitoring/dashboard-automation.py` - Automate dashboard creation

### Success Criteria
✅ Custom Grafana dashboard created (4 panels)
✅ Prometheus queries returning data
✅ Dashboard showing real-time metrics
✅ All tests passing (8/8)

**Next Section:** Section 16 (OpenTelemetry & Documentation)

---

## Section 16: Phase 4.3 - OpenTelemetry & Documentation 📚

**Status:** ☐ Not Started | ☐ In Progress | ☐ Complete

**Reference:** IMPLEMENTATION-GUIDE.md lines 2655-2810
**Timeline:** 3 hours
**Prerequisites:** Section 15 complete

### Deliverables
- [ ] `src/apex_memory/config/telemetry.py`
  - OpenTelemetry configuration
  - OTLP exporter setup
  - TracerProvider initialization
- [ ] `docs/temporal-operations.md`
  - Daily operations guide
  - Troubleshooting guide
  - Deployment procedures
  - Rollback procedures
- [ ] Team training materials
  - Training agenda
  - Temporal UI walkthrough
  - Debugging guide

### Expected Tests (10 tests)
- `test_telemetry_setup()` - Telemetry configured when enabled
- `test_telemetry_disabled()` - Telemetry skipped when disabled
- `test_tracer_provider_configured()` - TracerProvider set
- `test_otlp_exporter_configured()` - Exporter configured
- `test_tracing_endpoint()` - OTLP endpoint from config
- `test_spans_exported()` - Spans exported to backend
- `test_workflow_trace()` - Workflow creates trace
- `test_activity_trace()` - Activity creates trace
- `test_distributed_trace()` - Trace spans workflows and activities
- `test_trace_correlation()` - Trace IDs correlated

### Expected Documentation
- `docs/temporal-operations.md` (operational runbook)
- `docs/temporal-training-agenda.md` (team training)
- `docs/temporal-troubleshooting.md` (common issues)

### Success Criteria
✅ OpenTelemetry tracing configured
✅ Distributed traces visible in backend
✅ Operational runbook complete
✅ Team training agenda created
✅ All tests passing (10/10)

**Phase 4 Complete!** 🎉

**Next Section:** Section 17 (Testing Strategy & Rollback)

---

## Section 17: Testing Strategy & Rollback 🧪

**Status:** ☐ Not Started | ☐ In Progress | ☐ Complete

**Reference:** IMPLEMENTATION-GUIDE.md lines 2814-3110
**Timeline:** 2-3 hours
**Prerequisites:** Section 16 complete (Phase 4 done)

### Deliverables
- [ ] `tests/unit/test_temporal_activities.py`
  - Unit tests for all activities in isolation
- [ ] `tests/integration/test_temporal_saga_integration.py`
  - Integration tests with real Enhanced Saga
- [ ] `tests/load/test_concurrent_workflows.py`
  - Load tests (100, 1,000 concurrent workflows)
- [ ] Rollback scripts:
  - `scripts/rollback/emergency-rollback.sh` (instant)
  - `scripts/rollback/graceful-rollback.sh` (gradual)
  - `scripts/rollback/worker-version-rollback.sh` (worker versioning)
- [ ] Deployment checklist

### Expected Tests (25 tests)
**Unit Tests (10):**
- `test_parse_activity_isolated()` - Parse activity alone
- `test_extract_entities_isolated()` - Extract activity alone
- `test_generate_embeddings_isolated()` - Embeddings activity alone
- `test_write_databases_isolated()` - Write activity alone
- `test_webhook_validate_isolated()` - Webhook validation alone
- `test_webhook_parse_isolated()` - Webhook parsing alone
- `test_polling_fetch_isolated()` - Polling fetch alone
- `test_stream_collect_isolated()` - Stream collection alone
- `test_batch_fetch_isolated()` - Batch fetch alone
- `test_batch_parse_isolated()` - Batch parsing alone

**Integration Tests (10):**
- `test_temporal_saga_integration()` - Full workflow with Saga
- `test_saga_rollback_integration()` - Saga rollback works
- `test_saga_idempotency_integration()` - Idempotency preserved
- `test_saga_circuit_breaker_integration()` - Circuit breakers work
- `test_webhook_to_ingestion_integration()` - Webhook → Ingestion
- `test_polling_to_ingestion_integration()` - Polling → Ingestion
- `test_streaming_to_ingestion_integration()` - Stream → Ingestion
- `test_batch_to_ingestion_integration()` - Batch → Ingestion
- `test_multi_source_integration()` - All sources integrated
- `test_end_to_end_integration()` - Complete end-to-end

**Load Tests (5):**
- `test_100_concurrent_workflows()` - 100 workflows in parallel
- `test_1000_concurrent_workflows()` - 1,000 workflows in parallel
- `test_sustained_throughput()` - Sustained load over 10 minutes
- `test_worker_scaling()` - Workers scale under load
- `test_saga_under_load()` - Saga stable under load

### Rollback Scripts
**Emergency Rollback (<5 minutes):**
- Set `TEMPORAL_ROLLOUT=0` via environment variable
- OR shut down Temporal (automatic fallback to legacy)

**Graceful Rollback (<30 minutes):**
- Gradually reduce rollout: 100% → 50% → 10% → 0%
- Let running workflows complete

**Worker Versioning Rollback:**
- Rollback to previous worker version
- No workflow interruption

### Success Criteria
✅ All unit tests passing (10/10)
✅ All integration tests passing (10/10)
✅ All load tests passing (5/5)
✅ Saga baseline still passing (121/121)
✅ Rollback scripts tested and working
✅ Deployment checklist complete

**🎉 ALL 17 SECTIONS COMPLETE! TEMPORAL IMPLEMENTATION DONE! 🎉**

---

## Progress Tracking

### Completed Sections: 0/17

**Phase 1 (Infrastructure):**
- [ ] Section 1: Pre-Flight & Setup
- [ ] Section 2: Docker Compose Infrastructure
- [ ] Section 3: Python SDK & Configuration
- [ ] Section 4: Worker Infrastructure
- [ ] Section 5: Hello World Validation
- [ ] Section 6: Monitoring & Testing

**Phase 2 (Ingestion Migration):**
- [ ] Section 7: Ingestion Activities
- [ ] Section 8: Ingestion Workflow
- [ ] Section 9: Gradual Rollout
- [ ] Section 10: Ingestion Testing & Rollout

**Phase 3 (Multi-Source Integration):**
- [ ] Section 11: Webhook Workflows
- [ ] Section 12: Polling Workflows
- [ ] Section 13: Streaming & Batch Workflows

**Phase 4 (Monitoring & Observability):**
- [ ] Section 14: Temporal UI & Search
- [ ] Section 15: Prometheus & Grafana
- [ ] Section 16: OpenTelemetry & Documentation
- [ ] Section 17: Testing Strategy & Rollback

---

## Execution Commands

### Start a Section
```bash
/execute
```

### After Each Section
```bash
/compact
```

### Check Progress
```bash
cat EXECUTION-ROADMAP.md | grep "☑ Complete" | wc -l
```

---

## Notes

- **Context Compact Required:** After each section to prevent context overflow
- **Test Coverage:** Aim for 15-30 tests per section
- **Saga Baseline:** Always verify 121/121 Saga tests still passing
- **Rollback Capability:** Test rollback procedures at each phase boundary

---

**Created:** 2025-10-18
**Owner:** Apex Infrastructure Team
**Status:** Ready for Section 1
