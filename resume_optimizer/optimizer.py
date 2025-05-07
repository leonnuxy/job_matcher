"""
Main optimizer module that coordinates the resume optimization process.

This module brings together prompt building, LLM client, caching, and schema validation.
"""

import json
import logging
import os
from typing import Dict, Any, Optional
import jsonschema

from .prompt_builder import build_prompt
from .llm_client import call_model, LLMClientError
from .cache import generate_cache_key, get_default_cache
from .config import CACHE_TTL_SECONDS

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class OptimizerError(Exception):
    """Base class for optimizer errors."""
    pass


class SchemaValidationError(OptimizerError):
    """Raised when LLM response fails schema validation."""
    pass


class InputValidationError(OptimizerError):
    """Raised when inputs fail validation."""
    pass


def _load_schema() -> Dict[str, Any]:
    """
    Load the JSON schema for validation.
    
    Returns:
        Dict[str, Any]: The loaded schema.
    """
    schema_path = os.path.join(os.path.dirname(__file__), 'schema.json')
    with open(schema_path, 'r') as f:
        return json.load(f)


def _validate_inputs(resume_text: str, job_description: str) -> None:
    """
    Validate the inputs to ensure they are suitable for optimization.
    
    Args:
        resume_text (str): The resume text to optimize.
        job_description (str): The job description to optimize against.
        
    Raises:
        InputValidationError: If inputs fail validation.
    """
    if not resume_text:
        raise InputValidationError("Resume text cannot be empty")
    if not job_description:
        raise InputValidationError("Job description cannot be empty")
    
    # Validate minimum length for meaningful analysis
    min_resume_length = 50
    min_job_desc_length = 20
    
    if len(resume_text) < min_resume_length:
        raise InputValidationError(f"Resume text too short (min {min_resume_length} chars)")
    if len(job_description) < min_job_desc_length:
        raise InputValidationError(f"Job description too short (min {min_job_desc_length} chars)")


def _parse_llm_response(response_text: str) -> Dict[str, Any]:
    """
    Parse and validate the LLM response against the schema.
    
    Args:
        response_text (str): The raw text response from the LLM.
        
    Returns:
        Dict[str, Any]: The parsed response as a dictionary.
        
    Raises:
        SchemaValidationError: If the response doesn't match the schema.
    """
    # Load schema for validation
    schema = _load_schema()
    
    # Extract JSON from the response (handle potential text before/after JSON)
    try:
        # Try to parse the entire response as JSON first
        result = json.loads(response_text)
    except json.JSONDecodeError:
        # If that fails, try to extract JSON portion using common patterns
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1
        
        if json_start == -1 or json_end <= json_start:
            raise SchemaValidationError("No valid JSON found in LLM response")
        
        json_subset = response_text[json_start:json_end]
        try:
            result = json.loads(json_subset)
        except json.JSONDecodeError:
            raise SchemaValidationError("Failed to parse JSON from LLM response")
    
    # Validate against schema
    try:
        jsonschema.validate(result, schema)
        return result
    except jsonschema.exceptions.ValidationError as e:
        logger.error(f"Schema validation failed: {e}")
        raise SchemaValidationError(f"Response doesn't match schema: {e}")


def optimize_resume(resume_text: str, job_description: str) -> Dict[str, Any]:
    """
    Optimize a resume for a specific job description.
    
    Args:
        resume_text (str): The text content of the resume.
        job_description (str): The text content of the job description.
        
    Returns:
        Dict[str, Any]: Optimization results including suggestions and tweaks.
        
    Raises:
        InputValidationError: If inputs are invalid.
        LLMClientError: If there's an error calling the LLM.
        SchemaValidationError: If LLM response doesn't match the expected schema.
        OptimizerError: For other optimization-related errors.
    """
    try:
        # Validate inputs
        _validate_inputs(resume_text, job_description)
        
        # Generate cache key
        cache_key = generate_cache_key(resume_text, job_description)
        
        # Check cache
        cache = get_default_cache()
        cached_result = cache.get(cache_key)
        if cached_result:
            logger.info("Returning cached optimization result")
            return cached_result
        
        # Build prompt
        prompt = build_prompt(resume_text, job_description)
        
        # Call LLM
        response = call_model(prompt)
        
        # Parse and validate response
        result = _parse_llm_response(response)
        
        # Cache the validated result
        cache.set(cache_key, result, CACHE_TTL_SECONDS)
        
        return result
    
    except (InputValidationError, LLMClientError, SchemaValidationError) as e:
        # Re-raise known exceptions
        raise
    
    except Exception as e:
        # Catch-all for unexpected errors
        logger.exception("Unexpected error during resume optimization")
        raise OptimizerError(f"Resume optimization failed: {str(e)}")
