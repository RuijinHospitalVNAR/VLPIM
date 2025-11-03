# -*- coding: utf-8 -*-
# VLPIM: A Comprehensive Tool for Immunogenicity Modulation of Virus-like Particles - Makefile
# Provides convenient commands for common operations

.PHONY: help install test clean docker-build docker-run setup vlpim-help vlpim-config vlpim-validate vlpim-test

# Default target
help:
	@echo "VLPIM: A Comprehensive Tool for Immunogenicity Modulation of Virus-like Particles"
	@echo "========================================================"
	@echo ""
	@echo "Available commands:"
	@echo "  install      - Install Python dependencies"
	@echo "  setup        - Run full setup (Linux/macOS)"
	@echo "  test         - Run basic tests"
	@echo "  clean        - Clean temporary files"
	@echo "  help         - Show this help message"
	@echo ""
	@echo "VLPIM Commands:"
	@echo "  vlpim-help   - Show VLPIM help (VLPIM --help)"
	@echo "  vlpim-config - Show VLPIM configuration"
	@echo "  vlpim-validate - Validate VLPIM configuration"
	@echo "  vlpim-test   - Run VLPIM tests"
	@echo ""

# Install Python dependencies
install:
	@echo "Installing Python dependencies..."
	pip install -r requirements.txt
	@echo "Dependencies installed successfully!"

# Run environment setup script (Linux)
setup:
	@echo "Running environment setup script..."
	chmod +x scripts/install_environment.sh
	./scripts/install_environment.sh

# Run basic tests
test:
	@echo "Running basic tests..."
	python -c "import pandas, numpy, requests; print('✓ Python dependencies OK')"
	python -c "from src.vlpim.immunogenicity_optimization_pipeline import ImmunogenicityOptimizer; print('✓ Pipeline import OK')"
	python -m vlpim --help > /dev/null && echo "✓ Pipeline help command OK"
	@echo "All tests passed!"

# Clean temporary files
clean:
	@echo "Cleaning temporary files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.log" -delete
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	@echo "Cleanup completed!"


# Create conda environment
conda-env:
	@echo "Creating conda environment..."
	conda env create -f environment.yml
	@echo "Conda environment created! Activate with: conda activate vlpim"

# Update conda environment
conda-update:
	@echo "Updating conda environment..."
	conda env update -f environment.yml
	@echo "Conda environment updated!"

# Remove conda environment
conda-remove:
	@echo "Removing conda environment..."
	conda env remove -n vlpim
	@echo "Conda environment removed!"

# Format code
format:
	@echo "Formatting code with black..."
	black src/ tests/ scripts/
	@echo "Code formatting completed!"

# Lint code
lint:
	@echo "Running linter..."
	flake8 src/ tests/ scripts/
	@echo "Linting completed!"

# Type checking
type-check:
	@echo "Running type checker..."
	mypy src/ tests/ scripts/
	@echo "Type checking completed!"

# Run all code quality checks
quality: format lint type-check
	@echo "All quality checks completed!"

# Create example input files
example-input:
	@echo "Creating example input files..."
	mkdir -p input
	@echo ">example_protein" > input/example.fasta
	@echo "MKLLVLGCTAGCTTTCCGGA" >> input/example.fasta
	@echo "Example input files created in input/ directory"

# Run pipeline with example data
run-example:
	@echo "Running pipeline with example data..."
	python -m vlpim run --fasta input/example.fasta --pdb input/example.pdb --mode reduce --log-level DEBUG

# Show system information
info:
	@echo "System Information"
	@echo "=================="
	@echo "Python version:"
	python --version
	@echo ""
	@echo "Pip version:"
	pip --version
	@echo ""
	@echo "Installed packages:"
	pip list | grep -E "(pandas|numpy|requests|scipy)"
	@echo ""
	@echo "External tools check:"
	@which protein_mpnn > /dev/null 2>&1 && echo "✓ ProteinMPNN found" || echo "✗ ProteinMPNN not found"
	@which netMHCIIpan > /dev/null 2>&1 && echo "✓ NetMHCIIpan found" || echo "✗ NetMHCIIpan not found"
	@which alphafold3 > /dev/null 2>&1 && echo "✓ AlphaFold3 found" || echo "✗ AlphaFold3 not found"
	@which interface_analyzer > /dev/null 2>&1 && echo "✓ Rosetta interface_analyzer found" || echo "✗ Rosetta interface_analyzer not found"

# VLPIM Commands
vlpim-help:
	@echo "Running VLPIM help..."
	python -m vlpim help

vlpim-config:
	@echo "Showing VLPIM configuration..."
	python -m vlpim config

vlpim-validate:
	@echo "Validating VLPIM configuration..."
	python -m vlpim validate

vlpim-test:
	@echo "Running VLPIM tests..."
	python -m vlpim test

# Make VLPIM executable (Linux)
vlpim-install:
	@echo "Making VLPIM executable..."
	chmod +x src/vlpim/vlpim
	@echo "VLPIM is now executable. You can run: python -m vlpim help"
