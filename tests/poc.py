import tushare as ts
from stock_pandas import StockDataFrame
import finnhub
import pandas as pd
from datetime import datetime, timedelta
import akshare as ak

finnhub_api_key = 'd32hg9pr01qn0gi40fh0d32hg9pr01qn0gi40fhg'
ts_api_key = 'd45a1d8e8d02489cb9b86ebaa05f7658a327ad7a9558f082dcd896c3'
finnhub_client = finnhub.Client(api_key=finnhub_api_key)

def test_tushare():
    # 1. Get data from Tushare
    pro = ts.pro_api(ts_api_key)
    df = pro.daily(ts_code="300418.SZ", start_date="20250101", end_date="20250913")
    # 2. Convert to StockDataFrame
    stock = StockDataFrame(df)
    # 3. Use indicators
    print(stock['close'])
    print(stock['macd'])

# test_finnhub_insider_sentiment()
def check_tushare_user_points():
    pro = ts.pro_api(token=ts_api_key)
    # 设置你的token
    df = pro.user(token=ts_api_key)

    print(df)

def test_finnhub_stock_insider_transactions(ticker = "AAPL"):

    transactions = finnhub_client.stock_insider_transactions(ticker)

    # Format by date
    formatted_data = {}
    for trans in transactions.get('data', []):
        date = trans.get('filingDate', '')[:10]  # YYYY-MM-DD format
        if date not in formatted_data:
            formatted_data[date] = []
        formatted_data[date].append({
            'name': trans.get('name'),
            'share': trans.get('share'),
            'change': trans.get('change'),
            'transactionPrice': trans.get('transactionPrice'),
            'transactionCode': trans.get('transactionCode')  # B=Buy, S=Sell
        })
    print('done')

 # 2. Fetch Insider Sentiment
def test_finnhub_insider_sentiment(ticker = "AAPL"):
    # Get last 12 months
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)

    sentiment = finnhub_client.stock_insider_sentiment(
      ticker,
      start_date.strftime('%Y-%m-%d'),
      end_date.strftime('%Y-%m-%d')
    )

    # Format by date (monthly data)
    formatted_data = {}
    for item in sentiment.get('data', []):
      date = f"{item['year']}-{str(item['month']).zfill(2)}-01"
      formatted_data[date] = [{
          'year': item['year'],
          'month': item['month'],
          'change': item['change'],
          'mspr': item['mspr']  # Monthly Share Purchase Ratio
      }]


    print('done')




def test_akshare():
    stock_zh_a_hist_df = ak.stock_zh_a_hist(symbol="300418", period="daily", start_date="20250914", end_date='20250915', adjust="")
    print(stock_zh_a_hist_df.columns)
    print(stock_zh_a_hist_df)


if __name__ == '__main__':
    test_tushare()
    # check_tushare_user_points()