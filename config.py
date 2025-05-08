"""
Configuration module for the job_matcher application.
Handles environment variables and configuration settings.
"""
import os
import sys
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file if it exists
# Make sure we check for .env in the project root directory
env_path = Path(__file__).parent / '.env'
if not env_path.exists():
    print(f"Warning: .env file not found at {env_path}")
else:
    load_dotenv(dotenv_path=env_path)

# Validate that API keys are available
if not os.getenv('OPENAI_API_KEY') and not os.getenv('GEMINI_API_KEY'):
    print("Warning: Neither OPENAI_API_KEY nor GEMINI_API_KEY found in environment. Ensure your .env file exists and is properly formatted.")

def get_llm_provider():
    """Get the LLM provider from environment variables, defaults to 'gemini'"""
    return os.getenv('LLM_PROVIDER', 'gemini').lower()

def get_api_key():
    """
    Get the appropriate API key based on the LLM provider.
    Returns the API key for the selected provider.
    """
    provider = get_llm_provider()
    
    if provider == "gemini":
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY environment variable is not set. Please set it and try again.")
    elif provider == "openai":
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY environment variable is not set. Please set it and try again.")
    else:
        raise RuntimeError(f"Unknown LLM_PROVIDER: {provider}. Please use 'gemini' or 'openai'.")
    
    return api_key

# Export both API keys regardless of the current provider
# This allows the client to switch providers without reloading
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
