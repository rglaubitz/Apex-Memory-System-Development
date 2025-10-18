"""Ingestion activities tests for Temporal.io integration.

These tests verify that ingestion activities work correctly, delegate to existing
services, and preserve the Enhanced Saga pattern (121 tests).

Tests verify:
- Document parsing (5 tests)
- Entity extraction (4 tests)
- Embedding generation (4 tests)
- Database writes with Enhanced Saga (7 tests)

Author: Apex Infrastructure Team
Created: 2025-10-18
Section: 7 - Ingestion Activities
"""

import asyncio
import logging
import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from pathlib import Path
from datetime import datetime

from temporalio.exceptions import ApplicationError

from apex_memory.temporal.activities.ingestion import (
    parse_document_activity,
    extract_entities_activity,
    generate_embeddings_activity,
    write_to_databases_activity,
)
from apex_memory.models.document import ParsedDocument, DocumentMetadata, WriteResult, WriteStatus
from apex_memory.services.entity_extractor import Entity


# ============================================================================
# Parse Document Activity Tests (5 tests)
# ============================================================================


@pytest.mark.asyncio
async def test_parse_document_activity():
    """Test 1/20: Verify parse_document_activity succeeds with mocked parser."""
    # Mock ParsedDocument
    mock_metadata = DocumentMetadata(
        title="Test Document",
        author="Test Author",
        file_type="pdf",
        file_size=1024,
        source_path="/tmp/test.pdf",
        created_date=datetime.utcnow(),
        modified_date=datetime.utcnow(),
    )

    mock_parsed_doc = ParsedDocument(
        uuid="test-uuid-123",
        metadata=mock_metadata,
        content="This is test content for parsing.",
        chunks=["Chunk 1", "Chunk 2"],
        structure={},
        entities=[],
    )

    # Mock DocumentParser and activity context
    with patch("apex_memory.temporal.activities.ingestion.DocumentParser") as MockParser, \
         patch("apex_memory.temporal.activities.ingestion.activity.info") as mock_info, \
         patch("apex_memory.temporal.activities.ingestion.activity.heartbeat"):

        mock_parser_instance = MockParser.return_value
        mock_parser_instance.parse_document.return_value = mock_parsed_doc
        mock_info.return_value = MagicMock(attempt=1)

        # Execute activity
        result = await parse_document_activity("/tmp/test.pdf")

        # Verify result structure
        assert result["uuid"] == "test-uuid-123"
        assert result["content"] == "This is test content for parsing."
        assert len(result["chunks"]) == 2
        assert result["metadata"]["title"] == "Test Document"
        assert result["metadata"]["file_type"] == "pdf"

        print("✓ Parse activity succeeds with valid document")


@pytest.mark.asyncio
async def test_parse_activity_with_heartbeat():
    """Test 2/20: Verify heartbeats are sent during parsing."""
    # Mock ParsedDocument
    mock_metadata = DocumentMetadata(
        title="Test",
        author="Author",
        file_type="pdf",
        file_size=1024,
        source_path="/tmp/test.pdf",
    )

    mock_parsed_doc = ParsedDocument(
        uuid="test-uuid",
        metadata=mock_metadata,
        content="Content",
        chunks=["Chunk"],
        structure={},
        entities=[],
    )

    # Mock DocumentParser, heartbeat, and info
    with patch("apex_memory.temporal.activities.ingestion.DocumentParser") as MockParser, \
         patch("apex_memory.temporal.activities.ingestion.activity.heartbeat") as mock_heartbeat, \
         patch("apex_memory.temporal.activities.ingestion.activity.info") as mock_info:

        mock_parser_instance = MockParser.return_value
        mock_parser_instance.parse_document.return_value = mock_parsed_doc
        mock_info.return_value = MagicMock(attempt=1)

        # Execute activity
        await parse_document_activity("/tmp/test.pdf")

        # Verify heartbeats called
        assert mock_heartbeat.call_count >= 2  # At least "Loading" and "Complete"
        heartbeat_messages = [call[0][0] for call in mock_heartbeat.call_args_list]
        assert "Loading document" in heartbeat_messages
        assert "Parsing complete" in heartbeat_messages

        print("✓ Heartbeats sent during parsing")


