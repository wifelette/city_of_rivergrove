# Navigation Styling Options for mdBook Sidebar

## Option 1: Multi-line with HTML structure
We could use HTML in SUMMARY.md to create structured entries:

```html
- <span class="ord-entry">
    <span class="ord-number">#70-2001</span>
    <span class="ord-title">WQRA</span>
    <span class="ord-year">2001</span>
  </span>
```

Then style with CSS:
```css
.ord-entry {
    display: block;
    line-height: 1.2;
    padding: 0.5em 0;
}
.ord-number {
    font-weight: bold;
    display: block;
}
.ord-title {
    display: block;
    font-size: 0.9em;
}
.ord-year {
    color: #666;
    font-size: 0.8em;
}
```

## Option 2: Inline with visual separation
Keep single line but use visual cues:

```markdown
- **#70** · WQRA <small>(2001)</small>
```

With CSS:
```css
.chapter-item small {
    color: #999;
    font-size: 0.85em;
    font-weight: normal;
}
```

## Option 3: CSS ::before/::after pseudo-elements
Use data attributes and CSS to add the year as a subtle element:

In SUMMARY.md:
```html
- <span data-year="2001">#70 - WQRA</span>
```

CSS:
```css
[data-year]::after {
    content: attr(data-year);
    display: block;
    font-size: 0.75em;
    color: #999;
    margin-top: 2px;
}
```

## Option 4: Two-tier approach with groups
Group by decade or period:

```markdown
## 1990s
- #52-93 Manufactured Homes
- #59-97A Land Development
- #61-98 Land Development
- #62-98 Flood & Land Development

## 2000s
- #68-2000 Metro Compliance
- #69-2000 Title 3 Compliance
- #70-2001 WQRA
- #71-2002 Gates
```

## Option 5: Compact with hover details
Main display is minimal, full info on hover:

```css
.chapter-item {
    position: relative;
}
.chapter-item[title]::after {
    content: attr(title);
    position: absolute;
    left: 100%;
    background: #333;
    color: white;
    padding: 0.25em 0.5em;
    border-radius: 3px;
    white-space: nowrap;
    opacity: 0;
    transition: opacity 0.2s;
}
.chapter-item:hover[title]::after {
    opacity: 1;
}
```

## Recommendation

I suggest **Option 1 (Multi-line with HTML)** or **Option 4 (Groups)** because:
- They work well in narrow sidebars
- Provide clear visual hierarchy
- Keep all information visible but organized
- Are accessible and don't rely on hover states

The multi-line approach would look like:
```
#70-2001
WQRA
2001

#71-2002  
Gates
2002
```

Or with groups:
```
▼ 2000-2010
  #68 Metro Compliance
  #69 Title 3
  #70 WQRA
  #71 Gates
  #72 Penalties
```

Which approach appeals to you?