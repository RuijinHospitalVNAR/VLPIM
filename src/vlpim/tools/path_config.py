#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
路径配置文件

这个文件用于配置所有外部工具的路径，避免在代码中硬编码路径。
"""

import os
from pathlib import Path

class ToolPaths:
    """外部工具路径配置类"""
    
    def __init__(self):
        """初始化工具路径"""
        self._load_paths()
    
    def _load_paths(self):
        """从环境变量或默认位置加载工具路径"""
        
        # AlphaFold3 路径
        self.ALPHAFOLD3_PATH = os.getenv('ALPHAFOLD3_PATH', self._find_alphafold3())
        
        # ProteinMPNN 路径
        self.PROTEINMPNN_PATH = os.getenv('PROTEINMPNN_PATH', self._find_proteinmpnn())
        
        # NetMHCIIpan 路径
        self.NETMHCIIPAN_PATH = os.getenv('NETMHCIIPAN_PATH', self._find_netmhcii())
        
        # Rosetta 路径
        self.ROSETTA_PATH = os.getenv('ROSETTA_PATH', self._find_rosetta())
        
        # 用户输入路径
        self.USER_EPITOPES_PATH = os.getenv('USER_EPITOPES_PATH', '')
        
        # 模型权重路径
        self.PROTEINMPNN_MODEL_WEIGHTS = os.getenv(
            'PROTEINMPNN_MODEL_WEIGHTS', 
            os.path.join(self.PROTEINMPNN_PATH, 'model_weights') if self.PROTEINMPNN_PATH else ''
        )
        
        self.ALPHAFOLD3_MODEL_WEIGHTS = os.getenv(
            'ALPHAFOLD3_MODEL_WEIGHTS',
            os.path.join(self.ALPHAFOLD3_PATH, 'model_weights') if self.ALPHAFOLD3_PATH else ''
        )
    
    def _find_alphafold3(self) -> str:
        """自动查找 AlphaFold3 路径"""
        possible_paths = [
            "/opt/alphafold3",
            "/usr/local/alphafold3",
            "/home/user/alphafold3",
            "C:\\alphafold3",
            "C:\\Program Files\\alphafold3"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        # 尝试在 PATH 中找到
        try:
            import subprocess
            result = subprocess.run(['which', 'alphafold3'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                return os.path.dirname(result.stdout.strip())
        except:
            pass
        
        return ""
    
    def _find_proteinmpnn(self) -> str:
        """自动查找 ProteinMPNN 路径"""
        possible_paths = [
            "/opt/ProteinMPNN",
            "/usr/local/ProteinMPNN",
            "/home/user/ProteinMPNN"
        ]
        
        for path in possible_paths:
            if os.path.exists(path) and os.path.exists(os.path.join(path, 'protein_mpnn.py')):
                return path
        
        return ""
    
    def _find_netmhcii(self) -> str:
        """自动查找 NetMHCIIpan 路径"""
        possible_paths = [
            "/opt/netMHCIIpan",
            "/usr/local/netMHCIIpan",
            "/home/user/netMHCIIpan"
        ]
        
        for path in possible_paths:
            if os.path.exists(path) and os.path.exists(os.path.join(path, 'netMHCIIpan')):
                return path
        
        # 尝试在 PATH 中找到
        try:
            import subprocess
            result = subprocess.run(['which', 'netMHCIIpan'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                return os.path.dirname(result.stdout.strip())
        except:
            pass
        
        return ""
    
    def _find_rosetta(self) -> str:
        """自动查找 Rosetta 路径"""
        possible_paths = [
            "/opt/rosetta",
            "/usr/local/rosetta",
            "/home/user/rosetta"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                # 查找 interface_analyzer
                interface_analyzer_path = os.path.join(path, "main", "source", "bin", "interface_analyzer")
                if os.path.exists(interface_analyzer_path):
                    return path
        
        return ""
    
    def get_alphafold3_command(self) -> str:
        """获取 AlphaFold3 命令"""
        if self.ALPHAFOLD3_PATH:
            return os.path.join(self.ALPHAFOLD3_PATH, "alphafold3")
        return "alphafold3"
    
    def get_proteinmpnn_command(self) -> str:
        """获取 ProteinMPNN 命令"""
        if self.PROTEINMPNN_PATH:
            return os.path.join(self.PROTEINMPNN_PATH, "protein_mpnn_run.py")
        return "protein_mpnn_run.py"
    
    def get_model_weights_path(self) -> str:
        """Get AlphaFold3 model weights path."""
        if self.ALPHAFOLD3_PATH:
            return os.path.join(self.ALPHAFOLD3_PATH, "models")
        return ""
    
    def get_netmhcii_command(self) -> str:
        """获取 NetMHCIIpan 命令"""
        if self.NETMHCIIPAN_PATH:
            return os.path.join(self.NETMHCIIPAN_PATH, "netMHCIIpan")
        return "netMHCIIpan"
    
    def get_interface_analyzer_command(self) -> str:
        """获取 interface_analyzer 命令"""
        if self.ROSETTA_PATH:
            return os.path.join(self.ROSETTA_PATH, "main", "source", "bin", "interface_analyzer")
        return "interface_analyzer"
    
    def validate_paths(self) -> dict:
        """验证所有路径是否可用"""
        validation_results = {
            'alphafold3': {
                'path': self.ALPHAFOLD3_PATH,
                'command': self.get_alphafold3_command(),
                'available': self._check_command_available(self.get_alphafold3_command())
            },
            'proteinmpnn': {
                'path': self.PROTEINMPNN_PATH,
                'command': self.get_proteinmpnn_command(),
                'available': self._check_command_available(self.get_proteinmpnn_command())
            },
            'netmhcii': {
                'path': self.NETMHCIIPAN_PATH,
                'command': self.get_netmhcii_command(),
                'available': self._check_command_available(self.get_netmhcii_command())
            },
            'rosetta': {
                'path': self.ROSETTA_PATH,
                'command': self.get_interface_analyzer_command(),
                'available': self._check_command_available(self.get_interface_analyzer_command())
            }
        }
        
        return validation_results
    
    def _check_command_available(self, command: str) -> bool:
        """检查命令是否可用"""
        try:
            import subprocess
            result = subprocess.run(['which', command.split()[0]], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
    
    def print_paths(self):
        """打印所有路径信息"""
        print("=== 工具路径配置 ===")
        print(f"AlphaFold3 路径: {self.ALPHAFOLD3_PATH}")
        print(f"ProteinMPNN 路径: {self.PROTEINMPNN_PATH}")
        print(f"NetMHCIIpan 路径: {self.NETMHCIIPAN_PATH}")
        print(f"Rosetta 路径: {self.ROSETTA_PATH}")
        print(f"IEDB API 密钥: {'已设置' if self.IEDB_API_KEY else '未设置'}")
        print(f"ProteinMPNN 模型权重: {self.PROTEINMPNN_MODEL_WEIGHTS}")
        print(f"AlphaFold3 模型权重: {self.ALPHAFOLD3_MODEL_WEIGHTS}")
        
        print("\n=== 工具可用性检查 ===")
        validation = self.validate_paths()
        for tool, info in validation.items():
            status = "✓ 可用" if info['available'] else "✗ 不可用"
            print(f"{tool.upper()}: {status} ({info['command']})")

# 创建全局路径配置实例
tool_paths = ToolPaths()

# 导出常用函数
def get_alphafold3_path():
    return tool_paths.ALPHAFOLD3_PATH

def get_proteinmpnn_path():
    return tool_paths.PROTEINMPNN_PATH

def get_netmhcii_path():
    return tool_paths.NETMHCIIPAN_PATH

def get_rosetta_path():
    return tool_paths.ROSETTA_PATH

def get_proteinmpnn_model_weights():
    return tool_paths.PROTEINMPNN_MODEL_WEIGHTS

def get_alphafold3_model_weights():
    return tool_paths.ALPHAFOLD3_MODEL_WEIGHTS

def get_iedb_api_key():
    return tool_paths.IEDB_API_KEY

if __name__ == "__main__":
    # 测试路径配置
    tool_paths.print_paths()
