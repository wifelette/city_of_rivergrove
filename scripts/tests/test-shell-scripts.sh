#!/bin/bash
# Test that shell scripts call Python scripts directly (not via python3 interpreter)

echo "Testing shell script configurations..."
echo "======================================"

EXIT_CODE=0

# Check that shell scripts call scripts directly (./scripts/...) not via python3
echo "1. Checking shell scripts for direct script calls..."
SHELL_SCRIPTS="build-all.sh dev-server.sh scripts/fix-styles.sh"

for script in $SHELL_SCRIPTS; do
    if [ -f "$script" ]; then
        # Look for old-style python3 calls (should be ./scripts/... instead)
        bad_calls=$(grep -n "python3 scripts/" "$script" | grep -v "^#" | head -5)
        if [ -n "$bad_calls" ]; then
            echo "   ✗ $script has old python3 calls (should use ./scripts/ directly):"
            echo "$bad_calls" | sed 's/^/       Line /'
            EXIT_CODE=1
        else
            echo "   ✓ $script calls scripts directly"
        fi
    else
        echo "   ⚠ $script not found"
    fi
done

echo ""
echo "2. Checking for old mdbook serve processes..."
# Check for stale mdbook processes that might interfere
old_mdbook=$(ps aux | grep "mdbook serve" | grep -v grep | grep -v dev-server)
if [ -n "$old_mdbook" ]; then
    echo "   ⚠ Found old mdbook serve processes:"
    echo "$old_mdbook" | awk '{print "      PID " $2 " started " $9}'
    echo "   Run 'pkill -f mdbook' to clean up"
else
    echo "   ✓ No stale mdbook processes found"
fi

echo ""
echo "3. Testing git hooks..."
# Check that pre-commit hook exists and blocks mdbook serve
if [ -f ".git/hooks/pre-commit" ]; then
    if grep -q "mdbook serve" .git/hooks/pre-commit; then
        echo "   ✓ Pre-commit hook checks for mdbook serve"
    else
        echo "   ⚠ Pre-commit hook doesn't check for mdbook serve"
    fi
else
    echo "   ⚠ No pre-commit hook found"
fi

echo ""
echo "======================================"
if [ $EXIT_CODE -eq 0 ]; then
    echo "✓ All shell script tests passed!"
else
    echo "✗ Some tests failed - see above for details"
fi
exit $EXIT_CODE