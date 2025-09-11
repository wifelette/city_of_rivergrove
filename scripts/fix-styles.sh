#!/bin/bash
# Quick fix for disappearing styles issue
# Run this when CSS styles aren't showing up

set -e

echo "🔧 Fixing CSS styles..."

# 1. Copy theme directory to book (maintaining structure)
echo "  Copying theme files..."
rm -rf book/theme 2>/dev/null || true
cp -r theme book/

# 2. Verify CSS import path is correct (should be './theme/css/main.css')
echo "  Verifying CSS import path..."
# Fix any incorrect paths back to the correct one
sed -i '' 's|@import url('\''./theme/main.css'\'')|@import url('\''./theme/css/main.css'\'')|g' book/custom.css 2>/dev/null || true
sed -i '' 's|@import url("./theme/main.css")|@import url("./theme/css/main.css")|g' book/custom.css 2>/dev/null || true

# Verify the CSS file exists
if [ ! -f "book/theme/css/main.css" ]; then
    echo "  ❌ ERROR: CSS file not found at book/theme/css/main.css"
    exit 1
fi

# 3. Run postprocessors to restore HTML structure
echo "  Running custom list processor..."
python3 scripts/postprocessing/custom-list-processor.py >/dev/null

echo "  Running enhanced processor..."
python3 scripts/postprocessing/enhanced-custom-processor.py >/dev/null

echo "✅ Styles fixed! Refresh your browser."
echo ""
echo "💡 Tip: Use ./dev-server.sh instead of 'mdbook serve' to prevent this issue"