# Tushare data utilities for Chinese stock market data

import tushare as ts
import pandas as pd
from typing import Annotated, Optional
from datetime import datetime, timedelta
import traceback
import os

# Initialize Tushare API with token
def init_tushare_api(token: Optional[str] = None):
    """
    Initialize Tushare Pro API with token.
    Token can be passed or read from environment variable.
    """
    if token is None:
        token = os.getenv("TUSHARE_TOKEN")

    if not token:
        raise ValueError(
            "Tushare token not provided. "
            "Please set TUSHARE_TOKEN environment variable or pass token directly."
        )

    ts.set_token(token)
    return ts.pro_api()


class TushareUtils:
    def __init__(self, token: Optional[str] = None):
        """Initialize with Tushare Pro API"""
        self.pro = init_tushare_api(token)

    def get_stock_data(
        self,
        symbol: Annotated[str, "ticker symbol (e.g., 000001.SZ, 600000.SH)"],
        start_date: Annotated[str, "start date in YYYY-MM-DD format"],
        end_date: Annotated[str, "end date in YYYY-MM-DD format"],
    ) -> pd.DataFrame:
        """
        Retrieve Chinese stock price data for designated ticker symbol.

        Args:
            symbol: Ticker symbol (e.g., '000001.SZ' for Shenzhen, '600000.SH' for Shanghai)
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            DataFrame with stock price data
        """
        # Convert date format from YYYY-MM-DD to YYYYMMDD for Tushare
        start_date_ts = start_date.replace("-", "")
        end_date_ts = end_date.replace("-", "")

        # Fetch daily data
        df = self.pro.daily(
            ts_code=symbol,
            start_date=start_date_ts,
            end_date=end_date_ts
        )

        if df.empty:
            return pd.DataFrame()

        # Convert trade_date to datetime
        df['trade_date'] = pd.to_datetime(df['trade_date'])
        df = df.sort_values('trade_date')

        # Rename columns - keep lowercase for stockstats compatibility
        column_mapping = {
            'trade_date': 'date',
            'vol': 'volume',
            'amount': 'amount',
            'pre_close': 'previous_close',
            'change': 'change',
            'pct_chg': 'pct_change'
        }

        df = df.rename(columns=column_mapping)

        return df

    def get_company_info(
        self,
        symbol: Annotated[str, "ticker symbol"],
    ) -> dict:
        """
        Fetch company basic information.

        Args:
            symbol: Ticker symbol (e.g., '000001.SZ')

        Returns:
            Dictionary with company information
        """

        # ['ts_code', 'symbol', 'name', 'area', 'industry', 'cnspell', 'market', 'list_date', 'act_name', 'act_ent_type']
        df = self.pro.stock_basic(
            ts_code=symbol,
        )

        if df.empty:
            return {}

        return df.iloc[0].to_dict()

    def get_financial_indicators(
        self,
        symbol: Annotated[str, "ticker symbol"],
        period: Annotated[str, "reporting period (e.g., 20240331)"],
    ) -> pd.DataFrame:
        """
        Fetch financial indicators for a company.

        Args:
            symbol: Ticker symbol
            period: Reporting period in YYYYMMDD format

        Returns:
            DataFrame with financial indicators
        """
        df = self.pro.fina_indicator(
            ts_code=symbol,
            period=period
        )

        return df

    def get_income_statement(
        self,
        symbol: Annotated[str, "ticker symbol"],
        period: Annotated[str, "reporting period"],
    ) -> pd.DataFrame:
        """
        Fetch income statement data.

        Args:
            symbol: Ticker symbol
            period: Reporting period in YYYYMMDD format

        Returns:
            DataFrame with income statement data
        """
        df = self.pro.income(
            ts_code=symbol,
            period=period
        )

        return df

    def get_balance_sheet(
        self,
        symbol: Annotated[str, "ticker symbol"],
        period: Annotated[str, "reporting period"],
    ) -> pd.DataFrame:
        """
        Fetch balance sheet data.

        Args:
            symbol: Ticker symbol
            period: Reporting period in YYYYMMDD format

        Returns:
            DataFrame with balance sheet data
        """
        df = self.pro.balancesheet(
            ts_code=symbol,
            period=period
        )

        return df

    def get_cash_flow(
        self,
        symbol: Annotated[str, "ticker symbol"],
        period: Annotated[str, "reporting period"],
    ) -> pd.DataFrame:
        """
        Fetch cash flow statement data.

        Args:
            symbol: Ticker symbol
            period: Reporting period in YYYYMMDD format

        Returns:
            DataFrame with cash flow data
        """
        df = self.pro.cashflow(
            ts_code=symbol,
            period=period
        )

        return df

    def get_news(self,
                 date: Annotated[str, "Date for news/announcements in YYYY-MM-DD format"],
                 interval: Annotated[int, "Number of days to look back"] = 30,
                 ):
        """
        Get all news from multiple sources without filtering

        News sources:
        1. General news sources (sina, wallstreetcn, etc.)
        2. CCTV news
        3. Announcements (anns_d)
        4. Investor relations Q&A (irm_qa_sh, irm_qa_sz)
        """
        end_date = datetime.strptime(date, "%Y-%m-%d")
        start_date = end_date - timedelta(days=interval)

        # Format dates for news API
        start_date_str = start_date.strftime("%Y-%m-%d %H:%M:%S")
        end_date_str = end_date.strftime("%Y-%m-%d %H:%M:%S")

        all_news = []

        # 1. Get news from multiple sources
        srcs = ['sina', 'wallstreetcn', '10jqka', 'eastmoney', 'yuncaijing',
                'cls', 'yicai', 'fenghuang', 'jinrongjie']

        # try:
        #     news_df = self.pro.news(start_date=start_date_str, end_date=end_date_str)
        #
        #     if not news_df.empty:
        #         for _, row in news_df.iterrows():
        #             all_news.append({
        #                 'datetime': row.get('datetime', ''),
        #                 'title': row.get('title', ''),
        #                 'content': row.get('content', ''),
        #                 # 'source': src,
        #                 'type': 'news',
        #                 'ts_code': row.get('ts_code', ''),
        #                 'symbol': row.get('symbol', '')
        #             })
        # except Exception as e:
        #     print(traceback.format_exc())
        #     print(e.__str__())

        for src in srcs:
            try:
                news_df = self.pro.news(src=src, start_date=start_date_str, end_date=end_date_str)

                if not news_df.empty:
                    for _, row in news_df.iterrows():
                        all_news.append({
                            'datetime': row.get('datetime', ''),
                            'title': row.get('title', ''),
                            'content': row.get('content', ''),
                            'source': src,
                            'type': 'news',
                            # 'ts_code': row.get('ts_code', ''),
                            # 'symbol': row.get('symbol', '')
                        })
            except Exception as e:
                print(traceback.format_exc())
                print(e.__str__())
                # raise e
                # continue

        # 2. Get CCTV news, announcements, and IR Q&A for each day in interval
        for i in range(interval):
            current_date = end_date - timedelta(days=i)
            date_str = current_date.strftime("%Y%m%d")

            # CCTV News
            try:
                cctv_df = self.pro.cctv_news(date=date_str)
                if not cctv_df.empty:
                    for _, row in cctv_df.iterrows():
                        all_news.append({
                            'datetime': date_str,
                            'title': row.get('title', ''),
                            'content': row.get('content', ''),
                            'source': 'cctv',
                            'type': 'cctv_news',
                            # 'ts_code': '',
                            # 'symbol': ''
                        })
            except Exception as e:
                print(traceback.format_exc())
                print(e.__str__())

            # Announcements
            try:
                anns_df = self.pro.anns_d(ann_date=date_str)
                if not anns_df.empty:
                    for _, row in anns_df.iterrows():
                        all_news.append({
                            'datetime': row.get('ann_date', date_str),
                            'title': row.get('title', ''),
                            'content': row.get('content', ''),
                            'source': 'announcement',
                            'type': 'announcement',
                            # 'ts_code': row.get('ts_code', ''),
                            # 'symbol': row.get('symbol', '')
                        })
            except Exception as e:
                print(traceback.format_exc())
                print(e.__str__())

            # Shanghai IR Q&A
            try:
                irm_qa_sh_df = self.pro.irm_qa_sh(ann_date=date_str)
                if not irm_qa_sh_df.empty:
                    for _, row in irm_qa_sh_df.iterrows():
                        all_news.append({
                            'datetime': row.get('ann_date', date_str),
                            'title': row.get('question', ''),
                            'content': row.get('answer', ''),
                            'source': 'ir_qa_sh',
                            'type': 'ir_qa',
                            # 'ts_code': row.get('ts_code', ''),
                            # 'symbol': row.get('symbol', '')
                        })
            except Exception as e:
                print(traceback.format_exc())
                print(e.__str__())

            # Shenzhen IR Q&A
            try:
                irm_qa_sz_df = self.pro.irm_qa_sz(ann_date=date_str)
                if not irm_qa_sz_df.empty:
                    for _, row in irm_qa_sz_df.iterrows():
                        all_news.append({
                            'datetime': row.get('ann_date', date_str),
                            'title': row.get('question', ''),
                            'content': row.get('answer', ''),
                            'source': 'ir_qa_sz',
                            'type': 'ir_qa',
                            # 'ts_code': row.get('ts_code', ''),
                            # 'symbol': row.get('symbol', '')
                        })
            except Exception as e:
                print(traceback.format_exc())
                print(e.__str__())

        # Convert to DataFrame
        if all_news:
            return pd.DataFrame(all_news)
        else:
            return pd.DataFrame(columns=['datetime', 'title', 'content', 'source', 'type', 'ts_code', 'symbol'])


    def get_stock_info(
        self,
        symbol: Annotated[str, "Stock symbol (e.g., 000001.SZ, 600000.SH)"],
        date: Annotated[str, "Date for news/announcements in YYYY-MM-DD format"],
        interval: Annotated[int, "Number of days to look back"] = 30,
        max_limit: Annotated[int, "Maximum number of items to return"] = None,
    ) -> list:
        """
        Fetch various types of stock information from Tushare Pro API.

        Args:
            symbol: Stock symbol (e.g., '000001.SZ')
            date: Date for time-sensitive queries
            interval: Number of days to look back for news
            max_limit: Maximum number of results

        Returns:
            List of dictionaries containing the requested information
        """
        results = []

        # Get company basic information
        company_info = self.get_company_info(symbol)
        if company_info:
            results.append({
                'type': 'company_info',
                'name': company_info.get('name', ''),
                'symbol': company_info.get('symbol', ''),
                'industry': company_info.get('industry', ''),
                'area': company_info.get('area', ''),
                'market': company_info.get('market', ''),
                'list_date': company_info.get('list_date', ''),
                'concepts': company_info.get('concepts', '')
            })

            # Get all news
            news_df = self.get_news(date=date, interval=interval)

            if not news_df.empty:
                company_name = company_info.get('name', '')
                stock_code = symbol.split('.')[0]  # Extract code without exchange suffix

                # Filter news by company name or symbol
                filtered_news = []
                for _, row in news_df.iterrows():
                    # Check if news is related to this stock
                    is_related = False

                    # Check ts_code match
                    if row.get('ts_code') == symbol:
                        is_related = True
                    # Check symbol match
                    elif row.get('symbol') == stock_code:
                        is_related = True
                    # Check if company name appears in title or content
                    elif company_name:
                        title = str(row.get('title', '')).lower()
                        content = str(row.get('content', '')).lower()
                        company_lower = company_name.lower()
                        if company_lower in title or company_lower in content:
                            is_related = True
                    # Check if stock code appears in title or content
                    elif stock_code:
                        title = str(row.get('title', ''))
                        content = str(row.get('content', ''))
                        if stock_code in title or stock_code in content:
                            is_related = True

                    if is_related:
                        filtered_news.append({
                            'type': row['type'],
                            'datetime': row['datetime'],
                            'title': row['title'],
                            'content': row['content'][:500] if len(row['content']) > 500 else row['content'],  # Truncate long content
                            'source': row['source']
                        })

                # Sort by datetime and limit results
                filtered_news = sorted(filtered_news, key=lambda x: x['datetime'], reverse=True)[:max_limit]
                results.extend(filtered_news)

        return results

    def format_stock_info(self, info_list: list) -> str:
        """
        Format the stock info list into a readable string.

        Args:
            info_list: List of info dictionaries

        Returns:
            Formatted string for display
        """
        if not info_list:
            return "No information available."

        formatted = []

        for info in info_list:
            if info['type'] == 'company_info':
                formatted.append(
                    f"Company: {info['name']} ({info['symbol']})\n"
                    f"Industry: {info['industry']}, Area: {info['area']}\n"
                    f"Listed: {info['list_date']}, Market: {info['market']}\n"
                    f"Concepts: {info['concepts']}"
                )
            elif info['type'] in ['news', 'major_news']:
                formatted.append(
                    f"News: {info['title']}\n"
                    f"Date: {info['datetime']}, Source: {info['source']}\n"
                    f"Content: {info['content']}"
                )
            elif info['type'] == 'concept':
                formatted.append(f"Concept: {info['concept_name']} (Since: {info['in_date']})")
            elif info['type'] == 'financial':
                formatted.append(
                    f"Financial Data (Period: {info['period']}):\n"
                    f"ROE: {info['roe']}%, ROA: {info['roa']}%, EPS: {info['eps']}\n"
                    f"P/E: {info['pe']}, P/B: {info['pb']}\n"
                    f"Margins - Gross: {info['gross_margin']}%, Net: {info['net_margin']}%"
                )
            elif info['type'] == 'announcement':
                formatted.append(
                    f"Announcement ({info['ann_date']}): {info['title']}\n"
                    f"Type: {info['ann_type']}\n{info['content']}"
                )
            elif info['type'] == 'error':
                formatted.append(info['message'])

        return "\n\n".join(formatted)


# Singleton instance for reuse
_tushare_utils = None

def get_tushare_utils(token: Optional[str] = None) -> TushareUtils:
    """Get or create TushareUtils instance"""
    global _tushare_utils
    if _tushare_utils is None:
        _tushare_utils = TushareUtils(token)
    return _tushare_utils