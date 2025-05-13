#!/bin/bash

# Script to find matching LinkedIn jobs using the enhanced matcher
# This script will run the LinkedIn job parser with progressively lower thresholds
# until it finds some matching jobs.

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Display help information
show_help() {
  echo "Usage: $(basename "$0") [OPTIONS]"
  echo
  echo "Find matching LinkedIn jobs using the enhanced matcher."
  echo "This script will try progressively lower thresholds until matches are found."
  echo
  echo "Options:"
  echo "  --resume, -r PATH       Resume file path (default: ${SCRIPT_DIR}/data/resume.txt)"
  echo "  --input, -i PATH        LinkedIn jobs input JSON file (default: ${SCRIPT_DIR}/data/linkedin_search_results.json)"
  echo "  --output, -o DIR        Output directory for results (default: ${SCRIPT_DIR}/data/job_matches)"
  echo "  --mode MODE             Matching mode: standard, strict, or lenient (default: standard)"
  echo "  --debug                 Enable debug mode with more verbose output"
  echo "  --help, -h              Display this help and exit"
  echo
  exit 0
}

echo "Starting LinkedIn job matching with enhanced matcher..."

# Parse command-line arguments
ENABLE_DEBUG=false
while [[ $# -gt 0 ]]; do
  key="$1"

  case $key in
    --help|-h)
      show_help
      ;;
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
    --debug)
      ENABLE_DEBUG=true
      shift
      ;;
    --tfidf-weight|--keyword-weight|--title-weight)
      echo "Notice: Weight parameters are no longer used. Using matching mode '$MATCHING_MODE' instead."
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      echo "Usage: $0 [--resume|-r RESUME_PATH] [--input|-i JOBS_JSON] [--output|-o OUTPUT_DIR] [--mode MATCHING_MODE] [--debug]"
      exit 1
      ;;
  esac
done

# Set default values if not provided
RESUME=${RESUME:-"${SCRIPT_DIR}/data/resume.txt"}
JOBS=${JOBS:-"${SCRIPT_DIR}/data/linkedin_search_results.json"}
OUTPUT_DIR=${OUTPUT_DIR:-"${SCRIPT_DIR}/data/job_matches"}
MATCHING_MODE=${MATCHING_MODE:-"standard"}

mkdir -p "$OUTPUT_DIR"

echo "Configuration:"
echo "  Resume: $RESUME"
echo "  Jobs input: $JOBS"
echo "  Output directory: $OUTPUT_DIR"
echo "  Matching mode: $MATCHING_MODE"
echo "  Debug mode: $ENABLE_DEBUG"

# Check if required files exist
if [ ! -f "$RESUME" ]; then
    echo "ERROR: Resume file not found: $RESUME"
    echo "Please check the path and try again."
    exit 1
fi

if [ ! -f "$JOBS" ]; then
    echo "ERROR: Jobs input file not found: $JOBS"
    echo "Please check the path and try again."
    exit 1
fi

# Run the Python script with different thresholds
echo "Processing LinkedIn jobs with enhanced matcher..."
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Debug mode flag
DEBUG_FLAG=""
if [ "$ENABLE_DEBUG" = true ]; then
    DEBUG_FLAG="--debug"
fi

# Try with different thresholds if no results initially
for THRESHOLD in 0.7 0.6 0.5 0.4 0.3 0.2 0.1 0.05 0.01; do
    echo "Running with threshold: $THRESHOLD"
    OUTPUT_FILE="${OUTPUT_DIR}/linkedin_job_matches_${TIMESTAMP}_${THRESHOLD}.json"
    
    # Run the Python script using the correct main.py linkedin command
    if [ "$ENABLE_DEBUG" = true ]; then
        echo "DEBUG: Running command: python3 ${SCRIPT_DIR}/main.py linkedin --input \"$JOBS\" --output \"$OUTPUT_FILE\" --resume \"$RESUME\" --use-api --min-score $THRESHOLD --matching-mode $MATCHING_MODE $DEBUG_FLAG --export-md"
    fi
    
    python3 "${SCRIPT_DIR}/main.py" linkedin --input "$JOBS" --output "$OUTPUT_FILE" --resume "$RESUME" \
            --use-api --min-score $THRESHOLD --matching-mode $MATCHING_MODE \
            $DEBUG_FLAG --export-md
    
    # Check if we got any matches
    MATCH_COUNT=$(grep -c "\"match_score\":" "$OUTPUT_FILE" 2>/dev/null || echo "0")
    NON_ZERO_COUNT=$(grep -c "\"match_score\": [^0]" "$OUTPUT_FILE" 2>/dev/null || echo "0")
    if [[ $MATCH_COUNT -gt 0 ]] || [[ "$THRESHOLD" = "0.01" ]]; then
        echo "Found $NON_ZERO_COUNT jobs with non-zero match scores at threshold $THRESHOLD"
        
        # Create symlink to the latest result
        ln -sf "$(basename "$OUTPUT_FILE")" "${OUTPUT_DIR}/latest_linkedin_matches.json"
        ln -sf "$(basename "${OUTPUT_FILE%.json}.md")" "${OUTPUT_DIR}/latest_linkedin_matches.md"
        
        echo "Results saved to: $OUTPUT_FILE"
        echo "Markdown report: ${OUTPUT_FILE%.json}.md"
        
        # If we're at the lowest threshold and still have zero matches, we need to check why
        if [[ $MATCH_COUNT -eq 0 ]] && [[ "$THRESHOLD" = "0.01" ]]; then
            echo "WARNING: No jobs with non-zero match scores found even at lowest threshold."
            echo "This could indicate a problem with the matching algorithm or data."
            echo "Check the resume and job data to ensure they're in the expected format."
            
            if [ "$ENABLE_DEBUG" = true ]; then
                echo "DEBUG: Examining the first few job entries to diagnose issues..."
                python3 -c "import json; f=open('$OUTPUT_FILE'); d=json.load(f); print(json.dumps(d['jobs'][0:2], indent=2)) if 'jobs' in d and len(d['jobs'])>0 else print('No jobs found')"
            fi
        fi
        
        # Exit if we found matches or we're at the lowest threshold
        break
    fi
    
    echo "No matches found at threshold $THRESHOLD, trying lower threshold..."
done

echo "Job matching complete!"
