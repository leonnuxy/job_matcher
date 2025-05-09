#!/usr/bin/env python3
"""
Cover letter generation module that creates customized cover letters
based on templates and job details.
"""
import os
import re
import logging
from typing import Dict, Optional, Any, List, Set

def load_cover_letter_template() -> Optional[str]:
    """
    Load the cover letter template from the data directory.
    
    Returns:
        str: Cover letter template text or None if not found
    """
    # Get the parent directory path
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    template_path = os.path.join(parent_dir, "data", "cover_letter_template.txt")
    
    if not os.path.exists(template_path):
        print(f"Warning: Cover letter template not found at {template_path}")
        return None
        
    try:
        with open(template_path, "r") as f:
            content = f.read()
            if not content.strip():
                logging.warning("Cover letter template is empty")
                return None
            return content
    except Exception as e:
        logging.error(f"Error loading cover letter template: {e}")
        return None

def validate_template_fields(template: str) -> Set[str]:
    """
    Extract and validate all field placeholders from the template.
    
    Args:
        template: The cover letter template text
        
    Returns:
        Set[str]: Set of unique field names found in template
    """
    required_fields = set()
    placeholder_pattern = r"\{\{([^|{}]+)(?:\|([^{}]+))?\}\}"
    
    for match in re.finditer(placeholder_pattern, template):
        field_name = match.group(1).strip()
        required_fields.add(field_name)
    
    return required_fields

def check_missing_fields(template_fields: Set[str], available_fields: Set[str]) -> List[str]:
    """
    Check for any template fields that don't have corresponding values.
    
    Args:
        template_fields: Set of fields required by the template
        available_fields: Set of fields available from job data and defaults
        
    Returns:
        List[str]: List of missing field names
    """
    return sorted(list(template_fields - available_fields))

def generate_cover_letter(job: Dict[str, Any], template: str) -> str:
    """
    Generate a personalized cover letter by filling placeholders with job information.
    
    Args:
        job: Dictionary containing job details (title, company, location, etc.)
        template: Cover letter template with placeholders
        
    Returns:
        str: Filled cover letter text
    """
    if not template:
        return "Error: No cover letter template provided."
        
    # Validate template fields first
    template_fields = validate_template_fields(template)
        
    # Set default values based on the role
    is_solutions_engineer = "solution" in job.get("title", "").lower()
    
    defaults = {
        "hiring_team": "Hiring Team",
        "role_title": job.get("title", "the position"),
        "company_name": job.get("company", "your company"),
        "education": "Software Engineering graduate",
        "university": "University of Calgary",
        "experience1_company": "APEGA",
        "experience2_company": "Spartan Controls",
        "company_mission": job.get("snippet", "innovation and excellence")[:100] if job.get("snippet") else "innovation and excellence",
        "skill_summary": "develop and demonstrate technical solutions" if is_solutions_engineer else "develop robust, scalable software solutions",
        "industry_desc": "technology innovator",
        "experience1_accomplishments": "led technical integrations and provided solutions consulting" if is_solutions_engineer else "developed key software components",
        "experience1_metrics": "working closely with clients and engineering teams" if is_solutions_engineer else "following agile methodologies",
        "experience1_results": "improved client satisfaction by 40% and reduced integration time by 30%" if is_solutions_engineer else "improved system performance by 30%",
        "experience2_role": "Solutions Engineer" if is_solutions_engineer else "Software Developer",
        "experience2_accomplishments": "provided technical solutions and API integration support" if is_solutions_engineer else "collaborated on critical projects",
        "experience2_metrics": "resulting in 95% client satisfaction" if is_solutions_engineer else "delivered ahead of schedule",
        "passion_desc": "helping clients succeed through technical solutions" if is_solutions_engineer else "building impactful software solutions",
        "skill_list": "APIs, integration patterns, and customer-facing technical communication" if is_solutions_engineer else "Python, JavaScript, and cloud technologies",
        "certifications": "AWS Solutions Architect and API Design" if is_solutions_engineer else "AWS and Python",
        "teamwork_achievement": "successful cross-functional solutions delivery" if is_solutions_engineer else "successful team project deliveries",
        "additional_achievement": "developed comprehensive integration guides and technical documentation" if is_solutions_engineer else "contributed to open-source projects",
        "company_recognition": "innovator in the creator economy" if "creator" in job.get("description", "").lower() else "a leader in technology",
        "company_culture": "innovation and client success" if is_solutions_engineer else "innovation and collaboration",
        "personal_projects": "API integration tools and developer documentation" if is_solutions_engineer else "automation tools and web applications",
        "interview_details": "a technical discussion" if is_solutions_engineer else "an interview at your convenience",
        "applicant_name": "Noel Ugwoke"
    }
    
    # Try to extract location from job info
    location = job.get("location", "")
    if location:
        defaults["location"] = location
        # Also add a location context to various snippets where relevant
        defaults["company_recognition"] = f"a leader in technology in {location}"
        if "Remote" in location:
            defaults["skill_summary"] = f"develop robust, scalable software solutions in a remote environment"
        defaults["passion_desc"] = f"building impactful software solutions for the {location} market"
    
    # Use company name in hiring team if available
    if job.get("company"):
        defaults["hiring_team"] = f"{job.get('company')} Hiring Team"
    
    # Use snippet for company mission if available
    snippet = job.get("snippet", "")
    if snippet and len(snippet) > 20:
        defaults["company_mission"] = snippet[:100].strip()
    
    # Fill in the template placeholders
    filled_letter = template
    
    # Find all placeholder patterns like {{field|default}}
    placeholder_pattern = r"\{\{([^|{}]+)(?:\|([^{}]+))?\}\}"
    
    for match in re.finditer(placeholder_pattern, template):
        full_match = match.group(0)
        field_name = match.group(1).strip()
        default_value = match.group(2).strip() if match.group(2) else None
        
        # Set up available fields from multiple sources
    job_fields = set(field for field in job if job[field])
    common_mappings = {
        "role_title": "title",
        "company_name": "company",
    }
    mapped_fields = set(common_mappings.keys())
    default_fields = set(defaults.keys())
    available_fields = job_fields.union(mapped_fields).union(default_fields)
    
    # Check for missing required fields
    missing_fields = check_missing_fields(template_fields, available_fields)
    if missing_fields:
        logging.warning(f"Missing values for required fields: {', '.join(missing_fields)}")
    
    # Fill in the template placeholders
    filled_letter = template
    
    # Find all placeholder patterns like {{field|default}}
    placeholder_pattern = r"\{\{([^|{}]+)(?:\|([^{}]+))?\}\}"
    
    for match in re.finditer(placeholder_pattern, template):
        full_match = match.group(0)
        field_name = match.group(1).strip()
        default_value = match.group(2).strip() if match.group(2) else ""
        
        value = None
        
        # Try direct from job data first
        if field_name in job and job[field_name]:
            value = job[field_name]
            
        # Try mapped fields (e.g., title -> role_title)
        elif field_name in common_mappings and common_mappings[field_name] in job:
            value = job[common_mappings[field_name]]
            
        # Use our defaults if available
        if not value and field_name in defaults:
            value = defaults[field_name]
            
        # Fall back to template default or empty string
        if not value:
            value = default_value
            if field_name not in defaults and field_name not in job_fields:
                logging.debug(f"No value found for field: {field_name}, using default: {value}")
                
        # Replace the placeholder with the value
        filled_letter = filled_letter.replace(full_match, str(value))
    
    return filled_letter

