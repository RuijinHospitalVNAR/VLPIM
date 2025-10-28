# 如何调用真实工具 - 完整指南

## 概述

本指南详细说明如何将占位符实现替换为真实的工具调用，让免疫原性优化管道能够真正运行。

**重要说明**: 用户需要自己安装这些外部工具，VLPIM项目不提供安装帮助。本指南仅说明如何配置已安装工具的调用。

## 🔧 替换步骤

### 1. 替换 AlphaFold3 实现

**当前占位符文件**: `tools/alphafold3_runner.py`
**真实实现文件**: `tools/alphafold3_runner_real.py`

```bash
# 备份原文件
cp tools/alphafold3_runner.py tools/alphafold3_runner_backup.py

# 替换为真实实现
cp tools/alphafold3_runner_real.py tools/alphafold3_runner.py
```

**真实实现特点**:
- 调用 `run_alphafold.py` 作为入口点
- 使用 JSON 输入格式
- 支持多聚体结构预测
- 解析 PDB 输出文件
- 计算 RMSD 和置信度评分

### 2. 替换 ProteinMPNN 实现

**当前占位符文件**: `tools/protein_mpnn_wrapper.py`
**真实实现文件**: `tools/protein_mpnn_wrapper_real.py`

```bash
# 备份原文件
cp tools/protein_mpnn_wrapper.py tools/protein_mpnn_wrapper_backup.py

# 替换为真实实现
cp tools/protein_mpnn_wrapper_real.py tools/protein_mpnn_wrapper.py
```

**真实实现特点**:
- 调用 `protein_mpnn_run.py` 作为入口点
- 支持固定位置约束
- 使用 JSONL 格式的约束文件
- 支持多种采样温度
- 解析 FASTA 输出文件

### 3. 替换 NetMHCIIpan 实现

**当前占位符文件**: `tools/netmhcii_runner.py`
**真实实现文件**: `tools/netmhcii_runner_real.py`

```bash
# 备份原文件
cp tools/netmhcii_runner.py tools/netmhcii_runner_backup.py

# 替换为真实实现
cp tools/netmhcii_runner_real.py tools/netmhcii_runner.py
```

**真实实现特点**:
- 调用 NetMHCIIpan-4.3 可执行文件
- 支持 FASTA 输入格式
- 支持多种 HLA 等位基因
- 输出结合亲和力和 %rank 评分
- 解析标准输出格式

### 4. 替换 Rosetta 实现

**当前占位符文件**: `tools/rosetta_interface_analyzer.py`
**真实实现文件**: `tools/rosetta_interface_analyzer_real.py`

```bash
# 备份原文件
cp tools/rosetta_interface_analyzer.py tools/rosetta_interface_analyzer_backup.py

# 替换为真实实现
cp tools/rosetta_interface_analyzer_real.py tools/rosetta_interface_analyzer.py
```

**真实实现特点**:
- 调用 `interface_analyzer` 可执行文件
- 支持多聚体界面分析
- 计算 dG/dSASA、BUNS、packstat 等指标
- 解析 score 文件和 silent 文件
- 提供界面质量评估

## 🛠️ 工具安装和配置

**注意**: 以下工具需要用户自己安装，VLPIM项目不提供安装帮助。这里仅提供参考链接：

### AlphaFold3 安装

```bash
# 参考官方安装指南
# https://github.com/google-deepmind/alphafold3
```

### ProteinMPNN 安装

```bash
# 参考官方安装指南
# https://github.com/dauparas/ProteinMPNN
```

### NetMHCIIpan 安装

```bash
# 参考官方安装指南
# https://services.healthtech.dtu.dk/services/NetMHCIIpan-4.3/
```

### Rosetta 安装

```bash
# 参考官方安装指南
# https://www.rosettacommons.org/
```

## 🔍 验证工具调用

### 测试 AlphaFold3

```python
# 测试 AlphaFold3 调用
from tools.alphafold3_runner import predict_structure_and_score
import pandas as pd

# 创建测试数据
candidates_df = pd.DataFrame({
    'sequence': ['MKLLVLGCTAGCTTTCCGGA'],
    'score': [0.85]
})

# 运行预测
results = predict_structure_and_score(candidates_df, 'test_output')
print(f"预测结果: {len(results)} 个结构")
```

### 测试 ProteinMPNN

```python
# 测试 ProteinMPNN 调用
from tools.protein_mpnn_wrapper import generate_mutants
import pandas as pd

# 创建测试数据
epitope_df = pd.DataFrame({
    'sequence': ['MKLLVLGCT'],
    'start': [1],
    'end': [9]
})

# 运行序列生成
mutants = generate_mutants('test.pdb', epitope_df, 'reduce')
print(f"生成突变体: {len(mutants)} 个序列")
```

