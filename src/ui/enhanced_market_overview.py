"""
增强版大盘概览组件 - 适配新的上下布局设计
参考同花顺大盘指数显示风格
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QGridLayout, QFrame)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QPalette, QColor
from src.data.stock_data import data_provider
from src.utils.logger import get_logger

logger = get_logger(__name__)

class EnhancedMarketOverviewWidget(QWidget):
    """增强版大盘概览组件"""
    
    def __init__(self):
        super().__init__()
        self.index_cards = {}  # 存储指数卡片
        self.init_ui()
        self.refresh_data()
        
    def init_ui(self):
        """初始化界面 - 水平卡片布局"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        
        # 指数数据映射
        self.indices_info = {
            '上证指数': {'code': '000001', 'color': '#e74c3c'},
            '深证成指': {'code': '399001', 'color': '#3498db'},  
            '创业板指': {'code': '399006', 'color': '#f39c12'},
            '科创50': {'code': '000688', 'color': '#9b59b6'}
        }
        
        # 创建指数卡片
        for index_name, info in self.indices_info.items():
            card = self.create_index_card(index_name, info['color'])
            self.index_cards[index_name] = card
            layout.addWidget(card['widget'], 1)  # 等比例分布
            
    def create_index_card(self, index_name, color):
        """创建指数卡片 - 大尺寸显示"""
        # 主容器
        card_widget = QFrame()
        card_widget.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 2px solid {color};
                border-radius: 12px;
                padding: 8px;
                min-height: 140px;
            }}
            QFrame:hover {{
                border-color: {color};
                background-color: #f8f9fa;
                border-width: 3px;
            }}
        """)
        
        layout = QVBoxLayout(card_widget)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(8)
        
        # 指数名称 - 更大字体
        name_label = QLabel(index_name)
        name_label.setFont(QFont("微软雅黑", 14, QFont.Weight.Bold))
        name_label.setStyleSheet(f"color: {color}; padding: 3px 0;")
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(name_label)
        
        # 当前价格 - 更大字体
        price_label = QLabel("---.--")
        price_label.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        price_label.setStyleSheet("color: #2c3e50; padding: 5px 0;")
        price_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(price_label)
        
        # 涨跌信息容器
        change_container = QWidget()
        change_layout = QVBoxLayout(change_container)
        change_layout.setContentsMargins(0, 0, 0, 0)
        change_layout.setSpacing(3)
        
        # 涨跌额
        change_amount_label = QLabel("±-.--")
        change_amount_label.setFont(QFont("Arial", 13, QFont.Weight.Bold))
        change_amount_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 涨跌幅
        change_pct_label = QLabel("±-.--％")
        change_pct_label.setFont(QFont("Arial", 13, QFont.Weight.Bold))
        change_pct_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        change_layout.addWidget(change_amount_label)
        change_layout.addWidget(change_pct_label)
        layout.addWidget(change_container)
        
        # 成交量信息
        volume_label = QLabel("成交: ---万手")
        volume_label.setFont(QFont("微软雅黑", 10))
        volume_label.setStyleSheet("color: #7f8c8d; padding: 2px 0;")
        volume_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(volume_label)
        
        return {
            'widget': card_widget,
            'name': name_label,
            'price': price_label,
            'change_amount': change_amount_label,
            'change_pct': change_pct_label,
            'volume': volume_label
        }
        
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
                if index_name in self.index_cards:
                    card = self.index_cards[index_name]
                    
                    # 更新价格
                    price = data.get('现价', 0)
                    card['price'].setText(f"{price:.2f}")
                    
                    # 更新涨跌幅
                    change_pct = data.get('涨跌幅', 0)
                    change_amount = data.get('涨跌额', 0)
                    
                    card['change_amount'].setText(f"{change_amount:+.2f}")
                    card['change_pct'].setText(f"{change_pct:+.2f}%")
                    
                    # 设置颜色
                    if change_pct > 0:
                        color = "#e74c3c"  # 红色
                        arrow = "↗"
                    elif change_pct < 0:
                        color = "#27ae60"  # 绿色
                        arrow = "↘"
                    else:
                        color = "#34495e"  # 灰色
                        arrow = "→"
                    
                    card['price'].setStyleSheet(f"color: {color}; padding: 2px 0;")
                    card['change_amount'].setStyleSheet(f"color: {color};")
                    card['change_pct'].setStyleSheet(f"color: {color};")
                    
                    # 更新成交量
                    volume = data.get('成交量', 0)
                    if volume > 10000:
                        volume_text = f"成交: {volume/10000:.1f}万手"
                    else:
                        volume_text = f"成交: {volume:.0f}手"
                    card['volume'].setText(volume_text)
            
            logger.debug("大盘数据更新完成")
            
        except Exception as e:
            logger.error(f"更新大盘数据失败: {e}")
            self._show_error_message(str(e))
            
    def _show_no_data_message(self):
        """显示无数据消息"""
        for card in self.index_cards.values():
            card['price'].setText("无数据")
            card['change_amount'].setText("---")
            card['change_pct'].setText("---%")
            card['volume'].setText("成交: ---")
            
    def _show_error_message(self, error_msg):
        """显示错误消息"""
        for card in self.index_cards.values():
            card['price'].setText("获取失败")
            card['change_amount'].setText("---")
            card['change_pct'].setText("---%")
            card['volume'].setText("网络错误")
