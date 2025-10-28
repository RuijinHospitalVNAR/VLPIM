# 路径配置指南

## 概述

本指南详细说明如何配置外部工具的路径，让免疫原性优化管道能够正确调用真实工具。

**重要说明**: 用户需要自己安装这些外部工具，VLPIM项目不提供安装帮助。本指南仅说明如何配置已安装工具的路径。

## 🔧 配置方法

### 方法1：使用环境变量（推荐）

```bash
# 设置工具路径
export ALPHAFOLD3_PATH="/path/to/alphafold3"
export PROTEINMPNN_PATH="/path/to/ProteinMPNN"
export NETMHCIIPAN_PATH="/path/to/netMHCIIpan"
export ROSETTA_PATH="/path/to/rosetta"

# 设置模型权重路径
export PROTEINMPNN_MODEL_WEIGHTS="/path/to/ProteinMPNN/model_weights"
export ALPHAFOLD3_MODEL_WEIGHTS="/path/to/alphafold3/model_weights"

# 设置默认参数
export DEFAULT_OUTPUT_DIR="results"
export DEFAULT_LOG_LEVEL="INFO"
```

### 方法2：使用配置文件

在 `config/config_unified.yaml` 中配置：

```yaml
tools:
  alphafold3: "/path/to/alphafold3"
  proteinmpnn: "/path/to/ProteinMPNN"
  netmhcii: "/path/to/netMHCIIpan"
  rosetta: "/path/to/rosetta"

model_weights:
  proteinmpnn: "/path/to/ProteinMPNN/model_weights"
  alphafold3: "/path/to/alphafold3/model_weights"
```

### 方法3：自动检测

系统会自动检测以下常见路径：

```python
# Linux/macOS 常见路径
DEFAULT_PATHS = {
    'alphafold3': [
        '/opt/alphafold3',
        '/usr/local/alphafold3',
        '~/alphafold3'
    ],
    'proteinmpnn': [
        '/opt/ProteinMPNN',
        '/usr/local/ProteinMPNN',
        '~/ProteinMPNN'
    ],
    'netmhcii': [
        '/opt/netMHCIIpan',
        '/usr/local/netMHCIIpan',
        '~/netMHCIIpan'
    ],
    'rosetta': [
        '/opt/rosetta',
        '/usr/local/rosetta',
        '~/rosetta'
    ]
}
```

## 🛠️ 工具安装路径

### AlphaFold3

```bash
# 下载并解压
wget https://github.com/google-deepmind/alphafold3/releases/latest/download/alphafold3.tar.gz
tar -xzf alphafold3.tar.gz
export ALPHAFOLD3_PATH="/path/to/alphafold3"
```

### ProteinMPNN

```bash
# 克隆仓库
git clone https://github.com/dauparas/ProteinMPNN.git
cd ProteinMPNN
export PROTEINMPNN_PATH="/path/to/ProteinMPNN"
```

### NetMHCIIpan

```bash
# 下载并安装
wget https://services.healthtech.dtu.dk/download/NetMHCIIpan-4.3.tar.gz
tar -xzf NetMHCIIpan-4.3.tar.gz
export NETMHCIIPAN_PATH="/path/to/netMHCIIpan"
```

### Rosetta

```bash
# 下载并安装
wget https://www.rosettacommons.org/downloads/rosetta.tar.gz
tar -xzf rosetta.tar.gz
export ROSETTA_PATH="/path/to/rosetta"
```

## 🔍 验证配置

### 检查环境变量

```bash
# 检查环境变量是否设置
echo $ALPHAFOLD3_PATH
echo $PROTEINMPNN_PATH
echo $NETMHCIIPAN_PATH
echo $ROSETTA_PATH
```

### 验证工具可用性

```bash
# 使用VLPIM验证
python -m vlpim validate

# 手动检查工具
which alphafold3
which protein_mpnn_run.py
which netMHCIIpan
which interface_analyzer
```

### 测试工具调用

```bash
# 测试AlphaFold3
python -c "from src.vlpim.tools.alphafold3_wrapper import predict_structure_and_score; print('AlphaFold3 OK')"

# 测试ProteinMPNN
python -c "from src.vlpim.tools.protein_mpnn_wrapper import generate_mutants; print('ProteinMPNN OK')"

# 测试NetMHCIIpan
python -c "from src.vlpim.tools.netmhcii_runner import predict_epitopes_with_netmhcii; print('NetMHCIIpan OK')"

# 测试Rosetta
python -c "from src.vlpim.tools.rosetta_wrapper import analyze_interface; print('Rosetta OK')"
```

