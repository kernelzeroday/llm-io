# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Vision/Multimodal Support**: Complete support for image processing with vision models
  - Support for `llama-3.2-90b-vision` and `qwen2-vl-7b` models
  - Image input via URLs, local files, and binary content
  - Support for JPEG, PNG, GIF, and WebP formats
  - Multiple image attachments in single requests
  - Base64 encoding for local images
  - OpenAI-compatible vision message format
- Comprehensive `.gitignore` file for Python development
- Enhanced documentation with vision examples
- Attachment type validation and error handling

### Fixed
- JSON serialization issues with prompt options
- Generator-based execute method for proper streaming
- Test suite compatibility with new attachment handling
- Indentation and regex pattern matching in tests

### Changed
- Updated README with comprehensive vision documentation
- Improved error messages and logging
- Enhanced test coverage for multimodal functionality

## [1.0.0] - 2024-01-XX

### Added
- Initial release of LLM IO Intelligence plugin
- Support for 31+ language models from IO Intelligence API
- Support for 2 embedding models
- Real-time streaming responses
- Full OpenAI API compatibility
- Comprehensive error handling and logging
- Extensive model options (temperature, max_tokens, penalties, etc.)
- Complete test suite with 21+ tests
- Development environment setup
- Plugin registration and model discovery

### Models Supported
#### Text Models
- Llama 4 Maverick, Llama 3.3, Llama 3.1 Nemotron
- DeepSeek R1, DeepSeek R1 Distill variants
- Qwen 3, Qwen 2.5 variants
- Mistral Large, Ministral
- Phi 4, Phi 3.5 Mini
- Gemma 3, GLM 4
- And many more...

#### Embedding Models
- BGE Multilingual Gemma2
- MxBai Embed Large v1

### Features
- Streaming and non-streaming responses
- System prompts and conversation history
- Temperature, top-p, frequency/presence penalties
- Reasoning content support
- Comprehensive error handling
- Extensive logging and debugging
- Python API and CLI support 