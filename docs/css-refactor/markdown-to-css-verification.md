# Markdown to CSS Pattern Verification

## Overview
This document verifies that all markdown patterns in source documents correctly trigger the appropriate CSS styles through preprocessing and postprocessing.

## Pattern Verification Status

### ✅ Form Fields (Verified)
**Processor**: `scripts/preprocessing/form-fields-processor.py`

| Markdown Pattern | Generated HTML | CSS Class | Status |
|-----------------|----------------|-----------|--------|
| `{{filled:text}}` | `<span class="form-field-filled" data-tooltip="...">text</span>` | `.form-field-filled` | ✅ Working |
| `{{empty:short}}` | `<span class="form-field-empty form-field-short" data-tooltip="..."></span>` | `.form-field-empty.form-field-short` | ✅ Working |
| `{{empty:medium}}` | `<span class="form-field-empty form-field-medium" data-tooltip="..."></span>` | `.form-field-empty.form-field-medium` | ✅ Working |
| `{{empty:long}}` | `<span class="form-field-empty form-field-long" data-tooltip="..."></span>` | `.form-field-empty.form-field-long` | ✅ Working |

### ✅ Signatures (Fixed - Issue #25)
**Processor**: `scripts/preprocessing/sync-resolutions.py`

| Markdown Pattern | Generated HTML | CSS Class | Status |
|-----------------|----------------|-----------|--------|
| `{{signature}}` | `<span class="signature-mark" data-tooltip="...">Signature</span>` | `.signature-mark` | ✅ Fixed (tooltip inheritance resolved) |
| `[Signature]` | `<span class="signature-mark" data-tooltip="...">Signature</span>` | `.signature-mark` | ✅ Working |

### ✅ Document Notes
**Processor**: Built into mdBook processing + `enhanced-custom-processor.py`

| Markdown Pattern | Generated HTML | CSS Class | Status |
|-----------------|----------------|-----------|--------|
| `## Document Notes` | `<div class="document-notes">` | `.document-notes` | ✅ Working |
| `### Stamp {{page:3}}` | `<span class="note-type-label">Stamp</span> <span class="label-page-ref">page 3</span>` | `.note-type-label`, `.label-page-ref` | ✅ Working |
| `### Handwritten text` | `<span class="note-type-label">Handwritten text</span>` | `.note-type-label` | ✅ Working |

### ✅ Enhanced Lists
**Processor**: `scripts/postprocessing/unified-list-processor.py`

| Markdown Pattern | Generated HTML | CSS Class | Status |
|-----------------|----------------|-----------|--------|
| `(a) Item` | `<li class="alpha-list">` | `.alpha-list` | ✅ Working |
| `(b) Item` | `<li class="alpha-list">` | `.alpha-list` | ✅ Working |
| `(1) Item` | `<li class="numeric-list">` | `.numeric-list` | ✅ Working |
| `(i) Item` | `<li class="roman-list">` | `.roman-list` | ✅ Working |
| `(ii) Item` | `<li class="roman-list">` | `.roman-list` | ✅ Working |

### ✅ WHEREAS Clauses
**Processor**: `scripts/postprocessing/enhanced-custom-processor.py`

| Markdown Pattern | Generated HTML | CSS Class | Status |
|-----------------|----------------|-----------|--------|
| `WHEREAS, text...` | `<span class="whereas-marker">WHEREAS</span>, <span class="whereas-clause">text...</span>` | `.whereas-marker`, `.whereas-clause` | ✅ Working |

### ✅ Tables
**Processor**: Native mdBook + `clean-table-formatting.py`

| Markdown Pattern | Generated HTML | CSS Class | Status |
|-----------------|----------------|-----------|--------|
| Standard table | `<table>` | `.formatted-table` (via postprocessor) | ✅ Working |
| Fee schedule table | `<table class="fee-schedule-table">` | `.fee-schedule-table` | ✅ Working |

### ✅ Footnotes
**Processor**: `scripts/preprocessing/footnote-preprocessor.py`

| Markdown Pattern | Generated HTML | CSS Class | Status |
|-----------------|----------------|-----------|--------|
| `¹ **Title.** Text` | `<div class="footnotes">` | `.footnotes` | ✅ Working |
| Individual footnote | `<div class="footnote-definition">` | `.footnote-definition` | ✅ Working |

