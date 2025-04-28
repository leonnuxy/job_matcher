"""
ATS Comparison Tool

A consolidated tool that helps you compare your resume against job descriptions.
This lightweight implementation avoids heavy NLP dependencies while providing
robust functionality for ATS score simulation and comparison with external tools.

Features:
- Resume and job description skills extraction and matching
- Internal ATS score simulation
- Export capability for testing with external ATS tools
- Recording and comparing external ATS scores
- Generating comparison reports

Usage:
    python simple_ats_comparison.py
"""

import os
import sys
import json
import logging
import re
from pathlib import Path
from datetime import datetime
from collections import Counter

# Configure logging with file output
log_dir = Path(__file__).parent / "logs"
log_dir.mkdir(parents=True, exist_ok=True)
log_file = log_dir / f"ats_comparison_{datetime.now().strftime('%Y%m%d')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

# Define directories
TEST_DATA_DIR = Path(__file__).parent / "test_data"
RESULTS_DIR = Path(__file__).parent / "results"

# Ensure directories exist
TEST_DATA_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

def extract_skills_simple(text):
    """
    Extract potential skills from text using a predefined list of common technical skills.
    
    Args:
        text (str): The text to extract skills from (resume or job description)
        
    Returns:
        list: A list of skills found in the text
    """
    # Expand the common skills list to be more comprehensive
    common_skills = [
        # Programming Languages
        'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'ruby', 'php', 'go', 'rust',
        'swift', 'kotlin', 'scala', 'perl', 'r', 'bash', 'powershell', 'sql', 'ksh', 'shell',
        
        # Front-end
        'html', 'css', 'react', 'angular', 'vue', 'jquery', 'bootstrap', 'sass', 'less',
        'redux', 'webpack', 'babel', 'gatsby', 'next.js', 'svelte', 'ember', 'backbone',
        
        # Back-end & Frameworks
        'node', 'express', 'django', 'flask', 'spring', 'boot', 'rails', 'laravel',
        'asp.net', 'hibernate', 'symfony', '.net', '.net core', 'fastapi',
        
        # Databases
        'sql', 'mysql', 'postgresql', 'oracle', 'mongodb', 'cassandra', 'redis', 'elasticsearch',
        'dynamodb', 'sqlite', 'mariadb', 'couchdb', 'firestore', 'neo4j', 'nosql', 'cosmosdb',
        
        # DevOps & Cloud
        'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'jenkins', 'gitlab',
        'github', 'ci/cd', 'devops', 'ansible', 'puppet', 'chef', 'prometheus', 'grafana',
        'elk', 'helm', 'istio', 'vagrant', 'cloudformation', 'arm templates',
        
        # Version Control
        'git', 'svn', 'mercurial', 'bitbucket', 'github', 'gitlab', 'git flow',
        
        # Methodologies & Practices
        'agile', 'scrum', 'kanban', 'jira', 'tdd', 'bdd', 'ci/cd', 'sre', 'devops',
        'waterfall', 'lean', 'sdlc', 'rca', 'metrics',
        
        # Operating Systems
        'linux', 'windows', 'macos', 'unix', 'ubuntu', 'centos', 'rhel', 'debian',
        'fedora', 'red hat', 'suse',
        
        # API & Web Services
        'rest', 'soap', 'api', 'graphql', 'swagger', 'openapi', 'grpc', 'websocket',
        'oauth', 'jwt', 'http', 'https',
        
        # Data & ML
        'machine learning', 'ai', 'data science', 'big data', 'hadoop', 'spark',
        'pandas', 'numpy', 'scikit-learn', 'tensorflow', 'pytorch', 'keras',
        'tableau', 'power bi', 'etl', 'data mining', 'nlp', 'computer vision',
        
        # Testing
        'unit testing', 'integration testing', 'selenium', 'cypress', 'jest', 'mocha',
        'chai', 'junit', 'testng', 'pytest', 'jasmine', 'karma', 'cucumber',
        
        # Architecture
        'microservices', 'serverless', 'soa', 'event-driven', 'cqrs', 'mvc',
        'mvvm', 'restful', 'domain driven design',
        
        # Infrastructure
        'cloud', 'saas', 'paas', 'iaas', 'container', 'vm', 'virtualization',
        'server', 'load balancer', 'cdn', 'dns', 'vpc', 'subnet',
        
        # Security
        'cybersecurity', 'infosec', 'authentication', 'authorization', 'oauth',
        'encryption', 'ssl', 'tls', 'penetration testing', 'vulnerability',
        
        # Monitoring & Logging
        'monitoring', 'logging', 'splunk', 'elk', 'prometheus', 'grafana', 'datadog',
        'newrelic', 'appdynamics', 'cloudwatch', 'sentry', 'kibana', 'logstash',
        
        # Build Tools
        'maven', 'gradle', 'npm', 'yarn', 'pip', 'bundler', 'ant', 'make',
        'webpack', 'gulp', 'grunt', 'artifactory',
        
        # Mobile Development
        'android', 'ios', 'react native', 'flutter', 'xamarin', 'swift', 'kotlin',
        'objective-c',
        
        # Collaboration Tools
        'slack', 'teams', 'confluence', 'jira', 'trello', 'asana', 'notion',
        'sharepoint', 'gsuite', 'office 365'
    ]
    
    # Convert to lowercase for case-insensitive matching
    text_lower = text.lower()
    
    # Find skills in the text
    found_skills = []
    for skill in common_skills:
        # Use word boundaries to avoid partial matches
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            found_skills.append(skill)
    
    return found_skills

