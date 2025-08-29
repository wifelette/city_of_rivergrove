# Sidebar and Airtable Integration Workflow

## Overview

The City of Rivergrove website sidebar integrates with Airtable to display proper document titles and metadata. This document explains the workflow and how to avoid common issues where mdBook overwrites custom formatting.

## Key Components

### 1. Data Sources

- **Local Files**: Markdown documents in `Ordinances/`, `Resolutions/`, `Interpretations/`, and `Other/` folders
- **Airtable Metadata**: Document titles, status, and other metadata stored in Airtable
- **Relationships**: Cross-references between documents in `relationships.json`

### 2. Processing Pipeline

The correct order is critical to preserve custom formatting and Airtable data:

1. **Sync Documents**: Copy from main folders to `src/` (removes `#` from filenames)
2. **Pre-process**: Apply footnotes, auto-links, and other transformations
3. **Generate Relationships**: Build cross-reference data
4. **Sync Airtable**: Fetch latest metadata from Airtable API
5. **Generate SUMMARY.md**: Build sidebar navigation WITH Airtable titles
6. **Build mdBook**: Generate HTML from markdown
7. **Post-process**: Apply custom list formatting and styles
8. **Finalize**: Copy metadata to book directory

## Common Issues and Solutions

### Issue 1: mdBook Overwrites Custom Formatting

**Problem**: When `mdbook serve` is running, it auto-rebuilds on file changes but skips post-processing, causing:
- Form fields (blue filled fields, blank underlines) disappear
- Custom list formatting is lost
- Legal enumeration styles revert to standard markdown

**Solution**: 
- Use `./scripts/build/update-mdbook-airtable.sh` for full builds
- After changes while `mdbook serve` is running, manually run:
  ```bash
  python3 scripts/postprocessing/custom-list-processor.py
  ```

### Issue 2: Sidebar Not Using Airtable Titles

**Problem**: Sidebar shows extracted titles from files instead of curated Airtable titles

**Solution**:
- Ensure Airtable sync runs BEFORE generating SUMMARY.md
- Use `generate-summary-with-airtable.py` instead of `generate-summary.py`
- Run the enhanced build script: `./scripts/build/update-mdbook-airtable.sh`

### Issue 3: Missing Airtable Data

**Problem**: Documents show "Unknown" status or missing titles

**Solution**:
1. Check if document exists in Airtable:
   ```bash
   python3 scripts/mdbook/sync-airtable-metadata.py --reconcile
   ```
2. Update missing records in Airtable
3. Force refresh cache:
   ```bash
   python3 scripts/mdbook/sync-airtable-metadata.py --mode=full --force
   ```

## Recommended Workflows

### For Single Document Updates

```bash
# Update a single document and rebuild
./scripts/build/update-single.sh Ordinances/2024-Ord-#95-Example.md
```

### For Multiple Changes

```bash
# Full rebuild with all enhancements
./scripts/build/update-mdbook-airtable.sh
```

### For Development (with mdbook serve)

```bash
# Start mdbook serve in one terminal
mdbook serve

# In another terminal, after making changes:
# 1. Sync Airtable if needed
python3 scripts/mdbook/sync-airtable-metadata.py --if-stale

# 2. Regenerate SUMMARY with Airtable data
python3 scripts/mdbook/generate-summary-with-airtable.py

# 3. Apply post-processing manually
python3 scripts/postprocessing/custom-list-processor.py
```

## File Locations

- **Airtable Metadata Cache**: `src/airtable-metadata.json` and `book/airtable-metadata.json`
- **Relationships Data**: `src/relationships.json` and `book/relationships.json`
- **Navigation**: `src/SUMMARY.md`
- **Build Scripts**: `scripts/build/`
- **Processing Scripts**: `scripts/mdbook/`, `scripts/preprocessing/`, `scripts/postprocessing/`

## Environment Setup

Ensure you have the required environment variables in `.env`:

```bash
AIRTABLE_API_KEY=your_api_key_here
AIRTABLE_BASE_ID=appnsWognX10X9TDL
AIRTABLE_TABLE_NAME=Public Metadata
```

## Debugging

### Check Airtable Sync Status

```bash
# See what's in the cache
cat src/airtable-metadata.json | jq '.metadata'

# Check for mismatches
python3 scripts/mdbook/sync-airtable-metadata.py --reconcile
```

### Verify Processing Order

```bash
# Run build with verbose output
bash -x ./scripts/build/update-mdbook-airtable.sh
```

### Test Individual Components

```bash
# Test Airtable sync only
python3 scripts/mdbook/sync-airtable-metadata.py --mode=full --force

# Test SUMMARY generation only
python3 scripts/mdbook/generate-summary-with-airtable.py

# Test post-processing only
python3 scripts/postprocessing/custom-list-processor.py
```

## Best Practices

1. **Always use the enhanced build script** for production builds
2. **Don't rely on mdbook serve auto-rebuild** for final output
3. **Keep Airtable metadata up to date** - it's the source of truth for titles
4. **Run reconciliation regularly** to catch mismatches early
5. **Commit changes to both** the processing scripts and generated files

## Future Improvements

- [ ] Integrate Airtable sync into mdbook preprocessor
- [ ] Add real-time Airtable webhook updates
- [ ] Create unified processing pipeline
- [ ] Add automated testing for formatting preservation