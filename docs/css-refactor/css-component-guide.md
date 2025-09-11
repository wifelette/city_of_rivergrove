# CSS Component Guide

## Overview
This guide documents all CSS components in the City of Rivergrove documentation site's modular architecture.

## Architecture Overview

```
theme/css/
├── base/                    # Foundation layer
│   ├── variables.css        # Design tokens
│   └── typography.css       # Base text styles
├── layout/                  # Structure layer
│   ├── mdbook-overrides.css # mdBook customization
│   ├── page-structure.css   # Page layout
│   └── responsive.css       # Media queries
├── components/              # Component layer
│   ├── cards.css           # Card components
│   ├── footnotes.css       # Footnote styling
│   ├── tables.css          # Table enhancements
│   ├── navigation.css      # Navigation system
│   ├── relationships-panel.css # Right panel
│   └── form-controls.css   # Form elements
└── documents/               # Document-specific
    └── document-notes.css   # Digitization notes
```

## Component Documentation

### 1. Variables (`base/variables.css`)

**Purpose**: Central design token system for consistent styling

**Key Variables**:
- **Colors**: 51+ color variables including primary, secondary, text, and backgrounds
- **Spacing**: Padding and margin scales (xs, sm, md, lg, xl, xxl)
- **Typography**: Font sizes, weights, line heights
- **Borders**: Width, radius, and color definitions
- **Shadows**: Box shadow definitions
- **Transitions**: Animation timing

**Usage Example**:
```css
.my-component {
    padding: var(--space-padding-md);
    color: var(--color-text);
    border: var(--border-width-thin) solid var(--color-border);
}
```

### 2. Typography (`base/typography.css`)

**Purpose**: Base typography and heading styles

**Features**:
- Heading hierarchy (h1-h6)
- Blockquote styling
- Table spacing
- Special formatting classes

**Classes**:
- `.section-ref` - Section reference badges

**Usage**:
```html
<h2>Section Title</h2>
<span class="section-ref">§ 2.1</span>
```

### 3. Navigation (`components/navigation.css`)

**Purpose**: Complete sidebar navigation system

**Key Classes**:
- `.sidebar` - Main sidebar container
- `.nav-header` - Navigation header with controls
- `.nav-view-toggle` - View toggle buttons
- `.nav-btn` - Navigation button styles
- `.doc-link` - Document link formatting
- `.doc-number`, `.doc-title`, `.doc-year` - Document metadata

**States**:
- `.selected`, `.active` - Active document highlighting
- `.grouped-item` - Items under topic/decade headers

**Usage**:
```html
<div class="sidebar">
  <div class="nav-header">
    <div class="nav-view-toggle">
      <button class="nav-btn active">All</button>
      <button class="nav-btn">By Year</button>
    </div>
  </div>
  <li class="chapter-item">
    <a class="doc-link">
      <span class="doc-number">Ord #52</span>
      <span class="doc-title">Building Code</span>
      <span class="doc-year">2024</span>
    </a>
  </li>
</div>
```

### 4. Cards (`components/cards.css`)

**Purpose**: Card-based layouts for landing pages and document listings

**Components**:
- **Document Cards** (`.doc-card`)
  - Landing page navigation cards
  - Color-coded by document type
  - Hover effects and statistics
  
- **Simple Cards** (`.simple-card`)
  - Compact card layout
  - Document count display
  - Grid-based layout

**Classes**:
- `.doc-cards` - Card grid container
- `.doc-card` - Individual card
- `.ordinances-card`, `.resolutions-card`, `.interpretations-card` - Type-specific
- `.card-icon` - Icon display
- `.card-description` - Description text
- `.card-stats` - Statistics badge

**Usage**:
```html
<div class="doc-cards">
  <a href="/ordinances/" class="doc-card ordinances-card">
    <div class="card-icon">📋</div>
    <h2>Ordinances</h2>
    <p class="card-description">City laws and regulations</p>
    <span class="card-stats">52 documents</span>
  </a>
</div>
```

### 5. Form Controls (`components/form-controls.css`)

**Purpose**: Buttons, dropdowns, and form elements

**Components**:
- **Buttons** (`.btn`)
  - Primary, secondary variants
  - Size options (small, large)
  - Hover and active states
  
- **Dropdowns** (`.section-dropdown-btn`)
  - Section selector
  - Active state indication
  
- **Search** (`.nav-search-input`)
  - Search input with clear button
  
- **Toggles** (`.sort-toggle`)
  - Sort direction toggles
  - Toggle switches

**Usage**:
```html
<button class="btn btn-primary">Submit</button>
<input class="nav-search-input" placeholder="Search...">
<div class="sort-toggle">
  <button class="sort-toggle-btn active">↑</button>
  <button class="sort-toggle-btn">↓</button>
</div>
```

