#!/usr/bin/env python
"""
Test script for Google CSE job search and HTML fallback.
"""
import os
import json
from typing import Dict, List
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import services
from services.google_cse import search_google_for_jobs
from services.html_fallback import extract_job_details
from services.scraper import generate_simulated_jobs, ensure_job_descriptions

def analyze_description(desc: str) -> Dict:
    """Analyze a job description for quality metrics."""
    if not desc:
        return {
            "length": 0,
            "sentences": 0,
            "has_description": False,
            "desc_length_ok": False,
            "has_two_sentences": False,
            "passes_all": False
        }
    
    # Count periods as a simple way to estimate sentences
    # This is not perfect but works for our test case
    sentences = desc.count('.')
    
    # Quality checks
    has_description = bool(desc)
    desc_length_ok = len(desc) >= 100
    has_two_sentences = sentences >= 2
    passes_all = all([has_description, desc_length_ok, has_two_sentences])
    
    return {
        "length": len(desc),
        "sentences": sentences,
        "has_description": has_description,
        "desc_length_ok": desc_length_ok,
        "has_two_sentences": has_two_sentences,
        "passes_all": passes_all
    }

def mock_google_cse_results():
    """Create mock CSE results for testing when API rate limiting occurs."""
    return [
        {
            "title": "Python Developer",
            "company": "TechCalgary",
            "location": "Calgary, AB",
            "link": "https://jobs.techcalgary.com/python-developer-1234",
            "snippet": "We're looking for a Python Developer with experience in Django/Flask and cloud services. Must have 3+ years of Python experience."
        },
        {
            "title": "Senior Python Engineer",
            "company": "Calgary Tech Solutions",
            "location": "Calgary, AB",
            "link": "https://calgarytech.ca/careers/python-engineer",
            "snippet": "Join our team as a Python Engineer. Responsibilities include developing scalable applications, mentoring junior developers, and implementing best practices."
        },
        {
            "title": "Python/Django Developer",
            "company": "Alberta Software Inc.",
            "location": "Calgary, AB",
            "link": "https://albertasoftware.ca/jobs/developer-python",
            "snippet": "Looking for a Django developer to join our team! Build cutting-edge web applications. Experience with Django REST framework required."
        },
        {
            "title": "Full Stack Developer (Python)",
            "company": "Calgary Digital",
            "location": "Calgary, AB",
            "link": "https://calgarydigital.com/careers/fullstack-python",
            "snippet": "Full stack role focusing on Python backend with JS frontend (React or Vue). Creating responsive web applications for clients."
        },
        {
            "title": "Python Developer - Data Team",
            "company": "DataFlow Analytics",
            "location": "Calgary, AB",
            "link": "https://dataflowanalytics.com/careers/python-data",
            "snippet": "Developer with strong Python skills needed for our data team. Work with large datasets, implement ML models, and create data visualizations."
        }
    ]

