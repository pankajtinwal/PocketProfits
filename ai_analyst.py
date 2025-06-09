"""
AI Stock Analysis module for Finance Bot.
Uses Gemini to analyze stock data and provide insights.
"""

import os
import google.generativeai as genai
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# Configure Gemini
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# Initialize the model
model = genai.GenerativeModel('gemini-2.0-flash')

def format_to_crores(number, currency='INR'):
    """Formats a large number into Crores if currency is INR."""
    if currency == 'INR' and number is not None and isinstance(number, (int, float)):
        if number >= 10000000:
            return f"{number / 10000000:.2f} Cr."
        elif number >= 100000:
            return f"{number / 100000:.2f} Lakh"
    if isinstance(number, (int, float)):
        return f"{number:,}" # Add commas for other large numbers
    return str(number) # Return as string if not a number or not INR

# System prompt for stock analysis
STOCK_ANALYSIS_PROMPT = """
a) You are a financial analyst who is reviewing the *basic overview* of a company. 
b) This includes its name, ticker, current stock price, market cap, sector, industry, country, website, and business summary, you have to analyze
it and provide a short and sharp analysis of the stock's general standing. 
c) You also have data like 52-week highs and lows, PE ratio, PB ratio, average trading volume, and major holders.

d) Using this data:
1. Give a short and sharp analysis of the stock's general standing.
2. Highlight the market cap class (small-cap, mid-cap, large-cap) based on the currency.
3. Briefly assess how its price metrics (PE, PB) compare to sector norms if they look high or low.
4. Do not go deep into profitability or balance sheet health — that is for the next steps.
5. NEVER conclude the full analysis. Just end by teasing the next step.
6. Always mention the company website in your analysis at last in the answer if there is any.
7. Where relevant, briefly add any useful insights beyond the provided data.
8. Structure the answer in NUMBERED bullet points. Keep each point concise. Use a) b) c) etc. for sub-points.
9. Give one line space between each SUB-BULLET point, If you haven't already done so.
10. Use financial emojis to make the analysis more engaging.

✅ Provide a thorough and insightful analysis. Aim for a detailed response, typically between 1500 and 3500 characters, ensuring it stays under the 4000 character limit for Telegram.  
✅ End with a one-liner that says what the user will analyze in **Step 2: Detailed Financials & Ratios**.


Here's the stock data:
"""

# System prompt for detailed financial statement analysis (Step 2)
FINANCIAL_STATEMENT_ANALYSIS_PROMPT = """
a) You are analyzing the *income statements and key financial ratios* of a company. 
b) This includes annual and quarterly data for revenue, gross profit, net income, EBIT. 
c) Also includes Return on Equity, Return on Assets, profit margins, debt-to-equity ratio, current ratio, and insider/institutional holdings.
d) Your task:
1. Identify how revenue and net income trends have moved over years and recent quarters.
2. Mention if margins are strong or weak, and whether the company is improving.
3. Talk about capital structure and balance of debt.
4. Assess if ratios indicate profitability and financial efficiency.
5. Do not dive into total assets, liabilities, or cash flow as that is the next step.
6. Do not conclude. Just leave the user looking forward to Step 3.
7. Where relevant, briefly add any useful insights beyond the provided data.
8. Structure the answer in NUMBERED bullet points. Keep each point concise. Use a) b) c) etc. for sub-points, with one line of space between each.
9. Use financial emojis to make the analysis more engaging.

✅ Provide a thorough and insightful analysis. Aim for a detailed response, typically between 1500 and 3500 characters, ensuring it stays under the 4000 character limit for Telegram.  
✅ End with a one-liner that says Step 3 will analyze **Balance Sheet and Cash Flow Health.**


Here is the detailed financial report for the company:
"""

# System prompt for Balance Sheet and Cash Flow analysis (Step 3)
STEP3_BALANCE_SHEET_CASH_FLOW_ANALYSIS_PROMPT = """
a) You are evaluating the *balance sheet and cash flow statement* of a company. 
b) This includes data for Total Assets, Liabilities, Equity, Cash & Equivalents, Short/Long Term Debt, Net Debt, Operating/Investing/Financing cash flow, Capital Expenditures, and Free Cash Flow for recent years.
c) Your job:
1. Judge the company is financial health — asset base vs liabilities.
2. Highlight debt burden and liquidity safety.
3. Point out trends in cash flow from operations — is the company consistently generating cash?
4. Comment on CapEx vs Free Cash Flow and whether the firm is cash-rich or cash-strapped.
5. Do not summarize or provide a final investment decision.
6. Do not calculate debt to equity ratio with the help of data provided.
7. Where relevant, briefly add any useful insights beyond the provided data.
8. Structure the answer in NUMBERED bullet points. Keep each point concise. Use a) b) c) etc. for sub-points, with one line of space between each.
9. Use financial emojis to make the analysis more engaging.

✅ Provide a thorough and insightful analysis. Aim for a detailed response, typically between 1500 and 3500 characters, ensuring it stays under the 4000 character limit for Telegram.  
✅ End with a teaser like: "Final insights and verdict will follow in the concluding step."


Here is the Balance Sheet and Cash Flow Statement data for the company:
"""

