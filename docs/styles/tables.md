# Enhanced Tables Style Guide

## Overview

Tables in the City of Rivergrove documentation serve critical functions for presenting fee schedules, ordinance comparisons, meeting attendance records, and other structured data. This guide covers all table patterns and their proper usage.

## Basic Table Structure

### Standard Table Format

All tables should use bold column headers and proper markdown table syntax:

```markdown
| **Column Header** | **Column Header** |
|-------------------|-------------------|
| Content           | Content           |
```

**Rendered Example:**

| **Column Header** | **Column Header** |
|-------------------|-------------------|
| Content           | Content           |

### Key Requirements

- **Bold headers**: Always use `**Header Text**` in the first row
- **Separator row**: Use at least 3 dashes per column
- **Alignment**: Use pipes `|` to align columns for readability
- **Consistency**: Maintain consistent column widths across rows

## Fee Schedule Tables

Fee schedules are one of the most common table types in City documents. They require special formatting for clarity and legal compliance.

### Basic Fee Schedule

```markdown
| **PERMIT/APPLICATION TYPE** | **FEE** |
|-----------------------------|---------|
| **Building Permit (City Fee)** | $25.00 |
| **Variance/Hardship Relief** | Actual Costs |
| **Type I Review** | Actual Costs |
| **Type II Review** | Actual Costs |
```

**Rendered Example:**

| **PERMIT/APPLICATION TYPE** | **FEE** |
|-----------------------------|---------|
| **Building Permit (City Fee)** | $25.00 |
| **Variance/Hardship Relief** | Actual Costs |
| **Type I Review** | Actual Costs |
| **Type II Review** | Actual Costs |

### Fee Schedule with Footnotes

When fees require explanatory notes, use superscript numbers and footnotes:

```markdown
| **PERMIT/APPLICATION TYPE** | **FEE** |
|-----------------------------|---------|
| **Building Permit (City Fee)** | $25.00\*¹ |
| **Tree Cutting Permit Within WQRA** | $30 per tree + Actual Costs |
| **Appeal of Type II Decision** | Actual Costs² |

¹ **Basic building permit.** Plus the actual cost of hearings officer, notification and specialized services.

² **Based on ORS 227.175 (10) (iii)(b).** Actual costs include City's land use planners, engineers and attorneys.
```

**Important**: Escape asterisks in markdown tables: `$25.00\*¹` not `$25.00*¹`

### Multi-line Cell Content

For complex fee descriptions that span multiple lines:

```markdown
| **PERMIT TYPE** | **FEE** |
|-----------------|---------|
| **Appeal of Type I Decision**{{br}}(FEE TO BE PAID UPON FILING APPEAL) | $250.00 |
| **Appeal of Type II, III, and IV Decisions**{{br}}(DEPOSIT TO BE PAID UPON FILING APPEAL) | Actual Costs |
```

## Deposit Tables

Deposit schedules often appear as secondary tables:

```markdown
### Deposit Amounts:

| **Review Type** | **Deposit Amount** |
|-----------------|-------------------|
| **Type I Review** | $400 |
| **Type II Review** | $500 |
| **Type III Review** | $1,000 |
| **Partition** | $2,000 |
| **Subdivision** | $5,000 |
| **Appeal** | $250 |
```

## Meeting Attendance Tables

For recording attendance at City Council meetings:

```markdown
| **Council Member** | **Present** | **Absent** | **Excused** |
|-------------------|-------------|------------|-------------|
| **Mayor Kibbey** | ✓ | | |
| **Councilor Smith** | | | ✓ |
| **Councilor Johnson** | ✓ | | |
| **Councilor Williams** | | ✓ | |
```

## Tables in Blockquotes

Tables within blockquotes receive special styling for better contrast:

```markdown
> | **Item** | **Status** |
> |----------|------------|
> | Review Application | Complete |
> | Public Hearing | Scheduled |
> | Decision | Pending |
```

### CSS Classes Applied

- `blockquote table`: White background for contrast
- `blockquote table thead`: Gray header background
- `blockquote table tbody tr:nth-child(even)`: Alternating row colors

## Table Footnotes

Footnotes are automatically wrapped during the build process when they follow specific patterns:

### Automatic Processing

The system identifies footnotes by:
1. **Location**: Must appear immediately after a table
2. **Format**: Must start with superscript number (¹²³⁴⁵⁶⁷⁸⁹⁰)
3. **Structure**: Must have bold text after the number

### Manual Override

If automatic processing fails, manually wrap footnotes:

```markdown
<div class="table-footnotes">

¹ **Brief title.** Full explanation text.

² **Another note.** Additional details.

</div>
```

### CSS Classes

- `.table-footnotes`: Container with gray background and left border
- `table + .table-footnotes`: Ensures proper spacing after tables

## Styling and Visual Effects

### Row Hover Effects

Tables automatically receive hover effects for better readability:

```css
/* Applied automatically to all tables */
tbody tr:hover {
    background-color: var(--color-bg-subtle);
}
```

### Alternating Row Colors

Even rows receive subtle background coloring:

```css
/* Applied to even rows */
tbody tr:nth-child(even) {
    background-color: var(--color-bg-subtle);
}
```

### Border Styling

All table cells have consistent borders:
- **Header cells**: Medium bottom border for separation
- **Body cells**: Thin borders on all sides
- **Outer border**: Thin border around entire table

## Complex Table Examples

### Ordinance Comparison Table

```markdown
| **Ordinance** | **Topic** | **Adopted** | **Status** | **Notes** |
|---------------|-----------|-------------|------------|-----------|
| **Ord #52** | Water Quality | 1989-05-08 | Active | Amended 2001 |
| **Ord #70-2001** | WQRA Updates | 2001-11-12 | Active | Supersedes portions of #52 |
| **Ord #54-89C** | Land Development | 1989-12-11 | Repealed | Replaced by #82-2011 |
```

### Budget Summary Table

```markdown
| **Department** | **FY 2023-24** | **FY 2024-25** | **Change** | **% Change** |
|----------------|----------------|----------------|------------|--------------|
| **Administration** | $250,000 | $275,000 | $25,000 | +10.0% |
| **Public Works** | $450,000 | $480,000 | $30,000 | +6.7% |
| **Parks & Recreation** | $125,000 | $130,000 | $5,000 | +4.0% |
| **Total** | **$825,000** | **$885,000** | **$60,000** | **+7.3%** |
```

## Best Practices

### Do's
- ✓ Always bold column headers
- ✓ Use consistent column alignment
- ✓ Escape special characters in markdown tables (`\*`, `\|`)
- ✓ Include units in headers when applicable (e.g., "**Fee (USD)**")
- ✓ Use footnotes for explanatory text
- ✓ Bold totals rows for emphasis

### Don'ts
- ✗ Don't use HTML tables unless absolutely necessary
- ✗ Don't include lengthy explanations in cells (use footnotes)
- ✗ Don't mix alignment styles within a table
- ✗ Don't forget to escape asterisks when using footnote markers

## Accessibility Considerations

- Tables are automatically wrapped with proper ARIA labels
- Header cells use `<th>` elements with proper scope
- Footnotes are linked to their references
- Color contrast meets WCAG AA standards

## Technical Implementation

### CSS Files
- Primary styles: `theme/css/components/tables.css`
- Footnote styles: Included in tables.css
- Blockquote overrides: Included in tables.css

### Postprocessing
- Footnote wrapper: `scripts/postprocessing/wrap-footnotes.py`
- Table enhancement: Applied during mdBook build

### Testing
- Visual tests: `tests/visual/specs/tables.test.js`
- Accessibility tests: Included in build validation

---

*Last Updated: January 2025*