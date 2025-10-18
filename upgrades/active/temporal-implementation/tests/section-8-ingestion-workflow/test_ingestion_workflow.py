"""Tests for DocumentIngestionWorkflow.

This test suite validates the complete ingestion workflow orchestration:
- Workflow execution (happy path)
- Status tracking via queries
- Error handling and retries
- Activity failure scenarios
- Integration with Enhanced Saga

Tests use mocked activities following Temporal testing best practices.

Author: Apex Infrastructure Team
Created: 2025-10-18
"""

import pytest
from datetime import timedelta
from temporalio import activity, workflow
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker
from temporalio.exceptions import ApplicationError

# Import workflow under test
import sys
sys.path.insert(0, "/Users/richardglaubitz/Projects/apex-memory-system/src")

from apex_memory.temporal.workflows.ingestion import DocumentIngestionWorkflow


# ============================================================================
# Mock Activities
# ============================================================================


@activity.defn
async def mock_download_from_s3_activity(
    document_id: str,
    source: str,
    bucket=None,
    prefix=None,
) -> str:
    """Mock S3 download activity."""
    activity.logger.info(f"Mock: Downloading {document_id} from S3")
    return f"/tmp/test-{document_id}.pdf"


@activity.defn
async def mock_parse_document_activity(file_path: str) -> dict:
    """Mock parse document activity."""
    activity.logger.info(f"Mock: Parsing {file_path}")
    return {
        "uuid": "doc-abc-123",
        "content": "Test document content",
        "metadata": {
            "title": "Test Document",
            "author": "Test Author",
            "file_type": "pdf",
            "file_size": 1024,
            "source_path": file_path,
        },
        "chunks": [
            {"text": "Chunk 1", "index": 0},
            {"text": "Chunk 2", "index": 1},
        ],
    }


@activity.defn
async def mock_extract_entities_activity(parsed_doc: dict) -> list:
    """Mock entity extraction activity."""
    activity.logger.info(f"Mock: Extracting entities from {parsed_doc['uuid']}")
    return [
        {"uuid": "entity-1", "name": "Acme Corp", "entity_type": "organization"},
        {"uuid": "entity-2", "name": "John Doe", "entity_type": "person"},
    ]


@activity.defn
async def mock_generate_embeddings_activity(parsed_doc: dict) -> dict:
    """Mock embedding generation activity."""
    activity.logger.info(f"Mock: Generating embeddings for {parsed_doc['uuid']}")
    return {
        "document_embedding": [0.1] * 1536,
        "chunk_embeddings": [[0.2] * 1536, [0.3] * 1536],
    }


@activity.defn
async def mock_write_to_databases_activity(
    parsed_doc: dict,
    entities: list,
    embeddings: dict,
) -> dict:
    """Mock database write activity (Enhanced Saga)."""
    activity.logger.info(f"Mock: Writing {parsed_doc['uuid']} to databases")
    return {
        "status": "success",
        "document_id": parsed_doc["uuid"],
        "databases_written": ["neo4j", "postgres", "qdrant", "redis"],
    }


# ============================================================================
# Test 1-5: Workflow Execution
# ============================================================================


@pytest.mark.asyncio
async def test_ingestion_workflow_executes_successfully():
    """Test complete workflow executes all 5 steps successfully."""
    async with await WorkflowEnvironment.start_time_skipping() as env:
        async with Worker(
            env.client,
            task_queue="test-queue",
            workflows=[DocumentIngestionWorkflow],
            activities=[
                mock_download_from_s3_activity,
                mock_parse_document_activity,
                mock_extract_entities_activity,
                mock_generate_embeddings_activity,
                mock_write_to_databases_activity,
            ],
        ):
            result = await env.client.execute_workflow(
                DocumentIngestionWorkflow.run,
                "doc-123",
                "frontapp",
                id="test-workflow-success",
                task_queue="test-queue",
            )

            assert result["status"] == "success"
            assert result["document_id"] == "doc-123"
            assert result["source"] == "frontapp"
            assert "databases_written" in result
            assert len(result["databases_written"]) == 4


