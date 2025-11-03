#!/usr/bin/env python3
"""
Epitope Predictor

Basic epitope prediction utilities for VLPIM pipeline.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional


def identify_epitopes(sequence: str, length: int = 15) -> List[str]:
    """
    Basic epitope identification by sliding window.
    
    Args:
        sequence: Input protein sequence
        length: Peptide length (default: 15)
    
    Returns:
        List of potential epitopes
    """
    epitopes = []
    for i in range(len(sequence) - length + 1):
        epitope = sequence[i:i + length]
        epitopes.append(epitope)
    
    return epitopes


def load_user_epitopes(file_path: str) -> pd.DataFrame:
    """
    Load user-provided epitopes from file.
    
    Args:
        file_path: Path to epitopes file
    
    Returns:
        DataFrame with epitope information
    """
    try:
        if file_path.endswith('.csv'):
            return pd.read_csv(file_path)
        elif file_path.endswith(('.xls', '.xlsx')):
            return pd.read_excel(file_path)
        else:
            # Assume tab-separated
            return pd.read_csv(file_path, sep='\t')
    except Exception as e:
        raise ValueError(f"Failed to load epitopes from {file_path}: {e}")


if __name__ == "__main__":
    # Example usage
    test_sequence = "MKFLVNVALVFMVVYISYIY"
    epitopes = identify_epitopes(test_sequence)
    print(f"Found {len(epitopes)} potential epitopes")
    for i, ep in enumerate(epitopes):
        print(f"{i+1}: {ep}")
