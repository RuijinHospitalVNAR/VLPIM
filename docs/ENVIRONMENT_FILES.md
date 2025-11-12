# Environment Files and Configuration

This document describes the environment configuration files and setup scripts used in VLPIM.

## Overview

VLPIM uses several configuration files and scripts to manage the development and runtime environment. This document provides an overview of these files and their purposes.

## Configuration Files

### Python Dependencies

#### `requirements.txt`

Contains all Python package dependencies for pip installation.

**Usage:**
```bash
pip install -r requirements.txt
```

**Key Dependencies:**
- Core: `pandas`, `numpy`, `biopython`
- CLI: `click`, `pyyaml`
- Testing: `pytest`, `pytest-cov`
- Code Quality: `black`, `flake8`, `mypy`

#### `environment.yml`

Conda environment configuration with all dependencies.

**Usage:**
```bash
conda env create -f environment.yml
conda activate vlpim
```

**Features:**
- Python 3.8+ specification
- All Python dependencies
- System tools (git, wget, curl)
- Bioconda channel for bioinformatics tools

### Project Configuration

#### `pyproject.toml`

Modern Python project configuration file.

**Contains:**
- Project metadata
- Build system configuration
- Tool configurations (black, mypy, pytest)
- Dependency specifications

#### `setup.py`

Package installation script.

**Usage:**
```bash
pip install -e .
```

**Features:**
- Package metadata
- Entry points for CLI commands
- Package discovery

### Build Automation

#### `Makefile`

Convenient commands for common operations.

**Available Commands:**
```bash
make install      # Install dependencies
make test         # Run tests
make format       # Format code with black
make lint         # Run flake8 linter
make type-check   # Run mypy type checker
make clean        # Clean temporary files
```

## Installation Scripts

### `scripts/install_environment.sh`

Automated environment setup script for Linux/macOS.

**Features:**
- Checks Python version compatibility
- Creates virtual environment
- Installs Python dependencies
- Sets up basic directory structure
- Validates installation

**Usage:**
```bash
chmod +x scripts/install_environment.sh
./scripts/install_environment.sh
```

### `scripts/quick_start.sh`

Quick start guide script.

**Usage:**
```bash
chmod +x scripts/quick_start.sh
./scripts/quick_start.sh
```

### `scripts/validate_config.py`

Configuration validation script.

**Usage:**
```bash
python scripts/validate_config.py
```

**Checks:**
- Environment variables are set
- External tools are accessible
- Configuration files are valid

## Environment Variables

### Required Variables

These must be set for VLPIM to function:

```bash
export PROTEIN_MPNN_PATH="/path/to/ProteinMPNN"
export NETMHCIIPAN_PATH="/path/to/netMHCIIpan"
export ALPHAFOLD3_PATH="/path/to/alphafold3"
export ROSETTA_PATH="/path/to/rosetta"
```

### Optional Variables

```bash
export DEFAULT_OUTPUT_DIR="results"
export DEFAULT_LOG_LEVEL="INFO"
```

### Setting Variables

**Linux/macOS:**
Add to `~/.bashrc` or `~/.zshrc`:
```bash
export PROTEIN_MPNN_PATH="/path/to/ProteinMPNN"
# ... other variables
```

Then reload:
```bash
source ~/.bashrc  # or source ~/.zshrc
```

**Windows:**
Set via System Properties → Environment Variables, or in PowerShell:
```powershell
$env:PROTEIN_MPNN_PATH = "C:\path\to\ProteinMPNN"
```

## Configuration File: `config/config_unified.yaml`

Unified configuration file for all VLPIM settings.

**Structure:**
```yaml
tools:
  proteinmpnn:
    path: "/path/to/ProteinMPNN"
    executable: "protein_mpnn.py"
  netmhcii:
    path: "/path/to/netMHCIIpan"
    executable: "netMHCIIpan"
  alphafold3:
    path: "/path/to/alphafold3"
    executable: "alphafold3"
  rosetta:
    path: "/path/to/rosetta"
    executable: "interface_analyzer"

pipeline:
  basic:
    default_output_dir: "results"
    default_log_level: "INFO"
  # ... more settings
```

