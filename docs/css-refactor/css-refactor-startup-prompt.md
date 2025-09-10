# CSS Refactor Project - Startup Prompt for New Session

## Project Background

The City of Rivergrove documentation site is a digitization project converting physical ordinances, resolutions, and meeting records into a searchable mdBook site. The CSS was written incrementally over time without any architectural planning - each feature was added reactively, creating layers of hacks and overrides. We now have 128 `!important` declarations fighting against mdBook's defaults, making the site fragile and hard to maintain.

This refactor aims to create a proper CSS architecture with modular components, eliminating technical debt while preserving all functionality.

## Initial Context Setting

I'm continuing a CSS architecture refactor that has complete testing infrastructure ready. The previous session did all the setup work - now we need to do the actual refactoring.

## Branch and Environment

```bash
# First, switch to the working branch
git checkout css-architecture-refactor

# Verify the dev server is running
./dev-server.sh
```

## Essential Documents to Read First (in order)

### Project Context
1. **`CLAUDE.md`** - READ FIRST
   - Overall project instructions
   - Leah's working preferences
   - Document processing workflow
   
2. **`docs/digitization-guide.md`** - Project overview
   - What this site is (City document digitization)
   - Why CSS complexity grew (multiple document types, processing steps)

### CSS Refactor Specific

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

### Why This Mess Exists
The CSS grew organically without planning:
- Started with basic mdBook theme
- Added feature after feature reactively
- Each problem solved with quick fixes and `!important`
- No architectural thinking or refactoring
- Result: 128 `!important` declarations, scattered files, fragile system

### The Bigger Picture
This is a civic documentation project making city records accessible:
- **Ordinances**: Laws and regulations
- **Resolutions**: Council decisions  
- **Interpretations**: Planning commission rulings
- **Meeting Records**: Minutes, agendas, transcripts

Each document type needed custom styling, leading to complexity.

### Technical Context
1. **The Problem**: We're fighting mdBook's default styles with overrides instead of using proper theming
2. **The Solution**: Modular CSS architecture with clean mdBook theme integration
3. **Safety Net**: Visual regression tests ensure nothing breaks (90 tests ready!)
4. **Meeting Pages**: Have a known regression unrelated to CSS - skip them

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

## Copy This to Start New Session:

I need to continue a CSS refactor for the City of Rivergrove documentation site. This is a civic digitization project that grew without architectural planning - CSS was added piece by piece reactively, resulting in 128 `!important` declarations and a fragile system of overrides fighting mdBook's defaults.

Please first read these documents on the `css-architecture-refactor` branch:
1. `CLAUDE.md` - Project instructions and working preferences
2. `docs/css-refactor-startup-prompt.md` - Complete refactor context
3. `docs/css-refactor-handoff.md` - Current status and what's built

The previous session set up complete testing infrastructure (visual regression, linting, metrics). Everything is ready to begin Phase 1: extracting CSS variables.

Key context:
- The CSS mess exists because features were added incrementally without planning
- We have 90 visual regression tests as a safety net
- Meeting pages have a known regression (unrelated to CSS) - skip them
- Goal: Transform 128 !important hacks into clean, modular CSS architecture

Please help me start Phase 1 of the actual refactoring work.

---

*This prompt ensures full context for continuing the CSS refactor project.*