def calculate_similarity_simple(resume_skills, job_skills):
    """
    Calculate a similarity score between resume skills and job skills.
    
    Args:
        resume_skills (list): List of skills extracted from the resume
        job_skills (list): List of skills extracted from the job description
        
    Returns:
        float: A percentage score indicating how well the resume matches the job requirements
    """
    if not resume_skills or not job_skills:
        return 0
    
    # Convert to sets for intersection
    resume_set = set(skill.lower() for skill in resume_skills)
    job_set = set(skill.lower() for skill in job_skills)
    
    # Find matching skills
    matches = resume_set.intersection(job_set)
    
    # Calculate score as percentage of job skills matched
    score = (len(matches) / len(job_set)) * 100
    
    return round(score, 1)

def load_test_file(filename):
    """
    Load content from a test file
    
    Args:
        filename (str): Name of the file to load from the test_data directory
        
    Returns:
        str: Content of the file, or None if file not found
    """
    file_path = TEST_DATA_DIR / filename
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
        return None

def list_test_files():
    """
    List available test files in the test_data directory
    
    Returns:
        tuple: (list of resume files, list of job description files)
    """
    resumes = []
    job_descriptions = []
    
    for file_path in TEST_DATA_DIR.iterdir():
        if file_path.is_file():
            if 'resume' in file_path.name.lower():
                resumes.append(file_path.name)
            elif 'job' in file_path.name.lower():
                job_descriptions.append(file_path.name)
    
    return sorted(resumes), sorted(job_descriptions)

def calculate_internal_score(resume_text, job_description):
    """
    Calculate internal matching score using our simplified system
    
    Args:
        resume_text (str): The resume text
        job_description (str): The job description text
        
    Returns:
        dict: Dictionary containing similarity scores and extracted skills
    """
    # Extract skills
    resume_skills = extract_skills_simple(resume_text)
    job_skills = extract_skills_simple(job_description)
    
    # Calculate similarity
    similarity_score = calculate_similarity_simple(resume_skills, job_skills)
    
    # Enhanced ATS simulation score with keyword density and context
    # 60% similarity score + 30% keyword density + 10% keyword placement
    keyword_density_score = min(100, len(resume_skills) * 5)  
    
    # Simple keyword placement score - check if keywords appear in important sections
    # This is a simplified approximation
    placement_score = 0
    important_sections = ['summary', 'experience', 'skills', 'education']
    resume_lower = resume_text.lower()
    for section in important_sections:
        if section in resume_lower:
            placement_score += 25  # 25 points for each important section found
    placement_score = min(100, placement_score)  # Cap at 100
    
    # Calculate weighted score
    ats_score = (similarity_score * 0.6) + (keyword_density_score * 0.3) + (placement_score * 0.1)
    
    return {
        'similarity_score': similarity_score,
        'ats_score': round(ats_score, 1),
        'extracted_skills_from_resume': resume_skills,
        'extracted_skills_from_job': job_skills,
        'matching_skills': list(set(s.lower() for s in resume_skills).intersection(
                              set(s.lower() for s in job_skills)))
    }

