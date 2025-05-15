#!/usr/bin/env python3
"""
Cover letter generation module that creates customized cover letters
based on templates and job details. This is the central module for all
cover letter related functionality, including generation, sanitization,
extraction from LLM responses, and saving to files.
"""
import os
import re
import logging
import datetime
from typing import Dict, Optional, Any, List, Set, Tuple, Union
from pathlib import Path

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

def sanitize_cover_letter(content: str, job: Optional[Dict] = None) -> str:
    """
    Process a cover letter to replace common placeholders with appropriate values.
    
    Args:
        content: The cover letter content to sanitize
        job: Optional dictionary containing job details (title, company, etc.)
        
    Returns:
        str: Sanitized cover letter content
    """
    if not content:
        return content
        
    today = datetime.datetime.now().strftime('%B %d, %Y')
    
    # Extract job info if available
    company_name = job.get('company', 'the company') if job else 'the company'
    job_title = job.get('title', 'the position') if job else 'the position'
    job_description = job.get('description', '') if job else ''
    company_location = job.get('location', 'Remote') if job else 'Remote'
    
    # Replace company name placeholders
    content = re.sub(r'\[Company Name\]', company_name, content, flags=re.IGNORECASE)
    content = re.sub(r'\[company\]', company_name, content, flags=re.IGNORECASE)
    
    # Replace job title placeholders
    content = re.sub(r'\[Job Title\]', job_title, content, flags=re.IGNORECASE)
    content = re.sub(r'\[position\]', job_title, content, flags=re.IGNORECASE)
    content = re.sub(r'\[job title\]', job_title, content, flags=re.IGNORECASE)
        
    # Replace job platform placeholders - added flag for case-insensitive matching
    content = re.sub(r'\[Platform where you saw the.*?\]', 'LinkedIn job board', content, flags=re.IGNORECASE)
    content = re.sub(r'\[.*?job board.*?\]', 'LinkedIn job board', content, flags=re.IGNORECASE)
    content = re.sub(r'\[.*?job posting.*?\]', 'LinkedIn job board', content, flags=re.IGNORECASE)
    
    # Replace company-specific placeholders with context-aware replacements
    company_focus = ""
    if job:
        if "AI" in company_name or "machine" in company_name.lower() or "tech" in company_name.lower():
            company_focus = "developing innovative AI solutions"
        elif "data" in company_name.lower():
            company_focus = "transforming data into valuable business insights"
        elif "health" in company_name.lower() or "care" in company_name.lower() or "med" in company_name.lower():
            company_focus = "improving healthcare outcomes through technology"
        elif "finance" in company_name.lower() or "bank" in company_name.lower():
            company_focus = "revolutionizing financial services through technology"
        else:
            company_focus = "developing innovative solutions in the industry"
    else:
        company_focus = "developing innovative solutions in the industry"
    
    content = re.sub(r'\[mention a specific area of the company\'s work.*?\]', 
                    company_focus, content, flags=re.IGNORECASE)
    content = re.sub(r'\[.*?specific area of.*?work.*?\]',
                    company_focus, content, flags=re.IGNORECASE)
    
    # Replace other common placeholders with generic values
    content = re.sub(r'\[mention a positive aspect of the company.*?\]', 
                    'delivering innovative solutions', content, flags=re.IGNORECASE)
    content = re.sub(r'\[.*?positive aspect.*?\]', 
                    'innovation and technical excellence', content, flags=re.IGNORECASE)
    
    # Replace location placeholders
    content = re.sub(r'\[Company Location.*?\]', company_location, content, flags=re.IGNORECASE)
                    
    # Handle opening hook placeholder with context awareness
    skills_hook = ""
    if job and job_title:
        if "machine learning" in job_title.lower() or "ml" in job_title.lower() or "ai" in job_title.lower():
            skills_hook = "With 3+ years of experience developing scalable AI/ML solutions and containerized cloud applications"
        elif "data" in job_title.lower():
            skills_hook = "With extensive experience in data pipeline development and analytics using SQL, Python, and cloud platforms"
        elif "devops" in job_title.lower() or "cloud" in job_title.lower():
            skills_hook = "With hands-on expertise in implementing cloud infrastructure and DevOps practices using Docker, Kubernetes, and CI/CD pipelines"
        elif "front" in job_title.lower() or "ui" in job_title.lower() or "ux" in job_title.lower():
            skills_hook = "With a proven record of developing responsive and performant user interfaces using modern JavaScript frameworks"
        else:
            skills_hook = "With 3+ years of experience in software development and cloud technologies"
    else:
        skills_hook = "With 3+ years of experience developing scalable AI/ML solutions and containerized cloud applications"
    
    hook_pattern = r'\[Opening hook that highlights.*?\]'
    if re.search(hook_pattern, content, re.IGNORECASE):
        replacement = f"{skills_hook}, I am excited to apply for the {job_title} position at {company_name}." if job else f"{skills_hook}, I am excited to apply for this opportunity."
        content = re.sub(hook_pattern, replacement, content, flags=re.IGNORECASE)
    
    # Replace paragraphs if missing
    content = re.sub(r'\[Paragraph connecting specific.*?\]', 
                    'At APEGA, I developed containerized AI/ML applications using Python and TensorFlow on AWS, reducing model deployment time by 40% while maintaining 99.9% uptime for critical data pipelines.', 
                    content, flags=re.IGNORECASE)
                    
    content = re.sub(r'\[Paragraph linking another.*?\]', 
                    'I implemented automated testing workflows with PyTest and GitHub Actions at APEGA, achieving a defect rate below 0.5%. Additionally, I\'ve authored complex SQL transformations powering dashboards used by 30K+ users.', 
                    content, flags=re.IGNORECASE)
                    
    content = re.sub(r'\[Brief statement about interest.*?\]', 
                    'I\'m eager to collaborate with your team of experts and contribute to innovative solutions that drive real business impact.', 
                    content, flags=re.IGNORECASE)
    
    # Additional common placeholders
    content = re.sub(r'\[your address\]', 'Calgary, Alberta', content, flags=re.IGNORECASE)
    content = re.sub(r'\[city, state, zip\]', 'Calgary, AB T2P 3E5', content, flags=re.IGNORECASE)
    content = re.sub(r'\[your email\]', '1leonnoel1@gmail.com', content, flags=re.IGNORECASE)
    content = re.sub(r'\[your phone number\]', '306-490-2929', content, flags=re.IGNORECASE)
    content = re.sub(r'\[your name\]', 'Noel Ugwoke', content, flags=re.IGNORECASE)
    content = re.sub(r'\[date\]', today, content, flags=re.IGNORECASE)
    content = re.sub(r'\[current date\]', today, content, flags=re.IGNORECASE)
    content = re.sub(r'\[company address\]', '', content, flags=re.IGNORECASE)
    content = re.sub(r'\[company headquarters\]', '', content, flags=re.IGNORECASE)
    content = re.sub(r'\[hiring manager\'s name\]', 'Hiring Manager', content, flags=re.IGNORECASE)
    content = re.sub(r'\[hiring manager\]', 'Hiring Manager', content, flags=re.IGNORECASE)
    
    # Fix any possessive company names with apostrophe issues (Company's vs Companys)
    # Temporarily disabled as it's causing issues with company names that end with 's'
    # content = re.sub(r'(\w+)s\'s\s', r"\1's ", content)
    # content = re.sub(r'([A-Za-z]+[^s])s\s', r"\1's ", content)
    
    # Fix any double spaces
    content = re.sub(r'  +', ' ', content)
    
    # Fix extra blank lines between paragraphs (standardize to one blank line)
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    # Fix line spacing around salutation and signature
    content = re.sub(r'Dear Hiring Manager,\s*\n', 'Dear Hiring Manager,\n\n', content)
    content = re.sub(r'Sincerely,\s*\n', 'Sincerely,\n\n', content)
    
    # Generic catch-all for any remaining [placeholders]
    content = re.sub(r'\[.*?\]', '', content, flags=re.IGNORECASE)
    
    return content


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
    # Clean up common placeholders in the cover letter
    content = sanitize_cover_letter(content)
    
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

