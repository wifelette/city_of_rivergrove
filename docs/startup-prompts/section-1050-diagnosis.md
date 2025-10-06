# Section 1.050 List Fragmentation Diagnosis

## Quick Test Command
Run this to see the current state of Section 1.050:
```bash
python3 -c "
from bs4 import BeautifulSoup
from pathlib import Path

filepath = Path('book/ordinances/1989-Ord-54-89C-Land-Development.html')
with open(filepath, 'r') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

for h in soup.find_all(['h3']):
    if '1.050' in h.get_text():
        print('Section 1.050 structure:')
        current = h
        list_count = 0
        for _ in range(10):
            current = current.find_next_sibling()
            if not current:
                break
            if current.name == 'ul':
                list_count += 1
                items = current.find_all('li', recursive=False)
                print(f'  List {list_count}: {len(items)} items')
                for item in items:
                    marker = item.find('span')
                    if marker and marker.get_text() in ['(v)', '(w)', '(x)', '(y)', '(a)']:
                        print(f'    Contains: {marker.get_text()}')
            elif current.name in ['h2', 'h3', 'hr']:
                print(f'  Next section: {current.get_text()[:30]}...')
                break
"
```

## Expected Result (GOOD)
```
Section 1.050 structure:
  List 1: 25 items
    Contains: (v)
    Contains: (w)
    Contains: (x)
    Contains: (y)
  Next section: ARTICLE 2...
```

## Current Result (BAD)
```
Section 1.050 structure:
  List 1: 39 items  # Too many! Includes Article 2 content
    Contains: (v)
    Contains: (a)  # This is from Article 2!
  List 2: 1 items
    Contains: (w)  # Isolated!
  Next section: ARTICLE 2...
```

## Root Cause Chain
1. **Markdown**: Items (a)-(y) are paragraphs with blank lines between them
2. **mdBook**: Converts these to `<p>` tags, not a list
3. **Processor**: Tries to convert `<p>` tags to list
4. **Problem**: Creates multiple lists instead of one

## The Critical Code Section
File: `scripts/postprocessing/unified-list-processor.py`
Function: `convert_consecutive_paragraph_lists` (line ~403)

The special Section 1.050 handling tries to:
1. Find all definition paragraphs
2. Convert them to a single list
3. BUT: It's missing (w) and (y), and including Article 2 content

## Why (w) Is Special
- Has 4 indented sub-items in the markdown
- mdBook might handle it differently
- Gets isolated into its own list

## Solution Approaches to Try

### Approach 1: Fix the Special Handler
```python
# In convert_consecutive_paragraph_lists
# Need to ensure ALL definitions (a-y) are collected
# Stop BEFORE Article 2 content
```

### Approach 2: Merge Lists After Creation
```python
# After converting paragraphs to lists
# Find all consecutive alpha-lists in Section 1.050
# Merge them into one
```

### Approach 3: Preprocess the Markdown
```markdown
# Convert the source from:
(a) Definition...

(b) Definition...

# To:
(a) Definition...
(b) Definition...
```

## Files to Check
1. `/Users/leahsilber/Github/city_of_rivergrove/scripts/postprocessing/unified-list-processor.py` - The processor
2. `/Users/leahsilber/Github/city_of_rivergrove/src/ordinances/1989-Ord-54-89C-Land-Development.md` - The source
3. `/Users/leahsilber/Github/city_of_rivergrove/book/ordinances/1989-Ord-54-89C-Land-Development.html` - The output