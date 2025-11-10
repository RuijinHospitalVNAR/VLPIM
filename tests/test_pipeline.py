#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for the Immunogenicity Optimization Pipeline.

This script tests the pipeline components and validates the code structure.
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from immunogenicity_optimization_pipeline import (
    ImmunogenicityOptimizer, 
    PipelineConfig, 
    ImmunogenicityMode
)


class TestPipelineConfig(unittest.TestCase):
    """Test cases for PipelineConfig class."""
    
    def test_config_creation(self):
        """Test basic config creation."""
        config = PipelineConfig(
            fasta_path="test.fasta",
            pdb_path="test.pdb",
            mode=ImmunogenicityMode.REDUCE
        )
        
        self.assertEqual(config.fasta_path, "test.fasta")
        self.assertEqual(config.pdb_path, "test.pdb")
        self.assertEqual(config.mode, ImmunogenicityMode.REDUCE)
        self.assertEqual(config.output_dir, "results")
        self.assertEqual(config.log_level, "INFO")
    
    def test_config_defaults(self):
        """Test config default values."""
        config = PipelineConfig(
            fasta_path="test.fasta",
            pdb_path="test.pdb",
            mode=ImmunogenicityMode.ENHANCE
        )
        
        self.assertEqual(config.samples_per_temp, 20)
        self.assertEqual(config.temperatures, [0.1, 0.3, 0.5])
        self.assertEqual(config.max_candidates, 10)
        self.assertEqual(config.rmsd_threshold, 2.0)
        self.assertEqual(config.dockq_threshold, 0.23)
        self.assertEqual(config.neutral_score, 50.0)


