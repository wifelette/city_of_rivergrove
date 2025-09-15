# Lists Style Guide

## Overview

This comprehensive guide covers all list formatting patterns used in City of Rivergrove documents. Lists are a critical component of legal documents, appearing in ordinances, resolutions, and interpretations with various formatting requirements.

## Key Principles

1. **Consistency**: All list markers should be styled consistently across documents
2. **Blue markers**: All list markers (numbers, letters, roman numerals) display in blue (#0969da)
3. **No bullets**: Parenthetical lists like (a), (b), (c) should never show bullet points
4. **Proper nesting**: Nested lists maintain clear visual hierarchy through indentation

## Standard Ordered Lists

Traditional numbered lists using period notation.

### Markdown Input
```markdown
1. First numbered item
2. Second numbered item
3. Third numbered item with longer text that may wrap to multiple lines
4. Fourth numbered item
```

### Output
- Blue numbered markers (1., 2., 3., etc.)
- Standard indentation
- Automatic numbering

### Common Usage
- Procedural steps
- Sequential requirements
- Numbered sections in ordinances

## Alpha Parenthetical Lists

Lists using lowercase letters in parentheses: (a), (b), (c)

### Markdown Input
```markdown
(a) First alpha item with some text
(b) Second alpha item with more content
(c) Third alpha item with even more text
(d) Fourth alpha item
```

### Output
- Blue (a), (b), (c) markers
- **NO bullet points** (critical requirement)
- Consistent spacing and indentation

### Common Usage
- Definitions sections
- Subsections within numbered items
- Multiple conditions or requirements

## Numeric Parenthetical Lists

Lists using numbers in parentheses: (1), (2), (3)

### Markdown Input
```markdown
(1) First parenthetical numbered item
(2) Second parenthetical numbered item
(3) Third parenthetical numbered item
(4) Fourth parenthetical numbered item
```

### Output
- Blue (1), (2), (3) markers
- **NO bullet points**
- Same styling as alpha lists but with numbers

### Common Usage
- Alternative to standard numbered lists
- Nested requirements under alpha items
- Inline references within paragraphs

## Roman Numeral Lists

Lists using lowercase roman numerals: (i), (ii), (iii)

### Markdown Input
```markdown
(i) First roman numeral item
(ii) Second roman numeral item
(iii) Third roman numeral item
(iv) Fourth roman numeral item
```

### Output
- Blue (i), (ii), (iii) markers
- **NO bullet points**
- Typically used for third-level nesting

### Common Usage
- Third level of nesting
- Sub-subsections
- Detailed breakdowns

## Nested Lists

Lists can be nested to create hierarchical structures. Standard pattern:
1. Top level: Numbers (1., 2., 3.) or letters (a), (b), (c)
2. Second level: Opposite of top level
3. Third level: Roman numerals (i), (ii), (iii)

### Example: Alpha with Nested Numbers

```markdown
(a) Parent alpha item
    1. First nested numbered item
    2. Second nested numbered item
    3. Third nested numbered item
(b) Second parent alpha item
    1. Another nested numbered item
    2. Another nested numbered item
```

### Example: Numbers with Nested Alpha

```markdown
1. Parent numbered item
    (a) First nested alpha item
    (b) Second nested alpha item
    (c) Third nested alpha item
2. Second parent numbered item
    (a) Another nested alpha item
    (b) Another nested alpha item
```

### Complex Nesting

For deeply nested structures (rare but sometimes necessary):

```markdown
(a) Top level alpha item
    (1) Nested parenthetical number
        (i) Double nested roman numeral
        (ii) Another double nested roman
    (2) Second nested parenthetical
(b) Second top level alpha
```

**Note**: Due to markdown limitations, complex nesting may render with visual indentation rather than true nested HTML structures. The processor adds appropriate CSS classes to maintain visual hierarchy.

## Lists in Special Contexts

### Lists in Blockquotes

Common in ordinances when quoting definitions or other documents:

```markdown
> **Section 1. Definitions**
> 
> (a) "Building" means any structure
> (b) "Structure" means anything constructed
> (c) "Use" means the purpose for which land is occupied
```

### Lists in Tables

Lists within table cells maintain their formatting:

```markdown
| Section | Requirements |
|---------|-------------|
| A | (1) First requirement<br>(2) Second requirement<br>(3) Third requirement |
| B | (a) Alpha requirement<br>(b) Beta requirement<br>(c) Gamma requirement |
```

**Note**: Use `<br>` tags to separate list items within table cells.

### Lists in Document Notes

Lists within Document Notes sections maintain consistent formatting:

```markdown
## Document Notes

### Handwritten text {{page:2}}

(a) First note item
(b) Second note item
```

## Mixed Content Lists

Lists can include continuation paragraphs and nested content:

```markdown
(a) First item with a simple sentence.

   This is a continuation paragraph under item (a) with more detailed explanation.

(b) Second item with multiple paragraphs.

   First paragraph under item (b).
   
   Second paragraph under item (b) with more content.

(c) Third item with nested content.
   
   (1) Nested item under (c)
   (2) Another nested item
   (3) Third nested item
```

**Important**: Use 3-space indentation for continuation paragraphs to prevent markdown from converting them to code blocks.

## Special Formatting Patterns

### Bold Terms (Definition Style)

Common in definitions sections:

```markdown
(a) **Term One** - Definition of term one
(b) **Term Two** - Definition of term two
(c) **Term Three** - Definition of term three
```

### Inline List References

When list markers appear within a paragraph, they stay inline but still get blue styling:

```markdown
The requirements are: (1) First requirement, (2) Second requirement, and (3) Third requirement.
```

This pattern is common in legal text where conditions are listed within a sentence.

## Edge Cases and Important Notes

### Lists with Introductory Text

When a paragraph contains both introductory text and list items, the introductory text is preserved as a separate paragraph:

```markdown
The term does not, however, include either:
(1) any project for improvement of a structure
(2) any alteration of a structure listed on the National Register
```

Output:
- The introductory text ("The term does not, however, include either:") remains as a paragraph
- The list items (1) and (2) are converted to a proper list below it
- This preserves important contextual information that qualifies the list

This pattern is common in legal definitions where lists are preceded by qualifying statements like:
- "The following items are included:"
- "This does not include:"
- "Requirements consist of:"
- "The term means:"

### Single Item Lists

Single parenthetical references should NOT be converted to lists:

```markdown
This paragraph contains (1) a single parenthetical number reference.
```

The (1) stays inline as it's likely a reference, not a list.

### When NOT to Convert to Lists

Do not convert to lists when:
- Only one item with parenthetical notation exists
- The notation appears mid-sentence as a reference
- The context clearly indicates it's not a list item

### Long Markers

The system handles extended markers:
- Double letters: (aa), (bb), (cc)
- Long roman numerals: (xvii), (xviii), (xix)

## Technical Implementation

### Processing Order

1. **Preprocessing**: `standardize-list-format.py` normalizes certain patterns
2. **mdBook**: Converts markdown to HTML
3. **Postprocessing**: `unified-list-processor.py` adds classes and styling

### CSS Classes Applied

- `.alpha-list` - For (a), (b), (c) lists
- `.numeric-list` - For (1), (2), (3) lists  
- `.roman-list` - For (i), (ii), (iii) lists
- `.list-marker-alpha` - Span around alpha markers
- `.list-marker-numeric` - Span around numeric markers
- `.list-marker-roman` - Span around roman markers

### Key CSS Properties

```css
/* Hide bullets */
.alpha-list, .numeric-list, .roman-list {
    list-style: none !important;
}

/* Blue markers */
.list-marker-alpha, .list-marker-numeric, .list-marker-roman {
    color: #0969da;
    font-weight: bold;
}
```

## Testing

A comprehensive test document is available at `/src/other/list-test-comprehensive.md` that demonstrates all list patterns and edge cases. This should be reviewed when making any changes to list processing.

## Common Issues and Solutions

### Issue: Bullets showing on parenthetical lists
**Solution**: Ensure CSS includes `list-style: none !important`

### Issue: Lists not converting from (a) notation
**Solution**: Check that items are at start of line with consistent format

### Issue: Nested lists not indenting properly
**Solution**: Use proper markdown indentation (4 spaces or 1 tab)

### Issue: Continuation paragraphs becoming code blocks
**Solution**: Use 3-space indentation instead of 4

## See Also

- [Document Notes Style Guide](./document-notes.md) - For lists within Document Notes
- [Markdown Conventions](../markdown-conventions.md) - General markdown formatting
- [Form Fields](./form-fields.md) - For interactive list elements