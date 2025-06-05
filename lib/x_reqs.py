"""
Improved Job Requirements Extraction Module

This module handles extracting skills, technologies, and qualifications from job descriptions
using various NLP techniques including Rake-nltk, spaCy, and regex patterns with better filtering.
"""
import re
import logging
import spacy
from rake_nltk import Rake
import string

# Import stopwords from parser_utils
from lib.job_parser.parser_utils import (
    JOB_DESCRIPTION_STOP_WORDS, 
    TRANSLATOR, 
    clean_text
)

# Enhanced tech skills regex pattern
TECH_SKILLS_PATTERN = r'\b(python|django|flask|fastapi|java|spring|hibernate|kotlin|scala|maven|c\+\+|c#|\.net|sql|postgresql|mysql|oracle|mongodb|nosql|redis|aws|azure|gcp|cloud|docker|kubernetes|k8s|terraform|ansible|jenkins|ci/cd|devops|git|github|gitlab|bitbucket|rest|graphql|api|javascript|typescript|react|angular|vue|node\.?js|express|ruby|rails|php|laravel|symfony|html5?|css3?|sass|less|bootstrap|tailwind|jquery|d3\.js|webgl|unity3d|mobile|android|ios|swift|kotlin|flutter|react\s*native|automated\s*testing|selenium|cypress|jest|mocha|junit|testng|nlp|machine\s*learning|ml|ai|artificial\s*intelligence|data\s*science|pandas|numpy|scipy|scikit-learn|tensorflow|keras|pytorch|nlp|openai|llm|large\s*language\s*model|transformers|generative\s*ai|big\s*data|hadoop|spark|kafka|data\s*engineering|etl|data\s*warehouse|data\s*lake|snowflake|redshift|tableau|power\s*bi|looker|qlik|game\s*development|unreal\s*engine|unity|godot|blockchain|solidity|web3|ethereum|security|pentesting|cryptography|linux|unix|bash|powershell|networking|tcp/ip|http|rest|soap|microservices|serverless|lambda|function|kubernetes)\b'

# University degrees and education keywords
EDUCATION_PATTERN = r'\b(?:bachelor|master|phd|doctorate|bs|ms|msc|bsc|ba|ma|degree|diploma)\s+(?:of|in|on)?\s+(?:science|engineering|computer|computing|software|information|technology|it|development|programming|mathematics|statistics|data|ai|artificial intelligence|machine learning|physics|electrical|systems)\b'

# Known tech companies to detect
TECH_COMPANIES = [
    'google', 'facebook', 'meta', 'apple', 'microsoft', 'amazon', 'aws', 'netflix', 
    'twitter', 'linkedin', 'uber', 'airbnb', 'dropbox', 'slack', 'stripe', 'paypal', 
    'oracle', 'salesforce', 'adobe', 'ibm', 'intel', 'nvidia', 'amd', 'qualcomm',
    'samsung', 'sony', 'shopify', 'square', 'twilio', 'atlassian', 'zendesk', 'hubspot'
]

