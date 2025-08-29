# City of Rivergrove Document Style Guide

## Purpose
This guide ensures consistent formatting across all digitized City of Rivergrove documents (ordinances, resolutions, and interpretations).

## Headers and Titles

### Document Headers
- Main title as H1: `# ORDINANCE NO. XX-YYYY`
- Subtitle/description as H2: `## AN ORDINANCE...`
- Section headers as H3: `### Section 1`
- Subsection headers as H4: `#### Subsection A`

## Signature Blocks

### Standard Format
```markdown
[Signature], Name, Title  
**Date**: {{filled:MM/DD/YY}}  
```

### Important Rules
- Format: `[Signature], Name, Title` (all on one line)
- Names and titles are NOT bolded
- Add double spaces at the end of signature lines for proper Markdown line breaks
- Use `{{filled:}}` for handwritten dates (see [form-fields-syntax.md](form-fields-syntax.md))
- Transcribe dates exactly as written (e.g., "8-12-02" vs "8/12/02")
- Different signers may use different date formats - preserve these differences
- If the date was pre-printed (not handwritten), don't use `{{filled:}}`

## Footnotes

### In Tables
- Use superscript numbers: `$25.00*¹` or `Actual Costs²`
- In markdown tables, escape asterisks: `$25.00\*¹`

### Below Tables (Source Format)
Write footnotes in pure Markdown immediately after the table:

```markdown
| **Column** | **Value** |
|------------|-----------|
| Item       | Cost¹     |

¹ **Brief title.** Full explanation text.
² **Brief title.** Full explanation text.
```

### Automatic Processing
The footnote preprocessor will automatically wrap footnotes during build. It identifies footnotes by:
1. **Location**: Must appear immediately after a table
2. **Format**: Must start with superscript number (¹²³⁴⁵⁶⁷⁸⁹⁰)
3. **Structure**: Must have bold text after the number (indicates it's a footnote, not just a number)

### Safety Features
To avoid false positives:
- Only processes text immediately following tables
- Requires the specific format: `¹ **Bold text.** Additional text`
- Won't accidentally catch dates like `**12th**` or other numbered content
- Groups consecutive footnotes together

### Manual Override
If automatic processing fails, you can manually wrap footnotes:

```markdown
<div class="footnotes">

¹ **Brief title.** Full explanation text.

</div>
```

## Lists

### Numbered Lists
```markdown
1. First item
2. Second item
   - Sub-item with dash
   - Another sub-item
3. Third item
```

### Letter Lists (in legal text)
```markdown
**a.** First item  
**b.** Second item  
**c.** Third item  
```

### Roman Numerals (preserve as written)
```markdown
- (i) First item
- (ii) Second item
- (iii) Third item
```

## Tables

### Basic Format
```markdown
| **Column Header** | **Column Header** |
|-------------------|-------------------|
| Content | Content |
```

### Rules
- Bold column headers
- Use dashes for separator row (minimum 3 per column)
- Align columns with pipes for readability

## Special Formatting

### Handwritten Content
- Bold any content that was clearly filled in by hand: `Adopted on **March 15, 1998**`
- This makes it clear what was pre-printed vs. manually added

### Underlined Text
- Convert underlines to bold since Markdown doesn't support underlines

### Strikethrough Text
- Preserve using `~~text~~` when it appears in legal documents

### Page Breaks
- Generally ignore page breaks and transcribe continuously
- Only note if legally meaningful (e.g., "Continue on next page")

## Cross-References

### To Other Documents
```markdown
[Ordinance NO. 70-2001](../ordinances/2001-Ord-70-2001-WQRA.md)
```

### To Sections Within Same Document
```markdown
See Section III.A above
```

## File Naming

See **[naming-conventions.md](naming-conventions.md)** for complete file naming standards and organization rules.

## General Principles

1. **Preserve Original Content**: Don't fix typos or grammar unless explicitly asked
2. **Maintain Legal Accuracy**: Preserve all legal formatting, dates, and references exactly
3. **Consistency Over Perfection**: Follow these standards even if the original differs
4. **Document Everything**: Include stamps, signatures, dates, handwritten notes

## Updates to This Guide

This is a living document. When encountering new formatting situations:
1. Check existing documents for precedent
2. Choose the clearest, most accessible format
3. Document the decision here
4. Apply consistently going forward

---

*Last Updated: August 2024*