@pytest.mark.asyncio
async def test_ingestion_workflow_status_tracking():
    """Test workflow status updates correctly through all stages."""
    async with await WorkflowEnvironment.start_time_skipping() as env:
        async with Worker(
            env.client,
            task_queue="test-queue",
            workflows=[DocumentIngestionWorkflow],
            activities=[
                mock_download_from_s3_activity,
                mock_parse_document_activity,
                mock_extract_entities_activity,
                mock_generate_embeddings_activity,
                mock_write_to_databases_activity,
            ],
        ):
            # Start workflow (don't wait for completion)
            handle = await env.client.start_workflow(
                DocumentIngestionWorkflow.run,
                "doc-456",
                "turvo",
                id="test-workflow-status",
                task_queue="test-queue",
            )

            # Wait for workflow to complete
            result = await handle.result()

            # Query final status
            final_status = await handle.query(DocumentIngestionWorkflow.get_status)

            assert final_status["document_id"] == "doc-456"
            assert final_status["source"] == "turvo"
            assert final_status["status"] == "completed"
            assert result["status"] == "success"


@pytest.mark.asyncio
async def test_ingestion_workflow_with_custom_bucket():
    """Test workflow accepts custom S3 bucket parameter."""
    async with await WorkflowEnvironment.start_time_skipping() as env:
        async with Worker(
            env.client,
            task_queue="test-queue",
            workflows=[DocumentIngestionWorkflow],
            activities=[
                mock_download_from_s3_activity,
                mock_parse_document_activity,
                mock_extract_entities_activity,
                mock_generate_embeddings_activity,
                mock_write_to_databases_activity,
            ],
        ):
            result = await env.client.execute_workflow(
                DocumentIngestionWorkflow.run,
                "doc-789",
                "samsara",
                "custom-bucket",
                "custom/prefix",
                id="test-workflow-custom-bucket",
                task_queue="test-queue",
            )

            assert result["status"] == "success"
            assert result["document_id"] == "doc-789"


@pytest.mark.asyncio
async def test_ingestion_workflow_retry_on_download_failure():
    """Test workflow retries download activity on transient failure."""
    attempt_count = 0

    @activity.defn
    async def failing_download_activity(document_id, source, bucket=None, prefix=None):
        nonlocal attempt_count
        attempt_count += 1

        if attempt_count < 3:
            raise ApplicationError(
                f"Download failed, attempt {attempt_count}",
                type="S3DownloadError",
                non_retryable=False,
            )

        return f"/tmp/test-{document_id}.pdf"

    async with await WorkflowEnvironment.start_time_skipping() as env:
        async with Worker(
            env.client,
            task_queue="test-queue",
            workflows=[DocumentIngestionWorkflow],
            activities=[
                failing_download_activity,
                mock_parse_document_activity,
                mock_extract_entities_activity,
                mock_generate_embeddings_activity,
                mock_write_to_databases_activity,
            ],
        ):
            result = await env.client.execute_workflow(
                DocumentIngestionWorkflow.run,
                "doc-retry",
                "frontapp",
                id="test-workflow-retry-download",
                task_queue="test-queue",
            )

            assert result["status"] == "success"
            assert attempt_count == 3  # Verify retries happened


@pytest.mark.asyncio
async def test_ingestion_workflow_retry_on_embedding_failure():
    """Test workflow retries embedding generation on OpenAI rate limit."""
    attempt_count = 0

    @activity.defn
    async def failing_embedding_activity(parsed_doc):
        nonlocal attempt_count
        attempt_count += 1

        if attempt_count < 2:
            raise ApplicationError(
                "OpenAI rate limit exceeded",
                type="OpenAIRateLimitError",
                non_retryable=False,
            )

        return {
            "document_embedding": [0.1] * 1536,
            "chunk_embeddings": [[0.2] * 1536],
        }

    async with await WorkflowEnvironment.start_time_skipping() as env:
        async with Worker(
            env.client,
            task_queue="test-queue",
            workflows=[DocumentIngestionWorkflow],
            activities=[
                mock_download_from_s3_activity,
                mock_parse_document_activity,
                mock_extract_entities_activity,
                failing_embedding_activity,
                mock_write_to_databases_activity,
            ],
        ):
            result = await env.client.execute_workflow(
                DocumentIngestionWorkflow.run,
                "doc-embed-retry",
                "frontapp",
                id="test-workflow-retry-embedding",
                task_queue="test-queue",
            )

            assert result["status"] == "success"
            assert attempt_count == 2


