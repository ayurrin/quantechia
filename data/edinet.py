import datetime
import requests
import time
import unicodedata
import pandas as pd
import zipfile
import os

import re
import numpy as np
from arelle import Cntlr, ViewFileFactTable, ModelDtsObject, XbrlConst,ViewFileFactList
from arelle.XbrlConst import conceptNameLabelRole, standardLabel, terseLabel, documentationLabel

import requests
import zipfile
import os
import shutil
def del_files(doc_id):
        # フォルダの削除
    folder_name = doc_id
    shutil.rmtree(folder_name)

    # ファイルの削除
    file_name = f"{doc_id}.zip"
    os.remove(file_name)

class EdinetAPIClient:
    def __init__(self, api_key):
        # Initialize with the API key
        self.api_key = api_key
    def get_data(self, url, params, args={}):
        """Common method to fetch data from the API"""
        params["Subscription-Key"] = self.api_key
        response = requests.get(url, params=params, **args)
        
        # Check if the request was successful
        if response.status_code == 200:
            try:
                # Attempt to parse the JSON response
                json_data = response.json()
                # Check if 'results' is in the response
                if 'results' not in json_data:
                    # Handle case where 'results' is missing
                    error_message = "'results' not found in the response."
                    raise ValueError(error_message)  # Raise the error with message

                return json_data  # Return the data if everything is okay

            except ValueError:
                # Handle JSON parsing error or 'results' missing
                raise ValueError(f"Error: Failed to parse JSON response or 'results' is missing.\nResponse: {response.text}")
        else:
            # Handle API request failure
            raise ValueError(f"Failed to fetch data from the API. Status Code: {response.status_code}\nError Message: {response.text}")


class DocIdListRetriever:
    def __init__(self, api_client):
        # Initialize with the API client to fetch data
        self.api_client = api_client

    def make_day_list(self, start_date, end_date):
        """Generate a list of dates within the specified date range"""
        period = (end_date - start_date).days
        return [start_date + datetime.timedelta(days=d) for d in range(period + 1)]

    def make_doc_id_list(self, day_list):
        """Fetch company information from EDINET and create a list"""
        securities_report_data = []
        url = "https://disclosure.edinet-fsa.go.jp/api/v2/documents.json"
        
        # Fetch data for each day in the day list
        for day in day_list:
            params = {"date": day, "type": 2}
            json_data = self.api_client.get_data(url, params)
        
            # Filter the data based on specific conditions
            for result in json_data["results"]:
                ordinance_code = result["ordinanceCode"]
                form_code = result["formCode"]

                if ordinance_code == "010" and form_code == "030000":
                    securities_report_data.append(result)
            time.sleep(1)

        # Convert data into a DataFrame
        df = pd.DataFrame(securities_report_data)
        if len(df) > 0:
            # Format the security code and normalize company names
            df['Security Code'] = df['secCode'].astype(str).str[:4]
            df["Company Name"] = df["filerName"].apply(lambda x: unicodedata.normalize('NFKC', x))
            
        return df


class ZipFileDownloader:
    def __init__(self, api_client):
        # Initialize with the API client to download files
        self.api_client = api_client

    def download_zip_file(self, doc_id):
        """Download a ZIP file from EDINET and extract its contents"""
        url = f"https://disclosure.edinet-fsa.go.jp/api/v2/documents/{doc_id}"
        params = {"type": 1,"Subscription-Key":self.api_client.api_key}
        filename = f"{doc_id}.zip"
        extract_dir = filename.replace('.zip', '')

        # Fetch the file from EDINET API
        response = requests.get(url, params=params, stream=True)
        if response.status_code == 200:
            with open(filename, 'wb') as file:
                for chunk in response.iter_content(chunk_size=1024):
                    file.write(chunk)
            print(f"Download of ZIP file {filename} is complete.")
            
            # Extract the downloaded ZIP file
            zip_obj = zipfile.ZipFile(filename, 'r')

            # Create directory for extraction if it doesn't exist
            if not os.path.exists(extract_dir):
                os.makedirs(extract_dir)

            zip_obj.extractall(extract_dir)
            zip_obj.close()
            print(f"Extracted ZIP file {filename}.")
        else:
            print("Failed to download the ZIP file.")


# DataParser class to handle XBRL parsing, cleaning, and other operations
class DataParser:
    def __init__(self, extract_dir):
        """Initialize DataParser with the directory of extracted files"""
        self.extract_dir = extract_dir

    def get_xbrl_files(self):
        """Return a list of XBRL files in the extracted directory"""
        # Assuming XBRL files have the '.xbrl' extension
        return [os.path.join(self.extract_dir, f) for f in os.listdir(self.extract_dir) if f.endswith('.xbrl')]

