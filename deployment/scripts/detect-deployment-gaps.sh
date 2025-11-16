#!/bin/bash
#
# Deployment Gap Detection Script
#
# Purpose: Scans codebase for implemented features not yet documented in deployment guides
#
# Usage:
#   cd /path/to/Apex-Memory-System-Development
#   chmod +x deployment/scripts/detect-deployment-gaps.sh
#   ./deployment/scripts/detect-deployment-gaps.sh
#
# Exit Codes:
#   0 - No gaps found (all features documented)
#   1 - Gaps detected (missing deployment documentation)
#   2 - Script error (missing dependencies, wrong directory, etc.)

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Deployment Gap Detection Script${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Verify we're in the right directory
if [[ ! -d "deployment" ]] || [[ ! -d "apex-memory-system" ]]; then
    echo -e "${RED}ERROR: Must run from Apex-Memory-System-Development root directory${NC}"
    exit 2
fi

echo -e "${YELLOW}Scanning codebase for implemented features...${NC}"
echo ""

# Change to main codebase
cd apex-memory-system || exit 2

# Initialize counters
GAPS_FOUND=0
FEATURES_SCANNED=0

# Function to check if feature is documented
check_feature_documented() {
    local feature_name=$1
    local component_path="../deployment/components/${feature_name}/DEPLOYMENT-GUIDE.md"

    if [[ -f "$component_path" ]]; then
        return 0  # Documented
    else
        return 1  # Not documented
    fi
}

# Function to check if feature is referenced in main deployment plans
check_feature_referenced() {
    local feature_keyword=$1
    local needs_file="../deployment/DEPLOYMENT-NEEDS.md"
    local plan_file="../deployment/PRODUCTION-DEPLOYMENT-PLAN.md"

    if grep -qi "$feature_keyword" "$needs_file" "$plan_file" 2>/dev/null; then
        return 0  # Referenced
    else
        return 1  # Not referenced
    fi
}

echo -e "${BLUE}1. Checking Temporal Workflows...${NC}"
FEATURES_SCANNED=$((FEATURES_SCANNED + 1))

# Find all workflow files
WORKFLOW_FILES=$(find src/apex_memory/temporal/workflows -name "*.py" -type f 2>/dev/null | grep -v __pycache__ || true)

for workflow_file in $WORKFLOW_FILES; do
    workflow_name=$(basename "$workflow_file" .py | sed 's/_/ /g' | awk '{for(i=1;i<=NF;i++) $i=toupper(substr($i,1,1)) tolower(substr($i,2));}1')

    # Skip if "dev" or "test" in name
    if echo "$workflow_file" | grep -qiE "dev|test"; then
        continue
    fi

    # Extract class names (workflow definitions)
    WORKFLOWS=$(grep -E "^class.*Workflow" "$workflow_file" 2>/dev/null | awk '{print $2}' | sed 's/(.*//' || true)

    for workflow_class in $WORKFLOWS; do
        # Convert CamelCase to kebab-case for component path
        workflow_slug=$(echo "$workflow_class" | sed 's/Workflow$//' | sed 's/\([A-Z]\)/-\1/g' | sed 's/^-//' | tr '[:upper:]' '[:lower:]')

        # Check if documented
        if ! check_feature_documented "$workflow_slug"; then
            # Check if at least referenced in deployment plans
            if ! check_feature_referenced "$workflow_class"; then
                echo -e "  ${RED}✗ Missing: $workflow_class (from $workflow_file)${NC}"
                echo -e "    ${YELLOW}Expected: deployment/components/${workflow_slug}/DEPLOYMENT-GUIDE.md${NC}"
                GAPS_FOUND=$((GAPS_FOUND + 1))
            else
                echo -e "  ${YELLOW}⚠ Partially documented: $workflow_class (referenced but no component guide)${NC}"
            fi
        else
            echo -e "  ${GREEN}✓ Documented: $workflow_class${NC}"
        fi
    done
done

echo ""
echo -e "${BLUE}2. Checking API Endpoints (FastAPI routes)...${NC}"
FEATURES_SCANNED=$((FEATURES_SCANNED + 1))

# Find all API router files
API_FILES=$(find src/apex_memory/api -name "*.py" -type f 2>/dev/null | grep -v __pycache__ | grep -v __init__ || true)

for api_file in $API_FILES; do
    api_name=$(basename "$api_file" .py)

    # Skip main.py and generic files
    if [[ "$api_name" == "main" ]] || [[ "$api_name" == "dependencies" ]]; then
        continue
    fi

    # Convert to component path
    api_slug=$(echo "$api_name" | tr '_' '-')

    # Check if documented
    if ! check_feature_documented "$api_slug"; then
        # Check if at least referenced
        api_keyword=$(echo "$api_name" | sed 's/_/ /g')
        if ! check_feature_referenced "$api_keyword"; then
            # Only report if file has actual endpoints (router = APIRouter())
            if grep -q "router = APIRouter" "$api_file" 2>/dev/null; then
                echo -e "  ${RED}✗ Missing: $api_name API (from $api_file)${NC}"
                echo -e "    ${YELLOW}Expected: deployment/components/${api_slug}/DEPLOYMENT-GUIDE.md${NC}"
                GAPS_FOUND=$((GAPS_FOUND + 1))
            fi
        fi
    else
        echo -e "  ${GREEN}✓ Documented: $api_name API${NC}"
    fi
done

echo ""
echo -e "${BLUE}3. Checking Database Models (Alembic migrations)...${NC}"
FEATURES_SCANNED=$((FEATURES_SCANNED + 1))

# Find all migration files
MIGRATION_FILES=$(find alembic/versions -name "*.py" -type f 2>/dev/null | grep -v __pycache__ || true)

for migration_file in $MIGRATION_FILES; do
    # Extract table names from migration
    TABLES=$(grep -oE "create_table\(['\"]([^'\"]+)['\"]" "$migration_file" 2>/dev/null | sed "s/create_table(['\"]//;s/['\"].*//" || true)

    for table in $TABLES; do
        # Skip known infrastructure tables
        if echo "$table" | grep -qiE "alembic|version"; then
            continue
        fi

        # Convert table name to feature slug
        table_slug=$(echo "$table" | tr '_' '-')

        # Check if table has corresponding feature documentation
        if ! check_feature_documented "$table_slug"; then
            # Only report if table not mentioned anywhere in deployment docs
            if ! check_feature_referenced "$table"; then
                echo -e "  ${YELLOW}⚠ Table possibly undocumented: $table (migration: $(basename $migration_file))${NC}"
                # Don't increment GAPS_FOUND - tables are often implementation details
            fi
        fi
    done
done

echo ""
echo -e "${BLUE}4. Checking Environment Variables (.env.example)...${NC}"
FEATURES_SCANNED=$((FEATURES_SCANNED + 1))

if [[ -f ".env.example" ]]; then
    # Extract all env vars (lines starting with uppercase, containing =)
    ENV_VARS=$(grep -E '^[A-Z_]+=' .env.example 2>/dev/null | cut -d= -f1 || true)

    for env_var in $ENV_VARS; do
        # Skip infrastructure vars
        if echo "$env_var" | grep -qiE "DATABASE_URL|REDIS_URL|NEO4J|POSTGRES|OPENAI|ANTHROPIC|TEMPORAL"; then
            continue
        fi

        # Check if env var documented in DEPLOYMENT-NEEDS.md or component guides
        if ! grep -r "$env_var" ../deployment/components/ ../deployment/DEPLOYMENT-NEEDS.md ../deployment/production/GCP-DEPLOYMENT-GUIDE.md &>/dev/null; then
            echo -e "  ${YELLOW}⚠ Possibly undocumented env var: $env_var${NC}"
        fi
    done
fi

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Scan Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "Features scanned: ${FEATURES_SCANNED}"
echo -e "Documentation gaps found: ${RED}${GAPS_FOUND}${NC}"
echo ""

if [[ $GAPS_FOUND -eq 0 ]]; then
    echo -e "${GREEN}✓ No deployment gaps detected!${NC}"
    echo -e "${GREEN}All implemented features appear to be documented.${NC}"
    exit 0
else
    echo -e "${RED}✗ Deployment gaps detected!${NC}"
    echo ""
    echo -e "${YELLOW}Recommended Actions:${NC}"
    echo -e "  1. Review each missing feature above"
    echo -e "  2. For each gap, run: cp deployment/INTEGRATION-CHECKLIST-TEMPLATE.md deployment/components/<feature-name>/INTEGRATION-CHECKLIST.md"
    echo -e "  3. Complete all 6 phases of integration checklist"
    echo -e "  4. Re-run this script to verify gaps resolved"
    echo ""
    exit 1
fi
