# Quantechia

Quantechiaは、金融市場の分析と取引戦略のバックテストのためのPythonライブラリです。

## フォルダ構成

### quantechia

*   `__init__.py`: パッケージの初期化ファイル
*   `analysis.py`: 分析ツール
*   `utils.py`: ユーティリティ関数
*   `data/`: データ取得モジュール
    *   `__init__.py`
    *   `alpha_vantage.py`: Alpha Vantageからのデータ取得
    *   `data_fetcher.py`: データフェッチャー
    *   `edgar.py`: EDGARからのデータ取得
    *   `edinet_lifetechia.py`: EDINET Lifetechiaからのデータ取得
    *   `edinet.py`: EDINETからのデータ取得
    *   `fred.py`: FREDからのデータ取得
    *   `investing.py`: Investing.comからのデータ取得
    *   `tiingo.py`: Tiingoからのデータ取得
*   `factor/`: ファクター分析モジュール
    *   `create_factor.py`: ファクター作成
    *   `factor_data.py`: ファクターデータ
    *   `fama_french.py`: Fama-Frenchファクター
    *   `fredmd.py`: FRED-MDファクター
    *   `global_factors.py`: グローバルファクター
    *   `momentum.py`: モメンタムファクター
    *   `moving_average.py`: 移動平均ファクター
    *   `volatility.py`: ボラティリティファクター
*   `strategies/`: 取引戦略モジュール
    *   `basestrategy.py`: 基本戦略
    *   `risk.py`: リスク管理
    *   `trend.py`: トレンドフォロー戦略

### example

*   `backtest.ipynb`: バックテストの例
*   `equal_weight_strategy_report.html`: 等加重戦略レポート
*   `get_data.ipynb`: データ取得の例
*   `get_factor_data.ipynb`: ファクターデータ取得の例
*   `strategies.ipynb`: 戦略の例

## 説明

このライブラリは、金融市場のデータ分析、ファクター分析、および取引戦略のバックテストに使用できます。

## 使い方

1.  必要なライブラリをインストールします: `pip install -r requirements.txt`
2.  データ取得モジュールを使用して、金融市場のデータを取得します。
3.  ファクター分析モジュールを使用して、ファクターを作成および分析します。
4.  取引戦略モジュールを使用して、取引戦略をバックテストします。

## 例

`example` フォルダには、ライブラリの使用例がいくつか含まれています。