# System prompt for Final Summary Analysis (Step 4)
FINAL_SUMMARY_ANALYSIS_PROMPT = """

Core Instructions:
a) You are concluding a full 3-step fundamental analysis of a company. 
b) You've seen the stock's overview, financial statements, key ratios, balance sheet, and cash flows. 
c) Now your task is to give a clear and practical assessment based on everything observed earlier.
d) Structure the answer in numbered bullet points. Keep points concise. Use a), b), c) etc. for sub-points, with one line of space between each.
e) Instructions:
1. List UP TO five key Strengths of the company. Strenghts should only be based on the provided data snippets. DON'T MAKE ASSUMPTIONS.
2. List UP TO five key Weaknesses of the company. Weaknesses should only be based on the provided data snippets. DON'T MAKE ASSUMPTIONS.
3. Give a ginal OVERALL RATING of the company out of 10 based on the industry future, financial health etc. and be BRUTALLY HONEST, don't SUGARCOAT and TRY TO BE GOOD.
4. IGNORE the debt level of the company for final analysis.

Additional Guidelines:
- Be sharp and confident — don't be vague or diplomatic.
- Don't repeat info from earlier steps unless necessary to support a point.
- Wrap it up WITHOUT SUGARCOATING — make it feel like a proper analyst's closure.

✅ Provide a thorough and insightful analysis. Aim for a detailed response, typically between 1500 and 3500 characters, ensuring it stays under the 4000 character limit for Telegram.
✅ Use simple headers like `✅ Strengths`, `⚠️ Weaknesses`, and `📊 Ratings`.
"""


async def get_step1_overview_analysis(stock_overview_data):
    """
    Get AI analysis of stock data using Gemini.
    
    Args:
        stock_overview_data (dict): Stock overview data from stock_analyzer.analyze_stock
        
    Returns:
        dict: Analysis result
    """
    try:
        # Prepare data for Gemini
        analysis_prompt = STOCK_ANALYSIS_PROMPT
        
        # Use stock data directly without reformatting
        data = stock_overview_data['data']
        
        # Convert to string representation for Gemini
        stock_info = f"""
Stock Data Overview:
------------------
Name: {data['name']}
Ticker: {data['ticker']}
Current Price: {data['current_price']} {data['currency']}
Market Cap: {format_to_crores(data.get('market_cap'), data.get('currency'))}
52-Week Range: {data['52_week_low']} - {data['52_week_high']}
PE Ratio: {data['pe_ratio']}
PB Ratio: {data['pb_ratio']}
Average Volume: {format_to_crores(data.get('avg_volume'), data.get('currency'))}
Sector: {data['sector']}
Industry: {data['industry']}
Country: {data['country']}
Website: {data['website']}

Business Summary: 
{data['business_summary']}
        """
        
        # Send to Gemini
        response = await model.generate_content_async(analysis_prompt + stock_info)
        
        return {
            'success': True,
            'analysis': response.text,
            'stock_name': data['name'],
            'ticker': data['ticker']
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

async def get_step2_financial_analysis(formatted_financial_report, stock_name, ticker):
    """
    Get AI analysis of detailed financial report using Gemini.

    Args:
        formatted_financial_report (str): The formatted string of financial data.
        stock_name (str): Name of the stock.
        ticker (str): Ticker symbol of the stock.

    Returns:
        dict: Analysis result.
    """
    try:
        # Ensure the prompt clearly states it's for the provided company
        prompt_with_context = f"Company: {stock_name} ({ticker})\n\n{formatted_financial_report}"
        full_prompt = FINANCIAL_STATEMENT_ANALYSIS_PROMPT + "\n\n" + prompt_with_context
        
        response = await model.generate_content_async(full_prompt)
        
        return {
            'success': True,
            'analysis': response.text,
            'stock_name': stock_name,
            'ticker': ticker
        }

    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'stock_name': stock_name,
            'ticker': ticker
        }

async def get_step3_financial_analysis(formatted_step3_report, stock_name, ticker):
    """
    Get AI analysis of Step 3 (Balance Sheet & Cash Flow) financial report using Gemini.

    Args:
        formatted_step3_report (str): The formatted string of balance sheet and cash flow data.
        stock_name (str): Name of the stock.
        ticker (str): Ticker symbol of the stock.

    Returns:
        dict: Analysis result.
    """
    try:
        # Ensure the prompt clearly states it's for the provided company
        prompt_with_context = f"Company: {stock_name} ({ticker})\n\n{formatted_step3_report}"
        full_prompt = STEP3_BALANCE_SHEET_CASH_FLOW_ANALYSIS_PROMPT + "\n\n" + prompt_with_context
        
        response = await model.generate_content_async(full_prompt)
        
        return {
            'success': True,
            'analysis': response.text,
            'stock_name': stock_name,
            'ticker': ticker
        }

    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'stock_name': stock_name,
            'ticker': ticker
        }

