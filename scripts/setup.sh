#!/bin/bash

# Project setup script

echo "🚀 Setting up your Python project..."

# Check Python version
python_version=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.8 or higher is required. Current version: $python_version"
    exit 1
fi

echo "✅ Python $python_version detected"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Set up pre-commit hooks
echo "🪝 Setting up pre-commit hooks..."
pre-commit install

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "Please edit .env file with your configuration"
fi

# Create data directories
echo "📁 Creating data directories..."
mkdir -p data/{raw,processed,external}
mkdir -p logs

# Run initial tests
echo "🧪 Running initial tests..."
pytest

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Edit .env file with your configuration"
echo "3. Run the application: python src/main.py"
echo "4. Run tests: pytest"
echo "5. Start coding! 🚀"
