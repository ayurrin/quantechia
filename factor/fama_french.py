# Fama French データ取得
from pandas_datareader import famafrench as ff

def get_ff_dataname():
    return ff.get_available_datasets()

def get_ff(dataname=None, cycle='M', country='US', start=1960):
    """
    country:US, JPN
    """
    if dataname is None:
        
        if cycle=='D':
            if country == 'JPN':
                dataname = 'Japan_5_Factors_daily'
            else:
                dataname =  'F-F_Research_Data_5_Factors_2x3_daily'
        else:
            if country == 'JPN':
                dataname = 'Japan_5_Factors'
            else:
                dataname =  'F-F_Research_Data_5_Factors_2x3'
    data = ff.FamaFrenchReader(dataname, start=start,).read()
    

    if cycle=='Y':
        return data[1]
    else:
        return data[0]