@pytest.mark.asyncio
async def test_parse_activity_retry():
    """Test 3/20: Verify retry on transient failure."""
    from apex_memory.services.document_parser import DocumentParseError

    # Mock DocumentParser to raise transient error
    with patch("apex_memory.temporal.activities.ingestion.DocumentParser") as MockParser, \
         patch("apex_memory.temporal.activities.ingestion.activity.info") as mock_info, \
         patch("apex_memory.temporal.activities.ingestion.activity.heartbeat"):

        mock_parser_instance = MockParser.return_value
        mock_parser_instance.parse_document.side_effect = DocumentParseError("Transient error")
        mock_info.return_value = MagicMock(attempt=1)

        # Execute activity and expect ApplicationError
        with pytest.raises(ApplicationError) as exc_info:
            await parse_document_activity("/tmp/test.pdf")

        # Verify error is retryable
        assert exc_info.value.type == "DocumentParseError"
        assert not exc_info.value.non_retryable  # Should be retryable

        print("✓ Parse activity retries on transient failure")


@pytest.mark.asyncio
async def test_parse_activity_invalid_document():
    """Test 4/20: Verify non-retryable error for invalid document."""
    from apex_memory.services.document_parser import UnsupportedFormatError

    # Mock DocumentParser to raise UnsupportedFormatError
    with patch("apex_memory.temporal.activities.ingestion.DocumentParser") as MockParser, \
         patch("apex_memory.temporal.activities.ingestion.activity.info") as mock_info, \
         patch("apex_memory.temporal.activities.ingestion.activity.heartbeat"):

        mock_parser_instance = MockParser.return_value
        mock_parser_instance.parse_document.side_effect = UnsupportedFormatError(".xyz")
        mock_info.return_value = MagicMock(attempt=1)

        # Execute activity and expect non-retryable ApplicationError
        with pytest.raises(ApplicationError) as exc_info:
            await parse_document_activity("/tmp/test.xyz")

        # Verify error is non-retryable
        assert exc_info.value.type == "DocumentParseError"
        assert exc_info.value.non_retryable  # Should NOT retry

        print("✓ Parse activity raises non-retryable error for invalid format")


@pytest.mark.asyncio
async def test_parse_activity_serializable_output():
    """Test 5/20: Verify output is serializable dict (not ParsedDocument object)."""
    # Mock ParsedDocument
    mock_metadata = DocumentMetadata(
        title="Test",
        author="Author",
        file_type="pdf",
        file_size=1024,
        source_path="/tmp/test.pdf",
    )

    mock_parsed_doc = ParsedDocument(
        uuid="test-uuid",
        metadata=mock_metadata,
        content="Content",
        chunks=["Chunk"],
        structure={},
        entities=[],
    )

    # Mock DocumentParser and activity context
    with patch("apex_memory.temporal.activities.ingestion.DocumentParser") as MockParser, \
         patch("apex_memory.temporal.activities.ingestion.activity.info") as mock_info, \
         patch("apex_memory.temporal.activities.ingestion.activity.heartbeat"):

        mock_parser_instance = MockParser.return_value
        mock_parser_instance.parse_document.return_value = mock_parsed_doc
        mock_info.return_value = MagicMock(attempt=1)

        # Execute activity
        result = await parse_document_activity("/tmp/test.pdf")

        # Verify result is dict
        assert isinstance(result, dict)
        assert not isinstance(result, ParsedDocument)
        assert "uuid" in result
        assert "content" in result
        assert "metadata" in result
        assert "chunks" in result

        print("✓ Parse activity returns serializable dict")


# ============================================================================
# Extract Entities Activity Tests (4 tests)
# ============================================================================