def export_for_external_testing(resume_file, job_file):
    """
    Export resume and job description for testing in external ATS systems
    
    Args:
        resume_file (str): Name of the resume file
        job_file (str): Name of the job description file
        
    Returns:
        dict: Information about the export, or False if export failed
    """
    resume_text = load_test_file(resume_file)
    job_text = load_test_file(job_file)
    
    if not resume_text or not job_text:
        return False
    
    # Create export directory
    export_dir = RESULTS_DIR / "export_for_ats"
    export_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate a timestamp for the export
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Export files with clear names for external testing
    export_resume = export_dir / f"{timestamp}_{resume_file}"
    export_job = export_dir / f"{timestamp}_{job_file}"
    
    with open(export_resume, 'w', encoding='utf-8') as f:
        f.write(resume_text)
    
    with open(export_job, 'w', encoding='utf-8') as f:
        f.write(job_text)
    
    # Calculate internal score for this pair
    internal_score = calculate_internal_score(resume_text, job_text)
    
    export_info = {
        'resume_file': str(export_resume),
        'job_file': str(export_job),
        'timestamp': timestamp,
        'test_score': internal_score['ats_score'],  # Add calculated internal score
        'external_scores': None  # Initialize as null
    }
    
    # Export information as a JSON file
    with open(export_dir / f"{timestamp}_info.json", 'w', encoding='utf-8') as f:
        json.dump(export_info, f, indent=2)
    
    logging.info(f"Exported files for external ATS testing:")
    logging.info(f"Resume: {export_resume}")
    logging.info(f"Job Description: {export_job}")
    logging.info(f"Internal test score: {internal_score['ats_score']}")
    
    return export_info

def record_external_score(export_timestamp, external_ats_name, external_score):
    """
    Record an external ATS score for comparison
    
    Args:
        export_timestamp (str): The timestamp of the export
        external_ats_name (str): Name of the external ATS tool
        external_score (float): Score from the external ATS tool
        
    Returns:
        bool: True if successful, False otherwise
    """
    # Find the info file
    info_file = RESULTS_DIR / "export_for_ats" / f"{export_timestamp}_info.json"
    if not info_file.exists():
        logging.error(f"Info file not found: {info_file}")
        return False
    
    # Load export info
    with open(info_file, 'r', encoding='utf-8') as f:
        export_info = json.load(f)
    
    # Initialize external_scores properly regardless of current type
    if export_info['external_scores'] is None or not isinstance(export_info['external_scores'], dict):
        # If external_scores exists but isn't a dict (e.g., it's an int), convert it
        if export_info['external_scores'] is not None:
            # Save the old value in the new dictionary under 'Original' key
            old_value = export_info['external_scores']
            logging.info(f"Converting existing non-dictionary score ({old_value}) to dictionary format")
            export_info['external_scores'] = {'Original': old_value}
        else:
            export_info['external_scores'] = {}
    
    # Add external score information
    export_info['external_scores'][external_ats_name] = external_score
    
    # Save updated info
    with open(info_file, 'w', encoding='utf-8') as f:
        json.dump(export_info, f, indent=2)
    
    logging.info(f"Recorded external score from {external_ats_name}: {external_score}%")
    
    return True

