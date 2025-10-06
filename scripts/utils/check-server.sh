#!/bin/bash
# Quick script to verify the dev server is actually running

echo "🔍 Checking server status..."

# Check if mdbook is listening on port 3000
if lsof -i :3000 | grep -q mdbook; then
    echo "✅ mdbook is running on port 3000"
    
    # Test if it's responding
    if curl -s http://localhost:3000/ | head -1 | grep -q "DOCTYPE"; then
        echo "✅ Server is responding correctly"
        echo ""
        echo "🌐 Server URL: http://localhost:3000"
        exit 0
    else
        echo "⚠️  mdbook is listening but not responding correctly"
        exit 1
    fi
else
    echo "❌ No mdbook process found on port 3000"
    
    # Check if anything else is using the port
    if lsof -i :3000 | grep -q LISTEN; then
        echo "⚠️  Something else is using port 3000:"
        lsof -i :3000 | head -3
    fi
    
    echo ""
    echo "💡 To start the server, run: ./dev-server.sh"
    exit 1
fi
