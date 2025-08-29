# City of Rivergrove Digital Repository

Searchable, centralized repository of City of Rivergrove ordinances, resolutions, and interpretations.

## Quick Start

Main build commands:
```bash
./scripts/build/update-mdbook.sh              # Full rebuild
./scripts/build/update-single.sh [file]       # Single file update  
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
- [Project Guide](docs/digitization-guide.md) - Complete project documentation
- [Build Architecture](docs/build-architecture.md) - Build system and dependencies
- [Airtable Integration](docs/airtable-integration.md) - Airtable sync documentation
- [Navigation Redesign](docs/navigation-redesign.md) - Navigation system design
- [Markdown Conventions](docs/markdown-conventions.md) - Document formatting standards

### Style Guides
- [Naming Conventions](docs/styles/naming-conventions.md) - File naming standards
- [Style Guide](docs/styles/STYLE-GUIDE.md) - Writing style guidelines
- [Signature Formatting](docs/styles/signature-formatting.md) - Signature block standards
- [Form Fields](docs/styles/form-fields-syntax.md) - Form field syntax
- [Inline Images](docs/styles/inline-images-guide.md) - Image handling

### Technical Documentation
- [Scripts README](scripts/README.md) - Script documentation
- [Startup Prompts](docs/startup-prompts.md) - Quick start prompts for Claude

## Live Site

After running build scripts, view at: http://localhost:3000