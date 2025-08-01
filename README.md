# ZerodhaWise

A comprehensive Python application for analyzing and managing Zerodha trading portfolios.

## Features

- **Portfolio Analysis**: Analyze your Zerodha portfolio performance, holdings, and P&L
- **Real-time Data**: Fetch real-time market data and portfolio updates
- **Performance Metrics**: Calculate key performance indicators like Sharpe ratio, drawdown, etc.
- **Risk Analysis**: Analyze portfolio risk and diversification
- **Visualization**: Generate charts and reports for portfolio insights
- **Automated Alerts**: Set up alerts for portfolio changes and market movements

## Prerequisites

- Python 3.8+
- Zerodha Kite Connect API credentials
- Required Python packages (see requirements.txt)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd ZerodhaWise
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up your Zerodha API credentials:
```bash
cp config/config.example.yaml config/config.yaml
# Edit config.yaml with your API credentials
```

## Configuration

Create a `config/config.yaml` file with your Zerodha API credentials:

```yaml
zerodha:
  api_key: "your_api_key"
  api_secret: "your_api_secret"
  access_token: "your_access_token"

database:
  url: "sqlite:///portfolio.db"

logging:
  level: "INFO"
  file: "logs/zerodhawise.log"
```

## Usage

### Basic Portfolio Analysis

```python
from zerodhawise.portfolio import PortfolioAnalyzer

analyzer = PortfolioAnalyzer()
portfolio = analyzer.get_portfolio()
print(portfolio.summary())
```

### Performance Analysis

```python
from zerodhawise.performance import PerformanceAnalyzer

perf_analyzer = PerformanceAnalyzer()
metrics = perf_analyzer.calculate_metrics()
print(metrics)
```

### Risk Analysis

```python
from zerodhawise.risk import RiskAnalyzer

risk_analyzer = RiskAnalyzer()
risk_metrics = risk_analyzer.analyze_risk()
print(risk_metrics)
```

## Project Structure

```
ZerodhaWise/
├── src/
│   ├── __init__.py
│   ├── portfolio.py          # Portfolio management and analysis
│   ├── performance.py        # Performance calculations
│   ├── risk.py              # Risk analysis
│   ├── data.py              # Data fetching and processing
│   ├── visualization.py      # Charts and reports
│   └── utils.py             # Utility functions
├── config/
│   ├── config.yaml          # Configuration file
│   └── config.example.yaml  # Example configuration
├── tests/
│   ├── __init__.py
│   ├── test_portfolio.py
│   ├── test_performance.py
│   └── test_risk.py
├── logs/                    # Log files
├── data/                    # Data storage
├── reports/                 # Generated reports
├── requirements.txt
├── setup.py
└── README.md
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Disclaimer

This software is for educational and personal use only. Please ensure compliance with Zerodha's terms of service and applicable regulations when using this tool for trading decisions. 