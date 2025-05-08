"""
Tests for the llm_client.py module.
"""
import os
import pytest
from unittest.mock import patch, MagicMock

@pytest.fixture(autouse=True)
def setup_testing_env(monkeypatch):
    """Set up the testing environment."""
    monkeypatch.setenv("TESTING", "true")

def test_llm_client_initialization():
    """Test LLMClient initialization."""
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from llm_client import LLMClient
    
    client = LLMClient("test-model")
    assert client.model_name == "test-model"

def test_llm_client_generate_in_test_mode():
    """Test LLMClient generate method in test mode."""
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from llm_client import LLMClient
    
    client = LLMClient("test-model")
    result = client.generate("This is a test prompt")
    
    assert "# Optimized Resume" in result
    assert "dummy output" in result

def test_llm_provider_selection():
    """Test LLM provider selection logic."""
    with patch.dict(os.environ, {"TESTING": "true"}):
        import sys
        import importlib
        
        # Remove previously imported module if it exists
        if 'llm_client' in sys.modules:
            del sys.modules['llm_client']
        
        # Test Gemini provider
        with patch.dict(os.environ, {"LLM_PROVIDER": "gemini", "GEMINI_API_KEY": "test_key"}):
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            llm_client = importlib.import_module('llm_client')
            assert llm_client.LLM_PROVIDER == "gemini"
        
        # Remove module to reload with new environment
        if 'llm_client' in sys.modules:
            del sys.modules['llm_client']
        
        # Test OpenAI provider
        with patch.dict(os.environ, {"LLM_PROVIDER": "openai", "OPENAI_API_KEY": "test_key"}):
            llm_client = importlib.import_module('llm_client')
            assert llm_client.LLM_PROVIDER == "openai"
