#!/usr/bin/env python3
"""
mdBook preprocessor that ensures SUMMARY.md is always regenerated with Airtable metadata.
This runs BEFORE mdBook processes the book, ensuring sidebar always has correct titles and tags.
"""

import json
import sys
import subprocess
from pathlib import Path

def main():
    # mdBook sends the book context via stdin
    context, book = json.load(sys.stdin)
    
    # Get the root directory
    root_dir = Path(context["root"])
    
    # Regenerate SUMMARY.md with Airtable metadata
    # This ensures the sidebar always has the latest titles and special states
    script_path = root_dir / "scripts" / "mdbook" / "generate-summary-with-airtable.py"
    
    try:
        # Run the summary generator silently
        result = subprocess.run(
            ["python3", str(script_path)],
            cwd=str(root_dir),
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            # Log error but don't fail the build
            sys.stderr.write(f"Warning: Failed to regenerate SUMMARY.md: {result.stderr}\n")
    except Exception as e:
        # Log error but don't fail the build
        sys.stderr.write(f"Warning: Error regenerating SUMMARY.md: {e}\n")
    
    # Return the book unchanged - we only needed to regenerate SUMMARY.md
    print(json.dumps(book))
    return 0

if __name__ == "__main__":
    sys.exit(main())