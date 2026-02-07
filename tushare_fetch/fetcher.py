"""
Tushare data fetcher for downloading historical stock data.
"""

import os
import sys
import time
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Optional, List
import logging

# Import tushare from installed package (avoid local folder shadowing)
import tushare as ts

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TushareFetcher:
    """Fetcher for downloading Chinese stock market data from Tushare."""

    def __init__(self, token: str, data_dir: str = "data/tushare"):
        """
        Initialize Tushare fetcher.

        Args:
            token: Tushare API token
            data_dir: Directory to save data
        """
        self.token = token
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Initialize Tushare API directly with token
        self.pro = ts.pro_api(token)

        logger.info(f"Initialized TushareFetcher with data directory: {self.data_dir}")

    def fetch_stock_basic(self, save: bool = True) -> pd.DataFrame:
        """
        Fetch basic information for all stocks.

        Args:
            save: Whether to save to file

        Returns:
            DataFrame with stock basic information
        """
        logger.info("Fetching stock basic information...")

        df = self.pro.stock_basic(
            fields=[
                "ts_code",
                "symbol",
                "name",
                "area",
                "industry",
                "cnspell",
                "market",
                "list_date",
                "act_name",
                "act_ent_type"
            ]
        )

        logger.info(f"Fetched {len(df)} stocks")

        if save:
            output_file = self.data_dir / "stock_basic.csv"
            df.to_csv(output_file, index=False, encoding='utf-8-sig')
            logger.info(f"Saved to {output_file}")

        return df

    def fetch_daily_data(
        self,
        ts_code: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Fetch daily trading data for a single stock.

        Args:
            ts_code: Stock code (e.g., '000001.SZ')
            start_date: Start date in YYYYMMDD format (default: from listing)
            end_date: End date in YYYYMMDD format (default: today)

        Returns:
            DataFrame with daily trading data
        """
        if end_date is None:
            end_date = datetime.now().strftime("%Y%m%d")

        try:
            df = self.pro.daily(
                ts_code=ts_code,
                start_date=start_date,
                end_date=end_date,
                fields=[
                    "ts_code",
                    "trade_date",
                    "open",
                    "high",
                    "low",
                    "close",
                    "pre_close",
                    "change",
                    "pct_chg",
                    "vol",
                    "amount"
                ]
            )
            return df
        except Exception as e:
            logger.error(f"Error fetching data for {ts_code}: {e}")
            return pd.DataFrame()

    def fetch_all_daily_data(
        self,
        stock_list: Optional[List[str]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        batch_size: int = 100,
        delay: float = 0.2
    ):
        """
        Fetch daily data for all stocks and save to individual files.

        Args:
            stock_list: List of stock codes (if None, fetch from stock_basic)
            start_date: Start date in YYYYMMDD format
            end_date: End date in YYYYMMDD format
            batch_size: Number of stocks to process before checkpointing
            delay: Delay between API calls in seconds (to avoid rate limits)
        """
        # Get stock list if not provided
        if stock_list is None:
            logger.info("Fetching stock list...")
            stock_basic_df = self.fetch_stock_basic(save=True)
            stock_list = stock_basic_df['ts_code'].tolist()

        total_stocks = len(stock_list)
        logger.info(f"Starting to fetch daily data for {total_stocks} stocks")

        # Create daily data directory
        daily_dir = self.data_dir / "daily"
        daily_dir.mkdir(exist_ok=True)

        # Track progress
        progress_file = self.data_dir / "fetch_progress.txt"
        completed_stocks = self._load_progress(progress_file)

        # Process stocks
        for idx, ts_code in enumerate(stock_list, 1):
            if ts_code in completed_stocks:
                logger.info(f"[{idx}/{total_stocks}] Skipping {ts_code} (already completed)")
                continue

            logger.info(f"[{idx}/{total_stocks}] Fetching {ts_code}...")

            df = self.fetch_daily_data(ts_code, start_date, end_date)

            if not df.empty:
                # Save to CSV
                output_file = daily_dir / f"{ts_code}.csv"
                df.to_csv(output_file, index=False, encoding='utf-8-sig')
                logger.info(f"  Saved {len(df)} records to {output_file}")
            else:
                logger.warning(f"  No data for {ts_code}")

            # Update progress
            completed_stocks.add(ts_code)
            self._save_progress(progress_file, completed_stocks)

            # Rate limiting
            time.sleep(delay)

            # Checkpoint every batch_size stocks
            if idx % batch_size == 0:
                logger.info(f"Checkpoint: Completed {idx}/{total_stocks} stocks")

        logger.info(f"Completed fetching data for all {total_stocks} stocks")

    def _load_progress(self, progress_file: Path) -> set:
        """Load progress from file."""
        if progress_file.exists():
            with open(progress_file, 'r') as f:
                return set(line.strip() for line in f if line.strip())
        return set()

    def _save_progress(self, progress_file: Path, completed_stocks: set):
        """Save progress to file."""
        with open(progress_file, 'w') as f:
            for ts_code in sorted(completed_stocks):
                f.write(f"{ts_code}\n")

    def merge_daily_data(self, output_file: str = "all_daily_data.parquet"):
        """
        Merge all individual daily data files into a single file.

        Args:
            output_file: Output filename (supports .csv or .parquet)
        """
        daily_dir = self.data_dir / "daily"

        if not daily_dir.exists():
            logger.error("Daily data directory does not exist")
            return

        logger.info("Merging all daily data files...")

        all_files = list(daily_dir.glob("*.csv"))
        logger.info(f"Found {len(all_files)} files to merge")

        dfs = []
        for file in all_files:
            try:
                df = pd.read_csv(file)
                dfs.append(df)
            except Exception as e:
                logger.error(f"Error reading {file}: {e}")

        if dfs:
            merged_df = pd.concat(dfs, ignore_index=True)
            logger.info(f"Merged {len(merged_df)} total records")

            output_path = self.data_dir / output_file

            if output_file.endswith('.parquet'):
                merged_df.to_parquet(output_path, index=False)
            else:
                merged_df.to_csv(output_path, index=False, encoding='utf-8-sig')

            logger.info(f"Saved merged data to {output_path}")
        else:
            logger.warning("No data to merge")
