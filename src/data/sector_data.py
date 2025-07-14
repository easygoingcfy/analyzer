#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
板块数据提供者
支持行业板块和概念板块的数据获取与分析
"""

import pandas as pd
import numpy as np
import requests
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Union, Tuple
import threading
from src.utils.logger import get_logger

logger = get_logger(__name__)

class SectorDataProvider:
    """板块数据提供者"""
    
    def __init__(self):
        self._cache = {}
        self._cache_timeout = 600  # 10分钟缓存
        self._last_update = {}
        self._lock = threading.Lock()
        
        # 初始化板块映射
        self._init_sector_mapping()
    
    def _init_sector_mapping(self):
        """初始化板块映射关系"""
        # 行业板块映射
        self.industry_sectors = {
            '银行': ['000001', '600036', '002142', '600000', '600015', '601328'],
            '白酒': ['600519', '000858', '000568', '002304', '000596', '600809'],
            '医药生物': ['600276', '300760', '000661', '300015', '002821', '000963'],
            '房地产': ['000002', '600048', '000069', '001979', '600340', '000656'],
            '汽车': ['000625', '600104', '002594', '601633', '600066', '000800'],
            '电子': ['000725', '002415', '300059', '688111', '002230', '300433'],
            '化工': ['600309', '002648', '600438', '000301', '002274', '600596'],
            '机械设备': ['600031', '000157', '300274', '002008', '300014', '000528'],
            '食品饮料': ['600887', '000876', '002568', '600298', '000895', '002304'],
            '非银金融': ['000776', '600030', '000166', '601688', '601318', '601601']
        }
        
        # 概念板块映射
        self.concept_sectors = {
            '新能源汽车': ['002594', '300750', '688005', '002460', '300014', '002050'],
            '芯片概念': ['000725', '002230', '300433', '600584', '000063', '002049'],
            '5G概念': ['000063', '002415', '600050', '000938', '002253', '300136'],
            '人工智能': ['300059', '002241', '300253', '000938', '688088', '688111'],
            '新基建': ['600031', '000725', '000063', '300408', '002202', '600741'],
            '碳中和': ['600438', '600516', '002129', '000151', '000883', '002129'],
            '锂电池': ['300750', '002460', '300014', '002050', '300073', '300037'],
            '光伏': ['688005', '002129', '300274', '000591', '300118', '002506'],
            '军工': ['000768', '002013', '300159', '600038', '000547', '002025'],
            '生物医药': ['300760', '688180', '300142', '300601', '688139', '000661']
        }
    
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
                return self._cache[cache_key].copy() if hasattr(self._cache[cache_key], 'copy') else self._cache[cache_key]
        return None
    
    def _set_cache(self, cache_key: str, data):
        """设置缓存"""
        with self._lock:
            self._cache[cache_key] = data.copy() if hasattr(data, 'copy') else data
            self._last_update[cache_key] = time.time()
    
    def get_sector_list(self, sector_type: str = 'all') -> pd.DataFrame:
        """
        获取板块列表
        
        Args:
            sector_type: 'industry' (行业板块), 'concept' (概念板块), 'all' (全部)
        
        Returns:
            板块列表DataFrame
        """
        cache_key = self._get_cache_key("sector_list", sector_type=sector_type)
        cached_data = self._get_from_cache(cache_key)
        if cached_data is not None:
            return cached_data
        
        try:
            sectors = []
            
            if sector_type in ['industry', 'all']:
                for sector_name, stocks in self.industry_sectors.items():
                    sectors.append({
                        '板块代码': f'IND_{sector_name}',
                        '板块名称': sector_name,
                        '板块类型': '行业板块',
                        '成分股数量': len(stocks),
                        '成分股': ','.join(stocks)
                    })
            
            if sector_type in ['concept', 'all']:
                for sector_name, stocks in self.concept_sectors.items():
                    sectors.append({
                        '板块代码': f'CON_{sector_name}',
                        '板块名称': sector_name,
                        '板块类型': '概念板块',
                        '成分股数量': len(stocks),
                        '成分股': ','.join(stocks)
                    })
            
            if not sectors:
                logger.warning(f"未找到板块类型: {sector_type}")
                return pd.DataFrame()
            
            result = pd.DataFrame(sectors)
            self._set_cache(cache_key, result)
            logger.info(f"成功获取{sector_type}板块列表，共{len(result)}个板块")
            return result
            
        except Exception as e:
            logger.error(f"获取板块列表失败: {e}")
            return pd.DataFrame()
    
    def get_sector_realtime_data(self, sector_codes: List[str] = None) -> pd.DataFrame:
        """
        获取板块实时数据
        
        Args:
            sector_codes: 板块代码列表，None表示获取所有板块
        
        Returns:
            板块实时数据DataFrame
        """
        cache_key = self._get_cache_key("sector_realtime", sector_codes=str(sector_codes))
        cached_data = self._get_from_cache(cache_key)
        if cached_data is not None:
            return cached_data
        
        try:
            # 先获取板块列表
            sector_list = self.get_sector_list()
            if sector_list.empty:
                return pd.DataFrame()
            
            # 筛选指定板块
            if sector_codes:
                sector_list = sector_list[sector_list['板块代码'].isin(sector_codes)]
            
            sector_data = []
            
            for _, sector in sector_list.iterrows():
                sector_code = sector['板块代码']
                sector_name = sector['板块名称']
                sector_type = sector['板块类型']
                stock_codes = sector['成分股'].split(',')
                
                # 计算板块指标
                sector_metrics = self._calculate_sector_metrics(stock_codes, sector_name)
                
                sector_data.append({
                    '板块代码': sector_code,
                    '板块名称': sector_name,
                    '板块类型': sector_type,
                    '成分股数量': len(stock_codes),
                    '平均涨跌幅': sector_metrics['avg_change_pct'],
                    '涨停数量': sector_metrics['limit_up_count'],
                    '跌停数量': sector_metrics['limit_down_count'],
                    '总成交额': sector_metrics['total_amount'],
                    '平均换手率': sector_metrics['avg_turnover'],
                    '领涨股': sector_metrics['top_gainer'],
                    '领跌股': sector_metrics['top_loser'],
                    '热度指数': sector_metrics['heat_index'],
                    '更新时间': datetime.now().strftime('%H:%M:%S')
                })
            
            if sector_data:
                result = pd.DataFrame(sector_data)
                # 按热度指数排序
                result = result.sort_values('热度指数', ascending=False)
                
                self._set_cache(cache_key, result)
                logger.info(f"成功获取{len(result)}个板块的实时数据")
                return result
            else:
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"获取板块实时数据失败: {e}")
            return self._generate_mock_sector_data()
    
    def _calculate_sector_metrics(self, stock_codes: List[str], sector_name: str) -> Dict:
        """计算板块指标"""
        try:
            # 这里应该获取真实的股票数据，暂时用模拟数据
            metrics = self._generate_mock_sector_metrics(stock_codes, sector_name)
            return metrics
            
        except Exception as e:
            logger.warning(f"计算板块{sector_name}指标失败: {e}")
            return self._generate_mock_sector_metrics(stock_codes, sector_name)
    
    def _generate_mock_sector_metrics(self, stock_codes: List[str], sector_name: str) -> Dict:
        """生成模拟板块指标"""
        import random
        
        # 生成随机指标
        stock_count = len(stock_codes)
        avg_change_pct = random.uniform(-8.0, 8.0)
        
        # 根据板块特性调整
        sector_bias = {
            '银行': -1.0,
            '白酒': 2.0,
            '医药生物': 1.5,
            '新能源汽车': 3.0,
            '芯片概念': 2.5,
            '5G概念': 1.8
        }
        
        if sector_name in sector_bias:
            avg_change_pct += sector_bias[sector_name]
        
        # 限制在合理范围内
        avg_change_pct = max(-10.0, min(10.0, avg_change_pct))
        
        # 计算其他指标
        limit_up_count = random.randint(0, max(1, stock_count // 5)) if avg_change_pct > 5 else 0
        limit_down_count = random.randint(0, max(1, stock_count // 10)) if avg_change_pct < -5 else 0
        
        total_amount = random.randint(1000000000, 50000000000)  # 10亿到500亿
        avg_turnover = random.uniform(1.0, 15.0)
        
        # 随机选择领涨股和领跌股
        top_gainer = random.choice(stock_codes) if stock_codes else ''
        top_loser = random.choice(stock_codes) if stock_codes else ''
        
        # 计算热度指数（综合多个因素）
        heat_index = (
            abs(avg_change_pct) * 10 +  # 涨跌幅权重
            (limit_up_count + limit_down_count) * 20 +  # 涨跌停权重
            (total_amount / 1000000000) * 2 +  # 成交额权重
            avg_turnover * 3  # 换手率权重
        )
        heat_index = round(min(100, heat_index), 1)
        
        return {
            'avg_change_pct': round(avg_change_pct, 2),
            'limit_up_count': limit_up_count,
            'limit_down_count': limit_down_count,
            'total_amount': total_amount,
            'avg_turnover': round(avg_turnover, 2),
            'top_gainer': top_gainer,
            'top_loser': top_loser,
            'heat_index': heat_index
        }
    
    def _generate_mock_sector_data(self) -> pd.DataFrame:
        """生成模拟板块数据"""
        try:
            sector_list = self.get_sector_list()
            if sector_list.empty:
                # 如果获取不到板块列表，创建基础数据
                basic_sectors = [
                    {'板块代码': 'IND_银行', '板块名称': '银行', '板块类型': '行业板块', '成分股': '000001,600036'},
                    {'板块代码': 'IND_白酒', '板块名称': '白酒', '板块类型': '行业板块', '成分股': '600519,000858'},
                    {'板块代码': 'CON_新能源汽车', '板块名称': '新能源汽车', '板块类型': '概念板块', '成分股': '002594,300750'},
                    {'板块代码': 'CON_芯片概念', '板块名称': '芯片概念', '板块类型': '概念板块', '成分股': '000725,002230'}
                ]
                sector_list = pd.DataFrame(basic_sectors)
            
            return self.get_sector_realtime_data()
            
        except Exception as e:
            logger.error(f"生成模拟板块数据失败: {e}")
            return pd.DataFrame()
    
    def get_sector_historical_data(self, sector_code: str, days: int = 30) -> pd.DataFrame:
        """
        获取板块历史数据
        
        Args:
            sector_code: 板块代码
            days: 历史天数
        
        Returns:
            板块历史数据DataFrame
        """
        cache_key = self._get_cache_key("sector_history", sector_code=sector_code, days=days)
        cached_data = self._get_from_cache(cache_key)
        if cached_data is not None:
            return cached_data
        
        try:
            # 获取板块信息
            sector_list = self.get_sector_list()
            sector_info = sector_list[sector_list['板块代码'] == sector_code]
            
            if sector_info.empty:
                logger.warning(f"未找到板块: {sector_code}")
                return pd.DataFrame()
            
            sector_name = sector_info.iloc[0]['板块名称']
            stock_codes = sector_info.iloc[0]['成分股'].split(',')
            
            # 生成历史数据
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            dates = []
            current = start_date
            while current <= end_date:
                if current.weekday() < 5:  # 工作日
                    dates.append(current)
                current += timedelta(days=1)
            
            history_data = []
            for date in dates:
                # 模拟历史指标
                metrics = self._generate_mock_sector_metrics(stock_codes, sector_name)
                
                history_data.append({
                    '日期': date,
                    '板块代码': sector_code,
                    '板块名称': sector_name,
                    '平均涨跌幅': metrics['avg_change_pct'],
                    '涨停数量': metrics['limit_up_count'],
                    '跌停数量': metrics['limit_down_count'],
                    '总成交额': metrics['total_amount'],
                    '平均换手率': metrics['avg_turnover'],
                    '热度指数': metrics['heat_index']
                })
            
            result = pd.DataFrame(history_data)
            result = result.sort_values('日期')
            
            self._set_cache(cache_key, result)
            logger.info(f"成功获取板块{sector_name}的{days}天历史数据")
            return result
            
        except Exception as e:
            logger.error(f"获取板块历史数据失败: {e}")
            return pd.DataFrame()
    
    def search_sectors(self, keyword: str) -> pd.DataFrame:
        """
        搜索板块
        
        Args:
            keyword: 搜索关键词
        
        Returns:
            匹配的板块列表
        """
        try:
            sector_list = self.get_sector_list()
            if sector_list.empty:
                return pd.DataFrame()
            
            # 搜索板块名称
            mask = sector_list['板块名称'].str.contains(keyword, na=False, case=False)
            result = sector_list[mask]
            
            logger.info(f"搜索'{keyword}'找到{len(result)}个板块")
            return result
            
        except Exception as e:
            logger.error(f"搜索板块失败: {e}")
            return pd.DataFrame()
    
    def get_sector_stocks(self, sector_code: str) -> List[str]:
        """
        获取板块成分股
        
        Args:
            sector_code: 板块代码
        
        Returns:
            成分股代码列表
        """
        try:
            sector_list = self.get_sector_list()
            sector_info = sector_list[sector_list['板块代码'] == sector_code]
            
            if sector_info.empty:
                return []
            
            stock_codes = sector_info.iloc[0]['成分股'].split(',')
            return [code.strip() for code in stock_codes if code.strip()]
            
        except Exception as e:
            logger.error(f"获取板块成分股失败: {e}")
            return []
    
    def get_hot_sectors(self, sector_type: str = 'all', limit: int = 10) -> pd.DataFrame:
        """
        获取热门板块排行
        
        Args:
            sector_type: 板块类型
            limit: 返回数量限制
        
        Returns:
            热门板块DataFrame
        """
        try:
            sector_data = self.get_sector_realtime_data()
            if sector_data.empty:
                return pd.DataFrame()
            
            # 筛选板块类型
            if sector_type != 'all':
                type_map = {'industry': '行业板块', 'concept': '概念板块'}
                if sector_type in type_map:
                    sector_data = sector_data[sector_data['板块类型'] == type_map[sector_type]]
            
            # 按热度指数排序
            hot_sectors = sector_data.nlargest(limit, '热度指数')
            
            logger.info(f"成功获取{len(hot_sectors)}个热门板块")
            return hot_sectors
            
        except Exception as e:
            logger.error(f"获取热门板块失败: {e}")
            return pd.DataFrame()

# 全局板块数据提供者实例
sector_data_provider = SectorDataProvider()
