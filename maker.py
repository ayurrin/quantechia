import os

def create_data_folders():
    base_dir = "data"
    files = {
        "data/utils.py": """# 共通ユーティリティ関数""",
        "data/alpha_vantage.py": """# Alpha Vantage データ取得""",
        "data/edinet.py": """# EDINET データ取得""",
        "data/edgar.py": """# EDGAR データ取得""",
        "data/fred.py": """# FRED データ取得""",
        "data/yahoo_finance.py": """# Yahoo Finance データ取得""",
        "data/investing.py": """# Investing.com データ取得""",
        "data/stooq.py": """# Stooq データ取得""",
        "data/tiingo.py": """# Tiingo データ取得""",
        "data/econdb.py": """# Econdb データ取得""",
        "data/bank_of_canada.py": """# Bank of Canada データ取得""",
        "data/world_bank.py": """# World Bank データ取得""",
        "data/fama_french.py": """# Fama French データ取得""",
        "data/global_factors.py": """# Global Factor Data データ取得""",
        "data/data_fetcher.py": """
# データ取得を統一的に扱うモジュール
import importlib

def fetch_data(source, *args, **kwargs):
    try:
        module = importlib.import_module(f"data.{source}")
        if hasattr(module, "fetch"):
            return module.fetch(*args, **kwargs)
        else:
            raise AttributeError(f"{source} に 'fetch' 関数がありません")
    except ModuleNotFoundError:
        raise ImportError(f"{source} モジュールが見つかりません")
"""
    }
    
    os.makedirs(base_dir, exist_ok=True)
    
    for file_path, content in files.items():
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
    
if __name__ == "__main__":
    create_data_folders()