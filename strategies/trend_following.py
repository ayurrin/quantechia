import pandas as pd

def trend_following(price: pd.DataFrame, window: int = 20) -> pd.DataFrame:
    """
    単純なトレンドフォロー戦略。
    価格データを受け取り、移動平均線に基づいて投資ウェイトを計算します。

    Args:
        price (pd.DataFrame): 価格データ。各列が銘柄、各行が日付。
        window (int): 移動平均線の計算期間。

    Returns:
        pd.DataFrame: 各銘柄の投資ウェイト。
    """
    # 移動平均線を計算
    moving_average = price.rolling(window=window).mean()

    # 現在の価格が移動平均線より上なら買い、下なら売る
    # ウェイトを0から1の間に制限
    weight = (price > moving_average).astype(float)
    weight = weight.clip(0, 1)

    return weight