def extract_job_requirements(job_text):
    """
    Extracts potential skills, technologies, and qualifications from the job description
    using an improved approach with better filtering and classification.

    Args:
        job_text (str): The job description text.

    Returns:
        list: A sorted list of potential requirement keywords/phrases.
    """
    logging.debug("Extracting job requirements")  # Changed to debug

    if not job_text or not job_text.strip():
        logging.debug("Empty job text provided for requirements extraction.")  # Changed to debug
        return []

    try:
        # 0. Preprocessing: Clean text
        text_lower = clean_text(job_text)
        
        # Remove common 'ago' timestamps which contaminate the results
        text_lower = re.sub(r'\d+\s+(?:hours?|days?|weeks?|months?|years?)\s+ago', '', text_lower)
        
        # Early detect if this is likely a job snippet rather than full description
        is_snippet = len(text_lower.split()) < 50
        logging.debug(f"Text appears to be a {'snippet' if is_snippet else 'full description'}")

        # 1. Regex for specific tech skills (highest confidence)
        tech_skills = set()
        tech_skills_matches = re.findall(TECH_SKILLS_PATTERN, text_lower, re.I)
        for skill in tech_skills_matches:
            # Normalize skill names
            normalized_skill = skill.lower().strip()
            if normalized_skill.startswith('python'): normalized_skill = 'python'
            elif normalized_skill.startswith('java') and not normalized_skill.startswith('javascript'): 
                normalized_skill = 'java'
            elif normalized_skill.endswith('.js'): normalized_skill = normalized_skill[:-3]
            elif normalized_skill.startswith('react'): normalized_skill = 'react'
            elif normalized_skill.startswith('angular'): normalized_skill = 'angular'
            elif normalized_skill.startswith('vue'): normalized_skill = 'vue'
            elif normalized_skill.startswith('node'): normalized_skill = 'node.js'
            
            tech_skills.add(normalized_skill)
            
        logging.debug(f"Regex tech skills: {tech_skills}")
        
        # 2. Education requirements
        education_reqs = set()
        education_matches = re.findall(EDUCATION_PATTERN, text_lower, re.I)
        for edu in education_matches:
            education_reqs.add(edu.lower().strip())
        
        logging.debug(f"Education requirements: {education_reqs}")
            
        # 3. Extract years of experience patterns
        experience_reqs = set()
        experience_patterns = [
            r'(\d+\+?\s*(?:-\s*\d+)?\s+years?\s+(?:of\s+)?experience)',
            r'(minimum\s+of\s+\d+\s+years?\s+(?:of\s+)?experience)',
            r'(at\s+least\s+\d+\s+years?\s+(?:of\s+)?experience)',
            r'(experience\s*:\s*\d+\+?\s+years?)'
        ]
        
        for pattern in experience_patterns:
            matches = re.findall(pattern, text_lower, re.I)
            experience_reqs.update([match.lower().strip() for match in matches])
        
        logging.debug(f"Experience requirements: {experience_reqs}")
        
        # 4. Detect tech companies mentions
        company_mentions = set()
        for company in TECH_COMPANIES:
            if re.search(r'\b' + re.escape(company) + r'\b', text_lower, re.I):
                company_mentions.add(company)
                
        logging.debug(f"Tech company mentions: {company_mentions}")
        
        # 5. Use spaCy only for more detailed extraction in full job descriptions
        # Skip for snippets to avoid noise
        noun_chunks = set()
        entities = set()
        
        if not is_snippet:
            try:
                nlp = spacy.load('en_core_web_sm')
                doc = nlp(text_lower)
                
                # Get noun chunks (for skills, technologies)
                for chunk in doc.noun_chunks:
                    chunk_text = chunk.text.strip().lower()
                    # Filter chunks: length > 1 word, not just stop words, contains relevant POS
                    words = chunk_text.split()
                    if (len(words) > 1 and 
                        len(words) <= 4 and
                        not all(word in JOB_DESCRIPTION_STOP_WORDS for word in words) and
                        any(token.pos_ in ['NOUN', 'PROPN'] for token in chunk)):
                        noun_chunks.add(chunk_text)
                
                # Get named entities
                allowed_entity_labels = {'PRODUCT', 'ORG', 'GPE'}
                for ent in doc.ents:
                    if ent.label_ in allowed_entity_labels:
                        text = ent.text.lower().strip()
                        if (len(text) > 2 and 
                            not text in JOB_DESCRIPTION_STOP_WORDS and
                            not all(word in JOB_DESCRIPTION_STOP_WORDS for word in text.split())):
                            entities.add(text)
            except Exception as e:
                logging.warning(f"Error in spaCy processing: {e}")
        
        # 6. Combine all sources
        all_requirements = set()
        all_requirements.update(tech_skills)
        all_requirements.update(education_reqs)
        all_requirements.update(experience_reqs)
        all_requirements.update(company_mentions)
        
        # Only add noun chunks and entities if not a snippet
        if not is_snippet:
            filtered_noun_chunks = set()
            for chunk in noun_chunks:
                # Only keep chunks that seem like real technical terms or requirements
                if (not chunk in JOB_DESCRIPTION_STOP_WORDS and
                    not any(common in chunk for common in ['hour', 'day', 'week', 'month', 'year', 'ago']) and
                    not any(chunk.startswith(word) for word in ['the', 'this', 'that', 'our', 'your'])):
                    filtered_noun_chunks.add(chunk)
                    
            all_requirements.update(filtered_noun_chunks)
            all_requirements.update(entities)
        
        # 7. Clean and filter final results
        cleaned_requirements = set()
        for req in all_requirements:
            # Basic cleaning
            cleaned = req.lower().translate(TRANSLATOR).strip()
            cleaned = re.sub(r'\s+', ' ', cleaned).strip()
            
            # Apply filters
            if (cleaned and 
                len(cleaned) > 1 and
                not cleaned.isdigit() and
                cleaned not in JOB_DESCRIPTION_STOP_WORDS and
                not all(word in JOB_DESCRIPTION_STOP_WORDS for word in cleaned.split())):
                cleaned_requirements.add(cleaned)
        
        logging.info(f"Extracted {len(cleaned_requirements)} potential requirements after filtering.")
        return sorted(list(cleaned_requirements))
        
    except Exception as e:
        logging.exception(f"Unexpected error during job requirements extraction: {e}. Text snippet: '{job_text[:100]}...'")
        return []
