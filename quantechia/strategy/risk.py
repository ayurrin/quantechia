from .basestrategy import BaseStrategy
import scipy.optimize as op
import numpy as np
import pandas as pd
from scipy.optimize import minimize
import riskfolio as rp
from abc import ABC, abstractmethod

def cal_risk_parity(Sigma):
    n = Sigma.shape[0]

    def calculate_portfolio_var(w, Sigma):
        w = np.matrix(w)
        return np.dot(np.dot(w, Sigma), w.T)

    def calculate_risk_contribution(w, Sigma):
        w = np.matrix(w)
        sigma_p = np.sqrt(calculate_portfolio_var(w, Sigma))
        RC = np.multiply(np.dot(Sigma, w.T), w.T) / sigma_p
        return RC

    def risk_parity_objective(w):
        sigma_p = np.sqrt(calculate_portfolio_var(w, Sigma))
        risk_target = np.asmatrix(np.multiply(sigma_p, [1. / n] * n))
        RC = calculate_risk_contribution(w, Sigma)
        obj = sum(np.square(RC - risk_target.T))
        return obj

    cons = [{'type': 'eq', 'fun': lambda w: np.sum(w) - 1}]
    bnds = [(0, None)] * n
    x0 = [1. / n] * n

    result = op.minimize(risk_parity_objective, x0=x0, method='SLSQP', bounds=bnds, constraints=cons)

    if not result.success:
        raise ValueError("Risk parity optimization failed: " + result.message)

    return result.x
class RiskParityStrategyScipy(BaseStrategy):
    """
    Rolling Risk Parity Strategy using user-defined cal_risk_parity.
    """

    def __init__(self, price_data: pd.DataFrame, lookback: int = 60, **kwargs):
        super().__init__(price_data, **kwargs)
        self.lookback = lookback

    def calculate_weight(self):
        """
        Calculate rolling risk parity weights using past `lookback` days and custom optimizer.
        """
        dates = self.rtn_data.index
        assets = self.rtn_data.columns
        weights = []

        for i in range(len(self.rtn_data)):
            if i < self.lookback:
                weights.append([np.nan] * len(assets))
                continue

            window_rtn = self.rtn_data.iloc[i - self.lookback:i]
            Sigma = (100*window_rtn).cov().values  # 共分散行列

            try:
                w_opt = cal_risk_parity(Sigma)
            except Exception as e:
                print(f"Optimization failed at index {i}: {e}")
                w_opt = [np.nan] * len(assets)

            weights.append(w_opt)

        self.weight = pd.DataFrame(weights, index=dates, columns=assets)
        return self.weight



