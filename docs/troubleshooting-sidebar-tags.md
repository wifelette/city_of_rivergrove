# Troubleshooting: Sidebar Tags Disappearing

## Problem
Special state tags ([SUPERSEDED], [NEVER PASSED], [REPEALED]) repeatedly disappear from the sidebar even after being fixed.

## Root Causes Discovered

### 1. Dev Server Uses --quick Flag (MAIN ISSUE)
**Problem**: The `dev-server.sh` script was running `./build-all.sh --quick` for initial builds, which skips Airtable sync entirely.

**Impact**: 
- Server starts with stale or missing metadata
- Tags don't appear because special_state data isn't loaded from Airtable
- Titles revert to fallback values instead of Airtable's short_title

**Fix**: Remove `--quick` flag from dev-server.sh line 137:
```bash
# Before (WRONG):
./build-all.sh --quick >/dev/null 2>&1

# After (CORRECT):
./build-all.sh >/dev/null 2>&1
```

### 2. Metadata Cache Gets Overwritten with Partial Data
**Problem**: Various scripts were performing incremental updates that sometimes only synced 3 documents instead of all 41.

**Impact**: 
- Full metadata (41 documents) gets replaced with partial data (3 documents)
- Special state information is lost for most documents
- System silently falls back to file-based titles

**Fix**: Always use `--force` flag when tags are missing:
```bash
python3 scripts/mdbook/sync-airtable-metadata.py --force
```

### 3. Wrong Summary Generator Being Used
**Problem**: Some scripts were calling `generate-summary.py` instead of `generate-summary-with-airtable.py`.

**Files affected**:
- `dev-server.sh` (line 117) - FIXED
- `build-one.sh` - FIXED

**Fix**: Always use the Airtable-aware version:
```bash
python3 scripts/mdbook/generate-summary-with-airtable.py
```

### 4. Special State Stored as Array in Airtable
**Problem**: Airtable returns special_state as an array `["Superseded"]` but code was treating it as a string.

**Fix**: Handle both formats in generate-summary-with-airtable.py:
```python
if special_state:
    if isinstance(special_state, list):
        state = special_state[0] if special_state else None
    else:
        state = special_state
```

## Quick Diagnosis Commands

Check if metadata is complete:
```bash
# Should show 41 documents, not 3
grep -c '"display_name"' book/airtable-metadata.json
```

Check if tags are in SUMMARY.md:
```bash
grep -E "\[SUPERSEDED\]|\[NEVER PASSED\]|\[REPEALED\]" src/SUMMARY.md
```

Check which documents have special states:
```bash
python3 -c "import json; d=json.load(open('book/airtable-metadata.json')); [print(k, v.get('special_state')) for k,v in d['documents'].items() if v.get('special_state')]"
```

## Full Recovery Process

If tags disappear again:

1. **Force full Airtable sync**:
   ```bash
   python3 scripts/mdbook/sync-airtable-metadata.py --force
   ```

2. **Regenerate SUMMARY.md with Airtable data**:
   ```bash
   python3 scripts/mdbook/generate-summary-with-airtable.py
   ```

3. **Rebuild mdBook**:
   ```bash
   mdbook build
   ```

4. **Restart server** (if running):
   ```bash
   pkill -f "mdbook serve"
   ./dev-server.sh
   ```

5. **Hard refresh browser**: Cmd+Shift+R (Mac) or Ctrl+Shift+R (PC)

## Prevention

1. **Never use --quick flag** for production or when you need accurate metadata
2. **Always verify metadata count** after builds (should be 41, not 3)
3. **Use build-all.sh without flags** for full rebuilds
4. **Monitor the metadata file** - if it suddenly shrinks, something overwrote it

## Documents with Special States (as of Aug 2024)

- **Ordinance #69-2000**: Never Passed
- **Resolution #256-2018**: Superseded  
- **Resolution #259-2018**: Superseded
- **Resolution #265-2019**: Never Passed