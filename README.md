# Job Matching and Resume Optimization Project

This project aims to automate the process of finding relevant job postings, extracting job requirements, matching your resume to those requirements, and optimizing your resume for Applicant Tracking Systems (ATS).

## Project Structure

The project is organized into several modules:

- **optimizer/** - Resume optimization functionality
  - `optimize.py` - Core optimization logic using AI
  
- **services/** - Supporting services
  - `llm_client.py` - Client for interacting with AI language models
  - `utils.py` - Utility functions for file handling and more
  - `scraper.py` - Robust job board scraping functionality
  
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

4.  **Prepare your files:**
    * Place your resume in `data/resume.txt` (plain text format)
    * Create `data/search_terms.txt` with one job search keyword per line (lines starting with # are ignored)

5.  **Database setup:**
    * The application uses a MySQL database to store job search results
    * Configure your database connection details in the appropriate configuration file
    * The application will automatically create the necessary tables

## Usage

### Command Line Interface

#### Main Application

Run the `main.py` script:

```bash
python main.py
```

This will:
1. Read your resume from `data/resume.txt`
2. Read the job description from `data/job_descriptions/job_description.txt`
3. Use the chosen LLM provider (Gemini or OpenAI) to generate an optimized resume
4. Save the result to `data/optimization_results/` with a timestamp

You can also specify a custom job description file and output options:

```bash
python main.py --job path/to/job_description.txt --suffix custom_name --no-timestamp
```

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
