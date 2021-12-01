import pandas as _pd

# --------------------------------------------------------------------------------------------
def control(data, rf=0, freq=252, ignore_na=False, asset_list=None, start=None, end=None):
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
