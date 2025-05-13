# Enhanced Job Matcher + Resume Optimizer

This feature integrates the enhanced job matching algorithm with the resume optimizer to create better tailored resumes for specific job descriptions.

## What's New

1. **Enhanced Matching Algorithm**
   - 10% more lenient matching overall
   - Better keyword detection and scoring
   - Improved title and role matching
   - Higher baseline score floors
   - More emphasis on keywords and less on TF-IDF scores

2. **Combined Search & Optimize Workflow**
   - Search for jobs on LinkedIn
   - Match against your resume with enhanced scoring
   - Generate optimized resumes for top matches
   - Analyze keyword gaps and address them

## How to Use

### Method 1: All-in-One Search and Optimize

```bash
./search_optimize.sh --search "Software Engineer" --location "Calgary"
```

**Options:**
- `--search, -s`: Job search term (default: "Software Developer")
- `--location, -l`: Job location (default: "Canada")
- `--recency, -r`: Jobs posted in the last N hours (default: 48)
- `--top-jobs`: Number of top matches to optimize for (default: 10)
- `--min-score`: Minimum match score (0.0-1.0) to consider (default: 0.3)
- `--matching-mode`: "standard", "lenient" or "very_lenient" (default: "lenient")
- `--resume`: Path to your resume (default: data/resume.txt)
- `--output-dir`: Output directory (default: data/job_matches)

### Method 2: Direct Resume Optimization with Enhanced Matching

```bash
python optimizer/enhanced_optimizer.py --job "path/to/job_description.txt" --resume "path/to/resume.txt"
```

**Options:**
- `--job, -j`: Job description file
- `--resume, -r`: Resume file
- `--prompt, -p`: Custom prompt template
- `--analyze-only`: Only analyze match without generating resume

## Output

The script produces:
1. Optimized resume in Markdown format
2. Match analysis JSON file with:
   - Match score
   - Missing keywords
   - Matching keywords
   - Resume keyword analysis

## Examples

### Basic search and optimization:
```bash
./search_optimize.sh --search "Data Engineer" --location "Toronto"
```

### Optimize for very specific roles:
```bash
./search_optimize.sh --search "Python Developer" --location "Remote" --recency 72 --min-score 0.4
```

### Just analyze a specific job description:
```bash
python optimizer/enhanced_optimizer.py --job "data/job_descriptions/senior_dev_amazon.txt" --analyze-only
```

## Tips for Better Results

1. **For the best matches:**
   - Use a detailed, keyword-rich resume with industry-standard terms
   - Include relevant technologies, frameworks, and methodologies
   - Structure your resume with clear experience and skill sections

2. **To improve match scores:**
   - Add more relevant keywords from job postings to your base resume
   - Ensure your job titles align with industry standards
   - Add a skills section that highlights technology keywords

3. **When optimizing:**
   - Review the generated resume for accuracy
   - Check the missing keywords identified in the analysis file
   - Make manual adjustments if needed for better personalization
