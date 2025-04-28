import logging
import spacy
from rake_nltk import Rake


def extract_resume_text(resume_file):
    """
    Extracts and returns the text content from the given resume file.
    Logs an error and returns an empty string if the file does not exist or is empty.
    """
    try:
        with open(resume_file, 'r', encoding='utf-8') as f:
            text = f.read()
            if not text.strip():
                logging.error(f"Resume file '{resume_file}' is empty.")
                return ""
            return text
    except FileNotFoundError:
        logging.error(f"Resume file '{resume_file}' not found.")
    except Exception as e:
        logging.error(f"Error reading resume file '{resume_file}': {e}")
    return ""


def extract_resume_skills(resume_text):
    """
    Extracts skills/keywords from the resume text using Rake-nltk, spaCy, regex, and tech keyword matching.
    Returns a list of skills as strings.
    """
    print("Extracting Skills")
    if not resume_text or not resume_text.strip():
        return []
    # Rake-Nltk extraction
    rake = Rake(min_length=2, max_length=3)
    rake.extract_keywords_from_text(resume_text)
    ranked_phrases = set(rake.get_ranked_phrases()[:15])
    # Regex for versioned skills and common tech
    import re
    regex_skills = set(re.findall(r'Python\s+[23](?:\.\d+)?|SQL|AWS|Java\s*\d+|C\+\+|C#|TypeScript|JavaScript|Docker|Kubernetes|Terraform|Prometheus|Grafana|Jenkins|Linux|REST', resume_text, re.I))
    # spaCy for verbs, nouns, and NER
    nlp = spacy.load('en_core_web_sm')
    doc = nlp(resume_text)
    verbs = {token.lemma_ for token in doc if token.pos_ == 'VERB'}
    nouns = {token.lemma_ for token in doc if token.pos_ == 'NOUN'}
    entities = {ent.text for ent in doc.ents if ent.label_ in ['ORG', 'PRODUCT', 'SKILL', 'LANGUAGE']}
    # All-caps words (common for tech skills)
    all_caps = set(re.findall(r'\b[A-Z]{2,}\b', resume_text))
    # Common tech keywords
    tech_keywords = [
        'python', 'aws', 'docker', 'kubernetes', 'sql', 'rest', 'agile', 'ci/cd', 'linux',
        'terraform', 'prometheus', 'grafana', 'github actions', 'jenkins', 'infrastructure as code',
        'java', 'javascript', 'typescript', 'django', 'maven', 'gradle', 'git', 'bitbucket', 'github',
        'bash', 'ksh', 'spark', 'kafka', 'scikit-learn', 'vue.js'
    ]
    text_lower = resume_text.lower()
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
    keywords = {kw.strip() for kw in keywords if kw.strip()}
    return sorted(keywords, key=lambda x: x.lower())
