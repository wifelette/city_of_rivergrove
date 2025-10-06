#!/bin/bash
# Test that shell scripts use correct Python paths

echo "Testing shell script configurations..."
echo "======================================"

EXIT_CODE=0

# Check that shell scripts use /usr/bin/python3 not just python3
echo "1. Checking shell scripts for Python calls..."
SHELL_SCRIPTS="build-all.sh dev-server.sh scripts/fix-styles.sh"

for script in $SHELL_SCRIPTS; do
    if [ -f "$script" ]; then
        # Look for python3 calls that don't use full path
        bad_calls=$(grep -n "python3 " "$script" | grep -v "/usr/bin/python3" | grep -v "^#" | head -5)
        if [ -n "$bad_calls" ]; then
            echo "   ✗ $script has unqualified python3 calls:"
            echo "$bad_calls" | sed 's/^/       Line /'
            EXIT_CODE=1
        else
            echo "   ✓ $script uses /usr/bin/python3 correctly"
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