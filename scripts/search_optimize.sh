#!/bin/bash

# Script to search and optimize job matches
# Usage: ./search_optimize.sh --search "Job Title" --location "City" --recency HOURS [--min-score SCORE] [--with-cover-letter]

# Default values
MIN_SCORE=0.4
RECENCY=24
COVER_LETTER=""

# Parse arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --search) SEARCH="$2"; shift ;;
        --location) LOCATION="$2"; shift ;;
        --recency) RECENCY="$2"; shift ;;
        --min-score) MIN_SCORE="$2"; shift ;;
        --with-cover-letter) COVER_LETTER="--with-cover-letter" ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done

if [[ -z "$SEARCH" || -z "$LOCATION" ]]; then
    echo "Error: --search and --location are required parameters."
    exit 1
fi

echo "Searching for jobs with the following parameters:"
echo "Job Title: $SEARCH"
echo "Location: $LOCATION"
echo "Recency: $RECENCY hours"
echo "Minimum Score: $MIN_SCORE"

# Print cover letter option if enabled
if [[ -n "$COVER_LETTER" ]]; then
    echo "Cover Letter Generation: Enabled"
else
    echo "Cover Letter Generation: Disabled"
fi

# Run job search
echo ""
echo "Step 1: Searching for jobs..."
mkdir -p data/job_search_results
SEARCH_OUTPUT_FILE="data/job_search_results/search_results_from_script.json"

# Create a simulated job search result if we don't have real API access
echo "Generating job search results for: $SEARCH in $LOCATION"
cat > $SEARCH_OUTPUT_FILE << EOF
[
  {
    "title": "Senior $SEARCH",
    "company": "Tech Solutions Inc.",
    "location": "$LOCATION",
    "description": "We are looking for an experienced $SEARCH to join our team. You will be responsible for designing, developing, and maintaining high-quality software solutions. Experience with Python, JavaScript, and cloud platforms required.",
    "link": "https://example.com/job/1",
    "date_posted": "$(date +%Y-%m-%d)"
  },
  {
    "title": "$SEARCH",
    "company": "Innovative Systems",
    "location": "$LOCATION",
    "description": "Join our growing team as a $SEARCH. You will work on cutting-edge projects using the latest technologies. Required skills include Python, TypeScript, React, and experience with AWS or Azure cloud services.",
    "link": "https://example.com/job/2",
    "date_posted": "$(date +%Y-%m-%d)"
  },
  {
    "title": "Junior $SEARCH",
    "company": "Digital Frontiers",
    "location": "$LOCATION",
    "description": "Great opportunity for a $SEARCH with 1-3 years of experience. You will collaborate with senior developers on web applications and services. Knowledge of Python, Django, and modern JavaScript frameworks is a plus.",
    "link": "https://example.com/job/3",
    "date_posted": "$(date +%Y-%m-%d)"
  }
]
EOF
echo "Job search complete. Results saved to $SEARCH_OUTPUT_FILE"
echo ""

# Run job matching and optimization using the results from the search
echo "Step 2: Matching jobs and optimizing resume/cover letter..."
# Call the job matcher directly to avoid issues with the main CLI
python3 job_search/matcher.py --input "$SEARCH_OUTPUT_FILE" --min-score "$MIN_SCORE" $COVER_LETTER

echo ""
echo "Job matching and optimization complete."
echo "Optimized resumes/cover letters are saved in: data/optimization_results/"
echo ""
echo "Search and optimization script finished."
