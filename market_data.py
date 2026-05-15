import yfinance as yf
import requests

# Note: Get a free API key at https://finnhub.io/
FINNHUB_API_KEY = "d822s7hr01qrojfdpjpgd822s7hr01qrojfdpjq0"

def get_fundamentals(symbol):
    try:
        if symbol.endswith(".NS"):
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # 1. Get raw value
            raw_div = info.get("dividendYield") 
            
            # 2. Normalize Indian Yield (TCS Fix)
            # If yfinance gives a large number like 4.7, it's a percentage. 
            # If it's over 100, it's likely a data error or dividend amount, so we cap it.
            if raw_div:
                if raw_div > 1: # It's already in percentage form (e.g., 4.79)
                    div_yield = raw_div / 100
                else: # It's in decimal form (e.g., 0.0479)
                    div_yield = raw_div
            else:
                div_yield = 0
                
            return {
                "pe_ratio": info.get("trailingPE", "N/A"),
                "52_week_high": info.get("fiftyTwoWeekHigh", "N/A"),
                "52_week_low": info.get("fiftyTwoWeekLow", "N/A"),
                "dividend_yield": div_yield # Store as decimal (0.0479)
            }
        
        else:
            url = f"https://finnhub.io/api/v1/stock/metric?symbol={symbol}&metric=all&token={FINNHUB_API_KEY}"
            r = requests.get(url)
            data = r.json()
            if 'metric' in data:
                m = data['metric']
                # Finnhub US yield is usually a percentage (e.g., 1.23) 
                raw_div = m.get('dividendYieldIndicatedAnnual')
                div_yield = (raw_div / 100) if raw_div else 0
                
                return {
                    "pe_ratio": m.get("peBasicExclExtraTTM", "N/A"),
                    "52_week_high": m.get("52WeekHigh", "N/A"),
                    "52_week_low": m.get("52WeekLow", "N/A"),
                    "dividend_yield": div_yield # Store as decimal (0.0123)
                }
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None
    
def get_finnhub_news(symbol):
    """
    Finnhub remains excellent for news headlines across both markets.
    """
    clean_symbol = symbol.replace(".NS", "")
    # Finnhub uses standard ticker symbols for global news
    url = f"https://finnhub.io/api/v1/company-news?symbol={clean_symbol}&from=2024-01-01&to=2026-05-13&token={FINNHUB_API_KEY}"
    
    try:
        r = requests.get(url)
        data = r.json()
        headlines = [article['headline'] for article in data[:10] if 'headline' in article]
        return headlines
    except:
        return []