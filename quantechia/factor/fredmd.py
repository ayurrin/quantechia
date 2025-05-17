#source https://github.com/joe5saia/FredMD changed

import pandas as pd
import numpy as np
import sklearn.decomposition as skd
import sklearn.preprocessing as skp
import sklearn.pipeline as skpipe
import math


class FredMD:
    """
    FredMDオブジェクト。FRED-MDデータセット（https://research.stlouisfed.org/econ/mccracken/fred-databases/）に基づいてファクターを作成します。
    メソッド:
    1) FredMD(): ダウンロードされたデータでオブジェクトを初期化
    2) estimate_factors(): 全推定を実行
    3) factors_em(): 欠損値を扱うためにEMアルゴリズムでファクターを推定
    4) baing(): Bai-Ngファクター選択アルゴリズムを推定
    5) apply_transforms(): 各シリーズに変換を適用
    6) remove_outliers(): 外れ値を削除
    7) factor_standardizer_method(): 標準化手法を適切なsklearn.StandardScalerに変換
    8) data_transforms(): 変換コードに従ってシリーズを定常化する関数を適用
    9) download_data(): FRED-MDデータセットをダウンロード
    10) V(): 説明分散関数

    """

    def __init__(self, num_factors=None, vintage_date=None, max_factors=8, standardize_method=2, ic_penalty_method=2, start_date=None, end_date=None) -> None:
        """
        FredMDオブジェクトを作成
        引数:
        1) num_factors = None: 推定するファクターの数。Noneの場合、情報基準に基づいて真のファクター数を推定
        2) vintage_date = None: 使用するデータのビンテージ（"year-month"形式、例："2020-10"）。Noneの場合、現在のビンテージを使用
        3) max_factors = 8: 情報基準に対してテストするファクターの最大数。num_factorsが数値の場合、これは無視される
        4) standardize_method = 2: ファクターを推定する前にデータを標準化する方法。0 = 変換なし、1 = 平均値のみ除去、2 = 平均値と分散で標準化。デフォルトは2。
        5) ic_penalty_method = 2: 情報基準のペナルティ項。詳細は http://www.columbia.edu/~sn2294/pub/ecta02.pdf のページ201、方程式9を参照。
        """
        # 引数のバリデーション
        if standardize_method not in [0, 1, 2]:
            raise ValueError(f"standardize_methodは[0, 1, 2]のいずれかである必要があります。受け取った値: {standardize_method}")
        if ic_penalty_method not in [1, 2, 3]:
            raise ValueError(f"ic_penalty_methodは[1, 2, 3]のいずれかである必要があります。受け取った値: {ic_penalty_method}")

        # データのダウンロード
        self.raw_data, self.transform_codes = self.download_data(vintage_date)
        # max_factorsのチェック
        if max_factors > self.raw_data.shape[1]:
            raise ValueError(f"max_factorsはシリーズの数未満である必要があります。max_factors({max_factors}) > シリーズの数({self.raw_data.shape[1]})")

        self.standardize_method = standardize_method
        self.ic_penalty_method = ic_penalty_method
        self.max_factors = max_factors
        self.num_factors = num_factors
        self.start_date = start_date
        self.end_date = end_date

    @staticmethod
    def download_data(vintage_date):
        if vintage_date is None:
            url = 'https://www.stlouisfed.org/-/media/project/frbstl/stlouisfed/research/fred-md/monthly/current.csv'
        else:
            url = f'https://www.stlouisfed.org/-/media/project/frbstl/stlouisfed/research/fred-md/monthly/{vintage_date}.csv'

        transform_df = pd.read_csv(url, header=0, nrows=1, index_col=0).transpose()
        transform_df.index.rename("series", inplace=True)
        transform_df.columns = ['transform']
        transform_codes = transform_df.to_dict()['transform']
        data = pd.read_csv(url, names=transform_codes.keys(), skiprows=2, index_col=0, engine='python', parse_dates=True)
        return data, transform_codes

    @staticmethod
    def factor_standardizer_method(code):
        """
        希望する機能を持つsklearn標準スケーラーオブジェクトを出力します
        コード:
        0) 変換なし
        1) 平均値のみ除去
        2) 平均値と標準化
        """
        if code == 0:
            return skp.StandardScaler(with_mean=False, with_std=False)
        elif code == 1:
            return skp.StandardScaler(with_mean=True, with_std=False)
        elif code == 2:
            return skp.StandardScaler(with_mean=True, with_std=True)
        else:
            raise ValueError("standardize_methodは[0, 1, 2]のいずれかである必要があります")

    @staticmethod
    def data_transforms(series, transform_code):
        """
        変換コードに従って単一シリーズを変換
        入力:
        1) series: 変換するpandasシリーズ
        2) transform_code: シリーズの変換コード
        出力:
        変換されたシリーズ
        """
        if transform_code == 1:
            # 水準
            return series
        elif transform_code == 2:
            # 1階差分
            return series.diff()
        elif transform_code == 3:
            # 2階差分
            return series.diff().diff()
        elif transform_code == 4:
            # 自然対数
            return np.log(series)
        elif transform_code == 5:
            # 対数1階差分
            return np.log(series).diff()
        elif transform_code == 6:
            # 対数2階差分
            return np.log(series).diff().diff()
        elif transform_code == 7:
            # 割合変化の1階差分
            return series.pct_change().diff()
        else:
            raise ValueError("transform_codeは[1, 2, ..., 7]のいずれかである必要があります")

    def apply_transforms(self):
        """
        各シリーズに変換を適用し、主にNaNを含む最初の2行を削除
        結果をself.seriesに保存
        """
        self.series = pd.DataFrame({key: self.data_transforms(self.raw_data[key], value) for (key, value) in self.transform_codes.items()})
        
        self.series.drop(self.series.index[[0, 1]], inplace=True)
        if self.start_date:
            self.series = self.series[self.series.index>=self.start_date]
        if self.end_date:
            self.series = self.series[self.series.index<=self.end_date]
    def remove_outliers(self):
        """
        self.seriesの各シリーズから外れ値を削除
        外れ値の定義: シリーズXのデータポイントxがabs(x-中央値)>10*四分位範囲の場合、外れ値と見なされる
        """
        outlier_mask = abs((self.series - self.series.median()) / (self.series.quantile(0.75) - self.series.quantile(0.25))) > 10
        for col in self.series.columns:
            self.series.loc[outlier_mask[col], col] = np.nan

    def factors_em(self, max_iterations=50, tolerance=math.sqrt(0.000001)):
        """
        欠損値を扱うためにEMアルゴリズムでファクターを推定
        入力:
        max_iterations: 最大反復回数
        tolerance: 予測されたシリーズ値の反復間での収束の許容範囲
        アルゴリズム:
        1) initial_nas: NaNの位置のブールマスク
        2) working_data: NaNを平均値で置換した標準化データ行列
        3) F: 予備的なファクター推定
        4) data_hat_last: 最後のSVDモデルの予測標準値。data_hatとdata_hat_lastは厳密には平均0分散1ではない
        5) data_hatが収束するまで反復
        6) 元のデータからNaNを埋める
        保存:
        1) self.svdmodel: 標準化ステップとSVDモデルを含むsklearnパイプライン
        2) self.series_filled: self.seriesのNaNをself.svdmodelからの予測値で埋めたもの
        """
        # 推定パイプラインの定義
        pipeline = skpipe.Pipeline([('Standardize', self.factor_standardizer_method(self.standardize_method)),
                                    ('Factors', skd.TruncatedSVD(self.num_factors, algorithm='arpack'))])
        initial_scaler = self.factor_standardizer_method(self.standardize_method)

        # 計算用のnumpy配列作成
        actual_data = self.series.to_numpy(copy=True)
        initial_nas = self.series.isna().to_numpy(copy=True)
        working_data = initial_scaler.fit_transform(self.series.fillna(value=self.series.mean(), axis='index').to_numpy(copy=True))

        # 初期モデルの推定
        factors = pipeline.fit_transform(working_data)
        data_hat_last = pipeline.inverse_transform(factors)

        # モデルが収束するまで反復
        iteration = 0
        distance = tolerance + 1
        while (iteration < max_iterations) and (distance > tolerance):
            factors = pipeline.fit_transform(working_data)
            data_hat = pipeline.inverse_transform(factors)
            distance = np.linalg.norm(data_hat - data_hat_last, 2) / np.linalg.norm(data_hat_last, 2)
            data_hat_last = data_hat.copy()
            working_data[initial_nas] = data_hat[initial_nas]
            iteration += 1

        # 結果の出力
        if iteration == max_iterations:
            print(f"EMアルゴリズムは最大反復回数{max_iterations}で収束に失敗しました。距離 = {distance}、許容範囲は{tolerance}でした")

        # 結果の保存
        actual_data[initial_nas] = initial_scaler.inverse_transform(working_data)[initial_nas]
        self.svdmodel = pipeline
        self.series_filled = pd.DataFrame(actual_data, index=self.series.index, columns=self.series.columns)
        self.factors = pd.DataFrame(factors, index=self.series_filled.index, columns=[f"F{i}" for i in range(1, factors.shape[1] + 1)])

    @staticmethod
    def V(X, factors, loadings):
        """
        ファクター分散
        """
        T, N = X.shape
        NT = N * T
        return np.linalg.norm(X - factors @ loadings, 2) / NT

    def baing(self):
        """
        Bai-Ng情報基準を使用して使用するファクターの数を決定
        参考文献: http://www.columbia.edu/~sn2294/pub/ecta02.pdf
        """
        # 推定パイプラインの定義
        pipeline = skpipe.Pipeline([('Standardize', self.factor_standardizer_method(self.standardize_method)),
                                    ('Factors', skd.TruncatedSVD(self.max_factors, algorithm='arpack'))])
        initial_scaler = self.factor_standardizer_method(self.standardize_method)

        # 設定
        working_data = initial_scaler.fit_transform(self.series.fillna(value=self.series.mean(), axis='index').to_numpy(copy=True))
        T, N = working_data.shape
        NT = N * T
        NT1 = N + T
        # 情報基準ペナルティの作成
        if self.ic_penalty_method == 1:
            penalty_terms = [i * math.log(NT / NT1) * NT1 / NT for i in range(self.max_factors)]
        elif self.ic_penalty_method == 2:
            penalty_terms = [i * math.log(min(N, T)) * NT1 / NT for i in range(self.max_factors)]
        elif self.ic_penalty_method == 3:
            penalty_terms = [i * math.log(min(N, T)) / min(N, T) for i in range(self.max_factors)]
        else:
            raise ValueError("ic_penalty_methodは1, 2, 3のいずれかである必要があります")

        # 最大ファクターでモデルをフィット
        factors = pipeline.fit_transform(working_data)
        loadings = pipeline['Factors'].components_
        explained_variance = [self.V(working_data, factors[:, 0:i], loadings[0:i, :]) for i in range(self.max_factors)]
        information_criteria = np.log(explained_variance) + penalty_terms
        optimal_num_factors = np.argmin(information_criteria)
        self.num_factors = optimal_num_factors

    def estimate_factors(self, start_date=None, end_date=None):
        """
        推定ルーチンを実行
        使用するファクターの数が指定されていない場合、その数を推定
        """
        self.start_date = start_date
        self.end_date = end_date
        self.apply_transforms()
        self.remove_outliers()
        if self.num_factors is None:
            self.baing()
        self.factors_em()
        return self.factors

