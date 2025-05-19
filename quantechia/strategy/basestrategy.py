import pandas as pd
import numpy as np
import quantstats as qs
from ..utils import calculate_portfolio,calculate_return, calculate_daily_weight, calculate_turnover, calculate_sharpe_ratio, calculate_max_drawdown, calculate_winning_rate
class BaseStrategy:
    """
    取引戦略の基本クラス。

    すべての取引戦略の基本となるクラスです。
    """

    def __init__(self, 
                 price_data: pd.DataFrame = None, 
                 rtn_data: pd.DataFrame = None, 
                 strategy_name: str = None, 
                 initial_capital: float = 1, 
                 shift_num: int = 1, 
                 cost: bool = True, 
                 cost_unit: float = 0.0005):
        """
        初期化メソッド。

        Args:
            price_data (pd.DataFrame, optional): 価格データ。
            rtn_data (pd.DataFrame, optional): リターンデータ。
            strategy_name (str, optional): 戦略名。デフォルトはNone。
            initial_capital (float, optional): 初期資本。デフォルトは1。
            shift_num (int, optional): シフト数。デフォルトは1。
            cost (bool, optional): コストの有無。デフォルトはTrue。
            cost_unit (float, optional): コストの単位。デフォルトは0.0005。
        """
        if price_data is not None:
            self.price_data = price_data
            self.rtn_data = price_data.pct_change().iloc[1:]
        elif rtn_data is not None:
            self.rtn_data = rtn_data
            self.price_data = (1 + rtn_data).cumprod()
            # 最初の行に初期資本を適用するなら以下のように：
            self.price_data *= initial_capital
        else:
            raise ValueError("price_data か rtn_data のいずれかを指定してください。")

        self.strategy_name = strategy_name if strategy_name else 'Strategy'
        self.weight = None
        self.initial_capital = initial_capital
        self.shift_num = shift_num
        self.cost = cost
        self.cost_unit = cost_unit

        self.rtn = None
        self.port = None
        self.rtn_by_asset = None

    def calculate_weight(self) -> pd.DataFrame:
        """
        戦略の重みを計算します。

        このメソッドは、サブクラスでオーバーライドする必要があります。

        Returns:
            pd.DataFrame: 戦略の重み。
        """
        raise NotImplementedError("Subclasses should implement this method.")

    def calculate_daily_weight(self) -> pd.DataFrame:
        """
        Calculate daily weight.
        """
        return calculate_daily_weight(self.weight, self.price_data, self.shift_num)
    
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
        # Calculate returns based on the weight and price data
        self.rtn_by_asset, self.rtn = calculate_return(self.price_data, self.weight, mode='daily', shift_num=shift_num, cost=cost, cost_unit=cost_unit)
        
        self.port = calculate_portfolio(self.rtn, self.initial_capital)
        self.port.name = self.strategy_name
        self.rtn.name = self.strategy_name

        return self.rtn

    def evaluate(self, report_path=None,display_mode=None, freq='ME',**kwargs) -> dict:
        """
        戦略のパフォーマンスを評価します。

        Args:
            report_path (str, optional): レポートのパス。デフォルトはNone。
            display_mode (str, optional): 表示モード。デフォルトはNone。
            freq (str, optional): 頻度。デフォルトは'ME'。

        Returns:
            dict: シャープレシオ、最大ドローダウン、勝率、ターンオーバーを含む辞書。
        """
        if self.rtn is None:
            self.calculate_returns(**kwargs)
        # Calculate Sharpe ratio
        sharpe_ratio = qs.stats.sharpe(self.rtn)
        # Calculate maximum drawdown
        max_drawdown = qs.stats.max_drawdown(self.rtn)
        # Calculate winning rate
        winning_rate = qs.stats.win_rate(self.rtn)

        turnover = calculate_turnover(self.weight, freq=freq)

        rtn = self.rtn.squeeze() if isinstance(self.rtn, pd.DataFrame) else self.rtn
        if report_path:
            try:
                qs.reports.html(rtn, output=report_path, **kwargs)
            except Exception as e:
                print(f'Report Error: {e}')
        if display_mode == 'basic':
            qs.reports.basic(rtn, **kwargs)
        elif display_mode == 'full':
            qs.reports.full(rtn, **kwargs)
        elif display_mode == 'stats':
            qs.reports.stats(rtn, **kwargs)
        elif display_mode == 'plot':
            qs.reports.plots(rtn, **kwargs)
            

        return {
            "sharpe_ratio": sharpe_ratio,
            "max_drawdown": max_drawdown,
            "winning_rate": winning_rate,
            "turnover": turnover,
        }

