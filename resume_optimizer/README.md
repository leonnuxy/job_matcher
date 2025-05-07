# Resume Optimizer

A structured package for optimizing resumes based on job descriptions using LLM models.

## Overview

This package provides a clean, maintainable solution for resume optimization with the following components:

- **Prompt Builder**: Constructs well-structured prompts for the LLM
- **LLM Client**: Handles communication with Google Gemini API, with retries and error handling
- **Cache**: Provides efficient caching of optimization results
- **Schema Validation**: Ensures LLM responses conform to the expected structure
- **Comprehensive Testing**: Unit tests for all components

## Usage

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
    print()
```

## Response Schema

The optimization results follow this JSON schema:

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

## Configuration

Set the following environment variables:

- `GEMINI_API_KEY`: Your Google Gemini API key
- `GEMINI_MODEL`: Model to use (default: "models/gemini-1.5-flash")
- `CACHE_TTL_SECONDS`: Cache TTL in seconds (default: 3600)
- `REQUEST_TIMEOUT_SECONDS`: API timeout in seconds (default: 5)
- `MAX_RETRIES`: Maximum retry attempts (default: 3)
- `BACKOFF_FACTOR`: Retry backoff factor (default: 0.5)
- `TEMPERATURE`: LLM temperature (default: 0.2)
- `MAX_OUTPUT_TOKENS`: Maximum output tokens (default: 2048)

## Running Tests

```bash
# Run all tests
pytest resume_optimizer/tests/

# Run specific test file
pytest resume_optimizer/tests/test_optimizer.py

# Run with coverage
pytest --cov=resume_optimizer resume_optimizer/tests/
```

## Development Notes

### Architecture

- `prompt_builder.py`: Manages LLM prompt templates and construction
- `cache.py`: Provides in-memory caching (designed for easy upgrade to Redis)
- `llm_client.py`: Handles Gemini API communication with error handling
- `optimizer.py`: Orchestrates the optimization process
- `schema.json`: Defines the expected output structure
- `config.py`: Manages configuration from environment variables

### Future Improvements

- Add Redis cache backend option
- Support multiple LLM providers
- Add template management for different optimization strategies
- Implement streaming response handling for large inputs
