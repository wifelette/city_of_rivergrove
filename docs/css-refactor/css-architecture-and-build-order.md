# CSS Architecture and Build Order Documentation

## The Problem We Discovered

When making CSS changes, files in `book/theme/css/` were repeatedly disappearing. This was caused by the mdBook build process which cleans/overwrites the `book/` directory on each build.

## Root Cause

1. **mdBook's default behavior**: When `mdbook build` runs, it cleans and regenerates the entire `book/` directory
2. **CSS imports expect files in book/**: The `book/custom.css` file imports from `./theme/css/main.css` (relative to book/)
3. **Build script copies theme AFTER build**: The `build-all.sh` script copies the theme directory to book/ AFTER running mdbook build
4. **Dev server auto-rebuilds**: When mdBook detects changes, it auto-rebuilds, wiping out manually copied CSS files

## The Correct CSS Architecture

### File Locations

```
city_of_rivergrove/
├── theme/                    # SOURCE CSS FILES (edit these!)
│   └── css/
│       ├── main.css         # Main entry point
│       ├── base/            # Variables and typography
│       ├── layout/          # Page structure
│       ├── components/      # UI components
│       └── documents/       # Document-specific styles
├── book/                     # GENERATED OUTPUT (never edit!)
│   ├── custom.css           # Imports ./theme/css/main.css
│   └── theme/               # COPIED from root theme/ by build scripts
│       └── css/
└── src/                      # mdBook source files
```

### Key Principles

1. **NEVER edit files in book/** - They will be overwritten on next build
2. **ALWAYS edit files in theme/** - These are the source files
3. **Build scripts copy theme/ to book/** - This happens AFTER mdbook build
4. **The copy must happen after EVERY mdbook build** - Including auto-rebuilds

## Build Order and CSS Handling

### build-all.sh Process

```bash
# Step 10: Build mdBook (cleans book/ directory!)
mdbook build

# Step 11: Copy theme and other assets (MUST be after build)
cp -r theme book/
cp navigation-standalone.js book/
cp src/relationships.json book/

# Step 12-13: Apply postprocessing (modifies HTML in book/)
python3 scripts/postprocessing/custom-list-processor.py
python3 scripts/postprocessing/enhanced-custom-processor.py
```

### dev-server.sh Process

The dev server handles this correctly:
1. Runs initial `build-all.sh` which copies theme
2. Starts `mdbook serve` (which auto-rebuilds on changes)
3. When CSS changes detected, copies theme to book/
4. Runs postprocessors after each rebuild

## Common Issues and Solutions

### Issue 1: CSS not loading (404 error)
**Symptom**: Console shows 404 for `/theme/css/main.css`
**Cause**: Theme directory not copied to book/ after mdbook build
**Solution**: Run `cp -r theme book/` or use build scripts

### Issue 2: CSS changes not appearing
**Symptom**: Edit CSS but changes don't show in browser
**Cause**: Editing files in book/ instead of theme/
**Solution**: Edit files in theme/ and let build scripts copy them

### Issue 3: CSS disappears after refresh
**Symptom**: CSS works, then disappears after mdBook auto-rebuild
**Cause**: mdBook cleaned book/ but theme wasn't re-copied
**Solution**: Use dev-server.sh which handles this automatically

## Recommended Workflow

### For CSS Development

1. **Always use dev-server.sh** for development:
   ```bash
   ./dev-server.sh
   ```
   This handles all copying and rebuilding automatically.

2. **Edit CSS files in theme/ directory**:
   ```bash
   # Edit source files
   vim theme/css/components/form-fields.css
   ```

3. **Never manually copy to book/**:
   The dev server watches for CSS changes and copies automatically.

### For Production Builds

Use `build-all.sh` which handles the complete process:
```bash
./build-all.sh
```

### Manual CSS Updates (Emergency Only)

If you must manually update CSS without rebuilding:
```bash
# Copy theme to book
cp -r theme book/

# Run postprocessors to apply classes
python3 scripts/postprocessing/custom-list-processor.py
python3 scripts/postprocessing/enhanced-custom-processor.py
```

## Testing CSS Changes

### Quick Test
1. Edit CSS in `theme/css/`
2. If using dev-server.sh, changes auto-apply
3. If using mdbook serve, manually run: `cp -r theme book/`

### Full Test
```bash
# Full rebuild with all processing
./build-all.sh

# Verify CSS loads
open http://localhost:3000
# Check browser console for 404 errors
```

## Prevention Measures

### Current Safeguards
- dev-server.sh automatically copies theme after detecting CSS changes
- build-all.sh copies theme after mdbook build
- Both scripts run postprocessors after copying

### Recommended Improvements
1. Add a pre-build hook to mdBook that preserves theme/
2. Consider using symlinks instead of copying (but test cross-platform)
3. Add automated tests to verify CSS loads correctly
4. Add warning comments in book/theme/ files: "DO NOT EDIT - Generated from /theme/"

## Summary

The CSS architecture is designed to separate source files (theme/) from generated output (book/). The build process must:
1. Build mdBook (which cleans book/)
2. Copy theme/ to book/theme/
3. Run postprocessors

This order is critical and must be maintained in all build scripts and development workflows.