def generate_comparison_report(export_timestamp):
    """
    Generate a report comparing internal and external scores
    
    Args:
        export_timestamp (str): The timestamp of the export
        
    Returns:
        dict: Report data, or False if report generation failed
    """
    # Find the info file
    info_file = RESULTS_DIR / "export_for_ats" / f"{export_timestamp}_info.json"
    if not info_file.exists():
        logging.error(f"Info file not found: {info_file}")
        return False
    
    # Load export info
    with open(info_file, 'r', encoding='utf-8') as f:
        export_info = json.load(f)
    
    if 'external_scores' not in export_info or not export_info['external_scores']:
        logging.error("No external scores recorded yet.")
        return False
    
    # Get the original filenames
    resume_filename = os.path.basename(export_info['resume_file']).replace(f"{export_timestamp}_", "")
    job_filename = os.path.basename(export_info['job_file']).replace(f"{export_timestamp}_", "")
    
    # Calculate internal scores
    resume_text = load_test_file(resume_filename)
    job_text = load_test_file(job_filename)
    
    if not resume_text or not job_text:
        logging.error("Could not load original test files.")
        return False
    
    internal_scores = calculate_internal_score(resume_text, job_text)
    
    # Generate report
    report = {
        'timestamp': export_info['timestamp'],
        'resume_file': resume_filename,
        'job_file': job_filename,
        'internal_scores': internal_scores,
        'external_scores': export_info['external_scores'],
        'comparisons': {}
    }
    
    # Calculate differences
    for ats_name, ext_score in export_info['external_scores'].items():
        if isinstance(ext_score, (int, float)):
            diff = internal_scores['ats_score'] - ext_score
            report['comparisons'][ats_name] = {
                'difference': diff,
                'absolute_difference': abs(diff)
            }
    
    # Save report
    reports_dir = RESULTS_DIR / "comparison_reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    report_file = reports_dir / f"{export_timestamp}_comparison.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    
    # Generate human-readable summary
    summary_file = reports_dir / f"{export_timestamp}_summary.txt"
    
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("ATS COMPARISON REPORT\n")
        f.write("====================\n\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Resume: {resume_filename}\n")
        f.write(f"Job Description: {job_filename}\n\n")
        
        f.write("INTERNAL SCORES\n")
        f.write("-------------------------\n")
        f.write(f"Similarity Score: {internal_scores['similarity_score']}%\n")
        f.write(f"ATS Simulation Score: {internal_scores['ats_score']}%\n\n")
        
        f.write("Skills Found in Resume:\n")
        for skill in internal_scores['extracted_skills_from_resume']:
            f.write(f"- {skill}\n")
        f.write("\n")
        
        f.write("Skills Required in Job:\n")
        for skill in internal_scores['extracted_skills_from_job']:
            f.write(f"- {skill}\n")
        f.write("\n")
        
        f.write("Matching Skills:\n")
        for skill in internal_scores['matching_skills']:
            f.write(f"- {skill}\n")
        f.write("\n")
        
        f.write("EXTERNAL SCORES\n")
        f.write("-------------------------\n")
        for ats_name, score in export_info['external_scores'].items():
            f.write(f"{ats_name}: {score}%\n")
        f.write("\n")
        
        f.write("COMPARISON\n")
        f.write("-------------------------\n")
        for ats_name, comp in report['comparisons'].items():
            f.write(f"Internal vs {ats_name}: {comp['difference']:+.2f}% difference\n")
        
        # Calculate average external score
        valid_scores = [score for score in export_info['external_scores'].values() 
                      if isinstance(score, (int, float))]
        
        if valid_scores:
            avg_ext_score = sum(valid_scores) / len(valid_scores)
            f.write(f"\nAverage External Score: {avg_ext_score:.2f}%\n")
            f.write(f"Internal ATS Score: {internal_scores['ats_score']:.2f}%\n")
            f.write(f"Overall Difference: {internal_scores['ats_score'] - avg_ext_score:+.2f}%\n")
            
            # Add recommendations based on the comparison
            f.write("\nRECOMMENDATIONS\n")
            f.write("-------------------------\n")
            if internal_scores['ats_score'] < avg_ext_score - 10:
                f.write("Our internal ATS score appears to be stricter than external systems.\n")
                f.write("This may provide a more conservative estimate for resume optimization.\n")
            elif internal_scores['ats_score'] > avg_ext_score + 10:
                f.write("Our internal ATS score appears to be more lenient than external systems.\n")
                f.write("Consider focusing on the specific areas identified by external ATS tools.\n")
            else:
                f.write("Our internal ATS scoring is well-aligned with external systems.\n")
                f.write("Focus on increasing your match percentage by adding missing skills.\n")
    
    logging.info(f"Comparison report generated: {report_file}")
    logging.info(f"Summary report generated: {summary_file}")
    
    return report