### ⚠️ Definition Lists
**Processor**: `scripts/postprocessing/fix-definition-sublists.py`

| Markdown Pattern | Generated HTML | CSS Class | Status |
|-----------------|----------------|-----------|--------|
| `Term: Definition` | `<dl>` with `<dt>` and `<dd>` | `.definition-list`, `.definition-item` | ⚠️ Needs verification |

### ✅ Cross-References
**Processor**: `scripts/preprocessing/auto-link-converter.py`

| Markdown Pattern | Generated HTML | CSS Class | Status |
|-----------------|----------------|-----------|--------|
| `Ordinance #52` | `<a href="../ordinances/...">Ordinance #52</a>` | Auto-linked | ✅ Working |
| `Resolution #259` | `<a href="../resolutions/...">Resolution #259</a>` | Auto-linked | ✅ Working |

## Processing Pipeline Verification

### Stage 1: Preprocessing (source-documents → /src)
1. ✅ `form-fields-processor.py` - Converts `{{filled:}}` and `{{empty:}}` patterns
2. ✅ `sync-*.py` scripts - Handle document-specific patterns (signatures, etc.)
3. ✅ `footnote-preprocessor.py` - Wraps footnotes in proper containers
4. ✅ `auto-link-converter.py` - Creates cross-reference links
5. ✅ `special-lists-preprocessor.py` - Prepares special list formats

### Stage 2: mdBook Build (/src → /book)
- ✅ Converts markdown to HTML
- ✅ Applies base structure
- ✅ Preserves custom HTML from preprocessing

### Stage 3: Postprocessing (/book HTML files)
1. ✅ `unified-list-processor.py` - Adds classes to parenthetical lists
2. ✅ `enhanced-custom-processor.py` - Adds document notes, WHEREAS clauses
3. ✅ `clean-table-formatting.py` - Enhances table formatting
4. ⚠️ `fix-definition-sublists.py` - Needs verification

## Testing Recommendations

### Critical Patterns to Test
1. **Form fields in different contexts**:
   - In headers: `# ORDINANCE {{filled:52}}`
   - In paragraphs: `The city of {{filled:Rivergrove}}`
   - In lists: `- {{filled:Item 1}}`

2. **Nested list structures**:
   ```markdown
   1. Main item
      (a) Sub-item
      (b) Sub-item
         (i) Sub-sub-item
   ```

3. **Mixed content in document notes**:
   ```markdown
   ## Document Notes
   ### Stamp {{page:3}}
   COPY
   ### Handwritten text {{page:2}}
   {{filled:John Doe}}, Mayor
   ```

4. **Signature blocks with form fields**:
   ```markdown
   {{signature}}
   {{filled:John Doe}}, Mayor
   ```

## Known Issues

1. **Definition Lists**: CSS classes may not be consistently applied
2. **Custom numbered lists**: Starting at non-1 values needs verification
3. **Nested parenthetical lists**: Deep nesting may lose formatting

## Recommendations

1. **Add visual regression tests** for critical patterns
2. **Create test documents** with all pattern combinations
3. **Add validation to build pipeline** to catch broken patterns
4. **Document edge cases** in pattern usage

## Files to Review

### Preprocessing Scripts
- `/scripts/preprocessing/form-fields-processor.py` ✅
- `/scripts/preprocessing/sync-resolutions.py` ✅
- `/scripts/preprocessing/footnote-preprocessor.py` ✅
- `/scripts/preprocessing/special-lists-preprocessor.py` ✅

### Postprocessing Scripts
- `/scripts/postprocessing/unified-list-processor.py` ✅
- `/scripts/postprocessing/enhanced-custom-processor.py` ✅
- `/scripts/postprocessing/clean-table-formatting.py` ✅
- `/scripts/postprocessing/fix-definition-sublists.py` ⚠️

### CSS Files
- `/theme/css/components/form-fields.css` ✅
- `/theme/css/components/lists.css` ✅
- `/theme/css/documents/document-notes.css` ✅
- `/theme/css/components/tables.css` ✅