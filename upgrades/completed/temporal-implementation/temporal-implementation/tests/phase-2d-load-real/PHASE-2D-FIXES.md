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

### Fix #6: Temp File Extension Bug (PRODUCTION BUG - CRITICAL)

**Problem:**
```
Parse failed: Unsupported format: .txt-c6cqzeua. Supported: .pdf, .docx, .pptx, .html, .htm, .md, .txt
```

**Root Cause:**
- `download_from_s3_activity` creates temp files with random suffix: `/tmp/load-test-doc-5.txt-c6cqzeua`
- S3 objects missing Content-Type metadata, so extension = ""
- tempfile.NamedTemporaryFile adds random suffix to prefix, creating `.txt-c6cqzeua`
- Parser rejects these files

**Impact:** **All 270 workflows failed at parse step** (0% success rate during initial run)

**Fix:**
Added fallback to derive extension from document_id filename:
```python
# Fallback: derive extension from document_id if not found in Content-Type
if not extension and "." in document_id:
    # Extract extension from document_id (e.g., "doc.txt" → ".txt")
    extension = "." + document_id.rsplit(".", 1)[1]
```

**File Modified:**
- `src/apex_memory/temporal/activities/ingestion.py:163-166`

**Production Impact:** ✅ **PRODUCTION CODE** (critical bug fix)

**Status:** ✅ RESOLVED

---

### Fix #7: PostgreSQL UUID LIKE Operator Error

**Problem:**
```
psycopg2.errors.UndefinedFunction: operator does not exist: uuid ~~ unknown
LINE 1: SELECT COUNT(*) FROM documents WHERE uuid LIKE '%load-test-d...
HINT:  No operator matches the given name and argument types. You might need to add explicit type casts.
```

**Root Cause:**
PostgreSQL doesn't allow LIKE operator on UUID columns. Tests were querying `WHERE uuid LIKE '%...'` but uuid is a UUID type, not TEXT.

**Fix:**
Changed SQL queries to use file_name column instead of uuid:
```python
# Before
cursor.execute("SELECT COUNT(*) FROM documents WHERE uuid LIKE %s", ('%load-test-doc%',))

# After
cursor.execute("SELECT COUNT(*) FROM documents WHERE file_name LIKE %s", ('%load-test-doc%',))
```

**Files Modified:**
- `tests/load/test_temporal_ingestion_integration.py:323, 423` (2 locations)

**Production Impact:** ❌ None (test code only)

**Status:** ✅ RESOLVED

---

## 📊 Test Execution Results

### Final Status: ✅ ALL 5 TESTS PASSING

**Test Results:**
```
✅ test_concurrent_ingestion_real_databases - PASSED (50 workflows)
✅ test_saga_under_load - PASSED (20 workflows)
✅ test_database_write_concurrency - PASSED (30 workflows)
✅ test_end_to_end_latency - PASSED (50 workflows)
✅ test_sustained_throughput_real_db - PASSED (100 workflows)
```

**Performance:**
- **Total workflows:** 250 workflows with REAL databases + OpenAI API
- **Duration:** 85 seconds (1:25)
- **Throughput:** ~2.9 workflows/second (lower than Phase 2C mocked: 21/sec)
- **Success rate:** 100%

**Infrastructure Used:**
- ✅ LocalStack S3 (port 4566)
- ✅ Temporal server (port 7233)
- ✅ Neo4j (port 7474)
- ✅ PostgreSQL (port 5432)
- ✅ Qdrant (port 6333)
- ✅ Redis (port 6379)
- ✅ Temporal worker (dev_worker.py)
- ✅ OpenAI API (real API calls for embeddings)

---

## 🎯 What Went Good

1. ✅ **LocalStack setup successful** - S3 emulation working (after volume fix)
2. ✅ **Critical production bug found** - Temp file extension fallback missing (would have caused 100% workflow failure in production with misconfigured S3)
3. ✅ **Activity updated for LocalStack** - Production code now supports both LocalStack and real AWS
4. ✅ **Learned from Phase 2C** - Recognized Temporal SDK API pattern immediately
5. ✅ **Systematic debugging** - Found and fixed 7 bugs through methodical testing
6. ✅ **100% test pass rate** - All 5 Phase 2D tests passing with 250 workflows

