"""
Text processing utilities for job descriptions, snippets, and resumes.
Functions for cleaning, normalizing, and extracting information from text.
"""
import re
from typing import Optional, List, Dict, Set


def clean_job_title(raw_title: str, snippet: str = "") -> str:
    """
    Clean a job title by removing dates, page numbers, and other irrelevant information.
    
    Args:
        raw_title: The raw job title string
        snippet: Optional snippet text that might contain relevant job title information
        
    Returns:
        cleaned_title: A cleaner version of the job title
    """
    # Check if this is likely a job search results page
    is_search_page = re.search(r'^\d+\+?\s+|jobs|employment|careers', raw_title.lower()) is not None
    
    # Remove dates (various formats) from title
    cleaned_title = re.sub(r'\s+\d+\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*,?\s+202\d\s*[\|\-]?.*$', '', raw_title)
    cleaned_title = re.sub(r'\s+\d+\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?$', '', cleaned_title)
    
    # Remove year references
    cleaned_title = re.sub(r'\s+202\d\s*[\|\-]?.*$', '', cleaned_title)
    cleaned_title = re.sub(r'\s+202\d$', '', cleaned_title)
    
    # Remove job board suffixes 
    cleaned_title = re.sub(r' - (Job Posting|Career|Job Application|Jobs|Careers|Job Opportunity|Apply Now).*$', '', cleaned_title)
    
    # Clean up leading numbers (like "50+ Python Jobs")
    cleaned_title = re.sub(r'^\d+\+?\s+', '', cleaned_title)
    
    # Remove other common suffixes
    cleaned_title = re.sub(r' – Apply Now$', '', cleaned_title)
    cleaned_title = re.sub(r'\s+in\s+[A-Za-z, ]+\.\.\.?$', '', cleaned_title)
    cleaned_title = re.sub(r'\s*\|.*$', '', cleaned_title)
    cleaned_title = re.sub(r'Employment.*$', '', cleaned_title)
    
    # Clean up common prefixes
    cleaned_title = re.sub(r'^(?:Job:|Position:|Hiring:)\s*', '', cleaned_title)
    
    # If this looks like a job search results page, try to extract specific job titles
    if is_search_page:
        # Try to extract job titles from the title and snippet
        combined_text = f"{cleaned_title} {snippet}"
        
        # Look for common patterns in job search titles
        search_title_match = re.search(r'(?:^\d+\+?\s+)?(.*?)(?:\s+Jobs|$)', cleaned_title)
        if search_title_match:
            job_type = search_title_match.group(1).strip()
            if job_type and len(job_type) > 3:
                cleaned_title = job_type
                
        # Try to find specific job titles in the combined text
        job_title_patterns = [
            # Python roles
            r'((?:Senior|Staff|Principal|Junior|Lead|Mid)\s*Python\s+Developer)',
            r'(Python\s+(?:Software|Backend|Full\s*Stack)\s+Engineer)',
            # Developer roles
            r'((?:Senior|Staff|Principal|Junior|Lead|Mid)\s*(?:Software|Full\s*Stack|Frontend|Backend)\s+(?:Developer|Engineer))',
            # Data/ML roles  
            r'((?:Senior|Staff|Principal|Junior|Lead|Mid)\s*Data\s+Scientist)',
            r'((?:Senior|Staff|Principal|Junior|Lead|Mid)\s*Machine\s+Learning\s+Engineer)',
            # Other roles
            r'((?:Senior|Staff|Principal|Junior|Lead|Mid)\s*DevOps\s+Engineer)'
        ]
        
        for pattern in job_title_patterns:
            match = re.search(pattern, combined_text, re.IGNORECASE)
            if match:
                return match.group(1)
    
    # Final cleanup and standardization
    cleaned_title = cleaned_title.strip()
    
    # Standardize common job title variations
    cleaned_title = re.sub(r'(?i)software engineer(?:ing)?', 'Software Engineer', cleaned_title)
    cleaned_title = re.sub(r'(?i)sr\.?\s+', 'Senior ', cleaned_title)
    cleaned_title = re.sub(r'(?i)jr\.?\s+', 'Junior ', cleaned_title)
    
    # Default to raw title if our cleaning made it too short
    return cleaned_title if len(cleaned_title) > 3 else raw_title.strip()


def clean_job_snippet(snippet: str) -> str:
    """
    Clean a job snippet by removing timestamps, ellipses, and common prefixes.
    
    Args:
        snippet: The raw snippet string
        
    Returns:
        cleaned_snippet: A cleaner version of the snippet
    """
    # Remove timestamps like "5 days ago" from the beginning
    cleaned_snippet = re.sub(r'^\s*(?:\d+\s+(?:hour|day|week|month)s?\s+ago|Posted \d+\s+days?)\s*[:\-\.\s]*', '', snippet)
    
    # Remove common prefixes
    cleaned_snippet = re.sub(r'^\s*(?:Job Description|Description|About the Role|Position Summary)\s*[:\-\.\s]*', '', cleaned_snippet)
    
    # Remove ellipses from the end
    cleaned_snippet = re.sub(r'[\s\.]+…$', '', cleaned_snippet)
    
    return cleaned_snippet.strip()


