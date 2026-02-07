# TradingAgents Analyst Process Documentation

## Overview

The TradingAgents framework employs a sophisticated multi-agent system where specialized analysts work in parallel to gather and analyze different aspects of market data. Each analyst operates as an independent LLM-powered agent with specific tools and responsibilities.

## Analyst Team Structure

The system includes four specialized analysts, each focusing on a distinct domain:

### 1. Market Analyst
**Location**: `tradingagents/agents/analysts/market_analyst.py`

**Purpose**: Performs technical analysis using quantitative indicators and price patterns.

**Key Responsibilities**:
- Analyzes price movements and trends using technical indicators
- Selects up to 8 most relevant indicators from categories:
  - **Moving Averages**: SMA (50, 200), EMA (10)
  - **MACD Components**: MACD line, Signal line, Histogram
  - **Momentum**: RSI (Relative Strength Index)
  - **Volatility**: Bollinger Bands (Upper, Middle, Lower), ATR
  - **Volume-Based**: VWMA (Volume Weighted Moving Average)

**Tools Used**:
- `get_YFin_data`: Fetches historical price data from Yahoo Finance
- `get_stockstats_indicators_report`: Generates technical indicator calculations

**Output**: Detailed technical analysis report with trend analysis and a summary markdown table

### 2. Fundamentals Analyst
**Location**: `tradingagents/agents/analysts/fundamentals_analyst.py`

**Purpose**: Evaluates company financial health and intrinsic value.

**Key Responsibilities**:
- Analyzes financial statements (balance sheet, income statement, cash flow)
- Reviews insider transactions and sentiment
- Evaluates company financial history and metrics
- Assesses company profile and business fundamentals

**Tools Used**:
- Online mode: `get_fundamentals_openai`
- Offline mode:
  - `get_finnhub_company_insider_sentiment`
  - `get_finnhub_company_insider_transactions`
  - `get_simfin_balance_sheet`
  - `get_simfin_cashflow`
  - `get_simfin_income_stmt`

**Output**: Comprehensive fundamental analysis report with financial metrics and insider activity

### 3. News Analyst
**Location**: `tradingagents/agents/analysts/news_analyst.py`

**Purpose**: Monitors and analyzes global news and macroeconomic events.

**Key Responsibilities**:
- Tracks global economic news and events
- Analyzes macroeconomic trends
- Identifies market-moving news
- Evaluates geopolitical impacts on markets

**Tools Used**:
- Online mode: `get_global_news_openai`, `get_google_news`
- Offline mode: `get_finnhub_news`, `get_reddit_news`, `get_google_news`

**Output**: News analysis report covering relevant global and company-specific events

### 4. Social Media Analyst
**Location**: `tradingagents/agents/analysts/social_media_analyst.py`

**Purpose**: Gauges public sentiment and social media trends.

**Key Responsibilities**:
- Analyzes social media posts and discussions
- Measures public sentiment toward specific companies
- Tracks trending topics and viral content
- Evaluates daily sentiment variations

**Tools Used**:
- Online mode: `get_stock_news_openai`
- Offline mode: `get_reddit_stock_info`

**Output**: Sentiment analysis report with social media insights and public perception metrics

## Process Flow

### 1. Initialization Phase
```python
# Each analyst receives:
- trade_date: The date for analysis
- company_of_interest: Ticker symbol
- messages: Conversation history
- config: Online/offline tool selection
```

### 2. Parallel Execution
All selected analysts run simultaneously, each:
1. Receiving the same initial state
2. Using their specialized tools to gather data
3. Applying their domain-specific prompts
4. Generating independent analysis reports

### 3. Tool Execution Pattern
Each analyst follows this pattern:
```python
1. Select appropriate tools based on config (online vs offline)
2. Create specialized system prompt with analysis instructions
3. Bind tools to LLM for function calling
4. Execute tool calls to gather data
5. Process and analyze retrieved information
6. Generate structured report with markdown table
```

