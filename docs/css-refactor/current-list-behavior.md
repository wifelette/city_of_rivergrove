# Current List Behavior Documentation - January 12, 2025

## Purpose
This document captures the current working state of list rendering after rolling back the problematic changes. This serves as a baseline for future improvements.

## What's Currently Working

### Standard Ordered Lists (OL)
- **Status**: ✅ Mostly working
- **Color**: Blue markers (via `ol li::marker { color: var(--color-primary); }`)
- **Example**: Resolution 72 - numbered lists display correctly with blue numbers
- **Issues**: None known

### Unordered Lists with Alpha Notation - (a), (b), (c)
- **Status**: ⚠️ Partially working
- **Color**: Grey markers (not blue as specified in style guide)
- **Bullets**: Showing bullets alongside the (a), (b) notation
- **Example**: Ordinance 73-2003A - shows both bullets AND (a), (b) notation
- **Issues**: 
  - Bullets should be hidden when alpha notation is present
  - Markers should be blue, not grey

### Unordered Lists with Numeric Notation - (1), (2), (3)
- **Status**: ⚠️ Partially working
- **Color**: Inconsistent - sometimes blue, sometimes grey
- **Bullets**: Showing bullets alongside the (1), (2) notation
- **Example**: Ordinance 52 - shows both bullets AND (1), (2) notation
- **Issues**:
  - Bullets should be hidden when numeric notation is present
  - Color inconsistency across documents

### Nested Lists
- **Status**: ⚠️ Inconsistent
- **Behavior**: Different styling at different nesting levels
- **Example**: Ordinance 73-2003A - nested (1), (2) lists are blue but parent (a), (b) lists are grey
- **Issues**: Inconsistent color inheritance

## HTML Structure Variations

### Type 1: Simple List Items
```html
<ul>
  <li>(a) Content directly in li tag</li>
</ul>
```

### Type 2: List Items with Paragraphs
```html
<ul>
  <li>
    <p>(a) Content wrapped in paragraph tag</p>
  </li>
</ul>
```

### Type 3: Mixed Content
```html
<ul>
  <li>(a) Some content
    <p>Additional paragraph content</p>
  </li>
</ul>
```

## Current Postprocessors Touching Lists

1. **custom-list-processor.py** (rolled back to basic version)
   - Currently only processes Document Notes sections
   - No longer attempting to modify list markers

2. **enhanced-custom-processor.py**
   - Processes Document Notes with badge styling
   - May interact with lists in Document Notes sections

3. **fix-numbered-lists.py**
   - Purpose unclear - needs investigation
   - May be conflicting with other processors

## CSS Rules Currently Applied

### From mdbook-overrides.css
```css
/* Standard ordered list markers - WORKING */
ol li::marker {
    color: var(--color-primary, #0969da);
}

/* Attempted fixes for alpha/numeric lists - NOT WORKING */
/* These classes exist but aren't being applied because 
   custom-list-processor.py was rolled back */
.alpha-list-no-bullets,
.numeric-list-no-bullets {
    list-style: none;
    padding-left: 2em;
}
```

## Known Issues Summary

1. **Bullets showing on manual notation lists**
   - Lists with (a), (b), (c) or (1), (2), (3) show both bullets and notation
   - Should only show the notation

2. **Inconsistent marker colors**
   - Some markers blue, some grey
   - All should be blue per style guide

3. **No badge rendering**
   - Navigation badges for document types not showing
   - Lost when migrating to navigation-standalone.js

4. **Document Notes formatting**
   - Inconsistent rendering across documents
   - Sometimes shows badges, sometimes doesn't

## Test Documents for Verification

1. **Ordinance 52** - Complex nested lists with (1), (2) notation
2. **Ordinance 73-2003A** - Mixed (a), (b) parent lists with (1), (2) nested lists
3. **Resolution 72** - Simple numbered list (working baseline)
4. **Ordinance 54-89C** - Alpha notation lists

## Next Steps Required

1. Create comprehensive test file with all list variations
2. Audit all postprocessors to understand their interactions
3. Implement systematic fix with proper testing
4. Add visual regression tests to prevent future breakage
5. Consider consolidating list processing into single postprocessor