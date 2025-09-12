#!/bin/bash
# PATH override for mdbook in this project
# Place this directory first in PATH to intercept mdbook commands

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

if [ "$1" = "serve" ]; then
    clear
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${RED}                    ⚠️  STOP! WRONG COMMAND! ⚠️${NC}"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "${YELLOW}You tried to run: mdbook serve${NC}"
    echo -e "${RED}This command will DELETE all CSS and break formatting!${NC}"
    echo ""
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}                    ✅ USE THIS INSTEAD ✅${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "   ${BLUE}./dev-server.sh${NC}"
    echo ""
    echo "Why use dev-server.sh?"
    echo "  • Compiles CSS from modular files"
    echo "  • Runs custom list processor"
    echo "  • Runs enhanced document processor"
    echo "  • Watches for changes and auto-rebuilds"
    echo "  • Prevents the 'disappearing styles' bug"
    echo ""
    echo -e "${YELLOW}Redirecting to ./dev-server.sh in 3 seconds...${NC}"
    sleep 3
    exec ./dev-server.sh
else
    # Pass through for other mdbook commands
    exec /usr/local/bin/mdbook "$@"
fi