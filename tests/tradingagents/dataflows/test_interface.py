#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test suite for interface.py functions including Tushare and other data sources
"""

import sys
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

# Load environment variables
load_dotenv()

from tradingagents.dataflows.interface import (
    get_tushare_stock_info,
    get_tushare_data_online,
    get_reddit_company_news,
    get_reddit_global_news,
    get_finnhub_news,
    get_google_news,
    get_YFin_data_online,
    get_stockstats_indicator,
    get_stock_stats_indicators_window
)


def print_section_header(title):
    """Helper function to print formatted section headers"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def test_tushare_stock_info():
    """Test get_tushare_stock_info with various information types"""

    # Test parameters
    symbol = "300418.SZ"  # Kunlun Tech
    test_date = "2025-09-19"

    print_section_header("TESTING TUSHARE STOCK INFO FUNCTIONS")

    # Test 1: Company Information
    print("\n### 1. Company Information ###")
    print("-" * 40)
    try:
        company_info = get_tushare_stock_info(
            symbol=symbol,
            info_type="company",
            date=test_date,
            max_limit=10
        )
        print(company_info)
    except Exception as e:
        print(f"Error: {e}")

    # Test 2: Financial Data
    print("\n### 2. Financial Data ###")
    print("-" * 40)
    try:
        financial_info = get_tushare_stock_info(
            symbol=symbol,
            info_type="financial",
            date="2024-09-30",  # Use quarter end date
            max_limit=1
        )
        print(financial_info)
    except Exception as e:
        print(f"Error: {e}")

    # Test 3: Concepts/Themes
    print("\n### 3. Stock Concepts/Themes ###")
    print("-" * 40)
    try:
        concepts_info = get_tushare_stock_info(
            symbol=symbol,
            info_type="concept",
            date=test_date,
            max_limit=5
        )
        print(concepts_info)
    except Exception as e:
        print(f"Error: {e}")

    # Test 4: News (may require special permissions)
    print("\n### 4. Stock News ###")
    print("-" * 40)
    try:
        news_info = get_tushare_stock_info(
            symbol=symbol,
            info_type="news",
            date=test_date,
            max_limit=3
        )
        print(news_info)
    except Exception as e:
        print(f"Error: {e}")


def test_tushare_price_data():
    """Test Tushare price data retrieval"""

    print_section_header("TESTING TUSHARE PRICE DATA")

    symbol = "300418.SZ"
    start_date = "2024-11-01"
    end_date = "2024-11-15"

    print(f"\n### Price Data for {symbol} ###")
    print("-" * 40)
    try:
        price_data = get_tushare_data_online(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date
        )
        # Show first 500 chars
        print(price_data[:500] + "...")
    except Exception as e:
        print(f"Error: {e}")


def test_reddit_functions():
    """Test Reddit news functions for comparison"""

    print_section_header("TESTING REDDIT NEWS FUNCTIONS")

    # Test parameters - use current date to match available data
    ticker = "GOOGL"  # Changed to GOOGL since we have data for it
    test_date = "2025-09-18"  # Current date to match the data we have
    look_back_days = 2  # Only look back 2 days since we have recent data

    # Test 1: Company News from Reddit
    print("\n### 1. Reddit Company News ###")
    print("-" * 40)
    try:
        reddit_company = get_reddit_company_news(
            ticker=ticker,
            start_date=test_date,
            look_back_days=look_back_days,
            max_limit_per_day=5
        )
        if reddit_company:
            print(reddit_company[:1000])  # Show first 1000 chars
        else:
            print("No Reddit company news found")
    except Exception as e:
        print(f"Error: {e}")
        print("Note: Reddit data files may not be available")

    # Test 2: Global News from Reddit
    print("\n### 2. Reddit Global News ###")
    print("-" * 40)
    try:
        reddit_global = get_reddit_global_news(
            start_date=test_date,
            look_back_days=look_back_days,
            max_limit_per_day=5
        )
        if reddit_global:
            print(reddit_global[:1000])  # Show first 1000 chars
        else:
            print("No Reddit global news found")
    except Exception as e:
        print(f"Error: {e}")
        print("Note: Reddit data files may not be available")


