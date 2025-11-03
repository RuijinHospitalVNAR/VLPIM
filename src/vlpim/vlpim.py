#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VLPIM - Variable Length Protein Immunogenicity Modulator

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
import subprocess
from pathlib import Path
from typing import List, Optional

def setup_logging(level: str = "INFO"):
    """设置日志"""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )

def show_help():
    """显示VLPIM帮助信息"""
    help_text = """
VLPIM - Variable Length Protein Immunogenicity Modulator
========================================================

VLPIM是一个综合计算工作流，用于通过以下步骤调节蛋白质免疫原性：
1. 使用NetMHCIIpan或用户提供的抗原位点进行抗原位点识别
2. 使用ProteinMPNN从选定的抗原位点区域生成序列
3. 使用NetMHCIIpan评估HLA-DRB1等位基因的MHC-II亲和力
4. 基于免疫原性调节方向进行评分
5. 使用AlphaFold3进行结构模拟，基于RMSD、界面分析(dG/dSASA, packstat, BUNS)进行排序

基本用法:
--------
VLPIM run --fasta <FASTA文件> --pdb <PDB文件> [选项]

必需参数:
--------
  --fasta FILE           输入FASTA文件路径
  --pdb FILE             输入PDB文件路径
  --mode {reduce,enhance} 免疫原性调节模式: reduce(降低) 或 enhance(增强)

可选参数:
--------
  --epitopes FILE        用户提供的抗原位点CSV文件 (可选)
  --output-dir DIR       结果输出目录 (默认: results)
  --log-level LEVEL      日志级别: DEBUG, INFO, WARNING, ERROR (默认: INFO)

ProteinMPNN参数:
--------------
  --samples-per-temp N   每个温度的样本数 (默认: 20)
  --temperatures FLOAT   温度值列表，用空格分隔 (默认: 0.1 0.3 0.5)

结构预测参数:
-----------
  --max-candidates N     结构预测的最大候选数 (默认: 10)
  --rmsd-threshold FLOAT RMSD阈值用于结构过滤 (默认: 2.0)

界面分析参数:
-----------
  --interface-analysis    启用Rosetta界面分析 (默认: True)
  --dg-dsasa-threshold FLOAT dG/dSASA阈值用于界面过滤 (默认: -0.5)
  --buns-threshold N      BUNS阈值用于界面过滤 (默认: 5)
  --packstat-threshold FLOAT Packstat阈值用于界面过滤 (默认: 0.6)

其他命令:
--------
  VLPIM config           显示配置信息
  VLPIM validate         验证配置和工具可用性
  VLPIM setup            运行安装脚本
  VLPIM test             运行基本测试

抗原位点文件格式:
--------------
如果使用--epitopes选项，CSV文件应包含以下列：

| 列名      | 描述           | 示例        |
|-----------|----------------|-------------|
| sequence  | 抗原位点序列   | "MKLLVL"    |
| start     | 蛋白质起始位置 | 10          |
| end       | 蛋白质结束位置 | 15          |

示例epitopes.csv:
sequence,start,end
MKLLVL,10,15
GCTAGCT,25,31

使用示例:
--------
# 基本用法 - 降低免疫原性
VLPIM run --fasta protein.fasta --pdb protein.pdb --mode reduce

# 使用用户提供的抗原位点
VLPIM run --fasta protein.fasta --pdb protein.pdb --mode reduce --epitopes epitopes.csv

# 增强免疫原性，自定义参数
VLPIM run --fasta protein.fasta --pdb protein.pdb --mode enhance \\
    --max-candidates 20 --samples-per-temp 50 --dg-dsasa-threshold -0.3

# 自定义输出目录和日志级别
VLPIM run --fasta protein.fasta --pdb protein.pdb --mode reduce \\
    --output-dir custom_results --log-level DEBUG

环境变量配置:
-----------
以下环境变量可用于配置外部工具路径：

# 外部工具路径
export PROTEIN_MPNN_PATH="/path/to/ProteinMPNN"
export NETMHCIIPAN_PATH="/path/to/netMHCIIpan"
export ALPHAFOLD3_PATH="/path/to/alphafold3"
export ROSETTA_PATH="/path/to/rosetta"

# 用户输入路径 (可选)
export USER_EPITOPES_PATH="/path/to/epitopes.csv"

# 默认参数
export DEFAULT_OUTPUT_DIR="results"
export DEFAULT_LOG_LEVEL="INFO"

配置文件:
--------
可以通过config_unified.yaml文件配置所有参数，包括：
- 外部工具路径
- 管道参数
- 系统资源设置
- 高级配置选项

输出文件:
--------
管道生成以下输出文件：
- epitope_predictions.csv: 预测的抗原位点及评分
- mutant_sequences.fasta: 生成的突变序列
- mhc_binding_scores.csv: MHC-II结合亲和力评分
- final_ranked_candidates.csv: 最终排序的候选序列及结构和界面分析
- config.json: 运行使用的配置
- pipeline.log: 详细日志文件

故障排除:
--------
1. 工具未找到: 确保ProteinMPNN、NetMHCIIpan、AlphaFold3和Rosetta已安装并在PATH中
2. 内存问题: 对于大蛋白质，减少--samples-per-temp或--max-candidates参数
3. 超时错误: 增加超时值或减少批处理大小
4. 文件权限: 确保输出目录有写入权限

更多信息:
--------
- 详细安装说明: 参见 INSTALL.md
- 使用指南: 参见 README.md
- 配置指南: 参见 PATH_CONFIGURATION_GUIDE.md
- 问题报告: 请在GitHub上提交issue

版本: 1.0
作者: [Chufan Wang]
日期: 2025
"""
    print(help_text)

