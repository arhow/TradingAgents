#!/usr/bin/env python3
"""Final test of the get_stock_news_openai function"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tradingagents.dataflows.interface import get_stock_news_openai

def test_final_function():
    """Test the actual function as it exists"""

    print("=" * 80)
    print("FINAL TEST OF get_stock_news_openai")
    print("=" * 80)

    ticker = "AAPL"
    curr_date = "2025-09-19"

    print(f"\nParameters:")
    print(f"  Ticker: {ticker}")
    print(f"  Date: {curr_date}")
    print()

    print("Calling get_stock_news_openai...")
    print("(Watch for any debug output from the function)")
    print("-" * 40)

    try:
        result = get_stock_news_openai(ticker, curr_date)

        print("-" * 40)
        print("\n✓ Function completed successfully!")

        print(f"\nResult:")
        print(f"  Type: {type(result)}")

        if result is None:
            print("  ✗ Result is None (exception occurred)")
        elif result == "No results returned from social media search.":
            print("  ⚠️ Fallback message returned (output_text was empty)")
        else:
            print(f"  ✓ Got actual content!")
            print(f"  Length: {len(result)} characters")
            print(f"\nFirst 300 characters:")
            print("-" * 40)
            print(result[:300])
            if len(result) > 300:
                print("... [truncated]")

    except AttributeError as e:
        print(f"\n✗ AttributeError: {e}")
        print("The fix didn't work - still getting the original error")

    except Exception as e:
        print(f"\n✗ Other error: {type(e).__name__}: {e}")

    print("\n" + "=" * 80)

if __name__ == "__main__":
    test_final_function()