"""
Stock analysis functionality for the Finance Bot.
This module handles retrieving and formatting stock data using yfinance.
"""

import yfinance as yf
import pandas as pd

def analyze_stock(ticker_symbol):
    """
    Analyze a stock using yfinance and return fundamental data.
    
    Args:
        ticker_symbol (str): Stock ticker symbol (e.g., 'RELIANCE.NS')
        
    Returns:
        dict: Dictionary containing stock analysis or error message
    """
    try:
        # Get stock data from yfinance
        stock = yf.Ticker(ticker_symbol)
        info = stock.info
        
        # Check if we got valid data
        if 'longName' not in info:
            return {'error': f"Could not find data for ticker '{ticker_symbol}'. Please ensure you've entered a valid ticker symbol."}
        
        # Collect fundamental data
        fundamental_data = {
            'name': info.get('longName', 'N/A'),
            'ticker': ticker_symbol,
            'current_price': info.get('currentPrice', info.get('regularMarketPrice', 'N/A')),
            'currency': info.get('currency', 'INR'),
            'business_summary': info.get('longBusinessSummary', 'N/A'),
            'sector': info.get('sector', 'N/A'),
            'industry': info.get('industry', 'N/A'),
            'website': info.get('website', 'N/A'),
            'founded_year': info.get('startDate', 'N/A'),
            '52_week_low': info.get('fiftyTwoWeekLow', 'N/A'),
            '52_week_high': info.get('fiftyTwoWeekHigh', 'N/A'),
            'pe_ratio': info.get('trailingPE', 'N/A'),
            'pb_ratio': info.get('priceToBook', 'N/A'),
            'market_cap': info.get('marketCap', 'N/A'),
            'avg_volume': info.get('averageVolume', 'N/A'),
            'country': info.get('country', 'India'),
        }
        
        # Try to get institutional holdings
        try:
            institutional_holdings = stock.institutional_holders
            fundamental_data['institutional_holders'] = institutional_holdings
        except:
            fundamental_data['institutional_holders'] = 'N/A'
        
        # Try to get major holders (includes promoter holding)
        try:
            major_holders = stock.major_holders
            fundamental_data['major_holders'] = major_holders
        except:
            fundamental_data['major_holders'] = 'N/A'
            
        return {'success': True, 'data': fundamental_data}
        
    except Exception as e:
        return {'error': f"An error occurred: {str(e)}"}


def format_stock_analysis(analysis_result):
    """
    Format the stock analysis result into a readable message.
    
    Args:
        analysis_result (dict): Result from analyze_stock function
        
    Returns:
        str: Formatted message
    """
    if 'error' in analysis_result:
        return f"❌ *Error*: {analysis_result['error']}"
    
    data = analysis_result['data']
    currency_symbol = '₹' if data['currency'] == 'INR' else '$'
            
    # Format market cap in crores/billions
    market_cap_formatted = "N/A"
    if data['market_cap'] != 'N/A':
        if data['currency'] == 'INR':
            market_cap_cr = data['market_cap'] / 10000000  # Convert to crores
            market_cap_formatted = f"{market_cap_cr:.2f} Cr"
        else:
            market_cap_b = data['market_cap'] / 1000000000  # Convert to billions
            market_cap_formatted = f"{market_cap_b:.2f} B"
    
    message = f"""📊 *Stock Overview: {data['name']} ({data['ticker']})*
------------------------

💰 *Price*: {currency_symbol}{data['current_price']}
🏢 *Market Cap*: {market_cap_formatted}
📈 *52-Week Range*: {currency_symbol}{data['52_week_low']} - {currency_symbol}{data['52_week_high']}
📊 *PE Ratio*: {data['pe_ratio']}
📘 *PB Ratio*: {data['pb_ratio']}
📉 *Avg Volume*: {data['avg_volume']:,}

🔍 *About*:
  • Sector: {data['sector']}
  • Industry: {data['industry']}
  • Country: {data['country']}
  • Website: {data['website']}

📝 *Business Summary*:
{data['business_summary'][:500]}...
"""
    return message

