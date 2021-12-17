import pandas as _pd
import numpy as _np
import json as _json

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
def _calc_expected_shortfall(df, window, conf):
    """ Applied to pandas df with a single column """

    # Calculate returns
    ret = df.pct_change()
    
    # Calculate VaR
    var = ret.rolling(window=window, min_periods=window).quantile(1-conf)
    
    # Create list to add ES values to
    shortfall_series = []
    
    for period in ret.rolling(window, window):
        
        # Find current VaR value of the period
        var_value = var.loc[period.index][-1]
        
        # Calculate expected shortfall (mean of values less than the VaR)
        es = period[period<var_value].mean()
        
        # Append to list
        shortfall_series.append(es)
    
    # Create pd series to return
    pds = _pd.Series(shortfall_series, index = ret.index)
    
    return  pds

# def _calc_expected_shortfall_v2(df, window, conf):
#     """ Applied to pandas df with a single column """
#     # Calculate returns
#     ret = df.pct_change()
    
#     # Calculate VaR
#     var = ret.rolling(window=window, min_periods=window).quantile(1-conf)
    
#     ct = _pd.concat([ret,var],axis=1)

#     ct.columns = ['RET','VAR']
    
#     es_series = list(map(lambda x: x.RET[x.RET<x.VAR.loc[x.index[-1]]].mean(),
#                                   ct.rolling(window=window,min_periods=window)))
    
#     es_sr = _pd.Series(es_series, index = ret.index)
    
#     return es_sr

# --------------------------------------------------------------------------------------------
def _calc_ytd(df):
    
    # Forward fill
    df = df.ffill()
    
    years = sorted((set(df.index.year)),reverse=False)
    
    if len(years) == 1:
        
        start_date = list(df.index)[0]
        end_date = list(df.index)[-1]
        return df.loc[[start_date,end_date]]
    
    else:
        
        current_year = str(years[-1])
        current_year_date = df.loc[current_year].iloc[-1].name
    
        previous_year = str(years[-2])
        previous_year_date = df.loc[previous_year].iloc[-1].name

        return df.loc[[previous_year_date,current_year_date]]

# --------------------------------------------------------------------------------------------
def _calc_mtd(df):
    
    # Forward fill
    df = df.ffill()
    
    current_month = df.index.month[-1]
    
    if  current_month == 1:
        return _calc_ytd(df)
    
    else:
        
        previous_month = str(current_month-1)
        current_year = str(sorted((set(df.index.year)),reverse=False)[-1])
        
        last_month_date = list(df.loc[current_year+'-'+previous_month].index)[-1]
        current_month_date = list(df.index)[-1]
        
        return df.loc[[last_month_date, current_month_date]]

# --------------------------------------------------------------------------------------------
def _calc_custom_range(df, start, end):
    """
    Calculates asset returns over the requested period. Assumes start, end dates are in the index.
    df: Pandas DataFrame with dates in its index and asset prices as values
    start, end: date as string in the following format 'YYYY-MM-DD' e.g. '2019-12-31'
    """
    if (start is not None) & (end is not None):
        df = df.pct_change().loc[start:end].ffill().dropna(axis=1)
        return df
    else:
        print('Please add both a start and an end date.')

# --------------------------------------------------------------------------------------------
def _concat_market_segments(df, db):
    """Concat df with market segments stored in market_segments table."""
    ms = db.market_segments_info()

    df = _pd.concat([df,ms],axis=1)

    return df

# --------------------------------------------------------------------------------------------
def calc_cumulative_ret(df, start=None, end=None, db=None):
    """
    Calculates cumulative returns over different lookback periods.
    df: Pandas DataFrame with dates in its index and asset prices as values
    start, end: date as string in the following format 'YYYY-MM-DD'
    db: instance of PostgerSQL connection
    """
    days_in_month = 21
    
    # Forward fill prices
    df = df.ffill()
    
    ret = _pd.DataFrame(df.pct_change().iloc[-1])
    ret.columns = ['1-day']
    
    ret['1-wk'] = df.pct_change(5).iloc[-1]
    ret['1-mo'] = df.pct_change(1*days_in_month).iloc[-1]
    ret['3-mo'] = df.pct_change(3*days_in_month).iloc[-1]
    ret['1-yr'] = df.pct_change(12*days_in_month).iloc[-1]
    ret['MtD'] = _calc_mtd(df).pct_change().iloc[-1]
    ret['YtD'] = _calc_ytd(df).pct_change().iloc[-1]

    if (start is not None) & (end is not None):
        custom = _calc_custom_range(df, start, end).add(1).cumprod()
        ret['Custom'] = custom.iloc[[0,-1]].pct_change().iloc[-1]


    if db is not None:
        ret = _concat_market_segments(ret, db)
        
    return ret



# --------------------------------------------------------------------------------------------
def calc_annualised_vol(df, start=None, end=None, db=None):
    """
    Calculates annualised volatility over different lookback periods.
    df: Pandas DataFrame with dates in its index and asset prices as values
    start, end: date as string in the following format 'YYYY-MM-DD'
    db: instance of PostgerSQL connection
    """
    days_in_month = 21
    ann_rate = _np.sqrt(days_in_month*12)
    
    # Forward fill prices
    df = df.ffill()
    
    vol = _pd.DataFrame(df.pct_change().iloc[-1*days_in_month:].std()*ann_rate)
    vol.columns = ['1-mo']
    
    vol['3-mo'] = df.pct_change().iloc[-3*days_in_month:].std()*ann_rate
    vol['1-yr'] = df.pct_change().iloc[-12*days_in_month:].std()*ann_rate
    vol['MtD'] = df.pct_change().loc[_calc_mtd(df).index[0]:].std()*ann_rate
    vol['YtD'] = df.pct_change().loc[_calc_ytd(df).index[0]:].std()*ann_rate

    if (start is not None) & (end is not None):
        vol['Custom'] = _calc_custom_range(df, start, end).std()*ann_rate
    
    if db is not None:
        vol = _concat_market_segments(vol, db)

    return vol

# --------------------------------------------------------------------------------------------

def calc_annualised_ret(df, start=None, end=None, db=None):
    """
    Calculates annualised mean returns over different lookback periods.
    df: Pandas DataFrame with dates in its index and asset prices as values
    start, end: date as string in the following format 'YYYY-MM-DD'
    db: instance of PostgerSQL connection
    """
    days_in_month = 21
    ann_rate = days_in_month*12
    
    # Forward fill prices
    df = df.ffill()
    
    mu = _pd.DataFrame(df.pct_change().iloc[-1*days_in_month:].mean()*ann_rate)
    mu.columns = ['1-mo']
    
    mu['3-mo'] = df.pct_change().iloc[-3*days_in_month:].mean()*ann_rate
    mu['1-yr'] = df.pct_change().iloc[-12*days_in_month:].mean()*ann_rate
    mu['MtD'] = df.pct_change().loc[_calc_mtd(df).index[0]:].mean()*ann_rate
    mu['YtD'] = df.pct_change().loc[_calc_ytd(df).index[0]:].mean()*ann_rate

    if (start is not None) & (end is not None):
        mu['Custom'] = _calc_custom_range(df, start, end).mean()*ann_rate
    
    if db is not None:
        mu = _concat_market_segments(mu, db)

    return mu


# --------------------------------------------------------------------------------------------