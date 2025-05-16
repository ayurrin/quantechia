
# データ取得を統一的に扱うモジュール
import importlib
import os
from dotenv import load_dotenv
from data.alpha_vantage import get_data
from data import edinet, edinet_lifetechia, edgar, fred, investing, tiingo

import yfinance as yf
import pandas_datareader as web
from datetime import date
from dateutil.relativedelta import relativedelta
import pandas as pd
import requests
import time
import numpy as np

import importlib
from data import alpha_vantage
importlib.reload(alpha_vantage)
load_dotenv()

class FinancialDataFetcher:
    def __init__(self):
        self.alpha_vantage_key = os.getenv('ALPHAVANTAGE_API_KEY')
        self.edinet_key = os.getenv('EDINET_API')
        self.lifetechia_key = os.getenv('lifetechia_API')
        self.fred_key = os.getenv('FRED_API')
        self.tiingo_key = os.getenv('Tiingo_API')
        self.email = os.getenv('email')
    def ticker_search(self, source, **kwargs):
        return get_data("SYMBOL_SEARCH", self.alpha_vantage_key, **kwargs)
        

    def get_historical_data(self, source, **kwargs):
        """ヒストリカルデータ取得"""
        if source == "alpha_vantage":
            function = kwargs.pop('function', 'TIME_SERIES_DAILY')
            res = get_data(function, self.alpha_vantage_key,is_df=False, **kwargs)
            stock_data = pd.DataFrame.from_dict(res[list(res.keys())[1]], orient="index", dtype=float)
            return stock_data
        elif source == "yahoo":
            return yf.download(**kwargs)
        elif source == "data_reader":
            #name =['AAPL'], data_source='stooq')
            return web.DataReader(**kwargs).sort_index()
        elif source == "investing":
            fetcher = investing.InvestingDataFetcher(email=self.email)
            return fetcher.get_data(**kwargs)
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
            zip_file_downloader = edinet.ZipFileDownloader(api_client)
            zip_file_downloader.download_zip_file(doc_id)

            # Initialize the DataParser with the extraction directory
            data_parser = edinet.DataParser(extract_dir=doc_id+'/XBRL/PublicDoc/')
            data_parser.get_xbrl_files()
            xbrl_p = edinet.XBRLParser(data_parser.get_xbrl_files()[0])
            df_std = xbrl_p.get_standard_data()
            edinet.del_files(doc_id)
            return df_std

        elif source == "lifetechia":
            return edinet_lifetechia.get_financial_data(self.lifetechia_key, **kwargs)
        elif source == "edgar":
            fetcher = edgar.EdgarDataFetcher(self.email)
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

    

#other source
#fred database https://www.stlouisfed.org/research/economists/mccracken/fred-databases
def get_fredmd():
    df = pd.read_csv("https://www.stlouisfed.org/-/media/project/frbstl/stlouisfed/research/fred-md/monthly/current.csv")
    df = df.iloc[1:,:].set_index('sasdate')
    df.index = pd.to_datetime(df.index, format='%m/%d/%Y')
    return df
def get_fredqd():
    df = pd.read_csv("https://www.stlouisfed.org/-/media/project/frbstl/stlouisfed/research/fred-md/quarterly/current.csv")
    df = df.iloc[2:,:].set_index('sasdate')
    df.index = pd.to_datetime(df.index, format='%m/%d/%Y')
    return df


#TOPIX Ticker
def get_topix_list(list_type='TPX'):
    '''#TOPIX銘柄コードの取得
    TPX:all
    TX30:Core30
    TX100:TOPIX100
    TX500:TOPIX500
    TX1000:TOPIX1000

    ・TOPIX Core30…TOPIX Core30、TOPIX 100（大型株）、TOPIX 500、TOPIX 1000
    ・TOPIX Large70…TOPIX Large70、TOPIX 100（大型株）、TOPIX 500、TOPIX 1000
    ・TOPIX Mid400…TOPIX Mid400（中型株）、TOPIX 500、TOPIX 1000
    ・TOPIX Small500 (TOPIX Small 1)…TOPIX Small（小型株）、TOPIX Small500、TOPIX 1000
    ・TOPIX Small 2…TOPIX Smalｌ（小型株） (TOPIX1000には含まれません)
    '''
    # CSVファイルのURL
    url = "https://www.jpx.co.jp/automation/markets/indices/topix/files/topixweight_j.csv"

    # HTTPリクエストを送信してファイルをダウンロード
    response = requests.get(url)

    
    # カレントディレクトリを取得
    current_dir = os.getcwd()
    file_path = os.path.join(current_dir, "topixweight_j.csv")

    # ステータスコードが200（成功）の場合
    if response.status_code == 200:
        # ダウンロードしたCSVデータをファイルに保存
        with open(file_path, "wb") as f:
            f.write(response.content)

        # ファイルをPandas DataFrameに読み込む
        data_df = pd.read_csv(file_path, encoding='shift-jis')

    else:
        print(f"Failed to download the file. Status code: {response.status_code}")
    if list_type == 'TX30':
        topix_list = list(data_df[(data_df['ニューインデックス区分']=='TOPIX Core30')]['コード'].astype(str))
    elif list_type == 'TX100':
        topix_list = list(data_df[(data_df['ニューインデックス区分']=='TOPIX Core30') | (data_df['ニューインデックス区分']=='TOPIX Large70') ]['コード'].astype(str))
    elif list_type == 'TX500':
        topix_list = list(data_df[(data_df['ニューインデックス区分']=='TOPIX Mid400')|(data_df['ニューインデックス区分']=='TOPIX Core30') | (data_df['ニューインデックス区分']=='TOPIX Large70') ]['コード'].astype(str))
    elif list_type == 'TX1000':
        topix_list = list(data_df[(data_df['ニューインデックス区分']=='TOPIX Small 1')|(data_df['ニューインデックス区分']=='TOPIX Mid400')|(data_df['ニューインデックス区分']=='TOPIX Core30') | (data_df['ニューインデックス区分']=='TOPIX Large70') ]['コード'].astype(str))
    else:
        topix_list = list(data_df['コード'].astype(str))
    os.remove(file_path)
    return topix_list

