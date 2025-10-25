#!/bin/bash
# Section 7: Ingestion Activities - Test Runner
# Run all 20 ingestion activity tests with proper PYTHONPATH

cd /Users/richardglaubitz/Projects/apex-memory-system

echo "Running Section 7: Ingestion Activities Tests..."
echo "=================================================="
echo ""

PYTHONPATH=/Users/richardglaubitz/Projects/apex-memory-system/src:$PYTHONPATH \
    python3 -m pytest \
    /Users/richardglaubitz/Projects/Apex-Memory-System-Development/upgrades/active/temporal-implementation/tests/section-7-ingestion-activities/test_ingestion_activities.py \
    -v

echo ""
echo "=================================================="
echo "Test Results:"
echo "  Expected: 20 tests (19 passing, 1 skipped)"
echo "  - Parse Activity: 5 tests"
echo "  - Extract Entities: 4 tests"
echo "  - Generate Embeddings: 4 tests"
echo "  - Write Databases: 7 tests (1 integration test skipped)"
echo ""
echo "Note: Integration test skipped unless databases configured"
echo ""
echo "To run Enhanced Saga tests (verify 121 tests still pass):"
echo "  pytest tests/ -k 'saga or database_writer' -v"
echo ""
echo "To run activities manually:"
echo "  python examples/section-7/parse-document-standalone.py /path/to/doc.pdf"
echo "  python examples/section-7/write-databases-with-saga.py"
