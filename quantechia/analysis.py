import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import japanize_matplotlib

def compare_strategies(strategies: list):
    """
    複数の戦略を比較分析する。

    Args:
        strategies (list): Backteststrategy のインスタンスのリスト。

    Returns:
        pd.DataFrame: 各戦略の評価結果、リターン、ポートフォリオをまとめた DataFrame。
    """
    results = []
    returns = []
    portfolios = []
    strategy_names = []

    for strategy in strategies:
        strategy_names.append(strategy.strategy_name)
    
        results.append(strategy.evaluate())
        returns.append(strategy.rtn)
        portfolios.append(strategy.port)

    # 評価結果を DataFrame にまとめる
    results_df = pd.DataFrame(results, index=strategy_names)

    # リターンを DataFrame にまとめる
    returns_df = pd.concat(returns, axis=1, keys=strategy_names)

    # ポートフォリオを DataFrame にまとめる
    portfolios_df = pd.concat(portfolios, axis=1, keys=strategy_names)

    # ポートフォリオの可視化
    plt.figure(figsize=(12, 6))
    for strategy_name, portfolio in portfolios_df.items():
        plt.plot(portfolio, label=strategy_name)
    plt.xlabel("Date")
    plt.ylabel("Portfolio Value")
    plt.title("Portfolio Comparison")
    plt.legend()
    plt.grid(True)
    plt.show()

    return results_df, returns_df, portfolios_df

class RiskContribution:
    def __init__(self, weight_df: pd.DataFrame, rtn_df: pd.DataFrame, lookback: int = 60):
        self.weight_df = weight_df
        self.rtn_df = rtn_df
        self.lookback = lookback
        self.rc_df = None
        self.rc_ratio_df = None

    def calculate(self):
        rc_list = []
        for i in range(self.lookback, len(self.rtn_df)):
            date = self.rtn_df.index[i]
            rtn_window = self.rtn_df.iloc[i - self.lookback:i]
            w = self.weight_df.loc[date].values

            if np.any(np.isnan(w)):
                rc_list.append(pd.Series([np.nan] * len(w), index=self.rtn_df.columns, name=date))
                continue

            cov = rtn_window.cov().values
            mrc = cov @ w
            rc = w * mrc

            rc_series = pd.Series(rc, index=self.rtn_df.columns, name=date)
            rc_list.append(rc_series)

        self.rc_df = pd.DataFrame(rc_list)

        # 比率（各日の合計を1に）に変換
        self.rc_ratio_df = self.rc_df.div(self.rc_df.sum(axis=1), axis=0)

    def get_rc_dataframe(self) -> pd.DataFrame:
        return self.rc_df

    def get_ratio_dataframe(self) -> pd.DataFrame:
        return self.rc_ratio_df

    def plot(self, ratio: bool = True):
        if ratio:
            if self.rc_ratio_df is None:
                raise ValueError("比率ベースのリスク寄与度が未計算です。`calculate()`を先に呼び出してください。")
            df = self.rc_ratio_df
            ylabel = "リスク寄与度（比率）"
        else:
            if self.rc_df is None:
                raise ValueError("リスク寄与度が未計算です。`calculate()`を先に呼び出してください。")
            df = self.rc_df
            ylabel = "リスク寄与度（絶対値）"

        df.plot(kind='area', stacked=True, figsize=(12, 6))
        plt.ylabel(ylabel)
        plt.title("Rolling Risk Contributions")
        plt.tight_layout()
        plt.show()