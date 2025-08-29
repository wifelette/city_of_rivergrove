# City of Rivergrove Digital Repository

A searchable, centralized repository of all City of Rivergrove ordinances, resolutions, and interpretations. Converting hard-to-read photocopied versions into accessible markdown documents with full-text search capabilities.

🌐 **Live Site**: [GitHub Pages](https://wifelette.github.io/city_of_rivergrove/)  
📋 **Project Guide**: [digitization-guide.md](digitization-guide.md)

## Quick Start

### Local Development

1. **Start the mdBook server**:
   ```bash
   mdbook serve
   ```

2. **Edit files** in the `source-documents/Ordinances/` directory

3. **Sync changes**:
   ```bash
   ./scripts/build/update-mdbook.sh
   ```

4. **View at**: http://localhost:3000

### File Organization

- **`source-documents/Ordinances/`** - Main directory for editing (with `#` in filenames)
- **`src/ordinances/`** - mdBook source (synced from main directory)
- **`book/`** - Generated static site

## Current Status

### ✅ Completed
- Style E format implemented (#XX - Title (Year))
- List formatting fixes applied to all ordinances
- Manual sync workflow established
- Cross-reference system working
- Full-text search enabled

### ⚠️ Known Issues
- Automated file sync occasionally overrides content (use manual sync)
- File watcher available but not recommended due to stability

### 🔄 In Progress
- Enhanced navigation controls ([Issue #10](https://github.com/wifelette/city_of_rivergrove/issues/10))
- Right panel for document relationships
- Improved sync stability

## Document Standards

All documents follow consistent formatting:

- **Proper markdown lists**: Manual numbering `(1)` converted to `1.`
- **Legal formatting preserved**: Roman numerals `(i)` as `- (i)`
- **Bold nested markers**: Letter lists use `**a.**` for visibility
- **Cross-references**: Automatic linking between related documents

## Scripts

- **`./scripts/build/update-mdbook.sh`** - Safe sync and rebuild (recommended)
- **`./scripts/build/update-single.sh`** - Update single file (faster)
- **`./scripts/preprocessing/sync-ordinances.py`** - Manual sync only
- **`./scripts/utilities/watch-and-sync.py`** - Auto file watcher (use with caution)

For detailed workflow information, see [digitization-guide.md](digitization-guide.md).
