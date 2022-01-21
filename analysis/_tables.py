import numpy as _np
import pandas as _pd
import requests as _requests
import json as _json
from ._portfolio import Portfolio

# --------------------------------------------------------------------------------------------
def _ishares_constituents(ishares_id, weight):  
    '''
    Return information on Blackrock's iShares ETFs (see constants file for mapping info)
    '''
    try:
        suffix = '/fund/1506575576011.ajax?tab=all&fileType=json'
        url = 'https://www.ishares.com/uk/individual/en/products/'+ishares_id+suffix
        
        res = _requests.get(url)
        clean_data = _json.loads(res.content)['aaData']

        dct = {}

        for ind, l in enumerate(clean_data):
            
            dct[ind+1] = {'Symbol':l[0],'Security':l[1],
                          'Sector':l[2],'Asset Class':l[3],
                          'RawWei':l[5]['raw'],'ISIN':l[8],
                          'Country':l[10],'FX':l[12]}
                
        df = _pd.DataFrame(dct).T
        df['Weight'] = df['RawWei']*weight
        
        return df
    
    except Exception as e:
        print(e.args)

# --------------------------------------------------------------------------------------------
def _sum_top_constituents(df):
    '''
    Sum top-20 records and subtract from 100.
    '''
    if df.shape[0]>20:
        length = 20
    else:
        length = df.shape[0]
    df.loc[length+1,:] = ['Total Above',df.loc[:length,'Weight'].sum()]
    df.loc[length+2,:] = ['Total Other',100-df.loc[length+1,'Weight']]
    
    return df.head(22)

# --------------------------------------------------------------------------------------------
def _top_constituents(df):
    '''
    Construct table with top constituents for each aggregation type.
    '''
    df_out = _pd.DataFrame()
    for col in ['Security','Country','Sector','Asset Class','FX']:

        sup = df.groupby(col).sum().sort_values(by='Weight',ascending=False)

        # Add column with index values
        sup[col] = sup.index

        # Reindex
        sup.index = [i for i in range(1,len(sup)+1)]

        # Rearange columns
        sup = sup[[col,'Weight']]

        # Add top and bottom
        sup=_sum_top_constituents(sup)

        # Format table and change column names
        sup[['Weight']] = sup[['Weight']].applymap('{:,.1f}%'.format)
        sup.columns = [sup.columns[0], sup.columns[0]+' W']

        # Concat new columns
        df_out = _pd.concat([df_out,sup],axis=1).fillna('')

    return df_out

# --------------------------------------------------------------------------------------------
def table_portfolio_concentration(assets_list=None, weights=None, db=None, verbose=False):
    '''
    assets: list of iShares ETF symbols
    weights: list of weights (weight of each ETF)
    '''
    # group_by: isin, security, sector, country or asset_class
    group_by = 'Security'
    
    # Query ishares table and convert DF to a dictionary of ETF symbols and their respective iShares ids
    db.execute_sql('SELECT * FROM ishares')
    ishares = db.fetch().set_index('symbol').to_dict()['ishares_id']
    
    # Weights list if none is passed
    if weights is None:
        weights = [1/len(assets_list) for i in assets_list]
    
    # Dataframe to return
    df = _pd.DataFrame()
    
    # Retrieve json
    for ind, etf in enumerate(assets_list):
        df = _pd.concat([df,_ishares_constituents(ishares[etf], weights[ind])])
    
    # Group by security and keep weights first
    w = df.groupby(group_by).sum().sort_values(by='Weight', ascending=False)[['Weight']]

    # Group by security and add other key columns
    cols = df.groupby(group_by).last()[['Country','Sector','Asset Class','Symbol','ISIN','FX']]
    
    # Concat concentrated weights and key columns by 
    df = _pd.concat([w,cols],axis=1)
    
    if verbose==False:
        df = _top_constituents(df=df)

    return df

# --------------------------------------------------------------------------------------------
def table_fund_details(assets_list=None, db=None):
    """
    
    """
    db.execute_sql('SELECT * FROM etfs_data')
    df = db.fetch()
    df['symbol'] = list(map(lambda x: x.split(':')[0], df.ft_symbol))
    
    if assets_list is None:
        assets_list = df['symbol'].values
    
    df = df[df.symbol.isin(assets_list)]
    
    # Selected columns
    df = df[['symbol','isin','launch_date','aum','exp_ratio','top_10',
             'sec_technology','sec_healthcare','sec_financials',
             'sec_communications','sec_cyclicals','sec_defensives']].set_index('symbol')
    
    # Rename columns
    df = df.rename({'isin':'ISIN', 'aum':'AUM-bn',
                    'exp_ratio': 'Expense', 'launch_date':'Launch',
                    'top_10':'Top-10','sec_technology':'InfoTech','sec_healthcare':'HCare',
                    'sec_financials':'Fin','sec_communications':'Telco',
                    'sec_cyclicals':'Cycl','sec_defensives':'Def'},axis=1)
    
    # Make AUM to appear as float
    df['AUM-bn'] = list(map(lambda x: float(x.split('GBP')[1].replace(' ','').replace('<','').replace('bn','')),df['AUM-bn']))

    # Change some columns' dtype to float
    labels_2p = ['Expense']
    labels_1p = ['Top-10','InfoTech','HCare','Fin','Telco','Cycl','Def']
    labels = labels_1p + labels_2p

    for col in labels:
        df[col] = df[col].astype(float)
    
    # Replace -1 with NaN
    df = df.replace(-1.0, 0)

    # Change column format
    df[labels_2p] = (df[labels_2p]).applymap('{:,.2f}%'.format)
    df[labels_1p] = (df[labels_1p]).applymap('{:,.1f}%'.format)


    return df