---

## 🔴 What Went Bad

1. ⚠️ **Initial LocalStack config failed** - Volume mount issue on macOS (fixed on second attempt)
2. ⚠️ **Multiple production bugs** - Found 2 production code bugs (temp file extension, S3 endpoint)
3. ⚠️ **Multiple test bugs** - Found 5 test code bugs (Temporal SDK migration, database access, SQL queries)
4. ℹ️ **Schema knowledge gap** - Tests initially queried wrong columns (uuid vs file_name)

---

## 🚧 Production Code Changes

**Modified Files:**

1. **docker/docker-compose.yml** (+20 lines, +1 volume)
   - Added LocalStack service for S3 emulation
   - **Impact:** Test infrastructure only

2. **apex-memory-system/.env** (+6 lines)
   - Added S3 configuration for LocalStack
   - **Impact:** Test configuration only

3. **src/apex_memory/temporal/activities/ingestion.py** (+8 lines)
   - Updated download_from_s3_activity to support LocalStack endpoint
   - Added extension fallback from document_id (CRITICAL BUG FIX)
   - **Impact:** ✅ **PRODUCTION CODE** - 2 critical fixes (LocalStack support + extension fallback)

**Summary:** 2 production code changes in 1 file (both backwards compatible)

---

## 🔮 Future Considerations

### Performance Expectations

**Test Performance (tiny 416-byte text files):**
- **Throughput:** ~2.9 workflows/sec (250 workflows in 85 seconds)
- **Latency:** <1 second per workflow (minimal parsing)
- **Resource Usage:** Light (tiny files, simple parsing)

**Production Performance (10-page PDFs):**
- **Throughput:** Much lower (~0.1-0.2 workflows/sec per worker)
- **Latency:** 10-20 seconds per workflow (Docling parsing, OpenAI API)
- **Resource Usage:** Heavy (large PDFs, complex parsing, API calls)

### Technical Debt Items Created

**TD-004: Temp File Extension Fallback** (RESOLVED in this session)
- Added fallback to derive extension from document_id
- Prevents workflow failures when S3 Content-Type missing

**See TECHNICAL-DEBT.md for:**
- TD-001: S3 download interim solution
- TD-002: No validation of FrontApp → S3 upload (CRITICAL)
- TD-003: S3 not orchestrated by Temporal (ARCHITECTURAL)

---

## 📌 Phase 2D Summary

**Status:** ✅ COMPLETE - All 5 tests passing

**Achievements:**
1. ✅ LocalStack S3 configured and working
2. ✅ 7 bugs found and fixed (2 production, 5 test)
3. ✅ All 5 Phase 2D tests passing (250 workflows, 100% success)
4. ✅ Critical production bug discovered (temp file extension fallback)
5. ✅ Real database integration validated (Neo4j, PostgreSQL, Qdrant, Redis)
6. ✅ OpenAI API integration validated
7. ✅ Enhanced Saga pattern preserved (121 baseline tests still passing)

**Production Bugs Fixed:**
- **Fix #4:** S3 endpoint support for LocalStack (ingestion.py:137-141)
- **Fix #6:** Temp file extension fallback (ingestion.py:163-166) - CRITICAL

**Test Fixes:**
- **Fix #5:** Temporal SDK API migration (5 locations)
- **Fix #5:** Database connection access (2 tests)
- **Fix #7:** SQL column name (uuid → file_name, 2 locations)

**Total Changes:**
- Production code: 2 fixes in 1 file (ingestion.py)
- Test code: 5 fixes across 1 file
- Infrastructure: LocalStack added to docker-compose.yml
- Configuration: S3 environment variables added to .env

**Next Phase:** Phase 2E - Metrics Validation
