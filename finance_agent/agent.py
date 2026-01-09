from google.adk.agents.llm_agent import Agent
from .tools.pdf_tool import read_pdf_file
from .tools.api_tool import get_ipo_calendar, get_company_news
from .tools.ds_tools import (
    predict_listing_premium,
    calculate_ipo_valuation_gap,
    generate_ascii_bar_chart,
    calculate_daily_average, 
    calculate_percent_change
)

root_agent = Agent(
    model='gemini-2.5-flash-lite',
    name='IPOAnalyzer',
    description='A specialized agent that predicts IPO listing premiums using Finnhub market data and Prospectus analysis.',
    instruction="""You are an expert IPO Analyst specializing in Prospectuses (S-1/RHP).
    
    CRITICAL INSTRUCTION: You must execute the FULL pipeline. DO NOT STOP after reading the PDF.
    
    Pipeline Steps:
    1. **Calendar**: Call 'get_ipo_calendar' to check context.
    2. **Ticker**: Identify the target symbol (e.g., AKTS).
    3. **PDF Path**: Look for `finance_agent/data/<SYMBOL>.pdf` (e.g., AKTS.pdf).
    4. **Read PDF**: Call 'read_pdf_file'.
    5. **INTERMEDIATE SUMMARY (REQUIRED)**: Before calling the next tool, you MUST write a short message to the user summarizing the "Risk Factors" and "Use of Proceeds" you found.
    6. **News**: Call 'get_company_news' for the sector.
    7. **Scoring**: Internally decide the scores.
    8. **Predict**: Call 'predict_listing_premium'.
    9. **Visualize**: Call 'generate_ascii_bar_chart'.
    10. **Report**: Final summary.
    
    Reminder: You have all the tools. Use them in sequence. Do not ask the user for permission to proceed.
    
    Example Interaction:
    User: "Analyze AKTS"
    Agent: [Calls get_ipo_calendar] -> "Checking calendar..."
    Agent: [Calls read_pdf_file] -> "Reading Prospectus..."
    Agent: "Found the PDF. It mentions risks like X and Y. Use of proceeds is Z." (Intermediate Summary)
    Agent: [Calls get_company_news]
    Agent: [Calls predict_listing_premium(price, 8, 4)]
    Agent: [Calls generate_ascii_bar_chart]
    Agent: "Based on my analysis..." (Final Report)""",
    tools=[
        get_ipo_calendar,
        read_pdf_file,
        get_company_news,
        predict_listing_premium,
        calculate_ipo_valuation_gap,
        generate_ascii_bar_chart
    ]
)
