#!/usr/bin/env python3
"""Test to understand web search response structure"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tradingagents.dataflows.config import get_config
from openai import OpenAI

def test_web_search_response():
    """Test the response structure when using web search"""

    config = get_config()
    client = OpenAI(base_url=config["backend_url"])

    print("Testing OpenAI Responses API with web search...")
    print("-" * 50)

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
                            "text": "What is the current weather in New York? Just give me temperature.",
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
            max_output_tokens=200,
            top_p=1,
            store=True,
        )

        print(f"Response type: {type(response)}")
        print(f"Response has 'output': {hasattr(response, 'output')}")
        print(f"Response has 'output_text': {hasattr(response, 'output_text')}")

        # Check output_text first (simplest approach)
        if hasattr(response, 'output_text') and response.output_text:
            print(f"\n✓ Found output_text attribute")
            print(f"  Type: {type(response.output_text)}")
            print(f"  Value: {response.output_text}")

            # Try to extract actual text
            if isinstance(response.output_text, str):
                return response.output_text
            elif hasattr(response.output_text, 'text'):
                return response.output_text.text
            elif hasattr(response.output_text, 'content'):
                return response.output_text.content

        # Check text attribute
        if hasattr(response, 'text') and response.text:
            print(f"\n✓ Found text attribute")
            print(f"  Type: {type(response.text)}")
            print(f"  Value: {response.text}")

            if isinstance(response.text, str):
                return response.text

        # Check output items
        if hasattr(response, 'output'):
            print(f"\nresponse.output length: {len(response.output)}")

            for i, item in enumerate(response.output):
                print(f"\nItem {i}: {item.__class__.__name__}")

                # Check different item types
                if item.__class__.__name__ == 'ResponseReasoningItem':
                    print(f"  - Reasoning item")
                    if item.summary:
                        print(f"  - Has summary: {item.summary}")
                    if item.content:
                        print(f"  - Has content: {item.content}")

                elif item.__class__.__name__ == 'ResponseFunctionWebSearch':
                    print(f"  - Web search item")
                    print(f"  - Attributes: {[attr for attr in dir(item) if not attr.startswith('_')]}")

                    # Try to find content attributes
                    if hasattr(item, 'results'):
                        print(f"  - Has results: {item.results}")
                    if hasattr(item, 'query'):
                        print(f"  - Has query: {item.query}")
                    if hasattr(item, 'status'):
                        print(f"  - Has status: {item.status}")

                elif hasattr(item, 'content'):
                    # Generic content item
                    if item.content:
                        if isinstance(item.content, list) and len(item.content) > 0:
                            if hasattr(item.content[0], 'text'):
                                print(f"  ✓ Found text in content: {item.content[0].text}")
                                return item.content[0].text

        print("\nCouldn't find text content in response")

    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_web_search_response()