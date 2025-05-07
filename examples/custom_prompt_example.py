"""
Example of how to use a custom prompt template with the resume optimizer.

This demonstrates how to create and use custom prompt templates
to guide the optimization process.
"""

import os
import sys
import json
from pathlib import Path

# Add the parent directory to the path so we can import resume_optimizer
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from resume_optimizer import optimize_resume
from resume_optimizer.prompt_builder import build_prompt, DEFAULT_PROMPT_TEMPLATE


def create_custom_prompt_template():
    """
    Create a custom prompt template for ATS-focused optimization.
    
    Returns:
        str: Custom prompt template
    """
    return """
    As an ATS (Applicant Tracking System) optimization expert, analyze the resume and job description below.
    Your objective is to enhance the resume specifically for ATS compatibility while maintaining human readability.
    
    Format your response as a JSON object with the following structure:

    {
      "summary": "A brief summary of how well the resume matches the job description",
      "skills_to_add": ["List of skills missing from resume that should be added"],
      "skills_to_remove": ["List of skills in resume that are irrelevant to this job"],
      "experience_tweaks": [
        {
          "original": "Original resume bullet or section",
          "optimized": "Improved version that better aligns with job description"
        }
      ],
      "formatting_suggestions": ["Specific formatting changes to improve ATS compatibility"],
      "collaboration_points": ["Areas where collaboration would strengthen the resume for this role"]
    }
    
    Focus particularly on:
    1. Keyword optimization for ATS scanning
    2. Proper formatting to avoid ATS parsing issues
    3. Strategic placement of keywords
    4. Use of industry-standard terminology
    
    RESUME:
    {resume_text}
    
    JOB DESCRIPTION:
    {job_description}
    
    Remember to maintain the exact JSON structure shown above and ensure all required keys are present.
    """


def use_custom_prompt_example():
    """Example of using a custom prompt template."""
    # Sample inputs
    resume_text = """
    John Smith
    Software Engineer
    
    Experience:
    - 3 years developing web applications 
    - Created user interfaces with React
    - Some experience with Python scripting
    
    Skills:
    JavaScript, React, HTML, CSS, Python
    """
    
    job_description = """
    Senior Software Engineer
    
    Requirements:
    - 5+ years experience with web development
    - Expert in JavaScript, React and Node.js
    - Experience with CI/CD pipelines
    - AWS cloud infrastructure knowledge
    """
    
    # Create custom template
    custom_template = create_custom_prompt_template()
    
    # Build a prompt using the custom template
    prompt = custom_template.format(
        resume_text=resume_text,
        job_description=job_description
    )
    
    print("CUSTOM PROMPT TEMPLATE EXAMPLE:")
    print("-------------------------------")
    print("\nOriginal resume:")
    print(resume_text)
    print("\nJob description:")
    print(job_description)
    print("\nGenerated prompt (would be sent to LLM):")
    print("----------------------------------------")
    print(prompt)
    print("----------------------------------------")
    
    # Note: In a real implementation, you would need to modify or extend
    # the prompt_builder.py module to accept a custom template parameter:
    #
    # def build_prompt(resume_text, job_description, template=None):
    #     """Build a prompt using the provided template or the default."""
    #     if template is None:
    #         template = load_prompt_template()
    #     return template.format(resume_text=resume_text, job_description=job_description)


if __name__ == "__main__":
    use_custom_prompt_example()