class BaseRiskfolioStrategy(BaseStrategy, ABC):
    """
    Riskfolio-Libベースの柔軟な戦略クラス（統合版）
    """

    def __init__(self, price_data: pd.DataFrame, lookback: int = 60,
                 optimizer: str = 'optimization', strategy_name: str = "Flexible Strategy",
                 opt_params: dict = None, **kwargs):
        super().__init__(price_data, **kwargs)
        self.lookback = lookback
        self.optimizer = optimizer
        self.strategy_name = strategy_name
        self.opt_params = opt_params if opt_params is not None else {}

    def _create_portfolio(self, returns: pd.DataFrame, **kwargs) -> rp.Portfolio:
        """
        rp.Portfolioの生成。引数は自由に渡せる。
        """
        # 例えば returns は必須で、他は任意のkwargで
        portfolio_args = kwargs.get('portfolio_args', {})
        port = rp.Portfolio(returns=returns, **portfolio_args)
        return port

    def _apply_preprocessing(self, port: rp.Portfolio, preprocessing_params: dict):
        """
        複数の前処理メソッドを条件に応じて呼ぶ
        preprocessing_params = {
            'assets_stats': { ... },
            'blacklitterman_stats': { ... },
            'factors_stats': { ... },
            'blfactors_stats': { ... },
            'wc_stats': { ... }
        }
        """
        if 'assets_stats' in preprocessing_params:
            port.assets_stats(**preprocessing_params['assets_stats'])

        if 'blacklitterman_stats' in preprocessing_params:
            port.blacklitterman_stats(**preprocessing_params['blacklitterman_stats'])

        if 'factors_stats' in preprocessing_params:
            port.factors_stats(**preprocessing_params['factors_stats'])

        if 'blfactors_stats' in preprocessing_params:
            port.blfactors_stats(**preprocessing_params['blfactors_stats'])

        if 'wc_stats' in preprocessing_params:
            port.wc_stats(**preprocessing_params['wc_stats'])

        if 'custom_stats' in preprocessing_params:
            for func, params in preprocessing_params['custom_stats'].items():
                if hasattr(port, func):
                    getattr(port, func)(**params)
                else:
                    raise ValueError(f"Function {func} not found in Portfolio class.")

    def _generate_opt_params(self, window_rtn) -> dict:
        """
        最適化用のパラメータを生成するメソッド。
        ここで定義したパラメータは、_optimize_weightsメソッドで使用される。
        """
        opt_params = self.opt_params.copy()
        
        return opt_params

    def _update_opt_params(self, opt_params: dict, port: rp.Portfolio) -> dict:
        """
        最適化用のパラメータを更新するメソッド。
        ここで定義したパラメータは、_optimize_weightsメソッドで使用される。
        """

        return opt_params

    def _optimize_weights(self, window_rtn: pd.DataFrame) -> np.ndarray:
        opt_params = self._generate_opt_params(window_rtn)
        # Portfolio生成時に必要な引数（もしあれば）
        portfolio_args = self.opt_params.get('portfolio_args', {})
        port = self._create_portfolio(window_rtn, portfolio_args=portfolio_args)

        opt_params = self._update_opt_params(opt_params, port)

        # 前処理のパラメータ辞書（空でもOK）
        preprocessing_params = opt_params.get('preprocessing_params', {})
        # 前処理を適用
        self._apply_preprocessing(port,  preprocessing_params)

        # 最適化用パラメータ
        optimize_params = opt_params.get('optimize_params', {})

        

        if self.optimizer == 'rp':
            w = port.rp_optimization(**optimize_params)
        elif self.optimizer == 'rrp':
            w = port.rrp_optimization(**optimize_params)
        elif self.optimizer == 'wc':
            w = port.wc_optimization(**optimize_params)
        elif self.optimizer == 'frc':
            w = port.frc_optimization(**optimize_params)
        else:
            optimize_params['obj'] = opt_params.get('obj', 'Sharpe')
            w = port.optimization(**optimize_params)

        return w.values.flatten()
    
    def calculate_weight(self) -> pd.DataFrame:
        dates = self.rtn_data.index
        assets = self.rtn_data.columns
        weights = []

        for i in range(len(self.rtn_data)):
            if i < self.lookback:
                weights.append([np.nan] * len(assets))
                continue

            window_rtn = self.rtn_data.iloc[i - self.lookback:i]

            try:
                w = self._optimize_weights(window_rtn)
                weights.append(w)
            except Exception as e:
                print(f"Optimization failed at index {i}: {e}")
                weights.append([np.nan] * len(assets))

        self.weight = pd.DataFrame(weights, index=dates, columns=assets)
        return self.weight
    
DEFAULT_OPT_PARAMS = {
    'preprocessing_params': {
        'assets_stats': {
            'method_mu': 'hist',
            'method_cov': 'ledoit'
        }
    },
    'optimize_params': {}
    
}

class RiskParityStrategy(BaseRiskfolioStrategy):
    def __init__(self, price_data, lookback=60, **kwargs):
        kwargs.setdefault('strategy_name', 'Risk Parity')
        super().__init__(
            price_data,
            lookback=lookback,
            optimizer='rp',
            opt_params=DEFAULT_OPT_PARAMS,
            **kwargs
        )
