import unittest
import pandas as pd
from quantechia.strategies import basestrategy

class TestBaseStrategy(unittest.TestCase):
    def test_base_strategy_initialization(self):
        # テストケース1：BaseStrategyの初期化
        prices = [100, 105, 110, 105, 120]
        dates = pd.to_datetime(['2025-01-01', '2025-01-02', '2025-01-03', '2025-01-04', '2025-01-05'])
        prices_df = pd.DataFrame({'Asset1': prices}, index=dates)  # DataFrameに変換
        strategy = basestrategy.BaseStrategy(prices_df, strategy_name="TestStrategy")
        self.assertEqual(strategy.price_data.equals(prices_df), True)
        self.assertEqual(strategy.strategy_name, "TestStrategy")

    def test_base_strategy_calculate_weight_not_implemented(self):
        # テストケース2：calculate_weightメソッドが実装されていない場合にエラーが発生することを確認
        prices = [100, 105, 110, 105, 120]
        dates = pd.to_datetime(['2025-01-01', '2025-01-02', '2025-01-03', '2025-01-04', '2025-01-05'])
        prices_df = pd.DataFrame({'Asset1': prices}, index=dates)  # DataFrameに変換
        strategy = basestrategy.BaseStrategy(prices_df)
        with self.assertRaises(NotImplementedError):
            strategy.calculate_weight()

if __name__ == '__main__':
    unittest.main()
