#!/bin/bash
# Simplified single-file update for City of Rivergrove mdBook site
# This replaces: update-single.sh
# Usage: ./build-one.sh <file-path>
# Example: ./build-one.sh source-documents/Ordinances/1974-Ord-#16-Parks.md

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check arguments
if [ $# -eq 0 ]; then
    echo -e "${RED}Error: No file specified${NC}"
    echo ""
    echo "Usage: ./build-one.sh <file-path>"
    echo ""
    echo "Examples:"
    echo "  ./build-one.sh source-documents/Ordinances/1974-Ord-#16-Parks.md"
    echo "  ./build-one.sh source-documents/Resolutions/2024-Res-#300-Fee-Schedule.md"
    echo "  ./build-one.sh source-documents/Interpretations/2023-06-15-RE-Section-5-Zoning.md"
    exit 1
fi

SOURCE_FILE="$1"
FILENAME=$(basename "$SOURCE_FILE")

# Check if file exists
if [ ! -f "$SOURCE_FILE" ]; then
    echo -e "${RED}Error: File not found: $SOURCE_FILE${NC}"
    exit 1
fi

echo -e "${BLUE}📄 Single File Update${NC}"
echo "====================="
echo "File: $FILENAME"
echo ""

# Determine document type and sync accordingly
echo "🔄 Step 1: Syncing file to /src..."

if [[ "$SOURCE_FILE" == source-documents/Ordinances/* ]]; then
    echo "  Type: Ordinance"
    python3 scripts/preprocessing/sync-ordinances.py
    DEST_DIR="src/ordinances"
    
elif [[ "$SOURCE_FILE" == source-documents/Resolutions/* ]]; then
    echo "  Type: Resolution"
    python3 scripts/preprocessing/sync-resolutions.py
    DEST_DIR="src/resolutions"
    
elif [[ "$SOURCE_FILE" == source-documents/Interpretations/* ]]; then
    echo "  Type: Interpretation"
    python3 scripts/preprocessing/sync-interpretations.py
    DEST_DIR="src/interpretations"
    
elif [[ "$SOURCE_FILE" == source-documents/Other/* ]]; then
    echo "  Type: Other Document"
    python3 scripts/preprocessing/sync-other.py
    DEST_DIR="src/other"
    
elif [[ "$SOURCE_FILE" == source-documents/Meetings/* ]]; then
    echo "  Type: Meeting Document"
    python3 scripts/preprocessing/sync-meetings.py
    
    # Determine specific type for destination
    if [[ "$FILENAME" == *Agenda* ]]; then
        DEST_DIR="src/agendas"
    elif [[ "$FILENAME" == *Minutes* ]]; then
        DEST_DIR="src/minutes"
    elif [[ "$FILENAME" == *Transcript* ]]; then
        DEST_DIR="src/transcripts"
    else
        echo -e "${RED}Error: Unknown meeting document type in $FILENAME${NC}"
        exit 1
    fi
    
else
    echo -e "${RED}Error: File must be in a recognized source-documents/ subdirectory${NC}"
    echo "  Supported: Ordinances/, Resolutions/, Interpretations/, Other/, Meetings/"
    exit 1
fi

# Get destination filename (remove # if present)
DEST_FILENAME=$(echo "$FILENAME" | sed 's/#//g')
DEST_FILE="$DEST_DIR/$DEST_FILENAME"

echo -e "  ${GREEN}✓ Synced to $DEST_FILE${NC}"
echo ""

# Validate form field syntax
echo "🔍 Step 2: Validating form fields..."
if python3 scripts/validation/validate-form-fields.py "$SOURCE_FILE" --quiet 2>/dev/null; then
    echo -e "  ${GREEN}✓ Form fields valid${NC}"
else
    echo -e "  ${RED}✗ Form field errors found!${NC}"
    echo ""
    # Show detailed errors
    python3 scripts/validation/validate-form-fields.py "$SOURCE_FILE"
    echo ""
    echo -e "${YELLOW}Fix the errors above and try again${NC}"
    exit 1
fi
echo ""

# Process the specific file through the pipeline
echo "🔧 Step 3: Processing file..."

# Only run if file exists in destination
if [ -f "$DEST_FILE" ]; then
    # Footnotes
    echo -n "  • Footnotes... "
    python3 scripts/preprocessing/footnote-preprocessor.py "$DEST_FILE" 2>/dev/null || true
    echo -e "${GREEN}✓${NC}"
    
    # Auto-links
    echo -n "  • URL/Email links... "
    python3 scripts/preprocessing/auto-link-converter.py "$DEST_FILE" 2>/dev/null || true
    echo -e "${GREEN}✓${NC}"
fi

# Cross-references (needs to scan all files)
echo -n "  • Cross-references... "
python3 scripts/mdbook/add-cross-references.py >/dev/null 2>&1
echo -e "${GREEN}✓${NC}"

echo ""

# Regenerate only what's needed
echo "📋 Step 4: Updating indexes..."

echo -n "  • Table of contents... "
python3 scripts/mdbook/generate-summary-with-airtable.py >/dev/null 2>&1
echo -e "${GREEN}✓${NC}"

echo -n "  • Relationships... "
python3 scripts/mdbook/generate-relationships.py >/dev/null 2>&1
# Copy to book directory for navigation to use
cp src/relationships.json book/relationships.json 2>/dev/null || true
echo -e "${GREEN}✓${NC}"

# Check if this is a meeting document
if [[ "$SOURCE_FILE" == source-documents/Meetings/* ]]; then
    if [ -f "scripts/mdbook/sync-meetings-metadata.py" ]; then
        echo -n "  • Meeting metadata... "
        python3 scripts/mdbook/sync-meetings-metadata.py >/dev/null 2>&1
        if [ -f "book/meetings-metadata.json" ]; then
            cp book/meetings-metadata.json src/ 2>/dev/null
        fi
        echo -e "${GREEN}✓${NC}"
    fi
else
    # Update just this file in Airtable metadata (if available)
    if [ -f "scripts/mdbook/sync-airtable-metadata.py" ]; then
        echo -n "  • Airtable metadata... "
        if python3 scripts/mdbook/sync-airtable-metadata.py --mode=single --file="$FILENAME" --create-if-missing >/dev/null 2>&1; then
            if [ -f "book/airtable-metadata.json" ]; then
                cp book/airtable-metadata.json src/ 2>/dev/null
            fi
            echo -e "${GREEN}✓${NC}"
        else
            echo -e "${YELLOW}skipped${NC}"
        fi
    fi
fi

echo ""

# Rebuild mdBook
echo "📚 Step 5: Rebuilding mdBook..."
mdbook build >/dev/null 2>&1
echo -e "  ${GREEN}✓ Built${NC}"

# Copy images, theme, and navigation to book directory
if [ -d "images" ]; then
    cp -r images book/ 2>/dev/null
fi
if [ -d "theme" ]; then
    cp -r theme book/ 2>/dev/null
fi
if [ -f "navigation-standalone.js" ]; then
    cp navigation-standalone.js book/ 2>/dev/null
fi
echo ""

# Apply postprocessing
echo "🎨 Step 6: Applying custom formatting..."
python3 scripts/postprocessing/unified-list-processor.py >/dev/null 2>&1
if [ -f "scripts/postprocessing/enhanced-custom-processor.py" ]; then
    python3 scripts/postprocessing/enhanced-custom-processor.py >/dev/null 2>&1
fi
echo -e "  ${GREEN}✓ Formatted${NC}"
echo ""

# Done!
echo "====================="
echo -e "${GREEN}✅ Update complete!${NC}"
echo ""
echo "📖 View at: http://localhost:3000"

# Check if mdbook serve is running
if pgrep -f "mdbook serve" > /dev/null; then
    echo -e "${GREEN}✓ Server is running - refresh your browser to see changes${NC}"
else
    echo -e "${YELLOW}⚠️  Server is not running!${NC}"
    echo "   Run ./dev-server.sh to start the development server"
fi