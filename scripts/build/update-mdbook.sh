#!/bin/bash
# Sync all documents and rebuild mdBook

echo "🔄 Syncing documents to src/ folders..."

echo "  📄 Syncing ordinances..."
python3 scripts/preprocessing/sync-ordinances.py

echo "  📄 Syncing resolutions..."
python3 scripts/preprocessing/sync-resolutions.py

echo "  📄 Syncing interpretations..."
python3 scripts/preprocessing/sync-interpretations.py

echo "  📄 Syncing other documents..."
python3 scripts/preprocessing/sync-other.py

echo "  📝 Processing footnotes..."
python3 scripts/preprocessing/footnote-preprocessor.py
echo "  ✓ Footnotes processed"


echo "  🔗 Converting URLs and emails to links..."
python3 scripts/preprocessing/auto-link-converter.py src/ordinances/*.md src/resolutions/*.md src/interpretations/*.md src/other/*.md 2>/dev/null || true
echo "  ✓ Links converted"

echo "  📋 Regenerating SUMMARY.md..."
python3 scripts/mdbook/generate-summary.py
echo "  ✓ Table of contents updated"

echo "  🔗 Generating relationships.json..."
python3 scripts/mdbook/generate-relationships.py
echo "  ✓ Document relationships updated"

echo "  🔗 Syncing Airtable metadata..."
python3 scripts/mdbook/sync-airtable-metadata.py --mode=full --if-stale
# Copy metadata to src directory so it's served by mdBook
if [ -f "book/airtable-metadata.json" ]; then
    cp book/airtable-metadata.json src/
fi
echo "  ✓ Airtable metadata synced"

echo "📚 Rebuilding mdBook..."
mdbook build

echo "  🎨 Applying custom formatting..."
python3 scripts/postprocessing/custom-list-processor.py

# Apply enhanced formatting if available
if [ -f "scripts/postprocessing/enhanced-custom-processor.py" ]; then
    echo "  ✨ Applying enhanced document-specific formatting..."
    python3 scripts/postprocessing/enhanced-custom-processor.py
fi

echo "✅ Done! Your changes should now be visible at http://localhost:3000"
