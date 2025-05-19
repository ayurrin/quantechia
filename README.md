# Quantechia

Quantechia is a Python library for financial market analysis and backtesting trading strategies.

## Folder Structure

### quantechia

*   `__init__.py`: Package initialization file
*   `analysis.py`: Analysis tools
*   `utils.py`: Utility functions
*   `data/`: Data acquisition module
    *   `__init__.py`
    *   `alpha_vantage.py`: Data acquisition from Alpha Vantage
    *   `data_fetcher.py`: Data fetcher
    *   `edgar.py`: Data acquisition from EDGAR
    *   `edinet_lifetechia.py`: Data acquisition from EDINET Lifetechia
    *   `edinet.py`: Data acquisition from EDINET
    *   `fred.py`: Data acquisition from FRED
    *   `investing.py`: Data acquisition from Investing.com
    *   `tiingo.py`: Data acquisition from Tiingo
*   `factor/`: Factor analysis module
    *   `create_factor.py`: Factor creation
    *   `factor_data.py`: Factor data
    *   `fama_french.py`: Fama-French factor
    *   `fredmd.py`: FRED-MD factor
    *   `global_factors.py`: Global factors
    *   `momentum.py`: Momentum factor
    *   `moving_average.py`: Moving average factor
    *   `volatility.py`: Volatility factor
*   `strategies/`: Trading strategy module
    *   `basestrategy.py`: Base strategy
    *   `risk.py`: Risk management
    *   `trend.py`: Trend following strategy

### example

*   `backtest.ipynb`: Backtest example
*   `equal_weight_strategy_report.html`: Equal weight strategy report
*   `get_data.ipynb`: Data acquisition example
*   `get_factor_data.ipynb`: Factor data acquisition example
*   `strategies.ipynb`: Strategy example

## Description

This library can be used for financial market data analysis, factor analysis, and backtesting trading strategies.

## Usage

1.  Install the required libraries: `pip install -r requirements.txt`
2.  Use the data acquisition module to acquire financial market data.
3.  Use the factor analysis module to create and analyze factors.
4.  Use the trading strategy module to backtest trading strategies.

## Example

The `example` folder contains several examples of how to use the library.
