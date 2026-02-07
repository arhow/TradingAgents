#!/usr/bin/env python3
"""Test to understand the structure of OpenAI Responses API objects"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tradingagents.dataflows.config import get_config
from openai import OpenAI

def test_response_structure():
    """Test and print the structure of response objects"""

    config = get_config()
    client = OpenAI(base_url=config["backend_url"])

    print("Testing OpenAI Responses API structure...")
    print("-" * 50)

    try:
        # Make a simple call
        response = client.responses.create(
            model=config["quick_think_llm"],
            input=[
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "input_text",
                            "text": "Say 'Hello World' and nothing else.",
                        }
                    ],
                }
            ],
            text={"format": {"type": "text"}},
            reasoning={},
            temperature=1,
            max_output_tokens=100,
            top_p=1,
            store=True,
        )

        print(f"Response type: {type(response)}")
        print(f"Response attributes: {dir(response)}")
        print()

        # Check if response has output attribute
        if hasattr(response, 'output'):
            print(f"response.output exists, type: {type(response.output)}")
            print(f"response.output length: {len(response.output)}")
            print()

            # Iterate through output items
            for i, item in enumerate(response.output):
                print(f"Item {i}:")
                print(f"  Type: {type(item)}")
                print(f"  Class name: {item.__class__.__name__}")
                print(f"  Attributes: {dir(item)}")

                # Try to get content/text from different possible attributes
                if hasattr(item, 'content'):
                    print(f"  Has 'content': {item.content}")
                if hasattr(item, 'text'):
                    print(f"  Has 'text': {item.text}")
                if hasattr(item, 'summary'):
                    print(f"  Has 'summary': {item.summary}")
                if hasattr(item, 'type'):
                    print(f"  Item type: {item.type}")

                print()

        # Try the documented way to access content
        print("Trying to extract text content:")
        try:
            # Method 1: Direct index access
            content = response.output[1].content[0].text
            print(f"Method 1 (response.output[1].content[0].text): {content}")
        except Exception as e:
            print(f"Method 1 failed: {e}")

        try:
            # Method 2: Try with first item
            content = response.output[0].content[0].text
            print(f"Method 2 (response.output[0].content[0].text): {content}")
        except Exception as e:
            print(f"Method 2 failed: {e}")

        try:
            # Method 3: Look for item with content
            for item in response.output:
                if hasattr(item, 'content') and item.content:
                    if isinstance(item.content, list) and len(item.content) > 0:
                        if hasattr(item.content[0], 'text'):
                            print(f"Method 3 (found content in item): {item.content[0].text}")
                            break
                        elif isinstance(item.content[0], str):
                            print(f"Method 3 (found string content): {item.content[0]}")
                            break
        except Exception as e:
            print(f"Method 3 failed: {e}")

    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")

if __name__ == "__main__":
    test_response_structure()