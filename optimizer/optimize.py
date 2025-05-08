"""
Resume optimization module that compares resume against job descriptions
and provides improvement recommendations using Gemini AI or OpenAI.
"""
import os
import sys
import argparse

# Add parent directory to sys.path if running as a module
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from services.llm_client import LLMClient, LLM_PROVIDER
from services.utils import save_optimized_resume

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
        default_template_path = os.path.join(parent_dir, "data", "resume_template", "Noel Ugwoke Resume.md")
        
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

def main():
    """
    Main entry point when script is executed directly
    """
    parser = argparse.ArgumentParser(description="Optimize resume for a job description")
    parser.add_argument("--resume", "-r", default=os.path.join(parent_dir, "data", "resume.txt"), 
                       help="Path to resume file (default: data/resume.txt)")
    parser.add_argument("--job", "-j", default=os.path.join(parent_dir, "data", "job_descriptions", "job_description.txt"),
                       help="Path to job description file (default: data/job_descriptions/job_description.txt)")
    parser.add_argument("--prompt", "-p", default=os.path.join(parent_dir, "prompt.txt"),
                       help="Path to prompt template file (default: prompt.txt)")
    parser.add_argument("--output", "-o", help="Output filename (optional)")
    parser.add_argument("--no-timestamp", action="store_true", help="Don't include timestamp in filename")
    args = parser.parse_args()

    # Load files
    try:
        # Check if files exist first
        for filepath in [args.prompt, args.resume, args.job]:
            if not os.path.exists(filepath):
                print(f"Error: File not found - {filepath}")
                print(f"Current directory: {os.getcwd()}")
                print(f"Make sure you're running from the project root directory")
                sys.exit(1)
                
        with open(args.prompt, "r") as f:
            prompt_template = f.read()
        with open(args.resume, "r") as f:
            resume_text = f.read()
        with open(args.job, "r") as f:
            job_description = f.read()
    except Exception as e:
        print(f"Error loading files: {e}")
        sys.exit(1)

    # Check directories
    out_dir = os.path.join(parent_dir, "data", "optimization_results")
    os.makedirs(out_dir, exist_ok=True)
    
    # Extract job title and company from job description for auto-naming
    job_title = ""
    company_name = ""
    try:
        # Simple extraction of job title and company from job description
        for line in job_description.split('\n')[:10]:  # Check first 10 lines only
            if "title:" in line.lower():
                job_title = line.split(":", 1)[1].strip().replace(" ", "_")
            elif "company:" in line.lower() or "organization:" in line.lower():
                company_name = line.split(":", 1)[1].strip().replace(" ", "_")
    except:
        pass
        
    # If output suffix not provided but we found job info, use that
    if not args.output and job_title and company_name:
        args.output = f"{job_title}_{company_name}"
    
    print(f"Optimizing resume using {LLM_PROVIDER.capitalize()}...")
    optimized_md = optimize_resume(resume_text, job_description, prompt_template)

    # Save output 
    output_path = save_optimized_resume(optimized_md, out_dir, 
                                       include_timestamp=not args.no_timestamp, 
                                       custom_suffix=args.output)
    
    print(f"Optimized resume saved to: {output_path}")
    
    # Print first few lines to confirm it worked
    preview_lines = optimized_md.split('\n')[:10]
    print("\nPreview:")
    print('\n'.join(preview_lines))
    print("...")

if __name__ == "__main__":
    main()