# LinkedIn Integration Module

## Overview

The LinkedIn integration provides functionality for analyzing LinkedIn job postings and determining how well they match your resume. It can extract job details from LinkedIn job URLs, check if job postings are still active, and calculate match scores against your resume.

## Features

- Extract job details from LinkedIn job URLs using guest API
- Check if job postings are still active
- Extract jobs from LinkedIn search results pages
- Calculate match scores against your resume
- Export results to JSON and Markdown formats

## Usage

### Through the Unified CLI

The LinkedIn functionality is integrated into the unified CLI system in `main.py`. You can use it with the `linkedin` subcommand:

```bash
# Process a single LinkedIn job URL
python main.py linkedin --url "https://www.linkedin.com/jobs/view/123456789"

# Process a LinkedIn search URL
python main.py linkedin --search-url "https://www.linkedin.com/jobs/search?keywords=python&location=canada"

# Process URLs from a text file (one URL per line)
python main.py linkedin --url-file "data/linkedin_urls.txt"

# Process LinkedIn jobs from job search results
python main.py linkedin --input "data/job_search_results/job_search_latest.json" --min-score 0.7

# Use LinkedIn guest API instead of HTML scraping
python main.py linkedin --url "https://www.linkedin.com/jobs/view/123456789" --use-api

# Save raw HTML responses for debugging
python main.py linkedin --url "https://www.linkedin.com/jobs/view/123456789" --save-html

# Export results to Markdown format
python main.py linkedin --url "https://www.linkedin.com/jobs/view/123456789" --export-md
```

### Using the Process LinkedIn Job Script Directly

You can also use the `process_linkedin_job.py` script directly:

```bash
# Process a single LinkedIn job URL
python process_linkedin_job.py --url "https://www.linkedin.com/jobs/view/123456789"

# Process a LinkedIn search URL
python process_linkedin_job.py --search-url "https://www.linkedin.com/jobs/search?keywords=python&location=canada"

# Process LinkedIn jobs from job search results
python process_linkedin_job.py --input "data/job_search_results/job_search_latest.json"
```

## Architecture

The LinkedIn integration is built with a clean, modular architecture:

- `services/linkedin.py`: Core LinkedIn-specific functionality
  - `extract_job_id_from_url()`: Extract job IDs from LinkedIn URLs
  - `fetch_job_via_api()`: Use LinkedIn guest API to fetch job details
  - `check_job_status()`: Check if a job is still active
  - `extract_job_title()`: Extract job title from HTML
  - `extract_jobs_from_search_url()`: Extract job listings from search results

- `process_linkedin_job.py`: Main script for processing LinkedIn jobs
  - Uses the functions from `services/linkedin.py`
  - Provides job analysis and match score calculation
  - Exports results to JSON and Markdown

## Testing

The LinkedIn integration includes a comprehensive test suite in `tests/test_linkedin.py`. You can run the tests using pytest:

```bash
# Run all tests
pytest tests/test_linkedin.py

# Run tests with verbose output
pytest -v tests/test_linkedin.py

# Or use the test runner script
./run_tests.py --linkedin
```
