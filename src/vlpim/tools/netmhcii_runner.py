#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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
from typing import List, Dict, Optional, Union
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
    """Parse NetMHCIIpan-4.3 output file supporting both standard and wide formats."""
    logger = logging.getLogger(__name__)
    
    try:
        with open(output_file, 'r') as f:
            lines = f.readlines()
    except Exception as e:
        logger.error(f"Failed to read NetMHCIIpan output file: {e}")
        raise
    
    if not lines:
        logger.warning("NetMHCIIpan output file is empty")
        return pd.DataFrame()
    
    # Detect wide-table format by looking for HLA allele names in the header
    is_wide_format = False
    hla_alleles: List[str] = []
    
    for line in lines[:3]:
        upper_line = line.upper()
        if ('HLA-' in upper_line) or ('DRB1_' in upper_line) or ('DQA1' in upper_line) or ('DPB' in upper_line):
            # Potential wide-table header, try to extract allele names separated by tabs
            parts = [part.strip() for part in line.split('\t') if part.strip()]
            allele_candidates = [
                part for part in parts
                if ('HLA-' in part.upper()) or ('DRB' in part.upper()) or ('DPA' in part.upper()) or ('DQA' in part.upper())
            ]
            if allele_candidates:
                is_wide_format = True
                hla_alleles = allele_candidates
                break
    
    if is_wide_format:
        logger.info(f"Detected NetMHCIIpan wide-table format with {len(hla_alleles)} alleles")
        return _parse_wide_table_format(lines, hla_alleles)
    
    logger.info("Detected NetMHCIIpan standard tabular format")
    return _parse_standard_format(lines)


def _parse_wide_table_format(lines: List[str], hla_alleles: List[str]) -> pd.DataFrame:
    """
    Parse wide-table NetMHCIIpan format where each allele has grouped columns
    (Core, Inverted, Score, Rank, Score_BA, nM, Rank_BA).
    """
    logger = logging.getLogger(__name__)
    epitopes: List[Dict[str, Union[str, float, int]]] = []
    
    # Identify the start of data (skip comments/empty lines)
    data_start_idx = 0
    for idx, line in enumerate(lines):
        stripped = line.strip()
        if stripped and not stripped.startswith('#'):
            data_start_idx = idx
            break
    
    cols_per_allele = 7
    data_start_col = 4  # After Pos, Peptide, ID, Target
    
    for line in lines[data_start_idx:]:
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue
        parts = stripped.split('\t')
        if len(parts) < data_start_col + 1:
            continue
        
        try:
            pos = int(parts[0])
        except ValueError:
            # Header line encountered unexpectedly
            continue
        
        peptide = parts[1]
        seq_id = parts[2] if len(parts) > 2 else "Sequence"
        
        for idx, allele in enumerate(hla_alleles):
            allele_start_col = data_start_col + idx * cols_per_allele
            if allele_start_col + 6 >= len(parts):
                continue
            
            def _safe_float(value: str) -> Optional[float]:
                try:
                    return float(value)
                except (TypeError, ValueError):
                    return None
            
            core = parts[allele_start_col]
            score = _safe_float(parts[allele_start_col + 2])
            rank = _safe_float(parts[allele_start_col + 3])
            score_ba = _safe_float(parts[allele_start_col + 4])
            nm = _safe_float(parts[allele_start_col + 5])
            rank_ba = _safe_float(parts[allele_start_col + 6])
            
            start_pos = pos
            end_pos = start_pos + len(peptide) - 1
            
            epitopes.append({
                'sequence': peptide,
                'core': core if core and core != 'NA' else peptide,
                'start': start_pos,
                'end': end_pos,
                'score': score if score is not None else 0.0,
                'rank_el': rank,
                'rank': rank_ba,
                'ic50': nm,
                'raw_score': score_ba,
                'allele': allele,
                'seq_id': seq_id,
                'method': 'NetMHCIIpan-4.3'
            })
    
    logger.info(f"Parsed {len(epitopes)} epitope records from wide-table output")
    return pd.DataFrame(epitopes)


