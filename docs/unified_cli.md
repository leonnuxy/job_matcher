# Unified CLI System

## Overview

The job_matcher project now features a unified command-line interface (CLI) that provides a consistent way to access all functionality. This system replaces the previous individual scripts with a single entry point and subcommands.

## Architecture

The unified CLI system is implemented in `main.py` with the following architecture:

- Main parser with subcommands for different functionalities
- Each subcommand has its own argument parser with specific options
- Command functions encapsulate the logic for each subcommand
- Helper functions to set up parsers consistently

## Available Commands

### optimize

Optimize your resume for a specific job description.

```bash
python main.py optimize [options]
```

Options:
- `--job`, `-j`: Path to the job description file (default: "data/job_descriptions/job_description.txt")
- `--resume`, `-r`: Path to the resume file (default: "data/resume.txt")
- `--suffix`, `-s`: Custom suffix for output filename
- `--no-timestamp`: Don't include timestamp in output filename

Example:
```bash
python main.py optimize --job "data/job_descriptions/software_engineer.txt"
```

### search

Search for jobs across multiple platforms.

```bash
python main.py search [options]
```

Options:
- `--terms`: Search terms to use (overrides search_terms.txt)
- `--locations`: Locations to search in (default: "Remote", "Canada", "USA")
- `--recency`: Recency in hours (default: 24)
- `--google`: Use Google Custom Search API if available (default)
- `--no-google`: Don't use Google Custom Search API
- `--max-jobs`: Maximum jobs to fetch per board/location (default: 10)
- `--output`: Custom path for output JSON file
- `--simulate`: Run in simulation mode (no actual API calls)

Example:
```bash
python main.py search --terms "Python Developer" "Data Scientist" --recency 48
```

### match

Calculate match scores for job listings against a resume.

```bash
python main.py match [options]
```

Options:
- `--with-cover-letter`: Generate cover letters alongside optimized resumes
- `--min-score`: Minimum match score threshold (0.0 to 1.0, default: 0.0)
- `--resume`, `-r`: Path to the resume file (default: "data/resume.txt")
- `--input`, `-i`: Path to specific job search results JSON file

Example:
```bash
python main.py match --min-score 0.7 --with-cover-letter
```

### linkedin

Process and analyze LinkedIn job postings.

```bash
python main.py linkedin [options]
```

Options:
- `--url`, `-u`: Process a single LinkedIn job URL
- `--search-url`, `-su`: Process a LinkedIn search results URL
- `--url-file`, `-uf`: Path to a text file containing LinkedIn job or search URLs
- `--input`, `-i`: Path(s) to job search results JSON file(s)
- `--output`, `-o`: Path to output JSON file (default: "data/job_descriptions/linkedin_jobs_analysis.json")
- `--export-md`, `-md`: Export results to Markdown format
- `--resume`, `-r`: Path to the resume file (default: "data/resume.txt")
- `--max-jobs`, `-m`: Maximum number of jobs to process (default: 5)
- `--use-api`, `-a`: Use LinkedIn guest API instead of fallback method
- `--save-html`, `-s`: Save raw HTML responses for debugging
- `--min-score`, `-ms`: Minimum match score to process (0.0 to 1.0, default: 0.0)
- `--verbose`, `-v`: Enable verbose output

Example:
```bash
python main.py linkedin --search-url "https://www.linkedin.com/jobs/search?keywords=python&location=canada" --max-jobs 10
```

### api

Start the FastAPI server for the web interface.

```bash
python main.py api [options]
```

Options:
- `--host`: Host address to bind the server to (default: "127.0.0.1")
- `--port`, `-p`: Port to run the server on (default: 8000)
- `--reload`: Reload server on code changes (default: True)
- `--no-reload`: Disable reloading server on code changes

Example:
```bash
python main.py api --port 8080 --host "0.0.0.0"
```

### all

Run the entire job search, match, and analysis pipeline.

```bash
python main.py all [options]
```

Options:
- Combines options from search, match, and linkedin commands
- `--process-linkedin`: Also process LinkedIn jobs after matching

Example:
```bash
python main.py all --terms "Software Engineer" --process-linkedin --min-score 0.7
```

## Getting Help

For detailed help on any command:

```bash
python main.py [command] --help
```

For general help:

```bash
python main.py --help
```
