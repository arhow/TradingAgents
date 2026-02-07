# 导入tushare
import tushare as ts
# 初始化pro接口
pro = ts.pro_api('d45a1d8e8d02489cb9b86ebaa05f7658a327ad7a9558f082dcd896c3')

# 拉取数据
df = pro.daily(**{
    "ts_code": "",
    "trade_date": "",
    "start_date": "",
    "end_date": "",
    "limit": "",
    "offset": ""
}, fields=[
    "ts_code",
    "trade_date",
    "open",
    "high",
    "low",
    "close",
    "pre_close",
    "change",
    "pct_chg",
    "vol",
    "amount"
])
print(df)