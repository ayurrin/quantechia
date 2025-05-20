from .basestrategy import BaseStrategy
import pandas as pd

class TrendFollowingStrategy(BaseStrategy):
    """
    Trend following strategy.
    """

    def __init__(self, price_data: pd.DataFrame, window: int = 20, strategy_name: str = None):
        super().__init__(price_data, strategy_name)
        self.window = window

    def calculate_weight(self) -> pd.DataFrame:
        """
        Calculate the weight for the trend following strategy.
        """
        moving_average = self.price_data.rolling(window=self.window).mean()
        self.weight = (self.price_data > moving_average).astype(float)
        return self.weight
import pandas as pd
import numpy as np
from abc import ABC, abstractmethod

class MomentumBaseStrategy(basestrategy.BaseStrategy, ABC):
    """
    モメンタム戦略の基底クラス。
    各モメンタム戦略に共通するロジックを提供します。
    """
    def __init__(self, price_data: pd.DataFrame = None, 
                 rtn_data: pd.DataFrame = None,
                 window: int = 12, 
                 strategy_name: str = None, 
                 initial_capital: float = 1, 
                 shift_num: int = 1, 
                 cost: bool = True, 
                 cost_unit: float = 0.0005):
        """
        モメンタム戦略の基底クラスの初期化メソッド
        
        Args:
            price_data: 価格データ
            rtn_data: リターンデータ
            window: モメンタムの計算期間
            strategy_name: 戦略名
            initial_capital: 初期資本
            shift_num: シフト数
            cost: コスト考慮フラグ
            cost_unit: コスト単位
        """
        super().__init__(price_data, rtn_data, strategy_name, initial_capital, shift_num, cost, cost_unit)
        self.window = window
    
    @abstractmethod
    def calculate_momentum_score(self) -> pd.DataFrame:
        """
        モメンタムスコアを計算する抽象メソッド。
        派生クラスでオーバーライドする必要があります。
        
        Returns:
            モメンタムスコアのDataFrame
        """
        pass
    
    def get_valid_score(self, momentum_score: pd.DataFrame) -> pd.DataFrame:
        """
        有効なスコア（NaNを含まない行）を取得します。
        
        Args:
            momentum_score: モメンタムスコア
            
        Returns:
            有効なスコアのDataFrame
        """
        return momentum_score.dropna(how='all')
    
    def calculate_weight(self) -> pd.DataFrame:
        """
        投資ウェイトを計算します。
        派生クラスでオーバーライドすることも可能です。
        
        Returns:
            投資ウェイトのDataFrame
        """
        # モメンタムスコアを計算
        momentum_score = self.calculate_momentum_score()
        
        # 有効なスコアを取得
        valid_score = self.get_valid_score(momentum_score)
        
        # 各スコアからウェイトを計算（デフォルトはベスト因子のみに投資）
        weights = self.convert_score_to_weight(valid_score)
        
        return weights
    
    def convert_score_to_weight(self, valid_score: pd.DataFrame) -> pd.DataFrame:
        """
        スコアをウェイトに変換します。
        派生クラスでオーバーライドすることも可能です。
        
        Args:
            valid_score: 有効なスコア
            
        Returns:
            投資ウェイトのDataFrame
        """
        # デフォルトは単純なベストファクター選択（派生クラスでオーバーライド可能）
        best_factor = valid_score.idxmax(axis=1)
        return pd.get_dummies(best_factor).astype(float)


class MomentumStrategy(MomentumBaseStrategy):
    """
    シンプルな累積リターンに基づくモメンタム戦略
    """
    def calculate_momentum_score(self) -> pd.DataFrame:
        """
        過去window期間の累積リターンを計算
        
        Returns:
            モメンタムスコアのDataFrame
        """
        # モメンタムスコア：過去window期間の累積リターン
        return (1 + self.rtn_data).rolling(window=self.window).apply(np.prod, raw=True) - 1


class MomentumStrategyRR(MomentumBaseStrategy):
    """
    リターン/リスク比に基づくモメンタム戦略
    """
    def calculate_momentum_score(self) -> pd.DataFrame:
        """
        リターン/リスク比を計算
        
        Returns:
            モメンタムスコアのDataFrame
        """
        rolling_mean = self.rtn_data.rolling(window=self.window).mean()
        rolling_std = self.rtn_data.rolling(window=max(10, self.window)).std()
        # リターン/リスク比を返す
        return rolling_mean / rolling_std