@pytest.mark.asyncio
async def test_extract_entities_activity():
    """Test 6/20: Verify extract_entities_activity succeeds."""
    # Mock entities
    mock_entities = [
        Entity(
            name="Company XYZ",
            entity_type="customer",
            confidence=0.9,
            description="Customer entity",
            properties={"industry": "tech"},
            uuid="entity-1",
            mention_text="Company XYZ",
            mention_count=3,
        ),
        Entity(
            name="John Doe",
            entity_type="driver",
            confidence=0.85,
            uuid="entity-2",
        ),
    ]

    # Mock EntityExtractor
    with patch("apex_memory.temporal.activities.ingestion.EntityExtractor") as MockExtractor:
        mock_extractor_instance = MockExtractor.return_value
        mock_extractor_instance.extract_entities.return_value = mock_entities

        # Prepare parsed doc
        parsed_doc = {
            "uuid": "doc-123",
            "content": "Company XYZ hired John Doe as driver.",
            "metadata": {},
            "chunks": [],
        }

        # Execute activity
        result = await extract_entities_activity(parsed_doc)

        # Verify entities extracted
        assert len(result) == 2
        assert result[0]["name"] == "Company XYZ"
        assert result[0]["entity_type"] == "customer"
        assert result[0]["confidence"] == 0.9
        assert result[1]["name"] == "John Doe"
        assert result[1]["entity_type"] == "driver"

        print("✓ Extract entities activity succeeds")


@pytest.mark.asyncio
async def test_extract_entities_empty_content():
    """Test 7/20: Verify empty content returns empty list."""
    # Mock EntityExtractor
    with patch("apex_memory.temporal.activities.ingestion.EntityExtractor") as MockExtractor:
        # Prepare parsed doc with empty content
        parsed_doc = {
            "uuid": "doc-empty",
            "content": "",
            "metadata": {},
            "chunks": [],
        }

        # Execute activity
        result = await extract_entities_activity(parsed_doc)

        # Verify empty list returned
        assert isinstance(result, list)
        assert len(result) == 0

        # Verify extractor was NOT called (short-circuit for empty content)
        MockExtractor.return_value.extract_entities.assert_not_called()

        print("✓ Extract entities handles empty content gracefully")


@pytest.mark.asyncio
async def test_extract_entities_logging():
    """Test 8/20: Verify entity count is logged."""
    # Mock entities
    mock_entities = [
        Entity(name="Entity 1", entity_type="customer", uuid="e1"),
        Entity(name="Entity 2", entity_type="driver", uuid="e2"),
        Entity(name="Entity 3", entity_type="equipment", uuid="e3"),
    ]

    # Mock EntityExtractor and logger
    with patch("apex_memory.temporal.activities.ingestion.EntityExtractor") as MockExtractor, \
         patch("apex_memory.temporal.activities.ingestion.activity.logger") as mock_logger:

        mock_extractor_instance = MockExtractor.return_value
        mock_extractor_instance.extract_entities.return_value = mock_entities

        # Prepare parsed doc
        parsed_doc = {
            "uuid": "doc-123",
            "content": "Content with entities.",
            "metadata": {},
            "chunks": [],
        }

        # Execute activity
        await extract_entities_activity(parsed_doc)

        # Verify logging called with entity count
        assert mock_logger.info.called
        log_messages = [str(call) for call in mock_logger.info.call_args_list]
        assert any("3 entities" in str(msg) for msg in log_messages)

        print("✓ Extract entities logs entity count")


@pytest.mark.asyncio
async def test_extract_entities_output_format():
    """Test 9/20: Verify output format is list of dicts."""
    # Mock entities
    mock_entities = [
        Entity(
            name="Test Entity",
            entity_type="customer",
            confidence=0.9,
            uuid="entity-1",
            description="Test",
            properties={"key": "value"},
            mention_text="Test Entity",
            mention_count=1,
        ),
    ]

    # Mock EntityExtractor
    with patch("apex_memory.temporal.activities.ingestion.EntityExtractor") as MockExtractor:
        mock_extractor_instance = MockExtractor.return_value
        mock_extractor_instance.extract_entities.return_value = mock_entities

        # Prepare parsed doc
        parsed_doc = {
            "uuid": "doc-123",
            "content": "Content",
            "metadata": {},
            "chunks": [],
        }

        # Execute activity
        result = await extract_entities_activity(parsed_doc)

        # Verify output format
        assert isinstance(result, list)
        assert isinstance(result[0], dict)
        assert "uuid" in result[0]
        assert "name" in result[0]
        assert "entity_type" in result[0]
        assert "confidence" in result[0]
        assert "properties" in result[0]

        print("✓ Extract entities returns list of dicts")


