# CSS Architecture Documentation

## Overview
This directory contains all documentation related to the CSS architecture refactor project for the City of Rivergrove documentation site.

## Quick Links

### 🎨 Interactive Resources
- **[Style Guide](style-guide.html)** - Interactive component showcase (open in browser)

### 📚 Main Documentation
- **[Component Guide](../css-component-guide.md)** - Complete component reference
- **[Architecture Patterns](../css-architecture-patterns.md)** - Design patterns and best practices
- **[Architecture Audit](../css-architecture-audit.md)** - Original audit and migration plan

### 📊 Phase Completion Reports
1. **[Phase 3 Complete](CSS-REFACTOR-PHASE-3-COMPLETE.md)** - !important elimination
2. **[Phase 4 Progress](CSS-REFACTOR-PHASE-4-PROGRESS.md)** - Mid-phase 4 status
3. **[Phase 4 Complete](CSS-REFACTOR-PHASE-4-COMPLETE.md)** - Component extraction
4. **[Phase 5 Complete](CSS-REFACTOR-PHASE-5-COMPLETE.md)** - Testing & documentation

### 🔧 Technical Documentation
- **[CSS Testing Guide](README-CSS-TESTING.md)** - Visual regression testing setup
- **[Refactor Handoff](../css-refactor-handoff.md)** - Project handoff documentation
- **[Refactor Status](CSS-REFACTOR-STATUS.md)** - Current status tracking
- **[Phase 4 Startup](css-refactor-phase-4-startup.md)** - Phase 4 startup instructions
- **[Startup Prompt](css-refactor-startup-prompt.md)** - Initial refactor prompt

## File Structure

```
docs/
├── css-refactor/           # This directory
│   ├── README.md          # You are here
│   ├── style-guide.html   # Interactive style guide
│   ├── POSTPROCESSING-CSS-MIGRATION.md # Build integration guide
│   ├── Phase reports      # Completion documentation
│   └── Technical guides   # Testing and setup
├── css-component-guide.md # Component documentation
├── css-architecture-*.md  # Architecture documentation
└── styles/                # Content style guides
    └── STYLE-GUIDE.md    # Content formatting guide
```

## CSS Architecture Structure

```
theme/css/
├── base/                  # Foundation
│   ├── variables.css     # 51+ design tokens
│   └── typography.css    # Text styles
├── layout/               # Structure
│   ├── mdbook-overrides.css
│   ├── page-structure.css
│   └── responsive.css    # All media queries
├── components/           # UI Components (6 files)
│   ├── cards.css
│   ├── footnotes.css
│   ├── tables.css
│   ├── navigation.css
│   ├── relationships-panel.css
│   └── form-controls.css
├── documents/            # Document-specific
│   └── document-notes.css
└── main.css             # Central imports
```

## Key Achievements

### Metrics
- **custom.css reduction**: 1131 → 20 lines (98% reduction)
- **!important eliminated**: 128 → 0 (100% elimination)
- **Modular files created**: 16 components (including enhanced-elements.css)
- **CSS variables**: 51+ design tokens
- **Test stability**: 90/105 passing (85.7%)
- **Inline CSS removed**: 560+ lines from Python processors (100% complete)

### Documentation
- ✅ Complete component documentation
- ✅ Interactive style guide
- ✅ Architecture patterns
- ✅ Validation tools
- ✅ Migration guides

## Build Integration

### Critical Requirements
- Theme directory must be copied AFTER mdBook builds
- Postprocessors handle asset copying via `copy_assets()`
- See [POSTPROCESSING-CSS-MIGRATION.md](POSTPROCESSING-CSS-MIGRATION.md) for details

## Tools & Scripts

### Validation
```bash
# Run CSS validator
node scripts/testing/css-validator.js

# Lint CSS
npm run lint:css

# Check metrics
npm run metrics:css
```

### Testing
```bash
# Visual regression tests
npm run test:visual

# Update baselines
npm run test:visual:update

# Interactive UI
npm run test:visual:ui
```

## Next Steps

### Phase 6: Optimization (Upcoming)
- CSS minification
- Critical CSS extraction
- Bundle optimization
- Performance monitoring

### Maintenance
- Keep documentation updated with changes
- Run validation regularly
- Update style guide with new components
- Maintain zero !important policy

---

*Last Updated: Phase 5 Complete - January 2025*