def save_cover_letter(content: str, out_dir: str, include_timestamp: bool = True, 
                     custom_suffix: str = "") -> str:
    """
    Save a cover letter to a file.
    
    Args:
        content: The content of the cover letter
        out_dir: Output directory path
        include_timestamp: Whether to include a timestamp in the filename
        custom_suffix: Optional custom suffix for the filename
        
    Returns:
        str: Path to the saved file
    """
    import datetime
    
    # Create the output directory if it doesn't exist
    os.makedirs(out_dir, exist_ok=True)
    
    # Create a filename
    timestamp = ""
    if include_timestamp:
        timestamp = f"_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
    
    suffix = ""
    if custom_suffix:
        suffix = f"_{custom_suffix}"
        
    filename = f"CoverLetter{suffix}{timestamp}.md"
    filepath = os.path.join(out_dir, filename)
    
    # Create a symlink to the latest cover letter
    latest_path = os.path.join(out_dir, "latest_cover_letter.md")
    
    # Write the cover letter to the file
    with open(filepath, "w") as f:
        f.write(content)
    
    # Update the "latest" symlink
    try:
        # Get absolute paths for reliable linking
        abs_latest_path = os.path.abspath(latest_path)
        abs_target_path = os.path.abspath(filepath)
        
        # Create relative path from symlink to target
        rel_target_path = os.path.relpath(abs_target_path, os.path.dirname(abs_latest_path))
        
        # Remove existing symlink if it exists
        if os.path.lexists(abs_latest_path):
            os.remove(abs_latest_path)
            
        # Create new symlink using relative path
        os.symlink(rel_target_path, abs_latest_path)
        logging.debug(f"Updated latest cover letter symlink to: {rel_target_path}")
    except Exception as e:
        logging.warning(f"Failed to create symlink for latest cover letter: {e}")
        
    return filepath