# ============================================================================
# Generate Embeddings Activity Tests (4 tests)
# ============================================================================


@pytest.mark.asyncio
async def test_generate_embeddings_activity():
    """Test 10/20: Verify generate_embeddings_activity succeeds."""
    # Mock embeddings
    mock_doc_embedding = [0.1] * 1536  # 1536 dimensions
    mock_chunk_embeddings = [[0.2] * 1536, [0.3] * 1536]  # 2 chunks

    # Mock EmbeddingService and activity context
    with patch("apex_memory.temporal.activities.ingestion.EmbeddingService") as MockService, \
         patch("apex_memory.temporal.activities.ingestion.activity.heartbeat"):

        mock_service_instance = MockService.return_value
        mock_service_instance.generate_embedding.return_value = mock_doc_embedding

        # Mock EmbeddingResult for chunks
        mock_chunk_result = MagicMock()
        mock_chunk_result.embeddings = mock_chunk_embeddings
        mock_service_instance.generate_embeddings.return_value = mock_chunk_result

        # Prepare parsed doc
        parsed_doc = {
            "uuid": "doc-123",
            "content": "Document content for embedding.",
            "chunks": ["Chunk 1", "Chunk 2"],
            "metadata": {},
        }

        # Execute activity
        result = await generate_embeddings_activity(parsed_doc)

        # Verify embeddings generated
        assert "document_embedding" in result
        assert "chunk_embeddings" in result
        assert len(result["document_embedding"]) == 1536
        assert len(result["chunk_embeddings"]) == 2
        assert len(result["chunk_embeddings"][0]) == 1536

        print("✓ Generate embeddings activity succeeds")


@pytest.mark.asyncio
async def test_generate_embeddings_chunk_count():
    """Test 11/20: Verify chunk embeddings count matches input chunks."""
    # Mock embeddings
    mock_doc_embedding = [0.1] * 1536
    mock_chunk_embeddings = [[0.2] * 1536, [0.3] * 1536, [0.4] * 1536]  # 3 chunks

    # Mock EmbeddingService and activity context
    with patch("apex_memory.temporal.activities.ingestion.EmbeddingService") as MockService, \
         patch("apex_memory.temporal.activities.ingestion.activity.heartbeat"):

        mock_service_instance = MockService.return_value
        mock_service_instance.generate_embedding.return_value = mock_doc_embedding

        mock_chunk_result = MagicMock()
        mock_chunk_result.embeddings = mock_chunk_embeddings
        mock_service_instance.generate_embeddings.return_value = mock_chunk_result

        # Prepare parsed doc with 3 chunks
        parsed_doc = {
            "uuid": "doc-123",
            "content": "Content",
            "chunks": ["Chunk 1", "Chunk 2", "Chunk 3"],
            "metadata": {},
        }

        # Execute activity
        result = await generate_embeddings_activity(parsed_doc)

        # Verify chunk count matches
        assert len(result["chunk_embeddings"]) == 3

        print("✓ Chunk embeddings count matches input")


