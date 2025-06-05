#!/bin/bash
# Script to run the job_matcher with search command to find matching jobs and optimize resumes

# Set current directory to the project root
cd "$(dirname "$0")"

# Make sure the script is executable
chmod +x ./job_matcher.py

# Step 1: Run the job search to find matching jobs
echo "Step 1: Running job search to find matching jobs..."
./job_matcher.py search

# Step 2: View the results
echo ""
echo "Step 2: Results saved in the results directory"
echo "Latest results file:"
find ./results -name "job_search_*.json" -type f -print0 | xargs -0 ls -t | head -1

# Step 3: Look for top matching jobs
echo ""
echo "Step 3: Finding the top matching jobs..."
TOP_JOBS_FILE=$(find ./results -name "job_search_*.json" -type f -print0 | xargs -0 ls -t | head -1)

# Check if a file was found
if [ -n "$TOP_JOBS_FILE" ]; then
    echo "Top matching jobs found in: $TOP_JOBS_FILE"
    echo "To view and optimize for specific jobs, run:"
    echo "./job_matcher.py optimize --job <job_description_file> --with-cover-letter"
else
    echo "No job search results found. Please run the search first."
fi

echo ""
echo "Done! Check the results directory for job search results and the optimization_results directory for optimized resumes."
