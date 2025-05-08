# Job Matching and Resume Optimization Project

This project aims to automate the process of finding relevant job postings, extracting job requirements, matching your resume to those requirements, and optimizing your resume for Applicant Tracking Systems (ATS).

## Project Structure

The project is organized into several modules:

- **optimizer/** - Resume optimization functionality
  - `optimize.py` - Core optimization logic using AI
  
- **services/** - Supporting services
  - `llm_client.py` - Client for interacting with AI language models
  - `utils.py` - Utility functions for file handling and more
  
- **api/** - API functionality
  - `api.py` - FastAPI endpoints for resume optimization
  - `run_api.py` - Script to run the API server
  
- **web/** - Web interface
  - `app.py` - Flask web application
  - `templates/` - HTML templates
  - `static/` - Static assets (CSS, JS, etc.)

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
- Results are stored in the database for future reference and analysis
