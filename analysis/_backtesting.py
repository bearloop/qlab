import pandas as _pd
import numpy as _np

class BackTest:
    
    def __init__(self, initial_capital=10000):
        self._cash = initial_capital    
    
    def _get_units(self, transaction_price, capital):
        """
        Figure out how many units of the asset in question will be bought given a
        transaction price and investment capital.
        """
        # How many units of the asset will be bought
        units = round(capital/transaction_price)

        # Asset value must be less than total investment
        if units*transaction_price > capital:
            return units-1
        
        else:
            return units
    
    
    def _calc_position(self, value_p=None, trade_p=None, signal=None, action=None, cash=0, units=0):
        """
        Calculates what happens when the strategy enters a position, liquidates its holdings or
        stands pat.
        """

        # ------------------------------------------------------
        # ------ what happens when you enter a position -------
        # ------------------------------------------------------
        if (signal=='IN') and (action=='BUY'):

            # Units purchased
            units = self._get_units(trade_p, cash)

            # Position initial cost
            cost = round(units * trade_p,4)

            # Cash value
            cash = round(cash - cost,4)
        
        # ------------------------------------------------------
        # ------ what happens when you get out of a position ---
        # ------------------------------------------------------
        elif (signal=='OUT') and (action=='SELL'):

            # Liquidate position to cash
            cash = cash + trade_p * units

            # Purchase Cost is considered to be 0 as there are no purchases made
            cost = 0
            
            # Also no assets are held so units = 0
            units = 0
        
        # ------------------------------------------------------  
        # ------ what happens when you don't do anything -------
        # ------------------------------------------------------
        elif (action=='NO ACTION'):
            # No actions were taken, cash is unchanged, units are unchanged, cost = 0
            cash = cash
            units = units
            cost = 0
        
        # Value of position
        valuation = round(units * value_p,4)
            
        # Value of position plus cash
        total = valuation + cash

        return units, cost, cash, valuation, total
    
    
    def evaluate_strat(self, df, name='Asset', signal='Signal'):
        """
        Expects a dataframe with two columns: name & signal.
        
        Signal: a list of 'IN'/'OUT' strings indicating whether the asset should be long or not
        Price: a list of asset prices (assumed to be end-of-day prices)
        
        Derived columns:
        Trade price: the mean price of a 2-day period that a transaction is assumed to take place
        Action: the order the strategy issues, 'NO ACTION', 'SELL' or 'BUY' depending on whether the
        asset is already held and on whether it should be long or not.
        Units: units of the asset held/purchased at any given time
        Cost: units * trade price (the invested capital)
        Cash: cash in the portfolio
        Valuation: units * value price (even for the same day valuation is different than the cost)
        Total: sum of valuation and cash
        """
        
        # Add Trade and Signal columns as per above

        df['Trade'] = df[name].rolling(2).mean()
        df['Action'] = df[signal].replace(['OUT','IN'],[0,1]).diff().replace([0,-1,1],['NO ACTION','SELL','BUY'])
        
        # Add the following columns that are handy for performance calculation
        new_labels = ['Units', 'Cost', 'Cash', 'Valuation', 'Total']
        df[new_labels] = _np.NaN

        # Find the first time you enter the strategy as long ('BUY')
        first_valid_buy = df[df['Action']=='BUY'].first_valid_index()
        
        # Start from this first date
        df = df.loc[first_valid_buy:,:]
        
        # Iterate over the period
        for i in df.index:

            if i == first_valid_buy:
                capital = self._cash
                units_position = 0

            else:
                capital = df.loc[previous_day,'Cash']
                units_position = df.loc[previous_day,'Units']
            
            # Fill the ['Units', 'Cost', 'Cash', 'Valuation', 'Total'] columns
            df.loc[i, new_labels] = self._calc_position(value_p=df.loc[i,name],
                                                        trade_p=df.loc[i,'Trade'],
                                                        signal=df.loc[i,signal],
                                                        action=df.loc[i,'Action'],
                                                        cash=capital,
                                                        units=units_position)
            
            # Keep track of the previous valid date to use in the else statement above
            previous_day = i
        
        # Calculate your benchmark - a buy and hold strategy!
        df['Buy_Hold'] = df[name].pct_change().add(1).cumprod().fillna(1)*df['Total'].iloc[0]
        
        return df



# class BackTest:
#     '''
#     Backtest strategy returns by passing a dataframe of price and signal.
#     Configurable by the following arguments.

