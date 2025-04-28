import re
import spacy
from collections import Counter
from string import punctuation
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Try to load spacy model, but provide fallback for when it's not available
try:
    nlp = spacy.load('en_core_web_sm')
except OSError:
    # Fallback to providing a helpful error message
    print("Error: The spaCy model 'en_core_web_sm' is not installed.")
    print("Please install it using: python -m spacy download en_core_web_sm")
    # Create a minimal object that won't break everything if someone 
    # tries to use basic functionality without the model
    class MinimalNLP:
        class Defaults:
            stop_words = set()
    nlp = MinimalNLP()

# List of common stopwords 
STOPWORDS = set(nlp.Defaults.stop_words) if hasattr(nlp, 'Defaults') else set()
CUSTOM_STOP_WORDS = {"example", "another", "etc", "responsible", "experience", "ability", "proficient", "skilled", "knowledge", "familiar", "including", "required", "preferred", "must", "should", "excellent", "strong", "demonstrated", "proven", "background", "understanding"}
STOPWORDS = STOPWORDS.union(CUSTOM_STOP_WORDS)

# === Simple ATS Logic from simple_ats_comparison.py ===
def extract_skills_simple(text):
    """Extract potential skills from text using a predefined list of common technical skills."""
    # Comprehensive list of common skills
    common_skills = [
        # Programming Languages
        'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'ruby', 'php', 'go', 'rust',
        'swift', 'kotlin', 'scala', 'perl', 'r', 'bash', 'powershell', 'sql', 'ksh', 'shell',
        
        # Front-end
        'html', 'css', 'react', 'angular', 'vue', 'jquery', 'bootstrap', 'sass', 'less',
        'redux', 'webpack', 'babel', 'gatsby', 'next.js', 'svelte', 'ember', 'backbone',
        
        # Back-end & Frameworks
        'node', 'express', 'django', 'flask', 'spring', 'boot', 'rails', 'laravel',
        'asp.net', 'hibernate', 'symfony', '.net', '.net core', 'fastapi',
        
        # Databases
        'sql', 'mysql', 'postgresql', 'oracle', 'mongodb', 'cassandra', 'redis', 'elasticsearch',
        'dynamodb', 'sqlite', 'mariadb', 'couchdb', 'firestore', 'neo4j', 'nosql', 'cosmosdb',
        
        # DevOps & Cloud
        'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'jenkins', 'gitlab',
        'github', 'ci/cd', 'devops', 'ansible', 'puppet', 'chef', 'prometheus', 'grafana',
        'elk', 'helm', 'istio', 'vagrant', 'cloudformation', 'arm templates',
        
        # Version Control
        'git', 'svn', 'mercurial', 'bitbucket', 'github', 'gitlab', 'git flow',
        
        # Methodologies & Practices
        'agile', 'scrum', 'kanban', 'jira', 'tdd', 'bdd', 'ci/cd', 'sre', 'devops',
        'waterfall', 'lean', 'sdlc', 'rca', 'metrics',
        
        # Operating Systems
        'linux', 'windows', 'macos', 'unix', 'ubuntu', 'centos', 'rhel', 'debian',
        'fedora', 'red hat', 'suse',
        
        # API & Web Services
        'rest', 'soap', 'api', 'graphql', 'swagger', 'openapi', 'grpc', 'websocket',
        'oauth', 'jwt', 'http', 'https',
        
        # Data & ML
        'machine learning', 'ai', 'data science', 'big data', 'hadoop', 'spark',
        'pandas', 'numpy', 'scikit-learn', 'tensorflow', 'pytorch', 'keras',
        'tableau', 'power bi', 'etl', 'data mining', 'nlp', 'computer vision',
        
        # Testing
        'unit testing', 'integration testing', 'selenium', 'cypress', 'jest', 'mocha',
        'chai', 'junit', 'testng', 'pytest', 'jasmine', 'karma', 'cucumber',
        
        # Architecture
        'microservices', 'serverless', 'soa', 'event-driven', 'cqrs', 'mvc',
        'mvvm', 'restful', 'domain driven design',
        
        # Infrastructure
        'cloud', 'saas', 'paas', 'iaas', 'container', 'vm', 'virtualization',
        'server', 'load balancer', 'cdn', 'dns', 'vpc', 'subnet',
        
        # Security
        'cybersecurity', 'infosec', 'authentication', 'authorization', 'oauth',
        'encryption', 'ssl', 'tls', 'penetration testing', 'vulnerability',
        
        # Monitoring & Logging
        'monitoring', 'logging', 'splunk', 'elk', 'prometheus', 'grafana', 'datadog',
        'newrelic', 'appdynamics', 'cloudwatch', 'sentry', 'kibana', 'logstash',
        
        # Build Tools
        'maven', 'gradle', 'npm', 'yarn', 'pip', 'bundler', 'ant', 'make',
        'webpack', 'gulp', 'grunt', 'artifactory',
        
        # Mobile Development
        'android', 'ios', 'react native', 'flutter', 'xamarin', 'swift', 'kotlin',
        'objective-c',
        
        # Collaboration Tools
        'slack', 'teams', 'confluence', 'jira', 'trello', 'asana', 'notion',
        'sharepoint', 'gsuite', 'office 365'
    ]
    
    # Convert to lowercase for case-insensitive matching
    text_lower = text.lower()
    
    # Find skills in the text
    found_skills = []
    for skill in common_skills:
        # Use word boundaries to avoid partial matches
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            found_skills.append(skill)
    
    return found_skills

