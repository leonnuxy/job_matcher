# Job Matching and Resume Optimization Project

This project aims to automate the process of finding relevant job postings, extracting job requirements, matching your resume to those requirements, and optimizing your resume for Applicant Tracking Systems (ATS).

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
    *   Obtain a Google Custom Search Engine API key and CSE ID.
    *   Set these values in `config.py` (or, preferably, as environment variables).
    *   **Important:** Do not commit your API keys to a public repository. Use environment variables instead.

4.  **Prepare your files:**
    * Place your resume in `data/resume.txt` (plain text format)
    * Create `data/search_terms.txt` with one job search keyword per line (lines starting with # are ignored)

5.  **Database setup:**
    * The application uses a MySQL database to store job search results
    * Configure your database connection details in the appropriate configuration file
    * The application will automatically create the necessary tables

## Usage

Run the `main.py` script:

```bash
python main.py
```

The script will:
1. Read search terms from `data/search_terms.txt`
2. Parse your resume from `data/resume.txt`
3. For each search term, find relevant job postings (filtering out senior roles)
4. Calculate similarity scores between your resume and job requirements
5. Simulate ATS analysis
6. Store results in the database and display them in the console

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
- Results are stored in the database for future reference and analysis
