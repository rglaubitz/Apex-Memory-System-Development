#!/bin/bash
#
# Phase 2E: Metrics Validation - Test Execution Script
#
# Runs all Phase 2E metrics validation tests.
#

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "================================================================================"
echo "Phase 2E: Metrics Validation"
echo "================================================================================"
echo ""

# Check if API server is running
echo -e "${YELLOW}📋 Checking API server...${NC}"
if curl -s http://localhost:8000/metrics > /dev/null 2>&1; then
    echo -e "${GREEN}✅ API server is running on port 8000${NC}"
else
    echo -e "${RED}❌ API server is NOT running${NC}"
    echo ""
    echo "Please start the API server first:"
    echo "  cd apex-memory-system"
    echo "  python -m uvicorn apex_memory.main:app --reload --port 8000"
    echo ""
    exit 1
fi

# Check if Prometheus is running
echo -e "${YELLOW}📋 Checking Prometheus...${NC}"
if curl -s http://localhost:9090/-/healthy > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Prometheus is running on port 9090${NC}"
else
    echo -e "${YELLOW}⚠️  Prometheus is NOT running (optional for endpoint tests)${NC}"
fi

# Check if Grafana is running
echo -e "${YELLOW}📋 Checking Grafana...${NC}"
if curl -s http://localhost:3001/api/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Grafana is running on port 3001${NC}"
else
    echo -e "${YELLOW}⚠️  Grafana is NOT running (optional for endpoint tests)${NC}"
fi

echo ""
echo "================================================================================"
echo "Running Tests"
echo "================================================================================"
echo ""

# Run Test 1: Metrics Endpoint Validation
echo -e "${YELLOW}Running Test 1: Metrics Endpoint Validation${NC}"
python3 test_metrics_endpoint.py

echo ""
echo "================================================================================"
echo -e "${GREEN}✅ Phase 2E Tests COMPLETE${NC}"
echo "================================================================================"
echo ""
echo "Summary:"
echo "  - ✅ All 26 Temporal metrics are present in /metrics endpoint"
echo "  - ✅ All metrics have correct Prometheus types"
echo "  - ✅ All metrics have TYPE definitions"
echo ""
echo "Next Steps:"
echo "  1. Run Phase 2D tests to populate metrics with data"
echo "  2. Validate Prometheus scraping (test_prometheus_integration.py)"
echo "  3. Validate Grafana dashboard (test_grafana_dashboard.py)"
echo ""
