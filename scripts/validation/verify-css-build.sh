#!/bin/bash
# Verify CSS files are properly built and accessible
# This catches the common issue of theme files not being copied to book/

set -e

echo "🔍 Verifying CSS Build Configuration"
echo "===================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track if any issues found
ISSUES_FOUND=false

# Check 1: Verify source theme directory exists
echo "1. Checking source theme directory..."
if [ -d "theme/css" ]; then
    echo -e "   ${GREEN}✓ theme/css/ exists${NC}"
    FILE_COUNT=$(find theme/css -name "*.css" | wc -l | tr -d ' ')
    echo "     Found $FILE_COUNT CSS files"
else
    echo -e "   ${RED}✗ theme/css/ directory missing!${NC}"
    ISSUES_FOUND=true
fi
echo ""

# Check 2: Verify book directory exists
echo "2. Checking book directory..."
if [ -d "book" ]; then
    echo -e "   ${GREEN}✓ book/ directory exists${NC}"
else
    echo -e "   ${YELLOW}⚠ book/ directory missing (run build first)${NC}"
    echo "     Run: ./build-all.sh"
    exit 1
fi
echo ""

# Check 3: Verify custom.css exists and has correct import
echo "3. Checking book/custom.css..."
if [ -f "book/custom.css" ]; then
    echo -e "   ${GREEN}✓ book/custom.css exists${NC}"
    
    # Check for the import statement
    if grep -q "@import url('./theme/css/main.css')" book/custom.css; then
        echo -e "   ${GREEN}✓ Import path is correct${NC}"
    else
        echo -e "   ${RED}✗ Import path is incorrect!${NC}"
        echo "     Expected: @import url('./theme/css/main.css');"
        echo "     Found:"
        grep "@import" book/custom.css | head -1 | sed 's/^/     /'
        ISSUES_FOUND=true
    fi
else
    echo -e "   ${RED}✗ book/custom.css missing!${NC}"
    ISSUES_FOUND=true
fi
echo ""

# Check 4: Verify theme files are copied to book
echo "4. Checking if theme is copied to book..."
if [ -d "book/theme/css" ]; then
    echo -e "   ${GREEN}✓ book/theme/css/ exists${NC}"
    BOOK_FILE_COUNT=$(find book/theme/css -name "*.css" | wc -l | tr -d ' ')
    echo "     Found $BOOK_FILE_COUNT CSS files"
    
    # Verify main.css specifically
    if [ -f "book/theme/css/main.css" ]; then
        echo -e "   ${GREEN}✓ book/theme/css/main.css exists${NC}"
    else
        echo -e "   ${RED}✗ book/theme/css/main.css missing!${NC}"
        ISSUES_FOUND=true
    fi
else
    echo -e "   ${RED}✗ book/theme/css/ missing!${NC}"
    echo "     Theme files not copied to book directory"
    echo "     Run: cp -r theme book/"
    ISSUES_FOUND=true
fi
echo ""

# Check 5: Verify critical CSS files
echo "5. Checking critical CSS modules..."
CRITICAL_FILES=(
    "base/variables.css"
    "base/typography.css"
    "components/form-fields.css"
    "documents/document-notes.css"
    "documents/enhanced-elements.css"
)

for file in "${CRITICAL_FILES[@]}"; do
    if [ -f "book/theme/css/$file" ]; then
        echo -e "   ${GREEN}✓ $file${NC}"
    else
        echo -e "   ${RED}✗ $file missing${NC}"
        ISSUES_FOUND=true
    fi
done
echo ""

# Check 6: Test if CSS would load in browser
echo "6. Testing CSS accessibility..."
if [ -f "book/theme/css/main.css" ] && [ -f "book/custom.css" ]; then
    # Check if server is running
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/custom.css | grep -q "200\|304"; then
        echo -e "   ${GREEN}✓ custom.css is accessible${NC}"
        
        if curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/theme/css/main.css | grep -q "200\|304"; then
            echo -e "   ${GREEN}✓ theme/css/main.css is accessible${NC}"
        else
            echo -e "   ${YELLOW}⚠ theme/css/main.css not accessible via server${NC}"
            echo "     (This might be normal if server isn't running)"
        fi
    else
        echo -e "   ${YELLOW}⚠ Server not running, cannot test accessibility${NC}"
        echo "     Run: ./dev-server.sh"
    fi
else
    echo -e "   ${RED}✗ Cannot test - files missing${NC}"
fi
echo ""

# Check 7: Verify build scripts have correct order
echo "7. Checking build script order..."
if [ -f "build-all.sh" ]; then
    # Check if theme copy comes after mdbook build
    BUILD_LINE=$(grep -n "mdbook build" build-all.sh | cut -d: -f1 | head -1)
    THEME_LINE=$(grep -n "cp -r theme book" build-all.sh | cut -d: -f1 | head -1)
    
    if [ -n "$BUILD_LINE" ] && [ -n "$THEME_LINE" ]; then
        if [ "$THEME_LINE" -gt "$BUILD_LINE" ]; then
            echo -e "   ${GREEN}✓ Theme copy happens AFTER mdbook build (correct)${NC}"
        else
            echo -e "   ${RED}✗ Theme copy happens BEFORE mdbook build (wrong!)${NC}"
            echo "     This will cause CSS to be deleted on build"
            ISSUES_FOUND=true
        fi
    else
        echo -e "   ${YELLOW}⚠ Could not verify build order${NC}"
    fi
else
    echo -e "   ${YELLOW}⚠ build-all.sh not found${NC}"
fi
echo ""

# Summary
echo "===================================="
if [ "$ISSUES_FOUND" = true ]; then
    echo -e "${RED}❌ CSS build verification FAILED${NC}"
    echo ""
    echo "To fix:"
    echo "1. Run: ./build-all.sh"
    echo "2. Or manually: cp -r theme book/"
    echo ""
    echo "For more info, see: docs/css-architecture-and-build-order.md"
    exit 1
else
    echo -e "${GREEN}✅ CSS build verification PASSED${NC}"
    echo ""
    echo "All CSS files are properly configured and accessible."
fi