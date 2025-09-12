# List Styling Rollback Notes - January 12, 2025

## What We Were Trying to Fix

### Original Issues Reported by User
1. **Missing blue color on list markers** - (a), (b), (c) and (1), (2), (3) markers were showing in grey instead of blue
2. **Bullets showing alongside alphanumeric markers** - Lists with (a), (b) notation were showing both bullets AND the notation
3. **Inconsistent styling across pages**:
   - Ord 73-2003A: Parent (a),(b) lists not blue, but nested (1),(2) lists were blue
   - Ord 52: Some lists blue, others not
   - Res 72: Standard numbered lists working correctly

## What We Attempted

### Changes Made to `custom-list-processor.py`
1. Added `process_alpha_ul_lists()` function to detect UL lists with (a), (b) markers
2. Added `process_numeric_ul_lists()` function to detect UL lists with (1), (2) markers  
3. Tried to wrap these markers in `<span class="list-marker-alpha">` tags for styling
4. Added complex logic to handle markers inside `<p>` tags within list items

### CSS Changes Made
1. Added classes to hide bullets: `alpha-list-no-bullets`, `numeric-list-no-bullets`
2. Added blue color styling for `.list-marker-alpha` and `.list-marker-numeric`
3. Added `ol li::marker { color: var(--color-primary); }` for standard numbered lists

## What Broke

### Major Regressions
1. **Ord 52 sections 4.4.1 and 4.4.2** - Lists completely collapsed into paragraphs, lost all list structure
2. **Inconsistent marker wrapping** - The span wrapping only worked for simple lists, not those with paragraphs
3. **Postprocessor conflicts** - Multiple processors touching the same HTML causing unpredictable results

## Why We're Rolling Back

1. **Breaking more than fixing** - The attempted fixes caused major regressions in previously working documents
2. **Complex paragraph handling not working** - Lists with content in `<p>` tags weren't getting processed correctly
3. **No test coverage** - Can't verify changes don't break other documents

## What We're Keeping

1. **CSS rule for ordered lists**: `ol li::marker { color: var(--color-primary); }` - This successfully makes standard numbered lists blue
2. **Enhanced custom processor** - Document Notes processing is working correctly
3. **Postprocess watcher improvements** - Marker file approach prevents rebuild loops
4. **Tooltip fixes** - Font inheritance issues resolved

## Next Steps

1. Roll back `custom-list-processor.py` to previous version
2. Create comprehensive test file with all list variations
3. Identify which postprocessor should handle which list type
4. Add visual regression tests before making changes
5. Fix list styling systematically with proper testing

## Root Cause Analysis

The fundamental issue is that we have multiple postprocessors (`custom-list-processor.py`, `enhanced-custom-processor.py`, `fix-numbered-lists.py`) all trying to process lists, and they're not coordinated. Additionally, the markdown source has inconsistent list formatting:
- Some use `- (a)` (unordered with manual markers)
- Some use `1.` (ordered lists)
- Some have content directly in `<li>`, others wrap in `<p>`

This inconsistency makes it very difficult to apply uniform styling without breaking edge cases.