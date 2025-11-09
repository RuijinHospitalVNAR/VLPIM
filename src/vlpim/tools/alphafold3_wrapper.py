#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AlphaFold3 Wrapper Tool

This module provides functionality to predict protein structures
using AlphaFold3.

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
import numpy as np
import re
import shutil
from typing import List, Dict, Optional, Tuple, Union
from pathlib import Path


def predict_structure(sequences: List[str], output_dir: str, 
                     max_candidates: int = 10) -> pd.DataFrame:
    """
    Predict protein structures using AlphaFold3.
    
    Args:
        sequences: List of protein sequences
        output_dir: Output directory for results
        max_candidates: Maximum number of structure candidates
        
    Returns:
        DataFrame containing structure prediction results
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Predicting structures using AlphaFold3 for {len(sequences)} sequences")
    
    try:
        # Get AlphaFold3 command
        from .path_config import PathConfig
        path_config = PathConfig()
        alphafold3_cmd = path_config.get_alphafold3_command()
        
        # Verify tool availability
        if not path_config._check_command_available(alphafold3_cmd):
            raise RuntimeError(f"AlphaFold3 not found: {alphafold3_cmd}")
        
        # Create temporary directory for inputs
        with tempfile.TemporaryDirectory() as temp_dir:
            results = []
            
            # Process each sequence
            for i, sequence in enumerate(sequences[:max_candidates]):
                logger.info(f"Predicting structure for sequence {i+1}/{min(len(sequences), max_candidates)}")
                
                # Create FASTA file for this sequence
                fasta_file = os.path.join(temp_dir, f"sequence_{i}.fasta")
                with open(fasta_file, 'w') as f:
                    f.write(f">sequence_{i}\n{sequence}\n")
                
                # Create output directory for this sequence
                seq_output_dir = os.path.join(output_dir, f"alphafold3_seq_{i}")
                os.makedirs(seq_output_dir, exist_ok=True)
                
                # Build AlphaFold3 command based on official documentation
                cmd_args = [
                    "python", "run_alphafold.py",  # Official entry point
                    "--json_path", _create_input_json(fasta_file, seq_output_dir),
                    "--model_dir", _get_model_weights_path(),
                    "--output_dir", seq_output_dir,
                    "--run_data_pipeline", "true",  # Enable data pipeline
                    "--run_inference", "true"       # Enable inference
                ]
                
                logger.info(f"Running AlphaFold3: {' '.join(cmd_args)}")
                
                # Execute AlphaFold3
                result = subprocess.run(
                    cmd_args,
                    capture_output=True,
                    text=True,
                    timeout=7200,  # 2 hours timeout
                    cwd=os.path.dirname(alphafold3_cmd)
                )
                
                if result.returncode != 0:
                    logger.warning(f"AlphaFold3 failed for sequence {i}: {result.stderr}")
                    continue
                
                # Parse output files
                structure_info = _parse_alphafold3_output(seq_output_dir, i)
                if structure_info:
                    results.append(structure_info)
                
                logger.info(f"Structure prediction completed for sequence {i}")
            
            logger.info(f"AlphaFold3 prediction completed: {len(results)} structures")
            return pd.DataFrame(results)
            
    except subprocess.TimeoutExpired:
        raise RuntimeError("AlphaFold3 execution timed out")
    except Exception as e:
        logger.error(f"AlphaFold3 prediction failed: {e}")
        raise


def _create_input_json(fasta_file: str, output_dir: str) -> str:
    """Create AlphaFold3 input JSON file based on official format."""
    import json
    
    # Read FASTA file to get sequence
    sequence = ""
    with open(fasta_file, 'r') as f:
        lines = f.readlines()
        for line in lines:
            if not line.startswith('>'):
                sequence += line.strip()
    
    # Create input JSON according to AlphaFold3 format
    input_data = {
        "input": {
            "sequence": sequence,
            "chain_id": "A"
        },
        "output": {
            "output_dir": output_dir
        }
    }
    
    # Save JSON file
    json_file = os.path.join(output_dir, "input.json")
    with open(json_file, 'w') as f:
        json.dump(input_data, f, indent=2)
    
    return json_file


def _get_model_weights_path() -> str:
    """Get AlphaFold3 model weights path from configuration."""
    from .path_config import PathConfig
    path_config = PathConfig()
    
    # Try to get model weights path from environment or config
    model_path = os.getenv('ALPHAFOLD3_MODEL_DIR', '')
    if not model_path:
        # Default path based on official documentation
        model_path = os.path.join(path_config.ALPHAFOLD3_PATH, "models")
    
    return model_path


def _parse_alphafold3_output(output_dir: str, sequence_id: int) -> Optional[Dict]:
    """Parse AlphaFold3 output files."""
    try:
        # Look for PDB files in output directory
        pdb_files = []
        for file_name in os.listdir(output_dir):
            if file_name.endswith('.pdb'):
                pdb_files.append(os.path.join(output_dir, file_name))
        
        if not pdb_files:
            return None
        
        # Get the best ranked structure (usually ranked_0.pdb)
        best_pdb = None
        for pdb_file in pdb_files:
            if 'ranked_0.pdb' in pdb_file:
                best_pdb = pdb_file
                break
        
        if not best_pdb:
            best_pdb = pdb_files[0]  # Use first available PDB
        
        # Calculate basic structure metrics
        structure_info = {
            'sequence_id': sequence_id,
            'pdb_path': best_pdb,
            'num_models': len(pdb_files),
            'confidence_score': _calculate_confidence_score(best_pdb),
            'structure_length': _get_structure_length(best_pdb)
        }
        
        return structure_info
        
    except Exception as e:
        logging.getLogger(__name__).error(f"Failed to parse AlphaFold3 output: {e}")
        return None


def _calculate_confidence_score(pdb_file: str) -> float:
    """Calculate confidence score from PDB file."""
    try:
        # Simple confidence calculation based on B-factors
        # In practice, AlphaFold3 provides confidence scores in the PDB file
        with open(pdb_file, 'r') as f:
            lines = f.readlines()
        
        b_factors = []
        for line in lines:
            if line.startswith('ATOM'):
                try:
                    b_factor = float(line[60:66].strip())
                    b_factors.append(b_factor)
                except (ValueError, IndexError):
                    continue
        
        if b_factors:
            # Convert B-factors to confidence scores (simplified)
            avg_b_factor = sum(b_factors) / len(b_factors)
            confidence = max(0, min(100, 100 - avg_b_factor))
            return round(confidence, 2)
        
        return 50.0  # Default confidence
        
    except Exception as e:
        logging.getLogger(__name__).warning(f"Failed to calculate confidence score: {e}")
        return 50.0


def _get_structure_length(pdb_file: str) -> int:
    """Get structure length from PDB file."""
    try:
        with open(pdb_file, 'r') as f:
            lines = f.readlines()
        
        residues = set()
        for line in lines:
            if line.startswith('ATOM'):
                try:
                    res_num = int(line[22:26].strip())
                    residues.add(res_num)
                except (ValueError, IndexError):
                    continue
        
        return len(residues)
        
    except Exception as e:
        logging.getLogger(__name__).warning(f"Failed to get structure length: {e}")
        return 0


def parse_pdb(pdb_path: str) -> Optional[np.ndarray]:
    """Parse PDB file and extract CA atom coordinates."""
    ca_coords = []
    try:
        with open(pdb_path, 'r') as handle:
            for line in handle:
                if line.startswith(('ATOM', 'HETATM')):
                    atom_name = line[12:16].strip()
                    if atom_name == 'CA':
                        try:
                            x = float(line[30:38])
                            y = float(line[38:46])
                            z = float(line[46:54])
                        except (ValueError, IndexError):
                            continue
                        ca_coords.append([x, y, z])
        if not ca_coords:
            logging.getLogger(__name__).warning(f"No CA atoms found in PDB: {pdb_path}")
            return None
        return np.asarray(ca_coords, dtype=float)
    except Exception as exc:
        logging.getLogger(__name__).error(f"Failed to parse PDB {pdb_path}: {exc}")
        return None


def parse_cif(cif_path: str) -> Optional[np.ndarray]:
    """Parse CIF file and extract CA atom coordinates."""
    ca_coords: List[List[float]] = []
    try:
        in_atom_site = False
        header_cols: Dict[str, int] = {}
        with open(cif_path, 'r') as handle:
            for raw_line in handle:
                line = raw_line.strip()
                if line.startswith('loop_'):
                    in_atom_site = False
                    header_cols = {}
                    continue
                if line.startswith('_atom_site.'):
                    in_atom_site = True
                    col_name = line.replace('_atom_site.', '').strip()
                    header_cols[col_name] = len(header_cols)
                    continue
                if in_atom_site and line and not line.startswith('#'):
                    parts = line.split()
                    if len(parts) < 13:
                        continue
                    atom_id_idx = header_cols.get('label_atom_id', 3)
                    x_idx = header_cols.get('Cartn_x', 10)
                    y_idx = header_cols.get('Cartn_y', 11)
                    z_idx = header_cols.get('Cartn_z', 12)
                    if max(atom_id_idx, x_idx, y_idx, z_idx) >= len(parts):
                        continue
                    if parts[atom_id_idx] == 'CA':
                        try:
                            x = float(parts[x_idx])
                            y = float(parts[y_idx])
                            z = float(parts[z_idx])
                            ca_coords.append([x, y, z])
                        except (ValueError, IndexError):
                            continue
        if not ca_coords:
            logging.getLogger(__name__).warning(f"No CA atoms found in CIF: {cif_path}")
            return None
        return np.asarray(ca_coords, dtype=float)
    except Exception as exc:
        logging.getLogger(__name__).error(f"Failed to parse CIF {cif_path}: {exc}")
        return None


def parse_structure(structure_path: str) -> Optional[np.ndarray]:
    """Parse structure file (PDB or CIF) and extract CA atom coordinates."""
    if structure_path.lower().endswith('.pdb'):
        return parse_pdb(structure_path)
    if structure_path.lower().endswith('.cif'):
        return parse_cif(structure_path)
    logging.getLogger(__name__).warning(f"Unsupported structure format for RMSD: {structure_path}")
    return None


def _center_coordinates(coords: np.ndarray) -> np.ndarray:
    """Center coordinates at origin."""
    return coords - np.mean(coords, axis=0)


def kabsch_algorithm(reference: np.ndarray, mobile: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Compute optimal rotation using the Kabsch algorithm."""
    ref_centered = _center_coordinates(reference)
    mob_centered = _center_coordinates(mobile)
    covariance = mob_centered.T @ ref_centered
    U, _, Vt = np.linalg.svd(covariance)
    rotation = U @ Vt
    if np.linalg.det(rotation) < 0:
        U[:, -1] *= -1
        rotation = U @ Vt
    translation = np.mean(reference, axis=0) - rotation @ np.mean(mobile, axis=0)
    return rotation, translation


