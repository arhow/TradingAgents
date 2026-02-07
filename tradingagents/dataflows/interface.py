from typing import Annotated, Dict
from .reddit_utils import fetch_top_from_category
from .yfin_utils import *
from .stockstats_utils import *
from .googlenews_utils import *
from .finnhub_utils import get_data_in_range
from .tushare_utils import get_tushare_utils
from dateutil.relativedelta import relativedelta
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import json
import os
import pandas as pd
from tqdm import tqdm
import yfinance as yf
from openai import OpenAI
from .config import get_config, set_config, DATA_DIR
import traceback


def get_finnhub_news(
    ticker: Annotated[
        str,
        "Search query of a company's, e.g. 'AAPL, TSM, etc.",
    ],
    curr_date: Annotated[str, "Current date in yyyy-mm-dd format"],
    look_back_days: Annotated[int, "how many days to look back"],
):
    """
    Retrieve news about a company within a time frame

    Args
        ticker (str): ticker for the company you are interested in
        start_date (str): Start date in yyyy-mm-dd format
        end_date (str): End date in yyyy-mm-dd format
    Returns
        str: dataframe containing the news of the company in the time frame

    """

    start_date = datetime.strptime(curr_date, "%Y-%m-%d")
    before = start_date - relativedelta(days=look_back_days)
    before = before.strftime("%Y-%m-%d")

    result = get_data_in_range(ticker, before, curr_date, "news_data", DATA_DIR)

    if len(result) == 0:
        return ""

    combined_result = ""
    for day, data in result.items():
        if len(data) == 0:
            continue
        for entry in data:
            current_news = (
                "### " + entry["headline"] + f" ({day})" + "\n" + entry["summary"]
            )
            combined_result += current_news + "\n\n"

    return f"## {ticker} News, from {before} to {curr_date}:\n" + str(combined_result)


def get_finnhub_company_insider_sentiment(
    ticker: Annotated[str, "ticker symbol for the company"],
    curr_date: Annotated[
        str,
        "current date of you are trading at, yyyy-mm-dd",
    ],
    look_back_days: Annotated[int, "number of days to look back"],
):
    """
    Retrieve insider sentiment about a company (retrieved from public SEC information) for the past 15 days
    Args:
        ticker (str): ticker symbol of the company
        curr_date (str): current date you are trading on, yyyy-mm-dd
    Returns:
        str: a report of the sentiment in the past 15 days starting at curr_date
    """

    date_obj = datetime.strptime(curr_date, "%Y-%m-%d")
    before = date_obj - relativedelta(days=look_back_days)
    before = before.strftime("%Y-%m-%d")

    data = get_data_in_range(ticker, before, curr_date, "insider_senti", DATA_DIR)

    if len(data) == 0:
        return ""

    result_str = ""
    seen_dicts = []
    for date, senti_list in data.items():
        for entry in senti_list:
            if entry not in seen_dicts:
                result_str += f"### {entry['year']}-{entry['month']}:\nChange: {entry['change']}\nMonthly Share Purchase Ratio: {entry['mspr']}\n\n"
                seen_dicts.append(entry)

    return (
        f"## {ticker} Insider Sentiment Data for {before} to {curr_date}:\n"
        + result_str
        + "The change field refers to the net buying/selling from all insiders' transactions. The mspr field refers to monthly share purchase ratio."
    )


def get_finnhub_company_insider_transactions(
    ticker: Annotated[str, "ticker symbol"],
    curr_date: Annotated[
        str,
        "current date you are trading at, yyyy-mm-dd",
    ],
    look_back_days: Annotated[int, "how many days to look back"],
):
    """
    Retrieve insider transcaction information about a company (retrieved from public SEC information) for the past 15 days
    Args:
        ticker (str): ticker symbol of the company
        curr_date (str): current date you are trading at, yyyy-mm-dd
    Returns:
        str: a report of the company's insider transaction/trading informtaion in the past 15 days
    """

    date_obj = datetime.strptime(curr_date, "%Y-%m-%d")
    before = date_obj - relativedelta(days=look_back_days)
    before = before.strftime("%Y-%m-%d")

    data = get_data_in_range(ticker, before, curr_date, "insider_trans", DATA_DIR)

    if len(data) == 0:
        return ""

    result_str = ""

    seen_dicts = []
    for date, senti_list in data.items():
        for entry in senti_list:
            if entry not in seen_dicts:
                result_str += f"### Filing Date: {entry['filingDate']}, {entry['name']}:\nChange:{entry['change']}\nShares: {entry['share']}\nTransaction Price: {entry['transactionPrice']}\nTransaction Code: {entry['transactionCode']}\n\n"
                seen_dicts.append(entry)

    return (
        f"## {ticker} insider transactions from {before} to {curr_date}:\n"
        + result_str
        + "The change field reflects the variation in share count—here a negative number indicates a reduction in holdings—while share specifies the total number of shares involved. The transactionPrice denotes the per-share price at which the trade was executed, and transactionDate marks when the transaction occurred. The name field identifies the insider making the trade, and transactionCode (e.g., S for sale) clarifies the nature of the transaction. FilingDate records when the transaction was officially reported, and the unique id links to the specific SEC filing, as indicated by the source. Additionally, the symbol ties the transaction to a particular company, isDerivative flags whether the trade involves derivative securities, and currency notes the currency context of the transaction."
    )