def show_config():
    """显示当前配置信息"""
    print("VLPIM 配置信息")
    print("=" * 50)
    
    # 检查配置文件
    config_file = "config/config_unified.yaml"
    if os.path.exists(config_file):
        print(f"[OK] 配置文件: {config_file}")
    else:
        print(f"[ERROR] 配置文件: {config_file} (未找到)")
    
    # 检查环境变量
    env_vars = [
        "PROTEIN_MPNN_PATH",
        "NETMHCIIPAN_PATH", 
        "ALPHAFOLD3_PATH",
        "ROSETTA_PATH",
        "USER_EPITOPES_PATH"
    ]
    
    print("\n环境变量:")
    for var in env_vars:
        value = os.getenv(var, "")
        if value:
            print(f"[OK] {var}: {value}")
        else:
            print(f"[NOT SET] {var}: (未设置)")
    
        # 检查工具可用性
        print("\n工具可用性:")
        tools = ["protein_mpnn.py", "netMHCIIpan", "alphafold3", "interface_analyzer"]
        for tool in tools:
            try:
                result = subprocess.run(["which", tool], capture_output=True, check=True)
                print(f"[OK] {tool}: {result.stdout.decode().strip()}")
            except subprocess.CalledProcessError:
                print(f"[NOT FOUND] {tool}: 未找到")