def calculate_similarity_simple(resume_skills, job_skills):
    """Calculate a similarity score between resume skills and job skills."""
    if not resume_skills or not job_skills:
        return 0
    
    # Convert to sets for intersection
    resume_set = set(skill.lower() for skill in resume_skills)
    job_set = set(skill.lower() for skill in job_skills)
    
    # Find matching skills
    matches = resume_set.intersection(job_set)
    
    # Calculate score as percentage of job skills matched
    score = (len(matches) / len(job_set)) * 100
    
    return round(score, 1)

# Keep the original _preprocess_text function that may be used elsewhere
def _preprocess_text(text):
    # Remove common OCR errors, normalize whitespace, ensure UTF-8
    text = text.replace('1', 'l').replace('0', 'O')  # Example OCR fixes
    text = re.sub(r'\s+', ' ', text)
    return text.encode('utf-8', errors='ignore').decode('utf-8')

# === Main ATS analysis function - uses the simpler implementation ===
def simulate_ats_analysis(resume_text, job_description, similarity_score=None):
    """
    Calculate ATS score using the same logic as the testing module.
    
    Args:
        resume_text (str): The text content of a resume
        job_description (str): The text content of a job description
        similarity_score (float, optional): If provided, uses this score instead of computing it
        
    Returns:
        float: A score representing the ATS matching percentage
    """
    # Preprocess texts
    resume_text = _preprocess_text(resume_text) if resume_text else ""
    job_description = _preprocess_text(job_description) if job_description else ""
    
    # Extract skills
    resume_skills = extract_skills_simple(resume_text)
    job_skills = extract_skills_simple(job_description)
    
    # Calculate similarity if not provided
    if similarity_score is None:
        similarity_score = calculate_similarity_simple(resume_skills, job_skills)
    
    # Enhanced ATS simulation score with keyword density and context
    # 60% similarity score + 30% keyword density + 10% keyword placement
    keyword_density_score = min(100, len(resume_skills) * 5)  
    
    # Simple keyword placement score - check if keywords appear in important sections
    placement_score = 0
    important_sections = ['summary', 'experience', 'skills', 'education']
    resume_lower = resume_text.lower()
    for section in important_sections:
        if section in resume_lower:
            placement_score += 25  # 25 points for each important section found
    placement_score = min(100, placement_score)  # Cap at 100
    
    # Calculate weighted score
    ats_score = (similarity_score * 0.6) + (keyword_density_score * 0.3) + (placement_score * 0.1)
    
    return round(ats_score, 1)

# Keep some of the original functions that might be useful for more advanced analysis
def _extract_keywords(text):
    """Extract keywords using spaCy if available, fallback to simple tokenization."""
    try:
        text = _preprocess_text(text)
        doc = nlp(text)
        keywords = [token.lemma_.lower() for token in doc 
                   if token.is_alpha and token.lemma_.lower() not in STOPWORDS]
        return keywords
    except Exception as e:
        # If spaCy fails, use a simpler approach
        print(f"Advanced keyword extraction failed: {e}")
        return [word.lower() for word in re.findall(r'\b\w+\b', text) 
               if word.lower() not in STOPWORDS]

def get_matching_skills(resume_text, job_description):
    """
    Get matched and missing skills between a resume and job description.
    Useful for providing detailed feedback.
    
    Args:
        resume_text (str): The content of the resume
        job_description (str): The content of the job description
        
    Returns:
        dict: Dictionary containing matched_skills and missing_skills
    """
    resume_skills = extract_skills_simple(resume_text)
    job_skills = extract_skills_simple(job_description)
    
    # Convert to sets for set operations
    resume_set = set(skill.lower() for skill in resume_skills)
    job_set = set(skill.lower() for skill in job_skills)
    
    # Find matching and missing skills
    matching_skills = resume_set.intersection(job_set)
    missing_skills = job_set - resume_set
    
    return {
        'matched_skills': list(matching_skills),
        'missing_skills': list(missing_skills),
        'resume_skills': resume_skills,
        'job_skills': job_skills
    }