def mock_job_description(job):
    """Create a more detailed job description based on the job snippet."""
    title = job.get("title", "")
    company = job.get("company", "")
    snippet = job.get("snippet", "")
    
    # Generate detailed job description based on the job title and snippet
    descriptions = {
        "Python Developer": f"""
## Python Developer at {company}

{company} is seeking an experienced Python Developer to join our growing team in Calgary, AB.

### About the Role
{snippet} Work on exciting projects across a variety of industries.

### Requirements:
- 3+ years of Python development experience
- Strong knowledge of Django or Flask frameworks
- Familiarity with cloud services (AWS, Azure, or GCP)
- Experience with RESTful APIs and microservices
- Solid understanding of database technologies (SQL and NoSQL)
- Bachelor's degree in Computer Science or equivalent experience

### Responsibilities:
- Develop and maintain web applications using Python
- Collaborate with cross-functional teams to define and implement new features
- Write clean, maintainable, and efficient code
- Participate in code reviews and mentor junior developers
- Troubleshoot and debug applications

### Benefits:
- Competitive salary and benefits package
- Professional development opportunities
- Flexible work arrangements
- Modern office in downtown Calgary
- Collaborative and inclusive work environment
""",
        
        "Senior Python Engineer": f"""
## Senior Python Engineer at {company}

{company} is looking for a Senior Python Engineer to help lead our development team in Calgary, AB.

### About the Role
{snippet} You'll help shape our technical direction and mentor the team.

### Requirements:
- 5+ years of professional Python development experience
- Expert knowledge of Python, PostgreSQL, and Redis
- Experience with high-scale applications and performance optimization
- Strong understanding of software design patterns and best practices
- Experience mentoring junior developers and providing technical leadership
- Bachelor's degree in Computer Science or equivalent experience

### Responsibilities:
- Design and implement scalable Python applications
- Lead code reviews and enforce coding standards
- Mentor junior developers and provide technical guidance
- Work with product management to define technical requirements
- Contribute to architectural decisions and technology selection
- Optimize application performance and scalability

### Benefits:
- Competitive salary and comprehensive benefits package
- Leadership development opportunities
- Flexible work arrangements with remote options
- Regular team events and professional development budget
- Modern tech stack and opportunities to explore new technologies
""",
        
        "Python/Django Developer": f"""
## Python/Django Developer at {company}

Join {company} as a Django Developer and help us build cutting-edge web applications.

### About the Role
{snippet} Strong understanding of Python programming principles needed.

### Requirements:
- 2+ years of experience with Django framework
- Proficiency with Django REST framework
- Solid understanding of Python programming principles
- Experience with front-end technologies (JavaScript, HTML, CSS)
- Familiarity with Git version control
- Knowledge of SQL databases (PostgreSQL preferred)

### Responsibilities:
- Develop and maintain Django-based web applications
- Create RESTful APIs using Django REST framework
- Implement front-end components that interact with Django backend
- Write unit tests and participate in code reviews
- Collaborate with designers and product managers
- Document code and development processes

### Benefits:
- Competitive compensation package
- Health and dental benefits
- Remote-friendly work environment
- Professional development opportunities
- Collaborative team of passionate developers
""",
        
        "Full Stack Developer (Python)": f"""
## Full Stack Developer (Python) at {company}

{company} is hiring a Full Stack Developer with strong Python skills for our Calgary office.

### About the Role
{snippet} Remote position with competitive salary.

### Requirements:
- 3+ years of experience with Python backend development
- 2+ years of experience with React or Vue.js
- Knowledge of RESTful API design principles
- Experience with SQL databases
- Understanding of Git workflow
- Familiarity with Agile development methodologies

### Responsibilities:
- Develop full-stack web applications using Python and JavaScript
- Build responsive user interfaces with React or Vue.js
- Create and maintain RESTful APIs
- Optimize applications for performance and scalability
- Collaborate with clients to understand requirements
- Participate in code reviews and team planning sessions

### Benefits:
- Competitive salary and benefits package
- Remote work option with flexible hours
- Professional development budget
- Modern tech stack with opportunities to learn
- Collaborative and supportive work environment
""",
        
        "Python Developer - Data Team": f"""
## Python Developer - Data Team at {company}

{company} is seeking a Python Developer to join our Data Team in Calgary.

### About the Role
{snippet} SQL and pandas experience a must.

### Requirements:
- 3+ years of Python development experience
- Strong knowledge of pandas, NumPy, and other data science libraries
- Experience with SQL and database optimization
- Familiarity with data visualization tools (Matplotlib, Seaborn, Plotly)
- Understanding of machine learning concepts
- Bachelor's degree in Computer Science, Data Science, or related field

### Responsibilities:
- Develop data processing pipelines using Python
- Create and maintain data models and databases
- Implement machine learning models for data analysis
- Generate insightful visualizations and reports
- Collaborate with data scientists and analysts
- Optimize code for performance with large datasets

### Benefits:
- Competitive salary based on experience
- Comprehensive benefits package
- Flexible work arrangements
- Continuous learning and development opportunities
- Collaborative team environment
- Cutting-edge data projects across various industries
"""
    }
    
    # Try to match by full title first
    if title in descriptions:
        return descriptions[title]
    
    # If not found, try matching by partial title
    for key in descriptions:
        if key in title:
            return descriptions[key]
    
    # Fallback to a generic description
    return f"""
## {title} at {company}

{company} is looking for a talented {title} to join our team in Calgary, AB.

### About the Role
{snippet}

### Requirements:
- Experience with Python and related frameworks
- Knowledge of software development principles
- Strong problem-solving skills
- Team player with good communication skills
- Bachelor's degree or equivalent experience

### Responsibilities:
- Develop and maintain software applications
- Collaborate with team members on projects
- Write clean and maintainable code
- Troubleshoot and debug issues
- Stay current with industry trends and technologies

### Benefits:
- Competitive salary and benefits
- Professional development opportunities
- Collaborative work environment
- Work-life balance
"""

