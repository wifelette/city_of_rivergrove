#!/bin/bash
# Check the status of mdbook server
# Usage: ./scripts/utils/check-server.sh

# Source server management utilities
source scripts/utils/server-management.sh

echo -e "${BLUE}🔍 Checking mdbook server status...${NC}"
echo "=================================="
echo ""

# Check if any mdbook processes are running
if pgrep -f "mdbook serve" > /dev/null; then
    PID=$(get_mdbook_server_pid)
    echo -e "${GREEN}✅ mdbook server is running${NC}"
    echo "   PID: $PID"
    
    # Check which port it's on
    if is_server_running_on_port 3000; then
        echo "   Port: 3000"
        echo "   URL: http://localhost:3000"
    else
        echo "   Port: Unknown (not 3000)"
    fi
    
    # Show process details
    echo ""
    echo "Process details:"
    ps -p $PID -o pid,ppid,user,start,time,command | head -2
else
    echo -e "${YELLOW}⚠️  No mdbook server is running${NC}"
    echo ""
    echo "To start the server, run:"
    echo "   ./dev-server.sh"
fi

echo ""

# Check if anything else is using port 3000
if is_server_running_on_port 3000; then
    if ! pgrep -f "mdbook serve" > /dev/null; then
        echo -e "${YELLOW}⚠️  Warning: Port 3000 is in use by another process${NC}"
        echo "   This may prevent mdbook from starting"
        echo ""
        echo "Process using port 3000:"
        lsof -i :3000 | grep LISTEN
    fi
fi

echo "=================================="
echo ""
echo "Server management commands:"
echo "  • Start server:    ./dev-server.sh"
echo "  • Stop server:     pkill -f 'mdbook serve'"
echo "  • Restart server:  ./dev-server.sh (auto-stops existing)"
echo "  • Check health:    ./scripts/utils/check-server.sh"