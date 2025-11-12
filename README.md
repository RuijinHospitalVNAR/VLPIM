# VLPIM: A Comprehensive Tool for Immunogenicity Modulation of Virus-like Particles

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Documentation](https://img.shields.io/badge/docs-latest-brightgreen.svg)](docs/)

A comprehensive computational workflow for modulating immunogenicity of virus-like particles through epitope identification, sequence generation, MHC-II binding evaluation, and structure prediction.

## Contents

<!-- TOC -->

- [Quick Start](#quick-start)
  * [Installation](#installation)
  * [Environment Variables Setup](#environment-variables-setup)
  * [Basic Usage](#basic-usage)
- [Setup](#setup)
  * [Requirements](#requirements)
  * [System Requirements](#system-requirements)
  * [Installation Steps](#installation-steps)
  * [Configuration](#configuration)
- [Usage](#usage)
  * [Command-Line Interface](#command-line-interface)
  * [Configuration Files](#configuration-files)
  * [Examples](#examples)
- [Output Format](#output-format)
- [Tips for Optimization](#tips-for-optimization)
- [Troubleshooting](#troubleshooting)
- [Citation](#citation)
- [Acknowledgments](#acknowledgments)

<!-- TOC -->

---

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/RuijinHospitalVNAR/VLPIM.git
cd VLPIM

# Install Python dependencies
pip install -r requirements.txt

# Run environment setup script
./scripts/install_environment.sh
```

### Environment Variables Setup

**⚠️ CRITICAL: Before running VLPIM, you MUST set up environment variables for external tools.**

Add the following to your `~/.bashrc` or `~/.zshrc`:

```bash
# Required: External tool paths
export PROTEIN_MPNN_PATH="/path/to/ProteinMPNN"
export NETMHCIIPAN_PATH="/path/to/netMHCIIpan"
export ALPHAFOLD3_PATH="/path/to/alphafold3"
export ROSETTA_PATH="/path/to/rosetta"

# Reload shell configuration
source ~/.bashrc  # or source ~/.zshrc
```

**Verify the setup:**
```bash
python -m vlpim config
python -m vlpim validate
```

### Basic Usage

**Reduce immunogenicity (default mode):**
```bash
python -m vlpim run \
  --fasta examples/protein.fasta \
  --pdb examples/protein.pdb \
  --mode reduce
```

**Enhance immunogenicity:**
```bash
python -m vlpim run \
  --fasta examples/protein.fasta \
  --pdb examples/protein.pdb \
  --mode enhance
```

**With user-provided epitopes:**
```bash
python -m vlpim run \
  --fasta examples/protein.fasta \
  --pdb examples/protein.pdb \
  --mode reduce \
  --epitopes examples/epitopes.csv
```

---

## Setup

### Requirements

**Prerequisites:**
- [ProteinMPNN](https://github.com/dauparas/ProteinMPNN) - For sequence generation
- [NetMHCIIpan](https://services.healthtech.dtu.dk/service.php?NetMHCIIpan-4.0) - For MHC-II binding prediction
- [AlphaFold3](https://github.com/google-deepmind/alphafold3) - For structure prediction
- [Rosetta](https://www.rosettacommons.org/) - For interface analysis

**⚠️ Important:** Users must install these tools independently. VLPIM does not provide installation assistance for external tools. See [External Tools Policy](EXTERNAL_TOOLS_POLICY.md) for details.

**Python Dependencies:**
- Python 3.8+
- pandas
- numpy
- biopython
- See `requirements.txt` for complete list

### System Requirements

- **CPU**: Multi-core processor recommended
- **Memory**: 16GB+ RAM (32GB+ recommended for large proteins)
- **Storage**: 10GB+ free space for results and temporary files
- **GPU**: Optional but recommended for AlphaFold3 structure prediction

> **Note:** Runtime varies significantly based on protein size and number of candidates. A typical run for a 200-residue protein with 10 candidates takes approximately 2-4 hours on a modern workstation.

### Installation Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/RuijinHospitalVNAR/VLPIM.git
   cd VLPIM
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   
   Or use conda:
   ```bash
   conda env create -f environment.yml
   conda activate vlpim
   ```

3. **Install external tools:**
   
   Follow the official installation guides for each tool:
   - [ProteinMPNN Installation](https://github.com/dauparas/ProteinMPNN)
   - [NetMHCIIpan Installation](https://services.healthtech.dtu.dk/services/NetMHCIIpan-4.3/)
   - [AlphaFold3 Installation](https://github.com/google-deepmind/alphafold3)
   - [Rosetta Installation](https://www.rosettacommons.org/software/license-and-download)

4. **Set environment variables:**
   
   Add tool paths to your shell configuration file (`~/.bashrc` or `~/.zshrc`):
   ```bash
   export PROTEIN_MPNN_PATH="/path/to/ProteinMPNN"
   export NETMHCIIPAN_PATH="/path/to/netMHCIIpan"
   export ALPHAFOLD3_PATH="/path/to/alphafold3"
   export ROSETTA_PATH="/path/to/rosetta"
   ```
   
   Then reload:
   ```bash
   source ~/.bashrc  # or source ~/.zshrc
   ```

5. **Validate installation:**
   ```bash
   python -m vlpim validate
   ```

### Configuration

VLPIM supports three configuration methods:

#### Method 1: Environment Variables (Recommended)

**This is the simplest and recommended approach.** Set environment variables in your shell configuration:

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

#### Method 2: Configuration File

Edit `config/config_unified.yaml`:

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

#### Method 3: Automatic Detection

VLPIM automatically searches common installation locations:
- `/opt/[tool_name]`
- `/usr/local/[tool_name]`
- `~/[tool_name]`
- System PATH

**Configuration Validation:**
```bash
# Check current configuration
python -m vlpim config

# Validate tool availability
python -m vlpim validate
```

---

## Usage

### Command-Line Interface

#### Basic Commands

**Run pipeline:**
```bash
python -m vlpim run --fasta <FASTA> --pdb <PDB> --mode {reduce|enhance}
```

**Show configuration:**
```bash
python -m vlpim config
```

**Validate setup:**
```bash
python -m vlpim validate
```

**Run tests:**
```bash
python -m vlpim test
```

#### Command-Line Options

**Required Arguments:**
- `--fasta FILE`: Input FASTA file path
- `--pdb FILE`: Input PDB file path
- `--mode {reduce|enhance}`: Immunogenicity modulation mode

**Optional Arguments:**
- `--epitopes FILE`: User-provided epitopes CSV file
- `--output-dir DIR`: Output directory (default: `results`)
- `--log-level LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)

**ProteinMPNN Parameters:**
- `--samples-per-temp N`: Number of samples per temperature (default: 20)
- `--temperatures FLOAT ...`: Temperature values (default: 0.1 0.3 0.5)

**Structure Prediction Parameters:**
- `--max-candidates N`: Maximum number of structure candidates (default: 10)
- `--rmsd-threshold FLOAT`: RMSD threshold for structure filtering (default: 2.0)

**Interface Analysis Parameters:**
- `--interface-analysis`: Enable Rosetta interface analysis (default: True)
- `--dg-dsasa-threshold FLOAT`: dG/dSASA threshold (default: -0.5)
- `--buns-threshold N`: BUNS threshold (default: 5)
- `--packstat-threshold FLOAT`: Packstat threshold (default: 0.6)

### Configuration Files

#### Epitopes CSV Format

If using `--epitopes`, the CSV file should contain:

| Column | Description | Example |
|--------|-------------|---------|
| `sequence` | Epitope peptide sequence | `MKLLVL` |
| `start` | Start position in protein (1-indexed) | `10` |
| `end` | End position in protein (1-indexed) | `15` |

**Example `epitopes.csv`:**
```csv
sequence,start,end
MKLLVL,10,15
GCTAGCT,25,31
```

### Examples

#### Example 1: Reduce Immunogenicity with Auto Epitope Prediction

```bash
python -m vlpim run \
  --fasta examples/protein.fasta \
  --pdb examples/protein.pdb \
  --mode reduce \
  --output-dir results/reduce_immunogenicity
```

#### Example 2: Enhance Immunogenicity with Custom Epitopes

```bash
python -m vlpim run \
  --fasta examples/protein.fasta \
  --pdb examples/protein.pdb \
  --mode enhance \
  --epitopes examples/custom_epitopes.csv \
  --samples-per-temp 30 \
  --max-candidates 20
```

#### Example 3: Custom Temperature Sampling

```bash
python -m vlpim run \
  --fasta examples/protein.fasta \
  --pdb examples/protein.pdb \
  --mode reduce \
  --temperatures 0.05 0.15 0.25 0.35 \
  --samples-per-temp 25
```

#### Example 4: Strict Interface Filtering

```bash
python -m vlpim run \
  --fasta examples/protein.fasta \
  --pdb examples/protein.pdb \
  --mode reduce \
  --dg-dsasa-threshold -1.0 \
  --buns-threshold 3 \
  --packstat-threshold 0.7
```

---

## Output Format

VLPIM generates organized output directories:

```
results/
├── <experiment_name>/
│   ├── epitopes/                    # Epitope prediction results
│   │   ├── predicted_epitopes.csv   # NetMHCIIpan predictions
│   │   └── epitope_summary.json     # Summary statistics
│   ├── sequences/                   # Generated sequences
│   │   ├── mutants.fasta           # ProteinMPNN generated sequences
│   │   └── sequence_metadata.csv    # Generation parameters
│   ├── mhc_evaluation/              # MHC-II binding evaluation
│   │   ├── binding_affinity.csv     # Per-allele binding scores
│   │   └── ranking.csv              # Ranked sequences
│   ├── structures/                  # Predicted structures
│   │   ├── candidate_0.pdb         # AlphaFold3 predictions
│   │   ├── candidate_1.pdb
│   │   └── structure_metrics.csv   # RMSD, confidence scores
│   ├── interface_analysis/          # Rosetta interface analysis
│   │   ├── interface_metrics.csv   # dG/dSASA, packstat, BUNS
│   │   └── interface_summary.json  # Quality assessment
│   ├── final_results/               # Final ranked candidates
│   │   ├── top_candidates.csv      # Best sequences with all metrics
│   │   └── summary_report.json     # Complete pipeline summary
│   └── logs/                        # Execution logs
│       ├── pipeline.log            # Main pipeline log
│       └── tool_logs/              # Individual tool logs
```

**Key Output Files:**

- `final_results/top_candidates.csv`: Complete list of optimized sequences with:
  - Original and mutated sequences
  - Epitope positions and scores
  - MHC-II binding affinities (per allele)
  - Structure prediction metrics (RMSD, confidence)
  - Interface analysis metrics (dG/dSASA, packstat, BUNS)
  - Overall ranking scores

- `final_results/summary_report.json`: Pipeline execution summary including:
  - Total sequences generated
  - Epitopes identified
  - Structures predicted
  - Final candidates selected
  - Execution time and resource usage

---

## Tips for Optimization

### Parameter Tuning

**For better sequence diversity:**
- Increase `--samples-per-temp` (e.g., 30-50)
- Use wider temperature range: `--temperatures 0.05 0.2 0.4 0.6`

**For faster execution:**
- Reduce `--max-candidates` (e.g., 5-8)
- Use fewer temperatures: `--temperatures 0.1 0.3`

**For stricter filtering:**
- Lower `--rmsd-threshold` (e.g., 1.5)
- More negative `--dg-dsasa-threshold` (e.g., -1.0)
- Lower `--buns-threshold` (e.g., 3)
- Higher `--packstat-threshold` (e.g., 0.7)

### Performance Optimization

**Memory Management:**
- For large proteins (>300 residues), reduce `--samples-per-temp`
- Process candidates in batches by setting `--max-candidates` appropriately

**Parallel Processing:**
- VLPIM automatically uses parallel processing where possible
- Ensure sufficient CPU cores and memory for concurrent tool execution

**Caching:**
- Results are cached to avoid redundant computations
- Clear cache if updating tool versions: `rm -rf cache/`

### Best Practices

1. **Start with small test runs:**
   ```bash
   python -m vlpim run --fasta test.fasta --pdb test.pdb --mode reduce \
     --samples-per-temp 5 --max-candidates 3
   ```

2. **Validate configuration before large runs:**
   ```bash
   python -m vlpim validate
   ```

3. **Monitor resource usage:**
   - Check disk space before long runs
   - Monitor memory usage during structure prediction

4. **Use user-provided epitopes when possible:**
   - Reduces computation time
   - More targeted optimization

---

## Troubleshooting

### Common Issues

#### 1. Tool Not Found

**Error:** `Tool not found: [tool_name]` or `RuntimeError: [tool] not found`

**Solution:**
1. **Check environment variables:**
   ```bash
   echo $PROTEIN_MPNN_PATH
   echo $NETMHCIIPAN_PATH
   echo $ALPHAFOLD3_PATH
   echo $ROSETTA_PATH
   ```

2. **Verify tool installation:**
   ```bash
   # Check if tools are accessible
   which protein_mpnn_run.py
   which netMHCIIpan
   which alphafold3
   which interface_analyzer
   ```

3. **Set environment variables:**
   ```bash
   # Add to ~/.bashrc or ~/.zshrc
   export PROTEIN_MPNN_PATH="/path/to/ProteinMPNN"
   export NETMHCIIPAN_PATH="/path/to/netMHCIIpan"
   export ALPHAFOLD3_PATH="/path/to/alphafold3"
   export ROSETTA_PATH="/path/to/rosetta"
   
   # Reload
   source ~/.bashrc
   ```

4. **Run validation:**
   ```bash
   python -m vlpim validate
   ```

#### 2. Permission Denied

**Error:** `Permission denied` or `Access denied`

**Solution:**
```bash
# Add execute permissions
chmod +x $PROTEIN_MPNN_PATH/protein_mpnn_run.py
chmod +x $NETMHCIIPAN_PATH/netMHCIIpan
chmod +x $ALPHAFOLD3_PATH/run_alphafold.py
chmod +x $ROSETTA_PATH/main/source/bin/interface_analyzer.*
```

#### 3. Memory Issues

**Error:** `Out of memory` or `MemoryError`

**Solution:**
- Reduce `--samples-per-temp` (e.g., from 20 to 10)
- Decrease `--max-candidates` (e.g., from 10 to 5)
- Increase system swap space
- Use a machine with more RAM

#### 4. Timeout Errors

**Error:** `Timeout` or `Execution timed out`

**Solution:**
- Increase timeout values in `config/config_unified.yaml`
- Reduce batch sizes (`--samples-per-temp`)
- Check system performance and resource availability
- For AlphaFold3: Ensure GPU is available and properly configured

#### 5. Configuration Validation Failed

**Error:** `Configuration validation failed`

**Solution:**
```bash
# Validate configuration
python -m vlpim validate

# Check configuration
python -m vlpim config

# Edit configuration file if needed
nano config/config_unified.yaml
```

#### 6. AlphaFold3 Structure Prediction Fails

**Error:** `AlphaFold3 execution failed` or `Structure prediction error`

**Solution:**
- Verify AlphaFold3 installation and model weights
- Check GPU availability: `nvidia-smi`
- Ensure sufficient disk space for temporary files
- Check AlphaFold3 logs in `results/*/logs/tool_logs/`

#### 7. NetMHCIIpan Epitope Prediction Fails

**Error:** `NetMHCIIpan failed` or `Epitope prediction error`

**Solution:**
- Verify NetMHCIIpan installation and database files
- Check FASTA file format (no special characters)
- Ensure HLA allele names are correct format (e.g., `DRB1*01:01`)
- Check NetMHCIIpan license and activation

### Getting Help

- **Check logs:** Review `results/*/logs/pipeline.log` for detailed error messages
- **Run in debug mode:** `python -m vlpim run ... --log-level DEBUG`
- **Validate tools:** `python -m vlpim validate`
- **Check documentation:** See [docs/](docs/) for detailed guides
- **Submit issues:** [GitHub Issues](https://github.com/RuijinHospitalVNAR/VLPIM/issues)

---

## Citation

If you use VLPIM in your research, please cite:

```bibtex
@software{vlpim,
  title={VLPIM: A Comprehensive Tool for Immunogenicity Modulation of Virus-like Particles},
  author={Wang, Chufan},
  year={2025},
  url={https://github.com/RuijinHospitalVNAR/VLPIM},
  version={1.0}
}
```

---

## Acknowledgments

VLPIM builds upon the following excellent tools and resources:

- **[ProteinMPNN](https://github.com/dauparas/ProteinMPNN)** - For sequence generation
- **[NetMHCIIpan](https://services.healthtech.dtu.dk/service.php?NetMHCIIpan-4.0)** - For MHC-II binding prediction
- **[AlphaFold3](https://www.deepmind.com/open-source/alphafold)** - For structure prediction
- **[Rosetta](https://www.rosettacommons.org/)** - For interface analysis

**Related Work:**
If you use components of this pipeline, please also cite the underlying methods:

- **ProteinMPNN**: Dauparas, J., et al. (2022). Robust deep learning–based protein sequence design using ProteinMPNN. Science, 378(6615), 49-56.
- **NetMHCIIpan**: Reynisson, B., et al. (2020). NetMHCIIpan-4.0: Improved prediction of binding to HLA class II molecules. Bioinformatics, 36(13), 4222-4224.
- **AlphaFold3**: Abramson, J., et al. (2024). Accurate structure prediction of biomolecular interactions with AlphaFold 3. Nature, 630(8016), 493-500.
- **Rosetta**: Koehler Leman, J., et al. (2020). Macromolecular modeling and design in Rosetta: recent methods and frameworks. Nature Methods, 17(7), 665-680.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### External Dependencies

Some components require separate licenses:

- **NetMHCIIpan**: Academic license required. See [NetMHCIIpan License](https://services.healthtech.dtu.dk/services/NetMHCIIpan-4.3/)
- **Rosetta**: Academic license required. See [Rosetta License](https://www.rosettacommons.org/software/license-and-download)
- **AlphaFold3**: Subject to AlphaFold3 Model Parameters Terms of Use. See [AlphaFold3 License](https://github.com/google-deepmind/alphafold3/blob/main/WEIGHTS_TERMS_OF_USE.md)

---

## Support

- 📧 **Email**: wcf231229@163.com
- 🐛 **Issues**: [GitHub Issues](https://github.com/RuijinHospitalVNAR/VLPIM/issues)
- 📖 **Documentation**: [docs/](docs/)
- 🤝 **Contributing**: [CONTRIBUTING.md](CONTRIBUTING.md)

---

## Project Structure

```
vlpim/
├── src/                           # Source code
│   └── vlpim/                    # Main package
│       ├── __init__.py
│       ├── immunogenicity_optimization_pipeline.py  # Main pipeline
│       ├── epitope_analyzer.py   # Epitope analysis
│       ├── vlpim.py              # CLI entry point
│       └── tools/                 # Tool wrappers
│           ├── alphafold3_wrapper.py
│           ├── protein_mpnn_wrapper.py
│           ├── netmhcii_runner.py
│           ├── rosetta_wrapper.py
│           └── path_config.py    # Path configuration
├── docs/                          # Documentation
│   ├── chinese_docs/             # Chinese documentation
│   └── ENVIRONMENT_FILES.md      # Environment setup guide
├── examples/                      # Example files
│   ├── example_epitopes.csv
│   ├── example_usage.py
│   └── protein.fasta
├── scripts/                       # Utility scripts
│   ├── install_environment.sh
│   ├── quick_start.sh
│   └── validate_config.py
├── tests/                         # Test files
│   ├── test_interface_analysis.py
│   └── test_pipeline.py
├── config/                        # Configuration files
│   └── config_unified.yaml
├── requirements.txt               # Python dependencies
├── environment.yml                # Conda environment
├── pyproject.toml                 # Project configuration
├── setup.py                       # Setup script
├── Makefile                       # Build automation
├── CHANGELOG.md                   # Changelog
├── CONTRIBUTING.md                # Contributing guidelines
├── EXTERNAL_TOOLS_POLICY.md       # External tools policy
├── LICENSE                        # MIT License
└── README.md                      # This file
```

---

**⚠️ Important Notes:**

- **External Tools**: Users must install ProteinMPNN, NetMHCIIpan, AlphaFold3, and Rosetta independently. VLPIM does not provide installation assistance for external tools.
- **Environment Variables**: Setting environment variables is **required** for VLPIM to function properly.
- **License Compliance**: Ensure you have appropriate licenses for all external tools before use.
- **Experimental Features**: Some features may be experimental. Check the [CHANGELOG.md](CHANGELOG.md) for the latest updates.
