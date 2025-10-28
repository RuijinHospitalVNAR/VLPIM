# VLPIM 用户自定义参数总结

## 概述

VLPIM: A Comprehensive Tool for Immunogenicity Modulation of Virus-like Particles 提供了丰富的参数配置选项，用户可以通过命令行参数、环境变量和配置文件来自定义管道的运行行为。

## 查看帮助

使用以下命令查看完整的参数说明：

```bash
# Linux/macOS
python -m vlpim help
# 或
python -m vlpim --help

# Windows
python -m vlpim help
# 或
python -m vlpim --help
```

## 主要参数分类

### 1. 输入文件参数

#### 必需参数
- `--fasta`: FASTA格式的蛋白质序列文件路径
- `--pdb`: PDB格式的蛋白质结构文件路径

#### 可选参数
- `--epitopes`: 用户提供的表位文件路径（CSV格式）
- `--mode`: 免疫原性调节模式（reduce/enhance）

### 2. 输出配置参数

- `--output-dir`: 输出目录路径（默认：results）
- `--log-level`: 日志级别（DEBUG/INFO/WARNING/ERROR）
- `--log-file`: 日志文件路径（可选）

### 3. 表位预测参数

#### NetMHCIIpan参数
- `--hla-alleles`: HLA等位基因列表
- `--peptide-length`: 肽段长度（默认：15）
- `--binding-threshold`: 结合阈值（默认：500nM）

#### 用户提供表位
- `--epitopes`: 表位文件路径
- `--epitope-format`: 表位文件格式（CSV/TSV）

### 4. 序列生成参数

#### ProteinMPNN参数
- `--samples-per-temp`: 每个温度下的样本数（默认：20）
- `--temperatures`: 采样温度列表（默认：[0.1, 0.3, 0.5]）
- `--max-length`: 最大序列长度（默认：200000）
- `--model-name`: 模型名称（默认：v_48_020）

### 5. 结构预测参数

#### AlphaFold3参数
- `--max-candidates`: 最大候选数（默认：10）
- `--rmsd-threshold`: RMSD阈值（默认：2.0）
- `--confidence-threshold`: 置信度阈值（默认：0.7）

### 6. 界面分析参数

#### Rosetta参数
- `--dg-dsasa-threshold`: dG/dSASA阈值（默认：-0.5）
- `--buns-threshold`: BUNS阈值（默认：5）
- `--packstat-threshold`: Packstat阈值（默认：0.6）

### 7. 环境变量参数

#### 工具路径
- `PROTEIN_MPNN_PATH`: ProteinMPNN安装路径
- `NETMHCIIPAN_PATH`: NetMHCIIpan安装路径
- `ALPHAFOLD3_PATH`: AlphaFold3安装路径
- `ROSETTA_PATH`: Rosetta安装路径

#### 默认参数
- `DEFAULT_OUTPUT_DIR`: 默认输出目录
- `DEFAULT_LOG_LEVEL`: 默认日志级别

## 配置文件参数

### config_unified.yaml

```yaml
# 输入文件
fasta_path: "input/protein.fasta"
pdb_path: "input/protein.pdb"
mode: "reduce"

# 输出配置
output_dir: "results"
log_level: "INFO"

# 表位预测
hla_alleles:
  - "DRB1*01:01"
  - "DRB1*03:01"
  - "DRB1*04:01"
  - "DRB1*07:01"

# 序列生成
samples_per_temp: 20
temperatures: [0.1, 0.3, 0.5]

# 结构预测
max_candidates: 10
rmsd_threshold: 2.0

# 界面分析
dg_dsasa_threshold: -0.5
buns_threshold: 5
packstat_threshold: 0.6

# 工具路径
tools:
  proteinmpnn: "/path/to/ProteinMPNN"
  netmhcii: "/path/to/netMHCIIpan"
  alphafold3: "/path/to/alphafold3"
  rosetta: "/path/to/rosetta"
```

## 使用示例

### 基本用法
```bash
python -m vlpim run --fasta input/protein.fasta --pdb input/protein.pdb --mode reduce
```

### 使用用户提供的表位
```bash
python -m vlpim run --fasta input/protein.fasta --pdb input/protein.pdb --mode reduce --epitopes input/epitopes.csv
```

### 自定义参数
```bash
python -m vlpim run \
  --fasta input/protein.fasta \
  --pdb input/protein.pdb \
  --mode reduce \
  --output-dir custom_results \
  --samples-per-temp 50 \
  --max-candidates 20 \
  --log-level DEBUG
```

### 使用配置文件
```bash
python -m vlpim run --config config/custom_config.yaml
```

## 参数验证

使用以下命令验证配置：

```bash
# 验证配置文件
python -m vlpim validate

# 显示当前配置
python -m vlpim config

# 测试工具可用性
python -m vlpim test
```

## 注意事项

1. **必需参数**: `--fasta` 和 `--pdb` 是必需的
2. **文件格式**: 确保输入文件格式正确
3. **工具路径**: 确保外部工具已正确安装并设置环境变量
4. **权限**: 确保对输出目录有写权限
5. **资源**: 某些操作可能需要大量计算资源

## 故障排除

### 常见错误
- `FileNotFoundError`: 检查文件路径是否正确
- `PermissionError`: 检查文件权限
- `Tool not found`: 检查环境变量设置
- `Configuration validation failed`: 检查配置文件格式

### 调试模式
```bash
python -m vlpim run --log-level DEBUG --fasta input/protein.fasta --pdb input/protein.pdb
```
