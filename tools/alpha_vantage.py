import requests
from typing import Dict, Optional
from config import config

class AlphaVantageTool:
    """Tool for fetching financial data from Alpha Vantage API"""
    
    def __init__(self):
        self.api_key = config.ALPHA_VANTAGE_KEY
        self.base_url = config.ALPHA_VANTAGE_BASE_URL
        self.usd_to_inr = config.USD_TO_INR_RATE
    
    def _format_price(self, usd_price: str) -> str:
        """Convert USD price to INR and format as '₹INR (USD $amount)'"""
        try:
            usd_val = float(usd_price)
            inr_val = usd_val * self.usd_to_inr
            return f"₹{inr_val:,.2f} (USD ${usd_val:,.2f})"
        except (ValueError, TypeError):
            return usd_price
    
    def get_stock_quote(self, symbol: str) -> Optional[Dict]:
        """
        Get real-time stock quote for a given symbol
        
        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL', 'TSLA')
        
        Returns:
            Dictionary with stock data or None if error
        """
        if not self.api_key:
            return {"error": "Alpha Vantage API key not configured"}
        
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": self.api_key
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if "Global Quote" in data and data["Global Quote"]:
                quote = data["Global Quote"]
                price_usd = quote.get("05. price", "N/A")
                change_usd = quote.get("09. change", "N/A")
                
                return {
                    "symbol": quote.get("01. symbol", symbol),
                    "price": self._format_price(price_usd),
                    "change": self._format_price(change_usd) if change_usd != "N/A" else "N/A",
                    "change_percent": quote.get("10. change percent", "N/A"),
                    "latest_trading_day": quote.get("07. latest trading day", "N/A"),
                    "source": "Alpha Vantage - Market Data (INR)"
                }
            else:
                return {"error": f"No data found for symbol {symbol}"}
        
        except Exception as e:
            return {"error": f"Alpha Vantage API error: {str(e)}"}
    
    def get_commodity_price(self, commodity: str) -> Optional[Dict]:
        """
        Get commodity prices (e.g., gold, silver, oil)
        Note: Alpha Vantage has limited commodity support
        
        Args:
            commodity: Commodity symbol (e.g., 'GOLD', 'SILVER')
        
        Returns:
            Dictionary with commodity data or None if error
        """
        # Map common commodity names to ticker symbols
        commodity_map = {
            "gold": "GLD",  # SPDR Gold Shares ETF
            "silver": "SLV",  # iShares Silver Trust
            "oil": "USO",  # United States Oil Fund
        }
        
        symbol = commodity_map.get(commodity.lower(), commodity.upper())
        return self.get_stock_quote(symbol)
    
    def get_forex_rate(self, from_currency: str, to_currency: str) -> Optional[Dict]:
        """
        Get foreign exchange rate
        
        Args:
            from_currency: Base currency code (e.g., 'USD')
            to_currency: Target currency code (e.g., 'EUR')
        
        Returns:
            Dictionary with forex data or None if error
        """
        if not self.api_key:
            return {"error": "Alpha Vantage API key not configured"}
        
        params = {
            "function": "CURRENCY_EXCHANGE_RATE",
            "from_currency": from_currency.upper(),
            "to_currency": to_currency.upper(),
            "apikey": self.api_key
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if "Realtime Currency Exchange Rate" in data:
                rate_data = data["Realtime Currency Exchange Rate"]
                from_curr = rate_data.get("1. From_Currency Code", from_currency)
                to_curr = rate_data.get("3. To_Currency Code", to_currency)
                rate = rate_data.get("5. Exchange Rate", "N/A")
                
                # Format rate with INR conversion if USD is involved
                formatted_rate = rate
                if "USD" in [from_curr, to_curr] and rate != "N/A":
                    formatted_rate = self._format_price(rate)
                
                return {
                    "from": from_curr,
                    "to": to_curr,
                    "rate": formatted_rate,
                    "last_refreshed": rate_data.get("6. Last Refreshed", "N/A"),
                    "source": "Alpha Vantage - Forex Data (INR)"
                }
            else:
                return {"error": f"No forex data found for {from_currency}/{to_currency}"}
        
        except Exception as e:
            return {"error": f"Alpha Vantage API error: {str(e)}"}
    
    def search_financial_data(self, query: str) -> Optional[Dict]:
        """
        Generic search method that tries to interpret the query
        and fetch relevant financial data
        
        Args:
            query: Natural language query about financial data
        
        Returns:
            Dictionary with relevant financial data
        """
        query_lower = query.lower()
        
        # Check for commodity keywords
        if "gold" in query_lower:
            return self.get_commodity_price("gold")
        elif "silver" in query_lower:
            return self.get_commodity_price("silver")
        elif "oil" in query_lower:
            return self.get_commodity_price("oil")
        
        # Check for common stock symbols
        common_stocks = ["aapl", "tsla", "googl", "msft", "amzn", "meta", "nvda"]
        for stock in common_stocks:
            if stock in query_lower:
                return self.get_stock_quote(stock.upper())
        
        # Default: try to extract a symbol from the query
        words = query.split()
        for word in words:
            if word.isupper() and len(word) <= 5:  # Likely a ticker symbol
                return self.get_stock_quote(word)
        
        return {"error": "Could not interpret financial query"}