def get_detailed_financials(ticker_symbol):
    """
    Get detailed financial data (income statements) for a stock.
    
    Args:
        ticker_symbol (str): Stock ticker symbol.
        
    Returns:
        dict: Dictionary containing financial data or error message.
    """
    try:
        stock = yf.Ticker(ticker_symbol)
        
        # Get annual income statement (last 4 years)
        annual_financials = stock.financials
        if not annual_financials.empty:
            annual_financials_selected = annual_financials.iloc[:, :4]
        else:
            # Create an empty DataFrame with expected index if data is N/A
            annual_financials_selected = pd.DataFrame(index=['Total Revenue', 'Gross Profit', 'Net Income'])
            
        # Get quarterly income statement (last 4 quarters)
        quarterly_financials = stock.quarterly_financials
        if not quarterly_financials.empty:
            quarterly_financials_selected = quarterly_financials.iloc[:, :4]
        else:
            quarterly_financials_selected = pd.DataFrame(index=['Total Revenue', 'Gross Profit', 'Net Income'])
            
        return {
            'success': True,
            'annual_income_statement': annual_financials_selected,
            'quarterly_income_statement': quarterly_financials_selected,
            'stock_name': stock.info.get('longName', ticker_symbol),
            'ticker': ticker_symbol,
            'currency': stock.info.get('currency', 'N/A'),
            'ratios': {
                'return_on_equity': stock.info.get('returnOnEquity'),
                'return_on_assets': stock.info.get('returnOnAssets'),
                'profit_margin': stock.info.get('profitMargins'),
                'debt_to_equity': stock.info.get('debtToEquity'),
                'current_ratio': stock.info.get('currentRatio'),
                'held_percent_insiders': stock.info.get('heldPercentInsiders'),
                'held_percent_institutions': stock.info.get('heldPercentInstitutions')
            }
        }
        
    except Exception as e:
        return {'success': False, 'error': f"Error fetching detailed financials for {ticker_symbol}: {str(e)}"}

