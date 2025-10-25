#!/bin/bash
# Section 5: Hello World Validation - Test Runner
# Run all 10 Hello World tests with proper PYTHONPATH

cd /Users/richardglaubitz/Projects/apex-memory-system

echo "Running Section 5: Hello World Validation Tests..."
echo "=================================================="
echo ""

PYTHONPATH=/Users/richardglaubitz/Projects/apex-memory-system/src:$PYTHONPATH \
    python3 -m pytest \
    /Users/richardglaubitz/Projects/Apex-Memory-System-Development/upgrades/active/temporal-implementation/tests/section-5-hello-world/test_hello_world.py \
    -v

echo ""
echo "=================================================="
echo "Test Results:"
echo "  Note: Some tests require Temporal Server running"
echo ""
echo "To start Temporal Server:"
echo "  cd /Users/richardglaubitz/Projects/apex-memory-system/docker"
echo "  docker-compose -f temporal-compose.yml up -d"
echo ""
echo "To start worker (required for integration tests):"
echo "  python -m apex_memory.temporal.workers.dev_worker"
echo ""
echo "To test workflow manually:"
echo "  python scripts/test_hello_world.py"