def get_simfin_balance_sheet(
    ticker: Annotated[str, "ticker symbol"],
    freq: Annotated[
        str,
        "reporting frequency of the company's financial history: annual / quarterly",
    ],
    curr_date: Annotated[str, "current date you are trading at, yyyy-mm-dd"],
):
    data_path = os.path.join(
        DATA_DIR,
        "fundamental_data",
        "simfin_data_all",
        "balance_sheet",
        "companies",
        "us",
        f"us-balance-{freq}.csv",
    )
    df = pd.read_csv(data_path, sep=";")

    # Convert date strings to datetime objects and remove any time components
    df["Report Date"] = pd.to_datetime(df["Report Date"], utc=True).dt.normalize()
    df["Publish Date"] = pd.to_datetime(df["Publish Date"], utc=True).dt.normalize()

    # Convert the current date to datetime and normalize
    curr_date_dt = pd.to_datetime(curr_date, utc=True).normalize()

    # Filter the DataFrame for the given ticker and for reports that were published on or before the current date
    filtered_df = df[(df["Ticker"] == ticker) & (df["Publish Date"] <= curr_date_dt)]

    # Check if there are any available reports; if not, return a notification
    if filtered_df.empty:
        print("No balance sheet available before the given current date.")
        return ""

    # Get the most recent balance sheet by selecting the row with the latest Publish Date
    latest_balance_sheet = filtered_df.loc[filtered_df["Publish Date"].idxmax()]

    # drop the SimFinID column
    latest_balance_sheet = latest_balance_sheet.drop("SimFinId")

    return (
        f"## {freq} balance sheet for {ticker} released on {str(latest_balance_sheet['Publish Date'])[0:10]}: \n"
        + str(latest_balance_sheet)
        + "\n\nThis includes metadata like reporting dates and currency, share details, and a breakdown of assets, liabilities, and equity. Assets are grouped as current (liquid items like cash and receivables) and noncurrent (long-term investments and property). Liabilities are split between short-term obligations and long-term debts, while equity reflects shareholder funds such as paid-in capital and retained earnings. Together, these components ensure that total assets equal the sum of liabilities and equity."
    )


def get_simfin_cashflow(
    ticker: Annotated[str, "ticker symbol"],
    freq: Annotated[
        str,
        "reporting frequency of the company's financial history: annual / quarterly",
    ],
    curr_date: Annotated[str, "current date you are trading at, yyyy-mm-dd"],
):
    data_path = os.path.join(
        DATA_DIR,
        "fundamental_data",
        "simfin_data_all",
        "cash_flow",
        "companies",
        "us",
        f"us-cashflow-{freq}.csv",
    )
    df = pd.read_csv(data_path, sep=";")

    # Convert date strings to datetime objects and remove any time components
    df["Report Date"] = pd.to_datetime(df["Report Date"], utc=True).dt.normalize()
    df["Publish Date"] = pd.to_datetime(df["Publish Date"], utc=True).dt.normalize()

    # Convert the current date to datetime and normalize
    curr_date_dt = pd.to_datetime(curr_date, utc=True).normalize()

    # Filter the DataFrame for the given ticker and for reports that were published on or before the current date
    filtered_df = df[(df["Ticker"] == ticker) & (df["Publish Date"] <= curr_date_dt)]

    # Check if there are any available reports; if not, return a notification
    if filtered_df.empty:
        print("No cash flow statement available before the given current date.")
        return ""

    # Get the most recent cash flow statement by selecting the row with the latest Publish Date
    latest_cash_flow = filtered_df.loc[filtered_df["Publish Date"].idxmax()]

    # drop the SimFinID column
    latest_cash_flow = latest_cash_flow.drop("SimFinId")

    return (
        f"## {freq} cash flow statement for {ticker} released on {str(latest_cash_flow['Publish Date'])[0:10]}: \n"
        + str(latest_cash_flow)
        + "\n\nThis includes metadata like reporting dates and currency, share details, and a breakdown of cash movements. Operating activities show cash generated from core business operations, including net income adjustments for non-cash items and working capital changes. Investing activities cover asset acquisitions/disposals and investments. Financing activities include debt transactions, equity issuances/repurchases, and dividend payments. The net change in cash represents the overall increase or decrease in the company's cash position during the reporting period."
    )