# ============================================================================
# Test 6-8: Workflow Queries
# ============================================================================


@pytest.mark.asyncio
async def test_get_status_query_during_execution():
    """Test get_status query can be called during workflow execution."""

    # Create slow parse activity to keep workflow running
    @activity.defn
    async def slow_parse_activity(file_path: str) -> dict:
        import asyncio
        await asyncio.sleep(0.1)
        return mock_parse_document_activity.__wrapped__(file_path)

    async with await WorkflowEnvironment.start_time_skipping() as env:
        async with Worker(
            env.client,
            task_queue="test-queue",
            workflows=[DocumentIngestionWorkflow],
            activities=[
                mock_download_from_s3_activity,
                slow_parse_activity,
                mock_extract_entities_activity,
                mock_generate_embeddings_activity,
                mock_write_to_databases_activity,
            ],
        ):
            # Start workflow
            handle = await env.client.start_workflow(
                DocumentIngestionWorkflow.run,
                "doc-query-test",
                "frontapp",
                id="test-workflow-query",
                task_queue="test-queue",
            )

            # Query status immediately (workflow still running)
            status = await handle.query(DocumentIngestionWorkflow.get_status)

            assert status["document_id"] == "doc-query-test"
            assert status["source"] == "frontapp"
            assert status["status"] in [
                "pending",
                "downloading",
                "downloaded",
                "parsing",
                "parsed",
                "extracting_entities",
                "entities_extracted",
                "generating_embeddings",
                "embeddings_generated",
                "writing_databases",
                "completed",
            ]

            # Wait for completion
            await handle.result()


@pytest.mark.asyncio
async def test_get_status_query_after_completion():
    """Test get_status query returns correct final status."""
    async with await WorkflowEnvironment.start_time_skipping() as env:
        async with Worker(
            env.client,
            task_queue="test-queue",
            workflows=[DocumentIngestionWorkflow],
            activities=[
                mock_download_from_s3_activity,
                mock_parse_document_activity,
                mock_extract_entities_activity,
                mock_generate_embeddings_activity,
                mock_write_to_databases_activity,
            ],
        ):
            handle = await env.client.start_workflow(
                DocumentIngestionWorkflow.run,
                "doc-final-status",
                "turvo",
                id="test-workflow-final-status",
                task_queue="test-queue",
            )

            # Wait for completion
            result = await handle.result()

            # Query final status
            status = await handle.query(DocumentIngestionWorkflow.get_status)

            assert status["status"] == "completed"
            assert status["document_id"] == "doc-final-status"
            assert status["error"] is None
            assert result["status"] == "success"


@pytest.mark.asyncio
async def test_get_status_query_on_failure():
    """Test get_status query shows error when workflow fails."""

    @activity.defn
    async def always_failing_parse(file_path: str):
        raise ApplicationError(
            "Parse failed permanently",
            type="UnsupportedFormatError",
            non_retryable=True,
        )

    async with await WorkflowEnvironment.start_time_skipping() as env:
        async with Worker(
            env.client,
            task_queue="test-queue",
            workflows=[DocumentIngestionWorkflow],
            activities=[
                mock_download_from_s3_activity,
                always_failing_parse,
                mock_extract_entities_activity,
                mock_generate_embeddings_activity,
                mock_write_to_databases_activity,
            ],
        ):
            handle = await env.client.start_workflow(
                DocumentIngestionWorkflow.run,
                "doc-fail",
                "frontapp",
                id="test-workflow-failure-status",
                task_queue="test-queue",
            )

            # Wait for workflow (it will complete with failure result)
            result = await handle.result()

            # Query status
            status = await handle.query(DocumentIngestionWorkflow.get_status)

            assert status["status"] == "failed"
            assert status["error"] is not None
            assert "Parse failed" in status["error"]
            assert result["status"] == "failed"


