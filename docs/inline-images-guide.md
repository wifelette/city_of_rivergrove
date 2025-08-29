# Inline Images Guide

## Overview

The inline image system allows you to embed images (diagrams, maps, charts) directly into legal documents while maintaining clean markdown source files.

## Image Syntax

Use the special `{{image:}}` tag in your markdown files:

```markdown
{{image:filename|alt=alt text|caption=caption text}}
```

### Parameters

- **filename**: Short descriptor for the image (without extension or document prefix)
- **alt**: Alternative text for accessibility
- **caption**: Optional caption to display below the image

### Example

```markdown
{{image:slope-measurement|alt=Slope measurement diagrams|caption=Figure 1: Method for determining vegetated corridors}}
```

## File Organization

### Directory Structure
```
src/
└── images/
    ├── ordinances/
    ├── resolutions/
    └── interpretations/
```

### Naming Convention

Image files should follow this pattern:
`[YYYY]-[Type]-[#Number]-[Topic]-[descriptor].png`

Examples:
- `2001-Ord-70-2001-WQRA-slope-measurement.png`
- `2018-Res-259-Planning-Development-Fees-fee-table.png`

## Adding Images to Documents

### Step 1: Add the Image Tag

Edit the source document (in `Ordinances/`, `Resolutions/`, or `Interpretations/`) and add the image tag where you want the image to appear:

```markdown
## APPENDIX B

**SLOPE MEASUREMENT**

Method One: Calculate slope as rise over run...

{{image:slope-measurement|alt=Slope diagrams|caption=Diagrams showing slope measurement methods}}
```

### Step 2: Save the Image File

1. Save your image as a PNG file
2. Name it following the convention: `[document-name]-[descriptor].png`
3. Place it in the appropriate subdirectory:
   - Ordinances: `src/images/ordinances/`
   - Resolutions: `src/images/resolutions/`
   - Interpretations: `src/images/interpretations/`

### Step 3: Update mdBook

Run the update script to sync and rebuild:

```bash
# For a single file
./scripts/build/update-single.sh Ordinances/2001-Ord-#70-2001-WQRA.md

# For all files
./scripts/build/update-mdbook.sh
```

## How It Works

1. **Markdown Source**: Documents use the `{{image:}}` tag syntax
2. **Sync Processing**: During sync, the tag is converted to HTML `<figure>` elements
3. **HTML Output**: Images are rendered with proper styling and captions
4. **CSS Styling**: Custom styles ensure images look good on screen and in print

## Image Styling

Images automatically receive:
- Centered positioning
- Border and padding
- Responsive sizing (80% width on desktop, 100% on mobile)
- Print-friendly formatting
- Caption styling (italic, smaller text)

## Multiple Images in One Document

You can add multiple images by using different descriptors:

```markdown
{{image:map-overview|alt=Area map|caption=Figure 1: Protected water features}}

...later in document...

{{image:slope-diagram|alt=Slope calculation|caption=Figure 2: Slope measurement method}}
```

Just ensure each image file has the corresponding name:
- `2001-Ord-70-2001-WQRA-map-overview.png`
- `2001-Ord-70-2001-WQRA-slope-diagram.png`

## Best Practices

1. **Image Size**: Keep images under 1MB for fast loading
2. **Format**: Use PNG for diagrams, JPG for photos
3. **Resolution**: 150-300 DPI for good quality without excessive file size
4. **Alt Text**: Always provide descriptive alt text for accessibility
5. **Captions**: Use captions to explain what the image shows

## Troubleshooting

### Image Not Showing

1. Check the image file exists in the correct directory
2. Verify the filename matches the pattern exactly
3. Run the sync script to process the image tag
4. Check browser console for 404 errors

### Image Too Large/Small

The CSS automatically sizes images, but you can adjust by modifying the `.document-figure` styles in `custom-list-processor.py`.

### Processing Errors

If the `{{image:}}` tag isn't converting:
1. Check the syntax is correct
2. Ensure no typos in the tag
3. Run the sync script again
4. Check the processed file in `src/ordinances/` to see if conversion happened