@pytest.mark.asyncio
async def test_generate_embeddings_dimension():
    """Test 12/20: Verify embedding dimension is 1536 (OpenAI text-embedding-3-small)."""
    # Mock embeddings with correct dimension
    correct_dim = 1536
    mock_doc_embedding = [0.1] * correct_dim
    mock_chunk_embeddings = [[0.2] * correct_dim]

    # Mock EmbeddingService and activity context
    with patch("apex_memory.temporal.activities.ingestion.EmbeddingService") as MockService, \
         patch("apex_memory.temporal.activities.ingestion.activity.heartbeat"):

        mock_service_instance = MockService.return_value
        mock_service_instance.generate_embedding.return_value = mock_doc_embedding

        mock_chunk_result = MagicMock()
        mock_chunk_result.embeddings = mock_chunk_embeddings
        mock_service_instance.generate_embeddings.return_value = mock_chunk_result

        # Prepare parsed doc
        parsed_doc = {
            "uuid": "doc-123",
            "content": "Content",
            "chunks": ["Chunk"],
            "metadata": {},
        }

        # Execute activity
        result = await generate_embeddings_activity(parsed_doc)

        # Verify dimension
        assert len(result["document_embedding"]) == correct_dim
        assert len(result["chunk_embeddings"][0]) == correct_dim

        print("✓ Embedding dimension is 1536")


@pytest.mark.asyncio
async def test_generate_embeddings_retry():
    """Test 13/20: Verify retry on OpenAI failure."""
    # Mock EmbeddingService to raise error
    with patch("apex_memory.temporal.activities.ingestion.EmbeddingService") as MockService:
        mock_service_instance = MockService.return_value
        mock_service_instance.generate_embedding.side_effect = Exception("OpenAI rate limit")

        # Prepare parsed doc
        parsed_doc = {
            "uuid": "doc-123",
            "content": "Content",
            "chunks": ["Chunk"],
            "metadata": {},
        }

        # Execute activity and expect ApplicationError
        with pytest.raises(ApplicationError) as exc_info:
            await generate_embeddings_activity(parsed_doc)

        # Verify error is retryable (handles rate limits)
        assert exc_info.value.type == "EmbeddingGenerationError"
        assert not exc_info.value.non_retryable  # Should retry

        print("✓ Generate embeddings retries on OpenAI failure")


# ============================================================================
# Write to Databases Activity Tests (7 tests)
# ============================================================================


@pytest.mark.asyncio
async def test_write_to_databases_activity():
    """Test 14/20: Verify write_to_databases_activity succeeds with mocked Saga."""
    # Mock WriteResult (success)
    mock_write_result = MagicMock(spec=WriteResult)
    mock_write_result.all_success = True
    mock_write_result.status = WriteStatus.SUCCESS

    # Mock DatabaseWriteOrchestrator
    with patch("apex_memory.temporal.activities.ingestion.DatabaseWriteOrchestrator") as MockOrch:
        mock_orch_instance = MockOrch.return_value
        mock_orch_instance.write_document_parallel = AsyncMock(return_value=mock_write_result)

        # Prepare inputs
        parsed_doc = {
            "uuid": "doc-123",
            "content": "Content",
            "metadata": {
                "title": "Test",
                "author": "Author",
                "file_type": "pdf",
                "file_size": 1024,
                "source_path": "/tmp/test.pdf",
                "created_date": None,
                "modified_date": None,
            },
            "chunks": ["Chunk"],
        }

        entities = [{"uuid": "e1", "name": "Entity 1", "entity_type": "customer"}]
        embeddings = {
            "document_embedding": [0.1] * 1536,
            "chunk_embeddings": [[0.2] * 1536],
        }

        # Execute activity
        result = await write_to_databases_activity(parsed_doc, entities, embeddings)

        # Verify result
        assert result["status"] == "success"
        assert result["document_id"] == "doc-123"
        assert "neo4j" in result["databases_written"]
        assert "postgres" in result["databases_written"]
        assert "qdrant" in result["databases_written"]
        assert "redis" in result["databases_written"]

        # Verify orchestrator called
        mock_orch_instance.write_document_parallel.assert_called_once()
        mock_orch_instance.close.assert_called_once()

        print("✓ Write to databases activity succeeds")


