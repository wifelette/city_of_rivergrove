# SUMMARY.md Handling Guide

## What is SUMMARY.md?

SUMMARY.md is mdBook's internal navigation structure file. It defines the table of contents and hierarchy of the documentation but is **never displayed directly to users**.

## Key Principle: SUMMARY.md is NOT Content

Since SUMMARY.md is purely for mdBook's internal use:
- It should NOT be processed by content enhancement scripts
- It should NOT have cross-reference links added
- It should NOT have URLs auto-converted
- It should NOT be treated as user-facing content

## Current Protections

Our scripts already skip SUMMARY.md:
- `scripts/mdbook/add-cross-references.py` - Explicitly skips SUMMARY.md
- `scripts/preprocessing/auto-link-converter.py` - Explicitly skips SUMMARY.md
- Other content processors should follow this pattern

## Known Issue: Markdown Links in Titles

### Problem
When document H1 titles contain cross-reference links (e.g., `# Interpretation of [Ordinance 68-2000](...)`), these can break SUMMARY.md generation because mdBook cannot parse nested markdown links.

### Solution
The `scripts/utils/title_resolver.py` module strips markdown links when extracting titles for SUMMARY.md using the `strip_markdown_links()` method.

### Why Not Reorder the Build?
SUMMARY.md generation requires:
1. Relationships data (built from processed files)
2. Airtable metadata (needs relationships)

Therefore, it must run AFTER cross-references are added, not before.

## Best Practices

1. **Always skip SUMMARY.md** in content processing scripts:
   ```python
   if md_file.name == "SUMMARY.md":
       continue
   ```

2. **Strip markdown formatting** when extracting titles for SUMMARY.md
3. **Test mdBook builds** after changing title extraction logic
4. **Remember**: SUMMARY.md paths must match actual file locations in `/src`

## Common Errors

### Error: "failed to parse SUMMARY.md line X"
**Cause**: Usually means there's invalid markdown in SUMMARY.md, often nested links like `[text [link](url)]`
**Fix**: Check title extraction in `generate-summary-with-airtable.py` and ensure markdown links are stripped

### Error: "The link items for nested chapters must only contain a hyperlink"
**Cause**: Complex markdown in SUMMARY.md entries
**Fix**: Ensure titles are plain text without embedded formatting

## Related Files
- `scripts/mdbook/generate-summary-with-airtable.py` - Generates SUMMARY.md
- `scripts/utils/title_resolver.py` - Extracts and cleans titles
- `build-all.sh` - Defines build order (see Step 10)