def format_detailed_financials(financial_data):
    """
    Format detailed financial data into a readable Telegram message.
    
    Args:
        financial_data (dict): Data from get_detailed_financials.
        
    Returns:
        str: Formatted message.
    """
    if not financial_data.get('success'):
        return f"❌ *Error*: {financial_data.get('error', 'Could not fetch detailed financials.')}"

    stock_name = financial_data.get('stock_name', 'N/A')
    ticker = financial_data.get('ticker', 'N/A')
    currency = financial_data.get('currency', '')
    currency_symbol = '₹' if currency == 'INR' else ('$' if currency == 'USD' else currency)
    
    message = f"📊 *Detailed Financials: {stock_name} ({ticker})*\n\n"
    message += f"_(All figures in {currency_symbol} unless otherwise noted)_\n\n"

    key_items = ['Total Revenue', 'Gross Profit', 'Net Income', 'EBIT']

    # Format Annual Income Statement
    message += "🗓️ *Annual Income Statement (Last 4 Years)*\n"
    annual_data = financial_data.get('annual_income_statement')
    if isinstance(annual_data, pd.DataFrame) and not annual_data.empty:
        annual_df_filtered = annual_data[annual_data.index.isin(key_items)].reindex(key_items)
        annual_df_filtered.columns = [col.strftime('%Y') if hasattr(col, 'strftime') else str(col) for col in annual_df_filtered.columns]
        
        # Define column width for data
        data_col_width = 15

        formatted_rows = []
        for index, row in annual_df_filtered.iterrows():
            formatted_row = f"{index:<15}" # Item name column
            for val in row:
                if currency == 'INR' and isinstance(val, (int, float)) and not pd.isna(val):
                    val_cr = val / 10000000
                    formatted_val_str = f"{val_cr:,.2f} Cr"
                elif isinstance(val, (int, float)) and not pd.isna(val):
                    formatted_val_str = f"{val:,.0f}"
                else:
                    formatted_val_str = "N/A"
                formatted_row += f" {formatted_val_str:>{data_col_width}}"
            formatted_rows.append(formatted_row)
        
        header_str = "".join([f" {col_name:>{data_col_width}}" for col_name in annual_df_filtered.columns])
        message += f"```\n                 {header_str}\n{'-'* (15 + (data_col_width + 1) * len(annual_df_filtered.columns))}\n"
        message += "\n".join(formatted_rows)
        message += "\n```\n\n"
    else:
        message += "_No annual income statement data available._\n\n"

    # Format Quarterly Income Statement
    message += "📅 *Quarterly Income Statement (Last 4 Quarters)*\n"
    quarterly_data = financial_data.get('quarterly_income_statement')
    if isinstance(quarterly_data, pd.DataFrame) and not quarterly_data.empty:
        quarterly_df_filtered = quarterly_data[quarterly_data.index.isin(key_items)].reindex(key_items)
        quarterly_df_filtered.columns = [col.strftime('%Y-%m-%d') if hasattr(col, 'strftime') else str(col) for col in quarterly_df_filtered.columns]

        # Define column width for data
        data_col_width = 15

        formatted_rows = []
        for index, row in quarterly_df_filtered.iterrows():
            formatted_row = f"{index:<15}" # Item name column
            for val in row:
                if currency == 'INR' and isinstance(val, (int, float)) and not pd.isna(val):
                    val_cr = val / 10000000
                    formatted_val_str = f"{val_cr:,.2f} Cr"
                elif isinstance(val, (int, float)) and not pd.isna(val):
                    formatted_val_str = f"{val:,.0f}"
                else:
                    formatted_val_str = "N/A"
                formatted_row += f" {formatted_val_str:>{data_col_width}}"
            formatted_rows.append(formatted_row)

        header_str = "".join([f" {col_name:>{data_col_width}}" for col_name in quarterly_df_filtered.columns])
        message += f"```\n                 {header_str}\n{'-'* (15 + (data_col_width + 1) * len(quarterly_df_filtered.columns))}\n"
        message += "\n".join(formatted_rows)
        message += "\n```\n\n"
    else:
        message += "_No quarterly income statement data available._\n\n"
        
    # Format Key Ratios
    message += "🔑 *Key Financial Ratios*\n"
    ratios = financial_data.get('ratios', {})
    
    def format_ratio(value, is_percentage=False, decimals=2):
        if value is None or not isinstance(value, (int, float)):
            return 'N/A'
        if is_percentage:
            return f"{value * 100:.{decimals}f}%"
        return f"{value:.{decimals}f}"

    message += f"  • Return on Equity (ROE): {format_ratio(ratios.get('return_on_equity'), True)}\n"
    message += f"  • Return on Assets (ROA): {format_ratio(ratios.get('return_on_assets'), True)}\n"
    message += f"  • Profit Margin: {format_ratio(ratios.get('profit_margin'), True)}\n"
    debt_equity_val = ratios.get('debt_to_equity')
    if isinstance(debt_equity_val, (int, float)):
        debt_equity_val /= 100 # Convert from percentage to decimal ratio
    message += f"  • Total Debt/Equity: {format_ratio(debt_equity_val)}\n"
    message += f"  • Current Ratio: {format_ratio(ratios.get('current_ratio'))}\n"
    message += f"  • % Held by Insiders: {format_ratio(ratios.get('held_percent_insiders'), True)}\n"
    message += f"  • % Held by Institutions: {format_ratio(ratios.get('held_percent_institutions'), True)}\n\n"

    message += "_Data might be limited for some stocks or exchanges._"
    
    if len(message) > 4050: # Telegram's message limit is 4096, keep some buffer
        message = message[:4050] + "... (truncated)"
        
    return message

def get_step3_financial_statements(ticker_symbol):
    """
    Get Step 3 financial data (Balance Sheet, Cash Flow) for a stock.
    
    Args:
        ticker_symbol (str): Stock ticker symbol.
        
    Returns:
        dict: Dictionary containing financial data or error message.
    """
    try:
        stock = yf.Ticker(ticker_symbol)
        info = stock.info

        if 'longName' not in info:
            return {'success': False, 'error': f"Could not find data for ticker '{ticker_symbol}'."}

        # Get annual balance sheet (last 4 years)
        balance_sheet = stock.balance_sheet
        if not balance_sheet.empty:
            balance_sheet_selected = balance_sheet.iloc[:, :4]
        else:
            balance_sheet_selected = pd.DataFrame()
            
        # Get annual cash flow statement (last 4 years)
        cash_flow = stock.cashflow
        if not cash_flow.empty:
            cash_flow_selected = cash_flow.iloc[:, :4]
        else:
            cash_flow_selected = pd.DataFrame()
            
        return {
            'success': True,
            'balance_sheet': balance_sheet_selected,
            'cash_flow_statement': cash_flow_selected,
            'stock_name': info.get('longName', ticker_symbol),
            'ticker': ticker_symbol,
            'currency': info.get('currency', 'N/A')
        }
        
    except Exception as e:
        return {'success': False, 'error': f"Error fetching Step 3 financials for {ticker_symbol}: {str(e)}"}

