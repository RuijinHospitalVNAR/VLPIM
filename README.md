# VLPIM: A Comprehensive Tool for Immunogenicity Modulation of Virus-like Particles

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Documentation](https://img.shields.io/badge/docs-latest-brightgreen.svg)](docs/)

A comprehensive computational workflow for modulating immunogenicity of virus-like particles through epitope identification, sequence generation, MHC-II binding evaluation, and structure prediction.

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/RuijinHospitalVNAR/VLPIM.git
cd VLPIM

# Install dependencies
pip install -r requirements.txt

# Run environment setup
./scripts/install_environment.sh
```

### ⚠️ Required: Set Environment Variables

**Before running VLPIM, you must set up environment variables for the external tools:**

```bash
# Add to ~/.bashrc or ~/.zshrc
export PROTEIN_MPNN_PATH="/path/to/ProteinMPNN"
export NETMHCIIPAN_PATH="/path/to/netMHCIIpan"
export ALPHAFOLD3_PATH="/path/to/alphafold3"
export ROSETTA_PATH="/path/to/rosetta"

# Reload shell configuration
source ~/.bashrc
```

### Basic Usage

```bash
# Use user-provided epitopes
python -m vlpim run --fasta examples/protein.fasta --pdb examples/protein.pdb --mode reduce --epitopes examples/epitopes.csv

# Automatic epitope prediction
python -m vlpim run --fasta examples/protein.fasta --pdb examples/protein.pdb --mode reduce
```

## 📁 Project Structure

```
vlpim/
├── src/                    # Source code
│   └── vlpim/             # Main package
│       ├── __init__.py
│       ├── immunogenicity_optimization_pipeline.py
│       ├── vlpim.py         # CLI script
│       └── tools/          # Tool modules
│           ├── alphafold3_wrapper.py
│           ├── config_loader.py
│           ├── netmhcii_runner.py
│           ├── path_config.py
│           ├── protein_mpnn_wrapper.py
│           └── rosetta_wrapper.py
├── docs/                   # Documentation
│   └── ENVIRONMENT_FILES.md
├── examples/               # Example files
│   ├── example_epitopes.csv
│   ├── example_usage.py
│   └── protein.fasta
├── scripts/                # Utility scripts
│   ├── quick_start.sh
│   ├── install_environment.sh
│   └── validate_config.py
├── tests/                  # Test files
│   ├── test_interface_analysis.py
│   └── test_pipeline.py
├── config/                 # Configuration files
│   └── config_unified.yaml
├── requirements.txt        # Python dependencies
├── environment.yml         # Conda environment
├── pyproject.toml          # Project configuration
├── setup.py               # Setup script
├── Makefile               # Build automation
├── .gitignore             # Git ignore file
├── CHANGELOG.md           # Changelog
├── CONTRIBUTING.md        # Contributing guidelines
├── EXTERNAL_TOOLS_POLICY.md # External tools installation policy
├── LICENSE                # MIT License
└── README.md              # This file
```

## 🛠️ Prerequisites

### Required External Tools

VLPIM requires the following external tools to be installed by the user:

- **ProteinMPNN**: For sequence generation
- **NetMHCIIpan**: For MHC-II binding prediction  
- **AlphaFold3**: For structure prediction
- **Rosetta**: For interface analysis

**Note**: Users must install these tools independently. VLPIM does not provide installation assistance for external tools. See [External Tools Policy](EXTERNAL_TOOLS_POLICY.md) for details.

### ⚠️ Important: Environment Variables Setup

**After installing the tools independently, you MUST add their paths to your environment variables for VLPIM to work properly.**

Add the following lines to your `~/.bashrc` or `~/.zshrc` file:

```bash
# Required: External tool paths
export PROTEIN_MPNN_PATH="/path/to/ProteinMPNN"
export NETMHCIIPAN_PATH="/path/to/netMHCIIpan"
export ALPHAFOLD3_PATH="/path/to/alphafold3"
export ROSETTA_PATH="/path/to/rosetta"

# Optional: Default parameters
export DEFAULT_OUTPUT_DIR="results"
export DEFAULT_LOG_LEVEL="INFO"
```

**Then reload your shell configuration:**
```bash
source ~/.bashrc  # or source ~/.zshrc
```

**Verify the setup:**
```bash
python -m vlpim config
python -m vlpim validate
```

> 💡 **Tip**: This approach is much simpler than editing configuration files. Once set up, you can run VLPIM directly without any additional configuration!

## ⚙️ Configuration

### Method 1: Environment Variables (Recommended & Required)

**This is the recommended and simplest approach.** Set the following environment variables in your `~/.bashrc` or `~/.zshrc` after installing the external tools:

```bash
# Required: External tool paths (set these after installing the tools)
export PROTEIN_MPNN_PATH="/path/to/ProteinMPNN"
export NETMHCIIPAN_PATH="/path/to/netMHCIIpan"
export ALPHAFOLD3_PATH="/path/to/alphafold3"
export ROSETTA_PATH="/path/to/rosetta"

# Optional: User input paths
export USER_EPITOPES_PATH="/path/to/epitopes.csv"

# Optional: Default parameters
export DEFAULT_OUTPUT_DIR="results"
export DEFAULT_LOG_LEVEL="INFO"
```

**Reload your shell configuration:**
```bash
source ~/.bashrc  # or source ~/.zshrc
```

### Method 2: Configuration File (Alternative)

If you prefer using configuration files, edit `config/config_unified.yaml` after installing the external tools:

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
```

### Method 3: Automatic Detection

VLPIM will automatically search for tools in common Linux installation locations (after you have installed them):

- `/opt/[tool_name]`
- `/usr/local/[tool_name]`
- `/home/user/[tool_name]`
- System PATH

### Configuration Validation

Verify your configuration:

```bash
# Check configuration
python -m vlpim config

# Validate tool availability
python -m vlpim validate
```

## 🛠️ Features

- **Epitope Prediction**: Uses NetMHCIIpan for CD4+ T-cell epitope identification or accepts user-provided epitopes
- **Sequence Generation**: Leverages ProteinMPNN for generating mutant sequences
- **MHC-II Evaluation**: Evaluates binding affinity across multiple HLA-DRB1 alleles
- **Structure Prediction**: Uses AlphaFold3 for multimer structure prediction
- **Interface Analysis**: Uses Rosetta interface_analyzer for protein-protein interface analysis
- **Flexible Configuration**: Supports both immunogenicity reduction and enhancement modes
- **Comprehensive Logging**: Detailed logging and error handling throughout the pipeline

## 📖 Documentation

- [Usage Examples](examples/) - Example files and usage patterns
- [Environment Files](docs/ENVIRONMENT_FILES.md) - Environment configuration files
- [Contributing Guidelines](CONTRIBUTING.md) - How to contribute to the project
- [Changelog](CHANGELOG.md) - Project changelog

## 🧪 Testing

```bash
# Run tests
python -m vlpim test

# Validate configuration
python -m vlpim validate

# Show configuration
python -m vlpim config
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Tool Not Found
**Error**: `Tool not found: [tool_name]`

**Solution**:
- **Most common cause**: Environment variables not set properly
- Ensure the tool is installed and accessible
- **Check environment variables are set:**
```bash
echo $PROTEIN_MPNN_PATH
echo $NETMHCIIPAN_PATH
echo $ALPHAFOLD3_PATH
echo $ROSETTA_PATH
```
- **Set environment variables in ~/.bashrc:**
```bash
export PROTEIN_MPNN_PATH="/path/to/ProteinMPNN"
export NETMHCIIPAN_PATH="/path/to/netMHCIIpan"
export ALPHAFOLD3_PATH="/path/to/alphafold3"
export ROSETTA_PATH="/path/to/rosetta"
source ~/.bashrc
```
- Check if the tool is in your system PATH

```bash
# Check if tool is accessible
which protein_mpnn.py
which netMHCIIpan
which alphafold3
which interface_analyzer

# Set path explicitly
export NETMHCIIPAN_PATH="/path/to/netMHCIIpan"
```

#### 2. Permission Denied
**Error**: `Permission denied` or `Access denied`

**Solution**:
- Ensure you have execute permissions for the tool
- Run with appropriate user privileges
- Check file ownership and permissions

#### 3. Memory Issues
**Error**: `Out of memory` or `MemoryError`

**Solution**:
- Reduce `--samples-per-temp` parameter
- Decrease `--max-candidates` parameter
- Increase system memory or use a machine with more RAM

#### 4. Timeout Errors
**Error**: `Timeout` or `Execution timed out`

**Solution**:
- Increase timeout values in configuration
- Reduce batch sizes
- Check system performance and resource availability

#### 5. Configuration Issues
**Error**: `Configuration validation failed`

**Solution**:
```bash
# Validate configuration
python -m vlpim validate

# Check configuration
python -m vlpim config

# Edit configuration file
nano config/config_unified.yaml
```

### Getting Help

- Check the [Environment Files](docs/ENVIRONMENT_FILES.md) for environment configuration
- Review the [Usage Examples](examples/) for usage patterns
- Submit issues on [GitHub Issues](https://github.com/RuijinHospitalVNAR/VLPIM/issues)


## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

- 📧 Email: wcf231229@163.com
- 🐛 Issues: [GitHub Issues](https://github.com/RuijinHospitalVNAR/VLPIM/issues)
- 📖 Documentation: [docs/](docs/)
- 🤝 Contributing: [CONTRIBUTING.md](CONTRIBUTING.md)

## 🙏 Acknowledgments

- [ProteinMPNN](https://github.com/dauparas/ProteinMPNN) for sequence generation
- [NetMHCIIpan](https://services.healthtech.dtu.dk/service.php?NetMHCIIpan-4.0) for MHC-II binding prediction
- [AlphaFold3](https://www.deepmind.com/open-source/alphafold) for structure prediction
- [Rosetta](https://www.rosettacommons.org/) for interface analysis

## 📊 Citation

If you use VLPIM in your research, please cite:

```bibtex
@software{vlpim,
  title={VLPIM: A Comprehensive Tool for Immunogenicity Modulation of Virus-like Particles},
  author={Chufan Wang},
  year={2025},
  url={https://github.com/RuijinHospitalVNAR/VLPIM}
}
```
