#!/usr/bin/env python3
"""
ProteinMPNN Wrapper Tool

This module provides functionality to generate mutant sequences
using ProteinMPNN.

Author: [Chufan Wang]
Version: 1.0
Date: 2025
"""

import pandas as pd
import logging
import subprocess
import os
import tempfile
import json
from typing import List, Dict, Optional
from pathlib import Path


def generate_mutants(pdb_path: str, epitope_df: pd.DataFrame, 
                    mode: str, samples_per_temp: int = 20, 
                    temps: List[float] = None) -> List[str]:
    """
    Generate mutant sequences using ProteinMPNN.
    
    Args:
        pdb_path: Path to PDB file
        epitope_df: DataFrame containing epitope information
        mode: Immunogenicity mode (reduce/enhance)
        samples_per_temp: Number of samples per temperature
        temps: List of temperature values
        
    Returns:
        List of generated mutant sequences
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Generating mutants using ProteinMPNN from {pdb_path}")
    
    if temps is None:
        temps = [0.1, 0.3, 0.5]
    
    try:
        # Get ProteinMPNN command
        from .path_config import PathConfig
        path_config = PathConfig()
        proteinmpnn_cmd = path_config.get_proteinmpnn_command()
        
        # Verify tool availability
        if not path_config._check_command_available(proteinmpnn_cmd):
            raise RuntimeError(f"ProteinMPNN not found: {proteinmpnn_cmd}")
        
        # Create temporary directory for outputs
        with tempfile.TemporaryDirectory() as temp_dir:
            mutants = []
            
            # Process each temperature
            for temp in temps:
                logger.info(f"Generating mutants at temperature {temp}")
                
                # Create output file for this temperature
                output_file = os.path.join(temp_dir, f"mutants_T{temp}.fasta")
                
                # Build ProteinMPNN command based on official documentation
                cmd_args = [
                    "python", proteinmpnn_cmd,  # protein_mpnn_run.py
                    "--pdb_path", pdb_path,
                    "--out_folder", temp_dir,
                    "--num_seq_per_target", str(samples_per_temp),
                    "--sampling_temp", str(temp),
                    "--batch_size", "1",  # Default batch size
                    "--max_length", "200000",  # Default max length
                    "--model_name", "v_48_020"  # Default model
                ]
                
                # Add epitope constraints if available
                if not epitope_df.empty:
                    # Create fixed positions file for epitope regions
                    fixed_positions_file = os.path.join(temp_dir, f"fixed_positions_T{temp}.jsonl")
                    _create_fixed_positions_file(epitope_df, fixed_positions_file, mode)
                    cmd_args.extend(["--fixed_positions_jsonl", fixed_positions_file])
                
                logger.info(f"Running ProteinMPNN: {' '.join(cmd_args)}")
                
                # Execute ProteinMPNN
                result = subprocess.run(
                    cmd_args,
                    capture_output=True,
                    text=True,
                    timeout=3600,  # 1 hour timeout
                    cwd=os.path.dirname(proteinmpnn_cmd)
                )
                
                if result.returncode != 0:
                    logger.warning(f"ProteinMPNN failed at temperature {temp}: {result.stderr}")
                    continue
                
                # Parse output files
                temp_mutants = _parse_proteinmpnn_output(temp_dir, temp)
                mutants.extend(temp_mutants)
                
                logger.info(f"Generated {len(temp_mutants)} mutants at temperature {temp}")
            
            logger.info(f"ProteinMPNN generation completed: {len(mutants)} total mutants")
            return mutants
            
    except subprocess.TimeoutExpired:
        raise RuntimeError("ProteinMPNN execution timed out")
    except Exception as e:
        logger.error(f"ProteinMPNN generation failed: {e}")
        raise


def _create_fixed_positions_file(epitope_df: pd.DataFrame, fixed_positions_file: str, mode: str):
    """Create fixed positions file for ProteinMPNN based on official JSONL format."""
    import json
    
    # Create fixed positions dictionary
    fixed_positions = {}
    
    for _, row in epitope_df.iterrows():
        start_pos = int(row['start']) - 1  # Convert to 0-based indexing
        end_pos = int(row['end']) - 1
        
        # Create fixed positions based on mode
        if mode == 'reduce':
            # For immunogenicity reduction, fix epitope regions (don't mutate)
            for pos in range(start_pos, end_pos + 1):
                fixed_positions[f"A{pos}"] = "X"  # Fixed position
        else:  # enhance
            # For immunogenicity enhancement, allow mutations (no fixed positions)
            pass
    
    # Write JSONL file (one JSON object per line)
    with open(fixed_positions_file, 'w') as f:
        json.dump(fixed_positions, f)


def _parse_proteinmpnn_output(output_dir: str, temperature: float) -> List[str]:
    """Parse ProteinMPNN output files based on official format."""
    mutants = []
    
    try:
        # Look for output files in output directory
        for file_name in os.listdir(output_dir):
            if file_name.endswith('.fa') or file_name.endswith('.fasta'):
                fasta_file = os.path.join(output_dir, file_name)
                
                with open(fasta_file, 'r') as f:
                    content = f.read()
                
                # Parse FASTA sequences according to ProteinMPNN output format
                sequences = []
                current_seq = ""
                
                for line in content.split('\n'):
                    if line.startswith('>'):
                        if current_seq:
                            sequences.append(current_seq)
                        current_seq = ""
                    else:
                        current_seq += line.strip()
                
                if current_seq:
                    sequences.append(current_seq)
                
                mutants.extend(sequences)
                
    except Exception as e:
        logging.getLogger(__name__).error(f"Failed to parse ProteinMPNN output: {e}")
        raise
    
    return mutants


if __name__ == "__main__":
    # Test the implementation
    logging.basicConfig(level=logging.INFO)
    
    # Create test data
    test_pdb = "test_protein.pdb"
    test_epitopes = pd.DataFrame({
        'sequence': ['MKLLVL', 'GCTAGCT'],
        'start': [1, 10],
        'end': [6, 16],
        'score': [0.8, 0.6],
        'method': ['NetMHCIIpan', 'NetMHCIIpan']
    })
    
    try:
        # Create test PDB file (minimal)
        with open(test_pdb, 'w') as f:
            f.write("ATOM      1  N   ALA A   1      20.154  16.967  18.544  1.00 11.18           N\n")
            f.write("ATOM      2  CA  ALA A   1      19.030  16.067  18.544  1.00 11.18           C\n")
        
        # Test generation
        mutants = generate_mutants(test_pdb, test_epitopes, "reduce", samples_per_temp=5, temps=[0.1])
        print(f"Test results: {len(mutants)} mutants generated")
        
    except Exception as e:
        print(f"Test failed: {e}")
    finally:
        # Clean up test file
        if os.path.exists(test_pdb):
            os.unlink(test_pdb)