cols = ['Concept', 'Facts', 'Label', 'Name', 'LocalName', 'Namespace', 'ParentName', 'ParentLocalName', 'ParentNamespace', 'ID', 'Type', 'PeriodType', 'Balance', 'StandardLabel', 'TerseLabel', 'Documentation', 'LinkRole', 'LinkDefinition', 'PreferredLabelRole', 'Depth', 'ArcRole']

class MyViewFacts(ViewFileFactTable.ViewFacts):
    def __init__(self, modelXbrl, outfile, arcrole, linkrole, linkqname, arcqname, ignoreDims, showDimDefaults, labelrole, lang, cols,col_num=1,label_cell=None):
        super().__init__(modelXbrl, outfile, arcrole, linkrole, linkqname, arcqname, ignoreDims, showDimDefaults, labelrole, lang, cols)
        self.data = []

    def viewConcept(self, concept, modelObject, labelPrefix, preferredLabel, n, relationshipSet, visited):
        # bad relationship could identify non-concept or be None
        if (not isinstance(concept, ModelDtsObject.ModelConcept) or
            concept.substitutionGroupQname == XbrlConst.qnXbrldtDimensionItem):
            return
        cols = ['' for i in range(self.numCols)]
        i = 0
        for col in self.cols:
            if col == "Facts":
                self.setRowFacts(cols,concept,preferredLabel)
                i = self.numCols - (len(self.cols) - i - 1) # skip to next concept property column
            else:
                if col in ("Concept", "Label"):
                    cols[i] = labelPrefix + concept.label(preferredLabel,lang=self.lang,linkroleHint=relationshipSet.linkrole)


                i += 1

        attr = {"concept": str(concept.qname)}
        self.addRow(cols, treeIndent=n,
                    xmlRowElementName="facts", xmlRowEltAttr=attr, xmlCol0skipElt=True)
        self.add_content(concept, modelObject)
        if concept not in visited:
            visited.add(concept)
            for i, modelRel in enumerate(relationshipSet.fromModelObject(concept)):
                nestedRelationshipSet = relationshipSet
                targetRole = modelRel.targetRole
                if self.arcrole in XbrlConst.summationItems:
                    childPrefix = "({:0g}) ".format(modelRel.weight) # format without .0 on integer weights
                elif targetRole is None or len(targetRole) == 0:
                    targetRole = relationshipSet.linkrole
                    childPrefix = ""
                else:
                    nestedRelationshipSet = self.modelXbrl.relationshipSet(self.arcrole, targetRole, self.linkqname, self.arcqname)
                    childPrefix = "(via targetRole) "
                toConcept = modelRel.toModelObject
                if toConcept in visited:
                    childPrefix += "(loop)"
                labelrole = modelRel.preferredLabel
                if not labelrole or self.labelrole == conceptNameLabelRole:
                    labelrole = self.labelrole
                self.viewConcept(toConcept, modelRel, childPrefix, labelrole, n + 1, nestedRelationshipSet, visited)
            visited.remove(concept)
    def add_content(self, concept, modelObject):
        if concept.isNumeric:
            label = concept.label(lang='ja')
            s_label = concept.label(preferredLabel=standardLabel, lang='ja')
            facts = self.conceptFacts[concept.qname]

            if isinstance(modelObject, ModelDtsObject.ModelRelationship):
                parent_name = modelObject.fromModelObject.qname
                parent_label = modelObject.fromModelObject.label(preferredLabel=standardLabel, lang='ja')
            else:
                parent_name = None
                parent_label = None
            if isinstance(modelObject, str):
                link_def = self.linkRoleDefintions[modelObject]
            elif isinstance(modelObject, ModelDtsObject.ModelRelationship):
                link_def = self.linkRoleDefintions[modelObject.linkrole]
            for f in facts:
                if f.unit is not None:
                    unit = f.unit.value
                else:
                    unit = None
                value = f.xValue
                context = f.context
                self.data.append([concept.qname,concept.typeQname,concept.name, label, s_label, parent_name, parent_label,value, context.startDatetime, context.endDatetime, unit, link_def,context.id])



