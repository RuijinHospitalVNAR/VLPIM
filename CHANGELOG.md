<!-- -*- coding: utf-8 -*- -->
# Changelog

All notable changes to VLPIM: A Comprehensive Tool for Immunogenicity Modulation of Virus-like Particles will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-01-XX

### Added
- Initial release of VLPIM
- Comprehensive immunogenicity optimization pipeline
- Support for epitope prediction using NetMHCIIpan-4.3
- Sequence generation using ProteinMPNN
- Structure prediction using AlphaFold3
- Interface analysis using Rosetta interface_analyzer
- User-provided epitope support
- Flexible configuration system
- Comprehensive documentation

### Features
- **Epitope Prediction**: Uses NetMHCIIpan-4.3 for CD4+ T-cell epitope identification
- **Sequence Generation**: Leverages ProteinMPNN for generating mutant sequences
- **MHC-II Evaluation**: Evaluates binding affinity across multiple HLA-DRB1 alleles
- **Structure Prediction**: Uses AlphaFold3 for multimer structure prediction
- **Interface Analysis**: Uses Rosetta interface_analyzer for protein-protein interface analysis
- **Flexible Configuration**: Supports both immunogenicity reduction and enhancement modes
- **Comprehensive Logging**: Detailed logging and error handling throughout the pipeline

### Technical Details
- Python 3.8+ support
- Modular architecture with separate tool wrappers
- Environment variable configuration
- YAML configuration files
- Command-line interface with subcommands
- Comprehensive test suite
- Code quality tools (black, flake8, mypy)

### External Dependencies
- ProteinMPNN (from GitHub) - User must install independently
- NetMHCIIpan-4.3 (from DTU Health Tech) - User must install independently
- AlphaFold3 (from DeepMind) - User must install independently
- Rosetta (from University of Washington) - User must install independently

**Note**: VLPIM does not provide installation assistance for external tools. Users must install these tools independently and configure their paths.

### Documentation
- Comprehensive README with installation and usage instructions
- Environment configuration guide
- Usage examples
- API documentation

## [Unreleased]

### Planned
- GUI interface
- Web-based interface
- Additional epitope prediction tools
- Enhanced visualization capabilities
- Performance optimizations
- Additional output formats