def get_simfin_income_statements(
    ticker: Annotated[str, "ticker symbol"],
    freq: Annotated[
        str,
        "reporting frequency of the company's financial history: annual / quarterly",
    ],
    curr_date: Annotated[str, "current date you are trading at, yyyy-mm-dd"],
):
    data_path = os.path.join(
        DATA_DIR,
        "fundamental_data",
        "simfin_data_all",
        "income_statements",
        "companies",
        "us",
        f"us-income-{freq}.csv",
    )
    df = pd.read_csv(data_path, sep=";")

    # Convert date strings to datetime objects and remove any time components
    df["Report Date"] = pd.to_datetime(df["Report Date"], utc=True).dt.normalize()
    df["Publish Date"] = pd.to_datetime(df["Publish Date"], utc=True).dt.normalize()

    # Convert the current date to datetime and normalize
    curr_date_dt = pd.to_datetime(curr_date, utc=True).normalize()

    # Filter the DataFrame for the given ticker and for reports that were published on or before the current date
    filtered_df = df[(df["Ticker"] == ticker) & (df["Publish Date"] <= curr_date_dt)]

    # Check if there are any available reports; if not, return a notification
    if filtered_df.empty:
        print("No income statement available before the given current date.")
        return ""

    # Get the most recent income statement by selecting the row with the latest Publish Date
    latest_income = filtered_df.loc[filtered_df["Publish Date"].idxmax()]

    # drop the SimFinID column
    latest_income = latest_income.drop("SimFinId")

    return (
        f"## {freq} income statement for {ticker} released on {str(latest_income['Publish Date'])[0:10]}: \n"
        + str(latest_income)
        + "\n\nThis includes metadata like reporting dates and currency, share details, and a comprehensive breakdown of the company's financial performance. Starting with Revenue, it shows Cost of Revenue and resulting Gross Profit. Operating Expenses are detailed, including SG&A, R&D, and Depreciation. The statement then shows Operating Income, followed by non-operating items and Interest Expense, leading to Pretax Income. After accounting for Income Tax and any Extraordinary items, it concludes with Net Income, representing the company's bottom-line profit or loss for the period."
    )


def get_google_news(
    query: Annotated[str, "Query to search with"],
    curr_date: Annotated[str, "Curr date in yyyy-mm-dd format"],
    look_back_days: Annotated[int, "how many days to look back"],
) -> str:
    query = query.replace(" ", "+")

    start_date = datetime.strptime(curr_date, "%Y-%m-%d")
    before = start_date - relativedelta(days=look_back_days)
    before = before.strftime("%Y-%m-%d")

    news_results = getNewsData(query, before, curr_date)

    news_str = ""

    for news in news_results:
        news_str += (
            f"### {news['title']} (source: {news['source']}) \n\n{news['snippet']}\n\n"
        )

    if len(news_results) == 0:
        return ""

    return f"## {query} Google News, from {before} to {curr_date}:\n\n{news_str}"


def get_reddit_global_news(
    start_date: Annotated[str, "Start date in yyyy-mm-dd format"],
    look_back_days: Annotated[int, "how many days to look back"],
    max_limit_per_day: Annotated[int, "Maximum number of news per day"],
) -> str:
    """
    Retrieve the latest top reddit news
    Args:
        start_date: Start date in yyyy-mm-dd format
        end_date: End date in yyyy-mm-dd format
    Returns:
        str: A formatted dataframe containing the latest news articles posts on reddit and meta information in these columns: "created_utc", "id", "title", "selftext", "score", "num_comments", "url"
    """

    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    before = start_date - relativedelta(days=look_back_days)
    before = before.strftime("%Y-%m-%d")

    posts = []
    # iterate from start_date to end_date
    curr_date = datetime.strptime(before, "%Y-%m-%d")

    total_iterations = (start_date - curr_date).days + 1
    pbar = tqdm(desc=f"Getting Global News on {start_date}", total=total_iterations)

    while curr_date <= start_date:
        curr_date_str = curr_date.strftime("%Y-%m-%d")
        fetch_result = fetch_top_from_category(
            "global_news",
            curr_date_str,
            max_limit_per_day,
            data_path=os.path.join(DATA_DIR, "reddit_data"),
        )
        posts.extend(fetch_result)
        curr_date += relativedelta(days=1)
        pbar.update(1)

    pbar.close()

    if len(posts) == 0:
        return ""

    news_str = ""
    for post in posts:
        if post["content"] == "":
            news_str += f"### {post['title']}\n\n"
        else:
            news_str += f"### {post['title']}\n\n{post['content']}\n\n"

    return f"## Global News Reddit, from {before} to {curr_date}:\n{news_str}"


def get_reddit_company_news(
    ticker: Annotated[str, "ticker symbol of the company"],
    start_date: Annotated[str, "Start date in yyyy-mm-dd format"],
    look_back_days: Annotated[int, "how many days to look back"],
    max_limit_per_day: Annotated[int, "Maximum number of news per day"],
) -> str:
    """
    Retrieve the latest top reddit news
    Args:
        ticker: ticker symbol of the company
        start_date: Start date in yyyy-mm-dd format
        end_date: End date in yyyy-mm-dd format
    Returns:
        str: A formatted dataframe containing the latest news articles posts on reddit and meta information in these columns: "created_utc", "id", "title", "selftext", "score", "num_comments", "url"
    """

    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    before = start_date - relativedelta(days=look_back_days)
    before = before.strftime("%Y-%m-%d")

    posts = []
    # iterate from start_date to end_date
    curr_date = datetime.strptime(before, "%Y-%m-%d")

    total_iterations = (start_date - curr_date).days + 1
    pbar = tqdm(
        desc=f"Getting Company News for {ticker} on {start_date}",
        total=total_iterations,
    )

    while curr_date <= start_date:
        curr_date_str = curr_date.strftime("%Y-%m-%d")
        fetch_result = fetch_top_from_category(
            "company_news",
            curr_date_str,
            max_limit_per_day,
            ticker,
            data_path=os.path.join(DATA_DIR, "reddit_data"),
        )
        posts.extend(fetch_result)
        curr_date += relativedelta(days=1)

        pbar.update(1)

    pbar.close()

    if len(posts) == 0:
        return ""

    news_str = ""
    for post in posts:
        if post["content"] == "":
            news_str += f"### {post['title']}\n\n"
        else:
            news_str += f"### {post['title']}\n\n{post['content']}\n\n"

    return f"##{ticker} News Reddit, from {before} to {curr_date}:\n\n{news_str}"


