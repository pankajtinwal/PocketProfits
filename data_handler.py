import requests
import datetime
from typing import Dict, Any
from config import (INDICES, SECTOR_INDICES, SENSEX_STOCKS, GLOBAL_INDICES,
                   VIX_LEVELS, COMMODITIES, CURRENCIES, YH_FINANCE_API)

# Cache for market data
_market_cache = {
    'data': None,
    'last_updated': None,
    'cache_duration': datetime.timedelta(minutes=5)
}

def get_cached_market_data() -> Dict[str, Any]:
    """Get market data from cache if valid, otherwise fetch new data"""
    global _market_cache
    now = datetime.datetime.now()

    # Check if cache is valid
    if (_market_cache['data'] is not None and
        _market_cache['last_updated'] is not None and
        now - _market_cache['last_updated'] < _market_cache['cache_duration']):
        return _market_cache['data']

    # Prepare all symbols for a single API call
    all_symbols = (
        list(INDICES.values()) +
        list(SECTOR_INDICES.values()) +
        list(GLOBAL_INDICES.values()) +
        list(COMMODITIES.values()) +
        list(CURRENCIES.values()) +
        SENSEX_STOCKS
    )

    # Fetch fresh data
    url = f"{YH_FINANCE_API['base_url']}/market/v2/get-quotes"
    try:
        response = requests.get(
            url,
            headers=YH_FINANCE_API['headers'],
            params={'region': 'IN', 'symbols': ','.join(all_symbols)}
        )
        response.raise_for_status()
        
        data = response.json()
        result = {}
        
        for quote in data.get('quoteResponse', {}).get('result', []):
            symbol = quote.get('symbol', '')
            regular_market_price = quote.get('regularMarketPrice', 0)
            regular_market_change = quote.get('regularMarketChange', 0)
            regular_market_change_percent = quote.get('regularMarketChangePercent', 0)
            regular_market_time = quote.get('regularMarketTime', 0)
            
            result[symbol] = {
                'price': round(regular_market_price, 2),
                'change': round(regular_market_change, 2),
                'change_percent': round(regular_market_change_percent, 2),
                'timestamp': regular_market_time
            }
            
        # Update cache with new data and timestamp
        _market_cache['data'] = result
        _market_cache['last_updated'] = datetime.datetime.now()
        
        return result
    except Exception as e:
        return {'error': str(e)}

def get_vix_level(vix_value):
    """Determine VIX volatility level"""
    for level, range_data in VIX_LEVELS.items():
        if range_data['min'] <= vix_value < range_data['max']:
            return level
    return 'HIGH'  # Default to high if outside ranges

def get_market_overview():
    """Get market overview using cached data"""
    # Get data from cache or fresh API call
    all_data = get_cached_market_data()
    
    if 'error' in all_data:
        return {
            'indices': {'error': all_data['error']},
            'sectors': {'error': all_data['error']},
            'global': {'error': all_data['error']},
            'commodities': {'error': all_data['error']},
            'currencies': {'error': all_data['error']}
        }
    
    # Process indices data
    market_data = {}
    for index_name, symbol in INDICES.items():
        if symbol in all_data:
            data = all_data[symbol]
            if index_name == 'INDIA VIX':
                data['volatility_level'] = get_vix_level(data['price'])
            market_data[index_name] = data
        else:
            market_data[index_name] = {'error': 'Data not available'}
    
    # Process sector data
    sector_data = {}
    for sector_name, symbol in SECTOR_INDICES.items():
        if symbol in all_data:
            sector_data[sector_name] = all_data[symbol]
        else:
            sector_data[sector_name] = {'error': 'Data not available'}
    
    # Process global indices data
    global_data = {}
    for index_name, symbol in GLOBAL_INDICES.items():
        if symbol in all_data:
            global_data[index_name] = all_data[symbol]
        else:
            global_data[index_name] = {'error': 'Data not available'}
    
    # Process commodities data
    commodities_data = {}
    for commodity_name, symbol in COMMODITIES.items():
        if symbol in all_data:
            commodities_data[commodity_name] = all_data[symbol]
        else:
            commodities_data[commodity_name] = {'error': 'Data not available'}
    
    # Process currencies data
    currencies_data = {}
    for currency_name, symbol in CURRENCIES.items():
        if symbol in all_data:
            currencies_data[currency_name] = all_data[symbol]
        else:
            currencies_data[currency_name] = {'error': 'Data not available'}
    
    return {
        'indices': market_data,
        'sectors': sector_data,
        'global': global_data,
        'commodities': commodities_data,
        'currencies': currencies_data
    }

