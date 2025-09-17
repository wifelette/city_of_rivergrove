# Style Guide Subpage Template & Standards

## Overview
This document defines the standardized structure and design for all CSS Style Guide subpages.

## Subpage Structure

All style guide subpages must follow this consistent structure:

### 1. File Naming
- Pattern: `{component}-style-guide.html`
- Examples: `lists-style-guide.html`, `tables-style-guide.html`, `forms-style-guide.html`
- Location: `/docs/css-refactor/`

### 2. Page Layout

```
┌──────────────────────────────────────────────┐
│ Breadcrumb: ← Back to Style Guide / [Page]  │
├──────────────────────────────────────────────┤
│              Page Header                      │
│   - Title (h1)                               │
│   - Description (p)                          │
├─────────────┬────────────────────────────────┤
│             │                                │
│   Sticky    │                                │
│   Sidebar   │     Main Content Area          │
│   (250px)   │                                │
│             │                                │
│   TOC       │     Multiple sections          │
│   Links     │     with examples              │
│             │                                │
└─────────────┴────────────────────────────────┘
```

### 3. Required HTML Structure

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>City of Rivergrove - [Component] Style Guide</title>
    <link rel="stylesheet" href="../../theme/css/main.css">
    <style>
        /* Standard styles - see section 4 */
    </style>
</head>
<body>
    <!-- Breadcrumb -->
    <div class="breadcrumb">
        <a href="style-guide.html">← Back to Style Guide</a> / [Component] Style Guide
    </div>

    <!-- Header -->
    <div class="style-header">
        <h1>[Component] Style Guide</h1>
        <p>Comprehensive documentation for [describe component purpose]</p>
    </div>

    <!-- Main Container with Grid -->
    <div class="main-container">
        <!-- Sticky Sidebar Navigation -->
        <aside class="toc-container">
            <h3>📚 Contents</h3>
            <ul class="toc-list">
                <li><a href="#section1">Section 1</a></li>
                <li><a href="#section2">Section 2</a>
                    <ul>
                        <li><a href="#subsection">Subsection</a></li>
                    </ul>
                </li>
                <!-- Cross-links to other guides -->
                <li style="margin-top: 20px; padding-top: 15px; border-top: 1px solid #e5e7eb;">
                    <a href="other-guide.html">→ Other Guide</a>
                </li>
            </ul>
        </aside>

        <!-- Content Container -->
        <div class="content-container">
            <!-- Content sections -->
            <div class="style-section" id="section1">
                <!-- Section content -->
            </div>

            <!-- More sections... -->

            <!-- Footer -->
            <div class="style-section" style="text-align: center; background: #f0f9ff;">
                <p style="margin: 0; color: #666;">
                    <strong>City of Rivergrove [Component] Style Guide</strong><br>
                    Last Updated: [Date]<br>
                    <a href="style-guide.html" style="color: #0969da;">Return to Main Style Guide</a>
                </p>
            </div>
        </div>
    </div>
</body>
</html>
```

### 4. Required CSS Classes & Styles

```css
/* Base body styles */
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    line-height: 1.6;
    color: #333;
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
    background: #f5f5f5;
}

/* Breadcrumb */
.breadcrumb {
    margin-bottom: 20px;
    color: #666;
    font-size: 14px;
}

.breadcrumb a {
    color: #0969da;
    text-decoration: none;
}

.breadcrumb a:hover {
    text-decoration: underline;
}

/* Header */
.style-header {
    background: white;
    padding: 30px;
    border-radius: 8px;
    margin-bottom: 30px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

/* Main Grid Container */
.main-container {
    display: grid;
    grid-template-columns: 250px 1fr;
    gap: 30px;
    max-width: 1400px;
    margin: 0 auto;
}

/* Sticky Sidebar */
.toc-container {
    position: sticky;
    top: 20px;
    height: fit-content;
    background: white;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.toc-container h3 {
    color: #0969da;
    margin-top: 0;
    margin-bottom: 15px;
    font-size: 16px;
}

.toc-list {
    list-style: none;
    padding: 0;
    margin: 0;
}

.toc-list li {
    margin-bottom: 8px;
}

.toc-list a {
    color: #666;
    text-decoration: none;
    font-size: 14px;
    display: block;
    padding: 4px 0;
    border-left: 2px solid transparent;
    padding-left: 10px;
    transition: all 0.2s;
}

.toc-list a:hover {
    color: #0969da;
    border-left-color: #0969da;
    background: #f0f9ff;
}

/* Content Area */
.content-container {
    min-width: 0; /* Prevent overflow */
}

.style-section {
    background: white;
    padding: 30px;
    border-radius: 8px;
    margin-bottom: 20px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.style-section h2 {
    color: #0969da;
    border-bottom: 2px solid #e5e7eb;
    padding-bottom: 10px;
    margin-bottom: 20px;
}

/* Responsive */
@media (max-width: 768px) {
    .main-container {
        grid-template-columns: 1fr;
    }

    .toc-container {
        position: static;
        margin-bottom: 30px;
    }
}
```

### 5. Content Standards

#### Example Containers
```html
<div class="example-container">
    <div class="example-title">Example Name</div>
    <!-- Example content -->
</div>
```

#### Code Blocks
- Use `.code-snippet` for CSS/JS examples
- Use `.markdown-example` for Markdown syntax
- Always show both markdown and rendered output when relevant

#### Info/Warning Boxes
```html
<div class="info-box">
    <h4>ℹ️ Information</h4>
    <p>Helpful information here</p>
</div>

<div class="warning-box">
    <h4>⚠️ Warning</h4>
    <p>Important warning here</p>
</div>
```

### 6. Navigation Integration

#### Main Style Guide TOC Entry
In the main `style-guide.html`, each component with a subpage should have:
```html
<li><a href="#component">📊 Component Name</a>
    <ul class="toc-sub">
        <li><a href="component-style-guide.html">📖 Detailed Component Guide</a></li>
    </ul>
</li>
```

#### Cross-linking Between Subpages
Each subpage should link to related subpages in the sidebar:
```html
<li style="margin-top: 20px; padding-top: 15px; border-top: 1px solid #e5e7eb;">
    <a href="related-guide.html">→ Related Guide</a>
</li>
```

### 7. Consistency Checklist

Before publishing a new subpage, verify:

- [ ] Breadcrumb navigation at top
- [ ] Consistent header with title and description
- [ ] Grid layout with 250px sidebar
- [ ] Sticky sidebar navigation
- [ ] All sections have unique IDs for linking
- [ ] Footer with date and return link
- [ ] Responsive behavior at 768px breakpoint
- [ ] Cross-links to related guides in sidebar
- [ ] TOC entry in main style guide
- [ ] Consistent color scheme and typography
- [ ] Example containers with proper styling
- [ ] Code examples with syntax highlighting

## Current Subpages

| Component | File | Status | Notes |
|-----------|------|--------|-------|
| Lists | `lists-style-guide.html` | ✅ Complete | Original template |
| Tables | `tables-style-guide.html` | ✅ Complete | Updated to match |
| Forms | TBD | 🔄 Planned | Form fields, inputs |
| Navigation | TBD | 🔄 Planned | Sidebar, breadcrumbs |
| Document Components | TBD | 🔄 Planned | Notes, signatures |

## Future Enhancements

1. **Active Section Highlighting**: Highlight current section in sidebar as user scrolls
2. **Copy Code Buttons**: Add to all code examples
3. **Search Functionality**: Add search within subpages
4. **Print Styles**: Optimize for printing documentation
5. **Dark Mode Support**: Add theme toggle

---

*Last Updated: January 2025*