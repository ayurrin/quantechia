# Tiingo データ取得
import requests
import pandas as pd
from io import StringIO

class TiingoAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.tiingo.com/"

    def get_data(self, endpoint, csv=False, is_df=True, df_name=None, params=None):
        url = f"{self.base_url}{endpoint}?token={self.api_key}"
        headers = {'Content-Type': 'application/json'}
        
        if params:
            url += "&" + "&".join(f"{k}={v}" for k, v in params.items())

        if csv:
            with requests.Session() as s:
                download = s.get(url, headers=headers)
                decoded_content = download.content.decode('utf-8')
                df = pd.read_csv(StringIO(decoded_content))
            return df

        response = requests.get(url, headers=headers)
        data = response.json()

        if is_df:
            df_data = None
            if df_name and df_name in data:
                df_data = data[0][df_name]
            elif isinstance(data, list):
                max_len = 0
                for key, value in data[0].items():
                    if isinstance(value, list) and len(value) > max_len:
                        max_len = len(value)
                        df_data = value
            
            if df_data:
                return pd.DataFrame(df_data)
            return pd.DataFrame(data if isinstance(data, list) else [data])

        return data

    def get_company_info(self, ticker):
        return self.get_data(f"tiingo/daily/{ticker}")

    def get_news(self):
        return self.get_data("tiingo/news")

    def get_crypto_prices(self, tickers):
        return self.get_data("tiingo/crypto/prices", params={"tickers": tickers})

    def get_crypto_ticker(self, ticker):
        return self.get_data(f"tiingo/crypto", params={"tickers": ticker}, is_df=False)

    def get_forex_prices(self, tickers):
        return self.get_data("tiingo/fx/prices", params={"tickers": tickers})

    def get_forex_top(self, tickers):
        return self.get_data("tiingo/fx/top", params={"tickers": tickers})

    def get_stock_tickers(self, tickers):
        return self.get_data("iex", params={"tickers": tickers})

    def get_historical_stock_prices(self, ticker, start_date, freq="5min", columns="open,high,low,close,volume"):
        return self.get_data(f"iex/{ticker}/prices", params={
            "startDate": start_date,
            "resampleFreq": freq,
            "columns": columns
        })

    def get_fundamentals(self, ticker):
        return self.get_data(f"tiingo/fundamentals/{ticker}/daily")



