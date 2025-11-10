# VLPIM Pipeline Overview（VLPIM 流水线概览）

## Architecture（整体架构）
```mermaid
flowchart LR
    A[Input FASTA<br/>Input PDB<br/>输入序列与结构] --> B[PipelineConfig<br/>Logging Setup<br/>参数与日志初始化]
    B --> C{Epitope Source?<br/>抗原位点来源？}
    C -->|User CSV<br/>用户文件| D[Load & Validate<br/>User Epitopes<br/>加载并校验用户抗原位点]
    C -->|NetMHCIIpan| E[Run NetMHCIIpan<br/>Parse Output<br/>执行 NetMHCIIpan 并解析输出]
    E --> F[Filter & Extend<br/>Epitope Cores<br/>筛选并扩展核心序列]
    D --> F
    F --> G[ProteinMPNN<br/>Mutant Generation<br/>ProteinMPNN 生成突变体]
    G --> H[NetMHCIIpan<br/>MHC-II Evaluation<br/>NetMHCIIpan 评估 MHC-II]
    H --> I[Immunogenicity Scoring<br/>Candidate Ranking<br/>免疫原性评分与排序]
    I --> J[AlphaFold3 Prediction<br/>PDB Collection<br/>AlphaFold3 结构预测]
    J --> K[PyMOL / Iterative / BioPython / Kabsch<br/>RMSD Calculation<br/>RMSD 计算（优先级链路）]
    K --> L[Rosetta Interface Analysis<br/>(Placeholder)<br/>Rosetta 界面分析（预留）]
    L --> M[Final Ranking & Reports<br/>最终排序与报告输出]
    M --> N[Results Directory<br/>Logs · CSVs · FASTA<br/>结果目录与产物]
```

## Summary（摘要）
- **Entry point / 入口**：`src/vlpim/immunogenicity_optimization_pipeline.py` 负责调度全流程，可通过 `python -m vlpim` 或直接运行脚本调用。
- **External tooling / 外部工具**：依赖 ProteinMPNN、NetMHCIIpan、AlphaFold3、Rosetta；路径由环境变量或 `src/vlpim/tools/path_config.py` 自动解析。
- **Outputs / 产出**：所有结果保存在 `results/` 目录（配置快照、日志、抗原位点表、突变序列 FASTA、MHC 评分、最终排名）。

## Stage-by-Stage Detail（分阶段详解）

### 1. Configuration & Initialization（配置与初始化）
- CLI 参数映射到 `PipelineConfig`，设定 HLA 等位基因、采样温度、阈值等默认值。
- 日志同时输出到控制台与 `results/pipeline.log`；当前配置序列化到 `results/config.json` 以便复现。

### 2. Epitope Acquisition（抗原位点获取）
- **用户提供 CSV**：字段需包含 `sequence/start/end`，由 `_load_user_epitopes` 验证。
- **NetMHCIIpan 预测**：`tools/netmhcii_runner.predict_epitopes_with_netmhcii` 调用外部工具，现已支持标准与宽表输出。
- 按 `%Rank_EL`/`Rank` 分类强弱结合，挑选核心序列，并利用 `_extend_core_sequences` 按 FASTA 上下文延展至目标长度。
- 输出：`results/epitope_predictions.csv`。

### 3. Mutant Sequence Design（突变序列设计）
- `tools/protein_mpnn_wrapper.generate_mutants` 基于筛选的抗原位点与原始 PDB 生成突变体，支持减免/增强两种模式。
- 输出突变序列 FASTA：`results/mutant_sequences.fasta`。

