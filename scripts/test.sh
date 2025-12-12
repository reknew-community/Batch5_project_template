#!/bin/bash

# Test runner script

echo "🧪 Running tests..."

# Run linting
echo "🔍 Running linting..."
flake8 src tests

# Run formatting check
echo "🎨 Checking code formatting..."
black --check src tests

# Run import sorting check
echo "📦 Checking import sorting..."
isort --check-only src tests

# Run type checking
echo "🔤 Running type checking..."
mypy src

# Run security check
echo "🛡️ Running security check..."
bandit -r src

# Run tests with coverage
echo "🏃 Running tests with coverage..."
pytest --cov=src --cov-report=term-missing --cov-report=html

echo "✅ All checks completed!"