### 6. Tables (`components/tables.css`)

**Purpose**: Enhanced table styling

**Features**:
- Blockquote table improvements
- Alternating row colors
- Table footnotes
- Responsive sizing

**Classes**:
- `.table-footnotes` - Footnote container
- Automatic styling for `blockquote table`

**Usage**:
```html
<table>
  <thead>...</thead>
  <tbody>...</tbody>
</table>
<div class="table-footnotes">
  <p>† Source: City Records</p>
</div>
```

### 7. Relationships Panel (`components/relationships-panel.css`)

**Purpose**: Right sidebar for document relationships

**Components**:
- Panel container with collapse functionality
- Color-coded relationship sections
- Count badges
- Relationship item links

**Classes**:
- `.right-panel` - Main container
- `.right-panel-header` - Panel header
- `.relationship-section` - Section container
- `.relationship-count` - Count badge
- `.rel-doc-number`, `.rel-doc-title` - Document info

**Usage**:
```html
<div class="right-panel">
  <div class="right-panel-header">
    <h3>Related Documents</h3>
  </div>
  <div class="relationship-section amendments">
    <h5>Amendments <span class="relationship-count">3</span></h5>
    <div class="relationship-items">...</div>
  </div>
</div>
```

### 8. Document Notes (`documents/document-notes.css`)

**Purpose**: Digitization notes and metadata

**Features**:
- Distinctive visual styling
- Icon indicator
- Print-friendly
- Automatic HR hiding

**Usage**:
```html
<div class="document-note">
  <h2>Document Notes</h2>
  <p>This document was digitized from the original paper copy.</p>
</div>
```

### 9. Responsive Design (`layout/responsive.css`)

**Purpose**: All responsive breakpoints and adjustments

**Breakpoints**:
- **Tablet**: 1200px
- **Mobile**: 768px  
- **Small Mobile**: 480px
- **Print**: Print media styles
- **Accessibility**: Reduced motion support

**Features**:
- Component-specific adjustments
- Print optimization
- High DPI display support

## CSS Variable Reference

### Color Palette
```css
--color-primary: #0969da;      /* Primary blue */
--color-secondary: #059669;    /* Green accent */
--color-warning: #d97706;      /* Orange warning */
--color-purple: #8b5cf6;       /* Purple accent */
```

### Spacing Scale
```css
--space-padding-xs: 4px;
--space-padding-sm: 8px;
--space-padding-md: 12px;
--space-padding-lg: 16px;
--space-padding-xl: 24px;
--space-padding-xxl: 32px;
```

### Typography
```css
--font-weight-normal: 400;
--font-weight-medium: 500;
--font-weight-semibold: 600;
--font-weight-bold: 700;
--line-height-tight: 1.2;
--line-height-normal: 1.5;
--line-height-relaxed: 1.6;
```

## Best Practices

### 1. Always Use Variables
```css
/* Good */
.component {
    padding: var(--space-padding-md);
    color: var(--color-text);
}

/* Avoid */
.component {
    padding: 12px;
    color: #333;
}
```

### 2. Component Isolation
Each component should be self-contained and not depend on other components' styles.

### 3. Specificity Management
Use higher specificity instead of !important:
```css
/* Good */
html .sidebar {
    background: var(--color-bg-light);
}

/* Avoid */
.sidebar {
    background: #fff !important;
}
```

### 4. Responsive First
Consider responsive behavior from the start:
```css
.component {
    /* Base mobile styles */
}

@media (min-width: 768px) {
    .component {
        /* Tablet and up */
    }
}
```

## Migration Guide

### From Old Styles to New Components

| Old Class | New Component | Location |
|-----------|--------------|----------|
| Custom navigation | `.nav-header`, `.doc-link` | `navigation.css` |
| Inline buttons | `.btn`, `.btn-primary` | `form-controls.css` |
| Custom cards | `.doc-card`, `.simple-card` | `cards.css` |
| Hardcoded colors | CSS variables | `variables.css` |
| Media queries | Consolidated | `responsive.css` |

## Testing Components

### Visual Testing
```bash
# Run visual regression tests
npm run test:visual

# Update baselines if needed
npm run test:visual:update
```

### CSS Validation
```bash
# Lint CSS files
npm run lint:css

# Auto-fix issues
npm run lint:css:fix

# Check metrics
npm run metrics:css
```

## Contributing

When adding new components:
1. Create a new file in the appropriate directory
2. Use CSS variables for all values
3. Add to `main.css` imports
4. Document in this guide
5. Test with visual regression

---

*Last Updated: Phase 5 - CSS Architecture Documentation*