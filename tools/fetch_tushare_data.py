#!/usr/bin/env python3
"""
CLI tool to fetch Tushare data for Chinese stock market.

Usage:
    python tools/fetch_tushare_data.py --token YOUR_TOKEN
    python tools/fetch_tushare_data.py --token YOUR_TOKEN --start-date 20200101
    python tools/fetch_tushare_data.py --token YOUR_TOKEN --stock-basic-only
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path to import tushare_fetch module
sys.path.insert(0, str(Path(__file__).parent.parent))

from tushare_fetch.fetcher import TushareFetcher


def main():
    parser = argparse.ArgumentParser(
        description="Fetch Chinese stock market data from Tushare"
    )

    parser.add_argument(
        "--token",
        type=str,
        default="d45a1d8e8d02489cb9b86ebaa05f7658a327ad7a9558f082dcd896c3",
        help="Tushare API token (default: token from samples)"
    )

    parser.add_argument(
        "--data-dir",
        type=str,
        default="data/tushare",
        help="Directory to save data (default: data/tushare)"
    )

    parser.add_argument(
        "--start-date",
        type=str,
        default=None,
        help="Start date in YYYYMMDD format (default: from beginning)"
    )

    parser.add_argument(
        "--end-date",
        type=str,
        default=None,
        help="End date in YYYYMMDD format (default: today)"
    )

    parser.add_argument(
        "--stock-basic-only",
        action="store_true",
        help="Only fetch stock basic information"
    )

    parser.add_argument(
        "--merge-only",
        action="store_true",
        help="Only merge existing daily data files"
    )

    parser.add_argument(
        "--batch-size",
        type=int,
        default=100,
        help="Number of stocks to process before checkpointing (default: 100)"
    )

    parser.add_argument(
        "--delay",
        type=float,
        default=0.2,
        help="Delay between API calls in seconds (default: 0.2)"
    )

    args = parser.parse_args()

    # Initialize fetcher
    fetcher = TushareFetcher(token=args.token, data_dir=args.data_dir)

    if args.merge_only:
        # Only merge existing files
        print("Merging existing daily data files...")
        fetcher.merge_daily_data()
        print("Done!")
        return

    # Fetch stock basic information
    print("=" * 60)
    print("Fetching stock basic information...")
    print("=" * 60)
    stock_basic_df = fetcher.fetch_stock_basic(save=True)
    print(f"\nFetched {len(stock_basic_df)} stocks")
    print(stock_basic_df.head())

    if args.stock_basic_only:
        print("\nDone! (stock basic only)")
        return

    # Fetch daily data for all stocks
    print("\n" + "=" * 60)
    print("Fetching daily data for all stocks...")
    print("=" * 60)
    print(f"Start date: {args.start_date or 'from beginning'}")
    print(f"End date: {args.end_date or 'today'}")
    print(f"Batch size: {args.batch_size}")
    print(f"API delay: {args.delay}s")
    print("=" * 60)

    fetcher.fetch_all_daily_data(
        start_date=args.start_date,
        end_date=args.end_date,
        batch_size=args.batch_size,
        delay=args.delay
    )

    # Ask if user wants to merge
    print("\n" + "=" * 60)
    response = input("Merge all daily data into a single file? (y/n): ")
    if response.lower() == 'y':
        fetcher.merge_daily_data()

    print("\nDone!")


if __name__ == "__main__":
    main()
