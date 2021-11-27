import pandas as _pd
import numpy as _np

class BackTest:
    '''
    Backtest strategy returns by passing a dataframe of price and signal.
    Configurable by the following arguments.

    Arguments:
    ----------
    starting_capital: (int) the initial investment to the strategy
    sell_pct: (float) the percentage of assets the strategy sells in a SELL signal
                Does it make sense to sell the whole portfolio? if not set this to 1.
    drift_pct: (float) percentage by which the valuation price differs from the trading price
                when the strategy enters / exits a position
    min_fee: (float) minimum flat fee per transaction (buy or sell order)
    pct_fee: (float) percentage fee per transaction, applied to the transaction's value
    '''
    
    def __init__(self, starting_capital=1000, sell_pct=1, drift_pct=0.1/100, min_fee=2, pct_fee=0.2/100):
        self._starting_capital = starting_capital
        self._drift = {'BUY': drift_pct, 'SELL': -drift_pct, 'HOLD': 0}
        self._min_fee = min_fee
        self._pct_fee = pct_fee
        self._sell_pct = sell_pct
    

    def _net_returns(self, df):
        '''
        The passed dataframe must have the following columns:
        --------
        Capital - Shows the gross cumulative return/capital the strategy has generated.
        Position - Shows the position the strategy has at each date.
                   Valid values for the Position column are HOLD, SELL or BUY.
        '''
        # Calculate fees
        df['Fees_%'] = (df['Capital']*df['Position'].replace(['HOLD','BUY','SELL'],[0,-1,-1])*(self._pct_fee)).cumsum()
        df['Fees_Flat'] = (df['Position'].replace(['HOLD','BUY','SELL'],[0,-1,-1])*(self._min_fee)).cumsum()
        df['Fees_Total'] = df[['Fees_%','Fees_Flat']].sum(axis=1)

        # Calculate signal returns net of fees
        df['Capital_Net'] = df['Capital'] + df['Fees_Total']

        return df

    
    def _gross_returns(self, df):
        '''
        TO DO
        '''
        capital = self._starting_capital
        
        # Iterate over the dataframe to calculate the signal's returns
        for date, row in df.iterrows():

            asset_is_held = (row['Signal'] == 1) & (row['Position'] == 'HOLD')
            asset_is_sold = (row['Signal'] == 0) & (row['Position'] == 'SELL')

            if asset_is_held:
                capital = (1+df.loc[date,'Trading_Price_%'])*capital
                df.loc[date,'Capital'] = capital

            elif asset_is_sold:
# Fix this by breaking it down between invested capital and cash
# if the strategy sells it should sell from the invested capital and only by the % specified
# if the strategy buys it should buy only using the cash
# if a strategy holds (neither buys nor sells) the cash should be unchanged
                capital = (1+df.loc[date,'Trading_Price_%'])*capital*self._sell_pct

            else:
                df.loc[date,'Capital'] = capital
        
        return df


    def btest_single_asset(self, data, prices, signal):
        '''
        TO DO
        -------
        Signal: signal represents an action at time T, based on information processed up to T-1
        '''
        # Create a dataframe with closing prices, signal and capital data
        df = _pd.DataFrame(columns = ['Valuation_Price'])
        df['Valuation_Price'] = data[prices]
        df['Signal'] = data[signal]
        df['Capital'] = _np.NaN
        
        # Position translates signal to buy, sell, hold positions / orders
        df['Position'] = df['Signal'].diff().replace([_np.NaN,0,-1,1],
                                                     ['HOLD','HOLD','SELL','BUY'])
        
        # Trading price is the price the strategy buys / sells including a drift term
        df['Trading_Price'] = df['Valuation_Price']* (1+df['Position'].replace(
                                                        ['HOLD','SELL','BUY'],
                                                        [self._drift['HOLD'],
                                                         self._drift['SELL'],
                                                         self._drift['BUY']]))
        # Calculate percentages for trading price column
        df['Trading_Price_%'] = df['Trading_Price'].pct_change()

        # Calculate Buy & Hold strategy
        df['Buy_and_Hold'] = df['Valuation_Price'].pct_change().add(1).cumprod().fillna(1)*self._starting_capital

        # Calculate signal gross returns
        df = self._gross_returns(df)

        # Calculate strategy fees / costs and net returns
        df = self._net_returns(df)

        return df

    
    