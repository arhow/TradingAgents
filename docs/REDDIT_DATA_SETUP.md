# Reddit Data Setup Guide

This guide explains how to download Reddit stock data for use with the TradingAgents system.

## Prerequisites

1. **Reddit Account**: You need a Reddit account to create an app
2. **PRAW Library**: Already included in requirements.txt

## Step 1: Get Reddit API Credentials

1. **Log in to Reddit** with your account
2. Go to https://www.reddit.com/prefs/apps
3. Click "Create App" or "Create Another App" at the bottom
4. Fill in the form:
   - **Name**: YourAppName (e.g., "StockDataCollector")
   - **App type**: Select **"script"** (IMPORTANT - must be script, not web app!)
   - **Description**: Optional (e.g., "Collect stock discussion data")
   - **About URL**: Leave blank
   - **Redirect URI**: `http://localhost:8080` (required even though not used)
5. Click "Create app"
6. You'll see your app created. Note down:
   - **CLIENT_ID**: The 14-character string right under "personal use script" (e.g., "FFTtkIQGxr5G6H")
   - **CLIENT_SECRET**: The longer "secret" string (e.g., "gWcJBkZGgVEaniAQbGVEzO17rP3Jtw")

## Step 2: Configure Credentials

### Option A: Using .env file (Recommended)

Update the `.env` file in the project root:

```bash
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
REDDIT_USERNAME=YourRedditUsername
REDDIT_USER_AGENT=StockCollector/1.0 by u/YourRedditUsername
```

**IMPORTANT**: The user agent MUST include "by u/YourUsername" format!

### Option B: Edit the script directly

Edit `download_reddit_data.py` and add your credentials:

```python
CLIENT_ID = "your_client_id_here"
CLIENT_SECRET = "your_client_secret_here"
USER_AGENT = "StockCollector/1.0 by YourRedditUsername"
```

## Step 3: Run the Downloader

```bash
python download_reddit_data.py
```

The script will:
- Connect to Reddit API
- Download posts from stock-related subreddits
- Search for specific stock tickers (AAPL, TSLA, etc.)
- Save data in the expected JSONL format

## Step 4: Verify Data

Check that data was created:

```bash
# Linux/Mac
ls -la /home/wang/pyworkspace/data/tradingagents/reddit_data/

# Windows WSL
ls -la /mnt/d/pyworkspace/data/tradingagents/reddit_data/
```

You should see:
```
reddit_data/
├── company_news/
│   ├── wallstreetbets.jsonl
│   ├── stocks.jsonl
│   └── investing.jsonl
└── global_news/
    ├── worldnews.jsonl
    ├── news.jsonl
    └── economics.jsonl
```

## Customization

Edit `download_reddit_data.py` to customize:

- **DAYS_BACK**: Number of days to look back (default: 30)
- **US_TICKERS**: List of US stock tickers to search
- **CHINESE_TICKERS**: List of Chinese stock tickers
- **COMPANY_SUBREDDITS**: Subreddits for company news
- **NEWS_SUBREDDITS**: Subreddits for global news
- **MARKET_KEYWORDS**: Keywords for market news

## Rate Limits

Reddit API has rate limits:
- 60 requests per minute
- The script includes 1-second delays between requests
- First run may take 10-30 minutes depending on settings

## Troubleshooting

### "401 Unauthorized" Error
- Check your CLIENT_ID and CLIENT_SECRET are correct
- Make sure app type is "script" not "web app"
- Verify the user agent format includes "by u/YourUsername"
- The Reddit app may have been deleted - create a new one
- Credentials may have expired - regenerate them

### No Data Found
- Reddit search can be limited
- Try broader date ranges
- Some subreddits may have less content
- Popular tickers (AAPL, TSLA) will have more results

### Path Issues on Windows/WSL
If running on Windows with WSL, adjust the OUTPUT_DIR:
```python
OUTPUT_DIR = "/mnt/d/pyworkspace/data/tradingagents/reddit_data"
```

## Testing the Data

After downloading, test with:

```python
from tradingagents.dataflows.interface import get_reddit_company_news

# Test company news
result = get_reddit_company_news(
    ticker="AAPL",
    start_date="2024-11-15",
    look_back_days=7,
    max_limit_per_day=5
)
print(result)
```

## Note on Data Quality

- Reddit data is user-generated and may contain:
  - Speculation and rumors
  - Memes and jokes
  - Biased opinions
  - Inaccurate information

- Use Reddit data as sentiment indicators, not financial advice
- The more recent the data, the more likely it is to be available
- Historical data (>1 year old) may be limited