def get_stock_stats_indicators_window(
    symbol: Annotated[str, "ticker symbol of the company"],
    indicator: Annotated[str, "technical indicator to get the analysis and report of"],
    curr_date: Annotated[
        str, "The current trading date you are trading on, YYYY-mm-dd"
    ],
    look_back_days: Annotated[int, "how many days to look back"],
    online: Annotated[bool, "to fetch data online or offline"],
) -> str:

    best_ind_params = {
        # Moving Averages
        "close_50_sma": (
            "50 SMA: A medium-term trend indicator. "
            "Usage: Identify trend direction and serve as dynamic support/resistance. "
            "Tips: It lags price; combine with faster indicators for timely signals."
        ),
        "close_200_sma": (
            "200 SMA: A long-term trend benchmark. "
            "Usage: Confirm overall market trend and identify golden/death cross setups. "
            "Tips: It reacts slowly; best for strategic trend confirmation rather than frequent trading entries."
        ),
        "close_10_ema": (
            "10 EMA: A responsive short-term average. "
            "Usage: Capture quick shifts in momentum and potential entry points. "
            "Tips: Prone to noise in choppy markets; use alongside longer averages for filtering false signals."
        ),
        # MACD Related
        "macd": (
            "MACD: Computes momentum via differences of EMAs. "
            "Usage: Look for crossovers and divergence as signals of trend changes. "
            "Tips: Confirm with other indicators in low-volatility or sideways markets."
        ),
        "macds": (
            "MACD Signal: An EMA smoothing of the MACD line. "
            "Usage: Use crossovers with the MACD line to trigger trades. "
            "Tips: Should be part of a broader strategy to avoid false positives."
        ),
        "macdh": (
            "MACD Histogram: Shows the gap between the MACD line and its signal. "
            "Usage: Visualize momentum strength and spot divergence early. "
            "Tips: Can be volatile; complement with additional filters in fast-moving markets."
        ),
        # Momentum Indicators
        "rsi": (
            "RSI: Measures momentum to flag overbought/oversold conditions. "
            "Usage: Apply 70/30 thresholds and watch for divergence to signal reversals. "
            "Tips: In strong trends, RSI may remain extreme; always cross-check with trend analysis."
        ),
        # Volatility Indicators
        "boll": (
            "Bollinger Middle: A 20 SMA serving as the basis for Bollinger Bands. "
            "Usage: Acts as a dynamic benchmark for price movement. "
            "Tips: Combine with the upper and lower bands to effectively spot breakouts or reversals."
        ),
        "boll_ub": (
            "Bollinger Upper Band: Typically 2 standard deviations above the middle line. "
            "Usage: Signals potential overbought conditions and breakout zones. "
            "Tips: Confirm signals with other tools; prices may ride the band in strong trends."
        ),
        "boll_lb": (
            "Bollinger Lower Band: Typically 2 standard deviations below the middle line. "
            "Usage: Indicates potential oversold conditions. "
            "Tips: Use additional analysis to avoid false reversal signals."
        ),
        "atr": (
            "ATR: Averages true range to measure volatility. "
            "Usage: Set stop-loss levels and adjust position sizes based on current market volatility. "
            "Tips: It's a reactive measure, so use it as part of a broader risk management strategy."
        ),
        # Volume-Based Indicators
        "vwma": (
            "VWMA: A moving average weighted by volume. "
            "Usage: Confirm trends by integrating price action with volume data. "
            "Tips: Watch for skewed results from volume spikes; use in combination with other volume analyses."
        ),
        "mfi": (
            "MFI: The Money Flow Index is a momentum indicator that uses both price and volume to measure buying and selling pressure. "
            "Usage: Identify overbought (>80) or oversold (<20) conditions and confirm the strength of trends or reversals. "
            "Tips: Use alongside RSI or MACD to confirm signals; divergence between price and MFI can indicate potential reversals."
        ),
    }

    if indicator not in best_ind_params:
        raise ValueError(
            f"Indicator {indicator} is not supported. Please choose from: {list(best_ind_params.keys())}"
        )

    end_date = curr_date
    curr_date = datetime.strptime(curr_date, "%Y-%m-%d")
    before = curr_date - relativedelta(days=look_back_days)

    if not online:
        # read from YFin data
        data = pd.read_csv(
            os.path.join(
                DATA_DIR,
                f"market_data/price_data/{symbol}-YFin-data-2015-01-01-2025-03-25.csv",
            )
        )
        data["Date"] = pd.to_datetime(data["Date"], utc=True)
        dates_in_df = data["Date"].astype(str).str[:10]

        ind_string = ""
        while curr_date >= before:
            # only do the trading dates
            if curr_date.strftime("%Y-%m-%d") in dates_in_df.values:
                indicator_value = get_stockstats_indicator(
                    symbol, indicator, curr_date.strftime("%Y-%m-%d"), online
                )

                ind_string += f"{curr_date.strftime('%Y-%m-%d')}: {indicator_value}\n"

            curr_date = curr_date - relativedelta(days=1)
    else:
        # online gathering
        ind_string = ""
        while curr_date >= before:
            indicator_value = get_stockstats_indicator(
                symbol, indicator, curr_date.strftime("%Y-%m-%d"), online
            )

            ind_string += f"{curr_date.strftime('%Y-%m-%d')}: {indicator_value}\n"

            curr_date = curr_date - relativedelta(days=1)

    result_str = (
        f"## {indicator} values from {before.strftime('%Y-%m-%d')} to {end_date}:\n\n"
        + ind_string
        + "\n\n"
        + best_ind_params.get(indicator, "No description available.")
    )

    return result_str


