import sys
import os
from dotenv import load_dotenv
import pandas as pd

# プロジェクトルートのパスを追加（quantechiaがあるディレクトリ）
sys.path.append('/app/')
load_dotenv()

import pandas as pd
import numpy as np
from backtest.engine import BacktestEngine
from strategies.trend_following import trend_following

# ダミーデータを作成
np.random.seed(42)
price_data = pd.DataFrame(np.random.randn(100, 3), columns=['A', 'B', 'C'])
weight_data = trend_following(price_data, window=20)
trade_units = pd.Series([0.01, 0.005, 0.0025], index=['A', 'B', 'C'])

# バックテストエンジンを初期化
engine = BacktestEngine(
    price_data=price_data,
    weight_data=weight_data,
    trade_units=trade_units,
    initial_capital=1000
)

# バックテストを実行
engine.run()

# 結果を表示
print("Portfolio Simple:", engine.portfolio_simple)
print("Portfolio Trade:", engine.portfolio_trade)