def run_interactive_session():
    """Run an interactive session for manual ATS comparison"""
    print("\n=== ATS Comparison Tool ===\n")
    print("This tool helps you compare internal ATS scores with external ATS systems.")
    
    while True:
        print("\nOptions:")
        print("1. List available test files")
        print("2. Export resume and job for external testing")
        print("3. Record external ATS score")
        print("4. Generate comparison report")
        print("5. Quick test (internal scoring only)")
        print("6. Exit")
        
        try:
            choice = input("\nEnter your choice (1-6): ")
            
            if choice == '1':
                resumes, jobs = list_test_files()
                print("\nAvailable Resume Files:")
                for i, r in enumerate(resumes, 1):
                    print(f"{i}. {r}")
                print("\nAvailable Job Description Files:")
                for i, j in enumerate(jobs, 1):
                    print(f"{i}. {j}")
            
            elif choice == '2':
                resumes, jobs = list_test_files()
                
                if not resumes or not jobs:
                    print("No test files available. Please add resume and job description files to the test_data directory.")
                    continue
                
                print("\nAvailable Resume Files:")
                for i, r in enumerate(resumes, 1):
                    print(f"{i}. {r}")
                
                resume_choice = int(input("\nSelect resume file number: "))
                if resume_choice < 1 or resume_choice > len(resumes):
                    print("Invalid choice.")
                    continue
                
                print("\nAvailable Job Description Files:")
                for i, j in enumerate(jobs, 1):
                    print(f"{i}. {j}")
                
                job_choice = int(input("\nSelect job description file number: "))
                if job_choice < 1 or job_choice > len(jobs):
                    print("Invalid choice.")
                    continue
                
                export_info = export_for_external_testing(resumes[resume_choice-1], jobs[job_choice-1])
                if export_info:
                    print(f"\nFiles exported for external testing. Timestamp: {export_info['timestamp']}")
                    print("Use this timestamp when recording external scores.")
                    
                    # Automatically show the internal score
                    resume_text = load_test_file(resumes[resume_choice-1])
                    job_text = load_test_file(jobs[job_choice-1])
                    internal_score = calculate_internal_score(resume_text, job_text)
                    
                    print("\n=== Internal Score Preview ===")
                    print(f"Similarity Score: {internal_score['similarity_score']}%")
                    print(f"ATS Simulation Score: {internal_score['ats_score']}%")
                    print(f"Matching Skills: {', '.join(internal_score['matching_skills'])}")
            
            elif choice == '3':
                timestamp = input("\nEnter the export timestamp: ")
                ats_name = input("Enter the name of the external ATS tool: ")
                try:
                    external_score = float(input("Enter the score from the external ATS tool (0-100): "))
                except ValueError:
                    print("Invalid score. Please enter a number between 0 and 100.")
                    continue
                
                result = record_external_score(timestamp, ats_name, external_score)
                if result:
                    print("External score recorded successfully.")
            
            elif choice == '4':
                timestamp = input("\nEnter the export timestamp for the report: ")
                report = generate_comparison_report(timestamp)
                if report:
                    print("Comparison report generated successfully.")
                    # Display path to the generated report
                    summary_file = RESULTS_DIR / "comparison_reports" / f"{timestamp}_summary.txt"
                    print(f"Summary report: {summary_file}")
            
            elif choice == '5':
                resumes, jobs = list_test_files()
                
                if not resumes or not jobs:
                    print("No test files available.")
                    continue
                
                print("\nAvailable Resume Files:")
                for i, r in enumerate(resumes, 1):
                    print(f"{i}. {r}")
                
                resume_choice = int(input("\nSelect resume file number: "))
                if resume_choice < 1 or resume_choice > len(resumes):
                    print("Invalid choice.")
                    continue
                
                print("\nAvailable Job Description Files:")
                for i, j in enumerate(jobs, 1):
                    print(f"{i}. {j}")
                
                job_choice = int(input("\nSelect job description file number: "))
                if job_choice < 1 or job_choice > len(jobs):
                    print("Invalid choice.")
                    continue
                
                resume_text = load_test_file(resumes[resume_choice-1])
                job_text = load_test_file(jobs[job_choice-1])
                
                if not resume_text or not job_text:
                    print("Error loading files.")
                    continue
                
                internal_score = calculate_internal_score(resume_text, job_text)
                
                print("\n=== Internal Score Results ===")
                print(f"Resume: {resumes[resume_choice-1]}")
                print(f"Job: {jobs[job_choice-1]}")
                print(f"Similarity Score: {internal_score['similarity_score']}%")
                print(f"ATS Simulation Score: {internal_score['ats_score']}%")
                
                print("\nSkills Found in Resume:")
                for skill in internal_score['extracted_skills_from_resume']:
                    print(f"- {skill}")
                
                print("\nSkills Required in Job:")
                for skill in internal_score['extracted_skills_from_job']:
                    print(f"- {skill}")
                
                print("\nMatching Skills:")
                for skill in internal_score['matching_skills']:
                    print(f"- {skill}")
                
                # Add recommendations
                print("\nRecommendations:")
                missing_skills = set(s.lower() for s in internal_score['extracted_skills_from_job']) - \
                                set(s.lower() for s in internal_score['matching_skills'])
                if missing_skills:
                    print("Consider adding these missing skills to your resume:")
                    for skill in missing_skills:
                        print(f"- {skill}")
                else:
                    print("Your resume includes all the required skills for this job!")
                
                if internal_score['ats_score'] < 70:
                    print("\nYour ATS score is below 70%. Consider optimizing your resume for this job.")
                else:
                    print("\nYour resume is well-matched for this job position!")
            
            elif choice == '6':
                print("\nExiting ATS Comparison Tool. Goodbye!")
                break
            
            else:
                print("Invalid choice. Please try again.")
                
        except ValueError as e:
            print(f"Invalid input: {e}")
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            print(f"An error occurred: {e}")
            print("Check the logs for more details.")

if __name__ == "__main__":
    try:
        # Show welcome message with available test files
        print("Welcome to the ATS Comparison Tool!")
        resumes, jobs = list_test_files()
        print(f"\nFound {len(resumes)} resume(s) and {len(jobs)} job description(s) in the test data directory.")
        print(f"Log file: {log_file}")
        
        run_interactive_session()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user. Exiting...")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        print(f"An unexpected error occurred: {e}")
        print(f"Check the log file: {log_file}")
