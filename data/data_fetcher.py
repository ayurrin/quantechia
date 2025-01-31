
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