def calculate_rmsd_kabsch(reference_file: str, candidate_file: str) -> float:
    """Calculate RMSD using the Kabsch algorithm on CA atoms."""
    logger = logging.getLogger(__name__)
    ref_coords = parse_structure(reference_file)
    mob_coords = parse_structure(candidate_file)
    if ref_coords is None:
        raise ValueError(f"No CA atoms found in reference structure {reference_file}")
    if mob_coords is None:
        raise ValueError(f"No CA atoms found in candidate structure {candidate_file}")
    min_len = min(len(ref_coords), len(mob_coords))
    if min_len < 3:
        raise ValueError("Not enough atoms for RMSD calculation (need at least 3 CA atoms)")
    ref_subset = ref_coords[:min_len]
    mob_subset = mob_coords[:min_len]
    rotation, translation = kabsch_algorithm(ref_subset, mob_subset)
    mob_aligned = (rotation @ mob_subset.T).T + translation
    squared_diff = np.sum((ref_subset - mob_aligned) ** 2, axis=1)
    rmsd = float(np.sqrt(np.mean(squared_diff)))
    logger.debug(f"Kabsch RMSD ({os.path.basename(candidate_file)}): {rmsd:.4f}")
    return rmsd


def _get_ca_atoms_for_chain(structure_path: str, chain_id: Optional[str] = None) -> List["Atom"]:
    """Extract Bio.PDB Atom objects for CA atoms."""
    from Bio.PDB import PDBParser, MMCIFParser

    parser = MMCIFParser(QUIET=True) if structure_path.lower().endswith('.cif') else PDBParser(QUIET=True)
    structure = parser.get_structure('structure', structure_path)
    model = next(structure.get_models())

    ca_atoms: List["Atom"] = []
    for chain in model:
        if chain_id and chain.id != chain_id:
            continue
        for residue in chain:
            atom = residue.child_dict.get('CA') if hasattr(residue, 'child_dict') else None
            if atom is not None:
                ca_atoms.append(atom)
    return ca_atoms


