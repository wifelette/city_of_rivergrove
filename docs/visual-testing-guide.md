# Visual Regression Testing Guide

## Overview

This repository uses Playwright for automated visual regression testing to catch unintended CSS and layout changes. Visual tests capture screenshots of pages and components, then compare them pixel-by-pixel to baseline images.

## Why Visual Testing?

Visual regression testing solves a critical problem: **CSS changes in one area can break layout in completely different sections**.

### Real Example from This Project

When adding hanging indent CSS for list formatting in Section 2.060, we accidentally:
- Added extra indentation to Section 5.080 setback specifications
- Created spacing issues in Section 5.120 nested lists

Visual testing would have caught both regressions immediately by comparing full-page screenshots.

## Running Visual Tests

### Quick Commands

```bash
# Run all visual tests
npm run test:visual

# Run only list formatting tests
npm run test:visual -- --grep "List Formatting"

# Update baselines after intentional UI changes
npm run test:visual:update

# Interactive UI to review visual diffs
npm run test:visual:ui
```

### Workflow: Making CSS Changes

**1. Before changing CSS:**
```bash
npm run test:visual
```
This ensures your baseline is clean. All tests should pass.

**2. Make your CSS changes**

Edit files in `theme/css/` as needed.

**3. After changing CSS:**
```bash
npm run test:visual
```

If tests fail, you'll see:
- ❌ Which tests failed
- 📊 Pixel difference count
- 📁 Diff images in `tests/visual/test-results/`

**4. Review the differences:**

```bash
npm run test:visual:ui
```

This opens an interactive UI where you can:
- See before/after comparisons
- View highlighted differences
- Accept or reject changes

**5. If changes are intentional:**

```bash
npm run test:visual:update
git add tests/visual/specs/
git commit -m "Update visual baselines after CSS refactor"
```

## Test Structure

### Test Files

Located in `tests/visual/specs/`:

- **`lists.spec.js`** - List formatting across all types (alpha, numeric, roman, nested)
- **`documents.spec.js`** - Full document pages (ordinances, resolutions, interpretations)
- **`homepage.spec.js`** - Homepage layout and navigation
- **`form-fields.spec.js`** - Form field styling and interactions
- **`enhanced-elements.spec.js`** - Definition items, tables, WHEREAS clauses
- **`document-notes.spec.js`** - Document notes badges and formatting

### Snapshot Organization

Baselines are stored in `tests/visual/specs/[test-file]-snapshots/`:
- Naming: `[snapshot-name]-[browser]-[platform].png`
- Example: `ord-54-full-page-Desktop-Chrome-darwin.png`

### Browser & Device Coverage

Tests run on:
- **Desktop Chrome** (1920x1080)
- **Desktop Firefox** (1920x1080)
- **Desktop Safari** (1920x1080)
- **Tablet** - iPad Pro (1024x1366)
- **Mobile** - iPhone 12 (390x844)

## List Formatting Tests

The `lists.spec.js` file specifically tests for the regressions we encountered:

### Full Page Tests
- **Ord #54 complete page** - Catches any regression anywhere in the document

### Critical Sections
- **Section 5.080** - Setback specifications with special formatting
- **Section 5.120** - Nested numeric lists under alpha items
- **Section 2.060** - Hanging indent for wrapped text (the original issue!)

### Responsive Tests
- Mobile viewport rendering
- Print mode styling

## Understanding Test Results

### When Tests Pass ✓

```
✓ [Desktop Chrome] › Section 5.080 setback specifications (4.3s)
```

The screenshot matches the baseline pixel-for-pixel.

### When Tests Fail ✘

```
✘ [Desktop Chrome] › Section 5.080 setback specifications

  Expected: section-5080-setbacks-Desktop-Chrome-darwin.png
  Received: 127 pixels differ

  Diff: tests/visual/test-results/.../section-5080-setbacks-diff.png
```

Check the diff image to see what changed (highlighted in magenta/red).

