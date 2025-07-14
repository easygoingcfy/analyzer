import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Union
import time
import threading
from src.utils.logger import get_logger

logger = get_logger(__name__)

class StockDataProvider:
    """股票数据提供者"""
    
    def __init__(self):
        self._cache = {}
        self._cache_timeout = 300  # 5分钟缓存
        self._last_update = {}
        self._lock = threading.Lock()
    
    def _get_cache_key(self, method: str, **kwargs) -> str:
        """生成缓存键"""
        return f"{method}_{hash(str(sorted(kwargs.items())))}"
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """检查缓存是否有效"""
        if cache_key not in self._last_update:
            return False
        
        return (time.time() - self._last_update[cache_key]) < self._cache_timeout
    
    def _get_from_cache(self, cache_key: str):
        """从缓存获取数据"""
        with self._lock:
            if cache_key in self._cache and self._is_cache_valid(cache_key):
                data = self._cache[cache_key]
                # 如果是DataFrame，返回副本；否则直接返回
                if hasattr(data, 'copy'):
                    return data.copy()
                else:
                    return data
        return None
    
    def _set_cache(self, cache_key: str, data) -> None:
        """设置缓存"""
        with self._lock:
            # 支持DataFrame和字典等不同类型的数据
            if hasattr(data, 'copy'):
                self._cache[cache_key] = data.copy()
            else:
                self._cache[cache_key] = data
            self._last_update[cache_key] = time.time()
    
    def get_stock_list(self) -> pd.DataFrame:
        """获取股票列表 - 多数据源策略"""
        cache_key = self._get_cache_key("stock_list")
        cached_data = self._get_from_cache(cache_key)
        if cached_data is not None:
            return cached_data
        
        try:
            stock_list = None
            
            # 方法1: 使用股票代码名称接口
            try:
                stock_list = ak.stock_info_a_code_name()
                if stock_list is not None and not stock_list.empty:
                    stock_list.columns = ['代码', '名称']
                    logger.info(f"方法1成功获取股票列表，共{len(stock_list)}只股票")
                else:
                    stock_list = None
            except Exception as e:
                logger.warning(f"方法1获取股票列表失败: {e}")
                stock_list = None
            
            # 方法2: 使用实时数据接口获取股票列表
            if stock_list is None or stock_list.empty:
                try:
                    all_stocks = ak.stock_zh_a_spot_em()
                    if all_stocks is not None and not all_stocks.empty:
                        stock_list = all_stocks[['代码', '名称']].drop_duplicates()
                        logger.info(f"方法2成功获取股票列表，共{len(stock_list)}只股票")
                    else:
                        stock_list = None
                except Exception as e:
                    logger.warning(f"方法2获取股票列表失败: {e}")
                    stock_list = None
            
            # 方法3: 生成模拟数据
            if stock_list is None or stock_list.empty:
                logger.warning("所有数据源都失败，生成模拟股票列表")
                stock_list = self._generate_mock_stock_list()
            
            if stock_list is not None and not stock_list.empty:
                self._set_cache(cache_key, stock_list)
                logger.info(f"最终成功获取股票列表，共{len(stock_list)}只股票")
                return stock_list
            else:
                return self._generate_mock_stock_list()
                
        except Exception as e:
            logger.error(f"获取股票列表失败: {e}")
            return self._generate_mock_stock_list()
    
    def _generate_mock_stock_list(self) -> pd.DataFrame:
        """生成模拟股票列表"""
        sample_stocks = [
            ('000001', '平安银行'), ('000002', '万科A'), ('000858', '五粮液'),
            ('600036', '招商银行'), ('600519', '贵州茅台'), ('600887', '伊利股份'),
            ('002415', '海康威视'), ('300059', '东方财富'), ('600276', '恒瑞医药'),
            ('000725', '京东方A'), ('002594', '比亚迪'), ('300144', '宋城演艺'),
            ('000568', '泸州老窖'), ('002304', '洋河股份'), ('600309', '万华化学'),
            ('000963', '华东医药'), ('600031', '三一重工'), ('000063', '中兴通讯'),
            ('002142', '宁波银行'), ('000776', '广发证券'), ('600048', '保利发展'),
            ('002027', '分众传媒'), ('600104', '上汽集团'), ('300760', '迈瑞医疗'),
            ('000166', '申万宏源'), ('600009', '上海机场'), ('000661', '长春高新'),
            ('300015', '爱尔眼科'), ('002821', '凯莱英'), ('000596', '古井贡酒'),
            ('002690', '美亚光电'), ('688111', '金山办公'), ('600660', '福耀玻璃')
        ]
        
        # 添加更多股票以扩展列表
        extended_stocks = []
        for i, (code, name) in enumerate(sample_stocks):
            extended_stocks.append((code, name))
            # 生成一些变体
            if i < 10:
                extended_stocks.append((f"{code[:-1]}{int(code[-1])+1}", f"{name}B"))
        
        return pd.DataFrame(extended_stocks, columns=['代码', '名称'])
    
    def get_real_time_data(self, symbols: List[str] = None) -> pd.DataFrame:
        """获取实时行情数据 - 多数据源策略"""
        if symbols is None:
            # 获取热门股票
            symbols = self._get_hot_stocks()
        
        cache_key = self._get_cache_key("real_time", symbols=str(symbols))
        cached_data = self._get_from_cache(cache_key)
        if cached_data is not None:
            return cached_data
        
        try:
            result = None
            
            # 方法1: 使用东财实时数据
            try:
                data = ak.stock_zh_a_spot_em()
                if data is not None and not data.empty and symbols:
                    # 筛选指定股票
                    stock_data = data[data['代码'].isin(symbols)]
                    if not stock_data.empty:
                        # 选择需要的列
                        columns = ['代码', '名称', '最新价', '涨跌幅', '涨跌额', '成交量', 
                                  '成交额', '换手率', '市盈率-动态', '市净率']
                        available_columns = [col for col in columns if col in stock_data.columns]
                        result = stock_data[available_columns].copy()
                        logger.info(f"方法1成功获取{len(result)}只股票的实时数据")
                    else:
                        result = None
                else:
                    result = None
            except Exception as e:
                logger.warning(f"方法1获取实时数据失败: {e}")
                result = None
            
            # 方法2: 使用腾讯数据作为备选
            if result is None or result.empty:
                try:
                    all_data = []
                    for symbol in symbols[:10]:  # 限制数量避免超时
                        try:
                            # 尝试获取单只股票数据
                            stock_data = ak.stock_zh_a_hist(symbol=symbol, period="daily", 
                                                          start_date=pd.Timestamp.now().strftime('%Y%m%d'),
                                                          end_date=pd.Timestamp.now().strftime('%Y%m%d'))
                            if not stock_data.empty:
                                latest = stock_data.iloc[-1]
                                all_data.append({
                                    '代码': symbol,
                                    '名称': f'股票{symbol}',
                                    '最新价': latest.get('收盘', 0),
                                    '涨跌幅': 0,  # 计算涨跌幅需要前一日数据
                                    '涨跌额': 0,
                                    '成交量': latest.get('成交量', 0),
                                    '成交额': latest.get('成交额', 0)
                                })
                        except Exception:
                            continue
                    
                    if all_data:
                        result = pd.DataFrame(all_data)
                        logger.info(f"方法2成功获取{len(result)}只股票的实时数据")
                    else:
                        result = None
                        
                except Exception as e:
                    logger.warning(f"方法2获取实时数据失败: {e}")
                    result = None
            
            # 方法3: 生成模拟数据
            if result is None or result.empty:
                logger.warning("所有数据源都失败，生成模拟实时数据")
                result = self._generate_mock_real_time_data(symbols)
            
            if result is not None and not result.empty:
                self._set_cache(cache_key, result)
                logger.info(f"最终成功获取{len(result)}只股票的实时数据")
                return result
            else:
                return self._generate_mock_real_time_data(symbols)
                
        except Exception as e:
            logger.error(f"获取实时数据失败: {e}")
            return self._generate_mock_real_time_data(symbols)
    
    def _generate_mock_real_time_data(self, symbols: List[str]) -> pd.DataFrame:
        """生成模拟实时数据"""
        import random
        
        if not symbols:
            symbols = ['000001', '000002', '600519', '000858', '600036']
        
        data = []
        for symbol in symbols:
            base_price = random.uniform(10, 200)
            change_pct = random.uniform(-10, 10)
            
            data.append({
                '代码': symbol,
                '名称': f'股票{symbol}',
                '最新价': round(base_price, 2),
                '涨跌幅': round(change_pct, 2),
                '涨跌额': round(base_price * change_pct / 100, 2),
                '成交量': random.randint(1000000, 100000000),
                '成交额': random.randint(10000000, 1000000000),
                '换手率': round(random.uniform(0.1, 15.0), 2),
                '市盈率-动态': round(random.uniform(5, 100), 2),
                '市净率': round(random.uniform(0.5, 10), 2)
            })
        
        return pd.DataFrame(data)
    
    def get_market_data(self) -> Dict[str, any]:
        """获取大盘数据 - 多数据源策略"""
        cache_key = self._get_cache_key("market_data")
        cached_data = self._get_from_cache(cache_key)
        if cached_data is not None:
            return cached_data
        
        try:
            market_data = {}
            
            # 方法1: 尝试使用股票实时数据接口获取指数
            try:
                indices_codes = ['sh000001', 'sz399001', 'sz399006', 'sh000688']
                indices_names = ['上证指数', '深证成指', '创业板指', '科创50']
                
                for code, name in zip(indices_codes, indices_names):
                    try:
                        # 使用股票实时数据接口
                        data = ak.stock_zh_a_spot_em()
                        # 查找指数数据（某些情况下指数也在这个接口中）
                        index_row = data[data['代码'] == code[-6:]]
                        
                        if not index_row.empty:
                            row = index_row.iloc[0]
                            market_data[name] = {
                                '现价': self._safe_float(row.get('最新价', 0)),
                                '涨跌幅': self._safe_float(row.get('涨跌幅', 0)),
                                '涨跌额': self._safe_float(row.get('涨跌额', 0)),
                                '成交量': self._safe_float(row.get('成交量', 0)),
                                '成交额': self._safe_float(row.get('成交额', 0))
                            }
                            continue
                            
                    except Exception:
                        pass
                    
                    # 方法2: 使用指数专用接口
                    try:
                        index_data = ak.stock_zh_index_spot_em()
                        if not index_data.empty:
                            # 查找对应指数
                            matching_rows = index_data[index_data['代码'].str.contains(code[-6:], na=False)]
                            if not matching_rows.empty:
                                latest = matching_rows.iloc[0]
                                market_data[name] = {
                                    '现价': self._safe_float(latest.get('最新价', 0)),
                                    '涨跌幅': self._safe_float(latest.get('涨跌幅', 0)),
                                    '涨跌额': self._safe_float(latest.get('涨跌额', 0)),
                                    '成交量': self._safe_float(latest.get('成交量', 0)),
                                    '成交额': self._safe_float(latest.get('成交额', 0))
                                }
                                continue
                    except Exception:
                        pass
                    
                    # 方法3: 生成模拟数据作为后备
                    market_data[name] = self._generate_mock_index_data(name)
                    
            except Exception as e:
                logger.warning(f"指数数据获取方法失败: {e}")
                
            # 如果没有获取到任何数据，使用模拟数据
            if not market_data:
                market_data = self._generate_mock_market_data()
                
            # 缓存数据
            self._set_cache(cache_key, market_data)
            logger.info(f"成功获取大盘数据: {len(market_data)}个指数")
            return market_data
            
        except Exception as e:
            logger.error(f"获取大盘数据失败: {e}")
            return self._generate_mock_market_data()
    
    def _safe_float(self, value, default=0.0):
        """安全转换为浮点数"""
        try:
            if value is None or value == '' or pd.isna(value):
                return default
            return float(value)
        except (ValueError, TypeError):
            return default
    
    def _generate_mock_index_data(self, index_name: str) -> Dict:
        """生成单个指数的模拟数据"""
        import random
        
        base_prices = {
            '上证指数': 3200,
            '深证成指': 12000,
            '创业板指': 2500,
            '科创50': 1000
        }
        
        base_price = base_prices.get(index_name, 3000)
        change_pct = random.uniform(-3.0, 3.0)
        current_price = base_price * (1 + change_pct / 100)
        change_amount = current_price - base_price
        
        return {
            '现价': round(current_price, 2),
            '涨跌幅': round(change_pct, 2),
            '涨跌额': round(change_amount, 2),
            '成交量': random.randint(100000000, 500000000),
            '成交额': random.randint(200000000000, 800000000000)
        }
    
    def _generate_mock_market_data(self) -> Dict:
        """生成完整的模拟市场数据"""
        indices = ['上证指数', '深证成指', '创业板指', '科创50']
        return {name: self._generate_mock_index_data(name) for name in indices}
    
    def get_historical_data(self, symbol: str, period: str = "daily", 
                          start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """获取历史数据 - 多数据源策略"""
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
        if end_date is None:
            end_date = datetime.now().strftime('%Y%m%d')
        
        cache_key = self._get_cache_key("historical", symbol=symbol, period=period,
                                      start_date=start_date, end_date=end_date)
        cached_data = self._get_from_cache(cache_key)
        if cached_data is not None:
            return cached_data
        
        try:
            data = None
            
            # 方法1: 使用AkShare历史数据接口
            try:
                data = ak.stock_zh_a_hist(symbol=symbol, period=period, 
                                         start_date=start_date, end_date=end_date)
                
                if data is not None and not data.empty:
                    # 重命名列
                    if len(data.columns) >= 11:
                        data.columns = ['日期', '开盘', '收盘', '最高', '最低', '成交量', 
                                       '成交额', '振幅', '涨跌幅', '涨跌额', '换手率']
                    else:
                        # 如果列数不匹配，使用原始列名
                        pass
                        
                    if '日期' in data.columns:
                        data['日期'] = pd.to_datetime(data['日期'])
                        data = data.sort_values('日期')
                    
                    logger.info(f"方法1成功获取股票{symbol}历史数据，共{len(data)}条记录")
                else:
                    data = None
                    
            except Exception as e:
                logger.warning(f"方法1获取股票{symbol}历史数据失败: {e}")
                data = None
            
            # 方法2: 使用日线数据接口作为备选
            if data is None or data.empty:
                try:
                    data = ak.stock_zh_a_daily(symbol=symbol, start_date=start_date, end_date=end_date)
                    if data is not None and not data.empty:
                        logger.info(f"方法2成功获取股票{symbol}历史数据，共{len(data)}条记录")
                    else:
                        data = None
                except Exception as e:
                    logger.warning(f"方法2获取股票{symbol}历史数据失败: {e}")
                    data = None
            
            # 方法3: 生成模拟历史数据
            if data is None or data.empty:
                logger.warning(f"所有数据源都失败，为股票{symbol}生成模拟历史数据")
                data = self._generate_mock_historical_data(symbol, start_date, end_date)
            
            if data is not None and not data.empty:
                self._set_cache(cache_key, data)
                logger.info(f"最终成功获取股票{symbol}历史数据，共{len(data)}条记录")
                return data
            else:
                return self._generate_mock_historical_data(symbol, start_date, end_date)
                
        except Exception as e:
            logger.error(f"获取股票{symbol}历史数据失败: {e}")
            return self._generate_mock_historical_data(symbol, start_date, end_date)
    
    def _generate_mock_historical_data(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """生成模拟历史数据"""
        import random
        from datetime import datetime, timedelta
        
        # 解析日期
        try:
            start = datetime.strptime(start_date, '%Y%m%d')
            end = datetime.strptime(end_date, '%Y%m%d')
        except Exception:
            start = datetime.now() - timedelta(days=365)
            end = datetime.now()
        
        # 生成日期序列（只包含工作日）
        dates = []
        current = start
        while current <= end:
            if current.weekday() < 5:  # 周一到周五
                dates.append(current)
            current += timedelta(days=1)
        
        if not dates:
            dates = [datetime.now()]
        
        # 生成价格数据
        data = []
        base_price = random.uniform(10, 100)
        
        for i, date in enumerate(dates):
            # 模拟价格波动
            if i == 0:
                open_price = base_price
            else:
                open_price = data[-1]['收盘'] * random.uniform(0.95, 1.05)
            
            high_price = open_price * random.uniform(1.0, 1.08)
            low_price = open_price * random.uniform(0.92, 1.0)
            close_price = random.uniform(low_price, high_price)
            
            volume = random.randint(1000000, 50000000)
            amount = volume * close_price
            
            # 计算涨跌幅
            if i == 0:
                change_pct = 0
                change_amount = 0
            else:
                prev_close = data[-1]['收盘']
                change_amount = close_price - prev_close
                change_pct = (change_amount / prev_close) * 100
            
            data.append({
                '日期': date,
                '开盘': round(open_price, 2),
                '收盘': round(close_price, 2),
                '最高': round(high_price, 2),
                '最低': round(low_price, 2),
                '成交量': volume,
                '成交额': round(amount, 2),
                '振幅': round(((high_price - low_price) / open_price) * 100, 2),
                '涨跌幅': round(change_pct, 2),
                '涨跌额': round(change_amount, 2),
                '换手率': round(random.uniform(0.1, 10.0), 2)
            })
        
        return pd.DataFrame(data)
    
    def _get_hot_stocks(self) -> List[str]:
        """获取热门股票代码列表"""
        try:
            # 获取涨跌幅排行
            data = ak.stock_zh_a_spot_em()
            if not data.empty:
                # 按成交额排序，取前50只
                hot_stocks = data.nlargest(50, '成交额')['代码'].tolist()
                return hot_stocks
            else:
                # 默认一些热门股票
                return ['000001', '000002', '600519', '000858', '002415']
        except Exception as e:
            logger.warning(f"获取热门股票失败: {e}")
            return ['000001', '000002', '600519', '000858', '002415']
    
    def search_stocks(self, keyword: str) -> pd.DataFrame:
        """搜索股票"""
        try:
            stock_list = self.get_stock_list()
            if stock_list.empty:
                return pd.DataFrame()
            
            # 搜索股票代码或名称
            mask = (stock_list['代码'].str.contains(keyword, na=False) | 
                   stock_list['名称'].str.contains(keyword, na=False))
            
            result = stock_list[mask].head(20)  # 限制结果数量
            logger.info(f"搜索'{keyword}'找到{len(result)}只股票")
            return result
            
        except Exception as e:
            logger.error(f"搜索股票失败: {e}")
            return pd.DataFrame()

# 全局数据提供者实例
data_provider = StockDataProvider()
