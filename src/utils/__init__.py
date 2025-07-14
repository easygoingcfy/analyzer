import logging
import os
from datetime import datetime

def setup_logger():
    """设置日志配置"""
    # 创建logs目录
    logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")
    os.makedirs(logs_dir, exist_ok=True)
    
    # 配置日志格式
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # 配置根日志器
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.FileHandler(
                os.path.join(logs_dir, f'app_{datetime.now().strftime("%Y%m%d")}.log'),
                encoding='utf-8'
            ),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)

def get_logger(name):
    """获取指定名称的日志器"""
    return logging.getLogger(name)
