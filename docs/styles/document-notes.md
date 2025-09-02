# Document Notes Style Guide

## Overview

Document notes provide a standardized way to add supplementary information about digitization, source documents, or historical context. These notes appear with special styling to distinguish them from the main document content.

## When to Use Document Notes

Use document notes for:

- **Digitization notes**: Explaining changes made during digitization (e.g., ALL CAPS conversion)
- **Source document notes**: Describing artifacts, missing pages, or peculiarities in the original
- **Historical notes**: Providing context about document versions or amendments
- **Handwritten notations**: Documenting stamps, handwritten notes, or other markings

## Markdown Syntax

Simply create a section with one of these headers:

```markdown
## Document Notes

Content about the document...

## Digitization Notes

Content about digitization process...

## Source Document Notes

Content about the source document...

## Handwritten notations

Content about handwritten elements...
```

The processor will automatically:

- Detect these section headers (case-insensitive, partial matches work)
- Wrap the section in special styling
- Standardize the header to "Document Notes"
- Apply the visual treatment

## Formatting Notes with Labels and Page References

For notes about specific elements in the source document, use this format:

```markdown
## Document Notes

### Handwritten text {{page:1}}

I certify this to be a true copy. Rosalie Morrison, City Recorder, March 9, 1976

### Stamp {{page:1}}

City of Rivergrove, P.O. Box 110, Lake Oswego 97034

### Stamp {{page:2}}

Department of Land Conservation and Development (LCDC), Received: MAR 11 1976, SALEM
```

The `{{page:X}}` notation goes directly in the H3 header and will be displayed as part of the label.

### Common Label Types

- **Handwritten text:** For handwritten additions or annotations
- **Stamp:** For official stamps or seals
- **Editor's note:** For editorial clarifications
- **Digitization note:** For notes about the digitization process
- **Historical note:** For historical context
- **Missing content:** For pages or sections that are missing

### Page References

To indicate what page in the source document contains the noted item:

1. **In source documents**, use the notation: `{{page:X}}`

   - Example: `{{page:1}}` for page 1
   - Example: `{{page:2}}` for page 2

2. **During processing**, this automatically converts to: `[page X]`

   - The sync scripts convert `{{page:1}}` → `[page 1]`
   - The HTML processor styles these in lighter gray

3. **Final appearance**: Page references appear subtle and professional
   - Styled in gray (#6c757d) at 0.9em size
   - Always placed at the end of the note item

## Examples

### Example 1: ALL CAPS Conversion

```markdown
## Document Notes

The source document for this Ordinance is in ALL CAPITAL LETTERS as was sometimes the way it was done years ago. It has been converted to standard titlecase for readability, though the ALL CAPS format remains retained in the source PDF.
```

### Example 2: Multiple Note Types with Page References

```markdown
## Document Notes

### Handwritten text {{page:1}}

Approved by unanimous vote

### Stamp {{page:1}}

City of Rivergrove Official Seal

### Digitization note

Pages 3-5 of the original document were illegible due to water damage and have been reconstructed from backup copies.

### Editor's note

This ordinance was later amended by Ordinance #75 in 1995.
```

### Example 3: Simple Historical Note

```markdown
## Document Notes

A version of this Ordinance, stipulating 7 members of the council, was reviewed (first reading) on April 10, 1978, and then the version above replaced it and was executed.
```

## Visual Styling

Document notes appear with:

- White card background with subtle shadow
- Gray top accent bar for visual separation
- 📝 Note icon
- Standardized "DOCUMENT NOTES" header
- Professional, non-alarming appearance

The top accent bar eliminates the need for `---` separators before note sections.

## Technical Implementation

- **CSS**: Styles defined in `custom.css` (`.document-note` class)
- **Processing**: Handled by `enhanced-custom-processor.py`
- **Automatic**: Applied during the build process, no manual HTML needed

## Best Practices

1. **Be concise**: Keep notes brief and factual
2. **Be consistent**: Use similar language across documents
3. **Focus on clarity**: Explain what readers need to know about the source
4. **Avoid redundancy**: Don't repeat information already in the document
5. **Use labels**: Clearly identify the type of note (handwritten, stamp, etc.)
6. **Include page references**: Help readers locate content in the source document

## Related Documentation

- [Form Fields Guide](form-fields.md) - For blank and filled form fields
- [Signature Formatting](signature-formatting.md) - For signature blocks
- [Naming Conventions](naming-conventions.md) - For file naming standards
