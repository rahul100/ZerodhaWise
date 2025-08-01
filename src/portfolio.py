"""
Portfolio analysis module for ZerodhaWise.

This module provides comprehensive portfolio analysis functionality including
portfolio fetching, analysis, and management.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from kiteconnect import KiteConnect
from .utils import load_config, setup_logging
from .data import DataManager


class PortfolioAnalyzer:
    """
    Main class for portfolio analysis and management.
    
    This class provides methods to fetch, analyze, and manage Zerodha portfolio data.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the PortfolioAnalyzer.
        
        Args:
            config_path: Path to configuration file. If None, uses default config.
        """
        self.config = load_config(config_path)
        self.logger = setup_logging(__name__)
        self.data_manager = DataManager(self.config)
        
        # Initialize Kite Connect
        self.kite = KiteConnect(api_key=self.config['zerodha']['api_key'])
        if 'access_token' in self.config['zerodha']:
            self.kite.set_access_token(self.config['zerodha']['access_token'])
    
    def get_portfolio(self) -> Dict[str, Any]:
        """
        Fetch current portfolio from Zerodha.
        
        Returns:
            Dictionary containing portfolio data including holdings, margins, etc.
        """
        try:
            self.logger.info("Fetching portfolio data from Zerodha...")
            
            # Fetch holdings
            holdings = self.kite.holdings()
            
            # Fetch positions
            positions = self.kite.positions()
            
            # Fetch margins
            margins = self.kite.margins()
            
            portfolio = {
                'holdings': holdings,
                'positions': positions,
                'margins': margins,
                'timestamp': datetime.now().isoformat()
            }
            
            # Save to database
            self.data_manager.save_portfolio(portfolio)
            
            self.logger.info(f"Successfully fetched portfolio with {len(holdings)} holdings")
            return portfolio
            
        except Exception as e:
            self.logger.error(f"Error fetching portfolio: {str(e)}")
            raise
    
    def analyze_portfolio(self, portfolio: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze portfolio performance and composition.
        
        Args:
            portfolio: Portfolio data. If None, fetches current portfolio.
            
        Returns:
            Dictionary containing portfolio analysis results.
        """
        if portfolio is None:
            portfolio = self.get_portfolio()
        
        holdings = portfolio['holdings']
        
        # Calculate basic metrics
        total_value = sum(float(holding['market_value']) for holding in holdings)
        total_pnl = sum(float(holding['pnl']) for holding in holdings)
        
        # Sector analysis
        sector_analysis = self._analyze_sectors(holdings)
        
        # Top holdings
        top_holdings = sorted(holdings, key=lambda x: float(x['market_value']), reverse=True)[:10]
        
        # P&L analysis
        pnl_analysis = self._analyze_pnl(holdings)
        
        analysis = {
            'total_value': total_value,
            'total_pnl': total_pnl,
            'total_pnl_percentage': (total_pnl / total_value * 100) if total_value > 0 else 0,
            'number_of_holdings': len(holdings),
            'sector_analysis': sector_analysis,
            'top_holdings': top_holdings,
            'pnl_analysis': pnl_analysis,
            'timestamp': datetime.now().isoformat()
        }
        
        return analysis
    
    def _analyze_sectors(self, holdings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze portfolio by sectors."""
        sector_data = {}
        
        for holding in holdings:
            sector = holding.get('sector', 'Unknown')
            market_value = float(holding['market_value'])
            
            if sector not in sector_data:
                sector_data[sector] = {
                    'total_value': 0,
                    'holdings': [],
                    'count': 0
                }
            
            sector_data[sector]['total_value'] += market_value
            sector_data[sector]['holdings'].append(holding)
            sector_data[sector]['count'] += 1
        
        # Calculate percentages
        total_value = sum(data['total_value'] for data in sector_data.values())
        
        for sector in sector_data:
            sector_data[sector]['percentage'] = (
                sector_data[sector]['total_value'] / total_value * 100
            ) if total_value > 0 else 0
        
        return sector_data
    
    def _analyze_pnl(self, holdings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze P&L distribution."""
        positive_pnl = [h for h in holdings if float(h['pnl']) > 0]
        negative_pnl = [h for h in holdings if float(h['pnl']) < 0]
        
        return {
            'positive_count': len(positive_pnl),
            'negative_count': len(negative_pnl),
            'total_positive_pnl': sum(float(h['pnl']) for h in positive_pnl),
            'total_negative_pnl': sum(float(h['pnl']) for h in negative_pnl),
            'best_performer': max(holdings, key=lambda x: float(x['pnl'])) if holdings else None,
            'worst_performer': min(holdings, key=lambda x: float(x['pnl'])) if holdings else None
        }
    
    def get_portfolio_summary(self) -> str:
        """
        Get a formatted summary of the portfolio.
        
        Returns:
            Formatted string containing portfolio summary.
        """
        portfolio = self.get_portfolio()
        analysis = self.analyze_portfolio(portfolio)
        
        summary = f"""
Portfolio Summary
================
Total Value: ₹{analysis['total_value']:,.2f}
Total P&L: ₹{analysis['total_pnl']:,.2f} ({analysis['total_pnl_percentage']:.2f}%)
Number of Holdings: {analysis['number_of_holdings']}

Top Sectors:
"""
        
        # Add top sectors
        sectors = sorted(
            analysis['sector_analysis'].items(),
            key=lambda x: x[1]['total_value'],
            reverse=True
        )[:5]
        
        for sector, data in sectors:
            summary += f"- {sector}: {data['percentage']:.1f}% (₹{data['total_value']:,.2f})\n"
        
        summary += f"""
P&L Analysis:
- Positive P&L Stocks: {analysis['pnl_analysis']['positive_count']}
- Negative P&L Stocks: {analysis['pnl_analysis']['negative_count']}
- Total Positive P&L: ₹{analysis['pnl_analysis']['total_positive_pnl']:,.2f}
- Total Negative P&L: ₹{analysis['pnl_analysis']['total_negative_pnl']:,.2f}
"""
        
        return summary
    
    def get_historical_portfolio(self, days: int = 30) -> pd.DataFrame:
        """
        Get historical portfolio data.
        
        Args:
            days: Number of days to fetch historical data.
            
        Returns:
            DataFrame containing historical portfolio data.
        """
        return self.data_manager.get_historical_portfolio(days)
    
    def export_portfolio_report(self, filename: str = None) -> str:
        """
        Export portfolio analysis to a file.
        
        Args:
            filename: Output filename. If None, generates default name.
            
        Returns:
            Path to the exported file.
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"portfolio_report_{timestamp}.txt"
        
        portfolio = self.get_portfolio()
        analysis = self.analyze_portfolio(portfolio)
        summary = self.get_portfolio_summary()
        
        # Create detailed report
        report = f"""
ZerodhaWise Portfolio Report
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
{'='*50}

{summary}

Detailed Holdings:
"""
        
        holdings = portfolio['holdings']
        for i, holding in enumerate(holdings, 1):
            report += f"""
{i}. {holding['tradingsymbol']} ({holding['exchange']})
    Quantity: {holding['quantity']}
    Market Value: ₹{float(holding['market_value']):,.2f}
    P&L: ₹{float(holding['pnl']):,.2f}
    P&L %: {(float(holding['pnl']) / float(holding['market_value']) * 100):.2f}%
"""
        
        # Save report
        import os
        os.makedirs('reports', exist_ok=True)
        filepath = os.path.join('reports', filename)
        
        with open(filepath, 'w') as f:
            f.write(report)
        
        self.logger.info(f"Portfolio report exported to {filepath}")
        return filepath 