# City of Rivergrove Scripts Organization

## Quick Start - Main Build Scripts

The most commonly used scripts are in `scripts/build/`:

- **`./scripts/build/update-mdbook.sh`** - Full sync and rebuild of all documents
- **`./scripts/build/update-single.sh [file]`** - Quick sync and rebuild for a single file
- **`./scripts/build/update-mdbook-enhanced.sh`** - Full build with enhanced formatting (tables, WHEREAS clauses, etc.)

## Directory Structure

### build/
Main orchestration scripts that tie everything together:
- `update-mdbook.sh` - Standard full build
- `update-single.sh` - Single file update
- `update-mdbook-enhanced.sh` - Enhanced formatting build
- `build.sh` - Original build script

### preprocessing/
Scripts that modify source markdown BEFORE mdBook builds:
- `standardize-single.py` - Fix headers and signatures for one file
- `standardize-headers.py` - Batch fix all ordinance headers
- `fix-signatures.py` - Batch fix all signature blocks
- `sync-ordinances.py` - Sync ordinances from source to src/
- `footnote-preprocessor.py` - Process footnote formatting

### postprocessing/
Scripts that enhance HTML AFTER mdBook builds:
- `custom-list-processor.py` - Standard list formatting
- `enhanced-custom-processor.py` - Document-specific formatting
- `fix-numbered-lists.py` - Fix numbered list issues
- `fix-definition-sublists.py` - Fix definition sublists
- `clean-table-formatting.py` - Clean table formatting

### mdbook/
Scripts for mdBook-specific generation:
- `generate-summary.py` - Create SUMMARY.md table of contents
- `add-cross-references.py` - Add cross-references between docs
- `cross-reference-preprocessor.py` - Process cross-references
- `generate-relationships.py` - Generate relationship data

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