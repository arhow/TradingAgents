#!/usr/bin/env python3
"""Test get_stock_news_openai function with individual site searches"""

import traceback
import dotenv
import json
import sys
import os
from datetime import datetime, timedelta

# Load environment variables
dotenv.load_dotenv()

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tradingagents.dataflows.interface import get_stock_news_openai

def test_get_stock_news_openai():
    """Test the get_stock_news_openai function"""

    # Test parameters
    ticker = '昆仑万维'
    symbol = '300418.SZ'
    curr_date = '2025-09-20'

    print("=" * 80)
    print("Testing get_stock_news_openai with Individual Site Searches")
    print("=" * 80)
    print(f"\nParameters:")
    print(f"  Ticker (Company Name): {ticker}")
    print(f"  Symbol (Stock Code): {symbol}")
    print(f"  Current Date: {curr_date}")

    # Calculate expected date range
    end_date_dt = datetime.strptime(curr_date, '%Y-%m-%d')
    start_date_dt = end_date_dt - timedelta(days=7)
    print(f"  Expected Date Range: {start_date_dt.strftime('%Y-%m-%d')} to {end_date_dt.strftime('%Y-%m-%d')}")
    print()

    print("Starting search (searching each site individually)...")
    print("This will search the following Chinese platforms:")
    print("  - 东方财富股吧, 百度贴吧, 知乎, 微博, 雪球 (social media)")
    print("  - 新浪财经, 华尔街见闻, 同花顺, 东方财富新闻, 财联社 (news)")
    print("-" * 60)

    try:
        # Call the function
        result = get_stock_news_openai(symbol, ticker, curr_date)

        print("-" * 60)

        if result is None:
            print("\n✗ ERROR: Function returned None")
            print("This indicates an exception occurred during execution")
            return

        print("\n✓ Function completed successfully!")

        # Try to parse the result as JSON
        try:
            result_json = json.loads(result)

            # Display summary
            summary = result_json.get("summary", {})
            print("\n" + "=" * 60)
            print("SEARCH SUMMARY:")
            print("=" * 60)
            print(f"  Total items found: {summary.get('total_items_found', 0)}")
            print(f"  Unique items: {summary.get('unique_items', 0)}")
            print(f"  Sites searched: {summary.get('sites_searched', 0)}")
            print(f"  Date range: {summary.get('date_range', 'N/A')}")

            # Display per-site results
            print("\nPER-SITE RESULTS:")
            print("-" * 40)
            search_details = summary.get('search_details', [])

            if search_details:
                for detail in search_details:
                    site_name = detail.get('site', 'Unknown')
                    found_count = detail.get('found_count', 0)
                    status = "✓" if found_count > 0 else "○"
                    print(f"  {status} {site_name}: {found_count} items")
            else:
                print("  No search details available")

            # Display sample items
            items = result_json.get("items", [])
            if items:
                print("\n" + "=" * 60)
                print(f"SAMPLE ITEMS (showing first 5 of {len(items)}):")
                print("=" * 60)

                for i, item in enumerate(items[:5], 1):
                    print(f"\n{i}. [{item.get('platform', 'Unknown')}] {item.get('datetime_local', 'No date')}")

                    # Show title/snippet
                    snippet = item.get('title_or_snippet', 'No content')
                    if len(snippet) > 150:
                        snippet = snippet[:150] + "..."
                    print(f"   {snippet}")

                    # Show URL
                    url = item.get('url', 'No URL')
                    if len(url) > 80:
                        url = url[:77] + "..."
                    print(f"   URL: {url}")

                    # Show category and author if available
                    category = item.get('category', 'unknown')
                    author = item.get('author', 'anonymous')
                    print(f"   Type: {category}, Author: {author}")
            else:
                print("\n○ No items found in search results")

            # Save results to file
            # output_file = f"test_results_{symbol}_{curr_date.replace('-', '')}.json"
            # with open(output_file, "w", encoding="utf-8") as f:
            #     json.dump(result_json, f, ensure_ascii=False, indent=2)
            # print(f"\n✓ Full results saved to: {output_file}")

        except json.JSONDecodeError as e:
            print(f"\n⚠️ WARNING: Could not parse result as JSON")
            print(f"JSON Error: {e}")
            print("\nRaw output (first 500 characters):")
            print("-" * 40)
            print(result[:500] if len(result) > 500 else result)
            if len(result) > 500:
                print("... [truncated]")

    except Exception as e:
        print("\n✗ EXCEPTION OCCURRED:")
        print(f"  Type: {type(e).__name__}")
        print(f"  Message: {e}")
        print("\nTraceback:")
        print(traceback.format_exc())

    print("\n" + "=" * 80)
    print("Test completed")
    print("=" * 80)

if __name__ == "__main__":
    test_get_stock_news_openai()