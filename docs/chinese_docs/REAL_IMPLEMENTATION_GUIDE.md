# 真实实现指南

## 当前状态

**⚠️ 重要：目前所有工具模块都是占位符实现**

即使工作站上安装了 AlphaFold3、ProteinMPNN、NetMHCIIpan、Rosetta 等工具，软件也无法正常运行，因为代码中没有真正调用这些工具。

**重要说明**: 用户需要自己安装这些外部工具，VLPIM项目不提供安装帮助。本指南仅说明如何实现真实工具调用。

## 需要实现的功能

### 1. AlphaFold3 真实实现

```python
# 替换 tools/alphafold3_runner.py 中的占位符
def predict_structure_and_score(candidates_df: pd.DataFrame, 
                               rmsd_threshold: float = 2.0) -> pd.DataFrame:
    """真实的 AlphaFold3 实现"""
    results = []
    
    for idx, row in candidates_df.iterrows():
        sequence = row['sequence']
        
        # 创建 FASTA 文件
        fasta_file = f"temp/sequence_{idx}.fasta"
        with open(fasta_file, 'w') as f:
            f.write(f">sequence_{idx}\n{sequence}\n")
        
        # 调用 AlphaFold3
        cmd = [
            "python", "run_alphafold.py",
            "--fasta_path", fasta_file,
            "--output_dir", f"temp/alphafold3_{idx}",
            "--model_preset", "multimer",
            "--max_template_date", "2023-12-31"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            # 解析 PDB 文件
            pdb_file = f"temp/alphafold3_{idx}/ranked_0.pdb"
            if os.path.exists(pdb_file):
                # 计算 RMSD 和置信度
                rmsd = calculate_rmsd(pdb_file, reference_pdb)
                confidence = calculate_confidence(pdb_file)
                
                results.append({
                    'sequence_id': idx,
                    'sequence': sequence,
                    'predicted_pdb_path': pdb_file,
                    'rmsd': rmsd,
                    'confidence': confidence,
                    'rank': 1
                })
    
    return pd.DataFrame(results)
```

### 2. ProteinMPNN 真实实现

```python
# 替换 tools/protein_mpnn_wrapper.py 中的占位符
def generate_mutants(pdb_path: str, epitope_df: pd.DataFrame, 
                    mode: str, samples_per_temp: int = 20) -> List[str]:
    """真实的 ProteinMPNN 实现"""
    mutants = []
    
    # 创建固定位置文件
    fixed_positions = create_fixed_positions(epitope_df, mode)
    
    for temp in [0.1, 0.3, 0.5]:
        # 调用 ProteinMPNN
        cmd = [
            "python", "protein_mpnn_run.py",
            "--pdb_path", pdb_path,
            "--out_folder", f"temp/proteinmpnn_{temp}",
            "--num_seq_per_target", str(samples_per_temp),
            "--sampling_temp", str(temp),
            "--fixed_positions", fixed_positions
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            # 解析输出文件
            output_file = f"temp/proteinmpnn_{temp}/seqs.fasta"
            if os.path.exists(output_file):
                with open(output_file, 'r') as f:
                    content = f.read()
                    sequences = parse_fasta(content)
                    mutants.extend(sequences)
    
    return mutants
```

### 3. NetMHCIIpan 真实实现

```python
# 替换 tools/netmhcii_runner.py 中的占位符
def predict_epitopes_with_netmhcii(fasta_path: str, hla_alleles: List[str]) -> pd.DataFrame:
    """真实的 NetMHCIIpan 实现"""
    epitopes = []
    
    # 调用 NetMHCIIpan
    cmd = [
        "netMHCIIpan",
        "-f", fasta_path,
        "-a", ",".join(hla_alleles),
        "-inptype", "1",
        "-length", "15",
        "-BA",
        "-outdir", "temp/netmhcii"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        # 解析输出文件
        output_file = "temp/netmhcii/netMHCIIpan.out"
        if os.path.exists(output_file):
            with open(output_file, 'r') as f:
                lines = f.readlines()
                for line in lines:
                    if not line.startswith('#'):
                        parts = line.strip().split()
                        if len(parts) >= 8:
                            epitopes.append({
                                'sequence': parts[0],
                                'allele': parts[1],
                                'score': float(parts[2]),
                                'rank': float(parts[3]),
                                'start': int(parts[4]),
                                'end': int(parts[4]) + len(parts[0]) - 1
                            })
    
    return pd.DataFrame(epitopes)
```

### 4. Rosetta 真实实现

