"""
Job Parser Test Module

This module provides comprehensive testing functionality for job parsing features:
- Extract job descriptions from various sources (API snippets, HTML, plain text)
- Identify key requirements from job descriptions
- Validate parsing accuracy against sample data
- Test edge cases like empty or malformed job descriptions

Usage:
    python job_parser_test.py
"""

import os
import sys
import json
import logging
from pathlib import Path
import re
from datetime import datetime

# Add project root to path for imports
TESTS_ROOT = Path(__file__).parent.parent
PROJECT_ROOT = TESTS_ROOT.parent
sys.path.append(str(PROJECT_ROOT))

# Import job parser module
from lib import job_parser

# Configure logging
log_dir = TESTS_ROOT / "logs"
log_dir.mkdir(parents=True, exist_ok=True)
log_file = log_dir / f"job_parser_test_{datetime.now().strftime('%Y%m%d')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

# Define directories
TEST_DATA_DIR = TESTS_ROOT / "data"
RESULTS_DIR = TESTS_ROOT / "results"

# Ensure directories exist
TEST_DATA_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
(RESULTS_DIR / "job_parser").mkdir(parents=True, exist_ok=True)

def load_test_file(filename):
    """Load content from a test file"""
    file_path = TEST_DATA_DIR / filename
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
        return None

def save_result(result_data, test_name):
    """Save test results to a JSON file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_file = RESULTS_DIR / "job_parser" / f"{test_name}_{timestamp}.json"
    
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(result_data, f, indent=2)
    
    logging.info(f"Results saved to {result_file}")
    return result_file

def generate_sample_job_descriptions():
    """Generate sample job descriptions for testing if they don't exist"""
    job_samples = {
        "job_api_snippet.txt": """
Software Engineer - Python
ABC Tech Solutions

We are looking for a Software Engineer with strong Python skills to join our team.
Requirements include 3+ years experience with Python, Django, and SQL. Knowledge of AWS services is a plus.
You will be responsible for developing and maintaining web applications, APIs, and backend services.
        """,
        
        "job_html.txt": """
<div class="job-description">
    <h2>Full Stack Developer</h2>
    <p>XYZ Corporation is seeking a talented Full Stack Developer to join our team.</p>
    <h3>Requirements:</h3>
    <ul>
        <li>5+ years of experience with JavaScript, React, and Node.js</li>
        <li>Experience with database design and SQL/NoSQL databases</li>
        <li>Knowledge of cloud platforms (AWS, Azure, or GCP)</li>
        <li>Strong problem-solving skills and attention to detail</li>
    </ul>
    <h3>Responsibilities:</h3>
    <ul>
        <li>Design and develop user-facing features</li>
        <li>Build reusable code and libraries for future use</li>
        <li>Optimize applications for maximum speed and scalability</li>
    </ul>
</div>
        """,
        
        "job_plain_text.txt": """
Data Scientist
Data Analytics Inc.

Job Description:
We're looking for a Data Scientist to help us extract insights from our data.

Required Skills:
- Master's degree in Computer Science, Statistics, or related field
- Experience with Python, R, and SQL
- Knowledge of machine learning algorithms
- Experience with data visualization tools
- Strong analytical and problem-solving skills

Responsibilities:
- Develop and implement machine learning models
- Analyze large datasets to identify patterns and trends
- Create visualizations and reports for stakeholders
- Collaborate with cross-functional teams
        """,
        
        "job_empty.txt": "",
        
        "job_malformed.txt": """
Data *&^% Science ##@!
Requirements: ????? Maybe Python
Responsibilities: Something something data
        """
    }
    
    for filename, content in job_samples.items():
        file_path = TEST_DATA_DIR / filename
        if not file_path.exists():
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logging.info(f"Created sample job description: {filename}")
    
    logging.info("Sample job descriptions generated")

def test_extract_job_description():
    """Test job description extraction functionality"""
    test_files = ["job_api_snippet.txt", "job_html.txt", "job_plain_text.txt", "job_empty.txt", "job_malformed.txt"]
    results = {}
    
    for test_file in test_files:
        content = load_test_file(test_file)
        if content is None:
            continue
            
        logging.info(f"Testing job description extraction for {test_file}")
        extracted_description = job_parser.extract_job_description(content)
        
        results[test_file] = {
            "original_length": len(content),
            "extracted_length": len(extracted_description) if extracted_description else 0,
            "extracted_description": extracted_description,
            "success": extracted_description is not None and len(extracted_description) > 0
        }
    
    # Save results
    result_file = save_result(results, "description_extraction")
    
    # Log summary
    success_count = sum(1 for result in results.values() if result["success"])
    logging.info(f"Extraction test completed: {success_count}/{len(results)} successful")
    
    return results

