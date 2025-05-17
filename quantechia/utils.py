import pandas as pd
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
    returns = returns.iloc[shift_num:]

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