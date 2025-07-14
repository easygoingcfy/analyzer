from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QTabWidget, QMenuBar, QStatusBar, QSplitter, 
                             QToolBar, QDockWidget, QMessageBox, QLabel,
                             QPushButton, QFrame)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QAction, QIcon, QFont, QPixmap
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

class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.setup_connections()
        self.restore_window_state()
        self.setup_timer()
        
        # 立即进行一次数据更新
        self.initial_data_load()
        
    def initial_data_load(self):
        """初始数据加载"""
        try:
            logger.info("开始初始数据加载...")
            
            # 立即更新一次数据
            self.update_data()
            
            # 确保板块信息也刷新
            if hasattr(self, 'sector_info'):
                self.sector_info.refresh_data()
                
            logger.info("初始数据加载完成")
            
        except Exception as e:
            logger.error(f"初始数据加载失败: {e}")
        
    def init_ui(self):
        """初始化用户界面 - 优化版本"""
        self.setWindowTitle("📊 A股投资分析工具 v2.0 - 优雅版")
        self.setMinimumSize(1400, 900)  # 更大的最小尺寸，适配更多信息
        
        # 设置中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(8, 8, 8, 8)  # 更大的边距
        main_layout.setSpacing(12)  # 更大的间距
        
        # 创建主分割器 - 左侧信息面板 + 右侧主要内容
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(self.main_splitter)
        
        # 左侧信息面板 (30% 宽度)
        self.setup_left_info_panel()
        
        # 右侧主要内容区域 (70% 宽度) - 更大的信息展示区域
        self.setup_main_content_area()
        
        # 设置分割器比例 - 重点是更大的主要内容区域
        self.main_splitter.setSizes([420, 980])  # 30% vs 70%
        self.main_splitter.setChildrenCollapsible(False)
        
        # 创建菜单栏
        self.create_menu_bar()
        
        # 创建工具栏
        self.create_tool_bar()
        
        # 创建状态栏
        self.create_status_bar()
        
        # 设置优雅样式
        self.apply_elegant_theme()
        
    def setup_left_info_panel(self):
        """设置左侧信息面板 - 紧凑但信息丰富"""
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(10)
        
        # 大盘概览 (紧凑版 - 高度限制)
        market_frame = self.create_info_frame("📈 大盘概览")
        market_layout = QVBoxLayout(market_frame)
        
        self.market_overview = MarketOverviewWidget()
        self.market_overview.setMaximumHeight(180)  # 限制高度，保持紧凑
        market_layout.addWidget(self.market_overview)
        
        left_layout.addWidget(market_frame)
        
        # 板块信息 (主要空间 - 可扩展)
        sector_frame = self.create_info_frame("🏭 板块动态")
        sector_layout = QVBoxLayout(sector_frame)
        
        self.sector_info = SectorInfoPanel()
        sector_layout.addWidget(self.sector_info)
        
        left_layout.addWidget(sector_frame, 1)  # 扩展占用剩余空间
        
        # 自选股池 (紧凑版 - 高度限制)
        pool_frame = self.create_info_frame("⭐ 自选股")
        pool_layout = QVBoxLayout(pool_frame)
        
        self.stock_pool = StockPoolWidget()
        self.stock_pool.setMaximumHeight(220)  # 限制高度
        pool_layout.addWidget(self.stock_pool)
        
        left_layout.addWidget(pool_frame)
        
        self.main_splitter.addWidget(left_widget)
        
    def setup_main_content_area(self):
        """设置主要内容区域 - 大幅展示空间"""
        # 创建标签页容器 - 更大的内容区域
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(False)  # 禁用关闭按钮，保持简洁
        self.tab_widget.setMovable(True)
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        
        # 股票列表标签页 (优化布局)
        self.stock_list_widget = StockListWidget()
        self.tab_widget.addTab(self.stock_list_widget, "📋 股票列表")
        
        # 图表分析标签页 (更大的图表区域)
        self.chart_view = ChartViewWidget()
        self.tab_widget.addTab(self.chart_view, "📊 图表分析")
        
        # 数据分析标签页 (新增)
        analysis_widget = self.create_analysis_tab()
        self.tab_widget.addTab(analysis_widget, "📈 数据分析")
        
        self.main_splitter.addWidget(self.tab_widget)
        
    def create_info_frame(self, title: str):
        """创建信息框架"""
        from PyQt6.QtWidgets import QFrame
        frame = QFrame()
        frame.setFrameStyle(QFrame.Shape.StyledPanel)
        
        # 添加标题
        layout = QVBoxLayout(frame)
        title_label = QLabel(title)
        title_label.setFont(QFont("微软雅黑", 11, QFont.Weight.Bold))
        title_label.setStyleSheet("""
            QLabel {
                color: #374151;
                padding: 5px;
                background-color: #F3F4F6;
                border-radius: 4px;
                margin-bottom: 5px;
            }
        """)
        layout.addWidget(title_label)
        
        return frame
        
    def create_analysis_tab(self):
        """创建数据分析标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 分析功能标题
        title_label = QLabel("📈 高级数据分析中心")
        title_label.setFont(QFont("微软雅黑", 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #1F2937; margin: 20px;")
        layout.addWidget(title_label)
        
        # 功能说明
        info_label = QLabel("""
        🚀 即将推出的功能：
        
        • 💹 技术指标分析：RSI、MACD、布林带等
        • 📊 基本面分析：PE、PB、ROE等财务指标
        • 🔍 量化策略回测：自定义策略验证
        • 📈 趋势预测：基于机器学习的价格预测
        • 💰 投资组合优化：风险收益平衡分析
        • 🎯 智能选股：多因子选股模型
        """)
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setStyleSheet("""
            QLabel {
                color: #6B7280; 
                font-size: 14px; 
                line-height: 1.6;
                background-color: #F9FAFB;
                border: 1px solid #E5E7EB;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        layout.addWidget(info_label)
        
        layout.addStretch()  # 弹性空间
        
        return widget
        
    def create_menu_bar(self):
        """创建菜单栏 - 优化版本"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu('📁 文件(&F)')
        
        new_action = QAction('🆕 新建窗口(&N)', self)
        new_action.setShortcut('Ctrl+N')
        new_action.triggered.connect(self.new_window)
        file_menu.addAction(new_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('🚪 退出(&X)', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 视图菜单
        view_menu = menubar.addMenu('👁️ 视图(&V)')
        
        layout_action = QAction('📐 布局设置(&L)', self)
        layout_action.triggered.connect(self.show_layout_settings)
        view_menu.addAction(layout_action)
        
        theme_action = QAction('🎨 主题设置(&T)', self)
        theme_action.triggered.connect(self.show_theme_settings)
        view_menu.addAction(theme_action)
        
        view_menu.addSeparator()
        
        fullscreen_action = QAction('🖥️ 全屏模式(&F)', self)
        fullscreen_action.setShortcut('F11')
        fullscreen_action.triggered.connect(self.toggle_fullscreen)
        view_menu.addAction(fullscreen_action)
        
        # 数据菜单
        data_menu = menubar.addMenu('📊 数据(&D)')
        
        refresh_action = QAction('🔄 刷新数据(&R)', self)
        refresh_action.setShortcut('F5')
        refresh_action.triggered.connect(self.refresh_all_data)
        data_menu.addAction(refresh_action)
        
        data_menu.addSeparator()
        
        export_action = QAction('📋 导出数据(&E)', self)
        export_action.triggered.connect(self.export_data)
        data_menu.addAction(export_action)
        
        # 工具菜单  
        tools_menu = menubar.addMenu('🔧 工具(&T)')
        
        strategy_action = QAction('🧠 策略选股(&S)', self)
        strategy_action.setShortcut('Ctrl+S')
        strategy_action.triggered.connect(self.open_strategy_window)
        tools_menu.addAction(strategy_action)
        
        tools_menu.addSeparator()
        
        calculator_action = QAction('🧮 收益计算器(&C)', self)
        calculator_action.triggered.connect(self.show_calculator)
        tools_menu.addAction(calculator_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu('❓ 帮助(&H)')
        
        about_action = QAction('ℹ️ 关于(&A)', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def create_tool_bar(self):
        """创建工具栏 - 优化版本"""
        toolbar = QToolBar("主工具栏")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        # 刷新按钮
        refresh_action = QAction('🔄 刷新', self)
        refresh_action.setToolTip('刷新数据 (F5)')
        refresh_action.triggered.connect(self.refresh_all_data)
        toolbar.addAction(refresh_action)
        
        toolbar.addSeparator()
        
        # 策略选股按钮
        strategy_action = QAction('🧠 策略选股', self)
        strategy_action.setToolTip('打开策略选股窗口 (Ctrl+S)')
        strategy_action.triggered.connect(self.open_strategy_window)
        toolbar.addAction(strategy_action)
        
        toolbar.addSeparator()
        
        # 全屏按钮
        fullscreen_action = QAction('🖥️ 全屏', self)
        fullscreen_action.setToolTip('切换全屏模式 (F11)')
        fullscreen_action.triggered.connect(self.toggle_fullscreen)
        toolbar.addAction(fullscreen_action)
        
        # 设置按钮
        settings_action = QAction('⚙️ 设置', self)
        settings_action.setToolTip('应用设置')
        settings_action.triggered.connect(self.show_settings)
        toolbar.addAction(settings_action)
        
    def create_status_bar(self):
        """创建状态栏"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # 数据更新时间标签
        self.update_time_label = QLabel("数据更新时间: --")
        self.status_bar.addWidget(self.update_time_label)
        
        # 连接状态标签
        self.connection_label = QLabel("连接状态: 正常")
        self.status_bar.addPermanentWidget(self.connection_label)
        
    def setup_connections(self):
        """设置信号连接"""
        # 股票池选择信号
        self.stock_pool.stock_selected.connect(self.on_stock_selected)
        
        # 股票列表选择信号
        self.stock_list_widget.stock_selected.connect(self.on_stock_selected)
        
        # 板块信息选择信号
        self.sector_info.sector_selected.connect(self.on_sector_selected)
        
        # 标签页关闭信号
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        
    def setup_timer(self):
        """设置定时器"""
        # 数据更新定时器
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_data)
        
        # 从配置读取更新间隔
        interval = config_manager.get('data.update_interval', 5000)
        self.update_timer.start(interval)
        
        logger.info(f"数据更新定时器已启动，间隔: {interval}ms")
        
    def update_data(self):
        """更新数据"""
        try:
            # 更新大盘数据
            self.market_overview.refresh_data()
            
            # 更新股票列表数据
            self.stock_list_widget.refresh_data()
            
            # 更新状态栏时间
            from datetime import datetime
            current_time = datetime.now().strftime('%H:%M:%S')
            self.update_time_label.setText(f"数据更新时间: {current_time}")
            
        except Exception as e:
            logger.error(f"更新数据失败: {e}")
            self.connection_label.setText("连接状态: 异常")
    
    def on_stock_selected(self, stock_code: str, stock_name: str):
        """处理股票选择事件"""
        logger.info(f"选择股票: {stock_code} - {stock_name}")
        
        # 更新图表视图
        self.chart_view.load_stock(stock_code, stock_name)
        
        # 切换到图表标签页
        self.tab_widget.setCurrentIndex(1)
    
    def on_sector_selected(self, sector_code: str, sector_name: str):
        """处理板块选择事件"""
        logger.info(f"选择板块: {sector_code} - {sector_name}")
        
        # 获取板块成分股
        from src.data.sector_data import sector_data_provider
        stocks = sector_data_provider.get_sector_stocks(sector_code)
        
        if stocks:
            # 在股票列表中显示板块成分股
            self.stock_list_widget.filter_by_stocks(stocks)
            # 切换到股票列表标签页
            self.tab_widget.setCurrentIndex(0)
            # 更新状态栏
            self.status_bar.showMessage(f"已显示板块 {sector_name} 的 {len(stocks)} 只成分股", 3000)
        else:
            QMessageBox.information(self, "提示", f"板块 {sector_name} 暂无成分股数据")
    
    def refresh_all_data(self):
        """刷新所有数据"""
        self.update_data()
        logger.info("手动刷新数据完成")
        
    def new_window(self):
        """新建窗口"""
        new_window = MainWindow()
        new_window.show()
        
    def close_tab(self, index: int):
        """关闭标签页"""
        if index >= 2:  # 只能关闭第3个及以后的标签页
            self.tab_widget.removeTab(index)
    
    def show_layout_settings(self):
        """显示布局设置"""
        QMessageBox.information(self, "布局设置", "布局设置功能正在开发中...")
        
    def show_theme_settings(self):
        """显示主题设置"""
        QMessageBox.information(self, "主题设置", "主题设置功能正在开发中...")
        
    def open_strategy_window(self):
        """打开策略选股窗口"""
        try:
            from src.ui.strategy_window import StrategyWindow
            
            if not hasattr(self, 'strategy_window') or not self.strategy_window.isVisible():
                self.strategy_window = StrategyWindow(self)
                self.strategy_window.strategy_applied.connect(self.on_strategy_applied)
                self.strategy_window.show()
            else:
                self.strategy_window.raise_()
                self.strategy_window.activateWindow()
        except ImportError:
            QMessageBox.information(self, "提示", "策略选股窗口正在开发中...")
    
    def on_strategy_applied(self, stocks):
        """处理策略选股结果"""
        if stocks:
            self.stock_list_widget.filter_by_stocks(stocks)
            self.tab_widget.setCurrentIndex(0)  # 切换到股票列表
            self.status_bar.showMessage(f"策略选股完成，共筛选出 {len(stocks)} 只股票", 5000)
        
    def toggle_fullscreen(self):
        """切换全屏模式"""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
    
    def export_data(self):
        """导出数据"""
        QMessageBox.information(self, "导出数据", "数据导出功能开发中...")
        
    def show_calculator(self):
        """显示收益计算器"""
        QMessageBox.information(self, "收益计算器", "收益计算器功能开发中...")
        
    def show_strategy_editor(self):
        """兼容性方法 - 重定向到策略选股窗口"""
        self.open_strategy_window()
        
    def show_settings(self):
        """显示设置对话框"""
        QMessageBox.information(self, "设置", "设置功能正在开发中...")
        
    def show_about(self):
        """显示关于对话框"""
        QMessageBox.about(self, "关于", 
                         "📊 A股投资分析工具 v2.0 - 优雅版\\n\\n"
                         "🚀 基于新设计原则的股票分析工具\\n"
                         "✨ 响应速度优先 | 高度可定制 | 直观易用 | 数据准确\\n\\n"
                         "📈 支持功能：\\n"
                         "• 实时行情监控\\n"
                         "• 板块动态分析\\n"
                         "• 智能策略选股\\n"
                         "• 图表技术分析\\n\\n"
                         "🛠️ 技术支持：Python + PyQt6")
    
    def apply_elegant_theme(self):
        """应用优雅主题"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #F9FAFB;
                color: #1F2937;
            }
            
            QTabWidget::pane {
                border: 1px solid #E5E7EB;
                background-color: #FFFFFF;
                border-radius: 8px;
            }
            
            QTabBar::tab {
                background-color: #F3F4F6;
                color: #6B7280;
                padding: 12px 20px;
                margin-right: 4px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: 500;
                min-width: 100px;
            }
            
            QTabBar::tab:selected {
                background-color: #FFFFFF;
                color: #1F2937;
                border-bottom: 3px solid #3B82F6;
                font-weight: 600;
            }
            
            QTabBar::tab:hover {
                background-color: #E5E7EB;
                color: #374151;
            }
            
            QToolBar {
                background-color: #FFFFFF;
                border: none;
                border-bottom: 1px solid #E5E7EB;
                spacing: 8px;
                padding: 8px;
            }
            
            QToolBar QToolButton {
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: 500;
            }
            
            QToolBar QToolButton:hover {
                background-color: #F3F4F6;
                border-color: #D1D5DB;
            }
            
            QStatusBar {
                background-color: #F9FAFB;
                border-top: 1px solid #E5E7EB;
                color: #6B7280;
                font-size: 12px;
            }
            
            QMenuBar {
                background-color: #FFFFFF;
                color: #1F2937;
                border-bottom: 1px solid #E5E7EB;
                font-weight: 500;
            }
            
            QMenuBar::item {
                background-color: transparent;
                padding: 8px 12px;
                border-radius: 4px;
            }
            
            QMenuBar::item:selected {
                background-color: #F3F4F6;
                color: #1F2937;
            }
            
            QSplitter::handle {
                background-color: #E5E7EB;
                width: 2px;
                border-radius: 1px;
            }
            
            QSplitter::handle:hover {
                background-color: #3B82F6;
            }
            
            QFrame[frameShape="4"] {
                background-color: #FFFFFF;
                border: 1px solid #E5E7EB;
                border-radius: 8px;
                margin: 4px;
            }
        """)
    
    def restore_window_state(self):
        """恢复窗口状态"""
        size = config_manager.get('ui.window_size', [1200, 800])
        position = config_manager.get('ui.window_position', [100, 100])
        
        self.resize(size[0], size[1])
        self.move(position[0], position[1])
        
    def save_window_state(self):
        """保存窗口状态"""
        config_manager.set('ui.window_size', [self.width(), self.height()])
        config_manager.set('ui.window_position', [self.x(), self.y()])
        config_manager.save()
        
    def closeEvent(self, event):
        """窗口关闭事件"""
        self.save_window_state()
        
        # 停止定时器
        if hasattr(self, 'update_timer'):
            self.update_timer.stop()
            
        logger.info("应用程序正在退出...")
        event.accept()
    
    # 新增功能方法
    def open_strategy_window(self):
        """打开策略选股窗口"""
        from src.ui.strategy_window import StrategyWindow
        
        if not hasattr(self, 'strategy_window') or not self.strategy_window.isVisible():
            self.strategy_window = StrategyWindow(self)
            self.strategy_window.strategy_applied.connect(self.on_strategy_applied)
            self.strategy_window.show()
        else:
            self.strategy_window.raise_()
            self.strategy_window.activateWindow()
    
    def on_strategy_applied(self, stocks):
        """处理策略选股结果"""
        if stocks:
            self.stock_list_widget.filter_by_stocks(stocks)
            self.tab_widget.setCurrentIndex(0)  # 切换到股票列表
            self.status_bar.showMessage(f"策略选股完成，共筛选出 {len(stocks)} 只股票", 5000)
        
    def toggle_fullscreen(self):
        """切换全屏模式"""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
    
    def export_data(self):
        """导出数据"""
        QMessageBox.information(self, "导出数据", "数据导出功能开发中...")
        
    def show_calculator(self):
        """显示收益计算器"""
        QMessageBox.information(self, "收益计算器", "收益计算器功能开发中...")
        
    def apply_elegant_theme(self):
        """应用优雅主题"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #F9FAFB;
                color: #1F2937;
            }
            
            QTabWidget::pane {
                border: 1px solid #E5E7EB;
                background-color: #FFFFFF;
                border-radius: 8px;
            }
            
            QTabBar::tab {
                background-color: #F3F4F6;
                color: #6B7280;
                padding: 12px 20px;
                margin-right: 4px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: 500;
                min-width: 100px;
            }
            
            QTabBar::tab:selected {
                background-color: #FFFFFF;
                color: #1F2937;
                border-bottom: 3px solid #3B82F6;
                font-weight: 600;
            }
            
            QTabBar::tab:hover {
                background-color: #E5E7EB;
                color: #374151;
            }
            
            QToolBar {
                background-color: #FFFFFF;
                border: none;
                border-bottom: 1px solid #E5E7EB;
                spacing: 8px;
                padding: 8px;
            }
            
            QToolBar QToolButton {
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: 500;
            }
            
            QToolBar QToolButton:hover {
                background-color: #F3F4F6;
                border-color: #D1D5DB;
            }
            
            QStatusBar {
                background-color: #F9FAFB;
                border-top: 1px solid #E5E7EB;
                color: #6B7280;
                font-size: 12px;
            }
            
            QMenuBar {
                background-color: #FFFFFF;
                color: #1F2937;
                border-bottom: 1px solid #E5E7EB;
                font-weight: 500;
            }
            
            QMenuBar::item {
                background-color: transparent;
                padding: 8px 12px;
                border-radius: 4px;
            }
            
            QMenuBar::item:selected {
                background-color: #F3F4F6;
                color: #1F2937;
            }
            
            QSplitter::handle {
                background-color: #E5E7EB;
                width: 2px;
                border-radius: 1px;
            }
            
            QSplitter::handle:hover {
                background-color: #3B82F6;
            }
            
            QFrame[frameShape="4"] {
                background-color: #FFFFFF;
                border: 1px solid #E5E7EB;
                border-radius: 8px;
                margin: 4px;
            }
        """)
    
    # 删除旧的apply_theme方法引用