## 🚨 常见问题

### 1. 工具未找到

**错误信息**: `Tool not found: [tool_name]`

**解决方案**:
- 检查环境变量是否正确设置
- 确认工具已正确安装
- 检查PATH环境变量
- 使用绝对路径

### 2. 权限问题

**错误信息**: `Permission denied`

**解决方案**:
- 检查文件权限
- 使用chmod添加执行权限
- 确认用户有访问权限

### 3. 依赖缺失

**错误信息**: `Module not found`

**解决方案**:
- 安装Python依赖
- 检查Python版本兼容性
- 安装系统依赖

### 4. 配置验证失败

**错误信息**: `Configuration validation failed`

**解决方案**:
- 检查配置文件格式
- 验证路径是否存在
- 检查YAML语法

## 📝 配置示例

### 完整的环境变量配置

```bash
# 添加到 ~/.bashrc 或 ~/.zshrc
# 工具路径
export ALPHAFOLD3_PATH="/opt/alphafold3"
export PROTEINMPNN_PATH="/opt/ProteinMPNN"
export NETMHCIIPAN_PATH="/opt/netMHCIIpan"
export ROSETTA_PATH="/opt/rosetta"

# 模型权重路径
export PROTEINMPNN_MODEL_WEIGHTS="/opt/ProteinMPNN/model_weights"
export ALPHAFOLD3_MODEL_WEIGHTS="/opt/alphafold3/model_weights"

# 默认参数
export DEFAULT_OUTPUT_DIR="results"
export DEFAULT_LOG_LEVEL="INFO"
export DEFAULT_MAX_CANDIDATES="10"
export DEFAULT_RMSD_THRESHOLD="2.0"

# 重新加载配置
source ~/.bashrc
```

### 完整的配置文件

```yaml
# config/config_unified.yaml
tools:
  alphafold3: "/opt/alphafold3"
  proteinmpnn: "/opt/ProteinMPNN"
  netmhcii: "/opt/netMHCIIpan"
  rosetta: "/opt/rosetta"

model_weights:
  proteinmpnn: "/opt/ProteinMPNN/model_weights"
  alphafold3: "/opt/alphafold3/model_weights"

defaults:
  output_dir: "results"
  log_level: "INFO"
  max_candidates: 10
  rmsd_threshold: 2.0
  samples_per_temp: 20
  temperatures: [0.1, 0.3, 0.5]

hla_alleles:
  - "DRB1*01:01"
  - "DRB1*03:01"
  - "DRB1*04:01"
  - "DRB1*07:01"
  - "DRB1*08:01"
  - "DRB1*11:01"
  - "DRB1*13:01"
  - "DRB1*15:01"
```

## 🔧 高级配置

### 自定义工具路径

```python
# 在代码中自定义路径
from src.vlpim.tools.path_config import PathConfig

path_config = PathConfig()
path_config.ALPHAFOLD3_PATH = "/custom/path/to/alphafold3"
path_config.PROTEINMPNN_PATH = "/custom/path/to/ProteinMPNN"
```

### 动态路径检测

```python
# 自动检测工具路径
def find_tool_path(tool_name):
    """自动检测工具路径"""
    import shutil
    return shutil.which(tool_name)
```

### 多版本支持

```bash
# 支持多个版本的工具
export ALPHAFOLD3_PATH="/opt/alphafold3-v1.0"
export ALPHAFOLD3_PATH_V2="/opt/alphafold3-v2.0"
```

## 📚 参考资源

- [AlphaFold3 安装指南](https://github.com/google-deepmind/alphafold3)
- [ProteinMPNN 安装指南](https://github.com/dauparas/ProteinMPNN)
- [NetMHCIIpan 安装指南](https://services.healthtech.dtu.dk/services/NetMHCIIpan-4.3/)
- [Rosetta 安装指南](https://www.rosettacommons.org/)

## 🆘 获取帮助

如果遇到配置问题，可以：

1. 查看日志文件获取详细错误信息
2. 使用 `python -m vlpim validate` 验证配置
3. 检查工具是否正常工作
4. 参考官方文档
5. 提交问题到GitHub Issues
