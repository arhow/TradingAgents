from tradingagents.graph.aseries_trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# akshare https://github.com/akfamily/akshare
# https://tushare.pro/user/token
# https://github.com/jealous/stockstats
# https://finnhub.io/dashboard
# https://tsanghi.com/fin/index
# openBB

# Create a custom config
config = DEFAULT_CONFIG.copy()
# config["llm_provider"] = "google"  # Use a different model
# config["backend_url"] = "https://generativelanguage.googleapis.com/v1"  # Use a different backend
config["deep_think_llm"] = "gpt-5"  # Use a different model
config["quick_think_llm"] = "gpt-5"  # Use a different model
config["max_debate_rounds"] = 1  # Increase debate rounds
config["online_tools"] = True  # Use online tools for Tushare data

# Initialize with custom config
ta = TradingAgentsGraph(debug=True, config=config)

# forward propagate
_, decision = ta.propagate("300418.SZ", '昆仑万维', "2025-09-21")
print(decision)

# Memorize mistakes and reflect
# ta.reflect_and_remember(1000) # parameter is the position returns
