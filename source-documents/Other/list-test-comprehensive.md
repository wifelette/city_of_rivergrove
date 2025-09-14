# Comprehensive List Test Document

This document contains all list variations found in City of Rivergrove documents to test the unified list processing system.

## Standard Ordered Lists

These should display with blue numbers:

1. First numbered item
2. Second numbered item
3. Third numbered item with longer text that may wrap to multiple lines to test spacing
4. Fourth numbered item

## Alpha Parenthetical Lists

These should display with blue (a), (b), (c) markers and NO bullets:

(a) First alpha item with some text
(b) Second alpha item with more content
(c) Third alpha item with even more text that wraps to multiple lines
(d) Fourth alpha item

## Numeric Parenthetical Lists

These should display with blue (1), (2), (3) markers and NO bullets:

(1) First parenthetical numbered item
(2) Second parenthetical numbered item  
(3) Third parenthetical numbered item with longer content
(4) Fourth parenthetical numbered item

## Roman Numeral Lists

These should display with blue (i), (ii), (iii) markers and NO bullets:

(i) First roman numeral item
(ii) Second roman numeral item
(iii) Third roman numeral item with longer text
(iv) Fourth roman numeral item

## Nested Lists

### Alpha with Nested Numbers

(a) Parent alpha item
    1. First nested numbered item
    2. Second nested numbered item
    3. Third nested numbered item
(b) Second parent alpha item
    1. Another nested numbered item
    2. Another nested numbered item
(c) Third parent alpha item

### Numbers with Nested Alpha

1. Parent numbered item
    (a) First nested alpha item
    (b) Second nested alpha item  
    (c) Third nested alpha item
2. Second parent numbered item
    (a) Another nested alpha item
    (b) Another nested alpha item

### Complex Nesting

(a) Top level alpha item
    (1) Nested parenthetical number
        (i) Double nested roman numeral
        (ii) Another double nested roman
    (2) Second nested parenthetical
(b) Second top level alpha
    (1) More nested content
    (2) Even more nested content

## Lists in Blockquotes

As found in some ordinances:

> **Section 1. Definitions**
> 
> (a) "Building" means any structure
> (b) "Structure" means anything constructed
> (c) "Use" means the purpose for which land is occupied

## Mixed Content Lists

Lists with paragraphs and other content:

(a) First item with a simple sentence.

   This is a continuation paragraph under item (a) with more detailed explanation.

(b) Second item with multiple paragraphs.

   First paragraph under item (b).
   
   Second paragraph under item (b) with more content.

(c) Third item with nested content.
   
   (1) Nested item under (c)
   
   (2) Another nested item
   
   (3) Third nested item

## Lists with Special Formatting

### Bold Terms (Definition Style)

(a) **Term One** - Definition of term one
(b) **Term Two** - Definition of term two  
(c) **Term Three** - Definition of term three

### Lists in Tables

| Section | Requirements |
|---------|-------------|
| A | (1) First requirement<br>(2) Second requirement<br>(3) Third requirement |
| B | (a) Alpha requirement<br>(b) Beta requirement<br>(c) Gamma requirement |

## Document Notes

### Stamp {{page:3}}

COPY

### Handwritten text {{page:2}}

Test note content with:
(a) First note item
(b) Second note item

## Edge Cases

### Single Item Lists (Should NOT be converted)

This paragraph contains (1) a single parenthetical number reference that should not become a list.

Similarly, this has (a) single letter reference that stays inline.

### Lists Starting Mid-Paragraph

The requirements are: (1) First requirement, (2) Second requirement, and (3) Third requirement.

### Very Long Markers

(aa) Double letter marker
(bb) Another double letter marker
(xvii) Long roman numeral marker
(xviii) Another long roman numeral

## Validation Checklist

After processing, verify:

- [ ] Standard numbered lists have blue numbers
- [ ] Alpha lists show (a), (b) with NO bullets and blue color
- [ ] Numeric parenthetical lists show (1), (2) with NO bullets and blue color  
- [ ] Roman numeral lists show (i), (ii) with NO bullets and blue color
- [ ] Nested lists maintain proper indentation
- [ ] Lists in blockquotes display correctly
- [ ] Document Notes have proper badges
- [ ] Single parenthetical references stay inline
- [ ] No duplicate processing artifacts
- [ ] All markers are consistently styled