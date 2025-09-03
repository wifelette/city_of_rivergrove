# Troubleshooting Guide

## Missing Documents in Navigation

### Problem: Document exists but doesn't appear in sidebar

**Symptoms:**
- Document is accessible via direct URL
- Document appears in SUMMARY.md and toc.js
- Document count on homepage is correct
- Document is missing from the sidebar navigation

**Root Cause:**
The custom navigation system (`navigation-standalone.js`) reads from `relationships.json`, which is generated from Airtable metadata. If a document isn't in Airtable or isn't syncing properly, it won't appear in the navigation even if it exists in all other files.

**Solution:**
1. Check if document exists in Airtable (correct table for document type)
2. Verify the record has all required fields filled
3. Force refresh the metadata:
   ```bash
   rm book/.airtable-cache.json  # Clear cache
   python3 scripts/mdbook/sync-meetings-metadata.py  # For meetings
   # OR
   python3 scripts/airtable/sync-metadata.py  # For other documents
   ```
4. Regenerate relationships.json:
   ```bash
   python3 scripts/mdbook/generate-relationships.py
   ```
5. Copy to book folder:
   ```bash
   cp src/relationships.json book/relationships.json
   ```
6. Hard refresh browser (Cmd+Shift+R)

### Special Case: Multiple Documents from Same Date

The system CAN handle multiple documents from the same date (e.g., both Agenda and Minutes from 2017-06-12). Each document needs:
- Its own Airtable record with unique record ID
- Proper document type field (agenda/minutes/transcript)
- All required metadata fields

## Timezone Issues in Meeting Dates

### Problem: Meeting dates display one day off

**Symptoms:**
- Dates in sidebar show as day before actual date
- Example: June 12, 2017 displays as June 11, 2017

**Root Cause:**
Timezone conversion issue when syncing from Airtable. Dates stored as UTC midnight get converted to previous day in Pacific timezone.

**Solution:**
Fix the timezone handling in Airtable or ensure dates are stored with proper timezone offset.

**Tracked in:** GitHub Issue #23

## Build vs Dev Server Differences

### Problem: Formatting disappears when using mdbook serve

**Symptoms:**
- Form fields lose their styling
- Custom formatting disappears
- Works fine with build scripts but breaks with plain `mdbook serve`

**Root Cause:**
`mdbook serve` auto-rebuilds but doesn't run our custom postprocessors.

**Solution:**
- Use `./dev-server.sh` for development (includes all processors)
- If you must use plain `mdbook serve`, restore formatting with:
  ```bash
  python3 scripts/postprocessing/custom-list-processor.py
  ```

## Navigation Not Updating

### Problem: Changes to documents don't appear in navigation

**Root Cause:**
The navigation system has multiple layers of caching:
1. Airtable cache (`.airtable-cache.json`)
2. Browser cache for JavaScript files
3. Generated files (`relationships.json`, `toc.js`)

**Solution:**
1. Clear Airtable cache: `rm book/.airtable-cache.json`
2. Rebuild everything: `./build-all.sh`
3. Hard refresh browser: Cmd+Shift+R
4. If still not working, check browser console for errors

## Duplicate Navigation Elements

### Problem: Navigation elements appear twice

**Symptoms:**
- `#standalone-navigation` ID appears multiple times
- Documents listed twice in sidebar

**Root Cause:**
Multiple instances of navigation JavaScript running or DOM not properly cleaned up.

**Solution:**
1. Check that navigation-standalone.js properly removes old elements
2. Ensure only one instance of the script is running
3. Clear browser cache and reload