# Optimizer Module Consolidation

This directory contains optimizer modules for tailoring resumes and cover letters to specific job descriptions.

## Important Notice

This directory now contains a consolidated `optimizer.py` file that brings together functionality from:

1. `optimize.py` - Original basic optimizer 
2. `enhanced_optimizer.py` - Enhanced optimizer with keyword matching
3. `enhanced_optimizer_with_cover_letter.py` - Enhanced optimizer with cover letter
4. **`optimizer.py`** - **NEW CONSOLIDATED FILE with all functionality**

## Migration Approach

All original files are kept intact to maintain backward compatibility. This approach avoids disrupting existing code that relies on specific imports.

The consolidated module implements its own versions of utility functions to avoid circular dependencies, making it completely self-contained and ready to use.

## Usage For New Code

For new code, use the consolidated module directly:

```python
# Import the module
from optimizer import optimizer 

# Use its functions
result = optimizer.optimize_resume(resume_text, job_description, prompt_template)
```

## Features

The consolidated optimizer (`optimizer.py`) provides:

1. Basic resume optimization
2. Enhanced resume optimization with keyword matching
3. Cover letter generation
4. Placeholder sanitization in both resume and cover letter

## CLI Usage

You can run the consolidated optimizer from the command line:

```bash
python -m optimizer.optimizer --resume path/to/resume.txt --job path/to/job.txt
```

Optional flags:
- `--no-cover-letter` - Skip cover letter generation
- `--analyze-only` - Only analyze match without generating resume
- `--basic` - Use basic optimization without enhanced matching
