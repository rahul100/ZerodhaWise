#!/usr/bin/env python3
"""
Example script demonstrating ZerodhaWise usage.

This script shows how to use the ZerodhaWise library to analyze
portfolio data and generate reports.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from portfolio import PortfolioAnalyzer
from performance import PerformanceAnalyzer
from risk import RiskAnalyzer
from visualization import ChartGenerator
from utils import create_sample_data, setup_logging


def main():
    """Main example function."""
    print("ZerodhaWise - Portfolio Analysis Example")
    print("=" * 50)
    
    # Setup logging
    logger = setup_logging(__name__)
    
    try:
        # Initialize analyzers
        print("Initializing analyzers...")
        portfolio_analyzer = PortfolioAnalyzer()
        performance_analyzer = PerformanceAnalyzer()
        risk_analyzer = RiskAnalyzer()
        chart_generator = ChartGenerator()
        
        # Create sample data for demonstration
        print("Creating sample portfolio data...")
        sample_portfolio = create_sample_data()
        
        # Analyze portfolio
        print("Analyzing portfolio...")
        portfolio_analysis = portfolio_analyzer.analyze_portfolio(sample_portfolio)
        
        print(f"\nPortfolio Analysis Results:")
        print(f"Total Value: ₹{portfolio_analysis['total_value']:,.2f}")
        print(f"Total P&L: ₹{portfolio_analysis['total_pnl']:,.2f}")
        print(f"Number of Holdings: {portfolio_analysis['number_of_holdings']}")
        print(f"P&L Percentage: {portfolio_analysis['total_pnl_percentage']:.2f}%")
        
        # Show sector analysis
        print(f"\nSector Analysis:")
        for sector, data in portfolio_analysis['sector_analysis'].items():
            print(f"  {sector}: {data['percentage']:.1f}% (₹{data['total_value']:,.2f})")
        
        # Show top holdings
        print(f"\nTop Holdings:")
        for i, holding in enumerate(portfolio_analysis['top_holdings'][:5], 1):
            print(f"  {i}. {holding['tradingsymbol']}: ₹{float(holding['market_value']):,.2f}")
        
        # Risk analysis
        print(f"\nPerforming risk analysis...")
        risk_analysis = risk_analyzer.analyze_portfolio_risk(sample_portfolio)
        
        if 'error' not in risk_analysis:
            print(f"Risk Score: {risk_analysis['risk_score']:.2f}/10")
            print(f"Diversification Score: {risk_analysis['diversification_score']:.2f}/10")
            print(f"Portfolio Volatility: {risk_analysis['portfolio_volatility']:.2%}")
            print(f"95% VaR: {risk_analysis['var_95']:.2%}")
        
        # Diversification analysis
        print(f"\nPerforming diversification analysis...")
        diversification = risk_analyzer.analyze_diversification(sample_portfolio['holdings'])
        
        if 'error' not in diversification:
            print(f"Herfindahl-Hirschman Index: {diversification['herfindahl_hirschman_index']:.3f}")
            print(f"Effective Number of Stocks: {diversification['effective_number_of_stocks']:.1f}")
            
            print(f"\nDiversification Recommendations:")
            for rec in diversification['diversification_recommendations']:
                print(f"  - {rec}")
        
        # Generate charts
        print(f"\nGenerating charts...")
        chart_path = chart_generator.create_portfolio_summary_chart(sample_portfolio)
        if chart_path:
            print(f"Portfolio chart saved to: {chart_path}")
        
        # Generate reports
        print(f"\nGenerating reports...")
        portfolio_report = portfolio_analyzer.export_portfolio_report()
        print(f"Portfolio report saved to: {portfolio_report}")
        
        risk_report = risk_analyzer.generate_risk_report(sample_portfolio)
        print(f"Risk report saved to: {risk_report}")
        
        print(f"\nExample completed successfully!")
        print(f"Check the 'reports' directory for generated files.")
        
    except Exception as e:
        logger.error(f"Error in example: {str(e)}")
        print(f"Error: {str(e)}")
        return 1
    
    return 0


def demo_with_real_data():
    """Demonstrate usage with real Zerodha data (requires API credentials)."""
    print("\n" + "=" * 50)
    print("Real Data Demo (requires Zerodha API credentials)")
    print("=" * 50)
    
    try:
        # Initialize analyzer
        portfolio_analyzer = PortfolioAnalyzer()
        
        # Fetch real portfolio data
        print("Fetching portfolio data from Zerodha...")
        portfolio = portfolio_analyzer.get_portfolio()
        
        if portfolio and portfolio.get('holdings'):
            print(f"Successfully fetched portfolio with {len(portfolio['holdings'])} holdings")
            
            # Analyze portfolio
            analysis = portfolio_analyzer.analyze_portfolio(portfolio)
            
            print(f"\nReal Portfolio Analysis:")
            print(f"Total Value: ₹{analysis['total_value']:,.2f}")
            print(f"Total P&L: ₹{analysis['total_pnl']:,.2f}")
            print(f"Number of Holdings: {analysis['number_of_holdings']}")
            
            # Generate summary
            summary = portfolio_analyzer.get_portfolio_summary()
            print(f"\n{summary}")
            
        else:
            print("No portfolio data available. Please check your Zerodha API credentials.")
            print("You can set up your credentials in config/config.yaml")
            
    except Exception as e:
        print(f"Error fetching real data: {str(e)}")
        print("Make sure you have valid Zerodha API credentials configured.")


if __name__ == "__main__":
    # Run the example with sample data
    exit_code = main()
    
    # Optionally run with real data (uncomment if you have API credentials)
    # demo_with_real_data()
    
    sys.exit(exit_code) 