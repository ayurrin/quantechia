# Qunatechia - クオンツ運用・分析のためのPythonライブラリ

## 概要
Qunatechiaは、クオンツ運用や金融分析を効率的に行うためのPythonライブラリです。
データの取得・前処理、ファクター計算、売買戦略の実装、バックテスト、可視化などの機能を提供します。

## 機能一覧
### 1. データ取得・前処理 (`data/`)
- 株価、為替、仮想通貨データの取得（API・CSV対応）
- 欠損値処理、正規化、スケーリングなどの前処理

### 2. ファクター計算 (`factor/`)
- 移動平均（SMA、EMA、WMA）
- モメンタム指標（RSI、MACD、Stochastic）
- ボラティリティ指標（ATR、ボリンジャーバンド）

### 3. 売買戦略 (`strategies/`)
- **リバーサル戦略**（平均回帰戦略）
- **トレンドフォロー戦略**（ブレイクアウト戦略、モメンタム戦略）
- **アルファファクター戦略**（ファンダメンタル×クオンツ分析）

### 4. バックテスト (`backtest/`)
- シミュレーションエンジン（ローリングウィンドウ、ウォークフォワード分析対応）
- パフォーマンス評価（シャープレシオ、最大ドローダウン、勝率など）

### 5. 可視化 (`visualization/`)
- 株価チャートとファクターのオーバーレイ
- 戦略ごとのパフォーマンス比較

## ディレクトリ構成
```
qunatechia/
│── data/                # データ取得・管理
│   ├── fetch.py         # APIやデータソースから取得
│   ├── preprocess.py    # データの前処理
│── factor/              # ファクター計算
│   ├── moving_average.py
│   ├── momentum.py
│   ├── volatility.py
│── strategies/          # 売買戦略の実装
│   ├── mean_reversion.py
│   ├── trend_following.py
│── backtest/            # バックテスト用モジュール
│   ├── engine.py        # バックテストのエンジン
│   ├── metrics.py       # パフォーマンス評価指標
│── visualization/       # 可視化
│   ├── plot.py
│── utils/               # ユーティリティ関数
│   ├── config.py
│── tests/               # ユニットテスト
│── examples/            # サンプルコード
│── README.md            # ライブラリの説明
│── setup.py             # パッケージのセットアップ
```

## 使用技術
| 機能            | ライブラリ |
|----------------|-----------|
| データ取得     | `pandas`, `yfinance`, `alpha_vantage` |
| データ前処理   | `pandas`, `numpy`, `scipy` |
| ファクター計算 | `talib`, `ta` |
| バックテスト   | `backtrader`, `zipline` |
| 可視化         | `matplotlib`, `plotly`, `seaborn` |

## インストール方法
```
pip install qunatechia
```

## 使い方
```python
from qunatechia.data.fetch import get_stock_data
from qunatechia.factor.momentum import calculate_rsi

# データ取得
stock_data = get_stock_data("AAPL", start="2023-01-01", end="2023-12-31")

# RSI 計算
rsi = calculate_rsi(stock_data["close"], period=14)
print(rsi)
```

## ライセンス
MIT License

