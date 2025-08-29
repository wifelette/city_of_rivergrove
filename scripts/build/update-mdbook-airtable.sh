#!/bin/bash
# Enhanced mdBook build script with proper processing order and Airtable integration
# This script ensures custom formatting is preserved and Airtable data is properly integrated

echo "🔄 Enhanced mdBook Build with Airtable Integration"
echo "=================================================="

# Step 1: Sync documents to src/ folders
echo ""
echo "📁 Step 1: Syncing documents to src/ folders..."
echo "------------------------------------------------"

echo "  📄 Syncing ordinances..."
python3 scripts/preprocessing/sync-ordinances.py

echo "  📄 Syncing resolutions..."
python3 scripts/preprocessing/sync-resolutions.py

echo "  📄 Syncing interpretations..."
python3 scripts/preprocessing/sync-interpretations.py

echo "  📄 Syncing other documents..."
python3 scripts/preprocessing/sync-other.py

# Step 2: Pre-processing (standardization and conversion)
echo ""
echo "🔧 Step 2: Pre-processing documents..."
echo "------------------------------------------------"

echo "  📝 Processing footnotes..."
python3 scripts/preprocessing/footnote-preprocessor.py
echo "  ✓ Footnotes processed"

echo "  🔗 Converting URLs and emails to links..."
python3 scripts/preprocessing/auto-link-converter.py src/ordinances/*.md src/resolutions/*.md src/interpretations/*.md src/other/*.md 2>/dev/null || true
echo "  ✓ Links converted"

echo "  🔗 Adding cross-references between documents..."
python3 scripts/mdbook/add-cross-references.py
echo "  ✓ Cross-references added"

# Step 3: Generate relationships data
echo ""
echo "🔗 Step 3: Generating relationship data..."
echo "------------------------------------------------"

echo "  📊 Generating relationships.json..."
python3 scripts/mdbook/generate-relationships.py
echo "  ✓ Document relationships updated"

# Step 4: Sync Airtable metadata (BEFORE generating SUMMARY.md)
echo ""
echo "☁️  Step 4: Syncing Airtable metadata..."
echo "------------------------------------------------"

echo "  🔄 Fetching latest from Airtable..."
python3 scripts/mdbook/sync-airtable-metadata.py --mode=full --if-stale

# Copy metadata to src directory so it's available for SUMMARY generation
if [ -f "book/airtable-metadata.json" ]; then
    cp book/airtable-metadata.json src/
    echo "  ✓ Metadata copied to src/"
fi

if [ -f "book/relationships.json" ]; then
    cp book/relationships.json src/
    echo "  ✓ Relationships copied to src/"
fi

echo "  ✓ Airtable metadata synced"

# Step 5: Generate SUMMARY.md with Airtable data
echo ""
echo "📋 Step 5: Generating navigation with Airtable data..."
echo "------------------------------------------------"

# Use the enhanced version if it exists, otherwise fall back to standard
if [ -f "scripts/mdbook/generate-summary-with-airtable.py" ]; then
    echo "  📋 Using enhanced SUMMARY generator with Airtable integration..."
    python3 scripts/mdbook/generate-summary-with-airtable.py
else
    echo "  📋 Using standard SUMMARY generator..."
    python3 scripts/mdbook/generate-summary.py
fi
echo "  ✓ Table of contents updated"

# Step 6: Build mdBook
echo ""
echo "📚 Step 6: Building mdBook..."
echo "------------------------------------------------"

# Kill any existing mdbook serve process to avoid conflicts
pkill -f "mdbook serve" 2>/dev/null || true

# Build the book
mdbook build

echo "  ✓ mdBook built"

# Step 7: Post-processing (apply custom formatting)
echo ""
echo "🎨 Step 7: Applying custom formatting..."
echo "------------------------------------------------"

echo "  🎨 Applying custom list formatting..."
python3 scripts/postprocessing/custom-list-processor.py

# Apply enhanced formatting if available
if [ -f "scripts/postprocessing/enhanced-custom-processor.py" ]; then
    echo "  ✨ Applying enhanced document-specific formatting..."
    python3 scripts/postprocessing/enhanced-custom-processor.py
fi

echo "  ✓ Custom formatting applied"

# Step 8: Final metadata copy to book directory
echo ""
echo "📦 Step 8: Finalizing build..."
echo "------------------------------------------------"

# Ensure metadata files are in the book directory for runtime access
if [ -f "src/airtable-metadata.json" ]; then
    cp src/airtable-metadata.json book/
    echo "  ✓ Airtable metadata available in book/"
fi

if [ -f "src/relationships.json" ]; then
    cp src/relationships.json book/
    echo "  ✓ Relationships data available in book/"
fi

# Summary
echo ""
echo "=================================================="
echo "✅ Build Complete!"
echo ""
echo "Processing order summary:"
echo "  1. Document sync to src/"
echo "  2. Pre-processing (footnotes, links)"
echo "  3. Relationship generation"
echo "  4. Airtable metadata sync"
echo "  5. SUMMARY.md generation with Airtable data"
echo "  6. mdBook build"
echo "  7. Post-processing (custom formatting)"
echo "  8. Finalization"
echo ""
echo "📖 Your site is ready at: http://localhost:3000"
echo ""
echo "⚠️  Note: If using 'mdbook serve', it will auto-rebuild but skip post-processing."
echo "    Run this script again after changes to ensure all formatting is applied."