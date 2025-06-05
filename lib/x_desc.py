"""
Improved Job Description Extraction Module

This module handles extracting the main job description content from various
sources including HTML and plain text job postings with enhanced detection.
"""
import re
import logging
import spacy
from bs4 import BeautifulSoup
import html

def extract_job_description(job_text):
    """
    Extracts the main job description section from a full job posting (plain text or HTML).
    Uses improved section heading detection and handles snippets better.

    Args:
        job_text (str): The full job posting as plain text or HTML.

    Returns:
        str: The most relevant job description section, or an empty string if extraction fails.
    """
    logging.debug("Extracting job description")  # Changed to debug

    if not job_text or not job_text.strip():
        logging.debug("Empty job text provided.")  # Changed to debug
        return ""

    try:
        # Handle snippets vs. full descriptions
        is_snippet = len(job_text.split()) < 50
        logging.debug(f"Text appears to be a {'snippet' if is_snippet else 'full text'}")
        
        # If snippet, clean up timestamps
        if is_snippet:
            # Remove timestamps like "X hours/days ago"
            cleaned_snippet = re.sub(r'^\s*\d+\s+(?:hours?|days?|weeks?|months?|years?)\s+ago\s*\.{3}\s*', '', job_text)
            cleaned_snippet = re.sub(r'^\s*\d+\s+(?:hours?|days?|weeks?|months?|years?)\s+ago\s*', '', cleaned_snippet)
            return cleaned_snippet.strip()

        # If HTML, extract visible text
        if '<' in job_text and '>' in job_text:
            try:
                # Try to decode HTML entities first
                decoded_html = html.unescape(job_text)
                soup = BeautifulSoup(decoded_html, 'html.parser')
                
                # Remove script and style elements that aren't visible
                for script_or_style in soup(["script", "style"]):
                    script_or_style.extract()
                    
                # Use newline as separator, strip leading/trailing whitespace
                job_text = soup.get_text(separator='\n', strip=True)
                logging.debug("HTML parsing successful.")
            except Exception as e:
                logging.error(f"Error parsing HTML: {e}")
                # Continue with original text if HTML parsing fails

        # Section heading patterns (expanded and improved)
        section_patterns = [
            # Job description sections
            r'(?i)^\s*(job\s+description|role\s+overview|about\s+the\s+role|position\s+summary|position\s+overview|what\s+you\s+will\s+do|your\s+role|opportunity\s+description|job\s+summary)[\s:]*$',
            # Responsibilities sections
            r'(?i)^\s*(responsibilities|duties|key\s+responsibilities|main\s+responsibilities|responsibilities\s+include|job\s+duties|your\s+responsibilities)[\s:]*$',
            # Requirements sections
            r'(?i)^\s*(requirements|qualifications|skills\s+required|what\s+you\s+bring|what\s+we\'re\s+looking\s+for|required\s+skills|desired\s+skills|experience|required\s+experience)[\s:]*$',
            # General summary sections
            r'(?i)^\s*(summary|overview|purpose|job\s+details|position\s+details|about\s+the\s+job|about\s+this\s+role)[\s:]*$',
            # Company sections
            r'(?i)^\s*(about\s+us|about\s+the\s+company|company\s+overview|who\s+we\s+are)[\s:]*$',
            # Benefits sections
            r'(?i)^\s*(benefits|perks|compensation|what\s+we\s+offer)[\s:]*$',
        ]

        # Split into lines and find section indices with their headings
        lines = [line.strip() for line in job_text.splitlines()]
        section_indices = []
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            for pattern in section_patterns:
                if re.match(pattern, line_lower):
                    section_indices.append((i, line_lower))
                    break

        # If no section headings found, try to find sections with ALL CAPS
        if not section_indices:
            for i, line in enumerate(lines):
                # Check for short ALL CAPS lines that might be section headers
                if (line.isupper() and 
                    3 <= len(line.split()) <= 5 and 
                    len(line) <= 50):
                    section_indices.append((i, line.lower()))

        # Sort sections by preferred headings
        preferred_headings = [
            'job description', 'role overview', 'position summary', 'position overview', 
            'responsibilities', 'duties', 'what you will do', 'job summary'
        ]

        main_section_start = 0
        main_section_end = len(lines)
        found_preferred = False

        # First try to find a preferred section
        for idx, heading in section_indices:
            if any(pref_heading in heading for pref_heading in preferred_headings):
                main_section_start = idx + 1
                # Find the next section after this one
                next_sections = [i for i, _ in section_indices if i > idx]
                main_section_end = next_sections[0] if next_sections else len(lines)
                found_preferred = True
                break

        # If no preferred section found, use the first section identified
        if not found_preferred and section_indices:
            main_section_start = section_indices[0][0] + 1
            next_sections = [i for i, _ in section_indices if i > section_indices[0][0]]
            main_section_end = next_sections[0] if next_sections else len(lines)

        # Extract the description lines, ensuring they are not empty
        desc_lines = [line for line in lines[main_section_start:main_section_end] if line]
        desc = '\n'.join(desc_lines).strip()

        # If still too short or empty, return the full text
        if not desc or len(desc.split()) < 30:
            # Check if full text is very short - could be a snippet
            if len(job_text.split()) < 100:
                # For very short texts, just clean it up a bit and return
                cleaned_text = re.sub(r'^\s*\d+\s+(?:hours?|days?|weeks?|months?|years?)\s+ago\s*\.{3}\s*', '', job_text)
                cleaned_text = re.sub(r'^\s*\d+\s+(?:hours?|days?|weeks?|months?|years?)\s+ago\s*', '', cleaned_text)
                return cleaned_text.strip() or job_text
            
            logging.info("Description extraction resulted in short text. Using spaCy fallback.")
            try:
                nlp = spacy.load('en_core_web_sm')
                doc = nlp(job_text)
                sentences = [sent.text.strip() for sent in doc.sents]
                
                # If we have enough sentences, take first 15
                if len(sentences) >= 10:
                    desc = ' '.join(sentences[:15]).strip()
                else:
                    # Otherwise just use the full text
                    desc = job_text.strip()
            except Exception as e:
                logging.error(f"Error during sentence segmentation fallback: {e}")
                desc = job_text.strip()

        # Final cleanup
        # Remove redundant whitespace
        desc = re.sub(r'\s+', ' ', desc)
        # Remove timestamps
        desc = re.sub(r'^\s*\d+\s+(?:hours?|days?|weeks?|months?|years?)\s+ago\s*\.{3}\s*', '', desc)
        desc = re.sub(r'^\s*\d+\s+(?:hours?|days?|weeks?|months?|years?)\s+ago\s*', '', desc)
        
        logging.info("Job description extraction successful.")
        return desc.strip()

    except Exception as e:
        logging.exception(f"Unexpected error during job description extraction: {e}")
        return job_text.strip()  # Return original text on failure as fallback
