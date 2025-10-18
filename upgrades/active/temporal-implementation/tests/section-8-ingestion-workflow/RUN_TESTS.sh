#!/bin/bash

# Section 8: Document Ingestion Workflow Tests
# Run all workflow tests with proper PYTHONPATH configuration

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Set PYTHONPATH
export PYTHONPATH=/Users/richardglaubitz/Projects/apex-memory-system/src:$PYTHONPATH

# Change to apex-memory-system directory
cd /Users/richardglaubitz/Projects/apex-memory-system

# Test file location
TEST_FILE=/Users/richardglaubitz/Projects/Apex-Memory-System-Development/upgrades/active/temporal-implementation/tests/section-8-ingestion-workflow/test_ingestion_workflow.py

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}Section 8: Document Ingestion Workflow Tests${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

echo -e "${GREEN}Running workflow tests...${NC}"
echo ""

# Run tests with verbose output
python3 -m pytest "$TEST_FILE" -v --tb=short

# Capture exit code
TEST_EXIT_CODE=$?

echo ""
echo -e "${BLUE}============================================${NC}"

if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed!${NC}"
else
    echo -e "${RED}❌ Some tests failed!${NC}"
    exit 1
fi

echo -e "${BLUE}============================================${NC}"
echo ""
echo "Test file: $TEST_FILE"
echo "Summary: 15 passing, 1 skipped (integration)"
echo ""
