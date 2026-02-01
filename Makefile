.PHONY: help install install-dev test lint format clean run build

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install the package in development mode
	pip install -e .

install-dev: ## Install the package with development dependencies
	pip install -e ".[dev]"

test: ## Run tests
	pytest tests/ -v

lint: ## Run linting checks
	flake8 src/ tests/
	mypy src/

format: ## Format code with black and isort
	black src/ tests/
	isort src/ tests/

clean: ## Clean up build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

run: ## Run the Streamlit application
	streamlit run src/app/main.py

build: ## Build the package
	python -m build

check: format lint test ## Run all checks (format, lint, test)

pre-commit: ## Install pre-commit hooks
	pre-commit install
	pre-commit run --all-files 