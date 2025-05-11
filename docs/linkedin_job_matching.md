# LinkedIn Job Matching Enhancement

This document describes the enhanced LinkedIn job matching functionality in the job_matcher project.

## Overview

The LinkedIn job matching integration has been enhanced to leverage the advanced scoring mechanism from the main `matcher.py` module. This ensures that match scores are calculated consistently and robustly when using the LinkedIn service. With the new customizable matching options, you can now fine-tune how jobs are matched to your resume.

## Key Features

### Enhanced Match Scoring

LinkedIn job listings are now scored using a weighted combination of:

1. **TF-IDF Similarity (Default: 60%)** - A sophisticated text-similarity technique that compares your resume to job descriptions.
2. **Keyword Matching (Default: 30%)** - Direct matching of technical skills and keywords.
3. **Title Relevance (Default: 10%)** - Considers how well the job title keywords match your resume.

### Customizable Matching Profiles

You can now create custom matching profiles with different weights for each component:

```bash
# Example: Emphasize keyword matching for technical roles
python process_linkedin_job.py --keyword-weight 0.5 --tfidf-weight 0.4 --title-weight 0.1
```

### Matching Modes

Three matching modes are available to adjust how strict or lenient the matching algorithm is:

1. **Standard**: Uses the default threshold multiplier (1.0)
2. **Strict**: Uses a higher threshold multiplier (1.2), requiring stronger matches
3. **Lenient**: Uses a lower threshold multiplier (0.8), allowing more potential matches

```bash
# Example: Use lenient mode to see more potential matches
python process_linkedin_job.py --matching-mode lenient
```

### Search URL Processing

When processing LinkedIn search URLs, the system now:
- Automatically loads your resume to calculate match scores for all jobs in search results
- Evaluates each job listing against your resume, even before detailed job information is fetched
- Prioritizes higher-matching jobs when fetching details

### File Handling Improvements

The system now handles both:
- Directory paths containing multiple job files
- Direct JSON file inputs with job listings

### Convenience Script

A new script (`find_matching_linkedin_jobs.sh`) is included to help you find matching LinkedIn jobs. It:
- Progressively tries lower thresholds until finding matches
- Exports results to both JSON and Markdown formats
- Provides a summary of high, medium, and low matches

## Using the Enhanced Matcher

### Process a LinkedIn Search URL

```bash
python process_linkedin_job.py --search-url "https://www.linkedin.com/jobs/search/?keywords=software%20engineer" --resume data/resume.txt
```

### Process Multiple LinkedIn URLs from a File

```bash
python process_linkedin_job.py --url-file data/linkedin_urls.txt --resume data/resume.txt --export-md
```

### Find Jobs with Progressively Lower Thresholds

The script now supports advanced matching options:

```bash
./find_matching_linkedin_jobs.sh --resume data/resume.txt --mode lenient
```

Available options:
- `--resume`, `-r`: Path to resume text file
- `--input`, `-i`: Path to LinkedIn search results JSON
- `--output`, `-o`: Output directory path
- `--mode`: Matching mode (standard, strict, lenient)
- `--tfidf-weight`: Weight for TF-IDF text similarity
- `--keyword-weight`: Weight for keyword matching
- `--title-weight`: Weight for job title relevance

## Advanced Usage Examples

### Finding Jobs That Match Technical Skills

For a resume heavily focused on technical skills, increase the keyword weight:

```bash
python process_linkedin_job.py --input jobs.json --resume resume.txt --keyword-weight 0.5 --tfidf-weight 0.4 --title-weight 0.1
```

### Finding Jobs with Matching Job Titles

To prioritize job title matching:

```bash
python process_linkedin_job.py --input jobs.json --resume resume.txt --title-weight 0.3 --tfidf-weight 0.4 --keyword-weight 0.3
```

### Finding More Potential Matches

When you want to see more potential matches even if they're not perfect matches:

```bash
python process_linkedin_job.py --input jobs.json --resume resume.txt --matching-mode lenient
```

## How to Choose the Right Settings

- **Standard Mode**: Good for normal job searches, balancing precision and recall
- **Strict Mode**: Good for focused job searches when you want only the best matches
- **Lenient Mode**: Good for exploratory searches to see more potential opportunities

- **Higher TF-IDF Weight**: Better for matching overall context and job requirements
- **Higher Keyword Weight**: Better for matching specific skills and technologies
- **Higher Title Weight**: Better for matching specific job roles or titles

## Match Score Interpretation

The match scores range from 0.0 to 1.0 and can be interpreted as:
- **0.7-1.0**: High match (you are very well-qualified for this position)
- **0.4-0.7**: Medium match (you have relevant skills but may need to emphasize specific areas)
- **0.0-0.4**: Low match (this job may require skills that aren't prominent in your resume)

## Technical Implementation

The enhancement involved:
1. Updating the LinkedIn service methods to accept resume text
2. Integrating the `calculate_match_score` function from `job_search.matcher`
3. Adding title-based keyword extraction for better matching
4. Supporting both direct file paths and directory paths for job data

## Future Improvements

Potential future enhancements:
- Add command-line parameters to adjust weights for different components
- Cache results to avoid redundant API calls
- Implement parallel processing for large job listings
- Add machine learning-based relevance scoring
