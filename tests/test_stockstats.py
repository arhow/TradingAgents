#!/usr/bin/env python3
"""
Test script for stockstats_utils.py to verify data format compatibility
"""

import pandas as pd
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tradingagents.dataflows.stockstats_utils import StockstatsUtils
from tradingagents.dataflows.tushare_utils import get_tushare_utils
from stockstats import wrap
import numpy as np

def test_tushare_data_format():
    """Test if Tushare data format works with stockstats"""
    print("\n=== Testing Tushare Data Format ===")

    # Get data from Tushare
    tushare = get_tushare_utils()
    symbol = "300418.SZ"
    start_date = "2024-01-01"
    end_date = "2024-12-31"

    print(f"Fetching data for {symbol} from {start_date} to {end_date}")
    data = tushare.get_stock_data(symbol, start_date, end_date)

    print("\n1. Raw Tushare Data:")
    print(f"   Columns: {list(data.columns)}")
    print(f"   Data types:\n{data.dtypes}")
    print(f"   First 3 rows:\n{data.head(3)}")

    # Test wrapping with stockstats
    print("\n2. Testing stockstats wrap:")
    try:
        # Important: stockstats expects lowercase column names internally
        # But we need to check what columns are actually present
        df = wrap(data)
        print("   ✓ Wrap successful")
        print(f"   Available columns after wrap: {list(df.columns)}")

        # Test calculating an indicator
        print("\n3. Testing indicator calculation:")
        try:
            # Calculate RSI
            rsi = df['rsi']
            print(f"   ✓ RSI calculation successful")
            print(f"   RSI sample values: {rsi.tail(3).values}")
        except Exception as e:
            print(f"   ✗ RSI calculation failed: {e}")

        # Test other indicators
        indicators_to_test = ['close_10_sma', 'macd', 'boll']
        for indicator in indicators_to_test:
            try:
                values = df[indicator]
                print(f"   ✓ {indicator} calculation successful")
            except Exception as e:
                print(f"   ✗ {indicator} calculation failed: {e}")

    except Exception as e:
        print(f"   ✗ Wrap failed: {e}")
        print("\n   Trying to fix column names...")

        # Check if we need to adjust column names
        print(f"   Current columns: {list(data.columns)}")

        # Stockstats needs these specific columns (case matters!)
        required_cols = ['open', 'high', 'low', 'close', 'volume']
        current_cols_lower = [col.lower() for col in data.columns]

        missing_cols = [col for col in required_cols if col not in current_cols_lower]
        if missing_cols:
            print(f"   Missing required columns: {missing_cols}")

def test_stockstats_get_stock_stats():
    """Test the get_stock_stats method"""
    print("\n=== Testing StockstatsUtils.get_stock_stats ===")

    symbol = "300418.SZ"
    indicator = "rsi"
    curr_date = "2024-11-15"  # Use a recent trading day

    print(f"Testing get_stock_stats for {symbol} on {curr_date}")
    print(f"Indicator: {indicator}")

    try:
        # Test online mode
        result = StockstatsUtils.get_stock_stats(
            symbol=symbol,
            indicator=indicator,
            curr_date=curr_date,
            data_dir="",
            online=True
        )
        print(f"\nResult: {result}")

        if "N/A" in str(result):
            print("\n⚠️  Got N/A result. Checking available dates...")
            # Load data to check what dates are actually available
            tushare = get_tushare_utils()
            data = tushare.get_stock_data(symbol, "2024-11-01", "2024-11-30")
            print(f"Available dates in November 2024:")
            print(data['Date'].values[:10])

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()

def test_date_matching():
    """Test date matching logic"""
    print("\n=== Testing Date Matching Logic ===")

    # Create sample data like Tushare would return
    dates = pd.date_range('2024-11-01', '2024-11-20', freq='B')  # Business days only
    sample_data = pd.DataFrame({
        'Date': dates,
        'Open': np.random.uniform(10, 20, len(dates)),
        'High': np.random.uniform(20, 30, len(dates)),
        'Low': np.random.uniform(5, 10, len(dates)),
        'Close': np.random.uniform(15, 25, len(dates)),
        'Volume': np.random.randint(1000, 10000, len(dates))
    })

    print("Sample data dates:")
    print(sample_data['Date'].head())

    # Test date matching
    test_date = "2024-11-15"
    test_date_dt = pd.to_datetime(test_date)

    print(f"\nTesting match for {test_date}")

    # Method 1: Using dt.date
    matches1 = sample_data[sample_data['Date'].dt.date == test_date_dt.date()]
    print(f"Method 1 (dt.date): Found {len(matches1)} matches")

    # Method 2: Using string comparison with formatted dates
    sample_data['Date_str'] = sample_data['Date'].dt.strftime('%Y-%m-%d')
    matches2 = sample_data[sample_data['Date_str'] == test_date]
    print(f"Method 2 (string): Found {len(matches2)} matches")

    if len(matches1) > 0:
        print(f"✓ Date matching works!")
    else:
        print(f"✗ Date matching failed")

if __name__ == "__main__":
    print("=" * 50)
    print("StockStats Utils Test Suite")
    print("=" * 50)

    try:
        # Test 1: Check Tushare data format
        test_tushare_data_format()

        # Test 2: Test the actual get_stock_stats function
        test_stockstats_get_stock_stats()

        # Test 3: Test date matching logic
        test_date_matching()

    except Exception as e:
        print(f"\n✗ Test suite failed: {e}")
        import traceback
        traceback.print_exc()