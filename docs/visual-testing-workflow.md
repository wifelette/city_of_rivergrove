# Visual Testing Workflow

Quick reference for working with visual regression tests.

## Running Tests

```bash
# Run all visual tests
npm run test:visual

# Run with interactive UI (for reviewing diffs)
npm run test:visual:ui

# Run specific file
npm run test:visual tests/visual/specs/document-notes.spec.js

# Run tests matching a pattern
npx playwright test --grep "form fields"
```

## Updating Baselines (When Changes Are Intentional)

### Option 1: Interactive Review with Auto Test Run (Recommended for Quick Reviews)

```bash
npm run vr
# or
npm run test:visual:review
```

This will:
1. Run all tests automatically (takes ~2 minutes)
2. Show you a numbered list of failed tests
3. Let you interactively select and review tests
4. Update only the selected baselines

**Interactive commands:**
- Enter a test number (e.g., `5`) to review/update that test
  - Then choose: `[v]iew`, `[u]pdate`, or `[s]kip`
- `ui` - Opens Playwright UI with only failed tests
- `report` - Opens HTML report
- `all` - Update all failed tests
- `done` - Finish

### Option 2: UI-First Workflow (Recommended for UI Preference)

```bash
npm run vr:ui
```

This skips the initial test run and goes straight to interactive mode:
1. Type `ui` to open Playwright UI
2. Review all tests in the UI (it will run them)
3. Come back to terminal and use commands to update:
   - `update:file:font-sizes` - Update all tests in font-sizes.spec.js
   - `update:grep:headers should scale` - Update tests matching pattern
   - `update:all` - Update ALL tests
4. Type `done` to apply updates

### Option 2: Update by File

```bash
# Update all tests in a specific file
npm run test:visual:update:file tests/visual/specs/document-notes.spec.js
```

### Option 3: Update by Pattern

```bash
# Update all tests matching a pattern
npm run test:visual:update:grep "document notes"
```

### Option 4: Update Everything

```bash
# Update ALL baselines (use with caution!)
npm run test:visual:update
```

## Typical Workflow

1. **Make CSS changes** in `theme/css/`
2. **Run tests** in VSCode extension or via `npm run test:visual`
3. **Review failures**:
   - In VSCode: Click failed test → "Show Trace" to see diff
   - Or use: `npm run test:visual:ui` for interactive UI
4. **Update baselines** for intentional changes:
   - Use `npm run test:visual:review` for selective updates
   - Or use `npm run test:visual:update:file [file]` for whole files
5. **Run tests again** to confirm everything passes
6. **Commit** the updated baselines

## VSCode Extension

The Playwright Test extension shows tests in the Testing panel:

- ▶️ Run individual tests
- 👁️ View test results inline
- 📊 See pass/fail status

To see visual diffs:
- Click failed test → "Show Trace" → View screenshots
- Or use `npm run test:visual:ui` for better diff viewer

**Note:** The VSCode extension doesn't have a built-in "accept changes" button. Use the npm scripts above to update baselines.

## Tips

- **Before updating:** Always review diffs to ensure changes are intentional
- **Group updates:** Use `file:` pattern to update related tests together
- **Version control:** Git will show you exactly what changed in the snapshots
- **Test on all browsers:** Baselines are per-browser, so a change might affect Chrome but not Firefox

## Common Commands

```bash
# Quick test & review workflow
npm run test:visual && npm run test:visual:review

# Review in UI, then update specific file
npm run test:visual:ui
npm run test:visual:update:file tests/visual/specs/lists.spec.js

# Update all document-notes tests
npm run test:visual:review
# Then select: file:document-notes
```

## Troubleshooting

**Tests fail after CSS changes:**
- This is expected! Review the diffs to confirm the changes look correct
- Use `npm run test:visual:review` to selectively accept changes

**Baselines keep changing:**
- Check if fonts are rendering differently
- Ensure mdbook server is running (tests expect localhost:3000)
- Screenshots are pixel-perfect, so even 1px difference = failure

**Can't find test results:**
- HTML report: `open tests/visual/test-report/index.html`
- Screenshots: `tests/visual/test-results/` (for failures)
- Baselines: `tests/visual/specs/*.spec.js-snapshots/`
