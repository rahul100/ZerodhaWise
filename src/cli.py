"""
Command-line interface for ZerodhaWise.

This module provides a command-line interface for the ZerodhaWise application,
allowing users to interact with the portfolio analysis tools.
"""

import argparse
import sys
import os
from typing import Optional
from datetime import datetime
import pandas as pd

from .portfolio import PortfolioAnalyzer
from .performance import PerformanceAnalyzer
from .risk import RiskAnalyzer
from .visualization import ChartGenerator
from .utils import load_config, setup_logging, create_sample_data


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Zerodhawise - Portfolio Analysis Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  zerodhawise portfolio --summary
  zerodhawise performance --days 30
  zerodhawise risk --analyze
  zerodhawise charts --all
  zerodhawise report --comprehensive
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Portfolio command
    portfolio_parser = subparsers.add_parser('portfolio', help='Portfolio analysis')
    portfolio_parser.add_argument('--summary', action='store_true', help='Show portfolio summary')
    portfolio_parser.add_argument('--details', action='store_true', help='Show detailed holdings')
    portfolio_parser.add_argument('--export', type=str, help='Export portfolio to file')
    portfolio_parser.add_argument('--config', type=str, help='Path to config file')
    
    # Performance command
    performance_parser = subparsers.add_parser('performance', help='Performance analysis')
    performance_parser.add_argument('--days', type=int, default=30, help='Number of days to analyze')
    performance_parser.add_argument('--metrics', action='store_true', help='Show performance metrics')
    performance_parser.add_argument('--export', type=str, help='Export performance report')
    performance_parser.add_argument('--config', type=str, help='Path to config file')
    
    # Risk command
    risk_parser = subparsers.add_parser('risk', help='Risk analysis')
    risk_parser.add_argument('--analyze', action='store_true', help='Analyze portfolio risk')
    risk_parser.add_argument('--diversification', action='store_true', help='Show diversification analysis')
    risk_parser.add_argument('--export', type=str, help='Export risk report')
    risk_parser.add_argument('--config', type=str, help='Path to config file')
    
    # Charts command
    charts_parser = subparsers.add_parser('charts', help='Generate charts')
    charts_parser.add_argument('--all', action='store_true', help='Generate all charts')
    charts_parser.add_argument('--portfolio', action='store_true', help='Generate portfolio charts')
    charts_parser.add_argument('--performance', action='store_true', help='Generate performance charts')
    charts_parser.add_argument('--risk', action='store_true', help='Generate risk charts')
    charts_parser.add_argument('--interactive', action='store_true', help='Generate interactive dashboard')
    charts_parser.add_argument('--config', type=str, help='Path to config file')
    
    # Report command
    report_parser = subparsers.add_parser('report', help='Generate reports')
    report_parser.add_argument('--comprehensive', action='store_true', help='Generate comprehensive report')
    report_parser.add_argument('--portfolio', action='store_true', help='Generate portfolio report')
    report_parser.add_argument('--performance', action='store_true', help='Generate performance report')
    report_parser.add_argument('--risk', action='store_true', help='Generate risk report')
    report_parser.add_argument('--output', type=str, help='Output directory for reports')
    report_parser.add_argument('--config', type=str, help='Path to config file')
    
    # Setup command
    setup_parser = subparsers.add_parser('setup', help='Setup and configuration')
    setup_parser.add_argument('--init', action='store_true', help='Initialize project structure')
    setup_parser.add_argument('--config', type=str, help='Path to config file')
    setup_parser.add_argument('--sample-data', action='store_true', help='Create sample data for testing')
    
    # Data command
    data_parser = subparsers.add_parser('data', help='Data management')
    data_parser.add_argument('--backup', action='store_true', help='Backup database')
    data_parser.add_argument('--restore', type=str, help='Restore database from backup')
    data_parser.add_argument('--cleanup', action='store_true', help='Clean up old data')
    data_parser.add_argument('--stats', action='store_true', help='Show database statistics')
    data_parser.add_argument('--config', type=str, help='Path to config file')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Setup logging
    config = load_config(args.config)
    logger = setup_logging(__name__, config)
    
    try:
        if args.command == 'portfolio':
            handle_portfolio_command(args, config)
        elif args.command == 'performance':
            handle_performance_command(args, config)
        elif args.command == 'risk':
            handle_risk_command(args, config)
        elif args.command == 'charts':
            handle_charts_command(args, config)
        elif args.command == 'report':
            handle_report_command(args, config)
        elif args.command == 'setup':
            handle_setup_command(args, config)
        elif args.command == 'data':
            handle_data_command(args, config)
        else:
            print(f"Unknown command: {args.command}")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Error executing command: {str(e)}")
        print(f"Error: {str(e)}")
        sys.exit(1)


