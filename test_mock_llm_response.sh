#!/bin/bash
# Mock LLM output to test the cover letter sanitization without API keys

# Generate a mock LLM response
cat > /tmp/mock_llm_response.txt << EOF
---BEGIN_RESUME---
# NOEL UGWOKE
Calgary, Alberta | 306-490-2929 | 1leonnoel1@gmail.com | [LinkedIn](https://www.linkedin.com/in/noelugwoke/) | [Portfolio](https://noelugwoke.com/)

## TECHNICAL SKILLS
- **Languages & Frameworks:** Python, TypeScript/Node.js, SQL, Java, JavaScript, C++, C#
- **Data & Analytics:** Apache Spark, Kafka, AWS S3/EMR, dbt, Snowflake/Redshift, Glue Catalog, Pandas
- **Cloud & DevOps:** Docker, Kubernetes, GitHub Actions, Jenkins, Terraform, Serverless (AWS-Lambda)
- **Testing & Quality:** PyTest, Jest, Data-quality checks, CI pipelines, Code reviews
- **Processes:** Agile/Scrum, Test‑Driven Development, Design patterns, Continuous Delivery
- **Machine Learning:** TensorFlow, PyTorch, Scikit-learn, MLOps, Feature Engineering

## PROFESSIONAL EXPERIENCE

**Software Engineer (Cloud & Data)**
APEGA | Calgary, AB | Dec 2022 – Dec 2024
* Developed and deployed scalable, containerized AI/ML applications on AWS using Kubernetes, leveraging Python, TensorFlow, and PyTorch.
* Authored complex SQL transformations and materialised views powering dashboards used by 30K+ users.
* Automated nightly pipeline tests with PyTest & GitHub Actions; defect rate ► < 0.5%.
* Led peer code reviews and sprint retros; mentored two juniors on SQL optimisation.
* Built GitHub Actions workflow that unit tested, and auto published Lambda artefacts; deploy time ▼ 35%.

**Tools Used:** Python, SQL, PyTorch, Kubernetes, AWS, MLOps, Docker, Git, Agile/Scrum

**Software Developer – WebApps (DevOps)**
Spartan Controls | Calgary, AB | Jul 2021 – Nov 2022
* Developed React applications for IoT dashboards, optimizing load times and user interface responsiveness, which led to a 40% increase in user engagement.
* Utilized Java to develop RESTful APIs for user authentication, data retrieval, and real-time notifications, enhancing functionality and scalability.
* Implemented serverless functions using AWS Lambda to handle specific backend tasks efficiently.
* Built CI/CD pipelines using Jenkins for automated testing and deployment utilizing Docker and Kubernetes.

**Tools Used:** Java, JavaScript, RESTful APIs, React, AWS Lambda, Jenkins, Docker, Kubernetes

## KEY PROJECT
**AI Resume Optimizer** | Personal Project | 2023
* Designed a Python/MySQL application to analyze resumes against job descriptions, improving alignment for 100+ test users.
**[Python, MySQL, NLP, Ollama, Mistral]**

## EDUCATION & CERTIFICATIONS
* **BSc. Computer Science**, University of Calgary | 2016–2022
* **AWS Certified Cloud Practitioner**, Amazon Web Services | Jan 2023
* **Google Cloud Professional Developer**, Google Cloud | 2023–2026
---END_RESUME---

---BEGIN_COVER_LETTER---
Noel Ugwoke
[Your Address]
[City, State, Zip]
[Your Email]
[Your Phone Number]
[Date]

Hiring Manager
[Company Name]
[Company Address]
[City, State, Zip]

Dear Hiring Manager,

I am writing to express my interest in the [Job Title] position at [Company Name] as advertised on [Platform where you saw the ad]. With my background in software development and machine learning, I am excited about the opportunity to contribute to your team.

In my current role at APEGA, I have developed and deployed scalable, containerized AI/ML applications on AWS using Kubernetes, leveraging Python, TensorFlow, and PyTorch. This experience aligns perfectly with the requirements outlined in your job description. Additionally, I have created robust data pipelines and implemented MLOps practices to ensure reliable and scalable machine learning solutions.

I am particularly drawn to [Company Name]'s work in [Mention a specific area of the company's work if known, otherwise, mention something positive like "cutting-edge technology" or "impactful projects"]. My experience in developing AI-powered applications and my passion for solving complex problems make me confident in my ability to make significant contributions to your team.

Thank you for considering my application. I would welcome the opportunity to discuss how my skills and experience align with your needs for the [Job Title] role. I look forward to hearing from you soon.

Sincerely,
Noel Ugwoke
---END_COVER_LETTER---
EOF

