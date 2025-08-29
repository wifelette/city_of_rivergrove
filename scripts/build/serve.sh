#!/bin/bash
# Custom serve script that runs postprocessing after mdBook rebuilds

echo "🚀 Starting mdBook with automatic postprocessing..."
echo "   Press Ctrl+C to stop"
echo ""

# Kill any existing mdbook serve process
pkill -f "mdbook serve" 2>/dev/null

# Function to run postprocessor
run_postprocessor() {
    echo "  🎨 Running postprocessor..."
    python3 scripts/postprocessing/custom-list-processor.py >/dev/null 2>&1
    if [ -f "scripts/postprocessing/enhanced-custom-processor.py" ]; then
        python3 scripts/postprocessing/enhanced-custom-processor.py >/dev/null 2>&1
    fi
    echo "  ✓ Postprocessing complete"
}

# Initial build with postprocessing
echo "📚 Running initial build..."
mdbook build
run_postprocessor

# Start mdbook serve in background
mdbook serve --port 3000 &
MDBOOK_PID=$!

echo "✅ Server running at http://localhost:3000"
echo ""

# Monitor for file changes in book directory and run postprocessor
# Using fswatch if available, otherwise fall back to a simple loop
if command -v fswatch >/dev/null 2>&1; then
    echo "📁 Watching for changes (using fswatch)..."
    fswatch -o book/*.html book/**/*.html 2>/dev/null | while read change; do
        run_postprocessor
    done
else
    echo "📁 Watching for changes (polling mode)..."
    echo "   (Install fswatch for better performance: brew install fswatch)"
    
    # Simple polling fallback
    LAST_MODIFIED=$(find book -name "*.html" -type f -exec stat -f "%m" {} \; 2>/dev/null | sort -n | tail -1)
    
    while true; do
        sleep 2
        CURRENT_MODIFIED=$(find book -name "*.html" -type f -exec stat -f "%m" {} \; 2>/dev/null | sort -n | tail -1)
        
        if [ "$CURRENT_MODIFIED" != "$LAST_MODIFIED" ]; then
            run_postprocessor
            LAST_MODIFIED=$CURRENT_MODIFIED
        fi
    done
fi

# Clean up on exit
trap "kill $MDBOOK_PID 2>/dev/null; exit" INT TERM
wait $MDBOOK_PID