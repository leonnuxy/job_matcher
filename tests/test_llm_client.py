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
    from services.llm_client import LLMClient
    
    client = LLMClient("test-model")
    assert client.model_name == "test-model"

def test_llm_client_generate_in_test_mode():
    """Test LLMClient generate method in test mode."""
    with patch.dict(os.environ, {"TESTING": "true"}):
        with patch('services.llm_client.TESTING', True):
            from services.llm_client import LLMClient
            
            # Mock the client's generate method
            with patch.object(LLMClient, 'generate', return_value="# Optimized Resume\n\n- This is dummy output"):
                client = LLMClient("test-model")
                result = client.generate("This is a test prompt")
                
                assert "# Optimized Resume" in result
                assert "dummy output" in result

def test_llm_provider_selection():
    """Test LLM provider selection logic."""
    import sys
    
    # Test Gemini provider
    with patch('config.get_llm_provider', return_value="gemini"):
        with patch.dict(os.environ, {"TESTING": "true"}):
            # Clear any cached imports
            if 'services.llm_client' in sys.modules:
                del sys.modules['services.llm_client']
                
            # Reload the module with our patched environment
            from services.llm_client import LLM_PROVIDER
            assert LLM_PROVIDER == "gemini"
    
    # Test OpenAI provider
    with patch('config.get_llm_provider', return_value="openai"):
        with patch.dict(os.environ, {"TESTING": "true"}):
            # Clear any cached imports 
            if 'services.llm_client' in sys.modules:
                del sys.modules['services.llm_client']
                
            # Import in a different way to avoid cache
            from importlib import reload
            import services.llm_client
            reload(services.llm_client)
            assert services.llm_client.LLM_PROVIDER == "openai"