def _parse_standard_format(lines: List[str]) -> pd.DataFrame:
    """Parse standard NetMHCIIpan format."""
    epitopes: List[Dict[str, Union[str, float, int]]] = []
    logger = logging.getLogger(__name__)
    
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('#') or not stripped:
            continue
        
        parts = stripped.split()
        if len(parts) < 4:
            continue
        
        try:
            pos = int(parts[0])
            peptide = parts[1]
        except (ValueError, IndexError):
            continue
        
        seq_id = parts[2] if len(parts) > 2 else ""
        allele = parts[3]
        
        # Helper to safely convert float
        def _safe_float(idx: int) -> Optional[float]:
            try:
                return float(parts[idx])
            except (IndexError, ValueError):
                return None
        
        start_pos = pos
        end_pos = start_pos + len(peptide) - 1
        
        if len(parts) >= 10:
            core = parts[4]
            rank_el = _safe_float(5)
            ba_rank = _safe_float(6)
            ba_ic50 = _safe_float(7)
            ba_raw = _safe_float(8)
            score = _safe_float(9)
        else:
            core = peptide if len(parts) >= 4 else ""
            rank_el = None
            ba_rank = _safe_float(4)
            ba_ic50 = _safe_float(5)
            ba_raw = _safe_float(6)
            score = _safe_float(7)
        
        epitopes.append({
            'sequence': peptide,
            'core': core if core else peptide,
            'start': start_pos,
            'end': end_pos,
            'score': score if score is not None else (ba_raw if ba_raw is not None else 0.0),
            'rank_el': rank_el,
            'rank': ba_rank,
            'ic50': ba_ic50,
            'raw_score': ba_raw,
            'allele': allele,
            'seq_id': seq_id,
            'method': 'NetMHCIIpan-4.3'
        })
    
    logger.info(f"Parsed {len(epitopes)} epitope records from standard output")
    return pd.DataFrame(epitopes)


def evaluate_mhc_affinity(mutant_file: str, group_by: str = 'auto') -> pd.DataFrame:
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
        
        # Determine grouping identifier
        if group_by == 'seq_id':
            id_column = 'seq_id' if 'seq_id' in affinity_df.columns else 'sequence'
        elif group_by == 'sequence':
            id_column = 'sequence'
        else:
            if 'seq_id' in affinity_df.columns and affinity_df['seq_id'].notna().any():
                id_column = 'seq_id'
            else:
                id_column = 'sequence'
        
        label_column = 'Sequence_ID' if id_column == 'seq_id' else 'sequence'
        affinity_df[id_column] = affinity_df[id_column].fillna(affinity_df['sequence'])
        
        sequence_lookup = affinity_df[[id_column, 'sequence']].drop_duplicates()
        
        # Add individual allele rank (percentile) scores
        pivot_rank_df = affinity_df.pivot_table(
            index=id_column,
            columns='allele',
            values='rank',
            fill_value=999
        ).reset_index()
        pivot_rank_df.columns = [
            f'Rank_{col}' if col != id_column else label_column for col in pivot_rank_df.columns
        ]

        # Add individual allele IC50 values
        pivot_ic50_df = affinity_df.pivot_table(
            index=id_column,
            columns='allele',
            values='ic50',
            fill_value=1e9
        ).reset_index()
        pivot_ic50_df.columns = [
            f'IC50_{col}' if col != id_column else label_column for col in pivot_ic50_df.columns
        ]

        # Merge rank and IC50 wide tables
        merged_df = pd.merge(pivot_rank_df, pivot_ic50_df, on=label_column, how='outer')
        
        if label_column == 'Sequence_ID':
            merged_df = merged_df.merge(
                sequence_lookup.rename(columns={id_column: 'Sequence_ID', 'sequence': 'Epitope_Sequence'}),
                on='Sequence_ID',
                how='left'
            )
        else:
            merged_df = merged_df.rename(columns={'sequence': 'Epitope_Sequence'})
        
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
