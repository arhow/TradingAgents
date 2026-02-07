import os
import tushare as ts
import dotenv
dotenv.load_dotenv()

ts_key = os.getenv('TUSHARE_TOKEN')
pro = ts.pro_api()

# Get one row and print all column names supported by stock_basic
df = pro.stock_basic(limit=1)  # no fields => all columns
print(list(df.columns))
# print(df.head())
for col in df.columns:
    print(col, df[col].iloc[0])
"""
['ts_code', 'symbol', 'name', 'area', 'industry', 'cnspell', 'market', 'list_date', 'act_name', 'act_ent_type']
ts_code 000001.SZ
symbol 000001
name 平安银行
area 深圳
industry 银行
cnspell payh
market 主板
list_date 19910403
act_name 无实际控制人
act_ent_type 无
"""