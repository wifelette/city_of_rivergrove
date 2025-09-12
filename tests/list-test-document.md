# List Styling Test Document

This document contains all variations of lists found in the City of Rivergrove documents to test styling consistency.

## Standard Ordered Lists

### Simple Numbered List
1. First item
2. Second item
3. Third item

### Nested Numbered List
1. First parent item
   1. First nested item
   2. Second nested item
2. Second parent item
   1. Another nested item
   2. Yet another nested item

## Unordered Lists with Alpha Notation

### Simple Alpha List (Lowercase)
- (a) First alpha item
- (b) Second alpha item
- (c) Third alpha item

### Nested Alpha List
- (a) First parent alpha
  - (1) First nested numeric
  - (2) Second nested numeric
- (b) Second parent alpha
  - (1) Another nested numeric
  - (2) Yet another nested numeric

### Alpha List with Paragraphs
- (a) This is the first item with multiple paragraphs.

  This is a second paragraph in the same list item.

- (b) This is the second item.

  It also has multiple paragraphs.

## Unordered Lists with Numeric Notation

### Simple Numeric List in Parentheses
- (1) First numeric item
- (2) Second numeric item
- (3) Third numeric item

### Nested Numeric List
- (1) First parent numeric
  - (a) First nested alpha
  - (b) Second nested alpha
- (2) Second parent numeric
  - (a) Another nested alpha
  - (b) Yet another nested alpha

## Roman Numeral Lists

### Lowercase Roman
- (i) First roman item
- (ii) Second roman item
- (iii) Third roman item

### Uppercase Roman
- (I) First roman item
- (II) Second roman item
- (III) Third roman item

## Mixed Notation Lists

### Complex Nested Structure (Like Ord 52)
- (a) Parent level alpha item
  - (1) First numeric sub-item
    - (i) First roman sub-sub-item
    - (ii) Second roman sub-sub-item
  - (2) Second numeric sub-item
- (b) Second parent alpha item
  - (1) Another numeric sub-item

## Lists Inside Block Quotes

> ### Quoted List Section
> 
> - (a) First quoted item
> - (b) Second quoted item
> - (c) Third quoted item

## Lists with Complex Content

### List with Code Blocks
- (a) Item with code:
  ```
  Example code block
  ```
- (b) Item with inline `code`

### List with Links and Emphasis
- (a) Item with **bold text**
- (b) Item with *italic text*
- (c) Item with [link text](http://example.com)

## Edge Cases

### List Starting with Different Markers
- (d) Starting at d instead of a
- (e) Next item
- (f) Third item

### List with Gaps
- (1) First item
- (3) Third item (skipping 2)
- (5) Fifth item (skipping 4)

## Document Notes Section Test

## Document Notes

### Stamp {{page:1}}
RECORDED

### Handwritten text {{page:2}}
This is handwritten text that should be styled appropriately.

### Footnotes {{page:3}}
- (a) First footnote item
- (b) Second footnote item

---

## Expected Behavior

All numbered lists (1., 2., 3.) should have:
- Blue markers
- Proper indentation
- No bullets

All manual notation lists ((a), (1), (i)) should have:
- No bullets (hidden via CSS)
- Blue notation text
- Proper indentation

Document Notes should have:
- Badge-style headers
- Proper formatting for different note types
- Consistent styling across all documents