# ============================================================================
# Test 9-12: Error Handling
# ============================================================================


@pytest.mark.asyncio
async def test_workflow_validation_error_no_retry():
    """Test workflow does not retry on non-retryable validation errors."""

    @activity.defn
    async def validation_error_parse(file_path: str):
        raise ApplicationError(
            "Invalid document format",
            type="ValidationError",
            non_retryable=True,
        )

    async with await WorkflowEnvironment.start_time_skipping() as env:
        async with Worker(
            env.client,
            task_queue="test-queue",
            workflows=[DocumentIngestionWorkflow],
            activities=[
                mock_download_from_s3_activity,
                validation_error_parse,
                mock_extract_entities_activity,
                mock_generate_embeddings_activity,
                mock_write_to_databases_activity,
            ],
        ):
            result = await env.client.execute_workflow(
                DocumentIngestionWorkflow.run,
                "doc-validation-error",
                "frontapp",
                id="test-workflow-validation-error",
                task_queue="test-queue",
            )

            assert result["status"] == "failed"
            assert "Invalid document format" in result["error"]


@pytest.mark.asyncio
async def test_workflow_document_not_found_error():
    """Test workflow handles document not found gracefully."""

    @activity.defn
    async def not_found_download(document_id, source, bucket=None, prefix=None):
        raise ApplicationError(
            f"Document not found: s3://bucket/{document_id}",
            type="DocumentNotFoundError",
            non_retryable=True,
        )

    async with await WorkflowEnvironment.start_time_skipping() as env:
        async with Worker(
            env.client,
            task_queue="test-queue",
            workflows=[DocumentIngestionWorkflow],
            activities=[
                not_found_download,
                mock_parse_document_activity,
                mock_extract_entities_activity,
                mock_generate_embeddings_activity,
                mock_write_to_databases_activity,
            ],
        ):
            result = await env.client.execute_workflow(
                DocumentIngestionWorkflow.run,
                "doc-not-found",
                "frontapp",
                id="test-workflow-not-found",
                task_queue="test-queue",
            )

            assert result["status"] == "failed"
            assert "Document not found" in result["error"]


@pytest.mark.asyncio
async def test_workflow_saga_rollback():
    """Test workflow handles Enhanced Saga rollback on database write failure."""

    @activity.defn
    async def failing_write_activity(parsed_doc, entities, embeddings):
        raise ApplicationError(
            "Database write failed, saga rolled back",
            type="DatabaseWriteError",
            non_retryable=False,  # Retryable
        )

    attempt_count = 0

    @activity.defn
    async def retrying_write_activity(parsed_doc, entities, embeddings):
        nonlocal attempt_count
        attempt_count += 1

        if attempt_count < 3:
            raise ApplicationError(
                "Database temporarily unavailable",
                type="DatabaseWriteError",
                non_retryable=False,
            )

        return {
            "status": "success",
            "document_id": parsed_doc["uuid"],
            "databases_written": ["neo4j", "postgres", "qdrant", "redis"],
        }

    async with await WorkflowEnvironment.start_time_skipping() as env:
        async with Worker(
            env.client,
            task_queue="test-queue",
            workflows=[DocumentIngestionWorkflow],
            activities=[
                mock_download_from_s3_activity,
                mock_parse_document_activity,
                mock_extract_entities_activity,
                mock_generate_embeddings_activity,
                retrying_write_activity,
            ],
        ):
            result = await env.client.execute_workflow(
                DocumentIngestionWorkflow.run,
                "doc-saga-retry",
                "frontapp",
                id="test-workflow-saga-retry",
                task_queue="test-queue",
            )

            assert result["status"] == "success"
            assert attempt_count == 3  # Verify retries


