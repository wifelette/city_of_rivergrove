#!/bin/bash
# Consolidated build script for City of Rivergrove mdBook site
# This replaces: update-mdbook.sh, update-mdbook-enhanced.sh, update-mdbook-airtable.sh, build.sh
# Usage: ./build-all.sh [options]
# Options:
#   --quick    Skip Airtable sync (faster for local testing)
#   --help     Show this help message

set -e  # Exit on any error

# Parse command line arguments
SKIP_AIRTABLE=false
for arg in "$@"; do
    case $arg in
        --quick)
            SKIP_AIRTABLE=true
            shift
            ;;
        --help)
            echo "City of Rivergrove - Master Build Script"
            echo ""
            echo "Usage: ./build-all.sh [options]"
            echo ""
            echo "Options:"
            echo "  --quick    Skip Airtable sync (faster for local testing)"
            echo "  --help     Show this help message"
            echo ""
            echo "This script performs a complete rebuild of the mdBook site with all"
            echo "processing steps in the correct order."
            exit 0
            ;;
        *)
            echo "Unknown option: $arg"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Check if mdbook serve is running and track it
SERVER_WAS_RUNNING=false
if pgrep -f "mdbook serve" > /dev/null; then
    echo "⚠️  Detected mdbook serve running - stopping it to prevent conflicts..."
    SERVER_WAS_RUNNING=true
    pkill -f "mdbook serve"
    sleep 1
fi

echo "🚀 City of Rivergrove - Complete Build"
echo "======================================"
echo ""

# STEP 1: Sync all documents from source to /src
echo "📁 Step 1: Syncing documents to /src..."
echo "  • Ordinances..."
python3 scripts/preprocessing/sync-ordinances.py
echo "  • Resolutions..."
python3 scripts/preprocessing/sync-resolutions.py
echo "  • Interpretations..."
python3 scripts/preprocessing/sync-interpretations.py
echo "  • Meeting documents..."
python3 scripts/preprocessing/sync-meetings.py
echo "  • Other documents..."
python3 scripts/preprocessing/sync-other.py
echo "  ✅ All documents synced"
echo ""

# STEP 2: Validate no HTML in source files
echo "🚫 Step 2: Checking for HTML in markdown files..."
python3 scripts/validation/validate-no-html.py source-documents --quiet || {
    echo "  ❌ HTML found in source files!"
    echo "  Run 'python3 scripts/validation/validate-no-html.py' for details"
    exit 1
}
echo "  ✅ No HTML in source files"
echo ""

# STEP 3: Validate form field syntax
echo "🔍 Step 3: Validating form field syntax..."
python3 scripts/validation/validate-form-fields.py --quiet || {
    echo "  ❌ Form field validation failed!"
    echo "  Run 'python3 scripts/validation/validate-form-fields.py' for details"
    exit 1
}
echo "  ✅ Form fields validated"
echo ""

# STEP 4: Process footnotes
echo "📝 Step 4: Processing footnotes..."
python3 scripts/preprocessing/footnote-preprocessor.py
echo "  ✅ Footnotes processed"
echo ""

