# Job Matcher

A tool for matching resumes against job descriptions from LinkedIn and other sources.

## Features

- Compare a resume against multiple job descriptions using TF-IDF and cosine similarity
- Text normalization for better keyword matching (case-insensitive, punctuation-free comparisons)
- Rank jobs by match score
- Generate optimized resumes tailored to specific job descriptions
- Generate cover letters (optional)
- Save match results to CSV for further analysis

## Installation

1. Ensure you have Python 3.6+ installed
2. Install required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

### Command-Line Interface

The script `run_matcher.py` provides a command-line interface for the job matcher:

```bash
./job_search/run_matcher.py --resume-path /path/to/resume.txt --threshold 0.6 --top-n 5
```

#### Command-Line Arguments

| Argument               | Description                                       | Default      |
|------------------------|---------------------------------------------------|--------------|
| `-r`, `--resume-path`  | Path to the resume file                           | Default path |
| `-d`, `--results-dir`  | Directory with job search results or path to JSON file | Default dir  |
| `-t`, `--threshold`    | Minimum match score threshold (0.0-1.0)           | 0.5          |
| `-n`, `--top-n`        | Number of top matches to process                  | 3            |
| `-c`, `--cover-letter` | Generate cover letters for matching jobs          | False        |

### API Usage

You can also use the job matcher programmatically:

```python
from job_search.matcher import main as run_matcher

run_matcher(
    resume_path='/path/to/resume.txt',
    results_dir='/path/to/job/results',
    match_threshold=0.6,
    top_n=5,
    with_cover_letter=True
)
```

## How It Works

1. **Text Normalization**: All text is normalized by converting to lowercase, removing non-alphanumeric characters, and standardizing whitespace.
2. **Matching**: The system uses TF-IDF vectorization and cosine similarity to calculate match scores between the resume and job descriptions.
3. **Ranking**: Jobs are ranked by match score, with higher scores indicating better matches.
4. **Output**: 
   - Match results are saved to a CSV file with job details and scores
   - For top matches, optimized resumes (and optionally cover letters) are generated

## Data Structure

Match results are returned as a pandas DataFrame with the following columns:

- `id`: Job ID (if available)
- `title`: Job title
- `company`: Company name
- `score`: Match score (0.0-1.0)
- `location`: Job location
- `link`: URL to the job posting
- `job`: Full job data (for internal use)
