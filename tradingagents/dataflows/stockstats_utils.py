import pandas as pd
from stockstats import wrap
from typing import Annotated
import os
from .config import get_config
from .tushare_utils import get_tushare_utils


class StockstatsUtils:
    @staticmethod
    def get_stock_stats(
        symbol: Annotated[str, "ticker symbol for the company"],
        indicator: Annotated[
            str, "quantitative indicators based off of the stock data for the company"
        ],
        curr_date: Annotated[
            str, "curr date for retrieving stock price data, YYYY-mm-dd"
        ],
        data_dir: Annotated[
            str,
            "directory where the stock data is stored.",
        ],
        online: Annotated[
            bool,
            "whether to use online tools to fetch data or offline tools. If True, will use online tools.",
        ] = False,
    ):
        df = None
        data = None

        if not online:
            try:
                data = pd.read_csv(
                    os.path.join(
                        data_dir,
                        f"{symbol}-YFin-data-2015-01-01-2025-03-25.csv",
                    )
                )
                df = wrap(data)
            except FileNotFoundError:
                raise Exception("Stockstats fail: Yahoo Finance data not fetched yet!")
        else:
            # Get today's date as YYYY-mm-dd to add to cache
            today_date = pd.Timestamp.today()
            curr_date = pd.to_datetime(curr_date)

            end_date = today_date
            start_date = today_date - pd.DateOffset(years=15)
            start_date = start_date.strftime("%Y-%m-%d")
            end_date = end_date.strftime("%Y-%m-%d")

            # Get config and ensure cache directory exists
            config = get_config()
            os.makedirs(config["data_cache_dir"], exist_ok=True)

            data_file = os.path.join(
                config["data_cache_dir"],
                f"{symbol}-data-{start_date}-{end_date}.csv",
            )

            if os.path.exists(data_file):
                data = pd.read_csv(data_file)
            else:
                tushare_utils = get_tushare_utils()
                data = tushare_utils.get_stock_data(symbol, start_date, end_date)
                data.to_csv(data_file, index=False)

            # Ensure date column is datetime and set as index for stockstats
            if 'Date' in data.columns:
                data['Date'] = pd.to_datetime(data['Date'])
                data = data.set_index('Date')
            elif 'date' in data.columns:
                data['date'] = pd.to_datetime(data['date'])
                data = data.set_index('date')

            df = wrap(data)

        df[indicator]  # trigger stockstats to calculate the indicator
        # Compare dates properly - after setting index, access by index
        curr_date_dt = pd.to_datetime(curr_date)
        matching_rows = df[df.index.date == curr_date_dt.date()]

        if not matching_rows.empty:
            indicator_value = matching_rows[indicator].values[0]
            return indicator_value
        else:
            return "N/A: Not a trading day (weekend or holiday)"
