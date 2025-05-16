from factor import fredmd
from factor import fama_french, global_factors
import importlib
import os
import pandas as pd

def get_factor_data(source, **kwargs):
    """ファクター取得"""
    if source == "fama_french":
        return fama_french.get_ff(**kwargs)
    elif source == "global":
        return global_factors.get_global_factor(**kwargs)
    elif source == 'fredmd':
        return get_fredmd_factor(**kwargs)
    else:
        raise ValueError("Invalid source for factor data")

def get_fredmd_factor(**args):
    fred_md = fredmd.FredMD(**args)
    fred_md.estimate_factors()
    factors = fred_md.factors
    return factors