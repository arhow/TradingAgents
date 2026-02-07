#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test suite for Reddit data downloader
Tests the Reddit download functionality and data format compatibility
"""

import os
import sys
import json
import tempfile
import shutil
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

# Load environment variables
load_dotenv()

from tradingagents.dataflows.reddit_downloader import RedditStockDownloader
from tradingagents.dataflows.interface import get_reddit_company_news, get_reddit_global_news
from tradingagents.dataflows.config import DATA_DIR


def test_reddit_api_credentials():
    """Test that Reddit API credentials are configured"""

    client_id = os.getenv("REDDIT_CLIENT_ID", "")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET", "")

    if not client_id or not client_secret:
        print("\n⚠️  Reddit API credentials not found in environment variables")
        print("To run Reddit downloader tests with real API:")
        print("1. Create a Reddit app at https://www.reddit.com/prefs/apps")
        print("2. Add to .env file:")
        print("   REDDIT_CLIENT_ID=your_client_id")
        print("   REDDIT_CLIENT_SECRET=your_client_secret")
        raise Exception("Reddit API credentials not configured")

    assert client_id != "", "REDDIT_CLIENT_ID should not be empty"
    assert client_secret != "", "REDDIT_CLIENT_SECRET should not be empty"
    print("✅ Reddit API credentials found")


def test_reddit_connection():
    """Test connection to Reddit API"""

    client_id = os.getenv("REDDIT_CLIENT_ID", "")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET", "")
    reddit_username = os.getenv("REDDIT_USERNAME", "YourUsername")
    reddit_user_agent = os.getenv("REDDIT_USER_AGENT", f"TestAgent/1.0 by u/{reddit_username}")

    if not client_id or not client_secret:
        raise Exception("Reddit API credentials not configured")

    try:
        downloader = RedditStockDownloader(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=reddit_user_agent
        )

        # Test connection by accessing a subreddit
        test_sub = downloader.reddit.subreddit("python")
        description = test_sub.description

        assert description is not None
        print("✅ Successfully connected to Reddit API")

    except Exception as e:
        if "401" in str(e):
            print(f"⚠️  401 Authentication Error: {e}")
            print("\nPossible causes:")
            print("1. Invalid client_id or client_secret")
            print("2. Reddit app may have been deleted or revoked")
            print("3. Credentials may have expired")
            print("\nTo fix:")
            print("1. Go to https://www.reddit.com/prefs/apps")
            print("2. Create a new 'script' type app")
            print("3. Update REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET in .env")
            raise Exception(f"Reddit authentication failed: {e}")
        else:
            raise Exception(f"Failed to connect to Reddit API: {e}")


def test_download_sample_data():
    """Test downloading a small sample of Reddit data"""

    client_id = os.getenv("REDDIT_CLIENT_ID", "")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET", "")
    reddit_username = os.getenv("REDDIT_USERNAME", "YourUsername")
    reddit_user_agent = os.getenv("REDDIT_USER_AGENT", f"TestAgent/1.0 by u/{reddit_username}")

    if not client_id or not client_secret:
        raise Exception("Reddit API credentials not configured")

    # Use app's default data directory
    output_dir = os.path.join(DATA_DIR, "reddit_data")

    try:
        downloader = RedditStockDownloader(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=reddit_user_agent
        )

        # Test with minimal data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)  # Only last week

        print(f"\n📥 Downloading sample data from {start_date.date()} to {end_date.date()}")

        # Download limited company news
        # Using more general terms since specific tickers might not have posts
        company_posts = downloader.download_company_news(
            tickers=["GOOGL", "NVDA"],  # Tickers that are more likely to have posts
            start_date=start_date,
            end_date=end_date,
            subreddits=["stocks"],  # Only 1 subreddit
            posts_per_ticker=10  # Increased to 10 to have better chance of finding posts
        )

        # Save to app's data directory
        downloader.save_to_jsonl(company_posts, output_dir, 'company_news')

        # Verify files were created
        company_news_dir = os.path.join(output_dir, 'company_news')
        assert os.path.exists(company_news_dir), "Company news directory not created"

        jsonl_files = [f for f in os.listdir(company_news_dir) if f.endswith('.jsonl')]
        assert len(jsonl_files) > 0, "No JSONL files created"

        print(f"✅ Created {len(jsonl_files)} JSONL files")

        # Verify file content
        for jsonl_file in jsonl_files:
            file_path = os.path.join(company_news_dir, jsonl_file)
            with open(file_path, 'r') as f:
                lines = f.readlines()
                if lines:
                    # Check first line is valid JSON
                    first_post = json.loads(lines[0])
                    assert 'created_utc' in first_post
                    assert 'title' in first_post
                    assert 'id' in first_post
                    print(f"  ✓ {jsonl_file}: {len(lines)} posts")

        print(f"\n📁 Data saved to: {output_dir}")

    except Exception as e:
        raise e


def test_data_format_compatibility():
    """Test that downloaded data format is compatible with existing functions"""

    # Create mock data in the expected format
    temp_dir = tempfile.mkdtemp()

    try:
        # Create mock Reddit data
        mock_posts = [
            {
                "created_utc": int((datetime.now() - timedelta(days=1)).timestamp()),
                "id": "test123",
                "title": "AAPL to the moon! 🚀",
                "selftext": "Apple just announced amazing earnings",
                "ups": 100,
                "num_comments": 50,
                "url": "https://reddit.com/r/stocks/test123"
            },
            {
                "created_utc": int((datetime.now() - timedelta(days=2)).timestamp()),
                "id": "test456",
                "title": "Why AAPL is overvalued",
                "selftext": "Here's my analysis on Apple stock...",
                "ups": 75,
                "num_comments": 30,
                "url": "https://reddit.com/r/stocks/test456"
            }
        ]

        # Save mock data in expected structure
        company_news_dir = os.path.join(temp_dir, 'reddit_data', 'company_news')
        os.makedirs(company_news_dir, exist_ok=True)

        mock_file = os.path.join(company_news_dir, 'stocks.jsonl')
        with open(mock_file, 'w') as f:
            for post in mock_posts:
                f.write(json.dumps(post) + '\n')

        # Test that the interface functions can read this data
        # Note: We'd need to mock the DATA_DIR to point to temp_dir
        # This is more of a format validation than full integration test

        # Verify the file format
        with open(mock_file, 'r') as f:
            for line in f:
                post = json.loads(line)
                assert isinstance(post['created_utc'], int)
                assert isinstance(post['title'], str)
                assert isinstance(post['ups'], int)

        print("✅ Data format is compatible with expected structure")

    finally:
        shutil.rmtree(temp_dir)


def test_mock_downloader():
    """Test the downloader with mocked Reddit API"""

    with patch('praw.Reddit') as mock_reddit:
        # Mock the Reddit instance
        mock_reddit_instance = Mock()
        mock_reddit.return_value = mock_reddit_instance

        # Mock subreddit
        mock_subreddit = Mock()
        mock_reddit_instance.subreddit.return_value = mock_subreddit

        # Mock submissions
        mock_submission = Mock()
        mock_submission.created_utc = int(datetime.now().timestamp())
        mock_submission.id = "mock123"
        mock_submission.title = "TSLA Discussion Thread"
        mock_submission.selftext = "What do you think about Tesla?"
        mock_submission.ups = 500
        mock_submission.num_comments = 100
        mock_submission.url = "https://reddit.com/mock"
        mock_submission.author = Mock()
        mock_submission.author.__str__ = Mock(return_value="test_user")

        mock_subreddit.hot.return_value = [mock_submission]
        mock_subreddit.new.return_value = [mock_submission]
        mock_subreddit.top.return_value = [mock_submission]

        # Test downloader with mock
        downloader = RedditStockDownloader(
            client_id="mock_id",
            client_secret="mock_secret",
            user_agent="MockAgent/1.0"
        )

        end_date = datetime.now()
        start_date = end_date - timedelta(days=1)

        posts = downloader.search_posts_by_date_range(
            "stocks",
            start_date,
            end_date,
            query="TSLA"
        )

        assert len(posts) > 0
        assert posts[0]['title'] == "TSLA Discussion Thread"
        print("✅ Mock downloader works correctly")


def test_integration_small_sample():
    """Integration test with small real data sample"""

    client_id = os.getenv("REDDIT_CLIENT_ID", "")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET", "")
    reddit_username = os.getenv("REDDIT_USERNAME", "YourUsername")
    user_agent = os.getenv("REDDIT_USER_AGENT", f"TestAgent/1.0 by u/{reddit_username}")

    if not client_id or not client_secret:
        raise Exception("Reddit API credentials not configured")

    print("\n" + "="*60)
    print("Reddit Downloader Integration Test")
    print("="*60)

    # Use app's default data directory
    output_dir = os.path.join(DATA_DIR, "reddit_data")

    try:
        # Initialize downloader
        print("\n🔌 Connecting to Reddit API...")
        downloader = RedditStockDownloader(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
        print("✅ Connected successfully")

        # Download minimal data for testing
        end_date = datetime.now()
        start_date = end_date - timedelta(days=3)  # Only 3 days

        print(f"\n📊 Downloading test data ({start_date.date()} to {end_date.date()})...")

        # Test company news with minimal data
        company_posts = downloader.download_company_news(
            tickers=["AAPL"],  # Just Apple
            start_date=start_date,
            end_date=end_date,
            subreddits=["stocks"],  # Just one subreddit
            posts_per_ticker=3  # Only 3 posts
        )

        # Save data
        downloader.save_to_jsonl(company_posts, output_dir, 'company_news')

        # Test global news with minimal data
        global_posts = downloader.download_global_news(
            start_date=start_date,
            end_date=end_date,
            subreddits=["economics"],  # Just one subreddit
            keywords=["stock market"],  # Just one keyword
            posts_per_keyword=3  # Only 3 posts
        )

        # Save data
        downloader.save_to_jsonl(global_posts, output_dir, 'global_news')

        # Verify structure
        print("\n📁 Verifying data structure...")

        company_dir = os.path.join(output_dir, 'company_news')
        global_dir = os.path.join(output_dir, 'global_news')

        assert os.path.exists(company_dir), "Company news directory not created"
        assert os.path.exists(global_dir), "Global news directory not created"

        # Count posts
        total_company = sum(len(posts) for posts in company_posts.values())
        total_global = sum(len(posts) for posts in global_posts.values())

        print(f"\n✅ Test successful!")
        print(f"  - Company news: {total_company} posts")
        print(f"  - Global news: {total_global} posts")
        print(f"  - Data saved to: {output_dir}")

    except Exception as e:
        raise Exception(f"Integration test failed: {e}")


def main():
    """Run all tests"""

    print("\n" + "#"*60)
    print("# Reddit Downloader Test Suite")
    print("#"*60)

    # Run tests
    tests = [
        ("API Credentials", test_reddit_api_credentials),
        ("Reddit Connection", test_reddit_connection),
        ("Data Format", test_data_format_compatibility),
        ("Mock Downloader", test_mock_downloader),
        ("Sample Download", test_download_sample_data),
        ("Integration Test", test_integration_small_sample),
    ]

    passed = 0
    failed = 0
    skipped = 0

    for test_name, test_func in tests:
        print(f"\n### Testing: {test_name}")
        print("-"*40)
        try:
            test_func()
            passed += 1
        except Exception as e:
            if "credentials not configured" in str(e).lower():
                print(f"⚠️  Skipped: {e}")
                skipped += 1
            else:
                print(f"❌ Failed: {e}")
                failed += 1

    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"⚠️  Skipped: {skipped}")

    if failed == 0:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {failed} tests failed")


if __name__ == "__main__":
    main()