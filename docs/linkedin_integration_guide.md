# LinkedIn Job Matching Integration Guide

This guide covers the LinkedIn job matching features in the Job Matcher application, including the enhanced scoring mechanism and convenience scripts.

## Table of Contents
- [Overview](#overview)
- [Scripts and Tools](#scripts-and-tools)
- [Advanced Matching Options](#advanced-matching-options)
- [Working with LinkedIn Jobs](#working-with-linkedin-jobs)
- [Troubleshooting](#troubleshooting)

## Overview

The LinkedIn job matching integration provides a seamless way to match your resume against LinkedIn job postings. It uses an enhanced matching algorithm that combines multiple techniques:

1. **TF-IDF Text Similarity** - Compares the text content of your resume with job descriptions
2. **Keyword Matching** - Identifies important keywords and skills in both documents
3. **Job Title Relevance** - Evaluates how well your experience matches the job title

These components are weighted and combined to produce a final match score between 0.0 and 1.0.

## Scripts and Tools

### Main Integration Script

The `linkedin_integration.sh` script provides an interactive interface for all LinkedIn job matching features:

```bash
./linkedin_integration.sh
```

This launches a menu-based interface where you can:
- Run job matcher with customizable settings
- Process LinkedIn search URLs to extract job listings
- Process individual LinkedIn job URLs
- Find matching jobs with automatic threshold adjustment
- Change matching settings and weights

### Finding Matching Jobs

The `find_matching_linkedin_jobs.sh` script automatically tries progressively lower match thresholds until it finds jobs that match your resume:

```bash
./find_matching_linkedin_jobs.sh --resume path/to/resume.txt --input path/to/linkedin_jobs.json
```

Options:
- `--resume, -r`: Path to your resume text file
- `--input, -i`: Path to LinkedIn jobs JSON file
- `--output, -o`: Output directory for results
- `--mode`: Matching mode (standard, strict, lenient)
- `--tfidf-weight`: Weight for TF-IDF similarity (0.0-1.0)
- `--keyword-weight`: Weight for keyword matching (0.0-1.0)
- `--title-weight`: Weight for job title relevance (0.0-1.0)

### Command Line Usage

You can also use the main CLI directly:

```bash
python main.py linkedin [OPTIONS]
```

Key options:
- `--url`: Process a single LinkedIn job URL
- `--search-url`: Process a LinkedIn search URL to extract multiple jobs
- `--input`: Path to JSON file(s) with LinkedIn job listings
- `--resume`: Path to resume text file
- `--min-score`: Minimum match score threshold (0.0-1.0)
- `--export-md`: Generate Markdown report in addition to JSON output

## Advanced Matching Options

### Matching Modes

- **standard**: Balanced matching that works well for most resumes and job descriptions
- **strict**: Requires stronger evidence of matches, reducing false positives
- **lenient**: Allows more matches with less evidence, useful for exploratory searches

### Customizing Weights

You can adjust the weights of different matching components:

- **TF-IDF weight** (default 0.6): Text similarity importance
- **Keyword weight** (default 0.3): Keyword matching importance
- **Title weight** (default 0.1): Job title matching importance

The weights should add up to 1.0 for best results.

## Working with LinkedIn Jobs

### Collecting LinkedIn Job URLs

1. Search for jobs on LinkedIn that match your criteria
2. Copy the search URL from your browser
3. Use the integration script to process this search URL

Or collect individual job URLs:
1. Find job postings on LinkedIn
2. Copy their URLs (they should start with `https://www.linkedin.com/jobs/view/`)
3. Process them individually or save them in a text file

### Understanding Match Scores

Match scores are categorized into:
- **High matches** (>0.7): Strong fit with your resume
- **Medium matches** (0.4-0.7): Partial match worth considering
- **Low matches** (<0.4): Poor match or insufficient information

## Troubleshooting

### Common Issues

- **No matches found**: Try using lenient mode or adjusting weights
- **Error accessing files**: Check file paths and permissions
- **Script execution errors**: Ensure Python environment is properly set up

### File Locations

The default locations for key files:
- Resume: `data/resume.txt`
- Job listings: `data/linkedin_search_results.json`
- Output directory: `data/job_matches/`

You can customize these locations using command line options or through the interactive menu.
