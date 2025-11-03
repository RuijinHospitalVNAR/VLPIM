<!-- -*- coding: utf-8 -*- -->
# Contributing to VLPIM

Thank you for your interest in contributing to VLPIM (Variable Length Protein Immunogenicity Modulator)! This document provides guidelines and information for contributors.

## Code of Conduct

This project follows a code of conduct that we expect all contributors to follow. Please be respectful and constructive in all interactions.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Basic knowledge of bioinformatics and protein structure

### Development Setup

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/chufan/VLPIM.git
   cd VLPIM
   ```

3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. Install development dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -e .
   ```

5. Install development tools:
   ```bash
   pip install pytest black flake8 mypy
   ```

## Development Workflow

### Making Changes

1. Create a new branch for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes following the coding standards below

3. Test your changes:
   ```bash
   python -m pytest tests/
   python -m vlpim test
   ```

4. Format and lint your code:
   ```bash
   make format
   make lint
   make type-check
   ```

5. Commit your changes with a descriptive message:
   ```bash
   git add .
   git commit -m "Add feature: brief description of changes"
   ```

6. Push to your fork and create a Pull Request

## Coding Standards

### Python Code Style

- Follow PEP 8 style guidelines
- Use type hints for function parameters and return values
- Write docstrings for all functions and classes
- Use meaningful variable and function names

### Code Formatting

We use `black` for code formatting:
```bash
black src/ tests/ scripts/
```

### Linting

We use `flake8` for linting:
```bash
flake8 src/ tests/ scripts/
```

### Type Checking

We use `mypy` for type checking:
```bash
mypy src/ tests/ scripts/
```

## Testing

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_pipeline.py

# Run with coverage
python -m pytest --cov=src tests/
```

### Writing Tests

- Write tests for new functionality
- Use descriptive test names
- Test both success and failure cases
- Mock external dependencies when appropriate

## Documentation

### Code Documentation

- Write docstrings for all public functions and classes
- Use Google-style docstrings
- Include examples in docstrings when helpful

### User Documentation

- Update README.md for user-facing changes
- Add examples to the examples/ directory
- Update CHANGELOG.md for significant changes

## Pull Request Process

### Before Submitting

1. Ensure all tests pass
2. Run code quality checks (format, lint, type-check)
3. Update documentation if needed
4. Update CHANGELOG.md if applicable

### Pull Request Guidelines

- Use a descriptive title
- Provide a clear description of changes
- Reference any related issues
- Include screenshots for UI changes
- Ensure CI passes

### Review Process

- All PRs require review before merging
- Address reviewer feedback promptly
- Be open to suggestions and improvements

## Reporting Issues

### Bug Reports

When reporting bugs, please include:

- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- System information (OS, Python version, etc.)
- Error messages or logs

### Feature Requests

For feature requests, please include:

- Clear description of the proposed feature
- Use case and motivation
- Potential implementation approach (if known)
- Any relevant references or examples

## External Tool Integration

### Adding New Tools

When integrating new external tools:

1. Create a wrapper module in `src/vlpim/tools/`
2. Follow the existing pattern for tool wrappers
3. Add configuration options to `config_unified.yaml`
4. Update `path_config.py` for path management
5. Add tests for the new wrapper
6. Update documentation

**Important**: VLPIM does not provide installation assistance for external tools. Users must install tools independently and configure their paths.

### Tool Wrapper Guidelines

- Use subprocess for external tool calls
- Implement proper error handling
- Parse tool outputs consistently
- Add timeout handling for long-running processes
- Log tool execution details

## Release Process

### Version Numbering

We follow [Semantic Versioning](https://semver.org/):
- MAJOR: Incompatible API changes
- MINOR: New functionality in a backwards compatible manner
- PATCH: Backwards compatible bug fixes

### Release Checklist

1. Update version numbers in `pyproject.toml` and `setup.py`
2. Update CHANGELOG.md
3. Run full test suite
4. Create release tag
5. Build and test distribution packages

## Getting Help

- Check existing issues and discussions
- Join our community discussions
- Contact maintainers for questions

## License

By contributing to VLPIM, you agree that your contributions will be licensed under the MIT License.