def get_stockstats_indicator(
    symbol: Annotated[str, "ticker symbol of the company"],
    indicator: Annotated[str, "technical indicator to get the analysis and report of"],
    curr_date: Annotated[
        str, "The current trading date you are trading on, YYYY-mm-dd"
    ],
    online: Annotated[bool, "to fetch data online or offline"],
) -> str:

    curr_date = datetime.strptime(curr_date, "%Y-%m-%d")
    curr_date = curr_date.strftime("%Y-%m-%d")

    try:
        indicator_value = StockstatsUtils.get_stock_stats(
            symbol,
            indicator,
            curr_date,
            os.path.join(DATA_DIR, "market_data", "price_data"),
            online=online,
        )
    except Exception as e:
        print(
            f"Error getting stockstats indicator data for indicator {indicator} on {curr_date}: {e}"
        )
        return ""

    return str(indicator_value)


def get_YFin_data_window(
    symbol: Annotated[str, "ticker symbol of the company"],
    curr_date: Annotated[str, "Start date in yyyy-mm-dd format"],
    look_back_days: Annotated[int, "how many days to look back"],
) -> str:
    # calculate past days
    date_obj = datetime.strptime(curr_date, "%Y-%m-%d")
    before = date_obj - relativedelta(days=look_back_days)
    start_date = before.strftime("%Y-%m-%d")

    # read in data
    data = pd.read_csv(
        os.path.join(
            DATA_DIR,
            f"market_data/price_data/{symbol}-YFin-data-2015-01-01-2025-03-25.csv",
        )
    )

    # Extract just the date part for comparison
    data["DateOnly"] = data["Date"].str[:10]

    # Filter data between the start and end dates (inclusive)
    filtered_data = data[
        (data["DateOnly"] >= start_date) & (data["DateOnly"] <= curr_date)
    ]

    # Drop the temporary column we created
    filtered_data = filtered_data.drop("DateOnly", axis=1)

    # Set pandas display options to show the full DataFrame
    with pd.option_context(
        "display.max_rows", None, "display.max_columns", None, "display.width", None
    ):
        df_string = filtered_data.to_string()

    return (
        f"## Raw Market Data for {symbol} from {start_date} to {curr_date}:\n\n"
        + df_string
    )


def get_YFin_data_online(
    symbol: Annotated[str, "ticker symbol of the company"],
    start_date: Annotated[str, "Start date in yyyy-mm-dd format"],
    end_date: Annotated[str, "End date in yyyy-mm-dd format"],
):

    datetime.strptime(start_date, "%Y-%m-%d")
    datetime.strptime(end_date, "%Y-%m-%d")

    # Create ticker object
    ticker = yf.Ticker(symbol.upper())

    # Fetch historical data for the specified date range
    data = ticker.history(start=start_date, end=end_date)

    # Check if data is empty
    if data.empty:
        return (
            f"No data found for symbol '{symbol}' between {start_date} and {end_date}"
        )

    # Remove timezone info from index for cleaner output
    if data.index.tz is not None:
        data.index = data.index.tz_localize(None)

    # Round numerical values to 2 decimal places for cleaner display
    numeric_columns = ["Open", "High", "Low", "Close", "Adj Close"]
    for col in numeric_columns:
        if col in data.columns:
            data[col] = data[col].round(2)

    # Convert DataFrame to CSV string
    csv_string = data.to_csv()

    # Add header information
    header = f"# Stock data for {symbol.upper()} from {start_date} to {end_date}\n"
    header += f"# Total records: {len(data)}\n"
    header += f"# Data retrieved on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

    return header + csv_string


