import numpy as np
from trading_system import Strategy

# 均线交叉策略
class MACrossStrategy(Strategy):
    def __init__(self, short_window=5, long_window=20, buy_shares=100):
        self.short_window = short_window  # 短期均线窗口
        self.long_window = long_window    # 长期均线窗口
        self.buy_shares = buy_shares      # 每次买入股数
        
    def generate_signals(self, data):
        signals = np.zeros(len(data))
        
        # 确定价格列名
        price_col = '收盘'
        if price_col not in data.columns and '收盘价' in data.columns:
            price_col = '收盘价'
        
        # 计算短期和长期移动平均
        data['short_ma'] = data[price_col].rolling(window=self.short_window).mean()
        data['long_ma'] = data[price_col].rolling(window=self.long_window).mean()
        
        # 初始化持仓状态
        position = 0
        
        # 生成信号
        for i in range(self.long_window, len(data)):
            # 金叉：短期均线上穿长期均线
            if data['short_ma'].iloc[i-1] <= data['long_ma'].iloc[i-1] and \
               data['short_ma'].iloc[i] > data['long_ma'].iloc[i] and \
               position == 0:
                signals[i] = self.buy_shares  # 买入信号
                position += self.buy_shares
            
            # 死叉：短期均线下穿长期均线
            elif data['short_ma'].iloc[i-1] >= data['long_ma'].iloc[i-1] and \
                 data['short_ma'].iloc[i] < data['long_ma'].iloc[i] and \
                 position > 0:
                signals[i] = -position  # 卖出全部持仓
                position = 0
                
        return signals
    
    def get_name(self):
        return f"MA交叉策略({self.short_window},{self.long_window})"

# 动量策略
class MomentumStrategy(Strategy):
    def __init__(self, momentum_window=10, threshold=0.05, buy_shares=100):
        self.momentum_window = momentum_window  # 动量窗口
        self.threshold = threshold              # 动量阈值
        self.buy_shares = buy_shares            # 每次买入股数
        
    def generate_signals(self, data):
        signals = np.zeros(len(data))
        
        # 确定价格列名
        price_col = '收盘'
        if price_col not in data.columns and '收盘价' in data.columns:
            price_col = '收盘价'
            
        # 计算动量：当前价格与n天前价格的变化率
        data['momentum'] = data[price_col].pct_change(periods=self.momentum_window)
        
        # 初始化持仓状态
        position = 0
        
        # 生成信号
        for i in range(self.momentum_window + 1, len(data)):
            # 强动量买入信号
            if data['momentum'].iloc[i] > self.threshold and position == 0:
                signals[i] = self.buy_shares
                position += self.buy_shares
            
            # 动量反转卖出信号
            elif data['momentum'].iloc[i] < -self.threshold and position > 0:
                signals[i] = -position  # 卖出全部持仓
                position = 0
                
        return signals
    
    def get_name(self):
        return f"动量策略({self.momentum_window},{self.threshold})"