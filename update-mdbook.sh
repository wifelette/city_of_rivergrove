#!/bin/bash
# Sync all documents and rebuild mdBook

echo "🔄 Syncing documents to src/ folders..."

echo "  📄 Syncing ordinances..."
python3 sync-ordinances.py

echo "  📄 Syncing resolutions..."
if [ -d "Resolutions" ]; then
    mkdir -p src/resolutions
    updated=0
    # Copy all .md files, removing # from filenames
    for file in Resolutions/*.md; do
        if [ -f "$file" ]; then
            filename=$(basename "$file" | sed 's/#//g')
            dest="src/resolutions/$filename"
            # Check if file needs updating
            if [ ! -f "$dest" ] || ! cmp -s "$file" "$dest"; then
                cp "$file" "$dest"
                echo "    ✓ Updated: $filename"
                ((updated++))
            fi
        fi
    done
    # Remove files that no longer exist in source
    for dest in src/resolutions/*.md; do
        if [ -f "$dest" ]; then
            filename=$(basename "$dest")
            # Check if source exists (need to add # back for some files)
            source_file="Resolutions/$filename"
            source_file_with_hash="Resolutions/$(echo "$filename" | sed 's/\([0-9]\{4\}-Res-\)\([0-9]\)/\1#\2/')"
            if [ ! -f "$source_file" ] && [ ! -f "$source_file_with_hash" ]; then
                rm "$dest"
                echo "    ✗ Removed: $filename"
                ((updated++))
            fi
        fi
    done
    if [ $updated -eq 0 ]; then
        echo "    No changes needed ($(ls -1 Resolutions/*.md 2>/dev/null | wc -l | tr -d ' ') files already in sync)"
    fi
fi

echo "  📄 Syncing interpretations..."
if [ -d "Interpretations" ]; then
    mkdir -p src/interpretations
    updated=0
    # Copy all .md files
    for file in Interpretations/*.md; do
        if [ -f "$file" ]; then
            filename=$(basename "$file")
            dest="src/interpretations/$filename"
            if [ ! -f "$dest" ] || ! cmp -s "$file" "$dest"; then
                cp "$file" "$dest"
                echo "    ✓ Updated: $filename"
                ((updated++))
            fi
        fi
    done
    # Remove files that no longer exist in source
    for dest in src/interpretations/*.md; do
        if [ -f "$dest" ]; then
            filename=$(basename "$dest")
            if [ ! -f "Interpretations/$filename" ]; then
                rm "$dest"
                echo "    ✗ Removed: $filename"
                ((updated++))
            fi
        fi
    done
    if [ $updated -eq 0 ]; then
        echo "    No changes needed ($(ls -1 Interpretations/*.md 2>/dev/null | wc -l | tr -d ' ') files already in sync)"
    fi
fi

echo "  📄 Syncing other documents..."
if [ -d "Other" ]; then
    mkdir -p src/other
    updated=0
    # Copy all .md files
    for file in Other/*.md; do
        if [ -f "$file" ]; then
            filename=$(basename "$file")
            dest="src/other/$filename"
            if [ ! -f "$dest" ] || ! cmp -s "$file" "$dest"; then
                cp "$file" "$dest"
                echo "    ✓ Updated: $filename"
                ((updated++))
            fi
        fi
    done
    # Remove files that no longer exist in source
    for dest in src/other/*.md; do
        if [ -f "$dest" ]; then
            filename=$(basename "$dest")
            if [ ! -f "Other/$filename" ]; then
                rm "$dest"
                echo "    ✗ Removed: $filename"
                ((updated++))
            fi
        fi
    done
    if [ $updated -eq 0 ]; then
        echo "    No changes needed ($(ls -1 Other/*.md 2>/dev/null | wc -l | tr -d ' ') files already in sync)"
    fi
fi

echo "  📝 Processing footnotes..."
python3 footnote-preprocessor.py
echo "  ✓ Footnotes processed"

echo "  📋 Regenerating SUMMARY.md..."
python3 generate-summary.py
echo "  ✓ Table of contents updated"

echo "📚 Rebuilding mdBook..."
mdbook build

echo "  🎨 Applying custom formatting..."
python3 custom-list-processor.py

echo "✅ Done! Your changes should now be visible at http://localhost:3000"
