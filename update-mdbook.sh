#!/bin/bash
# Script to automatically update mdBook when new documents are added
# This handles copying files to src/ and updating SUMMARY.md

echo "🔄 Updating mdBook with new documents..."

# Function to sync markdown files from a directory to src/
sync_directory() {
    local source_dir=$1
    local dest_dir=$2
    
    echo "Syncing $source_dir to $dest_dir..."
    
    # Create destination directory if it doesn't exist
    mkdir -p "$dest_dir"
    
    # Remove old files first (but not symlinks)
    find "$dest_dir" -type f -name "*.md" -exec rm {} \;
    
    # Copy all markdown files, excluding any that start with a dot
    for file in "$source_dir"/*.md; do
        if [ -f "$file" ]; then
            basename=$(basename "$file")
            # Skip hidden files and special files
            if [[ ! "$basename" =~ ^\. ]]; then
                # Remove # from filenames and replace spaces with hyphens for mdBook compatibility
                clean_name="${basename//#/}"
                clean_name="${clean_name// /-}"
                cp "$file" "$dest_dir/$clean_name"
                echo "  ✓ Copied $basename -> $clean_name"
            fi
        fi
    done
}

# Sync all document directories
sync_directory "Ordinances" "src/ordinances"
sync_directory "Resolutions" "src/resolutions"
sync_directory "Interpretations" "src/interpretations"
sync_directory "Transcripts" "src/transcripts"

echo ""
echo "🔧 Fixing signature formatting..."
python3 fix-signatures.py

echo ""
echo "📝 Generating SUMMARY.md..."
python3 generate-summary.py

echo ""
echo "🏗️ Building mdBook..."

# Build the book with cross-references
./build.sh

echo ""
echo "✅ mdBook update complete!"
echo ""
echo "To view locally, run: mdbook serve"