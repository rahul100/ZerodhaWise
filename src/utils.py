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

import pandas as pd
import yfinance as yf
import time
import logging



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


def get_sector_details_for_nse_stocks():

    """
    Fetches a list of all stocks from NSE then uses yfinance to get info on the stock including
    the sector and market capitalization.

    Returns: None
        
    """

    nse_df = pd.read_csv('data/sec_list.csv', header=0)

    list_of_tickers = nse_df['Symbol'].tolist()

    final_dict = {}
    for ticker in list_of_tickers:
        stock_info = yf.Ticker(f'{ticker}.NS').info
        final_dict[ticker] = stock_info
    with open('data/nse_ticker_info.json','w') as f:
        json.dump(final_dict,f)
# def get_sector_and_mcap(ticker_nse,):
#     with open('data/nse_ticker_info.json', 'r') as f:
#         ticker_with_details = json.load(f)

#     print(ticker_with_details['21STCENMGM']['sector'])



    


if __name__ == '__main__':
    # To run this example, make sure you have the required libraries installed:
    # pip install pandas yfinance
    get_sector_details_for_nse_stocks()
    with open('data/nse_ticker_info.json', 'r') as f:
        ticker_with_details = json.load(f)
    pticker_with_details.keys()
    print(ticker_with_details['21STCENMGM']['sector'])
    
    
    # comprehensive_data = get_comprehensive_nse_bse_stocks()
    
    # # Print sample data for the first 5 stocks
    # print("\n--- Sample Stock Data ---")
    # for i, (symbol, data) in enumerate(comprehensive_data.items()):
    #     if i >= 10:
    #         break
    #     print(f"{symbol}: Sector='{data['sector']}', Market Cap={data['market_cap']}")