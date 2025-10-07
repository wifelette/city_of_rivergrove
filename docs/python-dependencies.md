# Python Dependencies Management

## Current Solution: requirements.txt + pip install

### What Happened (Historical Context)
Homebrew Python updates have repeatedly broken our scripts by removing installed packages. We've evolved through several solutions:
1. **Sept 2025**: System Python (`/usr/bin/python3`) to avoid Homebrew updates
2. **Oct 2025**: Back to `#!/usr/bin/env python3` with `requirements.txt` for proper dependency management

### The Current Solution
We now use standard Python dependency management:
- **requirements.txt** - Tracks all Python dependencies with versions
- **pip install --break-system-packages** - Installs to Homebrew Python (externally managed)
- **GitHub Actions** - Automatically installs from requirements.txt in CI/CD

### Setup Instructions

#### 1. Install Dependencies Locally
```bash
pip3 install --break-system-packages -r requirements.txt
```

The `--break-system-packages` flag is required for Homebrew Python 3.13+, which is "externally managed" and normally blocks pip installs.

#### 2. Required Modules
Our scripts require these Python modules (see `requirements.txt`):
- `beautifulsoup4==4.14.2` - HTML parsing and manipulation
- `lxml==6.0.2` - XML/HTML parser (faster than html.parser)
- `python-dotenv` - Environment variable loading
- `requests` - HTTP requests (Airtable integration)
- `pyairtable` - Airtable API client

#### 3. Script Shebangs
All Python scripts use:
```python
#!/usr/bin/env python3
```

This finds Python from PATH, which works:
- **Locally**: With Homebrew Python + installed dependencies
- **GitHub Actions**: With setup-python action setting PATH

**Never use hardcoded paths** like `#!/usr/bin/python3` - breaks in CI/CD.

#### 4. Adding New Dependencies
When adding a new Python module:

1. Install it locally:
   ```bash
   pip3 install --break-system-packages module-name
   ```

2. Add to `requirements.txt` with version:
   ```bash
   pip3 freeze | grep module-name >> requirements.txt
   ```

3. Commit both the code changes and updated requirements.txt

### Troubleshooting

#### If Scripts Fail with Module Import Errors
1. Verify Python version and location:
   ```bash
   which python3  # Should show Homebrew Python
   python3 --version  # Should be 3.13+
   ```

2. Check if dependencies are installed:
   ```bash
   pip3 list | grep -E "beautifulsoup4|lxml|dotenv"
   ```

3. If missing, install from requirements.txt:
   ```bash
   pip3 install --break-system-packages -r requirements.txt
   ```

4. Test specific imports:
   ```bash
   python3 -c "import bs4; print('BeautifulSoup4 OK')"
   python3 -c "import lxml; print('lxml OK')"
   python3 -c "import dotenv; print('python-dotenv OK')"
   ```

#### If Dev Server Won't Start
The dev server may fail if postprocessing scripts can't import dependencies. Check:
```bash
# Test the main processor directly
./scripts/postprocessing/enhanced-custom-processor.py --help
```

If you see `ModuleNotFoundError: No module named 'bs4'`, install dependencies.

#### If pip install fails with "externally-managed-environment" error
This is expected with Homebrew Python 3.13+. Use the `--break-system-packages` flag:
```bash
pip3 install --break-system-packages -r requirements.txt
```

### Key Files That Require These Dependencies
Critical scripts that use BeautifulSoup4/lxml:
- `scripts/postprocessing/enhanced-custom-processor.py` - Main HTML postprocessor
- `scripts/postprocessing/unified-list-processor.py` - List formatting processor
- `scripts/tests/test-list-formatting.py` - List formatting tests
- `scripts/validation/validate-form-fields.py` - Form field validation
- `scripts/mdbook/sync-airtable-metadata.py` - Airtable sync (uses dotenv)

### Why Not Use Virtual Environments?
We intentionally don't use Python virtual environments because:
1. Scripts are called directly (executable with shebang) by build system
2. The dev server spawns these scripts without venv activation
3. GitHub Actions uses setup-python which manages dependencies globally
4. Simpler workflow for a documentation project with few dependencies
5. requirements.txt provides sufficient dependency tracking

### CI/CD Integration
The `.github/workflows/deploy.yml` workflow automatically installs dependencies:
```yaml
- name: Install Python dependencies
  run: |
    pip install --upgrade pip
    pip install -r requirements.txt
```

This ensures consistent dependencies between local development and production builds.

### Summary
- **All scripts use**: `#!/usr/bin/env python3` (finds Python from PATH)
- **Local setup**: `pip3 install --break-system-packages -r requirements.txt`
- **CI/CD setup**: `pip install -r requirements.txt` (no flag needed in Actions)
- **New dependencies**: Add to requirements.txt with version pinning
- **Troubleshooting**: Check `pip3 list` for installed packages