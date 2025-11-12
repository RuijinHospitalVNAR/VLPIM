# Contributing to VLPIM

Thank you for your interest in contributing to VLPIM (Variable Length Protein Immunogenicity Modulator)! This document provides guidelines and information for contributors.

## Contents

<!-- TOC -->

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
  * [Prerequisites](#prerequisites)
  * [Development Setup](#development-setup)
- [Development Workflow](#development-workflow)
  * [Making Changes](#making-changes)
  * [Coding Standards](#coding-standards)
  * [Testing](#testing)
  * [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)
- [Reporting Issues](#reporting-issues)
- [External Tool Integration](#external-tool-integration)
- [Release Process](#release-process)
- [Getting Help](#getting-help)

<!-- TOC -->

---

## Code of Conduct

This project follows a code of conduct that we expect all contributors to follow. Please be respectful and constructive in all interactions.

---

## Getting Started

### Prerequisites

- **Python**: 3.8 or higher
- **Git**: For version control
- **Basic knowledge**: Bioinformatics and protein structure
- **External Tools**: See [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md) for required external tools

### Development Setup

1. **Fork the repository** on GitHub

2. **Clone your fork locally:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/VLPIM.git
   cd VLPIM
   ```

3. **Add upstream remote:**
   ```bash
   git remote add upstream https://github.com/RuijinHospitalVNAR/VLPIM.git
   ```

4. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

5. **Install dependencies:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   pip install -e .
   ```

6. **Install development tools:**
   ```bash
   pip install pytest black flake8 mypy
   ```

7. **Set up external tools:**
   
   Follow the [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md) to install and configure external tools (ProteinMPNN, NetMHCIIpan, AlphaFold3, Rosetta).

8. **Verify setup:**
   ```bash
   python -m vlpim validate
   python -m pytest tests/
   ```

---

## Development Workflow

### Making Changes

1. **Update your fork:**
   ```bash
   git checkout main
   git pull upstream main
   ```

2. **Create a new branch:**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/bug-description
   ```

3. **Make your changes** following the coding standards below

4. **Test your changes:**
   ```bash
   python -m pytest tests/
   python -m vlpim test
   ```

5. **Format and lint your code:**
   ```bash
   make format
   make lint
   make type-check
   ```

6. **Commit your changes:**
   ```bash
   git add .
   git commit -m "Add feature: brief description of changes"
   ```
   
   **Commit message guidelines:**
   - Use present tense ("Add feature" not "Added feature")
   - Use imperative mood ("Fix bug" not "Fixes bug")
   - Keep first line under 50 characters
   - Add detailed description if needed

7. **Push to your fork:**
   ```bash
   git push origin feature/your-feature-name
   ```

8. **Create a Pull Request** on GitHub

---

## Coding Standards

### Python Code Style

- **Follow PEP 8** style guidelines
- **Use type hints** for function parameters and return values
- **Write docstrings** for all functions and classes (Google-style)
- **Use meaningful names** for variables and functions
- **Keep functions focused** - one responsibility per function
- **Limit line length** to 88 characters (Black default)

### Code Formatting

We use `black` for automatic code formatting:

```bash
# Format all Python files
black src/ tests/ scripts/

# Check formatting without making changes
black --check src/ tests/ scripts/
```

**Configuration:** Black is configured in `pyproject.toml`

### Linting

We use `flake8` for linting:

```bash
# Lint all Python files
flake8 src/ tests/ scripts/

# Show statistics
flake8 --statistics src/ tests/ scripts/
```

**Configuration:** Flake8 configuration is in `setup.cfg` or `.flake8`

### Type Checking

We use `mypy` for static type checking:

```bash
# Type check all Python files
mypy src/ tests/ scripts/

# Show error summary
mypy --show-error-summary src/
```

**Configuration:** Mypy configuration is in `pyproject.toml`

### Example Code Structure

```python
"""Module docstring describing the module's purpose."""

from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


def example_function(param1: str, param2: Optional[int] = None) -> List[str]:
    """
    Brief description of the function.
    
    Args:
        param1: Description of param1
        param2: Description of param2 (optional)
    
    Returns:
        Description of return value
    
    Raises:
        ValueError: When param1 is invalid
    
    Example:
        >>> result = example_function("test", 42)
        >>> print(result)
        ['test', '42']
    """
    if not param1:
        raise ValueError("param1 cannot be empty")
    
    result = [param1]
    if param2 is not None:
        result.append(str(param2))
    
    return result
```

---

## Testing

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_pipeline.py

# Run specific test function
python -m pytest tests/test_pipeline.py::test_specific_function

# Run with coverage
python -m pytest --cov=src --cov-report=html tests/

# Run with verbose output
python -m pytest -v tests/

# Run tests matching a pattern
python -m pytest -k "test_epitope" tests/
```

### Writing Tests

**Guidelines:**
- Write tests for all new functionality
- Use descriptive test names: `test_function_name_scenario`
- Test both success and failure cases
- Mock external dependencies when appropriate
- Use fixtures for common setup/teardown
- Aim for high code coverage (>80%)

**Example Test:**

```python
import pytest
from unittest.mock import Mock, patch
from vlpim.tools.protein_mpnn_wrapper import generate_mutants


def test_generate_mutants_success():
    """Test successful mutant generation."""
    # Arrange
    pdb_path = "test.pdb"
    epitopes = [{"sequence": "MKLLVL", "start": 1, "end": 6}]
    
    # Act
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = Mock(returncode=0, stdout=">seq1\nMKLLVL")
        result = generate_mutants(pdb_path, epitopes, "reduce")
    
    # Assert
    assert len(result) > 0
    assert "MKLLVL" in result[0]


def test_generate_mutants_failure():
    """Test mutant generation failure handling."""
    # Arrange
    pdb_path = "nonexistent.pdb"
    epitopes = []
    
    # Act & Assert
    with pytest.raises(FileNotFoundError):
        generate_mutants(pdb_path, epitopes, "reduce")
```

---

## Documentation

### Code Documentation

**Docstring Guidelines:**
- Use Google-style docstrings
- Include module-level docstrings
- Document all public functions and classes
- Include parameter types and descriptions
- Document return values and exceptions
- Add examples when helpful

**Example Docstring:**

```python
def predict_epitopes(fasta_path: str, alleles: List[str]) -> pd.DataFrame:
    """
    Predict CD4+ T-cell epitopes using NetMHCIIpan.
    
    This function uses NetMHCIIpan to predict MHC-II binding epitopes
    for the given protein sequence and HLA alleles.
    
    Args:
        fasta_path: Path to input FASTA file containing protein sequence
        alleles: List of HLA-DRB1 alleles (e.g., ['DRB1*01:01', 'DRB1*03:01'])
    
    Returns:
        DataFrame containing predicted epitopes with columns:
        - sequence: Peptide sequence
        - start: Start position in protein
        - end: End position in protein
        - allele: HLA allele
        - affinity: Binding affinity (nM)
        - rank: Percentile rank
    
    Raises:
        FileNotFoundError: If fasta_path does not exist
        ValueError: If alleles list is empty
        RuntimeError: If NetMHCIIpan execution fails
    
    Example:
        >>> alleles = ['DRB1*01:01', 'DRB1*03:01']
        >>> epitopes = predict_epitopes('protein.fasta', alleles)
        >>> print(epitopes.head())
    """
```

### User Documentation

**When to update:**
- **README.md**: User-facing changes, new features, installation updates
- **INSTALLATION_GUIDE.md**: Installation process changes, new tools
- **CHANGELOG.md**: All significant changes (see [Keep a Changelog](https://keepachangelog.com/))
- **Examples**: Add examples to `examples/` directory for new features

**Documentation Style:**
- Use clear, concise language
- Include code examples
- Add screenshots for UI changes
- Keep documentation up-to-date with code

---

## Pull Request Process

### Before Submitting

**Checklist:**
- [ ] All tests pass (`python -m pytest tests/`)
- [ ] Code is formatted (`make format`)
- [ ] Linting passes (`make lint`)
- [ ] Type checking passes (`make type-check`)
- [ ] Documentation is updated
- [ ] CHANGELOG.md is updated (if applicable)
- [ ] Commit messages follow guidelines

### Pull Request Guidelines

**Title:**
- Use descriptive title (e.g., "Add support for custom epitope formats")
- Prefix with type: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`

**Description:**
- Provide clear description of changes
- Reference related issues: `Fixes #123`
- Include motivation and approach
- Add screenshots for UI changes
- List breaking changes if any

**Example PR Description:**

```markdown
## Description
Adds support for custom epitope input formats (CSV, JSON, TSV).

## Motivation
Users requested more flexible epitope input options beyond the current CSV format.

## Changes
- Added `EpitopeParser` class supporting multiple formats
- Updated CLI to accept `--epitope-format` parameter
- Added validation for each format
- Updated documentation

## Testing
- Added tests for all supported formats
- Updated integration tests
- Tested with real-world data

## Related Issues
Fixes #123
Related to #456
```

### Review Process

**For Contributors:**
- Be patient - reviews may take time
- Address reviewer feedback promptly
- Be open to suggestions and improvements
- Ask questions if feedback is unclear

**For Reviewers:**
- Be constructive and respectful
- Explain reasoning for requested changes
- Approve when satisfied
- Request changes when needed

---

## Reporting Issues

### Bug Reports

**Required Information:**
- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- System information (OS, Python version, tool versions)
- Error messages or logs
- Minimal reproducible example (if possible)

**Bug Report Template:**

```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Run command '...'
2. With input '...'
3. See error

**Expected behavior**
What you expected to happen.

**Actual behavior**
What actually happened.

**Environment:**
- OS: [e.g., Ubuntu 20.04]
- Python version: [e.g., 3.9.7]
- VLPIM version: [e.g., 1.0.0]
- External tools: [versions if known]

**Error logs**
```
Paste error logs here
```

**Additional context**
Any other relevant information.
```

### Feature Requests

**Required Information:**
- Clear description of proposed feature
- Use case and motivation
- Potential implementation approach (if known)
- Any relevant references or examples

**Feature Request Template:**

```markdown
**Feature Description**
Clear description of the proposed feature.

**Use Case**
Why is this feature needed? What problem does it solve?

**Proposed Solution**
How should this feature work?

**Alternatives Considered**
Other approaches you've considered.

**Additional Context**
Any other relevant information, references, or examples.
```

---

## External Tool Integration

### Adding New Tools

**Steps:**

1. **Create wrapper module** in `src/vlpim/tools/`:
   ```python
   # src/vlpim/tools/new_tool_wrapper.py
   """Wrapper for NewTool integration."""
   
   import subprocess
   from pathlib import Path
   from typing import Dict, List
   
   def run_new_tool(input_path: str, options: Dict) -> List[str]:
       """Run NewTool and return results."""
       # Implementation
   ```

2. **Follow existing patterns:**
   - Use `subprocess` for external calls
   - Implement proper error handling
   - Parse outputs consistently
   - Add timeout handling
   - Log execution details

3. **Add configuration:**
   - Update `config/config_unified.yaml`
   - Update `src/vlpim/tools/path_config.py`
   - Add environment variable support

4. **Add tests:**
   - Unit tests for wrapper functions
   - Integration tests if possible
   - Mock external tool calls

5. **Update documentation:**
   - Add to README.md
   - Update INSTALLATION_GUIDE.md
   - Add usage examples

**⚠️ Important:** VLPIM does not provide installation assistance for external tools. Users must install tools independently and configure their paths. See [EXTERNAL_TOOLS_POLICY.md](EXTERNAL_TOOLS_POLICY.md) for details.

### Tool Wrapper Guidelines

**Best Practices:**
- Use `subprocess.run()` with proper timeout
- Validate inputs before calling external tools
- Parse outputs into structured data (DataFrames, dicts)
- Handle errors gracefully with informative messages
- Log tool execution for debugging
- Support both absolute and relative paths

**Example Wrapper:**

```python
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


def run_tool_wrapper(
    input_file: str,
    output_dir: str,
    options: Optional[Dict] = None,
    timeout: int = 3600
) -> List[str]:
    """
    Run external tool with proper error handling.
    
    Args:
        input_file: Path to input file
        output_dir: Directory for output files
        options: Optional tool-specific options
        timeout: Timeout in seconds
    
    Returns:
        List of output file paths
    
    Raises:
        FileNotFoundError: If input file doesn't exist
        RuntimeError: If tool execution fails
    """
    input_path = Path(input_file)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    cmd = ["tool_executable", "--input", str(input_path)]
    if options:
        for key, value in options.items():
            cmd.extend([f"--{key}", str(value)])
    
    logger.info(f"Running tool: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(
            cmd,
            cwd=str(output_path),
            capture_output=True,
            text=True,
            timeout=timeout,
            check=True
        )
        logger.info(f"Tool completed successfully")
        return [str(output_path / "output.txt")]
    
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"Tool execution timed out after {timeout}s")
    
    except subprocess.CalledProcessError as e:
        logger.error(f"Tool failed: {e.stderr}")
        raise RuntimeError(f"Tool execution failed: {e.stderr}")
```

---

## Release Process

### Version Numbering

We follow [Semantic Versioning](https://semver.org/):
- **MAJOR** (X.0.0): Incompatible API changes
- **MINOR** (0.X.0): New functionality in a backwards compatible manner
- **PATCH** (0.0.X): Backwards compatible bug fixes

### Release Checklist

**Before Release:**
1. [ ] Update version numbers:
   - `pyproject.toml`
   - `setup.py`
   - `src/vlpim/__init__.py`
2. [ ] Update `CHANGELOG.md`:
   - Add new version section
   - List all changes
   - Update links
3. [ ] Run full test suite:
   ```bash
   python -m pytest tests/ --cov=src
   ```
4. [ ] Run code quality checks:
   ```bash
   make format
   make lint
   make type-check
   ```
5. [ ] Update documentation:
   - Review README.md
   - Update INSTALLATION_GUIDE.md if needed
   - Check all examples work

**Release Steps:**
1. Create release branch: `git checkout -b release/v1.0.0`
2. Finalize CHANGELOG.md
3. Commit version updates: `git commit -m "chore: bump version to 1.0.0"`
4. Create tag: `git tag -a v1.0.0 -m "Release version 1.0.0"`
5. Push tag: `git push origin v1.0.0`
6. Merge to main
7. Create GitHub release with release notes

---

## Getting Help

**Resources:**
- **Documentation**: Check [README.md](README.md) and [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md)
- **Issues**: Search existing [GitHub Issues](https://github.com/RuijinHospitalVNAR/VLPIM/issues)
- **Discussions**: Join [GitHub Discussions](https://github.com/RuijinHospitalVNAR/VLPIM/discussions)
- **Email**: Contact maintainers at wcf231229@163.com

**Before Asking:**
- Search existing issues and discussions
- Check documentation thoroughly
- Try to reproduce the issue
- Gather relevant information (logs, versions, etc.)

---

## License

By contributing to VLPIM, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to VLPIM!** 🎉