### 测试 NetMHCIIpan

```python
# 测试 NetMHCIIpan 调用
from tools.netmhcii_runner import predict_epitopes_with_netmhcii

# 运行表位预测
epitopes = predict_epitopes_with_netmhcii('test.fasta', ['DRB1*01:01'], 'test_output')
print(f"预测表位: {len(epitopes)} 个")
```

### 测试 Rosetta

```python
# 测试 Rosetta 调用
from tools.rosetta_interface_analyzer import analyze_interface
import pandas as pd

# 创建测试数据
structure_df = pd.DataFrame({
    'predicted_pdb_path': ['test.pdb'],
    'sequence_id': [0]
})

# 运行界面分析
interface_results = analyze_interface(structure_df, 'test_output')
print(f"界面分析结果: {len(interface_results)} 个")
```

## 🚨 常见问题解决

### 1. 工具未找到

**错误**: `Tool not found: [tool_name]`

**解决方案**:
```bash
# 检查环境变量
echo $ALPHAFOLD3_PATH
echo $PROTEINMPNN_PATH
echo $NETMHCIIPAN_PATH
echo $ROSETTA_PATH

# 检查工具是否在PATH中
which alphafold3
which protein_mpnn_run.py
which netMHCIIpan
which interface_analyzer
```

### 2. 权限问题

**错误**: `Permission denied`

**解决方案**:
```bash
# 添加执行权限
chmod +x /path/to/alphafold3/run_alphafold.py
chmod +x /path/to/ProteinMPNN/protein_mpnn_run.py
chmod +x /path/to/netMHCIIpan/netMHCIIpan
chmod +x /path/to/rosetta/interface_analyzer
```

### 3. 依赖缺失

**错误**: `Module not found`

**解决方案**:
```bash
# 安装Python依赖
pip install -r requirements.txt

# 安装系统依赖
sudo apt install build-essential python3-dev

# 检查Python版本
python3 --version
```

### 4. 内存不足

**错误**: `MemoryError`

**解决方案**:
```bash
# 增加交换空间
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# 优化内存使用
export OMP_NUM_THREADS=2
export MKL_NUM_THREADS=2
```

## 📊 性能优化

### 并行处理

```python
# 在工具包装器中启用并行处理
import multiprocessing as mp

def parallel_predict(candidates):
    with mp.Pool(processes=4) as pool:
        results = pool.map(predict_single, candidates)
    return results
```

### 缓存机制

```python
# 实现结果缓存
import pickle
import hashlib

def cache_results(func):
    def wrapper(*args, **kwargs):
        # 生成缓存键
        cache_key = hashlib.md5(str(args).encode()).hexdigest()
        cache_file = f"cache/{cache_key}.pkl"
        
        # 检查缓存
        if os.path.exists(cache_file):
            with open(cache_file, 'rb') as f:
                return pickle.load(f)
        
        # 运行函数并缓存结果
        result = func(*args, **kwargs)
        with open(cache_file, 'wb') as f:
            pickle.dump(result, f)
        
        return result
    return wrapper
```

### 资源监控

```python
# 监控资源使用
import psutil
import time

def monitor_resources():
    while True:
        cpu_percent = psutil.cpu_percent()
        memory_percent = psutil.virtual_memory().percent
        print(f"CPU: {cpu_percent}%, Memory: {memory_percent}%")
        time.sleep(1)
```

## 🔄 更新和维护

### 定期更新

```bash
# 更新工具版本
git pull origin main

# 重新安装依赖
pip install -r requirements.txt --upgrade

# 重新验证工具
python -m vlpim validate
```

### 备份配置

```bash
# 备份配置文件
cp config/config_unified.yaml config/config_unified.yaml.backup

# 备份环境变量
env | grep -E "(ALPHAFOLD3|PROTEINMPNN|NETMHCIIPAN|ROSETTA)" > env_backup.txt
```

### 日志管理

```bash
# 清理旧日志
find results/ -name "*.log" -mtime +7 -delete

# 压缩日志文件
gzip results/pipeline.log
```

## 📚 参考资源

- [AlphaFold3 官方文档](https://github.com/google-deepmind/alphafold3)
- [ProteinMPNN 官方文档](https://github.com/dauparas/ProteinMPNN)
- [NetMHCIIpan 官方文档](https://services.healthtech.dtu.dk/services/NetMHCIIpan-4.3/)
- [Rosetta 官方文档](https://www.rosettacommons.org/)

## 🆘 获取帮助

如果遇到问题，可以：

1. 查看详细日志文件
2. 使用调试模式运行
3. 检查工具是否正常工作
4. 参考官方文档
5. 提交问题到GitHub Issues
