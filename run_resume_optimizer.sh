#!/bin/bash
# Script to run the resume optimization with the updated prompt template
# This script directly generates separate resume and cover letter files
# by processing the Gemini API response and cleaning placeholders

# Set current directory to the project root
cd "$(dirname "$0")"

# Function to display help
show_help() {
  echo "Usage:"
  echo "  $0 <job_description_file>    # Run optimization with automatic document splitting"
  echo ""
  echo "Example:"
  echo "  $0 data/job_descriptions/job_description.txt"
}

# Check for help flag
if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
  show_help
  exit 0
fi

# Ensure a job description file was provided
if [ $# -eq 0 ]; then
  echo "Error: No job description file provided."
  show_help
  exit 1
fi

JOB_DESC_FILE="$1"

# Ensure the job description file exists
if [ ! -f "$JOB_DESC_FILE" ]; then
  echo "Error: Job description file '$JOB_DESC_FILE' not found."
  exit 1
fi

# Run the resume_optimizer CLI which uses the same prompt template
echo "Running resume optimization with the resume_optimizer package..."
python3 -m resume_optimizer.cli "$JOB_DESC_FILE"

echo ""
echo "Done! The optimized resume and cover letter files have been created."
echo "They are cleaned and ready to use without any manual editing of placeholders."