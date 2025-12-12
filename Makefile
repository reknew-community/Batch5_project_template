.PHONY: help install install-dev test lint format type-check clean docs docker-build docker-run

help: ## Show this help message
	@echo 'Usage: make [target] ...'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install production dependencies
	pip install -r requirements.txt

install-dev: ## Install development dependencies
	pip install -r requirements.txt -r requirements-dev.txt
	pre-commit install

test: ## Run tests
	pytest

test-cov: ## Run tests with coverage
	pytest --cov=src --cov-report=html --cov-report=term

lint: ## Run linting
	flake8 src tests
	pylint src

format: ## Format code
	black src tests
	isort src tests

type-check: ## Run type checking
	mypy src

security: ## Run security checks
	bandit -r src

clean: ## Clean up cache files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf htmlcov
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info

docs: ## Build documentation
	cd docs && make html

docker-build: ## Build Docker image
	docker build -t your-project .

docker-run: ## Run Docker container
	docker run -p 8000:8000 your-project

docker-compose-up: ## Start services with docker-compose
	docker-compose up -d

docker-compose-down: ## Stop services with docker-compose
	docker-compose down

all-checks: format lint type-check security test ## Run all code quality checks
