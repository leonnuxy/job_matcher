"""
Job matching utilities for comparing resumes with job descriptions.
Includes keyword extraction, similarity scoring, and matching algorithms.
"""
import re
from collections import Counter
from typing import List, Dict, Optional, Union
from .text_processing import normalize_text, normalize_job_text

def extract_job_keywords(text: str, min_length: int = 4, include_technical: bool = True) -> List[str]:
    """
    Extract job-relevant keywords from text, with special handling for technical terms.
    
    Args:
        text: The text to extract keywords from
        min_length: Minimum length for a keyword
        include_technical: Whether to include technical term detection
        
    Returns:
        List of extracted keywords
    """
    if not text:
        return []
        
    # Basic keyword extraction
    text_lower = text.lower()
    words = re.findall(r'\b[A-Za-z][\w\+\#\-\.]*\b', text_lower)
    keywords = [word for word in words if len(word) >= min_length]
    
    # Count frequencies
    keyword_counter = Counter(keywords)
    
    # Technical keywords by category (if enabled)
    if include_technical:
        tech_keywords = {
            # Programming languages
            'languages': [
                'python', 'javascript', 'typescript', 'java', 'c#', 'c++', 'ruby', 'php', 
                'go', 'rust', 'kotlin', 'swift', 'scala', 'r', 'bash', 'shell', 'perl'
            ],
            # Web frameworks
            'web_frameworks': [
                'react', 'angular', 'vue', 'svelte', 'next.js', 'nuxt', 'express', 
                'django', 'flask', 'spring', 'rails', 'laravel', 'asp.net'
            ],
            # Cloud platforms
            'cloud': [
                'aws', 'azure', 'gcp', 'google cloud', 'ibm cloud', 'oracle cloud',
                'digitalocean', 'heroku', 'netlify', 'vercel'
            ],
            # DevOps & Infrastructure
            'devops': [
                'kubernetes', 'k8s', 'docker', 'terraform', 'ansible', 'jenkins', 
                'github actions', 'gitlab ci', 'circleci', 'prometheus', 'grafana'
            ],
            # Databases
            'databases': [
                'sql', 'nosql', 'mongodb', 'postgresql', 'mysql', 'sqlite', 'redis',
                'elasticsearch', 'dynamodb', 'cassandra', 'firestore', 'mariadb'
            ],
            # AI/ML
            'ai_ml': [
                'machine learning', 'ml', 'deep learning', 'ai', 'artificial intelligence',
                'nlp', 'natural language processing', 'tensorflow', 'pytorch', 'keras'
            ],
            # Roles & methodologies
            'roles': [
                'full stack', 'frontend', 'backend', 'devops', 'data engineer', 'data scientist',
                'sre', 'site reliability', 'qa', 'quality assurance', 'product manager',
                'agile', 'scrum', 'kanban', 'continuous integration'
            ]
        }
        
        # Add technical keywords that appear in the text
        for category, tech_terms in tech_keywords.items():
            for term in tech_terms:
                # Use word boundary check for single words
                if ' ' in term:  # Multi-word term
                    if term in text_lower:
                        keyword_counter[term] += 3  # Give more weight to technical terms
                else:  # Single word - use word boundary check
                    pattern = r'\b' + re.escape(term) + r'\b'
                    if re.search(pattern, text_lower):
                        keyword_counter[term] += 3  # Give more weight to technical terms
    
    # Get unique keywords sorted by frequency
    return [kw for kw, _ in keyword_counter.most_common(50)]


def compute_jaccard_similarity(text1: str, text2: str) -> float:
    """
    Calculate similarity between two text strings using Jaccard similarity.
    
    Args:
        text1: First text string
        text2: Second text string
        
    Returns:
        Similarity score between 0.0 and 1.0
    """
    if not text1 or not text2:
        return 0.0
    
    # Extract keywords from both texts
    from .text_processing import extract_text_keywords
    keywords1 = set(extract_text_keywords(text1))
    keywords2 = set(extract_text_keywords(text2))
    
    # Calculate Jaccard similarity: intersection / union
    intersection = keywords1.intersection(keywords2)
    union = keywords1.union(keywords2)
    
    if not union:
        return 0.0
        
    return len(intersection) / len(union)


