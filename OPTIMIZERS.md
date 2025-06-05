# Resume Optimization Components

This document explains the different resume optimization components in the project and when to use each one.

## 🎯 Recommended Usage

### 1. For Command Line Usage (Most Common):

Use the resume_optimizer package CLI:

```bash
# Optimize a resume for a job description
python -m resume_optimizer.cli path/to/job_description.txt

# Or use the convenience script
./run_resume_optimizer.sh path/to/job_description.txt
```

### 2. For Python Code Integration:

#### Option A: Use the High-Level Package (Recommended for structured data)

```python
from resume_optimizer import optimize_resume

result = optimize_resume(resume_text, job_description)
print(f"Match summary: {result['summary']}")
print(f"Skills to add: {result['skills_to_add']}")
# See resume_optimizer/schema.json for full response structure
```

#### Option B: Use the Document Generation Utility (For document extraction)

```python
from lib.optimization_utils import generate_optimized_documents

resume, cover_letter, raw_response = generate_optimized_documents(resume_text, job_description)
# resume and cover_letter are ready-to-use strings extracted from the response
```

## 📊 Component Status

| Component | Purpose | Status | Last Updated |
|-----------|---------|--------|--------------|
| `resume_optimizer` package | Structured package with JSON schema validation, caching, error handling | ✅ **Active** | Jun 2025 |
| `lib/optimization_utils.py` | Utility library for extracting documents from Gemini responses | ✅ **Active** | Jun 2025 |
| `resume_optimizer/cli.py` | Command-line interface for the package | ✅ **Active** | Jun 2025 |
| `tests/test_resume_optimizer_package.py` | Test suite for resume optimization | ✅ **Active** | Jun 2025 |
| ~~`test_prompt.py`~~ | Legacy standalone testing script | ❌ **Removed** | - |
| ~~`simple_optimizer.py`~~ | Legacy testing script | ❌ **Removed** | - |
| ~~`lib.api_calls.optimize_resume_with_gemini()`~~ | Legacy function with hardcoded prompt | ❌ **Removed** | - |

## 🔧 Recent Changes (June 2025)

✅ **Completed Consolidation:**
- Removed duplicate implementations
- Standardized on centralized utilities
- Updated all consumers to use new APIs
- Added comprehensive test coverage
- Created CLI interface for ease of use

❌ **Deprecated and Removed:**
- `test_prompt.py` and `simple_optimizer.py` scripts
- `optimize_resume_with_gemini()` function from `lib/api_calls.py`
- Legacy test file `tests/test_resume_optimizer_fix.py`

## Input/Output Formats

### Input

Both approaches accept:
- `resume_text`: Plain text resume content
- `job_description`: Plain text job description content

### Output Differences

1. **resume_optimizer package** returns structured JSON:
```json
{
  "summary": "Summary of match",
  "skills_to_add": ["skill1", "skill2"],
  "skills_to_remove": ["skill3"],
  "experience_tweaks": [
    {
      "original": "Original bullet",
      "optimized": "Improved bullet"
    }
  ],
  "formatting_suggestions": ["Format tip 1"],
  "collaboration_points": ["Point 1"]
}
```

2. **optimization_utils** returns:
   - `resume`: Extracted resume text between delimiters
   - `cover_letter`: Extracted cover letter text between delimiters
   - `raw_response`: The full raw text from the LLM

## Prompt Templates

Both approaches can use the same prompt file (`prompt.txt`) in the project root.

## Implementation Notes

1. The centralized `PROMPT_FILE_PATH` is defined in `config.py` and used by both systems.
2. Resume output formats depend on the prompt structure:
   - JSON output structure is defined in `resume_optimizer/schema.json`
   - Delimiter-based extraction uses `---BEGIN_RESUME---` and `---END_RESUME---`