def get_sp_data():
    # S&P 500構成銘柄がリストされているWikipediaページのURL
    url = 'http://en.wikipedia.org/wiki/List_of_S%26P_500_companies'

    # Wikipediaページ中のすべての表を読み込む
    tables = pd.read_html(url)

    # S&P 500構成銘柄が含まれる最初の表を取得
    df_sp500 = tables[0]
    columns = [
        'Symbol', 'Security', 'GICS Sector', 'GICS Sub-Industry',
        'Headquarters Location', 'Date added', 'CIK', 'Founded'
    ]
    df_sp500.columns = columns
    return df_sp500


def get_yf_rtn(ticker_list, log_rtn=False,raw=False, **args):
    price_df = yf.download(ticker_list, **args)
    if raw:
        return price_df
    if log_rtn:
        rtn = np.log(price_df['Close'] / price_df['Close'].shift(1))
    else:
        rtn = price_df[['Close']].pct_change()
    return rtn.iloc[1:,:]

def get_stooq_rtn(ticker_list,log_rtn=False,raw=False, **args):
    
    price_sq =  web.DataReader(ticker_list,data_source='stooq', **args).sort_index()
    if raw:
        return price_sq
    if log_rtn:
        rtn = np.log(price_sq['Close'] / price_sq['Close'].shift(1))
    else:
        rtn = price_sq['Close'].pct_change()
    return rtn.iloc[1:,:]

def get_av_rtn_(ticker, log_rtn=False,raw=False, **args):
    fetcher = FinancialDataFetcher()
    price_df = fetcher.get_historical_data("alpha_vantage", symbol=ticker,**args)

    if raw:
        return price_df
    if log_rtn:
        rtn = np.log(price_df['4. close'] / price_df['4. close'].shift(1))
    else:
        rtn = price_df[['4. close']].pct_change()
    return rtn.iloc[1:,:]
def get_av_rtn(ticker_list, log_rtn=False,raw=False, **args):
    rtn = pd.DataFrame()
    for ticker in ticker_list:
        rtn_ = get_av_rtn_(ticker, log_rtn, raw, **args)
        rtn = pd.concat([rtn, rtn_],axis=1)
        time.sleep(0.5)
    return rtn


def get_recession_df():
    url = "https://www.nber.org/sites/default/files/2023-03/BCDC_spreadsheet_for_website.xlsx"

    # Read the Excel file into a DataFrame
    df = pd.read_excel(url, engine='openpyxl')
    df.columns = df.iloc[1,:]
    df = df.iloc[3:-7,2:10]
    df.columns = [
        'start','end', 'Peak month number',  'Trough month number', 'Duration, peak to trough', 'Duration, trough to peak','Duration, trough to trough', 'Duration, peak to peak'
    ]

    # Function to convert the date string to the desired format
    def convert_date(date_str):
        # Extract the month and year part
        month_year = date_str.split('(')[0]
        # Convert to datetime object
        date_obj = pd.to_datetime(month_year, format='%B %Y ')
        # Get the last day of the month
        last_day = date_obj + pd.offsets.MonthEnd(0)
        # Convert to desired string format
        return last_day.strftime('%Y%m%d')


    # Apply the function to the 'date' column
    df['start_str'] = df['start'].apply(convert_date)
    df['end_str'] = df['end'].apply(convert_date)
    df['start_date'] = pd.to_datetime(df['start_str'],format='%Y%m%d')
    df['end_date'] = pd.to_datetime(df['end_str'],format='%Y%m%d')

    date_range = pd.date_range(start=df['start_date'].min(), end=pd.Timestamp.now().normalize() + pd.offsets.MonthEnd(0), freq='ME')

    # Create a DataFrame with the date_range as index and a 'recession' column initialized to 0
    recession_df = pd.DataFrame(index=date_range)
    recession_df['recession'] = 0

    # Set recession periods based on start_date and end_date
    for _, row in df.iterrows():
        recession_df.loc[row['start_date']:row['end_date'], 'recession'] = 1
    return recession_df