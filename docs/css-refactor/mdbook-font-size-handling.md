# mdBook Font Size Handling

## The 62.5% Root Font Size Trick

mdBook uses a common CSS pattern where it sets the root font-size to 62.5%:

```css
:root {
    /* Browser default font-size is 16px, this way 1 rem = 10px */
    font-size: 62.5%;
}
```

This makes calculations easier:
- 1rem = 10px (instead of 16px)
- 1.6rem = 16px
- 2.4rem = 24px
- etc.

## The Problem We Encountered

When we set `body { font-size: 1rem; }` thinking it would be 16px, it was actually 10px because of mdBook's root scaling. This made all content appear 62.5% smaller than intended.

## The Solution

We must account for mdBook's scaling in our typography:

```css
body {
    /* mdBook sets :root font-size to 62.5%, so 1rem = 10px
       We need 1.6rem to get back to 16px default size */
    font-size: 1.6rem;
}
```

## Important Notes

1. **All rem-based sizes must account for this scaling**
   - If you want 16px, use 1.6rem
   - If you want 12px, use 1.2rem
   - If you want 20px, use 2rem

2. **Consider using px for absolute sizes**
   - Tooltips, badges, and UI elements that need consistent sizing
   - Elements that shouldn't scale with root font size

3. **Test font sizes after CSS changes**
   - Run the visual regression tests: `npm run test:visual -- font-sizes.spec.js`
   - Check computed styles in browser DevTools
   - Verify body font-size is 16px, not 10px

## Files Affected

- `theme/css/rivergrove-typography.css` - Base body font size
- `theme/css/base/variables.css` - Font size variables (using em, not rem)
- `tests/visual/specs/font-sizes.spec.js` - Visual regression tests

## Testing

Always verify font sizes after CSS changes:

```bash
# Run font size tests
npm run test:visual -- font-sizes.spec.js

# Or check manually in DevTools console
document.defaultView.getComputedStyle(document.body).fontSize
# Should return "16px"
```