# Job Matching and Resume Optimization Project

A comprehensive automation system for finding relevant job postings, extracting job requirements, matching resumes to those requirements, and optimizing resumes for Applicant Tracking Systems (ATS).

## Table of Contents

- [Job Matching and Resume Optimization Project](#job-matching-and-resume-optimization-project)
  - [Table of Contents](#table-of-contents)
  - [Overview \& Features](#overview--features)
  - [Quick Start](#quick-start)
  - [Installation \& Setup](#installation--setup)
    - [1. Create Virtual Environment](#1-create-virtual-environment)
    - [2. Install Dependencies](#2-install-dependencies)
    - [3. Configure API Keys](#3-configure-api-keys)
    - [4. Prepare Data Files](#4-prepare-data-files)
    - [5. Database Setup](#5-database-setup)
  - [Core Components](#core-components)
    - [Job Parser Package](#job-parser-package)
      - [Modules](#modules)
      - [Usage](#usage)
      - [Implementation Features](#implementation-features)
    - [Resume Optimizer Package](#resume-optimizer-package)
      - [Architecture](#architecture)
      - [Usage](#usage-1)
      - [Response Schema](#response-schema)
    - [Testing Framework](#testing-framework)
      - [Directory Structure](#directory-structure)
      - [Available Tests](#available-tests)
  - [Usage Examples](#usage-examples)
    - [Basic Job Matching](#basic-job-matching)
    - [Resume Optimization](#resume-optimization)
    - [Running Tests](#running-tests)
  - [Configuration](#configuration)
    - [Environment Variables](#environment-variables)
    - [Configuration Files](#configuration-files)
  - [API Reference](#api-reference)
    - [Main Functions](#main-functions)
    - [Core Modules](#core-modules)
  - [Development](#development)
    - [Project Structure](#project-structure)
    - [Adding New Features](#adding-new-features)
    - [Code Quality](#code-quality)
  - [Contributing \& Future Improvements](#contributing--future-improvements)
    - [Current Limitations](#current-limitations)
    - [Planned Improvements](#planned-improvements)
    - [Contributing](#contributing)
  - [Results and Output](#results-and-output)

## Overview & Features

This project provides an end-to-end solution for job matching and resume optimization:

- **Automated Job Search**: Find relevant job postings using Google Custom Search
- **Intelligent Parsing**: Extract job descriptions, requirements, and locations from various sources
- **Resume Matching**: Calculate similarity scores between resumes and job requirements
- **ATS Analysis**: Simulate Applicant Tracking System behavior
- **Resume Optimization**: Use LLM models to optimize resumes for specific job descriptions
- **Comprehensive Testing**: Full testing framework for all components
- **Database Storage**: Store and analyze job search results over time

## Quick Start

```bash
# Clone and setup
git clone <repository-url>
cd job_matcher
python -m venv .venv
source .venv/bin/activate  # On Linux/macOS
pip install -r requirements.txt

# Configure API keys (see Configuration section)
# Add your resume to data/resume.txt
# Add search terms to data/search_terms.txt

# Run the system
python main.py
```

## Installation & Setup

### 1. Create Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate  # On Linux/macOS
.venv\Scripts\activate     # On Windows
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure API Keys

- Obtain a Google Custom Search Engine API key and CSE ID
- Set these values in `config.py` or as environment variables
- **Important**: Do not commit API keys to public repositories

### 4. Prepare Data Files

- Place your resume in `data/resume.txt` (plain text format)
- Create `data/search_terms.txt` with one job search keyword per line
- Lines starting with `#` in search terms file are ignored

### 5. Database Setup

- Configure MySQL database connection details in the configuration file
- The application will automatically create necessary tables

## Core Components

### Job Parser Package

Located in `lib/job_parser/`, this package handles extraction of job information from various sources.

#### Modules

- **extract_description.py**: Extracts main job description content from HTML or plain text
- **extract_requirements.py**: Identifies skills, technologies, and qualifications
- **extract_location.py**: Determines job location from job descriptions
- **parser_utils.py**: Shared utilities and constants

#### Usage

```python
from lib.job_parser import (
    extract_job_description,
    extract_job_requirements, 
    extract_job_location
)

# Extract job description
description = extract_job_description(job_text)

# Extract requirements
skills = extract_job_requirements(job_text)

# Extract location
location = extract_job_location(job_text)
```

#### Implementation Features

- Uses NLP techniques including Rake-nltk, spaCy, and regex patterns
- Handles both HTML and plain text job postings
- Filters out common non-skill words via stop word list
- Prioritizes and normalizes technology keywords

### Resume Optimizer Package

Located in `resume_optimizer/`, this package provides structured resume optimization using LLM models.

#### Architecture

- **prompt_builder.py**: Constructs well-structured prompts for the LLM
- **llm_client.py**: Handles Google Gemini API communication with retries and error handling
- **cache.py**: Provides efficient caching of optimization results
- **optimizer.py**: Orchestrates the optimization process
- **schema.json**: Defines the expected output structure
- **config.py**: Manages configuration from environment variables

#### Usage

```python
from resume_optimizer import optimize_resume

# Load resume and job description
with open("resume.txt", "r") as f:
    resume_text = f.read()

with open("job_description.txt", "r") as f:
    job_description = f.read()

# Optimize the resume
result = optimize_resume(resume_text, job_description)

# Process the results
print(f"Summary: {result['summary']}")
print(f"Skills to add: {', '.join(result['skills_to_add'])}")
print(f"Skills to remove: {', '.join(result['skills_to_remove'])}")

# Print experience tweaks
for tweak in result['experience_tweaks']:
    print(f"Original: {tweak['original']}")
    print(f"Optimized: {tweak['optimized']}")
```

#### Response Schema

```json
{
  "summary": "Brief summary of optimization suggestions",
  "skills_to_add": ["skill1", "skill2"],
  "skills_to_remove": ["skill3"],
  "experience_tweaks": [
    {
      "original": "Original bullet point",
      "optimized": "Improved bullet point"
    }
  ],
  "formatting_suggestions": ["Suggestion 1", "Suggestion 2"],
  "collaboration_points": ["Point 1", "Point 2"]
}
```

### Testing Framework

Located in `tests/`, this comprehensive testing framework validates all components.

#### Directory Structure

```
/tests
  /data       - Test data files (resumes, job descriptions)
  /scripts    - Test scripts
  /results    - Test results (generated JSON reports)
  /logs       - Test log files
```

#### Available Tests

**ATS Comparison Tests**
```bash
python tests/scripts/ats_comparison.py
```
- Compare resumes against job descriptions
- Calculate internal ATS scores
- Export files for testing with external ATS systems

**Job Parser Tests**
```bash
python tests/scripts/job_parser_simple_test.py
```
- Test extraction from various sources (API snippets, HTML, plain text)
- Validate job requirements identification
- Quality evaluation of extracted requirements

## Usage Examples

### Basic Job Matching

Run the complete job matching pipeline:

```bash
python main.py
```

This will:
1. Read search terms from `data/search_terms.txt`
2. Parse your resume from `data/resume.txt`
3. Find relevant job postings (filtering out senior roles)
4. Calculate similarity scores between resume and job requirements
5. Simulate ATS analysis
6. Store results in database and display in console

### Resume Optimization

Optimize a resume for a specific job:

```python
from resume_optimizer import optimize_resume

# Your existing code here
result = optimize_resume(resume_text, job_description)

# Save optimized resume
with open("optimized_resume.txt", "w") as f:
    f.write(result['optimized_resume'])
```

### Running Tests

**Run Resume Optimizer Tests**
```bash
# Run all tests
pytest resume_optimizer/tests/

# Run specific test file
pytest resume_optimizer/tests/test_optimizer.py

# Run with coverage
pytest --cov=resume_optimizer resume_optimizer/tests/
```

**Generate Test Data**
```bash
python tests/scripts/create_test_data.py
```

## Configuration

### Environment Variables

**Google Custom Search API**
- `GOOGLE_API_KEY`: Your Google API key
- `GOOGLE_CSE_ID`: Your Custom Search Engine ID

**Resume Optimizer (Gemini API)**
- `GEMINI_API_KEY`: Your Google Gemini API key
- `GEMINI_MODEL`: Model to use (default: "models/gemini-1.5-flash")
- `CACHE_TTL_SECONDS`: Cache TTL in seconds (default: 3600)
- `REQUEST_TIMEOUT_SECONDS`: API timeout in seconds (default: 5)
- `MAX_RETRIES`: Maximum retry attempts (default: 3)
- `BACKOFF_FACTOR`: Retry backoff factor (default: 0.5)
- `TEMPERATURE`: LLM temperature (default: 0.2)
- `MAX_OUTPUT_TOKENS`: Maximum output tokens (default: 2048)

### Configuration Files

- `config.py`: Main configuration file
- `resume_optimizer/config.py`: Resume optimizer specific configuration

## API Reference

### Main Functions

**Job Matching**
```python
from main import main
main()  # Run complete job matching pipeline
```

**Job Parser**
```python
from lib.job_parser import extract_job_description, extract_job_requirements, extract_job_location
```

**Resume Optimizer**
```python
from resume_optimizer import optimize_resume
```

### Core Modules

- `lib/matcher.py`: Resume-to-job matching algorithms
- `lib/ats.py`: ATS simulation functionality
- `lib/scraper.py`: Web scraping utilities
- `lib/database.py`: Database operations
- `services/`: Various utility services

## Development

### Project Structure

```
job_matcher/
├── main.py                 # Main application entry point
├── config.py              # Configuration management
├── requirements.txt       # Python dependencies
├── data/                  # Data files (resumes, search terms, results)
├── lib/                   # Core libraries
│   ├── job_parser/        # Job parsing package
│   ├── matcher.py         # Matching algorithms
│   ├── ats.py            # ATS simulation
│   └── ...
├── resume_optimizer/      # Resume optimization package
├── services/             # Utility services
├── tests/               # Testing framework
└── examples/            # Usage examples
```

### Adding New Features

1. **New Job Sources**: Extend `lib/scraper.py` or create new scrapers
2. **Enhanced Matching**: Modify algorithms in `lib/matcher.py`
3. **Additional Tests**: Add scripts to `tests/scripts/`
4. **New Optimizations**: Extend the resume optimizer package

### Code Quality

- Follow PEP 8 style guidelines
- Add comprehensive tests for new features
- Update documentation when adding new functionality
- Use type hints where appropriate

## Contributing & Future Improvements

### Current Limitations

- Web scraping can be fragile due to website layout changes
- ATS analysis is simulated and may not reflect real ATS behavior
- Maximum job age is configurable but defaults to 24 hours

### Planned Improvements

**Resume Optimizer**
- Add Redis cache backend option
- Support multiple LLM providers
- Add template management for different optimization strategies
- Implement streaming response handling for large inputs

**Job Parser**
- Enhanced NLP processing
- Support for more job board formats
- Improved location extraction
- Better skill normalization

**Testing**
- Integration with real ATS systems
- Performance benchmarking
- Automated regression testing

### Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## Results and Output

The system generates several types of output:

- **Console Results**: Real-time job matching scores and analysis
- **Database Storage**: Persistent storage of all job search results
- **CSV Exports**: Top matching jobs exported to CSV format
- **Optimized Resumes**: Generated in both Markdown and PDF formats
- **Test Reports**: Comprehensive testing results in JSON format

Results include:
- Job title and link
- Extracted keywords/requirements from job descriptions
- Similarity scores (how well your resume matches job requirements)
- ATS simulation scores (how an ATS might rank your resume)
- Optimization suggestions and improved resume versions

---

For detailed technical documentation on specific components, see:
- [Job Parser Details](lib/job_parser/README.md)
- [Resume Optimizer Details](resume_optimizer/README.md)
- [Testing Framework Details](tests/README.md)
