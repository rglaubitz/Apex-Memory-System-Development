"""Parse Document Activity - Standalone Example.

This example demonstrates how to test the parse_document_activity
in isolation without running a full workflow.

The activity wraps the existing DocumentParser service (which uses Docling)
and makes it available for Temporal workflows.

Prerequisites:
    1. Document file to parse (PDF, DOCX, PPTX, TXT, or Markdown)

Usage:
    python examples/section-7/parse-document-standalone.py /path/to/document.pdf

Author: Apex Infrastructure Team
Created: 2025-10-18
"""

import asyncio
import sys
import json
from pathlib import Path

# Add src to path for local testing
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "apex-memory-system" / "src"))

from apex_memory.temporal.activities.ingestion import parse_document_activity


async def main():
    """Execute parse_document_activity standalone."""

    # Get file path from command line or use default
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        # Use a test file
        file_path = "/tmp/test-document.txt"

        # Create test file if it doesn't exist
        test_file = Path(file_path)
        if not test_file.exists():
            test_file.parent.mkdir(parents=True, exist_ok=True)
            test_file.write_text(
                "This is a test document for parsing.\n\n"
                "It contains multiple paragraphs to demonstrate chunking.\n\n"
                "The DocumentParser uses Docling when available, "
                "with fallbacks to format-specific parsers."
            )
            print(f"Created test file: {file_path}")

    print(f"\n{'=' * 70}")
    print(f"Parse Document Activity - Standalone Execution")
    print(f"{'=' * 70}\n")

    print(f"File to parse: {file_path}")

    # Check file exists
    if not Path(file_path).exists():
        print(f"\n❌ Error: File not found: {file_path}")
        print("\nUsage: python examples/section-7/parse-document-standalone.py <file-path>")
        return

    print(f"\nExecuting parse_document_activity...\n")

    try:
        # Execute the activity
        result = await parse_document_activity(file_path)

        print(f"✅ Parsing successful!\n")

        # Display results
        print(f"Document UUID: {result['uuid']}")
        print(f"Content length: {len(result['content'])} characters")
        print(f"Number of chunks: {len(result['chunks'])}")

        print(f"\nMetadata:")
        for key, value in result['metadata'].items():
            print(f"  {key}: {value}")

        print(f"\nContent preview (first 200 chars):")
        print(f"  {result['content'][:200]}...")

        print(f"\nChunks preview:")
        for i, chunk in enumerate(result['chunks'][:3], 1):
            print(f"  Chunk {i}: {chunk[:100]}...")

        if len(result['chunks']) > 3:
            print(f"  ... and {len(result['chunks']) - 3} more chunks")

        # Save result to JSON for inspection
        output_file = Path("/tmp/parse_result.json")
        with open(output_file, "w") as f:
            json.dump(result, f, indent=2, default=str)

        print(f"\n📄 Full result saved to: {output_file}")

    except Exception as e:
        print(f"\n❌ Parsing failed: {str(e)}")
        import traceback
        traceback.print_exc()

    print(f"\n{'=' * 70}\n")


if __name__ == "__main__":
    asyncio.run(main())
