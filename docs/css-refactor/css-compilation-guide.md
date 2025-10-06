# CSS Compilation Guide

## Overview

As of September 2025, the City of Rivergrove documentation site uses a **compiled CSS approach** to solve the recurring issue of CSS files being deleted during mdBook builds.

## The Problem We Solved

Previously, our modular CSS architecture (with files in `theme/css/`) would get deleted every time mdBook rebuilt because:
1. mdBook cleans the `book/` directory on every build
2. mdBook doesn't know about our custom `theme/` directory
3. Manual copying of CSS files after builds was unreliable

## The Solution: CSS Compilation

We now compile all modular CSS files into a single `custom.css` file that mdBook handles natively.

### How It Works

1. **Source Files**: CSS modules remain in `theme/css/` for organization
2. **Compilation**: `scripts/build/compile-css.py` combines all modules into one file
3. **Output**: Creates `custom.css` in the root (mdBook copies this automatically)
4. **Persistence**: The compiled CSS survives mdBook rebuilds

### CSS Module Structure

```
theme/css/
├── base/
│   ├── variables.css      # CSS custom properties
│   └── typography.css     # Base typography
├── layout/
│   ├── mdbook-overrides.css
│   ├── page-structure.css
│   └── responsive.css
├── components/
│   ├── cards.css
│   ├── footnotes.css
│   ├── tables.css
│   ├── navigation.css
│   ├── relationships-panel.css
│   ├── form-controls.css
│   └── form-fields.css
├── documents/
│   ├── document-notes.css
│   └── enhanced-elements.css
├── main.css               # Import manifest (for reference)
└── rivergrove-typography.css
```

## Using the CSS Compilation

### Automatic Compilation

The CSS is automatically compiled in these scenarios:

1. **During builds**: `./build-all.sh` compiles CSS before mdBook build
2. **In dev server**: `./dev-server.sh` recompiles when CSS files change
3. **Quick fix**: `./scripts/fix-styles.sh` recompiles CSS

### Manual Compilation

To manually compile CSS:

```bash
python3 scripts/build/compile-css.py
```

This will:
- Read all CSS modules from `theme/css/`
- Combine them in the correct order
- Output to `custom.css` and `book/custom.css`

## Making CSS Changes

### Step 1: Edit Source Files

Always edit the source files in `theme/css/`, never the compiled `custom.css`:

```bash
# Example: Edit navigation styles
vim theme/css/components/navigation.css
```

### Step 2: Compile Changes

Run the compilation:

```bash
python3 scripts/build/compile-css.py
```

### Step 3: Verify

Check that your changes are in the compiled output:

```bash
grep "your-new-style" book/custom.css
```

## Important Notes

### Never Edit custom.css Directly

The root `custom.css` and `book/custom.css` are auto-generated. Any direct edits will be lost on the next compilation.

### CSS Import Order

The compilation script maintains a specific order:
1. Google Fonts imports (preserved)
2. Variables and base styles
3. Layout overrides
4. Components
5. Document-specific styles
6. Typography overrides

### File @import Statements

The compilation process:
- Removes file @import statements (files are inlined)
- Preserves external @imports (like Google Fonts)
- Prevents duplicate Google Font imports

## Troubleshooting

### Styles Not Appearing

1. Run compilation: `python3 scripts/build/compile-css.py`
2. Run postprocessors: 
   ```bash
   python3 scripts/postprocessing/custom-list-processor.py
   python3 scripts/postprocessing/enhanced-custom-processor.py
   ```
3. Clear browser cache and refresh

### Compilation Errors

If compilation fails:
1. Check for syntax errors in source CSS files
2. Verify all referenced files exist in `theme/css/`
3. Check the import order in the compilation script

### CSS Not Updating

If changes aren't reflected:
1. Ensure you edited files in `theme/css/`, not `book/`
2. Run compilation after edits
3. If using dev server, it should auto-compile on CSS changes

## Benefits of This Approach

1. **Reliability**: CSS always persists through mdBook builds
2. **Performance**: Single CSS file loads faster than multiple imports
3. **Maintainability**: Source files stay modular and organized
4. **Compatibility**: Works with mdBook's standard build process
5. **No Manual Steps**: No need to manually copy theme directories

## Migration Notes

When this system was implemented (September 2025), we:
- Kept all source CSS files in `theme/css/` unchanged
- Created the compilation script to combine them
- Updated all build scripts to use compilation instead of copying
- The old `@import url('./theme/css/main.css')` approach is no longer used

## Testing CSS Changes

After making CSS changes, use visual regression testing to catch unintended layout changes:

```bash
# Before making CSS changes
npm run test:visual

# Make changes, compile, rebuild
python3 scripts/build/compile-css.py
./build-all.sh

# Check for visual regressions
npm run test:visual

# Review differences
npm run test:visual:ui
```

See [Visual Testing Guide](../visual-testing-guide.md) for complete workflow.

## Related Documentation

- [CSS Architecture Overview](./README.md)
- [Build System Documentation](../build-architecture.md)
- [Development Server Guide](../mdbook-guide.md#development-server)
- [Visual Testing Guide](../visual-testing-guide.md)