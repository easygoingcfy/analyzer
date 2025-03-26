"""交易系统架构设计
"""

import pandas as pd
import numpy as np
from abc import ABC, abstractmethod
from datetime import datetime

# 策略抽象类
class Strategy(ABC):
    @abstractmethod
    def generate_signals(self, data):
        """生成交易信号"""
        pass
    
    @abstractmethod
    def get_name(self):
        """获取策略名称"""
        pass

# 投资组合管理类
class Portfolio:
    def __init__(self, initial_cash=100000, tax_config=None):
        self.initial_cash = initial_cash  # 保存初始资金
        self.cash = initial_cash          # 当前现金
        self.position = 0                 # 当前持仓数量
        self.transactions = []            # 交易记录
        self.initial_buy = True           # 标记是否为初始建仓

        # 跟踪累计成本和盈利
        self.total_investment = 0          # 总投入资金（买入成本+税费-卖出净收入）
        self.total_buy_cost = 0            # 总买入成本
        self.total_buy_tax = 0             # 总买入税费
        self.total_sell_income = 0         # 总卖出收入
        self.total_sell_tax = 0            # 总卖出税费
        
        # 添加初始状态记录
        self.transactions.append({
            '日期': datetime.now().date(),
            '操作': '初始化',
            '价格': 0,
            '数量': 0,
            '成本': 0,
            '税费': 0,
            '总成本': 0,
            '现金': self.cash,
            '持仓': self.position,
            '市值': 0,
            '总资产': self.cash,
            '累计投入': 0,
            '累计盈亏': 0,
            '盈亏率': 0
        })
        
        # 税费配置
        self.tax_config = tax_config or {
            "buy": {
                "commission": 0.0003,
                "transfer_fee": 0.00002
            },
            "sell": {
                "commission": 0.0003,
                "stamp_duty": 0.001,
                "transfer_fee": 0.00002
            },
            "min_commission": 5.0
        }
        
    def calculate_buy_tax(self, price, shares):
        """计算买入税费"""
        amount = price * shares
        commission = max(amount * self.tax_config["buy"]["commission"], 
                         self.tax_config["min_commission"])
        transfer_fee = amount * self.tax_config["buy"]["transfer_fee"]
        total_tax = commission + transfer_fee
        return total_tax
        
    def calculate_sell_tax(self, price, shares):
        """计算卖出税费"""
        amount = price * shares
        commission = max(amount * self.tax_config["sell"]["commission"], 
                         self.tax_config["min_commission"])
        stamp_duty = amount * self.tax_config["sell"]["stamp_duty"]
        transfer_fee = amount * self.tax_config["sell"]["transfer_fee"]
        total_tax = commission + stamp_duty + transfer_fee
        return total_tax
    
    def buy(self, date, price, shares):
        """买入股票"""
        # 处理初始建仓情况
        if self.initial_buy:
            # 计算可以买入的最大股数（必须是100的整数倍）
            max_shares = int(self.cash / price / 100) * 100
            if max_shares > 0:
                shares = max_shares
                self.initial_buy = False
            else:
                return False, "初始资金不足，无法建仓"
        
        cost = price * shares
        tax = self.calculate_buy_tax(price, shares)
        total_cost = cost + tax
        
        if total_cost > self.cash:
            # 资金不足，计算实际可买入数量
            max_shares_with_tax = int(self.cash / (price * (1 + self.tax_config["buy"]["commission"] + self.tax_config["buy"]["transfer_fee"])) / 100) * 100
            if max_shares_with_tax <= 0:
                return False, "资金不足，无法买入"
            shares = max_shares_with_tax
            cost = price * shares
            tax = self.calculate_buy_tax(price, shares)
            total_cost = cost + tax
        
        # 更新资金状态
        self.cash -= total_cost
        self.position += shares
        
        # 更新累计数据
        self.total_buy_cost += cost
        self.total_buy_tax += tax
        self.total_investment += total_cost
        
        # 计算当前盈亏
        current_value = price * self.position
        current_profit = current_value - self.total_investment
        profit_ratio = current_profit / self.total_investment * 100 if self.total_investment > 0 else 0
        
        # 记录交易
        self.transactions.append({
            '日期': date,
            '操作': '买入',
            '价格': price,
            '数量': shares,
            '成本': cost,
            '税费': tax,
            '总成本': total_cost,
            '现金': self.cash,
            '持仓': self.position,
            '市值': current_value,
            '总资产': self.cash + current_value,
            '累计投入': self.total_investment,
            '累计盈亏': current_profit,
            '盈亏率': profit_ratio
        })
        
        return True, f"买入 {shares} 股，价格: {price:.2f}，税费: {tax:.2f}"
    
    def sell(self, date, price, shares):
        """卖出股票"""
        if shares > self.position:
            shares = self.position
            
        if shares <= 0:
            return False, "持仓不足，无法卖出"
            
        income = price * shares
        tax = self.calculate_sell_tax(price, shares)
        net_income = income - tax
        
        # 更新资金状态
        self.cash += net_income
        self.position -= shares
        
        # 更新累计数据
        self.total_sell_income += income
        self.total_sell_tax += tax
        self.total_investment -= net_income  # 卖出收回部分投资
        
        # 确保total_investment不会变为负值
        if self.total_investment < 0:
            self.total_investment = 0
            
        # 计算当前盈亏
        current_value = price * self.position
        current_profit = current_value - self.total_investment + self.total_sell_income - self.total_buy_cost
        profit_ratio = current_profit / self.total_buy_cost * 100 if self.total_buy_cost > 0 else 0
        
        # 记录交易
        self.transactions.append({
            '日期': date,
            '操作': '卖出',
            '价格': price,
            '数量': shares,
            '收入': income,
            '税费': tax,
            '净收入': net_income,
            '现金': self.cash,
            '持仓': self.position,
            '市值': current_value,
            '总资产': self.cash + current_value,
            '累计投入': self.total_investment,
            '累计盈亏': current_profit,
            '盈亏率': profit_ratio
        })
        
        return True, f"卖出 {shares} 股，价格: {price:.2f}，税费: {tax:.2f}"
    
    def update(self, date, price):
        """更新每日持仓价值"""
        if not self.transactions or self.transactions[-1]['日期'] != date:
            current_value = price * self.position
            
            # 计算当前盈亏
            current_profit = 0
            profit_ratio = 0
            
            if self.position > 0:
                current_profit = current_value - self.total_investment
                profit_ratio = current_profit / self.total_investment * 100 if self.total_investment > 0 else 0
            
            self.transactions.append({
                '日期': date,
                '操作': '持有',
                '价格': price,
                '数量': 0,
                '收入/成本': 0,
                '税费': 0,
                '现金': self.cash,
                '持仓': self.position,
                '市值': current_value,
                '总资产': self.cash + current_value,
                '累计投入': self.total_investment,
                '累计盈亏': current_profit,
                '盈亏率': profit_ratio
            })
        
    def get_transactions_df(self):
        """获取交易记录DataFrame"""
        return pd.DataFrame(self.transactions)
    
    def get_statistics(self):
        """计算交易统计数据"""
        df = self.get_transactions_df()
        
        # 交易次数
        buy_count = len(df[df['操作'] == '买入'])
        sell_count = len(df[df['操作'] == '卖出'])
        
        # 税费
        total_tax = df['税费'].sum()
        
        # 资产价值
        max_asset = df['总资产'].max()
        min_asset = df['总资产'].min()
        
        # 计算最新的盈亏数据
        latest_row = df.iloc[-1]
        current_profit = latest_row['累计盈亏']
        profit_ratio = latest_row['盈亏率']
        
        # 计算每笔交易的盈亏
        max_profit_in_single_trade = 0
        max_loss_in_single_trade = 0
        
        buy_records = []
        for idx, row in df.iterrows():
            if row['操作'] == '买入':
                buy_records.append({
                    'price': row['价格'],
                    'shares': row['数量']
                })
            elif row['操作'] == '卖出' and buy_records:
                # 简单的FIFO计算
                remaining_shares = row['数量']
                trade_profit = 0
                
                while remaining_shares > 0 and buy_records:
                    buy_record = buy_records[0]
                    if buy_record['shares'] <= remaining_shares:
                        # 全部卖出
                        trade_profit += (row['价格'] - buy_record['price']) * buy_record['shares']
                        remaining_shares -= buy_record['shares']
                        buy_records.pop(0)
                    else:
                        # 部分卖出
                        trade_profit += (row['价格'] - buy_record['price']) * remaining_shares
                        buy_record['shares'] -= remaining_shares
                        remaining_shares = 0
                
                max_profit_in_single_trade = max(max_profit_in_single_trade, trade_profit)
                max_loss_in_single_trade = min(max_loss_in_single_trade, trade_profit)
        
        # 返回统计结果
        return {
            "初始资产": self.initial_cash,
            "最终资产": df.iloc[-1]['总资产'],
            "收益率": (df.iloc[-1]['总资产'] - self.initial_cash) / self.initial_cash * 100,
            "买入次数": buy_count,
            "卖出次数": sell_count,
            "总交易次数": buy_count + sell_count,
            "总税费": total_tax,
            "最高总资产": max_asset,
            "最低总资产": min_asset,
            "当前盈亏": current_profit,
            "盈亏率": profit_ratio,
            "总买入成本": self.total_buy_cost,
            "总卖出收入": self.total_sell_income,
            "总买入税费": self.total_buy_tax,
            "总卖出税费": self.total_sell_tax,
            "单笔最大盈利": max_profit_in_single_trade,
            "单笔最大亏损": max_loss_in_single_trade
        }

