#!/bin/bash
# Comprehensive test suite for CSS build pipeline
# Tests that CSS files are correctly copied and accessible after builds

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test results
TESTS_PASSED=0
TESTS_FAILED=0
FAILED_TESTS=()

# Test function
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    echo -n "  Testing: $test_name... "
    
    if eval "$test_command" >/dev/null 2>&1; then
        echo -e "${GREEN}✓${NC}"
        ((TESTS_PASSED++))
        return 0
    else
        echo -e "${RED}✗${NC}"
        ((TESTS_FAILED++))
        FAILED_TESTS+=("$test_name")
        return 1
    fi
}

echo -e "${BLUE}🧪 CSS Build Pipeline Test Suite${NC}"
echo "=================================="
echo ""

# Test 1: Check if theme source directory exists
echo "1️⃣  Testing source files..."
run_test "theme directory exists" "[ -d theme ]"
run_test "theme/css directory exists" "[ -d theme/css ]"
run_test "main.css exists" "[ -f theme/css/main.css ]"
run_test "CSS modules exist" "[ -f theme/css/base/variables.css ]"
# CRITICAL: Check that the SOURCE custom.css has the correct import path
run_test "source custom.css has correct path" "grep -q \"@import url('./theme/css/main.css')\" custom.css"
echo ""

# Test 2: Test mdBook build and theme copy
echo "2️⃣  Testing mdBook build process..."
echo "  Running mdBook build..."
mdbook build >/dev/null 2>&1

run_test "book directory created" "[ -d book ]"
run_test "custom.css created" "[ -f book/custom.css ]"
run_test "theme NOT auto-copied by mdBook" "[ ! -d book/theme ]"

echo "  Copying theme manually..."
cp -r theme book/ 2>/dev/null

run_test "theme copied successfully" "[ -d book/theme ]"
run_test "CSS files accessible" "[ -f book/theme/css/main.css ]"
echo ""

# Test 3: Verify CSS import path
echo "3️⃣  Testing CSS import paths..."
if grep -q "@import url('./theme/css/main.css')" book/custom.css 2>/dev/null; then
    run_test "correct import path in custom.css" "true"
else
    run_test "correct import path in custom.css" "false"
fi

# Test if CSS actually loads (check if file is accessible via relative path)
if [ -f "book/theme/css/main.css" ]; then
    # From book/custom.css, the path ./theme/css/main.css should resolve
    cd book 2>/dev/null
    run_test "CSS path resolves correctly" "[ -f ./theme/css/main.css ]"
    cd .. 2>/dev/null
else
    run_test "CSS path resolves correctly" "false"
fi
echo ""

# Test 4: Test fix-styles.sh script
echo "4️⃣  Testing fix-styles.sh script..."
# First, remove theme to simulate the problem
rm -rf book/theme 2>/dev/null || true

run_test "theme removed for testing" "[ ! -d book/theme ]"

# Run fix script
./scripts/fix-styles.sh >/dev/null 2>&1

run_test "fix-styles.sh restores theme" "[ -d book/theme ]"
run_test "fix-styles.sh preserves correct path" "grep -q \"@import url('./theme/css/main.css')\" book/custom.css"
run_test "CSS files accessible after fix" "[ -f book/theme/css/main.css ]"
echo ""

# Test 5: Test validation scripts
echo "5️⃣  Testing validation scripts..."
run_test "check-src-modifications.sh exists" "[ -f scripts/validation/check-src-modifications.sh ]"
run_test "check-src-modifications.sh is executable" "[ -x scripts/validation/check-src-modifications.sh ]"
run_test "src validation passes" "./scripts/validation/check-src-modifications.sh"
echo ""

# Test 6: Test build scripts have CSS checks
echo "6️⃣  Testing build script safeguards..."
run_test "build-all.sh has CSS verification" "grep -q 'book/theme/css/main.css' build-all.sh"
run_test "dev-server.sh has CSS verification" "grep -q 'book/theme/css/main.css' dev-server.sh"
run_test "fix-styles.sh has CSS verification" "grep -q 'book/theme/css/main.css' scripts/fix-styles.sh"
echo ""

# Test 7: Test CSS module structure
echo "7️⃣  Testing CSS module structure..."
CSS_MODULES=(
    "base/variables.css"
    "base/typography.css"
    "layout/mdbook-overrides.css"
    "layout/page-structure.css"
    "components/form-fields.css"
    "documents/document-notes.css"
)

for module in "${CSS_MODULES[@]}"; do
    run_test "module: $module" "[ -f theme/css/$module ]"
done
echo ""

# Test 8: Test postprocessors can run
echo "8️⃣  Testing postprocessors..."
run_test "custom-list-processor exists" "[ -f scripts/postprocessing/custom-list-processor.py ]"
run_test "enhanced-custom-processor exists" "[ -f scripts/postprocessing/enhanced-custom-processor.py ]"

# Ensure theme is in place before running postprocessors
cp -r theme book/ 2>/dev/null || true

run_test "custom-list-processor runs" "python3 scripts/postprocessing/custom-list-processor.py"
run_test "enhanced-custom-processor runs" "python3 scripts/postprocessing/enhanced-custom-processor.py"
echo ""

# Summary
echo "=================================="
echo -e "${BLUE}📊 Test Summary${NC}"
echo "=================================="
echo -e "Tests Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Tests Failed: ${RED}$TESTS_FAILED${NC}"

if [ ${#FAILED_TESTS[@]} -gt 0 ]; then
    echo ""
    echo -e "${RED}Failed Tests:${NC}"
    for test in "${FAILED_TESTS[@]}"; do
        echo "  • $test"
    done
    echo ""
    echo -e "${YELLOW}⚠️  Some tests failed. Run with -v for verbose output.${NC}"
    exit 1
else
    echo ""
    echo -e "${GREEN}✅ All CSS pipeline tests passed!${NC}"
    echo ""
    echo "The CSS build pipeline is working correctly:"
    echo "  • Source files are in place"
    echo "  • Build process copies theme correctly"
    echo "  • Import paths are correct"
    echo "  • Recovery scripts work"
    echo "  • Validation is in place"
fi