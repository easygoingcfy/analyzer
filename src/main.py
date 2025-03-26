import os
from datetime import datetime
from excel_handler import ExcelHandler
from trading_system import TradingSystem
from strategy_impl import MACrossStrategy, MomentumStrategy
from config import TradingConfig

def main():
    # 直接使用config.py中定义的参数
    config = TradingConfig()
    
    # 文件路径
    input_file = r"C:\Users\gwj\Documents\bigA\金证.xlsx"

    input_dir = os.path.dirname(input_file)
    input_filename = os.path.basename(input_file)
    output_file = os.path.join(input_dir, f"回测结果_{config.strategy_name}_{input_filename}")
    
    # 读取数据
    excel_handler = ExcelHandler()
    stock_data = excel_handler.read_stock_data(input_file)
    
    if stock_data is None:
        print("无法读取股票数据，程序退出。")
        return
    
    # 创建策略
    if config.strategy_name == "MACrossStrategy":
        strategy_params = config.strategy_params["MACrossStrategy"]
        strategy = MACrossStrategy(
            short_window=strategy_params["short_window"], 
            long_window=strategy_params["long_window"],
            buy_shares=config.buy_shares
        )
    elif config.strategy_name == "MomentumStrategy":
        strategy_params = config.strategy_params["MomentumStrategy"]
        strategy = MomentumStrategy(
            momentum_window=strategy_params["momentum_window"], 
            threshold=strategy_params["threshold"],
            buy_shares=config.buy_shares
        )
    else:
        print(f"未知策略: {config.strategy_name}，使用默认策略")
        strategy = MACrossStrategy(short_window=5, long_window=20, buy_shares=100)
    
    # 创建交易系统并运行回测
    trading_system = TradingSystem(strategy, initial_cash=config.initial_cash, 
                                  tax_config=config.tax_rate)
    results = trading_system.run_backtest(stock_data)
    
    # 保存结果
    excel_handler.write_backtest_results(results, output_file)
    
    # 获取统计数据
    stats = trading_system.get_statistics()
    
    # 显示统计信息
    print(f"\n{'='*50}")
    print(f"策略: {strategy.get_name()}")
    print(f"{'='*50}")
    print(f"初始资产: {stats['初始资产']:.2f}")
    print(f"最终资产: {stats['最终资产']:.2f}")
    print(f"收益率: {stats['收益率']:.2f}%")
    print(f"-"*50)
    print(f"买入次数: {stats['买入次数']}")
    print(f"卖出次数: {stats['卖出次数']}")
    print(f"总交易次数: {stats['总交易次数']}")
    print(f"总税费: {stats['总税费']:.2f}")
    print(f"-"*50)
    print(f"最高总资产: {stats['最高总资产']:.2f}")
    print(f"最低总资产: {stats['最低总资产']:.2f}")
    print(f"最大盈利: {stats['最大盈利']:.2f}")
    print(f"最大亏损: {stats['最大亏损']:.2f}")
    print(f"{'='*50}")

if __name__ == "__main__":
    main()