# --------------------------------------------------------------------------------------------
def table_holdings_summary(db=None):
    """
    
    """
    df = Portfolio(db).fetch_transactions()
    
    # Calculate transaction costs
    df['cap_paid'] = df['transaction_price'].mul(df['transaction_quantity'])
    
    # Group by symbol/holding
    df = df.groupby('symbol').sum()
    
    # Filter for current holdings (ignore closed positions)
    df = df[df['transaction_quantity']>0]
    
    # Average unit cost per symbol
    df['cap_paid_share'] = df['cap_paid'].div(df['transaction_quantity'])
    
    # Last unit price per symbol
    asset_prices = db.prices_table_read()
    asset_prices = asset_prices.ffill()
    df['last_price'] = asset_prices[df.index].iloc[-1]
    
    # Position value per symbol
    df['position'] = df['last_price'].mul(df['transaction_quantity'])
    
    # Pnl per symbol & percentage over cost
    df['pnl'] = df['position']-df['cap_paid']
    df['pnl_pct'] = df['pnl'].div(df['cap_paid'])
    
    # Sory by cost
    df = df.sort_values(by='cap_paid',ascending=False)
    
    # Allocation
    df['weight'] = df['position'].div(df['position'].sum())
    
    # Drop "transaction_price"
    df = df.drop('transaction_price',axis=1)
    
    # Rename columns
    df = df.rename({'transaction_quantity':'Units', 'cap_paid':'Cost',
                    'cap_paid_share': 'Cost/unit', 'last_price':'Last Price',
                    'position':'Position','pnl':'PnL','pnl_pct':'PnL %',
                    'weight':'Allocation'},axis=1)
    
    # Format columns
    labels_2p = ['PnL %','Allocation']
    df[labels_2p] = (df[labels_2p]*100).applymap('{:,.2f}%'.format)

    labels_2f = ['Cost','Position','PnL']
    df[labels_2f] = (df[labels_2f]).applymap('€{:,.2f}'.format)

    labels_3f = ['Cost/unit','Last Price']
    df[labels_3f] = (df[labels_3f]).applymap('€{:,.3f}'.format)
    
    return df

# --------------------------------------------------------------------------------------------
def table_securities_stats(df):
    """
    
    """
    month, week = 21, 5

    data_df = _pd.DataFrame()
    
    for sec in df.columns:
        
        # prices = _pd.DataFrame(df[sec].dropna())
        prices = _pd.DataFrame(df[sec].ffill().dropna())
        
        # Calculate periods
        data_df.loc['Start',sec] = prices.index[0].date().strftime('%d/%m/%y')
        data_df.loc['End',sec] = prices.index[-1].date().strftime('%d/%m/%y')
        data_df.loc['Periods',sec] = prices.count()[0]
        
        # Distribution data
        data_df.loc['Mean Ret',sec] = prices.pct_change().mean()[0]
        data_df.loc['Stand Dev',sec] = prices.pct_change().std()[0]
        data_df.loc['Skewness',sec] = prices.pct_change().skew()[0]
        data_df.loc['Kurtosis',sec] = prices.pct_change().kurt()[0]

        # Sharpe ratio (risk-free = 0)
        data_df.loc['Sharpe',sec] = data_df.loc['Mean Ret',sec]*(12*month) / (data_df.loc['Stand Dev',sec]*(_np.sqrt(12*month)))

        # Calculate returns
        data_df.loc['Rt-1d',sec] = prices.pct_change().iloc[-1][0]
        data_df.loc['Rt-1wk',sec] = prices.pct_change(week).iloc[-1][0]
        data_df.loc['Rt-1mo',sec] = prices.pct_change(month).iloc[-1][0]
        data_df.loc['Rt-3mo',sec] = prices.pct_change(3*month).iloc[-1][0]
        data_df.loc['Rt-1yr',sec] = prices.pct_change(12*month).iloc[-1][0]
        data_df.loc['CAGR',sec] = ( (1+prices.pct_change()).prod()**(252/prices.pct_change().count()) )[0] - 1
        data_df.loc['Mean-1yr',sec] = (prices.pct_change().iloc[-12*month:].mean()*(12*month))[0]

        # Calculate vol
        data_df.loc['Vol-1yr',sec] = (prices.pct_change().iloc[-12*month:].std()*_np.sqrt(12*month))[0]
        
        # Calculate current drawdown
        data_df.loc['Drawdown',sec] = (prices.iloc[-1]/prices.max()-1)[0]
        data_df.loc['Max Drawdown',sec] = ( (prices/prices.cummax()) -1 ).min()[0]
    
    # Display format
    data_df = data_df.T

    labels_2p = ['Rt-1d','Rt-1wk','Rt-1mo','Rt-3mo','Mean Ret','Stand Dev']
    data_df[labels_2p] = (data_df[labels_2p]*100).applymap('{:,.2f}%'.format)

    labels_1p = ['Rt-1yr','CAGR','Mean-1yr','Vol-1yr','Drawdown','Max Drawdown']
    data_df[labels_1p] = (data_df[labels_1p]*100).applymap('{:,.1f}%'.format)

    labels_2f = ['Skewness','Kurtosis', 'Sharpe']
    data_df[labels_2f] = (data_df[labels_2f]).applymap('{:,.2f}'.format)

    return data_df

# --------------------------------------------------------------------------------------------