def get_tushare_data_online(symbol: Annotated[str, "ticker symbol of the company"],
                            start_date: Annotated[str, "Start date in yyyy-mm-dd format"],
                            end_date: Annotated[str, "End date in yyyy-mm-dd format"],
                            ):
    """
    Retrieve Chinese stock price data for a given ticker symbol from Tushare.

    Args:
        symbol: Ticker symbol for Chinese stocks (e.g., '000001.SZ' for Shenzhen, '600000.SH' for Shanghai)
        start_date: Start date in yyyy-mm-dd format
        end_date: End date in yyyy-mm-dd format

    Returns:
        str: A formatted CSV string containing the stock price data
    """

    # Validate date formats
    datetime.strptime(start_date, "%Y-%m-%d")
    datetime.strptime(end_date, "%Y-%m-%d")

    try:
        # Get or create TushareUtils instance
        tushare_utils = get_tushare_utils()

        # Fetch stock data
        data = tushare_utils.get_stock_data(symbol, start_date, end_date)

        # Check if data is empty
        if data.empty:
            return f"No data found for symbol '{symbol}' between {start_date} and {end_date}"

        # Round numerical values to 2 decimal places for cleaner display
        numeric_columns = ['ts_code', 'trade_date', 'open', 'high', 'low', 'close', 'pre_close', 'change', 'pct_chg', 'vol', 'amount']

        for col in numeric_columns:
            if col in data.columns:
                data[col] = data[col].round(2)

        # Convert DataFrame to CSV string
        csv_string = data.to_csv()

        # Add header information
        header = f"# Chinese stock data for {symbol} from {start_date} to {end_date}\n"
        header += f"# Total records: {len(data)}\n"
        header += f"# Data retrieved from Tushare on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        return header + csv_string

    except Exception as e:
        return f"Error fetching Tushare data for {symbol}: {str(e)}. Please ensure TUSHARE_TOKEN is set."


def get_tushare_stock_info(
    symbol: Annotated[str, "Stock symbol (e.g., 000001.SZ, 600000.SH)"],
    info_type: Annotated[
        str,
        "Type of information: 'company', 'news', 'concept', 'financial', 'announcement'",
    ],
    date: Annotated[str, "Date for news/announcements in YYYY-MM-DD format"],
    max_limit: Annotated[int, "Maximum number of items to return"] = 10,
) -> str:
    """
    Retrieve various types of stock information from Tushare Pro API.

    This function provides access to company information, news, concepts,
    financial data, and announcements for Chinese A-share stocks.

    Args:
        symbol: Stock symbol (e.g., '000001.SZ' for Shenzhen, '600000.SH' for Shanghai)
        info_type: Type of information to fetch
        date: Date for time-sensitive queries (YYYY-MM-DD format)
        max_limit: Maximum number of results to return

    Returns:
        str: Formatted information as a human-readable string
    """
    try:
        # Get or create TushareUtils instance
        tushare_utils = get_tushare_utils()

        # Fetch the requested information
        info_list = tushare_utils.get_stock_info(
            symbol=symbol,
            info_type=info_type,
            date=date,
            max_limit=max_limit
        )

        # Format the results for display
        formatted_result = tushare_utils.format_stock_info(info_list)

        # Add header
        header = f"# Tushare Stock Information\n"
        header += f"# Symbol: {symbol}\n"
        header += f"# Info Type: {info_type}\n"
        header += f"# Date: {date}\n"
        header += f"# Retrieved: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        header += "=" * 60 + "\n\n"

        return header + formatted_result

    except Exception as e:
        return f"Error fetching {info_type} for '{symbol}': {str(e)}"


def get_tushare_stock_news(
    symbol: Annotated[str, "Stock symbol (e.g., 000001.SZ, 600000.SH)"],
    date: Annotated[str, "Date for news in YYYY-MM-DD format"],
    interval: Annotated[int, "Number of days to look back"] = 7,
    max_limit: Annotated[int, "Maximum number of news items to return"] = None,
) -> str:
    """
    Get filtered news for a specific Chinese stock from Tushare.

    Args:
        symbol: Stock symbol (e.g., '000001.SZ')
        date: Date for news queries
        interval: Number of days to look back
        max_limit: Maximum number of results

    Returns:
        Formatted string with stock-specific news
    """
    try:
        tushare_utils = get_tushare_utils()

        # Get filtered stock information including news
        stock_info = tushare_utils.get_stock_info(
            symbol=symbol,
            date=date,
            interval=interval,
            max_limit=max_limit
        )

        if not stock_info:
            return f"No news found for {symbol} in the last {interval} days"

        # Format output
        output = f"## {symbol} News from Tushare\n"
        output += f"## Date: {date} (looking back {interval} days)\n"
        output += "=" * 60 + "\n\n"

        for item in stock_info:
            if item['type'] == 'company_info':
                output += f"### Company: {item['name']} ({item['symbol']})\n"
                output += f"Industry: {item['industry']}, Area: {item['area']}\n\n"
            elif item['type'] in ['news', 'cctv_news', 'announcement', 'ir_qa']:
                output += f"### [{item['type'].upper()}] {item['title']}\n"
                output += f"Date: {item['datetime']}, Source: {item['source']}\n"
                output += f"{item['content']}\n\n"

        return output

    except Exception as e:
        return f"Error fetching news for '{symbol}': {str(e)}"


