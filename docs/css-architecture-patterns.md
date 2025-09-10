# CSS Architecture Patterns

## Overview
This document outlines the architectural patterns and best practices established during the CSS refactor project.

## Core Principles

### 1. Zero !important Declaration Policy
**Pattern**: Use higher specificity instead of !important
```css
/* ❌ Avoid */
.sidebar {
    background: #fff !important;
}

/* ✅ Preferred */
html .sidebar {
    background: var(--color-bg-light);
}
```

**Rationale**: !important creates maintenance nightmares and breaks the natural CSS cascade.

### 2. Design Token System
**Pattern**: All values should reference CSS variables
```css
/* ❌ Avoid */
.component {
    padding: 12px;
    color: #333;
}

/* ✅ Preferred */
.component {
    padding: var(--space-padding-md);
    color: var(--color-text);
}
```

**Benefits**:
- Single source of truth
- Easy theme switching
- Consistent spacing and colors
- Simplified maintenance

### 3. Modular File Organization
**Pattern**: Organize CSS by concern, not by page

```
theme/css/
├── base/       # Foundation
├── layout/     # Structure
├── components/ # Reusable UI
└── documents/  # Document-specific
```

**Benefits**:
- Clear separation of concerns
- Easy to find and modify styles
- Prevents duplication
- Supports code reuse

### 4. Component Isolation
**Pattern**: Each component should be self-contained

```css
/* navigation.css - Complete and isolated */
.nav-header { /* ... */ }
.nav-controls { /* ... */ }
.nav-btn { /* ... */ }
```

**Rules**:
- No dependencies on other components
- All related styles in one file
- Clear naming conventions
- Documented purpose

### 5. Responsive-First Design
**Pattern**: Mobile-first with progressive enhancement

```css
/* Base (mobile) styles */
.component {
    padding: var(--space-padding-sm);
}

/* Tablet and up */
@media (min-width: 768px) {
    .component {
        padding: var(--space-padding-md);
    }
}

/* Desktop */
@media (min-width: 1200px) {
    .component {
        padding: var(--space-padding-lg);
    }
}
```

## Naming Conventions

### BEM-Inspired Naming
While not strict BEM, we use similar principles:

```css
/* Block */
.card { }

/* Element */
.card-title { }
.card-description { }

/* Modifier */
.card.ordinances-card { }
.btn.btn-primary { }
```

### Semantic Class Names
Names should describe purpose, not appearance:

```css
/* ❌ Avoid */
.blue-box { }
.big-text { }

/* ✅ Preferred */
.alert-info { }
.section-title { }
```

## State Management

### Active/Selected States
**Pattern**: Use consistent state classes

```css
/* Navigation states */
.nav-btn.active { }
.doc-link.selected { }

/* Hover states */
.component:hover { }

/* Focus states */
.input:focus { }
```

### Loading and Transition States
```css
/* Smooth transitions */
.component {
    transition: var(--transition-normal);
}

/* Loading states */
.component.loading {
    opacity: 0.6;
    pointer-events: none;
}
```

## Color System

### Semantic Color Variables
Colors should have semantic meaning:

```css
:root {
    /* Primary actions */
    --color-primary: #0969da;
    
    /* Success/approval */
    --color-secondary: #059669;
    
    /* Warnings/amendments */
    --color-warning: #d97706;
    
    /* Special/interpretations */
    --color-purple: #8b5cf6;
}
```

### Background Hierarchy
```css
:root {
    --color-bg-primary: #ffffff;    /* Main content */
    --color-bg-light: #f8f9fa;      /* Subtle sections */
    --color-bg-neutral: #f3f4f6;    /* Neutral elements */
}
```

## Spacing System

### Consistent Scale
Use a predictable spacing scale:

```css
:root {
    --space-padding-xs: 4px;    /* 0.25rem */
    --space-padding-sm: 8px;    /* 0.5rem */
    --space-padding-md: 12px;   /* 0.75rem */
    --space-padding-lg: 16px;   /* 1rem */
    --space-padding-xl: 24px;   /* 1.5rem */
    --space-padding-xxl: 32px;  /* 2rem */
}
```

### Application Rules
- Use padding for internal spacing
- Use margin for external spacing
- Prefer gap in flex/grid layouts

## Typography Patterns

### Font Weight Scale
```css
:root {
    --font-weight-normal: 400;
    --font-weight-medium: 500;
    --font-weight-semibold: 600;
    --font-weight-bold: 700;
}
```

