# mdBook Documentation Site

## Overview

The repository includes an mdBook static site generator that creates a searchable, browsable website from all digitized documents. The site includes enhanced navigation with list formatting fixes and improved document display.

- **Live Site**: https://wifelette.github.io/city_of_rivergrove/
- **Related Guides**:
  - [Build Architecture](build-architecture.md) - Complete build system documentation
  - [Scripts Guide](../scripts/SCRIPTS-GUIDE.md) - All script documentation
  - [Markdown Conventions](markdown-conventions.md) - Document formatting standards

## File Structure & Sync Workflow

**IMPORTANT**: There are two separate directories for ordinances:

- **`source-documents/Ordinances/`** (capital O) - Main directory for editing files (includes `#` in filenames)
- **`src/ordinances/`** (lowercase o) - mdBook source directory (filenames without `#`)

**⚠️ NEVER EDIT FILES IN `/src` DIRECTLY!** The `/src` directory is automatically generated from source documents. Any direct edits to `/src` will be lost when sync scripts run. Always edit files in `source-documents/` or the main folders (`Ordinances/`, `Resolutions/`, etc.)

### Current Workflow

1. **Edit files** in the main `source-documents/` directories
2. **For development**: Run `./dev-server.sh` for hot-reload from source edits
3. **For single file**: Run `./build-one.sh [file]` to update one document
4. **For full rebuild**: Run `./build-all.sh` to rebuild everything
5. **View changes** at `http://localhost:3000`

### Automated Sync (Not Recommended)

**Automated sync** is available but currently **not recommended** due to content override issues:

- `./scripts/utilities/watch-and-sync.py` - File watcher for auto-sync (use with caution)
- Issue: Unknown process sometimes generates auto-headers that override file content
- **Symptom**: File content temporarily disappears and gets replaced with auto-generated headers
- **Workaround**: Use manual sync with `./build-all.sh` and restore content if needed

## Directory Structure

```text
city_of_rivergrove/
├── source-documents/           # Main editing directory (with # in filenames)
├── src/                  # Source content for mdBook
│   ├── SUMMARY.md       # Table of contents
│   ├── introduction.md  # Welcome page
│   ├── ordinances/      # Synced ordinance files (no # in filenames)
│   ├── resolutions/     # Resolution markdown files
│   ├── interpretations/ # Interpretation markdown files
│   └── transcripts/     # Transcript markdown files
├── book/                # Built static website (generated)
├── scripts/
│   ├── build/
│   │   └── (deprecated)  # Old scripts moved to deprecated/
│   ├── preprocessing/
│   │   └── sync-ordinances.py  # Manual sync script
│   └── utilities/
│       └── watch-and-sync.py   # Auto file watcher (use with caution)
├── book.toml           # mdBook configuration
├── custom.css          # Custom styling (must be at root for mdBook)
└── navigation-standalone.js  # Navigation enhancements (must be at root for mdBook)
```

### Critical File Locations

**IMPORTANT**: mdBook requires certain files at specific locations:

- Files referenced in `book.toml` as `additional-css` or `additional-js` MUST be at the **root level**, not in `src/`
- During build, these root files are copied to both `src/` and `book/`
- The actual source of truth for `custom.css` is the root-level file
- If mdBook fails with "No such file or directory", check that required files exist at root

## Local Development

1. **Start mdBook server**:
   ```bash
   mdbook serve
   ```

2. **Edit files** in `source-documents/` directories (Ordinances/, Resolutions/, etc.)

3. **Sync changes**:
   - **For single file**: `./build-one.sh [path/to/file.md]`
   - **For all files**: `./build-all.sh`

4. **View at** `http://localhost:3000`

## List Formatting Standards

Legal documents require exact preservation of enumeration styles for reference integrity. Our system uses post-processing to handle special list formats while keeping source markdown pure.

### Source Format Preservation

- Keep original legal formatting in source files: `(1)`, `(a)`, `(i)`
- Do NOT convert to standard markdown lists in source files
- The custom-list-processor.py handles conversion during build

### Supported List Formats

- **Numbered lists**: `(1)`, `(2)`, `(3)` → Rendered with preserved markers
- **Letter lists**: `(a)`, `(b)`, `(c)` → Rendered with preserved markers
- **Roman numerals**: `(i)`, `(ii)`, `(iii)` → Rendered with preserved markers
- **Standard markdown**: `1.`, `2.`, `3.` → Standard rendering

### Processing Workflow

1. Source files maintain exact legal formatting
2. mdBook builds HTML from markdown
3. `custom-list-processor.py` post-processes HTML to create proper lists
4. CSS styling preserves original markers while improving visual structure

### Example Source Markdown

```markdown
(1) First numbered item with legal formatting
(2) Second numbered item
    (a) Letter subitem preserved exactly
    (b) Another letter subitem
        (i) Roman numeral nested item
        (ii) Another roman numeral
(3) Third numbered item
```

### Common Issues Resolved

- Lists not rendering as lists (appearing as paragraphs)
- Wrong enumeration conversion (letters to numbers, etc.)
- Sync scripts overwriting manual fixes
- Need to preserve exact legal enumeration for reference

## Navigation System

**Implementation Complete**: [GitHub Issue #10](https://github.com/wifelette/city_of_rivergrove/issues/10) (Closed)

The enhanced navigation system is fully operational with:

- ✅ Style E format (#XX - Title (Year))
- ✅ List formatting fixes for all documents
- ✅ Enhanced navigation controls with dropdown context switcher
- ✅ Other Documents section (City Charter, etc.)
- ✅ Clean home page with hidden sidebars
- ✅ Minimum threshold grouping (10+ documents)
- ✅ Document selection states and active indicators
- ✅ mdBook UI elements properly hidden

### Known Limitations

- File sync workflow needs stability improvements (use manual sync)
- Right panel for document relationships not yet implemented

## Features

- **Full-text search**: All documents searchable
- **Cross-references**: Automatic linking between documents
- **Proper list rendering**: All nested lists display correctly
- **Responsive design**: Works on desktop and mobile
- **GitHub integration**: Direct links to source files

## Maintenance

- Edit in `source-documents/Ordinances/` directory (main source of truth)
- Use `./build-all.sh` for safe syncing
- The `book/` directory is generated and can be safely regenerated
- Monitor [Issue #10](https://github.com/wifelette/city_of_rivergrove/issues/10) for navigation updates

## mdBook Serve Limitations

**IMPORTANT**: If `mdbook serve` is running, it auto-rebuilds when files change BUT does NOT run our postprocessors.

This means form fields (blue filled fields, blank underlines) and other custom formatting will disappear.

**To see the REAL appearance with all formatting:**
1. After any changes while `mdbook serve` is running
2. Manually run: `python3 scripts/postprocessing/custom-list-processor.py`
3. This restores form field styling and other custom formatting

Alternatively, use the build scripts which include postprocessing.