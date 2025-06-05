"""
Configuration settings for Job Matcher application.
API keys and other sensitive information should be stored in environment variables
and loaded here.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Google Custom Search API credentials
API_KEY = os.getenv('GOOGLE_API_KEY')
CSE_ID = os.getenv('GOOGLE_CSE_ID')

# Gemini AI API key
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'database': os.getenv('DB_NAME', 'job_matcher'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'port': int(os.getenv('DB_PORT', 3306)),
}

# Job search settings
MAX_JOB_AGE_HOURS = int(os.getenv('MAX_JOB_AGE_HOURS', 24))
MAX_SEARCH_RESULTS = int(os.getenv('MAX_SEARCH_RESULTS', 10))

# Paths configuration
# Assuming config.py is in the project root directory
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
RESULTS_DIR = os.path.join(PROJECT_ROOT, 'results')
PROMPT_FILE_PATH = os.path.join(PROJECT_ROOT, 'prompt.txt') # Centralize prompt file path

# Ensure directories exist
# DATA_DIR might not need to be created here if it's expected to exist with inputs
os.makedirs(RESULTS_DIR, exist_ok=True)