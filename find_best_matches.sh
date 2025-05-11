#!/bin/zsh
#
# Script to find job matches by trying different thresholds
# 

RESUME_PATH="${1:-data/resume.txt}"
JOBS_PATH="${2:-data/linkedin_search_results.json}"
MAX_JOBS="${3:-5}"
THRESHOLDS=(0.6 0.5 0.4 0.3 0.2 0.1 0.05 0.01)

echo "Starting job matching with progressively lower thresholds..."
echo "Resume: $RESUME_PATH"
echo "Jobs data: $JOBS_PATH"
echo "Max jobs to process: $MAX_JOBS"
echo ""

for threshold in "${THRESHOLDS[@]}"; do
    echo "Trying with threshold: $threshold"
    
    # Run the matcher with current threshold
    OUTPUT=$(./job_search/run_matcher.py --resume-path "$RESUME_PATH" --results-dir "$JOBS_PATH" --threshold "$threshold" --top-n "$MAX_JOBS")
    
    # Check if we found matches (look for "Found" in the output)
    if echo "$OUTPUT" | grep -q "Found .* matching jobs"; then
        echo "$OUTPUT"
        echo ""
        echo "✅ Found matches with threshold $threshold!"
        exit 0
    fi
done

echo ""
echo "❌ No matches found even with the lowest threshold ($THRESHOLDS[-1])."
echo "Try updating your resume to better match the job descriptions or add more jobs to search."
exit 1
