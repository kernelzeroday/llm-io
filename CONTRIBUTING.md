# Contributing to LLM IO Intelligence Plugin

Thank you for your interest in contributing to the LLM IO Intelligence plugin! This document provides guidelines and information for contributors.

## Development Setup

### Prerequisites
- Python 3.8 or higher
- Git
- An IO Intelligence API key

### Setting up the Development Environment

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd llm-io-intelligence
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Install the plugin in development mode**:
   ```bash
   llm install -e .
   ```

5. **Set up environment variables**:
   ```bash
   export IOINTELLIGENCE_API_KEY="your-api-key-here"
   ```

## Testing

### Running Tests

We use pytest for testing. Run the full test suite:

```bash
# Run all tests
pytest -vv --tb=short --maxfail=1

# Run specific test class
pytest -vv test_io_intelligence.py::TestIOIntelligenceModel

# Run with coverage
pytest --cov=llm_io_intelligence --cov-report=html
```

### Test Structure

- `test_io_intelligence.py` - Main test suite
- `test_streaming.py` - Streaming functionality tests
- `direct_streaming_test.py` - Direct streaming tests

### Writing Tests

When adding new features:

1. **Write tests first** (TDD approach)
2. **Test edge cases** and error conditions
3. **Mock external API calls** to avoid hitting rate limits
4. **Use descriptive test names** that explain what is being tested
5. **Follow the existing test patterns** in the codebase

Example test structure:
```python
class TestNewFeature:
    def setup_method(self):
        self.model = IOIntelligenceModel("test-model", "test", 1000)
    
    @patch.dict(os.environ, {"IOINTELLIGENCE_API_KEY": "test-key"})
    def test_new_feature_success(self):
        # Test implementation
        pass
    
    def test_new_feature_error_handling(self):
        # Test error cases
        pass
```

## Code Style

### Python Style Guidelines

- Follow [PEP 8](https://pep8.org/) style guidelines
- Use type hints where appropriate
- Write docstrings for public functions and classes
- Keep functions focused and small
- Use descriptive variable and function names

### Code Formatting

We recommend using:
- `black` for code formatting
- `isort` for import sorting
- `flake8` for linting

```bash
# Format code
black llm_io_intelligence.py test_io_intelligence.py

# Sort imports
isort llm_io_intelligence.py test_io_intelligence.py

# Lint code
flake8 llm_io_intelligence.py
```

## Adding New Models

To add support for new models:

1. **Update the models list** in `register_models()`:
   ```python
   models = [
       # ... existing models ...
       ("new-model-id", "provider/full-model-name", context_length),
   ]
   ```

2. **Add tests** for the new model:
   ```python
   def test_new_model_registration(self):
       # Test that the model is properly registered
       pass
   ```

3. **Update documentation** in README.md
4. **Test the model** manually to ensure it works

## Adding New Features

### Feature Development Process

1. **Create an issue** describing the feature
2. **Fork the repository** and create a feature branch
3. **Implement the feature** with tests
4. **Update documentation** as needed
5. **Submit a pull request**

### Vision/Multimodal Features

When working with vision features:

- Test with multiple image formats (JPEG, PNG, GIF, WebP)
- Test with both URLs and local files
- Handle base64 encoding properly
- Test with multiple attachments
- Ensure proper error handling for unsupported formats

### API Compatibility

- Maintain OpenAI API compatibility
- Follow existing patterns for options and parameters
- Ensure backward compatibility when possible
- Document any breaking changes

## Documentation

### README Updates

When adding features:
- Update the features list
- Add usage examples
- Update the model list if applicable
- Add any new configuration options

### Code Documentation

- Write clear docstrings for public APIs
- Include type hints
- Document complex algorithms or logic
- Add inline comments for non-obvious code

## Pull Request Guidelines

### Before Submitting

1. **Run all tests** and ensure they pass
2. **Update documentation** as needed
3. **Add tests** for new functionality
4. **Follow code style** guidelines
5. **Write clear commit messages**

### Pull Request Template

```
## Description
Brief description of the changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] New tests added for new functionality
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
```

## Release Process

### Version Numbering

We follow [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Run full test suite
4. Create release tag
5. Update documentation

## Getting Help

- **Issues**: Create a GitHub issue for bugs or feature requests
- **Discussions**: Use GitHub Discussions for questions
- **Documentation**: Check the README and code comments

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Follow the project's coding standards

Thank you for contributing to the LLM IO Intelligence plugin! 