#!/bin/bash
# Sync all documents and rebuild mdBook

echo "🔄 Syncing documents to src/ folders..."

echo "  📄 Syncing ordinances..."
python3 sync-ordinances.py

echo "  📄 Syncing resolutions..."
if [ -d "Resolutions" ]; then
    mkdir -p src/resolutions
    # Remove existing files
    rm -f src/resolutions/*.md 2>/dev/null
    # Copy all .md files, removing # from filenames
    for file in Resolutions/*.md; do
        if [ -f "$file" ]; then
            filename=$(basename "$file" | sed 's/#//g')
            cp "$file" "src/resolutions/$filename"
        fi
    done
    echo "  ✓ Resolutions synced"
fi

echo "  📄 Syncing interpretations..."
if [ -d "Interpretations" ]; then
    mkdir -p src/interpretations
    # Remove existing files
    rm -f src/interpretations/*.md 2>/dev/null
    # Copy all .md files
    for file in Interpretations/*.md; do
        if [ -f "$file" ]; then
            cp "$file" "src/interpretations/"
        fi
    done
    echo "  ✓ Interpretations synced"
fi

echo "  📄 Syncing other documents..."
if [ -d "Other" ]; then
    mkdir -p src/other
    # Remove existing files
    rm -f src/other/*.md 2>/dev/null
    # Copy all .md files
    for file in Other/*.md; do
        if [ -f "$file" ]; then
            cp "$file" "src/other/"
        fi
    done
    echo "  ✓ Other documents synced"
fi

echo "📚 Rebuilding mdBook..."
mdbook build

echo "✅ Done! Your changes should now be visible at http://localhost:3000"
