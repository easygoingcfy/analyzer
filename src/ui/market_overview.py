from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QGroupBox, QGridLayout, QFrame)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QPalette, QColor
from src.data.stock_data import data_provider
from src.utils.logger import get_logger

logger = get_logger(__name__)

class MarketOverviewWidget(QWidget):
    """大盘概览组件"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.refresh_data()
        
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        
        # 标题
        title_label = QLabel("大盘概览")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # 大盘指数组
        self.indices_group = QGroupBox("主要指数")
        self.setup_indices_layout()
        layout.addWidget(self.indices_group)
        
        # 市场统计组
        self.stats_group = QGroupBox("市场统计")
        self.setup_stats_layout()
        layout.addWidget(self.stats_group)
        
        # 添加弹性空间
        layout.addStretch()
        
    def setup_indices_layout(self):
        """设置指数布局"""
        layout = QVBoxLayout(self.indices_group)
        layout.setSpacing(5)
        
        # 指数数据字典
        self.index_labels = {}
        
        indices = ['上证指数', '深证成指', '创业板指', '科创50']
        
        for index_name in indices:
            # 创建指数显示框架
            frame = QFrame()
            frame.setFrameStyle(QFrame.Shape.Box)
            frame.setLineWidth(1)
            
            frame_layout = QVBoxLayout(frame)
            frame_layout.setContentsMargins(8, 5, 8, 5)
            frame_layout.setSpacing(2)
            
            # 指数名称
            name_label = QLabel(index_name)
            name_label.setFont(QFont("Microsoft YaHei", 9, QFont.Weight.Bold))
            frame_layout.addWidget(name_label)
            
            # 指数价格和涨跌
            price_layout = QHBoxLayout()
            
            price_label = QLabel("--")
            price_label.setFont(QFont("Microsoft YaHei", 10, QFont.Weight.Bold))
            price_layout.addWidget(price_label)
            
            change_label = QLabel("--")
            change_label.setFont(QFont("Microsoft YaHei", 8))
            price_layout.addWidget(change_label)
            
            price_layout.addStretch()
            frame_layout.addLayout(price_layout)
            
            # 保存标签引用
            self.index_labels[index_name] = {
                'price': price_label,
                'change': change_label
            }
            
            layout.addWidget(frame)
    
    def setup_stats_layout(self):
        """设置统计布局"""
        layout = QGridLayout(self.stats_group)
        layout.setSpacing(8)
        
        # 统计项目
        stats_items = [
            ('上涨家数', '--'),
            ('下跌家数', '--'),
            ('平盘家数', '--'),
            ('涨停家数', '--'),
            ('跌停家数', '--'),
            ('总成交额', '--')
        ]
        
        self.stats_labels = {}
        
        for i, (label_text, default_value) in enumerate(stats_items):
            row = i // 2
            col = (i % 2) * 2
            
            # 标签
            label = QLabel(label_text + ":")
            label.setFont(QFont("Microsoft YaHei", 8))
            layout.addWidget(label, row, col)
            
            # 数值
            value_label = QLabel(default_value)
            value_label.setFont(QFont("Microsoft YaHei", 8, QFont.Weight.Bold))
            layout.addWidget(value_label, row, col + 1)
            
            self.stats_labels[label_text] = value_label
    
    def refresh_data(self):
        """刷新数据"""
        try:
            logger.debug("开始刷新大盘数据...")
            
            # 获取大盘数据
            market_data = data_provider.get_market_data()
            
            if not market_data:
                logger.warning("未获取到大盘数据")
                self._show_no_data_message()
                return
            
            # 更新指数数据
            for index_name, data in market_data.items():
                if index_name in self.index_labels:
                    labels = self.index_labels[index_name]
                    
                    # 更新价格
                    price = data.get('现价', 0)
                    labels['price'].setText(f"{price:.2f}")
                    
                    # 更新涨跌幅
                    change_pct = data.get('涨跌幅', 0)
                    change_amount = data.get('涨跌额', 0)
                    
                    change_text = f"{change_pct:+.2f}% ({change_amount:+.2f})"
                    labels['change'].setText(change_text)
                    
                    # 设置颜色
                    if change_pct > 0:
                        color = "red"
                    elif change_pct < 0:
                        color = "green"
                    else:
                        color = "black"
                    
                    labels['price'].setStyleSheet(f"color: {color}; font-weight: bold;")
                    labels['change'].setStyleSheet(f"color: {color}; font-weight: bold;")
            
            # 更新统计数据
            self._update_market_stats()
            
            logger.debug("大盘数据更新完成")
            
        except Exception as e:
            logger.error(f"更新大盘数据失败: {e}")
            self._show_error_message(str(e))
            
    def _show_no_data_message(self):
        """显示无数据消息"""
        for index_name in self.index_labels:
            labels = self.index_labels[index_name]
            labels['price'].setText("--")
            labels['change'].setText("数据获取中...")
            labels['price'].setStyleSheet("color: gray;")
            labels['change'].setStyleSheet("color: gray;")
            
    def _show_error_message(self, error_msg: str):
        """显示错误消息"""
        for index_name in self.index_labels:
            labels = self.index_labels[index_name]
            labels['price'].setText("--")
            labels['change'].setText("连接异常")
            labels['price'].setStyleSheet("color: red;")
            labels['change'].setStyleSheet("color: red;")
            
    def _update_market_stats(self):
        """更新市场统计数据"""
        try:
            # 这里应该从数据源获取真实的市场统计数据
            # 目前使用模拟数据
            import random
            
            total_stocks = 4800
            up_count = random.randint(1500, 2500)
            down_count = random.randint(1500, 2500)
            flat_count = total_stocks - up_count - down_count
            
            stats_data = {
                '上涨家数': f"{up_count}",
                '下跌家数': f"{down_count}",
                '平盘家数': f"{flat_count}",
                '涨停家数': f"{random.randint(10, 100)}",
                '跌停家数': f"{random.randint(5, 50)}",
                '总成交额': f"{random.randint(8000, 15000)}亿"
            }
            
            for stat_name, value in stats_data.items():
                if stat_name in self.stats_labels:
                    label = self.stats_labels[stat_name]
                    label.setText(value)
                    
                    # 设置上涨下跌颜色
                    if stat_name == '上涨家数':
                        label.setStyleSheet("color: red;")
                    elif stat_name == '下跌家数':
                        label.setStyleSheet("color: green;")
                    else:
                        label.setStyleSheet("color: black;")
                        
        except Exception as e:
            logger.error(f"更新市场统计失败: {e}")