def get_tushare_news(
    date: Annotated[str, "Date for news in YYYY-MM-DD format"],
    interval: Annotated[int, "Number of days to look back"] = 7,
) -> str:
    """
    Get all news from Tushare without filtering by specific stock.
    Includes news from multiple sources, CCTV news, announcements, and IR Q&A.

    Args:
        date: Date for news queries
        interval: Number of days to look back

    Returns:
        Formatted string with all available news
    """
    try:
        tushare_utils = get_tushare_utils()

        # Get all news
        news_df = tushare_utils.get_news(
            date=date,
            interval=interval
        )

        if news_df.empty:
            return f"No news found for the last {interval} days"

        # Format output
        output = f"## Tushare News (All Sources)\n"
        output += f"## Date: {date} (looking back {interval} days)\n"
        output += f"## Total items: {len(news_df)}\n"
        output += "=" * 60 + "\n\n"

        # Group by type
        news_types = news_df['type'].unique()

        for news_type in news_types:
            type_news = news_df[news_df['type'] == news_type]
            output += f"### {news_type.upper()} ({len(type_news)} items)\n"
            output += "-" * 40 + "\n"

            # Show first few items from each type
            for _, row in type_news.head(5).iterrows():
                output += f"\n**{row['title']}**\n"
                output += f"Date: {row['datetime']}"
                if row.get('source'):
                    output += f", Source: {row['source']}"
                if row.get('ts_code'):
                    output += f", Stock: {row['ts_code']}"
                output += "\n"

                # Show content preview
                content = row['content']
                if content and len(content) > 200:
                    output += f"{content[:200]}...\n"
                elif content:
                    output += f"{content}\n"
                output += "\n"

            if len(type_news) > 5:
                output += f"... and {len(type_news) - 5} more {news_type} items\n\n"

        return output

    except Exception as e:
        return f"Error fetching news: {str(e)}"


def get_YFin_data(
    symbol: Annotated[str, "ticker symbol of the company"],
    start_date: Annotated[str, "Start date in yyyy-mm-dd format"],
    end_date: Annotated[str, "End date in yyyy-mm-dd format"],
) -> str:
    # read in data
    data = pd.read_csv(
        os.path.join(
            DATA_DIR,
            f"market_data/price_data/{symbol}-YFin-data-2015-01-01-2025-03-25.csv",
        )
    )

    if end_date > "2025-03-25":
        raise Exception(
            f"Get_YFin_Data: {end_date} is outside of the data range of 2015-01-01 to 2025-03-25"
        )

    # Extract just the date part for comparison
    data["DateOnly"] = data["Date"].str[:10]

    # Filter data between the start and end dates (inclusive)
    filtered_data = data[
        (data["DateOnly"] >= start_date) & (data["DateOnly"] <= end_date)
    ]

    # Drop the temporary column we created
    filtered_data = filtered_data.drop("DateOnly", axis=1)

    # remove the index from the dataframe
    filtered_data = filtered_data.reset_index(drop=True)

    return filtered_data


