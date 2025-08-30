#!/bin/bash
# Build script for Rivergrove mdBook site
# This script assumes documents are already synced to /src and processes them for mdBook

echo "🔗 Converting URLs and emails to links..."
python3 scripts/preprocessing/auto-link-converter.py src/ordinances/*.md src/resolutions/*.md src/interpretations/*.md src/other/*.md 2>/dev/null || true

echo "🔗 Adding cross-reference links..."
python3 scripts/mdbook/add-cross-references.py

echo "📚 Building mdBook..."
mdbook build

echo "🎨 Applying custom formatting..."
python3 scripts/postprocessing/custom-list-processor.py

# Apply enhanced formatting if available
if [ -f "scripts/postprocessing/enhanced-custom-processor.py" ]; then
    echo "✨ Applying enhanced document-specific formatting..."
    python3 scripts/postprocessing/enhanced-custom-processor.py
fi

echo "✅ Build complete!"