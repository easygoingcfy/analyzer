#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
重构的主窗口 - 优雅的交互设计
基于新的设计原则：响应速度优先、高度可定制、直观易用、数据准确性
"""

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QTabWidget, QStatusBar, QSplitter, 
                             QToolBar, QMessageBox, QLabel,
                             QFrame, QPushButton, QComboBox,
                             QProgressBar)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QAction, QFont
import sys
import os

from src.ui.market_overview import MarketOverviewWidget
from src.ui.stock_list import StockListWidget
from src.ui.chart_view import ChartViewWidget
from src.ui.stock_pool import StockPoolWidget
from src.ui.sector_info import SectorInfoPanel
from src.utils.config import config_manager
from src.utils.logger import get_logger

logger = get_logger(__name__)

class ElegantMainWindow(QMainWindow):
    """优雅的主窗口 - 重构版本"""
    
    # 信号定义
    stock_selected = pyqtSignal(str, str)  # 股票代码, 股票名称
    theme_changed = pyqtSignal(str)        # 主题变化
    layout_changed = pyqtSignal(str)       # 布局变化
    
    def __init__(self):
        super().__init__()
        self.settings = QSettings("AStockAnalyzer", "MainWindow")
        self.current_theme = "modern_dark"
        self.layout_mode = "focus"  # focus, split, wide
        self.init_ui()
        self.setup_connections()
        self.setup_performance_optimization()
        self.restore_window_state()
        self.apply_elegant_theme()
        
    def init_ui(self):
        """初始化用户界面 - 优雅设计"""
        self.setWindowTitle("📊 A股投资分析工具 v2.0 - 优雅版")
        self.setMinimumSize(1400, 900)  # 更大的最小尺寸
        
        # 创建菜单栏
        self.setup_menu_bar()
        
        # 创建工具栏
        self.setup_toolbar()
        
        # 创建中心布局
        self.setup_central_layout()
        
        # 创建状态栏
        self.setup_status_bar()
        
        # 创建可停靠窗口
        self.setup_dock_widgets()
        
    def setup_menu_bar(self):
        """设置菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu("📁 文件")
        
        new_action = QAction("🆕 新建窗口", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self.new_window)
        file_menu.addAction(new_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("🚪 退出", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 视图菜单
        view_menu = menubar.addMenu("👁️ 视图")
        
        # 布局模式子菜单
        layout_menu = view_menu.addMenu("📐 布局模式")
        
        focus_action = QAction("🎯 聚焦模式", self)
        focus_action.setCheckable(True)
        focus_action.setChecked(True)
        focus_action.triggered.connect(lambda: self.set_layout_mode("focus"))
        layout_menu.addAction(focus_action)
        
        split_action = QAction("📊 分屏模式", self)
        split_action.setCheckable(True)
        split_action.triggered.connect(lambda: self.set_layout_mode("split"))
        layout_menu.addAction(split_action)
        
        wide_action = QAction("🖥️ 宽屏模式", self)
        wide_action.setCheckable(True)
        wide_action.triggered.connect(lambda: self.set_layout_mode("wide"))
        layout_menu.addAction(wide_action)
        
        # 主题子菜单
        theme_menu = view_menu.addMenu("🎨 主题")
        
        dark_action = QAction("🌙 现代暗色", self)
        dark_action.setCheckable(True)
        dark_action.setChecked(True)
        dark_action.triggered.connect(lambda: self.set_theme("modern_dark"))
        theme_menu.addAction(dark_action)
        
        light_action = QAction("☀️ 简洁亮色", self)
        light_action.setCheckable(True)
        light_action.triggered.connect(lambda: self.set_theme("clean_light"))
        theme_menu.addAction(light_action)
        
        professional_action = QAction("💼 专业版", self)
        professional_action.setCheckable(True)
        professional_action.triggered.connect(lambda: self.set_theme("professional"))
        theme_menu.addAction(professional_action)
        
        # 工具菜单
        tools_menu = menubar.addMenu("🔧 工具")
        
        strategy_action = QAction("🧠 策略选股", self)
        strategy_action.setShortcut("Ctrl+S")
        strategy_action.triggered.connect(self.open_strategy_window)
        tools_menu.addAction(strategy_action)
        
        data_action = QAction("📊 数据管理", self)
        data_action.triggered.connect(self.open_data_manager)
        tools_menu.addAction(data_action)
        
        settings_action = QAction("⚙️ 偏好设置", self)
        settings_action.setShortcut("Ctrl+,")
        settings_action.triggered.connect(self.open_settings)
        tools_menu.addAction(settings_action)
        
    def setup_toolbar(self):
        """设置工具栏"""
        toolbar = QToolBar("主工具栏")
        toolbar.setMovable(False)
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.addToolBar(toolbar)
        
        # 快速操作按钮
        refresh_action = QAction("🔄", self)
        refresh_action.setToolTip("刷新数据 (F5)")
        refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(self.refresh_all_data)
        toolbar.addAction(refresh_action)
        
        toolbar.addSeparator()
        
        strategy_action = QAction("🧠", self)
        strategy_action.setToolTip("策略选股 (Ctrl+S)")
        strategy_action.triggered.connect(self.open_strategy_window)
        toolbar.addAction(strategy_action)
        
        toolbar.addSeparator()
        
        # 布局切换
        layout_combo = QComboBox()
        layout_combo.addItems(["🎯 聚焦模式", "📊 分屏模式", "🖥️ 宽屏模式"])
        layout_combo.currentTextChanged.connect(self.on_layout_combo_changed)
        toolbar.addWidget(QLabel("布局:"))
        toolbar.addWidget(layout_combo)
        
        toolbar.addSeparator()
        
        # 数据状态指示器
        self.data_status_label = QLabel("🟢 数据连接正常")
        self.data_status_label.setStyleSheet("color: #10B981; font-weight: bold;")
        toolbar.addWidget(self.data_status_label)
        
    def setup_central_layout(self):
        """设置中央布局 - 更大的信息展示区域"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(12)
        
        # 创建主分割器
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(self.main_splitter)
        
        # 左侧信息面板 (40% 宽度)
        self.setup_left_info_panel()
        
        # 右侧主要内容区域 (60% 宽度)
        self.setup_main_content_area()
        
        # 设置分割器比例
        self.main_splitter.setSizes([600, 900])  # 更大的右侧区域
        self.main_splitter.setChildrenCollapsible(False)
        
    def setup_left_info_panel(self):
        """设置左侧信息面板"""
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(8)
        
        # 大盘概览 (紧凑版)
        market_frame = QFrame()
        market_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        market_layout = QVBoxLayout(market_frame)
        
        market_title = QLabel("📈 大盘概览")
        market_title.setFont(QFont("微软雅黑", 11, QFont.Weight.Bold))
        market_layout.addWidget(market_title)
        
        self.market_overview = MarketOverviewWidget()
        self.market_overview.setMaximumHeight(200)  # 限制高度
        market_layout.addWidget(self.market_overview)
        
        left_layout.addWidget(market_frame)
        
        # 板块信息 (占主要空间)
        sector_frame = QFrame()
        sector_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        sector_layout = QVBoxLayout(sector_frame)
        
        sector_title = QLabel("🏭 板块动态")
        sector_title.setFont(QFont("微软雅黑", 11, QFont.Weight.Bold))
        sector_layout.addWidget(sector_title)
        
        self.sector_info = SectorInfoPanel()
        sector_layout.addWidget(self.sector_info)
        
        left_layout.addWidget(sector_frame, 1)  # 扩展占用剩余空间
        
        # 自选股池 (紧凑版)
        pool_frame = QFrame()
        pool_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        pool_layout = QVBoxLayout(pool_frame)
        
        pool_title = QLabel("⭐ 自选股")
        pool_title.setFont(QFont("微软雅黑", 11, QFont.Weight.Bold))
        pool_layout.addWidget(pool_title)
        
        self.stock_pool = StockPoolWidget()
        self.stock_pool.setMaximumHeight(250)  # 限制高度
        pool_layout.addWidget(self.stock_pool)
        
        left_layout.addWidget(pool_frame)
        
        self.main_splitter.addWidget(left_widget)
        
    def setup_main_content_area(self):
        """设置主要内容区域 - 大幅展示空间"""
        # 创建标签页容器
        self.main_tab_widget = QTabWidget()
        self.main_tab_widget.setTabsClosable(False)
        self.main_tab_widget.setMovable(True)
        self.main_tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        
        # 股票列表标签页 (优化布局)
        self.stock_list_widget = StockListWidget()
        self.main_tab_widget.addTab(self.stock_list_widget, "📋 股票列表")
        
        # 图表分析标签页 (更大的图表区域)
        self.chart_view = ChartViewWidget()
        self.main_tab_widget.addTab(self.chart_view, "📊 图表分析")
        
        # 数据分析标签页
        analysis_widget = self.create_analysis_tab()
        self.main_tab_widget.addTab(analysis_widget, "📈 数据分析")
        
        self.main_splitter.addWidget(self.main_tab_widget)
        
    def create_analysis_tab(self):
        """创建数据分析标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 分析功能占位
        title_label = QLabel("📈 数据分析中心")
        title_label.setFont(QFont("微软雅黑", 14, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        info_label = QLabel("高级数据分析功能开发中...")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setStyleSheet("color: #6B7280; font-size: 12px;")
        layout.addWidget(info_label)
        
        return widget
        
    def setup_status_bar(self):
        """设置状态栏"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # 左侧信息
        self.status_label = QLabel("就绪")
        self.status_bar.addWidget(self.status_label)
        
        # 中间弹性空间
        self.status_bar.addPermanentWidget(QLabel(""), 1)
        
        # 右侧信息
        self.update_time_label = QLabel("数据更新: --")
        self.status_bar.addPermanentWidget(self.update_time_label)
        
        self.connection_label = QLabel("🟢 连接正常")
        self.status_bar.addPermanentWidget(self.connection_label)
        
        # 性能指示器
        self.performance_bar = QProgressBar()
        self.performance_bar.setMaximumWidth(100)
        self.performance_bar.setTextVisible(False)
        self.performance_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #374151;
                border-radius: 3px;
                background-color: #1F2937;
            }
            QProgressBar::chunk {
                background-color: #10B981;
                border-radius: 2px;
            }
        """)
        self.status_bar.addPermanentWidget(QLabel("性能:"))
        self.status_bar.addPermanentWidget(self.performance_bar)
        
    def setup_dock_widgets(self):
        """设置可停靠窗口 (用于高级功能)"""
        # 预留接口，用于未来扩展
        pass
        
    def setup_connections(self):
        """设置信号连接"""
        # 股票选择信号
        self.stock_pool.stock_selected.connect(self.on_stock_selected)
        self.stock_list_widget.stock_selected.connect(self.on_stock_selected)
        
        # 板块选择信号
        self.sector_info.sector_selected.connect(self.on_sector_selected)
        
        # 标签页切换信号
        self.main_tab_widget.currentChanged.connect(self.on_tab_changed)
        
    def setup_performance_optimization(self):
        """设置性能优化"""
        # 数据更新定时器 (优化频率)
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_data)
        self.update_timer.start(2000)  # 2秒更新，提高响应性
        
        # 性能监控定时器
        self.performance_timer = QTimer()
        self.performance_timer.timeout.connect(self.update_performance_indicator)
        self.performance_timer.start(1000)  # 1秒更新性能指标
        
    def apply_elegant_theme(self):
        """应用优雅主题"""
        if self.current_theme == "modern_dark":
            self.apply_modern_dark_theme()
        elif self.current_theme == "clean_light":
            self.apply_clean_light_theme()
        elif self.current_theme == "professional":
            self.apply_professional_theme()
    
    def apply_modern_dark_theme(self):
        """应用现代暗色主题"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1E1E1E;
                color: #FFFFFF;
            }
            QTabWidget::pane {
                border: 1px solid #404040;
                background-color: #2D2D2D;
            }
            QTabBar::tab {
                background-color: #404040;
                color: #FFFFFF;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }
            QTabBar::tab:selected {
                background-color: #0D7377;
                color: #FFFFFF;
            }
            QTabBar::tab:hover {
                background-color: #505050;
            }
            QFrame {
                background-color: #2D2D2D;
                border: 1px solid #404040;
                border-radius: 8px;
                margin: 2px;
            }
            QLabel {
                color: #FFFFFF;
            }
            QToolBar {
                background-color: #2D2D2D;
                border: none;
                padding: 4px;
            }
            QMenuBar {
                background-color: #2D2D2D;
                color: #FFFFFF;
                border: none;
            }
            QMenuBar::item:selected {
                background-color: #0D7377;
                color: #FFFFFF;
            }
            QStatusBar {
                background-color: #2D2D2D;
                color: #FFFFFF;
                border-top: 1px solid #404040;
            }
        """)
        
    def apply_clean_light_theme(self):
        """应用简洁亮色主题"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #FFFFFF;
                color: #1F2937;
            }
            QTabWidget::pane {
                border: 1px solid #E5E7EB;
                background-color: #F9FAFB;
            }
            QTabBar::tab {
                background-color: #F3F4F6;
                color: #1F2937;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }
            QTabBar::tab:selected {
                background-color: #3B82F6;
                color: #FFFFFF;
            }
            QTabBar::tab:hover {
                background-color: #E5E7EB;
            }
            QFrame {
                background-color: #FFFFFF;
                border: 1px solid #E5E7EB;
                border-radius: 8px;
                margin: 2px;
            }
            QLabel {
                color: #1F2937;
            }
        """)
        
    def apply_professional_theme(self):
        """应用专业版主题"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0F172A;
                color: #F1F5F9;
            }
            QTabWidget::pane {
                border: 1px solid #334155;
                background-color: #1E293B;
            }
            QTabBar::tab {
                background-color: #334155;
                color: #F1F5F9;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }
            QTabBar::tab:selected {
                background-color: #0EA5E9;
                color: #FFFFFF;
            }
            QFrame {
                background-color: #1E293B;
                border: 1px solid #334155;
                border-radius: 8px;
                margin: 2px;
            }
        """)
    
    # 事件处理方法
    def set_theme(self, theme_name: str):
        """设置主题"""
        self.current_theme = theme_name
        self.apply_elegant_theme()
        self.theme_changed.emit(theme_name)
        self.status_label.setText(f"已切换到{theme_name}主题")
        
    def set_layout_mode(self, mode: str):
        """设置布局模式"""
        self.layout_mode = mode
        if mode == "focus":
            self.main_splitter.setSizes([500, 1000])
        elif mode == "split":
            self.main_splitter.setSizes([750, 750])
        elif mode == "wide":
            self.main_splitter.setSizes([400, 1100])
        
        self.layout_changed.emit(mode)
        self.status_label.setText(f"已切换到{mode}布局模式")
        
    def on_layout_combo_changed(self, text: str):
        """布局组合框变化处理"""
        mode_map = {
            "🎯 聚焦模式": "focus",
            "📊 分屏模式": "split", 
            "🖥️ 宽屏模式": "wide"
        }
        if text in mode_map:
            self.set_layout_mode(mode_map[text])
    
    def on_stock_selected(self, stock_code: str, stock_name: str):
        """处理股票选择事件"""
        self.stock_selected.emit(stock_code, stock_name)
        
        # 更新图表视图
        self.chart_view.load_stock(stock_code, stock_name)
        
        # 切换到图表标签页
        self.main_tab_widget.setCurrentIndex(1)
        
        self.status_label.setText(f"已选择: {stock_code} - {stock_name}")
        
    def on_sector_selected(self, sector_code: str, sector_name: str):
        """处理板块选择事件"""
        # 获取板块成分股并在股票列表中显示
        from src.data.sector_data import sector_data_provider
        stocks = sector_data_provider.get_sector_stocks(sector_code)
        
        if stocks:
            self.stock_list_widget.filter_by_stocks(stocks)
            self.main_tab_widget.setCurrentIndex(0)  # 切换到股票列表
            self.status_label.setText(f"已显示板块 {sector_name} 的 {len(stocks)} 只成分股")
        else:
            QMessageBox.information(self, "提示", f"板块 {sector_name} 暂无成分股数据")
    
    def on_tab_changed(self, index: int):
        """标签页变化处理"""
        tab_names = ["股票列表", "图表分析", "数据分析"]
        if 0 <= index < len(tab_names):
            self.status_label.setText(f"当前页面: {tab_names[index]}")
    
    def update_data(self):
        """更新数据"""
        try:
            # 更新大盘数据
            self.market_overview.refresh_data()
            
            # 更新股票列表 (如果当前标签页是股票列表)
            if self.main_tab_widget.currentIndex() == 0:
                self.stock_list_widget.refresh_data()
                
            # 更新时间戳
            from datetime import datetime
            current_time = datetime.now().strftime("%H:%M:%S")
            self.update_time_label.setText(f"数据更新: {current_time}")
            self.connection_label.setText("🟢 连接正常")
            self.data_status_label.setText("🟢 数据连接正常")
            self.data_status_label.setStyleSheet("color: #10B981; font-weight: bold;")
            
        except Exception as e:
            logger.error(f"更新数据失败: {e}")
            self.connection_label.setText("🔴 连接异常")
            self.data_status_label.setText("🔴 数据连接异常")
            self.data_status_label.setStyleSheet("color: #EF4444; font-weight: bold;")
    
    def update_performance_indicator(self):
        """更新性能指标"""
        # 模拟性能数据
        import random
        performance = random.randint(70, 100)
        self.performance_bar.setValue(performance)
        
        if performance >= 90:
            color = "#10B981"  # 绿色
        elif performance >= 70:
            color = "#F59E0B"  # 黄色
        else:
            color = "#EF4444"  # 红色
            
        self.performance_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid #374151;
                border-radius: 3px;
                background-color: #1F2937;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 2px;
            }}
        """)
    
    def refresh_all_data(self):
        """刷新所有数据"""
        self.update_data()
        self.status_label.setText("数据刷新完成")
        
    def open_strategy_window(self):
        """打开策略选股窗口"""
        from src.ui.strategy_window import StrategyWindow
        if not hasattr(self, 'strategy_window') or not self.strategy_window.isVisible():
            self.strategy_window = StrategyWindow(self)
            self.strategy_window.show()
        else:
            self.strategy_window.raise_()
            self.strategy_window.activateWindow()
        
    def open_data_manager(self):
        """打开数据管理窗口"""
        QMessageBox.information(self, "数据管理", "数据管理功能开发中...")
        
    def open_settings(self):
        """打开设置窗口"""
        QMessageBox.information(self, "偏好设置", "偏好设置功能开发中...")
        
    def new_window(self):
        """新建窗口"""
        new_window = ElegantMainWindow()
        new_window.show()
        
    def restore_window_state(self):
        """恢复窗口状态"""
        try:
            geometry = self.settings.value("geometry")
            if geometry:
                self.restoreGeometry(geometry)
            
            state = self.settings.value("windowState")
            if state:
                self.restoreState(state)
                
            # 恢复主题和布局
            saved_theme = self.settings.value("theme", "modern_dark")
            saved_layout = self.settings.value("layout", "focus")
            
            self.set_theme(saved_theme)
            self.set_layout_mode(saved_layout)
            
        except Exception as e:
            logger.warning(f"恢复窗口状态失败: {e}")
    
    def closeEvent(self, event):
        """关闭事件"""
        try:
            # 保存窗口状态
            self.settings.setValue("geometry", self.saveGeometry())
            self.settings.setValue("windowState", self.saveState())
            self.settings.setValue("theme", self.current_theme)
            self.settings.setValue("layout", self.layout_mode)
            
            # 关闭策略窗口
            if hasattr(self, 'strategy_window') and self.strategy_window.isVisible():
                self.strategy_window.close()
                
        except Exception as e:
            logger.error(f"保存窗口状态失败: {e}")
            
        event.accept()
