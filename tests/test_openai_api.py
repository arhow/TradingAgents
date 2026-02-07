#!/usr/bin/env python3
"""Test OpenAI API to understand the error"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tradingagents.dataflows.config import get_config
from openai import OpenAI

def test_openai_api():
    """Test different OpenAI API formats"""

    config = get_config()
    print(f"Config keys: {config.keys()}")
    print(f"Backend URL: {config.get('backend_url', 'Not set')}")
    print(f"Quick think LLM: {config.get('quick_think_llm', 'Not set')}")

    # Test 1: Check if backend_url is set
    if "backend_url" in config and config["backend_url"]:
        print(f"\nUsing custom backend URL: {config['backend_url']}")
        client = OpenAI(base_url=config["backend_url"])
    else:
        print("\nUsing standard OpenAI API")
        client = OpenAI()

    # Test 2: Check what attributes the client has
    print(f"\nClient attributes: {dir(client)}")

    # Test 3: Check if 'responses' exists
    if hasattr(client, 'responses'):
        print("Client has 'responses' attribute")
    else:
        print("Client does NOT have 'responses' attribute")

    # Test 4: Check if 'chat' exists
    if hasattr(client, 'chat'):
        print("Client has 'chat' attribute")
        if hasattr(client.chat, 'completions'):
            print("Client has 'chat.completions' attribute")
    else:
        print("Client does NOT have 'chat' attribute")

    # Test 5: Try to understand the actual structure
    print("\nTrying to call the API...")

    # First try the custom format
    try:
        print("Attempting custom format (client.responses.create)...")
        response = client.responses.create(
            model=config["quick_think_llm"],
            input=[{"role": "system", "content": [{"type": "input_text", "text": "Test"}]}],
            text={"format": {"type": "text"}},
            reasoning={},
            temperature=1,
            max_output_tokens=100,
            top_p=1,
            store=True,
        )
        print("SUCCESS: Custom format works!")
        print(f"Response type: {type(response)}")
        return
    except AttributeError as e:
        print(f"FAILED: Custom format - AttributeError: {e}")
    except Exception as e:
        print(f"FAILED: Custom format - Other error: {type(e).__name__}: {e}")

    # Then try standard OpenAI format
    try:
        print("\nAttempting standard format (client.chat.completions.create)...")
        response = client.chat.completions.create(
            model=config.get("quick_think_llm", "gpt-3.5-turbo"),
            messages=[{"role": "system", "content": "Test"}],
            temperature=1,
            max_tokens=100,
        )
        print("SUCCESS: Standard format works!")
        print(f"Response: {response.choices[0].message.content}")
        return
    except Exception as e:
        print(f"FAILED: Standard format - {type(e).__name__}: {e}")

    print("\nNeither API format worked. Please check your configuration.")

if __name__ == "__main__":
    test_openai_api()