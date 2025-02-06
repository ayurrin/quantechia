import requests
import pandas as pd
from urllib.parse import urlencode, quote

def get_financial_data(api_key, company_name=None, sec_code=None, doc_id=None, start_date=None, end_date=None):
    """
    財務データを取得する関数

    Args:
        api_url (str): APIのベースURL
        api_key (str): APIキー
        company_name (str, optional): 企業名
        sec_code (list or str, optional): 証券コード（単体またはリスト）
        doc_id (list or str, optional): ドキュメントID（単体またはリスト）
        start_date (str, optional): 開始日（YYYY-MM-DD）
        end_date (str, optional): 終了日（YYYY-MM-DD）

    Returns:
        pd.DataFrame: 取得したデータのデータフレーム
    """
    api_url = "https://lifetechia.com/wp-json/financial/v1/get/"
    # パラメータ辞書を作成
    params = {}

    if company_name:
        params["company_name"] = company_name

    if sec_code:
        if isinstance(sec_code, list):
            params["sec_code[]"] = sec_code  # リスト形式に対応
        else:
            params["sec_code"] = sec_code

    if doc_id:
        if isinstance(doc_id, list):
            params["doc_id[]"] = doc_id  # リスト形式に対応
        else:
            params["doc_id"] = doc_id

    if start_date:
        params["start_date"] = start_date

    if end_date:
        params["end_date"] = end_date

    # クエリパラメータをエンコード
    query_string = urlencode(params, doseq=True)
    final_url = f"{api_url}?{query_string}" if params else api_url  # パラメータがない場合はそのままアクセス

    # APIリクエスト用のヘッダー
    headers = {"X-API-Key": api_key}

    # APIリクエストの送信
    response = requests.get(final_url, headers=headers)

    # レスポンスの処理
    if response.status_code == 200:
        data = response.json()
        return pd.DataFrame(data)  # データフレームに変換
    else:
        print("Error:", response.status_code, response.text.encode().decode('unicode_escape'))
        return pd.DataFrame()  # 空のデータフレームを返す
