# CSS Architecture Audit - City of Rivergrove

## Current State Analysis

### 1. File Structure Issues

**CSS Files Scattered Across Project:**
- `/custom.css` - Main override file (1196 lines, 128 !important declarations)
- `/src/custom.css` - Duplicate in src directory
- `/src/sidebar-resize.css` - Orphaned sidebar styling
- `/theme/css/rivergrove-typography.css` - Attempted modularization
- `/scripts/config/special-formatting.css` - Processing-specific styles
- mdBook default files (general.css, chrome.css, variables.css)

**Problems:**
- No clear separation of concerns
- Duplicate files in different locations
- Mixed mdBook defaults with custom overrides
- No naming convention or module structure

### 2. CSS Override Anti-Patterns

**Massive !important Usage (128 instances):**
```css
/* Examples from custom.css */
#sidebar { display: none !important; }
.page-wrapper { margin-left: 300px !important; }
.nav-chapters { display: none !important; }
```

**Why This Happened:**
- Fighting against mdBook's default styles instead of working with them
- No proper theme customization approach
- Reactive fixes added over time without refactoring
- Specificity wars with mdBook's inline styles

### 3. Lack of Architecture

**Current Issues:**
- No CSS methodology (BEM, SMACSS, etc.)
- No component-based structure
- Styles mixed between:
  - Layout (page structure)
  - Components (cards, navigation)
  - Utilities (spacing, typography)
  - Document-specific (ordinances, resolutions)
  - Processing artifacts (filled forms, footnotes)

### 4. Technical Debt Accumulation

**Symptoms:**
- Browser console warnings about conflicting styles
- Layout shifts during page load
- Broken styles after mdBook updates
- Difficulty making simple changes
- No way to test styles

## Root Causes

1. **Incremental Development**: Features added one-by-one without overall design
2. **mdBook Limitations**: Working against the tool rather than with it
3. **No Testing**: Changes made blindly, hoping nothing breaks
4. **No Documentation**: No style guide or component library
5. **Processing Pipeline Complexity**: Multiple build steps adding inline styles

## Proposed Solution Architecture

### 1. Modular CSS Structure

```
theme/
├── css/
│   ├── base/
│   │   ├── reset.css         # Normalize browser defaults
│   │   ├── typography.css    # Base font styles
│   │   └── variables.css     # CSS custom properties
│   ├── layout/
│   │   ├── page.css          # Page structure
│   │   ├── navigation.css    # Nav sidebar
│   │   └── content.css       # Main content area
│   ├── components/
│   │   ├── cards.css         # Landing page cards
│   │   ├── forms.css         # Form field styling
│   │   ├── tables.css        # Table formatting
│   │   ├── footnotes.css     # Footnote styling
│   │   └── signatures.css    # Signature blocks
│   ├── documents/
│   │   ├── ordinances.css    # Ordinance-specific
│   │   ├── resolutions.css   # Resolution-specific
│   │   └── interpretations.css # Interpretation-specific
│   └── utilities/
│       ├── spacing.css       # Margin/padding utilities
│       └── display.css       # Show/hide utilities
```

### 2. CSS Architecture Principles

**Use CSS Custom Properties:**
```css
:root {
  --nav-width: 300px;
  --sidebar-width: 280px;
  --content-max-width: 800px;
  --color-primary: #3b82f6;
  --spacing-unit: 8px;
}
```

**Component-Based Approach:**
```css
/* Instead of: */
.simple-card h3 { ... }  /* Too generic */

/* Use: */
.card--landing { ... }
.card__title { ... }
.card__count { ... }
```

**Specificity Management:**
- Maximum 3 levels of nesting
- No ID selectors for styling
- Minimal use of !important (only for utilities)
- Use data attributes for state

### 3. mdBook Theme Integration

**Proper Theme Override:**
```toml
# book.toml
[output.html]
theme = "theme"
default-theme = "rivergrove"
preferred-dark-theme = "rivergrove"
```

**Custom theme.toml:**
- Define color schemes
- Set font stacks
- Configure layout variables

### 4. Testing Infrastructure

**Visual Regression Testing:**
- Percy or BackstopJS for screenshot comparison
- Test matrix:
  - Document types (ordinances, resolutions, etc.)
  - Screen sizes (mobile, tablet, desktop)
  - Browsers (Chrome, Firefox, Safari)

**Style Linting:**
- Stylelint configuration
- Rules for:
  - Property order
  - Selector complexity
  - !important usage
  - Naming conventions

**Component Testing:**
- Storybook for component library
- Isolated component development
- Documentation of variants

### 5. Build Pipeline Integration

**CSS Processing:**
1. PostCSS for:
   - Autoprefixer
   - CSS nesting
   - Custom property fallbacks
2. CSS minification
3. Source maps for debugging

**Critical CSS:**
- Inline critical styles
- Lazy-load non-critical styles
- Prevent FOUC (Flash of Unstyled Content)

## Migration Plan

### Phase 1: Audit & Document (Week 1)
- [x] Complete CSS audit
- [ ] Document all component types
- [ ] Create style inventory
- [ ] Identify critical vs non-critical styles

### Phase 2: Setup Infrastructure (Week 2)
- [ ] Setup PostCSS pipeline
- [ ] Configure Stylelint
- [ ] Setup visual regression testing
- [ ] Create component library structure

### Phase 3: Refactor Core Styles (Week 3-4)
- [ ] Extract CSS variables
- [ ] Modularize base styles
- [ ] Refactor layout system
- [ ] Remove !important declarations

### Phase 4: Component Migration (Week 5-6)
- [ ] Migrate card components
- [ ] Migrate navigation
- [ ] Migrate document styles
- [ ] Migrate utility classes

### Phase 5: Testing & Documentation (Week 7)
- [ ] Write visual regression tests
- [ ] Create style guide
- [ ] Document component usage
- [ ] Performance testing

### Phase 6: Cleanup & Optimization (Week 8)
- [ ] Remove old CSS files
- [ ] Optimize build pipeline
- [ ] Final testing
- [ ] Deploy

## Success Metrics

1. **Code Quality:**
   - < 10 !important declarations
   - No duplicate styles
   - 100% Stylelint compliance

2. **Performance:**
   - < 50KB total CSS
   - < 100ms style parsing
   - No layout shifts

3. **Maintainability:**
   - Clear component boundaries
   - Documented style guide
   - Passing visual tests

4. **Developer Experience:**
   - Easy to add new components
   - Clear naming conventions
   - Fast build times

## Risk Mitigation

1. **Gradual Migration:** Keep old styles during transition
2. **Feature Flags:** Toggle between old/new styles
3. **Comprehensive Testing:** Visual regression for all pages
4. **Rollback Plan:** Git branches for each phase
5. **Documentation:** Record all decisions and patterns

## Next Steps

1. Review and approve this audit
2. Set up testing infrastructure
3. Begin Phase 1 implementation
4. Weekly progress reviews

---

*Document created: January 2025*
*Last updated: January 2025*