### 4. MHC-II Binding Evaluation（MHC-II 亲和力评估）
- 从每条突变 VLP 中提取突变抗原位点，写入 `mutant_epitopes.fasta` 并作为 NetMHCIIpan 输入。
- `evaluate_mhc_affinity` 以表位 ID（`mutant_xxxx|epitope_yyyy`）返回 `Rank_*` / `IC50_*`；`compute_immunogenicity_scores` 将每个等位基因的 IC50 做排名归一化（与 `run_ic50_sum.py` 一致），再按突变体求和。
- 无论 `mode=reduce` 还是 `mode=enhance`，最终的 `Overall_Immunogenicity_Score` 越小越好：降低模式通过“100-归一化”反转，增强模式保持原值，后续统一按最小值筛选。
- 保存两份表格：`results/mhc_binding_epitope_scores.csv`（逐位点）与 `results/mhc_binding_scores.csv`（同一突变体多表位得分相加，用于排序）。

### 5. Structure Prediction & RMSD（结构预测与 RMSD）
- `tools/alphafold3_wrapper.predict_structure` 调用 AlphaFold3，收集每个候选的 PDB（默认 `ranked_0.pdb`）。
- RMSD 流程 `calculate_rmsd` 优先级链路：PyMOL `align`（API/CLI） → Bio.PDB 迭代剪枝 → BioPython Superimposer → Kabsch。
- 将 RMSD 写入候选表；结果保存为 `results/final_ranked_candidates.csv`。
- Rosetta 界面分析函数留有空位，未来可接入 `analyze_interface`。

### 6. Completion（收尾）
- `run_pipeline` 返回包含抗原位点 DataFrame、突变列表、MHC 评分、最终候选、运行时间的字典。
- 日志总结列出生成的文件路径，方便快速定位。

## Execution Checklist（执行清单）
1. 安装外部工具并设置环境变量：`PROTEIN_MPNN_PATH`、`NETMHCIIPAN_PATH`、`ALPHAFOLD3_PATH`、`ROSETTA_PATH`。
2. 使用 `environment.yml` 或 `requirements.txt` 创建 Python 环境。
3. 运行流水线示例：
   ```bash
   python -m vlpim \
       --fasta protein.fasta \
       --pdb protein.pdb \
       --mode reduce \
       --output-dir results
   ```
4. 检查 `results/` 目录，关注 `pipeline.log` 中的警告或错误。

## Example Commands（命令示例）

### 环境与配置验证
```bash
python -m vlpim config      # 输出当前配置（含外部工具路径）
python -m vlpim validate    # 校验 NetMHCIIpan、ProteinMPNN 等是否可用
```

### 运行减免免疫原性示例
```bash
python -m vlpim \
    --fasta data/vlp_sequence.fasta \
    --pdb data/vlp_structure.pdb \
    --mode reduce \
    --output-dir results_reduce \
    --log-level INFO
```

### 运行增强免疫原性示例（指定自定义抗原位点）
```bash
python -m vlpim \
    --fasta data/vlp_sequence.fasta \
    --pdb data/vlp_structure.pdb \
    --mode enhance \
    --epitopes data/custom_epitopes.csv \
    --max-candidates 20 \
    --samples-per-temp 50 \
    --temperatures 0.1 0.3 0.6 \
    --output-dir results_enhance \
    --log-level DEBUG
```

### 单独运行 RMSD 工具（`scripts/run_rmsd.py`）
```bash
python scripts/run_rmsd.py \
    --reference reference.pdb \
    --candidate-dir ./alphafold_outputs \
    --output rmsd_summary.csv \
    --method biopython
```

### 快速查看输出
```bash
ls results
tail -n 20 results/pipeline.log
head -n 5 results/final_ranked_candidates.csv
```

> **提示**：路径需根据实际情况调整；确保外部工具已安装并加入环境变量。

## Recent Enhancements（近期改进）
- NetMHCIIpan 解析器现已支持宽表格式，与独立分析脚本保持一致。
- RMSD 计算从占位符升级为 PyMOL → 迭代剪枝 → BioPython → Kabsch 的完整链路。
- 流水线在具备序列与工具条件时，将自动尝试 AlphaFold3 预测与 RMSD 评分。
