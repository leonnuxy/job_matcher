"""
Job Requirements Extraction Module

This module handles extracting skills, technologies, and qualifications from job descriptions
using various NLP techniques including Rake-nltk, spaCy, and regex patterns.
"""
import re
import logging
import spacy
from rake_nltk import Rake
from lib.job_parser.parser_utils import (
    JOB_DESCRIPTION_STOP_WORDS, 
    TRANSLATOR, 
    clean_text
)

def extract_job_requirements(job_text):
    """
    Extracts potential skills, technologies, and qualifications from the job description
    using Rake-nltk, spaCy (NER, Noun Chunks), and specific regex patterns.
    Filters results against a stop-word list.

    Args:
        job_text (str): The job description text.

    Returns:
        list: A sorted list of potential requirement keywords/phrases.
    """
    logging.info("Extracting job requirements")

    if not job_text or not job_text.strip():
        logging.warning("Empty job text provided for requirements extraction.")
        return []

    try:
        # 0. Preprocessing: Lowercase, remove URLs, normalize whitespace
        text_lower = clean_text(job_text)

        logging.debug(f"Preprocessed text (first 100 chars): {text_lower[:100]}")

        # 1. Rake-Nltk extraction (focus on longer phrases)
        rake = Rake(min_length=2, max_length=4, stopwords=JOB_DESCRIPTION_STOP_WORDS) # Use stop words here
        rake.extract_keywords_from_text(text_lower)
        ranked_phrases = set(rake.get_ranked_phrases()[:15]) # Get lowercased phrases
        logging.debug(f"Rake phrases: {ranked_phrases}")

        # 2. Regex for specific versioned skills and common tech (refined)
        # Added PostgreSQL, ensured word boundaries, runs on lowercased text
        # Kept original case in pattern for potential acronyms like AWS, GCP but match is case-insensitive
        regex_skills_matches = re.findall(
            r'\b(python\s*\d?\.?\d*|sql|postgresql|aws|azure|gcp|java\s*\d*|c\+\+|c#|\.net|typescript|javascript|react(?:\.?js)?|angular(?:\.?js)?|vue(?:\.?js)?|node(?:\.?js)?|docker|kubernetes|terraform|ansible|jenkins|git|linux|rest(?:ful)?\s*api[s]?|graphql|spark|kafka|hadoop|tableau|power\s*bi)\b',
            text_lower, # Use lowercased text
            re.I # Case-insensitive still useful if pattern had mixed case
        )
        # Normalize regex results (e.g., 'python 3.9' -> 'python', 'react.js' -> 'react')
        regex_skills = set()
        for skill in regex_skills_matches:
            normalized_skill = skill.lower().strip()
            if normalized_skill.startswith('python'): normalized_skill = 'python'
            elif normalized_skill.startswith('java'): normalized_skill = 'java'
            elif normalized_skill.endswith('.js'): normalized_skill = normalized_skill[:-3]
            elif normalized_skill.startswith('react'): normalized_skill = 'react'
            elif normalized_skill.startswith('angular'): normalized_skill = 'angular'
            elif normalized_skill.startswith('vue'): normalized_skill = 'vue'
            elif normalized_skill.startswith('node'): normalized_skill = 'node'
            elif normalized_skill.startswith('power'): normalized_skill = 'power bi' # Handle space
            elif normalized_skill.startswith('rest'): normalized_skill = 'rest api' # Normalize
            # Add more normalizations if needed
            regex_skills.add(normalized_skill)

        logging.debug(f"Regex skills (normalized): {regex_skills}")

        # 3. spaCy for Noun Chunks and relevant Named Entities
        # Use the preprocessed lowercased text
        nlp = spacy.load('en_core_web_sm')
        doc = nlp(text_lower) # Process lowercased text

        # Extract Noun Chunks
        noun_chunks = set()
        for chunk in doc.noun_chunks:
            chunk_text = chunk.text.strip()
            # Filter chunks: length > 1 word, not just stop words, contains relevant POS
            words = chunk_text.split()
            if len(words) > 1 and \
               not all(word in JOB_DESCRIPTION_STOP_WORDS for word in words) and \
               any(token.pos_ in ['NOUN', 'PROPN', 'ADJ'] for token in chunk):
                 noun_chunks.add(chunk_text)
        logging.debug(f"Noun chunks: {noun_chunks}")

        # Extract relevant Named Entities
        entities = set()
        allowed_entity_labels = {'PRODUCT', 'SKILL', 'LANGUAGE', 'WORK_OF_ART', 'ORG'} # Added ORG back broadly for now
        # known_tech_orgs = {'amazon', 'google', 'microsoft', 'oracle', 'apache'} # Keep for potential future refinement

        for ent in doc.ents:
            label = ent.label_
            text_lower_ent = ent.text.lower().strip() # Already lowercase from doc
            if label in allowed_entity_labels:
                 # Avoid adding single-word entities that are stop words unless maybe uppercase in original? (Harder now)
                 # Let's filter based on stop words directly
                 if text_lower_ent not in JOB_DESCRIPTION_STOP_WORDS:
                    entities.add(text_lower_ent)
            # elif label == 'ORG' and text_lower_ent in known_tech_orgs:
            #      entities.add(text_lower_ent)
        logging.debug(f"Entities: {entities}")

        # 4. Combine all sources
        keywords = set()
        keywords.update(ranked_phrases)
        keywords.update(regex_skills)
        keywords.update(noun_chunks)
        keywords.update(entities)

        # 5. Clean up and Filter more aggressively
        cleaned_keywords = set()

        for kw in keywords:
            # Basic cleaning: strip whitespace, remove most punctuation, ensure lowercase
            # Apply translation to remove punctuation
            kw_cleaned = kw.lower().translate(TRANSLATOR).strip()
            # Replace multiple spaces that might result from punctuation removal
            kw_cleaned = re.sub(r'\s+', ' ', kw_cleaned).strip()

            # Filter conditions:
            if (kw_cleaned and # Not empty after cleaning
                kw_cleaned not in JOB_DESCRIPTION_STOP_WORDS and # Not a stop word itself
                len(kw_cleaned) > 1 and # More than one character
                not kw_cleaned.isdigit() and # Not just digits
                # Check if all constituent words are stop words
                not all(word in JOB_DESCRIPTION_STOP_WORDS for word in kw_cleaned.split())
                ):
                    # Handle specific cases like 'c #' -> 'c#'
                    if kw_cleaned == 'c #': kw_cleaned = 'c#'
                    elif kw_cleaned == 'c + +': kw_cleaned = 'c++'
                    # Add the cleaned, lowercased version
                    cleaned_keywords.add(kw_cleaned)

        logging.info(f"Extracted {len(cleaned_keywords)} potential requirements after filtering.")
        # Final check: remove any remaining single-letter keywords unless they are 'c' (for C language)
        final_keywords = {kw for kw in cleaned_keywords if len(kw) > 1 or kw == 'c'}

        return sorted(list(final_keywords)) # Return list

    except Exception as e:
        logging.exception(f"Unexpected error during job requirements extraction: {e}. Text snippet: '{job_text[:100]}...'")
        return []
