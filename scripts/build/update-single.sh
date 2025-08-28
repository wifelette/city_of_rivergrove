#!/bin/bash
# Sync a single document to src/ and rebuild mdBook
# Usage: ./update-single.sh <path/to/file.md>

if [ $# -eq 0 ]; then
    echo "Usage: ./update-single.sh <path/to/file.md>"
    echo "Example: ./update-single.sh Resolutions/2024-Res-#300-Fee-Schedule-Modification.md"
    exit 1
fi

SOURCE_FILE="$1"

if [ ! -f "$SOURCE_FILE" ]; then
    echo "Error: File not found: $SOURCE_FILE"
    exit 1
fi

# Determine the directory and destination based on the source path
if [[ "$SOURCE_FILE" == Ordinances/*.md ]]; then
    DEST_DIR="src/ordinances"
    PREFIX="Ordinances/"
elif [[ "$SOURCE_FILE" == Resolutions/*.md ]]; then
    DEST_DIR="src/resolutions"
    PREFIX="Resolutions/"
elif [[ "$SOURCE_FILE" == Interpretations/*.md ]]; then
    DEST_DIR="src/interpretations"
    PREFIX="Interpretations/"
elif [[ "$SOURCE_FILE" == Other/*.md ]]; then
    DEST_DIR="src/other"
    PREFIX="Other/"
else
    echo "Error: File must be in Ordinances/, Resolutions/, Interpretations/, or Other/ directory"
    exit 1
fi

# Get filename and remove # character for destination
FILENAME=$(basename "$SOURCE_FILE")
DEST_FILENAME=$(echo "$FILENAME" | sed 's/#//g')
DEST_FILE="$DEST_DIR/$DEST_FILENAME"

# Create destination directory if it doesn't exist
mkdir -p "$DEST_DIR"

# Copy the file
echo "📄 Syncing $SOURCE_FILE -> $DEST_FILE"
cp "$SOURCE_FILE" "$DEST_FILE"

# Run the footnote preprocessor on just this file
echo "📝 Processing footnotes..."
python3 scripts/preprocessing/footnote-preprocessor.py "$DEST_FILE" 2>/dev/null || true

# Run the special list preprocessor for document-specific list handling
echo "📝 Processing special lists..."
python3 scripts/preprocessing/special-lists-preprocessor.py "$DEST_FILE" 2>/dev/null || true

# Regenerate SUMMARY.md (needed to include new files)
echo "📋 Regenerating SUMMARY.md..."
python3 scripts/mdbook/generate-summary.py

# Regenerate relationships.json (needed for navigation)
echo "🔗 Generating relationships.json..."
python3 scripts/mdbook/generate-relationships.py

# Rebuild mdBook
echo "📚 Rebuilding mdBook..."
mdbook build

# Apply custom formatting
echo "🎨 Applying custom formatting..."
python3 scripts/postprocessing/custom-list-processor.py

# Apply enhanced formatting if available
if [ -f "scripts/postprocessing/enhanced-custom-processor.py" ]; then
    echo "✨ Applying enhanced document-specific formatting..."
    python3 scripts/postprocessing/enhanced-custom-processor.py
fi

echo "✅ Done! Your changes should now be visible at http://localhost:3000"