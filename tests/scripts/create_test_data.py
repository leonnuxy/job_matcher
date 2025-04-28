"""
Test Data Creation Utility

Creates sample resumes and job descriptions for testing the manual ATS comparison module.
Uses actual resume from project's data directory instead of dummy data.
"""

import os
from pathlib import Path
import shutil

# Define directories
PROJECT_ROOT = Path(__file__).parent.parent
TEST_DATA_DIR = Path(__file__).parent / "test_data"
DATA_DIR = PROJECT_ROOT / "data"

# Ensure test data directory exists
TEST_DATA_DIR.mkdir(parents=True, exist_ok=True)

def read_resume_file():
    """Read the actual resume file from the project's data directory"""
    resume_path = DATA_DIR / "resume.txt"
    if not resume_path.exists():
        print(f"Error: Resume file not found at {resume_path}")
        return None
    
    try:
        with open(resume_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading resume file: {e}")
        return None

def create_modified_resume(original_resume):
    """Create a slightly modified version of the original resume"""
    if not original_resume:
        return None
    
    # This is a simple modification - in a real case you might want to do more
    # sophisticated changes like adding/removing skills or experiences
    lines = original_resume.split('\n')
    modified_lines = []
    
    for line in lines:
        # Example transformation: Adding "(Modified)" to the resume title/name line
        if line.strip() and len(modified_lines) < 3:  # Assuming name is in first few lines
            if not any(keyword in line.lower() for keyword in ['email', 'phone', 'address', '@']):
                line = line + " (Modified Version)"
        modified_lines.append(line)
    
    # Add a slightly different skill set as an example
    modified_lines.append("\nADDITIONAL SKILLS (Modified Version)")
    modified_lines.append("- Advanced data visualization")
    modified_lines.append("- Project management experience")
    modified_lines.append("- Experience with agile methodologies")
    
    return '\n'.join(modified_lines)

# Sample job description text
job_description1 = """
Software Developer - Remote
TechInnovate Solutions

Job Description:
We are seeking a skilled Software Developer to join our growing team. The ideal candidate will be responsible for developing and maintaining web applications, designing database schemas, and collaborating with cross-functional teams.

Requirements:
- 3+ years of experience in software development
- Proficiency in Python and JavaScript
- Experience with web frameworks such as Django or Flask
- Strong knowledge of SQL databases (PostgreSQL preferred)
- Familiarity with AWS cloud services
- Experience with version control systems (Git)
- Excellent problem-solving abilities

Responsibilities:
- Develop and maintain web applications
- Write clean, maintainable, and efficient code
- Collaborate with front-end developers and other team members
- Troubleshoot and debug applications
- Implement security and data protection measures

Benefits:
- Competitive salary
- Remote work options
- Health insurance
- 401(k) matching
- Professional development opportunities
"""

job_description2 = """
Data Scientist - Hybrid
Data Analytics Pro

Job Description:
We are looking for a Data Scientist to help us discover insights from data and build prediction models. The ideal candidate should have a strong background in statistics, machine learning, and data manipulation.

Requirements:
- Bachelor's degree in Computer Science, Statistics, or related field
- 2+ years of experience in data science or related field
- Proficiency in Python, R, or similar programming languages
- Experience with data visualization tools (Tableau, PowerBI)
- Knowledge of SQL and database systems
- Experience with machine learning algorithms and libraries
- Strong analytical and problem-solving skills

Responsibilities:
- Analyze large datasets to identify trends and patterns
- Build and deploy machine learning models
- Create data visualizations and dashboards
- Collaborate with product and engineering teams
- Present findings to stakeholders

Benefits:
- Competitive compensation
- Flexible work schedule
- Health and dental insurance
- Continuous learning opportunities
- Modern office environment
"""

# Create test files
def create_test_file(filename, content):
    """Create a test file with the given filename and content"""
    file_path = TEST_DATA_DIR / filename
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Created file: {file_path}")

# Get actual resume content
resume_content = read_resume_file()
if resume_content:
    # Create a test file with the original resume
    create_test_file("resume_original.txt", resume_content)
    
    # Create a modified version for comparison testing
    modified_content = create_modified_resume(resume_content)
    if modified_content:
        create_test_file("resume_modified.txt", modified_content)
    
    print(f"Created resume test files from your actual resume.txt")
else:
    print("Falling back to sample resume data.")
    # Create a basic sample resume if the original couldn't be read
    sample_resume = """
    John Doe
    Software Developer
    john.doe@email.com | (123) 456-7890
    
    SKILLS
    Programming: Python, JavaScript, SQL
    Frameworks: Django, Flask, React
    Tools: Git, Docker, AWS
    
    EXPERIENCE
    Software Developer - XYZ Company
    - Built web applications with Python and JavaScript
    - Worked with SQL databases and cloud infrastructure
    """
    create_test_file("resume_sample.txt", sample_resume)

# Create job description files
create_test_file("job1.txt", job_description1)
create_test_file("job2.txt", job_description2)

# Create a copy of the original resume.txt in the test directory for convenience
try:
    shutil.copy(DATA_DIR / "resume.txt", TEST_DATA_DIR / "resume.txt")
    print(f"Copied original resume.txt to test directory")
except Exception as e:
    print(f"Could not copy original resume.txt: {e}")

print("\nTest data creation completed!")
print("\nAvailable resume files for testing:")
print("1. resume.txt - Your original resume")
print("2. resume_original.txt - Same as above (for consistent naming)")
print("3. resume_modified.txt - Slightly modified version for comparison testing")
print("\nJob description files:")
print("1. job1.txt - Software Developer position")
print("2. job2.txt - Data Scientist position")
print("\nYou can now use these files with the manual_ats_comparison.py utility.")
