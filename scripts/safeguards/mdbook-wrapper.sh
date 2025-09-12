#!/bin/bash
# Wrapper script to prevent direct mdbook serve usage
# This intercepts mdbook commands and redirects serve to our dev-server.sh

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if the first argument is "serve"
if [ "$1" = "serve" ]; then
    echo -e "${RED}❌ Direct 'mdbook serve' is disabled!${NC}"
    echo ""
    echo -e "${YELLOW}This command causes CSS and formatting issues.${NC}"
    echo ""
    echo -e "${GREEN}✅ Instead, use:${NC}"
    echo -e "   ${GREEN}./dev-server.sh${NC}"
    echo ""
    echo "The dev-server script:"
    echo "  • Compiles CSS properly"
    echo "  • Runs necessary postprocessors"
    echo "  • Maintains all custom formatting"
    echo "  • Prevents style loss on rebuilds"
    echo ""
    echo -e "${YELLOW}Starting ./dev-server.sh for you now...${NC}"
    echo ""
    
    # Start the correct server
    exec ./dev-server.sh
else
    # For all other mdbook commands (build, clean, etc.), pass through
    exec /usr/local/bin/mdbook "$@"
fi