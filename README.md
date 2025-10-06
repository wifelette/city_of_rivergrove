# City of Rivergrove Digital Repository

Searchable, centralized repository of City of Rivergrove ordinances, resolutions, and interpretations.

## Quick Start

Main build commands:
```bash
./build-all.sh                                # Full rebuild
./build-one.sh [file]                         # Single file update
./dev-server.sh                               # Development server
```

## Repository Structure

```
city_of_rivergrove/
├── source-documents/        # All source document folders
│   ├── Ordinances/         # Ordinance documents (.md and .pdf)
│   ├── Resolutions/        # Resolution documents (.md and .pdf)
│   ├── Interpretations/    # Planning Commission interpretations
│   ├── Other/              # Other documents (City Charter, etc.)
│   └── Transcripts/        # Meeting transcripts
│
├── src/                    # mdBook source files (auto-generated)
├── book/                   # mdBook output (HTML site)
│
├── scripts/                # All processing scripts
│   ├── build/             # Main orchestration scripts
│   ├── preprocessing/     # Scripts that run before mdBook
│   ├── postprocessing/    # Scripts that run after mdBook
│   ├── mdbook/           # mdBook-specific generation
│   ├── utilities/        # Helper tools
│   └── config/           # Configuration files
│
├── docs/                  # Project documentation
│   └── styles/           # Formatting standards
├── mockups/              # UI prototypes and mockups
├── tests/                # Test files
├── airtable/             # Airtable integration
│
└── CLAUDE.md            # Instructions for Claude Code
```

## Key Files

- **CLAUDE.md** - Instructions for Claude Code assistant
- **book.toml** - mdBook configuration
- **custom.css** - Site styling

## Documentation

### Main Guides
- [Build Quick Start](docs/build-quickstart.md) - Quick start guide for building the site
- [Project Overview](docs/digitization-guide.md) - Project overview and workflow guides
- [Claude Desktop Guide](docs/claude-desktop-guide.md) - Document processing & Airtable
- [Claude Code Guide](docs/claude-code-guide.md) - Repository management
- [mdBook Guide](docs/mdbook-guide.md) - Site generation and technical details
- [Build Architecture](docs/build-architecture.md) - Build system and dependencies
- [Airtable Integration](docs/airtable-integration.md) - Airtable sync documentation
- [Markdown Conventions](docs/markdown-conventions.md) - Document formatting standards

### Style Guides
- [Naming Conventions](docs/styles/naming-conventions.md) - File naming standards
- [Style Guide](docs/styles/STYLE-GUIDE.md) - Writing style guidelines
- [Signature Formatting](docs/styles/signature-formatting.md) - Signature block standards
- [Form Fields](docs/styles/form-fields.md) - Form field syntax
- [Inline Images](docs/styles/inline-images.md) - Image handling

### Technical Documentation
- [Scripts Guide](docs/scripts/SCRIPTS-GUIDE.md) - Complete script documentation
- [Visual Testing Guide](docs/visual-testing-guide.md) - Automated visual regression testing
- [Startup Prompts](docs/startup-prompts.md) - Quick start prompts for Claude

## Live Site

- **Production**: https://wifelette.github.io/city_of_rivergrove/
- **Local Development**: http://localhost:3000 (after running `./dev-server.sh`)