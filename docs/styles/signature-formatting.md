# Signature Formatting Guide

## Overview

This guide defines the standard format for signature blocks in all City of Rivergrove documents (ordinances, resolutions, and interpretations).

## Standard Format

```markdown
[Signature], Name, Title  
**Date**: {{filled:8-12-02}}  

[Signature], Name, Title  
**Date**: {{filled:8/12/02}}  
```

## Formatting Rules

### Basic Structure
- **Format**: `[Signature], Name, Title` (all on one line)
- **Line breaks**: Add double spaces at the end of signature lines for proper Markdown line breaks
- **Placeholder**: Use `[Signature]` for actual signatures

### Names and Titles
- Names and titles are **NOT** bolded
- Keep exact capitalization from source document
- Include full titles as written (e.g., "City Recorder", "Mayor")

### Dates
- **Handwritten dates**: Use `{{filled:}}` syntax (see [form-fields-syntax.md](form-fields-syntax.md))
  - Example: `**Date**: {{filled:8-12-02}}`
- **Pre-printed dates**: Don't use `{{filled:}}`, just transcribe as regular text
  - Example: `**Date**: January 1, 2024`
- **Format preservation**: Transcribe dates exactly as written
  - Different signers may use different formats (8-12-02 vs 8/12/02)
  - Preserve these differences

## Common Patterns

### Mayor and City Recorder
```markdown
[Signature], John Smith, Mayor  
**Date**: {{filled:10-12-98}}  

[Signature], Jane Doe, City Recorder  
**Date**: {{filled:10/12/98}}  
```

### Multiple Signatures (Same Date)
```markdown
[Signature], John Smith, Mayor  
[Signature], Jane Doe, City Recorder  
**Date**: {{filled:March 15, 2024}}  
```

### ATTEST Section
```markdown
[Signature]
John Nelson, Mayor

**ATTEST:**

[Signature]
Rosalie Morrison, City Recorder
```

## Special Cases

### Adoption Statements
For ordinances with adoption dates in the text:
```markdown
**ADOPTED** by the Rivergrove City Council this {{filled:12}} day of {{filled:June, 1978}}
```

### Reading Dates
```markdown
**FIRST READING** {{filled:May 5, 1978}}
**SECOND READING** {{filled:June 12, 1978}}
```

## Automation

Run `scripts/preprocessing/fix-signatures.py` to standardize formatting automatically. This script:
- Fixes line break formatting
- Ensures consistent Date: prefix formatting
- Preserves original date content

## Visual Result

After processing:
- Handwritten dates appear with blue highlighting
- Signature placeholders remain as plain text
- Proper spacing and line breaks are maintained