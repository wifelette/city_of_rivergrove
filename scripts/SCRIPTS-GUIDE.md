# Scripts Documentation - City of Rivergrove

## ⚠️ Important: Processing Order Matters!

**See `/docs/build-architecture.md` for complete build system documentation and dependencies.**

## Quick Start - The Only 3 Scripts You Need

**All build scripts are now in the repository root for easy access:**

- **`./build-all.sh [--quick]`** - Complete rebuild with all processing (use `--quick` to skip Airtable)
- **`./build-one.sh [file]`** - Smart single-file update with auto-detection
- **`./dev-server.sh`** - Development server with hot-reload from source edits

## Directory Structure

### Root Directory Build Scripts
The three main scripts are in the repository root:
- `build-all.sh` - Complete rebuild with all processing
- `build-one.sh` - Smart single-file update
- `dev-server.sh` - Development server with hot-reload

### scripts/build/ (DEPRECATED)
Old scripts with deprecation warnings - do not use:
- `update-mdbook.sh` - ❌ Use `./build-all.sh` instead
- `update-single.sh` - ❌ Use `./build-one.sh` instead  
- `serve.sh` - ❌ Use `./dev-server.sh` instead
- Others - ❌ All replaced by the three main scripts

### preprocessing/
Scripts that modify source markdown BEFORE mdBook builds:
- `sync-ordinances.py` - Copy ordinances to src/, remove #, apply form fields
- `sync-resolutions.py` - Copy resolutions to src/, remove #, apply form fields  
- `sync-interpretations.py` - Copy interpretations to src/
- `sync-other.py` - Copy other documents to src/
- `footnote-preprocessor.py` - Convert footnote syntax to HTML
- `auto-link-converter.py` - Convert URLs/emails to markdown links
- `standardize-single.py` - Fix headers and signatures for one file
- `remove-manual-links.py` - Remove manual markdown links (one-time cleanup)

### validation/
Scripts that ensure document syntax is correct:
- `validate-form-fields.py` - Check {{filled:}} tag syntax, detect unclosed tags

### postprocessing/
Scripts that enhance HTML AFTER mdBook builds:
- `custom-list-processor.py` - Apply form fields, fix special lists, add tooltips
- `enhanced-custom-processor.py` - Document-specific formatting (tables, WHEREAS clauses)
- `fix-numbered-lists.py` - Fix numbered list issues (legacy)
- `fix-definition-sublists.py` - Fix definition sublists (legacy)
- `clean-table-formatting.py` - Clean table formatting (legacy)

### mdbook/
Scripts for mdBook-specific generation:
- `add-cross-references.py` - Convert document references to clickable links
- `generate-summary.py` - Create SUMMARY.md table of contents
- `generate-relationships.py` - Build document relationship graph
- `sync-airtable-metadata.py` - Fetch and sync Airtable metadata
- `cross-reference-preprocessor.py` - mdBook preprocessor for cross-refs (not currently used)

### utilities/
Helper and analysis tools:
- `watch-and-sync.py` - File watcher for auto-sync
- `audit-airtable-coverage.py` - Check Airtable coverage
- `identify-missing-metadata.py` - Find missing metadata

### config/
Configuration files:
- `formatting-config.json` - Document formatting rules
- `special-formatting.css` - Enhanced CSS styles

## Workflow

1. **Source markdown** → preprocessing scripts modify headers/signatures
2. **mdBook builds** → Converts markdown to HTML
3. **Postprocessing** → Enhances HTML with special formatting
4. **Output** → Beautiful, legally-accurate documents

## Most Common Commands

```bash
# Development server (hot-reload from source edits)
./dev-server.sh

# Process a single document
python3 scripts/preprocessing/standardize-single.py source-documents/Resolutions/2024-Res-#300-Fee-Schedule.md
./build-one.sh source-documents/Resolutions/2024-Res-#300-Fee-Schedule.md

# Full rebuild
./build-all.sh

# Full rebuild without Airtable (faster)
./build-all.sh --quick

# Validate form field syntax
python3 scripts/validation/validate-form-fields.py  # Check all files
python3 scripts/validation/validate-form-fields.py source-documents/Ordinances/example.md  # Check one file
python3 scripts/validation/validate-form-fields.py --fix  # Auto-fix simple issues
```

## Key Improvements

1. **Simplified to 3 scripts** - Down from 6+ confusing variants
2. **Smart detection** - Scripts auto-detect document types
3. **True hot-reload** - `dev-server.sh` watches source files, not generated output
4. **Safety rails** - Warns about /src edits, stops conflicting processes
5. **Clear names** - `build-all`, `build-one`, `dev-server` are self-explanatory