# Create a temporary script to test our sanitization logic on the mock response
cat > /tmp/test_mock_llm_processing.py << EOF
#!/usr/bin/env python3
import os
import sys
import re
import datetime

# Add parent directory to sys.path for imports
parent_dir = os.path.dirname(os.path.abspath(__file__))
if parent_dir not in sys.path:
    sys.path.append("/Users/noel/Documents/Projects-Local/job_matcher")

from services.utils import extract_text_between_delimiters
from services.cover_letter import sanitize_cover_letter

# Mock job info
job_info = {
    "title": "Machine Learning Engineer",
    "company": "Innovative Systems",
    "location": "Remote"
}

# Read the mock LLM response
with open("/tmp/mock_llm_response.txt", "r") as f:
    full_llm_response = f.read()

# Extract resume and cover letter
resume_md = extract_text_between_delimiters(full_llm_response, "---BEGIN_RESUME---", "---END_RESUME---")
cover_letter_md = extract_text_between_delimiters(full_llm_response, "---BEGIN_COVER_LETTER---", "---END_COVER_LETTER---")

# Process the cover letter to replace placeholders
if cover_letter_md and job_info:
    # Replace common placeholders in the cover letter
    company_name = job_info.get('company', 'the company')
    job_title = job_info.get('title', 'the position')
    
    # Replace company name placeholders
    cover_letter_md = re.sub(r'\[Company Name\]', company_name, cover_letter_md, flags=re.IGNORECASE)
    cover_letter_md = re.sub(r'\[company\]', company_name, cover_letter_md, flags=re.IGNORECASE)
    
    # Replace job title placeholders
    cover_letter_md = re.sub(r'\[Job Title\]', job_title, cover_letter_md, flags=re.IGNORECASE)
    cover_letter_md = re.sub(r'\[position\]', job_title, cover_letter_md, flags=re.IGNORECASE)
    
    # Replace date placeholders with current date
    today = datetime.datetime.now().strftime('%B %d, %Y')
    cover_letter_md = re.sub(r'\[Current Date\]', today, cover_letter_md, flags=re.IGNORECASE)
    cover_letter_md = re.sub(r'\[Date\]', today, cover_letter_md, flags=re.IGNORECASE)
    
    # Replace platform/source placeholders with LinkedIn
    cover_letter_md = re.sub(r'\[Platform where you saw the.*?\]', 'LinkedIn job board', cover_letter_md, flags=re.IGNORECASE)
    cover_letter_md = re.sub(r'\[.*?job board.*?\]', 'LinkedIn job board', cover_letter_md, flags=re.IGNORECASE)
    cover_letter_md = re.sub(r'\[.*?job posting.*?\]', 'LinkedIn job board', cover_letter_md, flags=re.IGNORECASE)
    
    # Replace location placeholders
    company_location = job_info.get('location', 'Remote')
    cover_letter_md = re.sub(r'\[Company Location.*?\]', company_location, cover_letter_md, flags=re.IGNORECASE)
    
    # Handle specific company work area placeholders
    cover_letter_md = re.sub(r'\[mention a specific area of the company\'s work.*?\]', 
                            'developing innovative solutions', cover_letter_md, flags=re.IGNORECASE)
    cover_letter_md = re.sub(r'\[.*?specific area of.*?work.*?\]',
                            'developing cutting-edge technology', cover_letter_md, flags=re.IGNORECASE)
    
    # Handle other common placeholders
    cover_letter_md = re.sub(r'\[mention a positive aspect of the company.*?\]', 
                            'delivering innovative solutions', cover_letter_md, flags=re.IGNORECASE)
    cover_letter_md = re.sub(r'\[.*?positive aspect.*?\]', 
                            'innovation and technical excellence', cover_letter_md, flags=re.IGNORECASE)
    
    # Further sanitize the cover letter with our additional cleaning function
    cover_letter_md = sanitize_cover_letter(cover_letter_md)
                        
# Print the results
print("===== OPTIMIZED RESUME =====")
print(resume_md if resume_md else "No resume found in LLM response")
print("\n===== COVER LETTER =====")
print(cover_letter_md if cover_letter_md else "No cover letter found in LLM response")

# Check if any placeholders remain in the cover letter
if cover_letter_md:
    remaining = re.findall(r'\[.*?\]', cover_letter_md)
    if remaining:
        print(f"\nWARNING: {len(remaining)} placeholders remain after sanitization:")
        for p in remaining:
            print(f"  - {p}")
    else:
        print("\nSUCCESS: All placeholders successfully replaced!")
EOF

# Make the script executable
chmod +x /tmp/test_mock_llm_processing.py

# Run the test
python3 /tmp/test_mock_llm_processing.py

# Clean up
echo "Test files saved to /tmp/mock_llm_response.txt and /tmp/test_mock_llm_processing.py"