def extract_text_between_delimiters(text: str, start_delimiter: str, end_delimiter: str) -> Optional[str]:
    """
    Extracts text from a string between specified start and end delimiters.

    Args:
        text: The string to search within.
        start_delimiter: The starting delimiter string.
        end_delimiter: The ending delimiter string.

    Returns:
        The extracted text if both delimiters are found, otherwise None.
    """
    start_index = text.find(start_delimiter)
    if start_index == -1:
        return None
    
    start_index += len(start_delimiter)
    end_index = text.find(end_delimiter, start_index)
    if end_index == -1:
        return None
        
    return text[start_index:end_index].strip()


def regex_search(text: str, patterns: List[str]) -> Optional[str]:
    """
    Search for the first match of any pattern in the text.
    
    Args:
        text: Text to search in
        patterns: List of regex patterns to search for
        
    Returns:
        The first match found or None if no match
    """
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE|re.DOTALL)
        if m:
            return m.group(1).strip()
    return None


def normalize_text(text: str) -> str:
    """
    Utility function to normalize text by converting to lowercase, removing excess whitespace,
    and standardizing punctuation.
    
    This is a generic text processing utility that's different from the job-specific
    normalizations.
    
    Args:
        text: The text to normalize
        
    Returns:
        Normalized text string
    """
    if not text:
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Replace multiple spaces with a single space
    text = re.sub(r'\s+', ' ', text)
    
    # Standardize punctuation (remove most punctuation except periods and commas)
    text = re.sub(r'[^\w\s\.,]', '', text)
    
    return text.strip()


def normalize_job_text(text: str) -> str:
    """
    Normalize text for job matching by converting to lowercase, removing non-alphanumeric characters,
    and standardizing whitespace. This is a stronger normalization than normalize_text().
    
    Args:
        text: Text to normalize
        
    Returns:
        Normalized text
    """
    if not text:
        return ""
    
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def extract_text_keywords(text: str, stop_words: Optional[List[str]] = None) -> List[str]:
    """
    Generic utility to extract keywords from text by removing stop words.
    
    Args:
        text: The text to extract keywords from
        stop_words: Optional list of stop words to exclude
        
    Returns:
        List of keywords
    """
    if not text:
        return []
        
    if stop_words is None:
        # Common English stop words
        stop_words = ["i", "me", "my", "myself", "we", "our", "ours", "ourselves", 
                      "you", "your", "yours", "yourself", "yourselves", "he", "him", 
                      "his", "himself", "she", "her", "hers", "herself", "it", "its", 
                      "itself", "they", "them", "their", "theirs", "themselves", 
                      "what", "which", "who", "whom", "this", "that", "these", 
                      "those", "am", "is", "are", "was", "were", "be", "been", 
                      "being", "have", "has", "had", "having", "do", "does", "did", 
                      "doing", "a", "an", "the", "and", "but", "if", "or", "because", 
                      "as", "until", "while", "of", "at", "by", "for", "with", 
                      "about", "against", "between", "into", "through", "during", 
                      "before", "after", "above", "below", "to", "from", "up", "down", 
                      "in", "out", "on", "off", "over", "under", "again", "further", 
                      "then", "once", "here", "there", "when", "where", "why", "how", 
                      "all", "any", "both", "each", "few", "more", "most", "other", 
                      "some", "such", "no", "nor", "not", "only", "own", "same", "so", 
                      "than", "too", "very", "s", "t", "can", "will", "just", "don", 
                      "should", "now"]
    
    # Normalize text
    normalized = normalize_text(text)
    
    # Split into words
    words = re.findall(r'\b\w+\b', normalized)
    
    # Filter out stop words and very short words
    keywords = [word for word in words if word not in stop_words and len(word) > 2]
    
    return keywords


def extract_skills_from_text(text: str, skill_patterns: Optional[List[str]] = None) -> List[str]:
    """
    Extract technical skills from text using regex patterns.
    
    Args:
        text: The text to extract skills from
        skill_patterns: Optional list of regex patterns for skills
        
    Returns:
        List of found skills
    """
    if not text:
        return []
    
    if skill_patterns is None:
        # Default patterns for common technical skills
        skill_patterns = [
            r'\b(?:python|java|javascript|typescript|c\+\+|ruby|go|rust|php|swift|kotlin)\b',
            r'\b(?:react|angular|vue|node\.?js|express|django|flask|spring|rails)\b',
            r'\b(?:html|css|sass|less|bootstrap|tailwind)\b',
            r'\b(?:sql|mysql|postgresql|mongodb|firebase|dynamodb|redis|cassandra)\b',
            r'\b(?:aws|azure|gcp|docker|kubernetes|terraform|jenkins|ci/cd)\b',
            r'\b(?:git|github|gitlab|bitbucket)\b',
            r'\b(?:agile|scrum|kanban|jira)\b',
            r'\b(?:machine learning|deep learning|artificial intelligence|ai|ml|nlp)\b',
            r'\b(?:data science|data analysis|statistics|pandas|numpy|tensorflow|pytorch)\b'
        ]
    
    found_skills = []
    normalized_text = text.lower()
    
    for pattern in skill_patterns:
        matches = re.findall(pattern, normalized_text, re.IGNORECASE)
        found_skills.extend([match.lower() for match in matches])
    
    # Remove duplicates and sort
    return sorted(list(set(found_skills)))
