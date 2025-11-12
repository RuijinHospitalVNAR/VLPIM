# VLPIM Installation Guide

This guide provides step-by-step instructions for installing VLPIM and all required external tools.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Python Environment Setup](#python-environment-setup)
- [External Tools Installation](#external-tools-installation)
- [Environment Variables Configuration](#environment-variables-configuration)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements

- **Operating System**: Linux (Ubuntu 20.04+ recommended) or macOS
- **Python**: 3.8 or higher
- **Memory**: 16GB+ RAM (32GB+ recommended)
- **Storage**: 20GB+ free space
- **GPU**: Optional but recommended for AlphaFold3

### Required Software

- Python 3.8+
- pip or conda
- Git
- GCC/G++ compiler (for some tools)

---

## Python Environment Setup

### Option 1: Using pip

```bash
# Clone the repository
git clone https://github.com/RuijinHospitalVNAR/VLPIM.git
cd VLPIM

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### Option 2: Using conda

```bash
# Clone the repository
git clone https://github.com/RuijinHospitalVNAR/VLPIM.git
cd VLPIM

# Create conda environment
conda env create -f environment.yml
conda activate vlpim

# Install additional dependencies if needed
pip install -r requirements.txt
```

### Verify Python Installation

```bash
python --version  # Should be 3.8+
pip list  # Check installed packages
```

---

## External Tools Installation

**⚠️ Important:** VLPIM requires these tools to be installed separately. Follow the official installation guides for each tool.

### 1. ProteinMPNN

**Download and Installation:**

```bash
# Clone ProteinMPNN repository
git clone https://github.com/dauparas/ProteinMPNN.git
cd ProteinMPNN

# Install dependencies
pip install torch numpy

# Download model weights (if not included)
# Follow instructions in ProteinMPNN README

# Test installation
python protein_mpnn_run.py --help
```

**Set Environment Variable:**
```bash
export PROTEIN_MPNN_PATH="/path/to/ProteinMPNN"
```

**Verification:**
```bash
cd $PROTEIN_MPNN_PATH
python protein_mpnn_run.py --help
```

---

### 2. NetMHCIIpan

**Download:**
- Visit: https://services.healthtech.dtu.dk/services/NetMHCIIpan-4.3/
- Download the appropriate version for your system
- **Note:** Academic license required

**Installation:**

```bash
# Extract downloaded archive
tar -xzf netMHCIIpan-4.3.tar.gz
cd netMHCIIpan-4.3

# Follow installation instructions in the package
# Typically involves:
./configure
make

# Install data files (if required)
# Follow package-specific instructions
```

**Set Environment Variable:**
```bash
export NETMHCIIPAN_PATH="/path/to/netMHCIIpan-4.3"
```

**Verification:**
```bash
$NETMHCIIPAN_PATH/netMHCIIpan --help
```

---

### 3. AlphaFold3

**⚠️ Note:** AlphaFold3 installation is complex and requires significant resources. Consider using Singularity/Docker if available.

**Option A: Direct Installation**

```bash
# Clone AlphaFold3 repository
git clone https://github.com/google-deepmind/alphafold3.git
cd alphafold3

# Follow official installation guide:
# https://github.com/google-deepmind/alphafold3

# Install dependencies
pip install -r requirements.txt

# Download model weights (large files, ~10GB+)
# Follow instructions in AF3 repository
```

**Option B: Using Singularity (Recommended)**

```bash
# Build Singularity image (if you have access)
# Or download pre-built image if available

# Set paths
export ALPHAFOLD3_PATH="/path/to/alphafold3"
export ALPHAFOLD3_SIF="/path/to/alphafold3.sif"
export ALPHAFOLD3_MODEL_DIR="/path/to/af3_models"
export ALPHAFOLD3_DB_DIR="/path/to/af3_databases"
```

**Set Environment Variable:**
```bash
export ALPHAFOLD3_PATH="/path/to/alphafold3"
```

**Verification:**
```bash
cd $ALPHAFOLD3_PATH
python run_alphafold.py --help
```

---

### 4. Rosetta

**⚠️ Note:** Rosetta requires academic license. Commercial use requires separate license.

**Download:**
- Visit: https://www.rosettacommons.org/software/license-and-download
- Download Rosetta (requires registration and license agreement)
- Extract to desired location

**Installation:**

```bash
# Extract Rosetta
tar -xzf rosetta_src_*.tar.gz
cd rosetta_src_*

# Compile (if needed)
# Follow instructions in Rosetta documentation

# Set up environment
source Rosetta/main/source/bin/Rosetta.bashrc
```

**Set Environment Variable:**
```bash
export ROSETTA_PATH="/path/to/rosetta_src_XXXX"
```

**Verification:**
```bash
$ROSETTA_PATH/main/source/bin/interface_analyzer.* -help
```

---

## Environment Variables Configuration

### Step 1: Add to Shell Configuration

Add the following lines to your `~/.bashrc` (Linux) or `~/.zshrc` (macOS):

```bash
# VLPIM External Tools Configuration
export PROTEIN_MPNN_PATH="/path/to/ProteinMPNN"
export NETMHCIIPAN_PATH="/path/to/netMHCIIpan-4.3"
export ALPHAFOLD3_PATH="/path/to/alphafold3"
export ROSETTA_PATH="/path/to/rosetta_src_XXXX"

# Optional: Default parameters
export DEFAULT_OUTPUT_DIR="results"
export DEFAULT_LOG_LEVEL="INFO"
```

### Step 2: Reload Shell Configuration

```bash
source ~/.bashrc  # or source ~/.zshrc
```

### Step 3: Verify Environment Variables

```bash
echo $PROTEIN_MPNN_PATH
echo $NETMHCIIPAN_PATH
echo $ALPHAFOLD3_PATH
echo $ROSETTA_PATH
```

---

## Verification

### Step 1: Validate Configuration

```bash
# Check VLPIM configuration
python -m vlpim config

# Expected output should show all tool paths
```

### Step 2: Validate Tool Availability

```bash
# Validate all tools
python -m vlpim validate

# Expected output:
# ✓ ProteinMPNN: Available
# ✓ NetMHCIIpan: Available
# ✓ AlphaFold3: Available
# ✓ Rosetta: Available
```

### Step 3: Run Test Suite

```bash
# Run basic tests
python -m vlpim test

# Or run specific test files
python -m pytest tests/
```

### Step 4: Quick Test Run

```bash
# Test with example data (if available)
python -m vlpim run \
  --fasta examples/protein.fasta \
  --pdb examples/protein.pdb \
  --mode reduce \
  --samples-per-temp 2 \
  --max-candidates 1
```

---

## Troubleshooting

### Issue: Environment Variables Not Set

**Symptoms:**
- `Tool not found` errors
- `RuntimeError: [tool] not found`

**Solution:**
1. Check if variables are set: `echo $PROTEIN_MPNN_PATH`
2. Add to `~/.bashrc` or `~/.zshrc`
3. Reload: `source ~/.bashrc`
4. Verify in new terminal session

### Issue: Tool Executable Not Found

**Symptoms:**
- `FileNotFoundError` or `Command not found`

**Solution:**
1. Verify tool installation: `ls $PROTEIN_MPNN_PATH`
2. Check executable exists: `ls $PROTEIN_MPNN_PATH/protein_mpnn_run.py`
3. Verify PATH: `which protein_mpnn_run.py`
4. Add tool directory to PATH if needed

### Issue: Permission Denied

**Symptoms:**
- `Permission denied` errors

**Solution:**
```bash
# Add execute permissions
chmod +x $PROTEIN_MPNN_PATH/protein_mpnn_run.py
chmod +x $NETMHCIIPAN_PATH/netMHCIIpan
chmod +x $ALPHAFOLD3_PATH/run_alphafold.py
chmod +x $ROSETTA_PATH/main/source/bin/interface_analyzer.*
```

### Issue: Python Dependencies Missing

**Symptoms:**
- `ModuleNotFoundError`
- Import errors

**Solution:**
```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade

# Or with conda
conda env update -f environment.yml
```

### Issue: Tool-Specific Errors

**ProteinMPNN:**
- Ensure PyTorch is installed: `pip install torch`
- Check model weights are present

**NetMHCIIpan:**
- Verify license activation
- Check data files are installed
- Ensure correct version (4.3+)

**AlphaFold3:**
- Verify model weights downloaded
- Check database paths configured
- Ensure sufficient disk space (50GB+)

**Rosetta:**
- Verify license is active
- Check compilation completed successfully
- Ensure database files are present

---

## Next Steps

After successful installation:

1. **Read the [README.md](README.md)** for usage instructions
2. **Check [examples/](examples/)** for example files
3. **Review [docs/](docs/)** for detailed documentation
4. **Run a test:** `python -m vlpim validate`

---

## Getting Help

If you encounter issues during installation:

1. **Check logs:** Review error messages carefully
2. **Validate tools:** Run `python -m vlpim validate`
3. **Check documentation:** See [docs/](docs/) for detailed guides
4. **Submit issues:** [GitHub Issues](https://github.com/RuijinHospitalVNAR/VLPIM/issues)

---

## Installation Checklist

- [ ] Python 3.8+ installed
- [ ] VLPIM repository cloned
- [ ] Python dependencies installed (`pip install -r requirements.txt`)
- [ ] ProteinMPNN installed and tested
- [ ] NetMHCIIpan installed and tested
- [ ] AlphaFold3 installed and tested (or Singularity image ready)
- [ ] Rosetta installed and tested
- [ ] Environment variables set in `~/.bashrc` or `~/.zshrc`
- [ ] Shell configuration reloaded
- [ ] Configuration validated (`python -m vlpim validate`)
- [ ] Test run completed successfully

---

**Last Updated:** 2025-01-XX

