# Style Persistence Solution

## The Problem We Kept Encountering

Styles would appear and disappear repeatedly during development:
- Document Notes styling would vanish
- Enhanced formatting would be lost
- Tooltips would lose their styling
- The cycle would repeat endlessly

## Root Cause Discovery

The issue was a feedback loop:
1. We run postprocessors → HTML files are enhanced with styling
2. mdBook detects file changes (from our postprocessors!)
3. mdBook rebuilds everything from scratch → overwrites our enhancements
4. Styles disappear
5. We manually re-run postprocessors
6. Cycle repeats

This is why styles kept "appearing and disappearing" - every time mdBook detected ANY change, it would rebuild and wipe out our postprocessor enhancements.

## The Solution: Postprocess Watcher

Created `scripts/utils/mdbook-postprocess-watcher.sh` that:
- Monitors for mdBook rebuilds
- Detects when HTML lacks our enhancements
- Automatically re-runs postprocessors after mdBook finishes
- Includes cooldown to prevent infinite loops

Integrated into `dev-server.sh` to run alongside mdBook serve.

## Key Implementation Details

### Detection Method
```bash
# Check if index.html contains our enhanced markers
if ! grep -q "document-note" "$index_file" 2>/dev/null; then
    # File exists but doesn't have our enhancements - mdBook rebuilt!
    return 0
fi
```

### Cooldown Protection
```bash
POSTPROCESS_COOLDOWN=3  # Don't run more than once every 3 seconds
if [ $((current_time - LAST_POSTPROCESS_TIME)) -lt $POSTPROCESS_COOLDOWN ]; then
    return
fi
```

## Navigation Badges

The navigation badges for special states (Superseded, Never Passed) are:
- Implemented in `navigation-standalone.js`
- Pull data from `airtable-metadata.json`
- Display dynamically when JavaScript loads
- Currently exist for 4 documents:
  - Resolution #259-2018 (Superseded)
  - Resolution #256-2018 (Superseded)
  - Resolution #265-2019 (Never Passed)
  - Ordinance #69-2000 (Never Passed)

## Testing the Solution

1. Start dev server: `./dev-server.sh`
2. Watch the output for "🔄 Detected mdBook rebuild"
3. Verify "✅ Postprocessors applied" follows
4. Check that Document Notes styling persists
5. Verify navigation badges appear for special state documents

## Why This Kept Happening

We kept missing this because:
- The cycle was intermittent (depended on what triggered rebuilds)
- We'd fix it temporarily by running postprocessors manually
- The root cause (mdBook detecting postprocessor changes) wasn't obvious
- Each "fix" would work until the next rebuild

## Lesson Learned

When styles disappear in mdBook:
- Don't just re-run postprocessors manually
- Check if mdBook is rebuilding and overwriting changes
- Implement automatic recovery mechanisms
- Monitor file modification times to detect rebuild cycles