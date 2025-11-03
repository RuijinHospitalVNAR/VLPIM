#!/usr/bin/env python3
"""
NetMHCIIpan Runner Tool

This module provides functionality to evaluate MHC-II binding affinity
using NetMHCIIpan.

Author: [Chufan Wang]
Version: 1.0
Date: 2025
"""

import pandas as pd
import logging
import subprocess
import os
import tempfile
from typing import List, Dict, Optional
from pathlib import Path


def predict_epitopes_with_netmhcii(fasta_path: str, hla_alleles: List[str], output_dir: str) -> pd.DataFrame:
    """
    Predict epitopes using NetMHCIIpan.
    
    Args:
        fasta_path: Path to FASTA file
        hla_alleles: List of HLA alleles to test
        output_dir: Output directory for results
        
    Returns:
        DataFrame containing epitope predictions
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Predicting epitopes using NetMHCIIpan from {fasta_path}")
    
    try:
        # Get NetMHCIIpan command
        from .path_config import PathConfig
        path_config = PathConfig()
        netmhcii_cmd = path_config.get_netmhcii_command()
        
        # Verify tool availability
        if not path_config._check_command_available(netmhcii_cmd):
            raise RuntimeError(f"NetMHCIIpan not found: {netmhcii_cmd}")
        
        # Create temporary output file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
            temp_output = temp_file.name
        
        try:
            # Build NetMHCIIpan command based on official documentation
            cmd_args = [
                netmhcii_cmd,
                "-f", fasta_path,
                "-a", ",".join(hla_alleles),
                "-inptype", "1",  # FASTA format
                "-length", "15",  # Peptide length (variable length supported)
                "-BA",  # Output binding affinity
                "-rank",  # Output %rank scores
                "-outdir", output_dir,
                "-outfile", temp_output,
                "-version", "4.3"  # Specify version 4.3
            ]
            
            logger.info(f"Running NetMHCIIpan: {' '.join(cmd_args)}")
            
            # Execute NetMHCIIpan
            result = subprocess.run(
                cmd_args,
                capture_output=True,
                text=True,
                timeout=1800,  # 30 minutes timeout
                cwd=output_dir
            )
            
            if result.returncode != 0:
                raise RuntimeError(f"NetMHCIIpan failed: {result.stderr}")
            
            # Parse output file
            epitopes_df = _parse_netmhcii_output(temp_output)
            
            logger.info(f"NetMHCIIpan prediction completed: {len(epitopes_df)} epitopes")
            return epitopes_df
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_output):
                os.unlink(temp_output)
                
    except subprocess.TimeoutExpired:
        raise RuntimeError("NetMHCIIpan execution timed out")
    except Exception as e:
        logger.error(f"NetMHCIIpan prediction failed: {e}")
        raise


def _parse_netmhcii_output(output_file: str) -> pd.DataFrame:
    """Parse NetMHCIIpan-4.3 output file based on official format.
    
    Expected format: Pos Peptide ID Allele Core %Rank_EL BA_Rank BA_IC50 BA_Raw Score
    Or alternative: Pos Peptide ID Allele BA_Rank BA_IC50 BA_Raw Score (if Core not available)
    """
    epitopes = []
    
    try:
        with open(output_file, 'r') as f:
            lines = f.readlines()
        
        for line in lines:
            line = line.strip()
            if line.startswith('#') or not line:
                continue
                
            parts = line.split()
            # Try to parse format with Core and %Rank_EL (9+ columns)
            if len(parts) >= 9:
                try:
                    pos = int(parts[0])
                    peptide = parts[1]
                    seq_id = parts[2] if len(parts) > 2 else ""
                    allele = parts[3]
                    core = parts[4] if len(parts) > 4 else ""
                    rank_el = float(parts[5]) if len(parts) > 5 else None
                    ba_rank = float(parts[6]) if len(parts) > 6 else None
                    ba_ic50 = float(parts[7]) if len(parts) > 7 else None
                    ba_raw = float(parts[8]) if len(parts) > 8 else None
                    score = float(parts[9]) if len(parts) > 9 else None
                    
                    # Calculate position information
                    start_pos = pos
                    end_pos = start_pos + len(peptide) - 1
                    
                    epitopes.append({
                        'sequence': peptide,
                        'core': core if core else peptide,  # Use peptide as core if core not available
                        'start': start_pos,
                        'end': end_pos,
                        'score': score if score is not None else ba_raw if ba_raw is not None else 0.0,
                        'rank_el': rank_el,  # %Rank_EL
                        'rank': ba_rank,     # BA_Rank
                        'ic50': ba_ic50,
                        'raw_score': ba_raw,
                        'allele': allele,
                        'seq_id': seq_id,
                        'method': 'NetMHCIIpan-4.3'
                    })
                except (ValueError, IndexError) as e:
                    # Try alternative format without Core (8 columns)
                    if len(parts) >= 8:
                        try:
                            pos = int(parts[0])
                            peptide = parts[1]
                            seq_id = parts[2] if len(parts) > 2 else ""
                            allele = parts[3]
                            ba_rank = float(parts[4])
                            ba_ic50 = float(parts[5])
                            ba_raw = float(parts[6])
                            score = float(parts[7])
                            
                            start_pos = pos
                            end_pos = start_pos + len(peptide) - 1
                            
                            epitopes.append({
                                'sequence': peptide,
                                'core': peptide,  # Use peptide as core when not available
                                'start': start_pos,
                                'end': end_pos,
                                'score': score,
                                'rank_el': None,  # Not available
                                'rank': ba_rank,
                                'ic50': ba_ic50,
                                'raw_score': ba_raw,
                                'allele': allele,
                                'seq_id': seq_id,
                                'method': 'NetMHCIIpan-4.3'
                            })
                        except (ValueError, IndexError):
                            continue
                    continue
    
    except Exception as e:
        logging.getLogger(__name__).error(f"Failed to parse NetMHCIIpan output: {e}")
        raise
    
    return pd.DataFrame(epitopes)


def evaluate_mhc_affinity(mutant_file: str) -> pd.DataFrame:
    """
    Evaluate MHC-II binding affinity for mutant sequences.
    
    Args:
        mutant_file: Path to FASTA file containing mutant sequences
        
    Returns:
        DataFrame containing MHC-II binding results
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Evaluating MHC-II binding for {mutant_file}")
    
    try:
        # Default HLA alleles supported by NetMHCIIpan-4.3
        hla_alleles = [
            "DRB1*01:01", "DRB1*03:01", "DRB1*04:01", "DRB1*07:01",
            "DRB1*08:01", "DRB1*11:01", "DRB1*13:01", "DRB1*15:01",
            "DRB1*16:01", "DRB1*04:05", "DRB1*11:04", "DRB1*13:02",
            "DRB1*14:01", "DRB1*15:02", "DRB1*03:02", "DRB1*04:02"
        ]
        
        # Get output directory
        output_dir = os.path.dirname(mutant_file)
        
        # Use the prediction function
        affinity_df = predict_epitopes_with_netmhcii(mutant_file, hla_alleles, output_dir)
        
        # Group by sequence and calculate average scores
        grouped_df = affinity_df.groupby('sequence').agg({
            'score': 'mean',
            'rank': 'mean'
        }).reset_index()
        
        # Add individual allele rank (percentile) scores
        pivot_rank_df = affinity_df.pivot_table(
            index='sequence',
            columns='allele',
            values='rank',
            fill_value=999
        ).reset_index()
        # Rename columns to match expected format for rank
        pivot_rank_df.columns = [f'Rank_{col}' if col != 'sequence' else col for col in pivot_rank_df.columns]

        # Add individual allele IC50 values
        pivot_ic50_df = affinity_df.pivot_table(
            index='sequence',
            columns='allele',
            values='ic50',
            fill_value=1e9
        ).reset_index()
        # Rename columns to match expected format for IC50
        pivot_ic50_df.columns = [f'IC50_{col}' if col != 'sequence' else col for col in pivot_ic50_df.columns]

        # Merge rank and IC50 wide tables
        merged_df = pd.merge(pivot_rank_df, pivot_ic50_df, on='sequence', how='outer')
        
        logger.info("MHC-II evaluation completed")
        return merged_df
        
    except Exception as e:
        logger.error(f"MHC-II evaluation failed: {e}")
        raise


if __name__ == "__main__":
    # Test the implementation
    logging.basicConfig(level=logging.INFO)
    
    # Create test data
    test_fasta = "test_sequence.fasta"
    test_alleles = ["DRB1*01:01", "DRB1*03:01"]
    
    try:
        # Create test FASTA file
        with open(test_fasta, 'w') as f:
            f.write(">test_protein\nMKLLVLGCTAGCTTTCCGGA\n")
        
        # Test prediction
        results = predict_epitopes_with_netmhcii(test_fasta, test_alleles, ".")
        print(f"Test results: {len(results)} epitopes predicted")
        
    except Exception as e:
        print(f"Test failed: {e}")
    finally:
        # Clean up test file
        if os.path.exists(test_fasta):
            os.unlink(test_fasta)
