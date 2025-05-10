#!/usr/bin/env bash
set -euo pipefail

echo "1/5 → Deleting __pycache__ directories…"
find . -type d -name "__pycache__" -print -exec rm -rf {} +

echo "2/5 → Deleting stray backup & test files…"
rm -f main.py.new
rm -f test_google_cse.py test_scraper.py test_reusme.md

echo "3/5 → Preparing archive directories…"
mkdir -p archive/job_search_results
mkdir -p archive/job_descriptions
mkdir -p archive/optimization_results
mkdir -p archive/linkedin_html

echo "4/5 → Archiving old run artifacts…"
# Job search results
mv data/job_search_results/job_search_*.json archive/job_search_results/ || true
mv data/job_search_results/real_time_searches_*.json archive/job_search_results/ || true
mv data/job_search_results/test_scraper_output_*.json archive/job_search_results/ || true

# Job descriptions
mv data/job_descriptions/*.json archive/job_descriptions/ || true
mv data/job_descriptions/*.md archive/job_descriptions/ || true

# Optimization results
mv data/optimization_results/Resume_*.md archive/optimization_results/ || true
mv data/optimization_results/CoverLetter_*.md archive/optimization_results/ || true
mv data/optimization_results/*.pdf archive/optimization_results/ || true

# LinkedIn HTML snapshots
mv data/linkedin_html/*.html archive/linkedin_html/ || true

echo "5/5 → Cleanup complete. Remaining structure is now:"
tree -I "__pycache__|archive"
