#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test file for get_news and get_stock_info methods in tushare_utils.py
"""

import sys
import os
from dotenv import load_dotenv
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

# Load environment variables
load_dotenv()

from tradingagents.dataflows.tushare_utils import TushareUtils


def print_section_header(title):
    """Helper function to print formatted section headers"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def test_get_news():
    """Test the get_news method that collects all news without filtering"""

    print_section_header("TESTING GET_NEWS METHOD (ALL NEWS COLLECTION)")

    # Initialize TushareUtils
    tushare_utils = TushareUtils()

    # Test parameters
    test_date = "2025-09-19"
    interval = 2  # Look back only 2 days to avoid timeout

    print(f"\nFetching all news for date: {test_date}")
    print(f"Look back interval: {interval} days")
    print("-" * 40)

    try:
        # Get all news
        news_df = tushare_utils.get_news(
            date=test_date,
            interval=interval
        )

        if not news_df.empty:
            print(f"\nTotal news items found: {len(news_df)}")

            # Group by type and source
            print("\n### News Distribution by Type ###")
            type_counts = news_df['type'].value_counts()
            for news_type, count in type_counts.items():
                print(f"  {news_type}: {count}")

            print("\n### News Distribution by Source ###")
            source_counts = news_df['source'].value_counts()
            for source, count in source_counts.items():
                print(f"  {source}: {count}")

            # Show sample news items
            print("\n### Sample News Items (First 3) ###")
            for idx, row in news_df.head(3).iterrows():
                print(f"\nItem {idx + 1}:")
                print(f"  Type: {row['type']}")
                print(f"  Source: {row['source']}")
                print(f"  Date: {row['datetime']}")
                print(f"  Title: {row['title'][:100]}..." if len(row['title']) > 100 else f"  Title: {row['title']}")
                if row.get('ts_code'):
                    print(f"  Stock Code: {row['ts_code']}")
        else:
            print("No news found for the specified period.")

    except Exception as e:
        print(f"Error fetching news: {e}")


def test_get_stock_info():
    """Test the get_stock_info method that filters news for specific stock"""

    print_section_header("TESTING GET_STOCK_INFO METHOD (FILTERED NEWS)")

    # Initialize TushareUtils
    tushare_utils = TushareUtils()

    # Test parameters
    test_stocks = [
        "300418.SZ",  # Kunlun Tech (创业板)
        # "000001.SZ",  # Ping An Bank (深圳主板)
        # "600000.SH",  # Pudong Development Bank (上海主板)
    ]
    test_date = "2025-09-19"
    interval = 2  # Reduced to avoid timeout
    max_limit = 1000

    for symbol in test_stocks:
        print(f"\n### Testing Stock: {symbol} ###")
        print("-" * 40)

        try:
            # Get stock information
            stock_info = tushare_utils.get_stock_info(
                symbol=symbol,
                date=test_date,
                interval=interval,
                max_limit=max_limit
            )

            if stock_info:
                print(f"Total items found: {len(stock_info)}")

                for idx, info in enumerate(stock_info):
                    if info['type'] == 'company_info':
                        print(f"\nCompany Information:")
                        print(f"  Name: {info['name']}")
                        print(f"  Symbol: {info['symbol']}")
                        print(f"  Industry: {info['industry']}")
                        print(f"  Area: {info['area']}")
                        print(f"  Market: {info['market']}")
                        print(f"  Listed Date: {info['list_date']}")
                    else:
                        print(f"\n{info['type'].upper()} - Item {idx}:")
                        print(f"  Date: {info['datetime']}")
                        print(f"  Source: {info['source']}")
                        print(f"  Title: {info['title'][:80]}..." if len(info['title']) > 80 else f"  Title: {info['title']}")
            else:
                print("No information found for this stock.")

        except Exception as e:
            print(f"Error fetching stock info for {symbol}: {e}")


def test_news_filtering():
    """Test the filtering logic in get_stock_info"""

    print_section_header("TESTING NEWS FILTERING LOGIC")

    # Initialize TushareUtils
    tushare_utils = TushareUtils()

    # Test specific stock
    symbol = "000001.SZ"  # Ping An Bank
    test_date = "2025-09-19"
    interval = 30  # Longer interval to get more data

    print(f"\nFetching data for {symbol} with {interval} day interval")
    print("-" * 40)

    try:
        # Get all news first
        all_news_df = tushare_utils.get_news(date=test_date, interval=interval)
        print(f"Total news items (unfiltered): {len(all_news_df)}")

        # Get filtered stock info
        stock_info = tushare_utils.get_stock_info(
            symbol=symbol,
            date=test_date,
            interval=interval,
            max_limit=20
        )

        # Count only news items (exclude company_info)
        news_items = [item for item in stock_info if item['type'] != 'company_info']
        print(f"Filtered news items for {symbol}: {len(news_items)}")

        # Show filtering statistics
        if news_items:
            news_types = {}
            for item in news_items:
                news_type = item['type']
                if news_type not in news_types:
                    news_types[news_type] = 0
                news_types[news_type] += 1

            print("\n### Filtered News by Type ###")
            for news_type, count in news_types.items():
                print(f"  {news_type}: {count}")

    except Exception as e:
        print(f"Error in filtering test: {e}")


def test_different_intervals():
    """Test with different interval values"""

    print_section_header("TESTING DIFFERENT INTERVAL VALUES")

    # Initialize TushareUtils
    tushare_utils = TushareUtils()

    test_date = "2025-09-19"
    intervals = [30]

    print(f"\nTesting news collection with different intervals")
    print("-" * 40)

    for interval in intervals:
        try:
            news_df = tushare_utils.get_news(
                date=test_date,
                interval=interval
            )

            print(f"\nInterval: {interval} days")
            print(f"  Total news items: {len(news_df)}")

            if not news_df.empty:
                # Show date range
                min_date = news_df['datetime'].min()
                max_date = news_df['datetime'].max()
                print(f"  Date range: {min_date} to {max_date}")

        except Exception as e:
            print(f"Error with interval {interval}: {e}")


def main():
    """Main test runner"""

    print("\n" + "#" * 80)
    print("#" + " " * 78 + "#")
    print("#" + " " * 15 + "TUSHARE GET_NEWS AND GET_STOCK_INFO TEST SUITE" + " " * 16 + "#")
    print("#" + " " * 78 + "#")
    print("#" * 80)

    # Note about API limits
    print("\n" + "!" * 80)
    print("! NOTE: Tushare API has rate limits. Some tests may fail due to rate limiting. !")
    print("! If you encounter errors, please wait a few minutes and try again.            !")
    print("!" * 80)

    # Run tests
    test_get_news()
    test_get_stock_info()
    # test_news_filtering()
    # test_different_intervals()

    print("\n" + "#" * 80)
    print("#" + " " * 30 + "TESTS COMPLETED" + " " * 33 + "#")
    print("#" * 80)
    print()


if __name__ == "__main__":
    main()