def main():
    # Ensure SIMULATION_MODE is set to False
    os.environ["SIMULATION_MODE"] = "false"
    
    # Define the specific job URL to test
    specific_url = "https://careers.beehiiv.com/en/postings/5309bab1-b5a6-40bd-b4f2-3f9fb4c5fc87"
    
    logging.info(f"Testing HTML fallback scraper with specific job URL: {specific_url}")
    print(f"Testing URL: {specific_url}")
    
    # Create a minimal job object
    job = {
        "title": "Beehiiv Job Posting",
        "company": "beehiiv",
        "link": specific_url
    }
    
    # Test the HTML fallback scraper directly on this specific URL
    logging.info(f"Extracting job details from specific URL...")
    details = extract_job_details(specific_url, job)
    
    # Add the description to the job object
    if details.get("description"):
        job["description"] = details.get("description")
        logging.info(f"Successfully extracted description of length: {len(job['description'])}")
    else:
        logging.warning(f"Failed to extract description from {specific_url}")
        job["description"] = "Failed to extract description."
    
    # Put the job in a list for consistent processing with the analyze logic
    enriched_jobs = [job]
    
    # Print raw JSON
    print("===== RAW JSON ARRAY OF JOB OBJECTS =====")
    print(json.dumps(enriched_jobs, indent=2))
    print("\n")
    
    # Analyze descriptions
    results = []
    for job in enriched_jobs:
        desc_analysis = analyze_description(job.get("description", ""))
        results.append({
            "title": job.get("title", ""),
            "company": job.get("company", ""),
            "link": job.get("link", ""),
            "description_length": desc_analysis["length"],
            "passes_all_checks": desc_analysis["passes_all"],
            "analysis": desc_analysis
        })
    
    # Print report
    print("===== JOB DESCRIPTION QUALITY REPORT =====")
    print(f"{'Title':<30} | {'Company':<20} | {'Desc Length':<11} | {'Status':<6} | {'Issues'}")
    print("-" * 100)
    
    for result in results:
        title = result["title"][:27] + "..." if len(result["title"]) > 30 else result["title"].ljust(30)
        company = result["company"][:17] + "..." if len(result["company"]) > 20 else result["company"].ljust(20)
        
        analysis = result["analysis"]
        status = "✅" if analysis["passes_all"] else "❌"
        
        issues = []
        if not analysis["has_description"]:
            issues.append("No description")
        if not analysis["desc_length_ok"]:
            issues.append("Too short")
        if not analysis["has_two_sentences"]:
            issues.append("Not enough sentences")
        
        issues_str = ", ".join(issues) if issues else "None"
        
        print(f"{title} | {company} | {analysis['length']:<11} | {status:<6} | {issues_str}")
    
    # Summary
    passed = sum(1 for r in results if r["analysis"]["passes_all"])
    failed = len(results) - passed
    
    print("\n===== SUMMARY =====")
    print(f"Total jobs: {len(results)}")
    print(f"Passed all checks: {passed}")
    print(f"Failed checks: {failed}")
    
    if failed > 0:
        print("\nFailures:")
        for r in results:
            if not r["analysis"]["passes_all"]:
                issues = []
                if not r["analysis"]["has_description"]:
                    issues.append("No description")
                if not r["analysis"]["desc_length_ok"]:
                    issues.append("Description < 100 chars")
                if not r["analysis"]["has_two_sentences"]:
                    issues.append("Less than 2 sentences")
                
                print(f"- {r['title']} ({r['company']}): {', '.join(issues)}")

if __name__ == "__main__":
    main()