def get_top_movers():
    """Get top movers using cached data"""
    try:
        # Use cached data
        data = get_cached_market_data()
        
        if 'error' in data:
            return {'error': data['error']}
        
        # Calculate daily changes
        changes = {}
        advances = 0
        declines = 0
        unchanged = 0
        
        # Process each stock
        for stock in SENSEX_STOCKS:
            if stock in data:
                stock_data = data[stock]
                company_name = stock.replace('.NS', '')
                
                # Store stock data
                changes[company_name] = {
                    'symbol': stock,
                    'price': stock_data['price'],
                    'change': stock_data['change'],
                    'change_percent': stock_data['change_percent']
                }
                
                # Count advances, declines, and unchanged
                if stock_data['change_percent'] > 0.1:
                    advances += 1
                elif stock_data['change_percent'] < -0.1:
                    declines += 1
                else:
                    unchanged += 1
        
        # Sort by percentage change
        sorted_changes = sorted(changes.items(), key=lambda x: x[1]['change_percent'])
        
        # Get top 3 losers and gainers
        losers = sorted_changes[:3]
        gainers = sorted_changes[-3:]
        gainers.reverse()  # To have highest gainer first
        
        return {
            'gainers': [{'name': name, **data} for name, data in gainers],
            'losers': [{'name': name, **data} for name, data in losers],
            'market_breadth': {
                'advances': advances,
                'declines': declines,
                'unchanged': unchanged
            }
        }
    except Exception as e:
        return {'error': str(e)}