### Common Failure Reasons

1. **Intentional CSS changes** - Update baselines
2. **Unintended regressions** - Fix the CSS
3. **Font loading timing** - Flaky, re-run
4. **Browser rendering differences** - Expected for Firefox (see Known Issues)

## Known Issues

### Firefox Timeouts

Firefox tests sometimes timeout waiting for element stability. This is a known Playwright/Firefox issue with complex layouts.

**Workaround:** Focus on Chrome/Safari baselines. Firefox failures can be ignored unless they reveal actual bugs.

### Safari Pixel Differences

After CSS refactors that change specificity, Safari may show sub-pixel rendering differences that are invisible to human eyes.

**Workaround:** Acceptable trade-off for architectural improvements. Update baselines if needed.

## Configuration

### Playwright Config

Location: `tests/visual/playwright.config.js`

Key settings:
```javascript
{
  baseURL: 'http://localhost:3000',
  timeout: 30000,
  screenshot: {
    mode: 'only-on-failure',
    fullPage: true
  }
}
```

### Auto-starting Dev Server

Tests automatically start the dev server if it's not running:
```javascript
webServer: {
  command: 'npm run serve',
  port: 3000,
  reuseExistingServer: true
}
```

## Best Practices

### When to Update Baselines

✅ **DO update baselines when:**
- You intentionally changed CSS
- You refactored list formatting
- You updated typography
- You modified component styling

❌ **DON'T update baselines when:**
- Tests are failing due to bugs
- You haven't reviewed the diff images
- The changes are unexpected

### Writing New Tests

When adding new visual tests:

1. **Use specific selectors**
   ```javascript
   // Good
   page.locator('#section-5080-general-building-setbacks')

   // Bad
   page.locator('h3').first()
   ```

2. **Test critical sections**
   - Sections with complex formatting
   - Areas prone to regression
   - Responsive breakpoints

3. **Capture full context**
   ```javascript
   // Capture entire section, not just one element
   const section = page.locator('#section-id').locator('..');
   await expect(section).toHaveScreenshot('section.png');
   ```

4. **Name snapshots descriptively**
   ```javascript
   // Good
   'section-5080-setbacks.png'
   'nested-alpha-numeric-lists.png'

   // Bad
   'test1.png'
   'screenshot.png'
   ```

## Troubleshooting

### Tests fail after CSS compilation

```bash
# Recompile CSS
/usr/bin/python3 scripts/build/compile-css.py

# Rebuild site
./build-all.sh --quick

# Re-run tests
npm run test:visual
```

### "Cannot find snapshot" error

Run with `--update-snapshots` to create the baseline:
```bash
npm run test:visual:update -- --grep "your test name"
```

### Flaky tests (pass sometimes, fail others)

1. Increase timeout in test:
   ```javascript
   await expect(page).toHaveScreenshot('name.png', {
     timeout: 10000
   });
   ```

2. Wait for specific conditions:
   ```javascript
   await page.waitForLoadState('networkidle');
   await page.waitForSelector('.list-marker-alpha');
   ```

### All tests fail after git pull

Someone updated the CSS. Review changes, then update baselines if appropriate:
```bash
npm run test:visual:ui  # Review
npm run test:visual:update  # Accept
```

## CI/CD Integration (Future)

To add visual testing to GitHub Actions:

```yaml
# .github/workflows/visual-tests.yml
name: Visual Regression Tests

on: [pull_request]

jobs:
  test:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm install
      - run: npm run test:visual
      - uses: actions/upload-artifact@v3
        if: failure()
        with:
          name: visual-test-results
          path: tests/visual/test-results/
```

## Resources

- [Playwright Visual Testing Docs](https://playwright.dev/docs/test-snapshots)
- [Project Test Specs](../tests/visual/specs/)
- [Known Visual Issues](../tests/visual/KNOWN-ISSUES.md)
- [CSS Compilation Guide](./css-refactor/css-compilation-guide.md)
