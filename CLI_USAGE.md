# How to Use the Job Matcher CLI

The Job Matcher CLI has been improved to use default configuration files and simplify usage. The main improvements are:

1. Default use of `data/search_terms.txt` for search terms
2. Default use of `data/resume.txt` for resume content
3. Added proper import path resolution for more reliable execution
4. Added missing `optimize` command for resume optimization

## Running the CLI

You can run the CLI using the wrapper script:

```bash
# From the project root directory
./job_matcher.py [command] [options]
```

Or run it directly with Python with proper path resolution:

```bash
# From the project root directory
python job_matcher.py [command] [options]
```

## Available Commands

1. **Search for Jobs**:
```bash
./job_matcher.py search
# Uses search terms from data/search_terms.txt by default
```

With custom parameters:
```bash
./job_matcher.py search --terms "Python Developer" "Data Scientist" --locations "Remote" "Canada"
```

2. **Match Jobs Against Resume**:
```bash
./job_matcher.py match
# Uses resume from data/resume.txt by default
```

With custom parameters:
```bash
./job_matcher.py match --resume "data/resume.txt" --min-score 0.7
```

3. **Optimize Resume for Job**:
```bash
./job_matcher.py optimize
# Uses data/resume.txt and data/job_descriptions/job_description.txt by default
```

With custom parameters and cover letter:
```bash
./job_matcher.py optimize --job "data/job_descriptions/senior_developer.txt" --with-cover-letter
```

4. **Process LinkedIn Jobs**:
```bash
./job_matcher.py linkedin --search-url "https://www.linkedin.com/jobs/search?keywords=python&location=canada"
# Uses resume.txt by default for matching
```

Direct job URL:
```bash
./job_matcher.py linkedin --url "https://www.linkedin.com/jobs/view/4219164109"
```

## Default Paths

- Resume: `data/resume.txt`
- Search terms: `data/search_terms.txt`
- Job description: `data/job_descriptions/job_description.txt`
- Output directory: `data/optimization_results/` for optimized resumes and cover letters

You can override any of these defaults by providing the appropriate command-line arguments.