async def get_final_summary_analysis(stock_name, ticker):
    """
    Get a final AI summary analysis for the stock using Gemini,
    based on all previously discussed information in the conversation.

    Args:
        stock_name (str): Name of the stock.
        ticker (str): Ticker symbol of the stock.

    Returns:
        dict: Analysis result.
    """
    try:
        # The prompt will be formatted with the stock name and ticker
        # to help Gemini focus on the correct entity in the conversation history.
        prompt_content = FINAL_SUMMARY_ANALYSIS_PROMPT.format(stock_name=stock_name, ticker=ticker)
        
        # Send to Gemini. Gemini is expected to use the conversation history.
        response = await model.generate_content_async(prompt_content)
        
        return {
            'success': True,
            'analysis': response.text,
            'stock_name': stock_name,
            'ticker': ticker
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'stock_name': stock_name,
            'ticker': ticker
        }

import re

def format_ai_analysis(analysis_result):
    """
    Format the AI analysis result into a readable message, improving Markdown.
    
    Args:
        analysis_result (dict): Result from AI analysis functions.
        
    Returns:
        str: Formatted message for Telegram.
    """
    if not analysis_result.get('success', False):
        error_msg = analysis_result.get('error', 'Unknown error.')
        stock_info = ""
        if 'stock_name' in analysis_result and 'ticker' in analysis_result:
            stock_info = f" for {analysis_result.get('stock_name', 'N/A')} ({analysis_result.get('ticker', 'N/A')})"
        return f"❌ *Error*: Could not generate AI analysis{stock_info}. Details: {error_msg}"

    analysis_text = analysis_result.get('analysis', '')

    # Aggressive sanitization to prevent parsing errors:
    # Remove backticks, all asterisks, and all underscores first.
    analysis_text = analysis_text.replace('`', '')
    analysis_text = analysis_text.replace('*', '') # Remove all asterisks
    analysis_text = analysis_text.replace('_', '') # Remove all underscores
    # Replace standalone square brackets (less likely to cause parsing errors but good for consistency)
    analysis_text = analysis_text.replace('[', '(').replace(']', ')') 

    # Bold all numbers (integers, decimals, including those with commas)
    analysis_text = re.sub(r'(\b\d{1,3}(?:,\d{3})*(?:\.\d+)?\b|\b\d+(?:\.\d+)?\b)', r'*\1*', analysis_text)

    lines = analysis_text.split('\n')
    processed_lines = []
    
    headings_to_bold = [
        "✅ Strengths", "Strengths:",
        "⚠️ Weaknesses", "Weaknesses:",
        "📊 Ratings", "Ratings:",
        "Overall Assessment:", "Key Highlights:", "Analysis:", "Summary:",
        "Fundamental Quality:", "Financial Health:", "Overall Stock Quality:",
        "Stock Data Overview:", "Business Summary:"
    ]

    for line in lines:
        stripped_line = line.strip()
        if stripped_line: # Process non-empty lines
            made_bold = False
            for heading_keyword in headings_to_bold:
                # Check if the line starts with the heading keyword (case-insensitive)
                if stripped_line.lower().startswith(heading_keyword.lower()):
                    # Since all '*' were removed, we just add them back for our headings
                    processed_lines.append(f"*{stripped_line}*")
                    made_bold = True
                    break
            if not made_bold:
                # Check if the line is a numbered or lettered list item and bold it
                if re.match(r"^\s*([\d\w]+[\.\)])\s+", stripped_line):
                    processed_lines.append(f"*{line.strip()}*") # Bold the stripped line to avoid leading/trailing whitespace issues with bolding
                else:
                    processed_lines.append(line) # Keep original line (now without any '*' or '_')
        else:
            processed_lines.append(line) # Keep empty lines for spacing
    
    analysis_text = "\n".join(processed_lines)

    # Add some padding around the main analysis text
    analysis_text = "\n" + analysis_text.strip() + "\n"

    # Character limit (prompts ask for <4000). This is a pre-split trim.
    if len(analysis_text) > 3900: 
        analysis_text = analysis_text[:3850] + "\n... (trimmed for length)"

    stock_name = analysis_result.get('stock_name', 'N/A')
    ticker = analysis_result.get('ticker', 'N/A')
    
    # Removed the disclaimer note
    message = f"""🧠 *AI Analysis: {stock_name} ({ticker})*
{analysis_text}"""
    return message

# This function has been removed as we're now using a direct flow approach
