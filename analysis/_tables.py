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
    df = df[['symbol','isin','aum','exp_ratio','launch_date','top_10',
             'sec_technology','sec_healthcare','sec_financials',
             'sec_communications','sec_cyclicals','sec_defensives']].set_index('symbol')
    
    # Rename columns
    df = df.rename({'isin':'ISIN', 'aum':'Fund AUM',
                    'exp_ratio': 'Expense %', 'launch_date':'Launch',
                    'top_10':'Top-10 %','sec_technology':'IT %','sec_healthcare':'HC %',
                    'sec_financials':'FIN %','sec_communications':'TEL %',
                    'sec_cyclicals':'CYCL %','sec_defensives':'DEF %'},axis=1)
    
    # Change some columns' dtype to float
    for col in df.columns:
        if '%' in col:
            df[col] = df[col].astype(float)
    
    # Replace -1 with NaN
    df = df.replace(-1.0, _np.NaN)
    
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
        data_df.loc['Start',sec] = prices.index[0].date().strftime('%d/%m/%Y')
        data_df.loc['End',sec] = prices.index[-1].date().strftime('%d/%m/%Y')
        data_df.loc['Periods',sec] = prices.count()[0]
        
        # Calculate returns
        data_df.loc['Ret: 1-d',sec] = prices.pct_change().iloc[-1][0]
        data_df.loc['Ret: 1-wk',sec] = prices.pct_change(week).iloc[-1][0]
        data_df.loc['Ret: 1-mo',sec] = prices.pct_change(month).iloc[-1][0]
        data_df.loc['Ret: 3-mo',sec] = prices.pct_change(3*month).iloc[-1][0]
        data_df.loc['Ret: 1-yr',sec] = prices.pct_change(12*month).iloc[-1][0]
        data_df.loc['CAGR',sec] = ( (1+prices.pct_change()).prod()**(252/prices.pct_change().count()) )[0] - 1
        data_df.loc['E(r) (1-yr, ann)',sec] = (prices.pct_change().iloc[-12*month:].mean()*(12*month))[0]

        # Calculate vol
        data_df.loc['Vol (1-yr, ann)',sec] = (prices.pct_change().iloc[-12*month:].std()*_np.sqrt(12*month))[0]
        
        # Calculate current drawdown
        data_df.loc['Drawdown',sec] = (prices.iloc[-1]/prices.max()-1)[0]
        data_df.loc['Max Drawdown',sec] = ( (prices/prices.cummax()) -1 ).min()[0]
        
        # Distribution data
        data_df.loc['Mean ret',sec] = prices.pct_change().mean()[0]
        data_df.loc['Stand Dev',sec] = prices.pct_change().std()[0]
        data_df.loc['Skewness',sec] = prices.pct_change().skew()[0]
        data_df.loc['Kurtosis',sec] = prices.pct_change().kurt()[0]
        
    return data_df

# --------------------------------------------------------------------------------------------