def format_market_message():
    """Format market data into a readable message with improved visual formatting"""
    try:
        # Get market data from cache
        market_overview = get_market_overview()
        market_data = market_overview['indices']
        sector_data = market_overview['sectors']
        global_data = market_overview['global']
        movers_data = get_top_movers()
        
        # Get current date and time
        now = datetime.datetime.now()
        cache_time = _market_cache['last_updated']
        date_str = cache_time.strftime("%d %b %Y")
        time_str = cache_time.strftime("%I:%M %p")
        
        # Calculate data age
        data_age = now - cache_time
        delay_str = f"Data delayed by {data_age.seconds // 60} mins"
        
        # Start building the message with the header
        message = f"""📊🇮🇳 *INDIAN MARKET SNAPSHOT* 🇮🇳📊
-----------------------------------
As of {date_str} at {time_str} IST
⏰ {delay_str}

"""
        
        # Format major indices section
        message += "📈 *MAJOR INDICES*\n-------------------"
        
        # Add VIX information first if available
        if 'INDIA VIX' in market_data and 'error' not in market_data['INDIA VIX']:
            vix_data = market_data['INDIA VIX']
            vix_emoji = "🟢" if vix_data['price'] < 15 else "🟡" if vix_data['price'] < 25 else "🔴"
            message += f"\n• *INDIA VIX* {vix_emoji}: {vix_data['price']:.2f} ({vix_data['volatility_level']} Volatility)"
            # Remove VIX from market_data to avoid duplicate printing
            market_data = {k: v for k, v in market_data.items() if k != 'INDIA VIX'}
        for index_name, data in market_data.items():
            if 'error' in data:
                message += f"\n• *{index_name}*: Data unavailable"
                continue
                
            change_emoji = "🔴" if data['change'] < 0 else "🟢"
            change_sign = "-" if data['change'] < 0 else "+"
            message += f"\n• *{index_name}*: ₹{data['price']:,.2f}  {change_emoji} ({change_sign}{abs(data['change']):,.2f}, {change_sign}{abs(data['change_percent']):.2f}%)"
        
        # Format sector & market cap snapshot
        message += "\n\n📊 *SECTOR & MARKET CAP*\n-------------------"
        for sector_name, data in sector_data.items():
            if 'error' in data:
                message += f"\n• *{sector_name}*: Data unavailable"
                continue
                
            change_emoji = "🔴" if data['change'] < 0 else "🟢"
            change_sign = "-" if data['change'] < 0 else "+"
            message += f"\n{change_emoji} *{sector_name}*: ₹{data['price']:,.2f}  ({change_sign}{abs(data['change']):,.2f}, {change_sign}{abs(data['change_percent']):.2f}%)"
        
        # Format movers section
        message += "\n\n🔝 *TOP GAINERS & LOSERS (SENSEX)* 🔝\n-----------------------------------"
        
        if 'error' in movers_data:
            message += f"\nError fetching movers data: {movers_data['error']}"
        else:
            # Gainers
            message += "\n\n*TOP GAINERS:*"
            for gainer in movers_data['gainers']:
                message += f"\n🟢 *{gainer['name']}*: ₹{gainer['price']:,.2f}  (+{gainer['change_percent']:.2f}%)"
            
            message += "\n\n*TOP LOSERS:*"
            for loser in movers_data['losers']:
                message += f"\n🔴 *{loser['name']}*: ₹{loser['price']:,.2f}  ({loser['change_percent']:.2f}%)"
            
            # Add commodities section
            message += "\n\n💰 *COMMODITIES & CURRENCIES*\n-------------------"
            
            # Display commodities
            for commodity_name, data in market_overview['commodities'].items():
                if 'error' in data:
                    message += f"\n• *{commodity_name}*: Data unavailable"
                    continue
                    
                change_emoji = "🔴" if data['change'] < 0 else "🟢"
                change_sign = "-" if data['change'] < 0 else "+"
                currency = '$' if 'CRUDE' in commodity_name else '₹'
                message += f"\n• *{commodity_name}*: {currency}{data['price']:,.2f}  {change_emoji} ({change_sign}{abs(data['change_percent']):.2f}%)"
            
            # Display currencies
            for currency_name, data in market_overview['currencies'].items():
                if 'error' in data:
                    message += f"\n• *{currency_name}*: Data unavailable"
                    continue
                    
                change_emoji = "🔴" if data['change'] < 0 else "🟢"
                change_sign = "-" if data['change'] < 0 else "+"
                message += f"\n• *{currency_name}*: ₹{data['price']:,.2f}  {change_emoji} ({change_sign}{abs(data['change_percent']):.2f}%)"
            
            # Add global indices section
            message += "\n\n🌎 *GLOBAL INDICES*\n-------------------"
            for index_name, data in global_data.items():
                if 'error' in data:
                    message += f"\n• *{index_name}*: Data unavailable"
                    continue
                    
                change_emoji = "🔴" if data['change'] < 0 else "🟢"
                change_sign = "-" if data['change'] < 0 else "+"
                message += f"\n• *{index_name}*: {change_emoji} {change_sign}{abs(data['change_percent']):.2f}%"
            
            # Add market breadth section if available
            if 'market_breadth' in movers_data:
                breadth = movers_data['market_breadth']
                message += f"\n\n📊 *SENSEX MARKET BREADTH* 📊\n---------------------------"
                message += f"\nAdvances: *{breadth['advances']}* | Declines: *{breadth['declines']}* | Unchanged: *{breadth['unchanged']}*"
        
        # Add disclaimer
        message += "\n\n-----------------------------------\n_Data sourced from Yahoo Finance. May be delayed.\nDisclaimer: For informational purposes only. Not financial advice._"
        
        return message
    
    except Exception as e:
        return f"Error generating market overview: {str(e)}"
