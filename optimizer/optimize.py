"""
Resume optimization module that compares resume against job descriptions
and provides improvement recommendations using Gemini AI or OpenAI.
"""
import os
import sys

# Add parent directory to sys.path if running as a module
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from services.llm_client import LLMClient, LLM_PROVIDER

# Define model names for different providers
MODEL_MAP = {
    "gemini": "gemini-1.5-flash",
    "openai": "gpt-4.1-mini"  # or whatever OpenAI model you prefer
}

# Initialize the LLM client
client = LLMClient(model_name=MODEL_MAP[LLM_PROVIDER])

def optimize_resume(resume_text: str, job_description: str, prompt_template: str) -> str:
    """
    Returns the AI-generated, Markdown-formatted optimized resume.
    """
    try:
        # Replace placeholders directly instead of using string.format() to avoid KeyError issues
        prompt = prompt_template.replace("{resume_text}", resume_text.strip())
        prompt = prompt.replace("{job_description}", job_description.strip())
        
        # Generate content using the LLM client (handles both Gemini and OpenAI)
        return client.generate(prompt)
    except Exception as e:
        print(f"Warning: Error calling {LLM_PROVIDER.capitalize()} API: {e}")
        print("Using default resume template instead...")
        
        # Return a pre-defined resume template for testing/development
        default_template_path = "data/resume_template/Noel Ugwoke Resume.md"
        
        # Check if the file exists
        if os.path.exists(default_template_path):
            with open(default_template_path, "r") as f:
                return f.read()
        else:
            # If the file doesn't exist, return a simple template
            return """# NOEL UGWOKE
Calgary, Alberta | 306-490-2929 | 1leonnoel1@gmail.com | [LinkedIn](https://www.linkedin.com/in/noelugwoke/) | [Portfolio](https://noelugwoke.com/)

## TECHNICAL SKILLS
- **Languages & Frameworks:**  Python, TypeScript/Node.js, SQL, Java, JavaScript, C++, C#
- **Data & Analytics:** Apache Spark, Kafka, AWS S3/EMR, dbt, Snowflake/Redshift, Pandas
- **Cloud & DevOps:** Docker, Kubernetes, GitHub Actions, Jenkins, Terraform, AWS-Lambda

## PROFESSIONAL EXPERIENCE

**Software Engineer (Cloud & Data)**
APEGA | Calgary, AB | Dec 2022 – Dec 2024
*   Developed and deployed containerized applications on AWS using Kubernetes
*   Automated pipeline tests with PyTest & GitHub Actions
*   Built GitHub Actions workflows that improved deployment time by 35%

## EDUCATION & CERTIFICATIONS
*   **BSc. Computer Science** University of Calgary | 2016-2022
*   **AWS** Certified Cloud Practitioner | Jan 2023
"""