class EqualWeightStrategy(BaseStrategy):
    """
    均等 weighting 戦略。
    """

    def calculate_weight(self):
        """
        Calculate the equal weight for the strategy.
        """
        num_assets = len(self.price_data.columns)
        self.weight = pd.DataFrame(1 / num_assets, index=self.price_data.index, columns=self.price_data.columns)
        return self.weight

class RebalanceStrategy(BaseStrategy):
    """
    指定された頻度に基づいてポートフォリオをリバランスする戦略。
    """

    def __init__(self, price_data: pd.DataFrame,rebalance_freq=None, lookback: int = 60, **kwargs):
        super().__init__(price_data, **kwargs)
        self.rebalance_freq = rebalance_freq
        self.rebalance_dates = self.get_rebalance_dates()
        self.lookback = lookback
    
    def get_rebalance_dates(self):
        """
        self.rebalance_freqで指定された頻度に基づいてリバランス日を取得します。
        返される日付は、self.price_data.index内に存在することが保証されています。
        """
        idx = self.rtn_data.index

        if self.rebalance_freq is None:
            return idx

        elif isinstance(self.rebalance_freq, str):
            if self.rebalance_freq.upper().startswith("M"):  # Monthly
                return idx[idx.is_month_end]
            elif self.rebalance_freq.upper().startswith("Q"):  # Quarterly
                return idx[idx.is_quarter_end]
            elif self.rebalance_freq.upper().startswith("A") or self.rebalance_freq.upper().startswith("Y"):  # Annual
                return idx[idx.is_year_end]
            elif self.rebalance_freq.upper().startswith("W"):  # Weekly
                return self.rtn_data.groupby(idx.to_period("W")).tail(1).index
            else:
                # デフォルト処理（例：'5D'などの期間指定）→ ただし存在しない日付の可能性あり
                return self.rtn_data.resample(self.rebalance_freq).last().dropna().index

        elif isinstance(self.rebalance_freq, int):
            return idx[::self.rebalance_freq]

        elif isinstance(self.rebalance_freq, list):
            return idx[self.rebalance_freq]

        elif isinstance(self.rebalance_freq, pd.DatetimeIndex):
            return self.rebalance_freq[self.rebalance_freq.isin(idx)]

        elif isinstance(self.rebalance_freq, pd.PeriodIndex):
            return idx[idx.to_period(self.rebalance_freq.freq).isin(self.rebalance_freq)]

        else:
            raise ValueError("Unsupported type for rebalance_freq.")


    def calculate_weight(self):
        """
        過去の`lookback`日数とカスタムオプティマイザを使用して、ローリングリスクパリティの重みを計算します。
        """
        assets = self.rtn_data.columns
        weights = []

        for date in self.rebalance_dates:
            i = self.rtn_data.index.get_loc(date)
            if i < self.lookback:
                weights.append([np.nan] * len(assets))
                continue

            window_rtn = self.rtn_data.iloc[i - self.lookback:i]
            w = self.calculate_current_weight(window_rtn)
            weights.append(w)

        self.weight = pd.DataFrame(weights, index=self.rebalance_dates, columns=assets)
        return self.weight
    
    def calculate_current_weight(self, window_rtn):
        """
        カスタムオプティマイザを使用して重みを計算します。
        """
        cov_matrix = window_rtn.cov()
        inv_cov_matrix = np.linalg.inv(cov_matrix)
        ones = np.ones(len(window_rtn.columns))
        w = inv_cov_matrix @ ones
        w /= np.sum(w)
        return w
