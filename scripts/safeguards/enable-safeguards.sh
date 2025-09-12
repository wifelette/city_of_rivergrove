#!/bin/bash
# Enable safeguards to prevent accidental mdbook serve usage

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}Setting up mdbook safeguards...${NC}"
echo ""

# 1. Set up git hooks
if [ -d ".git" ]; then
    echo "1. Configuring git hooks..."
    git config core.hooksPath .githooks
    echo -e "   ${GREEN}✓ Git hooks configured${NC}"
else
    echo -e "   ${YELLOW}⚠ Not a git repository, skipping git hooks${NC}"
fi

# 2. Set up mdbook wrapper symlink
echo ""
echo "2. Setting up mdbook wrapper:"
if [ ! -e "mdbook" ]; then
    ln -s scripts/safeguards/mdbook-wrapper.sh mdbook
    echo -e "   ${GREEN}✓ Created mdbook wrapper symlink${NC}"
else
    echo -e "   ${GREEN}✓ mdbook wrapper already exists${NC}"
fi

# 3. Set up .envrc if desired
echo ""
echo "3. Directory environment setup (optional):"
echo "   To set up directory-specific overrides:"
echo "   ${BLUE}cp scripts/safeguards/envrc-template .envrc${NC}"
echo "   Then either:"
echo "   - Use direnv: ${BLUE}brew install direnv && direnv allow${NC}"
echo "   - Or manually: ${BLUE}source .envrc${NC}"

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Safeguards created successfully!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "Available safeguards:"
echo "  • ./mdbook symlink - redirects serve to dev-server.sh"
echo "  • .githooks/pre-commit - prevents commits with mdbook serve running"
echo "  • scripts/safeguards/ - Contains all safeguard scripts"
echo "  • Optional: .envrc for directory-specific overrides"
echo ""
echo -e "${BLUE}These safeguards will prevent the 'mdbook serve' mistake!${NC}"