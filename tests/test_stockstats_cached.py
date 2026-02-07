#!/usr/bin/env python3
"""
Test script using cached data to verify stockstats compatibility
"""

import pandas as pd
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stockstats import wrap

def test_cached_data():
    """Test cached data format with stockstats"""

    cache_file = "/mnt/d/pyworkspace/TradingAgents/tradingagents/dataflows/data_cache/300418.SZ-data-2010-09-17-2025-09-17.csv"

    print("\n=== Testing Cached Data ===")
    print(f"Loading: {cache_file}")

    data = pd.read_csv(cache_file)

    print("\n1. Data Structure:")
    print(f"   Columns: {list(data.columns)}")
    print(f"   Shape: {data.shape}")
    print(f"   First 3 rows:")
    print(data.head(3))

    print("\n2. Data types:")
    print(data.dtypes)

    print("\n3. Testing stockstats wrap:")

    # Convert Date to datetime if needed
    if 'Date' in data.columns:
        data['Date'] = pd.to_datetime(data['Date'])
        print("   ✓ Converted Date to datetime")

    # Try wrapping with stockstats
    try:
        df = wrap(data)
        print("   ✓ Wrap successful!")
        print(f"   Available columns: {list(df.columns)[:10]}...")  # Show first 10

        # Test RSI calculation
        print("\n4. Testing RSI indicator:")
        rsi = df['rsi']
        print(f"   ✓ RSI calculated successfully")
        # Show last few non-NaN values
        rsi_values = rsi.dropna().tail(5)
        print(f"   Sample RSI values: {rsi_values.values}")

        # Test other indicators
        print("\n5. Testing other indicators:")
        test_indicators = ['close_10_sma', 'macd', 'boll', 'atr', 'vwma']

        for indicator in test_indicators:
            try:
                values = df[indicator]
                non_nan = values.dropna()
                if len(non_nan) > 0:
                    print(f"   ✓ {indicator}: {non_nan.iloc[-1]:.2f}")
                else:
                    print(f"   ⚠ {indicator}: All NaN values")
            except Exception as e:
                print(f"   ✗ {indicator}: {e}")

        # Test date matching
        print("\n6. Testing date matching:")
        test_dates = ["2024-11-15", "2024-11-14", "2024-11-13"]

        for test_date in test_dates:
            test_dt = pd.to_datetime(test_date)

            # Try matching
            matches = df[df['Date'].dt.date == test_dt.date()]

            if not matches.empty:
                print(f"   ✓ Found data for {test_date}")
                print(f"      Close: {matches['close'].values[0]:.2f}, RSI: {matches['rsi'].values[0]:.2f}")
            else:
                print(f"   ✗ No data for {test_date}")

    except Exception as e:
        print(f"   ✗ Wrap failed: {e}")
        print("\n   Debugging column names:")

        # Check column name case
        print(f"   Original columns: {list(data.columns)}")

        # Try lowercase conversion
        data_lower = data.copy()
        data_lower.columns = [col.lower() if col != 'Date' else col for col in data_lower.columns]
        print(f"   After case adjustment: {list(data_lower.columns)}")

        try:
            df2 = wrap(data_lower)
            print("   ✓ Wrap successful after column name adjustment!")
        except Exception as e2:
            print(f"   ✗ Still failed: {e2}")

def test_date_format():
    """Test different date formats"""
    print("\n=== Testing Date Formats ===")

    cache_file = "/mnt/d/pyworkspace/TradingAgents/tradingagents/dataflows/data_cache/300418.SZ-data-2010-09-17-2025-09-17.csv"
    data = pd.read_csv(cache_file)

    # Show raw date values
    print("\n1. Raw Date values (first 5):")
    print(data['Date'].head())

    # Convert to datetime
    data['Date'] = pd.to_datetime(data['Date'])

    print("\n2. After pd.to_datetime (first 5):")
    print(data['Date'].head())

    print("\n3. Date data type:")
    print(f"   Type: {data['Date'].dtype}")

    # Test different date matching approaches
    test_date = "2024-11-15"
    print(f"\n4. Testing match for {test_date}:")

    test_dt = pd.to_datetime(test_date)

    # Method 1: Using dt.date
    matches1 = data[data['Date'].dt.date == test_dt.date()]
    print(f"   Method 1 (dt.date): {len(matches1)} matches")

    # Method 2: String comparison after formatting
    data['Date_str'] = data['Date'].dt.strftime('%Y-%m-%d')
    matches2 = data[data['Date_str'] == test_date]
    print(f"   Method 2 (string): {len(matches2)} matches")

    # Method 3: Direct datetime comparison (same day)
    matches3 = data[(data['Date'] >= test_dt) & (data['Date'] < test_dt + pd.Timedelta(days=1))]
    print(f"   Method 3 (datetime range): {len(matches3)} matches")

    # Show what dates ARE available around that time
    print("\n5. Available dates around 2024-11-15:")
    november_data = data[(data['Date'] >= '2024-11-01') & (data['Date'] <= '2024-11-30')]
    print(f"   Found {len(november_data)} trading days in November 2024")
    if len(november_data) > 0:
        print("   Dates:")
        for date in november_data['Date'].head(10):
            print(f"      {date.strftime('%Y-%m-%d')} ({date.strftime('%A')})")

if __name__ == "__main__":
    try:
        test_cached_data()
        test_date_format()
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()