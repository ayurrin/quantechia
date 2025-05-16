import urllib.parse
import httpx as req
import pandas as pd


class InvestingDataFetcher:
    BASE_URL = "http://api.scraperlink.com/investpy/"
    REQUIRED_PARAMS = {
        'stocks': {'type', 'country', 'symbol', 'from_date', 'to_date'},
        'cryptos': {'type', 'symbol', 'from_date', 'to_date'},
        'currency_crosses': {'type', 'name', 'from_date', 'to_date'},
        'bonds': {'type', 'from_date', 'to_date'},
        'commodities': {'type', 'from_date', 'to_date'},
        'etfs': {'type', 'from_date', 'to_date'},
        'funds': {'type', 'from_date', 'to_date'},
        'indices': {'type', 'from_date', 'to_date'},
        'certificates': {'type', 'from_date', 'to_date'}
    }

    def __init__(self, email):
        self.email = email

    def generate_url(self, product='stock', **kwargs):
        if product not in self.REQUIRED_PARAMS:
            raise ValueError("Invalid product specified.")

        missing_params = self.REQUIRED_PARAMS[product] - set(kwargs.keys())
        if missing_params:
            raise ValueError(f"Required parameters are missing: {', '.join(missing_params)}")

        params = urllib.parse.urlencode(kwargs)
        return f"{self.BASE_URL}?email={self.email}&product={product}&{params}"

    def get_data(self, **params):
        url = self.generate_url(**params)
        print(url)
        res = req.get(url, timeout=60)

        if res.text.lower() in ('email verification sent.', 'email address not verified.'):
            raise PermissionError('The Scraper API sent a verification link to your email address. Please verify your email before running the code again.')

        if res.status_code in (400, 404, 401, 500):
            raise RuntimeError(f"Error {res.status_code}: {res.text}")

        if res.status_code != 200:
            raise RuntimeError(f"Unknown error {res.status_code}: {res.text}")

        res_json = res.json().get('data', [])
        if not res_json:
            return pd.DataFrame()

        raw_df = pd.DataFrame(res_json)
        df = raw_df[['last_close', 'last_open', 'last_max', 'last_min', 'volumeRaw', 'change_precent']].copy()
        df.rename(columns={
            'last_close': 'Price',
            'last_open': 'Open',
            'last_max': 'High',
            'last_min': 'Low',
            'volumeRaw': 'Volume',
            'change_precent': 'Change'
        }, inplace=True)

        df['Date'] = pd.to_datetime(raw_df['rowDateTimestamp']).dt.strftime('%Y-%m-%d')
        return df.set_index('Date')