**Note:** Environment variables take precedence over config file settings.

## Quick Start Options

### Option 1: Automated Setup (Recommended)

```bash
# Clone repository
git clone https://github.com/RuijinHospitalVNAR/VLPIM.git
cd VLPIM

# Run setup script
./scripts/install_environment.sh

# Set environment variables (see above)
# Install external tools (see INSTALLATION_GUIDE.md)

# Validate
python -m vlpim validate
```

### Option 2: Conda Environment

```bash
# Create conda environment
conda env create -f environment.yml
conda activate vlpim

# Set environment variables
# Install external tools

# Validate
python -m vlpim validate
```

### Option 3: Manual Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -e .

# Set environment variables
# Install external tools

# Validate
python -m vlpim validate
```

## Verification

After installation, verify everything works:

```bash
# Check Python imports
python -c "import pandas, numpy, biopython; print('✓ Dependencies OK')"

# Check VLPIM import
python -c "import vlpim; print('✓ VLPIM OK')"

# Validate configuration
python -m vlpim validate

# Check configuration
python -m vlpim config

# Run tests
python -m pytest tests/
```

## External Tools

**Important:** VLPIM requires external tools to be installed separately:

1. **ProteinMPNN** - See [INSTALLATION_GUIDE.md](../INSTALLATION_GUIDE.md)
2. **NetMHCIIpan** - See [INSTALLATION_GUIDE.md](../INSTALLATION_GUIDE.md)
3. **AlphaFold3** - See [INSTALLATION_GUIDE.md](../INSTALLATION_GUIDE.md)
4. **Rosetta** - See [INSTALLATION_GUIDE.md](../INSTALLATION_GUIDE.md)

See [EXTERNAL_TOOLS_POLICY.md](../EXTERNAL_TOOLS_POLICY.md) for policy details.

## Troubleshooting

### Common Issues

#### 1. Environment Variables Not Set

**Error:** `Tool not found` or `RuntimeError: [tool] not found`

**Solution:**
```bash
# Check variables
echo $PROTEIN_MPNN_PATH
echo $NETMHCIIPAN_PATH

# Set variables (add to ~/.bashrc)
export PROTEIN_MPNN_PATH="/path/to/ProteinMPNN"
source ~/.bashrc
```

#### 2. Python Dependencies Missing

**Error:** `ModuleNotFoundError`

**Solution:**
```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade

# Or with conda
conda env update -f environment.yml
```

#### 3. Configuration File Issues

**Error:** `Configuration validation failed`

**Solution:**
```bash
# Validate configuration
python -m vlpim validate

# Check config file syntax
python -c "import yaml; yaml.safe_load(open('config/config_unified.yaml'))"
```

## Updating Environment

### Update Python Dependencies

**Pip:**
```bash
pip install -r requirements.txt --upgrade
```

**Conda:**
```bash
conda env update -f environment.yml
```

### Update External Tools

Follow tool-specific update procedures. See [INSTALLATION_GUIDE.md](../INSTALLATION_GUIDE.md).

## Related Documentation

- [INSTALLATION_GUIDE.md](../INSTALLATION_GUIDE.md) - Comprehensive installation guide
- [README.md](../README.md) - Main documentation with configuration examples
- [EXTERNAL_TOOLS_POLICY.md](../EXTERNAL_TOOLS_POLICY.md) - External tools policy
- [CONTRIBUTING.md](../CONTRIBUTING.md) - Development setup guide

## Support

For environment setup issues:
1. Check [INSTALLATION_GUIDE.md](../INSTALLATION_GUIDE.md)
2. Review [Troubleshooting section in README.md](../README.md#troubleshooting)
3. Run validation: `python -m vlpim validate`
4. Check [GitHub Issues](https://github.com/RuijinHospitalVNAR/VLPIM/issues)

---

**Last Updated:** 2025-01-XX
