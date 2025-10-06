# Python Dependencies Management

## Issue: Homebrew Python Updates Breaking Scripts

### What Happened
On September 26, 2025, Homebrew automatically updated Python from 3.12.x to 3.13.7, which removed all previously installed pip packages including BeautifulSoup4 and python-dotenv. This broke all our Python scripts that relied on these modules.

### The Solution
All Python scripts now use the system Python (`/usr/bin/python3`) directly instead of relying on whatever Python is in the PATH (`/usr/bin/env python3`). The system Python has all required modules installed and is not affected by Homebrew updates.

### Prevention

#### 1. Check Python Path
Always verify which Python your scripts are using:
```bash
which python3  # Shows what's in PATH (often Homebrew)
/usr/bin/python3 --version  # System Python (stable)
```

#### 2. Required Modules
Our scripts require these Python modules:
- `beautifulsoup4` - HTML parsing and manipulation
- `python-dotenv` - Environment variable loading

These are installed in system Python at:
- `/Library/Python/3.9/site-packages/`

#### 3. Ensure Scripts Use System Python
Run this utility script periodically or after adding new Python scripts:
```bash
./scripts/utils/ensure-system-python.sh
```

This script:
- Finds all Python scripts using `#!/usr/bin/env python3`
- Updates them to use `#!/usr/bin/python3` (system Python)
- Reports which files were updated

#### 4. Installing New Dependencies
If you need to install new Python modules, install them for system Python:
```bash
/usr/bin/python3 -m pip install --user module-name
```

Never use:
```bash
pip3 install module-name  # This installs to Homebrew Python
```

### Troubleshooting

#### If Scripts Fail with Module Import Errors
1. Check which Python is being used:
   ```bash
   head -1 script-name.py
   ```

2. If it shows `#!/usr/bin/env python3`, update it:
   ```bash
   ./scripts/utils/ensure-system-python.sh
   ```

3. Verify modules are available in system Python:
   ```bash
   /usr/bin/python3 -c "import bs4; print('BeautifulSoup4 OK')"
   /usr/bin/python3 -c "import dotenv; print('python-dotenv OK')"
   ```

#### If Dev Server Won't Start
The dev server may fail if the postprocessing scripts can't run. Check:
```bash
# Test the main processor directly
/usr/bin/python3 scripts/postprocessing/unified-list-processor.py book/ordinances/1989-Ord-54-89C-Land-Development.html
```

### Key Files That Require These Dependencies
Critical scripts that use BeautifulSoup4:
- `scripts/postprocessing/unified-list-processor.py` - Main list formatting processor
- `scripts/tests/test-list-formatting.py` - List formatting tests
- `scripts/validation/check-styles-health.py` - Style health checks
- `scripts/mdbook/sync-airtable-metadata.py` - Airtable sync (uses dotenv)

### Why Not Use Virtual Environments?
We intentionally don't use Python virtual environments because:
1. Scripts need to run automatically during the build process
2. The dev server spawns these scripts without activation commands
3. System Python provides a stable, consistent environment
4. Avoiding complexity for a documentation project

### Summary
- Always use `/usr/bin/python3` (system Python) in script shebangs
- Never rely on `/usr/bin/env python3` (finds Homebrew Python)
- Run `ensure-system-python.sh` after adding new scripts
- Install modules to system Python with `--user` flag