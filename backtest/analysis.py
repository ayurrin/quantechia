import pandas as pd
from backtest.engine import BacktestEngine
import matplotlib.pyplot as plt

def compare_strategies(engines: list):
    """
    複数の戦略を比較分析する。

    Args:
        engines (list): BacktestEngine のインスタンスのリスト。

    Returns:
        pd.DataFrame: 各戦略の評価結果、リターン、ポートフォリオをまとめた DataFrame。
    """
    results = []
    returns = []
    portfolios = []
    strategy_names = []

    for engine in engines:
        strategy_names.append(engine.weight_data.name if hasattr(engine.weight_data, 'name') else 'Strategy')
        engine.run()
        results.append(engine.evaluate())
        returns.append(engine.returns)
        portfolios.append(engine.portfolio)

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
