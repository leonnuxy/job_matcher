#!/usr/bin/env python3
"""
Main script to run the job search and matching process.

This script is now a wrapper around the unified CLI in main.py.
For detailed options and examples, run:
    python main.py search --help

Examples:
    python main.py search --simulate --terms "Python Developer" "Data Scientist"
    python main.py search --locations "New York" "San Francisco" --recency 5 --google
    python main.py search --terms "DevOps Engineer" --recency 0.1
    python main.py search --no-google
"""
from main import main

if __name__ == "__main__":
    main()
    print("  OPENAI_API_KEY=your_openai_api_key (for resume optimization)")
    print("\nRunning without these may limit functionality. Use --simulate for testing.")
    print("Use --no-google to disable Google Custom Search API usage.\n")

if __name__ == "__main__":
    main()
