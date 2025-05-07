"""
Example of how to extend the resume optimizer schema.

This demonstrates how to customize the schema to add additional fields
or modify validation requirements.
"""

import os
import sys
import json
from pathlib import Path

# Add the parent directory to the path so we can import resume_optimizer
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from resume_optimizer import optimize_resume
from resume_optimizer.optimizer import _load_schema, _parse_llm_response
import jsonschema


def extend_schema(custom_fields, required_fields=None):
    """
    Extend the base schema with custom fields.
    
    Args:
        custom_fields (dict): Custom fields to add to the schema
        required_fields (list, optional): List of field names to add to required list
        
    Returns:
        dict: Extended schema
    """
    # Load the base schema
    schema = _load_schema()
    
    # Add custom fields to the schema properties
    for field_name, field_schema in custom_fields.items():
        schema["properties"][field_name] = field_schema
    
    # Add new required fields if specified
    if required_fields:
        for field in required_fields:
            if field not in schema["required"]:
                schema["required"].append(field)
    
    return schema


def custom_schema_example():
    """Example of extending the resume optimizer schema."""
    # Define custom fields to add to the schema
    custom_fields = {
        "salary_range": {
            "type": "object",
            "properties": {
                "min": {"type": "number"},
                "max": {"type": "number"},
                "currency": {"type": "string"}
            },
            "required": ["min", "max"]
        },
        "interview_tips": {
            "type": "array",
            "items": {"type": "string"}
        }
    }
    
    # Define which fields should be required
    required_fields = ["interview_tips"]
    
    # Extend the schema
    extended_schema = extend_schema(custom_fields, required_fields)
    
    # Create an example result that includes the custom fields
    example_result = {
        "summary": "Your resume is a good match for the job description.",
        "skills_to_add": ["Docker", "Kubernetes"],
        "skills_to_remove": ["jQuery"],
        "experience_tweaks": [
            {
                "original": "Developed web applications",
                "optimized": "Developed scalable web applications with React and Node.js"
            }
        ],
        "formatting_suggestions": ["Use bullet points for skills"],
        "collaboration_points": ["Highlight teamwork experience"],
        "salary_range": {
            "min": 80000,
            "max": 110000,
            "currency": "USD"
        },
        "interview_tips": [
            "Prepare examples of your experience with Docker",
            "Be ready to discuss your approach to scalability"
        ]
    }
    
    # Validate the example result against the extended schema
    try:
        jsonschema.validate(example_result, extended_schema)
        print("✓ Extended schema validation passed!")
        print("\nExtended schema:")
        print(json.dumps(extended_schema, indent=2))
        print("\nValid example result:")
        print(json.dumps(example_result, indent=2))
    except jsonschema.exceptions.ValidationError as e:
        print(f"✗ Extended schema validation failed: {e}")
    
    # Test validation with missing required fields
    invalid_result = example_result.copy()
    del invalid_result["interview_tips"]  # Remove a required field
    
    try:
        jsonschema.validate(invalid_result, extended_schema)
        print("\n✓ Validation passed for invalid result (should fail)")
    except jsonschema.exceptions.ValidationError as e:
        print(f"\n✓ Validation correctly failed for invalid result: {e}")


if __name__ == "__main__":
    custom_schema_example()
