
# データ取得を統一的に扱うモジュール
import importlib
import os
from dotenv import load_dotenv
from data.alpha_vantage import get_data
from data import edinet, edinet_lifetechia, edgar, fred, investing, tiingo
from factor import fama_french, global_factors
import yfinance as yf
import pandas_datareader as web
from datetime import date
from dateutil.relativedelta import relativedelta

load_dotenv()

class FinancialDataFetcher:
    def __init__(self):
        self.alpha_vantage_key = os.getenv('ALPHAVANTAGE_API_KEY')
        self.edinet_key = os.getenv('EDINET_API')
        self.lifetechia_key = os.getenv('lifetechia_API')
        self.fred_key = os.getenv('FRED_API')
        self.tiingo_key = os.getenv('Tiingo_API')

    def get_historical_data(self, source, **kwargs):
        """ヒストリカルデータ取得"""
        if source == "alpha_vantage":
            return get_data("SYMBOL_SEARCH", self.alpha_vantage_key, **kwargs)
        elif source == "yahoo":
            return yf.download(**kwargs)
        elif source == "data_reader":
            #name =['AAPL'], data_source='stooq')
            return web.DataReader(**kwargs)
        elif source == "investing":
            fetcher = investing.InvestingDataFetcher(email=kwargs["email"])
             del kwargs["email"]
            return fetcher.get_data(kwargs["params"])
        elif source == "tiingo":
            tiingo_api = tiingo.TiingoAPI(self.tiingo_key)
            return tiingo_api.get_stock_tickers(**kwargs)
        else:
            raise ValueError("Invalid source for historical data")

    def get_financial_data(self, source, **kwargs):
        """財務データ取得"""
        if source == "edinet":
            api_client = edinet.EdinetAPIClient(self.edinet_key)
            doc_id = kwargs["doc_id"]
            # ZIPファイルのダウンロード
            zip_file_downloader = ZipFileDownloader(api_client)
            zip_file_downloader.download_zip_file(doc_id)

            # Initialize the DataParser with the extraction directory
            data_parser = DataParser(extract_dir=doc_id+'/XBRL/PublicDoc/')
            data_parser.get_xbrl_files()
            xbrl_p = XBRLParser(data_parser.get_xbrl_files()[0])
            df_std = xbrl_p.get_standard_data()
            del_files(doc_id)
            return df_std

        elif source == "lifetechia":
            return edinet_lifetechia.get_financial_data(self.lifetechia_key, **kwargs)
        elif source == "edgar":
            fetcher = edgar.EdgarDataFetcher(kwargs["email"])
            del kwargs["email"]
            if 'cik' in kwargs.keys() and 'concept_name' in kwargs.keys():
                return fetcher.get_company_concept(kwargs["cik"], kwargs["concept_name"])
            elif 'cik' in kwargs.keys():
                return fetcher.get_company_facts(kwargs["cik"])
            else:
                return fetcher.get_all_companies_concept(**kwargs)
        elif source == "fred":
            fred_api = fred.FREDData(self.fred_key)
            return fred_api.fetch_series_data(**kwargs)
        else:
            raise ValueError("Invalid source for financial data")

    def get_factor_data(self, source, **kwargs):
        """ファクター取得"""
        if source == "fama_french":
            return fama_french.get_ff(**kwargs)
        elif source == "global":
            return global_factors.get_global_factor(**kwargs)
        else:
            raise ValueError("Invalid source for factor data")

