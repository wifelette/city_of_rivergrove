# CSS Documentation Index

## 📁 Documentation Structure

All CSS documentation is now properly organized:

### Main Documentation (`docs/css-refactor/`)
- **[css-component-guide.md](css-refactor/css-component-guide.md)** - Component reference guide
- **[css-architecture-patterns.md](css-refactor/css-architecture-patterns.md)** - Architecture patterns & best practices
- **[css-architecture-audit.md](css-refactor/css-architecture-audit.md)** - Original audit and 8-week plan
- **[css-architecture-and-build-order.md](css-refactor/css-architecture-and-build-order.md)** - CSS build process and troubleshooting

### CSS Refactor Project (`docs/css-refactor/`)
- **[README.md](css-refactor/README.md)** - CSS refactor documentation index
- **[style-guide.html](css-refactor/style-guide.html)** - Interactive style guide
- **Phase Reports** - Complete documentation of all 5 phases
- **Technical Guides** - Testing setup and handoff docs

### Content Style Guides (`docs/styles/`)
- **[STYLE-GUIDE.md](styles/STYLE-GUIDE.md)** - Content formatting guide
- **[naming-conventions.md](styles/naming-conventions.md)** - File naming standards
- **[form-fields.md](styles/form-fields.md)** - Form field syntax
- **[signature-formatting.md](styles/signature-formatting.md)** - Signature blocks
- **[document-notes.md](styles/document-notes.md)** - Digitization notes

## 🎯 Quick Access

### For Developers
1. **Interactive Style Guide**: Open `docs/css-refactor/style-guide.html` in browser
2. **Component Reference**: See `docs/css-refactor/css-component-guide.md`
3. **Best Practices**: Read `docs/css-refactor/css-architecture-patterns.md`
4. **Build Process**: Read `docs/css-refactor/css-architecture-and-build-order.md`

### For Content Editors
1. **Content Formatting**: See `docs/styles/STYLE-GUIDE.md`
2. **Naming Files**: Follow `docs/styles/naming-conventions.md`

## 🏗️ CSS Architecture

```
theme/css/
├── base/           # Foundation (variables, typography)
├── layout/         # Structure (page layout, responsive)
├── components/     # UI components (6 files)
├── documents/      # Document-specific styles
└── main.css        # Central import manager
```

## 📊 Key Metrics

- **13** modular CSS files
- **51+** CSS variables
- **0** !important declarations
- **84%** reduction in custom.css
- **100%** documentation coverage

---

*For complete CSS refactor documentation, see [docs/css-refactor/README.md](css-refactor/README.md)*