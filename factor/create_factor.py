import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from factor_analyzer import FactorAnalyzer

def cal_pca_factor(returns_df, num_components=None, cum_thresh=0.8):
    # データの標準化
    scaler = StandardScaler()
    standardized_returns = scaler.fit_transform(returns_df)

    # PCAの適用
    pca = PCA()
    pca.fit(standardized_returns)

    # 累積寄与率を計算
    cumulative_variance = np.cumsum(pca.explained_variance_ratio_)

    # 累積寄与率が80%を超える主成分数を決定
    if not num_components:
        num_components = np.argmax(cumulative_variance >= cum_thresh) + 1

    # 選ばれた主成分を用いてデータを変換
    principal_components = pca.transform(standardized_returns)[:, :num_components]

    # ファクターの生成
    factors = pd.DataFrame(principal_components, columns=[f'PC{i+1}' for i in range(num_components)],index=returns_df.index)
    return factors

def cal_fa_factor(returns_df, num_components=3):
    # データの標準化（NaNやinfを処理）
    scaler = StandardScaler()
    standardized_returns = scaler.fit_transform(np.nan_to_num(returns_df))

    # 因子分析の適用
    fa = FactorAnalyzer(n_factors=num_components, rotation='varimax')
    fa.fit(standardized_returns)

    # 因子スコアの計算
    factor_scores = fa.transform(standardized_returns)

    # ファクターの生成
    fa_factors = pd.DataFrame(factor_scores, columns=[f'Factor{i+1}' for i in range(num_components)], index=returns_df.index)
    return fa_factors

def rolling_factor(returns_df,method='pac', window=60, **args):
    if method == 'pca':
        method = cal_pca_factor
    elif method == 'fa':
        method = cal_fa_factor

    factors_list = []

    for i in range(window, len(returns_df) + 1):
        rolling_window = returns_df.iloc[i-window:i]  # 過去n日間のデータを取得
        
        # 既存の method を呼び出してPCAを計算
        factors = method(rolling_window, **args)

        # 最新日のデータを取得
        factors_list.append(factors.iloc[-1])

    # DataFrameとして整理
    factors_df = pd.DataFrame(factors_list, index=returns_df.index[window-1:])

    return factors_df