def extract_cover_letter(optimization_response: str, job: Dict = None) -> Optional[str]:
    """
    Extract the cover letter content from the LLM response and replace placeholders.
    
    Args:
        optimization_response: The full response from the LLM
        job: Dictionary containing job details to replace placeholders
        
    Returns:
        str: Extracted cover letter text or None if not found
    """
    cover_letter_pattern = r"---BEGIN_COVER_LETTER---(.*?)---END_COVER_LETTER---"
    match = re.search(cover_letter_pattern, optimization_response, re.DOTALL)
    
    if match:
        cover_letter_text = match.group(1).strip()
        
        # Replace placeholders if job details are provided
        if job:
            cover_letter_text = sanitize_cover_letter(cover_letter_text, job)
        
        return f"---BEGIN_COVER_LETTER---\n{cover_letter_text}\n---END_COVER_LETTER---"
    
    return None


def load_template(path: str) -> Optional[str]:
    """
    Load a cover letter template from a specified path.
    
    Args:
        path: Path to the template file
        
    Returns:
        str: Template text or None if not found
    """
    try:
        if not os.path.exists(path):
            logging.warning(f"Cover letter template not found at {path}")
            return None
            
        with open(path, "r") as f:
            content = f.read()
            if not content.strip():
                logging.warning("Cover letter template is empty")
                return None
            return content
    except Exception as e:
        logging.error(f"Error loading cover letter template: {e}")
        return None

def generate_cover_letter_from_llm_response(
    optimization_response: str, 
    job_info: Dict
) -> Optional[str]:
    """
    Extract and process a cover letter from an LLM optimization response.
    
    Args:
        optimization_response: The full response from the LLM
        job_info: Dictionary containing job details like title and company
        
    Returns:
        str: Processed cover letter text or None if extraction fails
    """
    # First extract the cover letter portion from the response
    extracted_cover_letter = extract_cover_letter(optimization_response, job_info)
    
    if not extracted_cover_letter:
        logging.warning("Failed to extract cover letter from LLM response")
        return None
        
    # Return the extracted and sanitized cover letter
    return extracted_cover_letter
