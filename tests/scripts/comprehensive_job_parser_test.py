"""
Enhanced Job Parser Comprehensive Test

This script performs thorough testing of the enhanced job parser by:
1. Testing extraction from various job posting formats (HTML, plain text, etc.)
2. Testing with job postings in different languages
3. Testing with job postings from different industries
4. Testing with short job snippets vs. full descriptions
5. Comparing results with the original parser

Usage: python comprehensive_job_parser_test.py
"""

import os
import sys
import logging
import json
import re
from pathlib import Path
from datetime import datetime
import pandas as pd
from bs4 import BeautifulSoup

# Add project root to path for imports
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
sys.path.append(str(PROJECT_ROOT))

# Import both job parser versions for comparison
from lib import job_parser, job_parser_enhanced

# Configure logging
LOG_DIR = SCRIPT_DIR.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / f"job_parser_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

# Test data directory
TEST_DATA_DIR = SCRIPT_DIR.parent / "data"
RESULTS_DIR = SCRIPT_DIR.parent / "results" / "job_parser"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# Define different test categories
TEST_CATEGORIES = {
    "html": "Job postings in HTML format",
    "plain_text": "Job postings in plain text format",
    "snippets": "Short job snippets rather than full descriptions",
    "full_descriptions": "Complete job descriptions with multiple sections",
    "non_english": "Job postings in languages other than English",
    "tech_jobs": "Job postings in the technology sector",
    "finance_jobs": "Job postings in the finance sector",
    "remote_jobs": "Remote job postings",
    "onsite_jobs": "On-site job postings with specific locations",
}

# Sample job postings for each category
def prepare_test_data():
    """Collect test data from existing files and create additional test cases"""
    test_data = {}
    
    # Load existing test data
    for file in TEST_DATA_DIR.glob("job*.txt"):
        with open(file, "r", encoding="utf-8") as f:
            content = f.read()
            
        category = "plain_text"
        if "<html" in content.lower() or "<body" in content.lower():
            category = "html"
        elif len(content.split()) < 50:
            category = "snippets"
        elif "remote" in content.lower():
            category = "remote_jobs"
        
        if category not in test_data:
            test_data[category] = []
        
        test_data[category].append({
            "name": file.stem,
            "content": content,
            "source": str(file)
        })
    
    # Load data from job search results
    results_dir = PROJECT_ROOT / "results"
    json_files = list(results_dir.glob("job_search_*.json"))
    
    if json_files:
        # Use the most recent file
        latest_file = max(json_files, key=os.path.getmtime)
        with open(latest_file, "r", encoding="utf-8") as f:
            job_data = json.load(f)
        
        # Extract job descriptions from search results
        job_count = 0
        for search_term, jobs in job_data.items():
            for job in jobs:
                job_count += 1
                if job_count > 50:  # Limit to avoid processing too many jobs
                    break
                    
                job_desc = job.get("job_description", "")
                job_title = job.get("title", f"Unknown Job {job_count}")
                
                if not job_desc:
                    continue
                    
                # Categorize based on content
                category = "full_descriptions"
                if len(job_desc.split()) < 50:
                    category = "snippets"
                elif "remote" in job_desc.lower() or "work from home" in job_desc.lower():
                    category = "remote_jobs"
                elif any(tech in job_desc.lower() for tech in ["software", "developer", "engineer", "python", "java"]):
                    category = "tech_jobs"
                elif any(fin in job_desc.lower() for fin in ["finance", "banking", "accountant", "financial"]):
                    category = "finance_jobs"
                elif any(lang in job_desc.lower() for lang in ["français", "español", "deutsche"]):
                    category = "non_english"
                    
                if category not in test_data:
                    test_data[category] = []
                    
                test_data[category].append({
                    "name": re.sub(r'[^a-zA-Z0-9]', '_', job_title)[:30],
                    "content": job_desc,
                    "source": "search_results"
                })
    
    # Add some synthetic test cases if needed categories are empty
    if "non_english" not in test_data or not test_data["non_english"]:
        test_data["non_english"] = [{
            "name": "french_job_posting",
            "content": """
            Développeur Full Stack - Montréal, QC
            
            Description du poste:
            Nous recherchons un développeur full stack passionné pour rejoindre notre équipe à Montréal.
            
            Responsabilités:
            - Développer des fonctionnalités front-end et back-end
            - Collaborer avec l'équipe de design
            - Participer aux revues de code
            
            Compétences requises:
            - JavaScript, TypeScript, React
            - Node.js, Express
            - MongoDB ou PostgreSQL
            - 3+ ans d'expérience
            
            Lieu: Montréal, Québec (hybride)
            """,
            "source": "synthetic"
        }]
    
    if "onsite_jobs" not in test_data or not test_data["onsite_jobs"]:
        test_data["onsite_jobs"] = [{
            "name": "onsite_calgary_job",
            "content": """
            Software Developer - Calgary Office
            
            About the role:
            We're looking for a skilled developer to join our downtown Calgary office.
            
            What you'll do:
            - Build web applications using modern frameworks
            - Implement new features based on user feedback
            - Work closely with our product team
            
            Requirements:
            - Strong JavaScript skills
            - Experience with React and Node.js
            - Bachelor's degree in Computer Science or related field
            - 2+ years of professional development experience
            
            Location: 333 5th Avenue SW, Calgary, Alberta
            
            This is an on-site position at our newly renovated Calgary office.
            """,
            "source": "synthetic"
        }]
    
    return test_data