@pytest.mark.asyncio
async def test_workflow_unsupported_format_error():
    """Test workflow fails fast on unsupported document format."""

    @activity.defn
    async def unsupported_format_parse(file_path: str):
        raise ApplicationError(
            "Unsupported file format: .xyz",
            type="UnsupportedFormatError",
            non_retryable=True,
        )

    async with await WorkflowEnvironment.start_time_skipping() as env:
        async with Worker(
            env.client,
            task_queue="test-queue",
            workflows=[DocumentIngestionWorkflow],
            activities=[
                mock_download_from_s3_activity,
                unsupported_format_parse,
                mock_extract_entities_activity,
                mock_generate_embeddings_activity,
                mock_write_to_databases_activity,
            ],
        ):
            result = await env.client.execute_workflow(
                DocumentIngestionWorkflow.run,
                "doc-unsupported",
                "frontapp",
                id="test-workflow-unsupported-format",
                task_queue="test-queue",
            )

            assert result["status"] == "failed"
            assert "Unsupported file format" in result["error"]


# ============================================================================
# Test 13-15: Edge Cases
# ============================================================================


@pytest.mark.asyncio
async def test_workflow_empty_document():
    """Test workflow handles empty document gracefully."""

    @activity.defn
    async def empty_parse_activity(file_path: str) -> dict:
        return {
            "uuid": "doc-empty",
            "content": "",
            "metadata": {
                "title": "",
                "author": "",
                "file_type": "txt",
                "file_size": 0,
                "source_path": file_path,
            },
            "chunks": [],
        }

    @activity.defn
    async def empty_entities_activity(parsed_doc: dict) -> list:
        return []  # No entities in empty document

    async with await WorkflowEnvironment.start_time_skipping() as env:
        async with Worker(
            env.client,
            task_queue="test-queue",
            workflows=[DocumentIngestionWorkflow],
            activities=[
                mock_download_from_s3_activity,
                empty_parse_activity,
                empty_entities_activity,
                mock_generate_embeddings_activity,
                mock_write_to_databases_activity,
            ],
        ):
            result = await env.client.execute_workflow(
                DocumentIngestionWorkflow.run,
                "doc-empty",
                "frontapp",
                id="test-workflow-empty-doc",
                task_queue="test-queue",
            )

            # Workflow should complete successfully even with empty content
            assert result["status"] == "success"


@pytest.mark.asyncio
async def test_workflow_large_document():
    """Test workflow handles large document with many chunks."""

    @activity.defn
    async def large_parse_activity(file_path: str) -> dict:
        # Simulate 100 chunks
        chunks = [{"text": f"Chunk {i}", "index": i} for i in range(100)]
        return {
            "uuid": "doc-large",
            "content": "Large document content" * 1000,
            "metadata": {
                "title": "Large Document",
                "author": "Test",
                "file_type": "pdf",
                "file_size": 1024 * 1024 * 10,  # 10MB
                "source_path": file_path,
            },
            "chunks": chunks,
        }

    @activity.defn
    async def large_embeddings_activity(parsed_doc: dict) -> dict:
        chunk_count = len(parsed_doc["chunks"])
        return {
            "document_embedding": [0.1] * 1536,
            "chunk_embeddings": [[0.2] * 1536 for _ in range(chunk_count)],
        }

    async with await WorkflowEnvironment.start_time_skipping() as env:
        async with Worker(
            env.client,
            task_queue="test-queue",
            workflows=[DocumentIngestionWorkflow],
            activities=[
                mock_download_from_s3_activity,
                large_parse_activity,
                mock_extract_entities_activity,
                large_embeddings_activity,
                mock_write_to_databases_activity,
            ],
        ):
            result = await env.client.execute_workflow(
                DocumentIngestionWorkflow.run,
                "doc-large",
                "frontapp",
                id="test-workflow-large-doc",
                task_queue="test-queue",
            )

            assert result["status"] == "success"


