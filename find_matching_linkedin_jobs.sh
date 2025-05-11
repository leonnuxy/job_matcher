#!/bin/bash

# Script to find matching LinkedIn jobs using the enhanced matcher
# This script will run the LinkedIn job parser with progressively lower thresholds
# until it finds some matching jobs.

echo "Starting LinkedIn job matching with enhanced matcher..."

# Parse command-line arguments
while [[ $# -gt 0 ]]; do
  key="$1"

  case $key in
    --resume|-r)
      RESUME="$2"
      shift 2
      ;;
    --input|-i)
      JOBS="$2"
      shift 2
      ;;
    --output|-o)
      OUTPUT_DIR="$2"
      shift 2
      ;;
    --mode)
      MATCHING_MODE="$2"
      shift 2
      ;;
    --tfidf-weight)
      TFIDF_WEIGHT="$2"
      shift 2
      ;;
    --keyword-weight)
      KEYWORD_WEIGHT="$2"
      shift 2
      ;;
    --title-weight)
      TITLE_WEIGHT="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      echo "Usage: $0 [--resume|-r RESUME_PATH] [--input|-i JOBS_JSON] [--output|-o OUTPUT_DIR] [--mode MATCHING_MODE] [--tfidf-weight WEIGHT] [--keyword-weight WEIGHT] [--title-weight WEIGHT]"
      exit 1
      ;;
  esac
done

# Set default values if not provided
RESUME=${RESUME:-"data/resume.txt"}
JOBS=${JOBS:-"data/linkedin_search_results.json"}
OUTPUT_DIR=${OUTPUT_DIR:-"data/job_matches"}
MATCHING_MODE=${MATCHING_MODE:-"standard"}
TFIDF_WEIGHT=${TFIDF_WEIGHT:-0.6}
KEYWORD_WEIGHT=${KEYWORD_WEIGHT:-0.3}
TITLE_WEIGHT=${TITLE_WEIGHT:-0.1}

mkdir -p "$OUTPUT_DIR"

echo "Configuration:"
echo "  Resume: $RESUME"
echo "  Jobs input: $JOBS"
echo "  Output directory: $OUTPUT_DIR"
echo "  Matching mode: $MATCHING_MODE"
echo "  TF-IDF weight: $TFIDF_WEIGHT"
echo "  Keyword weight: $KEYWORD_WEIGHT"
echo "  Title weight: $TITLE_WEIGHT"

# Thresholds to try (in descending order)
THRESHOLDS=(0.7 0.6 0.5 0.4 0.3 0.2 0.1 0.05 0.01)

# Function to check if we found matches
check_matches() {
    local matches=$(cat "$1" | grep -E '"high_matches"|"medium_matches"|"low_matches"' | grep -v ": 0" | wc -l)
    if [ $matches -gt 0 ]; then
        return 0  # Found matches
    else
        return 1  # No matches
    fi
}

# Try each threshold until we find matches
for threshold in "${THRESHOLDS[@]}"; do
    echo "Trying threshold: $threshold"
    
    # Format the output file name with timestamp and threshold
    OUTPUT="${OUTPUT_DIR}/linkedin_matches_${threshold}_$(date +%Y%m%d_%H%M%S).json"
    
    # Run the job matcher with the current threshold and custom matching configuration
    python process_linkedin_job.py linkedin --input "$JOBS" --output "$OUTPUT" --resume "$RESUME" --min-score "$threshold" --export-md \
      --matching-mode "$MATCHING_MODE" --tfidf-weight "$TFIDF_WEIGHT" --keyword-weight "$KEYWORD_WEIGHT" --title-weight "$TITLE_WEIGHT"
    
    # Check if we found matches
    if check_matches "$OUTPUT"; then
        echo "Found matches with threshold: $threshold"
        echo "Results saved to: $OUTPUT"
        
        # Also show the markdown file path
        MD_FILE="${OUTPUT%.json}.md"
        if [ -f "$MD_FILE" ]; then
            echo "Markdown report: $MD_FILE"
        fi
        
        exit 0
    else
        echo "No matches found with threshold: $threshold. Trying lower threshold..."
    fi
done

echo "No matches found with any threshold. Please check your resume and job descriptions."
exit 1
