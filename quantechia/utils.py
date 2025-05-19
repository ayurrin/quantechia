import pandas as pd

def calculate_daily_weight(price_data, weight_data):
    """ドリフトしたウェイトを計算"""
    rebalance_dates = weight_data.index
    index_range = price_data.loc[rebalance_dates[0]:].index
    base_price = price_data.loc[rebalance_dates].reindex(index_range).ffill()
    cum_rtn = price_data.loc[index_range] / base_price

    # ドリフト後のウェイト
    raw_weight = weight_data.reindex(index_range).ffill()
    drifted_weight = cum_rtn * raw_weight
    drifted_weight = drifted_weight.div(drifted_weight.sum(axis=1), axis=0)  # 正規化
    
    return drifted_weight
def calc_rtn(price_data, weight_data, shift_num=1, cost=True, cost_unit=0.0005):
    """リバランス日間の実現リターン"""
    rebalance_dates = weight_data.index
    returns = price_data.resample('D').ffill().loc[rebalance_dates].pct_change()
    shifted_weights = weight_data.shift(shift_num)
    if cost:
        # 前回リバランスとの差分に対してコストをかける（絶対値）
        cost_data = weight_data.diff().abs() * cost_unit
        rtn = ((shifted_weights * returns) - cost_data)
    else:
        rtn = (shifted_weights * returns)

    return rtn
def calc_daily_rtn(price_data, weight_data, shift_num=1, cost=True, cost_unit=0.0005):
    """累積リターンから日次リターンを精緻に計算"""
    # 基準価格をリバランス日ごとに更新
    rebalance_dates = weight_data.index
    index_range = price_data.loc[rebalance_dates[0]:].index
    price_data = price_data.resample('D').ffill()
    base_price = price_data.loc[rebalance_dates].reindex(index_range).ffill()
    base_price = base_price.shift(shift_num).bfill()  # リバランス日を基準にするため、1日シフト

    # 累積リターンとウェイト反映
    cum_rtn = price_data.loc[index_range] / base_price
    weights = weight_data.reindex(index_range).ffill().shift(shift_num)  # 前回リバランス時点のウェイト
    daily_rtn_cum = (cum_rtn * weights)

    # 累積をリバランス日にリセット
    reset_point = daily_rtn_cum.copy()
    reset_point.loc[rebalance_dates] = weight_data.loc[rebalance_dates]
    daily_rtn  = daily_rtn_cum.div(reset_point.sum(axis=1).shift(shift_num), axis=0) -weights

    if cost:
        cost_data = weight_data.reindex(index_range).ffill().diff().abs() * cost_unit
        daily_rtn = daily_rtn - cost_data

    
    return daily_rtn

def calculate_returns(price_data, weight_data, mode=None, shift_num=1, cost=True, cost_unit=0.0005) -> pd.DataFrame:
    """
    リターンを計算する。


    Returns:
        pd.DataFrame: リターンデータ。
    """
    if mode == 'daily':
        # 日次リターンを計算
        returns = calc_daily_rtn(price_data, weight_data, shift_num, cost, cost_unit)
    
    else:
        returns = calc_rtn(price_data, weight_data, shift_num, cost, cost_unit)

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

def calculate_turnover(weight: pd.DataFrame, freq='ME') -> pd.DataFrame:
    """
    回転率を計算する。

    Args:
        weight (pd.DataFrame): ウェイトデータ。
        freq (str): 集計頻度。デフォルトは'M'（月次）。

    Returns:
        pd.DataFrame: 回転率データ。
    """
    # ウェイトの変化を計算
    weight_change = weight.diff().abs().sum(axis=1)

    # 集計頻度に基づいて回転率を計算
    turnover = weight_change.resample(freq).sum().mean()

    return turnover