def run_extraction_tests(test_data):
    """Run extraction tests on all test data and compare results between parsers"""
    results = []
    
    for category, jobs in test_data.items():
        logging.info(f"Testing category: {category} - {TEST_CATEGORIES.get(category, '')}")
        
        for job in jobs:
            job_name = job["name"]
            job_content = job["content"]
            job_source = job["source"]
            
            logging.info(f"  Processing job: {job_name}")
            
            # Run original parser
            orig_start = datetime.now()
            orig_desc = job_parser.extract_job_description(job_content)
            orig_reqs = job_parser.extract_job_requirements(job_content)
            orig_loc = job_parser.extract_job_location(job_content)
            orig_time = (datetime.now() - orig_start).total_seconds()
            
            # Run enhanced parser
            enhanced_start = datetime.now()
            enh_desc = job_parser_enhanced.extract_job_description(job_content)
            enh_reqs = job_parser_enhanced.extract_job_requirements(job_content)
            enh_loc = job_parser_enhanced.extract_job_location(job_content)
            enhanced_time = (datetime.now() - enhanced_start).total_seconds()
            
            # Calculate metrics
            desc_diff = abs(len(orig_desc) - len(enh_desc))
            desc_improvement = "N/A" if not orig_desc else "Better" if len(enh_desc) > len(orig_desc) else "Same" if len(enh_desc) == len(orig_desc) else "Worse"
            
            reqs_diff = len(set(enh_reqs) - set(orig_reqs))
            reqs_improvement = "Better" if reqs_diff > 0 else "Same" if reqs_diff == 0 else "Worse"
            
            loc_match = orig_loc == enh_loc
            loc_improvement = "Same" if loc_match else "Different"
            
            # Create result entry
            result = {
                "category": category,
                "job_name": job_name,
                "source": job_source,
                "original_description_length": len(orig_desc) if orig_desc else 0,
                "enhanced_description_length": len(enh_desc) if enh_desc else 0,
                "description_diff": desc_diff,
                "description_improvement": desc_improvement,
                "original_requirements_count": len(orig_reqs),
                "enhanced_requirements_count": len(enh_reqs),
                "requirements_diff": reqs_diff,
                "requirements_improvement": reqs_improvement,
                "original_location": orig_loc,
                "enhanced_location": enh_loc,
                "location_match": loc_match,
                "location_improvement": loc_improvement,
                "original_time_seconds": orig_time,
                "enhanced_time_seconds": enhanced_time,
                "performance_ratio": enhanced_time / orig_time if orig_time > 0 else "N/A"
            }
            
            results.append(result)
            
            # Log detailed comparison
            logging.info(f"    Description: {result['description_improvement']} " +
                       f"({result['original_description_length']} vs {result['enhanced_description_length']} chars)")
            logging.info(f"    Requirements: {result['requirements_improvement']} " +
                       f"({result['original_requirements_count']} vs {result['enhanced_requirements_count']} items)")
            logging.info(f"    Location: {result['location_improvement']} " +
                       f"(Original: {result['original_location']}, Enhanced: {result['enhanced_location']})")
            logging.info(f"    Processing time: {result['original_time_seconds']:.4f}s vs {result['enhanced_time_seconds']:.4f}s")
    
    return results

