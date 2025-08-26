#!/bin/bash
# Build script for Rivergrove mdBook site
# This script adds cross-references and then builds the book

echo "Adding cross-reference links..."
python3 add-cross-references.py

echo "Building mdBook..."
mdbook build

echo "Build complete!"