def calculate_job_match_score(resume_text: str, job_description: Union[Dict, str], 
                          matching_profile: Optional[Dict] = None) -> float:
    """
    Calculate how well a resume matches a job description using multiple techniques:
    - TF-IDF and cosine similarity for semantic matching
    - Direct keyword matching for technical skills
    - Job title relevance for role fit
    
    Args:
        resume_text: Resume text
        job_description: Job dictionary with 'description' field or job description string
        matching_profile: Optional matching profile configuration dictionary
        
    Returns:
        Match score between 0 and 1
    """
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
    except ImportError:
        print("Warning: sklearn not installed. Using basic matching only.")
        # Fall back to basic matching if sklearn is not available
        return _calculate_basic_match_score(resume_text, job_description, matching_profile)
        
    # Set default matching profile
    if matching_profile is None:
        matching_profile = {
            "threshold_multiplier": 1.1,  # Standard mode
            "mode": "standard"
        }
        
    # Extract text and keywords
    if isinstance(job_description, dict):
        desc = job_description.get("description", "")
        job_keywords = job_description.get("keywords", [])
        job_title = job_description.get("title", "")
    else:
        desc = job_description
        job_keywords = []
        job_title = ""
    
    if not desc:
        return 0.0
        
    # Normalize texts
    resume_norm = normalize_job_text(resume_text)
    desc_norm = normalize_job_text(desc)
    
    # 1. TF-IDF and cosine similarity
    tfidf = TfidfVectorizer(
        stop_words="english", 
        max_df=1.0,  # Allow terms that appear in all documents
        min_df=1,    # Keep terms that appear at least once
        ngram_range=(1, 2)  # Use both unigrams and bigrams
    )
    
    docs = [resume_norm, desc_norm]
    X = tfidf.fit_transform(docs)
    tfidf_score = float(cosine_similarity(X[0:1], X[1:2])[0,0])
    
    # Boost the TF-IDF score (they tend to be very small naturally)
    tfidf_score = min(tfidf_score * 3.0, 1.0)
    
    # Add a minimum floor to ensure we don't get too many zeros
    if tfidf_score > 0:
        tfidf_score = max(tfidf_score, 0.18)
    
    # 2. Keyword matching
    keyword_score = 0.0
    if not job_keywords and desc:
        # Extract keywords if not provided
        job_keywords = extract_job_keywords(desc)
        
    if job_keywords:
        resume_lower = resume_text.lower()
        matched_count = 0
        partial_matches = 0
        
        for kw in job_keywords:
            kw_lower = kw.lower()
            # Check for exact matches or common variations
            if (kw_lower in resume_lower or 
                (kw_lower.endswith('s') and kw_lower[:-1] in resume_lower) or 
                (kw_lower + 's' in resume_lower)):
                matched_count += 1
            else:
                # More lenient approach: Check for word parts
                if len(kw_lower) >= 4:
                    # Try to find the first part of the keyword in the resume
                    if kw_lower[:3] in resume_lower or kw_lower[-3:] in resume_lower:
                        partial_matches += 0.7
        
        matched_count += partial_matches
        keyword_score = matched_count / max(1, len(job_keywords))
        
        # Give a bonus for high keyword matches
        if matched_count >= 2:
            keyword_score = min(keyword_score * 1.6, 1.0)
    
    # 3. Job title matching
    title_score = 0.2  # Base score
    if job_title:
        # Include meaningful title words
        title_words = [w for w in normalize_job_text(job_title).split() if len(w) > 2]
        if title_words:
            resume_words = set(resume_norm.split())
            matches = 0
            
            for word in title_words:
                if word in resume_words:
                    matches += 1.3
                else:
                    # Partial matching
                    for resume_word in resume_words:
                        if (word in resume_word and len(word) > 2) or (resume_word in word and len(resume_word) > 2):
                            matches += 0.8
                            break
            
            calculated_score = matches / len(title_words)
            title_score = max(title_score, calculated_score)
            
            # Give stronger bonuses for important role matches
            role_keywords = ['developer', 'engineer', 'analyst', 'scientist', 'manager', 
                            'programmer', 'consultant', 'specialist', 'architect', 'lead']
            for role in role_keywords:
                if role in job_title.lower() and role in resume_text.lower():
                    title_score = min(title_score + 0.35, 1.0)
                    break
    
    # Calculate weighted final score
    final_score = (0.55 * tfidf_score) + (0.35 * keyword_score) + (0.1 * title_score)
    
    # Apply threshold multiplier
    mult = matching_profile.get("threshold_multiplier", 1.0)
    final_score = min(final_score * mult, 1.0)
    
    return round(final_score, 3)