# 交易系统类
class TradingSystem:
    def __init__(self, strategy, initial_cash=100000, tax_config=None):
        self.strategy = strategy
        self.portfolio = Portfolio(initial_cash, tax_config)
        
    def run_backtest(self, data):
        """运行回测"""
        signals = self.strategy.generate_signals(data)
        
        # 第一个有效日期自动建仓（使用第一个非NaN的日期）
        first_valid_idx = 0
        for i in range(len(data)):
            if not pd.isna(data.iloc[i]['收盘']):
                first_valid_idx = i
                break
        
        # 初始建仓
        date = data.iloc[first_valid_idx]['日期'].date() if hasattr(data.iloc[first_valid_idx]['日期'], 'date') else data.iloc[first_valid_idx]['日期']
        price = data.iloc[first_valid_idx]['收盘']
        self.portfolio.buy(date, price, 100)  # 数量无关紧要，会在buy方法中计算
        
        # 根据信号交易
        for i in range(first_valid_idx + 1, len(data)):
            date = data.iloc[i]['日期']
            price = data.iloc[i]['收盘']
            signal = signals[i]
            
            # 执行交易信号
            if signal > 0:  # 买入信号
                self.portfolio.buy(date, price, signal)
            elif signal < 0:  # 卖出信号
                self.portfolio.sell(date, price, abs(signal))
            else:  # 不操作
                self.portfolio.update(date, price)
        
        return self.portfolio.get_transactions_df()
    
    def get_statistics(self):
        """获取交易统计数据"""
        return self.portfolio.get_statistics()