# 🚀 Build System Quick Start

> **⚠️ CRITICAL WARNINGS - READ FIRST!**
> 
> 1. **NEVER edit files in `/src` directly** - they are auto-generated and changes will be LOST
> 2. **NEVER use `mdbook serve`** - it breaks our custom formatting. Use `./dev-server.sh` instead
> 3. **ALWAYS edit files in `source-documents/`** directories

## The Only 3 Commands You Need

### 1. 🔨 Full Rebuild
```bash
./build-all.sh
```
Rebuilds everything from source. Use when:
- First time setup
- Multiple files changed
- Something seems broken

### 2. 📝 Single File Update
```bash
./build-one.sh source-documents/Ordinances/1974-Ord-#16-Parks.md
```
Quick update for one file. Use when:
- You just edited one document
- Testing changes to a specific file

### 3. 👀 Development Server
```bash
./dev-server.sh
```
Starts local server with auto-reload. Use when:
- Viewing the site locally
- Making multiple edits
- Testing navigation/formatting

**That's it!** These three scripts handle everything.

---

## If Something Goes Wrong

### Form fields disappeared / Blue boxes missing
Run: `./build-all.sh`

### Cross-references not linking
Run: `./build-all.sh`

### Changes disappeared / File reverted
You probably edited in `/src` instead of `source-documents/`. Edit the source file and run `./build-all.sh`

### "mdbook serve" is running
Kill it with Ctrl+C and use `./dev-server.sh` instead

---

## Complete Processing Workflow

When processing a new document:

1. **Find document** in metadata (MCP tool)
2. **Standardize** the file:
   ```bash
   python3 scripts/preprocessing/standardize-single.py source-documents/[type]/[file].md
   ```
3. **Check naming** follows conventions (both .md and .pdf)
4. **Copy PDF** to same folder as .md
5. **Commit and push** both files
6. **Update mdBook**:
   ```bash
   ./build-one.sh source-documents/[type]/[file].md
   ```
7. **Provide URLs** for Airtable
8. **Update Issue #3** checklist

---

## What Each Script Does

- **`build-all.sh`**: Complete rebuild with all processing steps in correct order
- **`build-one.sh`**: Smart single-file update (figures out document type automatically)
- **`dev-server.sh`**: Development server that applies custom formatting automatically

## Old Scripts (DEPRECATED - Don't Use)

These are being phased out:
- ❌ `scripts/build/update-mdbook.sh` → Use `./build-all.sh`
- ❌ `scripts/build/update-single.sh` → Use `./build-one.sh`
- ❌ `scripts/build/serve.sh` → Use `./dev-server.sh`
- ❌ `mdbook serve` → Use `./dev-server.sh`

---

## Quick Tips

- Run from repository root (`/Users/leahsilber/Github/city_of_rivergrove/`)
- Scripts are smart - they detect document types automatically
- Use `--quick` flag with `build-all.sh` to skip Airtable sync (faster)
- Check `docs/build-system-audit.md` for detailed technical information