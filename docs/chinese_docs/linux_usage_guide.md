# Linux 系统使用指南

## 系统要求检查

```bash
# 检查 Python 版本
python3 --version

# 检查 pip
pip3 --version

# 检查 Git
git --version
```

**重要说明**: 用户需要自己安装以下外部工具，VLPIM项目不提供安装帮助：
- AlphaFold3
- ProteinMPNN  
- NetMHCIIpan
- Rosetta

## 安装步骤

### 方法一：使用自动化脚本（推荐）

```bash
# 克隆仓库
git clone https://github.com/RuijinHospitalVNAR/VLPIM.git
cd VLPIM

# 运行环境配置脚本
chmod +x scripts/install_environment.sh
./scripts/install_environment.sh
```

### 方法二：手动安装

```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 安装项目
pip install -e .
```

### 方法三：使用Conda

```bash
# 创建Conda环境
conda env create -f environment.yml

# 激活环境
conda activate vlpim

# 安装项目
pip install -e .
```

## 环境变量配置

### 设置工具路径

```bash
# 添加到 ~/.bashrc
echo 'export ALPHAFOLD3_PATH="/path/to/alphafold3"' >> ~/.bashrc
echo 'export PROTEINMPNN_PATH="/path/to/ProteinMPNN"' >> ~/.bashrc
echo 'export NETMHCIIPAN_PATH="/path/to/netMHCIIpan"' >> ~/.bashrc
echo 'export ROSETTA_PATH="/path/to/rosetta"' >> ~/.bashrc

# 重新加载配置
source ~/.bashrc
```

### 验证环境变量

```bash
# 检查环境变量
echo $ALPHAFOLD3_PATH
echo $PROTEINMPNN_PATH
echo $NETMHCIIPAN_PATH
echo $ROSETTA_PATH
```

## 外部工具安装

**注意**: 以下工具需要用户自己安装，VLPIM项目不提供安装帮助。这里仅提供参考链接：

### AlphaFold3

```bash
# 参考官方安装指南
# https://github.com/google-deepmind/alphafold3
```

### ProteinMPNN

```bash
# 参考官方安装指南  
# https://github.com/dauparas/ProteinMPNN
```

### NetMHCIIpan

```bash
# 参考官方安装指南
# https://services.healthtech.dtu.dk/services/NetMHCIIpan-4.3/
```

### Rosetta

```bash
# 参考官方安装指南
# https://www.rosettacommons.org/
```

## 使用示例

### 基本使用

```bash
# 运行免疫原性优化
python -m vlpim run --fasta examples/protein.fasta --pdb examples/protein.pdb --mode reduce
```

### 使用用户提供的表位

```bash
# 使用自定义表位文件
python -m vlpim run --fasta examples/protein.fasta --pdb examples/protein.pdb --mode reduce --epitopes examples/example_epitopes.csv
```

### 自定义参数

```bash
# 自定义输出目录和参数
python -m vlpim run \
  --fasta examples/protein.fasta \
  --pdb examples/protein.pdb \
  --mode reduce \
  --output-dir custom_results \
  --samples-per-temp 50 \
  --max-candidates 20 \
  --log-level DEBUG
```

## 配置验证

### 验证工具安装

```bash
# 验证所有工具
python -m vlpim validate

# 显示当前配置
python -m vlpim config

# 运行测试
python -m vlpim test
```

### 手动验证工具

```bash
# 检查工具是否可用
which alphafold3
which protein_mpnn_run.py
which netMHCIIpan
which interface_analyzer
```

## 故障排除

### 常见问题

#### 1. Python版本问题

```bash
# 检查Python版本
python3 --version

# 如果版本过低，升级Python
sudo apt update
sudo apt install python3.10 python3.10-venv python3.10-pip
```

#### 2. 依赖安装失败

```bash
# 更新pip
pip install --upgrade pip

# 安装系统依赖
sudo apt install build-essential python3-dev

# 重新安装依赖
pip install -r requirements.txt
```

#### 3. 权限问题

```bash
# 添加执行权限
chmod +x scripts/setup.sh
chmod +x scripts/quick_start.sh

# 检查文件权限
ls -la scripts/
```

#### 4. 环境变量问题

```bash
# 检查环境变量
env | grep -E "(ALPHAFOLD3|PROTEINMPNN|NETMHCIIPAN|ROSETTA)"

# 重新加载配置
source ~/.bashrc
```

### 调试模式

```bash
# 启用调试日志
python -m vlpim run --log-level DEBUG --fasta examples/protein.fasta --pdb examples/protein.pdb

# 查看详细错误信息
python -m vlpim run --fasta examples/protein.fasta --pdb examples/protein.pdb 2>&1 | tee debug.log
```

## 性能优化

### 系统优化

```bash
# 增加文件描述符限制
echo "* soft nofile 65536" >> /etc/security/limits.conf
echo "* hard nofile 65536" >> /etc/security/limits.conf

# 优化内存使用
echo "vm.swappiness=10" >> /etc/sysctl.conf
```

### 并行处理

```bash
# 设置并行线程数
export OMP_NUM_THREADS=4
export MKL_NUM_THREADS=4

# 运行管道
python -m vlpim run --fasta examples/protein.fasta --pdb examples/protein.pdb --mode reduce
```

## 监控和日志

### 查看日志

```bash
# 查看实时日志
tail -f results/pipeline.log

# 查看错误日志
grep ERROR results/pipeline.log

# 查看警告日志
grep WARNING results/pipeline.log
```

### 系统监控

```bash
# 监控CPU使用率
top -p $(pgrep -f "python.*vlpim")

# 监控内存使用
ps aux | grep vlpim

# 监控磁盘使用
df -h
```

## 备份和恢复

### 备份配置

```bash
# 备份配置文件
cp config/config_unified.yaml config/config_unified.yaml.backup

# 备份环境变量
env | grep -E "(ALPHAFOLD3|PROTEINMPNN|NETMHCIIPAN|ROSETTA)" > env_backup.txt
```

### 恢复配置

```bash
# 恢复配置文件
cp config/config_unified.yaml.backup config/config_unified.yaml

# 恢复环境变量
source env_backup.txt
```

## 更新和维护

### 更新项目

```bash
# 拉取最新代码
git pull origin main

# 更新依赖
pip install -r requirements.txt --upgrade

# 重新安装项目
pip install -e .
```

### 清理临时文件

```bash
# 使用Makefile清理
make clean

# 手动清理
rm -rf __pycache__/
rm -rf .pytest_cache/
rm -rf results/temp/
```

## 获取帮助

### 在线资源

- [GitHub仓库](https://github.com/RuijinHospitalVNAR/VLPIM)
- [问题追踪](https://github.com/RuijinHospitalVNAR/VLPIM/issues)
- [文档](https://github.com/RuijinHospitalVNAR/VLPIM#readme)

### 社区支持

- 提交问题到GitHub Issues
- 参与讨论
- 贡献代码

### 联系支持

- 邮箱：wcf1112@sjtu.edu.cn
- GitHub：@chufan
