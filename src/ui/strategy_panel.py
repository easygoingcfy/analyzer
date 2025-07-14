from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QGroupBox, QTreeWidget, QTreeWidgetItem,
                             QTabWidget, QTextEdit, QComboBox, QSpinBox, QCheckBox,
                             QFormLayout, QScrollArea, QMessageBox, QDialog,
                             QDialogButtonBox, QFrame, QLineEdit, QTableWidget,
                             QTableWidgetItem, QHeaderView, QAbstractItemView)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon
import pandas as pd
from src.utils.config import config_manager
from src.data.stock_data import data_provider
from src.utils.logger import get_logger

logger = get_logger(__name__)

class StrategyPanelWidget(QWidget):
    """策略面板组件"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_saved_strategies()
        
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # 标题
        title_label = QLabel("策略中心")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        
        # 策略构建标签页
        self.setup_strategy_builder_tab()
        
        # 已保存策略标签页
        self.setup_saved_strategies_tab()
        
        # 选股结果标签页
        self.setup_results_tab()
        
        layout.addWidget(self.tab_widget)
        
    def setup_strategy_builder_tab(self):
        """设置策略构建标签页"""
        builder_widget = QWidget()
        layout = QVBoxLayout(builder_widget)
        
        # 策略基本信息
        self.setup_strategy_info(layout)
        
        # 条件设置区域
        self.setup_conditions_area(layout)
        
        # 操作按钮
        self.setup_action_buttons(layout)
        
        self.tab_widget.addTab(builder_widget, "策略构建")
        
    def setup_strategy_info(self, parent_layout):
        """设置策略基本信息"""
        info_group = QGroupBox("策略信息")
        layout = QFormLayout(info_group)
        
        # 策略名称
        self.strategy_name_input = QLineEdit()
        self.strategy_name_input.setPlaceholderText("输入策略名称...")
        layout.addRow("策略名称:", self.strategy_name_input)
        
        # 策略描述
        self.strategy_desc_input = QTextEdit()
        self.strategy_desc_input.setMaximumHeight(60)
        self.strategy_desc_input.setPlaceholderText("输入策略描述...")
        layout.addRow("策略描述:", self.strategy_desc_input)
        
        parent_layout.addWidget(info_group)
        
    def setup_conditions_area(self, parent_layout):
        """设置条件区域"""
        conditions_group = QGroupBox("选股条件")
        layout = QVBoxLayout(conditions_group)
        
        # 条件工具栏
        toolbar_layout = QHBoxLayout()
        
        add_condition_btn = QPushButton("添加条件")
        add_condition_btn.clicked.connect(self.add_condition)
        toolbar_layout.addWidget(add_condition_btn)
        
        clear_conditions_btn = QPushButton("清空条件")
        clear_conditions_btn.clicked.connect(self.clear_conditions)
        toolbar_layout.addWidget(clear_conditions_btn)
        
        toolbar_layout.addStretch()
        layout.addLayout(toolbar_layout)
        
        # 条件列表
        self.conditions_tree = QTreeWidget()
        self.conditions_tree.setHeaderLabels(["条件类型", "字段", "运算符", "值", "逻辑"])
        self.conditions_tree.setMaximumHeight(200)
        layout.addWidget(self.conditions_tree)
        
        parent_layout.addWidget(conditions_group)
        
    def setup_action_buttons(self, parent_layout):
        """设置操作按钮"""
        button_layout = QHBoxLayout()
        
        # 预览按钮
        preview_btn = QPushButton("预览结果")
        preview_btn.clicked.connect(self.preview_strategy)
        button_layout.addWidget(preview_btn)
        
        # 执行选股按钮
        execute_btn = QPushButton("执行选股")
        execute_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
        """)
        execute_btn.clicked.connect(self.execute_strategy)
        button_layout.addWidget(execute_btn)
        
        # 保存策略按钮
        save_btn = QPushButton("保存策略")
        save_btn.clicked.connect(self.save_strategy)
        button_layout.addWidget(save_btn)
        
        parent_layout.addLayout(button_layout)
        
    def setup_saved_strategies_tab(self):
        """设置已保存策略标签页"""
        saved_widget = QWidget()
        layout = QVBoxLayout(saved_widget)
        
        # 工具栏
        toolbar_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("刷新")
        refresh_btn.clicked.connect(self.load_saved_strategies)
        toolbar_layout.addWidget(refresh_btn)
        
        toolbar_layout.addStretch()
        layout.addLayout(toolbar_layout)
        
        # 策略列表
        self.saved_strategies_tree = QTreeWidget()
        self.saved_strategies_tree.setHeaderLabels(["策略名称", "创建时间", "描述"])
        self.saved_strategies_tree.itemDoubleClicked.connect(self.load_strategy)
        self.saved_strategies_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.saved_strategies_tree.customContextMenuRequested.connect(self.show_strategy_menu)
        layout.addWidget(self.saved_strategies_tree)
        
        self.tab_widget.addTab(saved_widget, "已保存策略")
        
    def setup_results_tab(self):
        """设置选股结果标签页"""
        results_widget = QWidget()
        layout = QVBoxLayout(results_widget)
        
        # 结果信息
        self.results_info_label = QLabel("选股结果: 0 只股票")
        results_font = QFont()
        results_font.setBold(True)
        self.results_info_label.setFont(results_font)
        layout.addWidget(self.results_info_label)
        
        # 结果表格
        self.results_table = QTableWidget()
        self.setup_results_table()
        layout.addWidget(self.results_table)
        
        # 导出按钮
        export_layout = QHBoxLayout()
        export_layout.addStretch()
        
        export_btn = QPushButton("导出结果")
        export_btn.clicked.connect(self.export_results)
        export_layout.addWidget(export_btn)
        
        layout.addLayout(export_layout)
        
        self.tab_widget.addTab(results_widget, "选股结果")
        
    def setup_results_table(self):
        """设置结果表格"""
        columns = ["代码", "名称", "现价", "涨跌幅", "成交额", "市盈率", "市净率"]
        self.results_table.setColumnCount(len(columns))
        self.results_table.setHorizontalHeaderLabels(columns)
        
        # 设置表格属性
        self.results_table.setAlternatingRowColors(True)
        self.results_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.results_table.setSortingEnabled(True)
        
        # 设置列宽
        header = self.results_table.horizontalHeader()
        header.setStretchLastSection(True)
        self.results_table.setColumnWidth(0, 80)
        self.results_table.setColumnWidth(1, 100)
        
    def add_condition(self):
        """添加条件"""
        dialog = ConditionDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            condition = dialog.get_condition()
            self.add_condition_to_tree(condition)
            
    def add_condition_to_tree(self, condition):
        """添加条件到树控件"""
        item = QTreeWidgetItem(self.conditions_tree)
        item.setText(0, condition['category'])
        item.setText(1, condition['field'])
        item.setText(2, condition['operator'])
        item.setText(3, str(condition['value']))
        item.setText(4, condition['logic'])
        
        # 存储完整条件数据
        item.setData(0, Qt.ItemDataRole.UserRole, condition)
        
    def clear_conditions(self):
        """清空条件"""
        self.conditions_tree.clear()
        
    def preview_strategy(self):
        """预览策略结果"""
        conditions = self.get_conditions_from_tree()
        if not conditions:
            QMessageBox.warning(self, "警告", "请至少添加一个选股条件")
            return
            
        QMessageBox.information(self, "预览", f"预览功能开发中...\\n当前有{len(conditions)}个条件")
        
    def execute_strategy(self):
        """执行选股策略"""
        conditions = self.get_conditions_from_tree()
        if not conditions:
            QMessageBox.warning(self, "警告", "请至少添加一个选股条件")
            return
            
        try:
            # 执行选股逻辑
            results = self.run_stock_selection(conditions)
            
            # 更新结果
            self.update_results_table(results)
            
            # 切换到结果标签页
            self.tab_widget.setCurrentIndex(2)
            
            QMessageBox.information(self, "完成", f"选股完成，共筛选出 {len(results)} 只股票")
            
        except Exception as e:
            logger.error(f"执行选股策略失败: {e}")
            QMessageBox.critical(self, "错误", f"执行选股失败: {str(e)}")
            
    def run_stock_selection(self, conditions):
        """运行股票选择逻辑"""
        # 这里实现实际的选股逻辑
        # 目前返回模拟数据
        import random
        
        # 获取股票列表
        stock_list = data_provider.get_stock_list()
        if stock_list.empty:
            return pd.DataFrame()
            
        # 随机选择一些股票作为演示
        sample_size = min(20, len(stock_list))
        selected_stocks = stock_list.sample(n=sample_size)
        
        # 获取这些股票的实时数据
        symbols = selected_stocks['代码'].tolist()
        real_time_data = data_provider.get_real_time_data(symbols[:10])  # 限制数量避免请求过多
        
        return real_time_data
        
    def update_results_table(self, results):
        """更新结果表格"""
        if results.empty:
            self.results_table.setRowCount(0)
            self.results_info_label.setText("选股结果: 0 只股票")
            return
            
        self.results_table.setRowCount(len(results))
        self.results_info_label.setText(f"选股结果: {len(results)} 只股票")
        
        column_mapping = {
            0: '代码',
            1: '名称',
            2: '最新价',
            3: '涨跌幅',
            4: '成交额',
            5: '市盈率-动态',
            6: '市净率'
        }
        
        for row in range(len(results)):
            row_data = results.iloc[row]
            
            for col in range(self.results_table.columnCount()):
                if col in column_mapping:
                    data_key = column_mapping[col]
                    if data_key in row_data:
                        value = row_data[data_key]
                        formatted_value = self.format_table_value(col, value)
                        
                        item = QTableWidgetItem(str(formatted_value))
                        self.results_table.setItem(row, col, item)
                    else:
                        item = QTableWidgetItem("--")
                        self.results_table.setItem(row, col, item)
                        
    def format_table_value(self, col, value):
        """格式化表格值"""
        if pd.isna(value) or value == '':
            return '--'
            
        try:
            if col == 2:  # 现价
                return f"{float(value):.2f}"
            elif col == 3:  # 涨跌幅
                return f"{float(value):.2f}%"
            elif col == 4:  # 成交额
                val = float(value)
                if val >= 100000000:
                    return f"{val/100000000:.1f}亿"
                elif val >= 10000:
                    return f"{val/10000:.1f}万"
                else:
                    return f"{val:.0f}"
            elif col in [5, 6]:  # 市盈率、市净率
                return f"{float(value):.2f}"
            else:
                return str(value)
        except:
            return str(value) if value is not None else '--'
            
    def save_strategy(self):
        """保存策略"""
        strategy_name = self.strategy_name_input.text().strip()
        if not strategy_name:
            QMessageBox.warning(self, "警告", "请输入策略名称")
            return
            
        conditions = self.get_conditions_from_tree()
        if not conditions:
            QMessageBox.warning(self, "警告", "请至少添加一个选股条件")
            return
            
        strategy_data = {
            'name': strategy_name,
            'description': self.strategy_desc_input.toPlainText(),
            'conditions': conditions,
            'created_time': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # 保存到配置
        saved_strategies = config_manager.get('strategy.saved_strategies', {})
        saved_strategies[strategy_name] = strategy_data
        config_manager.set('strategy.saved_strategies', saved_strategies)
        
        QMessageBox.information(self, "成功", f"策略 '{strategy_name}' 已保存")
        
        # 刷新已保存策略列表
        self.load_saved_strategies()
        
    def get_conditions_from_tree(self):
        """从树控件获取条件"""
        conditions = []
        for i in range(self.conditions_tree.topLevelItemCount()):
            item = self.conditions_tree.topLevelItem(i)
            condition = item.data(0, Qt.ItemDataRole.UserRole)
            if condition:
                conditions.append(condition)
        return conditions
        
    def load_saved_strategies(self):
        """加载已保存的策略"""
        self.saved_strategies_tree.clear()
        
        saved_strategies = config_manager.get('strategy.saved_strategies', {})
        
        for name, strategy_data in saved_strategies.items():
            item = QTreeWidgetItem(self.saved_strategies_tree)
            item.setText(0, name)
            item.setText(1, strategy_data.get('created_time', ''))
            item.setText(2, strategy_data.get('description', ''))
            
            # 存储策略数据
            item.setData(0, Qt.ItemDataRole.UserRole, strategy_data)
            
    def load_strategy(self, item):
        """加载策略"""
        strategy_data = item.data(0, Qt.ItemDataRole.UserRole)
        if not strategy_data:
            return
            
        # 设置策略信息
        self.strategy_name_input.setText(strategy_data['name'])
        self.strategy_desc_input.setPlainText(strategy_data.get('description', ''))
        
        # 清空现有条件
        self.clear_conditions()
        
        # 加载条件
        conditions = strategy_data.get('conditions', [])
        for condition in conditions:
            self.add_condition_to_tree(condition)
            
        # 切换到策略构建标签页
        self.tab_widget.setCurrentIndex(0)
        
        QMessageBox.information(self, "加载成功", f"策略 '{strategy_data['name']}' 已加载")
        
    def show_strategy_menu(self, position):
        """显示策略右键菜单"""
        # 实现策略右键菜单（删除、重命名等）
        pass
        
    def export_results(self):
        """导出选股结果"""
        QMessageBox.information(self, "导出", "导出功能开发中...")
        
    def show_editor(self):
        """显示策略编辑器"""
        self.tab_widget.setCurrentIndex(0)


class ConditionDialog(QDialog):
    """条件设置对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("添加选股条件")
        self.setFixedSize(400, 300)
        self.init_ui()
        
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        
        # 条件表单
        form_layout = QFormLayout()
        
        # 条件类别
        self.category_combo = QComboBox()
        self.category_combo.addItems(["技术面", "基本面", "热度面", "自定义"])
        self.category_combo.currentTextChanged.connect(self.on_category_changed)
        form_layout.addRow("条件类别:", self.category_combo)
        
        # 字段选择
        self.field_combo = QComboBox()
        form_layout.addRow("字段:", self.field_combo)
        
        # 运算符
        self.operator_combo = QComboBox()
        self.operator_combo.addItems(["大于", "小于", "等于", "大于等于", "小于等于", "不等于", "包含", "不包含"])
        form_layout.addRow("运算符:", self.operator_combo)
        
        # 值
        self.value_input = QLineEdit()
        form_layout.addRow("值:", self.value_input)
        
        # 逻辑关系
        self.logic_combo = QComboBox()
        self.logic_combo.addItems(["且(AND)", "或(OR)"])
        form_layout.addRow("逻辑关系:", self.logic_combo)
        
        layout.addLayout(form_layout)
        
        # 按钮
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # 初始化字段
        self.on_category_changed("技术面")
        
    def on_category_changed(self, category):
        """类别改变事件"""
        self.field_combo.clear()
        
        fields = {
            "技术面": ["现价", "涨跌幅", "成交量", "成交额", "换手率", "市盈率", "市净率", "RSI", "MACD", "KDJ"],
            "基本面": ["每股收益", "净资产收益率", "资产负债率", "营业收入", "净利润", "毛利率"],
            "热度面": ["搜索热度", "资讯数量", "讨论热度", "资金流向"],
            "自定义": ["自定义指标1", "自定义指标2"]
        }
        
        if category in fields:
            self.field_combo.addItems(fields[category])
            
    def get_condition(self):
        """获取条件"""
        return {
            'category': self.category_combo.currentText(),
            'field': self.field_combo.currentText(),
            'operator': self.operator_combo.currentText(),
            'value': self.value_input.text(),
            'logic': self.logic_combo.currentText()
        }
