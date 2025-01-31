import requests
import pandas as pd
from io import StringIO

def get_data(function, api_key, params=None, is_df=True, df_name=None, csv=False):
    # ベースURL
    base_url = f'https://www.alphavantage.co/query?function={function}'
    
    # パラメータを追加
    if params:
        param_list = []
        for key, value in params.items():
            if isinstance(value, list):
                for v in value:
                    param_list.append(f'{key}={v}')
            else:
                param_list.append(f'{key}={value}')
        
        param_str = '&'.join(param_list)
        url = f'{base_url}&{param_str}'
    else:
        url = base_url
    
    url += f'&apikey={api_key}'
    print(url)
    if csv:
        with requests.Session() as s:
            download = s.get(url)
            decoded_content = download.content.decode('utf-8')
        
            # StringIOを使ってPandasのデータフレームに変換
            df = pd.read_csv(StringIO(decoded_content))
        return df

    r = requests.get(url)
    data = r.json()
    
    if is_df:
        if df_name and df_name in data:
            df_data = data[df_name]
        else:
            # 最も長いリストを持つキーを検索
            max_len = 0
            df_data = None
            for key, value in data.items():
                if isinstance(value, list) and len(value) > max_len:
                    max_len = len(value)
                    df_data = value
        if df_data:
            df = pd.DataFrame(df_data)
        else:
            df = pd.DataFrame([data])  
    
        return df
    else:
        return data
