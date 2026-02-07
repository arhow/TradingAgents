#!/usr/bin/env python3
"""Test with increased max_output_tokens"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tradingagents.dataflows.interface import get_stock_news_openai

# First, let's patch the function temporarily to use more tokens
from tradingagents.dataflows.config import get_config
from openai import OpenAI

def test_stock_news_with_more_tokens():
    """Test with increased token limit"""

    print("Testing with increased max_output_tokens...")
    print("-" * 40)

    config = get_config()
    client = OpenAI(base_url=config["backend_url"])

    ticker = "AAPL"
    curr_date = "2025-09-19"

    try:
        print(f"Calling API with max_output_tokens=10000 (instead of 4096)")

        response = client.responses.create(
            model=config["quick_think_llm"],
            input=[
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "input_text",
                            "text": f"Can you search Social Media for {ticker} from 7 days before {curr_date} to {curr_date}? Make sure you only get the data posted during that period.",
                        }
                    ],
                }
            ],
            text={"format": {"type": "text"}},
            reasoning={},
            tools=[
                {
                    "type": "web_search_preview",
                    "user_location": {"type": "approximate"},
                    "search_context_size": "low",
                }
            ],
            temperature=1,
            max_output_tokens=10000,  # Increased from 4096
            top_p=1,
            store=True,
        )

        print(f"\nResponse Status: {response.status}")

        if response.status == "incomplete":
            print(f"  Still incomplete. Reason: {response.incomplete_details}")

        print(f"\nOutput Text:")
        print(f"  Is empty: {response.output_text == ''}")

        if response.output_text:
            print(f"  Length: {len(response.output_text)} characters")
            print(f"\nContent Preview:")
            print("-" * 40)
            print(response.output_text[:500])
            if len(response.output_text) > 500:
                print("... [truncated]")
        else:
            print("  output_text is still empty")

            # Try to understand what's in the output
            print(f"\nOutput items: {len(response.output)}")
            for i, item in enumerate(response.output):
                print(f"  {i}: {item.__class__.__name__} - Status: {getattr(item, 'status', 'N/A')}")

    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")

if __name__ == "__main__":
    test_stock_news_with_more_tokens()