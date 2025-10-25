"""DocumentIngestionWorkflow with custom S3 configuration.

This example demonstrates:
- Passing custom S3 bucket
- Passing custom S3 key prefix
- Useful for multi-environment deployments (dev, staging, prod)

Prerequisites:
- Temporal server running on localhost:7233
- Worker running (python -m apex_memory.temporal.workers.dev_worker)
- Document in custom S3 location

Usage:
    python ingest-with-custom-config.py doc-123 samsara my-custom-bucket samsara/fleet/docs

Author: Apex Infrastructure Team
Created: 2025-10-18
"""

import asyncio
import sys
from temporalio.client import Client

sys.path.insert(0, "/Users/richardglaubitz/Projects/apex-memory-system/src")

from apex_memory.temporal.workflows.ingestion import DocumentIngestionWorkflow


async def main():
    """Execute workflow with custom S3 configuration."""

    if len(sys.argv) < 5:
        print("Usage: python ingest-with-custom-config.py <document_id> <source> <bucket> <prefix>")
        print("Example: python ingest-with-custom-config.py doc-123 samsara my-bucket samsara/fleet")
        sys.exit(1)

    document_id = sys.argv[1]
    source = sys.argv[2]
    bucket = sys.argv[3]
    prefix = sys.argv[4]

    print(f"\n🚀 Starting ingestion workflow with custom S3 config")
    print(f"   Document ID: {document_id}")
    print(f"   Source: {source}")
    print(f"   S3 Bucket: {bucket}")
    print(f"   S3 Prefix: {prefix}")
    print(f"   Full S3 path: s3://{bucket}/{prefix}/{document_id}")
    print()

    # Connect to Temporal
    client = await Client.connect("localhost:7233")

    try:
        # Execute workflow with custom S3 config
        result = await client.execute_workflow(
            DocumentIngestionWorkflow.run,
            document_id,
            source,
            bucket,  # Custom bucket
            prefix,  # Custom prefix
            id=f"ingest-{document_id}",
            task_queue="apex-ingestion-queue",
        )

        # Print result
        if result["status"] == "success":
            print("✅ Ingestion completed successfully!")
            print(f"   Document ID: {result['document_id']}")
            print(f"   Source: {result['source']}")
            print(f"   Databases written: {', '.join(result['databases_written'])}")
            print()
            print("💡 Tip: Custom S3 configurations are useful for:")
            print("   - Multi-environment deployments (dev, staging, prod)")
            print("   - Different storage tiers (hot, cold, archive)")
            print("   - Customer-specific buckets")
            print("   - Compliance requirements (regional storage)")
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