### Line Height Scale
```css
:root {
    --line-height-tight: 1.2;    /* Headings */
    --line-height-normal: 1.5;   /* UI elements */
    --line-height-relaxed: 1.6;  /* Body text */
    --line-height-loose: 1.8;    /* Readable content */
}
```

## Component Patterns

### Card Component Pattern
```css
/* Container */
.card {
    background: var(--color-bg-primary);
    border: var(--border-width-thin) solid var(--color-border);
    border-radius: var(--border-radius-lg);
    padding: var(--space-padding-lg);
}

/* Type variants */
.card.ordinances-card { }
.card.resolutions-card { }

/* Interactive states */
.card:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-md);
}
```

### Form Control Pattern
```css
/* Base input */
.input {
    padding: var(--space-padding-sm) var(--space-padding-md);
    border: var(--border-width-thin) solid var(--color-border);
    border-radius: var(--border-radius-md);
    font-size: 14px;
}

/* Focus state */
.input:focus {
    outline: none;
    border-color: var(--color-primary);
    box-shadow: 0 0 0 3px rgba(9, 105, 218, 0.1);
}
```

## Performance Patterns

### CSS Variable Fallbacks
For critical properties, provide fallbacks:

```css
.component {
    color: #333;
    color: var(--color-text, #333);
}
```

### Minimize Reflows
Group related properties:

```css
/* Trigger single reflow */
.component {
    /* Layout properties together */
    display: flex;
    width: 100%;
    height: 200px;
    
    /* Paint properties together */
    background: white;
    color: black;
    border: 1px solid gray;
}
```

## Migration Patterns

### Progressive Enhancement
Start with working basics, enhance with CSS variables:

```css
/* Phase 1: Working baseline */
.component {
    padding: 12px;
    color: #333;
}

/* Phase 2: Enhance with variables */
.component {
    padding: var(--space-padding-md, 12px);
    color: var(--color-text, #333);
}
```

### Gradual Extraction
Move styles incrementally:

1. Identify component boundaries
2. Extract to new file
3. Replace hardcoded values with variables
4. Test thoroughly
5. Remove from original location

## Testing Patterns

### Visual Regression Testing
Every change should maintain visual fidelity:

```bash
# Before changes
npm run test:visual

# After changes
npm run test:visual

# Update if intentional
npm run test:visual:update
```

### CSS Validation
Regular validation ensures quality:

```bash
# Lint CSS
npm run lint:css

# Check metrics
npm run metrics:css
```

## Documentation Patterns

### Component Documentation
Each component should include:

```css
/*
 * Component Name
 * Purpose: What it does
 * Usage: Where it's used
 * Dependencies: Required variables/files
 */
```

### Inline Comments
Use sparingly, focus on "why" not "what":

```css
/* Higher specificity to override mdBook defaults */
html .sidebar {
    background: var(--color-bg-light);
}
```

## Anti-Patterns to Avoid

### 1. Inline Styles
Never use inline styles except for dynamic values.

### 2. ID Selectors for Styling
IDs are for JavaScript, not CSS.

### 3. Overly Specific Selectors
```css
/* ❌ Too specific */
body div.content ul li a.link { }

/* ✅ Better */
.content-link { }
```

### 4. Magic Numbers
```css
/* ❌ Magic number */
.component {
    top: 37px;
}

/* ✅ Semantic value */
.component {
    top: calc(var(--header-height) + var(--space-padding-sm));
}
```

### 5. Mixing Concerns
Keep structure, skin, and behavior separate.

## Future Considerations

### CSS Custom Properties API
Prepare for future enhancements:

```css
@property --color-primary {
    syntax: '<color>';
    initial-value: #0969da;
    inherits: true;
}
```

### Container Queries
Plan for container-based responsive design:

```css
@container (min-width: 400px) {
    .card {
        grid-template-columns: 2fr 1fr;
    }
}
```

### Cascade Layers
Consider future organization with layers:

```css
@layer base, layout, components, utilities;
```

---

## Summary

These patterns ensure:
- **Maintainability**: Easy to update and extend
- **Consistency**: Predictable behavior across components
- **Performance**: Optimized rendering and loading
- **Scalability**: Grows with the project
- **Documentation**: Self-documenting code

Following these patterns will keep the CSS architecture clean, efficient, and maintainable for years to come.