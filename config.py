import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
RAPID_API_KEY = os.getenv('RAPID_API_KEY')

# API Configuration
YH_FINANCE_API = {
    'host': 'yh-finance.p.rapidapi.com',
    'base_url': 'https://yh-finance.p.rapidapi.com',
    'headers': {
        'X-RapidAPI-Key': RAPID_API_KEY,
        'X-RapidAPI-Host': 'yh-finance.p.rapidapi.com'
    }
}

# VIX Volatility Levels
VIX_LEVELS = {
    'LOW': {'min': 0, 'max': 15},
    'MODERATE': {'min': 15, 'max': 25},
    'HIGH': {'min': 25, 'max': float('inf')}
}

# Indian Market Indices
INDICES = {
    'NIFTY 50': '^NSEI',
    'SENSEX': '^BSESN',
    'BANK NIFTY': '^NSEBANK',
    'INDIA VIX': '^INDIAVIX'
}

# Sector & Market Cap Indices
SECTOR_INDICES = {
    'NIFTY IT': '^CNXIT',
    'NIFTY AUTO': '^CNXAUTO',
    'NIFTY PHARMA': '^CNXPHARMA',
    'NIFTY MIDCAP SELECT': 'NIFTY_MID_SELECT.NS',
    'NIFTY SMALLCAP': '^CNXSC'
}

# Global Market Indices
GLOBAL_INDICES = {
    'S&P 500': '^GSPC',
    'NASDAQ': '^IXIC',
    'DOW JONES': '^DJI',
    'FTSE 100': '^FTSE',
    'NIKKEI 225': '^N225'
}

# Commodities
COMMODITIES  = {
    'GOLD': 'GC=F',
    'CRUDE OIL (BRENT)': 'BZ=F'
}

# Currencies
CURRENCIES = {
    'USD/INR': 'INR=X'
}

# Sensex constituents for top gainers/losers
SENSEX_STOCKS = [
    'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'ICICIBANK.NS',
    'HINDUNILVR.NS', 'ADANIPORTS.NS', 'KOTAKBANK.NS', 'BAJFINANCE.NS', 'SBIN.NS',
    'BHARTIARTL.NS', 'ITC.NS', 'AXISBANK.NS', 'ASIANPAINT.NS', 'MARUTI.NS',
    'HCLTECH.NS', 'LT.NS', 'SUNPHARMA.NS', 'ULTRACEMCO.NS', 'TITAN.NS',
    'BAJAJFINSV.NS', 'NTPC.NS', 'POWERGRID.NS', 'TATASTEEL.NS', 'TECHM.NS',
    'TATAMOTORS.NS', 'M&M.NS', 'INDUSINDBK.NS', 'NESTLEIND.NS', 'WIPRO.NS'
]