class TestImmunogenicityOptimizer(unittest.TestCase):
    """Test cases for ImmunogenicityOptimizer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = PipelineConfig(
            fasta_path="test.fasta",
            pdb_path="test.pdb",
            mode=ImmunogenicityMode.REDUCE,
            output_dir="test_results"
        )
        self.optimizer = ImmunogenicityOptimizer(self.config)
    
    def test_optimizer_initialization(self):
        """Test optimizer initialization."""
        self.assertEqual(self.optimizer.config, self.config)
        self.assertIsNotNone(self.optimizer.logger)
        self.assertIsNotNone(self.optimizer.start_time)
    
    def test_compute_immunogenicity_scores_reduce(self):
        """Test immunogenicity score computation for reduction mode."""
        import pandas as pd
        
        # Create test data (lower IC50 -> stronger binding)
        df = pd.DataFrame({
            'sequence_id': ['seq1', 'seq2', 'seq3'],
            'IC50_DRB1*01:01': [25.0, 150.0, 400.0],
            'IC50_DRB1*03:01': [30.0, 180.0, 420.0]
        })
        
        # Test reduce mode (strong binding should yield higher penalty scores)
        result_df = self.optimizer.compute_immunogenicity_scores(df)
        
        # Check that score columns were added
        self.assertIn('Score_DRB1*01:01', result_df.columns)
        self.assertIn('Score_DRB1*03:01', result_df.columns)
        self.assertIn('Overall_Immunogenicity_Score', result_df.columns)
        
        # Strong binders (seq1) should have higher scores than weak binders (seq3)
        self.assertGreater(result_df.loc[0, 'Score_DRB1*01:01'], result_df.loc[2, 'Score_DRB1*01:01'])
    
    def test_compute_immunogenicity_scores_enhance(self):
        """Test immunogenicity score computation for enhancement mode."""
        import pandas as pd
        
        # Change mode to enhance
        self.optimizer.config.mode = ImmunogenicityMode.ENHANCE
        
        # Create test data
        df = pd.DataFrame({
            'sequence_id': ['seq1', 'seq2', 'seq3'],
            'IC50_DRB1*01:01': [25.0, 150.0, 400.0],
            'IC50_DRB1*03:01': [30.0, 180.0, 420.0]
        })
        
        # Test enhance mode (strong binding should yield lower scores)
        result_df = self.optimizer.compute_immunogenicity_scores(df)
        
        # Check that score columns were added
        self.assertIn('Score_DRB1*01:01', result_df.columns)
        self.assertIn('Score_DRB1*03:01', result_df.columns)
        self.assertIn('Overall_Immunogenicity_Score', result_df.columns)
        
        # Strong binders (seq1) should have lower scores than weak binders (seq3)
        self.assertLess(result_df.loc[0, 'Score_DRB1*01:01'], result_df.loc[2, 'Score_DRB1*01:01'])
    
    def test_compute_immunogenicity_scores_empty_df(self):
        """Test immunogenicity score computation with empty DataFrame."""
        import pandas as pd
        
        df = pd.DataFrame()
        result_df = self.optimizer.compute_immunogenicity_scores(df)
        
        self.assertTrue(result_df.empty)
    
    def test_compute_immunogenicity_scores_identical_ranks(self):
        """Test immunogenicity score computation with identical ranks."""
        import pandas as pd
        
        # Create test data with identical ranks
        df = pd.DataFrame({
            'sequence_id': ['seq1', 'seq2', 'seq3'],
            'IC50_DRB1*01:01': [100.0, 100.0, 100.0],
            'IC50_DRB1*03:01': [200.0, 200.0, 200.0]
        })
        
        result_df = self.optimizer.compute_immunogenicity_scores(df)
        
        # Check that neutral scores were assigned
        self.assertEqual(result_df.loc[0, 'Score_DRB1*01:01'], 50.0)
        self.assertEqual(result_df.loc[0, 'Score_DRB1*03:01'], 50.0)


class TestInputValidation(unittest.TestCase):
    """Test cases for input validation."""
    
    def test_validate_inputs_success(self):
        """Test successful input validation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            fasta_file = os.path.join(temp_dir, "test.fasta")
            pdb_file = os.path.join(temp_dir, "test.pdb")
            
            with open(fasta_file, 'w') as f:
                f.write(">test_sequence\nMKLLVLGCTAGCT\n")
            
            with open(pdb_file, 'w') as f:
                f.write("ATOM      1  N   ALA A   1      20.154  16.967  23.862  1.00 11.18           N\n")
            
            config = PipelineConfig(
                fasta_path=fasta_file,
                pdb_path=pdb_file,
                mode=ImmunogenicityMode.REDUCE
            )
            
            optimizer = ImmunogenicityOptimizer(config)
            
            # Should not raise an exception
            optimizer._validate_inputs()
    
    def test_validate_inputs_missing_fasta(self):
        """Test input validation with missing FASTA file."""
        config = PipelineConfig(
            fasta_path="nonexistent.fasta",
            pdb_path="test.pdb",
            mode=ImmunogenicityMode.REDUCE
        )
        
        optimizer = ImmunogenicityOptimizer(config)
        
        with self.assertRaises(FileNotFoundError):
            optimizer._validate_inputs()
    
    def test_validate_inputs_missing_pdb(self):
        """Test input validation with missing PDB file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            fasta_file = os.path.join(temp_dir, "test.fasta")
            
            with open(fasta_file, 'w') as f:
                f.write(">test_sequence\nMKLLVLGCTAGCT\n")
            
            config = PipelineConfig(
                fasta_path=fasta_file,
                pdb_path="nonexistent.pdb",
                mode=ImmunogenicityMode.REDUCE
            )
            
            optimizer = ImmunogenicityOptimizer(config)
            
            with self.assertRaises(FileNotFoundError):
                optimizer._validate_inputs()
    
    def test_validate_inputs_invalid_extension(self):
        """Test input validation with invalid file extensions."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create files with wrong extensions
            fasta_file = os.path.join(temp_dir, "test.txt")
            pdb_file = os.path.join(temp_dir, "test.txt")
            
            with open(fasta_file, 'w') as f:
                f.write(">test_sequence\nMKLLVLGCTAGCT\n")
            
            with open(pdb_file, 'w') as f:
                f.write("ATOM      1  N   ALA A   1      20.154  16.967  23.862  1.00 11.18           N\n")
            
            config = PipelineConfig(
                fasta_path=fasta_file,
                pdb_path=pdb_file,
                mode=ImmunogenicityMode.REDUCE
            )
            
            optimizer = ImmunogenicityOptimizer(config)
            
            with self.assertRaises(ValueError):
                optimizer._validate_inputs()


