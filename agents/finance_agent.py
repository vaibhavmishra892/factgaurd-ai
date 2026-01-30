from crewai import Agent, LLM
from crewai.tools import tool
from config import config
from tools.alpha_vantage import AlphaVantageTool

# Initialize Alpha Vantage client
av_client = AlphaVantageTool()

@tool("Financial Data Fetcher")
def fetch_financial_data(query: str) -> str:
    """
    Fetch financial data for stocks, forex, or commodities.
    
    Input should be one of:
    - Stock symbol like 'AAPL', 'MSFT', 'TSLA'
    - Commodity like 'GOLD', 'SILVER', 'OIL'
    - Forex pair like 'EUR/USD', 'GBP/USD'
    """
    query_upper = query.upper().strip()
    
    if query_upper in ['GOLD', 'SILVER', 'OIL', 'PLATINUM', 'COPPER']:
        commodity_symbols = {
            'GOLD': 'XAU', 'SILVER': 'XAG', 'OIL': 'BRENT',
            'PLATINUM': 'XPT', 'COPPER': 'XCU'
        }
        symbol = commodity_symbols.get(query_upper, query_upper)
        result = av_client.get_forex_rate(symbol, 'USD')
    elif '/' in query_upper:
        parts = query_upper.split('/')
        result = av_client.get_forex_rate(parts[0], parts[1])
    else:
        result = av_client.get_stock_quote(query_upper)
    
    if 'error' in result:
        return f"Error fetching data for {query}: {result['error']}"
    
    return str(result)


def create_finance_agent() -> Agent:
    """Create the Finance Agent for verifying financial claims."""
    
    llm = LLM(
        model=config.LLM_MODEL,
        api_key=config.CEREBRAS_API_KEY,
        base_url=config.CEREBRAS_BASE_URL,
        temperature=config.LLM_TEMPERATURE,
        timeout=300,
        max_retries=3
    )
    
    return Agent(
        role="Financial Data Analyst",
        goal="Verify financial and market-related claims using reliable data sources",
        backstory="""You are a financial analyst specializing in fact-checking market claims.
        
        Your expertise includes:
        - Stock prices and market data
        - Commodity prices (gold, silver, oil)
        - Currency exchange rates
        - Financial news and announcements
        
        CRITICAL EVIDENCE USAGE RULES:
        - Only cite sources that DIRECTLY provide the data point in question
        - For price claims: cite exact figures from authoritative sources only
        - Do NOT use tangential market articles as evidence for specific price claims
        - If data is unavailable, state: "Current market data does not confirm this figure"
        - Distinguish between:
          * Direct data: "Gold was $2,500/oz on [date]"
          * Context only: "Article discusses gold prices generally" (not evidence)
        
        Remember:
        - Financial claims are often time-sensitive
        - Always note the date/time of data
        - Use authoritative financial sources only""",
        verbose=True,
        allow_delegation=False,
        max_iter=5,
        llm=llm
    )
