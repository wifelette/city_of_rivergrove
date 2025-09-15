#!/bin/bash
#
# Run All Validation Checks
# Comprehensive validation suite for the City of Rivergrove repository
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔍 Running all validation checks...${NC}\n"

# Track overall status
ALL_PASSED=true

# 1. Form Field Validation
echo -e "${BLUE}1. Checking form fields...${NC}"
if python3 scripts/validation/validate-form-fields.py src/; then
    echo -e "${GREEN}  ✓ Form fields valid${NC}\n"
else
    echo -e "${RED}  ✗ Form field issues found${NC}\n"
    ALL_PASSED=false
fi

# 2. List Nesting Validation
echo -e "${BLUE}2. Checking list nesting...${NC}"
if python3 scripts/validation/check-list-nesting.py src/; then
    echo -e "${GREEN}  ✓ List nesting correct${NC}\n"
else
    echo -e "${RED}  ✗ List nesting issues found${NC}\n"
    ALL_PASSED=false
fi

# 3. Style Health Check
echo -e "${BLUE}3. Checking CSS health...${NC}"
if python3 scripts/validation/check-styles-health.py; then
    echo -e "${GREEN}  ✓ Styles healthy${NC}\n"
else
    echo -e "${YELLOW}  ⚠ Style issues detected${NC}\n"
    # Don't fail the build for style issues
fi

# 4. Tooltip Style Check (if signature marks exist)
echo -e "${BLUE}4. Checking tooltip styles...${NC}"
if python3 scripts/validation/check-tooltip-styles.py 2>/dev/null; then
    echo -e "${GREEN}  ✓ Tooltip styles correct${NC}\n"
else
    echo -e "${YELLOW}  ⚠ Tooltip style issues${NC}\n"
    # Don't fail for tooltip issues
fi

# Summary
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
if [ "$ALL_PASSED" = true ]; then
    echo -e "${GREEN}✅ All critical validations passed!${NC}"
    exit 0
else
    echo -e "${RED}❌ Some validations failed. Please fix the issues above.${NC}"
    exit 1
fi