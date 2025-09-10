# CSS Postprocessing Migration Guide

## Overview
This document explains how CSS was migrated from inline injection in Python postprocessors to the modular CSS architecture.

## Critical Build Requirements

### Asset Copying
**IMPORTANT**: The `theme/` and `images/` directories must be copied to `book/` AFTER mdBook builds, as mdBook clears the book directory on each rebuild.

### Implementation Points

1. **build-all.sh** - Copies assets after mdBook build (Step 11)
2. **build-one.sh** - Copies assets after mdBook build  
3. **dev-server.sh** - Copies on CSS file changes
4. **custom-list-processor.py** - `copy_assets()` function ensures assets are present
5. **enhanced-custom-processor.py** - No longer injects CSS, only adds semantic classes

## Files Modified

### Python Processors
- `scripts/postprocessing/custom-list-processor.py`
  - Removed 300+ lines of inline CSS
  - Added `copy_assets()` function
  - CSS now from: `theme/css/components/form-fields.css`, `theme/css/layout/mdbook-overrides.css`

- `scripts/postprocessing/enhanced-custom-processor.py`
  - Removed 260+ lines of inline CSS for Document Notes
  - Still adds semantic classes (`document-note`, `note-type-label`, etc.)
  - CSS now from: `theme/css/documents/document-notes.css`

### Build Scripts
- Added theme/images copying to:
  - `build-all.sh` (line 168-171)
  - `build-one.sh` (line 181-183)
  - `dev-server.sh` (line 134-138)

### CSS Files Created
- `theme/css/components/form-fields.css` - Form field styling ({{filled:}} notation)
- `theme/css/documents/document-notes.css` - Document Notes section styling
- `theme/css/layout/mdbook-overrides.css` - Custom list overrides

## How It Works

1. **mdBook builds** → Clears book/ directory
2. **Postprocessors run** → Apply HTML transformations
3. **copy_assets() runs** → Copies theme/ and images/ to book/
4. **Browser loads** → CSS via @import chain from custom.css

## Import Chain
```
custom.css
└── @import theme/css/main.css
    ├── @import base/variables.css
    ├── @import base/typography.css
    ├── @import layout/mdbook-overrides.css
    ├── @import components/form-fields.css
    └── @import documents/document-notes.css
```

## Testing
After any changes to postprocessing:
1. Run `python3 scripts/postprocessing/custom-list-processor.py`
2. Check that theme/ exists in book/
3. Verify CSS loads: `curl http://localhost:3000/theme/css/main.css`
4. Check form fields render with blue backgrounds
5. Check Document Notes have proper styling

## Common Issues

### CSS Not Loading
- **Cause**: theme/ not copied to book/
- **Fix**: Run postprocessor or `cp -r theme book/`

### Old Styles Showing
- **Cause**: Cached inline styles in HTML
- **Fix**: Run both postprocessors to clean HTML

### MutationObserver Error
- **Cause**: document.body not ready
- **Fix**: Added null check in navigation-standalone.js (line 1590)

## Maintenance Notes
- Never add CSS back to Python processors
- Always use CSS variables from variables.css
- Test asset copying after any build script changes
- Keep form field validation separate from styling