### 4. Report Generation
Each analyst produces:
- **Detailed Analysis**: In-depth examination of their domain
- **Key Insights**: Actionable findings for traders
- **Markdown Table**: Organized summary of critical points
- **Trading Implications**: How findings might affect trading decisions

## Configuration Options

### Online vs Offline Mode
```python
config["online_tools"] = True  # Real-time data
config["online_tools"] = False # Cached historical data
```

- **Online Mode**: Uses real-time APIs for current market data
- **Offline Mode**: Uses cached data from TradingDB for backtesting

### LLM Selection
```python
quick_thinking_llm  # Used by all analysts (fast responses)
deep_thinking_llm   # Reserved for complex reasoning tasks
```

## Integration with Trading Pipeline

### Data Flow
```
1. User Input (Ticker + Date)
    ↓
2. Parallel Analyst Execution
    ├── Market Analyst → Technical Report
    ├── Fundamentals Analyst → Financial Report
    ├── News Analyst → News Report
    └── Social Media Analyst → Sentiment Report
    ↓
3. Reports Aggregation
    ↓
4. Research Team Analysis (Bull/Bear Debate)
    ↓
5. Trading Decision
```

### State Management
Each analyst updates the shared `AgentState` with:
- `messages`: Tool calls and responses
- `[analyst]_report`: Their specific analysis report
- Additional domain-specific fields

## Best Practices

### 1. Analyst Selection
Choose analysts based on trading strategy:
- **Day Trading**: Focus on market and social media analysts
- **Value Investing**: Prioritize fundamentals analyst
- **News Trading**: Emphasize news and social media analysts
- **Comprehensive**: Use all four analysts

### 2. Performance Optimization
- Use `gpt-4o-mini` for cost-effective testing
- Enable parallel execution for faster analysis
- Cache frequently accessed data in offline mode

### 3. Report Quality
Each analyst is instructed to:
- Avoid generic statements like "trends are mixed"
- Provide specific, actionable insights
- Include quantitative metrics where possible
- Structure findings in organized tables

## Example Usage

```python
from tradingagents.graph.trading_graph import TradingAgentsGraph

# Configure analysts
selected_analysts = ["market", "fundamentals", "news", "social"]

# Initialize graph with selected analysts
ta = TradingAgentsGraph(
    selected_analysts=selected_analysts,
    debug=True,
    config=config
)

# Run analysis
state, decision = ta.propagate("AAPL", "2024-05-10")

# Access individual reports
market_report = state["market_report"]
fundamentals_report = state["fundamentals_report"]
news_report = state["news_report"]
sentiment_report = state["sentiment_report"]
```

## Technical Implementation Details

### Prompt Engineering
Each analyst uses a sophisticated prompt template that:
1. Defines their role and expertise
2. Specifies available tools
3. Provides analysis guidelines
4. Requests structured output format

### Tool Binding
```python
chain = prompt | llm.bind_tools(tools)
result = chain.invoke(state["messages"])
```
The LangChain framework handles:
- Automatic tool selection
- Parameter extraction
- Error handling
- Response formatting

### Report Extraction
Reports are extracted from tool call results:
```python
if len(result.tool_calls) == 0:
    report = result.content  # Direct response
else:
    report = ""  # Populated by tool execution
```

## Extensibility

### Adding New Analysts
1. Create new file in `tradingagents/agents/analysts/`
2. Implement `create_[analyst_name]_analyst` function
3. Define specialized tools and prompts
4. Update graph setup to include new analyst
5. Add corresponding state fields

### Custom Tools
New data sources can be integrated by:
1. Adding tool functions to `Toolkit` class
2. Configuring online/offline variants
3. Binding to appropriate analysts
4. Handling tool responses in state

## Conclusion

The analyst process forms the foundation of TradingAgents' market intelligence gathering. By running specialized analysts in parallel, the system achieves comprehensive market coverage while maintaining computational efficiency. Each analyst's focused expertise ensures deep, actionable insights that feed into the subsequent research and trading decision phases.