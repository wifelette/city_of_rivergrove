# Markdown Conventions for City of Rivergrove Documents

This document outlines special markdown patterns and conventions used in the digitization of City of Rivergrove ordinances, resolutions, and interpretations.

## Table Footnotes

### When to Use

- For footnotes that appear directly below tables (e.g., numbered superscript references¹²³)
- For general notes about table contents (e.g., "Note: The middle column...")

### Markdown Pattern

```html
<div class="table-footnotes">
  ¹ **Primary Protected Water Features.** See definition... ² **Secondary
  Protected Water Features.** See definition...
</div>
```

Or for general notes:

```html
<div class="table-footnotes">
  **Note:** The middle column, being italicized...
</div>
```

### Styling Applied

- Light gray background (#f8f9fa)
- Left border (3px solid #dee2e6)
- Smaller font size (90%)
- Added padding for readability

## Lists Within Blockquotes

### When to Use

- For lettered or numbered lists that appear within quoted sections (amendments)

### Markdown Pattern

```markdown
> **Section Title**
>
> 1. First numbered item
> 2. Second numbered item
>    - a. Sub-item with bullet marker
>    - b. Another sub-item
>      1. Further nested item
>      2. Another nested item
```

### Key Points

- Always use bullet markers (`-`) before lettered items within blockquotes
- Use proper indentation (3 spaces per level)
- Numbered items at deeper levels need 5 spaces for proper nesting

## Cross-References

### Automatic Linking

The `add-cross-references.py` script automatically converts references to other documents into clickable links during the build process.

**Important:** Never add manual markdown links in source documents. Keep references as plain text and let the build process handle linking.

### Patterns Detected (case-insensitive)

#### Ordinances

- "Ordinance #52"
- "Ordinance 52"
- "Ord. #52"
- "Ord #52"
- "Ord. 52"
- "Ordinance No. 52"
- Year-suffixed patterns: "Ordinance #54-89", "Ordinance 70-2001"
- Letter-suffixed patterns: "Ordinance #54-89C"

#### Resolutions

- "Resolution #22"
- "Resolution 22"
- "Res. #22"
- "Res #22"

### Generated Link Format

Links automatically point to the correct file in the appropriate subdirectory:

- Ordinances: `../ordinances/YYYY-Ord-XX-Topic.md`
- Resolutions: `../resolutions/YYYY-Res-XX-Topic.md`

Note: The `#` character is removed from filenames in the /src directory for URL compatibility.

## Document Naming

See **[naming-conventions.md](naming-conventions.md)** for complete file naming standards and organization rules.

## Signature Blocks

### Pattern

```markdown
[Signature], Name, Title  
**Date:** MM-DD-YY
```

### Notes

- Two spaces at end of first line for proper line break
- Date on separate line with bold "Date:" prefix
- For handwritten dates, use `{{filled:}}` syntax (see [form-fields-syntax.md](form-fields-syntax.md))

## Tables

### Complex Tables

For tables with merged cells or complex formatting:

- Preserve as much structure as possible in markdown
- Use `<br>` tags for line breaks within cells
- Consider breaking very wide tables into multiple sections if needed
