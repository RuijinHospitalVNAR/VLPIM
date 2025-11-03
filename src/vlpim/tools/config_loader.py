#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一配置文件加载器

这个模块用于加载和管理统一配置文件，提供所有参数、环境和路径的集中管理。
"""

import os
import yaml
import json
from pathlib import Path
from typing import Dict, Any, Optional
import logging

class ConfigLoader:
    """统一配置加载器"""
    
    def __init__(self, config_file: str = "config_unified.yaml"):
        """
        初始化配置加载器
        
        Args:
            config_file: 配置文件路径
        """
        self.config_file = config_file
        self.config = {}
        self.logger = logging.getLogger(__name__)
        self._load_config()
    
    def _load_config(self):
        """加载配置文件"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = yaml.safe_load(f)
                self.logger.info(f"已加载配置文件: {self.config_file}")
            else:
                self.logger.warning(f"配置文件不存在: {self.config_file}，使用默认配置")
                self._create_default_config()
        except Exception as e:
            self.logger.error(f"加载配置文件失败: {e}")
            self._create_default_config()
    
    def _create_default_config(self):
        """创建默认配置"""
        self.config = {
            'tools': {
                'alphafold3': {
                    'path': '',
                    'model_weights': '',
                    'executable': 'alphafold3'
                },
                'proteinmpnn': {
                    'path': '',
                    'model_weights': '',
                    'executable': 'protein_mpnn.py'
                },
                'netmhcii': {
                    'path': '',
                    'executable': 'netMHCIIpan'
                },
                'rosetta': {
                    'path': '',
                    'executable': 'interface_analyzer',
                    'bin_path': 'main/source/bin'
                }
            },
            'user_input': {
                'epitopes_path': ''
            },
            'pipeline': {
                'basic': {
                    'default_output_dir': 'results',
                    'default_log_level': 'INFO',
                    'max_parallel_jobs': 4
                },
                'proteinmpnn': {
                    'default_temperatures': [0.1, 0.3, 0.5],
                    'default_samples_per_temp': 20,
                    'batch_size': 1,
                    'timeout': 1800
                },
                'alphafold3': {
                    'default_rmsd_threshold': 2.0,
                    'max_template_date': '2024-01-01',
                    'num_multimer_predictions_per_model': 1,
                    'timeout': 7200
                },
                'netmhcii': {
                    'default_hla_alleles': [
                        'DRB1*01:01', 'DRB1*03:01', 'DRB1*04:01', 'DRB1*07:01',
                        'DRB1*08:01', 'DRB1*11:01', 'DRB1*13:01', 'DRB1*15:01'
                    ],
                    'timeout': 1800
                },
                'rosetta': {
                    'default_dg_dsasa_threshold': -0.5,
                    'default_buns_threshold': 5,
                    'default_packstat_threshold': 0.6,
                    'timeout': 300
                },
                'ranking': {
                    'max_candidates': 10,
                    'ranking_criteria': ['RMSD', 'dG_dSASA', 'packstat', 'BUNS'],
                    'ranking_ascending': [True, True, False, True]
                }
            },
            'system': {
                'resources': {
                    'max_memory_gb': 32,
                    'max_cpu_cores': 16,
                    'use_gpu': False,
                    'cuda_device': '0'
                },
                'temp': {
                    'temp_dir': '/tmp',
                    'cleanup_temp_files': True
                },
                'logging': {
                    'log_file': 'pipeline.log',
                    'max_log_size_mb': 100,
                    'backup_count': 5,
                    'log_format': '%(asctime)s - %(levelname)s - %(message)s'
                }
            },
            'advanced': {
                'cache': {
                    'enable_cache': True,
                    'cache_dir': 'cache',
                    'cache_expiry_hours': 24
                },
                'retry': {
                    'max_retries': 3,
                    'retry_delay_seconds': 5,
                    'exponential_backoff': True
                },
                'performance': {
                    'enable_parallel_processing': True,
                    'chunk_size': 10,
                    'memory_efficient_mode': False
                }
            }
        }
    
    def get_tool_path(self, tool_name: str) -> str:
        """获取工具路径"""
        tool_config = self.config.get('tools', {}).get(tool_name, {})
        path = tool_config.get('path', '')
        
        # 优先使用环境变量
        env_var = f"{tool_name.upper()}_PATH"
        env_path = os.getenv(env_var, '')
        if env_path:
            return env_path
        
        return path
    
    def get_tool_executable(self, tool_name: str) -> str:
        """获取工具可执行文件路径"""
        tool_config = self.config.get('tools', {}).get(tool_name, {})
        executable = tool_config.get('executable', '')
        path = self.get_tool_path(tool_name)
        
        if path:
            if tool_name == 'rosetta':
                bin_path = tool_config.get('bin_path', 'main/source/bin')
                return os.path.join(path, bin_path, executable)
            else:
                return os.path.join(path, executable)
        
        return executable
    
    def get_model_weights_path(self, tool_name: str) -> str:
        """获取模型权重路径"""
        tool_config = self.config.get('tools', {}).get(tool_name, {})
        model_weights = tool_config.get('model_weights', '')
        
        # 优先使用环境变量
        env_var = f"{tool_name.upper()}_MODEL_WEIGHTS"
        env_path = os.getenv(env_var, '')
        if env_path:
            return env_path
        
        return model_weights
    
    def get_user_input_path(self, input_type: str) -> str:
        """获取用户输入文件路径"""
        user_input_config = self.config.get('user_input', {})
        return user_input_config.get(f'{input_type}_path', '')
    
    def get_pipeline_param(self, section: str, param: str, default: Any = None) -> Any:
        """获取管道参数"""
        section_config = self.config.get('pipeline', {}).get(section, {})
        return section_config.get(param, default)
    
    def get_system_param(self, section: str, param: str, default: Any = None) -> Any:
        """获取系统参数"""
        section_config = self.config.get('system', {}).get(section, {})
        return section_config.get(param, default)
    
    def get_advanced_param(self, section: str, param: str, default: Any = None) -> Any:
        """获取高级参数"""
        section_config = self.config.get('advanced', {}).get(section, {})
        return section_config.get(param, default)
    
    def update_config(self, updates: Dict[str, Any]):
        """更新配置"""
        self.config.update(updates)
        self._save_config()
    
    def _save_config(self):
        """保存配置到文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True)
            self.logger.info(f"配置已保存到: {self.config_file}")
        except Exception as e:
            self.logger.error(f"保存配置文件失败: {e}")
    
    def export_to_env_file(self, env_file: str = ".env"):
        """导出配置到环境变量文件"""
        env_lines = []
        env_lines.append("# 免疫原性优化管道 - 环境变量配置")
        env_lines.append("# 由 config_unified.yaml 自动生成")
        env_lines.append("")
        
        # 工具路径
        for tool_name in ['alphafold3', 'proteinmpnn', 'netmhcii', 'rosetta']:
            path = self.get_tool_path(tool_name)
            if path:
                env_lines.append(f"export {tool_name.upper()}_PATH=\"{path}\"")
        
        # 模型权重路径
        for tool_name in ['alphafold3', 'proteinmpnn']:
            model_weights = self.get_model_weights_path(tool_name)
            if model_weights:
                env_lines.append(f"export {tool_name.upper()}_MODEL_WEIGHTS=\"{model_weights}\"")
        
        # API 密钥
        iedb_api_key = self.get_api_key('iedb')
        if iedb_api_key:
            env_lines.append(f"export IEDB_API_KEY=\"{iedb_api_key}\"")
        
        # 系统参数
        output_dir = self.get_pipeline_param('basic', 'default_output_dir')
        if output_dir:
            env_lines.append(f"export DEFAULT_OUTPUT_DIR=\"{output_dir}\"")
        
        log_level = self.get_pipeline_param('basic', 'default_log_level')
        if log_level:
            env_lines.append(f"export DEFAULT_LOG_LEVEL=\"{log_level}\"")
        
        try:
            with open(env_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(env_lines))
            self.logger.info(f"环境变量文件已导出到: {env_file}")
        except Exception as e:
            self.logger.error(f"导出环境变量文件失败: {e}")
    
    def print_config_summary(self):
        """打印配置摘要"""
        print("=== 统一配置摘要 ===")
        print(f"配置文件: {self.config_file}")
        print()
        
        print("工具路径:")
        for tool_name in ['alphafold3', 'proteinmpnn', 'netmhcii', 'rosetta']:
            path = self.get_tool_path(tool_name)
            status = "[OK] 已配置" if path else "[NOT SET] 未配置"
            print(f"  {tool_name.upper()}: {status} ({path})")
        
        print()
        print("模型权重:")
        for tool_name in ['alphafold3', 'proteinmpnn']:
            model_weights = self.get_model_weights_path(tool_name)
            status = "[OK] 已配置" if model_weights else "[NOT SET] 未配置"
            print(f"  {tool_name.upper()}: {status} ({model_weights})")
        
        print()
        print("用户输入:")
        epitopes_path = self.get_user_input_path('epitopes')
        status = "[OK] 已配置" if epitopes_path else "[NOT SET] 未配置"
        print(f"  用户抗原位点: {status}")
        
        print()
        print("管道参数:")
        print(f"  默认输出目录: {self.get_pipeline_param('basic', 'default_output_dir')}")
        print(f"  默认日志级别: {self.get_pipeline_param('basic', 'default_log_level')}")
        print(f"  最大候选数: {self.get_pipeline_param('ranking', 'max_candidates')}")
        print(f"  RMSD 阈值: {self.get_pipeline_param('alphafold3', 'default_rmsd_threshold')}")

# 创建全局配置实例
config_loader = ConfigLoader()

# 导出常用函数
def get_tool_path(tool_name: str) -> str:
    return config_loader.get_tool_path(tool_name)

def get_tool_executable(tool_name: str) -> str:
    return config_loader.get_tool_executable(tool_name)

def get_model_weights_path(tool_name: str) -> str:
    return config_loader.get_model_weights_path(tool_name)

def get_user_input_path(input_type: str) -> str:
    return config_loader.get_user_input_path(input_type)

def get_pipeline_param(section: str, param: str, default: Any = None) -> Any:
    return config_loader.get_pipeline_param(section, param, default)

if __name__ == "__main__":
    # 测试配置加载器
    config_loader.print_config_summary()
    
    # 导出环境变量文件
    config_loader.export_to_env_file()
