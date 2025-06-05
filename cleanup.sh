#!/bin/bash
# Simple cleanup script for git pre-commit hook

echo "Running cleanup operations..."

# Remove any Python cache files
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true

# Remove any temporary files
find . -name "*.tmp" -delete 2>/dev/null || true
find . -name ".DS_Store" -delete 2>/dev/null || true

echo "Cleanup completed successfully."
exit 0
