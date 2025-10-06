#!/bin/bash
# Install git hooks for the City of Rivergrove repository

set -e

echo "📋 Installing git hooks..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the git hooks directory
HOOKS_DIR=".git/hooks"

if [ ! -d "$HOOKS_DIR" ]; then
    echo "❌ Error: Not in a git repository root directory"
    echo "   Run this script from the repository root"
    exit 1
fi

# Install our comprehensive pre-commit hook
if [ -f "scripts/hooks/pre-commit" ]; then
    echo "Installing comprehensive pre-commit hook..."
    cp scripts/hooks/pre-commit "$HOOKS_DIR/pre-commit"
    chmod +x "$HOOKS_DIR/pre-commit"
    echo -e "${GREEN}✅ Pre-commit hook installed${NC}"
    
    # Also ensure the old book check script is executable if it exists
    if [ -f "scripts/hooks/pre-commit-check-book-edits.sh" ]; then
        chmod +x "scripts/hooks/pre-commit-check-book-edits.sh"
    fi
else
    echo "⚠️  Warning: scripts/hooks/pre-commit not found"
fi

echo ""
echo "Git hooks installed successfully!"
echo ""
echo "The pre-commit hook will:"
echo "  • Prevent direct edits to /src files (except SUMMARY.md, etc.)"
echo "  • Prevent committing files from book/ directory"
echo "  • Show helpful guidance to edit source-documents/ instead"
echo "  • Run validation checks before commits"
echo "  • Remind to run visual tests when CSS files are modified"
echo ""
echo "To bypass the hook in an emergency (not recommended):"
echo "  git commit --no-verify"
echo ""
echo "To uninstall:"
echo "  rm .git/hooks/pre-commit"