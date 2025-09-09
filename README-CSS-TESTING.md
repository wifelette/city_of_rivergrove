# CSS Testing Infrastructure

## Overview

We've set up comprehensive testing infrastructure to support the CSS architecture refactor:

### 1. Visual Regression Testing (Playwright)
- **Purpose**: Catch unintended visual changes
- **Coverage**: Desktop, tablet, mobile across Chrome, Firefox, Safari
- **Run tests**: `npm run test:visual`
- **Update baselines**: `npm run test:visual:update`
- **View UI**: `npm run test:visual:ui`

### 2. CSS Quality Linting (Stylelint)
- **Purpose**: Enforce consistent CSS patterns
- **Key rules**:
  - No `!important` declarations (warnings)
  - No ID selectors for styling
  - Maximum 3 levels of nesting
  - Maximum specificity of 0,3,0
- **Run linter**: `npm run lint:css`
- **Auto-fix**: `npm run lint:css:fix`

### 3. CSS Metrics Tracking
- **Purpose**: Measure improvement progress
- **Tracks**:
  - Total `!important` count (currently 128)
  - High specificity selectors
  - File sizes
  - Nesting depth
  - Vendor prefixes
- **Run metrics**: `npm run metrics:css`

## Current Baseline

As of January 2025:
- **128 `!important` declarations** in custom.css
- **1196 lines** of override CSS
- **No component structure**
- **Mixed concerns** throughout files

## Testing Commands

```bash
# Install dependencies
npm install

# Run all tests
npm test

# Visual regression tests
npm run test:visual                 # Run tests
npm run test:visual:update          # Update screenshots
npm run test:visual:ui              # Interactive UI

# CSS linting
npm run lint:css                    # Check CSS
npm run lint:css:fix               # Auto-fix issues

# Metrics
npm run metrics:css                 # Generate metrics report
```

## Files Created

- `.stylelintrc.json` - Stylelint configuration
- `tests/visual/` - Playwright visual tests
- `scripts/testing/css-metrics.js` - Metrics analyzer
- `docs/css-architecture-audit.md` - Full audit document

## Next Steps

1. **Create baseline screenshots**: Run `npm run test:visual:update` to create initial screenshots
2. **Review Stylelint warnings**: Run `npm run lint:css` to see all issues
3. **Start refactoring**: Follow the migration plan in `docs/css-architecture-audit.md`
4. **Track progress**: Use metrics to measure improvement

## Success Criteria

- Reduce `!important` declarations from 128 to < 10
- Pass all visual regression tests
- 100% Stylelint compliance
- Modular component structure
- < 50KB total CSS