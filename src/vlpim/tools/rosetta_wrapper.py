#!/usr/bin/env python3
"""
Rosetta Interface Analyzer Wrapper Tool

This module provides functionality to analyze protein-protein interfaces
using Rosetta interface_analyzer.

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
from typing import List, Dict, Optional, Tuple
from pathlib import Path


def analyze_interface(pdb_path: str, output_dir: str) -> Dict:
    """
    Analyze protein-protein interface using Rosetta interface_analyzer.
    
    Args:
        pdb_path: Path to PDB file
        output_dir: Output directory for results
        
    Returns:
        Dictionary containing interface analysis results
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Analyzing interface using Rosetta for {pdb_path}")
    
    try:
        # Get Rosetta command
        from .path_config import PathConfig
        path_config = PathConfig()
        rosetta_cmd = path_config.get_rosetta_command()
        
        # Verify tool availability
        if not path_config._check_command_available(rosetta_cmd):
            raise RuntimeError(f"Rosetta interface_analyzer not found: {rosetta_cmd}")
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Build Rosetta interface_analyzer command based on official documentation
        cmd_args = [
            rosetta_cmd,
            "-s", pdb_path,
            "-out:file:scorefile", os.path.join(output_dir, "interface_score.sc"),
            "-out:file:o", os.path.join(output_dir, "interface_analysis.pdb"),
            "-interface_analyzer:interface", "A_B",  # Define interface chains
            "-interface_analyzer:compute_packstat", "true",  # Compute packstat
            "-interface_analyzer:pack_separated", "true",  # Pack separated
            "-interface_analyzer:pack_together", "true",  # Pack together
            "-interface_analyzer:use_centroid", "false",  # Use full atom
            "-interface_analyzer:compute_interface_delta_hbond_unsat", "true",  # Compute BUNS
            "-interface_analyzer:compute_interface_sc", "true",  # Compute interface SC
            "-out:file:silent", os.path.join(output_dir, "interface_analysis.silent")  # Silent output
        ]
        
        logger.info(f"Running Rosetta: {' '.join(cmd_args)}")
        
        # Execute Rosetta
        result = subprocess.run(
            cmd_args,
            capture_output=True,
            text=True,
            timeout=1800,  # 30 minutes timeout
            cwd=os.path.dirname(rosetta_cmd)
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"Rosetta failed: {result.stderr}")
        
        # Parse output files
        interface_results = _parse_rosetta_output(output_dir)
        
        logger.info("Rosetta interface analysis completed")
        return interface_results
        
    except subprocess.TimeoutExpired:
        raise RuntimeError("Rosetta execution timed out")
    except Exception as e:
        logger.error(f"Rosetta interface analysis failed: {e}")
        raise


def _parse_rosetta_output(output_dir: str) -> Dict:
    """Parse Rosetta interface_analyzer output files based on official format."""
    results = {
        'dg_dsasa': 0.0,
        'packstat': 0.0,
        'buns': 0,
        'interface_area': 0.0,
        'buried_surface_area': 0.0,
        'interface_sc': 0.0,
        'delta_unsat_hbonds': 0
    }
    
    try:
        # Parse score file (main output)
        score_file = os.path.join(output_dir, "interface_score.sc")
        if os.path.exists(score_file):
            with open(score_file, 'r') as f:
                lines = f.readlines()
            
            for line in lines:
                if line.startswith('SCORE:'):
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part == 'dG_separated':
                            try:
                                results['dg_dsasa'] = float(parts[i+1])
                            except (ValueError, IndexError):
                                pass
                        elif part == 'packstat':
                            try:
                                results['packstat'] = float(parts[i+1])
                            except (ValueError, IndexError):
                                pass
                        elif part == 'delta_unsat_hbonds':
                            try:
                                results['buns'] = int(float(parts[i+1]))
                            except (ValueError, IndexError):
                                pass
                        elif part == 'interface_sc':
                            try:
                                results['interface_sc'] = float(parts[i+1])
                            except (ValueError, IndexError):
                                pass
                        elif part == 'dSASA_int':
                            try:
                                results['interface_area'] = float(parts[i+1])
                            except (ValueError, IndexError):
                                pass
        
        # Calculate buried surface area (interface area / 2)
        results['buried_surface_area'] = results['interface_area'] / 2.0
        
        # Parse silent file for additional metrics if available
        silent_file = os.path.join(output_dir, "interface_analysis.silent")
        if os.path.exists(silent_file):
            _parse_silent_file(silent_file, results)
        
    except Exception as e:
        logging.getLogger(__name__).error(f"Failed to parse Rosetta output: {e}")
    
    return results