def format_step3_financial_statements(step3_data):
    """
    Format Step 3 financial data (Balance Sheet, Cash Flow) into a readable Telegram message.
    
    Args:
        step3_data (dict): Data from get_step3_financial_statements.
        
    Returns:
        str: Formatted message.
    """
    if not step3_data.get('success'):
        return f"❌ *Error*: {step3_data.get('error', 'Could not fetch Step 3 financials.')}"

    stock_name = step3_data.get('stock_name', 'N/A')
    ticker = step3_data.get('ticker', 'N/A')
    currency = step3_data.get('currency', '')
    currency_symbol = '₹' if currency == 'INR' else ('$' if currency == 'USD' else currency)
    
    message = f"🏦 *Step 3 Financials: {stock_name} ({ticker})*\n\n"
    message += f"_(All figures in {currency_symbol} unless otherwise noted. Displaying last 4 available years.)_\n\n"

    # --- Helper function to format a DataFrame section --- #
    def format_statement_df(df, title, key_items_list):
        statement_message = f"📋 *{title}*\n"
        if isinstance(df, pd.DataFrame) and not df.empty:
            # Filter for key items, preserving order if possible, and handling missing items
            existing_key_items = [item for item in key_items_list if item in df.index]
            df_filtered = df.reindex(existing_key_items) # Reindex to ensure order and include NaNs for missing specified keys
            
            df_filtered.columns = [col.strftime('%Y') if hasattr(col, 'strftime') else str(col) for col in df_filtered.columns]
            
            data_col_width = 15
            formatted_rows = []
            for index, row in df_filtered.iterrows():
                formatted_row = f"{index:<25}" # Increased width for item names
                for val in row:
                    if currency == 'INR' and isinstance(val, (int, float)) and not pd.isna(val):
                        val_cr = val / 10000000
                        formatted_val_str = f"{val_cr:,.2f} Cr"
                    elif isinstance(val, (int, float)) and not pd.isna(val):
                        formatted_val_str = f"{val:,.0f}"
                    else:
                        formatted_val_str = "N/A"
                    formatted_row += f" {formatted_val_str:>{data_col_width}}"
                formatted_rows.append(formatted_row)
            
            header_str = "".join([f" {col_name:>{data_col_width}}" for col_name in df_filtered.columns])
            # Adjust spacing for header to align with the wider item name column
            statement_message += f"```\n{'':<25} {header_str}\n{'-'* (25 + (data_col_width + 1) * len(df_filtered.columns))}\n"
            statement_message += "\n".join(formatted_rows)
            statement_message += "\n```\n\n"
        else:
            statement_message += f"_No {title.lower()} data available._\n\n"
        return statement_message
    # --- End of helper function --- #

    # Key items for Balance Sheet
    balance_sheet_keys = [
        'Total Assets', 'Current Assets', 'Cash And Cash Equivalents', 'Total Non Current Assets',
        'Total Liabilities Net Minority Interest', 'Current Liabilities', 'Total Non Current Liabilities Net Minority Interest',
        'Total Equity Gross Minority Interest', 'Stockholders Equity', # Common synonym for Total Equity
        'Long Term Debt', 'Short Term Debt', # More specific debt items if available
        'Net Debt' # Often useful if available
    ]
    # Key items for Cash Flow Statement
    cash_flow_keys = [
        'Operating Cash Flow', 'Investing Cash Flow', 'Financing Cash Flow',
        'End Cash Position', # Same as 'Cash And Cash Equivalents' at end of period
        'Capital Expenditure', 'Free Cash Flow'
    ]

    # Format Balance Sheet
    balance_sheet_data = step3_data.get('balance_sheet')
    message += format_statement_df(balance_sheet_data, "Balance Sheet (Annual)", balance_sheet_keys)

    # Format Cash Flow Statement
    cash_flow_data = step3_data.get('cash_flow_statement')
    message += format_statement_df(cash_flow_data, "Cash Flow Statement (Annual)", cash_flow_keys)

    message += "_Data might be limited for some stocks or exchanges._"
    
    # Truncate if too long for Telegram
    if len(message) > 4050:
        message = message[:4050] + "... (truncated)"
        
    return message
