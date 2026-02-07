# 导入tushare
import tushare as ts
# 初始化pro接口
pro = ts.pro_api('d45a1d8e8d02489cb9b86ebaa05f7658a327ad7a9558f082dcd896c3')

# 拉取数据
df = pro.stock_basic(**{
    "ts_code": "",
    "name": "",
    "exchange": "",
    "market": "",
    "is_hs": "",
    "list_status": "",
    "limit": "",
    "offset": ""
}, fields=[
    "ts_code",
    "symbol",
    "name",
    "area",
    "industry",
    "cnspell",
    "market",
    "list_date",
    "act_name",
    "act_ent_type"
])
print(df)