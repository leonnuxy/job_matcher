#!/bin/bash

# Script to search and optimize job matches
# Usage: ./search_optimize.sh --search "Job Title" --location "City" --recency HOURS [--min-score SCORE]

# Default values
MIN_SCORE=0.4
RECENCY=24

# Parse arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --search) SEARCH="$2"; shift ;;
        --location) LOCATION="$2"; shift ;;
        --recency) RECENCY="$2"; shift ;;
        --min-score) MIN_SCORE="$2"; shift ;;
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

# Simulate job search and optimization
python3 run_job_search.py --search "$SEARCH" --location "$LOCATION" --recency "$RECENCY" --min-score "$MIN_SCORE"
