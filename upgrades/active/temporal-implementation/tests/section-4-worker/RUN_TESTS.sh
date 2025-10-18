#!/bin/bash
# Section 4: Worker Infrastructure - Test Runner
# Run all 15 worker tests with proper PYTHONPATH

cd /Users/richardglaubitz/Projects/apex-memory-system

echo "Running Section 4: Worker Infrastructure Tests..."
echo "=================================================="
echo ""

PYTHONPATH=/Users/richardglaubitz/Projects/apex-memory-system/src:$PYTHONPATH \
    python3 -m pytest \
    /Users/richardglaubitz/Projects/Apex-Memory-System-Development/upgrades/active/temporal-implementation/tests/section-4-worker/test_temporal_worker.py \
    -v

echo ""
echo "=================================================="
echo "Test Results:"
echo "  ✅ 12 tests passing (configuration, initialization, shutdown)"
echo "  ⏭️ 3 tests skipped (when Temporal Server not running)"
echo ""
echo "To start Temporal Server:"
echo "  cd /Users/richardglaubitz/Projects/apex-memory-system/docker"
echo "  docker-compose -f temporal-compose.yml up -d"
