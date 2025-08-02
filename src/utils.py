"""
Utilities module for ZerodhaWise.

This module provides utility functions for configuration loading,
logging setup, and other common operations.
"""

import logging
import os
import yaml
from typing import Dict, Any, Optional, List
from datetime import datetime

import requests
import time
import re
from typing import Dict, Optional
from bs4 import BeautifulSoup
import json


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to configuration file. If None, uses default config.
        
    Returns:
        Dictionary containing configuration.
    """
    if config_path is None:
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'config.yaml')
            
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config
    
    # Default configuration
    # default_config = {
    #     'zerodha': {
    #         'api_key': '',
    #         'api_secret': '',
    #         'access_token': ''
    #     },
    #     'database': {
    #         'url': 'sqlite:///portfolio.db'
    #     },
    #     'logging': {
    #         'level': 'INFO',
    #         'file': 'logs/zerodhawise.log'
    #     }
    # }
    
    # try:
    #     if os.path.exists(config_path):
    #         with open(config_path, 'r') as f:
    #             config = yaml.safe_load(f)
    #             # Merge with default config
    #             for section, values in default_config.items():
    #                 if section not in config:
    #                     config[section] = values
    #                 else:
    #                     for key, value in values.items():
    #                         if key not in config[section]:
    #                             config[section][key] = value
    #             return config
    #     else:
    #         # Create default config file
    #         os.makedirs(os.path.dirname(config_path), exist_ok=True)
    #         with open(config_path, 'w') as f:
    #             yaml.dump(default_config, f, default_flow_style=False)
    #         return default_config
            
    # except Exception as e:
    #     print(f"Error loading config: {str(e)}")
    #     return default_config


def setup_logging(name: str, config: Optional[Dict[str, Any]] = None) -> logging.Logger:
    """
    Setup logging configuration.
    
    Args:
        name: Logger name.
        config: Configuration dictionary. If None, loads from config file.
        
    Returns:
        Configured logger instance.
    """
    if config is None:
        config = load_config()
    
    logger = logging.getLogger(name)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Set log level
    log_level = getattr(logging, config.get('logging', {}).get('level', 'INFO').upper())
    logger.setLevel(log_level)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Create file handler
    log_file = config.get('logging', {}).get('file', 'logs/zerodhawise.log')
    if log_file:
        try:
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            print(f"Warning: Could not setup file logging: {str(e)}")
    
    return logger


def format_currency(amount: float, currency: str = 'INR') -> str:
    """
    Format currency amount.
    
    Args:
        amount: Amount to format.
        currency: Currency code.
        
    Returns:
        Formatted currency string.
    """
    if currency == 'INR':
        return f"₹{amount:,.2f}"
    else:
        return f"{currency} {amount:,.2f}"


def format_percentage(value: float, decimal_places: int = 2) -> str:
    """
    Format percentage value.
    
    Args:
        value: Value to format as percentage.
        decimal_places: Number of decimal places.
        
    Returns:
        Formatted percentage string.
    """
    return f"{value:.{decimal_places}%}"


def calculate_percentage_change(old_value: float, new_value: float) -> float:
    """
    Calculate percentage change between two values.
    
    Args:
        old_value: Old value.
        new_value: New value.
        
    Returns:
        Percentage change.
    """
    if old_value == 0:
        return 0.0
    return ((new_value - old_value) / old_value) * 100


def validate_zerodha_credentials(config: Dict[str, Any]) -> bool:
    """
    Validate Zerodha API credentials.
    
    Args:
        config: Configuration dictionary.
        
    Returns:
        True if credentials are valid, False otherwise.
    """
    zerodha_config = config.get('zerodha', {})
    
    required_fields = ['api_key', 'api_secret']
    for field in required_fields:
        if not zerodha_config.get(field):
            return False
    
    return True


def create_sample_data() -> Dict[str, Any]:
    """
    Create sample portfolio data for testing.
    
    Returns:
        Dictionary containing sample portfolio data.
    """
    sample_holdings = [
        {
            'tradingsymbol': 'RELIANCE',
            'exchange': 'NSE',
            'quantity': 100,
            'market_value': 25000.0,
            'pnl': 2500.0,
            'sector': 'Oil & Gas'
        },
        {
            'tradingsymbol': 'TCS',
            'exchange': 'NSE',
            'quantity': 50,
            'market_value': 15000.0,
            'pnl': -500.0,
            'sector': 'IT'
        },
        {
            'tradingsymbol': 'HDFCBANK',
            'exchange': 'NSE',
            'quantity': 75,
            'market_value': 12000.0,
            'pnl': 1200.0,
            'sector': 'Banking'
        },
        {
            'tradingsymbol': 'INFY',
            'exchange': 'NSE',
            'quantity': 200,
            'market_value': 18000.0,
            'pnl': 1800.0,
            'sector': 'IT'
        },
        {
            'tradingsymbol': 'ITC',
            'exchange': 'NSE',
            'quantity': 300,
            'market_value': 9000.0,
            'pnl': -300.0,
            'sector': 'FMCG'
        }
    ]
    
    return {
        'holdings': sample_holdings,
        'positions': [],
        'margins': {
            'equity': {
                'available': 50000.0,
                'used': 79000.0,
                'total': 129000.0
            }
        },
        'timestamp': datetime.now().isoformat()
    }


def get_project_root() -> str:
    """
    Get the project root directory.
    
    Returns:
        Path to project root directory.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(current_dir)


