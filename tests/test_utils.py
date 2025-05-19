import unittest
import pandas as pd
from quantechia import utils

class TestUtils(unittest.TestCase):
    def test_calculate_returns(self):
        # テストケース1：正常な価格データ
        prices = [100, 105, 110, 105, 120]
        dates = pd.to_datetime(['2025-01-01', '2025-01-02', '2025-01-03', '2025-01-04', '2025-01-05'])
        prices_df = pd.DataFrame({'Asset1': prices}, index=dates)  # DataFrameに変換
        weight_data = pd.DataFrame({'Asset1': [1.0] * len(prices)}, index=dates)  # ウェイトデータ
        expected_returns = [0.05, 0.04761905, -0.04545455, 0.14285714]
        actual_returns, _ = utils.calculate_returns(prices_df, weight_data)  # weight_dataを渡す
        actual_returns = actual_returns.iloc[1:]['Asset1'].tolist()  # 最初の行を削除
        self.assertEqual(len(actual_returns), len(expected_returns))
        for i in range(len(actual_returns)):
            self.assertAlmostEqual(actual_returns[i], expected_returns[i], places=8)

    def test_calculate_returns_empty_list(self):
        # テストケース2：空の価格リスト
        dates = pd.to_datetime([])
        prices_df = pd.DataFrame({'Asset1': [], 'index': dates}).set_index('index')  # DataFrameに変換
        weight_data = pd.DataFrame({'Asset1': [], 'index': dates}).set_index('index')  # ウェイトデータ
        actual_returns, _ = utils.calculate_returns(prices_df, weight_data)  # weight_dataを渡す
        self.assertTrue(actual_returns.empty)

   
if __name__ == '__main__':
    unittest.main()
