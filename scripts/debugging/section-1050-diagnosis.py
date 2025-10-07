#!/usr/bin/env python3
"""
Quick diagnostic tool for Section 1.050 list fragmentation issue.
Run this to see the current state of the problem.
"""

from bs4 import BeautifulSoup
from pathlib import Path
import sys

def diagnose():
    filepath = Path('book/ordinances/1989-Ord-54-89C-Land-Development.html')

    if not filepath.exists():
        print(f"ERROR: File not found: {filepath}")
        print("Run: mdbook build")
        sys.exit(1)

    with open(filepath, 'r') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    print("=" * 70)
    print("SECTION 1.050 DEFINITIONS - LIST STRUCTURE DIAGNOSIS")
    print("=" * 70)

    found = False
    for h in soup.find_all(['h3']):
        if '1.050' in h.get_text():
            found = True
            print("\n✓ Found Section 1.050")

            # Analyze what comes after
            current = h
            list_count = 0
            total_items = 0
            problems = []

            for _ in range(10):
                current = current.find_next_sibling()
                if not current:
                    break

                if current.name == 'p':
                    text = current.get_text()[:60]
                    if text.startswith('('):
                        problems.append(f"  ⚠️  Paragraph not converted: {text}...")

                elif current.name == 'ul':
                    list_count += 1
                    items = current.find_all('li', recursive=False)
                    total_items += len(items)

                    print(f"\n  List #{list_count}: {len(items)} items")

                    # Check for key markers
                    important_markers = []
                    for item in items:
                        marker = item.find('span')
                        if marker:
                            marker_text = marker.get_text()
                            if marker_text in ['(a)', '(i)', '(v)', '(w)', '(x)', '(y)']:
                                important_markers.append(marker_text)

                                # Special check for nested items
                                nested = item.find('ul')
                                if nested:
                                    nested_count = len(nested.find_all('li'))
                                    print(f"    • {marker_text} ✓ (has {nested_count} nested items)")
                                else:
                                    print(f"    • {marker_text}")

                    # Check for Article 2 contamination
                    for item in items:
                        if "Except as provided by Section 2.040" in item.get_text():
                            problems.append("  🚨 Article 2 content mixed into definitions list!")

                elif current.name in ['h2', 'h3', 'hr']:
                    print(f"\n  Next section boundary: {current.get_text()[:30]}...")
                    break

            # Analysis
            print("\n" + "=" * 70)
            print("ANALYSIS:")
            print("=" * 70)

            if list_count == 1 and total_items == 25:
                print("✅ GOOD: Single list with exactly 25 items (a-y)")
            else:
                print(f"❌ PROBLEM: {list_count} lists with {total_items} total items")
                print("   Expected: 1 list with 25 items")

            if problems:
                print("\nISSUES FOUND:")
                for problem in problems:
                    print(problem)

            print("\nEXPECTED STRUCTURE:")
            print("  • One <ul> with 25 <li> items")
            print("  • Items (a) through (y) for definitions")
            print("  • Item (i) 'Lot' should have 3 nested items")
            print("  • Item (w) 'Street' should have 4 nested items")
            print("  • No content from Article 2 mixed in")

            break

    if not found:
        print("ERROR: Could not find Section 1.050 in the HTML")

if __name__ == '__main__':
    diagnose()