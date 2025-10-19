# Phase 2D Fixes - Load Tests (Real DBs)

**Date:** October 18, 2025
**Session:** Section 11 Testing - Phase 2D
**Status:** ✅ FIXES COMPLETE - Ready to Run

---

## 📋 Overview

**Goal:** Execute 5 load tests with REAL databases and REAL S3
**Command:** `pytest tests/load/test_temporal_ingestion_integration.py -v`
**Current Status:** Fixing infrastructure and API migration issues

**Tests to Run:**
1. test_concurrent_ingestion_real_databases - 50 concurrent workflows
2. test_saga_under_load - Enhanced Saga stability
3. test_database_write_concurrency - 4 databases handling parallel writes
4. test_end_to_end_latency - P50/P90/P99 latency measurement
5. test_sustained_throughput_real_db - Sustained 10+ docs/min

---

## 🔧 Fixes Applied

### Fix #1: S3 Credentials Missing

**Problem:**
```
botocore.exceptions.NoCredentialsError: Unable to locate credentials
```

**Root Cause:**
Phase 2D tests need S3 to upload/download test documents. No AWS credentials configured.

**Fix:**
Added LocalStack (AWS S3 emulator) instead of using real AWS.

**LocalStack Setup:**

1. **Added LocalStack to docker-compose.yml:**
```yaml
localstack:
  image: localstack/localstack:latest
  container_name: apex-localstack
  ports:
    - "4566:4566"  # LocalStack edge port
  environment:
    - SERVICES=s3
    - DEBUG=0
    - AWS_ACCESS_KEY_ID=test
    - AWS_SECRET_ACCESS_KEY=test
    - AWS_DEFAULT_REGION=us-east-1
  volumes:
    - localstack_data:/var/lib/localstack
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:4566/_localstack/health"]
    interval: 10s
    timeout: 5s
    retries: 10
  networks:
    - apex-network
```

2. **Added localstack_data volume:**
```yaml
volumes:
  # ... other volumes ...
  localstack_data:
```

**File Modified:**
- `docker/docker-compose.yml`

**Production Impact:** ❌ None (test infrastructure only)

**Status:** ✅ RESOLVED

---

### Fix #2: LocalStack Volume Configuration Issue

**Problem:**
```
OSError: [Errno 16] Device or resource busy: '/tmp/localstack'
LocalStack supervisor: localstack process (PID 14) returned with exit code 1
```

**Root Cause:**
Initial LocalStack configuration mounted `/tmp/localstack` which caused conflicts on macOS.

**Fix:**
Changed volume mount to `/var/lib/localstack` (LocalStack default):
```yaml
volumes:
  - localstack_data:/var/lib/localstack  # Changed from /tmp/localstack
```

Also removed unnecessary docker socket mount.

**File Modified:**
- `docker/docker-compose.yml`

**Production Impact:** ❌ None (test infrastructure only)

**Status:** ✅ RESOLVED

---

### Fix #3: S3 Environment Configuration

**Problem:**
Tests and activities need to know how to connect to LocalStack S3.

**Fix:**
Added S3 environment variables to `.env`:
```bash
# S3 Configuration (LocalStack for testing)
S3_ENDPOINT_URL=http://localhost:4566
AWS_ACCESS_KEY_ID=test
AWS_SECRET_ACCESS_KEY=test
AWS_DEFAULT_REGION=us-east-1
APEX_DOCUMENTS_BUCKET=apex-documents-test
```

**Files Modified:**
- `apex-memory-system/.env`

**Production Impact:** ❌ None (test configuration only)

**Status:** ✅ RESOLVED

---

### Fix #4: Activity S3 Client Doesn't Support LocalStack

**Problem:**
`download_from_s3_activity` creates boto3 client without endpoint_url parameter:
```python
s3_client = boto3.client("s3")  # Won't use LocalStack
```

**Root Cause:**
Activity hardcoded to use real AWS S3, doesn't check for S3_ENDPOINT_URL environment variable.

**Fix:**
Updated activity to support LocalStack endpoint:
```python
# Before
s3_client = boto3.client("s3")

# After
s3_endpoint = os.getenv("S3_ENDPOINT_URL")
s3_client = boto3.client(
    "s3",
    endpoint_url=s3_endpoint if s3_endpoint else None
)
```

**File Modified:**
- `src/apex_memory/temporal/activities/ingestion.py:137-141`

**Production Impact:** ✅ **PRODUCTION CODE** (enables LocalStack for testing, still works with real AWS)

**Status:** ✅ RESOLVED

---

### Fix #5: Temporal SDK API Migration (IN PROGRESS)

**Problem:**
```
TypeError: Client.execute_workflow() takes from 2 to 3 positional arguments
but 6 positional arguments (and 3 keyword-only arguments) were given
```

