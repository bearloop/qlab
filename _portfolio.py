from datetime import datetime as _datetime
from datetime import timedelta as _timedelta
import pandas as _pd


class Portfolio:

    def __init__(self, heroku_conn):
        self.db = heroku_conn

    # --------------------------------------------------------------------------------------------
    def _calc_value_and_cost_basis(self, price_per_share, number_of_shares, asset_prices):

        # Cost
        cost = (price_per_share.mul(number_of_shares)).sum(axis=1).reindex(
            asset_prices.index).cumsum().ffill().fillna(0)
        
        # Value
        value = (number_of_shares.reindex(asset_prices.index).cumsum().ffill(
                )).mul(asset_prices).sum(axis=1).ffill()

        return value, cost

    # --------------------------------------------------------------------------------------------
    def _calc_portfolio_returns(self, value, cost):

        # Df to calc returns: Step 1 add value and cost time series components
        df = _pd.concat([value,cost],axis=1)
        df.columns = ['End_Value','Cost']

        # Step 2 cacl flows component
        df['Flows'] = df.diff(1)['Cost']
        df['Flows'][0] = df['Cost'][0]

        # Step 3a Numerator of return calc: (Ending - Starting - Flows)
        df['Numerator'] = df['End_Value'] - df['End_Value'].shift(1) - df['Flows']

        # Step 3b Denominator of return calc: (Starting + Flows)
        df['Denominator'] = df['End_Value'].shift(1) + df['Flows']

        # Step 4 Calculate returns and cumulative returns (1+r_1)*(1+r_2)*..*(1+r_n)
        df['Return'] = df['Numerator'] / df['Denominator']
        df['Cumulative_Index'] = (df['Return']+1).cumprod().fillna(1)
        
        return df

    # --------------------------------------------------------------------------------------------
    def fetch_transactions(self):

        # Fetch all transactions
        self.db.execute_sql('SELECT * FROM transactions')
        tr = self.db.fetch()

        # Change types
        tr['id'] = tr['id'].astype(int)
        tr['transaction_price'] = tr['transaction_price'].astype(float)
        tr['transaction_date'] = list(map(lambda x: _datetime.strptime(x, '%d/%m/%Y'), tr['transaction_date']))

        # Set id
        tr = tr.set_index('id')
        
        return tr

    # --------------------------------------------------------------------------------------------

    # def _fetch_asset_prices(self, all_transactions, start_date):

    #         # Portfolio assets by date
    #         all_assets = 
    #         ap = all_assets.loc[start_date:].dropna(how='all',axis=1).ffill()
            
    #         return ap

    # --------------------------------------------------------------------------------------------
    def fetch_data(self):
        # Fetch transactions
        transactions = self.fetch_transactions()
        t_0 = min(transactions['transaction_date']) - _timedelta(1)

        # Group transactions by date and asset to get mean price and total shares traded
        groupings = transactions.groupby(['symbol','transaction_date'])

        # Shares quantity and price per share
        nos = groupings['transaction_quantity'].sum().unstack().T
        pps = groupings['transaction_price'].mean().unstack().T

        # Asset prices
        ap = self.db.prices_table_read(assets_list=list(set(transactions['symbol']))
                                    ).loc[t_0:].dropna(how='all',axis=1).ffill()
        # ap = self._fetch_asset_prices(all_transactions=transactions, start_date=t_0)

        # Calculate costs and value
        value, cost = self._calc_value_and_cost_basis(price_per_share=pps,
                                                    number_of_shares=nos,
                                                    asset_prices=ap)

        # Calculate portfolio returns
        port_returns = self._calc_portfolio_returns(value=value, cost=cost)

        return port_returns

    # --------------------------------------------------------------------------------------------