#!/usr/bin/env python3
"""
Test suite for cover letter generation functionality.
"""
import os
import sys
import pytest

# Add parent directory to sys.path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from services.cover_letter import (
    load_cover_letter_template,
    generate_cover_letter,
    save_cover_letter,
    validate_template_fields,
    check_missing_fields
)
from job_search.run import main as run_job_search
from job_search.matcher import optimize_for_job, load_resume

# Set up test environment
os.environ["TESTING"] = "1"
os.environ["SIMULATION_MODE"] = "1"

def test_cover_letter_flow():
    """Test the end-to-end flow of cover letter generation."""
    # Set up test paths
    test_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(test_dir)
    out_dir = os.path.join(base_dir, "data", "optimization_results")
    resume_path = os.path.join(base_dir, "data", "resume.txt")

    # Ensure resume exists
    if not os.path.exists(resume_path):
        with open(resume_path, "w") as f:
            f.write("Test Resume Content")

    # Create a mock job description
    mock_job = {
        "title": "Software Engineer",
        "company": "TechCorp Inc.",
        "location": "Remote",
        "description": "Looking for a skilled software engineer...",
        "snippet": "Join our innovative team..."
    }

    # Load resume
    resume = load_resume()
    assert resume is not None, "Failed to load resume"

    # Test template loading
    template = load_cover_letter_template()
    assert template is not None, "Failed to load cover letter template"

    # Test cover letter generation
    cover_letter = generate_cover_letter(mock_job, template)
    assert "TechCorp Inc." in cover_letter, "Company name not found in cover letter"
    assert "Software Engineer" in cover_letter, "Job title not found in cover letter"

    # Test file generation
    optimized_md, resume_path, cover_letter_path = optimize_for_job(resume, mock_job, True)
    
    assert optimized_md is not None, "Failed to generate optimized resume"
    assert resume_path is not None, "Failed to save resume"
    assert cover_letter_path is not None, "Failed to save cover letter"
    assert os.path.exists(resume_path), f"Resume file not found at {resume_path}"
    assert os.path.exists(cover_letter_path), f"Cover letter file not found at {cover_letter_path}"

def test_default_values():
    """Test that the cover letter generator handles missing job information gracefully."""
    # Create a minimal job description
    minimal_job = {
        "title": "Developer"
    }

    template = load_cover_letter_template()
    assert template is not None, "Failed to load cover letter template"

    # Generate cover letter with minimal info
    cover_letter = generate_cover_letter(minimal_job, template)
    
    # Check that default values were used
    assert "your company" in cover_letter.lower(), "Default company name not found"
    assert "developer" in cover_letter.lower(), "Job title not found"
    assert "dear" in cover_letter.lower(), "Salutation not found"

def test_placeholder_handling():
    """Test that the template processor handles various placeholder formats correctly."""
    job = {
        "title": "ML Engineer",
        "company": "AI Corp",
        "location": "San Francisco",
        "extra_field": "Should not appear"
    }

    # Test with missing template
    cover_letter = generate_cover_letter(job, None)
    assert "error" in cover_letter.lower(), "Should handle missing template gracefully"

    # Test with valid template
    template = load_cover_letter_template()
    assert template is not None, "Failed to load cover letter template"
    
    cover_letter = generate_cover_letter(job, template)
    assert "ML Engineer" in cover_letter, "Job title not found"
    assert "AI Corp" in cover_letter, "Company name not found"
    assert "San Francisco" in cover_letter, "Location not found"
    assert "extra_field" not in cover_letter, "Unexpected field found"

def test_template_field_validation():
    """Test that the template validation functions work correctly."""
    # Test with a simple template
    template = """
    Dear {{hiring_team|Hiring Team}},
    
    I am writing to apply for the {{role_title}} position at {{company_name}}.
    
    Best regards,
    {{applicant_name}}
    """
    
    # Test field extraction
    fields = validate_template_fields(template)
    assert fields == {"hiring_team", "role_title", "company_name", "applicant_name"}
    
    # Test missing field detection
    available_fields = {"hiring_team", "role_title", "other_field"}
    missing_fields = check_missing_fields(fields, available_fields)
    assert set(missing_fields) == {"company_name", "applicant_name"}
    
    # Test full generation with missing fields
    job_data = {
        "title": "Software Engineer",
        "company": "TechCorp"
    }
    
    result = generate_cover_letter(job_data, template)
    assert "Software Engineer" in result
    assert "TechCorp" in result
    assert "Best regards" in result  # Template structure preserved
    assert result.count("{{") == 0  # All placeholders replaced

if __name__ == "__main__":
    pytest.main([__file__])
