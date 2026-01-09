import math

def calculate_daily_average(high, low):
    """
    Calculates the simple average price of the day.
    
    Args:
        high: The day's high price.
        low: The day's low price.
    """
    return round((high + low) / 2, 2)

def calculate_percent_change(current, previous):
    """
    Standard DS function to calculate percentage growth or decline.
    """
    if previous == 0: return 0
    change = ((current - previous) / previous) * 100
    return round(change, 2)

def simple_valuation(eps, pe_ratio):
    """
    A basic valuation tool: Price = Earnings * Multiplier.
    
    Args:
        eps: Earnings Per Share from PDF.
        pe_ratio: A multiplier (e.g., 15 for average stocks).
    """
    return round(eps * pe_ratio, 2)

def calculate_volatility_score(daily_high, daily_low):
    range_pct = (daily_high - daily_low) / daily_low * 100
    if range_pct < 1: return 1
    if range_pct < 3: return 5
    return 10

def predict_listing_premium(expected_price_range: str, market_sentiment_score: int, fundamental_score: int):
    """
    Calculates IPO listing premium based on Agent's qualitative assessment.
    
    Args:
        expected_price_range: String like "$10.00 - $12.00".
        market_sentiment_score: 1-10 Score (1=Bearish, 5=Neutral, 10=Bullish). Based on news.
        fundamental_score: 1-10 Score (1=High Risk/Weak, 10=Solid financials/Low Risk). Based on Prospectus.
    """
    # Normalize scores to -1 to +1 scale relative to neutral (5)
    sentiment_factor = (market_sentiment_score - 5) * 2  # Range: -8 to +10 roughly
    fundamental_factor = (fundamental_score - 5) * 1.5   # Range: -6 to +7.5 (Fundamentals move price less than hype day 1)
    
    total_premium_pct = sentiment_factor + fundamental_factor
    
    # Cap limits for realism
    total_premium_pct = max(-15, min(60, total_premium_pct))
    
    return (f"Predicted Listing Premium: {total_premium_pct:.1f}% over {expected_price_range}\n"
            f"Model Inputs:\n"
            f"- Market Sentiment: {market_sentiment_score}/10 -> {sentiment_factor:+.1f}%\n"
            f"- Fundamental Strength: {fundamental_score}/10 -> {fundamental_factor:+.1f}%")

def calculate_ipo_valuation_gap(ipo_pe, sector_avg_pe):
    gap = ((sector_avg_pe - ipo_pe) / sector_avg_pe) * 100
    if gap > 0:
        return f"IPO is undervalued by {round(gap, 2)}% compared to sector."
    else:
        return f"IPO is overvalued by {round(abs(gap), 2)}% compared to sector."

def generate_ascii_bar_chart(label, percentage, width=20):
    """
    Generates a simple ASCII bar chart for visual representation in chat.
    Example: Sentiment [==========>          ] 50%
    """
    percentage = max(0, min(100, percentage)) # Clamp between 0-100
    filled_width = int((percentage / 100) * width)
    bar = "=" * filled_width + ">" + " " * (width - filled_width)
    return f"{label} [{bar}] {percentage}%"