**Root Cause:**
Same as Phase 2C - Temporal Python SDK breaking change from positional arguments to `args=[]` keyword parameter.

**Locations Needing Fix:**
1. test_concurrent_ingestion_real_databases (line 214)
2. test_saga_under_load (line 298)
3. test_database_write_concurrency (line 386)
4. test_end_to_end_latency (line 471)
5. test_sustained_throughput_real_db (line 554)

**Fix Pattern:**
```python
# Before
temporal_client.execute_workflow(
    DocumentIngestionWorkflow.run,
    doc_id,
    "load-test",
    bucket,
    "load-test",
    id=f"load-test-real-db-{doc_id}",
    task_queue="apex-load-test-real-db",
)

# After
temporal_client.execute_workflow(
    DocumentIngestionWorkflow.run,
    args=[doc_id, "load-test", bucket, "load-test"],  # document_id, source, bucket, prefix
    id=f"load-test-real-db-{doc_id}",
    task_queue="apex-load-test-real-db",
)
```

**Files Modified:**
- `tests/load/test_temporal_ingestion_integration.py:216, 297, 382, 464, 543` (5 locations)

**Production Impact:** ❌ None (test code only)

**Status:** ✅ RESOLVED

---

## 📊 Test Execution Results

### Current Status: ALL FIXES COMPLETE ✅

**✅ S3 Infrastructure:**
- LocalStack running and healthy
- Test fixture successfully uploaded 100 test documents to LocalStack
- S3 endpoints configured correctly

**✅ Temporal SDK API Migration:**
- All 5 test locations updated to args=[] format
- Test collection successful (5 tests collected)
- No syntax errors

**⏳ Next Step:**
- Run Phase 2D tests with real databases
- Tests may take 10-30 minutes due to real I/O (OpenAI, databases, S3)
- Expect different performance than Phase 2C mocked tests

---

## 🎯 What Went Good

1. ✅ **LocalStack setup successful** - S3 emulation working
2. ✅ **Volume issue quickly diagnosed** - Fixed on second attempt
3. ✅ **Activity updated for LocalStack** - Production code now supports both LocalStack and real AWS
4. ✅ **Learned from Phase 2C** - Recognized Temporal SDK API pattern immediately

---

## 🔴 What Went Bad

1. ⚠️ **Initial LocalStack config failed** - Volume mount issue on macOS
2. ⚠️ **Activity needed production code change** - Not just test code
3. ℹ️ **Same Temporal SDK migration needed** - Recurring pattern across all test suites

---

## 🚧 Production Code Changes

**Modified Files:**

1. **docker/docker-compose.yml** (+20 lines, +1 volume)
   - Added LocalStack service for S3 emulation
   - **Impact:** Test infrastructure only

2. **apex-memory-system/.env** (+6 lines)
   - Added S3 configuration for LocalStack
   - **Impact:** Test configuration only

3. **src/apex_memory/temporal/activities/ingestion.py** (+4 lines)
   - Updated download_from_s3_activity to support LocalStack endpoint
   - **Impact:** ✅ **PRODUCTION CODE** - Activity now works with both LocalStack and real AWS

**Summary:** 1 production code file modified (backwards compatible change)

---

## 🔮 Future Considerations

### Infrastructure Requirements

**For Phase 2D Tests:**
- ✅ LocalStack running (port 4566)
- ✅ Temporal server running (port 7233)
- ⏳ Neo4j running (port 7474)
- ⏳ PostgreSQL running (port 5432)
- ⏳ Qdrant running (port 6333)
- ⏳ Redis running (port 6379)
- ⏳ Temporal worker running (dev_worker.py)
- ⏳ OpenAI API key configured

### Performance Expectations

With REAL databases (vs mocked):
- **Throughput:** Lower than Phase 2C (mocked was 21 workflows/sec)
- **Latency:** Higher due to real I/O (expect P99 < 30s vs 114ms)
- **Resource Usage:** Significant DB, OpenAI, and S3 I/O

---

## 📌 Next Steps

1. ✅ LocalStack configured and running
2. ✅ Activity updated to support LocalStack
3. ✅ Apply Temporal SDK API migration (5 locations)
4. ✅ Commit fixes to both repositories
5. ⏳ Run all 5 Phase 2D tests (requires user approval - long-running)
6. ⏳ Document results
7. ⏳ Create INDEX.md summary

---

**Phase 2D Status:** ✅ FIXES COMPLETE - Ready to run tests

**Test Execution:** Tests ready but NOT yet run (require 10-30 minutes with real DBs + OpenAI)

**Summary of Fixes:**
- 5 fixes applied (S3 infrastructure, LocalStack setup, activity update, API migration)
- 1 production code change (download_from_s3_activity supports LocalStack)
- 5 test code changes (Temporal SDK API migration)
- All changes committed and ready