def handle_portfolio_command(args, config):
    """Handle portfolio command."""
    analyzer = PortfolioAnalyzer(config)
    
    if args.summary:
        print("Fetching portfolio summary...")
        summary = analyzer.get_portfolio_summary()
        print(summary)
    
    elif args.details:
        print("Fetching portfolio details...")
        portfolio = analyzer.get_portfolio()
        analysis = analyzer.analyze_portfolio(portfolio)
        
        print(f"\nPortfolio Analysis:")
        print(f"Total Value: ₹{analysis['total_value']:,.2f}")
        print(f"Total P&L: ₹{analysis['total_pnl']:,.2f}")
        print(f"Number of Holdings: {analysis['number_of_holdings']}")
        
        print(f"\nDetailed Holdings:")
        for i, holding in enumerate(portfolio['holdings'], 1):
            print(f"{i}. {holding['tradingsymbol']} ({holding['exchange']})")
            print(f"   Quantity: {holding['quantity']}")
            print(f"   Market Value: ₹{float(holding['market_value']):,.2f}")
            print(f"   P&L: ₹{float(holding['pnl']):,.2f}")
            print()
    
    elif args.export:
        print("Exporting portfolio report...")
        filepath = analyzer.export_portfolio_report(args.export)
        print(f"Portfolio report exported to: {filepath}")
    
    else:
        print("Please specify an action: --summary, --details, or --export")


def handle_performance_command(args, config):
    """Handle performance command."""
    analyzer = PerformanceAnalyzer(config)
    portfolio_analyzer = PortfolioAnalyzer(config)
    
    # Get historical portfolio data
    portfolio_data = portfolio_analyzer.get_historical_portfolio(args.days)
    
    if portfolio_data.empty:
        print("No historical portfolio data available.")
        print("Please run portfolio analysis first to collect data.")
        return
    
    if args.metrics:
        print("Calculating performance metrics...")
        returns_metrics = analyzer.calculate_returns(portfolio_data)
        risk_metrics = analyzer.calculate_risk_metrics(portfolio_data)
        
        print(f"\nPerformance Metrics:")
        if 'error' not in returns_metrics:
            print(f"Total Return: {returns_metrics['total_return']:.2%}")
            print(f"Annualized Return: {returns_metrics['annualized_return']:.2%}")
            print(f"Sharpe Ratio: {returns_metrics['sharpe_ratio']:.3f}")
            print(f"Maximum Drawdown: {returns_metrics['max_drawdown']:.2%}")
        
        print(f"\nRisk Metrics:")
        if 'error' not in risk_metrics:
            print(f"Volatility: {risk_metrics['volatility']:.2%}")
            print(f"95% VaR: {risk_metrics['var_95']:.2%}")
            print(f"Beta: {risk_metrics['beta']:.3f}")
    
    elif args.export:
        print("Generating performance report...")
        filepath = analyzer.generate_performance_report(portfolio_data, args.export)
        print(f"Performance report exported to: {filepath}")
    
    else:
        print("Please specify an action: --metrics or --export")


def handle_risk_command(args, config):
    """Handle risk command."""
    analyzer = RiskAnalyzer(config)
    portfolio_analyzer = PortfolioAnalyzer(config)
    
    # Get portfolio data
    portfolio = portfolio_analyzer.get_portfolio()
    
    if args.analyze:
        print("Analyzing portfolio risk...")
        risk_analysis = analyzer.analyze_portfolio_risk(portfolio)
        
        if 'error' not in risk_analysis:
            print(f"\nRisk Analysis:")
            print(f"Risk Score: {risk_analysis['risk_score']:.2f}/10")
            print(f"Diversification Score: {risk_analysis['diversification_score']:.2f}/10")
            print(f"Portfolio Volatility: {risk_analysis['portfolio_volatility']:.2%}")
            print(f"95% VaR: {risk_analysis['var_95']:.2%}")
            print(f"99% VaR: {risk_analysis['var_99']:.2%}")
    
    elif args.diversification:
        print("Analyzing portfolio diversification...")
        diversification = analyzer.analyze_diversification(portfolio['holdings'])
        
        if 'error' not in diversification:
            print(f"\nDiversification Analysis:")
            print(f"Herfindahl-Hirschman Index: {diversification['herfindahl_hirschman_index']:.3f}")
            print(f"Effective Number of Stocks: {diversification['effective_number_of_stocks']:.1f}")
            
            print(f"\nSector Diversification:")
            for sector, data in diversification['sector_diversification'].items():
                print(f"- {sector}: {data['percentage']:.1f}% ({data['count']} stocks)")
            
            print(f"\nRecommendations:")
            for rec in diversification['diversification_recommendations']:
                print(f"- {rec}")
    
    elif args.export:
        print("Generating risk report...")
        filepath = analyzer.generate_risk_report(portfolio, args.export)
        print(f"Risk report exported to: {filepath}")
    
    else:
        print("Please specify an action: --analyze, --diversification, or --export")


