# Resume Optimizer - Technical Documentation

> **Note**: For complete usage documentation, installation instructions, and examples, see the [main project README](../README.md#resume-optimizer-package).

This document contains technical details specific to the Resume Optimizer package for developers working on this component.

## Architecture Details

### Core Components

- `prompt_builder.py`: Manages LLM prompt templates and construction
- `cache.py`: Provides in-memory caching (designed for easy upgrade to Redis)
- `llm_client.py`: Handles Gemini API communication with error handling and retries
- `optimizer.py`: Orchestrates the optimization process and response validation
- `schema.json`: Defines the expected JSON output structure for LLM responses
- `config.py`: Manages configuration from environment variables with defaults

### File Structure

```
resume_optimizer/
├── __init__.py           # Package entry point
├── __main__.py          # CLI interface
├── cache.py             # Caching implementation
├── config.py            # Configuration management
├── llm_client.py        # Gemini API client
├── optimizer.py         # Main optimization logic
├── prompt_builder.py    # Prompt construction
├── schema.json          # Response validation schema
└── tests/              # Unit tests
    ├── test_cache.py
    ├── test_llm_client.py
    ├── test_optimizer.py
    └── test_prompt_builder.py
```

## Implementation Details

### Error Handling

The package implements comprehensive error handling:
- **API Errors**: Automatic retries with exponential backoff
- **Schema Validation**: Ensures LLM responses conform to expected structure
- **Timeout Handling**: Configurable request timeouts
- **Cache Failures**: Graceful degradation when cache is unavailable

### Performance Considerations

- **Caching**: Results are cached to avoid redundant API calls
- **Request Optimization**: Efficient prompt construction to minimize token usage
- **Async Ready**: Architecture supports future async implementation

### Testing Strategy

- **Unit Tests**: Individual component testing with mocks
- **Integration Tests**: End-to-end testing with real API calls (when configured)
- **Schema Tests**: Validation of response format compliance
- **Error Scenarios**: Testing of failure modes and recovery

## Development Setup

### Running Tests

```bash
# Run all tests
pytest resume_optimizer/tests/

# Run specific test file
pytest resume_optimizer/tests/test_optimizer.py

# Run with coverage
pytest --cov=resume_optimizer resume_optimizer/tests/ --cov-report=html

# Run integration tests (requires API key)
GEMINI_API_KEY=your_key pytest resume_optimizer/tests/test_integration.py
```

### Code Quality

```bash
# Format code
black resume_optimizer/

# Lint code
flake8 resume_optimizer/

# Type checking
mypy resume_optimizer/
```

## Configuration Details

### Environment Variables

All configuration is handled through environment variables with sensible defaults:

```python
# Core API settings
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # Required
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "models/gemini-1.5-flash")

# Performance tuning
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "3600"))
REQUEST_TIMEOUT_SECONDS = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "30"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
BACKOFF_FACTOR = float(os.getenv("BACKOFF_FACTOR", "0.5"))

# LLM parameters
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.2"))
MAX_OUTPUT_TOKENS = int(os.getenv("MAX_OUTPUT_TOKENS", "2048"))
```

## Future Improvements

### Planned Features

- **Multi-Provider Support**: Add support for OpenAI, Claude, and other LLM providers
- **Advanced Caching**: Redis backend for distributed caching
- **Template Management**: User-defined optimization templates
- **Streaming Responses**: Handle large resume optimizations with streaming
- **Batch Processing**: Optimize multiple resumes simultaneously
- **Custom Prompts**: Allow users to define custom optimization prompts

### Architecture Evolution

- **Plugin System**: Extensible architecture for custom optimization strategies
- **Metrics Collection**: Track optimization performance and success rates
- **A/B Testing**: Framework for testing different optimization approaches
- **API Server**: REST API for integration with web applications

## Troubleshooting

### Common Issues

1. **API Key Issues**
   ```
   Error: GEMINI_API_KEY environment variable not set
   Solution: Set your Gemini API key in environment variables
   ```

2. **Timeout Errors**
   ```
   Error: Request timeout after 30 seconds
   Solution: Increase REQUEST_TIMEOUT_SECONDS or check network connectivity
   ```

3. **Schema Validation Failures**
   ```
   Error: LLM response doesn't match expected schema
   Solution: Check if the model is responding in the correct format
   ```

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

from resume_optimizer import optimize_resume
result = optimize_resume(resume_text, job_description)
```

## Contributing

When contributing to this package:

1. **Add Tests**: All new features must include comprehensive tests
2. **Update Schema**: If changing response format, update `schema.json`
3. **Document Changes**: Update this README for architectural changes
4. **Performance**: Consider caching and API efficiency for new features
5. **Backwards Compatibility**: Maintain API compatibility when possible

For contribution guidelines and setup instructions, see the [main project documentation](../README.md#contributing--future-improvements).