#     Arguments:
#     ----------
#     starting_capital: (int) the initial investment to the strategy
#     sell_pct: (float) the percentage of assets the strategy sells in a SELL signal
#                 Does it make sense to sell the whole portfolio? if not set this to 1.
#     drift_pct: (float) percentage by which the valuation price differs from the trading price
#                 when the strategy enters / exits a position
#     min_fee: (float) minimum flat fee per transaction (buy or sell order)
#     pct_fee: (float) percentage fee per transaction, applied to the transaction's value
#     '''
    
#     def __init__(self, starting_capital=1000, sell_pct=1, drift_pct=0.1/100, min_fee=2, pct_fee=0.2/100):
#         self._starting_capital = starting_capital
#         self._drift = {'BUY': drift_pct, 'SELL': -drift_pct, 'HOLD': 0}
#         self._min_fee = min_fee
#         self._pct_fee = pct_fee
#         self._sell_pct = sell_pct
    

#     def _net_returns(self, df):
#         '''
#         The passed dataframe must have the following columns:
#         --------
#         Capital - Shows the gross cumulative return/capital the strategy has generated.
#         Position - Shows the position the strategy has at each date.
#                    Valid values for the Position column are HOLD, SELL or BUY.
#         '''
#         # Calculate fees
#         df['Fees_%'] = (df['Capital']*df['Position'].replace(['HOLD','BUY','SELL'],[0,-1,-1])*(self._pct_fee)).cumsum()
#         df['Fees_Flat'] = (df['Position'].replace(['HOLD','BUY','SELL'],[0,-1,-1])*(self._min_fee)).cumsum()
#         df['Fees_Total'] = df[['Fees_%','Fees_Flat']].sum(axis=1)

#         # Calculate signal returns net of fees
#         df['Capital_Net'] = df['Capital'] + df['Fees_Total']

#         return df

    
#     def _gross_returns(self, df):
#         '''
#         TO DO
#         '''
#         capital = self._starting_capital
        
#         # Iterate over the dataframe to calculate the signal's returns
#         for date, row in df.iterrows():

#             asset_is_held = (row['Signal'] == 1) & (row['Position'] == 'HOLD')
#             asset_is_sold = (row['Signal'] == 0) & (row['Position'] == 'SELL')

#             if asset_is_held:
#                 capital = (1+df.loc[date,'Trading_Price_%'])*capital
#                 df.loc[date,'Capital'] = capital

#             elif asset_is_sold:
# # Fix this by breaking it down between invested capital and cash
# # if the strategy sells it should sell from the invested capital and only by the % specified
# # if the strategy buys it should buy only using the cash
# # if a strategy holds (neither buys nor sells) the cash should be unchanged
#                 capital = (1+df.loc[date,'Trading_Price_%'])*capital*self._sell_pct
#                 df.loc[date,'Capital'] = capital
#             else:
#                 df.loc[date,'Capital'] = capital
        
#         return df


#     def btest_single_asset(self, data, prices, signal):
#         '''
#         TO DO
#         -------
#         Signal: signal represents an action at time T, based on information processed up to T-1
#         '''
#         # Create a dataframe with closing prices, signal and capital data
#         df = _pd.DataFrame(columns = ['Valuation_Price'])
#         df['Valuation_Price'] = data[prices]
#         df['Signal'] = data[signal]
#         df['Capital'] = _np.NaN
        
#         # Position translates signal to buy, sell, hold positions / orders
#         df['Position'] = df['Signal'].diff().replace([_np.NaN,0,-1,1],
#                                                      ['HOLD','HOLD','SELL','BUY'])
        
#         # Trading price is the price the strategy buys / sells the asset ie including a drift term
#         df['Trading_Price'] = df['Valuation_Price']* (1+df['Position'].replace(
#                                                         ['HOLD','SELL','BUY'],
#                                                         [self._drift['HOLD'],
#                                                          self._drift['SELL'],
#                                                          self._drift['BUY']]))
#         # Calculate percentages for trading price column
#         df['Trading_Price_%'] = df['Trading_Price'].pct_change()

#         # Calculate Buy & Hold strategy
#         df['Buy_and_Hold'] = df['Valuation_Price'].pct_change().add(1).cumprod().fillna(1)*self._starting_capital

#         # Calculate signal gross returns
#         df = self._gross_returns(df)

#         # Calculate strategy fees / costs and net returns
#         df = self._net_returns(df)

#         return df

    
    