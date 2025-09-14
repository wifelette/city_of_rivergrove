# List Processing Architecture

## Overview

This document defines the authoritative architecture for processing lists in the City of Rivergrove documentation system. It establishes clear responsibilities for each component to prevent conflicts and ensure maintainability.

## Design Principles

1. **Single Responsibility**: Each processor has ONE clearly defined job
2. **No Overlapping Logic**: Processors never duplicate functionality
3. **Clear Processing Order**: Dependencies are explicit and documented
4. **CSS-Based Styling**: Visual presentation handled purely by CSS, not by processors
5. **Preservation of Legal Format**: Original document notation is preserved

## List Types in Legal Documents

### Type 1: Standard Numbered Lists
- **Markdown**: `1.`, `2.`, `3.`
- **HTML Output**: `<ol><li>...</li></ol>`
- **CSS Class**: None needed (browser default)
- **Styling**: Blue numbers via CSS

### Type 2: Alpha Parenthetical Lists
- **Markdown**: `(a)`, `(b)`, `(c)` at line start
- **HTML Output**: `<ul class="alpha-list"><li><span class="list-marker-alpha">(a)</span> ...</li></ul>`
- **CSS Class**: `.alpha-list` (hides bullets), `.list-marker-alpha` (styles marker)
- **Styling**: No bullets, blue markers

### Type 3: Numeric Parenthetical Lists
- **Markdown**: `(1)`, `(2)`, `(3)` at line start
- **HTML Output**: `<ul class="numeric-list"><li><span class="list-marker-numeric">(1)</span> ...</li></ul>`
- **CSS Class**: `.numeric-list` (hides bullets), `.list-marker-numeric` (styles marker)
- **Styling**: No bullets, blue markers

### Type 4: Roman Numeral Lists
- **Markdown**: `(i)`, `(ii)`, `(iii)` (usually indented)
- **HTML Output**: `<ul class="roman-list"><li><span class="list-marker-roman">(i)</span> ...</li></ul>`
- **CSS Class**: `.roman-list` (hides bullets), `.list-marker-roman` (styles marker)
- **Styling**: No bullets, blue markers

## Processing Pipeline

### Stage 1: Preprocessing (Markdown → Markdown)

**Script**: `scripts/preprocessing/standardize-list-format.py`
**Responsibility**: Normalize list formats for consistent mdBook processing
**Actions**:
- Convert standalone `(1)`, `(2)` to `1.`, `2.` (proper ordered lists)
- Leave `(a)`, `(b)` unchanged (for postprocessor detection)
- Convert indented `(1)`, `(2)` under letters to nested `1.`, `2.`
- Leave roman numerals `(i)`, `(ii)` unchanged

### Stage 2: mdBook Processing (Markdown → HTML)

**Tool**: mdBook
**Responsibility**: Convert markdown to semantic HTML
**Actions**:
- Converts `1.`, `2.` to `<ol><li>...</li></ol>`
- Converts `- (a)` to `<ul><li>(a) ...</li></ul>`
- Standard markdown processing

### Stage 3: Postprocessing (HTML → HTML)

**Script**: `scripts/postprocessing/unified-list-processor.py` (NEW - replaces custom-list-processor.py)
**Responsibility**: Add semantic classes and wrap markers for CSS targeting
**Actions**:
1. Detect `<ul>` lists with `(a)`, `(b)` content → add class `.alpha-list`
2. Detect `<ul>` lists with `(1)`, `(2)` content → add class `.numeric-list`
3. Detect `<ul>` lists with `(i)`, `(ii)` content → add class `.roman-list`
4. Wrap markers in appropriate `<span>` tags
5. Process Document Notes (existing functionality)

**REMOVED**: List processing from `enhanced-custom-processor.py` (it only handles WHEREAS, tables, etc.)

### Stage 4: CSS Styling

**File**: `theme/css/components/lists.css` (NEW)
**Responsibility**: All visual presentation of lists
**Rules**:
```css
/* Hide bullets for manual notation lists */
.alpha-list, .numeric-list, .roman-list {
    list-style: none;
    padding-left: 2em;
}

/* Style all list markers in primary blue */
.list-marker-alpha, .list-marker-numeric, .list-marker-roman {
    color: var(--color-primary);
    font-weight: bold;
    margin-right: 0.5em;
}

/* Standard ordered lists also get blue numbers */
ol li::marker {
    color: var(--color-primary);
}
```

## File Responsibilities

### Scripts to Keep
- `scripts/preprocessing/standardize-list-format.py` - List normalization
- `scripts/postprocessing/unified-list-processor.py` - Semantic markup and Document Notes
- `scripts/postprocessing/enhanced-custom-processor.py` - WHEREAS, tables, other formatting (NO lists)

### Scripts to Remove
- `scripts/postprocessing/fix-numbered-lists.py` - Replaced by standardize-list-format.py
- `scripts/postprocessing/custom-list-processor.py` - Replaced by unified-list-processor.py

### CSS Files
- `theme/css/components/lists.css` - All list styling (NEW)
- Remove list-related rules from other CSS files

## Build Script Updates

### build-all.sh
```bash
# Preprocessing (includes list standardization)
python3 scripts/preprocessing/standardize-list-format.py

# ... mdBook build ...

# Postprocessing (single list processor)
python3 scripts/postprocessing/unified-list-processor.py
python3 scripts/postprocessing/enhanced-custom-processor.py
```

### dev-server.sh
Update `process_file_change()` to include standardize-list-format.py in preprocessing

## Testing Strategy

1. Create `test-documents/list-test-comprehensive.md` with all list variations
2. Visual regression tests comparing before/after
3. Automated validation of HTML structure
4. Check for CSS conflicts

## Migration Path

1. Create new unified-list-processor.py
2. Create lists.css with all list styles
3. Update build scripts
4. Test on subset of documents
5. Remove old processors
6. Full rebuild and validation

## Success Criteria

- All list types display correctly (no bullets where inappropriate)
- All markers are blue per style guide
- No processor conflicts or duplicate processing
- CSS compilation includes list styles
- Build scripts execute in correct order
- No regressions in existing documents

## Long-term Maintenance

- Single source of truth for each concern
- Clear documentation of responsibilities
- Test suite prevents regressions
- Modular CSS for easy updates
- No overlapping or conflicting processors