def _parse_silent_file(silent_file: str, results: Dict):
    """Parse Rosetta silent file for additional metrics."""
    try:
        with open(silent_file, 'r') as f:
            lines = f.readlines()
        
        for line in lines:
            if line.startswith('SCORE:'):
                parts = line.split()
                for i, part in enumerate(parts):
                    if part == 'dG_separated' and results['dg_dsasa'] == 0.0:
                        try:
                            results['dg_dsasa'] = float(parts[i+1])
                        except (ValueError, IndexError):
                            pass
                    elif part == 'packstat' and results['packstat'] == 0.0:
                        try:
                            results['packstat'] = float(parts[i+1])
                        except (ValueError, IndexError):
                            pass
                            
    except Exception as e:
        logging.getLogger(__name__).warning(f"Failed to parse silent file: {e}")


def calculate_interface_metrics(pdb_path: str, output_dir: str) -> Dict:
    """
    Calculate interface metrics using Rosetta.
    
    Args:
        pdb_path: Path to PDB file
        output_dir: Output directory for results
        
    Returns:
        Dictionary containing interface metrics
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Calculating interface metrics for {pdb_path}")
    
    try:
        # Run interface analysis
        interface_results = analyze_interface(pdb_path, output_dir)
        
        # Calculate additional metrics
        metrics = {
            'dg_dsasa': interface_results['dg_dsasa'],
            'packstat': interface_results['packstat'],
            'buns': interface_results['buns'],
            'interface_area': interface_results['interface_area'],
            'buried_surface_area': interface_results['buried_surface_area'],
            'interface_quality': _assess_interface_quality(interface_results)
        }
        
        logger.info("Interface metrics calculation completed")
        return metrics
        
    except Exception as e:
        logger.error(f"Interface metrics calculation failed: {e}")
        raise


def _assess_interface_quality(interface_results: Dict) -> str:
    """Assess interface quality based on Rosetta metrics."""
    dg_dsasa = interface_results['dg_dsasa']
    packstat = interface_results['packstat']
    buns = interface_results['buns']
    interface_sc = interface_results['interface_sc']
    
    # Quality assessment criteria based on Rosetta literature
    # dG_separated: more negative = better binding
    # packstat: higher = better packing (0-1 scale)
    # delta_unsat_hbonds: lower = fewer unsatisfied hydrogen bonds
    # interface_sc: higher = more side chain interactions
    
    score = 0
    
    # dG_separated scoring (more negative is better)
    if dg_dsasa < -10.0:
        score += 3
    elif dg_dsasa < -5.0:
        score += 2
    elif dg_dsasa < -1.0:
        score += 1
    
    # packstat scoring (higher is better)
    if packstat > 0.7:
        score += 3
    elif packstat > 0.5:
        score += 2
    elif packstat > 0.3:
        score += 1
    
    # BUNS scoring (lower is better)
    if buns < 2:
        score += 3
    elif buns < 5:
        score += 2
    elif buns < 10:
        score += 1
    
    # interface_sc scoring (higher is better)
    if interface_sc > 50:
        score += 1
    
    # Overall quality assessment
    if score >= 8:
        return "excellent"
    elif score >= 6:
        return "good"
    elif score >= 4:
        return "fair"
    else:
        return "poor"


if __name__ == "__main__":
    # Test the implementation
    logging.basicConfig(level=logging.INFO)
    
    # Create test PDB file
    test_pdb = "test_interface.pdb"
    
    try:
        # Create minimal test PDB file
        with open(test_pdb, 'w') as f:
            f.write("ATOM      1  N   ALA A   1      20.154  16.967  18.544  1.00 11.18           N\n")
            f.write("ATOM      2  CA  ALA A   1      19.030  16.067  18.544  1.00 11.18           C\n")
        
        # Test interface analysis
        results = analyze_interface(test_pdb, ".")
        print(f"Test results: {results}")
        
    except Exception as e:
        print(f"Test failed: {e}")
    finally:
        # Clean up test file
        if os.path.exists(test_pdb):
            os.unlink(test_pdb)
