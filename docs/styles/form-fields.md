# Form Fields Syntax Guide

## Overview

The form fields system automatically styles blank fields and filled-in fields in legal documents to match the original source documents.

## Unified Syntax

Use the same syntax for both blank and filled fields:

### Blank Fields (Unfilled)
```markdown
{{filled:}}
```
These appear as empty underlined spaces with a tooltip "Blank in source document" on hover.

### Filled Fields (Hand-written)
```markdown
{{filled:text here}}
```
These appear with blue highlighting and an underline to indicate they were hand-filled in the source document.

## Examples

```markdown
# Blank fields
This Agreement is entered into by the City and {{filled:}} (Applicant).
Date: {{filled:}}
Planning File No.: {{filled:}}

# Filled fields  
This ordinance was adopted on {{filled:March 15, 2024}} by the council.
The fee shall be {{filled:$250.00}} for residential applications.
Signed by {{filled:John Smith}}, Mayor.
```

## Legacy Support

The system still recognizes underscore patterns (`___`) from existing documents, but new documents should use the `{{filled:}}` syntax for consistency.

## Processing Workflow

1. When digitizing a document, preserve blank fields as underscores (`___`)
2. Mark hand-filled content with `{{filled:content}}` syntax
3. Run the form fields processor (automatically included in build)
4. The enhanced processor converts these to styled HTML during build

## Visual Result

- **Blank fields**: Empty underlined space with hover tooltip
- **Filled fields**: Blue background (#e3f2fd) with blue underline (#1976d2)

Both styles include hover effects and are print-friendly.

## Validation

Form field syntax is automatically validated at three levels:

### 1. VSCode (Real-time)
- Custom markdownlint rule detects errors as you type
- Shows red squiggles for unclosed `{{filled:` tags
- Warns about malformed tags and orphaned brackets

### 2. Build Scripts (Build-time)
- `scripts/validation/validate-form-fields.py` runs automatically
- Prevents broken tags from reaching production
- Shows clear error messages with line numbers

### 3. Dev Server (Save-time)
- Validates on every file save
- Blocks processing if errors are found
- Displays errors immediately for quick fixes

### Common Errors Caught
- Unclosed tags: `{{filled:text` (missing `}}`)
- Malformed tags: `{{filledtext}}` (missing `:`)
- Orphaned brackets: Random `}}` without opening
- Nested tags: `{{filled:{{filled:text}}}}` (not supported)

### Manual Validation
Run validation manually on any file or directory:
```bash
# Check a single file
python3 scripts/validation/validate-form-fields.py source-documents/Ordinances/example.md

# Check all documents
python3 scripts/validation/validate-form-fields.py

# Auto-fix simple issues (adds closing brackets)
python3 scripts/validation/validate-form-fields.py --fix
```