#!/bin/bash
# Ensure all Python scripts use system Python to avoid Homebrew dependency issues

echo "Checking and updating Python scripts to use system Python..."

# Find all Python files that use env python3
files=$(find scripts -name "*.py" -type f | xargs grep -l "^#!/usr/bin/env python3")

if [ -z "$files" ]; then
    echo "✓ All Python scripts already use system Python"
    exit 0
fi

echo "Found $(echo "$files" | wc -l | tr -d ' ') scripts using env python3"
echo "Updating to use system Python directly..."

for file in $files; do
    # Update the shebang
    sed -i '' 's|^#!/usr/bin/env python3|#!/usr/bin/python3|' "$file"
    echo "  Updated: $file"
done

echo ""
echo "✓ All Python scripts now use system Python (/usr/bin/python3)"
echo "This prevents issues when Homebrew updates Python and loses installed modules."