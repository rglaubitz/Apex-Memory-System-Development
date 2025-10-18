"""DocumentIngestionWorkflow with status query example.

This example demonstrates:
- Starting workflow asynchronously (non-blocking)
- Querying workflow status while it's running
- Polling for completion
- Reading final result

Prerequisites:
- Temporal server running on localhost:7233
- Worker running (python -m apex_memory.temporal.workers.dev_worker)
- Document uploaded to S3

Usage:
    python ingest-with-status-query.py doc-xyz-456 turvo

Author: Apex Infrastructure Team
Created: 2025-10-18
"""

import asyncio
import sys
from temporalio.client import Client

sys.path.insert(0, "/Users/richardglaubitz/Projects/apex-memory-system/src")

from apex_memory.temporal.workflows.ingestion import DocumentIngestionWorkflow


async def main():
    """Execute workflow with status polling."""

    if len(sys.argv) < 3:
        print("Usage: python ingest-with-status-query.py <document_id> <source>")
        print("Example: python ingest-with-status-query.py doc-xyz-456 turvo")
        sys.exit(1)

    document_id = sys.argv[1]
    source = sys.argv[2]

    print(f"\n🚀 Starting ingestion workflow: {document_id}")
    print()

    # Connect to Temporal
    client = await Client.connect("localhost:7233")

    try:
        # Start workflow (non-blocking)
        handle = await client.start_workflow(
            DocumentIngestionWorkflow.run,
            document_id,
            source,
            id=f"ingest-{document_id}",
            task_queue="apex-ingestion-queue",
        )

        print(f"✅ Workflow started: {handle.id}")
        print()

        # Poll status while workflow is running
        print("📊 Polling workflow status...")
        print()

        previous_status = None

        while True:
            # Query current status
            status = await handle.query(DocumentIngestionWorkflow.get_status)

            # Print status update only if changed
            if status["status"] != previous_status:
                print(f"   Status: {status['status']}")
                previous_status = status["status"]

            # Check if workflow completed
            if status["status"] in ["completed", "failed"]:
                break

            # Wait before next poll
            await asyncio.sleep(0.5)

        print()

        # Get final result
        result = await handle.result()

        # Print final result
        if result["status"] == "success":
            print("✅ Ingestion completed successfully!")
            print(f"   Document ID: {result['document_id']}")
            print(f"   Databases written: {', '.join(result['databases_written'])}")
        else:
            print("❌ Ingestion failed!")
            print(f"   Error: {result['error']}")

        # Query final status details
        final_status = await handle.query(DocumentIngestionWorkflow.get_status)
        print()
        print("📋 Final Status Details:")
        print(f"   Document ID: {final_status['document_id']}")
        print(f"   Source: {final_status['source']}")
        print(f"   Status: {final_status['status']}")
        print(f"   File Path: {final_status['file_path']}")
        if final_status['error']:
            print(f"   Error: {final_status['error']}")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

    print()
    print("📊 View workflow in Temporal UI: http://localhost:8088")
    print()


if __name__ == "__main__":
    asyncio.run(main())
