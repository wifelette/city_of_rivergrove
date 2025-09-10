#!/bin/bash
# Pre-commit hook to prevent committing files from book/ directory
# Install by running: ./scripts/hooks/install-hooks.sh

# Colors for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if any staged files are in book/ directory
BOOK_FILES=$(git diff --cached --name-only | grep "^book/" || true)

if [ -n "$BOOK_FILES" ]; then
    echo -e "${RED}❌ ERROR: Attempting to commit generated files from book/ directory!${NC}"
    echo ""
    echo "The following files should NOT be committed:"
    echo "$BOOK_FILES" | sed 's/^/  - /'
    echo ""
    echo -e "${YELLOW}These files are auto-generated. Instead:${NC}"
    echo "1. Edit the source files in theme/css/ or source-documents/"
    echo "2. Run ./build-all.sh to regenerate"
    echo "3. Commit the source files, not the generated ones"
    echo ""
    echo "To unstage these files:"
    echo "  git reset HEAD book/"
    echo ""
    exit 1
fi

# Check if any CSS files are being committed from book/
CSS_IN_BOOK=$(git diff --cached --name-only | grep "^book/.*\.css$" || true)

if [ -n "$CSS_IN_BOOK" ]; then
    echo -e "${RED}❌ ERROR: CSS files from book/ should never be committed!${NC}"
    echo ""
    echo "Found CSS files:"
    echo "$CSS_IN_BOOK" | sed 's/^/  - /'
    echo ""
    echo "Edit CSS files in theme/css/ instead"
    exit 1
fi

exit 0