def test_other_news_sources():
    """Test other news sources for comparison"""

    print_section_header("TESTING OTHER NEWS SOURCES")

    ticker = "AAPL"
    test_date = "2024-11-15"

    # Test 1: Finnhub News
    print("\n### 1. Finnhub News ###")
    print("-" * 40)
    try:
        finnhub_news = get_finnhub_news(
            ticker=ticker,
            curr_date=test_date,
            look_back_days=7
        )
        if finnhub_news:
            print(finnhub_news[:1000])
        else:
            print("No Finnhub news found")
    except Exception as e:
        print(f"Error: {e}")

    # Test 2: Google News
    print("\n### 2. Google News ###")
    print("-" * 40)
    try:
        google_news = get_google_news(
            query=f"{ticker} stock",
            curr_date=test_date,
            look_back_days=7
        )
        if google_news:
            print(google_news[:1000])
        else:
            print("No Google news found")
    except Exception as e:
        print(f"Error: {e}")


def test_technical_indicators():
    """Test technical indicators functions"""

    print_section_header("TESTING TECHNICAL INDICATORS")

    symbol = "300418.SZ"
    test_date = "2024-11-15"

    # Test single indicator
    print("\n### Single Indicator (RSI) ###")
    print("-" * 40)
    try:
        rsi_value = get_stockstats_indicator(
            symbol=symbol,
            indicator="rsi",
            curr_date=test_date,
            online=True
        )
        print(f"RSI for {symbol} on {test_date}: {rsi_value}")
    except Exception as e:
        print(f"Error: {e}")

    # Test indicator window
    print("\n### Indicator Window (MACD) ###")
    print("-" * 40)
    try:
        macd_window = get_stock_stats_indicators_window(
            symbol=symbol,
            indicator="macd",
            curr_date=test_date,
            look_back_days=5,
            online=True
        )
        print(macd_window[:500])  # Show first 500 chars
    except Exception as e:
        print(f"Error: {e}")


def test_yfin_data():
    """Test Yahoo Finance data retrieval"""

    print_section_header("TESTING YAHOO FINANCE DATA")

    # Test with US stock
    symbol = "AAPL"
    start_date = "2024-11-01"
    end_date = "2024-11-15"

    print(f"\n### YFin Data for {symbol} ###")
    print("-" * 40)
    try:
        yfin_data = get_YFin_data_online(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date
        )
        # Show first 500 chars
        print(yfin_data[:500] + "...")
    except Exception as e:
        print(f"Error: {e}")


def compare_output_formats():
    """Compare different output formats"""

    print_section_header("OUTPUT FORMAT COMPARISON")

    print("\n### Tushare Output Structure ###")
    print("-" * 40)
    print("Header format:")
    print("  # Tushare Stock Information")
    print("  # Symbol: [SYMBOL]")
    print("  # Info Type: [TYPE]")
    print("  # Date: [DATE]")
    print("  # Retrieved: [TIMESTAMP]")
    print("  " + "=" * 60)
    print("")
    print("Content format (varies by info_type):")
    print("  - Company: Name, Industry, Area, Listed, Market, Concepts")
    print("  - Financial: ROE, ROA, EPS, P/E, P/B, Margins")
    print("  - News: Title, Date, Source, Content")
    print("  - Concepts: Concept Name, In Date")

    print("\n### Reddit Output Structure ###")
    print("-" * 40)
    print("Header format:")
    print("  ## [TICKER] News Reddit, from [START] to [END]:")
    print("")
    print("Content format:")
    print("  ### [Post Title]")
    print("  [Post Content]")
    print("  (with metadata like upvotes, date)")

    print("\n### Finnhub Output Structure ###")
    print("-" * 40)
    print("Header format:")
    print("  ## [TICKER] News, from [START] to [END]:")
    print("")
    print("Content format:")
    print("  ### [Headline] (date)")
    print("  [Summary]")

    print("\n### YFin Output Structure ###")
    print("-" * 40)
    print("Header format:")
    print("  # Stock data for [SYMBOL] from [START] to [END]")
    print("  # Total records: [COUNT]")
    print("  # Data retrieved on: [TIMESTAMP]")
    print("")
    print("Content format:")
    print("  CSV format with columns:")
    print("  Date, Open, High, Low, Close, Adj Close, Volume")


