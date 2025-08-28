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
├── Ordinances/              # Ordinance documents (.md and .pdf)
├── Resolutions/             # Resolution documents (.md and .pdf)
├── Interpretations/         # Planning Commission interpretations
├── Other/                   # Other documents (City Charter, etc.)
│
├── src/                     # mdBook source files (auto-generated)
├── book/                    # mdBook output (HTML site)
│
├── scripts/                 # All processing scripts
│   ├── build/              # Main orchestration scripts
│   ├── preprocessing/      # Scripts that run before mdBook
│   ├── postprocessing/     # Scripts that run after mdBook
│   ├── mdbook/            # mdBook-specific generation
│   ├── utilities/         # Helper tools
│   └── config/            # Configuration files
│
├── airtable/               # Airtable integration
├── navigation-mockups/     # Navigation UI prototypes
├── docs/                   # Project documentation
│
└── CLAUDE.md              # Instructions for Claude Code
```

## Key Files

- **CLAUDE.md** - Instructions for Claude Code assistant
- **book.toml** - mdBook configuration
- **custom.css** - Site styling

## Documentation

- [Project Guide](docs/digitization-guide.md) - Complete project documentation
- [Markdown Conventions](docs/markdown-conventions.md) - Document formatting standards
- [Style Guide](docs/STYLE-GUIDE.md) - Writing style guidelines
- [Scripts README](scripts/README.md) - Script documentation

## Live Site

After running build scripts, view at: http://localhost:3000