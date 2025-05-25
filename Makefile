.PHONY: help install test test-verbose test-coverage clean lint format check-format install-dev uninstall

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install the plugin in development mode
	llm install -e .

install-dev:  ## Install development dependencies
	pip install -r requirements.txt
	pip install pytest pytest-cov black isort flake8

uninstall:  ## Uninstall the plugin
	llm uninstall llm-io-intelligence

test:  ## Run tests
	pytest -vv --tb=short --maxfail=1

test-verbose:  ## Run tests with verbose output
	pytest -vv --tb=long

test-coverage:  ## Run tests with coverage report
	pytest --cov=llm_io_intelligence --cov-report=html --cov-report=term

test-vision:  ## Test vision functionality (requires API key)
	@echo "Testing vision models..."
	llm 'Describe this image briefly' -a https://static.simonwillison.net/static/2024/pelicans.jpg -m llama-3.2-90b-vision

test-streaming:  ## Test streaming functionality (requires API key)
	@echo "Testing streaming..."
	llm 'Count to 5' -m llama-3.3-70b

test-embeddings:  ## Test embedding functionality (requires API key)
	@echo "Testing embeddings..."
	llm embed -m bge-multilingual-gemma2 "Hello world"

lint:  ## Run linting
	flake8 llm_io_intelligence.py test_io_intelligence.py

format:  ## Format code with black and isort
	black llm_io_intelligence.py test_io_intelligence.py
	isort llm_io_intelligence.py test_io_intelligence.py

check-format:  ## Check if code is properly formatted
	black --check llm_io_intelligence.py test_io_intelligence.py
	isort --check-only llm_io_intelligence.py test_io_intelligence.py

clean:  ## Clean up build artifacts and cache
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf __pycache__/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete

models:  ## List available models
	llm models list | grep "io-intelligence"

plugins:  ## Show installed LLM plugins
	llm plugins

setup-env:  ## Show environment setup instructions
	@echo "Set up your environment:"
	@echo "export IOINTELLIGENCE_API_KEY='your-api-key-here'"
	@echo ""
	@echo "Get your API key from: https://ai.io.net/ai-api-keys"

check-env:  ## Check if environment is properly configured
	@if [ -z "$$IOINTELLIGENCE_API_KEY" ]; then \
		echo "❌ IOINTELLIGENCE_API_KEY not set"; \
		echo "Run: export IOINTELLIGENCE_API_KEY='your-api-key'"; \
		exit 1; \
	else \
		echo "✅ IOINTELLIGENCE_API_KEY is set"; \
	fi

build:  ## Build the package
	python -m build

release-check:  ## Check if ready for release
	@echo "Checking release readiness..."
	@make check-format
	@make lint
	@make test
	@echo "✅ Ready for release!"

all-tests:  ## Run all tests including manual API tests
	@make test
	@make check-env
	@make test-vision
	@make test-streaming
	@make test-embeddings 