# STEP 5: Convert URLs and emails (MUST be before cross-references)
echo "🔗 Step 5: Converting URLs and emails to links..."
python3 scripts/preprocessing/auto-link-converter.py src/ordinances/*.md src/resolutions/*.md src/interpretations/*.md src/other/*.md 2>/dev/null || true
echo "  ✅ Links converted"
echo ""

# STEP 6: Add cross-references (MUST be after auto-link)
echo "🔗 Step 6: Adding cross-references between documents..."
python3 scripts/mdbook/add-cross-references.py
echo "  ✅ Cross-references added"
echo ""

# STEP 7: Update document counts
echo "📊 Step 7: Updating document counts..."
if [ -f "scripts/preprocessing/update-document-counts.py" ]; then
    python3 scripts/preprocessing/update-document-counts.py
    echo "  ✅ Document counts updated"
else
    echo "  ⏭️  Skipped (script not found)"
fi
echo ""

# STEP 8: Generate relationships (MUST be first for Airtable sync to work)
echo "🔗 Step 8: Generating document relationships..."
python3 scripts/mdbook/generate-relationships.py
# Copy to book directory for Airtable sync (which looks for book/relationships.json)
mkdir -p book
cp src/relationships.json book/relationships.json 2>/dev/null || true
echo "  ✅ Relationships updated"
echo ""

# STEP 9: Sync Airtable metadata (needs relationships.json)
if [ "$SKIP_AIRTABLE" = false ]; then
    echo "☁️  Step 9: Syncing Airtable metadata..."
    if [ -f "scripts/mdbook/sync-airtable-metadata.py" ]; then
        # Force sync in CI environment (GitHub Actions)
        if [ -n "$CI" ]; then
            python3 scripts/mdbook/sync-airtable-metadata.py --mode=full --force
        else
            python3 scripts/mdbook/sync-airtable-metadata.py --mode=full --if-stale
        fi
        # Copy metadata to src directory
        if [ -f "book/airtable-metadata.json" ]; then
            cp book/airtable-metadata.json src/
        fi
        echo "  ✅ Airtable metadata synced"
    else
        echo "  ⏭️  Skipped (script not found)"
    fi
    
    # Also sync meetings metadata
    echo "☁️  Syncing meetings metadata..."
    if [ -f "scripts/mdbook/sync-meetings-metadata.py" ]; then
        python3 scripts/mdbook/sync-meetings-metadata.py
        echo "  ✅ Meetings metadata synced"
    else
        echo "  ⏭️  Meetings metadata sync skipped (script not found)"
    fi
else
    echo "⏭️  Step 9: Skipping Airtable sync (--quick mode)"
fi
echo ""

# STEP 10: Generate SUMMARY.md (AFTER relationships AND Airtable sync)
echo "📋 Step 10: Generating table of contents..."
if [ -f "scripts/mdbook/generate-summary-with-airtable.py" ] && [ "$SKIP_AIRTABLE" = false ]; then
    python3 scripts/mdbook/generate-summary-with-airtable.py
else
    python3 scripts/mdbook/generate-summary.py
fi
echo "  ✅ Table of contents updated"
echo ""

# STEP 11: Build mdBook
echo "📚 Step 11: Building mdBook..."
mdbook build
echo "  ✅ mdBook built"
echo ""

# STEP 12: Copy images and data files to book directory
# CRITICAL: This MUST happen AFTER mdbook build, as mdbook cleans the book/ directory!
# The theme/ directory contains our modular CSS architecture and must be copied here.
echo "📂 Step 12: Copying images and data files..."
# Copy all images to the book directory
if [ -d "images" ]; then
    echo "  • Copying images directory..."
    cp -r images book/
fi
# Copy theme directory for CSS modules
if [ -d "theme" ]; then
    echo "  • Copying theme directory..."
    cp -r theme book/
fi
# Copy navigation JavaScript
if [ -f "navigation-standalone.js" ]; then
    echo "  • Copying navigation JavaScript..."
    cp navigation-standalone.js book/
fi
# Copy data files
if [ -f "src/relationships.json" ]; then
    cp src/relationships.json book/
fi
if [ -f "src/airtable-metadata.json" ]; then
    cp src/airtable-metadata.json book/
fi
echo "  ✅ Images and data files copied"
echo ""

# Add warnings to generated CSS files
if [ -f "scripts/build/add-readonly-warnings.sh" ]; then
    ./scripts/build/add-readonly-warnings.sh >/dev/null 2>&1
fi

# STEP 13: Apply custom formatting (MUST be after mdBook build)
echo "🎨 Step 13: Applying custom formatting..."
python3 scripts/postprocessing/custom-list-processor.py
echo "  ✅ Custom formatting applied"
echo ""

# STEP 14: Apply enhanced formatting (if available)
if [ -f "scripts/postprocessing/enhanced-custom-processor.py" ]; then
    echo "✨ Step 14: Applying enhanced document formatting..."
    python3 scripts/postprocessing/enhanced-custom-processor.py
    echo "  ✅ Enhanced formatting applied"
else
    echo "⏭️  Step 14: Enhanced formatting not available"
fi
echo ""

# Done!
echo "======================================"
echo "✅ Build complete!"
echo ""

# Restart server if it was running before
if [ "$SERVER_WAS_RUNNING" = true ]; then
    echo "🔄 Restarting development server..."
    ./dev-server.sh > /dev/null 2>&1 &
    sleep 2
    if pgrep -f "mdbook serve" > /dev/null; then
        echo "✅ Server restarted at http://localhost:3000"
    else
        echo "❌ Failed to restart server. Run './dev-server.sh' manually."
    fi
else
    echo "📖 View your site at: http://localhost:3000"
    echo "   Run ./dev-server.sh to start the development server"
fi
echo ""

# Check if any source files were edited in /src
if [ -n "$(git status --porcelain src/ 2>/dev/null | grep -v 'SUMMARY.md' | grep -v 'introduction.md')" ]; then
    echo "⚠️  Warning: Detected changes in /src directory"
    echo "   Remember: Never edit files in /src directly!"
    echo "   Always edit source-documents/ files instead."
fi