# Postprocessor Audit - January 12, 2025

## Current Postprocessors and Their Purposes

### 1. fix-numbered-lists.py (PREPROCESSING - runs on markdown)
- **Purpose**: Converts (1), (2) style lists in markdown to proper `1.`, `2.` format
- **When it runs**: During preprocessing, BEFORE mdBook converts to HTML
- **What it modifies**: 
  - (1), (2) → 1., 2. (numbered lists)
  - (a), (b) → **(a)**, **(b)** (definition lists with bold markers)
  - Indented (i), (ii) → Proper nested lists
- **Note**: This is a PREPROCESSING script, not a postprocessor

### 2. custom-list-processor.py (POSTPROCESSING - runs on HTML)
- **Purpose**: Originally for complex list styling, now mainly Document Notes
- **When it runs**: After mdBook generates HTML
- **Current functionality** (after rollback):
  - Process Document Notes sections with badges
  - No longer attempting to modify list markers
- **What it touches**:
  - H2 tags containing "Document Notes"
  - Creates badge-styled headers for note types

### 3. enhanced-custom-processor.py (POSTPROCESSING - runs on HTML)  
- **Purpose**: Enhanced version with multiple processors
- **When it runs**: After custom-list-processor.py
- **What it processes**:
  - Standard lists (numbered)
  - Letter lists (a, b, c)
  - Definition lists
  - Document Notes (duplicate of custom-list-processor?)
- **Potential conflicts**: May be duplicating custom-list-processor work

## Execution Order

Based on script analysis, the typical execution order is:

1. **Preprocessing** (on markdown files):
   - standardize-single.py (headers, signatures)
   - fix-numbered-lists.py (list format conversion)

2. **mdBook build** (markdown → HTML)

3. **Postprocessing** (on HTML files):
   - custom-list-processor.py
   - enhanced-custom-processor.py

## Problems Identified

### 1. Conflicting Processors
- Both custom-list-processor.py and enhanced-custom-processor.py process Document Notes
- Both have list processing functions that may conflict
- No clear separation of responsibilities

### 2. Preprocessing vs Postprocessing Confusion
- fix-numbered-lists.py changes markdown BEFORE HTML generation
- This means (a), (b) lists are already converted to **(a)**, **(b)** in HTML
- Postprocessors looking for "(a)" patterns won't find them - they're already bold

### 3. Order Dependencies
- enhanced-custom-processor runs after custom-list-processor
- If custom-list-processor modifies HTML structure, enhanced might not find expected patterns
- No documentation of what each processor expects as input

### 4. Duplicate Functionality
- Multiple processors trying to handle the same list types
- No clear ownership of which processor handles what

## Root Cause of List Issues

The main problem is that we're trying to fix styling issues at the wrong stage:

1. **Markdown lists with (a), (b) notation**:
   - fix-numbered-lists.py converts these to **(a)**, **(b)** 
   - mdBook then creates `<ul>` with bullets
   - We need CSS to hide those bullets, but the markers are already bold, not wrapped in spans

2. **Inconsistent HTML output**:
   - Some lists have content directly in `<li>`
   - Others wrap content in `<p>` tags
   - Processors need to handle both cases

3. **CSS can't target the right elements**:
   - We need to identify lists with manual notation to hide bullets
   - But the notation is just text, not in identifiable spans
   - Can't reliably detect via CSS alone

## Recommended Solution

### Option 1: Fix at Preprocessing Stage
- Modify fix-numbered-lists.py to NOT convert (a), (b) to bold
- Instead, keep them as-is for postprocessors to handle
- Let postprocessors wrap in appropriate spans for CSS targeting

### Option 2: Single Unified Postprocessor
- Combine all list processing into one processor
- Clear rules for each list type
- Consistent span wrapping for CSS hooks
- Remove duplicate functionality

### Option 3: Pure CSS Solution
- Use CSS attribute selectors to detect list content
- Hide bullets based on first characters of list items
- Requires consistent HTML structure

## Next Steps

1. Decide on approach (preprocessing vs postprocessing vs CSS)
2. Consolidate processors to avoid conflicts  
3. Add debug logging to understand what each processor sees
4. Create test suite to verify changes don't break documents
5. Document expected input/output for each processor