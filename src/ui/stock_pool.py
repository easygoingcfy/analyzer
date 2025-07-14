from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QListWidget, QListWidgetItem, QPushButton, QGroupBox,
                             QMenu, QInputDialog, QMessageBox, QAbstractItemView)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QAction
from src.utils.config import config_manager
from src.data.stock_data import data_provider
from src.utils.logger import get_logger

logger = get_logger(__name__)

class StockPoolWidget(QWidget):
    """股票池组件"""
    
    stock_selected = pyqtSignal(str, str)  # 股票代码, 股票名称
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_stock_pools()
        
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # 标题
        title_label = QLabel("股票池")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # 我的自选
        self.setup_my_stocks(layout)
        
        # 观察池
        self.setup_watch_list(layout)
        
        # 自定义股票池
        self.setup_custom_pools(layout)
        
    def setup_my_stocks(self, parent_layout):
        """设置我的自选"""
        group = QGroupBox("我的自选")
        layout = QVBoxLayout(group)
        
        # 工具栏
        toolbar_layout = QHBoxLayout()
        
        add_btn = QPushButton("添加")
        add_btn.setFixedSize(50, 25)
        add_btn.clicked.connect(self.add_to_my_stocks)
        toolbar_layout.addWidget(add_btn)
        
        clear_btn = QPushButton("清空")
        clear_btn.setFixedSize(50, 25)
        clear_btn.clicked.connect(self.clear_my_stocks)
        toolbar_layout.addWidget(clear_btn)
        
        toolbar_layout.addStretch()
        layout.addLayout(toolbar_layout)
        
        # 股票列表
        self.my_stocks_list = QListWidget()
        self.my_stocks_list.setMaximumHeight(150)
        self.my_stocks_list.itemDoubleClicked.connect(self.on_my_stock_double_clicked)
        self.my_stocks_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.my_stocks_list.customContextMenuRequested.connect(self.show_my_stocks_menu)
        layout.addWidget(self.my_stocks_list)
        
        parent_layout.addWidget(group)
        
    def setup_watch_list(self, parent_layout):
        """设置观察池"""
        group = QGroupBox("观察池")
        layout = QVBoxLayout(group)
        
        # 工具栏
        toolbar_layout = QHBoxLayout()
        
        add_btn = QPushButton("添加")
        add_btn.setFixedSize(50, 25)
        add_btn.clicked.connect(self.add_to_watch_list)
        toolbar_layout.addWidget(add_btn)
        
        clear_btn = QPushButton("清空")
        clear_btn.setFixedSize(50, 25)
        clear_btn.clicked.connect(self.clear_watch_list)
        toolbar_layout.addWidget(clear_btn)
        
        toolbar_layout.addStretch()
        layout.addLayout(toolbar_layout)
        
        # 股票列表
        self.watch_list_widget = QListWidget()
        self.watch_list_widget.setMaximumHeight(120)
        self.watch_list_widget.itemDoubleClicked.connect(self.on_watch_stock_double_clicked)
        self.watch_list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.watch_list_widget.customContextMenuRequested.connect(self.show_watch_list_menu)
        layout.addWidget(self.watch_list_widget)
        
        parent_layout.addWidget(group)
        
    def setup_custom_pools(self, parent_layout):
        """设置自定义股票池"""
        group = QGroupBox("自定义池")
        layout = QVBoxLayout(group)
        
        # 工具栏
        toolbar_layout = QHBoxLayout()
        
        create_btn = QPushButton("新建")
        create_btn.setFixedSize(50, 25)
        create_btn.clicked.connect(self.create_custom_pool)
        toolbar_layout.addWidget(create_btn)
        
        toolbar_layout.addStretch()
        layout.addLayout(toolbar_layout)
        
        # 自定义池列表
        self.custom_pools_list = QListWidget()
        self.custom_pools_list.setMaximumHeight(100)
        self.custom_pools_list.itemDoubleClicked.connect(self.on_custom_pool_double_clicked)
        self.custom_pools_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.custom_pools_list.customContextMenuRequested.connect(self.show_custom_pools_menu)
        layout.addWidget(self.custom_pools_list)
        
        parent_layout.addWidget(group)
        
    def load_stock_pools(self):
        """加载股票池数据"""
        # 加载我的自选
        my_stocks = config_manager.get('stock_pools.my_stocks', [])
        self.update_my_stocks_list(my_stocks)
        
        # 加载观察池
        watch_list = config_manager.get('stock_pools.watch_list', [])
        self.update_watch_list(watch_list)
        
        # 加载自定义池
        custom_pools = config_manager.get('stock_pools.custom_pools', {})
        self.update_custom_pools_list(custom_pools)
        
    def update_my_stocks_list(self, stocks):
        """更新我的自选列表"""
        self.my_stocks_list.clear()
        
        # 获取股票名称
        for stock_code in stocks:
            try:
                # 这里可以从缓存或API获取股票名称
                stock_name = self._get_stock_name(stock_code)
                item_text = f"{stock_code} {stock_name}"
                
                item = QListWidgetItem(item_text)
                item.setData(Qt.ItemDataRole.UserRole, stock_code)
                self.my_stocks_list.addItem(item)
            except Exception as e:
                logger.warning(f"获取股票{stock_code}名称失败: {e}")
                item = QListWidgetItem(stock_code)
                item.setData(Qt.ItemDataRole.UserRole, stock_code)
                self.my_stocks_list.addItem(item)
                
    def update_watch_list(self, stocks):
        """更新观察池列表"""
        self.watch_list_widget.clear()
        
        for stock_code in stocks:
            try:
                stock_name = self._get_stock_name(stock_code)
                item_text = f"{stock_code} {stock_name}"
                
                item = QListWidgetItem(item_text)
                item.setData(Qt.ItemDataRole.UserRole, stock_code)
                self.watch_list_widget.addItem(item)
            except Exception as e:
                logger.warning(f"获取股票{stock_code}名称失败: {e}")
                item = QListWidgetItem(stock_code)
                item.setData(Qt.ItemDataRole.UserRole, stock_code)
                self.watch_list_widget.addItem(item)
                
    def update_custom_pools_list(self, pools):
        """更新自定义池列表"""
        self.custom_pools_list.clear()
        
        for pool_name, stocks in pools.items():
            item_text = f"{pool_name} ({len(stocks)})"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, pool_name)
            self.custom_pools_list.addItem(item)
            
    def _get_stock_name(self, stock_code: str) -> str:
        """获取股票名称"""
        try:
            # 从股票列表中查找
            stock_list = data_provider.get_stock_list()
            if not stock_list.empty:
                match = stock_list[stock_list['代码'] == stock_code]
                if not match.empty:
                    return match.iloc[0]['名称']
        except:
            pass
        return "未知"
        
    def add_to_my_stocks(self):
        """添加到我的自选"""
        stock_code, ok = QInputDialog.getText(self, "添加股票", "请输入股票代码:")
        if ok and stock_code.strip():
            stock_code = stock_code.strip().upper()
            
            my_stocks = config_manager.get('stock_pools.my_stocks', [])
            if stock_code not in my_stocks:
                my_stocks.append(stock_code)
                config_manager.set('stock_pools.my_stocks', my_stocks)
                self.update_my_stocks_list(my_stocks)
                QMessageBox.information(self, "成功", f"已添加 {stock_code} 到我的自选")
            else:
                QMessageBox.information(self, "提示", f"{stock_code} 已在我的自选中")
                
    def clear_my_stocks(self):
        """清空我的自选"""
        reply = QMessageBox.question(self, "确认", "确定要清空我的自选吗？",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            config_manager.set('stock_pools.my_stocks', [])
            self.my_stocks_list.clear()
            
    def add_to_watch_list(self):
        """添加到观察池"""
        stock_code, ok = QInputDialog.getText(self, "添加股票", "请输入股票代码:")
        if ok and stock_code.strip():
            stock_code = stock_code.strip().upper()
            
            watch_list = config_manager.get('stock_pools.watch_list', [])
            if stock_code not in watch_list:
                watch_list.append(stock_code)
                config_manager.set('stock_pools.watch_list', watch_list)
                self.update_watch_list(watch_list)
                QMessageBox.information(self, "成功", f"已添加 {stock_code} 到观察池")
            else:
                QMessageBox.information(self, "提示", f"{stock_code} 已在观察池中")
                
    def clear_watch_list(self):
        """清空观察池"""
        reply = QMessageBox.question(self, "确认", "确定要清空观察池吗？",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            config_manager.set('stock_pools.watch_list', [])
            self.watch_list_widget.clear()
            
    def create_custom_pool(self):
        """创建自定义股票池"""
        pool_name, ok = QInputDialog.getText(self, "新建股票池", "请输入股票池名称:")
        if ok and pool_name.strip():
            pool_name = pool_name.strip()
            
            custom_pools = config_manager.get('stock_pools.custom_pools', {})
            if pool_name not in custom_pools:
                custom_pools[pool_name] = []
                config_manager.set('stock_pools.custom_pools', custom_pools)
                self.update_custom_pools_list(custom_pools)
                QMessageBox.information(self, "成功", f"已创建股票池: {pool_name}")
            else:
                QMessageBox.information(self, "提示", f"股票池 {pool_name} 已存在")
                
    def on_my_stock_double_clicked(self, item):
        """我的自选双击事件"""
        stock_code = item.data(Qt.ItemDataRole.UserRole)
        stock_name = self._get_stock_name(stock_code)
        self.stock_selected.emit(stock_code, stock_name)
        
    def on_watch_stock_double_clicked(self, item):
        """观察池双击事件"""
        stock_code = item.data(Qt.ItemDataRole.UserRole)
        stock_name = self._get_stock_name(stock_code)
        self.stock_selected.emit(stock_code, stock_name)
        
    def on_custom_pool_double_clicked(self, item):
        """自定义池双击事件"""
        pool_name = item.data(Qt.ItemDataRole.UserRole)
        QMessageBox.information(self, "股票池", f"股票池: {pool_name}\\n\\n功能开发中...")
        
    def show_my_stocks_menu(self, position):
        """显示我的自选右键菜单"""
        item = self.my_stocks_list.itemAt(position)
        if item is None:
            return
            
        stock_code = item.data(Qt.ItemDataRole.UserRole)
        
        menu = QMenu(self)
        
        view_action = QAction("查看详情", self)
        view_action.triggered.connect(lambda: self.view_stock_detail(stock_code))
        menu.addAction(view_action)
        
        remove_action = QAction("移除", self)
        remove_action.triggered.connect(lambda: self.remove_from_my_stocks(stock_code))
        menu.addAction(remove_action)
        
        menu.exec(self.my_stocks_list.mapToGlobal(position))
        
    def show_watch_list_menu(self, position):
        """显示观察池右键菜单"""
        item = self.watch_list_widget.itemAt(position)
        if item is None:
            return
            
        stock_code = item.data(Qt.ItemDataRole.UserRole)
        
        menu = QMenu(self)
        
        view_action = QAction("查看详情", self)
        view_action.triggered.connect(lambda: self.view_stock_detail(stock_code))
        menu.addAction(view_action)
        
        move_action = QAction("移至自选", self)
        move_action.triggered.connect(lambda: self.move_to_my_stocks(stock_code))
        menu.addAction(move_action)
        
        remove_action = QAction("移除", self)
        remove_action.triggered.connect(lambda: self.remove_from_watch_list(stock_code))
        menu.addAction(remove_action)
        
        menu.exec(self.watch_list_widget.mapToGlobal(position))
        
    def show_custom_pools_menu(self, position):
        """显示自定义池右键菜单"""
        item = self.custom_pools_list.itemAt(position)
        if item is None:
            return
            
        pool_name = item.data(Qt.ItemDataRole.UserRole)
        
        menu = QMenu(self)
        
        edit_action = QAction("编辑", self)
        edit_action.triggered.connect(lambda: self.edit_custom_pool(pool_name))
        menu.addAction(edit_action)
        
        delete_action = QAction("删除", self)
        delete_action.triggered.connect(lambda: self.delete_custom_pool(pool_name))
        menu.addAction(delete_action)
        
        menu.exec(self.custom_pools_list.mapToGlobal(position))
        
    def view_stock_detail(self, stock_code: str):
        """查看股票详情"""
        stock_name = self._get_stock_name(stock_code)
        self.stock_selected.emit(stock_code, stock_name)
        
    def remove_from_my_stocks(self, stock_code: str):
        """从我的自选移除"""
        my_stocks = config_manager.get('stock_pools.my_stocks', [])
        if stock_code in my_stocks:
            my_stocks.remove(stock_code)
            config_manager.set('stock_pools.my_stocks', my_stocks)
            self.update_my_stocks_list(my_stocks)
            
    def remove_from_watch_list(self, stock_code: str):
        """从观察池移除"""
        watch_list = config_manager.get('stock_pools.watch_list', [])
        if stock_code in watch_list:
            watch_list.remove(stock_code)
            config_manager.set('stock_pools.watch_list', watch_list)
            self.update_watch_list(watch_list)
            
    def move_to_my_stocks(self, stock_code: str):
        """移动到我的自选"""
        # 从观察池移除
        watch_list = config_manager.get('stock_pools.watch_list', [])
        if stock_code in watch_list:
            watch_list.remove(stock_code)
            config_manager.set('stock_pools.watch_list', watch_list)
            
        # 添加到我的自选
        my_stocks = config_manager.get('stock_pools.my_stocks', [])
        if stock_code not in my_stocks:
            my_stocks.append(stock_code)
            config_manager.set('stock_pools.my_stocks', my_stocks)
            
        # 更新界面
        self.update_watch_list(watch_list)
        self.update_my_stocks_list(my_stocks)
        
    def edit_custom_pool(self, pool_name: str):
        """编辑自定义股票池"""
        QMessageBox.information(self, "编辑股票池", f"编辑股票池 {pool_name} 功能开发中...")
        
    def delete_custom_pool(self, pool_name: str):
        """删除自定义股票池"""
        reply = QMessageBox.question(self, "确认", f"确定要删除股票池 {pool_name} 吗？",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            custom_pools = config_manager.get('stock_pools.custom_pools', {})
            if pool_name in custom_pools:
                del custom_pools[pool_name]
                config_manager.set('stock_pools.custom_pools', custom_pools)
                self.update_custom_pools_list(custom_pools)
