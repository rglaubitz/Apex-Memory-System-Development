"""DocumentIngestionWorkflow with comprehensive error handling.

This example demonstrates:
- Catching workflow errors
- Distinguishing between different error types
- Retry strategies
- Error reporting and logging

Prerequisites:
- Temporal server running on localhost:7233
- Worker running

Usage:
    python ingest-with-error-handling.py doc-not-exist frontapp

Author: Apex Infrastructure Team
Created: 2025-10-18
"""

import asyncio
import sys
from temporalio.client import Client
from temporalio.exceptions import WorkflowFailureError

sys.path.insert(0, "/Users/richardglaubitz/Projects/apex-memory-system/src")

from apex_memory.temporal.workflows.ingestion import DocumentIngestionWorkflow


async def main():
    """Execute workflow with comprehensive error handling."""

    if len(sys.argv) < 3:
        print("Usage: python ingest-with-error-handling.py <document_id> <source>")
        print("Example: python ingest-with-error-handling.py doc-404 frontapp")
        sys.exit(1)

    document_id = sys.argv[1]
    source = sys.argv[2]

    print(f"\n🚀 Starting ingestion workflow: {document_id}")
    print(f"   (This example demonstrates error handling)")
    print()

    # Connect to Temporal
    client = await Client.connect("localhost:7233")

    try:
        # Execute workflow
        result = await client.execute_workflow(
            DocumentIngestionWorkflow.run,
            document_id,
            source,
            id=f"ingest-error-demo-{document_id}",
            task_queue="apex-ingestion-queue",
        )

        # Workflow completed (may have succeeded or failed gracefully)
        if result["status"] == "success":
            print("✅ Ingestion completed successfully!")
            print(f"   Document ID: {result['document_id']}")
            print(f"   Databases written: {', '.join(result['databases_written'])}")

        elif result["status"] == "failed":
            print("⚠️  Ingestion failed (handled gracefully):")
            print(f"   Error: {result['error']}")
            print()

            # Analyze error type and provide guidance
            error_msg = result['error'].lower()

            if 'not found' in error_msg or '404' in error_msg:
                print("📋 Error Type: Document Not Found")
                print("   Possible causes:")
                print("   - Document doesn't exist in S3")
                print("   - Incorrect document ID")
                print("   - Wrong S3 bucket or prefix")
                print()
                print("   Recommended actions:")
                print("   - Verify document exists in S3")
                print("   - Check S3 bucket/prefix configuration")
                print("   - Review document upload process")

            elif 'validation' in error_msg:
                print("📋 Error Type: Validation Error")
                print("   Possible causes:")
                print("   - Invalid document metadata")
                print("   - Corrupted file")
                print("   - Invalid entity data")
                print()
                print("   Recommended actions:")
                print("   - Check document format")
                print("   - Verify metadata completeness")
                print("   - Re-upload document")

            elif 'unsupported' in error_msg:
                print("📋 Error Type: Unsupported Format")
                print("   Possible causes:")
                print("   - File format not supported (must be PDF, DOCX, PPTX, HTML, MD)")
                print("   - Corrupted file")
                print()
                print("   Recommended actions:")
                print("   - Convert to supported format")
                print("   - Check file integrity")

            elif 'database' in error_msg or 'saga' in error_msg:
                print("📋 Error Type: Database Write Error")
                print("   Possible causes:")
                print("   - Database temporarily unavailable")
                print("   - Network issues")
                print("   - Data validation failure")
                print()
                print("   Recommended actions:")
                print("   - Check database health")
                print("   - Review Enhanced Saga logs")
                print("   - Retry workflow after database recovery")

            elif 'openai' in error_msg or 'embedding' in error_msg or 'rate limit' in error_msg:
                print("📋 Error Type: OpenAI API Error")
                print("   Possible causes:")
                print("   - Rate limit exceeded")
                print("   - API key invalid")
                print("   - Network timeout")
                print()
                print("   Recommended actions:")
                print("   - Wait and retry (workflow has automatic retries)")
                print("   - Check OpenAI API key")
                print("   - Verify API quota")

            else:
                print("📋 Error Type: Unknown")
                print("   Review workflow logs for details")

    except WorkflowFailureError as e:
        # Workflow failed catastrophically (shouldn't happen with our error handling)
        print("❌ Workflow failed catastrophically!")
        print(f"   Error: {str(e)}")
        print()
        print("   This indicates a workflow-level failure (not activity failure).")
        print("   Check Temporal UI for complete error details.")
        sys.exit(1)

    except Exception as e:
        # Client-level error
        print(f"❌ Client error: {str(e)}")
        print()
        print("   Possible causes:")
        print("   - Temporal server not running")
        print("   - Worker not running")
        print("   - Network connectivity issues")
        sys.exit(1)

    print()
    print("📊 View detailed error logs in Temporal UI: http://localhost:8088")
    print(f"   Workflow ID: ingest-error-demo-{document_id}")
    print()


if __name__ == "__main__":
    asyncio.run(main())
