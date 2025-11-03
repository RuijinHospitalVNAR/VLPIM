#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VLPIM NetMHCIIpan Analysis Module
Based on the methodology from 总分析脚本.py
"""

import pandas as pd
import numpy as np
import re
from typing import List, Dict, Tuple
import logging

class NetMHCIIpanAnalyzer:
    """NetMHCIIpan结果分析器，基于总分析脚本的方法"""
    
    def __init__(self):
        self.logger = self._setup_logger()
    
    def _setup_logger(self):
        """设置日志"""
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        return logging.getLogger(__name__)
    
    def parse_netmhcii_output(self, file_content: str) -> pd.DataFrame:
        """
        解析NetMHCIIpan输出文件
        
        Args:
            file_content: NetMHCIIpan结果文件内容
            
        Returns:
            解析后的DataFrame
        """
        try:
            lines = file_content.strip().split('\n')
            
            # 提取等位基因名称
            allele_line = lines[0].strip()
            allele_pattern = r'DRB1_\d{4}'
            allele_matches = re.findall(allele_pattern, allele_line)
            alleles = []
            for match in allele_matches:
                code = match.split('_')[1]
                formatted_allele = f"DRB1*{code[:2]}:{code[2:]}"
                alleles.append(formatted_allele)
            
            self.logger.info(f"发现等位基因: {alleles}")
            
            # 解析数据行
            data_rows = []
            for line in lines[2:]:  # 跳过标题行
                line = line.strip()
                if line and not line.startswith('#'):
                    values = line.split('\t')
                    if len(values) >= 10:
                        pos = values[0]
                        peptide = values[1]
                        seq_id = values[2]
                        
                        # 处理每个等位基因的数据
                        allele_start_col = 3
                        cols_per_allele = 8
                        
                        for i, allele in enumerate(alleles):
                            start_idx = allele_start_col + (i * cols_per_allele)
                            
                            if start_idx + 6 < len(values):
                                try:
                                    score = float(values[start_idx + 2]) if values[start_idx + 2] else 0
                                    rank = float(values[start_idx + 3]) if values[start_idx + 3] else 0
                                    score_ba = float(values[start_idx + 4]) if values[start_idx + 4] else 0
                                    nm = float(values[start_idx + 5]) if values[start_idx + 5] else 0
                                    rank_ba = float(values[start_idx + 6]) if values[start_idx + 6] else 0
                                    
                                    row_data = {
                                        'Pos': pos,
                                        'Peptide': peptide,
                                        'Sequence_ID': seq_id,
                                        'Allele': allele,
                                        'Score': score,
                                        'Rank': rank,
                                        'Score_BA': score_ba,
                                        'BA_IC50': nm,  # nM值 - 关键数据
                                        'BA_Rank': rank_ba,
                                        'BA_Raw': score_ba
                                    }
                                    data_rows.append(row_data)
                                except (ValueError, IndexError) as e:
                                    self.logger.warning(f"跳过无效数据 {allele}: {e}")
                                    continue
            
            df = pd.DataFrame(data_rows)
            self.logger.info(f"解析了 {len(df)} 个表位记录")
            self.logger.info(f"发现 {df['Peptide'].nunique()} 个独特肽段")
            self.logger.info(f"发现 {df['Allele'].nunique()} 个HLA等位基因")
            
            return df
            
        except Exception as e:
            self.logger.error(f"解析NetMHCIIpan数据时出错: {e}")
            raise ValueError(f"解析NetMHCIIpan数据失败: {str(e)}")
    
    def calculate_rank_and_score(self, df: pd.DataFrame, col: str) -> pd.DataFrame:
        """
        基于总分析脚本的方法计算排名和评分
        
        Args:
            df: 包含nM值的DataFrame
            col: 要处理的列名（通常是BA_IC50）
            
        Returns:
            添加了Rank和Score列的DataFrame
        """
        # 计算排名（升序，越小排名越高）
        df[f'Rank_{col}'] = df[col].rank(method='average')
        min_rank = df[f'Rank_{col}'].min()
        max_rank = df[f'Rank_{col}'].max()
        
        # 计算评分：升原（免疫原性增强）
        # 公式：((rank - min_rank) / (max_rank - min_rank)) * 100
        df[f'Score_{col}'] = ((df[f'Rank_{col}'] - min_rank) / (max_rank - min_rank)) * 100
        
        self.logger.info(f"为列 {col} 计算了排名和评分")
        self.logger.info(f"排名范围: {min_rank:.2f} - {max_rank:.2f}")
        
        return df
    
    def analyze_immunogenicity(self, df: pd.DataFrame, mode: str = 'enhance') -> pd.DataFrame:
        """
        分析免疫原性，基于总分析脚本的方法
        
        Args:
            df: 解析后的NetMHCIIpan数据
            mode: 'enhance' (升原) 或 'reduce' (降原)
            
        Returns:
            包含免疫原性评分的DataFrame
        """
        try:
            # 按肽段分组
            peptide_groups = df.groupby('Peptide')
            results = []
            
            for peptide, group in peptide_groups:
                self.logger.info(f"分析肽段: {peptide}")
                
                # 为每个等位基因计算排名和评分
                allele_scores = {}
                total_score = 0
                
                for allele in group['Allele'].unique():
                    allele_data = group[group['Allele'] == allele]
                    nm_values = allele_data['BA_IC50'].values
                    
                    if len(nm_values) > 0:
                        # 创建临时DataFrame进行排名计算
                        temp_df = pd.DataFrame({'BA_IC50': nm_values})
                        temp_df = self.calculate_rank_and_score(temp_df, 'BA_IC50')
                        
                        # 获取评分
                        score = temp_df['Score_BA_IC50'].iloc[0]
                        allele_scores[allele] = {
                            'ic50': nm_values[0],
                            'rank': temp_df['Rank_BA_IC50'].iloc[0],
                            'score': score
                        }
                        total_score += score
                
                # 计算平均评分
                avg_score = total_score / len(allele_scores) if allele_scores else 0
                
                # 计算其他统计信息
                ic50_values = group['BA_IC50'].values
                rank_values = group['BA_Rank'].values
                
                peptide_result = {
                    'Peptide': peptide,
                    'Sequence_ID': group['Sequence_ID'].iloc[0],
                    'Total_Score': total_score,
                    'Average_Score': avg_score,
                    'Allele_Count': len(allele_scores),
                    'Min_IC50': np.min(ic50_values),
                    'Max_IC50': np.max(ic50_values),
                    'Avg_IC50': np.mean(ic50_values),
                    'Min_Rank': np.min(rank_values),
                    'Max_Rank': np.max(rank_values),
                    'Avg_Rank': np.mean(rank_values),
                    'Strong_Binders': sum(1 for ic50 in ic50_values if ic50 <= 50),
                    'Moderate_Binders': sum(1 for ic50 in ic50_values if 50 < ic50 <= 500),
                    'Weak_Binders': sum(1 for ic50 in ic50_values if ic50 > 500),
                    'Allele_Scores': allele_scores
                }
                
                results.append(peptide_result)
                self.logger.info(f"肽段 {peptide} 总评分: {total_score:.2f}, 平均评分: {avg_score:.2f}")
            
            # 转换为DataFrame并排序
            results_df = pd.DataFrame(results)
            results_df = results_df.sort_values('Total_Score', ascending=False)
            
            return results_df
            
        except Exception as e:
            self.logger.error(f"分析免疫原性时出错: {e}")
            raise ValueError(f"免疫原性分析失败: {str(e)}")
    
    def generate_analysis_report(self, results_df: pd.DataFrame, original_df: pd.DataFrame) -> Dict:
        """
        生成分析报告
        
        Args:
            results_df: 分析结果DataFrame
            original_df: 原始数据DataFrame
            
        Returns:
            包含分析报告的字典
        """
        try:
            # 基本统计
            total_epitopes = len(original_df)
            unique_peptides = len(results_df)
            alleles_tested = original_df['Allele'].nunique()
            
            # IC50统计
            ic50_values = original_df['BA_IC50'].values
            ic50_stats = {
                'min': float(np.min(ic50_values)),
                'max': float(np.max(ic50_values)),
                'mean': float(np.mean(ic50_values)),
                'median': float(np.median(ic50_values)),
                'std': float(np.std(ic50_values))
            }
            
            # Rank统计
            rank_values = original_df['BA_Rank'].values
            rank_stats = {
                'min': float(np.min(rank_values)),
                'max': float(np.max(rank_values)),
                'mean': float(np.mean(rank_values)),
                'median': float(np.median(rank_values)),
                'std': float(np.std(rank_values))
            }
            
            # 评分统计
            score_values = results_df['Total_Score'].values
            score_stats = {
                'min': float(np.min(score_values)),
                'max': float(np.max(score_values)),
                'mean': float(np.mean(score_values)),
                'median': float(np.median(score_values)),
                'std': float(np.std(score_values))
            }
            
            # 生成报告
            report = {
                'summary': {
                    'total_epitopes': total_epitopes,
                    'unique_peptides': unique_peptides,
                    'alleles_tested': alleles_tested,
                    'analysis_method': 'NetMHCIIpan_Rank_Score_Method',
                    'method_description': '基于nM值排名和评分的免疫原性分析方法'
                },
                'statistics': {
                    'ic50_stats': ic50_stats,
                    'rank_stats': rank_stats,
                    'score_stats': score_stats
                },
                'peptide_results': results_df.to_dict('records'),
                'top_peptides': results_df.head(10).to_dict('records')
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"生成分析报告时出错: {e}")
            raise ValueError(f"生成分析报告失败: {str(e)}")

def analyze_netmhcii_file(file_path: str, mode: str = 'enhance') -> Dict:
    """
    分析NetMHCIIpan文件的便捷函数
    
    Args:
        file_path: NetMHCIIpan结果文件路径
        mode: 'enhance' (升原) 或 'reduce' (降原)
        
    Returns:
        分析结果字典
    """
    analyzer = NetMHCIIpanAnalyzer()
    
    # 读取文件
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 解析数据
    df = analyzer.parse_netmhcii_output(content)
    
    # 分析免疫原性
    results_df = analyzer.analyze_immunogenicity(df, mode)
    
    # 生成报告
    report = analyzer.generate_analysis_report(results_df, df)
    
    return report

if __name__ == "__main__":
    # 示例用法
    print("🧪 VLPIM NetMHCIIpan分析器")
    print("基于总分析脚本.py的方法")
    print("=" * 50)
    
    # 这里可以添加测试代码
    print("分析器已准备就绪，可以分析NetMHCIIpan结果文件")
