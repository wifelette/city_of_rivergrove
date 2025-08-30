#!/bin/bash
# Smart development server that watches SOURCE documents and auto-processes
# Automatically syncs, processes, and rebuilds when you edit source files
# Usage: ./dev-server.sh

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 City of Rivergrove - Smart Development Server${NC}"
echo "=========================================="
echo ""

# Check if mdbook serve is already running
if pgrep -f "mdbook serve" > /dev/null; then
    echo -e "${YELLOW}⚠️  mdbook serve is already running${NC}"
    echo "   Stopping it to start our enhanced server..."
    pkill -f "mdbook serve"
    sleep 1
fi

# Function to process a changed file
process_file_change() {
    local file="$1"
    local filename=$(basename "$file")
    
    echo ""
    echo -e "${BLUE}📝 Detected change: $filename${NC}"
    
    # Determine document type and run appropriate sync
    if [[ "$file" == source-documents/Ordinances/* ]]; then
        echo "  Syncing ordinances..."
        python3 scripts/preprocessing/sync-ordinances.py >/dev/null 2>&1
    elif [[ "$file" == source-documents/Resolutions/* ]]; then
        echo "  Syncing resolutions..."
        python3 scripts/preprocessing/sync-resolutions.py >/dev/null 2>&1
    elif [[ "$file" == source-documents/Interpretations/* ]]; then
        echo "  Syncing interpretations..."
        python3 scripts/preprocessing/sync-interpretations.py >/dev/null 2>&1
    elif [[ "$file" == source-documents/Other/* ]]; then
        echo "  Syncing other documents..."
        python3 scripts/preprocessing/sync-other.py >/dev/null 2>&1
    elif [[ "$file" == source-documents/Meetings/* ]]; then
        echo "  Syncing meeting documents..."
        # Just copy meeting files
        local dest_filename=$(echo "$filename" | sed 's/#//g')
        if [[ "$file" == *Agenda* ]]; then
            cp "$file" "src/agendas/$dest_filename"
        elif [[ "$file" == *Minutes* ]]; then
            cp "$file" "src/minutes/$dest_filename"
        elif [[ "$file" == *Transcript* ]]; then
            cp "$file" "src/transcripts/$dest_filename"
        fi
    else
        echo -e "${YELLOW}  Skipping (not a recognized document type)${NC}"
        return
    fi
    
    # Get the destination file path (remove # from filename)
    local dest_filename=$(echo "$filename" | sed 's/#//g')
    local dest_file=""
    
    if [[ "$file" == source-documents/Ordinances/* ]]; then
        dest_file="src/ordinances/$dest_filename"
    elif [[ "$file" == source-documents/Resolutions/* ]]; then
        dest_file="src/resolutions/$dest_filename"
    elif [[ "$file" == source-documents/Interpretations/* ]]; then
        dest_file="src/interpretations/$dest_filename"
    elif [[ "$file" == source-documents/Other/* ]]; then
        dest_file="src/other/$dest_filename"
    fi
    
    # Run processing pipeline on the synced file
    if [ -n "$dest_file" ] && [ -f "$dest_file" ]; then
        echo "  Processing footnotes..."
        python3 scripts/preprocessing/footnote-preprocessor.py "$dest_file" >/dev/null 2>&1 || true
        
        echo "  Converting links..."
        python3 scripts/preprocessing/auto-link-converter.py "$dest_file" >/dev/null 2>&1 || true
    fi
    
    # Always update cross-references (they scan all files)
    echo "  Updating cross-references..."
    python3 scripts/mdbook/add-cross-references.py >/dev/null 2>&1
    
    # Regenerate SUMMARY.md and relationships
    echo "  Updating indexes..."
    python3 scripts/mdbook/generate-summary.py >/dev/null 2>&1
    python3 scripts/mdbook/generate-relationships.py >/dev/null 2>&1
    
    echo -e "${GREEN}  ✓ Processing complete${NC}"
}

# Function to run postprocessors
run_postprocessors() {
    if ! python3 scripts/postprocessing/custom-list-processor.py >/dev/null 2>&1; then
        echo -e "${RED}❌ Error in custom-list-processor.py${NC}"
        return 1
    fi
    
    if [ -f "scripts/postprocessing/enhanced-custom-processor.py" ]; then
        if ! python3 scripts/postprocessing/enhanced-custom-processor.py >/dev/null 2>&1; then
            echo -e "${RED}❌ Error in enhanced-custom-processor.py${NC}"
            return 1
        fi
    fi
    
    echo -e "${GREEN}✨ Custom formatting applied${NC}"
    return 0
}

# Initial build
echo "📚 Running initial build..."
./build-all.sh --quick >/dev/null 2>&1
echo -e "${GREEN}✅ Initial build complete${NC}"
echo ""

# Start mdbook serve in background
echo "🌐 Starting development server..."
mdbook serve --port 3000 &
MDBOOK_PID=$!

# Give it a moment to start
sleep 2

echo ""
echo "=========================================="
echo -e "${GREEN}✅ Server running at http://localhost:3000${NC}"
echo "=========================================="
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

# Function to watch for mdBook HTML changes and apply postprocessing
watch_html_changes() {
    if command -v fswatch >/dev/null 2>&1; then
        fswatch -o book/*.html book/**/*.html 2>/dev/null | while read change; do
            sleep 0.5  # Let mdBook finish writing
            run_postprocessors
        done
    else
        # Fallback polling for HTML changes
        LAST_HTML_MODIFIED=$(find book -name "*.html" -type f -exec stat -f "%m" {} \; 2>/dev/null | sort -n | tail -1)
        
        while true; do
            sleep 2
            CURRENT_HTML_MODIFIED=$(find book -name "*.html" -type f -exec stat -f "%m" {} \; 2>/dev/null | sort -n | tail -1)
            
            if [ "$CURRENT_HTML_MODIFIED" != "$LAST_HTML_MODIFIED" ]; then
                sleep 0.5  # Let mdBook finish writing
                run_postprocessors
                LAST_HTML_MODIFIED=$CURRENT_HTML_MODIFIED
            fi
        done
    fi
}

# Cleanup function
cleanup() {
    echo ""
    echo "🛑 Shutting down..."
    kill $MDBOOK_PID 2>/dev/null || true
    kill $SOURCE_WATCHER_PID 2>/dev/null || true
    kill $HTML_WATCHER_PID 2>/dev/null || true
    echo -e "${GREEN}✅ Server stopped${NC}"
    exit 0
}

# Set up signal handlers
trap cleanup INT TERM

# Start both watchers in background
watch_source_documents &
SOURCE_WATCHER_PID=$!

watch_html_changes &
HTML_WATCHER_PID=$!

# Wait for any process to exit
wait $MDBOOK_PID $SOURCE_WATCHER_PID $HTML_WATCHER_PID