def viewFacts(modelXbrl, outfile, arcrole=None, linkrole=None, linkqname=None, arcqname=None, ignoreDims=False, showDimDefaults=False, labelrole=None, lang=None, cols=None,col_num=1, label_cell=None):
    if outfile is None:
        outfile = 'test.csv'
        remove_file = True
    if not arcrole: arcrole=XbrlConst.parentChild
    view = MyViewFacts(modelXbrl, outfile, arcrole, linkrole, linkqname, arcqname, ignoreDims, showDimDefaults, labelrole, lang, cols,col_num, label_cell)

    view.view(modelXbrl.modelDocument)
    df = pd.DataFrame(view.data, columns=['Name','Type','LocalName','Label','StandardLabel','ParentName','ParentLabel', 'Value','StartDate','EndDate','Unit','LinkDefinition','ContextID'])
    view.close()
    if remove_file:
        os.remove(outfile)
    return pd.DataFrame(df)



class XBRLParser:
    def __init__(self, xbrl_file):
        """Initialize DataParser with the directory of extracted files"""
        self.xbrl_file_path = xbrl_file
        self.modelXbrl = None
 
    def read_xbrl_file(self):
        """Parse an XBRL file and return the extracted facts in a DataFrame"""
        ctrl = Cntlr.Cntlr(logFileName='logToPrint')
        self.modelXbrl = ctrl.modelManager.load(self.xbrl_file_path)

    def get_fact_list(self, file_path=None,cols=None, **args):
        if self.modelXbrl is None:
            self.read_xbrl_file()
        if cols is None:
            cols = ['Concept', 'Label', 'Name', 'LocalName', 'Namespace', 'contextRef', 'unitRef', 'Dec', 'Value',  'Period',  'ID', 'Type', 'PeriodType']
        if file_path is None:
            file_path = 'fact_list.csv'
            remove_file = True
        ViewFileFactList.viewFacts(self.modelXbrl, file_path, cols=cols, **args)
        df = pd.read_csv(file_path)
        if remove_file:
            os.remove(file_path)
        return df
    
    def get_fact_table(self, file_path=None, cols=None, **args):
        if self.modelXbrl is None:
            self.read_xbrl_file()
        if cols is None:
            cols = ['Concept', 'Facts', 'Label', 'Name', 'LocalName', 'Namespace', 'ParentName', 'ParentLocalName', 'ParentNamespace', 'ID', 'Type', 'PeriodType', 'Balance', 'StandardLabel', 'TerseLabel', 'Documentation', 'LinkRole', 'LinkDefinition', 'PreferredLabelRole', 'Depth', 'ArcRole']
        if file_path is None:
            file_path = 'fact_list.csv'
            remove_file = True
        ViewFileFactTable.viewFacts(self.modelXbrl, file_path, cols=cols, arcrole=XbrlConst.summationItem, **args)
        df = pd.read_csv(file_path)
        if remove_file:
            os.remove(file_path)
        return df

    
    # 年ごとの補完処理
    def fill_missing_values(self, group):
        # 欠損値が最も少ない行を基本行として選択
        base_row = group.loc[group.isna().sum(axis=1).idxmin()].copy()

        # 基本行の欠損値を、他の行のデータで補完
        for _, row in group.iterrows():
            base_row.fillna(row, inplace=True)

        return base_row

    def parse_duplicated_label(self, df):
        # Nameをキーとする辞書（検索高速化）
        name_to_parent = df.set_index('Name')['ParentName'].to_dict()
        name_to_parent_label = df.set_index('Name')['ParentLabel'].to_dict()
        name_to_label = df.set_index('Name')['StandardLabel'].to_dict()

        # 異なる Name で同じ StandardLabel を持つケースを検出
        duplicate_labels = df.groupby('StandardLabel')['Name'].nunique()
        duplicate_labels = duplicate_labels[duplicate_labels > 1].index.tolist()

        # StandardLabel の重複がなくなるまで処理

        for label in duplicate_labels:
            # 重複している StandardLabel を持つ行を取得
            duplicate_rows = df[df['StandardLabel'] == label]

            for idx, row in duplicate_rows.iterrows():
                name = row['Name']
                parent_name = row['ParentName']
                new_label = row['StandardLabel']

                # 親をたどって識別できるようにする
                while name in name_to_label:
                    parent_label = name_to_parent_label.get(name, "")
                    if parent_label:
                        new_label = parent_label + " / " + new_label  # 親のラベルを前に追加
                    else:
                        break  # これ以上さかのぼれない
                    
                    # 異なる Name での重複が解消されたら終了
                    if df[(df['StandardLabel'] == new_label) & (df['Name'] != name)].empty:
                        break
                    
                    name = name_to_parent.get(name)  # さらに上の親をたどる

                # それでも重複が解消されなかった場合 `_1`, `_2` をつける
                suffix = 1
                original_label = new_label
                while not df[(df['StandardLabel'] == new_label) & (df['Name'] != row['Name'])].empty:
                    new_label = f"{original_label}_{suffix}"
                    suffix += 1
                
                # ラベルを更新
                df.at[idx, 'StandardLabel'] = new_label
                name_to_label[row['Name']] = new_label  # 辞書も更新
        return df
        


    def parse_xbrl_data(self, pivot=True, groupby_year=True, main_label='StandardLabel'):
        if self.modelXbrl is None:
            self.read_xbrl_file()
        
        cols = ['Concept', 'Facts', 'Label', 'Name', 'LocalName', 'Namespace', 'ParentName', 'ParentLocalName', 'ParentNamespace', 'ID', 'Type', 'PeriodType', 'Balance', 'StandardLabel', 'TerseLabel', 'Documentation', 'LinkRole', 'LinkDefinition', 'PreferredLabelRole', 'Depth', 'ArcRole']
        
        df = viewFacts(self.modelXbrl,None, cols=cols, lang='ja')
        
        if len(df) > 0:
            df = df[df['Value'].isnull()==False]
            df = df.drop_duplicates(['Name','ContextID','Value'])
            # df = df[['Name','ParentName','StandardLabel','Value','StartDate','EndDate','Unit','ContextID','ParentLabel']]
            if not pivot:
                return df
            else:
                
                if main_label=='StandardLabel':
                    df = self.parse_duplicated_label(df)
                main_df_ = df.copy()
                
                main_df_ = main_df_.drop_duplicates(subset=[main_label,'EndDate'],keep='first')
                main_pivot = pd.pivot(main_df_,index=['EndDate'],columns=main_label,values='Value').reset_index()
                if groupby_year:
                    # 年ごとに処理を適用
                    filled_df = main_pivot.groupby(pd.to_datetime(main_pivot['EndDate']).dt.year).apply(self.fill_missing_values)

                    return filled_df
                else:
                    return main_pivot

    def get_standard_data(self, pivot=True, groupby_year=True, main_label='StandardLabel'):
        df = self.parse_xbrl_data(pivot=False)
        name_pfs = ['売上高',
            '売上総利益又は売上総損失（△）',
            '営業利益又は営業損失（△）',
            '経常利益又は経常損失（△）',
            '当期純利益又は当期純損失（△）',
            '親会社株主に帰属する当期純利益又は親会社株主に帰属する当期純損失（△）',
            # '金融費用',
            '営業活動によるキャッシュ・フロー',
            '投資活動によるキャッシュ・フロー',
            '財務活動によるキャッシュ・フロー',
            '資産',
            '負債',
            '流動資産',
            '流動負債',
            '純資産',
            '株主資本',
            '利益剰余金',
            '短期借入金',
            '長期借入金',
            '法人税等',
            '販売費及び一般管理費',
            '減価償却費',
            '受取利息及び受取配当金',
            '支払利息']
        name_crp = ['株価収益率',
        '発行済株式総数',
                            ]
        name_div = ['１株当たり配当額']
        id_pfs = list(df[(df['StandardLabel'].isin(name_pfs))&(df['Name'].astype(str).str.contains('jppfs_cor:'))].drop_duplicates(subset='Name')['Name'])
        id_cor = list(df[(df['StandardLabel'].isin(name_crp))&(df['Name'].astype(str).str.contains('jpcrp_cor:'))].drop_duplicates(subset='Name')['Name'])
        id_div = list(df[(df['StandardLabel'].isin(name_div))&(df['Name'].astype(str).str.contains('jpcrp_cor:'))].drop_duplicates(subset='Name')['Name'])
        name_id_list = id_pfs+id_cor+id_div

        
        df = df[df['Name'].isin(name_id_list)]
        
        main_df_ = df.copy()
        
        main_df_ = main_df_.drop_duplicates(subset=[main_label,'EndDate'],keep='first')
        main_pivot = pd.pivot(main_df_,index=['EndDate'],columns=main_label,values='Value').reset_index()
        if groupby_year:
            # 年ごとに処理を適用
            filled_df = main_pivot.groupby(pd.to_datetime(main_pivot['EndDate']).dt.year).apply(self.fill_missing_values)

            return filled_df
        else:
            return main_pivot

        