def generate_report(results):
    """Generate a comprehensive comparison report"""
    # Convert results to DataFrame for easier analysis
    df = pd.DataFrame(results)
    
    # Save raw results to CSV
    csv_file = RESULTS_DIR / f"job_parser_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    df.to_csv(csv_file, index=False)
    
    # Generate HTML report
    html_report = """
    <html>
    <head>
        <title>Job Parser Comparison Report</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            h1, h2 { color: #333; }
            table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
            tr:nth-child(even) { background-color: #f9f9f9; }
            .better { color: green; }
            .worse { color: red; }
            .same { color: orange; }
            .summary { margin: 20px 0; padding: 10px; background: #f5f5f5; border-radius: 5px; }
        </style>
    </head>
    <body>
        <h1>Job Parser Comparison Report</h1>
        <p>Generated on: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>
        
        <div class="summary">
            <h2>Summary</h2>
    """
    
    # Add summary statistics
    total_jobs = len(df)
    html_report += f"<p>Total jobs processed: {total_jobs}</p>"
    
    # Description stats
    desc_better = df[df['description_improvement'] == 'Better'].shape[0]
    desc_same = df[df['description_improvement'] == 'Same'].shape[0]
    desc_worse = df[df['description_improvement'] == 'Worse'].shape[0]
    
    html_report += f"""
        <h3>Description Extraction</h3>
        <p>Better: <span class="better">{desc_better} ({desc_better/total_jobs*100:.1f}%)</span></p>
        <p>Same: <span class="same">{desc_same} ({desc_same/total_jobs*100:.1f}%)</span></p>
        <p>Worse: <span class="worse">{desc_worse} ({desc_worse/total_jobs*100:.1f}%)</span></p>
    """
    
    # Requirements stats
    reqs_better = df[df['requirements_improvement'] == 'Better'].shape[0]
    reqs_same = df[df['requirements_improvement'] == 'Same'].shape[0]
    reqs_worse = df[df['requirements_improvement'] == 'Worse'].shape[0]
    
    html_report += f"""
        <h3>Requirements Extraction</h3>
        <p>Better: <span class="better">{reqs_better} ({reqs_better/total_jobs*100:.1f}%)</span></p>
        <p>Same: <span class="same">{reqs_same} ({reqs_same/total_jobs*100:.1f}%)</span></p>
        <p>Worse: <span class="worse">{reqs_worse} ({reqs_worse/total_jobs*100:.1f}%)</span></p>
    """
    
    # Location stats
    loc_match = df[df['location_match'] == True].shape[0]
    loc_diff = df[df['location_match'] == False].shape[0]
    
    html_report += f"""
        <h3>Location Extraction</h3>
        <p>Matching: {loc_match} ({loc_match/total_jobs*100:.1f}%)</p>
        <p>Different: {loc_diff} ({loc_diff/total_jobs*100:.1f}%)</p>
    """
    
    # Performance stats
    avg_perf = df['performance_ratio'].mean() if all(isinstance(x, (int, float)) for x in df['performance_ratio']) else "N/A"
    
    html_report += f"""
        <h3>Performance</h3>
        <p>Average processing time ratio (Enhanced/Original): {avg_perf:.2f}x</p>
        </div>
    """
    
    # Add detailed results by category
    html_report += "<h2>Results by Category</h2>"
    
    for category in df['category'].unique():
        category_df = df[df['category'] == category]
        html_report += f"<h3>{category} ({TEST_CATEGORIES.get(category, 'Unknown category')})</h3>"
        html_report += f"<p>Total jobs in category: {len(category_df)}</p>"
        
        # Create a table for this category
        html_report += """
        <table>
            <tr>
                <th>Job Name</th>
                <th>Description</th>
                <th>Requirements</th>
                <th>Location</th>
                <th>Performance</th>
            </tr>
        """
        
        for _, row in category_df.iterrows():
            html_report += f"""
            <tr>
                <td>{row['job_name']}</td>
                <td class="{row['description_improvement'].lower()}">
                    {row['description_improvement']} 
                    ({row['original_description_length']} vs {row['enhanced_description_length']} chars)
                </td>
                <td class="{row['requirements_improvement'].lower()}">
                    {row['requirements_improvement']}
                    ({row['original_requirements_count']} vs {row['enhanced_requirements_count']} items)
                </td>
                <td>
                    {'Same' if row['location_match'] else 'Different'}<br>
                    Orig: {row['original_location']}<br>
                    New: {row['enhanced_location']}
                </td>
                <td>
                    {row['original_time_seconds']:.3f}s vs {row['enhanced_time_seconds']:.3f}s<br>
                    Ratio: {row['performance_ratio']:.2f}x
                </td>
            </tr>
            """
        
        html_report += "</table>"
    
    html_report += """
        </body>
        </html>
    """
    
    # Save HTML report
    html_file = RESULTS_DIR / f"job_parser_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_report)
    
    return csv_file, html_file

def main():
    logging.info("Starting comprehensive job parser test")
    
    # Prepare test data
    logging.info("Preparing test data...")
    test_data = prepare_test_data()
    
    # Log test data summary
    for category, jobs in test_data.items():
        logging.info(f"  {category}: {len(jobs)} jobs")
    
    # Run tests
    logging.info("Running extraction tests...")
    results = run_extraction_tests(test_data)
    
    # Generate report
    logging.info("Generating comparison report...")
    csv_file, html_file = generate_report(results)
    
    logging.info(f"Test completed. Results saved to:")
    logging.info(f"  CSV: {csv_file}")
    logging.info(f"  HTML: {html_file}")
    logging.info(f"  Log: {LOG_FILE}")
    
    print(f"\nTest completed successfully!")
    print(f"CSV report: {csv_file}")
    print(f"HTML report: {html_file}")
    print(f"Log file: {LOG_FILE}")

if __name__ == "__main__":
    main()
