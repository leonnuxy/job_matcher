# lib/optimization_utils.py
import os
import re
import logging
from datetime import datetime
import google.generativeai as genai
from config import GEMINI_API_KEY, PROMPT_FILE_PATH

logger = logging.getLogger(__name__)

def extract_text_between_delimiters(text: str, start_delimiter: str, end_delimiter: str) -> str:
    """
    Extract text between two delimiters.
    """
    if not text or not start_delimiter or not end_delimiter:
        return ""
    
    pattern = f"{re.escape(start_delimiter)}(.*?){re.escape(end_delimiter)}"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""

def clean_generated_cover_letter(cover_letter: str) -> str:
    """Clean up common placeholders in the generated cover letter."""
    if not cover_letter:
        return ""

    today = datetime.now().strftime("%B %d, %Y")
    cover_letter = re.sub(r'\[Date\]', today, cover_letter, flags=re.IGNORECASE)
    
    # Remove address blocks more robustly
    cover_letter = re.sub(r'\[Hiring Manager Name\].*?\[Company Address\]\n?', '', cover_letter, flags=re.DOTALL | re.IGNORECASE)
    cover_letter = re.sub(r'\[Your Name\].*?\[Your Address\].*?\[Your Phone\].*?\[Your Email\]\n?', '', cover_letter, flags=re.DOTALL | re.IGNORECASE)

    cover_letter = re.sub(r',\s*as advertised on\s*\[.*?\]', '', cover_letter, flags=re.IGNORECASE)
    cover_letter = re.sub(r'\[Hiring Manager[^\]]*\]', 'Hiring Manager', cover_letter, flags=re.IGNORECASE)
    cover_letter = re.sub(r'\[Company Name\]', 'the company', cover_letter, flags=re.IGNORECASE) # Generic placeholder
    cover_letter = re.sub(r'\[Job Title\]', 'the position', cover_letter, flags=re.IGNORECASE) # Generic placeholder

    # Collapse excessive blank lines and remove leading/trailing whitespace on lines
    lines = [line.strip() for line in cover_letter.splitlines()]
    cover_letter = "\n".join(lines)
    cover_letter = re.sub(r'\n{3,}', '\n\n', cover_letter)
    
    return cover_letter.strip()

def generate_optimized_documents(resume_text: str, job_description: str) -> tuple:
    """
    Generates an optimized resume and cover letter using Gemini API.
    Returns (optimized_resume, cover_letter, full_raw_response) where each can be str or None.
    """
    try:
        with open(PROMPT_FILE_PATH, 'r', encoding='utf-8') as file:
            prompt_template = file.read()

        prompt = prompt_template.format(
            resume_text=resume_text,
            job_description=job_description
        )

        genai.configure(api_key=GEMINI_API_KEY)
        model_name = "models/gemini-1.5-flash" # Consider making this configurable
        logger.debug(f"Using Gemini model: {model_name} for optimization")  # Changed to debug
        model = genai.GenerativeModel(model_name)

        response = model.generate_content(prompt)
        optimization_result = response.text

        optimized_resume = extract_text_between_delimiters(optimization_result, "---BEGIN_RESUME---", "---END_RESUME---")
        cover_letter = extract_text_between_delimiters(optimization_result, "---BEGIN_COVER_LETTER---", "---END_COVER_LETTER---")

        return optimized_resume, clean_generated_cover_letter(cover_letter) if cover_letter else None, optimization_result
    except Exception as e:
        logger.error(f"Error during Gemini optimization: {e}", exc_info=True)
        return None, None, None
