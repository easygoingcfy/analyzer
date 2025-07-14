#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
板块信息面板
显示行业板块和概念板块的实时数据和热度排行
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                            QTableWidgetItem, QTabWidget, QLabel, QPushButton,
                            QComboBox, QLineEdit, QSplitter, QHeaderView,
                            QMessageBox, QMenu, QFrame)
from PyQt6.QtCore import QTimer, Qt, pyqtSignal, QThread, pyqtSlot
from PyQt6.QtGui import QFont, QColor, QAction
import pandas as pd
from src.data.sector_data import sector_data_provider
from src.utils.logger import get_logger

logger = get_logger(__name__)

class SectorDataWorker(QThread):
    """板块数据获取工作线程"""
    data_ready = pyqtSignal(pd.DataFrame)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, sector_type='all'):
        super().__init__()
        self.sector_type = sector_type
        self.running = True
    
    def run(self):
        """运行数据获取"""
        try:
            if self.running:
                data = sector_data_provider.get_sector_realtime_data()
                if not data.empty:
                    # 筛选板块类型
                    if self.sector_type == 'industry':
                        data = data[data['板块类型'] == '行业板块']
                    elif self.sector_type == 'concept':
                        data = data[data['板块类型'] == '概念板块']
                    
                    self.data_ready.emit(data)
                else:
                    self.error_occurred.emit("无法获取板块数据")
        except Exception as e:
            self.error_occurred.emit(f"获取板块数据失败: {str(e)}")
    
    def stop(self):
        """停止线程"""
        self.running = False