class RobustRiskParityStrategy(BaseRiskfolioStrategy):
    def __init__(self, price_data, lookback=60, **kwargs):
        kwargs.setdefault('strategy_name', 'Robust Risk Parity')
        super().__init__(
            price_data,
            lookback=lookback,
            optimizer='rrp',
            opt_params=DEFAULT_OPT_PARAMS,
            **kwargs
        )


class WorstCaseStrategy(BaseRiskfolioStrategy):
    def __init__(self, price_data, lookback=60, **kwargs):
        kwargs.setdefault('strategy_name', 'Worst Case Optimization')
        super().__init__(
            price_data,
            lookback=lookback,
            optimizer='wc',
            opt_params=DEFAULT_OPT_PARAMS,
            **kwargs
        )


class ForwardRobustStrategy(BaseRiskfolioStrategy):
    def __init__(self, price_data, lookback=60, **kwargs):
        kwargs.setdefault('strategy_name', 'Forward Robust Optimization')
        super().__init__(
            price_data,
            lookback=lookback,
            optimizer='frc',
            opt_params=DEFAULT_OPT_PARAMS,
            **kwargs
        )


class SharpeOptimizationStrategy(BaseRiskfolioStrategy):
    def __init__(self, price_data, lookback=60, obj='Sharpe', **kwargs):
        kwargs.setdefault('strategy_name', 'Sharpe Ratio Optimization')
        custom_params = DEFAULT_OPT_PARAMS.copy()
        custom_params.update({'obj': obj})
        super().__init__(
            price_data,
            lookback=lookback,
            optimizer='optimization',
            opt_params=custom_params,
            **kwargs
        )


class BlackLittermanStrategy(BaseRiskfolioStrategy):
    """
    Black-Litterman戦略：過去30日のr/r（Sharpe-like）に基づいてViewを生成。
    """

    def __init__(self, price_data: pd.DataFrame, lookback: int = 60,bl_view_window: int = 60,
                 top_k: int = 3, opt_params=None, **kwargs):
        if opt_params is None:
            opt_params = {
                'portfolio_args': {},
                'preprocessing_params': {
                    'assets_stats': {
                        'method_mu': 'hist',
                        'method_cov': 'ledoit'
                    }
                },
                'optimize_params': {'model': 'BL'},
            }
        super().__init__(price_data, lookback=lookback, optimizer='optimization',opt_params=opt_params, **kwargs)
        self.bl_view_window = bl_view_window  # View生成に使う日数
        self.top_k = min(top_k,len(price_data.columns))  # View対象の上位銘柄数

    def _generate_bl_views(self, window_rtn: pd.DataFrame):
        """
        Black-Litterman用のViewを生成
        """
        view_rtn = window_rtn[-self.bl_view_window:]
        mu = view_rtn.mean()
        sigma = view_rtn.std()
        rr = mu / sigma  # Sharpe-like ratio

        top_assets = rr.nlargest(self.top_k).index.tolist()

        n_assets = window_rtn.shape[1]
        P = []
        Q = []

        for asset in top_assets:
            p = [0.0] * n_assets
            idx = window_rtn.columns.get_loc(asset)
            p[idx] = 1.0
            P.append(p)
            Q.append(mu[asset])  

        return pd.DataFrame(P), pd.DataFrame(Q)

    def _update_opt_params(self,opt_params, port) -> dict:
        opt_params = opt_params.copy()
        window_rtn = port.returns
        # Black-Litterman View生成
        P, Q = self._generate_bl_views(window_rtn)
        if 'preprocessing_params' in opt_params:
            opt_params['preprocessing_params'] = {
                **opt_params['preprocessing_params'],
                'blacklitterman_stats': {
                    'P': P,
                    'Q': Q,
                }}
        else:

            opt_params['preprocessing_params'] = {
                'assets_stats': {
                    'method_mu': 'hist',
                    'method_cov': 'ledoit'
                },
                'blacklitterman_stats': {
                    'P': P,
                    'Q': Q,
                }
            }

        return opt_params
        