def test_extract_job_requirements():
    """Test job requirements extraction functionality"""
    test_files = ["job_api_snippet.txt", "job_html.txt", "job_plain_text.txt", "job_malformed.txt"]
    results = {}
    
    for test_file in test_files:
        content = load_test_file(test_file)
        if content is None:
            continue
            
        logging.info(f"Testing job requirements extraction for {test_file}")
        
        # First extract description, then requirements
        description = job_parser.extract_job_description(content)
        requirements = job_parser.extract_job_requirements(description)
        
        results[test_file] = {
            "description_length": len(description) if description else 0,
            "requirements_count": len(requirements) if requirements else 0,
            "requirements": requirements,
            "success": requirements is not None and len(requirements) > 0
        }
    
    # Save results
    result_file = save_result(results, "requirements_extraction")
    
    # Log summary
    success_count = sum(1 for result in results.values() if result["success"])
    logging.info(f"Requirements extraction test completed: {success_count}/{len(results)} successful")
    
    return results

def evaluate_requirements_quality(requirements, job_type):
    """
    Evaluate the quality of extracted requirements based on job type
    
    This is a simple heuristic to check if key skills for different job types are identified
    """
    job_type_keywords = {
        "software_engineer": ["python", "django", "sql", "aws"],
        "full_stack": ["javascript", "react", "node", "database"],
        "data_scientist": ["python", "r", "sql", "machine learning", "statistics"]
    }
    
    if job_type not in job_type_keywords:
        return {"score": 0, "reason": "Unknown job type"}
    
    keywords = job_type_keywords[job_type]
    found_keywords = []
    
    for keyword in keywords:
        for requirement in requirements:
            if keyword.lower() in requirement.lower():
                found_keywords.append(keyword)
                break
    
    score = len(found_keywords) / len(keywords) * 100
    
    return {
        "score": score,
        "found_keywords": found_keywords,
        "missing_keywords": list(set(keywords) - set(found_keywords)),
        "total_keywords": len(keywords),
        "found_count": len(found_keywords)
    }

def test_requirements_quality():
    """Test the quality of extracted requirements against expected skills"""
    test_cases = [
        {"file": "job_api_snippet.txt", "job_type": "software_engineer"},
        {"file": "job_html.txt", "job_type": "full_stack"},
        {"file": "job_plain_text.txt", "job_type": "data_scientist"}
    ]
    
    results = {}
    
    for case in test_cases:
        content = load_test_file(case["file"])
        if content is None:
            continue
            
        logging.info(f"Testing requirements quality for {case['file']}")
        
        # Extract description and requirements
        description = job_parser.extract_job_description(content)
        requirements = job_parser.extract_job_requirements(description)
        
        # Evaluate quality
        quality = evaluate_requirements_quality(requirements, case["job_type"])
        
        results[case["file"]] = {
            "job_type": case["job_type"],
            "requirements": requirements,
            "quality_evaluation": quality,
            "success": quality["score"] >= 50  # Arbitrary threshold for demonstration
        }
    
    # Save results
    result_file = save_result(results, "requirements_quality")
    
    # Log summary
    success_count = sum(1 for result in results.values() if result["success"])
    logging.info(f"Requirements quality test completed: {success_count}/{len(results)} meet quality threshold")
    
    return results

def run_all_tests():
    """Run all job parser tests"""
    logging.info("Starting job parser tests...")
    
    # Generate sample data if needed
    generate_sample_job_descriptions()
    
    # Run tests
    extraction_results = test_extract_job_description()
    requirements_results = test_extract_job_requirements()
    quality_results = test_requirements_quality()
    
    # Aggregate results
    overall_results = {
        "timestamp": datetime.now().isoformat(),
        "tests_run": 3,
        "description_extraction": {
            "success_rate": f"{sum(1 for r in extraction_results.values() if r['success'])}/{len(extraction_results)}"
        },
        "requirements_extraction": {
            "success_rate": f"{sum(1 for r in requirements_results.values() if r['success'])}/{len(requirements_results)}"
        },
        "requirements_quality": {
            "success_rate": f"{sum(1 for r in quality_results.values() if r['success'])}/{len(quality_results)}"
        }
    }
    
    # Save overall results
    save_result(overall_results, "overall_summary")
    
    logging.info("Job parser tests completed")
    return overall_results

def print_test_report(results):
    """Print a human-readable test report"""
    print("\n===== JOB PARSER TEST REPORT =====")
    print(f"Tests Run: {results['tests_run']}")
    print(f"Description Extraction Success: {results['description_extraction']['success_rate']}")
    print(f"Requirements Extraction Success: {results['requirements_extraction']['success_rate']}")
    print(f"Requirements Quality Success: {results['requirements_quality']['success_rate']}")
    print("==================================\n")

if __name__ == "__main__":
    try:
        print("Running Job Parser Tests...")
        results = run_all_tests()
        print_test_report(results)
    except KeyboardInterrupt:
        print("\nTests cancelled by user")
    except Exception as e:
        logging.error(f"An error occurred during testing: {e}")
        print(f"An error occurred: {e}")
        print(f"Check the log file: {log_file}")
