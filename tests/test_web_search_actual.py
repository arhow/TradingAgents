#!/usr/bin/env python3
"""Test actual web search with detailed output inspection"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tradingagents.dataflows.config import get_config
from openai import OpenAI

def test_web_search_detailed():
    """Test web search with detailed response inspection"""

    print("Testing Web Search Response Structure...")
    print("-" * 40)

    config = get_config()
    client = OpenAI(base_url=config["backend_url"])

    try:
        response = client.responses.create(
            model=config["quick_think_llm"],
            input=[
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "input_text",
                            "text": "Search for Apple stock news from the last 3 days and give me a brief summary.",
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
            max_output_tokens=500,
            top_p=1,
            store=True,
        )

        print(f"Response received!")
        print(f"  Status: {response.status}")
        print(f"  Model: {response.model}")

        print(f"\n1. response.output_text:")
        print(f"  Type: {type(response.output_text)}")
        print(f"  Value: '{response.output_text}'")
        print(f"  Is empty: {response.output_text == ''}")

        print(f"\n2. response.output items:")
        if hasattr(response, 'output'):
            print(f"  Number of items: {len(response.output)}")
            for i, item in enumerate(response.output):
                print(f"\n  Item {i}: {item.__class__.__name__}")

                # Check for different content attributes
                if hasattr(item, 'content') and item.content:
                    print(f"    Has content: Yes")
                    if isinstance(item.content, list):
                        print(f"    Content is list with {len(item.content)} items")
                        if len(item.content) > 0 and hasattr(item.content[0], 'text'):
                            print(f"    ✓ Found text: {item.content[0].text[:100]}...")

                if hasattr(item, 'summary') and item.summary:
                    print(f"    Has summary: Yes")
                    if isinstance(item.summary, list):
                        print(f"    Summary is list with {len(item.summary)} items")

                if hasattr(item, 'status'):
                    print(f"    Status: {item.status}")

        print(f"\n3. Alternative ways to get text:")

        # Check if there's any text in the response
        found_text = False

        # Method 1: Check all attributes
        for attr in dir(response):
            if not attr.startswith('_') and not attr.startswith('model_'):
                value = getattr(response, attr)
                if isinstance(value, str) and value and attr != 'id' and attr != 'object':
                    print(f"  Found string in response.{attr}: '{value[:50]}...'")
                    found_text = True
                    break

        if not found_text:
            print("  No text content found in response")

        print("\n4. Response status check:")
        if response.status == "incomplete":
            print("  ⚠️ Response is incomplete - this might be why output_text is empty")
            if hasattr(response, 'incomplete_details'):
                print(f"  Incomplete details: {response.incomplete_details}")

    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")

if __name__ == "__main__":
    test_web_search_detailed()