def get_stock_news_openai(symbol, ticker, curr_date):
    """
    Search for stock news from Chinese social media and news platforms.
    Searches each site individually for better coverage.

    Args:
        symbol: Stock code (e.g., '300418.SZ')
        ticker: Company name (e.g., '昆仑万维')
        curr_date: Current date in YYYY-MM-DD format

    Returns:
        str: JSON formatted search results or error message
    """
    config = get_config()
    client = OpenAI(base_url=config["backend_url"])

    # Define sites to search
    SITES = [
        ("东方财富股吧", ["guba.eastmoney.com"], "social"),
        ("百度贴吧", ["tieba.baidu.com"], "social"),
        ("知乎", ["zhihu.com"], "social"),
        ("微博", ["m.weibo.cn", "weibo.com"], "social"),
        ("雪球", ["xueqiu.com"], "social"),
        ("新浪财经", ["finance.sina.com.cn", "sina.com.cn"], "news"),
        ("华尔街见闻", ["wallstreetcn.com"], "news"),
        ("同花顺", ["10jqka.com.cn"], "news"),
        ("东方财富新闻", ["eastmoney.com"], "news"),
        ("财联社", ["cls.cn"], "news"),
    ]

    try:
        # Calculate date range
        from datetime import datetime, timedelta
        end_date_dt = datetime.strptime(curr_date, '%Y-%m-%d')
        start_date_dt = end_date_dt - timedelta(days=7)
        start_date = start_date_dt.strftime('%Y-%m-%d')
        end_date = end_date_dt.strftime('%Y-%m-%d')

        # Generate date variants for better search coverage
        date_variants = []
        for i in range(7, -1, -1):
            dt = end_date_dt - timedelta(days=i)
            date_variants.extend([
                dt.strftime('%Y-%m-%d'),
                dt.strftime('%Y年%m月%d日'),
                dt.strftime('%m-%d'),
                f"{dt.month}月{dt.day}日"
            ])

        # Keyword variants
        kw_variants = [ticker, symbol, "股票", "讨论", "帖子", "快讯", "公告"]

        def build_site_prompt(site_name, domains, category):
            """Build search prompt for a specific site"""
            dom = " OR ".join([f"site:{d}" for d in domains])
            kw = " / ".join(kw_variants)
            dates = " / ".join(date_variants[:8])  # Show first 8 for brevity

            return f"""
TARGET WINDOW
- Only keep items dated {start_date}–{end_date} inclusive, timezone = Asia/Shanghai.

SCOPE (single site)
- Platform: {site_name} ({category})
- Domains: {dom}
- Search with keywords: {kw}
- Date strings to match: {dates}

SEARCH RULES
1) Run multiple queries using the above domains (`site:`) + keywords + date strings.
2) If zero results, retry by:
   a) swapping keywords,
   b) using only code "{symbol}",
   c) dropping explicit date tokens from the query (but still filter by date at extraction)
3) Deduplicate by URL. Exclude pages without a clear timestamp within the window.

OUTPUT (JSON format):
{{
  "platform": "{site_name}",
  "category": "{category}",
  "items": [
    {{
      "author": "author name or null",
      "datetime_local": "YYYY-MM-DD HH:MM",
      "title_or_snippet": "content snippet",
      "url": "source URL"
    }}
  ],
  "found_count": number
}}
"""

        def search_one_site(site_info):
            """Search a single site and return results"""
            site_name, domains, category = site_info
            try:
                response = client.responses.create(
                    model=config.get("quick_think_llm", "gpt-4o"),
                    input=[
                        {"role": "system", "content": """You are an AI assistant with access to websearch functions.
The websearch function empowers you for real-time web search and information retrieval, particularly for current and
relevant data from the internet. Always include the source URL for information fetched from the web."""},
                        {"role": "user", "content": [
                            {"type": "input_text", "text": build_site_prompt(site_name, domains, category)}
                        ]}
                    ],
                    tools=[{
                        "type": "web_search_preview",
                        "search_context_size": "high",
                        "user_location": {"type": "approximate"}
                    }],
                    max_output_tokens=10000,  # Enough for single site results
                    top_p=1,
                    store=True,
                )

                text = response.output_text if response.output_text else None
                if text:
                    # Try to parse as JSON
                    try:
                        result = json.loads(text)
                        return result
                    except json.JSONDecodeError:
                        # Return raw text if not JSON
                        return {
                            "platform": site_name,
                            "category": category,
                            "items": [],
                            "found_count": 0,
                            "error": "Failed to parse response"
                        }
                return None

            except Exception as e:
                print(f"Error searching {site_name}: {e}")
                return None

        # Search all sites
        all_items = []
        search_summary = []

        print(f"\nSearching for {ticker} ({symbol}) from {start_date} to {end_date}")
        print("=" * 60)

        for site in SITES:
            print(f"Searching {site[0]}...")
            result = search_one_site(site)

            if result:
                # Extract items
                items = result.get("items", [])
                for item in items:
                    item["platform"] = result.get("platform", site[0])
                    item["category"] = result.get("category", site[2])
                all_items.extend(items)

                # Track search summary
                search_summary.append({
                    "site": site[0],
                    "found_count": result.get("found_count", len(items))
                })
                print(f"  Found {len(items)} items")
            else:
                print(f"  No response received")
                search_summary.append({
                    "site": site[0],
                    "found_count": 0
                })

        # Deduplicate items by URL
        seen_urls = set()
        unique_items = []
        for item in all_items:
            url = item.get("url")
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_items.append(item)

        # Sort by datetime
        unique_items.sort(key=lambda x: x.get("datetime_local", ""))

        # Prepare final result
        final_result = {
            "items": unique_items,
            "summary": {
                "total_items_found": len(all_items),
                "unique_items": len(unique_items),
                "sites_searched": len(SITES),
                "date_range": f"{start_date} to {end_date}",
                "search_details": search_summary
            }
        }

        print("\n" + "=" * 60)
        print(f"Total items found: {len(all_items)}")
        print(f"Unique items: {len(unique_items)}")

        # Convert to JSON string for output
        output = json.dumps(final_result, ensure_ascii=False, indent=2)
        return output

    except Exception as e:
        print(f"Error in get_stock_news_openai: {e}")
        print(traceback.format_exc())
        return None


def get_global_news_openai(curr_date):
    config = get_config()

    # Check tool-level configuration first (if method provided)
    if method:
        tool_vendors = config.get("tool_vendors", {})
        if method in tool_vendors:
            return tool_vendors[method]

    # Fall back to category-level configuration
    return config.get("data_vendors", {}).get(category, "default")

def route_to_vendor(method: str, *args, **kwargs):
    """Route method calls to appropriate vendor implementation with fallback support."""
    category = get_category_for_method(method)
    vendor_config = get_vendor(category, method)
    primary_vendors = [v.strip() for v in vendor_config.split(',')]

    if method not in VENDOR_METHODS:
        raise ValueError(f"Method '{method}' not supported")

    # Build fallback chain: primary vendors first, then remaining available vendors
    all_available_vendors = list(VENDOR_METHODS[method].keys())
    fallback_vendors = primary_vendors.copy()
    for vendor in all_available_vendors:
        if vendor not in fallback_vendors:
            fallback_vendors.append(vendor)

    for vendor in fallback_vendors:
        if vendor not in VENDOR_METHODS[method]:
            continue

        vendor_impl = VENDOR_METHODS[method][vendor]
        impl_func = vendor_impl[0] if isinstance(vendor_impl, list) else vendor_impl

        try:
            return impl_func(*args, **kwargs)
        except AlphaVantageRateLimitError:
            continue  # Only rate limits trigger fallback

    raise RuntimeError(f"No available vendor for '{method}'")