#!/usr/bin/env python3
"""Complete test to understand OpenAI Responses API structure"""

import os
import sys
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tradingagents.dataflows.config import get_config
from openai import OpenAI

def test_complete_response_structure():
    """Test to fully understand the response object structure"""

    config = get_config()
    client = OpenAI(base_url=config["backend_url"])

    print("=" * 80)
    print("COMPLETE OPENAI RESPONSES API STRUCTURE TEST")
    print("=" * 80)

    try:
        # Make a call with web search
        response = client.responses.create(
            model=config["quick_think_llm"],
            input=[
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "input_text",
                            "text": "Search for recent news about Apple stock and give me a brief summary.",
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

        print("\n1. RESPONSE OBJECT OVERVIEW")
        print("-" * 40)
        print(f"Response type: {type(response)}")
        print(f"Response class: {response.__class__.__name__}")

        print("\n2. TOP-LEVEL ATTRIBUTES")
        print("-" * 40)
        # Get all non-private attributes
        attrs = [attr for attr in dir(response) if not attr.startswith('_') and not attr.startswith('model_')]

        for attr in sorted(attrs):
            if hasattr(response, attr):
                value = getattr(response, attr)
                # Skip methods
                if callable(value):
                    continue

                if value is not None:
                    if isinstance(value, (str, int, float, bool)):
                        print(f"  {attr}: {value}")
                    elif isinstance(value, list):
                        print(f"  {attr}: List with {len(value)} items")
                    else:
                        print(f"  {attr}: {type(value).__name__}")

        print("\n3. RESPONSE.OUTPUT ANALYSIS")
        print("-" * 40)
        if hasattr(response, 'output'):
            print(f"response.output is a: {type(response.output)}")
            print(f"response.output length: {len(response.output)}")
            print("\nWhat response.output contains:")
            print("  - A list of items representing the model's reasoning process and function calls")
            print("  - Each item can be:")
            print("    • ResponseReasoningItem: The model's internal reasoning/thinking")
            print("    • ResponseFunctionWebSearch: A web search function call")
            print("    • ResponseTextItem: The actual text response to the user")

            print("\nDetailed output items:")
            for i, item in enumerate(response.output):
                print(f"\n  Item {i}:")
                print(f"    Type: {item.__class__.__name__}")

                if item.__class__.__name__ == 'ResponseReasoningItem':
                    print("    Purpose: Contains the model's reasoning/thinking process")
                    print(f"    Status: {item.status if hasattr(item, 'status') else 'N/A'}")
                    print(f"    Has summary: {bool(item.summary) if hasattr(item, 'summary') else False}")
                    print(f"    Has content: {bool(item.content) if hasattr(item, 'content') else False}")

                elif item.__class__.__name__ == 'ResponseFunctionWebSearch':
                    print("    Purpose: Web search function call made by the model")
                    print(f"    Status: {item.status if hasattr(item, 'status') else 'N/A'}")
                    if hasattr(item, 'query'):
                        print(f"    Query: {item.query}")
                    if hasattr(item, 'results'):
                        print(f"    Has results: {bool(item.results)}")

                elif item.__class__.__name__ == 'ResponseTextItem':
                    print("    Purpose: The actual text response to show the user")
                    if hasattr(item, 'content') and item.content:
                        if isinstance(item.content, list) and len(item.content) > 0:
                            if hasattr(item.content[0], 'text'):
                                text = item.content[0].text
                                print(f"    Text content: {text[:100]}..." if len(text) > 100 else f"    Text content: {text}")

        print("\n4. RESPONSE.OUTPUT_TEXT ANALYSIS")
        print("-" * 40)
        if hasattr(response, 'output_text'):
            print(f"response.output_text type: {type(response.output_text)}")

            if response.output_text:
                print("\nWhat response.output_text is:")
                print("  - The final formatted text output from the model")
                print("  - This is what should be shown to the user")
                print("  - It's the model's actual answer after reasoning and web search")

                # Try to get the actual text
                if isinstance(response.output_text, str):
                    print(f"\n  Actual text: {response.output_text[:200]}...")
                else:
                    print(f"  output_text is not a string, it's: {response.output_text}")

        print("\n5. OTHER IMPORTANT ATTRIBUTES")
        print("-" * 40)

        if hasattr(response, 'text'):
            print(f"response.text: {response.text}")
            print("  Purpose: Configuration for text output format")

        if hasattr(response, 'usage'):
            print(f"\nresponse.usage: {response.usage}")
            print("  Purpose: Token usage statistics")

        if hasattr(response, 'model'):
            print(f"\nresponse.model: {response.model}")
            print("  Purpose: The model that was used")

        print("\n6. HOW TO EXTRACT THE ACTUAL RESPONSE TEXT")
        print("-" * 40)
        print("The proper way to get the text response:")
        print("  1. Check response.output for ResponseTextItem objects")
        print("  2. Extract text from item.content[0].text")
        print("  3. Or use response.output_text if it contains the string directly")

        # Try to extract the actual text
        extracted_text = None

        # Method 1: Look for ResponseTextItem in output
        if hasattr(response, 'output'):
            for item in response.output:
                if item.__class__.__name__ == 'ResponseTextItem':
                    if hasattr(item, 'content') and item.content:
                        if isinstance(item.content, list) and len(item.content) > 0:
                            if hasattr(item.content[0], 'text'):
                                extracted_text = item.content[0].text
                                print(f"\n✓ Found text via ResponseTextItem: {extracted_text[:100]}...")
                                break

        # Method 2: Check output_text
        if not extracted_text and hasattr(response, 'output_text'):
            if isinstance(response.output_text, str):
                extracted_text = response.output_text
                print(f"\n✓ Found text via output_text: {extracted_text[:100]}...")

        if not extracted_text:
            print("\n✗ Could not find text content in response")

    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_complete_response_structure()