def _calculate_basic_match_score(resume_text: str, job_description: Union[Dict, str], 
                             matching_profile: Optional[Dict] = None) -> float:
    """
    Calculate a basic match score without requiring sklearn.
    Uses keyword and pattern matching only.
    
    Args:
        resume_text: Resume text
        job_description: Job dictionary with 'description' field or job description string
        matching_profile: Optional matching profile configuration dictionary
        
    Returns:
        Match score between 0 and 1
    """
    # Extract text and keywords
    if isinstance(job_description, dict):
        desc = job_description.get("description", "")
        job_keywords = job_description.get("keywords", [])
        job_title = job_description.get("title", "")
    else:
        desc = job_description
        job_keywords = []
        job_title = ""
    
    if not desc:
        return 0.0
        
    # Extract keywords if not provided
    if not job_keywords:
        job_keywords = extract_job_keywords(desc)
    
    # Normalize texts
    resume_lower = resume_text.lower()
    
    # Count keyword matches
    matched_count = 0
    partial_matches = 0
    
    for kw in job_keywords:
        kw_lower = kw.lower()
        if kw_lower in resume_lower:
            matched_count += 1
        elif (kw_lower.endswith('s') and kw_lower[:-1] in resume_lower) or (kw_lower + 's' in resume_lower):
            matched_count += 0.8
        elif len(kw_lower) >= 4 and (kw_lower[:3] in resume_lower or kw_lower[-3:] in resume_lower):
            partial_matches += 0.5
    
    # Calculate keyword score
    keyword_score = (matched_count + partial_matches) / max(1, len(job_keywords))
    
    # Title matching bonus
    title_bonus = 0
    if job_title:
        title_words = [w.lower() for w in job_title.split() if len(w) > 2]
        for word in title_words:
            if word in resume_lower:
                title_bonus += 0.1
    
    # Final score
    final_score = min(keyword_score + title_bonus, 1.0)
    
    # Apply threshold multiplier if provided
    if matching_profile and "threshold_multiplier" in matching_profile:
        mult = matching_profile["threshold_multiplier"]
        final_score = min(final_score * mult, 1.0)
    
    return round(final_score, 3)


def create_matching_profile(matching_mode: str = "standard") -> Dict:
    """
    Create a matching profile with appropriate settings based on mode.
    
    Args:
        matching_mode: The matching mode (standard, strict, lenient, very_lenient)
        
    Returns:
        Dictionary with matching profile settings
    """
    # Determine threshold multipliers based on matching mode
    if matching_mode == "strict":
        threshold_multiplier = 1.0  # Higher threshold for strict mode
    elif matching_mode == "lenient":
        threshold_multiplier = 1.5  # Boost scores by 50% for lenient mode
    elif matching_mode == "very_lenient":
        threshold_multiplier = 2.2  # Ultra lenient - more than double the scores
    else:  # standard
        threshold_multiplier = 1.1  # Make standard mode 10% more lenient by default
    
    return {
        "threshold_multiplier": threshold_multiplier,
        "mode": matching_mode
    }
