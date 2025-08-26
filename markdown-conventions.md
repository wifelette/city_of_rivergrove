# Markdown Conventions for City of Rivergrove Documents

This document outlines special markdown patterns and conventions used in the digitization of City of Rivergrove ordinances, resolutions, and interpretations.

## Table Footnotes

### When to Use
- For footnotes that appear directly below tables (e.g., numbered superscript references¹²³)
- For general notes about table contents (e.g., "Note: The middle column...")

### Markdown Pattern
```html
<div class="table-footnotes">

¹ **Primary Protected Water Features.** See definition...
² **Secondary Protected Water Features.** See definition...

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
The `add-cross-references.py` script automatically converts references to other ordinances into links.

### Pattern Detected
- "Ordinance #XX-XXXX"
- "Ordinance No. XX-XXXX"
- "Resolution #XX"

### Link Format
Links point to the markdown file in the appropriate subdirectory:
- Ordinances: `../ordinances/YYYY-Ord-#XX-YYYY-Description.md`
- Resolutions: `../resolutions/YYYY-Res-#XX-Description.md`

## Document Naming Conventions

### File Names
- Ordinances: `YYYY-Ord-#XX-YYYY-Description.md`
- Resolutions: `YYYY-Res-#XX-Description.md`
- Interpretations: `YYYY-MM-DD-RE-topic.md`

### In mdBook (src directory)
File names have `#` removed and spaces replaced with hyphens for URL compatibility.

## Signature Blocks

### Pattern
```markdown
[Signature], Name, Title  
**Date:** MM-DD-YY
```

### Notes
- Two spaces at end of first line for proper line break
- Date on separate line with bold "Date:" prefix

## Tables

### Complex Tables
For tables with merged cells or complex formatting:
- Preserve as much structure as possible in markdown
- Use `<br>` tags for line breaks within cells
- Consider breaking very wide tables into multiple sections if needed

## Future Conventions
This document will be updated as new patterns and conventions are established during the digitization process.