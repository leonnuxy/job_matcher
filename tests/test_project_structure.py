"""
Tests for the project structure.
"""
import os
import pytest


def test_project_structure():
    """Test that the project has the expected structure."""
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Check required files exist
    assert os.path.isfile(os.path.join(base_path, 'config.py'))
    assert os.path.isfile(os.path.join(base_path, 'prompt.txt'))
    assert os.path.isfile(os.path.join(base_path, 'optimize.py'))
    assert os.path.isfile(os.path.join(base_path, 'main.py'))
    assert os.path.isfile(os.path.join(base_path, 'requirements.txt'))
    
    # Check data directory structure
    assert os.path.isdir(os.path.join(base_path, 'data'))
    assert os.path.isfile(os.path.join(base_path, 'data', 'resume.txt'))
    assert os.path.isdir(os.path.join(base_path, 'data', 'job_descriptions'))
    assert os.path.isfile(os.path.join(base_path, 'data', 'job_descriptions', 'job_description.txt'))


def test_config_loads_api_key():
    """Test that the config module loads the API key from environment variables."""
    import os
    from unittest.mock import patch
    import sys
    
    # Import the function to test
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from config import get_api_key
    
    # Setup environment with mock API key for Gemini
    with patch.dict(os.environ, {'GEMINI_API_KEY': 'test_key', 'LLM_PROVIDER': 'gemini'}):
        assert get_api_key() == 'test_key'
        
    # Setup environment with mock API key for OpenAI
    with patch.dict(os.environ, {'OPENAI_API_KEY': 'test_openai_key', 'LLM_PROVIDER': 'openai'}):
        assert get_api_key() == 'test_openai_key'


def test_config_raises_error_when_missing_key():
    """Test that the config module raises RuntimeError when API key is missing."""
    import os
    from unittest.mock import patch
    import pytest
    import sys
    
    # Import the module
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from config import get_api_key
    
    # Test with empty environment for Gemini provider
    with patch.dict(os.environ, {'LLM_PROVIDER': 'gemini'}, clear=True):
        with pytest.raises(RuntimeError) as excinfo:
            get_api_key()
        
        assert "GEMINI_API_KEY environment variable is not set" in str(excinfo.value)
    
    # Test with empty environment for OpenAI provider
    with patch.dict(os.environ, {'LLM_PROVIDER': 'openai'}, clear=True):
        with pytest.raises(RuntimeError) as excinfo:
            get_api_key()
        
        assert "OPENAI_API_KEY environment variable is not set" in str(excinfo.value)
