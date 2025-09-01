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

## Examples

### Example 1: ALL CAPS Conversion

```markdown
## Document Notes

The source document for this Ordinance is in ALL CAPITAL LETTERS as was sometimes the way it was done years ago. It has been converted to standard titlecase for readability, though the ALL CAPS format remains retained in the source PDF.
```

### Example 2: Missing Pages

```markdown
## Source Document Notes

Pages 3-5 of the original document contained unrelated material from a different ordinance and were not included in this digitization.
```

### Example 3: Handwritten Elements

```markdown
## Handwritten notations, floating form fields, document footer artifacts and stamps

**Return to:** Executive Department  
Intergovernmental Relations Division  
ATTN: Dolores Streeter  
155 Cottage St. NE  
Salem, OR 97310
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

## Related Documentation

- [Form Fields Guide](form-fields.md) - For blank and filled form fields
- [Signature Formatting](signature-formatting.md) - For signature blocks
- [Naming Conventions](naming-conventions.md) - For file naming standards