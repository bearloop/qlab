import pandas as _pd
import numpy as _np
import json as _json
import pandas as _pd

# --------------------------------------------------------------------------------------------
def _convert_str_to_df(string, column):
    
    literal = _json.loads(string)
    
    df = _pd.DataFrame([(i[0],i[1]) for i in literal],columns=['Dates',column]).set_index('Dates')
    df.index = _pd.to_datetime(df.index)
    
    return df

def _convert_df_to_str(df,column):
    sup_df = df[column].dropna()
    ts = [(i[0].to_pydatetime().strftime('%Y/%m/%d %S:%M:%H'),i[1]) for i in sup_df.items()]

    ts_as_string = _json.dumps(ts)
    
    return ts_as_string

def _merge_data(df_old, df_new):
    
    df_merged = _pd.concat([df_old,df_new],axis=0)
    
    return df_merged

# --------------------------------------------------------------------------------------------
def utils_control(data, rf=0, freq=252, ignore_na=False, asset_list=None, start=None, end=None):
    '''
    Returns a price dataframe based on given settings (dates, asset list, N/A), excess returns and
    assets list.
    rf: Annualised risk free rate set to 0 by default
    freq: frequency annual time periods i.e. 252 for days, 52 for weeks, 12 for months / year
    assetList: columns names to filter for
    ignore_na: ignore null values
    start, end dates: same type and format with that of data index e.g. '16-09-2018'
    '''

    # Filter for dates
    if start!=None:
        data = data.loc[start:,:].copy()
    
    if end!=None:
        data = data.loc[:end,:].copy()

    # Return datetime index
    data.index = _pd.to_datetime(data.index)

    # Filter for assets list
    if asset_list is None:
        asset_list = data.columns
    else:
        data = data[asset_list].copy()

    # Drop null values
    if ignore_na:
        data = data.dropna()
    
    data = data.astype(float).round(6)
    
    # Calculate excess returns
    eret = data.pct_change() - rf*100/freq

    return data, eret

# --------------------------------------------------------------------------------------------
def utils_returns_calc(df):
    """
    Calculates returns for periods: 2Y, 1Y, 3M, 1M, 1W, 1D. Handles missing values.
    df: pandas DataFrame, with day-dates as its index and asset prices as values
    """
    df = df.copy()
    # Set constants here
    last = 1
    days_in_mo = 21
    days_in_we = 5
    periods = {'5Y':-days_in_mo*60-last,'2Y':-days_in_mo*24-last,'1Y':-days_in_mo*12-last,
               '3M':-days_in_mo*3-last,'1M':-days_in_mo-last,'1W':-days_in_we-last,'1D':-1-last}

    # Add reverse index to df to use as index (since the actual index holds dates)
    df['NumIndex'] = [-i for i in range(len(df),0,-1)]

    # Filter for your constants (returns ranges)
    df = df[df.NumIndex.isin(list(periods.values()) + [-last])]

    # Keep only the periods that are available
    marks = list(filter(lambda x: periods[x] in df['NumIndex'].to_list(),periods))

    # Calc returns and drop last day
    df = ((df.iloc[-1]/df)-1).replace(0,_np.NaN).dropna(how='all')

    # Drop index because you don't need it anymore
    df = df.drop(['NumIndex'],axis=1)
    
    # Replace dates index with string values ('1M' etc)
    df.index = marks
    
    return df.T

# --------------------------------------------------------------------------------------------