def test_chinese_vs_us_stocks():
    """Compare Chinese and US stock data availability"""

    print_section_header("CHINESE vs US STOCKS DATA AVAILABILITY")

    test_date = "2024-11-15"

    # Chinese stock test
    print("\n### Chinese Stock (300418.SZ - Kunlun Tech) ###")
    print("-" * 40)

    try:
        # Tushare company info
        tushare_info = get_tushare_stock_info(
            symbol="300418.SZ",
            info_type="company",
            date=test_date,
            max_limit=1
        )
        # Extract just the content part
        lines = tushare_info.split('\n')
        for i, line in enumerate(lines):
            if "====" in line and i < len(lines) - 1:
                print("Tushare Data Available:")
                for content_line in lines[i+1:]:
                    if content_line.strip():
                        print(f"  {content_line.strip()}")
                break
    except Exception as e:
        print(f"Tushare Error: {e}")

    # Try Reddit for Chinese stock (usually won't find much)
    try:
        reddit_cn = get_reddit_company_news(
            ticker="300418.SZ",
            start_date=test_date,
            look_back_days=7,
            max_limit_per_day=2
        )
        if reddit_cn:
            print(f"Reddit Data: Found {len(reddit_cn.split('###')) - 1} posts")
        else:
            print("Reddit Data: No data found (expected for Chinese stocks)")
    except:
        print("Reddit Data: Not available for Chinese stocks")

    # US stock test
    print("\n### US Stock (AAPL - Apple Inc.) ###")
    print("-" * 40)

    # Try Tushare for US stock (usually won't work)
    try:
        tushare_us = get_tushare_stock_info(
            symbol="AAPL",
            info_type="company",
            date=test_date,
            max_limit=1
        )
        if "No company data available" in tushare_us:
            print("Tushare Data: Not available for US stocks (expected)")
        else:
            print("Tushare Data: Available")
    except:
        print("Tushare Data: Not available for US stocks (expected)")

    # Try YFin for US stock
    try:
        yfin_data = get_YFin_data_online(
            symbol="AAPL",
            start_date="2024-11-01",
            end_date="2024-11-15"
        )
        if yfin_data:
            print("YFin Data: Available for US stocks")
    except Exception as e:
        print(f"YFin Data Error: {e}")


def test_data_coverage_summary():
    """Summarize data coverage for different sources"""

    print_section_header("DATA COVERAGE SUMMARY")

    print("\n### Data Source Coverage Matrix ###")
    print("-" * 40)
    print("")
    print("| Data Source     | Chinese Stocks | US Stocks |")
    print("|-----------------|----------------|-----------|")
    print("| Tushare         |  Full Support |  No      |")
    print("| Yahoo Finance   |  Limited      |  Full    |")
    print("| Reddit          |  Limited      |  Yes     |")
    print("| Finnhub         |  No           |  Yes     |")
    print("| Google News     | ~ Some         |  Yes     |")
    print("| StockStats      |  Yes (w/data) |  Yes     |")
    print("")
    print("Legend:")
    print("   = Full support")
    print("  ~ = Partial support")
    print("   = No support or very limited")


def main():
    """Main test runner"""

    print("\n" + "#" * 80)
    print("#" + " " * 78 + "#")
    print("#" + " " * 20 + "INTERFACE.PY TEST SUITE" + " " * 35 + "#")
    print("#" + " " * 78 + "#")
    print("#" * 80)

    # Run all tests
    # test_reddit_functions()
    test_tushare_stock_info()
    test_tushare_price_data()
    test_other_news_sources()
    test_technical_indicators()
    test_yfin_data()
    compare_output_formats()
    test_chinese_vs_us_stocks()
    test_data_coverage_summary()

    print("\n" + "#" * 80)
    print("#" + " " * 30 + "TESTS COMPLETED" + " " * 33 + "#")
    print("#" * 80)
    print()


if __name__ == "__main__":
    main()