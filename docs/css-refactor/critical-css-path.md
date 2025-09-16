# CRITICAL: CSS Import Path Documentation

## ⚠️ The Most Important Line in the Repository

The single most critical line for the entire site's styling is in `custom.css`:

```css
@import url('./theme/css/main.css');
```

**If this path is wrong, ALL CSS styling breaks site-wide.**

## Why This Matters

1. **mdBook copies `custom.css` to `book/custom.css` on every build**
   - This is mdBook's standard behavior
   - The file at the root is the source of truth

2. **The import path must match the actual file structure**
   - CSS files live at: `book/theme/css/main.css`
   - Import must be: `./theme/css/main.css`
   - NOT: `./theme/main.css` (missing `/css/`)

3. **A wrong path causes cascading failures**
   - No styles load
   - Form fields lose highlighting
   - Document formatting breaks
   - Navigation looks broken

## How We Protect Against This

### 🛡️ Layer 1: Pre-commit Hook
- Blocks commits if `custom.css` has wrong import path
- Provides immediate feedback to developers
- Located in: `scripts/hooks/pre-commit`

### 🛡️ Layer 2: Build-time Validation
- `build-all.sh` checks path before building
- Fails fast with clear error message
- Prevents broken builds from proceeding

### 🛡️ Layer 3: Test Suite
- `test-css-pipeline.sh` validates source file
- Runs 32+ tests including path validation
- Can be run manually anytime

### 🛡️ Layer 4: GitHub Actions CI
- `.github/workflows/css-validation.yml`
- Runs on every push and PR
- Catches issues before merge

### 🛡️ Layer 5: Documentation
- This file explains the criticality
- `BUILD-TROUBLESHOOTING.md` includes fixes
- Comments in scripts explain the issue

## What Can Go Wrong

### Scenario 1: Manual Edit Error
Someone edits `custom.css` and accidentally changes the path.

**Protection**: Pre-commit hook blocks the commit.

### Scenario 2: Script Modification
A script tries to "fix" the path incorrectly.

**Protection**: Build validation catches it before damage.

### Scenario 3: Merge Conflict Resolution
During a merge, the wrong path is chosen.

**Protection**: CI tests fail on the PR.

### Scenario 4: IDE Auto-"correction"
An IDE or linter thinks the path is wrong and "fixes" it.

**Protection**: Multiple validation layers catch it.

## If It Breaks Anyway

### Quick Fix:
```bash
# Fix the source file
sed -i '' "s|./theme/main.css|./theme/css/main.css|g" custom.css

# Rebuild
./build-all.sh
```

### How to Know It's Broken:
1. Browser console shows 404 for `/theme/css/main.css`
2. Site appears completely unstyled
3. Test suite fails on path check
4. Build script fails with path error

## Historical Context

This issue was discovered when CSS kept "disappearing" during builds. Investigation revealed:
1. Initial fix attempts patched symptoms (fix-styles.sh)
2. Root cause was the source `custom.css` having wrong path
3. mdBook was propagating the error on every build

Fixed in commits:
- `b4dfaf7` - Initial build improvements
- `67f5706` - Root cause fix

## Testing

Run this anytime to verify:
```bash
# Quick check
grep "@import" custom.css

# Full validation
./scripts/validation/test-css-pipeline.sh
```

## Remember

**Never change this import path unless the file structure changes:**
```css
@import url('./theme/css/main.css');
```

This line is tested, validated, and protected at multiple levels. If you think it needs changing, you're probably wrong. Check the actual file structure first.