def ensure_directory_exists(directory: str) -> bool:
    """
    Ensure a directory exists, create if it doesn't.
    
    Args:
        directory: Directory path.
        
    Returns:
        True if successful, False otherwise.
    """
    try:
        os.makedirs(directory, exist_ok=True)
        return True
    except Exception as e:
        print(f"Error creating directory {directory}: {str(e)}")
        return False


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe file operations.
    
    Args:
        filename: Original filename.
        
    Returns:
        Sanitized filename.
    """
    import re
    # Remove or replace invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip('. ')
    # Ensure filename is not empty
    if not sanitized:
        sanitized = 'unnamed_file'
    return sanitized


def get_file_size_mb(filepath: str) -> float:
    """
    Get file size in megabytes.
    
    Args:
        filepath: Path to file.
        
    Returns:
        File size in MB.
    """
    try:
        size_bytes = os.path.getsize(filepath)
        return size_bytes / (1024 * 1024)
    except Exception:
        return 0.0


def is_valid_date(date_string: str) -> bool:
    """
    Check if a string represents a valid date.
    
    Args:
        date_string: Date string to validate.
        
    Returns:
        True if valid date, False otherwise.
    """
    try:
        datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        return True
    except ValueError:
        return False


def parse_date_range(date_range: str) -> tuple:
    """
    Parse a date range string.
    
    Args:
        date_range: Date range string (e.g., "2023-01-01:2023-12-31").
        
    Returns:
        Tuple of (start_date, end_date) as datetime objects.
    """
    try:
        start_str, end_str = date_range.split(':')
        start_date = datetime.fromisoformat(start_str)
        end_date = datetime.fromisoformat(end_str)
        return start_date, end_date
    except Exception:
        return None, None 




def get_sector_mapping() -> Dict[str, str]:
    """
    Get sector mapping from NSE/BSE metadata using a free API.
    
    Returns:
        Dictionary mapping stock symbols to sectors.
    """
    sector_mapping = {}
    
    try:
        # Using NSE India's free API to get stock information
        # This API provides basic stock information including sector
        url = "https://www.nseindia.com/api/equity-stockIndices?index=SECURITIES%20IN%20F%26O"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        print(response.status_code)
        if response.status_code == 200:
            data = response.json()
            print(data)
            if 'data' in data:
                for item in data['data']:
                    symbol = item.get('symbol', '').strip()
                    sector = item.get('sector', 'Unknown').strip()
                    
                    if symbol and sector:
                        sector_mapping[symbol] = sector

            
    except Exception as e:
        logging.warning(f"Error fetching sector mapping from NSE API: {str(e)}")
    
    return sector_mapping



def get_nse_stocks_from_finology() -> Dict[str, Dict[str, Any]]:
    """
    Get all NSE stocks with sector and market cap information from Finology.
    
    Returns:
        Dictionary mapping stock symbols to sector and market cap information.
    """
    
    stocks_data = {}
    
    try:
        # Finology NSE stocks page
        url = "https://finology.in/stock-screener"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        print("Fetching NSE stocks data from Finology...")
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for stock data in the page
            # This might be in a table, JSON data, or API endpoint
            stock_elements = soup.find_all('tr', class_=re.compile(r'stock-row|company-row'))
            
            if not stock_elements:
                # Try alternative selectors
                stock_elements = soup.find_all('div', class_=re.compile(r'stock-item|company-item'))
            
            print(f"Found {len(stock_elements)} stock elements")
            
            for element in stock_elements:
                try:
                    # Extract stock information
                    symbol_elem = element.find('td', class_=re.compile(r'symbol|ticker')) or element.find('span', class_=re.compile(r'symbol|ticker'))
                    sector_elem = element.find('td', class_=re.compile(r'sector')) or element.find('span', class_=re.compile(r'sector'))
                    market_cap_elem = element.find('td', class_=re.compile(r'market-cap|mcap')) or element.find('span', class_=re.compile(r'market-cap|mcap'))
                    
                    if symbol_elem:
                        symbol = symbol_elem.get_text().strip()
                        sector = sector_elem.get_text().strip() if sector_elem else 'Unknown'
                        market_cap = market_cap_elem.get_text().strip() if market_cap_elem else 'Unknown'
                        
                        if symbol and symbol != '':
                            stocks_data[symbol] = {
                                'sector': sector,
                                'market_cap': market_cap,
                                'source': 'Finology'
                            }
                            
                except Exception as e:
                    print(f"Error parsing stock element: {str(e)}")
                    continue
            
            # If no data found in HTML, try to find JSON data
            if not stocks_data:
                print("No stock data found in HTML, trying to extract JSON data...")
                scripts = soup.find_all('script')
                
                for script in scripts:
                    if script.string and ('stock' in script.string.lower() or 'nse' in script.string.lower()):
                        # Look for JSON data in script tags
                        json_match = re.search(r'\{.*\}', script.string)
                        if json_match:
                            try:
                                import json
                                data = json.loads(json_match.group())
                                # Process JSON data if found
                                print("Found JSON data in script tag")
                            except:
                                continue
            
        else:
            print(f"Failed to fetch data from Finology. Status code: {response.status_code}")
            
    except Exception as e:
        print(f"Error fetching data from Finology: {str(e)}")
    
    return stocks_data


def get_nse_stocks_from_finology_api() -> Dict[str, Dict[str, Any]]:
    """
    Get NSE stocks data from Finology using their API endpoints.
    
    Returns:
        Dictionary mapping stock symbols to sector and market cap information.
    """
    import requests
    import json
    
    stocks_data = {}
    
    try:
        # Try different Finology API endpoints
        api_endpoints = [
            "https://finology.in/api/stocks/nse",
            "https://finology.in/api/screener/stocks",
            "https://finology.in/api/market/nse-stocks"
        ]
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json',
            'Referer': 'https://finology.in/stock-screener'
        }
        
        for endpoint in api_endpoints:
            try:
                print(f"Trying API endpoint: {endpoint}")
                response = requests.get(endpoint, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if isinstance(data, list):
                        # Process list of stocks
                        for stock in data:
                            symbol = stock.get('symbol', stock.get('ticker', ''))
                            if symbol:
                                stocks_data[symbol] = {
                                    'sector': stock.get('sector', 'Unknown'),
                                    'market_cap': stock.get('market_cap', stock.get('mcap', 'Unknown')),
                                    'company_name': stock.get('name', ''),
                                    'source': 'Finology API'
                                }
                    elif isinstance(data, dict) and 'data' in data:
                        # Process dictionary with data key
                        for stock in data['data']:
                            symbol = stock.get('symbol', stock.get('ticker', ''))
                            if symbol:
                                stocks_data[symbol] = {
                                    'sector': stock.get('sector', 'Unknown'),
                                    'market_cap': stock.get('market_cap', stock.get('mcap', 'Unknown')),
                                    'company_name': stock.get('name', ''),
                                    'source': 'Finology API'
                                }
                    
                    if stocks_data:
                        print(f"Successfully fetched {len(stocks_data)} stocks from {endpoint}")
                        break
                        
            except Exception as e:
                print(f"Error with endpoint {endpoint}: {str(e)}")
                continue
                
    except Exception as e:
        print(f"Error fetching data from Finology API: {str(e)}")
    
    return stocks_data


def get_nse_stocks_alternative_sources() -> Dict[str, Dict[str, Any]]:
    """
    Get NSE stocks from alternative sources like NSE India website or other financial data providers.
    
    Returns:
        Dictionary mapping stock symbols to sector and market cap information.
    """
    import requests
    from bs4 import BeautifulSoup
    
    stocks_data = {}
    
    try:
        # Try NSE India's equity list
        url = "https://www.nseindia.com/get-quotes/equity"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        print("Trying NSE India website...")
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for stock symbols in the page
            # This is a simplified approach - actual implementation would need to parse the specific structure
            stock_links = soup.find_all('a', href=re.compile(r'/get-quotes/equity/'))
            
            for link in stock_links:
                symbol = link.get_text().strip()
                if symbol and len(symbol) < 20:  # Reasonable symbol length
                    stocks_data[symbol] = {
                        'sector': 'Unknown',  # Would need additional API call to get sector
                        'market_cap': 'Unknown',
                        'source': 'NSE India'
                    }
            
            print(f"Found {len(stocks_data)} stocks from NSE India")
            
    except Exception as e:
        print(f"Error fetching from NSE India: {str(e)}")
    
    return stocks_data


def get_nse_stocks_from_moneycontrol() -> Dict[str, Dict[str, Any]]:
    """
    Get NSE stocks data from MoneyControl website.
    
    Returns:
        Dictionary mapping stock symbols to sector and market cap information.
    """
    import requests
    from bs4 import BeautifulSoup
    
    stocks_data = {}
    
    try:
        # MoneyControl NSE stocks page
        url = "https://www.moneycontrol.com/india/stockpricequote/"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        print("Fetching NSE stocks data from MoneyControl...")
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for stock links
            stock_links = soup.find_all('a', href=re.compile(r'/india/stockpricequote/'))
            
            for link in stock_links:
                try:
                    symbol = link.get_text().strip()
                    href = link.get('href', '')
                    
                    if symbol and len(symbol) < 20 and symbol.isupper():
                        # Extract sector from URL or link text
                        sector = 'Unknown'
                        if 'sector' in href.lower():
                            sector_match = re.search(r'sector/([^/]+)', href)
                            if sector_match:
                                sector = sector_match.group(1).replace('-', ' ').title()
                        
                        stocks_data[symbol] = {
                            'sector': sector,
                            'market_cap': 'Unknown',
                            'source': 'MoneyControl'
                        }
                        
                except Exception as e:
                    continue
            
            print(f"Found {len(stocks_data)} stocks from MoneyControl")
            
    except Exception as e:
        print(f"Error fetching from MoneyControl: {str(e)}")
    
    return stocks_data


def get_nse_stocks_from_screener() -> Dict[str, Dict[str, Any]]:
    """
    Get NSE stocks data from Screener.in website.
    
    Returns:
        Dictionary mapping stock symbols to sector and market cap information.
    """
    import requests
    from bs4 import BeautifulSoup
    
    stocks_data = {}
    
    try:
        # Screener.in NSE stocks page
        url = "https://www.screener.in/screens/stock-screener"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        print("Fetching NSE stocks data from Screener.in...")
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for stock table
            stock_table = soup.find('table', class_=re.compile(r'data-table|stock-table'))
            
            if stock_table:
                rows = stock_table.find_all('tr')
                
                for row in rows[1:]:  # Skip header row
                    try:
                        cells = row.find_all('td')
                        if len(cells) >= 3:
                            symbol = cells[0].get_text().strip()
                            sector = cells[1].get_text().strip() if len(cells) > 1 else 'Unknown'
                            market_cap = cells[2].get_text().strip() if len(cells) > 2 else 'Unknown'
                            
                            if symbol and symbol.isupper():
                                stocks_data[symbol] = {
                                    'sector': sector,
                                    'market_cap': market_cap,
                                    'source': 'Screener.in'
                                }
                                
                    except Exception as e:
                        continue
            
            print(f"Found {len(stocks_data)} stocks from Screener.in")
            
    except Exception as e:
        print(f"Error fetching from Screener.in: {str(e)}")
    
    return stocks_data


def get_nse_stocks_from_yahoo_finance() -> Dict[str, Dict[str, Any]]:
    """
    Get NSE stocks data using Yahoo Finance API.
    
    Returns:
        Dictionary mapping stock symbols to sector and market cap information.
    """
    import yfinance as yf
    
    stocks_data = {}
    
    # Common NSE stocks
    nse_symbols = [
        'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'ICICIBANK.NS', 
        'HINDUNILVR.NS', 'ITC.NS', 'SBIN.NS', 'BHARTIARTL.NS', 'KOTAKBANK.NS',
        'AXISBANK.NS', 'ASIANPAINT.NS', 'MARUTI.NS', 'HCLTECH.NS', 'SUNPHARMA.NS',
        'TATAMOTORS.NS', 'WIPRO.NS', 'ULTRACEMCO.NS', 'TITAN.NS', 'BAJFINANCE.NS'
    ]
    
    try:
        print("Fetching NSE stocks data from Yahoo Finance...")
        
        for symbol in nse_symbols:
            try:
                stock = yf.Ticker(symbol)
                info = stock.info
                
                if info and 'sector' in info:
                    clean_symbol = symbol.replace('.NS', '')
                    stocks_data[clean_symbol] = {
                        'sector': info.get('sector', 'Unknown'),
                        'market_cap': str(info.get('marketCap', 'Unknown')),
                        'company_name': info.get('longName', ''),
                        'source': 'Yahoo Finance'
                    }
                    
            except Exception as e:
                print(f"Error fetching {symbol}: {str(e)}")
                continue
        
        print(f"Found {len(stocks_data)} stocks from Yahoo Finance")
        
    except Exception as e:
        print(f"Error fetching from Yahoo Finance: {str(e)}")
    
    return stocks_data


def get_comprehensive_nse_stocks() -> Dict[str, Dict[str, Any]]:
    """
    Get comprehensive NSE stocks data from multiple sources.
    
    Returns:
        Dictionary mapping stock symbols to sector and market cap information.
    """
    print("Fetching NSE stocks from multiple sources...")
    
    all_stocks = {}
    
    # Try multiple sources
    sources = [
        ("Yahoo Finance", get_nse_stocks_from_yahoo_finance),
        ("Finology", get_nse_stocks_from_finology),
        ("Finology API", get_nse_stocks_from_finology_api),
        ("MoneyControl", get_nse_stocks_from_moneycontrol),
        ("Screener.in", get_nse_stocks_from_screener),
        ("Alternative Sources", get_nse_stocks_alternative_sources)
    ]
    
    for source_name, source_func in sources:
        try:
            print(f"\nTrying {source_name}...")
            stocks_data = source_func()
            
            if stocks_data:
                # Merge data, preferring sources that come first
                for symbol, info in stocks_data.items():
                    if symbol not in all_stocks:
                        all_stocks[symbol] = info
                    elif all_stocks[symbol].get('sector') == 'Unknown' and info.get('sector') != 'Unknown':
                        # Update with better sector information
                        all_stocks[symbol].update(info)
                
                print(f"✓ Added {len(stocks_data)} stocks from {source_name}")
            else:
                print(f"✗ No data from {source_name}")
                
        except Exception as e:
            print(f"✗ Error with {source_name}: {str(e)}")
            continue
    
    if all_stocks:
        print(f"\n✓ Successfully fetched {len(all_stocks)} unique stocks from all sources")
        
        # Show statistics
        sectors = {}
        sources_used = {}
        
        for info in all_stocks.values():
            sector = info.get('sector', 'Unknown')
            source = info.get('source', 'Unknown')
            sectors[sector] = sectors.get(sector, 0) + 1
            sources_used[source] = sources_used.get(source, 0) + 1
        
        print(f"\nSector distribution (top 10):")
        sorted_sectors = sorted(sectors.items(), key=lambda x: x[1], reverse=True)[:10]
        for sector, count in sorted_sectors:
            print(f"   {sector}: {count} stocks")
        
        print(f"\nData sources used:")
        for source, count in sources_used.items():
            print(f"   {source}: {count} stocks")
        
        # Show sample data
        sample_stocks = list(all_stocks.items())[:5]
        print(f"\nSample stocks:")
        for symbol, info in sample_stocks:
            print(f"   {symbol}: {info.get('sector', 'Unknown')} - {info.get('market_cap', 'Unknown')} ({info.get('source', 'Unknown')})")
    else:
        print("✗ Failed to fetch stocks from all sources")
    
    return all_stocks


def update_holdings_with_finology_data(holdings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Update holdings with sector and market cap information from Finology.
    
    Args:
        holdings: List of portfolio holdings
        
    Returns:
        Updated holdings with sector and market cap information
    """
    # Get comprehensive stock data
    stocks_data = get_comprehensive_nse_stocks()
    
    updated_holdings = []
    
    for holding in holdings:
        symbol = holding.get('tradingsymbol', '')
        
        if symbol and symbol in stocks_data:
            # Update holding with sector info
            stock_info = stocks_data[symbol]
            holding['sector'] = stock_info.get('sector', 'Unknown')
            holding['market_cap'] = stock_info.get('market_cap', 'Unknown')
            holding['company_name'] = stock_info.get('company_name', '')
            holding['data_source'] = stock_info.get('source', 'Unknown')
        
        updated_holdings.append(holding)
    
    return updated_holdings