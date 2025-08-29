#!/bin/bash
# Sync a single document to src/ and rebuild mdBook
# Usage: ./update-single.sh <path/to/file.md>

if [ $# -eq 0 ]; then
    echo "Usage: ./update-single.sh <path/to/file.md>"
    echo "Example: ./update-single.sh source-documents/Resolutions/2024-Res-#300-Fee-Schedule-Modification.md"
    exit 1
fi

SOURCE_FILE="$1"

if [ ! -f "$SOURCE_FILE" ]; then
    echo "Error: File not found: $SOURCE_FILE"
    exit 1
fi

# Determine the directory and destination based on the source path
if [[ "$SOURCE_FILE" == source-documents/Ordinances/*.md ]]; then
    DEST_DIR="src/ordinances"
    PREFIX="source-documents/Ordinances/"
elif [[ "$SOURCE_FILE" == source-documents/Resolutions/*.md ]]; then
    DEST_DIR="src/resolutions"
    PREFIX="source-documents/Resolutions/"
elif [[ "$SOURCE_FILE" == source-documents/Interpretations/*.md ]]; then
    DEST_DIR="src/interpretations"
    PREFIX="source-documents/Interpretations/"
elif [[ "$SOURCE_FILE" == source-documents/Other/*.md ]]; then
    DEST_DIR="src/other"
    PREFIX="source-documents/Other/"
else
    echo "Error: File must be in source-documents/Ordinances/, source-documents/Resolutions/, source-documents/Interpretations/, or source-documents/Other/ directory"
    exit 1
fi

# Get filename and remove # character for destination
FILENAME=$(basename "$SOURCE_FILE")
DEST_FILENAME=$(echo "$FILENAME" | sed 's/#//g')
DEST_FILE="$DEST_DIR/$DEST_FILENAME"

# Create destination directory if it doesn't exist
mkdir -p "$DEST_DIR"

# Use the appropriate sync script to process the file
echo "📄 Syncing $SOURCE_FILE (with form field processing)..."
if [[ "$SOURCE_FILE" == source-documents/Ordinances/*.md ]]; then
    python3 scripts/preprocessing/sync-ordinances.py
elif [[ "$SOURCE_FILE" == source-documents/Resolutions/*.md ]]; then
    python3 scripts/preprocessing/sync-resolutions.py
elif [[ "$SOURCE_FILE" == source-documents/Interpretations/*.md ]]; then
    python3 scripts/preprocessing/sync-interpretations.py
else
    # For source-documents/Other/ files, just copy directly as they don't need form field processing
    cp "$SOURCE_FILE" "$DEST_FILE"
fi

# Run the footnote preprocessor on just this file
echo "📝 Processing footnotes..."
python3 scripts/preprocessing/footnote-preprocessor.py "$DEST_FILE" 2>/dev/null || true

# Run the auto-link converter to make URLs and emails clickable
echo "🔗 Converting URLs and emails to links..."
python3 scripts/preprocessing/auto-link-converter.py "$DEST_FILE" 2>/dev/null || true

# Add cross-references between documents
echo "🔗 Adding cross-references..."
python3 scripts/mdbook/add-cross-references.py

# Form fields are now processed during sync, no separate step needed

# Regenerate SUMMARY.md (needed to include new files)
echo "📋 Regenerating SUMMARY.md..."
python3 scripts/mdbook/generate-summary.py

# Regenerate relationships.json (needed for navigation)
echo "🔗 Generating relationships.json..."
python3 scripts/mdbook/generate-relationships.py

# Update Airtable metadata for this single file
echo "🔗 Updating Airtable metadata for $FILENAME..."
python3 scripts/mdbook/sync-airtable-metadata.py --mode=single --file="$FILENAME" --create-if-missing

# Copy metadata to src directory so it's served by mdBook
if [ -f "book/airtable-metadata.json" ]; then
    cp book/airtable-metadata.json src/
fi

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