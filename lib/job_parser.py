import re
import spacy
from bs4 import BeautifulSoup
from rake_nltk import Rake
import logging

# Configure logging (optional, but highly recommended)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
                job_text = soup.get_text(separator='\n', strip=True) # Strip whitespace
                logging.debug("HTML parsing successful.")
            except Exception as e:
                logging.error(f"Error parsing HTML: {e}") # Include exception in log
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

        preferred_headings = ['job description', 'role overview', 'position summary', 'position overview']

        for idx, heading in section_indices:
            if any(pref_heading in heading for pref_heading in preferred_headings):
                main_section_start = idx + 1
                next_sections = [i for i, _ in section_indices if i > idx]
                main_section_end = next_sections[0] if next_sections else len(lines)
                break  # Important to break the loop
        else:  # Executes if the 'for' loop completes without a 'break'
            if section_indices:
                main_section_start = section_indices[0][0] + 1
                next_sections = [i for i, _ in section_indices if i > main_section_start]
                main_section_end = next_sections[0] if next_sections else len(lines)

        # Extract the description and strip each line (cleaner)
        desc_lines = [line for line in lines[main_section_start:main_section_end] if line] # Skip empty lines
        desc = '\n'.join(desc_lines).strip()

        # If still too short, fallback to first 10 sentences
        if len(desc.split()) < 30:
            logging.info("Description is too short. Using fallback sentence segmentation.")
            try:
                nlp = spacy.load('en_core_web_sm')
                doc = nlp(job_text)
                sentences = [sent.text.strip() for sent in doc.sents][:10] # Strip whitespace
                desc = ' '.join(sentences)
            except Exception as e:
                logging.error(f"Error during sentence segmentation fallback: {e}")
                return ""  # Return empty string on fallback failure

        logging.info("Job description extraction successful.")
        return desc

    except Exception as e:
        logging.exception(f"Unexpected error during job description extraction: {e}")
        return "" # Very important to return an empty string


def extract_job_requirements(job_text):
    """
    Extracts keywords/phrases from the job description using Rake-nltk, spaCy, and regex.
    Focuses on verbs (actions), nouns (skills/tech), and named entities (skills, technologies, experience).

    Args:
        job_text (str): The job description text.

    Returns:
        list: A sorted list of keywords/phrases.
    """
    logging.info("Extracting job requirements")

    if not job_text or not job_text.strip():
        logging.warning("Empty job text provided.")
        return []

    try:
        # Rake-Nltk extraction
        rake = Rake(min_length=2, max_length=3)
        rake.extract_keywords_from_text(job_text)
        ranked_phrases = set(rake.get_ranked_phrases()[:10])

        # Regex for versioned skills and common tech (case-insensitive, word boundaries)
        regex_skills = set(re.findall(r'\b(Python\s+[23](?:\.\d+)?|SQL|AWS|Java\s*\d+|C\+\+|C#|TypeScript|JavaScript|Docker|Kubernetes|Terraform|Prometheus|Grafana|Jenkins|Linux|REST)\b', job_text, re.I))

        # spaCy for verbs, nouns, and NER
        nlp = spacy.load('en_core_web_sm')
        doc = nlp(job_text)
        verbs = {token.lemma_ for token in doc if token.pos_ == 'VERB'}
        nouns = {token.lemma_ for token in doc if token.pos_ == 'NOUN'}
        entities = {ent.text for ent in doc.ents if ent.label_ in ['ORG', 'PRODUCT', 'SKILL', 'LANGUAGE']}

        # All-caps words (common for tech skills)
        all_caps = set(re.findall(r'\b[A-Z]{2,}\b', job_text))

        # Common tech keywords (moved to top-level for easy modification)
        tech_keywords = [
            'python', 'aws', 'docker', 'kubernetes', 'sql', 'rest', 'agile', 'ci/cd', 'linux',
            'terraform', 'prometheus', 'grafana', 'github actions', 'jenkins', 'infrastructure as code',
            'java', 'javascript', 'typescript', 'django', 'maven', 'gradle', 'git', 'bitbucket', 'github',
            'bash', 'ksh', 'spark', 'kafka', 'scikit-learn', 'vue.js'
        ]

        text_lower = job_text.lower()
        tech_found = {kw for kw in tech_keywords if kw in text_lower}

        # Combine all sources
        keywords = set()
        keywords.update(ranked_phrases)
        keywords.update(regex_skills)
        keywords.update(verbs)
        keywords.update(nouns)
        keywords.update(entities)
        keywords.update(all_caps)
        keywords.update(tech_found)

        # Clean up: remove empty, deduplicate, and sort
        keywords = {kw.strip() for kw in keywords if kw and isinstance(kw, str) and kw.strip()} #Robust checks

        logging.info("Job requirements extraction successful.")
        return sorted(keywords, key=lambda x: x.lower())

    except Exception as e:
        logging.exception(f"Unexpected error during job requirements extraction: {e}")
        return []