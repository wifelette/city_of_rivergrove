# CSS Refactor Project - Startup Prompt for New Session

## Initial Context Setting

I'm continuing a CSS architecture refactor for the City of Rivergrove documentation site. The previous session set up all testing infrastructure and created a comprehensive plan. I need to pick up where we left off and begin the actual refactoring work.

## Branch and Environment

```bash
# First, switch to the working branch
git checkout css-architecture-refactor

# Verify the dev server is running
./dev-server.sh
```

## Essential Documents to Read First (in order)

1. **`docs/css-refactor-handoff.md`** - START HERE
   - Complete project context
   - Current status
   - What's already built
   - Known issues to avoid

2. **`CSS-REFACTOR-STATUS.md`** - Current metrics
   - Baseline: 128 !important declarations
   - Testing infrastructure ready
   - Next steps outlined

3. **`docs/css-architecture-audit.md`** - Technical details
   - Why we have 128 !important hacks
   - Proposed modular architecture
   - 8-week migration plan

4. **`tests/visual/KNOWN-ISSUES.md`** - What's broken
   - Meeting pages have regression
   - Navigation sidebar missing
   - Tests handle these gracefully

## Quick Status Check

Run these commands to verify everything is working:

```bash
# Check current metrics (baseline: 128 !important)
npm run metrics:css

# Run visual tests (90 should pass)
npm run test:visual

# Check CSS linting issues
npm run lint:css
```

## Current Situation Summary

### What's Done ✅
- Complete testing infrastructure (Playwright, Stylelint, metrics)
- 90 baseline screenshots captured
- Full audit and 8-week plan documented
- All on branch `css-architecture-refactor`

### What's Broken ⚠️
- Meeting pages (/minutes/, /agendas/, /transcripts/) - regression, tests disabled
- Navigation sidebar not rendering - tests made optional
- Some CSS files don't parse in metrics tool

### What's Next 🚀
**Phase 1: Extract CSS Variables (Week 1)**
- Replace hardcoded values with CSS custom properties
- Start with `/custom.css` (1196 lines, 128 !important)
- Test after each change with `npm run test:visual`

## Key Context You Need

1. **The Problem**: We have 128 `!important` declarations because we're fighting mdBook's default styles instead of using proper theming. Files are scattered with no architecture.

2. **The Solution**: Modular CSS architecture with proper mdBook theme integration, eliminating overrides in favor of clean theming.

3. **Safety Net**: Visual regression tests ensure nothing breaks while refactoring. Run tests frequently!

4. **Meeting Pages**: Don't waste time on Meeting pages - they have a known regression unrelated to CSS. Focus on working pages.

## Recommended First Actions

1. **Verify Setup**:
   ```bash
   git status  # Should be on css-architecture-refactor
   npm test    # Should run lint + visual tests
   ```

2. **Review Current CSS Mess**:
   - Open `/custom.css` - see the 128 !important declarations
   - Note the lack of variables or structure
   - This is what we're fixing

3. **Start Phase 1**:
   - Create `/theme/css/base/variables.css`
   - Extract colors first (search for `#` in custom.css)
   - Then spacing values (px, rem, em)
   - Test after each batch of changes

## Success Criteria for Today

- [ ] CSS variables file created
- [ ] At least 20 hardcoded values replaced
- [ ] Visual tests still passing
- [ ] Document progress in handoff doc

## Important Commands

```bash
# Testing
npm run test:visual          # Run tests
npm run test:visual:update   # Update baselines after intentional changes

# Metrics
npm run metrics:css          # Track !important reduction

# Development
./dev-server.sh             # Start server
./build-all.sh              # Full rebuild
```

## Questions This Session Should Answer

1. Can we extract variables without breaking anything? (Use visual tests)
2. How many !important declarations can we eliminate in Phase 1?
3. Are there any unexpected dependencies on the current CSS structure?

## Final Notes

- **Don't recreate infrastructure** - it's all built and working
- **Test frequently** - every 10-15 changes
- **Document decisions** - update handoff doc with progress
- **Meeting pages are broken** - skip them, not your problem
- **Goal**: Reduce 128 !important to <10 over 8 weeks

---

*Use this prompt to start a new Claude session and continue the CSS refactor project with full context.*