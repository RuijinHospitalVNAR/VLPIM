# External Tools Policy

This document outlines VLPIM's policy regarding external tools and dependencies.

## Overview

VLPIM integrates with several external bioinformatics tools to provide comprehensive immunogenicity optimization capabilities. **VLPIM does not provide installation assistance or bundled distributions for these external tools.** Users are responsible for installing and configuring these tools independently.

## Policy Statement

**VLPIM does not:**
- Provide installation scripts for external tools
- Bundle external tools with the VLPIM distribution
- Provide support for installing external tools
- Guarantee compatibility with specific tool versions
- Provide troubleshooting for external tool installation issues

**VLPIM does:**
- Provide clear documentation on required tools
- Offer guidance on tool configuration
- Support multiple configuration methods (environment variables, config files)
- Provide validation tools to check tool availability
- Document tool requirements and versions

## Required External Tools

### 1. ProteinMPNN

**Purpose:** Protein sequence generation and design

**Source:** [GitHub Repository](https://github.com/dauparas/ProteinMPNN)

**Installation:** Users must follow the official ProteinMPNN installation guide

**Configuration:** Set `PROTEIN_MPNN_PATH` environment variable

**License:** Check ProteinMPNN repository for license terms

### 2. NetMHCIIpan

**Purpose:** MHC-II binding prediction for epitope identification

**Source:** [DTU Health Tech Services](https://services.healthtech.dtu.dk/service.php?NetMHCIIpan-4.0)

**Installation:** Users must download and install from DTU Health Tech

**Configuration:** Set `NETMHCIIPAN_PATH` environment variable

**License:** Academic license required. See [NetMHCIIpan License](https://services.healthtech.dtu.dk/services/NetMHCIIpan-4.3/)

**Note:** Commercial use requires separate license agreement

### 3. AlphaFold3

**Purpose:** Protein structure prediction

**Source:** [Google DeepMind](https://github.com/google-deepmind/alphafold3)

**Installation:** Users must follow the official AlphaFold3 installation guide

**Configuration:** Set `ALPHAFOLD3_PATH` environment variable

**License:** Subject to AlphaFold3 Model Parameters Terms of Use. See [AlphaFold3 License](https://github.com/google-deepmind/alphafold3/blob/main/WEIGHTS_TERMS_OF_USE.md)

**Note:** Requires significant computational resources and model weights download

### 4. Rosetta

**Purpose:** Protein-protein interface analysis

**Source:** [Rosetta Commons](https://www.rosettacommons.org/)

**Installation:** Users must download and install from Rosetta Commons

**Configuration:** Set `ROSETTA_PATH` environment variable

**License:** Academic license required. See [Rosetta License](https://www.rosettacommons.org/software/license-and-download)

**Note:** Commercial use requires separate license agreement

## Why This Policy?

### 1. License Compliance

Many external tools have specific license requirements:
- Academic vs. commercial licenses
- Terms of use restrictions
- Redistribution limitations

VLPIM cannot bundle tools with incompatible licenses.

### 2. Tool Complexity

External tools often have:
- Complex installation requirements
- Large model files (GBs)
- System-specific dependencies
- Version-specific configurations

Users need to install tools according to their system and requirements.

### 3. Version Management

Different users may need different tool versions:
- Research vs. production environments
- System compatibility
- Feature requirements

VLPIM supports multiple versions through flexible configuration.

### 4. Legal and Ethical Considerations

- Respecting tool developers' distribution policies
- Ensuring proper attribution
- Complying with academic and commercial licenses

## Configuration Methods

VLPIM supports multiple ways to configure external tool paths:

### Method 1: Environment Variables (Recommended)

```bash
export PROTEIN_MPNN_PATH="/path/to/ProteinMPNN"
export NETMHCIIPAN_PATH="/path/to/netMHCIIpan"
export ALPHAFOLD3_PATH="/path/to/alphafold3"
export ROSETTA_PATH="/path/to/rosetta"
```

### Method 2: Configuration File

Edit `config/config_unified.yaml`:

```yaml
tools:
  proteinmpnn:
    path: "/path/to/ProteinMPNN"
  netmhcii:
    path: "/path/to/netMHCIIpan"
  alphafold3:
    path: "/path/to/alphafold3"
  rosetta:
    path: "/path/to/rosetta"
```

### Method 3: Automatic Detection

VLPIM automatically searches common installation locations:
- `/opt/[tool_name]`
- `/usr/local/[tool_name]`
- `~/[tool_name]`
- System PATH

## Validation

Use VLPIM's validation tool to check tool availability:

```bash
python -m vlpim validate
```

This will check:
- Tool executables are accessible
- Paths are correctly configured
- Tools can be executed

## Getting Help

### For External Tool Installation

**VLPIM cannot help with:**
- Installing external tools
- Troubleshooting tool installation issues
- Resolving tool-specific errors
- License questions for external tools

**Contact the tool developers:**
- ProteinMPNN: [GitHub Issues](https://github.com/dauparas/ProteinMPNN/issues)
- NetMHCIIpan: [DTU Health Tech Support](https://services.healthtech.dtu.dk/)
- AlphaFold3: [GitHub Issues](https://github.com/google-deepmind/alphafold3/issues)
- Rosetta: [Rosetta Commons Support](https://www.rosettacommons.org/software/license-and-download)

### For VLPIM Configuration

**VLPIM can help with:**
- Configuring tool paths in VLPIM
- Troubleshooting VLPIM integration issues
- Understanding VLPIM's tool usage

**Resources:**
- [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md) - Detailed installation guide
- [README.md](README.md) - Configuration examples
- [GitHub Issues](https://github.com/RuijinHospitalVNAR/VLPIM/issues) - Report VLPIM-specific issues

## Installation Guides

For detailed installation instructions for each tool, see:

- [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md) - Comprehensive installation guide
- Tool-specific sections in the guide
- Official tool documentation (linked above)

## Version Compatibility

VLPIM has been tested with:
- ProteinMPNN: Latest version from GitHub
- NetMHCIIpan: 4.3+
- AlphaFold3: Latest version from GitHub
- Rosetta: Latest academic release

**Note:** VLPIM may work with other versions, but compatibility is not guaranteed. Users should test their specific tool versions.

## Contributing Tool Wrappers

If you want to add support for a new external tool:

1. **Check License Compatibility:**
   - Ensure the tool's license allows integration
   - Check redistribution restrictions

2. **Create Wrapper:**
   - Follow existing wrapper patterns
   - Implement proper error handling
   - Add configuration support

3. **Update Documentation:**
   - Add tool to this policy document
   - Update INSTALLATION_GUIDE.md
   - Add configuration examples

4. **Follow Policy:**
   - Do not bundle the tool
   - Do not provide installation scripts
   - Document user installation requirements

See [CONTRIBUTING.md](CONTRIBUTING.md) for more details.

## Summary

**Key Points:**
- ✅ VLPIM provides tool integration and configuration support
- ✅ Users must install external tools independently
- ✅ VLPIM supports multiple configuration methods
- ✅ VLPIM provides validation tools
- ❌ VLPIM does not provide installation assistance
- ❌ VLPIM does not bundle external tools

**For Installation Help:**
- See [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md)
- Contact tool developers directly
- Check tool-specific documentation

**For VLPIM Configuration Help:**
- See [README.md](README.md)
- Check [GitHub Issues](https://github.com/RuijinHospitalVNAR/VLPIM/issues)
- Contact VLPIM maintainers

---

**Last Updated:** 2025-01-XX

