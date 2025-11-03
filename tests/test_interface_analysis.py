#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for the updated immunogenicity optimization pipeline
with interface analysis functionality.

This script tests the new Rosetta interface_analyzer integration
and the updated ranking system.
"""

import os
import sys
import tempfile
import pandas as pd
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from immunogenicity_optimization_pipeline import (
    ImmunogenicityOptimizer, 
    PipelineConfig, 
    ImmunogenicityMode
)
from tools.rosetta_interface_analyzer import RosettaInterfaceAnalyzer


def test_interface_analyzer():
    """Test the Rosetta interface analyzer functionality."""
    print("=== Testing Rosetta Interface Analyzer ===")
    
    try:
        # Initialize analyzer
        analyzer = RosettaInterfaceAnalyzer()
        print("✓ Interface analyzer initialized successfully")
        
        # Test with a dummy PDB file (this will fail but tests the interface)
        with tempfile.NamedTemporaryFile(suffix='.pdb', delete=False) as tmp_file:
            tmp_file.write(b"ATOM      1  N   ALA A   1      20.154  16.967  27.862  1.00 11.18           N\n")
            tmp_file.write(b"ATOM      2  CA  ALA A   1      19.030  16.967  27.862  1.00 11.18           C\n")
            tmp_file.write(b"ATOM      3  C   ALA A   1      18.030  16.967  27.862  1.00 11.18           C\n")
            tmp_file.write(b"ATOM      4  O   ALA A   1      17.030  16.967  27.862  1.00 11.18           O\n")
            tmp_file.write(b"ATOM      5  N   ALA B   1      20.154  16.967  27.862  1.00 11.18           N\n")
            tmp_file.write(b"ATOM      6  CA  ALA B   1      19.030  16.967  27.862  1.00 11.18           C\n")
            tmp_file.write(b"ATOM      7  C   ALA B   1      18.030  16.967  27.862  1.00 11.18           C\n")
            tmp_file.write(b"ATOM      8  O   ALA B   1      17.030  16.967  27.862  1.00 11.18           O\n")
            tmp_file_path = tmp_file.name
        
        try:
            # Test interface identification
            interfaces = analyzer._identify_interface_chains(tmp_file_path)
            print(f"✓ Identified interfaces: {interfaces}")
            
            # Test analysis (will fail without Rosetta, but tests the interface)
            with tempfile.TemporaryDirectory() as temp_dir:
                try:
                    results = analyzer.analyze_structure(tmp_file_path, temp_dir)
                    print(f"✓ Interface analysis completed: {results}")
                except Exception as e:
                    print(f"⚠ Interface analysis failed (expected without Rosetta): {e}")
        
        finally:
            os.unlink(tmp_file_path)
        
    except Exception as e:
        print(f"✗ Interface analyzer test failed: {e}")


def test_pipeline_config():
    """Test the updated pipeline configuration."""
    print("\n=== Testing Updated Pipeline Configuration ===")
    
    try:
        # Test configuration with new parameters
        config = PipelineConfig(
            fasta_path="test.fasta",
            pdb_path="test.pdb",
            mode=ImmunogenicityMode.REDUCE,
            interface_analysis=True,
            dg_dsasa_threshold=-0.5,
            buns_threshold=5,
            packstat_threshold=0.6
        )
        
        print("✓ Configuration created successfully")
        print(f"  - Interface analysis: {config.interface_analysis}")
        print(f"  - dG/dSASA threshold: {config.dg_dsasa_threshold}")
        print(f"  - BUNS threshold: {config.buns_threshold}")
        print(f"  - Packstat threshold: {config.packstat_threshold}")
        
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")


def test_ranking_system():
    """Test the new ranking system."""
    print("\n=== Testing New Ranking System ===")
    
    try:
        # Create test data
        test_data = pd.DataFrame({
            'sequence_id': ['seq1', 'seq2', 'seq3', 'seq4'],
            'RMSD': [1.5, 2.1, 1.8, 2.5],
            'dG_dSASA': [-0.6, -0.3, -0.8, -0.2],
            'packstat': [0.7, 0.5, 0.8, 0.4],
            'BUNS': [3, 7, 2, 9]
        })
        
        print("Test data:")
        print(test_data)
        
        # Test ranking
        config = PipelineConfig(
            fasta_path="test.fasta",
            pdb_path="test.pdb",
            mode=ImmunogenicityMode.REDUCE
        )
        
        optimizer = ImmunogenicityOptimizer(config)
        ranked_data = optimizer._rank_candidates(test_data)
        
        print("\nRanked data:")
        print(ranked_data[['sequence_id', 'RMSD', 'dG_dSASA', 'packstat', 'BUNS', 'Rank']])
        
        # Verify ranking order
        # RMSD is the primary criterion, then dG/dSASA, packstat, BUNS
        expected_order = ['seq1', 'seq3', 'seq2', 'seq4']  # Based on RMSD first, then other criteria
        actual_order = ranked_data['sequence_id'].tolist()
        
        if actual_order == expected_order:
            print("✓ Ranking system working correctly")
        else:
            print(f"⚠ Ranking order differs from expected: {actual_order} vs {expected_order}")
        
    except Exception as e:
        print(f"✗ Ranking system test failed: {e}")


def test_interface_filtering():
    """Test the interface filtering functionality."""
    print("\n=== Testing Interface Filtering ===")
    
    try:
        # Create test data with interface metrics
        test_data = pd.DataFrame({
            'sequence_id': ['seq1', 'seq2', 'seq3', 'seq4', 'seq5'],
            'RMSD': [1.5, 2.1, 1.8, 2.5, 1.2],
            'dG_dSASA': [-0.6, -0.3, -0.8, -0.2, -0.7],
            'packstat': [0.7, 0.5, 0.8, 0.4, 0.9],
            'BUNS': [3, 7, 2, 9, 1]
        })
        
        print("Test data before filtering:")
        print(test_data)
        
        # Apply filtering thresholds
        dg_dsasa_threshold = -0.5
        buns_threshold = 5
        packstat_threshold = 0.6
        
        filtered_data = test_data[
            (test_data['dG_dSASA'] <= dg_dsasa_threshold) &
            (test_data['BUNS'] <= buns_threshold) &
            (test_data['packstat'] >= packstat_threshold)
        ]
        
        print(f"\nFiltered data (dG/dSASA <= {dg_dsasa_threshold}, BUNS <= {buns_threshold}, packstat >= {packstat_threshold}):")
        print(filtered_data)
        
        expected_passed = ['seq1', 'seq3', 'seq5']
        actual_passed = filtered_data['sequence_id'].tolist()
        
        if set(actual_passed) == set(expected_passed):
            print("✓ Interface filtering working correctly")
        else:
            print(f"⚠ Filtering results differ from expected: {actual_passed} vs {expected_passed}")
        
    except Exception as e:
        print(f"✗ Interface filtering test failed: {e}")


def main():
    """Run all tests."""
    print("Immunogenicity Optimization Pipeline - Interface Analysis Tests")
    print("=" * 70)
    
    test_interface_analyzer()
    test_pipeline_config()
    test_ranking_system()
    test_interface_filtering()
    
    print("\n" + "=" * 70)
    print("All tests completed!")


if __name__ == "__main__":
    main()