def calculate_rmsd_biopython(reference_file: str, candidate_file: str) -> float:
    """Calculate RMSD using Bio.PDB Superimposer on CA atoms."""
    logger = logging.getLogger(__name__)
    try:
        from Bio.PDB import PDBParser, MMCIFParser, Superimposer
    except Exception as exc:
        raise ImportError(f"Biopython is required for RMSD calculation: {exc}")

    parser_ref = MMCIFParser(QUIET=True) if reference_file.lower().endswith('.cif') else PDBParser(QUIET=True)
    parser_mob = MMCIFParser(QUIET=True) if candidate_file.lower().endswith('.cif') else PDBParser(QUIET=True)
    ref_structure = parser_ref.get_structure('ref', reference_file)
    mob_structure = parser_mob.get_structure('mob', candidate_file)

    ref_model = next(ref_structure.get_models())
    mob_model = next(mob_structure.get_models())

    ref_ca = [atom for atom in ref_model.get_atoms() if atom.get_id() == 'CA']
    mob_ca = [atom for atom in mob_model.get_atoms() if atom.get_id() == 'CA']

    if not ref_ca or not mob_ca:
        raise ValueError("No CA atoms found in one or both structures for Biopython RMSD")

    n_atoms = min(len(ref_ca), len(mob_ca))
    if n_atoms < 3:
        raise ValueError("Not enough atoms for RMSD calculation (need at least 3 CA atoms)")

    super_imposer = Superimposer()
    super_imposer.set_atoms(ref_ca[:n_atoms], mob_ca[:n_atoms])
    rmsd = float(super_imposer.rms)
    logger.debug(f"Biopython RMSD ({os.path.basename(candidate_file)}): {rmsd:.4f}")
    return rmsd


