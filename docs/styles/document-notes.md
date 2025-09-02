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

## Documents That May Need Notes

Based on repository analysis, these documents may benefit from Document Notes sections:

### Currently Have Notes (4 documents)
- **Resolutions:** #22 (handwritten notes, stamps), #72 (handwritten notations)
- **Ordinances:** #28 (document footer artifacts), #57-93 (ALL CAPS conversion)

### Potential Candidates - High Priority

These documents contain keywords suggesting they need Document Notes:

#### Resolutions with potential notes:
- **2018-Res-#256-Planning-Development-Fees** - May have stamps/certifications
- **2018-Res-#259-Planning-Development-Fees** - Similar to #256
- **2019-Res-#41425-Public-Records** - May have official stamps
- **2024-Res-#300-Fee-Schedule-Modification** - Recent document, check for stamps

#### Ordinances with potential notes:
- **1987-Ord-#52-Flood** - Multiple references to "certification" (technical term, not document note)
- **1989-Ord-#54-89C-Land-Development** - Check for stamps or handwritten notes
- **1999-Ord-#65-99-Sewer-Services** - May have certifications
- **2000-Ord-#68-2000-Metro-Compliance** - Has inline **Note:** sections that could be moved
- **2001-Ord-#70-2001-WQRA** - Has inline notes about missing sections
- **2002-Ord-#72-2002-Penalties-and-Abatement-Amendment** - Check for amendments notes
- **2003-Ord-#73-2003A-Conditional-Use-Provisions** - Check for handwritten notes
- **2011-Ord-#81-2011-Sign** - May have stamps or certifications
- **2018-Ord-#89-2018-Tree-Cutting-Amendment** - Has note about capitalized definitions

#### Interpretations with potential notes:
- **2004-10-11-RE-5.080-setbacks** - Check for stamps or notes
- **2008-02-04-RE-multi-family** - May already have notes section

### Search Strategy for Finding More

To find additional documents needing notes, search for:
1. `[Illegible]` in signature blocks
2. `**Note:**` or inline notes that should be moved
3. References to "ALL CAPS" or "ALL CAPITAL LETTERS"
4. "Missing page", "torn", "water damage", "faded"
5. "Stamp:", "Handwritten:", "Editor's note:"
6. Amendment or version history references

### Converting Inline Notes

If you find inline notes like `**Note:** text here` in documents, consider:
1. Moving them to a Document Notes section at the end for consistency
2. Keeping them inline only if integral to understanding immediate context
3. Using the appropriate label type when moving to Document Notes

## Related Documentation

- [Form Fields Guide](form-fields.md) - For blank and filled form fields
- [Signature Formatting](signature-formatting.md) - For signature blocks
- [Naming Conventions](naming-conventions.md) - For file naming standards