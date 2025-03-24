import akshare as ak
import sqlite3
import time
from datetime import datetime

# 注册日期适配器和转换器
sqlite3.register_adapter(datetime, lambda val: val.strftime('%Y-%m-%d %H:%M:%S'))
sqlite3.register_converter('timestamp', lambda val: datetime.strptime(val.decode('utf-8'), '%Y-%m-%d %H:%M:%S'))

# 创建或连接到SQLite数据库
conn = sqlite3.connect('stocks.db', detect_types=sqlite3.PARSE_DECLTYPES)
c = conn.cursor()

# 创建表格
c.execute('''CREATE TABLE IF NOT EXISTS stock_data
             (timestamp timestamp, symbol TEXT, open REAL, high REAL, low REAL, close REAL, volume INTEGER)''')

def fetch_stock_data(symbol):
    # 获取股票实时数据
    data = ak.stock_zh_a_spot_em()
    stock_data = data[data['代码'] == symbol]

    if not stock_data.empty:
        row = stock_data.iloc[0]
        print(f"{row['最新价']} - {row['成交量']}")

def fetch_stock_minute_data(symbol):
    # 获取股票分钟数据
    data = ak.stock_zh_a_minute(symbol=symbol, period="1", adjust="qfq")
    print(data)
    current_minute = datetime.now().strftime("%Y-%m-%d %H:%M")
    minute_data = data[data["时间"].str.startswith(current_minute)]

    if not minute_data.empty:
        row = minute_data.iloc[0]
        print(row)


if __name__ == "__main__":
    symbol = '603319'  # 指定股票代码
    while True:
        fetch_stock_data(symbol)
        # fetch_stock_minute_data(symbol)
        time.sleep(1)  # 每分钟获取一次数据