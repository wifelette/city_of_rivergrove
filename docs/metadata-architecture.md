# Metadata Architecture for City of Rivergrove

## Overview

The City of Rivergrove digitization project uses a dual-metadata system to enrich documents with additional information from Airtable while maintaining flexibility for different document types.

## Current Architecture

### Metadata Sources

1. **Airtable Database** (Source of Truth)
   - **Governing_Metadata Table**: Ordinances, Resolutions, Interpretations, Other documents
   - **Meetings_Metadata Table**: Agendas, Minutes, Transcripts
   - Contains: display names, short titles, special states, dates, URLs

2. **Local Cache Files**
   - `book/airtable-metadata.json`: Governing documents metadata
   - `book/meetings-metadata.json`: Meeting documents metadata
   - Cache lifetime: 24 hours (configurable)

### Data Flow

```
Airtable API
     ↓
sync-airtable-metadata.py / sync-meetings-metadata.py
     ↓
book/*.json cache files
     ↓
generate-summary-with-airtable.py
     ↓
src/SUMMARY.md
     ↓
mdBook build
     ↓
book/toc.html → Sidebar Display
```

## Key Components

### 1. Sync Scripts
- `scripts/mdbook/sync-airtable-metadata.py`: Syncs governing documents
- `scripts/mdbook/sync-meetings-metadata.py`: Syncs meeting documents
- Features:
  - Incremental updates for recent changes
  - Full sync when cache expires
  - Automatic filename matching with fuzzy logic

### 2. Summary Generator
- `scripts/mdbook/generate-summary-with-airtable.py`
- Reads both metadata files
- Enriches SUMMARY.md with:
  - Airtable display names and short titles
  - Special state tags ([SUPERSEDED], [NEVER PASSED], [REPEALED])
  - Proper document numbers and dates

### 3. Build Scripts
- `build-all.sh`: Full build with Airtable sync
- `build-one.sh`: Single file rebuild (now uses Airtable-aware generator)
- `dev-server.sh`: Development server with hot reload

## Special State Tags

Documents can have special states that appear as tags in the sidebar:
- **[SUPERSEDED]**: Document has been replaced by a newer version
- **[NEVER PASSED]**: Document was proposed but not enacted
- **[REPEALED]**: Document was previously active but has been repealed

These are stored as arrays in Airtable's `special_state` field.

## Known Issues and Solutions

### Issue 1: Tags Disappearing on Rebuild
**Problem**: mdBook's internal file watcher doesn't regenerate SUMMARY.md with Airtable data.
**Solution**: All build scripts now explicitly call `generate-summary-with-airtable.py`.

### Issue 2: Metadata Not Syncing
**Problem**: Cache prevents frequent Airtable API calls.
**Solution**: Use `--force` flag or delete cache files to force sync.

### Issue 3: Bifurcated Metadata
**Design Decision**: Meetings will have hundreds of documents with different metadata needs.
**Solution**: Separate tables and cache files for governing vs meeting documents.

## Best Practices

1. **Always run full build** (`./build-all.sh`) after major changes
2. **Force sync** when Airtable data changes: `python3 scripts/mdbook/sync-airtable-metadata.py --force`
3. **Check cache age** if metadata seems stale (24-hour default)
4. **Commit after fixes** to preserve metadata state

## Future Improvements

1. **Unified metadata interface**: Abstract the bifurcation behind a single API
2. **Real-time sync**: Webhook-based updates from Airtable
3. **Better error reporting**: Surface metadata mismatches more visibly
4. **Preprocessor integration**: Ensure SUMMARY.md always regenerates before mdBook builds

## Troubleshooting

### Missing Tags
1. Check if Airtable has the special_state field populated
2. Force sync: `python3 scripts/mdbook/sync-airtable-metadata.py --force`
3. Regenerate: `python3 scripts/mdbook/generate-summary-with-airtable.py`
4. Rebuild: `mdbook build`

### Wrong Titles
1. Verify Airtable has correct display_name and short_title
2. Check cache age in metadata files
3. Force sync if needed

### Dev Server Issues
1. Kill existing server: `pkill -f "mdbook serve"`
2. Restart with: `./dev-server.sh`
3. Check that port 3000 is free

## Configuration

### Cache Duration
Edit sync scripts to change cache lifetime:
```python
CACHE_DURATION_HOURS = 24  # Default
```

### API Keys
Set environment variable:
```bash
export AIRTABLE_API_KEY="your_key_here"
```

### Base IDs
- Governing: `appnsWognX10X9TDL`
- Meetings: (configured in sync script)