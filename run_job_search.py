#!/usr/bin/env python3
"""
Main script to run the job search and matching process.

This script can be run with various command line options:
- --search-only: Only run job search, not matching
- --match-only: Only run job matching, not search
- --simulate: Run in simulation mode (no actual API calls)
- --terms [TERMS]: Search terms to use (overrides search_terms.txt)
- --locations [LOCATIONS]: Locations to search in (default: Remote, Canada, USA)
- --recency HOURS: Only include results from the last N hours (default: 24)
- --google: Use Google Custom Search API if available (default)
- --no-google: Don't use Google Custom Search API
- --max-jobs N: Maximum jobs to fetch per board/location (default: 10)

Examples:
    python run_job_search.py --simulate --terms "Python Developer" "Data Scientist"
    python run_job_search.py --locations "New York" "San Francisco" --recency 5 --google
    python run_job_search.py --terms "DevOps Engineer" --recency 0.1 --search-only
    python run_job_search.py --no-google --search-only
"""
import os
import sys
from job_search.run import main

# Check if .env file exists, print helpful message if it doesn't
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
if not os.path.exists(env_path) and '--simulate' not in sys.argv:
    print("NOTE: No .env file found. Consider creating one with the following variables:")
    print("  GOOGLE_API_KEY=your_google_api_key")
    print("  GOOGLE_CSE_ID=your_google_custom_search_engine_id")
    print("  OPENAI_API_KEY=your_openai_api_key (for resume optimization)")
    print("\nRunning without these may limit functionality. Use --simulate for testing.")
    print("Use --no-google to disable Google Custom Search API usage.\n")

if __name__ == "__main__":
    main()
