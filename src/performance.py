"""
Performance analysis module for ZerodhaWise.

This module provides comprehensive performance analysis including
returns calculation, risk metrics, and performance attribution.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from scipy import stats
from utils import load_config, setup_logging
from data import DataManager


class PerformanceAnalyzer:
    """
    Class for analyzing portfolio performance and calculating key metrics.
    
    This class provides methods to calculate various performance metrics
    including returns, risk measures, and performance attribution.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the PerformanceAnalyzer.
        
        Args:
            config_path: Path to configuration file. If None, uses default config.
        """
        self.config = load_config(config_path)
        self.logger = setup_logging(__name__)
        self.data_manager = DataManager(self.config)
    
    def calculate_returns(self, portfolio_data: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate various return metrics.
        
        Args:
            portfolio_data: DataFrame containing portfolio value over time.
            
        Returns:
            Dictionary containing return metrics.
        """
        if len(portfolio_data) < 2:
            return {'error': 'Insufficient data for return calculation'}
        
        # Calculate daily returns
        portfolio_data['daily_return'] = portfolio_data['total_value'].pct_change()
        
        # Remove NaN values
        returns = portfolio_data['daily_return'].dropna()
        
        if len(returns) == 0:
            return {'error': 'No valid return data available'}
        
        # Calculate metrics
        total_return = (portfolio_data['total_value'].iloc[-1] / portfolio_data['total_value'].iloc[0]) - 1
        avg_daily_return = returns.mean()
        annualized_return = (1 + avg_daily_return) ** 252 - 1
        
        # Calculate rolling returns
        rolling_30d = portfolio_data['total_value'].pct_change(30).iloc[-1]
        rolling_90d = portfolio_data['total_value'].pct_change(90).iloc[-1]
        
        return {
            'total_return': total_return,
            'avg_daily_return': avg_daily_return,
            'annualized_return': annualized_return,
            'rolling_30d_return': rolling_30d,
            'rolling_90d_return': rolling_90d,
            'volatility': returns.std() * np.sqrt(252),  # Annualized volatility
            'sharpe_ratio': self._calculate_sharpe_ratio(returns),
            'max_drawdown': self._calculate_max_drawdown(portfolio_data['total_value']),
            'calmar_ratio': self._calculate_calmar_ratio(annualized_return, portfolio_data['total_value'])
        }
    
    def calculate_risk_metrics(self, portfolio_data: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate risk metrics for the portfolio.
        
        Args:
            portfolio_data: DataFrame containing portfolio value over time.
            
        Returns:
            Dictionary containing risk metrics.
        """
        if len(portfolio_data) < 2:
            return {'error': 'Insufficient data for risk calculation'}
        
        returns = portfolio_data['total_value'].pct_change().dropna()
        
        if len(returns) == 0:
            return {'error': 'No valid return data available'}
        
        # Calculate risk metrics
        volatility = returns.std() * np.sqrt(252)  # Annualized
        var_95 = np.percentile(returns, 5)  # 95% VaR
        cvar_95 = returns[returns <= var_95].mean()  # 95% CVaR
        
        # Calculate downside deviation
        downside_returns = returns[returns < 0]
        downside_deviation = downside_returns.std() * np.sqrt(252) if len(downside_returns) > 0 else 0
        
        # Calculate beta (assuming market data available)
        beta = self._calculate_beta(returns)
        
        return {
            'volatility': volatility,
            'var_95': var_95,
            'cvar_95': cvar_95,
            'downside_deviation': downside_deviation,
            'beta': beta,
            'skewness': stats.skew(returns),
            'kurtosis': stats.kurtosis(returns),
            'var_99': np.percentile(returns, 1),  # 99% VaR
            'cvar_99': returns[returns <= np.percentile(returns, 1)].mean()
        }
    
    def calculate_performance_attribution(self, portfolio_data: pd.DataFrame, 
                                       benchmark_data: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        """
        Calculate performance attribution analysis.
        
        Args:
            portfolio_data: DataFrame containing portfolio value over time.
            benchmark_data: DataFrame containing benchmark data (optional).
            
        Returns:
            Dictionary containing performance attribution metrics.
        """
        if len(portfolio_data) < 2:
            return {'error': 'Insufficient data for attribution analysis'}
        
        portfolio_returns = portfolio_data['total_value'].pct_change().dropna()
        
        attribution = {
            'portfolio_metrics': self.calculate_returns(portfolio_data),
            'risk_metrics': self.calculate_risk_metrics(portfolio_data)
        }
        
        if benchmark_data is not None and len(benchmark_data) > 1:
            benchmark_returns = benchmark_data['value'].pct_change().dropna()
            
            # Align returns
            common_dates = portfolio_returns.index.intersection(benchmark_returns.index)
            if len(common_dates) > 0:
                portfolio_aligned = portfolio_returns.loc[common_dates]
                benchmark_aligned = benchmark_returns.loc[common_dates]
                
                # Calculate excess returns
                excess_returns = portfolio_aligned - benchmark_aligned
                
                attribution['benchmark_comparison'] = {
                    'excess_return': excess_returns.mean() * 252,
                    'tracking_error': excess_returns.std() * np.sqrt(252),
                    'information_ratio': (excess_returns.mean() / excess_returns.std()) * np.sqrt(252),
                    'correlation': portfolio_aligned.corr(benchmark_aligned),
                    'beta': self._calculate_beta(portfolio_aligned, benchmark_aligned)
                }
        
        return attribution
    
    def calculate_rolling_metrics(self, portfolio_data: pd.DataFrame, 
                                window: int = 30) -> pd.DataFrame:
        """
        Calculate rolling performance metrics.
        
        Args:
            portfolio_data: DataFrame containing portfolio value over time.
            window: Rolling window size in days.
            
        Returns:
            DataFrame containing rolling metrics.
        """
        if len(portfolio_data) < window:
            return pd.DataFrame()
        
        returns = portfolio_data['total_value'].pct_change().dropna()
        
        rolling_metrics = pd.DataFrame(index=returns.index)
        
        # Rolling returns
        rolling_metrics['rolling_return'] = returns.rolling(window).mean() * 252
        
        # Rolling volatility
        rolling_metrics['rolling_volatility'] = returns.rolling(window).std() * np.sqrt(252)
        
        # Rolling Sharpe ratio
        rolling_metrics['rolling_sharpe'] = (
            rolling_metrics['rolling_return'] / rolling_metrics['rolling_volatility']
        )
        
        # Rolling drawdown
        rolling_metrics['rolling_drawdown'] = self._calculate_rolling_drawdown(
            portfolio_data['total_value'], window
        )
        
        return rolling_metrics
    
    def generate_performance_report(self, portfolio_data: pd.DataFrame, 
                                  filename: Optional[str] = None) -> str:
        """
        Generate a comprehensive performance report.
        
        Args:
            portfolio_data: DataFrame containing portfolio value over time.
            filename: Output filename. If None, generates default name.
            
        Returns:
            Path to the generated report file.
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"performance_report_{timestamp}.txt"
        
        # Calculate all metrics
        returns_metrics = self.calculate_returns(portfolio_data)
        risk_metrics = self.calculate_risk_metrics(portfolio_data)
        
        # Generate report
        report = f"""
ZerodhaWise Performance Report
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
{'='*50}

RETURN METRICS:
{'='*20}
"""
        
        if 'error' not in returns_metrics:
            report += f"""
Total Return: {returns_metrics['total_return']:.2%}
Annualized Return: {returns_metrics['annualized_return']:.2%}
Average Daily Return: {returns_metrics['avg_daily_return']:.4%}
30-Day Rolling Return: {returns_metrics['rolling_30d_return']:.2%}
90-Day Rolling Return: {returns_metrics['rolling_90d_return']:.2%}
Sharpe Ratio: {returns_metrics['sharpe_ratio']:.3f}
Calmar Ratio: {returns_metrics['calmar_ratio']:.3f}
Maximum Drawdown: {returns_metrics['max_drawdown']:.2%}
"""
        else:
            report += f"Error: {returns_metrics['error']}\n"
        
        report += f"""
RISK METRICS:
{'='*20}
"""
        
        if 'error' not in risk_metrics:
            report += f"""
Volatility (Annualized): {risk_metrics['volatility']:.2%}
95% Value at Risk: {risk_metrics['var_95']:.2%}
95% Conditional VaR: {risk_metrics['cvar_95']:.2%}
Downside Deviation: {risk_metrics['downside_deviation']:.2%}
Beta: {risk_metrics['beta']:.3f}
Skewness: {risk_metrics['skewness']:.3f}
Kurtosis: {risk_metrics['kurtosis']:.3f}
99% Value at Risk: {risk_metrics['var_99']:.2%}
99% Conditional VaR: {risk_metrics['cvar_99']:.2%}
"""
        else:
            report += f"Error: {risk_metrics['error']}\n"
        
        # Save report
        import os
        os.makedirs('reports', exist_ok=True)
        filepath = os.path.join('reports', filename)
        
        with open(filepath, 'w') as f:
            f.write(report)
        
        self.logger.info(f"Performance report exported to {filepath}")
        return filepath
    
    def _calculate_sharpe_ratio(self, returns: pd.Series, risk_free_rate: float = 0.02) -> float:
        """Calculate Sharpe ratio."""
        if returns.std() == 0:
            return 0.0
        
        excess_returns = returns.mean() - (risk_free_rate / 252)
        return (excess_returns / returns.std()) * np.sqrt(252)
    
    def _calculate_max_drawdown(self, portfolio_values: pd.Series) -> float:
        """Calculate maximum drawdown."""
        peak = portfolio_values.expanding().max()
        drawdown = (portfolio_values - peak) / peak
        return drawdown.min()
    
    def _calculate_calmar_ratio(self, annualized_return: float, portfolio_values: pd.Series) -> float:
        """Calculate Calmar ratio."""
        max_drawdown = abs(self._calculate_max_drawdown(portfolio_values))
        return annualized_return / max_drawdown if max_drawdown > 0 else 0
    
    def _calculate_beta(self, portfolio_returns: pd.Series, 
                       market_returns: Optional[pd.Series] = None) -> float:
        """Calculate beta relative to market."""
        if market_returns is None:
            # Use a simple market proxy (you can replace this with actual market data)
            return 1.0
        
        # Align returns
        common_dates = portfolio_returns.index.intersection(market_returns.index)
        if len(common_dates) < 2:
            return 1.0
        
        portfolio_aligned = portfolio_returns.loc[common_dates]
        market_aligned = market_returns.loc[common_dates]
        
        # Calculate beta
        covariance = np.cov(portfolio_aligned, market_aligned)[0, 1]
        market_variance = np.var(market_aligned)
        
        return covariance / market_variance if market_variance > 0 else 1.0
    
    def _calculate_rolling_drawdown(self, portfolio_values: pd.Series, window: int) -> pd.Series:
        """Calculate rolling drawdown."""
        rolling_peak = portfolio_values.rolling(window).max()
        drawdown = (portfolio_values - rolling_peak) / rolling_peak
        return drawdown 