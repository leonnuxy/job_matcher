"""
Prompt builder module for resume optimization.

This module handles loading and constructing prompts for the resume optimization LLM.
"""

import os
import json
from typing import Dict, Any

# Default prompt template
DEFAULT_PROMPT_TEMPLATE = """
As an expert resume optimizer, analyze the resume and job description below.
Provide specific, actionable suggestions to improve the resume to better match the job requirements.
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

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Remember to maintain the exact JSON structure shown above and ensure all required keys are present.
"""


def load_prompt_template() -> str:
    """
    Load the prompt template from the configured source.
    
    Returns:
        str: The prompt template string.
    """
    # Path to a YAML/JSON prompt template if we want to load from file
    # template_path = os.path.join(os.path.dirname(__file__), "prompt_template.yaml")
    
    # For now, just return the default template
    # In a future version, we might load from file if it exists
    return DEFAULT_PROMPT_TEMPLATE


def build_prompt(resume_text: str, job_description: str) -> str:
    """
    Build a prompt for the LLM by injecting inputs into the template.
    
    Args:
        resume_text (str): The text content of the resume.
        job_description (str): The text content of the job description.
        
    Returns:
        str: The complete prompt ready to send to the LLM.
    """
    template = load_prompt_template()
    
    # Validate inputs
    if not resume_text or not job_description:
        raise ValueError("Both resume_text and job_description must be provided")
    
    # Format the template with the inputs
    formatted_prompt = template.format(
        resume_text=resume_text,
        job_description=job_description
    )
    
    return formatted_prompt
