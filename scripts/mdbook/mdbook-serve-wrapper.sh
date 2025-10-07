#!/bin/bash
# Wrapper for mdbook serve that ensures SUMMARY.md is always regenerated with Airtable data
# This prevents the sidebar from losing special_state tags during rebuilds

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Get the port from command line args or use default
PORT="${1:-3000}"

# Directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOT_DIR="$( cd "$SCRIPT_DIR/../.." && pwd )"

cd "$ROOT_DIR"

echo -e "${GREEN}🔄 Regenerating SUMMARY.md with Airtable metadata...${NC}"
./scripts/mdbook/generate-summary-with-airtable.py

# Function to regenerate SUMMARY.md before each rebuild
regenerate_summary() {
    while true; do
        # Use inotifywait or fswatch to detect when mdBook is about to rebuild
        # For now, we'll just regenerate periodically
        sleep 5
        
        # Check if any src files have been modified recently
        if find src -name "*.md" -mmin -0.1 2>/dev/null | grep -q .; then
            echo -e "${YELLOW}📝 Detected changes, regenerating SUMMARY.md...${NC}"
            ./scripts/mdbook/generate-summary-with-airtable.py >/dev/null 2>&1
        fi
    done
}

# Start the background regenerator
regenerate_summary &
REGEN_PID=$!

# Cleanup function
cleanup() {
    kill $REGEN_PID 2>/dev/null || true
    exit 0
}

trap cleanup INT TERM

# Run mdbook serve
echo -e "${GREEN}🚀 Starting mdBook serve on port $PORT...${NC}"
mdbook serve --port "$PORT"

# Cleanup when mdbook exits
cleanup