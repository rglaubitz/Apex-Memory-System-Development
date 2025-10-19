#!/usr/bin/env python3
"""
Quick script to run test workflows through dev_worker to populate metrics.

This script executes workflows on the apex-ingestion-queue (dev_worker's queue)
so that metrics are recorded in the dev_worker's Prometheus registry.

Usage:
    python3 run_test_workflow.py --count 5
"""

import asyncio
import argparse
import sys
import os
import boto3
from datetime import timedelta

# Add src to path
sys.path.insert(0, "/Users/richardglaubitz/Projects/apex-memory-system/src")

from temporalio.client import Client
from apex_memory.temporal.workflows.ingestion import DocumentIngestionWorkflow


async def upload_test_document(doc_id: str, bucket: str) -> str:
    """Upload a test document to S3."""
    s3_client = boto3.client(
        "s3",
        endpoint_url=os.getenv("S3_ENDPOINT_URL", None),
    )

    # Create bucket if needed
    try:
        s3_client.create_bucket(Bucket=bucket)
    except:
        pass

    content = f"""Test Document for Metrics Validation

This is a test document for Phase 2E metrics validation.
Document ID: {doc_id}

Test Entities:
- Test Company Alpha (customer)
- Equipment Unit #1001 (equipment)
- Driver John Smith (driver)

This document tests the complete ingestion pipeline with metrics recording.
"""

    s3_key = f"metrics-test/{doc_id}"
    s3_client.put_object(
        Bucket=bucket,
        Key=s3_key,
        Body=content.encode('utf-8'),
        Metadata={
            "source": "metrics-test",
            "document-id": doc_id,
        }
    )

    return s3_key


async def run_test_workflows(count: int = 5):
    """Run test workflows through dev_worker.

    Args:
        count: Number of workflows to execute (default: 5)
    """
    print(f"\n🚀 Running {count} test workflows through dev_worker...")
    print(f"   Task Queue: apex-ingestion-queue")
    print(f"   Metrics Endpoint: http://localhost:9091/metrics")
    print("")

    # Connect to Temporal
    client = await Client.connect("localhost:7233")

    bucket = os.getenv("APEX_DOCUMENTS_BUCKET", "apex-documents-test")

    # Upload test documents
    print("📤 Uploading test documents to S3...")
    for i in range(count):
        doc_id = f"metrics-test-doc-{i}.txt"
        await upload_test_document(doc_id, bucket)
        print(f"   ✅ Uploaded {doc_id}")

    # Execute workflows
    print(f"\n⚙️  Executing {count} workflows...")
    workflow_handles = []

    for i in range(count):
        doc_id = f"metrics-test-doc-{i}.txt"

        handle = await client.start_workflow(
            DocumentIngestionWorkflow.run,
            args=[doc_id, "metrics-test", bucket, "metrics-test"],
            id=f"metrics-test-{doc_id}",
            task_queue="apex-ingestion-queue",  # Dev worker's queue!
            execution_timeout=timedelta(minutes=5),
        )
        workflow_handles.append(handle)
        print(f"   ⏳ Started workflow: {handle.id}")

    # Wait for completion
    print(f"\n⏳ Waiting for workflows to complete...")
    results = []
    for handle in workflow_handles:
        try:
            result = await handle.result()
            results.append(result)
            print(f"   ✅ {handle.id}: {result.get('status')}")
        except Exception as e:
            print(f"   ❌ {handle.id}: {str(e)}")
            results.append({"status": "failed", "error": str(e)})

    await client.close()

    # Summary
    successful = sum(1 for r in results if r.get("status") == "success")
    failed = len(results) - successful

    print(f"\n📊 Results:")
    print(f"   Total: {len(results)}")
    print(f"   Successful: {successful}")
    print(f"   Failed: {failed}")
    print(f"\n✅ Metrics should now be populated at http://localhost:9091/metrics")
    print(f"   Check with: curl http://localhost:9091/metrics | grep apex_temporal")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run test workflows to populate metrics")
    parser.add_argument("--count", type=int, default=5, help="Number of workflows to run (default: 5)")
    args = parser.parse_args()

    asyncio.run(run_test_workflows(args.count))
