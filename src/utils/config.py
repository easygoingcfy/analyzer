import json
import os
from typing import Dict, Any, Optional

class ConfigManager:
    """配置管理器"""
    
    def __init__(self):
        self.config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config")
        os.makedirs(self.config_dir, exist_ok=True)
        
        self.config_file = os.path.join(self.config_dir, "app_config.json")
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        default_config = {
            "ui": {
                "theme": "light",
                "window_size": [1200, 800],
                "window_position": [100, 100],
                "layout_templates": {}
            },
            "data": {
                "update_interval": 1000,  # 毫秒
                "data_sources": {
                    "akshare": True,
                    "tushare": False
                },
                "cache_enabled": True,
                "cache_duration": 300  # 秒
            },
            "strategy": {
                "max_results": 100,
                "saved_strategies": {}
            },
            "stock_pools": {
                "my_stocks": [],
                "watch_list": [],
                "custom_pools": {}
            },
            "display": {
                "columns": [
                    "代码", "名称", "现价", "涨跌幅", "涨跌额", 
                    "成交量", "成交额", "换手率", "市盈率", "市净率"
                ],
                "sort_column": "涨跌幅",
                "sort_order": "desc"
            }
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    saved_config = json.load(f)
                    # 合并默认配置和保存的配置
                    self._merge_config(default_config, saved_config)
                    return default_config
            except Exception as e:
                print(f"加载配置文件失败: {e}")
                return default_config
        else:
            self._save_config(default_config)
            return default_config
    
    def _merge_config(self, default: Dict[str, Any], saved: Dict[str, Any]):
        """递归合并配置"""
        for key, value in saved.items():
            if key in default:
                if isinstance(value, dict) and isinstance(default[key], dict):
                    self._merge_config(default[key], value)
                else:
                    default[key] = value
    
    def _save_config(self, config: Optional[Dict[str, Any]] = None):
        """保存配置到文件"""
        if config is None:
            config = self._config
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"保存配置文件失败: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """设置配置值"""
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        self._save_config()
    
    def save(self):
        """保存当前配置"""
        self._save_config()

# 全局配置管理器实例
config_manager = ConfigManager()
