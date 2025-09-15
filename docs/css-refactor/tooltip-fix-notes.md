# Tooltip Styling Fix Notes

## Issue #25: Signature Tooltip Inheritance Problem

### Problem
Signature tooltips (from `{{signature}}` markers) were inheriting font properties from their parent `.signature-mark` element (Dancing Script font, 1.4em size) despite having identical CSS to form field tooltips.

### Root Cause
CSS pseudo-elements (`::after`) can inherit certain properties from their parent element, particularly font properties. The signature mark uses a decorative font that was bleeding through to the tooltip.

### Solution
Added explicit font property resets to all tooltip pseudo-elements in `/theme/css/components/form-fields.css`:

```css
.signature-mark::after {
    /* Explicit font reset to prevent inheritance */
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    font-size: 12px;
    font-weight: normal;
    font-style: normal;
    line-height: 1.4;
    /* ... rest of tooltip styles ... */
}
```

### Files Modified
- `theme/css/components/form-fields.css` - Added explicit font resets to all tooltip styles
- `scripts/utils/title_resolver.py` - Added `strip_markdown_links()` to prevent SUMMARY.md issues

### Testing
- Test file available at `/test-tooltips.html`
- Tooltips should now display consistently across:
  - Form fields (`{{filled:text}}`)
  - Signature marks (`{{signature}}`)
  - All document contexts

### Related Issue
This fix also addressed a recurring SUMMARY.md parsing error caused by markdown links in document titles. See `/docs/SUMMARY-md-handling.md` for details.