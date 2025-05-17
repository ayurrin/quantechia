# Global Factor Data データ取得
import shutil
import requests
import zipfile
import pandas as pd
from bs4 import BeautifulSoup
import os

def get_global_factor(country='all_countries', theme='all_themes', term='monthly', cap='vw_cap'):
    # ダウンロードするファイルのURL
    url = f'https://jkpfactors.s3.amazonaws.com/public/%5B{country}%5D_%5B{theme}%5D_%5B{term}%5D_%5B{cap}%5D.zip'
    # ダウンロード用のセッションを作成
    session = requests.Session()
    response = session.get(url)

    # ファイル名の取得
    filename = url.split('/')[-1]  # URLの最後の部分をファイル名として使用

    # ファイルをダウンロード
    with open(filename, 'wb') as f:
        f.write(response.content)

    # ZIPファイルを解凍するディレクトリ
    extract_dir = 'tmp/' 
    if not os.path.exists(extract_dir):
        os.makedirs(extract_dir)

    # ZIPファイルを解凍
    with zipfile.ZipFile(filename, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)

    # 解凍されたCSVファイルのリストを取得
    csv_files = [f for f in os.listdir(extract_dir) if f.endswith('.csv')]

    # CSVファイルをPandasデータフレームに読み込む
    data_frames = []
    for csv_file in csv_files:
        csv_file_path = os.path.join(extract_dir, csv_file)
        df = pd.read_csv(csv_file_path)
        data_frames.append(df)

    # データフレームを結合
    if data_frames:
        df = pd.concat(data_frames, ignore_index=True)
    else:
        df = pd.DataFrame()  # 空のデータフレームを返す

    # 使用済みファイルの削除
    os.remove(filename)  # ZIPファイル削除
    shutil.rmtree(extract_dir)  # 解凍したフォルダごと削除

    return df