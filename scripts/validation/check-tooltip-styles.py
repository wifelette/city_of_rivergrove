#!/usr/bin/python3
"""
Validates that tooltip styles are correctly configured.
Checks for common issues that break tooltip display.
"""

import re
import sys
from pathlib import Path

def check_css_files():
    """Check CSS files for problematic opacity usage."""
    issues = []

    # Check form-fields.css
    css_file = Path('theme/css/components/form-fields.css')
    if css_file.exists():
        content = css_file.read_text()

        # Check for opacity on .signature-mark (excluding print styles, ::after, and hover states)
        # Split content into lines and check each rule individually
        lines = content.split('\n')
        in_print_block = False
        in_signature_mark = False
        brace_count = 0

        for i, line in enumerate(lines):
            # Track print media queries
            if '@media print' in line:
                in_print_block = True
            elif in_print_block and '}' in line:
                in_print_block = False

            # Check for problematic opacity (not in print, not in ::after, not in :hover)
            if ('.signature-mark {' in line and
                not in_print_block and
                '::after' not in line and
                ':hover' not in line):
                # Check next few lines for opacity
                for j in range(i, min(i+10, len(lines))):
                    if 'opacity:' in lines[j] and not 'opacity: 0' in lines[j] and not 'opacity: 1' in lines[j]:
                        issues.append("ERROR: .signature-mark should not use 'opacity' property - use rgba() for color instead")
                        break
                    if '}' in lines[j]:
                        break

        # Check that rgba is used for color
        if not re.search(r'\.signature-mark\s*{[^}]*color:\s*rgba\(', content, re.DOTALL):
            issues.append("WARNING: .signature-mark should use rgba() for transparent color")

    return issues

def check_html_files():
    """Check HTML files for inline opacity styles."""
    issues = []

    # Check style guide
    style_guide = Path('docs/css-refactor/style-guide.html')
    if style_guide.exists():
        content = style_guide.read_text()

        # Check for inline opacity on signature marks
        if re.search(r'class="signature-mark"[^>]*style="[^"]*opacity:', content):
            issues.append("ERROR: style-guide.html has inline opacity on signature-mark elements")

        # Check for problematic inline styles
        matches = re.findall(r'class="signature-mark"[^>]*style="([^"]*)"', content)
        for match in matches:
            if 'opacity:' in match and 'rgba' not in match:
                issues.append(f"ERROR: Found problematic inline style: {match[:50]}...")

    return issues

def main():
    """Run all validation checks."""
    print("Checking tooltip styles...")
    print("-" * 40)

    all_issues = []

    # Check CSS
    css_issues = check_css_files()
    all_issues.extend(css_issues)

    # Check HTML
    html_issues = check_html_files()
    all_issues.extend(html_issues)

    # Report results
    if all_issues:
        print("❌ Found issues with tooltip styles:\n")
        for issue in all_issues:
            print(f"  • {issue}")
        print("\nTooltips may not display correctly!")
        return 1
    else:
        print("✅ Tooltip styles are correctly configured")
        print("  • No opacity on .signature-mark")
        print("  • Using rgba() for transparent colors")
        print("  • No problematic inline styles found")
        return 0

if __name__ == "__main__":
    sys.exit(main())