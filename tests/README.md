# Job Matcher Testing Framework

This directory contains tests for the Job Matcher application. The testing framework is structured to make it easy to test different components of the application without heavyweight dependencies.

## Directory Structure

```
/tests
  /data       - Test data files (resumes, job descriptions)
  /scripts    - Test scripts
  /results    - Test results (generated JSON reports)
  /logs       - Test log files
```

## Available Tests

### ATS Comparison Tests

Tests the resume-to-job matching functionality:

```bash
python scripts/ats_comparison.py
```

This interactive tool helps you:
- Compare resumes against job descriptions
- Calculate internal ATS scores
- Export files for testing with external ATS systems
- Compare internal scores with external ATS results

### Job Parser Tests

Tests the job description and requirements extraction:

```bash
python scripts/job_parser_simple_test.py
```

This script tests:
- Extraction of job descriptions from various sources (API snippets, HTML, plain text)
- Identification of job requirements
- Quality evaluation of extracted requirements

## Test Data Generation

To generate test data for your tests:

```bash
python scripts/create_test_data.py
```

This will create sample resumes and job descriptions in the `data` directory.

## Results

Test results are stored in the `results` directory in JSON format. Results include:
- Extracted job descriptions and requirements
- Match scores
- Quality evaluations

## Logs

Detailed logs are written to the `logs` directory for debugging and analysis.

## Adding New Tests

Place new test scripts in the `scripts` directory and ensure they follow these guidelines:
- Use the standard directory structure (TEST_ROOT/data, TEST_ROOT/results, etc.)
- Include appropriate logging
- Generate clear, informative reports
