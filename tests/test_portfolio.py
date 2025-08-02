"""
Unit tests for portfolio module.
"""

import unittest
from unittest.mock import Mock, patch
import pandas as pd
from datetime import datetime

from src.portfolio import PortfolioAnalyzer
from src.utils import create_sample_data


class TestPortfolioAnalyzer(unittest.TestCase):
    """Test cases for PortfolioAnalyzer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            'zerodha': {
                'api_key': 'test_key',
                'api_secret': 'test_secret'
            },
            'database': {
                'url': 'sqlite:///:memory:'
            },
            'logging': {
                'level': 'INFO',
                'file': 'logs/test.log'
            }
        }
        
        self.sample_data = create_sample_data()
    
    @patch('src.portfolio.KiteConnect')
    def test_init(self, mock_kite):
        """Test PortfolioAnalyzer initialization."""
        analyzer = PortfolioAnalyzer()
        self.assertIsNotNone(analyzer)
        self.assertIsNotNone(analyzer.config)
    
    @patch('src.portfolio.KiteConnect')
    def test_analyze_portfolio(self, mock_kite):
        """Test portfolio analysis with sample data."""
        analyzer = PortfolioAnalyzer()
        
        # Mock the data manager
        analyzer.data_manager = Mock()
        
        analysis = analyzer.analyze_portfolio(self.sample_data)
        
        self.assertIsInstance(analysis, dict)
        self.assertIn('total_value', analysis)
        self.assertIn('total_pnl', analysis)
        self.assertIn('number_of_holdings', analysis)
        self.assertIn('sector_analysis', analysis)
        self.assertIn('top_holdings', analysis)
        self.assertIn('pnl_analysis', analysis)
    
    def test_analyze_sectors(self):
        """Test sector analysis."""
        analyzer = PortfolioAnalyzer()
        holdings = self.sample_data['holdings']
        
        sector_analysis = analyzer._analyze_sectors(holdings)
        
        self.assertIsInstance(sector_analysis, dict)
        self.assertGreater(len(sector_analysis), 0)
        
        # Check that all sectors have required keys
        for sector, data in sector_analysis.items():
            self.assertIn('total_value', data)
            self.assertIn('holdings', data)
            self.assertIn('count', data)
            self.assertIn('percentage', data)
    
    def test_analyze_pnl(self):
        """Test P&L analysis."""
        analyzer = PortfolioAnalyzer()
        holdings = self.sample_data['holdings']
        
        pnl_analysis = analyzer._analyze_pnl(holdings)
        
        self.assertIsInstance(pnl_analysis, dict)
        self.assertIn('positive_count', pnl_analysis)
        self.assertIn('negative_count', pnl_analysis)
        self.assertIn('total_positive_pnl', pnl_analysis)
        self.assertIn('total_negative_pnl', pnl_analysis)
    
    def test_get_portfolio_summary(self):
        """Test portfolio summary generation."""
        analyzer = PortfolioAnalyzer()
        
        # Mock the get_portfolio method
        analyzer.get_portfolio = Mock(return_value=self.sample_data)
        
        summary = analyzer.get_portfolio_summary()
        
        self.assertIsInstance(summary, str)
        self.assertIn('Portfolio Summary', summary)
        self.assertIn('Total Value', summary)
        self.assertIn('Total P&L', summary)
    
    def test_export_portfolio_report(self):
        """Test portfolio report export."""
        analyzer = PortfolioAnalyzer()
        
        # Mock the get_portfolio method
        analyzer.get_portfolio = Mock(return_value=self.sample_data)
        
        filepath = analyzer.export_portfolio_report()
        
        self.assertIsInstance(filepath, str)
        self.assertTrue(filepath.endswith('.txt'))
    
    def test_empty_portfolio(self):
        """Test handling of empty portfolio."""
        analyzer = PortfolioAnalyzer()
        empty_portfolio = {'holdings': [], 'positions': [], 'margins': {}}
        
        analysis = analyzer.analyze_portfolio(empty_portfolio)
        
        self.assertEqual(analysis['total_value'], 0)
        self.assertEqual(analysis['total_pnl'], 0)
        self.assertEqual(analysis['number_of_holdings'], 0)


class TestPortfolioDataValidation(unittest.TestCase):
    """Test cases for portfolio data validation."""
    
    def test_invalid_portfolio_data(self):
        """Test handling of invalid portfolio data."""
        analyzer = PortfolioAnalyzer()
        
        # Test with None
        with self.assertRaises(Exception):
            analyzer.analyze_portfolio(None)
        
        # Test with empty dict
        empty_data = {}
        analysis = analyzer.analyze_portfolio(empty_data)
        self.assertEqual(analysis['total_value'], 0)
    
    def test_malformed_holdings(self):
        """Test handling of malformed holdings data."""
        analyzer = PortfolioAnalyzer()
        
        # Test with holdings that have quantity and close_price but no market_value
        malformed_data = {
            'holdings': [
                {'tradingsymbol': 'TEST', 'quantity': 100, 'close_price': 50, 'pnl': 1000}
            ]
        }
        
        # Should not raise an exception now since market_value is calculated
        analysis = analyzer.analyze_portfolio(malformed_data)
        self.assertEqual(analysis['total_value'], 5000)  # 100 * 50
        self.assertEqual(analysis['number_of_holdings'], 1)


if __name__ == '__main__':
    unittest.main() 