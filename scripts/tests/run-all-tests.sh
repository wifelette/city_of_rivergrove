#!/bin/bash
# Run all test suites for the City of Rivergrove project

echo "🧪 Running all tests for City of Rivergrove"
echo "==========================================="
echo ""

TOTAL_FAILURES=0

# Test 1: Python configuration
echo "📐 Test Suite 1: Python Configuration"
echo "-------------------------------------"
if ./scripts/tests/test-python-path.sh; then
    echo ""
else
    ((TOTAL_FAILURES++))
    echo ""
fi

# Test 2: Shell scripts
echo "📐 Test Suite 2: Shell Scripts"
echo "------------------------------"
if ./scripts/tests/test-shell-scripts.sh; then
    echo ""
else
    ((TOTAL_FAILURES++))
    echo ""
fi

# Test 3: List formatting (if build exists)
echo "📐 Test Suite 3: List Formatting"
echo "--------------------------------"
if [ -f "book/ordinances/1989-Ord-54-89C-Land-Development.html" ]; then
    if /usr/bin/python3 scripts/tests/test-list-formatting.py book/ordinances/1989-Ord-54-89C-Land-Development.html 2>&1; then
        echo "✓ List formatting tests passed"
    else
        echo "⚠ Some list formatting tests failed (may include false positives)"
        ((TOTAL_FAILURES++))
    fi
else
    echo "⏭ Skipped - build needed first"
fi
echo ""

# Test 4: Form field validation
echo "📐 Test Suite 4: Form Field Validation"
echo "--------------------------------------"
if /usr/bin/python3 scripts/validation/validate-form-fields.py --quiet; then
    echo "✓ All form fields valid"
else
    echo "✗ Form field errors found"
    echo "  Run '/usr/bin/python3 scripts/validation/validate-form-fields.py' for details"
    ((TOTAL_FAILURES++))
fi
echo ""

# Test 5: Check for HTML in source files
echo "📐 Test Suite 5: Source File Validation"
echo "---------------------------------------"
if /usr/bin/python3 scripts/validation/validate-no-html.py source-documents --quiet; then
    echo "✓ No HTML in source files"
else
    echo "✗ HTML found in source files"
    echo "  Run '/usr/bin/python3 scripts/validation/validate-no-html.py' for details"
    ((TOTAL_FAILURES++))
fi
echo ""

# Test 6: Server health check
echo "📐 Test Suite 6: Server Status"
echo "------------------------------"
if ./scripts/utils/check-server.sh; then
    echo ""
else
    echo "ℹ Server not running - start with ./dev-server.sh"
    echo ""
fi

# Summary
echo "==========================================="
if [ $TOTAL_FAILURES -eq 0 ]; then
    echo "✅ All test suites passed!"
else
    echo "⚠ $TOTAL_FAILURES test suite(s) had issues"
    echo "See details above for specific failures"
fi

exit $TOTAL_FAILURES