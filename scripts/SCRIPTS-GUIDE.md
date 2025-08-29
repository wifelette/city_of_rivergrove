# Scripts Documentation - City of Rivergrove

## ⚠️ Important: Processing Order Matters!

**See `/docs/build-architecture.md` for complete build system documentation and dependencies.**

## Quick Start - Main Build Scripts

The most commonly used scripts are in `scripts/build/`:

- **`./scripts/build/update-mdbook.sh`** - Full sync and rebuild of all documents (recommended)
- **`./scripts/build/update-single.sh [file]`** - Quick sync and rebuild for a single file
- **`./scripts/build/update-mdbook-enhanced.sh`** - Full build with enhanced formatting
- **`./scripts/build/update-mdbook-airtable.sh`** - Full build with Airtable integration

## Directory Structure

### build/
Main orchestration scripts that tie everything together:
- `update-mdbook.sh` - Standard full build
- `update-single.sh` - Single file update
- `update-mdbook-enhanced.sh` - Enhanced formatting build
- `build.sh` - Original build script

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
# Process a single document
python3 scripts/preprocessing/standardize-single.py Resolutions/2024-Res-#300-Fee-Schedule.md
./scripts/build/update-single.sh Resolutions/2024-Res-#300-Fee-Schedule.md

# Full rebuild
./scripts/build/update-mdbook.sh

# Full rebuild with enhanced formatting
./scripts/build/update-mdbook-enhanced.sh
```