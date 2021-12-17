import numpy as _np
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

# def table_fund