def calculate_rmsd_iterative(reference_file: str,
                             candidate_file: str,
                             *,
                             chain_ref: Optional[str] = None,
                             chain_mob: Optional[str] = None,
                             cutoff: float = 2.0,
                             max_cycles: int = 5) -> Tuple[float, int, int]:
    """
    Iterative prune alignment using Bio.PDB Superimposer.

    Returns (rmsd, aligned_atoms, cycles_used).
    """
    logger = logging.getLogger(__name__)
    try:
        from Bio.PDB import Superimposer
    except Exception as exc:
        raise ImportError(f"Biopython is required for iterative RMSD: {exc}")

    ref_atoms = _get_ca_atoms_for_chain(reference_file, chain_ref)
    mob_atoms = _get_ca_atoms_for_chain(candidate_file, chain_mob)
    if not ref_atoms or not mob_atoms:
        raise ValueError("No CA atoms found for iterative RMSD calculation")

    n_atoms = min(len(ref_atoms), len(mob_atoms))
    if n_atoms < 3:
        raise ValueError("Not enough atoms for RMSD calculation (need at least 3 CA atoms)")

    ref_atoms = ref_atoms[:n_atoms]
    mob_atoms = mob_atoms[:n_atoms]

    ref_coords_all = np.asarray([atom.get_coord() for atom in ref_atoms], dtype=float)
    mob_coords_all = np.asarray([atom.get_coord() for atom in mob_atoms], dtype=float)

    mask = np.ones(n_atoms, dtype=bool)
    distances: Optional[np.ndarray] = None
    sup = Superimposer()
    used_cycles = 0

    for cycle in range(max_cycles):
        used_cycles = cycle + 1
        ref_inliers = [atom for atom, keep in zip(ref_atoms, mask) if keep]
        mob_inliers = [atom for atom, keep in zip(mob_atoms, mask) if keep]
        if len(ref_inliers) < 3 or len(mob_inliers) < 3:
            break
        sup.set_atoms(ref_inliers, mob_inliers)
        rotation, translation = sup.rotran
        mob_aligned = (rotation @ mob_coords_all.T).T + translation
        distances = np.linalg.norm(ref_coords_all - mob_aligned, axis=1)
        new_mask = distances < cutoff
        if np.array_equal(new_mask, mask) or not np.any(new_mask):
            mask = new_mask if np.any(new_mask) else mask
            break
        mask = new_mask

    if distances is None:
        raise RuntimeError("Iterative RMSD failed to compute distances")

    inlier_distances = distances[mask]
    if not np.any(mask):
        raise ValueError("All atoms excluded during iterative RMSD calculation")

    final_rmsd = float(np.sqrt(np.mean(inlier_distances ** 2)))
    aligned_atoms = int(np.sum(mask))
    logger.debug(
        f"Iterative RMSD ({os.path.basename(candidate_file)}): {final_rmsd:.4f} Å "
        f"with {aligned_atoms} atoms after {used_cycles} cycles"
    )
    return final_rmsd, aligned_atoms, used_cycles


