"""
ZerodhaWise - A comprehensive Python application for analyzing Zerodha trading portfolios.

This package provides tools for portfolio analysis, performance tracking, risk assessment,
and visualization of Zerodha trading data.
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .portfolio import PortfolioAnalyzer
from .performance import PerformanceAnalyzer
from .risk import RiskAnalyzer
from .data import DataManager
from .visualization import ChartGenerator

__all__ = [
    "PortfolioAnalyzer",
    "PerformanceAnalyzer", 
    "RiskAnalyzer",
    "DataManager",
    "ChartGenerator",
] 