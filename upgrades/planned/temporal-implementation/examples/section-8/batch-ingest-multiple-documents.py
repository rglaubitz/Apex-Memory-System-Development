"""Batch document ingestion example.

This example demonstrates:
- Spawning multiple workflow instances
- Parallel execution
- Progress tracking
- Result aggregation

Prerequisites:
- Temporal server running on localhost:7233
- Worker running
- Multiple documents in S3

Usage:
    python batch-ingest-multiple-documents.py frontapp doc-1,doc-2,doc-3

Author: Apex Infrastructure Team
Created: 2025-10-18
"""

import asyncio
import sys
from temporalio.client import Client

sys.path.insert(0, "/Users/richardglaubitz/Projects/apex-memory-system/src")

from apex_memory.temporal.workflows.ingestion import DocumentIngestionWorkflow


async def main():
    """Execute multiple ingestion workflows in parallel."""

    if len(sys.argv) < 3:
        print("Usage: python batch-ingest-multiple-documents.py <source> <doc1,doc2,doc3>")
        print("Example: python batch-ingest-multiple-documents.py frontapp doc-1,doc-2,doc-3")
        sys.exit(1)

    source = sys.argv[1]
    document_ids = sys.argv[2].split(",")

    print(f"\n🚀 Starting batch ingestion workflow")
    print(f"   Source: {source}")
    print(f"   Documents: {len(document_ids)}")
    print()

    # Connect to Temporal
    client = await Client.connect("localhost:7233")

    # Start all workflows
    print("📤 Starting workflows...")
    handles = []

    for doc_id in document_ids:
        try:
            handle = await client.start_workflow(
                DocumentIngestionWorkflow.run,
                doc_id,
                source,
                id=f"batch-ingest-{doc_id}",
                task_queue="apex-ingestion-queue",
            )
            handles.append((doc_id, handle))
            print(f"   ✅ Started: {doc_id}")

        except Exception as e:
            print(f"   ❌ Failed to start {doc_id}: {str(e)}")

    print()
    print(f"📊 {len(handles)} workflows started")
    print()

    # Poll for completion
    print("⏳ Waiting for workflows to complete...")
    print()

    completed = 0
    failed = 0
    results = []

    # Use asyncio.gather to wait for all workflows
    async def get_result(doc_id, handle):
        try:
            result = await handle.result()
            return (doc_id, result)
        except Exception as e:
            return (doc_id, {"status": "error", "error": str(e)})

    # Wait for all workflows
    results = await asyncio.gather(*[
        get_result(doc_id, handle) for doc_id, handle in handles
    ])

    # Analyze results
    print("📋 Results:")
    print()

    for doc_id, result in results:
        if result["status"] == "success":
            completed += 1
            print(f"   ✅ {doc_id}: Success")
            print(f"      Databases: {', '.join(result.get('databases_written', []))}")
        else:
            failed += 1
            print(f"   ❌ {doc_id}: Failed")
            print(f"      Error: {result.get('error', 'Unknown error')}")

    print()
    print("📊 Summary:")
    print(f"   Total: {len(document_ids)}")
    print(f"   Completed: {completed}")
    print(f"   Failed: {failed}")
    print(f"   Success Rate: {completed / len(document_ids) * 100:.1f}%")
    print()

    # Query final status of all workflows
    print("🔍 Final Status Check:")
    for doc_id, handle in handles:
        try:
            status = await handle.query(DocumentIngestionWorkflow.get_status)
            print(f"   {doc_id}: {status['status']}")
        except:
            print(f"   {doc_id}: Unable to query status")

    print()
    print("📊 View all workflows in Temporal UI: http://localhost:8088")
    print()


if __name__ == "__main__":
    asyncio.run(main())
