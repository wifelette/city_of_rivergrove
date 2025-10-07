#!/bin/bash
# Comprehensive test suite for CSS build pipeline
# Tests that CSS files are correctly copied and accessible after builds

# Note: NOT using 'set -e' because we want to collect all test failures
# and report them at the end, not exit on first failure

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
# CRITICAL: Check that custom.css is compiled (not an import file)
run_test "custom.css is compiled" "grep -q \"COMPILED CSS\" custom.css"
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

# Test 3: Verify CSS compilation persists through build
echo "3️⃣  Testing compiled CSS..."
run_test "compiled CSS preserved in book/" "grep -q \"COMPILED CSS\" book/custom.css"
run_test "compiled CSS has content" "[ \$(wc -l < book/custom.css) -gt 100 ]"
echo ""

# Test 4: Test fix-styles.sh script
echo "4️⃣  Testing fix-styles.sh script..."
# First, remove theme to simulate the problem
rm -rf book/theme 2>/dev/null || true

run_test "theme removed for testing" "[ ! -d book/theme ]"

# Run fix script
./scripts/fix-styles.sh >/dev/null 2>&1

run_test "fix-styles.sh compiles CSS" "grep -q \"COMPILED CSS\" custom.css"
run_test "CSS files accessible after fix" "[ -f custom.css ]"
echo ""

# Test 5: Test validation scripts
echo "5️⃣  Testing validation scripts..."
run_test "check-src-modifications.sh exists" "[ -f scripts/validation/check-src-modifications.sh ]"
run_test "check-src-modifications.sh is executable" "[ -x scripts/validation/check-src-modifications.sh ]"
run_test "src validation passes" "./scripts/validation/check-src-modifications.sh"
echo ""

# Test 6: Test build scripts have CSS compilation
echo "6️⃣  Testing build script CSS compilation..."
run_test "build-all.sh compiles CSS" "grep -q 'compile-css.py' build-all.sh"
run_test "dev-server.sh exists" "[ -f dev-server.sh ]"
run_test "fix-styles.sh compiles CSS" "grep -q 'compile-css.py' scripts/fix-styles.sh"
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

# Test 8: Test CSS compilation script
echo "8️⃣  Testing CSS compilation..."
run_test "compile-css.py exists" "[ -f scripts/build/compile-css.py ]"
run_test "compile-css.py is executable" "[ -x scripts/build/compile-css.py ]"
run_test "compile-css.py runs" "./scripts/build/compile-css.py"
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
    echo "  • CSS source modules are in place"
    echo "  • CSS compilation works"
    echo "  • Compiled CSS persists through builds"
    echo "  • Recovery scripts work"
    echo "  • Validation is in place"
fi