import pandas as pd
import numpy as np
import quantstats

def calculate_returns(rtn_data, weight_data, shift_num=1, cost=True, cost_unit=0.0005) -> pd.DataFrame:
    """
    リターンを計算する。


    Returns:
        pd.DataFrame: リターンデータ。
    """
    if cost:
        # コストを考慮したリターンを計算
        cost_data = weight_data.shift(shift_num).diff() * cost_unit
        returns = weight_data.shift(shift_num) * (rtn_data - cost_data)
    else:
    
        returns = weight_data.shift(shift_num) * rtn_data
    

    return returns, pd.DataFrame(returns.sum(axis=1))

def calculate_portfolio(returns: pd.DataFrame, initial_capital: float) -> pd.DataFrame:
    """
    ポートフォリオを計算する。

    Args:
        returns (pd.DataFrame): リターンデータ。
        initial_capital (float): 初期資本。

    Returns:
        pd.DataFrame: ポートフォリオデータ。
    """
    # ポートフォリオの価値を計算
    if isinstance(returns, pd.Series):
        portfolio = (1 + returns).cumprod() * initial_capital
    else:
        portfolio = (1 + returns.sum(axis=1)).cumprod() * initial_capital

    return portfolio

    
def calculate_sharpe_ratio(returns: pd.DataFrame, risk_free_rate: float = 0.0) -> float:
    """
    シャープレシオを計算する。

    Args:
        returns (pd.DataFrame): リターンデータ。
        risk_free_rate (float): リスクフリーレート。

    Returns:
        float: シャープレシオ。
    """
    # 平均リターンを計算
    mean_return = returns.mean().sum()

    # リターンの標準偏差を計算
    std_dev = returns.std().sum()

    # シャープレシオを計算
    sharpe_ratio = (mean_return - risk_free_rate) / std_dev

    return sharpe_ratio

def calculate_max_drawdown( portfolio: pd.Series) -> float:
    """
    最大ドローダウンを計算する。

    Args:
        portfolio (pd.Series): ポートフォリオデータ。

    Returns:
        float: 最大ドローダウン。
    """
    # 累積最大値を計算
    cumulative_max = portfolio.cummax()

    # ドローダウンを計算
    drawdown = portfolio / cumulative_max - 1

    # 最大ドローダウンを計算
    max_drawdown = drawdown.min()

    return max_drawdown

def calculate_winning_rate( returns: pd.DataFrame) -> float:
    """
    勝率を計算する。

    Args:
        returns (pd.DataFrame): リターンデータ。

    Returns:
        float: 勝率。
    """
    # 1日ごとのリターンがプラスの日を数える
    winning_days = (returns.sum(axis=1) > 0).sum()

    # 全体の取引日数を計算
    total_days = len(returns)

    # 勝率を計算
    winning_rate = winning_days / total_days

    return winning_rate

class BacktestEngine:
    def __init__(self, price_data: pd.DataFrame, weight_data: pd.DataFrame, initial_capital: float = 1):
        """
        バックテストエンジン。

        Args:
            price_data (pd.DataFrame): 価格データ。各列が銘柄、各行が日付。
            weight_data (pd.DataFrame): ウェイトデータ。各列が銘柄、各行が日付。
            trade_units (pd.Series): 各銘柄の取引単位。
            initial_capital (float): 初期資本。
            **kwargs: 戦略関数の引数。
        """
        self.initial_capital = initial_capital
        self.price_data = price_data
        self.weight_data = weight_data
        self.portfolio = None
        self.returns = None
        self.rtn_data = self.price_data.pct_change()

    def run(self, shift_num=1, cost=True, cost_unit=0.0005):
        """
        バックテストを実行する。
        """
       
        # リターンを計算
        self.returns_by_asset, self.returns = calculate_returns(self.rtn_data, self.weight_data, shift_num, cost, cost_unit)

        # ポートフォリオを計算
        self.portfolio = calculate_portfolio(self.returns_by_asset, self.initial_capital)

    
    def evaluate(self, report_path=None, **kwargs) -> dict:
        """
        パフォーマンスを評価する。
        """
        # シャープレシオを計算
        sharpe_ratio = calculate_sharpe_ratio(self.returns)

        # 最大ドローダウンを計算
        max_drawdown = calculate_max_drawdown(self.portfolio)

        # 勝率を計算
        winning_rate = calculate_winning_rate(self.returns)
        if report_path:
            try:
                quantstats.reports.html(self.returns.iloc[:,0],output=report_path, **kwargs)
            except:
                print('Report Error')
        return {
            "sharpe_ratio": sharpe_ratio,
            "max_drawdown": max_drawdown,
            "winning_rate": winning_rate,
        }