class SectorInfoPanel(QWidget):
    """板块信息面板"""
    
    sector_selected = pyqtSignal(str, str)  # 板块代码, 板块名称
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.setup_timer()
        self.worker = None
        
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # 标题和控制区域
        header_layout = QHBoxLayout()
        
        title_label = QLabel("📊 板块信息")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title_label.setFont(title_font)
        
        # 板块类型选择
        self.sector_type_combo = QComboBox()
        self.sector_type_combo.addItems(['全部板块', '行业板块', '概念板块'])
        self.sector_type_combo.currentTextChanged.connect(self.on_sector_type_changed)
        
        # 搜索框
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索板块...")
        self.search_input.textChanged.connect(self.on_search_text_changed)
        
        # 刷新按钮
        self.refresh_btn = QPushButton("🔄 刷新")
        self.refresh_btn.clicked.connect(self.refresh_data)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(QLabel("类型:"))
        header_layout.addWidget(self.sector_type_combo)
        header_layout.addWidget(self.search_input)
        header_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(header_layout)
        
        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        
        # 实时数据标签页
        self.realtime_tab = self.create_realtime_tab()
        self.tab_widget.addTab(self.realtime_tab, "实时数据")
        
        # 热度排行标签页
        self.hot_tab = self.create_hot_sectors_tab()
        self.tab_widget.addTab(self.hot_tab, "热度排行")
        
        layout.addWidget(self.tab_widget)
        
        # 状态标签
        self.status_label = QLabel("就绪")
        self.status_label.setStyleSheet("color: #666; font-size: 11px;")
        layout.addWidget(self.status_label)
    
    def create_realtime_tab(self) -> QWidget:
        """创建实时数据标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 5, 0, 0)
        
        # 板块数据表格
        self.sectors_table = QTableWidget()
        self.sectors_table.setAlternatingRowColors(True)
        self.sectors_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.sectors_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.sectors_table.customContextMenuRequested.connect(self.show_sector_context_menu)
        self.sectors_table.itemDoubleClicked.connect(self.on_sector_double_clicked)
        
        # 设置表格列
        columns = ['板块名称', '类型', '成分股数', '平均涨跌幅', '涨停数', '跌停数', 
                  '总成交额(亿)', '平均换手率', '领涨股', '热度指数', '更新时间']
        self.sectors_table.setColumnCount(len(columns))
        self.sectors_table.setHorizontalHeaderLabels(columns)
        
        # 设置列宽
        header = self.sectors_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)  # 板块名称
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)  # 类型
        header.setSectionResizeMode(9, QHeaderView.ResizeMode.Fixed)  # 热度指数
        header.resizeSection(0, 120)
        header.resizeSection(1, 80)
        header.resizeSection(9, 80)
        
        # 其他列自适应
        for i in [2, 3, 4, 5, 6, 7, 8, 10]:
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)
        
        layout.addWidget(self.sectors_table)
        return widget
    
    def create_hot_sectors_tab(self) -> QWidget:
        """创建热度排行标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 5, 0, 0)
        
        # 排行榜控制
        control_layout = QHBoxLayout()
        
        control_layout.addWidget(QLabel("排行榜类型:"))
        self.hot_type_combo = QComboBox()
        self.hot_type_combo.addItems(['全部', '行业板块', '概念板块'])
        self.hot_type_combo.currentTextChanged.connect(self.refresh_hot_sectors)
        
        control_layout.addWidget(self.hot_type_combo)
        control_layout.addStretch()
        
        layout.addLayout(control_layout)
        
        # 热度排行表格
        self.hot_table = QTableWidget()
        self.hot_table.setAlternatingRowColors(True)
        self.hot_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.hot_table.itemDoubleClicked.connect(self.on_hot_sector_double_clicked)
        
        # 设置热度排行表格列
        hot_columns = ['排名', '板块名称', '类型', '平均涨跌幅', '热度指数', '涨停数', '领涨股']
        self.hot_table.setColumnCount(len(hot_columns))
        self.hot_table.setHorizontalHeaderLabels(hot_columns)
        
        # 设置热度表格列宽
        hot_header = self.hot_table.horizontalHeader()
        hot_header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)  # 排名
        hot_header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)  # 板块名称
        hot_header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)  # 类型
        hot_header.resizeSection(0, 60)
        hot_header.resizeSection(1, 120)
        hot_header.resizeSection(2, 80)
        
        for i in [3, 4, 5, 6]:
            hot_header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)
        
        layout.addWidget(self.hot_table)
        return widget
    
    def setup_timer(self):
        """设置定时器"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_data)
        self.timer.start(30000)  # 30秒刷新一次
    
    def refresh_data(self):
        """刷新数据"""
        try:
            self.status_label.setText("正在获取板块数据...")
            self.refresh_btn.setEnabled(False)
            
            # 获取当前板块类型
            sector_type_map = {
                '全部板块': 'all',
                '行业板块': 'industry', 
                '概念板块': 'concept'
            }
            sector_type = sector_type_map.get(self.sector_type_combo.currentText(), 'all')
            
            # 停止之前的工作线程
            if self.worker and self.worker.isRunning():
                self.worker.stop()
                self.worker.wait()
            
            # 启动新的工作线程
            self.worker = SectorDataWorker(sector_type)
            self.worker.data_ready.connect(self.update_sectors_data)
            self.worker.error_occurred.connect(self.handle_error)
            self.worker.finished.connect(self.on_data_loading_finished)
            self.worker.start()
            
        except Exception as e:
            self.handle_error(f"刷新数据失败: {str(e)}")
    
    @pyqtSlot(pd.DataFrame)
    def update_sectors_data(self, data: pd.DataFrame):
        """更新板块数据"""
        try:
            if data.empty:
                self.status_label.setText("暂无板块数据")
                return
            
            # 应用搜索过滤
            search_text = self.search_input.text().strip()
            if search_text:
                mask = data['板块名称'].str.contains(search_text, case=False, na=False)
                data = data[mask]
            
            # 更新实时数据表格
            self.sectors_table.setRowCount(len(data))
            
            for row, (_, sector) in enumerate(data.iterrows()):
                # 板块名称
                name_item = QTableWidgetItem(sector['板块名称'])
                name_item.setData(Qt.ItemDataRole.UserRole, sector['板块代码'])
                self.sectors_table.setItem(row, 0, name_item)
                
                # 板块类型
                type_item = QTableWidgetItem(sector['板块类型'])
                self.sectors_table.setItem(row, 1, type_item)
                
                # 成分股数量
                count_item = QTableWidgetItem(str(sector['成分股数量']))
                self.sectors_table.setItem(row, 2, count_item)
                
                # 平均涨跌幅（带颜色）
                change_pct = sector['平均涨跌幅']
                change_item = QTableWidgetItem(f"{change_pct:+.2f}%")
                if change_pct > 0:
                    change_item.setForeground(QColor(220, 38, 38))  # 红色
                elif change_pct < 0:
                    change_item.setForeground(QColor(34, 197, 94))  # 绿色
                self.sectors_table.setItem(row, 3, change_item)
                
                # 涨停数量
                limit_up_item = QTableWidgetItem(str(sector['涨停数量']))
                if sector['涨停数量'] > 0:
                    limit_up_item.setForeground(QColor(220, 38, 38))
                self.sectors_table.setItem(row, 4, limit_up_item)
                
                # 跌停数量
                limit_down_item = QTableWidgetItem(str(sector['跌停数量']))
                if sector['跌停数量'] > 0:
                    limit_down_item.setForeground(QColor(34, 197, 94))
                self.sectors_table.setItem(row, 5, limit_down_item)
                
                # 总成交额（转换为亿元）
                amount_item = QTableWidgetItem(f"{sector['总成交额']/100000000:.1f}")
                self.sectors_table.setItem(row, 6, amount_item)
                
                # 平均换手率
                turnover_item = QTableWidgetItem(f"{sector['平均换手率']:.2f}%")
                self.sectors_table.setItem(row, 7, turnover_item)
                
                # 领涨股
                gainer_item = QTableWidgetItem(sector['领涨股'])
                self.sectors_table.setItem(row, 8, gainer_item)
                
                # 热度指数
                heat_item = QTableWidgetItem(f"{sector['热度指数']:.1f}")
                heat_value = sector['热度指数']
                if heat_value >= 80:
                    heat_item.setForeground(QColor(220, 38, 38))  # 高热度红色
                elif heat_value >= 60:
                    heat_item.setForeground(QColor(251, 146, 60))  # 中热度橙色
                self.sectors_table.setItem(row, 9, heat_item)
                
                # 更新时间
                time_item = QTableWidgetItem(sector['更新时间'])
                self.sectors_table.setItem(row, 10, time_item)
            
            # 更新热度排行
            self.refresh_hot_sectors()
            
            self.status_label.setText(f"已更新 {len(data)} 个板块数据 - {pd.Timestamp.now().strftime('%H:%M:%S')}")
            
        except Exception as e:
            logger.error(f"更新板块数据失败: {e}")
            self.status_label.setText(f"更新数据失败: {str(e)}")
    
    def refresh_hot_sectors(self):
        """刷新热度排行"""
        try:
            # 获取热度排行类型
            hot_type_map = {
                '全部': 'all',
                '行业板块': 'industry',
                '概念板块': 'concept'
            }
            hot_type = hot_type_map.get(self.hot_type_combo.currentText(), 'all')
            
            # 获取热门板块数据
            hot_data = sector_data_provider.get_hot_sectors(hot_type, limit=20)
            
            if hot_data.empty:
                self.hot_table.setRowCount(0)
                return
            
            # 更新热度排行表格
            self.hot_table.setRowCount(len(hot_data))
            
            for row, (_, sector) in enumerate(hot_data.iterrows()):
                # 排名
                rank_item = QTableWidgetItem(str(row + 1))
                rank_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if row < 3:  # 前三名特殊颜色
                    colors = [QColor(255, 215, 0), QColor(192, 192, 192), QColor(205, 127, 50)]
                    rank_item.setForeground(colors[row])
                self.hot_table.setItem(row, 0, rank_item)
                
                # 板块名称
                name_item = QTableWidgetItem(sector['板块名称'])
                name_item.setData(Qt.ItemDataRole.UserRole, sector['板块代码'])
                self.hot_table.setItem(row, 1, name_item)
                
                # 类型
                type_item = QTableWidgetItem(sector['板块类型'])
                self.hot_table.setItem(row, 2, type_item)
                
                # 平均涨跌幅
                change_pct = sector['平均涨跌幅']
                change_item = QTableWidgetItem(f"{change_pct:+.2f}%")
                if change_pct > 0:
                    change_item.setForeground(QColor(220, 38, 38))
                elif change_pct < 0:
                    change_item.setForeground(QColor(34, 197, 94))
                self.hot_table.setItem(row, 3, change_item)
                
                # 热度指数
                heat_item = QTableWidgetItem(f"{sector['热度指数']:.1f}")
                self.hot_table.setItem(row, 4, heat_item)
                
                # 涨停数
                limit_up_item = QTableWidgetItem(str(sector['涨停数量']))
                self.hot_table.setItem(row, 5, limit_up_item)
                
                # 领涨股
                gainer_item = QTableWidgetItem(sector['领涨股'])
                self.hot_table.setItem(row, 6, gainer_item)
                
        except Exception as e:
            logger.error(f"刷新热度排行失败: {e}")
    
    @pyqtSlot(str)
    def handle_error(self, error_msg: str):
        """处理错误"""
        logger.error(error_msg)
        self.status_label.setText(f"错误: {error_msg}")
        QMessageBox.warning(self, "错误", error_msg)
    
    @pyqtSlot()
    def on_data_loading_finished(self):
        """数据加载完成"""
        self.refresh_btn.setEnabled(True)
    
    def on_sector_type_changed(self, text: str):
        """板块类型改变"""
        self.refresh_data()
    
    def on_search_text_changed(self, text: str):
        """搜索文本改变"""
        # 实时过滤当前数据
        if hasattr(self, 'sectors_table'):
            self.filter_table_data(self.sectors_table, text, 0)  # 在板块名称列中搜索
    
    def filter_table_data(self, table: QTableWidget, search_text: str, column: int):
        """过滤表格数据"""
        for row in range(table.rowCount()):
            item = table.item(row, column)
            if item:
                # 如果搜索文本为空或者在项目文本中找到，显示该行
                visible = not search_text or search_text.lower() in item.text().lower()
                table.setRowHidden(row, not visible)
    
    def show_sector_context_menu(self, position):
        """显示板块右键菜单"""
        if self.sectors_table.itemAt(position) is None:
            return
        
        menu = QMenu(self)
        
        view_action = QAction("📈 查看板块详情", self)
        view_action.triggered.connect(self.view_sector_detail)
        menu.addAction(view_action)
        
        stocks_action = QAction("📋 查看成分股", self)
        stocks_action.triggered.connect(self.view_sector_stocks)
        menu.addAction(stocks_action)
        
        menu.addSeparator()
        
        copy_action = QAction("📋 复制板块名称", self)
        copy_action.triggered.connect(self.copy_sector_name)
        menu.addAction(copy_action)
        
        menu.exec(self.sectors_table.mapToGlobal(position))
    
    def on_sector_double_clicked(self, item):
        """板块双击事件"""
        self.view_sector_detail()
    
    def on_hot_sector_double_clicked(self, item):
        """热度排行双击事件"""
        row = item.row()
        name_item = self.hot_table.item(row, 1)
        if name_item:
            sector_code = name_item.data(Qt.ItemDataRole.UserRole)
            sector_name = name_item.text()
            self.sector_selected.emit(sector_code, sector_name)
    
    def view_sector_detail(self):
        """查看板块详情"""
        current_row = self.sectors_table.currentRow()
        if current_row >= 0:
            name_item = self.sectors_table.item(current_row, 0)
            if name_item:
                sector_code = name_item.data(Qt.ItemDataRole.UserRole)
                sector_name = name_item.text()
                self.sector_selected.emit(sector_code, sector_name)
    
    def view_sector_stocks(self):
        """查看板块成分股"""
        current_row = self.sectors_table.currentRow()
        if current_row >= 0:
            name_item = self.sectors_table.item(current_row, 0)
            if name_item:
                sector_code = name_item.data(Qt.ItemDataRole.UserRole)
                sector_name = name_item.text()
                
                # 获取成分股
                stocks = sector_data_provider.get_sector_stocks(sector_code)
                if stocks:
                    stocks_text = "\n".join([f"• {stock}" for stock in stocks])
                    QMessageBox.information(self, f"{sector_name} - 成分股", 
                                          f"成分股列表 ({len(stocks)}只):\n\n{stocks_text}")
                else:
                    QMessageBox.information(self, "提示", f"{sector_name} 暂无成分股数据")
    
    def copy_sector_name(self):
        """复制板块名称"""
        current_row = self.sectors_table.currentRow()
        if current_row >= 0:
            name_item = self.sectors_table.item(current_row, 0)
            if name_item:
                from PyQt6.QtWidgets import QApplication
                QApplication.clipboard().setText(name_item.text())
                self.status_label.setText(f"已复制: {name_item.text()}")
    
    def closeEvent(self, event):
        """关闭事件"""
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait()
        event.accept()
