#!/bin/bash
# Shared functions for managing mdbook server instances
# Source this file in other scripts: source scripts/utils/server-management.sh

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to stop all mdbook serve processes
stop_all_mdbook_servers() {
    local quiet=${1:-false}
    
    # Check if any mdbook serve processes are running
    if pgrep -f "mdbook serve" > /dev/null 2>&1; then
        if [ "$quiet" != "true" ]; then
            echo -e "${YELLOW}⚠️  Found existing mdbook server(s) running${NC}"
            echo "   Stopping them to prevent conflicts..."
        fi
        
        # Kill all mdbook serve processes
        pkill -f "mdbook serve" 2>/dev/null
        
        # Give them time to shut down
        sleep 1
        
        # Force kill if still running
        if pgrep -f "mdbook serve" > /dev/null 2>&1; then
            if [ "$quiet" != "true" ]; then
                echo "   Force stopping stubborn processes..."
            fi
            pkill -9 -f "mdbook serve" 2>/dev/null
            sleep 1
        fi
        
        if [ "$quiet" != "true" ]; then
            echo -e "${GREEN}   ✓ Previous servers stopped${NC}"
        fi
        return 0
    else
        if [ "$quiet" != "true" ]; then
            echo -e "${GREEN}✓ No existing mdbook servers found${NC}"
        fi
        return 1
    fi
}

# Function to check if mdbook server is running on a specific port
is_server_running_on_port() {
    local port=${1:-3000}
    
    # Check if anything is listening on the port
    if lsof -i :$port > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Function to wait for server to start
wait_for_server_start() {
    local port=${1:-3000}
    local max_wait=${2:-10}
    local waited=0
    
    echo -n "   Waiting for server to start"
    while [ $waited -lt $max_wait ]; do
        if is_server_running_on_port $port; then
            echo ""
            echo -e "${GREEN}   ✓ Server started successfully${NC}"
            return 0
        fi
        echo -n "."
        sleep 1
        waited=$((waited + 1))
    done
    
    echo ""
    echo -e "${RED}   ✗ Server failed to start after ${max_wait} seconds${NC}"
    return 1
}

# Function to safely start mdbook server
safe_start_mdbook_server() {
    local port=${1:-3000}
    local background=${2:-true}
    
    echo -e "${BLUE}🌐 Starting mdbook server on port $port...${NC}"
    
    # Stop any existing servers
    stop_all_mdbook_servers true
    
    # Start the server
    if [ "$background" = "true" ]; then
        mdbook serve --port $port > /dev/null 2>&1 &
        local server_pid=$!
        
        # Wait for it to start
        if wait_for_server_start $port; then
            echo -e "${GREEN}✅ Server running at http://localhost:$port (PID: $server_pid)${NC}"
            return 0
        else
            echo -e "${RED}❌ Failed to start server${NC}"
            return 1
        fi
    else
        # Run in foreground
        mdbook serve --port $port
    fi
}

# Function to get PID of mdbook server
get_mdbook_server_pid() {
    pgrep -f "mdbook serve" | head -1
}

# Function to check server health
check_server_health() {
    local port=${1:-3000}
    
    if is_server_running_on_port $port; then
        local pid=$(get_mdbook_server_pid)
        if [ -n "$pid" ]; then
            echo -e "${GREEN}✅ Server is healthy (PID: $pid, Port: $port)${NC}"
            return 0
        else
            echo -e "${YELLOW}⚠️  Something is using port $port but it's not mdbook${NC}"
            return 1
        fi
    else
        echo -e "${YELLOW}⚠️  No server running on port $port${NC}"
        return 1
    fi
}