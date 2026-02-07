# OpenAI Responses API Structure Guide

## Overview
The OpenAI Responses API returns a `Response` object with the following key attributes:

## 1. `response.output` - List of Processing Items
**Type:** `list`

**Purpose:** Contains a list of items representing the model's reasoning process and function calls

**What it contains:**
- **ResponseReasoningItem**: The model's internal reasoning/thinking process
  - Used for chain-of-thought reasoning
  - Contains the model's thinking steps
  - Usually has `status`, `summary`, and `content` attributes

- **ResponseFunctionWebSearch**: A web search function call
  - Represents when the model uses web search
  - Has `status` (e.g., "completed")
  - May have `query` and `results` attributes

- **ResponseTextItem**: The actual text response to the user
  - Contains the final answer
  - Access via `item.content[0].text`

## 2. `response.output_text` - Final Text Output
**Type:** `str`

**Purpose:** The final formatted text output from the model
- This is what should be shown to the user
- It's the model's actual answer after reasoning and web search
- Can be an empty string if the response is incomplete

## 3. Other Important Attributes

- `response.text`: Configuration for text output format (not the actual text)
- `response.usage`: Token usage statistics
- `response.model`: The model that was used
- `response.status`: Response status (e.g., "incomplete", "completed")
- `response.reasoning`: Reasoning configuration

## How to Extract Text from the Response

### Method 1: Use `output_text` (Simplest)
```python
if response.output_text:
    return response.output_text
```

### Method 2: Extract from `output` items
```python
for item in response.output:
    if item.__class__.__name__ == 'ResponseTextItem':
        if hasattr(item, 'content') and item.content:
            if isinstance(item.content, list) and len(item.content) > 0:
                if hasattr(item.content[0], 'text'):
                    return item.content[0].text
```

## Common Issues and Solutions

### Issue: `response.output[1].content[0].text` fails
**Reason:**
- `response.output` may not have index 1
- The item at any index might not have `content` attribute
- Items can be ResponseReasoningItem or ResponseFunctionWebSearch which don't have text content

**Solution:** Use `response.output_text` or iterate through items to find ResponseTextItem

### Issue: `response.output_text` is empty string
**Reason:** Response might be incomplete (check `response.status`)

**Solution:** Wait for completion or handle incomplete responses