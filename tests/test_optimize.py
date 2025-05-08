"""
Tests for the optimize.py module.
"""
import pytest
from unittest.mock import patch, MagicMock
from optimize import optimize_resume

class DummyLLMClient:
    def __init__(self, model_name):
        self.model_name = model_name
    
    def generate(self, prompt):
        return "# Optimized Resume\n\n- This is dummy output"

@pytest.fixture(autouse=True)
def patch_llm_client(monkeypatch):
    # Set testing mode environment variable
    monkeypatch.setenv("TESTING", "true")
    
    # Stub out the real LLM client
    mock_client = DummyLLMClient("test-model")
    monkeypatch.setattr('optimize.client', mock_client)

def test_optimize_resume_basic():
    resume = "Name: Jane Doe\nExperience: Python developer."
    jd = "Looking for a Python developer."
    prompt = "RESUME:\n{resume_text}\n\nJOB DESCRIPTION:\n{job_description}"
    
    result = optimize_resume(resume, jd, prompt)
    
    assert result == "# Optimized Resume\n\n- This is dummy output"
    assert isinstance(result, str)
    assert len(result) > 0
    prompt = "Resume: {resume_text}\nJD: {job_description}"
    output = optimize_resume(resume, jd, prompt)
    assert output.startswith("# Optimized Resume")
    assert "- This is dummy output" in output