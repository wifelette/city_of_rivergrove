#!/bin/bash
# Check for direct modifications to /src files that should only be auto-generated
# This helps prevent the common mistake of editing files in /src instead of source-documents/

set -e

# Colors for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo "🔍 Checking for direct /src modifications..."

# Files that are auto-generated and should never be manually edited
GENERATED_FILES=(
    "src/SUMMARY.md"
    "src/introduction.md"
    "src/relationships.json"
    "src/airtable-metadata.json"
)

# Directories where ALL files are auto-generated from source-documents/
GENERATED_DIRS=(
    "src/ordinances/"
    "src/resolutions/"
    "src/interpretations/"
    "src/other/"
    "src/agendas/"
    "src/minutes/"
    "src/transcripts/"
)

ISSUES_FOUND=false

# Check if running in git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Not in a git repository, skipping check${NC}"
    exit 0
fi

# Check for uncommitted changes in generated files
echo "Checking for uncommitted changes in auto-generated files..."

for file in "${GENERATED_FILES[@]}"; do
    if [ -f "$file" ] && git diff --quiet HEAD -- "$file" 2>/dev/null; then
        continue
    elif [ -f "$file" ] && ! git diff --quiet HEAD -- "$file" 2>/dev/null; then
        echo -e "${RED}✗ Direct modification detected: $file${NC}"
        echo "  This file is auto-generated. Edit the source files instead."
        ISSUES_FOUND=true
    fi
done

# Check for uncommitted changes in generated directories
for dir in "${GENERATED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        # Check if there are any modified files in this directory
        if ! git diff --quiet HEAD -- "$dir" 2>/dev/null; then
            modified_files=$(git diff --name-only HEAD -- "$dir" 2>/dev/null)
            if [ -n "$modified_files" ]; then
                echo -e "${RED}✗ Direct modifications in $dir:${NC}"
                echo "$modified_files" | sed 's/^/    /'
                echo "  These files are auto-generated from source-documents/"
                echo "  Edit the original files in source-documents/ instead."
                ISSUES_FOUND=true
            fi
        fi
        
        # Check for untracked files (new files added directly to /src)
        untracked=$(git ls-files --others --exclude-standard "$dir" 2>/dev/null)
        if [ -n "$untracked" ]; then
            echo -e "${YELLOW}⚠️  New untracked files in $dir:${NC}"
            echo "$untracked" | sed 's/^/    /'
            echo "  If these are meant to be permanent, add them to source-documents/ instead."
            ISSUES_FOUND=true
        fi
    fi
done

# Provide guidance if issues found
if [ "$ISSUES_FOUND" = true ]; then
    echo ""
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}⚠️  Direct /src modifications detected!${NC}"
    echo ""
    echo "The /src directory contains auto-generated files that are"
    echo "created from source-documents/ by the build scripts."
    echo ""
    echo "To fix this:"
    echo "1. Copy your changes to the corresponding files in source-documents/"
    echo "2. Run: git checkout -- src/"
    echo "3. Run: ./build-all.sh"
    echo ""
    echo "This will regenerate /src from your source documents."
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    exit 1
else
    echo -e "${GREEN}✅ No direct /src modifications found${NC}"
fi