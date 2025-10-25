"""Basic DocumentIngestionWorkflow execution example.

This example demonstrates the simplest way to execute the document ingestion
workflow with Temporal.

Prerequisites:
- Temporal server running on localhost:7233
- Worker running (python -m apex_memory.temporal.workers.dev_worker)
- Document uploaded to S3 at: s3://apex-documents/frontapp/{document_id}

Usage:
    python ingest-document-basic.py doc-abc-123 frontapp

Author: Apex Infrastructure Team
Created: 2025-10-18
"""

import asyncio
import sys
from temporalio.client import Client

# Add src to path
sys.path.insert(0, "/Users/richardglaubitz/Projects/apex-memory-system/src")

from apex_memory.temporal.workflows.ingestion import DocumentIngestionWorkflow


async def main():
    """Execute basic document ingestion workflow."""

    # Get document ID and source from command line
    if len(sys.argv) < 3:
        print("Usage: python ingest-document-basic.py <document_id> <source>")
        print("Example: python ingest-document-basic.py doc-abc-123 frontapp")
        sys.exit(1)

    document_id = sys.argv[1]
    source = sys.argv[2]

    print(f"\n🚀 Starting ingestion workflow for document: {document_id}")
    print(f"   Source: {source}")
    print(f"   S3 location: s3://apex-documents/{source}/{document_id}")
    print()

    # Connect to Temporal Server
    client = await Client.connect("localhost:7233")

    try:
        # Execute workflow (blocks until completion)
        result = await client.execute_workflow(
            DocumentIngestionWorkflow.run,
            document_id,
            source,
            id=f"ingest-{document_id}",
            task_queue="apex-ingestion-queue",
        )

        # Print result
        if result["status"] == "success":
            print("✅ Ingestion completed successfully!")
            print(f"   Document ID: {result['document_id']}")
            print(f"   Source: {result['source']}")
            print(f"   Databases written: {', '.join(result['databases_written'])}")
            print(f"   Workflow status: {result['workflow_status']}")
        else:
            print("❌ Ingestion failed!")
            print(f"   Error: {result['error']}")

    except Exception as e:
        print(f"❌ Workflow execution failed: {str(e)}")
        sys.exit(1)

    print()
    print("📊 View workflow in Temporal UI: http://localhost:8088")
    print()


if __name__ == "__main__":
    asyncio.run(main())
