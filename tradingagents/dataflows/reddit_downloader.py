#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reddit Stock News Downloader using PRAW
Downloads Reddit posts about stocks and saves them in the expected format
"""

import praw
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import argparse
from tqdm import tqdm
import time


class RedditStockDownloader:
    """Download stock-related posts from Reddit using PRAW"""

    def __init__(self, client_id: str, client_secret: str, user_agent: str):
        """
        Initialize Reddit API connection

        Args:
            client_id: Reddit API client ID
            client_secret: Reddit API client secret
            user_agent: User agent string for API requests
        """
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )

        # Company ticker mapping (same as in reddit_utils.py)
        self.ticker_to_company = {
            "AAPL": "Apple",
            "MSFT": "Microsoft",
            "GOOGL": "Google",
            "AMZN": "Amazon",
            "TSLA": "Tesla",
            "NVDA": "Nvidia",
            "META": "Meta OR Facebook",
            "AMD": "AMD",
            "INTC": "Intel",
            "BABA": "Alibaba",
            "NFLX": "Netflix",
            "PYPL": "PayPal",
            "PLTR": "Palantir",
            # Add more as needed
        }

        # Chinese stock tickers
        self.chinese_tickers = {
            "300418.SZ": "昆仑万维 OR Kunlun",
            "000001.SZ": "平安银行 OR Ping An Bank",
            "600000.SH": "浦发银行 OR Pudong Bank",
            "000002.SZ": "万科 OR Vanke",
            # Add more Chinese stocks as needed
        }

        self.all_tickers = {**self.ticker_to_company, **self.chinese_tickers}

    def search_posts_by_date_range(
        self,
        subreddit_name: str,
        start_date: datetime,
        end_date: datetime,
        query: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Search posts in a subreddit within a date range

        Args:
            subreddit_name: Name of the subreddit
            start_date: Start date for posts
            end_date: End date for posts
            query: Optional search query
            limit: Maximum number of posts to retrieve

        Returns:
            List of post dictionaries
        """
        subreddit = self.reddit.subreddit(subreddit_name)
        posts = []

        # Convert dates to timestamps
        start_timestamp = int(start_date.timestamp())
        end_timestamp = int(end_date.timestamp())

        # Search methods to try
        search_methods = ['hot', 'new', 'top']

        for method in search_methods:
            if method == 'hot':
                submissions = subreddit.hot(limit=limit)
            elif method == 'new':
                submissions = subreddit.new(limit=limit)
            elif method == 'top':
                submissions = subreddit.top(time_filter='month', limit=limit)

            for submission in submissions:
                # Check if post is within date range
                if start_timestamp <= submission.created_utc <= end_timestamp:
                    # If query specified, check if it's in title or text
                    if query:
                        query_lower = query.lower()
                        if (query_lower not in submission.title.lower() and
                            query_lower not in submission.selftext.lower()):
                            continue

                    post_data = {
                        "created_utc": int(submission.created_utc),
                        "id": submission.id,
                        "title": submission.title,
                        "selftext": submission.selftext,
                        "ups": submission.ups,
                        "num_comments": submission.num_comments,
                        "url": submission.url,
                        "subreddit": subreddit_name,
                        "author": str(submission.author) if submission.author else "[deleted]"
                    }
                    posts.append(post_data)

        return posts

    def download_company_news(
        self,
        tickers: List[str],
        start_date: datetime,
        end_date: datetime,
        subreddits: List[str] = None,
        posts_per_ticker: int = 50
    ) -> Dict[str, List[Dict]]:
        """
        Download company-specific news from Reddit

        Args:
            tickers: List of stock tickers to search for
            start_date: Start date for posts
            end_date: End date for posts
            subreddits: List of subreddits to search
            posts_per_ticker: Max posts per ticker

        Returns:
            Dictionary mapping subreddit to list of posts
        """
        if subreddits is None:
            subreddits = ["wallstreetbets", "stocks", "investing", "StockMarket"]

        all_posts = {sub: [] for sub in subreddits}

        for subreddit_name in subreddits:
            print(f"\nSearching r/{subreddit_name}...")

            for ticker in tqdm(tickers, desc=f"Tickers in r/{subreddit_name}"):
                try:
                    # Search for ticker symbol
                    posts = self.search_posts_by_date_range(
                        subreddit_name,
                        start_date,
                        end_date,
                        query=ticker,
                        limit=posts_per_ticker
                    )

                    # Also search for company name if available
                    if ticker in self.all_tickers:
                        company_names = self.all_tickers[ticker].split(" OR ")
                        for company_name in company_names:
                            company_posts = self.search_posts_by_date_range(
                                subreddit_name,
                                start_date,
                                end_date,
                                query=company_name,
                                limit=posts_per_ticker // len(company_names)
                            )
                            posts.extend(company_posts)

                    all_posts[subreddit_name].extend(posts)

                    # Rate limiting
                    time.sleep(1)

                except Exception as e:
                    print(f"Error searching for {ticker} in r/{subreddit_name}: {e}")
                    continue

        # Remove duplicates
        for subreddit_name in all_posts:
            seen_ids = set()
            unique_posts = []
            for post in all_posts[subreddit_name]:
                if post['id'] not in seen_ids:
                    seen_ids.add(post['id'])
                    unique_posts.append(post)
            all_posts[subreddit_name] = unique_posts

        return all_posts

    def download_global_news(
        self,
        start_date: datetime,
        end_date: datetime,
        subreddits: List[str] = None,
        keywords: List[str] = None,
        posts_per_keyword: int = 50
    ) -> Dict[str, List[Dict]]:
        """
        Download global market news from Reddit

        Args:
            start_date: Start date for posts
            end_date: End date for posts
            subreddits: List of news subreddits
            keywords: Market-related keywords to search
            posts_per_keyword: Max posts per keyword

        Returns:
            Dictionary mapping subreddit to list of posts
        """
        if subreddits is None:
            subreddits = ["worldnews", "news", "economics", "finance"]

        if keywords is None:
            keywords = [
                "stock market", "S&P 500", "NASDAQ", "Dow Jones",
                "Federal Reserve", "Fed rate", "inflation", "recession",
                "earnings", "GDP", "unemployment", "trade war",
                "interest rate", "market crash", "bull market", "bear market"
            ]

        all_posts = {sub: [] for sub in subreddits}

        for subreddit_name in subreddits:
            print(f"\nSearching r/{subreddit_name}...")

            for keyword in tqdm(keywords, desc=f"Keywords in r/{subreddit_name}"):
                try:
                    posts = self.search_posts_by_date_range(
                        subreddit_name,
                        start_date,
                        end_date,
                        query=keyword,
                        limit=posts_per_keyword
                    )
                    all_posts[subreddit_name].extend(posts)

                    # Rate limiting
                    time.sleep(1)

                except Exception as e:
                    print(f"Error searching for '{keyword}' in r/{subreddit_name}: {e}")
                    continue

        # Remove duplicates
        for subreddit_name in all_posts:
            seen_ids = set()
            unique_posts = []
            for post in all_posts[subreddit_name]:
                if post['id'] not in seen_ids:
                    seen_ids.add(post['id'])
                    unique_posts.append(post)
            all_posts[subreddit_name] = unique_posts

        return all_posts

    def save_to_jsonl(
        self,
        posts: Dict[str, List[Dict]],
        output_dir: str,
        category: str
    ):
        """
        Save posts to JSONL files in the expected format

        Args:
            posts: Dictionary mapping subreddit to list of posts
            output_dir: Output directory path
            category: Category name (e.g., 'company_news' or 'global_news')
        """
        category_dir = os.path.join(output_dir, category)
        os.makedirs(category_dir, exist_ok=True)

        for subreddit_name, subreddit_posts in posts.items():
            if not subreddit_posts:
                continue

            file_path = os.path.join(category_dir, f"{subreddit_name}.jsonl")

            # Sort posts by date
            subreddit_posts.sort(key=lambda x: x['created_utc'])

            with open(file_path, 'w') as f:
                for post in subreddit_posts:
                    f.write(json.dumps(post) + '\n')

            print(f"Saved {len(subreddit_posts)} posts to {file_path}")


