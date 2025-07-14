"""
优化版主窗口 - 同花顺风格上下布局
大幅放大指数和板块内容显示
"""
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QTabWidget, QMenuBar, QStatusBar, QToolBar, 
                             QMessageBox, QLabel, QPushButton, QFrame)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QAction, QIcon, QFont

from src.ui.enhanced_market_overview import EnhancedMarketOverviewWidget
from src.ui.stock_list import StockListWidget
from src.ui.chart_view import ChartViewWidget
from src.ui.stock_pool import StockPoolWidget
from src.ui.sector_info import SectorInfoPanel
from src.utils.config import config_manager
from src.utils.logger import get_logger

logger = get_logger(__name__)

class MainWindow(QMainWindow):
    """优化版主窗口 - 同花顺风格"""
    
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
            self.update_data()
            logger.info("初始数据加载完成")
        except Exception as e:
            logger.error(f"初始数据加载失败: {e}")
        
    def init_ui(self):
        """初始化用户界面 - 同花顺风格上下布局"""
        self.setWindowTitle("📊 A股投资分析工具 v2.0 - 专业版")
        self.setMinimumSize(1600, 1000)  # 更大的窗口以容纳更多信息
        
        # 设置中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局 - 垂直布局 (上下排列)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(12)
        
        # 1. 顶部大盘指数区域 (大幅放大)
        self.setup_large_market_area(main_layout)
        
        # 2. 中部板块信息区域 (大幅放大)
        self.setup_large_sector_area(main_layout)
        
        # 3. 底部股票信息和图表区域 (可伸缩)
        self.setup_stock_content_area(main_layout)
        
        # 创建菜单栏
        self.create_menu_bar()
        
        # 创建工具栏
        self.create_tool_bar()
        
        # 创建状态栏
        self.create_status_bar()
        
        # 设置专业主题
        self.apply_professional_theme()
        
    def setup_large_market_area(self, main_layout):
        """设置大尺寸大盘指数区域 - 参考同花顺"""
        # 创建大盘区域容器
        market_frame = QFrame()
        market_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        market_frame.setFixedHeight(220)  # 大幅增加高度
        market_frame.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 2px solid #3498db;
                border-radius: 10px;
                margin: 5px;
            }
        """)
        
        market_layout = QVBoxLayout(market_frame)
        market_layout.setContentsMargins(15, 15, 15, 15)
        market_layout.setSpacing(10)
        
        # 标题区域
        title_container = QWidget()
        title_layout = QHBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        
        market_title = QLabel("📈 大盘指数")
        market_title.setFont(QFont("微软雅黑", 16, QFont.Weight.Bold))
        market_title.setStyleSheet("color: #2c3e50; padding: 5px;")
        title_layout.addWidget(market_title)
        
        # 市场状态指示
        market_status = QLabel("🟢 交易中")
        market_status.setFont(QFont("微软雅黑", 12, QFont.Weight.Bold))
        market_status.setStyleSheet("color: #27ae60; padding: 5px;")
        title_layout.addWidget(market_status)
        
        title_layout.addStretch()
        
        # 快捷按钮
        refresh_btn = QPushButton("🔄 刷新")
        refresh_btn.setFixedSize(80, 35)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        refresh_btn.clicked.connect(self.refresh_all_data)
        title_layout.addWidget(refresh_btn)
        
        market_layout.addWidget(title_container)
        
        # 大盘概览组件 - 使用增强版
        self.market_overview = EnhancedMarketOverviewWidget()
        self.market_overview.setStyleSheet("background-color: transparent; border: none;")
        market_layout.addWidget(self.market_overview, 1)
        
        main_layout.addWidget(market_frame)
        
    def setup_large_sector_area(self, main_layout):
        """设置大尺寸板块信息区域"""
        # 创建板块区域容器
        sector_frame = QFrame()
        sector_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        sector_frame.setFixedHeight(320)  # 大幅增加高度
        sector_frame.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 2px solid #e74c3c;
                border-radius: 10px;
                margin: 5px;
            }
        """)
        
        sector_layout = QVBoxLayout(sector_frame)
        sector_layout.setContentsMargins(15, 15, 15, 15)
        sector_layout.setSpacing(10)
        
        # 标题区域
        title_container = QWidget()
        title_layout = QHBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        
        sector_title = QLabel("🏭 热门板块")
        sector_title.setFont(QFont("微软雅黑", 16, QFont.Weight.Bold))
        sector_title.setStyleSheet("color: #2c3e50; padding: 5px;")
        title_layout.addWidget(sector_title)
        
        title_layout.addStretch()
        
        # 自选股按钮
        pool_btn = QPushButton("⭐ 自选股")
        pool_btn.setFixedSize(80, 35)
        pool_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
        """)
        pool_btn.clicked.connect(self.show_stock_pool)
        title_layout.addWidget(pool_btn)
        
        sector_layout.addWidget(title_container)
        
        # 内容区域 - 板块信息和自选股并排显示
        content_container = QWidget()
        content_layout = QHBoxLayout(content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(15)
        
        # 板块信息组件 (70%)
        self.sector_info = SectorInfoPanel()
        self.sector_info.setStyleSheet("background-color: transparent; border: none;")
        content_layout.addWidget(self.sector_info, 7)
        
        # 自选股组件 (30%)
        self.stock_pool = StockPoolWidget()
        self.stock_pool.setStyleSheet("""
            StockPoolWidget {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        content_layout.addWidget(self.stock_pool, 3)
        
        sector_layout.addWidget(content_container, 1)
        main_layout.addWidget(sector_frame)
        
    def setup_stock_content_area(self, main_layout):
        """设置股票内容区域"""
        # 创建标签页容器
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(False)
        self.tab_widget.setMovable(True)
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        
        # 股票列表标签页
        self.stock_list_widget = StockListWidget()
        self.tab_widget.addTab(self.stock_list_widget, "📋 股票行情")
        
        # 图表分析标签页
        self.chart_view = ChartViewWidget()
        self.tab_widget.addTab(self.chart_view, "📊 技术分析")
        
        # 数据分析标签页
        analysis_widget = self.create_analysis_tab()
        self.tab_widget.addTab(analysis_widget, "🔬 数据挖掘")
        
        main_layout.addWidget(self.tab_widget, 1)  # 占用剩余空间
        
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
        
    def show_stock_pool(self):
        """显示自选股管理窗口"""
        try:
            QMessageBox.information(self, "自选股", "自选股管理功能开发中...")
        except Exception as e:
            logger.error(f"显示自选股失败: {e}")
    
    def apply_professional_theme(self):
        """应用专业主题 - 同花顺风格"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f6fa;
                color: #2c3e50;
            }
            QMenuBar {
                background-color: #34495e;
                color: white;
                padding: 5px;
                font-weight: bold;
                font-size: 13px;
            }
            QMenuBar::item {
                padding: 8px 12px;
                border-radius: 4px;
            }
            QMenuBar::item:selected {
                background-color: #3498db;
            }
            QToolBar {
                background-color: #ecf0f1;
                border: 1px solid #bdc3c7;
                spacing: 5px;
                padding: 8px;
                font-size: 12px;
                font-weight: bold;
            }
            QToolBar QToolButton {
                padding: 8px 12px;
                border-radius: 4px;
                border: 1px solid transparent;
            }
            QToolBar QToolButton:hover {
                background-color: #d5dbdb;
                border: 1px solid #95a5a6;
            }
            QTabWidget::pane {
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                background-color: white;
                margin-top: 5px;
            }
            QTabBar::tab {
                background-color: #ecf0f1;
                color: #2c3e50;
                padding: 12px 24px;
                margin-right: 3px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: bold;
                font-size: 13px;
                min-width: 100px;
            }
            QTabBar::tab:selected {
                background-color: #3498db;
                color: white;
            }
            QTabBar::tab:hover {
                background-color: #d5dbdb;
            }
            QStatusBar {
                background-color: #34495e;
                color: white;
                font-weight: bold;
                font-size: 12px;
                padding: 5px;
            }
        """)
        
    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu('文件')
        
        new_action = QAction('新建窗口', self)
        new_action.setShortcut('Ctrl+N')
        new_action.triggered.connect(self.new_window)
        file_menu.addAction(new_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('退出', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 工具菜单
        tools_menu = menubar.addMenu('工具')
        
        strategy_action = QAction('策略选股', self)
        strategy_action.setShortcut('Ctrl+S')
        strategy_action.triggered.connect(self.open_strategy_window)
        tools_menu.addAction(strategy_action)
        
        refresh_action = QAction('刷新数据', self)
        refresh_action.setShortcut('F5')
        refresh_action.triggered.connect(self.refresh_all_data)
        tools_menu.addAction(refresh_action)
        
        # 视图菜单
        view_menu = menubar.addMenu('视图')
        
        fullscreen_action = QAction('全屏', self)
        fullscreen_action.setShortcut('F11')
        fullscreen_action.triggered.connect(self.toggle_fullscreen)
        view_menu.addAction(fullscreen_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu('帮助')
        
        about_action = QAction('关于', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def create_tool_bar(self):
        """创建工具栏"""
        toolbar = self.addToolBar('主工具栏')
        toolbar.setMovable(False)
        
        # 刷新按钮
        refresh_action = QAction('🔄 刷新', self)
        refresh_action.setShortcut('F5')
        refresh_action.triggered.connect(self.refresh_all_data)
        toolbar.addAction(refresh_action)
        
        toolbar.addSeparator()
        
        # 策略选股按钮
        strategy_action = QAction('🎯 策略选股', self)
        strategy_action.setShortcut('Ctrl+S')
        strategy_action.triggered.connect(self.open_strategy_window)
        toolbar.addAction(strategy_action)
        
        toolbar.addSeparator()
        
        # 全屏按钮
        fullscreen_action = QAction('🖥️ 全屏', self)
        fullscreen_action.setShortcut('F11')
        fullscreen_action.triggered.connect(self.toggle_fullscreen)
        toolbar.addAction(fullscreen_action)
        
    def create_status_bar(self):
        """创建状态栏"""
        self.status_bar = self.statusBar()
        self.status_bar.showMessage('就绪 - A股投资分析工具 v2.0')
        
        # 添加右侧状态信息
        self.connection_status = QLabel('🟢 数据连接正常')
        self.status_bar.addPermanentWidget(self.connection_status)
        
        self.update_time = QLabel('更新时间: --:--:--')
        self.status_bar.addPermanentWidget(self.update_time)
        
    def setup_connections(self):
        """设置信号连接"""
        try:
            # 股票池选择信号
            if hasattr(self.stock_pool, 'stock_selected'):
                self.stock_pool.stock_selected.connect(self.on_stock_selected)
        
            # 股票列表选择信号
            if hasattr(self.stock_list_widget, 'stock_selected'):
                self.stock_list_widget.stock_selected.connect(self.on_stock_selected)
        
            # 板块信息选择信号
            if hasattr(self.sector_info, 'sector_selected'):
                self.sector_info.sector_selected.connect(self.on_sector_selected)
                
        except Exception as e:
            logger.warning(f"设置信号连接失败: {e}")
            
    def setup_timer(self):
        """设置定时器"""
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
            if hasattr(self, 'market_overview'):
                self.market_overview.refresh_data()
                
            # 更新板块数据
            if hasattr(self, 'sector_info'):
                self.sector_info.refresh_data()
                
            # 更新时间显示
            from datetime import datetime
            current_time = datetime.now().strftime("%H:%M:%S")
            self.update_time.setText(f'更新时间: {current_time}')
            
            logger.debug("数据更新完成")
            
        except Exception as e:
            logger.error(f"数据更新失败: {e}")
            self.status_bar.showMessage(f"数据更新失败: {e}", 3000)
    
    def on_stock_selected(self, stock_code: str, stock_name: str):
        """处理股票选择事件"""
        logger.info(f"选择股票: {stock_code} - {stock_name}")
        
        # 更新图表视图
        if hasattr(self, 'chart_view'):
            self.chart_view.load_stock(stock_code, stock_name)
        
        # 切换到图表标签页
        self.tab_widget.setCurrentIndex(1)
        
        self.status_bar.showMessage(f'已选择股票: {stock_name} ({stock_code})', 3000)
    
    def on_sector_selected(self, sector_code: str, sector_name: str):
        """处理板块选择事件"""
        logger.info(f"选择板块: {sector_code} - {sector_name}")
        
        # 获取板块成分股
        try:
            from src.data.sector_data import sector_data_provider
            stocks = sector_data_provider.get_sector_stocks(sector_code)
            
            if stocks and hasattr(self, 'stock_list_widget'):
                self.stock_list_widget.filter_by_stocks(stocks)
                self.tab_widget.setCurrentIndex(0)  # 切换到股票列表
                self.status_bar.showMessage(f'已切换到板块: {sector_name}', 3000)
            else:
                self.status_bar.showMessage(f'板块 {sector_name} 暂无数据', 3000)
                
        except Exception as e:
            logger.error(f"获取板块成分股失败: {e}")
            self.status_bar.showMessage(f'获取板块数据失败: {e}', 3000)
        
    def refresh_all_data(self):
        """刷新所有数据"""
        self.status_bar.showMessage('正在刷新数据...', 2000)
        self.update_data()
        
        # 也刷新股票列表
        if hasattr(self, 'stock_list_widget'):
            self.stock_list_widget.refresh_data()
            
        logger.info("手动刷新数据完成")
        
    def new_window(self):
        """新建窗口"""
        try:
            new_window = MainWindow()
            new_window.show()
        except Exception as e:
            logger.error(f"创建新窗口失败: {e}")
            
    def open_strategy_window(self):
        """打开策略选股窗口"""
        try:
            from src.ui.strategy_window import StrategyWindow
            self.strategy_window = StrategyWindow()
            self.strategy_window.show()
        except Exception as e:
            logger.error(f"打开策略窗口失败: {e}")
            QMessageBox.warning(self, "错误", f"无法打开策略选股窗口: {e}")
            
    def toggle_fullscreen(self):
        """切换全屏模式"""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
    
    def show_about(self):
        """显示关于对话框"""
        QMessageBox.about(self, "关于", 
                         "📊 A股投资分析工具 v2.0\\n\\n"
                         "专业级股票分析平台\\n"
                         "设计原则: 响应速度优先 | 高度可定制 | 直观易用 | 数据准确\\n\\n"
                         "© 2025 股票分析工具")
            
    def restore_window_state(self):
        """恢复窗口状态"""
        try:
            size = config_manager.get('ui.window_size', [1600, 1000])
            position = config_manager.get('ui.window_position', [100, 100])
            
            self.resize(size[0], size[1])
            self.move(position[0], position[1])
        except Exception as e:
            logger.warning(f"恢复窗口状态失败: {e}")
        
    def save_window_state(self):
        """保存窗口状态"""
        try:
            config_manager.set('ui.window_size', [self.width(), self.height()])
            config_manager.set('ui.window_position', [self.x(), self.y()])
            config_manager.save()
        except Exception as e:
            logger.warning(f"保存窗口状态失败: {e}")
        
    def closeEvent(self, event):
        """窗口关闭事件"""
        try:
            self.save_window_state()
            
            # 停止定时器
            if hasattr(self, 'update_timer'):
                self.update_timer.stop()
                
            logger.info("应用程序正在退出...")
            event.accept()
            
        except Exception as e:
            logger.error(f"关闭程序时发生错误: {e}")
            event.accept()
