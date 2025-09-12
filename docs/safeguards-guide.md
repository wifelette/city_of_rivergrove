# Safeguards Against Common Build Errors

## Overview

This guide documents the safeguards implemented to prevent common build errors, particularly the recurring "wrong script" problem where using `mdbook serve` directly causes CSS and formatting issues.

## The Problem

Using `mdbook serve` directly causes several issues:
1. **CSS Loss**: mdBook deletes our custom CSS on every rebuild
2. **Formatting Break**: Custom list processors don't run
3. **Missing Enhancements**: Document notes and other enhancements disappear
4. **Persistent Confusion**: The site looks fine initially, then breaks on first change

## The Solution: Multiple Safeguards

We've implemented several layers of protection to prevent this mistake:

### 1. Primary Safeguard: `./mdbook` Wrapper

**Location**: `./mdbook` (symlink to `scripts/safeguards/mdbook-wrapper.sh`)

**How it works**:
- Intercepts any `mdbook serve` command in the project root
- Shows a warning explaining why it's dangerous
- Automatically redirects to `./dev-server.sh`

**Usage**:
```bash
# This command is now safe - it redirects automatically
./mdbook serve
```

### 2. Git Hook Protection

**Location**: `.githooks/pre-commit`

**How it works**:
- Prevents commits if `mdbook serve` is running directly
- Warns about scripts containing `mdbook serve` references
- Already configured via `git config core.hooksPath .githooks`

### 3. Optional Directory Override

**Location**: `scripts/safeguards/envrc-template`

**How it works**:
- Provides a shell function that overrides the `mdbook` command
- Can be activated with `direnv` or manually sourced

**Setup** (optional):
```bash
cp scripts/safeguards/envrc-template .envrc
source .envrc  # Or use direnv
```

### 4. PATH Override Script

**Location**: `scripts/safeguards/mdbook-path-override.sh`

**How it works**:
- Provides a big, clear warning when `mdbook serve` is attempted
- Can be added to PATH for system-wide protection in this project

## Quick Setup

To enable all safeguards:

```bash
./scripts/safeguards/enable-safeguards.sh
```

This script:
1. Configures git hooks
2. Creates the mdbook wrapper symlink
3. Provides instructions for optional setups

## The Correct Workflow

### For Development

**Always use**: `./dev-server.sh`

This script:
- Compiles CSS from modular files
- Runs custom list processor
- Runs enhanced document processor  
- Watches for changes
- Maintains all styles and formatting

### For Production Builds

**Use**: `./build-all.sh`

This script:
- Performs complete rebuild with all processing
- Compiles CSS
- Syncs with Airtable
- Runs all pre and post processors

### For Single Document Updates

**Use**: `./build-one.sh [path/to/document.md]`

This script:
- Updates a single document
- Runs necessary processors
- Faster than full rebuild

## What NOT to Do

❌ **Never run**: `mdbook serve`
- Even if it seems to work initially
- It will break on the first file change
- Our safeguards will prevent this

❌ **Never run**: `mdbook build` directly for production
- Use `./build-all.sh` instead
- Ensures all processing happens

## File Organization

```
city_of_rivergrove/
├── ./mdbook                          # Symlink to wrapper (safe to use)
├── ./dev-server.sh                   # Development server (ALWAYS use this)
├── ./build-all.sh                    # Production build
├── ./build-one.sh                    # Single document update
├── .githooks/
│   └── pre-commit                    # Prevents commits with mdbook serve
└── scripts/
    ├── safeguards/
    │   ├── enable-safeguards.sh      # Setup script
    │   ├── mdbook-wrapper.sh         # Wrapper that redirects
    │   ├── mdbook-path-override.sh   # PATH override with warnings
    │   └── envrc-template            # Directory-specific override
    └── build/
        └── compile-css.py            # CSS compilation (auto-run by scripts)
```

## Related Issues This Solves

1. **"Styles keep disappearing"** - CSS compilation now persists through builds
2. **"Formatting breaks randomly"** - Postprocessors now always run
3. **"Works locally but not in production"** - Same scripts for both environments
4. **"I ran the wrong command"** - Safeguards prevent this

## Troubleshooting

### If styles are missing:
```bash
./scripts/fix-styles.sh
```

### If mdbook serve is stuck running:
```bash
pkill -f "mdbook serve"
./dev-server.sh
```

### If commits are blocked:
Check for running `mdbook serve` processes and kill them.

## Key Principle

**When in doubt, use `./dev-server.sh`**

This single command handles everything correctly and prevents all the common mistakes that have plagued this project.