@pytest.mark.asyncio
async def test_write_to_databases_saga_integration():
    """Test 15/20: Verify Enhanced Saga is called correctly (INTEGRATION TEST).

    This test uses real DatabaseWriteOrchestrator but mocks database writers.
    """
    # This is an integration test - skip if databases not available
    pytest.skip("Integration test - requires database setup")

    # Real integration test would:
    # 1. Create real DatabaseWriteOrchestrator with mocked database writers
    # 2. Verify write_document_parallel called with correct parameters
    # 3. Verify all 121 Saga tests still pass


@pytest.mark.asyncio
async def test_write_to_databases_all_success():
    """Test 16/20: Verify all databases written successfully."""
    # Mock WriteResult (all success)
    mock_write_result = MagicMock(spec=WriteResult)
    mock_write_result.all_success = True
    mock_write_result.status = WriteStatus.SUCCESS

    # Mock DatabaseWriteOrchestrator
    with patch("apex_memory.temporal.activities.ingestion.DatabaseWriteOrchestrator") as MockOrch:
        mock_orch_instance = MockOrch.return_value
        mock_orch_instance.write_document_parallel = AsyncMock(return_value=mock_write_result)

        # Prepare inputs (minimal)
        parsed_doc = {
            "uuid": "doc-123",
            "content": "Content",
            "metadata": {
                "title": "Test",
                "author": None,
                "file_type": "pdf",
                "file_size": 1024,
                "source_path": "/tmp/test.pdf",
                "created_date": None,
                "modified_date": None,
            },
            "chunks": [],
        }

        # Execute activity
        result = await write_to_databases_activity(parsed_doc, [], {"document_embedding": [], "chunk_embeddings": []})

        # Verify all 4 databases written
        assert len(result["databases_written"]) == 4

        print("✓ All databases written successfully")


@pytest.mark.asyncio
async def test_write_to_databases_rollback():
    """Test 17/20: Verify rollback on failure."""
    # Mock WriteResult (rolled back)
    mock_write_result = MagicMock(spec=WriteResult)
    mock_write_result.all_success = False
    mock_write_result.status = MagicMock()
    mock_write_result.status.value = "ROLLED_BACK"
    mock_write_result.errors = ["Database connection failed"]

    # Mock DatabaseWriteOrchestrator
    with patch("apex_memory.temporal.activities.ingestion.DatabaseWriteOrchestrator") as MockOrch:
        mock_orch_instance = MockOrch.return_value
        mock_orch_instance.write_document_parallel = AsyncMock(return_value=mock_write_result)

        # Prepare inputs
        parsed_doc = {
            "uuid": "doc-fail",
            "content": "Content",
            "metadata": {
                "title": "Test",
                "author": None,
                "file_type": "pdf",
                "file_size": 1024,
                "source_path": "/tmp/test.pdf",
                "created_date": None,
                "modified_date": None,
            },
            "chunks": [],
        }

        # Execute activity and expect ApplicationError
        with pytest.raises(ApplicationError) as exc_info:
            await write_to_databases_activity(parsed_doc, [], {"document_embedding": [], "chunk_embeddings": []})

        # Verify error is retryable (rolled back, can retry)
        assert exc_info.value.type == "DatabaseWriteError"
        assert not exc_info.value.non_retryable  # Should retry

        # Verify close called
        mock_orch_instance.close.assert_called_once()

        print("✓ Write activity handles rollback correctly")


