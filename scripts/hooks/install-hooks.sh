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

# Install pre-commit hook
if [ -f "scripts/hooks/pre-commit-check-book-edits.sh" ]; then
    # Create or append to pre-commit hook
    if [ -f "$HOOKS_DIR/pre-commit" ]; then
        # Check if our hook is already installed
        if grep -q "check-book-edits" "$HOOKS_DIR/pre-commit"; then
            echo -e "${YELLOW}⚠️  Pre-commit hook already installed${NC}"
        else
            # Append our check to existing pre-commit
            echo "" >> "$HOOKS_DIR/pre-commit"
            echo "# Check for book/ directory edits" >> "$HOOKS_DIR/pre-commit"
            echo "./scripts/hooks/pre-commit-check-book-edits.sh || exit 1" >> "$HOOKS_DIR/pre-commit"
            echo -e "${GREEN}✅ Added book/ check to existing pre-commit hook${NC}"
        fi
    else
        # Create new pre-commit hook
        cat > "$HOOKS_DIR/pre-commit" << 'EOF'
#!/bin/bash
# Git pre-commit hook for City of Rivergrove

# Check for book/ directory edits
./scripts/hooks/pre-commit-check-book-edits.sh || exit 1

exit 0
EOF
        echo -e "${GREEN}✅ Created pre-commit hook${NC}"
    fi
    
    # Make hook executable
    chmod +x "$HOOKS_DIR/pre-commit"
    chmod +x "scripts/hooks/pre-commit-check-book-edits.sh"
else
    echo "⚠️  Warning: pre-commit-check-book-edits.sh not found"
fi

echo ""
echo "Git hooks installed successfully!"
echo ""
echo "The pre-commit hook will:"
echo "  • Prevent committing files from book/ directory"
echo "  • Show helpful error messages if you try to commit generated files"
echo ""
echo "To bypass the hook in an emergency (not recommended):"
echo "  git commit --no-verify"