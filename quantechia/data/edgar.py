# EDGAR データ取得
import requests
import pandas as pd

class EdgarDataFetcher:
    BASE_URL = "https://data.sec.gov"
    TICKER_URL = "https://www.sec.gov/files/company_tickers.json"

    def __init__(self, email, print_url=False):
        """Initialize the fetcher with a user-provided email for the User-Agent."""
        self.headers = {"User-Agent": email}
        
        self.print_url = print_url

    def get_data(self, url):
        """Fetch JSON data from the specified URL."""
        if self.print_url:
            print(url)
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to retrieve data. Status code: {response.status_code}")
            return None

    def _load_ticker_data(self):
        """Load and preprocess company ticker data."""
        data = self.get_data(self.TICKER_URL)
        if data:
            df = pd.DataFrame(data).T
            df.columns = ["cik", "ticker", "title"]
            df["cik"] = df["cik"].apply(lambda x: f"{int(x):010d}")  # Format CIK as 10-digit string
            return df
        return None

    def search_cik(self, query):
        """Search for a company by ticker or name and return its CIK."""
        self.ticker_df = self._load_ticker_data()
        if self.ticker_df is None:
            print("Ticker data is not available.")
            return None
        
        result = self.ticker_df[
            (self.ticker_df["ticker"].str.contains(query, case=False, na=False)) |
            (self.ticker_df["title"].str.contains(query, case=False, na=False))
        ]
        return result if not result.empty else None

    def get_company_submissions(self, cik):
        """Retrieve recent filings for a given company."""
        url = f"{self.BASE_URL}/submissions/CIK{cik}.json"
        data = self.get_data(url)
        return pd.DataFrame(data["filings"]["recent"]) if data else None

    def get_company_concept(self, cik, concept_name, unit="USD"):
        """Retrieve financial data for a specific company and concept."""
        cik = str(cik).zfill(10)
        url = f"{self.BASE_URL}/api/xbrl/companyconcept/CIK{cik}/us-gaap/{concept_name}.json"
        data = self.get_data(url)
        return pd.DataFrame(data["units"].get(unit, [])) if data else None

    def get_all_companies_concept(self, concept_name, period, unit="USD"):
        """Retrieve financial data for all companies for a given period."""
        url = f"{self.BASE_URL}/api/xbrl/frames/us-gaap/{concept_name}/{unit}/{period}.json"
        data = self.get_data(url)
        return pd.DataFrame(data["data"]) if data else None

    def get_company_facts(self, cik):
        """Retrieve all financial data for a specific company."""
        cik = str(cik).zfill(10)
        url = f"{self.BASE_URL}/api/xbrl/companyfacts/CIK{cik}.json"
        data = self.get_data(url)
        return pd.DataFrame(data["facts"]["us-gaap"]).T if data else None

    def get_concepts_data(self, concept_dict):
    #     concept_dict = {
    #     'NetIncomeLoss': [['USD', f'CY{base_date}']],
    #     'StockholdersEquity': [['USD', f'CY{base_date}I']],
    #     'CommonStockSharesOutstanding': [['shares', f'CY{base_date}I']],
    #     'Assets': [['USD', f'CY{base_date}I'], ['USD', f'CY{date_b}I']]
    # }

        df = pd.DataFrame()
        for concept_name, params_list in concept_dict.items():
            for i, (unit, period) in enumerate(params_list):
                df_ = self.get_all_companies_concept(concept_name, period, unit)
                df_ = df_.loc[:, ['cik', 'end', 'val']].rename(columns={'val': f"{concept_name}_{i}" if i != 0 else concept_name})

                if df.empty:
                    df = df_
                else:
                    df = pd.merge(df, df_, on=['cik'], how='outer', suffixes=('', '_new'))
                    
                    # `end` が NaN の場合、新しく取得した `end_new` で補完
                    df['end'] = df['end'].fillna(df['end_new'])
                    
                    # 補完が終わったら `end_new` は不要なので削除
                    df.drop(columns=['end_new'], inplace=True)
        return df



