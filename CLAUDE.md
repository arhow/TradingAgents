# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TradingAgents is a multi-agent LLM financial trading framework built with LangGraph. It simulates real-world trading firms by deploying specialized AI agents (analysts, researchers, traders, risk managers) that collaboratively evaluate market conditions and make trading decisions.

## Key Architecture Components

### Agent Hierarchy
The system uses a multi-tiered agent architecture coordinated through `tradingagents/graph/trading_graph.py`:

1. **Analyst Team** (`tradingagents/agents/analysts/`)
   - Market Analyst: Technical analysis with indicators
   - Fundamentals Analyst: Company financials evaluation
   - News Analyst: Global news and macroeconomic analysis
   - Social Media Analyst: Sentiment analysis from social platforms

2. **Research Team** (`tradingagents/agents/researchers/`)
   - Bull Researcher: Optimistic market perspective
   - Bear Researcher: Pessimistic market perspective
   - Debate through structured discussions to balance views

3. **Trading & Risk Management**
   - Trader (`tradingagents/agents/trader/`): Makes trading decisions based on aggregated insights
   - Risk Managers (`tradingagents/agents/risk_mgmt/`): Conservative, Neutral, and Aggressive debators
   - Research Manager (`tradingagents/agents/managers/`): Coordinates research activities

### Data Flow Architecture
- **Data Sources** (`tradingagents/dataflows/`): Integrates FinnHub, Yahoo Finance, Reddit, Google News
- **State Management**: Uses LangGraph's state system with `AgentState`, `InvestDebateState`, `RiskDebateState`
- **Memory System** (`tradingagents/agents/utils/memory.py`): `FinancialSituationMemory` for agent learning

### Graph Orchestration
The main orchestration happens through LangGraph in `tradingagents/graph/`:
- `trading_graph.py`: Main entry point and graph construction
- `setup.py`: Graph component initialization
- `propagation.py`: Forward propagation logic
- `conditional_logic.py`: Decision routing between agents
- `reflection.py`: Learning from past decisions

## Common Development Commands

### Running the Application

```bash
# Main script execution
python main.py

# CLI interface
python -m cli.main
```

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Or using setup.py
pip install -e .
```

### Required Environment Variables

```bash
export FINNHUB_API_KEY=$YOUR_FINNHUB_API_KEY  # Required for financial data
export OPENAI_API_KEY=$YOUR_OPENAI_API_KEY    # Required for OpenAI models
# For other providers:
# export ANTHROPIC_API_KEY for Anthropic models
# export GOOGLE_API_KEY for Google models
```

## Configuration

The main configuration is in `tradingagents/default_config.py`:

- **LLM Settings**:
  - `llm_provider`: "openai", "anthropic", "google", "ollama", "openrouter"
  - `deep_think_llm`: Model for complex reasoning (default: "o4-mini")
  - `quick_think_llm`: Model for fast decisions (default: "gpt-4o-mini")
  - `backend_url`: API endpoint

- **Trading Parameters**:
  - `max_debate_rounds`: Number of debate rounds between researchers
  - `max_risk_discuss_rounds`: Risk assessment discussion rounds
  - `online_tools`: Use real-time data (True) or cached data (False)

## Key Implementation Patterns

### Creating Custom Agents
Agents inherit from base classes and implement specific analysis methods. They use LangChain tools and structured prompts for decision-making.

### Using the TradingAgentsGraph
```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

config = DEFAULT_CONFIG.copy()
config["llm_provider"] = "openai"
config["deep_think_llm"] = "gpt-4"
ta = TradingAgentsGraph(debug=True, config=config)
_, decision = ta.propagate("NVDA", "2024-05-10")
```

### Memory and Reflection
The system includes a reflection mechanism for learning from past trades:
```python
ta.reflect_and_remember(position_returns)  # Learn from trading outcomes
```

## Important Notes

- The framework makes extensive API calls - use cheaper models (gpt-4o-mini, o4-mini) for testing
- Results are saved to `./results` directory (configurable via `TRADINGAGENTS_RESULTS_DIR`)
- Data cache is stored in `tradingagents/dataflows/data_cache/`
- The system is designed for research purposes, not production trading
- CLI provides an interactive interface with real-time status updates of all agents


## Standard Workflow

1. First think through the problem, read the codebase for relevant files, and write a plan to tasks/todo.md.
2. The plan should have a list of todo items that you can check off as you complete them
3. Before you begin working, check in with me and I will verify the plan.
4. Then, begin working on the todo items, marking them as complete as you go.
5. Please every step of the way just give me a high level explanation of what changes you made
6. Make every task and code change you do as simple as possible. We want to avoid making any massive or complex changes. Every change should impact as little code as possible. Everything is about simplicity.
7. Finally, add a review section to the todo.md file with a summary of the changes you made and any other relevant information.