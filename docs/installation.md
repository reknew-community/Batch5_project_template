# Installation Guide

## Requirements

- Python 3.8 or higher
- pip (Python package installer)

## Quick Installation

```bash
# Clone the repository
git clone https://github.com/your-username/your-project.git
cd your-project

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Development Installation

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run tests to verify installation
pytest
```

## Configuration

1. Copy `.env.example` to `.env`
2. Edit `.env` with your configuration
3. Run the application: `python src/main.py`
