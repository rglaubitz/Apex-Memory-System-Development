"""Document Ingestion Workflow with Enhanced Saga Integration.

Demonstrates hybrid architecture:
- Temporal for orchestration
- Enhanced Saga for database writes

This is the pattern we'll use in production.
"""

import asyncio
from datetime import timedelta
from temporalio import workflow, activity
from temporalio.common import RetryPolicy
from temporalio.client import Client
from temporalio.worker import Worker

# Simulated imports (replace with actual in production)
from dataclasses import dataclass
from typing import List


@dataclass
class ParsedDocument:
    """Simulated ParsedDocument model."""
    uuid: str
    content: str
    chunks: List[str]


@activity.defn
async def parse_document(document_id: str) -> ParsedDocument:
    """Parse document (idempotent activity)."""
    activity.logger.info(f"Parsing document: {document_id}")
    
    # Simulate parsing
    await asyncio.sleep(0.5)
    
    return ParsedDocument(
        uuid=document_id,
        content="Sample content",
        chunks=["chunk1", "chunk2", "chunk3"]
    )


@activity.defn
async def extract_entities(parsed: ParsedDocument) -> List[dict]:
    """Extract entities (idempotent activity)."""
    activity.logger.info(f"Extracting entities from {parsed.uuid}")
    
    # Simulate entity extraction
    await asyncio.sleep(0.3)
    
    return [
        {"type": "person", "name": "John Doe"},
        {"type": "organization", "name": "Apex Corp"}
    ]


@activity.defn
async def write_to_databases(
    parsed: ParsedDocument, 
    entities: List[dict]
) -> dict:
    """Write to databases using Enhanced Saga.
    
    This activity DELEGATES to DatabaseWriteOrchestrator which handles:
    - Distributed locking
    - Idempotency
    - Circuit breakers
    - Retries
    - Atomic 4-DB writes
    - Rollback + DLQ
    """
    activity.logger.info(f"Writing {parsed.uuid} via Enhanced Saga")
    
    # Simulate Enhanced Saga call
    # In production: orchestrator.write_document_parallel(parsed, embeddings)
    await asyncio.sleep(1.0)
    
    activity.logger.info(f"✅ Write successful for {parsed.uuid}")
    return {
        "status": "success",
        "document_id": parsed.uuid,
        "databases": ["neo4j", "postgres", "qdrant", "redis"]
    }


@workflow.defn
class DocumentIngestionWorkflow:
    """Production ingestion workflow using Temporal + Enhanced Saga."""
    
    @workflow.run
    async def run(self, document_id: str) -> dict:
        """Orchestrate document ingestion.
        
        Args:
            document_id: ID of document to ingest
            
        Returns:
            Ingestion result
        """
        workflow.logger.info(f"Starting ingestion for {document_id}")
        
        # Step 1: Parse document
        parsed = await workflow.execute_activity(
            parse_document,
            document_id,
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=RetryPolicy(maximum_attempts=3)
        )
        
        workflow.logger.info(f"Parsed {len(parsed.chunks)} chunks")
        
        # Step 2: Extract entities
        entities = await workflow.execute_activity(
            extract_entities,
            parsed,
            start_to_close_timeout=timedelta(minutes=2),
            retry_policy=RetryPolicy(maximum_attempts=3)
        )
        
        workflow.logger.info(f"Extracted {len(entities)} entities")
        
        # Step 3: Write to databases (Enhanced Saga)
        result = await workflow.execute_activity(
            write_to_databases,
            parsed, entities,
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=RetryPolicy(
                initial_interval=timedelta(seconds=5),
                maximum_attempts=3
            )
        )
        
        workflow.logger.info(f"✅ Ingestion complete: {result}")
        return result


async def main():
    """Run ingestion workflow example."""
    client = await Client.connect("localhost:7233")
    
    print("Starting ingestion worker...")
    async with Worker(
        client,
        task_queue="ingestion-queue",
        workflows=[DocumentIngestionWorkflow],
        activities=[parse_document, extract_entities, write_to_databases]
    ):
        print("Worker started. Executing ingestion workflow...")
        
        result = await client.execute_workflow(
            DocumentIngestionWorkflow.run,
            "doc-123",
            id="ingest-doc-123",
            task_queue="ingestion-queue"
        )
        
        print(f"\n✅ Ingestion Result: {result}")
        print("View in Temporal UI: http://localhost:8088")


if __name__ == "__main__":
    asyncio.run(main())
