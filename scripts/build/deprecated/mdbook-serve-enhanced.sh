#!/bin/bash
# Enhanced mdbook serve that automatically maintains custom formatting
#
# This wrapper solves the problem where mdBook's auto-rebuild bypasses our
# custom processors (form fields, cross-references, custom lists).
#
# Usage: ./mdbook-serve-enhanced.sh [port]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PORT=${1:-3000}

echo "🚀 Starting Enhanced mdBook Server"
echo "=================================="

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down..."
    
    # Kill the watcher
    if [ ! -z "$WATCHER_PID" ]; then
        kill $WATCHER_PID 2>/dev/null || true
    fi
    
    # Kill mdbook serve
    if [ ! -z "$MDBOOK_PID" ]; then
        kill $MDBOOK_PID 2>/dev/null || true
    fi
    
    # Kill any orphaned processes
    pkill -f "mdbook-postprocess-watcher.py" 2>/dev/null || true
    
    echo -e "${GREEN}✅ Server stopped${NC}"
    exit 0
}

# Set up cleanup on script exit
trap cleanup INT TERM EXIT

# Check if mdbook is installed
if ! command -v mdbook &> /dev/null; then
    echo -e "${RED}❌ mdbook is not installed${NC}"
    echo "   Install with: cargo install mdbook"
    exit 1
fi

# Check if another mdbook serve is already running
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Port $PORT is already in use${NC}"
    echo "   Another mdbook serve might be running"
    echo ""
    echo "   To stop it: pkill -f 'mdbook serve'"
    echo "   Or use a different port: $0 3001"
    exit 1
fi

# Run initial build to ensure everything is processed
echo "📚 Running initial build with all processors..."
if [ -f "./build-all.sh" ]; then
    ./build-all.sh --quick >/dev/null 2>&1
    echo -e "${GREEN}✅ Initial build complete${NC}"
else
    echo -e "${YELLOW}⚠️  build-all.sh not found, skipping initial build${NC}"
fi

echo ""

# Start the post-processor watcher in background
echo "👁️  Starting post-processor watcher..."
python3 scripts/mdbook/mdbook-postprocess-watcher.py &
WATCHER_PID=$!

# Give the watcher a moment to initialize
sleep 1

# Start mdbook serve
echo "🌐 Starting mdBook server on port $PORT..."
echo ""
mdbook serve --port $PORT &
MDBOOK_PID=$!

# Wait a moment for server to start
sleep 2

echo "=========================================="
echo -e "${GREEN}✅ Enhanced server running${NC}"
echo "=========================================="
echo ""
echo "📖 Book URL: http://localhost:$PORT"
echo ""
echo "✨ Features:"
echo "   • Auto-rebuild on file changes (mdBook)"
echo "   • Auto-restore custom formatting (watcher)"
echo "   • Form fields stay blue"
echo "   • Cross-references keep working"
echo ""
echo "💡 Tips:"
echo "   • Edit files in src/ or source-documents/"
echo "   • Custom formatting auto-applies after each rebuild"
echo "   • Press Ctrl+C to stop"
echo ""

# Wait for processes
wait $MDBOOK_PID