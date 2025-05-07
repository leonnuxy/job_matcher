"""
Job Description Extraction Module

This module handles extracting the main job description content from various
sources including HTML and plain text job postings.
"""
import re
import logging
import spacy
from bs4 import BeautifulSoup
from lib.job_parser.parser_utils import clean_text

def extract_job_description(job_text):
    """
    Extracts the main job description section from a full job posting (plain text or HTML).
    Uses section heading detection and spaCy sentence segmentation for accuracy.

    Args:
        job_text (str): The full job posting as plain text or HTML.

    Returns:
        str: The most relevant job description section, or an empty string if extraction fails.
    """
    logging.info("Extracting job description")

    if not job_text or not job_text.strip():
        logging.warning("Empty job text provided.")
        return ""

    try:
        # If HTML, extract visible text
        if '<' in job_text and '>' in job_text:
            try:
                soup = BeautifulSoup(job_text, 'html.parser')
                # Use newline as separator, strip leading/trailing whitespace from the result
                job_text = soup.get_text(separator='\n', strip=True)
                logging.debug("HTML parsing successful.")
            except Exception as e:
                logging.error(f"Error parsing HTML: {e}")
                job_text = "" # Ensure job_text is empty on failure
        else:
            logging.debug("Job text is plain text.")

        # Section heading patterns (expand as needed) - More robust regex!
        section_patterns = [
            r'(?i)^\s*(job\s+description|role\s+overview|about\s+the\s+role|position\s+summary|position\s+overview|what\s+you\s+will\s+do|your\s+role)[\s:]*$',
            r'(?i)^\s*(responsibilities|duties|key\s+responsibilities)[\s:]*$',
            r'(?i)^\s*(requirements|qualifications|skills\s+required|what\s+you\s+bring|what\s+we\'re\s+looking\s+for)[\s:]*$',
            r'(?i)^\s*(summary|overview|purpose)[\s:]*$',
        ]

        # Split into lines and find section indices - Stripped lines for pattern matching
        lines = [line.strip() for line in job_text.splitlines()]
        section_indices = [(i, line.lower()) for i, line in enumerate(lines)
                           if any(re.match(pat, line) for pat in section_patterns)]

        # Heuristic: prefer the first 'job description' or 'role overview' section, else first section found
        main_section_start = 0
        main_section_end = len(lines)

        preferred_headings = ['job description', 'role overview', 'position summary', 'position overview', 'responsibilities']

        found_preferred = False
        for idx, heading in section_indices:
            if any(pref_heading in heading for pref_heading in preferred_headings):
                main_section_start = idx + 1
                # Find the index of the *next* section heading *after* the current one
                next_sections = [i for i, _ in section_indices if i > idx]
                main_section_end = next_sections[0] if next_sections else len(lines)
                found_preferred = True
                break # Use the first preferred section found

        # If no preferred section found, use the first section identified
        if not found_preferred and section_indices:
            main_section_start = section_indices[0][0] + 1
            # Find the index of the *next* section heading *after* the first one
            next_sections = [i for i, _ in section_indices if i > section_indices[0][0]]
            main_section_end = next_sections[0] if next_sections else len(lines)

        # Extract the description lines, ensuring they are not empty after stripping
        desc_lines = [line for line in lines[main_section_start:main_section_end] if line]
        desc = '\n'.join(desc_lines).strip()

        # If still too short or empty, fallback to first N sentences of the original text
        # (Use original job_text before line splitting for sentence segmentation)
        if not desc or len(desc.split()) < 30:
            logging.info("Description extraction resulted in short text. Using fallback sentence segmentation.")
            try:
                # Need the original text for proper sentence splitting if it was HTML
                original_text_for_spacy = job_text
                if '<' in job_text and '>' in job_text:
                     try:
                         soup = BeautifulSoup(job_text, 'html.parser')
                         original_text_for_spacy = soup.get_text(separator=' ', strip=True)
                     except Exception:
                         pass # Use the potentially messy text if parsing failed earlier

                nlp = spacy.load('en_core_web_sm')
                doc = nlp(original_text_for_spacy)
                sentences = [sent.text.strip() for sent in doc.sents][:10] # Take first 10 sentences
                desc = ' '.join(sentences).strip()
            except Exception as e:
                logging.error(f"Error during sentence segmentation fallback: {e}")
                return ""  # Return empty string on fallback failure

        logging.info("Job description extraction successful.")
        return desc

    except Exception as e:
        logging.exception(f"Unexpected error during job description extraction: {e}")
        return "" # Very important to return an empty string
