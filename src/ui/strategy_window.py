#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
策略选股窗口 - 独立的选股工具
基于设计原则：响应速度优先、高度可定制、直观易用、数据准确性
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem, 
                             QComboBox, QLineEdit, QSpinBox, QDoubleSpinBox,
                             QGroupBox, QTabWidget, QTextEdit, QCheckBox,
                             QProgressBar, QMessageBox, QFrame, QSplitter)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QThread, pyqtSlot
from PyQt6.QtGui import QFont, QColor, QAction
import sys
from datetime import datetime
import json

from src.data.data_provider import data_provider
from src.utils.logger import get_logger

logger = get_logger(__name__)

class StrategyBuilder(QWidget):
    """策略构建器"""
    
    strategy_ready = pyqtSignal(dict)  # 策略就绪信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # 标题
        title = QLabel("🧠 智能策略构建器")
        title.setFont(QFont("微软雅黑", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # 策略类型选择
        strategy_group = QGroupBox("📊 策略类型")
        strategy_layout = QVBoxLayout(strategy_group)
        
        self.strategy_combo = QComboBox()
        self.strategy_combo.addItems([
            "💹 技术指标策略", 
            "📈 价值投资策略", 
            "🚀 成长股策略",
            "💰 高股息策略",
            "📊 量价策略",
            "🔥 热门概念策略"
        ])
        self.strategy_combo.currentTextChanged.connect(self.on_strategy_changed)
        strategy_layout.addWidget(self.strategy_combo)
        
        layout.addWidget(strategy_group)
        
        # 参数设置区域
        self.params_group = QGroupBox("⚙️ 参数设置")
        self.params_layout = QVBoxLayout(self.params_group)
        
        self.create_technical_params()  # 默认显示技术指标参数
        
        layout.addWidget(self.params_group)
        
        # 执行按钮
        button_layout = QHBoxLayout()
        
        self.preview_btn = QPushButton("👀 预览结果")
        self.preview_btn.setFont(QFont("微软雅黑", 10, QFont.Weight.Bold))
        self.preview_btn.clicked.connect(self.preview_strategy)
        button_layout.addWidget(self.preview_btn)
        
        self.execute_btn = QPushButton("🚀 执行策略")
        self.execute_btn.setFont(QFont("微软雅黑", 10, QFont.Weight.Bold))
        self.execute_btn.setStyleSheet("""
            QPushButton {
                background-color: #10B981;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        self.execute_btn.clicked.connect(self.execute_strategy)
        button_layout.addWidget(self.execute_btn)
        
        layout.addWidget(QWidget())  # 弹性空间
        layout.addLayout(button_layout)
        
    def create_technical_params(self):
        """创建技术指标参数"""
        self.clear_params()
        
        # RSI参数
        rsi_layout = QHBoxLayout()
        rsi_layout.addWidget(QLabel("RSI周期:"))
        self.rsi_period = QSpinBox()
        self.rsi_period.setRange(5, 50)
        self.rsi_period.setValue(14)
        rsi_layout.addWidget(self.rsi_period)
        
        rsi_layout.addWidget(QLabel("RSI下限:"))
        self.rsi_lower = QDoubleSpinBox()
        self.rsi_lower.setRange(0, 50)
        self.rsi_lower.setValue(30)
        rsi_layout.addWidget(self.rsi_lower)
        
        rsi_layout.addWidget(QLabel("RSI上限:"))
        self.rsi_upper = QDoubleSpinBox()
        self.rsi_upper.setRange(50, 100)
        self.rsi_upper.setValue(70)
        rsi_layout.addWidget(self.rsi_upper)
        
        self.params_layout.addLayout(rsi_layout)
        
        # MACD参数
        macd_layout = QHBoxLayout()
        macd_layout.addWidget(QLabel("MACD快线:"))
        self.macd_fast = QSpinBox()
        self.macd_fast.setRange(5, 50)
        self.macd_fast.setValue(12)
        macd_layout.addWidget(self.macd_fast)
        
        macd_layout.addWidget(QLabel("MACD慢线:"))
        self.macd_slow = QSpinBox()
        self.macd_slow.setRange(10, 100)
        self.macd_slow.setValue(26)
        macd_layout.addWidget(self.macd_slow)
        
        macd_layout.addWidget(QLabel("MACD信号线:"))
        self.macd_signal = QSpinBox()
        self.macd_signal.setRange(5, 20)
        self.macd_signal.setValue(9)
        macd_layout.addWidget(self.macd_signal)
        
        self.params_layout.addLayout(macd_layout)
        
    def create_value_params(self):
        """创建价值投资参数"""
        self.clear_params()
        
        # PE参数
        pe_layout = QHBoxLayout()
        pe_layout.addWidget(QLabel("市盈率上限:"))
        self.pe_upper = QDoubleSpinBox()
        self.pe_upper.setRange(0, 100)
        self.pe_upper.setValue(20)
        pe_layout.addWidget(self.pe_upper)
        
        pe_layout.addWidget(QLabel("市净率上限:"))
        self.pb_upper = QDoubleSpinBox()
        self.pb_upper.setRange(0, 10)
        self.pb_upper.setValue(3)
        pe_layout.addWidget(self.pb_upper)
        
        self.params_layout.addLayout(pe_layout)
        
        # ROE参数
        roe_layout = QHBoxLayout()
        roe_layout.addWidget(QLabel("ROE下限(%):"))
        self.roe_lower = QDoubleSpinBox()
        self.roe_lower.setRange(0, 50)
        self.roe_lower.setValue(15)
        roe_layout.addWidget(self.roe_lower)
        
        roe_layout.addWidget(QLabel("负债率上限(%):"))
        self.debt_upper = QDoubleSpinBox()
        self.debt_upper.setRange(0, 100)
        self.debt_upper.setValue(60)
        roe_layout.addWidget(self.debt_upper)
        
        self.params_layout.addLayout(roe_layout)
        
    def create_growth_params(self):
        """创建成长股参数"""
        self.clear_params()
        
        # 营收增长
        revenue_layout = QHBoxLayout()
        revenue_layout.addWidget(QLabel("营收增长率下限(%):"))
        self.revenue_growth = QDoubleSpinBox()
        self.revenue_growth.setRange(0, 100)
        self.revenue_growth.setValue(20)
        revenue_layout.addWidget(self.revenue_growth)
        
        revenue_layout.addWidget(QLabel("利润增长率下限(%):"))
        self.profit_growth = QDoubleSpinBox()
        self.profit_growth.setRange(0, 100)
        self.profit_growth.setValue(25)
        revenue_layout.addWidget(self.profit_growth)
        
        self.params_layout.addLayout(revenue_layout)
        
    def create_dividend_params(self):
        """创建高股息参数"""
        self.clear_params()
        
        dividend_layout = QHBoxLayout()
        dividend_layout.addWidget(QLabel("股息率下限(%):"))
        self.dividend_yield = QDoubleSpinBox()
        self.dividend_yield.setRange(0, 20)
        self.dividend_yield.setValue(3)
        dividend_layout.addWidget(self.dividend_yield)
        
        dividend_layout.addWidget(QLabel("连续分红年数:"))
        self.dividend_years = QSpinBox()
        self.dividend_years.setRange(0, 20)
        self.dividend_years.setValue(3)
        dividend_layout.addWidget(self.dividend_years)
        
        self.params_layout.addLayout(dividend_layout)
        
    def create_volume_params(self):
        """创建量价策略参数"""
        self.clear_params()
        
        volume_layout = QHBoxLayout()
        volume_layout.addWidget(QLabel("成交量倍数:"))
        self.volume_ratio = QDoubleSpinBox()
        self.volume_ratio.setRange(1, 10)
        self.volume_ratio.setValue(2)
        volume_layout.addWidget(self.volume_ratio)
        
        volume_layout.addWidget(QLabel("涨幅下限(%):"))
        self.price_change = QDoubleSpinBox()
        self.price_change.setRange(0, 20)
        self.price_change.setValue(3)
        volume_layout.addWidget(self.price_change)
        
        self.params_layout.addLayout(volume_layout)
        
    def create_concept_params(self):
        """创建热门概念参数"""
        self.clear_params()
        
        concept_layout = QVBoxLayout()
        
        concept_layout.addWidget(QLabel("热门概念:"))
        self.concept_combo = QComboBox()
        self.concept_combo.addItems([
            "人工智能", "新能源汽车", "芯片半导体", 
            "5G通信", "医疗健康", "数字货币", 
            "军工航天", "新材料", "环保节能"
        ])
        concept_layout.addWidget(self.concept_combo)
        
        strength_layout = QHBoxLayout()
        strength_layout.addWidget(QLabel("板块强度要求:"))
        self.concept_strength = QComboBox()
        self.concept_strength.addItems(["强势", "中等", "弱势"])
        strength_layout.addWidget(self.concept_strength)
        concept_layout.addLayout(strength_layout)
        
        self.params_layout.addLayout(concept_layout)
        
    def clear_params(self):
        """清空参数区域"""
        while self.params_layout.count():
            child = self.params_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
    def on_strategy_changed(self, strategy_name):
        """策略类型变化"""
        if "技术指标" in strategy_name:
            self.create_technical_params()
        elif "价值投资" in strategy_name:
            self.create_value_params()
        elif "成长股" in strategy_name:
            self.create_growth_params()
        elif "高股息" in strategy_name:
            self.create_dividend_params()
        elif "量价" in strategy_name:
            self.create_volume_params()
        elif "热门概念" in strategy_name:
            self.create_concept_params()
            
    def preview_strategy(self):
        """预览策略结果"""
        QMessageBox.information(self, "预览", "策略预览功能开发中...")
        
    def execute_strategy(self):
        """执行策略"""
        strategy_name = self.strategy_combo.currentText()
        
        # 收集参数
        params = self.collect_params()
        
        strategy_data = {
            "name": strategy_name,
            "params": params,
            "timestamp": datetime.now().isoformat()
        }
        
        self.strategy_ready.emit(strategy_data)
        
    def collect_params(self):
        """收集当前参数"""
        strategy_name = self.strategy_combo.currentText()
        params = {}
        
        if "技术指标" in strategy_name:
            params = {
                "rsi_period": getattr(self, 'rsi_period', QSpinBox()).value() if hasattr(self, 'rsi_period') else 14,
                "rsi_lower": getattr(self, 'rsi_lower', QDoubleSpinBox()).value() if hasattr(self, 'rsi_lower') else 30,
                "rsi_upper": getattr(self, 'rsi_upper', QDoubleSpinBox()).value() if hasattr(self, 'rsi_upper') else 70,
                "macd_fast": getattr(self, 'macd_fast', QSpinBox()).value() if hasattr(self, 'macd_fast') else 12,
                "macd_slow": getattr(self, 'macd_slow', QSpinBox()).value() if hasattr(self, 'macd_slow') else 26,
                "macd_signal": getattr(self, 'macd_signal', QSpinBox()).value() if hasattr(self, 'macd_signal') else 9
            }
        elif "价值投资" in strategy_name:
            params = {
                "pe_upper": getattr(self, 'pe_upper', QDoubleSpinBox()).value() if hasattr(self, 'pe_upper') else 20,
                "pb_upper": getattr(self, 'pb_upper', QDoubleSpinBox()).value() if hasattr(self, 'pb_upper') else 3,
                "roe_lower": getattr(self, 'roe_lower', QDoubleSpinBox()).value() if hasattr(self, 'roe_lower') else 15,
                "debt_upper": getattr(self, 'debt_upper', QDoubleSpinBox()).value() if hasattr(self, 'debt_upper') else 60
            }
        # 其他策略类型的参数收集...
        
        return params


class StrategyResultsWidget(QWidget):
    """策略结果展示组件"""
    
    stock_selected = pyqtSignal(str, str)  # 股票代码, 股票名称
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # 结果表格
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(8)
        self.results_table.setHorizontalHeaderLabels([
            "股票代码", "股票名称", "现价", "涨跌幅", 
            "成交量", "市盈率", "评分", "操作"
        ])
        
        # 设置表格样式
        self.results_table.setAlternatingRowColors(True)
        self.results_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.results_table.horizontalHeader().setStretchLastSection(True)
        
        layout.addWidget(self.results_table)
        
        # 底部统计信息
        stats_layout = QHBoxLayout()
        
        self.total_label = QLabel("总计: 0 只")
        self.total_label.setFont(QFont("微软雅黑", 10, QFont.Weight.Bold))
        stats_layout.addWidget(self.total_label)
        
        stats_layout.addStretch()
        
        export_btn = QPushButton("📊 导出结果")
        export_btn.clicked.connect(self.export_results)
        stats_layout.addWidget(export_btn)
        
        layout.addLayout(stats_layout)
        
    def update_results(self, strategy_data):
        """更新策略结果"""
        # 模拟策略执行结果
        mock_results = [
            ["000001", "平安银行", "12.50", "+2.50%", "1200万", "6.5", "85", "买入"],
            ["000002", "万科A", "15.80", "+1.20%", "800万", "8.2", "78", "观望"],
            ["600036", "招商银行", "45.20", "+0.80%", "2000万", "7.8", "82", "买入"],
            ["600519", "贵州茅台", "1680.00", "-0.50%", "500万", "28.5", "75", "观望"],
            ["000858", "五粮液", "155.30", "+1.80%", "1500万", "22.3", "80", "买入"]
        ]
        
        self.results_table.setRowCount(len(mock_results))
        
        for row, data in enumerate(mock_results):
            for col, value in enumerate(data):
                item = QTableWidgetItem(str(value))
                
                # 设置颜色
                if col == 3:  # 涨跌幅列
                    if "+" in value:
                        item.setForeground(QColor("#EF4444"))  # 红色
                    else:
                        item.setForeground(QColor("#10B981"))  # 绿色
                elif col == 6:  # 评分列
                    score = float(value)
                    if score >= 80:
                        item.setForeground(QColor("#EF4444"))  # 红色
                    elif score >= 70:
                        item.setForeground(QColor("#F59E0B"))  # 黄色
                    else:
                        item.setForeground(QColor("#6B7280"))  # 灰色
                        
                self.results_table.setItem(row, col, item)
                
        self.total_label.setText(f"总计: {len(mock_results)} 只")
        
    def export_results(self):
        """导出结果"""
        QMessageBox.information(self, "导出", "结果导出功能开发中...")


class StrategyWindow(QWidget):
    """策略选股窗口"""
    
    strategy_applied = pyqtSignal(list)  # 策略结果信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.setup_connections()
        
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("🧠 A股策略选股工具")
        self.setGeometry(200, 200, 1200, 800)
        
        # 主布局
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)
        
        # 创建分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # 左侧策略构建区域 (40%)
        self.strategy_builder = StrategyBuilder()
        splitter.addWidget(self.strategy_builder)
        
        # 右侧结果展示区域 (60%)
        self.results_widget = StrategyResultsWidget()
        splitter.addWidget(self.results_widget)
        
        # 设置分割比例
        splitter.setSizes([480, 720])
        
        # 应用样式
        self.apply_style()
        
    def setup_connections(self):
        """设置信号连接"""
        self.strategy_builder.strategy_ready.connect(self.on_strategy_ready)
        
    def apply_style(self):
        """应用样式"""
        self.setStyleSheet("""
            QWidget {
                background-color: #1E1E1E;
                color: #FFFFFF;
                font-family: "微软雅黑";
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #404040;
                border-radius: 8px;
                margin: 10px 0px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QComboBox, QSpinBox, QDoubleSpinBox, QLineEdit {
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 5px;
                background-color: #2D2D2D;
                color: #FFFFFF;
            }
            QComboBox:hover, QSpinBox:hover, QDoubleSpinBox:hover, QLineEdit:hover {
                border-color: #0D7377;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                width: 12px;
                height: 12px;
            }
            QPushButton {
                border: 1px solid #404040;
                border-radius: 6px;
                padding: 8px 16px;
                background-color: #404040;
                color: #FFFFFF;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #505050;
                border-color: #0D7377;
            }
            QTableWidget {
                border: 1px solid #404040;
                background-color: #2D2D2D;
                alternate-background-color: #353535;
                gridline-color: #404040;
            }
            QTableWidget::item {
                padding: 8px;
                border: none;
            }
            QTableWidget::item:selected {
                background-color: #0D7377;
            }
            QHeaderView::section {
                background-color: #404040;
                color: #FFFFFF;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
        """)
        
    @pyqtSlot(dict)
    def on_strategy_ready(self, strategy_data):
        """处理策略就绪"""
        logger.info(f"策略执行: {strategy_data['name']}")
        
        # 更新结果显示
        self.results_widget.update_results(strategy_data)
        
        # 发送策略结果信号
        self.strategy_applied.emit([])  # 暂时发送空列表
        
    def closeEvent(self, event):
        """关闭事件"""
        logger.info("策略选股窗口关闭")
        event.accept()


# 测试代码
if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    window = StrategyWindow()
    window.show()
    
    sys.exit(app.exec())
