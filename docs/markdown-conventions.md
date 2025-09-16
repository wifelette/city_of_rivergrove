# Markdown Conventions for City of Rivergrove Documents

This document outlines special markdown patterns and conventions used in the digitization of City of Rivergrove ordinances, resolutions, and interpretations.

## Table Footnotes

### When to Use

- For footnotes that appear directly below tables (e.g., numbered superscript references¹²³)
- For general notes about table contents (e.g., "Note: The middle column...")

### Markdown Pattern

```markdown
{{table-footnote: ¹ **Primary Protected Water Features.** See definition... ² **Secondary Protected Water Features.** See definition...}}
```

Or for general notes:

```markdown
{{table-footnote: **Note:** The middle column, being italicized...}}
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

The `add-cross-references.py` script automatically converts references to other documents into clickable links during the build process, so there's nothing needed for that when Claude Desktop is digitizing.

**Important:** Never add manual markdown links (or any other HTML) in our new .md source files. Keep references as plain text and let the build process handle linking.

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

See **[styles/naming-conventions.md](styles/naming-conventions.md)** for complete file naming standards and organization rules.

## Signature Blocks

See **[styles/signature-formatting.md](styles/signature-formatting.md)** for complete signature block formatting standards.

## Document Notes

### When to Use

Document notes provide supplementary information about digitization, source documents, or historical context:

- **Digitization notes**: Explaining changes made during digitization (e.g., ALL CAPS conversion)
- **Source document notes**: Describing artifacts, missing pages, or peculiarities in the original
- **Historical notes**: Providing context about document versions or amendments
- **Handwritten notations**: Documenting stamps, handwritten notes, or other markings

### Markdown Pattern

Simply create a section with the header `## Document Notes`:

```markdown
## Document Notes

### Handwritten text {{page:1}}

I certify this to be a true copy. Rosalie Morrison, City Recorder

### Stamp {{page:3}}

COPY

### Digitization note

The source document for this Ordinance is in ALL CAPITAL LETTERS...
```

Use H3 headers for different note types, with optional `{{page:X}}` notation for page references.

### Styling Applied

- White card background with subtle shadow
- Gray top accent bar (eliminates need for `---` separator)
- 📝 Note icon
- Header automatically standardized to "DOCUMENT NOTES"
- Professional, non-alarming appearance

See **[styles/document-notes.md](styles/document-notes.md)** for complete documentation.

## Tables

### Complex Tables

For tables with merged cells or complex formatting:

- Preserve as much structure as possible in markdown
- Use `{{br}}` for line breaks within cells (processed during build)
- Consider breaking very wide tables into multiple sections if needed
