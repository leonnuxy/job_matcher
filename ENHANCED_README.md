# Job Matcher with Enhanced Resume Optimization

This project helps to automate job searching, matching, and resume optimization using AI.

## Quick Start

### 1. Run Job Search

To search for jobs based on the terms in `data/search_terms.txt` and find matches:

```bash
./run_job_search.sh
```

This will:
1. Search for jobs using the terms in `data/search_terms.txt`
2. Match them against your resume in `data/resume.txt`
3. Save results in the `results/` directory
4. Show you the path to the latest results file

### 2. Optimize Resume for a Specific Job

Once you've found a job you're interested in, save the job description to a file in `data/job_descriptions/`, then run:

```bash
./run_resume_optimizer.sh data/job_descriptions/your_job_description.txt
```

This will:
1. Use your resume from `data/resume.txt`
2. Apply the enhanced prompt template from `prompt.txt`
3. Generate an optimized resume and cover letter
4. Save the results in `data/optimization_results/`

## Features

- **Enhanced Resume Template**: The prompt template in `prompt.txt` has been optimized to:
  - Group similar skill lines to limit the Skills section to 5 bullet points
  - Format section headers like `### **Experience**`
  - Limit the summary to exactly two sentences
  - Format Education & Certifications as bullet points
  - Remove any placeholder text like "(mention if you have experience)"

- **Job Search**: Searches for jobs matching your search terms
- **Resume Matching**: Calculates match scores against your resume
- **AI Optimization**: Uses Google Gemini AI to tailor your resume for specific job descriptions

## Requirements

- Python 3.9+
- Google API credentials in config.py
- Required packages in requirements.txt

## Installation

```bash
pip install -r requirements.txt
```

Configure your API keys in `config.py`.

## Directory Structure

- `data/resume.txt` - Your resume text
- `data/search_terms.txt` - Job search queries
- `data/job_descriptions/` - Store job descriptions here
- `data/optimization_results/` - Contains optimized resumes and cover letters
- `results/` - Job search results
- `prompt.txt` - The enhanced prompt template

For more details on command-line usage, see `CLI_USAGE.md`.
