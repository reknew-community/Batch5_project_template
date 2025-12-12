# Contributing to Your Project

Thank you for considering contributing to this project! Here are some guidelines to help you get started.

## Development Setup

1. Fork the repository
2. Clone your fork: `git clone https://github.com/your-username/your-project.git`
3. Run the setup script: `./scripts/setup.sh`
4. Create a branch: `git checkout -b feature/your-feature`

## Code Style

- Follow PEP 8 style guidelines
- Use Black for code formatting: `black src tests`
- Sort imports with isort: `isort src tests`
- Run linting with flake8: `flake8 src tests`
- Add type hints and run mypy: `mypy src`

## Testing

- Write tests for new features
- Run tests: `pytest`
- Ensure good test coverage: `pytest --cov=src`
- Add integration tests when appropriate

## Pull Request Process

1. Update documentation if needed
2. Add tests for new functionality
3. Ensure all tests pass
4. Update CHANGELOG.md if applicable
5. Submit pull request with clear description

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow

## Questions?

Feel free to open an issue for any questions or discussions.
