"""
Visualization module for ZerodhaWise.

This module provides chart generation and visualization functionality
for portfolio analysis and reporting.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import os
from .utils import load_config, setup_logging, format_currency, format_percentage


class ChartGenerator:
    """
    Class for generating charts and visualizations.
    
    This class provides methods to create various charts for
    portfolio analysis and reporting.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the ChartGenerator.
        
        Args:
            config_path: Path to configuration file. If None, uses default config.
        """
        self.config = load_config(config_path)
        self.logger = setup_logging(__name__)
        
        # Set style for matplotlib
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
    
    def create_portfolio_summary_chart(self, portfolio_data: Dict[str, Any], 
                                     save_path: Optional[str] = None) -> str:
        """
        Create a comprehensive portfolio summary chart.
        
        Args:
            portfolio_data: Dictionary containing portfolio data.
            save_path: Path to save the chart. If None, generates default path.
            
        Returns:
            Path to the saved chart.
        """
        try:
            holdings = portfolio_data.get('holdings', [])
            if not holdings:
                self.logger.warning("No holdings data available for chart generation")
                return ""
            
            # Create subplots
            fig, axes = plt.subplots(2, 2, figsize=(15, 12))
            fig.suptitle('Portfolio Summary Dashboard', fontsize=16, fontweight='bold')
            
            # 1. Portfolio Composition (Pie Chart)
            self._create_composition_chart(holdings, axes[0, 0])
            
            # 2. P&L Distribution (Bar Chart)
            self._create_pnl_distribution_chart(holdings, axes[0, 1])
            
            # 3. Sector Allocation (Bar Chart)
            self._create_sector_allocation_chart(holdings, axes[1, 0])
            
            # 4. Top Holdings (Horizontal Bar Chart)
            self._create_top_holdings_chart(holdings, axes[1, 1])
            
            plt.tight_layout()
            
            # Save chart
            if save_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                save_path = f"reports/portfolio_summary_{timestamp}.png"
            
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            self.logger.info(f"Portfolio summary chart saved to {save_path}")
            return save_path
            
        except Exception as e:
            self.logger.error(f"Error creating portfolio summary chart: {str(e)}")
            return ""
    
    def create_performance_chart(self, portfolio_data: pd.DataFrame, 
                               save_path: Optional[str] = None) -> str:
        """
        Create portfolio performance chart.
        
        Args:
            portfolio_data: DataFrame containing historical portfolio data.
            save_path: Path to save the chart. If None, generates default path.
            
        Returns:
            Path to the saved chart.
        """
        try:
            if portfolio_data.empty:
                self.logger.warning("No portfolio data available for performance chart")
                return ""
            
            fig, axes = plt.subplots(2, 1, figsize=(15, 10))
            fig.suptitle('Portfolio Performance Analysis', fontsize=16, fontweight='bold')
            
            # 1. Portfolio Value Over Time
            self._create_portfolio_value_chart(portfolio_data, axes[0])
            
            # 2. Returns Distribution
            self._create_returns_distribution_chart(portfolio_data, axes[1])
            
            plt.tight_layout()
            
            # Save chart
            if save_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                save_path = f"reports/performance_analysis_{timestamp}.png"
            
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            self.logger.info(f"Performance chart saved to {save_path}")
            return save_path
            
        except Exception as e:
            self.logger.error(f"Error creating performance chart: {str(e)}")
            return ""
    
    def create_risk_analysis_chart(self, risk_data: Dict[str, Any], 
                                 save_path: Optional[str] = None) -> str:
        """
        Create risk analysis chart.
        
        Args:
            risk_data: Dictionary containing risk analysis data.
            save_path: Path to save the chart. If None, generates default path.
            
        Returns:
            Path to the saved chart.
        """
        try:
            fig, axes = plt.subplots(2, 2, figsize=(15, 12))
            fig.suptitle('Risk Analysis Dashboard', fontsize=16, fontweight='bold')
            
            # 1. Risk Score
            self._create_risk_score_chart(risk_data, axes[0, 0])
            
            # 2. Diversification Score
            self._create_diversification_chart(risk_data, axes[0, 1])
            
            # 3. Concentration Risk
            self._create_concentration_chart(risk_data, axes[1, 0])
            
            # 4. Sector Risk
            self._create_sector_risk_chart(risk_data, axes[1, 1])
            
            plt.tight_layout()
            
            # Save chart
            if save_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                save_path = f"reports/risk_analysis_{timestamp}.png"
            
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            self.logger.info(f"Risk analysis chart saved to {save_path}")
            return save_path
            
        except Exception as e:
            self.logger.error(f"Error creating risk analysis chart: {str(e)}")
            return ""
    
    def create_interactive_dashboard(self, portfolio_data: Dict[str, Any], 
                                   performance_data: pd.DataFrame,
                                   risk_data: Dict[str, Any]) -> str:
        """
        Create an interactive Plotly dashboard.
        
        Args:
            portfolio_data: Dictionary containing portfolio data.
            performance_data: DataFrame containing performance data.
            risk_data: Dictionary containing risk data.
            
        Returns:
            Path to the saved HTML dashboard.
        """
        try:
            # Create subplots
            fig = make_subplots(
                rows=3, cols=2,
                subplot_titles=('Portfolio Composition', 'P&L Distribution',
                              'Performance Over Time', 'Risk Metrics',
                              'Sector Allocation', 'Top Holdings'),
                specs=[[{"type": "pie"}, {"type": "bar"}],
                       [{"type": "scatter"}, {"type": "bar"}],
                       [{"type": "bar"}, {"type": "bar"}]]
            )
            
            holdings = portfolio_data.get('holdings', [])
            
            # 1. Portfolio Composition (Pie Chart)
            if holdings:
                symbols = [h['tradingsymbol'] for h in holdings]
                values = [float(h['market_value']) for h in holdings]
                
                fig.add_trace(
                    go.Pie(labels=symbols, values=values, name="Composition"),
                    row=1, col=1
                )
            
            # 2. P&L Distribution (Bar Chart)
            if holdings:
                symbols = [h['tradingsymbol'] for h in holdings]
                pnl_values = [float(h['pnl']) for h in holdings]
                colors = ['green' if pnl >= 0 else 'red' for pnl in pnl_values]
                
                fig.add_trace(
                    go.Bar(x=symbols, y=pnl_values, marker_color=colors, name="P&L"),
                    row=1, col=2
                )
            
            # 3. Performance Over Time (Line Chart)
            if not performance_data.empty:
                fig.add_trace(
                    go.Scatter(x=performance_data.index, y=performance_data['total_value'],
                              mode='lines', name="Portfolio Value"),
                    row=2, col=1
                )
            
            # 4. Risk Metrics (Bar Chart)
            if risk_data:
                risk_metrics = ['Risk Score', 'Diversification Score']
                risk_values = [
                    risk_data.get('risk_score', 0),
                    risk_data.get('diversification_score', 0)
                ]
                
                fig.add_trace(
                    go.Bar(x=risk_metrics, y=risk_values, name="Risk Metrics"),
                    row=2, col=2
                )
            
            # 5. Sector Allocation (Bar Chart)
            if holdings:
                sector_data = {}
                for holding in holdings:
                    sector = holding.get('sector', 'Unknown')
                    market_value = float(holding['market_value'])
                    sector_data[sector] = sector_data.get(sector, 0) + market_value
                
                sectors = list(sector_data.keys())
                sector_values = list(sector_data.values())
                
                fig.add_trace(
                    go.Bar(x=sectors, y=sector_values, name="Sector Allocation"),
                    row=3, col=1
                )
            
            # 6. Top Holdings (Bar Chart)
            if holdings:
                # Get top 10 holdings by market value
                sorted_holdings = sorted(holdings, key=lambda x: float(x['market_value']), reverse=True)[:10]
                symbols = [h['tradingsymbol'] for h in sorted_holdings]
                values = [float(h['market_value']) for h in sorted_holdings]
                
                fig.add_trace(
                    go.Bar(x=symbols, y=values, name="Top Holdings"),
                    row=3, col=2
                )
            
            # Update layout
            fig.update_layout(
                title_text="ZerodhaWise Portfolio Dashboard",
                showlegend=False,
                height=1200
            )
            
            # Save dashboard
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = f"reports/interactive_dashboard_{timestamp}.html"
            
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            fig.write_html(save_path)
            
            self.logger.info(f"Interactive dashboard saved to {save_path}")
            return save_path
            
        except Exception as e:
            self.logger.error(f"Error creating interactive dashboard: {str(e)}")
            return ""
    
    def _create_composition_chart(self, holdings: List[Dict[str, Any]], ax):
        """Create portfolio composition pie chart."""
        if not holdings:
            return
        
        symbols = [h['tradingsymbol'] for h in holdings]
        values = [float(h['market_value']) for h in holdings]
        
        ax.pie(values, labels=symbols, autopct='%1.1f%%', startangle=90)
        ax.set_title('Portfolio Composition')
    
    def _create_pnl_distribution_chart(self, holdings: List[Dict[str, Any]], ax):
        """Create P&L distribution bar chart."""
        if not holdings:
            return
        
        symbols = [h['tradingsymbol'] for h in holdings]
        pnl_values = [float(h['pnl']) for h in holdings]
        colors = ['green' if pnl >= 0 else 'red' for pnl in pnl_values]
        
        bars = ax.bar(symbols, pnl_values, color=colors)
        ax.set_title('P&L Distribution')
        ax.set_ylabel('P&L (₹)')
        ax.tick_params(axis='x', rotation=45)
        
        # Add value labels on bars
        for bar, value in zip(bars, pnl_values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{value:,.0f}', ha='center', va='bottom' if height >= 0 else 'top')
    
    def _create_sector_allocation_chart(self, holdings: List[Dict[str, Any]], ax):
        """Create sector allocation bar chart."""
        if not holdings:
            return
        
        sector_data = {}
        for holding in holdings:
            sector = holding.get('sector', 'Unknown')
            market_value = float(holding['market_value'])
            sector_data[sector] = sector_data.get(sector, 0) + market_value
        
        sectors = list(sector_data.keys())
        values = list(sector_data.values())
        
        bars = ax.bar(sectors, values)
        ax.set_title('Sector Allocation')
        ax.set_ylabel('Market Value (₹)')
        ax.tick_params(axis='x', rotation=45)
        
        # Add value labels on bars
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{value:,.0f}', ha='center', va='bottom')
    
    def _create_top_holdings_chart(self, holdings: List[Dict[str, Any]], ax):
        """Create top holdings horizontal bar chart."""
        if not holdings:
            return
        
        # Get top 10 holdings by market value
        sorted_holdings = sorted(holdings, key=lambda x: float(x['market_value']), reverse=True)[:10]
        symbols = [h['tradingsymbol'] for h in sorted_holdings]
        values = [float(h['market_value']) for h in sorted_holdings]
        
        bars = ax.barh(symbols, values)
        ax.set_title('Top Holdings by Market Value')
        ax.set_xlabel('Market Value (₹)')
        
        # Add value labels on bars
        for bar, value in zip(bars, values):
            width = bar.get_width()
            ax.text(width, bar.get_y() + bar.get_height()/2.,
                   f'{value:,.0f}', ha='left', va='center')
    
    def _create_portfolio_value_chart(self, portfolio_data: pd.DataFrame, ax):
        """Create portfolio value over time chart."""
        if portfolio_data.empty:
            return
        
        ax.plot(portfolio_data.index, portfolio_data['total_value'], linewidth=2)
        ax.set_title('Portfolio Value Over Time')
        ax.set_ylabel('Portfolio Value (₹)')
        ax.grid(True, alpha=0.3)
        
        # Format y-axis labels
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/1000:.0f}K'))
    
    def _create_returns_distribution_chart(self, portfolio_data: pd.DataFrame, ax):
        """Create returns distribution chart."""
        if portfolio_data.empty or len(portfolio_data) < 2:
            return
        
        returns = portfolio_data['total_value'].pct_change().dropna()
        
        ax.hist(returns, bins=30, alpha=0.7, edgecolor='black')
        ax.set_title('Returns Distribution')
        ax.set_xlabel('Daily Returns')
        ax.set_ylabel('Frequency')
        ax.axvline(returns.mean(), color='red', linestyle='--', label=f'Mean: {returns.mean():.3f}')
        ax.legend()
    
    def _create_risk_score_chart(self, risk_data: Dict[str, Any], ax):
        """Create risk score chart."""
        risk_score = risk_data.get('risk_score', 0)
        
        # Create gauge chart
        ax.pie([risk_score, 10-risk_score], labels=['Risk', 'Safe'], 
               colors=['red', 'lightgray'], startangle=90)
        ax.set_title(f'Risk Score: {risk_score:.1f}/10')
    
    def _create_diversification_chart(self, risk_data: Dict[str, Any], ax):
        """Create diversification score chart."""
        div_score = risk_data.get('diversification_score', 0)
        
        # Create gauge chart
        ax.pie([div_score, 10-div_score], labels=['Diversified', 'Concentrated'], 
               colors=['green', 'lightgray'], startangle=90)
        ax.set_title(f'Diversification Score: {div_score:.1f}/10')
    
    def _create_concentration_chart(self, risk_data: Dict[str, Any], ax):
        """Create concentration risk chart."""
        concentration_data = risk_data.get('concentration_risk', {})
        
        if concentration_data:
            metrics = ['Top 5 Concentration', 'Max Single Stock']
            values = [
                concentration_data.get('top_5_concentration', 0),
                concentration_data.get('max_single_stock_concentration', 0)
            ]
            
            bars = ax.bar(metrics, values, color=['orange', 'red'])
            ax.set_title('Concentration Risk')
            ax.set_ylabel('Percentage (%)')
            ax.set_ylim(0, 100)
            
            # Add value labels
            for bar, value in zip(bars, values):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{value:.1f}%', ha='center', va='bottom')
    
    def _create_sector_risk_chart(self, risk_data: Dict[str, Any], ax):
        """Create sector risk chart."""
        sector_data = risk_data.get('sector_risk', {})
        
        if sector_data and 'sector_concentrations' in sector_data:
            sectors = list(sector_data['sector_concentrations'].keys())
            percentages = [data['percentage'] for data in sector_data['sector_concentrations'].values()]
            
            bars = ax.bar(sectors, percentages)
            ax.set_title('Sector Concentration')
            ax.set_ylabel('Percentage (%)')
            ax.tick_params(axis='x', rotation=45)
            
            # Add value labels
            for bar, value in zip(bars, percentages):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{value:.1f}%', ha='center', va='bottom')
    
    def generate_report_charts(self, portfolio_data: Dict[str, Any],
                             performance_data: pd.DataFrame,
                             risk_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate all charts for a comprehensive report.
        
        Args:
            portfolio_data: Dictionary containing portfolio data.
            performance_data: DataFrame containing performance data.
            risk_data: Dictionary containing risk data.
            
        Returns:
            Dictionary containing paths to generated charts.
        """
        charts = {}
        
        try:
            # Generate portfolio summary chart
            charts['portfolio_summary'] = self.create_portfolio_summary_chart(portfolio_data)
            
            # Generate performance chart
            if not performance_data.empty:
                charts['performance'] = self.create_performance_chart(performance_data)
            
            # Generate risk analysis chart
            if risk_data:
                charts['risk_analysis'] = self.create_risk_analysis_chart(risk_data)
            
            # Generate interactive dashboard
            charts['interactive_dashboard'] = self.create_interactive_dashboard(
                portfolio_data, performance_data, risk_data
            )
            
            self.logger.info(f"Generated {len(charts)} charts for report")
            return charts
            
        except Exception as e:
            self.logger.error(f"Error generating report charts: {str(e)}")
            return {} 