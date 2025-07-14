from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTabWidget, QFrame, QSplitter,
                             QComboBox, QDateEdit, QSpinBox, QCheckBox)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont
import pyqtgraph as pg
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from src.data.stock_data import data_provider
from src.utils.logger import get_logger

logger = get_logger(__name__)

class ChartViewWidget(QWidget):
    """图表视图组件"""
    
    def __init__(self):
        super().__init__()
        self.current_stock_code = None
        self.current_stock_name = None
        self.current_data = pd.DataFrame()
        self.init_ui()
        
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # 工具栏
        self.setup_toolbar(layout)
        
        # 分割器
        splitter = QSplitter(Qt.Orientation.Vertical)
        layout.addWidget(splitter)
        
        # 主图表区域
        self.setup_main_chart(splitter)
        
        # 指标图表区域
        self.setup_indicator_chart(splitter)
        
        # 设置分割器比例
        splitter.setSizes([400, 200])
        
    def setup_toolbar(self, parent_layout):
        """设置工具栏"""
        toolbar_frame = QFrame()
        toolbar_frame.setFrameStyle(QFrame.Shape.Box)
        toolbar_frame.setMaximumHeight(50)
        
        toolbar_layout = QHBoxLayout(toolbar_frame)
        toolbar_layout.setContentsMargins(10, 5, 10, 5)
        
        # 股票信息
        self.stock_info_label = QLabel("请选择股票")
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.stock_info_label.setFont(font)
        toolbar_layout.addWidget(self.stock_info_label)
        
        toolbar_layout.addStretch()
        
        # 周期选择
        period_label = QLabel("周期:")
        toolbar_layout.addWidget(period_label)
        
        self.period_combo = QComboBox()
        self.period_combo.addItems(["日K", "周K", "月K", "5分钟", "15分钟", "30分钟", "60分钟"])
        self.period_combo.setCurrentText("日K")
        self.period_combo.currentTextChanged.connect(self.on_period_changed)
        toolbar_layout.addWidget(self.period_combo)
        
        # 复权选择
        adjust_label = QLabel("复权:")
        toolbar_layout.addWidget(adjust_label)
        
        self.adjust_combo = QComboBox()
        self.adjust_combo.addItems(["不复权", "前复权", "后复权"])
        self.adjust_combo.currentTextChanged.connect(self.on_adjust_changed)
        toolbar_layout.addWidget(self.adjust_combo)
        
        # 刷新按钮
        refresh_btn = QPushButton("刷新")
        refresh_btn.clicked.connect(self.refresh_chart)
        toolbar_layout.addWidget(refresh_btn)
        
        parent_layout.addWidget(toolbar_frame)
        
    def setup_main_chart(self, parent):
        """设置主图表"""
        # 创建图表窗口
        self.main_chart_widget = pg.GraphicsLayoutWidget()
        self.main_plot = self.main_chart_widget.addPlot(title="K线图")
        
        # 设置坐标轴
        self.main_plot.setLabel('left', '价格')
        self.main_plot.setLabel('bottom', '日期')
        self.main_plot.showGrid(x=True, y=True)
        
        # K线图数据项
        self.candlestick_item = None
        self.volume_item = None
        
        parent.addWidget(self.main_chart_widget)
        
    def setup_indicator_chart(self, parent):
        """设置指标图表"""
        # 创建标签页
        self.indicator_tabs = QTabWidget()
        
        # MACD标签页
        self.setup_macd_tab()
        
        # KDJ标签页
        self.setup_kdj_tab()
        
        # 成交量标签页
        self.setup_volume_tab()
        
        parent.addWidget(self.indicator_tabs)
        
    def setup_macd_tab(self):
        """设置MACD标签页"""
        macd_widget = pg.GraphicsLayoutWidget()
        self.macd_plot = macd_widget.addPlot(title="MACD")
        self.macd_plot.setLabel('left', 'MACD')
        self.macd_plot.setLabel('bottom', '日期')
        self.macd_plot.showGrid(x=True, y=True)
        
        self.indicator_tabs.addTab(macd_widget, "MACD")
        
    def setup_kdj_tab(self):
        """设置KDJ标签页"""
        kdj_widget = pg.GraphicsLayoutWidget()
        self.kdj_plot = kdj_widget.addPlot(title="KDJ")
        self.kdj_plot.setLabel('left', 'KDJ')
        self.kdj_plot.setLabel('bottom', '日期')
        self.kdj_plot.showGrid(x=True, y=True)
        
        self.indicator_tabs.addTab(kdj_widget, "KDJ")
        
    def setup_volume_tab(self):
        """设置成交量标签页"""
        volume_widget = pg.GraphicsLayoutWidget()
        self.volume_plot = volume_widget.addPlot(title="成交量")
        self.volume_plot.setLabel('left', '成交量')
        self.volume_plot.setLabel('bottom', '日期')
        self.volume_plot.showGrid(x=True, y=True)
        
        self.indicator_tabs.addTab(volume_widget, "成交量")
        
    def load_stock(self, stock_code: str, stock_name: str):
        """加载股票数据"""
        self.current_stock_code = stock_code
        self.current_stock_name = stock_name
        
        # 更新标题
        self.stock_info_label.setText(f"{stock_name} ({stock_code})")
        
        # 加载数据
        self.load_data()
        
    def load_data(self):
        """加载数据"""
        if not self.current_stock_code:
            return
            
        try:
            # 获取历史数据
            period_map = {
                "日K": "daily",
                "周K": "weekly", 
                "月K": "monthly"
            }
            
            period = period_map.get(self.period_combo.currentText(), "daily")
            
            # 获取一年的数据
            end_date = datetime.now().strftime('%Y%m%d')
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
            
            data = data_provider.get_historical_data(
                self.current_stock_code, 
                period=period,
                start_date=start_date,
                end_date=end_date
            )
            
            if not data.empty:
                self.current_data = data
                self.update_charts()
                logger.info(f"成功加载{self.current_stock_name}({self.current_stock_code})数据")
            else:
                logger.warning(f"未获取到{self.current_stock_code}的数据")
                
        except Exception as e:
            logger.error(f"加载股票数据失败: {e}")
            
    def update_charts(self):
        """更新图表"""
        if self.current_data.empty:
            return
            
        try:
            # 更新K线图
            self.update_candlestick_chart()
            
            # 更新指标图表
            self.update_indicator_charts()
            
        except Exception as e:
            logger.error(f"更新图表失败: {e}")
            
    def update_candlestick_chart(self):
        """更新K线图"""
        # 清除旧数据
        self.main_plot.clear()
        
        data = self.current_data.copy()
        
        # 准备数据
        dates = data['日期'].dt.strftime('%m-%d').tolist()
        opens = data['开盘'].values
        highs = data['最高'].values
        lows = data['最低'].values
        closes = data['收盘'].values
        
        # 创建x轴数据（使用索引）
        x = np.arange(len(data))
        
        # 绘制K线
        for i in range(len(data)):
            color = 'r' if closes[i] >= opens[i] else 'g'
            
            # 实体
            body_height = abs(closes[i] - opens[i])
            body_bottom = min(opens[i], closes[i])
            
            # 添加实体矩形
            rect = pg.QtWidgets.QGraphicsRectItem(i-0.3, body_bottom, 0.6, body_height)
            rect.setBrush(pg.mkBrush(color))
            rect.setPen(pg.mkPen(color))
            self.main_plot.addItem(rect)
            
            # 上影线
            if highs[i] > max(opens[i], closes[i]):
                line = pg.PlotCurveItem([i, i], [max(opens[i], closes[i]), highs[i]], pen=color)
                self.main_plot.addItem(line)
            
            # 下影线
            if lows[i] < min(opens[i], closes[i]):
                line = pg.PlotCurveItem([i, i], [lows[i], min(opens[i], closes[i])], pen=color)
                self.main_plot.addItem(line)
        
        # 设置x轴标签
        if len(dates) > 0:
            # 只显示部分日期标签以避免重叠
            step = max(1, len(dates) // 10)
            ticks = [(i, dates[i]) for i in range(0, len(dates), step)]
            
            axis = self.main_plot.getAxis('bottom')
            axis.setTicks([ticks])
            
        # 添加均线
        self.add_moving_averages(x, closes)
        
    def add_moving_averages(self, x, closes):
        """添加均线"""
        try:
            # 5日均线
            if len(closes) >= 5:
                ma5 = pd.Series(closes).rolling(window=5).mean()
                ma5_line = pg.PlotCurveItem(x, ma5, pen=pg.mkPen('blue', width=1))
                self.main_plot.addItem(ma5_line)
            
            # 10日均线
            if len(closes) >= 10:
                ma10 = pd.Series(closes).rolling(window=10).mean()
                ma10_line = pg.PlotCurveItem(x, ma10, pen=pg.mkPen('orange', width=1))
                self.main_plot.addItem(ma10_line)
            
            # 20日均线
            if len(closes) >= 20:
                ma20 = pd.Series(closes).rolling(window=20).mean()
                ma20_line = pg.PlotCurveItem(x, ma20, pen=pg.mkPen('purple', width=1))
                self.main_plot.addItem(ma20_line)
                
        except Exception as e:
            logger.warning(f"添加均线失败: {e}")
            
    def update_indicator_charts(self):
        """更新指标图表"""
        try:
            self.update_macd_chart()
            self.update_kdj_chart()
            self.update_volume_chart()
        except Exception as e:
            logger.error(f"更新指标图表失败: {e}")
            
    def update_macd_chart(self):
        """更新MACD图表"""
        self.macd_plot.clear()
        
        data = self.current_data.copy()
        closes = data['收盘'].values
        
        if len(closes) < 26:  # MACD需要至少26个数据点
            return
            
        try:
            # 计算MACD
            macd_data = self.calculate_macd(closes)
            
            x = np.arange(len(macd_data))
            
            # 绘制MACD线
            self.macd_plot.plot(x, macd_data['MACD'], pen='blue', name='MACD')
            self.macd_plot.plot(x, macd_data['Signal'], pen='red', name='Signal')
            
            # 绘制柱状图
            histogram = macd_data['Histogram']
            for i in range(len(histogram)):
                color = 'r' if histogram[i] >= 0 else 'g'
                bar = pg.BarGraphItem(x=[i], height=[abs(histogram[i])], width=0.8, brush=color)
                self.macd_plot.addItem(bar)
                
        except Exception as e:
            logger.warning(f"计算MACD失败: {e}")
            
    def update_kdj_chart(self):
        """更新KDJ图表"""
        self.kdj_plot.clear()
        
        data = self.current_data.copy()
        
        if len(data) < 9:  # KDJ需要至少9个数据点
            return
            
        try:
            # 计算KDJ
            kdj_data = self.calculate_kdj(data)
            
            x = np.arange(len(kdj_data))
            
            # 绘制KDJ线
            self.kdj_plot.plot(x, kdj_data['K'], pen='blue', name='K')
            self.kdj_plot.plot(x, kdj_data['D'], pen='red', name='D')
            self.kdj_plot.plot(x, kdj_data['J'], pen='green', name='J')
            
            # 添加参考线
            self.kdj_plot.addLine(y=80, pen=pg.mkPen('gray', style=Qt.PenStyle.DashLine))
            self.kdj_plot.addLine(y=20, pen=pg.mkPen('gray', style=Qt.PenStyle.DashLine))
            
        except Exception as e:
            logger.warning(f"计算KDJ失败: {e}")
            
    def update_volume_chart(self):
        """更新成交量图表"""
        self.volume_plot.clear()
        
        data = self.current_data.copy()
        volumes = data['成交量'].values
        closes = data['收盘'].values
        opens = data['开盘'].values
        
        x = np.arange(len(volumes))
        
        # 绘制成交量柱状图
        for i in range(len(volumes)):
            color = 'r' if closes[i] >= opens[i] else 'g'
            bar = pg.BarGraphItem(x=[i], height=[volumes[i]], width=0.8, brush=color)
            self.volume_plot.addItem(bar)
            
        # 添加成交量均线
        if len(volumes) >= 5:
            vol_ma5 = pd.Series(volumes).rolling(window=5).mean()
            self.volume_plot.plot(x, vol_ma5, pen='blue')
            
    def calculate_macd(self, prices, fast=12, slow=26, signal=9):
        """计算MACD指标"""
        prices_series = pd.Series(prices)
        
        # 计算EMA
        ema_fast = prices_series.ewm(span=fast).mean()
        ema_slow = prices_series.ewm(span=slow).mean()
        
        # 计算MACD线
        macd_line = ema_fast - ema_slow
        
        # 计算信号线
        signal_line = macd_line.ewm(span=signal).mean()
        
        # 计算柱状图
        histogram = macd_line - signal_line
        
        return pd.DataFrame({
            'MACD': macd_line,
            'Signal': signal_line,
            'Histogram': histogram
        }).fillna(0)
        
    def calculate_kdj(self, data, n=9, m1=3, m2=3):
        """计算KDJ指标"""
        highs = data['最高'].values
        lows = data['最低'].values
        closes = data['收盘'].values
        
        # 计算RSV
        rsv = []
        for i in range(len(closes)):
            if i < n - 1:
                rsv.append(50)  # 初始值
            else:
                period_high = np.max(highs[i-n+1:i+1])
                period_low = np.min(lows[i-n+1:i+1])
                
                if period_high == period_low:
                    rsv_val = 50
                else:
                    rsv_val = (closes[i] - period_low) / (period_high - period_low) * 100
                rsv.append(rsv_val)
        
        # 计算K值
        k_values = [50]  # 初始K值
        for i in range(1, len(rsv)):
            k_val = (2/3) * k_values[-1] + (1/3) * rsv[i]
            k_values.append(k_val)
            
        # 计算D值
        d_values = [50]  # 初始D值
        for i in range(1, len(k_values)):
            d_val = (2/3) * d_values[-1] + (1/3) * k_values[i]
            d_values.append(d_val)
            
        # 计算J值
        j_values = [3 * k - 2 * d for k, d in zip(k_values, d_values)]
        
        return pd.DataFrame({
            'K': k_values,
            'D': d_values,
            'J': j_values
        })
        
    def on_period_changed(self, period):
        """周期改变事件"""
        if self.current_stock_code:
            self.load_data()
            
    def on_adjust_changed(self, adjust):
        """复权改变事件"""
        if self.current_stock_code:
            self.load_data()
            
    def refresh_chart(self):
        """刷新图表"""
        if self.current_stock_code:
            self.load_data()
