#!/bin/bash
# Test that Python scripts use env Python (which respects PATH) and have required dependencies

echo "Testing Python configuration..."
echo "=============================="

# Check that scripts use env Python (not hardcoded paths)
echo "1. Checking script shebangs..."
bad_scripts=$(find scripts -name "*.py" -type f | xargs grep -l "^#!/usr/bin/python3")
if [ -z "$bad_scripts" ]; then
    echo "   ✓ All scripts use #!/usr/bin/env python3"
else
    echo "   ✗ These scripts still use hardcoded /usr/bin/python3:"
    echo "$bad_scripts" | sed 's/^/     /'
    exit 1
fi

# Check that Python (from PATH) has required modules
echo ""
echo "2. Checking Python dependencies (using PATH)..."
python3 -c "import bs4" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "   ✓ BeautifulSoup4 is installed"
else
    echo "   ✗ BeautifulSoup4 is missing"
    exit 1
fi

python3 -c "import dotenv" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "   ✓ python-dotenv is installed"
else
    echo "   ✗ python-dotenv is missing"
    exit 1
fi

# Test that the main processor works
echo ""
echo "3. Testing main list processor..."
test_file="book/ordinances/1989-Ord-54-89C-Land-Development.html"
if [ -f "$test_file" ]; then
    ./scripts/postprocessing/unified-list-processor.py "$test_file" >/dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "   ✓ List processor runs successfully"
    else
        echo "   ✗ List processor failed to run"
        exit 1
    fi
else
    echo "   ⚠ Test file not found (build may be needed)"
fi

echo ""
echo "=============================="
echo "✓ All Python configuration tests passed!"