def main():
    """Main function to run the downloader"""
    parser = argparse.ArgumentParser(description='Download Reddit stock data')
    parser.add_argument('--client-id', required=True, help='Reddit API client ID')
    parser.add_argument('--client-secret', required=True, help='Reddit API client secret')
    parser.add_argument('--user-agent', default='StockDataCollector/1.0 by u/YourRedditUsername',
                       help='User agent (format: AppName/Version by u/YourRedditUsername)')
    parser.add_argument('--output-dir', default='/home/wang/pyworkspace/data/tradingagents/reddit_data',
                       help='Output directory for data')
    parser.add_argument('--days-back', type=int, default=30, help='Number of days to look back')
    parser.add_argument('--tickers', nargs='+',
                       default=['AAPL', 'TSLA', 'NVDA', 'MSFT', 'AMZN'],
                       help='Stock tickers to search')
    parser.add_argument('--include-chinese', action='store_true',
                       help='Include Chinese stock tickers')

    args = parser.parse_args()

    # Initialize downloader
    downloader = RedditStockDownloader(
        client_id=args.client_id,
        client_secret=args.client_secret,
        user_agent=args.user_agent
    )

    # Set date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=args.days_back)

    print(f"Downloading Reddit data from {start_date.date()} to {end_date.date()}")

    # Add Chinese tickers if requested
    tickers = args.tickers
    if args.include_chinese:
        tickers.extend(['300418.SZ', '000001.SZ', '600000.SH'])

    # Download company news
    print("\n=== Downloading Company News ===")
    company_posts = downloader.download_company_news(
        tickers=tickers,
        start_date=start_date,
        end_date=end_date
    )
    downloader.save_to_jsonl(company_posts, args.output_dir, 'company_news')

    # Download global news
    print("\n=== Downloading Global News ===")
    global_posts = downloader.download_global_news(
        start_date=start_date,
        end_date=end_date
    )
    downloader.save_to_jsonl(global_posts, args.output_dir, 'global_news')

    print(f"\n✅ Download complete! Data saved to {args.output_dir}")


if __name__ == "__main__":
    main()