def validate_config():
    """验证配置"""
    print("运行配置验证...")
    try:
        result = subprocess.run([sys.executable, "scripts/validate_config.py"], 
                              capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("错误:", result.stderr)
    except Exception as e:
        print(f"验证失败: {e}")

def run_setup():
    """运行安装脚本"""
    print("运行安装脚本...")
    try:
        if os.path.exists("scripts/setup.sh"):
            subprocess.run(["bash", "scripts/setup.sh"], check=True)
        else:
            print("安装脚本 scripts/setup.sh 未找到")
    except Exception as e:
        print(f"安装失败: {e}")

def run_tests():
    """运行基本测试"""
    print("运行基本测试...")
    try:
        # 测试Python导入
        result = subprocess.run([sys.executable, "-c", 
                               "import pandas, numpy, requests; print('[OK] Python依赖OK')"], 
                              capture_output=True, text=True)
        print(result.stdout)
        
        # 测试管道导入
        result = subprocess.run([sys.executable, "-c", 
                               "from immunogenicity_optimization_pipeline import ImmunogenicityOptimizer; print('[OK] 管道导入OK')"], 
                              capture_output=True, text=True)
        print(result.stdout)
        
    except Exception as e:
        print(f"测试失败: {e}")

def run_pipeline(args):
    """运行免疫原性优化管道"""
    print("启动免疫原性优化管道...")
    
    # 构建命令
    cmd = [sys.executable, "src/vlpim/immunogenicity_optimization_pipeline.py"]
    
    # 添加参数
    cmd.extend(["--fasta", args.fasta])
    cmd.extend(["--pdb", args.pdb])
    cmd.extend(["--mode", args.mode])
    
    if args.epitopes:
        cmd.extend(["--epitopes", args.epitopes])
    if args.output_dir:
        cmd.extend(["--output-dir", args.output_dir])
    if args.log_level:
        cmd.extend(["--log-level", args.log_level])
    if args.samples_per_temp:
        cmd.extend(["--samples-per-temp", str(args.samples_per_temp)])
    if args.temperatures:
        cmd.extend(["--temperatures"] + [str(t) for t in args.temperatures])
    if args.max_candidates:
        cmd.extend(["--max-candidates", str(args.max_candidates)])
    if args.rmsd_threshold:
        cmd.extend(["--rmsd-threshold", str(args.rmsd_threshold)])
    if args.interface_analysis is not None:
        if args.interface_analysis:
            cmd.append("--interface-analysis")
    if args.dg_dsasa_threshold:
        cmd.extend(["--dg-dsasa-threshold", str(args.dg_dsasa_threshold)])
    if args.buns_threshold:
        cmd.extend(["--buns-threshold", str(args.buns_threshold)])
    if args.packstat_threshold:
        cmd.extend(["--packstat-threshold", str(args.packstat_threshold)])
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"管道运行失败: {e}")
        sys.exit(1)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="VLPIM - Variable Length Protein Immunogenicity Modulator",
        add_help=False
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # help命令
    help_parser = subparsers.add_parser('help', help='显示帮助信息')
    
    # run命令
    run_parser = subparsers.add_parser('run', help='运行免疫原性优化管道')
    
    # 必需参数
    run_parser.add_argument('--fasta', type=str, required=True,
                           help='输入FASTA文件路径')
    run_parser.add_argument('--pdb', type=str, required=True,
                           help='输入PDB文件路径')
    run_parser.add_argument('--mode', type=str, choices=['reduce', 'enhance'],
                           default='reduce',
                           help='免疫原性调节模式: reduce(降低) 或 enhance(增强)')
    
    # 可选参数
    run_parser.add_argument('--epitopes', type=str,
                           help='用户提供的抗原位点CSV文件')
    run_parser.add_argument('--output-dir', type=str, default='results',
                           help='结果输出目录')
    run_parser.add_argument('--log-level', type=str, 
                           choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                           default='INFO', help='日志级别')
    
    # ProteinMPNN参数
    run_parser.add_argument('--samples-per-temp', type=int, default=20,
                           help='每个温度的样本数')
    run_parser.add_argument('--temperatures', type=float, nargs='+',
                           default=[0.1, 0.3, 0.5],
                           help='温度值列表')
    
    # 结构预测参数
    run_parser.add_argument('--max-candidates', type=int, default=10,
                           help='结构预测的最大候选数')
    run_parser.add_argument('--rmsd-threshold', type=float, default=2.0,
                           help='RMSD阈值用于结构过滤')
    
    # 界面分析参数
    run_parser.add_argument('--interface-analysis', action='store_true',
                           default=True, help='启用Rosetta界面分析')
    run_parser.add_argument('--dg-dsasa-threshold', type=float, default=-0.5,
                           help='dG/dSASA阈值用于界面过滤')
    run_parser.add_argument('--buns-threshold', type=int, default=5,
                           help='BUNS阈值用于界面过滤')
    run_parser.add_argument('--packstat-threshold', type=float, default=0.6,
                           help='Packstat阈值用于界面过滤')
    
    # 其他命令
    config_parser = subparsers.add_parser('config', help='显示配置信息')
    validate_parser = subparsers.add_parser('validate', help='验证配置和工具可用性')
    setup_parser = subparsers.add_parser('setup', help='运行安装脚本')
    test_parser = subparsers.add_parser('test', help='运行基本测试')
    
    # 解析参数
    args = parser.parse_args()
    
    # 如果没有命令或命令是help，显示帮助
    if not args.command or args.command == 'help':
        show_help()
    elif args.command == 'config':
        show_config()
    elif args.command == 'validate':
        validate_config()
    elif args.command == 'setup':
        run_setup()
    elif args.command == 'test':
        run_tests()
    elif args.command == 'run':
        run_pipeline(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