class MomentumStrategyRank(MomentumStrategyRR):
    """
    リターン/リスク比のランキングに基づくモメンタム戦略
    """
    def convert_score_to_weight(self, valid_score: pd.DataFrame) -> pd.DataFrame:
        """
        スコアをランキングベースのウェイトに変換
        
        Args:
            valid_score: 有効なスコア
            
        Returns:
            投資ウェイトのDataFrame
        """
        # ランキング付け（大きいほど順位が高い＝スコアが良い）
        ranks = valid_score.rank(axis=1, ascending=False, method='min')
        
        # 各月のランクを正規化してウェイトに（合計1になるように）
        return ranks.div(ranks.sum(axis=1), axis=0)


class MomentumStrategyRRweight(MomentumStrategyRR):
    """
    リターン/リスク比を直接ウェイトとして使用するモメンタム戦略
    """
    def convert_score_to_weight(self, valid_score: pd.DataFrame) -> pd.DataFrame:
        """
        スコアを直接ウェイトに変換（クリッピングとスケーリングあり）
        
        Args:
            valid_score: 有効なスコア
            
        Returns:
            投資ウェイトのDataFrame
        """
        # スコアをクリッピング
        clipped_score = valid_score.clip(-1.5, 1.5)
        
        # 各月のスコアをそのままウェイトに（絶対値の合計でスケーリングして合計=1に）
        return clipped_score.div(clipped_score.abs().sum(axis=1), axis=0)


class MomentumStrategyLongShort(MomentumBaseStrategy):
    """
    直近リターンにボーナスを加えるロングショート型モメンタム戦略
    """
    def __init__(self, price_data: pd.DataFrame = None, 
                 rtn_data: pd.DataFrame = None,
                 window: int = 12, 
                 alpha: float = 1,
                 strategy_name: str = None, 
                 initial_capital: float = 1, 
                 shift_num: int = 1, 
                 cost: bool = True, 
                 cost_unit: float = 0.0005):
        """
        ロングショート型モメンタム戦略の初期化メソッド
        
        Args:
            price_data: 価格データ
            rtn_data: リターンデータ
            window: モメンタムの計算期間
            alpha: 直近リターントップに対するボーナス係数
            strategy_name: 戦略名
            initial_capital: 初期資本
            shift_num: シフト数
            cost: コスト考慮フラグ
            cost_unit: コスト単位
        """
        super().__init__(price_data, rtn_data, window, strategy_name, initial_capital, shift_num, cost, cost_unit)
        self.alpha = alpha
    
    def calculate_momentum_score(self) -> pd.DataFrame:
        """
        リターン/リスク比を計算し、直近トップファクターにボーナスを加える
        
        Returns:
            モメンタムスコアのDataFrame
        """
        # リターン/リスク比の計算
        rolling_mean = self.rtn_data.rolling(window=self.window).mean()
        rolling_std = self.rtn_data.rolling(window=max(10, self.window)).std()
        rr_score = rolling_mean / (rolling_std + 1e-8)
        rr_score = rr_score.clip(0, 1.5)
        
        # 直近1ヶ月のリターンを取得
        recent_return = self.rtn_data.shift(1)
        
        # NaN行を除外してトップファクターを取得
        top_factors = recent_return.dropna(how='all').idxmax(axis=1)
        
        # 補正マスクを作成
        bonus = pd.DataFrame(0, index=rr_score.index, columns=rr_score.columns)
        for date, factor in top_factors.items():
            if factor in bonus.columns:
                bonus.at[date, factor] = 1
        
        # 補正スコアの加算（ボーナスを加える）
        return rr_score + self.alpha * bonus
    
    def convert_score_to_weight(self, valid_score: pd.DataFrame) -> pd.DataFrame:
        """
        スコアをウェイトに変換
        
        Args:
            valid_score: 有効なスコア
            
        Returns:
            投資ウェイトのDataFrame
        """
        # スコアの合計が±1になるようにスケーリング
        return valid_score.div(valid_score.abs().sum(axis=1), axis=0)