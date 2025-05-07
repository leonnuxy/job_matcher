"""
Configuration settings for the resume optimizer.
"""

import os
from typing import Optional

# API Configuration
GEMINI_API_KEY: str = os.environ.get('GEMINI_API_KEY', '')
MODEL_NAME: str = os.environ.get('GEMINI_MODEL', 'models/gemini-1.5-flash')

# Cache Configuration
CACHE_TTL_SECONDS: int = int(os.environ.get('CACHE_TTL_SECONDS', 3600))  # Default: 1 hour

# API Request Configuration
REQUEST_TIMEOUT_SECONDS: int = int(os.environ.get('REQUEST_TIMEOUT_SECONDS', 5))
MAX_RETRIES: int = int(os.environ.get('MAX_RETRIES', 3))
BACKOFF_FACTOR: float = float(os.environ.get('BACKOFF_FACTOR', 0.5))

# LLM Configuration
TEMPERATURE: float = float(os.environ.get('TEMPERATURE', 0.2))
MAX_OUTPUT_TOKENS: int = int(os.environ.get('MAX_OUTPUT_TOKENS', 2048))

def get_api_key() -> Optional[str]:
    """
    Get the API key, prioritizing environment variables.
    
    Returns:
        Optional[str]: API key if available, None otherwise.
    """
    return GEMINI_API_KEY

def validate_config() -> bool:
    """
    Validate that required configuration parameters are set.
    
    Returns:
        bool: True if configuration is valid, False otherwise.
    """
    if not GEMINI_API_KEY:
        return False
    return True
