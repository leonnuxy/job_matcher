# Testing Framework - Technical Documentation

> **Note**: For testing usage and examples, see the [main project README](../README.md#testing-framework).

This document contains technical details about the testing framework architecture for developers working on tests and quality assurance.

## Framework Architecture

### Directory Structure

```
tests/
├── README.md                    # This file
├── simple_ats_comparison.py     # Lightweight ATS testing
├── test_*.py                   # Unit test files
├── data/                       # Test data and fixtures
│   ├── job_*.txt              # Sample job descriptions
│   ├── resume_*.txt           # Sample resumes
│   └── ...
├── scripts/                    # Test automation scripts
│   ├── ats_comparison.py       # Interactive ATS testing
│   ├── comprehensive_job_parser_test.py
│   ├── create_test_data.py     # Test data generation
│   ├── job_parser_*.py        # Parser testing scripts
│   └── test_*.py              # Various test utilities
└── results/                   # Generated test output
    └── logs/                  # Test execution logs
```

## Test Categories

### Unit Tests (`test_*.py`)

**Core Component Tests**
- `test_api_calls.py`: API integration testing
- `test_ats.py`: ATS simulation algorithm testing
- `test_integration.py`: End-to-end pipeline testing
- `test_job_parser.py`: Job parsing functionality
- `test_matcher.py`: Resume matching algorithms
- `test_parsers.py`: Various parser components
- `test_resume_parser.py`: Resume processing logic

**Resume Optimizer Tests**
- `test_resume_optimizer.py`: Main optimizer functionality
- `test_resume_optimizer_fix.py`: Bug fix validation
- `test_resume_optimizer_integration.py`: Integration testing

### Integration Tests (`scripts/`)

**ATS Testing Framework**
```bash
# Interactive ATS comparison tool
python scripts/ats_comparison.py

# Lightweight ATS testing
python tests/simple_ats_comparison.py
```

**Job Parser Testing Suite**
```bash
# Comprehensive parser testing
python scripts/comprehensive_job_parser_test.py

# Simple parser validation
python scripts/job_parser_simple_test.py

# Refactored parser testing
python scripts/test_job_parser_refactored.py

# Location extraction testing
python scripts/test_location_extraction.py
```

## Testing Infrastructure

### Test Data Management

**Data Generation**
```bash
python scripts/create_test_data.py
```

Generates:
- Synthetic job descriptions with various formats
- Sample resumes with different structures
- Test cases for edge scenarios

**Data Categories**
- `job_api_snippet.txt`: API response format testing
- `job_empty.txt`: Empty content handling
- `job_html.txt`: HTML parsing validation
- `job_malformed.txt`: Error handling testing
- `job_plain_text.txt`: Plain text extraction
- `resume_*.txt`: Various resume formats

### Test Execution Framework

**Automated Testing**
```bash
# Run all unit tests
python -m pytest tests/

# Run specific test categories
python -m pytest tests/test_job_parser.py -v

# Run with coverage reporting
python -m pytest tests/ --cov=lib --cov-report=html
```

**Manual Testing Scripts**
```bash
# Interactive testing
python scripts/ats_comparison.py

# Batch testing
python scripts/comprehensive_job_parser_test.py
```

## Test Result Analysis

### Output Formats

**JSON Reports**
```json
{
  "test_name": "job_parser_accuracy",
  "timestamp": "2025-05-28T10:20:00Z",
  "results": {
    "total_tests": 150,
    "passed": 142,
    "failed": 8,
    "accuracy": 0.947
  },
  "details": [...]
}
```

**CSV Exports**
- Match scores and comparisons
- Performance benchmarks
- Quality metrics over time

### Quality Metrics

**Parser Accuracy**
- Extraction precision/recall
- Keyword identification accuracy
- Location parsing success rate

**Matching Performance**
- Resume-job similarity accuracy
- ATS score correlation
- Processing speed benchmarks

**System Integration**
- End-to-end pipeline success rate
- Error recovery effectiveness
- Database consistency validation

## Test Configuration

### Environment Setup

**Test Environment Variables**
```bash
# Testing configuration
TEST_MODE=true
TEST_DATA_PATH=tests/data
TEST_RESULTS_PATH=tests/results

# API testing (optional)
GOOGLE_API_KEY_TEST=your_test_key
GEMINI_API_KEY_TEST=your_test_key
```

**Mock Configuration**
```python
# tests/conftest.py
import pytest
from unittest.mock import Mock

@pytest.fixture
def mock_api_client():
    """Mock API client for testing without real API calls"""
    return Mock()
```

### Test Data Standards

**Job Description Format**
```
Company: [Company Name]
Title: [Job Title]
Location: [Location]
Description: [Full job description]
Requirements: [Specific requirements]
```

**Resume Format**
```
Name: [Candidate Name]
Contact: [Contact Info]
Summary: [Professional summary]
Experience: [Work experience]
Skills: [Technical skills]
```

## Performance Testing

### Benchmark Standards

**Processing Speed**
- Job parsing: < 2 seconds per job
- Resume matching: < 1 second per comparison
- Database operations: < 100ms per query

**Memory Usage**
- Peak memory: < 512MB for typical workloads
- Memory leaks: None detected over 1000+ operations

**Accuracy Targets**
- Job requirement extraction: > 90% precision
- Resume matching: > 85% correlation with human evaluation
- Location extraction: > 95% accuracy

### Load Testing

```bash
# Stress test with multiple job descriptions
python scripts/load_test_parser.py --jobs=1000

# Memory profiling
python -m memory_profiler scripts/memory_test.py
```

## Continuous Integration

### Test Automation

**GitHub Actions Integration**
```yaml
# .github/workflows/test.yml
name: Test Suite
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: |
          pip install -r requirements.txt
          python -m pytest tests/ --cov=lib
```

**Pre-commit Hooks**
```bash
# Install pre-commit hooks
pre-commit install

# Run quality checks
pre-commit run --all-files
```

## Debugging and Troubleshooting

### Debug Mode

**Enable Verbose Logging**
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Run tests with detailed output
python scripts/job_parser_test.py --debug
```

**Test Isolation**
```bash
# Run single test for debugging
python -m pytest tests/test_matcher.py::test_specific_function -v -s
```

### Common Issues

**Test Data Problems**
1. Ensure test data files are UTF-8 encoded
2. Check file permissions in test directories
3. Verify mock data matches expected formats

**API Testing Issues**
1. Use test API keys for integration tests
2. Implement proper mocking for unit tests
3. Handle rate limiting in automated tests

**Performance Issues**
1. Profile memory usage during tests
2. Check for resource cleanup after tests
3. Monitor test execution time trends

## Contributing to Tests

### Adding New Tests

1. **Follow Naming Conventions**: `test_component_functionality.py`
2. **Include Documentation**: Clear docstrings and comments
3. **Use Appropriate Fixtures**: Leverage existing test data
4. **Mock External Dependencies**: Avoid real API calls in unit tests
5. **Assert Meaningful Results**: Test behavior, not implementation

### Test Quality Standards

- **Coverage**: Aim for >80% code coverage
- **Independence**: Tests should not depend on each other
- **Repeatability**: Tests should produce consistent results
- **Performance**: Tests should complete within reasonable time
- **Clarity**: Test purpose should be obvious from name and structure

For general contribution guidelines, see the [main project documentation](../README.md#contributing--future-improvements).