@pytest.mark.asyncio
async def test_workflow_logs_all_steps():
    """Test workflow logs all steps correctly."""
    logged_steps = []

    @activity.defn
    async def logging_download(document_id, source, bucket=None, prefix=None):
        logged_steps.append("download")
        return mock_download_from_s3_activity.__wrapped__(
            document_id, source, bucket, prefix
        )

    @activity.defn
    async def logging_parse(file_path: str):
        logged_steps.append("parse")
        return mock_parse_document_activity.__wrapped__(file_path)

    @activity.defn
    async def logging_extract(parsed_doc: dict):
        logged_steps.append("extract")
        return mock_extract_entities_activity.__wrapped__(parsed_doc)

    @activity.defn
    async def logging_embed(parsed_doc: dict):
        logged_steps.append("embed")
        return mock_generate_embeddings_activity.__wrapped__(parsed_doc)

    @activity.defn
    async def logging_write(parsed_doc, entities, embeddings):
        logged_steps.append("write")
        return mock_write_to_databases_activity.__wrapped__(
            parsed_doc, entities, embeddings
        )

    async with await WorkflowEnvironment.start_time_skipping() as env:
        async with Worker(
            env.client,
            task_queue="test-queue",
            workflows=[DocumentIngestionWorkflow],
            activities=[
                logging_download,
                logging_parse,
                logging_extract,
                logging_embed,
                logging_write,
            ],
        ):
            result = await env.client.execute_workflow(
                DocumentIngestionWorkflow.run,
                "doc-logging",
                "frontapp",
                id="test-workflow-logging",
                task_queue="test-queue",
            )

            assert result["status"] == "success"
            assert logged_steps == ["download", "parse", "extract", "embed", "write"]


# ============================================================================
# Test 16: Integration Test (Skipped)
# ============================================================================


@pytest.mark.skip(reason="Requires live Temporal server and databases")
@pytest.mark.asyncio
async def test_workflow_integration_with_real_temporal():
    """Integration test with real Temporal server and Enhanced Saga.

    This test requires:
    - Temporal server running on localhost:7233
    - All databases available (Neo4j, PostgreSQL, Qdrant, Redis)
    - Worker running with real activities
    - S3 bucket with test document

    Run manually when performing integration testing.
    """
    from temporalio.client import Client

    client = await Client.connect("localhost:7233")

    result = await client.execute_workflow(
        DocumentIngestionWorkflow.run,
        "test-doc-integration",
        "frontapp",
        id="integration-test-workflow",
        task_queue="apex-ingestion-queue",
    )

    assert result["status"] == "success"
    assert result["document_id"] == "test-doc-integration"
    assert len(result["databases_written"]) == 4


# ============================================================================
# Test Summary
# ============================================================================
"""
Test Coverage Summary:

Workflow Execution (5 tests):
- ✅ test_ingestion_workflow_executes_successfully
- ✅ test_ingestion_workflow_status_tracking
- ✅ test_ingestion_workflow_with_custom_bucket
- ✅ test_ingestion_workflow_retry_on_download_failure
- ✅ test_ingestion_workflow_retry_on_embedding_failure

Workflow Queries (3 tests):
- ✅ test_get_status_query_during_execution
- ✅ test_get_status_query_after_completion
- ✅ test_get_status_query_on_failure

Error Handling (4 tests):
- ✅ test_workflow_validation_error_no_retry
- ✅ test_workflow_document_not_found_error
- ✅ test_workflow_saga_rollback
- ✅ test_workflow_unsupported_format_error

Edge Cases (3 tests):
- ✅ test_workflow_empty_document
- ✅ test_workflow_large_document
- ✅ test_workflow_logs_all_steps

Integration (1 test, skipped):
- ⏭️  test_workflow_integration_with_real_temporal

Total: 16 tests (15 runnable, 1 skipped)

Run Command:
    cd /Users/richardglaubitz/Projects/apex-memory-system
    export PYTHONPATH=/Users/richardglaubitz/Projects/apex-memory-system/src:$PYTHONPATH
    pytest /Users/richardglaubitz/Projects/Apex-Memory-System-Development/upgrades/active/temporal-implementation/tests/section-8-ingestion-workflow/test_ingestion_workflow.py -v
"""
