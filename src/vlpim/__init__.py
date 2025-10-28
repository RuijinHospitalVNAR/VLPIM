"""
VLPIM: A Comprehensive Tool for Immunogenicity Modulation of Virus-like Particles

A comprehensive computational workflow for modulating immunogenicity of virus-like particles through:
1. Epitope identification using NetMHCIIpan or user-provided epitopes
2. Sequence generation with ProteinMPNN from selected epitope regions
3. MHC-II affinity evaluation across HLA-DRB1 alleles using NetMHCIIpan
4. Scoring based on immunogenicity adjustment direction
5. Structure simulation with AlphaFold3 and ranking based on RMSD, interface analysis (dG/dSASA, packstat, BUNS)

Author: Chufan Wang
Version: 1.0
Date: 2025
"""

__version__ = "1.0.0"
__author__ = "Chufan Wang"
__email__ = "wcf1112@sjtu.edu.cn"

from .immunogenicity_optimization_pipeline import ImmunogenicityOptimizer, PipelineConfig, ImmunogenicityMode

__all__ = [
    "ImmunogenicityOptimizer",
    "PipelineConfig", 
    "ImmunogenicityMode",
    "__version__",
    "__author__",
    "__email__"
]