class TestMockPipeline(unittest.TestCase):
    """Test cases with mocked external dependencies."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = PipelineConfig(
            fasta_path="test.fasta",
            pdb_path="test.pdb",
            mode=ImmunogenicityMode.REDUCE,
            output_dir="test_results"
        )
    
    @patch('immunogenicity_optimization_pipeline.predict_structure')
    @patch('immunogenicity_optimization_pipeline.evaluate_mhc_affinity')
    @patch.object(ImmunogenicityOptimizer, '_write_mutated_epitope_fasta')
    @patch.object(ImmunogenicityOptimizer, 'generate_mutant_sequences')
    @patch.object(ImmunogenicityOptimizer, 'predict_epitopes')
    def test_mock_pipeline_run(self, mock_epitopes, mock_mutants, mock_epitope_fasta,
                               mock_mhc, mock_af3):
        """Test pipeline run with mocked dependencies."""
        import pandas as pd
        
        # Mock return values
        mock_epitopes.return_value = pd.DataFrame({
            'sequence': ['AAAAAA', 'BBBBBB'],
            'start': [1, 7],
            'end': [6, 12]
        })
        
        mock_mutants.return_value = ['AAAAAAAAAAAA', 'BBBBBBBBBBBB']
        mock_epitope_fasta.return_value = (
            'mock_epitopes.fasta',
            {
                'mutant_0000|epitope_0000': 'mutant_0000',
                'mutant_0001|epitope_0001': 'mutant_0001'
            }
        )
        
        mock_mhc.return_value = pd.DataFrame({
            'Sequence_ID': ['mutant_0000|epitope_0000', 'mutant_0001|epitope_0001'],
            'IC50_DRB1*01:01': [25.0, 400.0],
            'IC50_DRB1*03:01': [30.0, 420.0]
        })
        
        mock_af3.return_value = pd.DataFrame({
            'sequence_id': ['mutant_0000', 'mutant_0001'],
            'pdb_path': ['path1.pdb', 'path2.pdb'],
            'confidence_score': [85.0, 75.0],
            'structure_length': [120, 118]
        })
        
        # Create optimizer
        optimizer = ImmunogenicityOptimizer(self.config)
        
        # Run pipeline
        results = optimizer.run_pipeline()
        
        # Verify results
        self.assertIn('epitopes', results)
        self.assertIn('mutants', results)
        self.assertIn('mhc_binding', results)
        self.assertIn('final_candidates', results)
        self.assertIn('runtime', results)
        
        # Verify mock calls
        mock_epitopes.assert_called_once()
        mock_mutants.assert_called_once()
        mock_mhc.assert_called_once()
        mock_af3.assert_called_once()


def run_tests():
    """Run all tests."""
    print("Running Immunogenicity Optimization Pipeline Tests...")
    print("=" * 60)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestPipelineConfig))
    test_suite.addTest(unittest.makeSuite(TestImmunogenicityOptimizer))
    test_suite.addTest(unittest.makeSuite(TestInputValidation))
    test_suite.addTest(unittest.makeSuite(TestMockPipeline))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("✅ All tests passed!")
    else:
        print(f"❌ {len(result.failures)} test(s) failed, {len(result.errors)} error(s)")
        for failure in result.failures:
            print(f"FAIL: {failure[0]}")
            print(f"      {failure[1]}")
        for error in result.errors:
            print(f"ERROR: {error[0]}")
            print(f"       {error[1]}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
