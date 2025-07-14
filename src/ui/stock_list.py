from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QLineEdit, QPushButton,
                             QComboBox, QLabel, QMenu, QMessageBox, QAbstractItemView)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QSortFilterProxyModel
from PyQt6.QtGui import QFont, QColor, QAction, QBrush
import pandas as pd
from src.data.stock_data import data_provider
from src.utils.config import config_manager
from src.utils.logger import get_logger

logger = get_logger(__name__)

class StockListWidget(QWidget):
    """股票列表组件"""
    
    stock_selected = pyqtSignal(str, str)  # 股票代码, 股票名称
    
    def __init__(self):
        super().__init__()
        self.current_data = pd.DataFrame()
        self.init_ui()
        self.load_initial_data()
        
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # 工具栏
        self.setup_toolbar(layout)
        
        # 股票表格
        self.setup_table(layout)
        
    def setup_toolbar(self, parent_layout):
        """设置工具栏"""
        toolbar_layout = QHBoxLayout()
        
        # 搜索框
        search_label = QLabel("搜索:")
        toolbar_layout.addWidget(search_label)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入股票代码或名称...")
        self.search_input.textChanged.connect(self.on_search_changed)
        toolbar_layout.addWidget(self.search_input)
        
        # 刷新按钮
        refresh_btn = QPushButton("刷新")
        refresh_btn.clicked.connect(self.refresh_data)
        toolbar_layout.addWidget(refresh_btn)
        
        # 显示模式选择
        mode_label = QLabel("显示:")
        toolbar_layout.addWidget(mode_label)
        
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["热门股票", "全部股票", "自选股票"])
        self.mode_combo.currentTextChanged.connect(self.on_mode_changed)
        toolbar_layout.addWidget(self.mode_combo)
        
        toolbar_layout.addStretch()
        parent_layout.addLayout(toolbar_layout)
        
    def setup_table(self, parent_layout):
        """设置表格"""
        self.table = QTableWidget()
        
        # 设置列
        columns = config_manager.get('display.columns', [
            '代码', '名称', '现价', '涨跌幅', '涨跌额', 
            '成交量', '成交额', '换手率', '市盈率', '市净率'
        ])
        
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)
        
        # 表格属性设置
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setSortingEnabled(True)
        
        # 设置列宽
        header = self.table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)  # 代码列固定宽度
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)  # 名称列固定宽度
        self.table.setColumnWidth(0, 80)
        self.table.setColumnWidth(1, 100)
        
        # 连接信号
        self.table.cellDoubleClicked.connect(self.on_cell_double_clicked)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        
        parent_layout.addWidget(self.table)
        
    def load_initial_data(self):
        """加载初始数据"""
        self.refresh_data()
        
    def refresh_data(self):
        """刷新数据"""
        try:
            mode = self.mode_combo.currentText()
            
            if mode == "热门股票":
                # 获取热门股票实时数据
                data = data_provider.get_real_time_data()
            elif mode == "全部股票":
                # 获取股票列表（基础信息）
                data = data_provider.get_stock_list()
                # 为了演示，只显示前100只股票的实时数据
                if not data.empty:
                    symbols = data['代码'].head(100).tolist()
                    data = data_provider.get_real_time_data(symbols)
            else:  # 自选股票
                # 从配置获取自选股列表
                my_stocks = config_manager.get('stock_pools.my_stocks', [])
                if my_stocks:
                    data = data_provider.get_real_time_data(my_stocks)
                else:
                    data = pd.DataFrame()
            
            self.current_data = data
            self.update_table(data)
            
            logger.info(f"股票列表数据刷新完成，共{len(data)}条记录")
            
        except Exception as e:
            logger.error(f"刷新股票列表数据失败: {e}")
            
    def update_table(self, data: pd.DataFrame):
        """更新表格数据"""
        if data.empty:
            self.table.setRowCount(0)
            return
            
        self.table.setRowCount(len(data))
        
        # 获取列映射
        column_mapping = {
            '代码': '代码',
            '名称': '名称', 
            '现价': '最新价',
            '涨跌幅': '涨跌幅',
            '涨跌额': '涨跌额',
            '成交量': '成交量',
            '成交额': '成交额',
            '换手率': '换手率',
            '市盈率': '市盈率-动态',
            '市净率': '市净率'
        }
        
        for row in range(len(data)):
            row_data = data.iloc[row]
            
            for col, header in enumerate(self.table.horizontalHeaderItem(col).text() for col in range(self.table.columnCount())):
                if header in column_mapping:
                    data_key = column_mapping[header]
                    if data_key in row_data:
                        value = row_data[data_key]
                        
                        # 格式化数值
                        formatted_value = self.format_value(header, value)
                        
                        item = QTableWidgetItem(str(formatted_value))
                        
                        # 设置数值类型的排序
                        if header in ['现价', '涨跌幅', '涨跌额', '成交量', '成交额', '换手率', '市盈率', '市净率']:
                            try:
                                item.setData(Qt.ItemDataRole.UserRole, float(value) if value != '--' and pd.notna(value) else 0)
                            except:
                                item.setData(Qt.ItemDataRole.UserRole, 0)
                        
                        # 设置颜色
                        if header in ['涨跌幅', '涨跌额']:
                            try:
                                val = float(value) if value != '--' and pd.notna(value) else 0
                                if val > 0:
                                    item.setForeground(QBrush(QColor(255, 0, 0)))  # 红色
                                elif val < 0:
                                    item.setForeground(QBrush(QColor(0, 128, 0)))  # 绿色
                            except:
                                pass
                        
                        self.table.setItem(row, col, item)
                    else:
                        item = QTableWidgetItem("--")
                        self.table.setItem(row, col, item)
        
        # 应用排序
        sort_column = config_manager.get('display.sort_column', '涨跌幅')
        sort_order = config_manager.get('display.sort_order', 'desc')
        
        headers = [self.table.horizontalHeaderItem(col).text() for col in range(self.table.columnCount())]
        if sort_column in headers:
            col_index = headers.index(sort_column)
            order = Qt.SortOrder.DescendingOrder if sort_order == 'desc' else Qt.SortOrder.AscendingOrder
            self.table.sortItems(col_index, order)
            
    def format_value(self, column: str, value) -> str:
        """格式化数值显示"""
        if pd.isna(value) or value == '' or value is None:
            return '--'
            
        try:
            if column in ['现价', '涨跌额']:
                return f"{float(value):.2f}"
            elif column == '涨跌幅':
                return f"{float(value):.2f}%"
            elif column in ['成交量', '成交额']:
                val = float(value)
                if val >= 100000000:  # 亿
                    return f"{val/100000000:.1f}亿"
                elif val >= 10000:  # 万
                    return f"{val/10000:.1f}万"
                else:
                    return f"{val:.0f}"
            elif column == '换手率':
                return f"{float(value):.2f}%"
            elif column in ['市盈率', '市净率']:
                return f"{float(value):.2f}"
            else:
                return str(value)
        except:
            return str(value) if value is not None else '--'
            
    def refresh_data(self):
        """刷新股票数据"""
        try:
            # 获取股票数据
            stock_data = data_provider.get_stock_list()
            self.current_data = stock_data
            
            # 保留当前搜索状态
            current_search = self.search_input.text().strip()
            
            if current_search:
                # 如果有搜索条件，应用过滤
                self.on_search_changed(current_search)
            else:
                # 否则显示全部数据
                self.update_table(stock_data)
            
            logger.info(f"股票列表数据刷新完成，共{len(stock_data)}条记录")
            
        except Exception as e:
            logger.error(f"刷新股票数据失败: {e}")
            
    def on_search_changed(self, text: str):
        """搜索文本改变"""
        if not text.strip():
            self.update_table(self.current_data)
            return
            
        try:
            # 过滤数据 - 支持代码和名称搜索
            filtered_data = self.current_data[
                self.current_data['代码'].str.contains(text, case=False, na=False) |
                self.current_data['名称'].str.contains(text, case=False, na=False)
            ]
            
            self.update_table(filtered_data)
            logger.debug(f"搜索'{text}'找到{len(filtered_data)}条记录")
            
        except Exception as e:
            logger.error(f"搜索失败: {e}")
            self.update_table(self.current_data)
        
    def on_mode_changed(self, mode: str):
        """显示模式改变"""
        self.refresh_data()
        
    def on_cell_double_clicked(self, row: int, column: int):
        """单元格双击事件"""
        # 获取股票代码和名称
        code_item = self.table.item(row, 0)  # 代码列
        name_item = self.table.item(row, 1)  # 名称列
        
        if code_item and name_item:
            stock_code = code_item.text()
            stock_name = name_item.text()
            self.stock_selected.emit(stock_code, stock_name)
            
    def show_context_menu(self, position):
        """显示右键菜单"""
        if self.table.itemAt(position) is None:
            return
            
        row = self.table.currentRow()
        if row < 0:
            return
            
        code_item = self.table.item(row, 0)
        name_item = self.table.item(row, 1)
        
        if not code_item or not name_item:
            return
            
        stock_code = code_item.text()
        stock_name = name_item.text()
        
        menu = QMenu(self)
        
        # 查看详情
        view_action = QAction("查看详情", self)
        view_action.triggered.connect(lambda: self.stock_selected.emit(stock_code, stock_name))
        menu.addAction(view_action)
        
        menu.addSeparator()
        
        # 添加到自选
        add_action = QAction("添加到自选", self)
        add_action.triggered.connect(lambda: self.add_to_favorites(stock_code, stock_name))
        menu.addAction(add_action)
        
        # 从自选移除
        remove_action = QAction("从自选移除", self)
        remove_action.triggered.connect(lambda: self.remove_from_favorites(stock_code))
        menu.addAction(remove_action)
        
        menu.exec(self.table.mapToGlobal(position))
        
    def add_to_favorites(self, stock_code: str, stock_name: str):
        """添加到自选"""
        my_stocks = config_manager.get('stock_pools.my_stocks', [])
        if stock_code not in my_stocks:
            my_stocks.append(stock_code)
            config_manager.set('stock_pools.my_stocks', my_stocks)
            QMessageBox.information(self, "成功", f"已将 {stock_name}({stock_code}) 添加到自选股")
        else:
            QMessageBox.information(self, "提示", f"{stock_name}({stock_code}) 已在自选股中")
            
    def remove_from_favorites(self, stock_code: str):
        """从自选移除"""
        my_stocks = config_manager.get('stock_pools.my_stocks', [])
        if stock_code in my_stocks:
            my_stocks.remove(stock_code)
            config_manager.set('stock_pools.my_stocks', my_stocks)
            QMessageBox.information(self, "成功", f"已从自选股中移除 {stock_code}")
            
            # 如果当前显示的是自选股，刷新数据
            if self.mode_combo.currentText() == "自选股票":
                self.refresh_data()
        else:
            QMessageBox.information(self, "提示", f"{stock_code} 不在自选股中")
    
    def filter_by_stocks(self, stock_codes: list):
        """按股票代码列表筛选显示"""
        try:
            if not stock_codes:
                logger.warning("股票代码列表为空")
                return
            
            # 获取完整的股票数据
            if self.current_data.empty:
                self.refresh_data()
            
            if self.current_data.empty:
                logger.warning("无股票数据可筛选")
                return
            
            # 筛选指定的股票
            if '代码' in self.current_data.columns:
                filtered_data = self.current_data[self.current_data['代码'].isin(stock_codes)]
            else:
                logger.warning("股票数据中没有'代码'列")
                return
            
            if filtered_data.empty:
                logger.warning(f"未找到匹配的股票数据，筛选代码: {stock_codes}")
                # 显示空表格
                self.stock_table.setRowCount(0)
                return
            
            # 更新表格显示
            self.update_stock_table(filtered_data)
            logger.info(f"按板块筛选显示 {len(filtered_data)} 只股票")
            
        except Exception as e:
            logger.error(f"筛选股票数据失败: {e}")
            QMessageBox.warning(self, "错误", f"筛选股票数据失败: {str(e)}")
