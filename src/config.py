"""交易系统配置
"""

class TradingConfig:
    # 交易基础参数
    initial_cash = 100000  # 初始资金
    buy_shares = 1000      # 每次买入股数（不是初始建仓时使用）
    
    # 策略参数 - 选择使用的策略
    strategy_name = "MACrossStrategy"  # 可选: "MACrossStrategy", "MomentumStrategy" 
    
    # 各策略的具体参数
    strategy_params = {
        "MACrossStrategy": {
            "short_window": 5,    # 短期均线窗口
            "long_window": 20,    # 长期均线窗口
        },
        "MomentumStrategy": {
            "momentum_window": 10,  # 动量计算窗口
            "threshold": 0.05,      # 动量阈值
        }
    }
    
    # 税费参数 - 中国A股市场标准
    tax_rate = {
        "buy": {
            "commission": 0.0003,      # 买入佣金费率
            "transfer_fee": 0.00002    # 过户费 (仅上海市场)
        },
        "sell": {
            "commission": 0.0003,      # 卖出佣金费率
            "stamp_duty": 0.001,       # 印花税
            "transfer_fee": 0.00002    # 过户费 (仅上海市场)
        },
        "min_commission": 5.0          # 最低佣金
    }