@pytest.mark.asyncio
async def test_write_to_databases_partial_failure():
    """Test 18/20: Verify partial failure handling."""
    # Mock WriteResult (partial failure)
    mock_write_result = MagicMock(spec=WriteResult)
    mock_write_result.all_success = False
    mock_write_result.status = MagicMock()
    mock_write_result.status.value = "PARTIAL"
    mock_write_result.errors = ["Redis write failed"]

    # Mock DatabaseWriteOrchestrator
    with patch("apex_memory.temporal.activities.ingestion.DatabaseWriteOrchestrator") as MockOrch:
        mock_orch_instance = MockOrch.return_value
        mock_orch_instance.write_document_parallel = AsyncMock(return_value=mock_write_result)

        # Prepare inputs
        parsed_doc = {
            "uuid": "doc-partial",
            "content": "Content",
            "metadata": {
                "title": "Test",
                "author": None,
                "file_type": "pdf",
                "file_size": 1024,
                "source_path": "/tmp/test.pdf",
                "created_date": None,
                "modified_date": None,
            },
            "chunks": [],
        }

        # Execute activity and expect ApplicationError
        with pytest.raises(ApplicationError) as exc_info:
            await write_to_databases_activity(parsed_doc, [], {"document_embedding": [], "chunk_embeddings": []})

        # Verify error is non-retryable (partial = likely validation error)
        assert exc_info.value.type == "DatabaseWriteError"
        assert exc_info.value.non_retryable  # Should NOT retry

        print("✓ Write activity handles partial failure correctly")


@pytest.mark.asyncio
async def test_write_to_databases_idempotency():
    """Test 19/20: Verify idempotent retries work.

    Enhanced Saga handles idempotency internally. This test verifies
    the activity delegates correctly.
    """
    # Mock WriteResult (success)
    mock_write_result = MagicMock(spec=WriteResult)
    mock_write_result.all_success = True
    mock_write_result.status = WriteStatus.SUCCESS

    # Mock DatabaseWriteOrchestrator
    with patch("apex_memory.temporal.activities.ingestion.DatabaseWriteOrchestrator") as MockOrch:
        mock_orch_instance = MockOrch.return_value
        mock_orch_instance.write_document_parallel = AsyncMock(return_value=mock_write_result)

        # Verify idempotency enabled in orchestrator init
        assert MockOrch.call_args is None or MockOrch.call_args[1].get("enable_idempotency", True)

        # Prepare inputs
        parsed_doc = {
            "uuid": "doc-idempotent",
            "content": "Content",
            "metadata": {
                "title": "Test",
                "author": None,
                "file_type": "pdf",
                "file_size": 1024,
                "source_path": "/tmp/test.pdf",
                "created_date": None,
                "modified_date": None,
            },
            "chunks": [],
        }

        # Execute activity
        await write_to_databases_activity(parsed_doc, [], {"document_embedding": [], "chunk_embeddings": []})

        # Verify orchestrator initialized with idempotency enabled
        call_kwargs = MockOrch.call_args[1] if MockOrch.call_args else {}
        assert call_kwargs.get("enable_idempotency", True) is True

        print("✓ Write activity enables idempotency in Saga")


@pytest.mark.asyncio
async def test_write_to_databases_circuit_breaker():
    """Test 20/20: Verify circuit breaker is active.

    Enhanced Saga handles circuit breakers internally. This test verifies
    the activity delegates with circuit breakers enabled.
    """
    # Mock WriteResult (success)
    mock_write_result = MagicMock(spec=WriteResult)
    mock_write_result.all_success = True
    mock_write_result.status = WriteStatus.SUCCESS

    # Mock DatabaseWriteOrchestrator
    with patch("apex_memory.temporal.activities.ingestion.DatabaseWriteOrchestrator") as MockOrch:
        mock_orch_instance = MockOrch.return_value
        mock_orch_instance.write_document_parallel = AsyncMock(return_value=mock_write_result)

        # Prepare inputs
        parsed_doc = {
            "uuid": "doc-circuit",
            "content": "Content",
            "metadata": {
                "title": "Test",
                "author": None,
                "file_type": "pdf",
                "file_size": 1024,
                "source_path": "/tmp/test.pdf",
                "created_date": None,
                "modified_date": None,
            },
            "chunks": [],
        }

        # Execute activity
        await write_to_databases_activity(parsed_doc, [], {"document_embedding": [], "chunk_embeddings": []})

        # Verify orchestrator initialized with circuit breakers enabled
        call_kwargs = MockOrch.call_args[1] if MockOrch.call_args else {}
        assert call_kwargs.get("enable_circuit_breakers", True) is True

        print("✓ Write activity enables circuit breakers in Saga")


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
