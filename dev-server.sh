#!/bin/bash
# Smart development server that watches SOURCE documents and auto-processes
# Automatically syncs, processes, and rebuilds when you edit source files
# Usage: ./dev-server.sh

# Don't use set -e here since we want to handle errors ourselves
# set -e would exit before we can check specific error types

# Source server management utilities
source scripts/utils/server-management.sh

echo -e "${BLUE}🚀 City of Rivergrove - Smart Development Server${NC}"
echo "=========================================="
echo ""

# Stop any existing servers
stop_all_mdbook_servers

# Track if we're currently processing to avoid loops
PROCESSING=false

# Function to process a changed file
process_file_change() {
    local file="$1"
    local filename=$(basename "$file")
    
    # Skip if we're already processing
    if [ "$PROCESSING" = true ]; then
        return
    fi
    
    PROCESSING=true
    
    echo ""
    echo -e "${BLUE}📝 Detected change: $filename${NC}"
    
    # First validate form field syntax
    echo "  Validating form fields..."
    if ! /usr/bin/python3 scripts/validation/validate-form-fields.py "$file" --quiet 2>/dev/null; then
        echo -e "${RED}  ✗ Form field errors detected!${NC}"
        /usr/bin/python3 scripts/validation/validate-form-fields.py "$file" 2>&1
        echo -e "${YELLOW}  Fix the errors above and save again${NC}"
        PROCESSING=false
        return
    fi
    
    # Determine document type and run appropriate sync
    if [[ "$file" == *source-documents/Ordinances/* ]]; then
        echo "  Syncing ordinances..."
        /usr/bin/python3 scripts/preprocessing/sync-ordinances.py >/dev/null 2>&1
    elif [[ "$file" == *source-documents/Resolutions/* ]]; then
        echo "  Syncing resolutions..."
        /usr/bin/python3 scripts/preprocessing/sync-resolutions.py >/dev/null 2>&1
    elif [[ "$file" == *source-documents/Interpretations/* ]]; then
        echo "  Syncing interpretations..."
        /usr/bin/python3 scripts/preprocessing/sync-interpretations.py >/dev/null 2>&1
    elif [[ "$file" == *source-documents/Other/* ]]; then
        echo "  Syncing other documents..."
        /usr/bin/python3 scripts/preprocessing/sync-other.py >/dev/null 2>&1
    elif [[ "$file" == *source-documents/Meetings/* ]]; then
        echo "  Syncing meeting documents..."
        # Just copy meeting files
        local dest_filename=$(echo "$filename" | sed 's/#//g')
        if [[ "$file" == *Agenda* ]]; then
            mkdir -p src/agendas
            cp "$file" "src/agendas/$dest_filename"
        elif [[ "$file" == *Minutes* ]]; then
            mkdir -p src/minutes
            cp "$file" "src/minutes/$dest_filename"
        elif [[ "$file" == *Transcript* ]]; then
            mkdir -p src/transcripts
            cp "$file" "src/transcripts/$dest_filename"
        fi
    else
        echo -e "${YELLOW}  Skipping (not a recognized document type)${NC}"
        PROCESSING=false
        return
    fi
    
    # Get the destination file path (remove # from filename)
    local dest_filename=$(echo "$filename" | sed 's/#//g')
    local dest_file=""
    
    if [[ "$file" == *source-documents/Ordinances/* ]]; then
        dest_file="src/ordinances/$dest_filename"
    elif [[ "$file" == *source-documents/Resolutions/* ]]; then
        dest_file="src/resolutions/$dest_filename"
    elif [[ "$file" == *source-documents/Interpretations/* ]]; then
        dest_file="src/interpretations/$dest_filename"
    elif [[ "$file" == *source-documents/Other/* ]]; then
        dest_file="src/other/$dest_filename"
    fi
    
    # Run processing pipeline on the synced file
    if [ -n "$dest_file" ] && [ -f "$dest_file" ]; then
        echo "  Standardizing list formats..."
        /usr/bin/python3 scripts/preprocessing/standardize-list-format.py >/dev/null 2>&1 || true

        echo "  Fixing mixed list formats..."
        /usr/bin/python3 scripts/preprocessing/fix-mixed-list-format.py "$dest_file" >/dev/null 2>&1 || true

        echo "  Processing footnotes..."
        /usr/bin/python3 scripts/preprocessing/footnote-preprocessor.py "$dest_file" >/dev/null 2>&1 || true
        
        echo "  Converting links..."
        /usr/bin/python3 scripts/preprocessing/auto-link-converter.py "$dest_file" >/dev/null 2>&1 || true
    fi
    
    # Always update cross-references (they scan all files)
    echo "  Updating cross-references..."
    /usr/bin/python3 scripts/mdbook/add-cross-references.py >/dev/null 2>&1
    
    # Regenerate SUMMARY.md and relationships
    echo "  Updating indexes..."
    /usr/bin/python3 scripts/mdbook/generate-summary-with-airtable.py >/dev/null 2>&1
    /usr/bin/python3 scripts/mdbook/generate-relationships.py >/dev/null 2>&1
    # Copy relationships to book directory for navigation to use
    cp src/relationships.json book/relationships.json 2>/dev/null || true
    
    # Wait for mdBook to detect changes and start rebuilding
    # Increased from 2 to 3 seconds to ensure mdBook has time to start
    sleep 3
    
    # Copy navigation if it was updated
    if [[ "$file" == "navigation-standalone.js" ]]; then
        echo "  Copying navigation to book directory..."
        cp navigation-standalone.js book/ 2>/dev/null
    fi
    
    # Recompile CSS if CSS was updated
    if [[ "$file" == *.css ]] || [[ "$file" == theme/* ]]; then
        echo "  Recompiling CSS..."
        /usr/bin/python3 scripts/build/compile-css.py >/dev/null 2>&1
    fi
    
    # Ensure mdBook has finished rebuilding before postprocessing
    # Check if index.html exists and is recent (modified in last 5 seconds)
    if [ -f "book/index.html" ]; then
        # Wait a bit more if the file was just created
        local age=$(( $(date +%s) - $(stat -f %m book/index.html 2>/dev/null || echo 0) ))
        if [ $age -le 1 ]; then
            echo "  Waiting for mdBook to complete..."
            sleep 1
        fi
    fi
    
    # Apply postprocessors after mdBook rebuilds
    # Apply enhanced processor for tables, WHEREAS, etc FIRST (NO list processing)
    echo "  Applying enhanced styling..."
    /usr/bin/python3 scripts/postprocessing/enhanced-custom-processor.py >/dev/null 2>&1

    # Use the NEW unified list processor v2 - single source of truth for ALL list processing
    echo "  Processing all lists..."
    /usr/bin/python3 scripts/postprocessing/unified-list-processor.py >/dev/null 2>&1

    # Run list formatting tests on critical files (suppress output unless there's an error)
    if [ -f "scripts/tests/test-list-formatting.py" ]; then
        echo "  Running list formatting tests..."
        if ! /usr/bin/python3 scripts/tests/test-list-formatting.py book/ordinances/1989-Ord-54-89C-Land-Development.html >/dev/null 2>&1; then
            echo -e "${YELLOW}    ⚠️  Some list formatting tests failed - run ./scripts/validation/test-list-changes.sh for details${NC}"
        fi
    fi

    # Quick style health check (show specific issues if found)
    if ! /usr/bin/python3 scripts/validation/check-styles-health.py --verbose 2>&1; then
        # Error messages already shown by the script with specific details
        :
    fi
    
    echo -e "${GREEN}  ✓ Processing complete${NC}"
    
    PROCESSING=false
}

# Initial build
echo "📚 Running initial build..."
# Capture build output to check for specific errors
BUILD_OUTPUT=$(./build-all.sh 2>&1)
BUILD_EXIT_CODE=$?

if [ $BUILD_EXIT_CODE -ne 0 ]; then
    # Check if it's just the SUMMARY.md parsing warning
    if echo "$BUILD_OUTPUT" | grep -q "Summary parsing failed\|failed to parse SUMMARY.md"; then
        echo -e "${YELLOW}⚠️  Build has SUMMARY.md warnings (non-critical), continuing...${NC}"
        echo "   (Run './build-all.sh' to see full output)"
    elif echo "$BUILD_OUTPUT" | grep -q "❌ Manual /src modifications detected"; then
        echo -e "${RED}❌ Build failed: Manual /src modifications detected${NC}"
        echo "   Run 'git checkout -- src/' then try again"
        exit 1
    elif echo "$BUILD_OUTPUT" | grep -q "⚠️  Auto-generated changes detected"; then
        echo -e "${YELLOW}⚠️  Build has auto-generated src/ changes (normal), continuing...${NC}"
        echo "   (Review with 'git diff src/' if needed)"
    else
        echo -e "${RED}❌ Build failed with errors:${NC}"
        echo "$BUILD_OUTPUT" | tail -20
        echo ""
        echo "Fix the errors above and try again"
        exit 1
    fi
else
    echo -e "${GREEN}✅ Initial build complete${NC}"
fi
echo ""

# Start mdbook serve in background with proper checks
echo "🌐 Starting development server..."
mdbook serve --port 3000 > /dev/null 2>&1 &
MDBOOK_PID=$!

# Wait for server to actually start
if wait_for_server_start 3000 10; then
    echo ""

    # Run postprocessors after mdbook serve rebuilds
    echo "🎨 Applying styles and processors..."
    /usr/bin/python3 scripts/build/compile-css.py >/dev/null 2>&1 || true
    # Run enhanced-custom-processor first for tables, WHEREAS, etc (NO list processing)
    /usr/bin/python3 scripts/postprocessing/enhanced-custom-processor.py >/dev/null 2>&1 || true
    # Use unified list processor v2 for ALL list processing
    /usr/bin/python3 scripts/postprocessing/unified-list-processor.py >/dev/null 2>&1 || true
    echo "✅ Styles applied"
    echo ""
    echo "=========================================="
    echo -e "${GREEN}✅ Server running at http://localhost:3000${NC}"
    echo "=========================================="
else
    echo -e "${RED}❌ Failed to start development server${NC}"
    echo "Check for errors in the build process"
    exit 1
fi
echo ""
echo "📁 Watching for changes in source-documents/..."
echo "   • Edit files in source-documents/"
echo "   • Changes auto-sync, process, and rebuild"
echo "   • Press Ctrl+C to stop"
echo ""

# Function to watch source-documents for changes
watch_source_documents() {
    if command -v fswatch >/dev/null 2>&1; then
        # Use fswatch for better performance
        # Exclude PDFs, git files, and other non-markdown files
        fswatch -r -e ".*\.pdf$" -e "\.git" -e "\.DS_Store" source-documents/ | while read changed_file; do
            if [[ "$changed_file" == *.md ]]; then
                process_file_change "$changed_file"
            fi
        done
    else
        echo -e "${YELLOW}💡 Tip: Install fswatch for better performance${NC}"
        echo "   brew install fswatch"
        echo ""
        
        # Fallback to find + stat polling
        declare -A LAST_MODIFIED
        
        # Get initial modification times
        while IFS= read -r -d '' file; do
            if [ -f "$file" ]; then
                LAST_MODIFIED["$file"]=$(stat -f "%m" "$file" 2>/dev/null)
            fi
        done < <(find source-documents -name "*.md" -type f -print0)
        
        # Poll for changes
        while true; do
            sleep 2
            
            while IFS= read -r -d '' file; do
                if [ -f "$file" ]; then
                    CURRENT=$(stat -f "%m" "$file" 2>/dev/null)
                    if [ "${LAST_MODIFIED[$file]}" != "$CURRENT" ]; then
                        LAST_MODIFIED["$file"]=$CURRENT
                        process_file_change "$file"
                    fi
                fi
            done < <(find source-documents -name "*.md" -type f -print0)
        done
    fi
}

# Cleanup function
cleanup() {
    echo ""
    echo "🛑 Shutting down..."
    kill $MDBOOK_PID 2>/dev/null || true
    kill $SOURCE_WATCHER_PID 2>/dev/null || true
    kill $POSTPROCESS_WATCHER_PID 2>/dev/null || true
    echo -e "${GREEN}✅ Server stopped${NC}"
    exit 0
}

# Set up signal handlers
trap cleanup INT TERM

# Start the source watcher in background
watch_source_documents &
SOURCE_WATCHER_PID=$!

# Start the postprocess watcher to handle mdBook rebuilds
# TEMPORARILY DISABLED - causing rebuild loops
# scripts/utils/mdbook-postprocess-watcher.sh &
# POSTPROCESS_WATCHER_PID=$!

# Wait for processes to exit
wait $MDBOOK_PID $SOURCE_WATCHER_PID $POSTPROCESS_WATCHER_PID