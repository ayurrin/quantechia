import pandas as pd
import numpy as np
import quantstats
from ..utils import calculate_portfolio, calculate_sharpe_ratio, calculate_max_drawdown, calculate_winning_rate
class BaseStrategy:
    """
    Base class for all trading strategies.
    """

    def __init__(self, price_data: pd.DataFrame, strategy_name: str = None, initial_capital: float = 1, shift_num: int = 1, cost: bool = True, cost_unit: float = 0.0005):
        
        self.price_data = price_data
        self.strategy_name = strategy_name if strategy_name else 'Strategy'
        self.weight = None
        self.rtn_data = self.price_data.pct_change().iloc[1:]
        self.initial_capital = initial_capital
        self.shift_num = shift_num
        self.cost = cost
        self.cost_unit = cost_unit

        self.rtn = None
        self.port = None
        self.rtn_by_asset = None

    def calculate_weight(self) -> pd.DataFrame:
        """
        Calculate the weight for the strategy.
        This method should be overridden by subclasses.
        """
        raise NotImplementedError("Subclasses should implement this method.")
    
    def calculate_returns(self, **kwargs) -> pd.DataFrame:
        """
        Calculate the returns based on the weight and price data.
        """
        #kwargsにある場合は、その値、そうでない場合はself
        shift_num = kwargs.get('shift_num', self.shift_num)
        cost = kwargs.get('cost', self.cost)
        cost_unit = kwargs.get('cost_unit', self.cost_unit)
       
        # Calculate returns
        if self.weight is None:
            self.calculate_weight()
        returns = self.rtn_data * self.weight.shift(shift_num)
        returns = returns.iloc[shift_num:]
        # If cost is True, apply transaction costs
        if cost:
            transaction_costs = (self.weight.diff().abs() * cost_unit)
            returns -= transaction_costs
        # Calculate portfolio returns
        self.rtn_by_asset = returns
        self.rtn = pd.DataFrame(returns.sum(axis=1),columns=[self.strategy_name])
        self.port = calculate_portfolio(self.rtn, self.initial_capital)
        self.port.name = self.strategy_name
        self.rtn.name = self.strategy_name

        return self.rtn

    def evaluate(self, report_path=None, **kwargs) -> dict:
        """
        Evaluate the performance of the strategy.
        """
        if self.rtn is None:
            self.calculate_returns(**kwargs)
        # Calculate Sharpe ratio
        sharpe_ratio = calculate_sharpe_ratio(self.rtn)
        # Calculate maximum drawdown
        max_drawdown = calculate_max_drawdown(self.port)
        # Calculate winning rate
        winning_rate = calculate_winning_rate(self.rtn)

        if report_path:
            try:
                rtn = self.rtn.squeeze() if isinstance(self.rtn, pd.DataFrame) else self.rtn
                quantstats.reports.html(rtn, output=report_path, **kwargs)
            except Exception as e:
                print(f'Report Error: {e}')

        return {
            "sharpe_ratio": sharpe_ratio,
            "max_drawdown": max_drawdown,
            "winning_rate": winning_rate,
        }

class EqualWeightStrategy(BaseStrategy):
    """
    Equal weight strategy.
    """

    def calculate_weight(self):
        """
        Calculate the equal weight for the strategy.
        """
        num_assets = len(self.price_data.columns)
        self.weight = pd.DataFrame(1 / num_assets, index=self.price_data.index, columns=self.price_data.columns)
        return self.weight

class TrendFollowingStrategy(BaseStrategy):
    """
    Trend following strategy.
    """

    def __init__(self, price_data: pd.DataFrame, window: int = 20, strategy_name: str = None):
        super().__init__(price_data, strategy_name)
        self.window = window

    def calculate_weight(self) -> pd.DataFrame:
        """
        Calculate the weight for the trend following strategy.
        """
        moving_average = self.price_data.rolling(window=self.window).mean()
        self.weight = (self.price_data > moving_average).astype(float)
        return self.weight
