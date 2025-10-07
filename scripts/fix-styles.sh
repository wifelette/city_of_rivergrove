#!/bin/bash
# Quick fix for disappearing styles issue
# Run this when CSS styles aren't showing up

set -e

echo "🔧 Fixing CSS styles..."

# 1. Compile CSS from modular files
echo "  Compiling CSS..."
if ! ./scripts/build/compile-css.py; then
    echo "  ❌ ERROR: CSS compilation failed"
    exit 1
fi

# 3. Run postprocessors to restore HTML structure
echo "  Running enhanced unified list processor..."
./scripts/postprocessing/unified-list-processor.py >/dev/null

echo "  Running enhanced custom processor..."
./scripts/postprocessing/enhanced-custom-processor.py >/dev/null

echo "✅ Styles fixed! Refresh your browser."
echo ""
echo "💡 Tip: Use ./dev-server.sh instead of 'mdbook serve' to prevent this issue"