# Build System Troubleshooting Guide

## Overview

This guide helps diagnose and fix common build system issues, particularly around CSS, file overwrites, and the processing pipeline.

## Quick Diagnostics

Run this command to test the entire CSS pipeline:
```bash
./scripts/validation/test-css-pipeline.sh
```

Check for direct /src modifications:
```bash
./scripts/validation/check-src-modifications.sh
```

## Common Issues and Solutions

### 🔴 Issue: CSS Styles Not Loading / 404 Errors

**Symptoms:**
- Browser console shows 404 for `/theme/css/main.css`
- Page appears unstyled
- CSS works initially then disappears

**Root Causes:** 
1. mdBook cleans the `book/` directory on every build, removing manually copied files
2. The source `custom.css` file has incorrect import path (`./theme/main.css` instead of `./theme/css/main.css`)

**Solutions:**

1. **Check source custom.css has correct import:**
   ```bash
   grep "@import" custom.css
   # Should show: @import url('./theme/css/main.css');
   # NOT: @import url('./theme/main.css');
   ```

2. **Quick Fix:**
   ```bash
   ./scripts/fix-styles.sh
   ```

3. **Proper Development:**
   ```bash
   # Use dev-server.sh instead of mdbook serve
   ./dev-server.sh
   ```

4. **Manual Fix:**
   ```bash
   # Fix source custom.css if needed
   sed -i '' "s|./theme/main.css|./theme/css/main.css|g" custom.css
   
   # Copy theme directory
   cp -r theme book/
   
   # Run postprocessors
   python3 scripts/postprocessing/custom-list-processor.py
   python3 scripts/postprocessing/enhanced-custom-processor.py
   ```

**Prevention:**
- Always use `./dev-server.sh` for development
- Never use plain `mdbook serve`
- Run full builds with `./build-all.sh`

---

### 🔴 Issue: Files Keep Getting Overwritten

**Symptoms:**
- Changes disappear after builds
- Files revert to old versions
- Edits don't persist

**Root Cause:**
Editing files in `/src` instead of `source-documents/`

**Solutions:**

1. **Check for direct edits:**
   ```bash
   ./scripts/validation/check-src-modifications.sh
   ```

2. **If edits detected:**
   ```bash
   # Copy your changes to source-documents/
   # Then reset /src
   git checkout -- src/
   
   # Rebuild from source
   ./build-all.sh
   ```

**Prevention:**
- NEVER edit files in `/src` directly
- Always edit files in `source-documents/`
- The `/src` directory is auto-generated

---

### 🔴 Issue: Form Fields or Special Formatting Disappears

**Symptoms:**
- Blue form field highlighting gone
- Document notes not styled
- Special lists show double numbering

**Root Cause:**
Postprocessors not running after mdBook rebuilds

**Solutions:**

1. **Run postprocessors manually:**
   ```bash
   python3 scripts/postprocessing/custom-list-processor.py
   python3 scripts/postprocessing/enhanced-custom-processor.py
   ```

2. **Use enhanced server:**
   ```bash
   ./dev-server.sh
   ```

**Prevention:**
- Use `./dev-server.sh` which auto-runs postprocessors
- Always run full builds with `./build-all.sh`

---

### 🟡 Issue: Build Fails with "CSS not found"

**Symptoms:**
- Build script exits with error
- Message: "CSS file not found at book/theme/css/main.css"

**Root Cause:**
Theme directory failed to copy after mdBook build

**Solutions:**

1. **Retry the build:**
   ```bash
   ./build-all.sh
   ```

2. **Manual fix:**
   ```bash
   cp -r theme book/
   # Then continue build
   ```

**Prevention:**
- Ensure `theme/` directory exists and is not empty
- Check file permissions

---

### 🟡 Issue: Cross-References Not Working

**Symptoms:**
- Document references not clickable
- "Ordinance #52" remains plain text

**Root Cause:**
Cross-reference script not running or running in wrong order

**Solutions:**

1. **Rebuild with proper order:**
   ```bash
   ./build-all.sh
   ```

2. **Manual fix:**
   ```bash
   # Must run AFTER auto-link converter
   python3 scripts/preprocessing/auto-link-converter.py src/**/*.md
   python3 scripts/mdbook/add-cross-references.py
   ```

**Prevention:**
- Never add manual markdown links for document references
- Let the build system handle cross-references

---

## Build Pipeline Order

The correct order is CRITICAL:

1. **Sync** documents from source-documents/ to /src
2. **Validate** form field syntax
3. **Process** footnotes
4. **Convert** URLs/emails to links
5. **Add** cross-references (AFTER auto-link)
6. **Generate** SUMMARY.md
7. **Build** mdBook (cleans book/ directory!)
8. **Copy** theme/ to book/ (AFTER mdBook build)
9. **Apply** postprocessors (custom-list, enhanced)

## Testing the Build System

### Run Full Test Suite
```bash
# Test CSS pipeline
./scripts/validation/test-css-pipeline.sh

# Check for src modifications
./scripts/validation/check-src-modifications.sh

# Verify CSS is working
ls -la book/theme/css/main.css
```

### Manual Health Check
```bash
# 1. Check theme source exists
ls -la theme/css/main.css

# 2. Build and check
mdbook build
ls -la book/theme/  # Should NOT exist yet

# 3. Copy theme
cp -r theme book/

# 4. Verify
ls -la book/theme/css/main.css  # Should exist now
```

## Environment-Specific Issues

### macOS
- Use `sed -i ''` for in-place edits
- File watching with fswatch recommended

### Linux
- Use `sed -i` (no empty string)
- inotify for file watching

### Windows
- May need Git Bash or WSL
- Path separators might need adjustment

## Recovery Commands

### Complete Reset and Rebuild
```bash
# Clean everything
rm -rf book/
git checkout -- src/

# Full rebuild
./build-all.sh
```

### Fix Styles Only
```bash
./scripts/fix-styles.sh
```

### Validate Everything
```bash
./scripts/validation/test-css-pipeline.sh
./scripts/validation/check-src-modifications.sh
python3 scripts/validation/validate-form-fields.py
```

## Prevention Best Practices

1. **Always use the right server:**
   - Development: `./dev-server.sh`
   - Never: plain `mdbook serve`

2. **Edit the right files:**
   - Edit: `source-documents/`
   - Never edit: `/src/`

3. **Use the right build command:**
   - Full build: `./build-all.sh`
   - Single file: `./build-one.sh [file]`
   - Quick build: `./build-all.sh --quick`

4. **Test after changes:**
   ```bash
   ./scripts/validation/test-css-pipeline.sh
   ```

## Getting Help

If issues persist after trying these solutions:

1. Run diagnostics:
   ```bash
   ./scripts/validation/test-css-pipeline.sh
   ```

2. Check recent changes:
   ```bash
   git status
   git diff
   ```

3. Look for error patterns in:
   - Browser console
   - Terminal output
   - Build logs

4. File an issue with:
   - Error messages
   - Steps to reproduce
   - Output of diagnostic scripts