#!/bin/bash
# Automatically test list formatting when list-related files are changed
#
# This script should be run:
# 1. Manually after changing list processors
# 2. As part of CI/CD pipeline
# 3. As a git pre-commit hook (optional)
#
# Usage:
#   ./scripts/validation/test-list-changes.sh        # Test all changes
#   ./scripts/validation/test-list-changes.sh --all  # Test all files
#   ./scripts/validation/test-list-changes.sh FILE   # Test specific file

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔍 List Formatting Regression Tests${NC}"
echo "=================================="

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Not in a git repository, testing all files${NC}"
    TEST_ALL=true
else
    # Check for changes to list-related files
    LIST_RELATED_FILES=$(git diff --name-only HEAD 2>/dev/null | grep -E "(list|List)" || true)
    LIST_PROCESSORS=$(git diff --name-only HEAD 2>/dev/null | grep -E "scripts/postprocessing.*\.py" || true)

    if [ -n "$LIST_PROCESSORS" ]; then
        echo -e "${YELLOW}📝 Detected changes to list processors:${NC}"
        echo "$LIST_PROCESSORS" | sed 's/^/    /'
        TEST_ALL=true
    elif [ -n "$LIST_RELATED_FILES" ]; then
        echo -e "${YELLOW}📝 Detected changes to list-related files:${NC}"
        echo "$LIST_RELATED_FILES" | sed 's/^/    /'
        TEST_ALL=true
    fi
fi

# Parse command line arguments
if [ "$1" = "--all" ]; then
    TEST_ALL=true
elif [ -n "$1" ]; then
    # Test specific file
    SPECIFIC_FILE="$1"
fi

# Determine what to test
if [ -n "$SPECIFIC_FILE" ]; then
    echo -e "${BLUE}Testing specific file: $SPECIFIC_FILE${NC}"
    TEST_FILES="$SPECIFIC_FILE"
elif [ "$TEST_ALL" = true ]; then
    echo -e "${BLUE}Testing all critical list formatting files${NC}"
    TEST_FILES=""  # Will use default in Python script
else
    # Check for recently built files
    RECENT_HTML=$(find book -name "*.html" -mmin -10 2>/dev/null | head -5)
    if [ -n "$RECENT_HTML" ]; then
        echo -e "${BLUE}Testing recently modified HTML files${NC}"
        TEST_FILES="$RECENT_HTML"
    else
        echo -e "${GREEN}✅ No list-related changes detected${NC}"
        exit 0
    fi
fi

# Run the Python test suite
echo ""
echo "Running test suite..."
echo "--------------------"

if [ -n "$TEST_FILES" ]; then
    python3 scripts/tests/test-list-formatting.py $TEST_FILES
else
    python3 scripts/tests/test-list-formatting.py
fi

TEST_RESULT=$?

# Check results
if [ $TEST_RESULT -eq 0 ]; then
    echo ""
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}✅ All list formatting tests passed!${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
else
    echo ""
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${RED}❌ List formatting tests failed!${NC}"
    echo ""
    echo "To fix:"
    echo "1. Review the failures above"
    echo "2. Check scripts/tests/list-test-results.json for details"
    echo "3. Run the list processor: python3 scripts/postprocessing/unified-list-processor-v2.py [file]"
    echo "4. Re-run tests: $0"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    exit 1
fi