def _find_pymol_executable() -> Optional[str]:
    """Locate a PyMOL executable if available."""
    for cmd in ('pymol', 'pymol2'):
        path = shutil.which(cmd)
        if path:
            return path
    candidate_paths = [
        r'C:\Program Files\PyMOL\PyMOL.exe',
        r'C:\Program Files (x86)\PyMOL\PyMOL.exe',
        '/usr/bin/pymol',
        '/usr/local/bin/pymol'
    ]
    for path in candidate_paths:
        if os.path.exists(path):
            return path
    return None


def calculate_rmsd_pymol(reference_file: str, candidate_file: str) -> float:
    """Calculate RMSD using PyMOL align (Python API or CLI)."""
    logger = logging.getLogger(__name__)

    # Try PyMOL Python API first
    try:
        import __main__
        __main__.pymol_argv = ['pymol', '-Q', '-c']
        import pymol
        from pymol import cmd

        pymol.finish_launching()
        ref_obj = 'ref_structure'
        mob_obj = 'mob_structure'
        cmd.load(reference_file, ref_obj)
        cmd.load(candidate_file, mob_obj)
        align_result = cmd.align(f"{mob_obj} and name CA", f"{ref_obj} and name CA", cycles=5, transform=1)
        rmsd_value = float(align_result[0]) if isinstance(align_result, (list, tuple)) and align_result else float(cmd.pair_fit(f"{mob_obj} and name CA", f"{ref_obj} and name CA")[0])
        cmd.delete(ref_obj)
        cmd.delete(mob_obj)
        cmd.delete('aln')
        logger.debug(f"PyMOL API RMSD ({os.path.basename(candidate_file)}): {rmsd_value:.4f}")
        return rmsd_value
    except Exception as exc:
        logger.debug(f"PyMOL Python API unavailable ({exc}); attempting CLI fallback.")

    pymol_exec = _find_pymol_executable()
    if not pymol_exec:
        raise RuntimeError("PyMOL executable not found")

    script_content = f"""
load {reference_file}, ref_structure
load {candidate_file}, mob_structure
align_result = cmd.align("mob_structure and name CA", "ref_structure and name CA", cycles=5, transform=1)
print("PYMOL_RMSD_VALUE={{}}".format(align_result[0]))
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.pml', delete=False) as script_file:
        script_file.write(script_content)
        script_path = script_file.name

    try:
        cmd_args = [pymol_exec, '-Q', '-c', '-r', script_path]
        result = subprocess.run(cmd_args, capture_output=True, text=True, timeout=120)
        output = result.stdout + "\n" + result.stderr
        match = re.search(r'PYMOL_RMSD_VALUE=([0-9.]+)', output)
        if match:
            rmsd_value = float(match.group(1))
            logger.debug(f"PyMOL CLI RMSD ({os.path.basename(candidate_file)}): {rmsd_value:.4f}")
            return rmsd_value
        raise RuntimeError("PyMOL CLI did not produce RMSD output")
    finally:
        try:
            os.unlink(script_path)
        except OSError:
            pass


def calculate_rmsd(reference_pdb: str,
                   candidate_pdb: str,
                   *,
                   method: str = 'auto') -> float:
    """
    Calculate RMSD between reference and candidate structures.
    
    Args:
        reference_pdb: Path to reference structure (PDB or CIF)
        candidate_pdb: Path to candidate structure (PDB or CIF)
        method: Calculation method ('auto', 'pymol', 'iterative', 'biopython', 'kabsch')
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Calculating RMSD ({method}) between {reference_pdb} and {candidate_pdb}")

    def _try_method(func, description: str):
        try:
            return func()
        except Exception as exc:
            logger.debug(f"{description} failed: {exc}")
            return None

    try:
        if method == 'pymol':
            return calculate_rmsd_pymol(reference_pdb, candidate_pdb)
        if method == 'iterative':
            rmsd_value, _, _ = calculate_rmsd_iterative(reference_pdb, candidate_pdb)
            return rmsd_value
        if method == 'biopython':
            return calculate_rmsd_biopython(reference_pdb, candidate_pdb)
        if method == 'kabsch':
            return calculate_rmsd_kabsch(reference_pdb, candidate_pdb)

        # Auto mode: PyMOL -> Iterative -> Biopython -> Kabsch
        rmsd_value = _try_method(lambda: calculate_rmsd_pymol(reference_pdb, candidate_pdb), "PyMOL RMSD")
        if rmsd_value is not None:
            logger.info(f"RMSD calculated via PyMOL: {rmsd_value:.4f} Å")
            return rmsd_value

        iterative_result = _try_method(
            lambda: calculate_rmsd_iterative(reference_pdb, candidate_pdb),
            "Iterative RMSD"
        )
        if iterative_result is not None:
            rmsd_value = iterative_result[0]
            logger.info(f"RMSD calculated via iterative alignment: {rmsd_value:.4f} Å")
            return rmsd_value

        rmsd_value = _try_method(lambda: calculate_rmsd_biopython(reference_pdb, candidate_pdb), "Biopython RMSD")
        if rmsd_value is not None:
            logger.info(f"RMSD calculated via Biopython: {rmsd_value:.4f} Å")
            return rmsd_value

        rmsd_value = calculate_rmsd_kabsch(reference_pdb, candidate_pdb)
        logger.info(f"RMSD calculated via Kabsch fallback: {rmsd_value:.4f} Å")
        return rmsd_value
    except Exception as exc:
        logger.error(f"RMSD calculation failed for {candidate_pdb}: {exc}")
        return 999.0


if __name__ == "__main__":
    # Test the implementation
    logging.basicConfig(level=logging.INFO)
    
    # Create test data
    test_sequences = [
        "MKLLVLGCTAGCTTTCCGGA",
        "MKLLVLGCTAGCTTTCCGGA"
    ]
    
    try:
        # Test prediction
        results = predict_structure(test_sequences, ".", max_candidates=2)
        print(f"Test results: {len(results)} structures predicted")
        
    except Exception as e:
        print(f"Test failed: {e}")
