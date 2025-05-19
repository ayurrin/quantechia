from .basestrategy import BaseStrategy
import pandas as pd

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
