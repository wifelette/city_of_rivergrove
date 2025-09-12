#!/bin/bash
# Monitors mdBook rebuilds and applies postprocessors after each rebuild
# This prevents the cycle where postprocessors trigger mdBook rebuilds

# Track the last time we ran postprocessors
LAST_POSTPROCESS_TIME=0
POSTPROCESS_COOLDOWN=10  # Don't run postprocessors more than once every 10 seconds

# Function to get file modification time in seconds
get_mtime() {
    stat -f %m "$1" 2>/dev/null || echo 0
}

# Function to run postprocessors
run_postprocessors() {
    local current_time=$(date +%s)
    
    # Check cooldown to prevent infinite loops
    if [ $((current_time - LAST_POSTPROCESS_TIME)) -lt $POSTPROCESS_COOLDOWN ]; then
        return
    fi
    
    echo "🎨 Applying postprocessors..."
    
    # Run custom list processor
    python3 scripts/postprocessing/custom-list-processor.py >/dev/null 2>&1
    
    # Run enhanced processor for Document Notes and other styling
    python3 scripts/postprocessing/enhanced-custom-processor.py >/dev/null 2>&1
    
    LAST_POSTPROCESS_TIME=$current_time
    
    # Touch marker file to indicate when we last processed
    touch book/.postprocessed
    
    echo "✅ Postprocessors applied"
}

# Function to check if mdBook has rebuilt
check_for_rebuild() {
    local marker_file="book/.postprocessed"
    
    # If marker doesn't exist, we need to process
    if [ ! -f "$marker_file" ]; then
        return 0
    fi
    
    # Check if any HTML file is newer than our marker
    local newest_html=$(find book -name "*.html" -type f -newer "$marker_file" 2>/dev/null | head -1)
    
    if [ -n "$newest_html" ]; then
        # Found HTML files newer than our marker - mdBook rebuilt!
        return 0
    fi
    
    return 1
}

echo "👁️  Watching for mdBook rebuilds..."
echo "   This ensures postprocessors run after each mdBook rebuild"
echo ""

# Initial run of postprocessors
run_postprocessors

# Main monitoring loop
while true; do
    sleep 2
    
    # Check if mdBook has rebuilt (files exist but lack our enhancements)
    if check_for_rebuild; then
        echo "🔄 Detected mdBook rebuild"
        run_postprocessors
    fi
done