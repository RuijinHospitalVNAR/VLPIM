#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Immunogenicity Optimization Pipeline

A comprehensive computational workflow for modulating protein immunogenicity through:
1. Epitope identification using NetMHCIIpan or user-provided epitopes
2. Sequence generation with ProteinMPNN from selected epitope regions
3. MHC-II affinity evaluation across HLA-DRB1 alleles using NetMHCIIpan
4. Scoring based on immunogenicity adjustment direction
5. Structure simulation with AlphaFold3 and ranking based on RMSD, interface analysis (dG/dSASA, packstat, BUNS)

Author: [Chufan Wang]
Version: 1.0
Date: 2025
"""

import os
import sys
import argparse
import logging
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from enum import Enum

import pandas as pd
import numpy as np

# Import custom tools (assuming they exist in tools/ directory)
try:
    from .tools.protein_mpnn_wrapper import generate_mutants
    from .tools.netmhcii_runner import evaluate_mhc_affinity
    from .tools.alphafold3_wrapper import predict_structure, calculate_rmsd
    from .tools.rosetta_wrapper import analyze_interface
except ImportError as e:
    logging.error(f"Failed to import required tools: {e}")
    logging.error("Please ensure all required tools are available in the tools/ directory")
    sys.exit(1)


class ImmunogenicityMode(Enum):
    """Enumeration for immunogenicity modulation modes."""
    REDUCE = "reduce"
    ENHANCE = "enhance"


@dataclass
class PipelineConfig:
    """Configuration class for the immunogenicity optimization pipeline."""
    # Input parameters
    fasta_path: str
    pdb_path: str
    mode: ImmunogenicityMode
    
    # Optional user-provided epitopes
    epitopes_path: Optional[str] = None
    
    # Output parameters
    output_dir: str = "results"
    log_level: str = "INFO"
    
    # ProteinMPNN parameters
    samples_per_temp: int = 20
    temperatures: List[float] = None
    
    # MHC-II parameters
    hla_alleles: List[str] = None
    
    # Structure prediction parameters
    max_candidates: int = 10
    rmsd_threshold: float = 2.0
    
    # Interface analysis parameters
    interface_analysis: bool = True
    dg_dsasa_threshold: float = -0.5
    buns_threshold: int = 5
    packstat_threshold: float = 0.6
    
    # Scoring parameters
    neutral_score: float = 50.0
    
    # Epitope selection parameters
    epitopes_number: int = 10
    epitope_length: int = 15  # Target epitope length (9-15 aa), extend from core if needed
    
    def __post_init__(self):
        """Initialize default values after object creation."""
        if self.temperatures is None:
            self.temperatures = [0.1, 0.3, 0.5]
        if self.hla_alleles is None:
            self.hla_alleles = [
                "HLA-DQA10102-DQB10501", "HLA-DQA10102-DQB10602", "HLA-DQA10102-DQB10604",
                "HLA-DQA10103-DQB10501", "HLA-DQA10103-DQB10603", "HLA-DQA10201-DQB10201",
                "HLA-DQA10201-DQB10202", "HLA-DQA10401-DQB10301", "HLA-DQA10501-DQB10201",
                "HLA-DQA10501-DQB10301", "HLA-DQA10505-DQB10301",
                "DRB1_0101", "DRB1_0102", "DRB1_0103", "DRB1_0301", "DRB1_0302",
                "DRB1_0401", "DRB1_0402", "DRB1_0403", "DRB1_0404", "DRB1_0405",
                "DRB1_0407", "DRB1_0408", "DRB1_0701", "DRB1_0801", "DRB1_0802",
                "DRB1_0803", "DRB1_0804", "DRB1_0901", "DRB1_1001", "DRB1_1101",
                "DRB1_1102", "DRB1_1104", "DRB1_1201", "DRB1_1202", "DRB1_1301",
                "DRB1_1302", "DRB1_1303", "DRB1_1401", "DRB1_1402", "DRB1_1454",
                "DRB1_1501", "DRB1_1502", "DRB1_1503", "DRB1_1601",
                "DRB3_0101", "DRB3_0202", "DRB3_0301",
                "DRB4_0101", "DRB4_0103",
                "DRB5_0101", "DRB5_0202",
                "HLA-DPA10103-DPB10101", "HLA-DPA10103-DPB10201", "HLA-DPA10103-DPB10301",
                "HLA-DPA10103-DPB10401", "HLA-DPA10103-DPB10402", "HLA-DPA10103-DPB10501",
                "HLA-DPA10103-DPB10601", "HLA-DPA10103-DPB11001", "HLA-DPA10103-DPB11101",
                "HLA-DPA10103-DPB11401", "HLA-DPA10103-DPB11501", "HLA-DPA10103-DPB11601",
                "HLA-DPA10103-DPB11701", "HLA-DPA10103-DPB12001", "HLA-DPA10103-DPB12301",
                "HLA-DPA10201-DPB10101", "HLA-DPA10201-DPB10301", "HLA-DPA10201-DPB10401",
                "HLA-DPA10201-DPB10901", "HLA-DPA10201-DPB11001", "HLA-DPA10201-DPB11101",
                "HLA-DPA10201-DPB11301", "HLA-DPA10201-DPB11401", "HLA-DPA10201-DPB11701",
                "HLA-DPA10202-DPB10202", "HLA-DPA10202-DPB10501", "HLA-DPA10202-DPB11901"
            ]


class ImmunogenicityOptimizer:
    """Main class for immunogenicity optimization pipeline."""
    
    def __init__(self, config: PipelineConfig):
        """Initialize the optimizer with configuration."""
        self.config = config
        self.logger = self._setup_logging()
        self.start_time = time.time()
        
    def _setup_logging(self) -> logging.Logger:
        """Set up logging configuration."""
        # Create output directory if it doesn't exist
        os.makedirs(self.config.output_dir, exist_ok=True)
        
        # Configure logging
        log_file = os.path.join(self.config.output_dir, "pipeline.log")
        logging.basicConfig(
            level=getattr(logging, self.config.log_level.upper()),
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        return logging.getLogger(__name__)
    
    def _validate_inputs(self) -> None:
        """Validate input files and parameters."""
        self.logger.info("Validating input parameters...")
        
        # Check FASTA file
        if not os.path.exists(self.config.fasta_path):
            raise FileNotFoundError(f"FASTA file not found: {self.config.fasta_path}")
        
        # Check PDB file
        if not os.path.exists(self.config.pdb_path):
            raise FileNotFoundError(f"PDB file not found: {self.config.pdb_path}")
        
        # Validate file extensions
        if not self.config.fasta_path.lower().endswith(('.fasta', '.fa')):
            raise ValueError(f"Invalid FASTA file extension: {self.config.fasta_path}")
        
        if not self.config.pdb_path.lower().endswith('.pdb'):
            raise ValueError(f"Invalid PDB file extension: {self.config.pdb_path}")
        
        # Validate mode
        if not isinstance(self.config.mode, ImmunogenicityMode):
            if isinstance(self.config.mode, str):
                self.config.mode = ImmunogenicityMode(self.config.mode.lower())
            else:
                raise ValueError(f"Invalid mode: {self.config.mode}")
        
        self.logger.info("Input validation completed successfully")
    
    def _save_config(self) -> None:
        """Save configuration to file for reproducibility."""
        config_file = os.path.join(self.config.output_dir, "config.json")
        config_dict = asdict(self.config)
        # Convert enum to string for JSON serialization
        config_dict['mode'] = self.config.mode.value
        
        with open(config_file, 'w') as f:
            json.dump(config_dict, f, indent=2)
        
        self.logger.info(f"Configuration saved to {config_file}")
    
    def compute_immunogenicity_scores(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Compute immunogenicity scores based on MHC-II binding IC50 values.
        
        Args:
            df: DataFrame containing MHC-II binding IC50 columns (IC50_*)
            
        Returns:
            DataFrame with added score columns
        """
        self.logger.info("Computing immunogenicity scores...")
        
        if df.empty:
            self.logger.warning("Empty DataFrame provided for scoring")
            return df
        
        score_columns = []
        mode = self.config.mode.value
        
        ic50_columns = [col for col in df.columns if col.startswith('IC50_')]
        if not ic50_columns:
            self.logger.warning("No IC50 columns found for scoring")
            return df
        
        for col in ic50_columns:
            allele = col.replace('IC50_', '')
            ic50_values = pd.to_numeric(df[col], errors='coerce')
            ranks = ic50_values.rank(method='average')
            min_rank = ranks.min()
            max_rank = ranks.max()
            denom = (max_rank - min_rank) if (max_rank - min_rank) != 0 else None
            
            if denom is None or pd.isna(denom):
                df[f'Score_{allele}'] = self.config.neutral_score
                self.logger.warning(f"Identical ranks for {allele}, using neutral score")
            else:
                # Rank-based normalization: map ranks to 0-100 (rank small -> lower value)
                normalized = ((ranks - min_rank) / denom) * 100.0
                
                if mode == 'reduce':
                    # Reduce mode: strong binding (lower rank) should yield higher contribution after inversion
                    df[f'Score_{allele}'] = 100.0 - normalized
                else:
                    # Enhance mode: keep as-is so stronger binding produces smaller scores for minimization later
                    df[f'Score_{allele}'] = normalized
            
            score_columns.append(f'Score_{allele}')
        
        # Add overall immunogenicity score (sum across alleles)
        if score_columns:
            df['Overall_Immunogenicity_Score'] = df[score_columns].sum(axis=1)
            self.logger.info(f"Computed scores for {len(score_columns)} alleles")
        else:
            self.logger.warning("No IC50 columns found for scoring")
        
        return df
    
    def predict_epitopes(self) -> pd.DataFrame:
        """Predict CD4+ T-cell epitopes or load user-provided epitopes."""
        self.logger.info("Step 1: Processing epitopes...")
        
        try:
            # 如果用户提供了抗原位点文件，直接加载
            if self.config.epitopes_path and os.path.exists(self.config.epitopes_path):
                self.logger.info(f"Loading user-provided epitopes from {self.config.epitopes_path}")
                epitope_df = self._load_user_epitopes(self.config.epitopes_path)
                self.logger.info(f"Loaded {len(epitope_df)} user-provided epitopes")
            else:
                # 否则使用NetMHCIIpan预测抗原位点
                self.logger.info("No user epitopes provided, using NetMHCIIpan for prediction")
                epitope_df = self._predict_epitopes_with_netmhcii()
                self.logger.info(f"Predicted {len(epitope_df)} epitopes using NetMHCIIpan")
            
            if epitope_df.empty:
                raise ValueError("No epitopes available")
            
            # Filter and select epitopes based on binding strength
            if not (self.config.epitopes_path and os.path.exists(self.config.epitopes_path)):
                # Only filter if we predicted with NetMHCIIpan
                epitope_df = self._filter_epitopes_by_binding(epitope_df)
                self.logger.info(f"After filtering: {len(epitope_df)} epitopes selected")
            
            # Extend core sequences to target length
            epitope_df = self._extend_core_sequences(epitope_df)
            
            # Save results
            epitope_file = os.path.join(self.config.output_dir, "epitope_predictions.csv")
            epitope_df.to_csv(epitope_file, index=False)
            
            self.logger.info(f"Epitope predictions saved to {epitope_file}")
            
            return epitope_df
            
        except Exception as e:
            self.logger.error(f"Epitope processing failed: {e}")
            raise
    
    def _load_user_epitopes(self, epitopes_path: str) -> pd.DataFrame:
        """Load user-provided epitopes from file."""
        try:
            # 支持CSV格式的抗原位点文件
            if epitopes_path.endswith('.csv'):
                epitope_df = pd.read_csv(epitopes_path)
                # 验证必要的列
                required_columns = ['sequence', 'start', 'end']
                missing_columns = [col for col in required_columns if col not in epitope_df.columns]
                if missing_columns:
                    raise ValueError(f"Missing required columns: {missing_columns}")
                return epitope_df
            else:
                raise ValueError("Only CSV format is supported for epitopes file")
        except Exception as e:
            self.logger.error(f"Failed to load user epitopes: {e}")
            raise
    
    def _get_sequence_length(self) -> int:
        """Get sequence length from FASTA file."""
        try:
            seq_length = 0
            with open(self.config.fasta_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('>'):
                        seq_length += len(line)
            return seq_length
        except Exception as e:
            self.logger.warning(f"Failed to read sequence length: {e}")
            raise
    
    def _predict_epitopes_with_netmhcii(self) -> pd.DataFrame:
        """Predict epitopes using NetMHCIIpan."""
        try:
            from .tools.netmhcii_runner import predict_epitopes_with_netmhcii
            
            # Use configured HLA alleles (default set in PipelineConfig.__post_init__)
            # Use NetMHCIIpan to predict epitopes
            epitope_df = predict_epitopes_with_netmhcii(
                self.config.fasta_path, 
                self.config.hla_alleles, 
                self.config.output_dir
            )
            
            self.logger.info(f"NetMHCIIpan epitope prediction completed: {len(epitope_df)} epitopes")
            return epitope_df

        except Exception as e:
            self.logger.error(f"NetMHCIIpan prediction failed: {e}")
            raise
    
    def _filter_epitopes_by_binding(self, epitope_df: pd.DataFrame) -> pd.DataFrame:
        """
        Filter epitopes based on strong/weak binding counts per Core sequence.
        
        Criteria:
        - Strong binding: %Rank_EL <= 1.00%
        - Weak binding: 1.00% < %Rank_EL <= 5.00%
        - Number of strong binding = strong + weak binding counts per Core
        
        For reduce mode: select top N cores with highest number of strong binding
        For enhance mode: select bottom N cores with lowest number of strong binding
        
        Args:
            epitope_df: DataFrame with epitope predictions
            
        Returns:
            Filtered DataFrame with selected epitopes
        """
        self.logger.info("Filtering epitopes based on binding strength...")
        
        if epitope_df.empty:
            return epitope_df
        
        # Determine which rank column to use
        rank_col = None
        if 'rank_el' in epitope_df.columns:
            rank_col = 'rank_el'
            self.logger.info("Using %Rank_EL for binding classification")
        elif 'rank' in epitope_df.columns:
            rank_col = 'rank'
            self.logger.warning("%Rank_EL not available, using BA_Rank instead")
        else:
            self.logger.warning("No rank information available, skipping filtering")
            return epitope_df
        
        # Ensure core column exists
        if 'core' not in epitope_df.columns:
            if 'sequence' in epitope_df.columns:
                epitope_df['core'] = epitope_df['sequence']
                self.logger.info("Core column not found, using sequence as core")
            else:
                self.logger.warning("Neither core nor sequence column found, skipping filtering")
                return epitope_df
        
        # Classify binding strength
        # Strong binding: %Rank <= 1.00%
        # Weak binding: 1.00% < %Rank <= 5.00%
        def classify_binding(rank_value):
            if pd.isna(rank_value):
                return None
            if rank_value <= 1.00:
                return 'strong'
            elif rank_value <= 5.00:
                return 'weak'
            else:
                return None
        
        epitope_df['binding_class'] = epitope_df[rank_col].apply(classify_binding)
        
        # Count strong and weak bindings per core
        core_binding_counts = []
        for core in epitope_df['core'].unique():
            core_data = epitope_df[epitope_df['core'] == core]
            strong_count = len(core_data[core_data['binding_class'] == 'strong'])
            weak_count = len(core_data[core_data['binding_class'] == 'weak'])
            number_of_strong_binding = strong_count + weak_count
            
            core_binding_counts.append({
                'core': core,
                'strong_count': strong_count,
                'weak_count': weak_count,
                'number_of_strong_binding': number_of_strong_binding
            })
        
        core_counts_df = pd.DataFrame(core_binding_counts)
        
        # Sort by number_of_strong_binding
        core_counts_df = core_counts_df.sort_values(
            'number_of_strong_binding',
            ascending=False
        ).reset_index(drop=True)
        
        self.logger.info(f"Core sequences ranked: {len(core_counts_df)} unique cores")
        self.logger.info(f"Top 5 cores by binding count: {core_counts_df.head(5)['core'].tolist()}")
        
        # Determine effective number of epitopes to select based on sequence length
        # To prevent overlapping mutation regions, limit epitopes for short sequences
        try:
            # Read sequence length from FASTA
            seq_length = self._get_sequence_length()
            if seq_length < 200:
                # For sequences shorter than 200 amino acids, limit to maximum 3 epitopes
                n_effective = min(self.config.epitopes_number, 3)
                self.logger.info(f"Sequence length ({seq_length} aa) < 200, limiting epitopes to {n_effective}")
            else:
                n_effective = self.config.epitopes_number
        except Exception as e:
            self.logger.warning(f"Could not determine sequence length: {e}, using user-defined value")
            n_effective = self.config.epitopes_number
        
        # Select top or bottom N cores based on mode
        if self.config.mode == ImmunogenicityMode.REDUCE:
            # Reduce mode: select cores with highest binding (top N)
            selected_cores = core_counts_df.head(n_effective)['core'].tolist()
            self.logger.info(f"Reduce mode: selecting top {n_effective} cores with highest binding")
        else:  # ENHANCE
            # Enhance mode: select cores with lowest binding (bottom N)
            selected_cores = core_counts_df.tail(n_effective)['core'].tolist()
            self.logger.info(f"Enhance mode: selecting bottom {n_effective} cores with lowest binding")
        
        # Filter epitope_df to only include selected cores
        filtered_df = epitope_df[epitope_df['core'].isin(selected_cores)].copy()
        
        # Add binding count information to filtered epitopes
        if not filtered_df.empty:
            core_counts_dict = dict(zip(
                core_counts_df['core'],
                core_counts_df['number_of_strong_binding']
            ))
            filtered_df['number_of_strong_binding'] = filtered_df['core'].map(core_counts_dict)
        
        self.logger.info(f"Selected {len(selected_cores)} cores, resulting in {len(filtered_df)} epitopes")
        
        return filtered_df
    
    def _extend_core_sequences(self, epitope_df: pd.DataFrame) -> pd.DataFrame:
        """
        Extend Core sequences to target epitope_length using amino acids from the original VLP sequence.
        
        Extension strategy:
        - Target length: epitope_length (default 15, range 9-15 aa)
        - Maximum forward extension (toward N-terminal): 2 amino acids
        - Maximum backward extension (toward C-terminal): 4 amino acids
        - Priority: extend forward first (up to 2 aa), then backward (up to 4 aa)
        - All extended amino acids come from the original input VLP sequence
        - Example: 9-mer core -> forward 2 aa + backward 4 aa -> 15-mer
        
        Args:
            epitope_df: DataFrame with core sequences and positions
            
        Returns:
            DataFrame with extended sequences and updated positions
        """
        self.logger.info(f"Extending core sequences to target length {self.config.epitope_length}...")
        
        if epitope_df.empty:
            return epitope_df
        
        # Get full protein sequence from original VLP FASTA file
        try:
            full_sequence = self._get_full_sequence()
            seq_length = len(full_sequence)
        except Exception as e:
            self.logger.warning(f"Could not read full sequence: {e}, skipping extension")
            return epitope_df
        
        # Validate target length
        if self.config.epitope_length < 9 or self.config.epitope_length > 15:
            self.logger.warning(f"Invalid epitope_length {self.config.epitope_length}, must be 9-15. Using 15.")
            target_length = 15
        else:
            target_length = self.config.epitope_length
        
        extended_sequences = []
        extended_starts = []
        extended_ends = []
        
        for _, row in epitope_df.iterrows():
            core_seq = row.get('core', row.get('sequence', ''))
            core_start = int(row.get('start', 1))
            core_end = int(row.get('end', core_start + len(core_seq) - 1))
            
            core_len = len(core_seq)
            
            # If core is already at or above target length, keep as is
            if core_len >= target_length:
                extended_sequences.append(core_seq)
                extended_starts.append(core_start)
                extended_ends.append(core_end)
                continue
            
            # Calculate extension needed
            extension_needed = target_length - core_len
            max_forward = min(2, extension_needed)
            max_backward = min(4, extension_needed - max_forward)
            
            # Calculate new start and end positions (1-based)
            new_start = max(1, core_start - max_forward)
            new_end = min(seq_length, core_end + max_backward)
            
            # Extract extended sequence from full sequence
            extended_seq = full_sequence[new_start - 1:new_end]
            
            extended_sequences.append(extended_seq)
            extended_starts.append(new_start)
            extended_ends.append(new_end)
            
            self.logger.debug(
                f"Extended core {core_seq} ({core_len}aa) at [{core_start}-{core_end}] "
                f"to {extended_seq} ({len(extended_seq)}aa) at [{new_start}-{new_end}]"
            )
        
        # Update DataFrame with extended sequences
        result_df = epitope_df.copy()
        result_df['sequence'] = extended_sequences
        result_df['start'] = extended_starts
        result_df['end'] = extended_ends
        
        self.logger.info(f"Extended {len(result_df)} epitope sequences")
        
        return result_df
    
    def _write_mutated_epitope_fasta(
        self,
        mutants: List[str],
        epitope_df: pd.DataFrame
    ) -> Tuple[str, Dict[str, str]]:
        """
        Build a FASTA file containing mutated epitope peptides extracted
        from each mutant sequence. Returns the FASTA path and a mapping
        from per-epitope identifiers to their parent mutant IDs.
        """
        if not mutants or epitope_df.empty:
            raise ValueError("Mutants or epitope definitions missing for epitope FASTA export")
        
        fasta_path = os.path.join(self.config.output_dir, "mutant_epitopes.fasta")
        seq_id_to_mutant: Dict[str, str] = {}
        
        with open(fasta_path, 'w') as fasta_file:
            for mutant_idx, sequence in enumerate(mutants):
                mutant_id = f"mutant_{mutant_idx:04d}"
                
                for ep_idx, row in epitope_df.iterrows():
                    start = int(row.get('start', 1)) - 1
                    end = int(row.get('end', start))
                    
                    if start < 0 or end > len(sequence):
                        self.logger.warning(
                            f"Epitope [{row.get('start')}-{row.get('end')}] exceeds bounds for {mutant_id}, skipping"
                        )
                        continue
                    
                    peptide = sequence[start:end]
                    seq_id = f"{mutant_id}|epitope_{ep_idx:04d}"
                    fasta_file.write(f">{seq_id}\n{peptide}\n")
                    seq_id_to_mutant[seq_id] = mutant_id
        
        self.logger.info(f"Mutated epitope FASTA saved to {fasta_path}")
        return fasta_path, seq_id_to_mutant
    
    def _get_full_sequence(self) -> str:
        """Get full protein sequence from FASTA file."""
        sequence = ""
        with open(self.config.fasta_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('>'):
                    sequence += line
        if not sequence:
            raise ValueError("Empty sequence read from FASTA file")
        return sequence
    
    def _aggregate_epitope_scores_by_mutant(
        self,
        epitope_scores: pd.DataFrame,
        seq_id_map: Dict[str, str],
        mutant_sequence_map: Dict[str, str]
    ) -> pd.DataFrame:
        """
        Aggregate per-epitope scores (Sequence_ID level) into per-mutant totals.
        """
        if epitope_scores.empty or 'Sequence_ID' not in epitope_scores.columns:
            return epitope_scores
        
        df = epitope_scores.copy()
        df['Mutant_ID'] = df['Sequence_ID'].map(seq_id_map).fillna('unknown')
        df['Epitope_Count'] = 1
        
        agg_dict: Dict[str, str] = {
            'Overall_Immunogenicity_Score': 'sum',
            'Epitope_Count': 'sum'
        }
        for col in df.columns:
            if col.startswith('Score_'):
                agg_dict[col] = 'mean'
            if col.startswith('IC50_'):
                agg_dict[col] = 'mean'
        
        grouped = df.groupby('Mutant_ID').agg(agg_dict).reset_index()
        grouped = grouped.rename(columns={'Mutant_ID': 'Sequence_ID'})
        grouped['sequence'] = grouped['Sequence_ID'].map(mutant_sequence_map).fillna('')
        
        return grouped
    
    def generate_mutant_sequences(self, epitope_df: pd.DataFrame) -> List[str]:
        """Generate mutant sequences using ProteinMPNN."""
        self.logger.info("Step 2: Generating mutant sequences with ProteinMPNN...")
        
        try:
            mutants = generate_mutants(
                self.config.pdb_path,
                epitope_df,
                self.config.mode.value,
                samples_per_temp=self.config.samples_per_temp,
                temps=self.config.temperatures
            )
            
            if not mutants:
                raise ValueError("No mutant sequences generated")
            
            # Save mutant sequences
            mutant_file = os.path.join(self.config.output_dir, "mutant_sequences.fasta")
            with open(mutant_file, 'w') as f:
                for i, seq in enumerate(mutants):
                    f.write(f">mutant_{i:04d}\n{seq}\n")
            
            self.logger.info(f"Generated {len(mutants)} mutant sequences")
            self.logger.info(f"Mutant sequences saved to {mutant_file}")
            
            return mutants
            
        except Exception as e:
            self.logger.error(f"Mutant generation failed: {e}")
            raise
    
    def evaluate_mhc_binding(
        self,
        mutant_file: str,
        seq_id_map: Dict[str, str],
        mutant_sequence_map: Dict[str, str]
    ) -> pd.DataFrame:
        """Evaluate MHC-II binding affinity."""
        self.logger.info("Step 3: Evaluating MHC-II binding affinity...")
        
        try:
            affinity_df = evaluate_mhc_affinity(mutant_file, group_by='seq_id')
            
            if affinity_df.empty:
                raise ValueError("No MHC-II binding results obtained")
            
            # Compute immunogenicity scores
            affinity_df = self.compute_immunogenicity_scores(affinity_df)
            
            # Save per-epitope results
            epitope_scores_file = os.path.join(self.config.output_dir, "mhc_binding_epitope_scores.csv")
            affinity_df.to_csv(epitope_scores_file, index=False)
            
            # Aggregate to per-mutant scores
            aggregated_df = self._aggregate_epitope_scores_by_mutant(
                affinity_df,
                seq_id_map,
                mutant_sequence_map
            )
            
            affinity_file = os.path.join(self.config.output_dir, "mhc_binding_scores.csv")
            aggregated_df.to_csv(affinity_file, index=False)
            
            self.logger.info(f"Evaluated {len(affinity_df)} epitope sequences for MHC-II binding")
            self.logger.info(f"Aggregated scores for {len(aggregated_df)} mutant sequences")
            self.logger.info(f"MHC binding scores saved to {affinity_file}")
            
            return aggregated_df
            
        except Exception as e:
            self.logger.error(f"MHC-II evaluation failed: {e}")
            raise
    
    def predict_structures_and_rank(self, affinity_df: pd.DataFrame) -> pd.DataFrame:
        """Predict structures and rank final candidates."""
        self.logger.info("Step 4: Predicting structures and filtering final candidates...")
        
        try:
            # Select top candidates based on overall immunogenicity score
            if self.config.mode == ImmunogenicityMode.ENHANCE:
                top_candidates = affinity_df.nlargest(
                    self.config.max_candidates, 
                    'Overall_Immunogenicity_Score'
                )
            else:
                top_candidates = affinity_df.nsmallest(
                    self.config.max_candidates, 
                    'Overall_Immunogenicity_Score'
                )
            
            if len(top_candidates) == 0:
                raise ValueError("No candidates selected for structure prediction")
            
            self.logger.info(f"Selected {len(top_candidates)} top candidates for structure prediction")
            
            structure_results = top_candidates.reset_index(drop=True).copy()
            
            # Attempt structure prediction if sequences are available
            if 'sequence' in top_candidates.columns:
                try:
                    predicted_structures = predict_structure(
                        top_candidates['sequence'].tolist(),
                        self.config.output_dir,
                        max_candidates=self.config.max_candidates
                    )
                    
                    if not predicted_structures.empty and 'pdb_path' in predicted_structures.columns:
                        predicted_structures = predicted_structures.reset_index(drop=True)
                        structure_results = pd.concat([structure_results, predicted_structures], axis=1)
                        
                        def _compute_rmsd(pdb_path: Union[str, float]) -> float:
                            if isinstance(pdb_path, str) and os.path.exists(pdb_path):
                                return calculate_rmsd(self.config.pdb_path, pdb_path, method='auto')
                            self.logger.warning(f"PDB path not found for RMSD calculation: {pdb_path}")
                            return 999.0
                        
                        structure_results['RMSD'] = structure_results['pdb_path'].apply(_compute_rmsd)
                    else:
                        self.logger.warning("AlphaFold3 returned no PDB paths; skipping RMSD calculation")
                except Exception as e:
                    self.logger.warning(f"Structure prediction skipped due to error: {e}")
            else:
                self.logger.warning("Sequence column not found in candidates; skipping AlphaFold3 prediction")
            
            # Perform interface analysis if enabled
            # Note: This is a placeholder - actual implementation needed
            # if self.config.interface_analysis:
            #     self.logger.info("Step 5: Performing interface analysis with Rosetta...")
            #     interface_results = analyze_interface(
            #         structure_results,
            #         dg_dsasa_threshold=self.config.dg_dsasa_threshold,
            #         buns_threshold=self.config.buns_threshold,
            #         packstat_threshold=self.config.packstat_threshold
            #     )
            #     
            #     # Rank candidates based on RMSD, dG/dSASA, packstat, BUNS
            #     final_results = self._rank_candidates(interface_results)
            # else:
            final_results = structure_results
            self.logger.info("Skipping interface analysis (not yet implemented)")
            
            # Save final results
            final_file = os.path.join(self.config.output_dir, "final_ranked_candidates.csv")
            final_results.to_csv(final_file, index=False)
            
            self.logger.info(f"Final candidates: {len(final_results)}")
            self.logger.info(f"Final results saved to {final_file}")
            
            return final_results
            
        except Exception as e:
            self.logger.error(f"Structure prediction failed: {e}")
            raise
    
    def _rank_candidates(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Rank candidates based on RMSD, dG/dSASA, packstat, BUNS.
        
        Args:
            df: DataFrame containing structure and interface analysis results
            
        Returns:
            DataFrame with ranked candidates
        """
        self.logger.info("Ranking candidates based on RMSD, dG/dSASA, packstat, BUNS...")
        
        if df.empty:
            return df
        
        # Create ranking criteria
        # Lower RMSD is better (ascending)
        # Lower dG/dSASA is better (more negative, ascending)
        # Higher packstat is better (descending)
        # Lower BUNS is better (ascending)
        
        # Sort by each criterion in order of priority
        df_sorted = df.sort_values(
            by=['RMSD', 'dG_dSASA', 'packstat', 'BUNS'],
            ascending=[True, True, False, True],
            na_position='last'
        ).reset_index(drop=True)
        
        # Add ranking column
        df_sorted['Rank'] = range(1, len(df_sorted) + 1)
        
        self.logger.info(f"Ranked {len(df_sorted)} candidates")
        
        return df_sorted
    
    def run_pipeline(self) -> Dict[str, Union[pd.DataFrame, List[str]]]:
        """
        Run the complete immunogenicity optimization pipeline.
        
        Returns:
            Dictionary containing all pipeline results
        """
        self.logger.info(f"Starting immunogenicity {self.config.mode.value} pipeline...")
        self.logger.info(f"Input FASTA: {self.config.fasta_path}")
        self.logger.info(f"Input PDB: {self.config.pdb_path}")
        self.logger.info(f"Output directory: {self.config.output_dir}")
        
        try:
            # Validate inputs
            self._validate_inputs()
            
            # Save configuration
            self._save_config()
            
            # Run pipeline steps
            epitope_df = self.predict_epitopes()
            mutants = self.generate_mutant_sequences(epitope_df)
            
            mutant_sequence_map = {f"mutant_{i:04d}": seq for i, seq in enumerate(mutants)}
            epitope_fasta, seq_id_map = self._write_mutated_epitope_fasta(mutants, epitope_df)
            
            affinity_df = self.evaluate_mhc_binding(epitope_fasta, seq_id_map, mutant_sequence_map)
            final_results = self.predict_structures_and_rank(affinity_df)
            
            # Calculate runtime
            runtime = time.time() - self.start_time
            
            # Log completion
            self.logger.info("=" * 60)
            self.logger.info("PIPELINE COMPLETED SUCCESSFULLY!")
            self.logger.info(f"Total runtime: {runtime:.2f} seconds")
            self.logger.info("Results saved in ./results directory:")
            self.logger.info("  - epitope_predictions.csv")
            self.logger.info("  - mutant_sequences.fasta")
            self.logger.info("  - mhc_binding_epitope_scores.csv")
            self.logger.info("  - mhc_binding_scores.csv")
            self.logger.info("  - final_ranked_candidates.csv")
            self.logger.info("  - config.json")
            self.logger.info("  - pipeline.log")
            self.logger.info("=" * 60)
            
            return {
                'epitopes': epitope_df,
                'mutants': mutants,
                'mhc_binding': affinity_df,
                'final_candidates': final_results,
                'runtime': runtime
            }
            
        except Exception as e:
            self.logger.error(f"Pipeline failed: {e}")
            self.logger.error("Check the log file for detailed error information")
            raise


def create_config_from_args(args) -> PipelineConfig:
    """Create configuration from command line arguments."""
    return PipelineConfig(
        fasta_path=args.fasta,
        pdb_path=args.pdb,
        mode=ImmunogenicityMode(args.mode),
        epitopes_path=args.epitopes,
        output_dir=args.output_dir,
        log_level=args.log_level,
        samples_per_temp=args.samples_per_temp,
        temperatures=args.temperatures,
        max_candidates=args.max_candidates,
        rmsd_threshold=args.rmsd_threshold,
        interface_analysis=args.interface_analysis,
        dg_dsasa_threshold=args.dg_dsasa_threshold,
        buns_threshold=args.buns_threshold,
        packstat_threshold=args.packstat_threshold,
        epitopes_number=args.epitopes_number,
        epitope_length=args.epitope_length
    )


def main():
    """Main entry point for the immunogenicity optimization pipeline."""
    parser = argparse.ArgumentParser(
        description="Immunogenicity Optimization Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage - reduce immunogenicity
  python immunogenicity_optimization_pipeline.py --fasta protein.fasta --pdb protein.pdb --mode reduce
  
  # Use user-provided epitopes
  python immunogenicity_optimization_pipeline.py --fasta protein.fasta --pdb protein.pdb --mode reduce --epitopes epitopes.csv
  
  # Enhance immunogenicity with custom parameters
  python immunogenicity_optimization_pipeline.py --fasta protein.fasta --pdb protein.pdb --mode enhance --max-candidates 20 --samples-per-temp 50 --dg-dsasa-threshold -0.3
  
  # Use custom output directory and log level
  python immunogenicity_optimization_pipeline.py --fasta protein.fasta --pdb protein.pdb --mode reduce --output-dir custom_results --log-level DEBUG
        """
    )
    
    # Required arguments
    parser.add_argument('--fasta', type=str, required=True,
                       help='Input FASTA file path')
    parser.add_argument('--pdb', type=str, required=True,
                       help='Input PDB file path')
    parser.add_argument('--mode', type=str, choices=['reduce', 'enhance'],
                       default='reduce',
                       help='Modulate immunogenicity: reduce or enhance (default: reduce)')
    
    # Optional user input arguments
    parser.add_argument('--epitopes', type=str,
                       help='Optional CSV file containing user-provided epitopes (columns: sequence, start, end)')
    
    # Epitope selection parameters
    parser.add_argument('--epitopes-number', type=int, default=10,
                       help='Number of epitopes to select based on binding strength (default: 10)')
    parser.add_argument('--epitope-length', type=int, default=15,
                       help='Target epitope length (9-15 aa), extends from core if needed (default: 15)')
    
    # Optional arguments
    parser.add_argument('--output-dir', type=str, default='results',
                       help='Output directory for results (default: results)')
    parser.add_argument('--log-level', type=str, choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       default='INFO', help='Logging level (default: INFO)')
    
    # ProteinMPNN parameters
    parser.add_argument('--samples-per-temp', type=int, default=20,
                       help='Number of samples per temperature (default: 20)')
    parser.add_argument('--temperatures', type=float, nargs='+', default=[0.1, 0.3, 0.5],
                       help='Temperature values for ProteinMPNN (default: 0.1 0.3 0.5)')
    
    # Structure prediction parameters
    parser.add_argument('--max-candidates', type=int, default=10,
                       help='Maximum number of candidates for structure prediction (default: 10)')
    parser.add_argument('--rmsd-threshold', type=float, default=2.0,
                       help='RMSD threshold for structure filtering (default: 2.0)')
    
    # Interface analysis parameters
    parser.add_argument('--interface-analysis', action='store_true', default=True,
                       help='Enable interface analysis with Rosetta (default: True)')
    parser.add_argument('--dg-dsasa-threshold', type=float, default=-0.5,
                       help='dG/dSASA threshold for interface filtering (default: -0.5)')
    parser.add_argument('--buns-threshold', type=int, default=5,
                       help='BUNS threshold for interface filtering (default: 5)')
    parser.add_argument('--packstat-threshold', type=float, default=0.6,
                       help='Packstat threshold for interface filtering (default: 0.6)')
    
    args = parser.parse_args()
    
    try:
        # Create configuration
        config = create_config_from_args(args)
        
        # Initialize and run pipeline
        optimizer = ImmunogenicityOptimizer(config)
        results = optimizer.run_pipeline()
        
        print("\n" + "=" * 60)
        print("PIPELINE COMPLETED SUCCESSFULLY!")
        print(f"Total runtime: {results['runtime']:.2f} seconds")
        print(f"Results saved in: {config.output_dir}")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\nPipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nPipeline failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