```python
# 替换 tools/rosetta_interface_analyzer.py 中的占位符
def analyze_interface(structure_results_df: pd.DataFrame) -> pd.DataFrame:
    """真实的 Rosetta 界面分析实现"""
    interface_results = []
    
    for idx, row in structure_results_df.iterrows():
        pdb_path = row['predicted_pdb_path']
        
        # 调用 interface_analyzer
        cmd = [
            "interface_analyzer",
            "-s", pdb_path,
            "-out:file:scorefile", f"temp/rosetta_{idx}/interface_score.sc",
            "-out:file:o", f"temp/rosetta_{idx}/interface_analysis.pdb",
            "-interface_analyzer:interface", "A_B",
            "-interface_analyzer:compute_packstat", "true",
            "-interface_analyzer:pack_separated", "true",
            "-interface_analyzer:pack_together", "true"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            # 解析 score 文件
            score_file = f"temp/rosetta_{idx}/interface_score.sc"
            if os.path.exists(score_file):
                with open(score_file, 'r') as f:
                    lines = f.readlines()
                    for line in lines:
                        if not line.startswith('#'):
                            parts = line.strip().split()
                            if len(parts) >= 10:
                                interface_results.append({
                                    'sequence_id': idx,
                                    'dG_separated': float(parts[1]),
                                    'dG_together': float(parts[2]),
                                    'dG_dSASA': float(parts[3]),
                                    'packstat': float(parts[4]),
                                    'delta_unsat_hbonds': int(parts[5]),
                                    'interface_sc': float(parts[6]),
                                    'dSASA_int': float(parts[7])
                                })
    
    return pd.DataFrame(interface_results)
```

## 实现步骤

### 1. 备份原始文件

```bash
# 备份所有占位符文件
cp tools/alphafold3_runner.py tools/alphafold3_runner_placeholder.py
cp tools/protein_mpnn_wrapper.py tools/protein_mpnn_wrapper_placeholder.py
cp tools/netmhcii_runner.py tools/netmhcii_runner_placeholder.py
cp tools/rosetta_interface_analyzer.py tools/rosetta_interface_analyzer_placeholder.py
```

### 2. 替换实现

```bash
# 替换为真实实现
cp tools/alphafold3_runner_real.py tools/alphafold3_runner.py
cp tools/protein_mpnn_wrapper_real.py tools/protein_mpnn_wrapper.py
cp tools/netmhcii_runner_real.py tools/netmhcii_runner.py
cp tools/rosetta_interface_analyzer_real.py tools/rosetta_interface_analyzer.py
```

### 3. 验证实现

```python
# 测试每个工具
from tools.alphafold3_runner import predict_structure_and_score
from tools.protein_mpnn_wrapper import generate_mutants
from tools.netmhcii_runner import predict_epitopes_with_netmhcii
from tools.rosetta_interface_analyzer import analyze_interface

# 运行测试
print("测试 AlphaFold3...")
# 测试代码

print("测试 ProteinMPNN...")
# 测试代码

print("测试 NetMHCIIpan...")
# 测试代码

print("测试 Rosetta...")
# 测试代码
```

## 注意事项

### 1. 错误处理

```python
# 添加适当的错误处理
try:
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
    if result.returncode != 0:
        raise RuntimeError(f"工具执行失败: {result.stderr}")
except subprocess.TimeoutExpired:
    raise RuntimeError("工具执行超时")
except Exception as e:
    raise RuntimeError(f"工具执行错误: {e}")
```

### 2. 输出解析

```python
# 确保输出解析的健壮性
def parse_output(output_file: str) -> List[Dict]:
    """解析工具输出文件"""
    results = []
    try:
        with open(output_file, 'r') as f:
            lines = f.readlines()
            for line in lines:
                if line.strip() and not line.startswith('#'):
                    # 解析逻辑
                    pass
    except Exception as e:
        logging.error(f"解析输出文件失败: {e}")
    return results
```

### 3. 资源管理

```python
# 管理临时文件和资源
import tempfile
import shutil

def cleanup_temp_files(temp_dir: str):
    """清理临时文件"""
    try:
        shutil.rmtree(temp_dir)
    except Exception as e:
        logging.warning(f"清理临时文件失败: {e}")
```

## 测试和验证

### 1. 单元测试

```python
# 为每个工具编写单元测试
import unittest

class TestAlphaFold3Runner(unittest.TestCase):
    def test_predict_structure_and_score(self):
        # 测试代码
        pass

class TestProteinMPNNWrapper(unittest.TestCase):
    def test_generate_mutants(self):
        # 测试代码
        pass
```

### 2. 集成测试

```python
# 测试整个管道
def test_full_pipeline():
    """测试完整的免疫原性优化管道"""
    # 测试代码
    pass
```

### 3. 性能测试

```python
# 测试性能
import time

def benchmark_tool(tool_func, *args, **kwargs):
    """基准测试工具性能"""
    start_time = time.time()
    result = tool_func(*args, **kwargs)
    end_time = time.time()
    print(f"执行时间: {end_time - start_time:.2f} 秒")
    return result
```

## 部署和维护

### 1. 版本控制

```bash
# 提交真实实现
git add tools/
git commit -m "实现真实工具调用"
git push origin main
```

### 2. 文档更新

```markdown
# 更新 README.md
- 添加工具安装说明
- 更新使用示例
- 添加故障排除指南
```

### 3. 持续集成

```yaml
# 添加 CI/CD 配置
name: Test Real Tools
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Test tools
        run: python -m pytest tests/
```

## 总结

实现真实工具调用需要：

1. **替换占位符**: 将所有占位符实现替换为真实的工具调用
2. **错误处理**: 添加适当的错误处理和超时机制
3. **输出解析**: 实现健壮的输出解析逻辑
4. **资源管理**: 管理临时文件和系统资源
5. **测试验证**: 编写全面的测试用例
6. **文档更新**: 更新相关文档和说明

完成这些步骤后，免疫原性优化管道就能够真正运行，为用户提供实际的免疫原性调节功能。
