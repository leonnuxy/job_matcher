# Simplified LinkedIn Job Matcher

This script provides a simplified way to search for LinkedIn jobs and match them against your resume using a more lenient matching approach. It was created to address the need for more reliable job matching with lower thresholds to ensure results are returned.

## Features

- **Simple Interface**: Easily search for jobs with a specific title in a specific location
- **Lenient Matching**: Uses a more forgiving matching algorithm (0.8 threshold multiplier)
- **Recent Jobs**: Filters for jobs posted within a specified timeframe
- **Markdown Reports**: Automatically generates readable reports of job matches
- **Low Threshold**: Sets a very low minimum score (0.01) to ensure results are returned

## Usage

```bash
# Basic usage with defaults (Software Developer jobs in Canada from last 48 hours)
./simplified_linkedin_search.py

# Search for a different job title
./simplified_linkedin_search.py --search "Data Scientist"

# Search in a different location
./simplified_linkedin_search.py --location "Remote"

# Search for very recent jobs (last 24 hours)
./simplified_linkedin_search.py --recency 24

# Get more job results
./simplified_linkedin_search.py --max-jobs 10

# Specify a custom output path
./simplified_linkedin_search.py --output "my_job_results.json"

# Don't export as Markdown (JSON only)
./simplified_linkedin_search.py --no-md

# Don't use LinkedIn guest API
./simplified_linkedin_search.py --no-api
```

## How It Works

1. **URL Generation**: Creates a LinkedIn search URL with your parameters
2. **Job Extraction**: Extracts job listings from the search results page
3. **Initial Scoring**: Calculates preliminary match scores for each job
4. **Detailed Analysis**: Fetches full job details for better matching
5. **Final Scoring**: Applies the full matching algorithm with lenient settings
6. **Report Generation**: Creates a detailed report of matching jobs

## Matching Algorithm

The script uses a simplified 3-component matching system:

1. **TF-IDF Similarity (60%)**: Measures how similar the job description is to your resume
2. **Keyword Matching (30%)**: Counts specific skills and keywords that match
3. **Title Relevance (10%)**: Evaluates job title relevance to your background

With the lenient mode, scores are boosted by a 0.8 multiplier to increase chances of finding matches.

## Output

Results are saved to the `data/job_matches/` directory with:
- A JSON file containing all job data
- A Markdown file with a formatted report of job matches
- A summary of match scores printed to the console

## Requirements

- Python 3.6+
- BeautifulSoup4
- Requests
- scikit-learn (for TF-IDF vectorization)

## Integration

This script works with the existing job_matcher project and can be incorporated into larger workflows.
