# Qunatechia - A Python Library for Quantitative Trading and Analysis

## Overview
Qunatechia is a Python library designed for efficient quantitative trading and financial analysis. It provides functionalities for data acquisition and preprocessing, factor calculations, trading strategy implementation, backtesting, and visualization.

## Features
### 1. Data Acquisition & Preprocessing (`data/`)
- Fetch stock, forex, and cryptocurrency data (supports API & CSV)
- Handle missing values, normalization, and scaling

### 2. Factor Calculation (`factor/`)
- Moving Averages (SMA, EMA, WMA)
- Momentum Indicators (RSI, MACD, Stochastic)
- Volatility Indicators (ATR, Bollinger Bands)

### 3. Trading Strategies (`strategies/`)
- **Reversal Strategy** (Mean Reversion)
- **Trend-Following Strategy** (Breakout & Momentum)
- **Alpha Factor Strategy** (Fundamental × Quantitative Analysis)

### 4. Backtesting (`backtest/`)
- Simulation engine (Rolling Window, Walk Forward Analysis)
- Performance evaluation (Sharpe Ratio, Max Drawdown, Win Rate, etc.)

### 5. Visualization (`visualization/`)
- Overlay stock charts with factors
- Compare performance of different strategies

## Directory Structure
```
qunatechia/
│── data/                # Data Acquisition & Management
│   ├── fetch.py         # Fetch data from APIs & sources
│   ├── preprocess.py    # Data preprocessing
│── factor/              # Factor Calculation
│   ├── moving_average.py
│   ├── momentum.py
│   ├── volatility.py
│── strategies/          # Trading Strategies
│   ├── mean_reversion.py
│   ├── trend_following.py
│── backtest/            # Backtesting Module
│   ├── engine.py        # Backtest Engine
│   ├── metrics.py       # Performance Evaluation
│── visualization/       # Visualization
│   ├── plot.py
│── utils/               # Utility Functions
│   ├── config.py
│── tests/               # Unit Tests
│── examples/            # Sample Code
│── README.md            # Library Documentation
│── setup.py             # Package Setup
```

## Technologies Used
| Feature         | Libraries |
|----------------|-----------|
| Data Acquisition | `pandas`, `yfinance`, `alpha_vantage` |
| Data Preprocessing | `pandas`, `numpy`, `scipy` |
| Factor Calculation | `talib`, `ta` |
| Backtesting | `backtrader`, `zipline` |
| Visualization | `matplotlib`, `plotly`, `seaborn` |

## Installation
```
pip install qunatechia
```

## Usage
```python
from qunatechia.data.fetch import get_stock_data
from qunatechia.factor.momentum import calculate_rsi

# Fetch data
stock_data = get_stock_data("AAPL", start="2023-01-01", end="2023-12-31")

# Calculate RSI
rsi = calculate_rsi(stock_data["close"], period=14)
print(rsi)
```

## License
MIT License

