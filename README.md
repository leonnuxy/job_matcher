# Job Matching and Resume Optimization Project

This project aims to automate the process of finding relevant job postings, extracting job requirements, matching your resume to those requirements, optimizing your resume for Applicant Tracking Systems (ATS), and generating tailored cover letters.

## Project Structure

The project is organized into several modules:

- **optimizer/** - Resume optimization functionality
  - `optimize.py` - Core optimization logic using AI
  
- **services/** - Supporting services
  - `llm_client.py` - Client for interacting with AI language models
  - `utils.py` - Utility functions for file handling and more
  - `scraper.py` - Robust job board scraping functionality
  - `linkedin.py` - LinkedIn-specific functionality including API and HTML parsing
  - `http_client.py` - HTTP client utilities
  - `html_fallback.py` - HTML parsing fallbacks for website scraping
  - `config.py` - Configuration settings
  
- **api/** - API functionality
  - `api.py` - FastAPI endpoints for resume optimization
  - `run_api.py` - Script to run the API server
  
- **web/** - Web interface
  - `app.py` - Flask web application
  - `templates/` - HTML templates
  - `static/` - Static assets (CSS, JS, etc.)
  
- **job_search/** - Job search and matching functionality
  - `search.py` - Job board scraping and search
  - `matcher.py` - Resume-job matching and optimization
  - `run.py` - Script to run search and matching

## Setup

1.  **Create a virtual environment:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Linux/macOS
    .venv\Scripts\activate  # On Windows
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure API keys:**
    *   Option 1: Set up Google Gemini API:
        - Obtain a Google Gemini API key from [Google AI Studio](https://makersuite.google.com/)
        - Set the environment variable: `export GEMINI_API_KEY=your_key_here`
        - Set LLM provider environment variable: `export LLM_PROVIDER=gemini`
    *   Option 2: Set up OpenAI API:
        - Obtain an OpenAI API key from [OpenAI Platform](https://platform.openai.com/)
        - Set the environment variable: `export OPENAI_API_KEY=your_key_here`
        - Set LLM provider environment variable: `export LLM_PROVIDER=openai`
    *   **Important:** Do not commit your API keys to a public repository. Use environment variables instead.

4. **Prepare your files**

   1. **Resume**  
      Place your plain-text resume at  
      ```
      data/resume.txt
      ```

   2. **Search terms**  
      Create a file at  
      ```
      data/search_terms.txt
      ```

## Unified Command-Line Interface

The project now features a unified CLI system with subcommands for all functionality:

```bash
# Main usage pattern
python main.py [command] [options]
```

### Available Commands

- **optimize**: Optimize resume for a specific job description
  ```bash
  python main.py optimize --job "data/job_descriptions/job_description.txt" --resume "data/resume.txt"
  ```

- **search**: Search for jobs across multiple platforms
  ```bash
  python main.py search --terms "Python Developer" --locations "Remote" "Canada"
  ```

- **match**: Calculate match scores for job listings against a resume
  ```bash
  python main.py match --min-score 0.6 --resume "data/resume.txt"
  ```

- **linkedin**: Process and analyze LinkedIn job postings
  ```bash
  # Process a single LinkedIn job URL
  python main.py linkedin --url "https://www.linkedin.com/jobs/view/123456789"
  
  # Process a LinkedIn search URL
  python main.py linkedin --search-url "https://www.linkedin.com/jobs/search?keywords=python&location=canada"
  
  # Process from job search results
  python main.py linkedin --input "data/job_search_results/job_search_latest.json"
  ```

- **api**: Start the FastAPI server for the web interface
  ```bash
  python main.py api --port 8000
  ```

- **all**: Run the entire job search, match, and analysis pipeline
  ```bash
  python main.py all --terms "Software Engineer" --process-linkedin
  ```

For detailed help on any command:
```bash
python main.py [command] --help
```
      ```  
      Each non-comment line should follow this CSV-style format:
      ```
      search_term, location, recency_in_hours
      ```
      - Lines beginning with `#` are ignored.  
      - `recency_in_hours` is a number (e.g. `0.1` = 6 minutes, `1` = 1 hour, `24` = 1 day, etc.).

      **Example `data/search_terms.txt`:**
      ```txt
      # List your queries, one per line:
      # Format: search_term, location, recency_in_hours
      # Recency values: 0.1 (6 min), 1 (1 hr), 5 (5 hrs), 24 (24 hrs), 72 (3 days)

      Python developer, Calgary, 48
      DevOps engineer, Edmonton, 72
      Cloud architect, Toronto, 48
      Machine learning engineer, Vancouver, 5
      ```



5.  **Database setup:**
    * The application uses a MySQL database to store job search results
    * Configure your database connection details in the appropriate configuration file
    * The application will automatically create the necessary tables

## Usage

### Command Line Interface

#### Running Job Search & Matching

The main script for running job searches and generating optimized documents is:

```bash
python run_job_search.py [options]
```

Options include:
- `--search-only` - Only run job search, not matching
- `--match-only` - Only run job matching, not search
- `--simulate` - Run in simulation mode (no API calls)
- `--terms TERMS [TERMS...]` - Search terms to use
- `--locations LOC [LOC...]` - Locations to search in
- `--recency HOURS` - Only include results from last N hours
- `--max-jobs N` - Maximum jobs to fetch per board/location
- `--with-cover-letter` - Generate cover letters alongside resumes

Examples:
```bash
# Run a full search with cover letters
python run_job_search.py --terms "Python Developer" --with-cover-letter

# Test the pipeline in simulation mode
python run_job_search.py --simulate --terms "DevOps Engineer" --with-cover-letter

# Only run matching on existing results
python run_job_search.py --match-only --with-cover-letter
```

For each matching job, the script will:
1. Read your resume from `data/resume.txt`
2. Load the cover letter template from `data/cover_letter_template.txt` (if `--with-cover-letter` is used)
3. Use AI to optimize your resume and cover letter for the job
4. Save both to `data/optimization_results/` with timestamps and job details in filenames
 
Output Naming Convention:
- Resumes: `Resume_JobTitle_Company_[timestamp].md`
- Cover Letters: `CoverLetter_JobTitle_Company_[timestamp].md`

Symlinks to the latest versions are maintained at:
- `data/optimization_results/latest_resume.md`
- `data/optimization_results/latest_cover_letter.md`

#### Resume Optimizer Module

You can also use the resume optimizer module directly:

```bash
python -m optimizer.optimize
```

This module provides more options for customizing the optimization process:

```bash
python -m optimizer.optimize --help
```

Available options:
- `--resume, -r`: Path to the resume file (default: data/resume.txt)
- `--job, -j`: Path to the job description file (default: data/job_descriptions/job_description.txt)
- `--prompt, -p`: Path to the prompt template file (default: prompt.txt)
- `--output, -o`: Custom output filename suffix
- `--no-timestamp`: Don't include timestamp in the output filename

Example usage:

```bash
# Basic usage
python -m optimizer.optimize

# With custom job description and output name
python -m optimizer.optimize --job data/job_descriptions/cloud_architect.txt --output cloud_architect

# Use your own resume and prompt template
python -m optimizer.optimize --resume path/to/my_resume.txt --prompt path/to/custom_prompt.txt --no-timestamp
```

The module will automatically extract the job title and company name from the job description to name the output file intelligently.

### API Usage

You can also use the API for resume optimization:

1. Run the API server:
```bash
python api/run_api.py
```

2. The API will be available at http://localhost:8000

3. You can use the following endpoints:
   - `POST /optimize` - Optimize a resume (see API documentation for request format)
   - `GET /health` - Health check endpoint

4. API documentation is available at:
   - http://localhost:8000/docs - Swagger UI
   - http://localhost:8000/redoc - ReDoc UI

### Web Interface

You can also use the web interface for a user-friendly experience:

1. Run the web server:
```bash
python run_web.py
```

2. Open your browser and navigate to http://localhost:5000

3. Use the form to paste your resume and job description

4. Click "Optimize Resume" to generate an optimized version

5. View the results in the browser and download as Markdown if needed

### Job Search and Matching

The project includes functionality to search job boards and match your resume to job listings:

1. Create a file `data/search_terms.txt` with your job search terms using the format:
```
# Format: search term, location, recency_in_hours
Python developer, Calgary, 24
DevOps engineer, Edmonton, 72
# Lines starting with # are ignored
Data scientist, Remote, 1
```

   The recency_hours parameter limits results to jobs posted within that time frame:
   - `0.1` - Jobs posted in the last 6 minutes
   - `1` - Jobs posted in the last hour
   - `24` - Jobs posted in the last day
   - `72` - Jobs posted in the last 3 days

2. **Google Custom Search API Setup (Optional but Recommended)**:
   * Create a Google Custom Search Engine at [Google Programmable Search Engine](https://programmablesearchengine.google.com/)
   * Get your Search Engine ID (cx)
   * Create an API key at [Google Cloud Platform](https://console.cloud.google.com/)
   * Add to your `.env` file:
     ```
     GOOGLE_API_KEY=your_api_key
     GOOGLE_CSE_ID=your_search_engine_id
     ```

3. Run the job search and matching process:
```bash
python run_job_search.py
```

This will:
1. Search for jobs using Google Custom Search API (if configured) or by scraping job boards
2. Save the results to `data/job_search_results/`
3. Match your resume against the found job listings
4. Optimize your resume for the top matching jobs

You can use various command-line options to customize the search:
```bash
# Only search for jobs with specific terms
python run_job_search.py --search-only --terms "Python Developer" "Data Engineer"
```

### Simplified LinkedIn Job Matcher

This script (`simplified_linkedin_search.py`) provides a simplified way to search for LinkedIn jobs and match them against your resume using a more lenient matching approach. It was created to address the need for more reliable job matching with lower thresholds to ensure results are returned.

#### Features

- **Simple Interface**: Easily search for jobs with a specific title in a specific location
- **Lenient Matching**: Uses a more forgiving matching algorithm (0.8 threshold multiplier)
- **Recent Jobs**: Filters for jobs posted within a specified timeframe
- **Markdown Reports**: Automatically generates readable reports of job matches
- **Low Threshold**: Sets a very low minimum score (0.01) to ensure results are returned

#### Usage

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

#### How It Works

1. **URL Generation**: Creates a LinkedIn search URL with your parameters
2. **Job Extraction**: Extracts job listings from the search results page
3. **Initial Scoring**: Calculates preliminary match scores for each job
4. **Detailed Analysis**: Fetches full job details for better matching
5. **Final Scoring**: Applies the full matching algorithm with lenient settings
6. **Report Generation**: Creates a detailed report of matching jobs

#### Matching Algorithm

The script uses a simplified 3-component matching system:

1. **TF-IDF Similarity (60%)**: Measures how similar the job description is to your resume
2. **Keyword Matching (30%)**: Counts specific skills and keywords that match
3. **Title Relevance (10%)**: Evaluates job title relevance to your background

With the lenient mode, scores are boosted by a 0.8 multiplier to increase chances of finding matches.

#### Output

Results are saved to the `data/job_matches/` directory with:
- A JSON file containing all job data
- A Markdown file with a formatted report of job matches
- A summary of match scores printed to the console

#### Requirements

- Python 3.6+
- BeautifulSoup4
- Requests
- scikit-learn (for TF-IDF vectorization)

#### Integration

This script works with the existing job_matcher project and can be incorporated into larger workflows.

```bash
# Search in specific locations
python run_job_search.py --locations "New York" "San Francisco" "Remote"

# Search in specific locations
python run_job_search.py --locations "New York" "San Francisco" "Remote"

# Set recency to find only very recent job postings (last hour)
python run_job_search.py --recency 1

# Combine parameters for more targeted searching
python run_job_search.py --terms "DevOps Engineer" --locations "Remote" --recency 24

# Run in simulation mode (no actual API calls)
python run_job_search.py --simulate

# Don't use Google Custom Search API (even if configured)
python run_job_search.py --no-google

# Only match existing job results with your resume
python run_job_search.py --match-only
```

### LLM Provider Options

You can switch between LLM providers by setting the `LLM_PROVIDER` environment variable:

```bash
# Use OpenAI
export LLM_PROVIDER=openai
export OPENAI_API_KEY=your_openai_key

# Use Google Gemini
export LLM_PROVIDER=gemini
export GEMINI_API_KEY=your_gemini_key
```

## Results

The results include:
- Job title and link
- Extracted keywords/requirements from the job description
- Similarity score (how well your resume matches the job requirements)
- ATS simulation score (how an ATS might rank your resume)

**Important Notes**
- The maximum job age can be configured in `main.py` (default: 24 hours)
- Web scraping can be fragile. Job board websites may change their layout, breaking the scraper.
- ATS analysis is simulated and may not accurately reflect the behavior of real ATS systems.
- Results are stored in JSON files in the `data/job_search_results/` directory

## LinkedIn Job Scraper

The project includes a dedicated LinkedIn job scraper (`process_linkedin_job.py`) that can extract and analyze LinkedIn job postings in detail.

### Features

- Extract job details from LinkedIn job postings using LinkedIn's guest API
- Check job status (active/inactive)
- Calculate match scores against your resume
- Export results to JSON and Markdown formats
- Process multiple LinkedIn jobs from search results or a single job URL
- Process LinkedIn search result URLs to extract job listings
- Process multiple URLs from a text file
- Filter jobs by minimum match score
- Save raw HTML responses for debugging
- **NEW:** Enhanced job matching using advanced scoring algorithm
- **NEW:** Convenience scripts for finding matching LinkedIn jobs

### Usage

#### Process a Single LinkedIn Job

To analyze a single LinkedIn job posting:

```bash
python process_linkedin_job.py --url "https://www.linkedin.com/jobs/view/job-title-at-company-jobid"
```

#### Process LinkedIn Jobs from Search Results JSON

To analyze multiple LinkedIn jobs from search results:

```bash
python process_linkedin_job.py --input "data/job_search_results/job_search_results.json"
```

#### Process a LinkedIn Search URL

To extract and analyze jobs from a LinkedIn search URL:

```bash
python process_linkedin_job.py --search-url "https://www.linkedin.com/jobs/search/?keywords=software%20developer" --resume data/resume.txt --export-md
```

#### Process URLs from a Text File

To process multiple LinkedIn job or search URLs from a text file:

```bash
python process_linkedin_job.py --url-file "data/linkedin_urls.txt"
```

The text file should contain one URL per line. Both job URLs and search URLs are supported:

```
https://www.linkedin.com/jobs/view/job-title-at-company-jobid
https://www.linkedin.com/jobs/search/?keywords=software%20developer
```

Lines starting with `//` are treated as comments and ignored.

#### Use the Enhanced LinkedIn Job Matcher

To find matching LinkedIn jobs using progressively lower thresholds:

```bash
./find_matching_linkedin_jobs.sh
```

The script will try different match score thresholds until it finds jobs matching your resume.

#### Interactive LinkedIn Integration

For an interactive menu of LinkedIn job matching options:

```bash
./linkedin_integration.sh
```

This provides a user-friendly way to access all LinkedIn job matching functionality.


## Cleaning Up and Maintenance

To keep your repository tidy and free of clutter from old outputs, test artifacts, and redundant files, use the provided cleanup script:

```bash
zsh cleanup.sh
```

This script will:
- Remove all `__pycache__/` folders and Python bytecode
- Move legacy, backup, and old output files to the `archive/` folder
- Delete unnecessary test artifacts and duplicate files
- Help maintain a clean, professional project structure

**Tip:** Review the script before running to ensure it matches your current cleanup needs. You can also adapt it for custom archiving or deletion rules as your project evolves.

Encourage all contributors to run this script regularly, especially before making pull requests or sharing the repository.

---
## Google Custom Search API Integration

This project includes integration with Google Custom Search API for more reliable job searching. To use this feature:

1. Create a Google Custom Search Engine at [Google Programmable Search Engine](https://programmablesearchengine.google.com/)
   - In your search engine settings, ensure you enable "Search the entire web"
   - You can optionally add specific job site URLs to prioritize (like indeed.com, linkedin.com, etc.)

2. Get your API credentials:
   - Get your Search Engine ID (cx) from your custom search engine settings
   - Create an API key at [Google Cloud Platform](https://console.cloud.google.com/)
   - Enable the "Custom Search API" in your Google Cloud project

3. Add the credentials to your `.env` file:
   ```
   GOOGLE_API_KEY=your_api_key_here
   GOOGLE_CSE_ID=your_search_engine_id_here
   ```

4. Run the job search with Google Custom Search:
   ```bash
   python run_job_search.py --google
   ```

Benefits of using Google Custom Search API:
- More reliable than direct web scraping
- Better search relevance
- Less likely to be blocked by job websites
- Simplified maintenance as you don't need to update scrapers when websites change

If Google Custom Search API credentials aren't available, the system will automatically fall back to traditional web scraping methods.
