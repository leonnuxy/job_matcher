"""
LLM client for Google's Gemini API.

This module wraps calls to Gemini with error handling, retries, and timeout.
"""

import time
import logging
from typing import Dict, Any, Optional
import google.generativeai as genai
from google.api_core import exceptions, retry
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception

from .config import (
    MODEL_NAME,
    get_api_key,
    REQUEST_TIMEOUT_SECONDS,
    MAX_RETRIES,
    BACKOFF_FACTOR,
    TEMPERATURE,
    MAX_OUTPUT_TOKENS,
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class LLMClientError(Exception):
    """Base class for LLM client errors."""
    pass


class LLMTimeoutError(LLMClientError):
    """Raised when LLM request times out."""
    pass


class LLMServerError(LLMClientError):
    """Raised when LLM server returns an error (5xx)."""
    pass


class LLMClientRequestError(LLMClientError):
    """Raised when LLM request is invalid (4xx)."""
    pass


class LLMResponseError(LLMClientError):
    """Raised when LLM response is malformed."""
    pass


def _is_retriable_error(exception):
    """
    Determine if an error is retriable.
    
    Args:
        exception: The exception to check.
        
    Returns:
        bool: True if the error is retriable, False otherwise.
    """
    if isinstance(exception, (LLMTimeoutError, LLMServerError)):
        return True
    if isinstance(exception, exceptions.ServiceUnavailable):
        return True
    if isinstance(exception, exceptions.ResourceExhausted):  # Rate limiting
        return True
    return False


@retry(
    stop=stop_after_attempt(MAX_RETRIES),
    wait=wait_exponential(multiplier=BACKOFF_FACTOR, min=1, max=10),
    retry=retry_if_exception(_is_retriable_error),
    reraise=True
)
def call_model(prompt: str) -> str:
    """
    Call the Gemini model with the given prompt.
    
    Args:
        prompt (str): The prompt to send to the model.
        
    Returns:
        str: The generated text response.
        
    Raises:
        LLMTimeoutError: If the request times out.
        LLMClientRequestError: If there's a client-side error (4xx).
        LLMServerError: If there's a server-side error (5xx).
        LLMResponseError: If the response is malformed.
        ValueError: If API key is not configured.
    """
    api_key = get_api_key()
    if not api_key:
        raise ValueError("API key not configured. Set GEMINI_API_KEY environment variable.")
    
    start_time = time.time()
    try:
        # Configure the Gemini API
        genai.configure(api_key=api_key)
        
        # Initialize the model
        model = genai.GenerativeModel(
            MODEL_NAME,
            generation_config={
                "temperature": TEMPERATURE,
                "max_output_tokens": MAX_OUTPUT_TOKENS,
            }
        )
        
        # Call the model with timeout
        response = model.generate_content(
            prompt,
            timeout=REQUEST_TIMEOUT_SECONDS
        )
        
        # Log successful call
        elapsed = time.time() - start_time
        logger.info(f"LLM call successful in {elapsed:.2f}s")
        
        # Check if response has text attribute
        if not hasattr(response, 'text'):
            raise LLMResponseError("Model response missing 'text' attribute")
        
        return response.text
    
    except exceptions.DeadlineExceeded:
        elapsed = time.time() - start_time
        logger.error(f"LLM request timed out after {elapsed:.2f}s")
        raise LLMTimeoutError(f"Request timed out after {elapsed:.2f}s")
    
    except exceptions.GoogleAPICallError as e:
        elapsed = time.time() - start_time
        status_code = getattr(e, 'code', None)
        
        if status_code and 400 <= status_code < 500:
            logger.error(f"LLM client error {status_code}: {str(e)}")
            raise LLMClientRequestError(f"Client error {status_code}: {str(e)}")
        
        if status_code and 500 <= status_code < 600:
            logger.error(f"LLM server error {status_code}: {str(e)}")
            raise LLMServerError(f"Server error {status_code}: {str(e)}")
        
        logger.error(f"LLM API error: {str(e)}")
        raise LLMClientError(f"API error: {str(e)}")
    
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"LLM unexpected error after {elapsed:.2f}s: {str(e)}")
        raise LLMClientError(f"Unexpected error: {str(e)}")
