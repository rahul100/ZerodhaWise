"""
Risk analysis module for ZerodhaWise.

This module provides comprehensive risk analysis including
portfolio risk assessment, diversification analysis, and risk metrics.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from scipy import stats
from sklearn.decomposition import PCA
from utils import load_config, setup_logging
from data import DataManager


class RiskAnalyzer:
    """
    Class for analyzing portfolio risk and diversification.
    
    This class provides methods to calculate various risk metrics
    and analyze portfolio diversification.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the RiskAnalyzer.
        
        Args:
            config_path: Path to configuration file. If None, uses default config.
        """
        self.config = load_config(config_path)
        self.logger = setup_logging(__name__)
        self.data_manager = DataManager(self.config)
    
    def _calculate_market_value(self, holding: Dict[str, Any]) -> float:
        """Calculate market value from quantity and close_price."""
        if 'market_value' in holding:
            return float(holding['market_value'])
        else:
            return float(holding['quantity']) * float(holding['close_price'])
    
    def analyze_portfolio_risk(self, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze overall portfolio risk.
        
        Args:
            portfolio_data: Dictionary containing portfolio holdings and data.
            
        Returns:
            Dictionary containing comprehensive risk analysis.
        """
        holdings = portfolio_data.get('holdings', [])
        
        if not holdings:
            return {'error': 'No holdings data available'}
        
        # Calculate basic risk metrics
        concentration_risk = self._calculate_concentration_risk(holdings)
        sector_risk = self._calculate_sector_risk(holdings)
        correlation_risk = self._calculate_correlation_risk(holdings)
        volatility_analysis = self._calculate_volatility_analysis(holdings)
        
        # Calculate portfolio-level risk metrics
        total_value = sum(self._calculate_market_value(holding) for holding in holdings)
        total_pnl = sum(float(holding['pnl']) for holding in holdings)
        
        risk_metrics = {
            'concentration_risk': concentration_risk,
            'sector_risk': sector_risk,
            'correlation_risk': correlation_risk,
            'volatility_analysis': volatility_analysis,
            'total_portfolio_value': total_value,
            'total_pnl': total_pnl,
            'portfolio_volatility': self._calculate_portfolio_volatility(holdings),
            'var_95': self._calculate_portfolio_var(holdings, 0.05),
            'var_99': self._calculate_portfolio_var(holdings, 0.01),
            'max_drawdown_risk': self._calculate_max_drawdown_risk(holdings),
            'diversification_score': self._calculate_diversification_score(holdings),
            'risk_score': self._calculate_overall_risk_score(holdings)
        }
        
        return risk_metrics
    
    def analyze_diversification(self, holdings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze portfolio diversification.
        
        Args:
            holdings: List of portfolio holdings.
            
        Returns:
            Dictionary containing diversification analysis.
        """
        if not holdings:
            return {'error': 'No holdings data available'}
        
        # Sector diversification
        sector_diversification = self._analyze_sector_diversification(holdings)
        
        # Stock concentration
        stock_concentration = self._analyze_stock_concentration(holdings)
        
        # Market cap diversification
        market_cap_diversification = self._analyze_market_cap_diversification(holdings)
        
        # Herfindahl-Hirschman Index
        hhi = self._calculate_hhi(holdings)
        
        # Effective number of stocks
        effective_stocks = self._calculate_effective_stocks(holdings)
        
        return {
            'sector_diversification': sector_diversification,
            'stock_concentration': stock_concentration,
            'market_cap_diversification': market_cap_diversification,
            'herfindahl_hirschman_index': hhi,
            'effective_number_of_stocks': effective_stocks,
            'diversification_recommendations': self._generate_diversification_recommendations(holdings)
        }
    
    def calculate_risk_metrics(self, holdings: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Calculate comprehensive risk metrics for portfolio holdings.
        
        Args:
            holdings: List of portfolio holdings.
            
        Returns:
            Dictionary containing risk metrics.
        """
        if not holdings:
            return {'error': 'No holdings data available'}
        
        # Calculate individual stock risk metrics
        stock_risks = []
        for holding in holdings:
            market_value = self._calculate_market_value(holding)
            pnl = float(holding['pnl'])
            
            # Calculate risk metrics for each stock
            stock_risk = {
                'symbol': holding['tradingsymbol'],
                'market_value': market_value,
                'pnl': pnl,
                'pnl_percentage': (pnl / market_value * 100) if market_value > 0 else 0,
                'weight': market_value / sum(self._calculate_market_value(h) for h in holdings),
                'volatility': self._estimate_stock_volatility(holding),
                'var_95': self._estimate_stock_var(holding, 0.05),
                'var_99': self._estimate_stock_var(holding, 0.01)
            }
            stock_risks.append(stock_risk)
        
        # Calculate portfolio-level metrics
        total_value = sum(self._calculate_market_value(h) for h in holdings)
        total_pnl = sum(float(h['pnl']) for h in holdings)
        
        # Portfolio volatility (weighted average)
        portfolio_volatility = sum(
            stock_risk['weight'] * stock_risk['volatility'] 
            for stock_risk in stock_risks
        )
        
        # Portfolio VaR
        portfolio_var_95 = sum(
            stock_risk['weight'] * stock_risk['var_95'] 
            for stock_risk in stock_risks
        )
        
        portfolio_var_99 = sum(
            stock_risk['weight'] * stock_risk['var_99'] 
            for stock_risk in stock_risks
        )
        
        return {
            'total_portfolio_value': total_value,
            'total_pnl': total_pnl,
            'portfolio_volatility': portfolio_volatility,
            'portfolio_var_95': portfolio_var_95,
            'portfolio_var_99': portfolio_var_99,
            'stock_risks': stock_risks,
            'risk_concentration': self._calculate_risk_concentration(stock_risks),
            'tail_risk': self._calculate_tail_risk(stock_risks)
        }
    
    def generate_risk_report(self, portfolio_data: Dict[str, Any], 
                           filename: Optional[str] = None) -> str:
        """
        Generate a comprehensive risk analysis report.
        
        Args:
            portfolio_data: Dictionary containing portfolio data.
            filename: Output filename. If None, generates default name.
            
        Returns:
            Path to the generated report file.
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"risk_report_{timestamp}.txt"
        
        # Calculate risk metrics
        risk_analysis = self.analyze_portfolio_risk(portfolio_data)
        diversification_analysis = self.analyze_diversification(portfolio_data.get('holdings', []))
        risk_metrics = self.calculate_risk_metrics(portfolio_data.get('holdings', []))
        
        # Generate report
        report = f"""
ZerodhaWise Risk Analysis Report
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
{'='*50}

PORTFOLIO RISK OVERVIEW:
{'='*30}
"""
        
        if 'error' not in risk_analysis:
            report += f"""
Total Portfolio Value: ₹{risk_analysis['total_portfolio_value']:,.2f}
Total P&L: ₹{risk_analysis['total_pnl']:,.2f}
Portfolio Volatility: {risk_analysis['portfolio_volatility']:.2%}
95% Value at Risk: {risk_analysis['var_95']:.2%}
99% Value at Risk: {risk_analysis['var_99']:.2%}
Risk Score: {risk_analysis['risk_score']:.2f}/10
Diversification Score: {risk_analysis['diversification_score']:.2f}/10
"""
        else:
            report += f"Error: {risk_analysis['error']}\n"
        
        report += f"""
DIVERSIFICATION ANALYSIS:
{'='*30}
"""
        
        if 'error' not in diversification_analysis:
            report += f"""
Herfindahl-Hirschman Index: {diversification_analysis['herfindahl_hirschman_index']:.3f}
Effective Number of Stocks: {diversification_analysis['effective_number_of_stocks']:.1f}
"""
            
            # Add sector diversification
            if 'sector_diversification' in diversification_analysis:
                sectors = diversification_analysis['sector_diversification']
                report += f"\nSector Diversification:\n"
                for sector, data in sectors.items():
                    report += f"- {sector}: {data['percentage']:.1f}% ({data['count']} stocks)\n"
        else:
            report += f"Error: {diversification_analysis['error']}\n"
        
        report += f"""
RISK RECOMMENDATIONS:
{'='*30}
"""
        
        if 'diversification_recommendations' in diversification_analysis:
            recommendations = diversification_analysis['diversification_recommendations']
            for rec in recommendations:
                report += f"- {rec}\n"
        
        # Save report
        import os
        os.makedirs('reports', exist_ok=True)
        filepath = os.path.join('reports', filename)
        
        with open(filepath, 'w') as f:
            f.write(report)
        
        self.logger.info(f"Risk report exported to {filepath}")
        return filepath
    
    def _calculate_concentration_risk(self, holdings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate concentration risk metrics."""
        if not holdings:
            return {}
        
        total_value = sum(self._calculate_market_value(h) for h in holdings)
        
        # Top 5 concentration
        sorted_holdings = sorted(holdings, key=lambda x: self._calculate_market_value(x), reverse=True)
        top_5_value = sum(self._calculate_market_value(h) for h in sorted_holdings[:5])
        top_5_concentration = (top_5_value / total_value * 100) if total_value > 0 else 0
        
        # Single stock concentration
        max_single_stock = max(self._calculate_market_value(h) for h in holdings)
        max_single_concentration = (max_single_stock / total_value * 100) if total_value > 0 else 0
        
        return {
            'top_5_concentration': top_5_concentration,
            'max_single_stock_concentration': max_single_concentration,
            'concentration_risk_level': self._assess_concentration_risk(top_5_concentration)
        }
    
    def _calculate_sector_risk(self, holdings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate sector-based risk metrics."""
        sector_data = {}
        
        for holding in holdings:
            sector = holding.get('sector', 'Unknown')
            market_value = self._calculate_market_value(holding)
            
            if sector not in sector_data:
                sector_data[sector] = {'total_value': 0, 'count': 0}
            
            sector_data[sector]['total_value'] += market_value
            sector_data[sector]['count'] += 1
        
        total_value = sum(data['total_value'] for data in sector_data.values())
        
        # Calculate sector concentrations
        sector_concentrations = {}
        for sector, data in sector_data.items():
            sector_concentrations[sector] = {
                'percentage': (data['total_value'] / total_value * 100) if total_value > 0 else 0,
                'count': data['count'],
                'total_value': data['total_value']
            }
        
        # Find highest sector concentration
        max_sector_concentration = max(
            data['percentage'] for data in sector_concentrations.values()
        ) if sector_concentrations else 0
        
        return {
            'sector_concentrations': sector_concentrations,
            'max_sector_concentration': max_sector_concentration,
            'sector_risk_level': self._assess_sector_risk(max_sector_concentration)
        }
    
    def _calculate_correlation_risk(self, holdings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate correlation-based risk metrics."""
        # This is a simplified correlation analysis
        # In a real implementation, you would need historical price data
        
        return {
            'correlation_risk_level': 'Medium',  # Placeholder
            'recommendation': 'Consider historical correlation analysis for better risk assessment'
        }
    
    def _calculate_volatility_analysis(self, holdings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate volatility-based risk metrics."""
        if not holdings:
            return {}
        
        # Calculate weighted average volatility
        total_value = sum(self._calculate_market_value(h) for h in holdings)
        weighted_volatility = 0
        
        for holding in holdings:
            weight = self._calculate_market_value(holding) / total_value if total_value > 0 else 0
            # Estimate volatility (in real implementation, use historical data)
            estimated_volatility = 0.25  # Placeholder - 25% annual volatility
            weighted_volatility += weight * estimated_volatility
        
        return {
            'portfolio_volatility': weighted_volatility,
            'volatility_risk_level': self._assess_volatility_risk(weighted_volatility)
        }
    
    def _calculate_portfolio_volatility(self, holdings: List[Dict[str, Any]]) -> float:
        """Calculate portfolio volatility."""
        # Simplified calculation - in real implementation, use historical data
        return 0.20  # Placeholder - 20% annual volatility
    
    def _calculate_portfolio_var(self, holdings: List[Dict[str, Any]], confidence_level: float) -> float:
        """Calculate portfolio Value at Risk."""
        # Simplified VaR calculation
        portfolio_volatility = self._calculate_portfolio_volatility(holdings)
        var_factor = stats.norm.ppf(confidence_level)
        return portfolio_volatility * var_factor
    
    def _calculate_max_drawdown_risk(self, holdings: List[Dict[str, Any]]) -> float:
        """Calculate maximum drawdown risk."""
        # Simplified calculation
        return 0.15  # Placeholder - 15% max drawdown
    
    def _calculate_diversification_score(self, holdings: List[Dict[str, Any]]) -> float:
        """Calculate diversification score (0-10)."""
        if not holdings:
            return 0.0
        
        # Calculate HHI
        total_value = sum(self._calculate_market_value(h) for h in holdings)
        hhi = sum((self._calculate_market_value(h) / total_value) ** 2 for h in holdings) if total_value > 0 else 1
        
        # Convert HHI to diversification score (0-10)
        # Lower HHI = higher diversification
        diversification_score = max(0, 10 - (hhi * 10))
        
        return diversification_score
    
    def _calculate_overall_risk_score(self, holdings: List[Dict[str, Any]]) -> float:
        """Calculate overall risk score (0-10)."""
        if not holdings:
            return 10.0  # Maximum risk if no holdings
        
        # Combine various risk factors
        concentration_risk = self._calculate_concentration_risk(holdings)
        sector_risk = self._calculate_sector_risk(holdings)
        volatility_risk = self._calculate_volatility_analysis(holdings)
        
        # Calculate weighted risk score
        risk_score = 0
        weights = {'concentration': 0.3, 'sector': 0.3, 'volatility': 0.4}
        
        # Concentration risk
        if 'top_5_concentration' in concentration_risk:
            concentration_score = min(10, concentration_risk['top_5_concentration'] / 10)
            risk_score += weights['concentration'] * concentration_score
        
        # Sector risk
        if 'max_sector_concentration' in sector_risk:
            sector_score = min(10, sector_risk['max_sector_concentration'] / 10)
            risk_score += weights['sector'] * sector_score
        
        # Volatility risk
        if 'portfolio_volatility' in volatility_risk:
            volatility_score = min(10, volatility_risk['portfolio_volatility'] * 40)  # Scale to 0-10
            risk_score += weights['volatility'] * volatility_score
        
        return min(10, risk_score)
    
    def _analyze_sector_diversification(self, holdings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze sector diversification."""
        sector_data = {}
        
        for holding in holdings:
            sector = holding.get('sector', 'Unknown')
            market_value = self._calculate_market_value(holding)
            
            if sector not in sector_data:
                sector_data[sector] = {'total_value': 0, 'count': 0}
            
            sector_data[sector]['total_value'] += market_value
            sector_data[sector]['count'] += 1
        
        total_value = sum(data['total_value'] for data in sector_data.values())
        
        for sector in sector_data:
            sector_data[sector]['percentage'] = (
                sector_data[sector]['total_value'] / total_value * 100
            ) if total_value > 0 else 0
        
        return sector_data
    
    def _analyze_stock_concentration(self, holdings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze stock concentration."""
        if not holdings:
            return {}
        
        total_value = sum(self._calculate_market_value(h) for h in holdings)
        
        # Calculate concentration metrics
        sorted_holdings = sorted(holdings, key=lambda x: self._calculate_market_value(x), reverse=True)
        
        concentration_metrics = {
            'top_1_concentration': (self._calculate_market_value(sorted_holdings[0]) / total_value * 100) if total_value > 0 else 0,
            'top_3_concentration': (sum(self._calculate_market_value(h) for h in sorted_holdings[:3]) / total_value * 100) if total_value > 0 else 0,
            'top_5_concentration': (sum(self._calculate_market_value(h) for h in sorted_holdings[:5]) / total_value * 100) if total_value > 0 else 0,
            'number_of_stocks': len(holdings)
        }
        
        return concentration_metrics
    
    def _analyze_market_cap_diversification(self, holdings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze market cap diversification."""
        # Simplified analysis - in real implementation, you would have market cap data
        return {
            'large_cap_percentage': 60.0,  # Placeholder
            'mid_cap_percentage': 30.0,    # Placeholder
            'small_cap_percentage': 10.0   # Placeholder
        }
    
    def _calculate_hhi(self, holdings: List[Dict[str, Any]]) -> float:
        """Calculate Herfindahl-Hirschman Index."""
        if not holdings:
            return 1.0  # Maximum concentration
        
        total_value = sum(self._calculate_market_value(h) for h in holdings)
        
        if total_value == 0:
            return 1.0
        
        hhi = sum((self._calculate_market_value(h) / total_value) ** 2 for h in holdings)
        return hhi
    
    def _calculate_effective_stocks(self, holdings: List[Dict[str, Any]]) -> float:
        """Calculate effective number of stocks."""
        hhi = self._calculate_hhi(holdings)
        return 1 / hhi if hhi > 0 else 0
    
    def _generate_diversification_recommendations(self, holdings: List[Dict[str, Any]]) -> List[str]:
        """Generate diversification recommendations."""
        recommendations = []
        
        # Analyze concentration
        concentration_risk = self._calculate_concentration_risk(holdings)
        if 'top_5_concentration' in concentration_risk:
            if concentration_risk['top_5_concentration'] > 70:
                recommendations.append("Consider reducing concentration in top 5 holdings")
        
        # Analyze sector concentration
        sector_risk = self._calculate_sector_risk(holdings)
        if 'max_sector_concentration' in sector_risk:
            if sector_risk['max_sector_concentration'] > 40:
                recommendations.append("Consider diversifying across more sectors")
        
        # Analyze number of stocks
        if len(holdings) < 10:
            recommendations.append("Consider increasing the number of stocks for better diversification")
        
        # Analyze HHI
        hhi = self._calculate_hhi(holdings)
        if hhi > 0.25:  # High concentration
            recommendations.append("Portfolio is highly concentrated - consider more diversification")
        
        if not recommendations:
            recommendations.append("Portfolio appears well-diversified")
        
        return recommendations
    
    def _assess_concentration_risk(self, concentration: float) -> str:
        """Assess concentration risk level."""
        if concentration > 80:
            return "High"
        elif concentration > 60:
            return "Medium"
        else:
            return "Low"
    
    def _assess_sector_risk(self, max_sector_concentration: float) -> str:
        """Assess sector risk level."""
        if max_sector_concentration > 50:
            return "High"
        elif max_sector_concentration > 30:
            return "Medium"
        else:
            return "Low"
    
    def _assess_volatility_risk(self, volatility: float) -> str:
        """Assess volatility risk level."""
        if volatility > 0.30:
            return "High"
        elif volatility > 0.20:
            return "Medium"
        else:
            return "Low"
    
    def _estimate_stock_volatility(self, holding: Dict[str, Any]) -> float:
        """Estimate stock volatility."""
        # Placeholder - in real implementation, use historical data
        return 0.25  # 25% annual volatility
    
    def _estimate_stock_var(self, holding: Dict[str, Any], confidence_level: float) -> float:
        """Estimate stock Value at Risk."""
        volatility = self._estimate_stock_volatility(holding)
        var_factor = stats.norm.ppf(confidence_level)
        return volatility * var_factor
    
    def _calculate_risk_concentration(self, stock_risks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate risk concentration metrics."""
        if not stock_risks:
            return {}
        
        # Calculate risk-weighted metrics
        total_risk = sum(stock_risk['weight'] * stock_risk['volatility'] for stock_risk in stock_risks)
        
        return {
            'total_risk': total_risk,
            'risk_concentration_score': sum(stock_risk['weight'] ** 2 for stock_risk in stock_risks)
        }
    
    def _calculate_tail_risk(self, stock_risks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate tail risk metrics."""
        if not stock_risks:
            return {}
        
        # Calculate portfolio tail risk
        portfolio_var_99 = sum(stock_risk['weight'] * stock_risk['var_99'] for stock_risk in stock_risks)
        
        return {
            'portfolio_var_99': portfolio_var_99,
            'tail_risk_level': 'High' if portfolio_var_99 > 0.05 else 'Medium' if portfolio_var_99 > 0.03 else 'Low'
        } 