def handle_charts_command(args, config):
    """Handle charts command."""
    generator = ChartGenerator(config)
    portfolio_analyzer = PortfolioAnalyzer(config)
    performance_analyzer = PerformanceAnalyzer(config)
    risk_analyzer = RiskAnalyzer(config)
    
    # Get data
    portfolio = portfolio_analyzer.get_portfolio()
    performance_data = portfolio_analyzer.get_historical_portfolio(30)
    risk_data = risk_analyzer.analyze_portfolio_risk(portfolio)
    
    if args.all or args.portfolio:
        print("Generating portfolio summary chart...")
        chart_path = generator.create_portfolio_summary_chart(portfolio)
        print(f"Portfolio chart saved to: {chart_path}")
    
    if args.all or args.performance:
        if not performance_data.empty:
            print("Generating performance chart...")
            chart_path = generator.create_performance_chart(performance_data)
            print(f"Performance chart saved to: {chart_path}")
        else:
            print("No performance data available for chart generation.")
    
    if args.all or args.risk:
        print("Generating risk analysis chart...")
        chart_path = generator.create_risk_analysis_chart(risk_data)
        print(f"Risk chart saved to: {chart_path}")
    
    if args.all or args.interactive:
        print("Generating interactive dashboard...")
        dashboard_path = generator.create_interactive_dashboard(
            portfolio, performance_data, risk_data
        )
        print(f"Interactive dashboard saved to: {dashboard_path}")
    
    if not any([args.all, args.portfolio, args.performance, args.risk, args.interactive]):
        print("Please specify which charts to generate: --all, --portfolio, --performance, --risk, or --interactive")


def handle_report_command(args, config):
    """Handle report command."""
    portfolio_analyzer = PortfolioAnalyzer(config)
    performance_analyzer = PerformanceAnalyzer(config)
    risk_analyzer = RiskAnalyzer(config)
    chart_generator = ChartGenerator(config)
    
    # Get data
    portfolio = portfolio_analyzer.get_portfolio()
    performance_data = portfolio_analyzer.get_historical_portfolio(30)
    risk_data = risk_analyzer.analyze_portfolio_risk(portfolio)
    
    output_dir = args.output or "reports"
    os.makedirs(output_dir, exist_ok=True)
    
    if args.comprehensive or args.portfolio:
        print("Generating portfolio report...")
        portfolio_report = portfolio_analyzer.export_portfolio_report()
        print(f"Portfolio report: {portfolio_report}")
    
    if args.comprehensive or args.performance:
        if not performance_data.empty:
            print("Generating performance report...")
            performance_report = performance_analyzer.generate_performance_report(performance_data)
            print(f"Performance report: {performance_report}")
        else:
            print("No performance data available for report generation.")
    
    if args.comprehensive or args.risk:
        print("Generating risk report...")
        risk_report = risk_analyzer.generate_risk_report(portfolio)
        print(f"Risk report: {risk_report}")
    
    if args.comprehensive:
        print("Generating comprehensive charts...")
        charts = chart_generator.generate_report_charts(portfolio, performance_data, risk_data)
        for chart_type, chart_path in charts.items():
            print(f"{chart_type} chart: {chart_path}")
    
    if not any([args.comprehensive, args.portfolio, args.performance, args.risk]):
        print("Please specify which reports to generate: --comprehensive, --portfolio, --performance, or --risk")


def handle_setup_command(args, config):
    """Handle setup command."""
    if args.init:
        print("Initializing ZerodhaWise project structure...")
        
        # Create directories
        directories = ['logs', 'data', 'reports', 'config']
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            print(f"Created directory: {directory}")
        
        # Create config file if it doesn't exist
        config_file = 'config/config.yaml'
        if not os.path.exists(config_file):
            import shutil
            shutil.copy('config/config.example.yaml', config_file)
            print(f"Created config file: {config_file}")
            print("Please update the config file with your Zerodha API credentials.")
        
        print("Project structure initialized successfully!")
    
    elif args.sample_data:
        print("Creating sample data for testing...")
        sample_data = create_sample_data()
        
        # Save sample data
        import json
        with open('data/sample_portfolio.json', 'w') as f:
            json.dump(sample_data, f, indent=2)
        
        print("Sample data created: data/sample_portfolio.json")
        print("You can use this data for testing the application.")
    
    else:
        print("Please specify an action: --init or --sample-data")


def handle_data_command(args, config):
    """Handle data command."""
    from .data import DataManager
    
    data_manager = DataManager(config)
    
    if args.backup:
        print("Creating database backup...")
        backup_path = f"data/backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        if data_manager.backup_database(backup_path):
            print(f"Database backed up to: {backup_path}")
        else:
            print("Backup failed.")
    
    elif args.restore:
        print(f"Restoring database from: {args.restore}")
        if data_manager.restore_database(args.restore):
            print("Database restored successfully.")
        else:
            print("Restore failed.")
    
    elif args.cleanup:
        print("Cleaning up old data...")
        deleted_count = data_manager.cleanup_old_data()
        print(f"Deleted {deleted_count} old records.")
    
    elif args.stats:
        print("Database statistics:")
        stats = data_manager.get_database_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")
    
    else:
        print("Please specify an action: --backup, --restore, --cleanup, or --stats")


if __name__ == "__main__":
    main() 