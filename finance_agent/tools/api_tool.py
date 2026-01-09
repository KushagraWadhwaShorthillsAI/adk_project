import requests
import os
from dotenv import load_dotenv

load_dotenv()

IPOALERTS_API_KEY = os.getenv("IPOALERTS_API_KEY")
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")

def get_ipo_calendar():
    """
    Fetches the IPO calendar for the upcoming month from Finnhub.
    Includes ticker, expected date, and price range.
    """
    if not FINNHUB_API_KEY:
        return "Error: FINNHUB_API_KEY not found."
    
    import datetime
    today = datetime.date.today().strftime('%Y-%m-%d')
    next_month = (datetime.date.today() + datetime.timedelta(days=30)).strftime('%Y-%m-%d')
    
    url = f"https://finnhub.io/api/v1/calendar/ipo?from={today}&to={next_month}&token={FINNHUB_API_KEY}"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if 'ipoCalendar' not in data or not data['ipoCalendar']:
            return "No upcoming IPOs found for the next 30 days."
            
        summary = []
        for ipo in data['ipoCalendar'][:5]: # Show top 5
            name = ipo.get('name', 'N/A')
            symbol = ipo.get('symbol', 'N/A')
            date = ipo.get('date', 'N/A')
            price = f"${ipo.get('price', 'N/A')}"
            summary.append(f"{name} ({symbol}) - Date: {date}, Expected Price: {price}")
            
        return "\n".join(summary)
    except Exception as e:
        return f"Error fetching IPO calendar: {str(e)}"

def get_company_news(symbol: str):
    """
    Fetches the latest company news headlines for a given stock ticker.
    
    Args:
        symbol: The stock ticker symbol.
    """
    if not FINNHUB_API_KEY:
        return "Error: FINNHUB_API_KEY not found."
    
    import datetime
    # Get news from the last 7 days
    today = datetime.date.today().strftime('%Y-%m-%d')
    last_week = (datetime.date.today() - datetime.timedelta(days=7)).strftime('%Y-%m-%d')
    
    url = f"https://finnhub.io/api/v1/company-news?symbol={symbol.upper()}&from={last_week}&to={today}&token={FINNHUB_API_KEY}"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if not data:
            return "No recent news found for this symbol."
            
        # Return only the top 5 headlines to save context space
        headlines = [news.get('headline') for news in data[:5]]
        return "\n".join(headlines)
    except Exception as e:
        return f"Error fetching news: {str(e)}"
