import os
import re
import logging
from datetime import datetime, timedelta
import google.generativeai as genai
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Import API keys from config
from config import API_KEY, CSE_ID, GEMINI_API_KEY

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def extract_location_from_snippet(snippet, search_term):
    """
    Extract location information from job snippets or search terms.
    
    Args:
        snippet (str): The job snippet text
        search_term (str): The original search term which may contain location
        
    Returns:
        str: The extracted location or None if not found
    """
    # First, try to extract location from search term (e.g., "Python developer Calgary")
    search_parts = search_term.split()
    if len(search_parts) > 1 and search_parts[-1].lower() not in ["jobs", "developer", "engineer", "position"]:
        possible_location = search_parts[-1]
        return possible_location
        
    # Try to extract location info from the snippet
    # Common location patterns in job snippets
    location_patterns = [
        r'in\s+([A-Za-z\s]+),\s+([A-Za-z\s]+)', # "in Calgary, Alberta"
        r'location[:\s]+([A-Za-z\s,]+)', # "Location: Calgary"
        r'([A-Za-z]+),\s+([A-Za-z]{2})', # "Calgary, AB"
        r'([A-Za-z\s]+)\s+([A-Za-z]{2})\s+([A-Za-z0-9]+)', # "Calgary AB T2P"
    ]
    
    for pattern in location_patterns:
        matches = re.search(pattern, snippet, re.IGNORECASE)
        if matches:
            return matches.group(0).strip()
    
    return None

def extract_company_from_title(title):
    """
    Extract company name from job title if possible.
    
    Args:
        title (str): The job title text
        
    Returns:
        str: The extracted company name or None if not found
    """
    # Common patterns for company names in titles
    company_patterns = [
        r'at\s+([A-Za-z0-9\s&]+)', # "at Company Name"
        r'hiring .+ at\s+([A-Za-z0-9\s&]+)', # "hiring ... at Company Name"
        r'([A-Za-z0-9\s&]+)\s+\|\s+LinkedIn', # "Company Name | LinkedIn"
        r'([A-Za-z0-9\s&]+)\s+hiring', # "Company Name hiring"
    ]
    
    for pattern in company_patterns:
        matches = re.search(pattern, title, re.IGNORECASE)
        if matches:
            company = matches.group(1).strip()
            # Clean up common unwanted suffixes
            company = re.sub(r'\s*\|\s*LinkedIn$', '', company)
            return company
    
    return None

def search_jobs(search_term, max_results=10, max_age_hours=24):
    """Search for job listings using Google Custom Search API."""
    api_key = API_KEY
    cse_id = CSE_ID
    try:
        service = build("customsearch", "v1", developerKey=api_key)
        # Add dateRestrict if max_age_hours is set
        params = {'q': search_term, 'cx': cse_id, 'num': max_results}
        if max_age_hours:
            # Google CSE supports dateRestrict in days only
            days = max(1, int(max_age_hours // 24))
            params['dateRestrict'] = f'd{days}'
        res = service.cse().list(**params).execute()
        items = res.get('items', [])
        results = []
        for item in items:
            # Extract location from search term or snippet
            location = extract_location_from_snippet(item.get('snippet', ''), search_term)
            
            # Extract company name from title if possible
            company = extract_company_from_title(item.get('title', ''))
            
            results.append({
                'title': item.get('title', ''),
                'link': item.get('link', ''),
                'snippet': item.get('snippet', ''),
                'location': location,
                'company': company
            })
        return results
    except HttpError as e:
        logging.error(f"Google CSE API error: {e}")
    except Exception as e:
        logging.error(f"Unexpected error in search_jobs: {e}")
    return []


def optimize_resume_with_gemini(resume_text, job_description):
    """
    Use Google's Gemini AI to optimize a resume for a specific job description.
    
    Args:
        resume_text (str): The text content of the resume
        job_description (str): The text content of the job description
        
    Returns:
        str: Optimization suggestions for the resume
    """
    try:
        # Configure the Gemini API
        genai.configure(api_key=GEMINI_API_KEY)
        
        # Use a model we know exists from our previous test
        model_name = "models/gemini-1.5-flash"
        logging.info(f"Using Gemini model: {model_name}")
        
        model = genai.GenerativeModel(model_name)
        
        # Create the prompt
        prompt = f"""
        As an expert resume optimizer, analyze the resume and job description below.
        Provide specific, actionable suggestions to improve the resume to better match the job requirements.
        Focus on:
        1. Skills alignment - identify missing skills that should be highlighted
        2. Experience framing - how to better present existing experience
        3. Keywords optimization - specific terms to include
        4. Formatting suggestions - if applicable
        
        RESUME:
        {resume_text}
        
        JOB DESCRIPTION:
        {job_description}
        
        Provide your response as a structured list of suggestions with clear, specific changes.
        """
        
        # Generate content with minimal configuration
        response = model.generate_content(prompt)
        
        # Log success
        logging.info("Resume optimization completed successfully")
        
        return response.text
        
    except Exception as e:
        logging.error(f"Error optimizing resume with Gemini: {e}")
        return f"Resume optimization failed: {str(e)}"
