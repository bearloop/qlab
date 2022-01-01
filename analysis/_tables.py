import numpy as _np
import pandas as _pd
from ._portfolio import Portfolio

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