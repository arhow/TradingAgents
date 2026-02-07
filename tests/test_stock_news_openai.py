#!/usr/bin/env python3
"""Test get_stock_news_openai function"""

import os
import sys
import signal
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tradingagents.dataflows.interface import get_stock_news_openai

# Timeout handler for long-running API calls
def timeout_handler(signum, frame):
    print("\n⚠️ Test timed out after 30 seconds")
    print("The API call is taking too long - this is likely due to the OpenAI Responses API")
    exit(1)

def test_get_stock_news_openai():
    """Test the get_stock_news_openai function"""

    symbol = "300418.SZ"
    ticker = "昆仑万维"
    curr_date = "2025-09-21"

    print("=" * 70)
    print(f"Testing get_stock_news_openai for {symbol} ({ticker}) on {curr_date}")
    print("=" * 70)
    print("\nExpected debug output from function:")
    print("  - Web search performed - Status: ...")
    print("  - Reasoning step - Status: ...")
    print("  - (Possibly) Text: ...")
    print("-" * 70)

    try:
        # Call the function with correct parameters: symbol, ticker, curr_date
        result = get_stock_news_openai(symbol, ticker, curr_date)

        print("-" * 70)
        print("\n✓ SUCCESS! Function executed without AttributeError")

        # Analyze the result
        print(f"\nResult Analysis:")
        print(f"  Type: {type(result)}")

        if result is None:
            print("  ⚠️ Result is None")
            print("  This means an exception occurred inside the function's try block")
            print("  Check the debug output above for error details")

        elif result == "No results returned from social media search.":
            print("  ⚠️ Received fallback message")
            print("  This means response.output_text was empty")
            print("  This often happens when:")
            print("    1. The response status is 'incomplete'")
            print("    2. Token limit was reached")
            print("    3. API timeout occurred")

        else:
            print(f"  ✓ Got actual content!")
            print(f"  Length: {len(result)} characters")

            # Show preview of result
            print(f"\nFirst 300 chars of result:")
            print("-" * 50)
            preview = result[:300] if len(result) > 300 else result
            print(preview)
            if len(result) > 300:
                print("... [truncated]")

    except AttributeError as e:
        print("-" * 70)
        print(f"\n✗ FAILED - AttributeError: {e}")
        print("\nThis means the fix didn't work properly.")
        print("The error was likely:")
        print("  'ResponseFunctionWebSearch' object has no attribute 'content'")

    except Exception as e:
        print("-" * 70)
        print(f"\n⚠️ Other error - {type(e).__name__}: {e}")

        if "timeout" in str(e).lower():
            print("\nThe API call timed out. This is common with the Responses API.")
        elif "api" in str(e).lower() or "token" in str(e).lower():
            print("\nPossible API configuration issue:")
            print("  - Check if OPENAI_API_KEY is set")
            print("  - Verify backend_url in config")
            print("  - Ensure you have access to the Responses API")

    print("\n" + "=" * 70)

if __name__ == "__main__":
    # Set a 30 second timeout
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(30)

    try:
        test_get_stock_news_openai()
    finally:
        signal.alarm(0)  # Cancel the alarm