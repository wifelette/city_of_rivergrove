#!/bin/bash
# Quick fix for disappearing styles issue
# Run this when CSS styles aren't showing up

set -e

echo "🔧 Fixing CSS styles..."

# 1. Copy theme directory to book
echo "  Copying theme files..."
rm -rf book/theme 2>/dev/null || true
cp -r theme/css book/theme

# 2. Fix import path in custom.css if needed
echo "  Checking CSS import path..."
sed -i '' 's|@import url('\''./theme/css/main.css'\'')|@import url('\''./theme/main.css'\'')|g' book/custom.css 2>/dev/null || true
sed -i '' 's|@import url("./theme/css/main.css")|@import url("./theme/main.css")|g' book/custom.css 2>/dev/null || true

# 3. Run postprocessors to restore HTML structure
echo "  Running custom list processor..."
python3 scripts/postprocessing/custom-list-processor.py >/dev/null

echo "  Running enhanced processor..."
python3 scripts/postprocessing/enhanced-custom-processor.py >/dev/null

echo "✅ Styles fixed! Refresh your browser."
echo ""
echo "💡 Tip: Use ./dev-server.sh instead of 'mdbook serve' to prevent this issue"