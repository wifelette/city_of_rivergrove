#!/bin/bash
# Enhanced mdBook update script with special formatting support
# This version uses both standard and enhanced processing for better document display

echo "🔄 Enhanced mdBook sync and build process..."
echo ""

# Step 1: Sync all documents to src/ folders
echo "📄 Step 1: Syncing documents to src/ folders..."

echo "  📄 Syncing ordinances..."
python3 scripts/preprocessing/sync-ordinances.py

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

echo ""
echo "📝 Step 2: Processing footnotes..."
python3 scripts/preprocessing/footnote-preprocessor.py
echo "  ✓ Footnotes processed"

echo ""
echo "📋 Step 3: Regenerating SUMMARY.md..."
python3 scripts/mdbook/generate-summary.py
echo "  ✓ Table of contents updated"

echo ""
echo "📚 Step 4: Building mdBook..."
mdbook build

echo ""
echo "🎨 Step 5: Applying standard list formatting..."
python3 scripts/postprocessing/custom-list-processor.py

echo ""
echo "✨ Step 6: Applying enhanced document-specific formatting..."
if [ -f "scripts/postprocessing/enhanced-custom-processor.py" ]; then
    python3 scripts/postprocessing/enhanced-custom-processor.py
else
    echo "  ⚠️  Enhanced processor not found, skipping..."
fi

echo ""
echo "🎯 Step 7: Copying special formatting CSS..."
if [ -f "scripts/config/special-formatting.css" ]; then
    # Check if book directory exists
    if [ -d "book" ]; then
        # Copy CSS to book directory
        cp scripts/config/special-formatting.css book/
        echo "  ✓ Special formatting CSS copied to book/"
        
        # Also inject link into HTML files if not already present
        for html_file in book/*.html book/**/*.html; do
            if [ -f "$html_file" ]; then
                # Check if the CSS link is already present
                if ! grep -q "special-formatting.css" "$html_file"; then
                    # Add link to special-formatting.css in the head section
                    sed -i.bak '/<\/head>/i\
    <link rel="stylesheet" href="/special-formatting.css">' "$html_file"
                fi
            fi
        done
        echo "  ✓ CSS links injected into HTML files"
        
        # Clean up backup files
        find book -name "*.bak" -delete
    else
        echo "  ⚠️  Book directory not found"
    fi
else
    echo "  ⚠️  Special formatting CSS not found"
fi

echo ""
echo "✅ Enhanced build complete!"
echo ""
echo "📊 Summary:"
echo "  • Documents synced to src/"
echo "  • Footnotes processed"
echo "  • Table of contents regenerated"
echo "  • mdBook built"
echo "  • Standard list formatting applied"
echo "  • Enhanced document-specific formatting applied"
echo "  • Special CSS styling injected"
echo ""
echo "🌐 Your enhanced site is ready at http://localhost:3000"
echo ""
echo "💡 Tips:"
echo "  • Documents with tables now have enhanced styling"
echo "  • WHEREAS clauses are specially formatted"
echo "  • Definition lists (like in Sign Ordinance) have custom styling"
echo "  • Complex nested lists preserve legal enumeration"
echo "  • Fee schedule tables are responsive and styled"