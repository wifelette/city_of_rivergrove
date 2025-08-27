#!/bin/bash
# Sync ordinances and rebuild mdBook

echo "🔄 Syncing ordinances from Ordinances/ to src/ordinances/..."
python3 sync-ordinances.py

echo "📚 Rebuilding mdBook..."
mdbook build

echo "✅ Done! Your changes should now be visible at http://localhost:3000"
