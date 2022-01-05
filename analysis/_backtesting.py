import pandas as _pd
import numpy as _np
import cvxpy as cp
import math

class BackTest:

    def __init__(self, initial_capital=10000):
        self._cash = initial_capital  

    # ---------------------------------------------------------------------------------------------------
    def _calc_target_units(self, units_t1, units_t0=None):
        """
        Return weights difference between t0 and t1.
        """
        if units_t0 is None:
            units_t0 = [0 for i in units_t1]
            
        return list(_np.array(units_t1) - _np.array(units_t0))

    # ---------------------------------------------------------------------------------------------------
    def _calc_single_asset_units(self, transaction_price, asset_allocated_capital):
        """
        Figure out how many units of the asset in question should be bought given a
        transaction price and investment capital.
        """
        # How many units of the asset will be bought
        try:
            return math.floor(asset_allocated_capital/transaction_price)
        except:
            # transaction price is either 0 or None so the asset can't be transacted upon
            return 0

    # ---------------------------------------------------------------------------------------------------
    def _calc_units_based_on_weights(self, transaction_prices, weights, capital):
        """
        Figure out how many units of each asset should be bought given the asset's
        transaction price and weight out of the investment capital.
        """
        assets_units = []
        
        for ind, wei in enumerate(weights):
            assets_units.append(self._calc_single_asset_units(transaction_prices[ind], wei*capital))
        # print(transaction_prices, weights, capital, assets_units)
        return assets_units

    # ---------------------------------------------------------------------------------------------------
    def _calc_position_cost(self, transaction_prices, assets_units):
        """
        Calculate position cost.
        """
        return round(sum(_np.array(transaction_prices) * _np.array(assets_units)),4)

    # ---------------------------------------------------------------------------------------------------
    def _calc_cash_in_the_portfolio(self, previous_cash, cost):
        """
        Calculate current cash position, given previous cash position (t_0) and any investments costs
        incurred / made.
        """
        return round(previous_cash - cost, 4)

    # ---------------------------------------------------------------------------------------------------
    def _calc_portfolio_value(self, valuation_prices, assets_units):
        """
        Calculate position value (Different than cost on the same day as eod prices != transaction prices).
        """
        return round(sum(_np.array(valuation_prices) * _np.array(assets_units)),4)

    # ---------------------------------------------------------------------------------------------------
    def _calc_total_value(self, valuation_prices, assets_units, current_cash):
        
        current_value = self._calc_portfolio_value(valuation_prices=valuation_prices, assets_units=assets_units)
        
        return current_value + current_cash

    # ---------------------------------------------------------------------------------------------------
    def _check_cash_balance(self, transaction_prices, cash, units_suggested, units_old=None):
        
        # If previous unit set is missing then the assets had not been held
        if units_old is None:
            units_old = [0 for i in units_suggested]
        
        # Variable dictionary to hold "new units"
        units_new = {}

        # Initialise constraints list
        constraints = []

        for i in range(len(units_suggested)):

            # New variable stored in dictionary units_new
            units_new[i] = cp.Variable(1, integer=True)

            # Lower bound
            constraints.append(0<=units_new[i])

            # Upper bound
            constraints.append(units_new[i]<=units_suggested[i])

        # Expression to minimize: [ cash - (net purchases) ], if net purchases are negative then the sum is sure > 0
        exp = cash -cp.sum([transaction_prices[ind] * (units_new[ind] - units_old[ind]) for ind in units_new.keys()])

        # Extra constraint of [ cash - (net purchases) must be >= zero ]
        constraints.append(exp >= 0)                           

        # Problem specification
        prob = cp.Problem(cp.Minimize(exp), constraints=constraints)

        # Only the ECOS_BB algorithm worked. It's considered unreliable for large scale problems but it should be
        # enough in this case
        prob.solve(solver='ECOS_BB') 
        
        # new_cash = round(exp.value[0],4) -> new cash balance if you want to return this

        # Return units that make sure cash balance is non-negative
        non_negative_cash_balance_units = [round(units_new[ind].value[0]) for ind in units_new.keys()]
            
        return non_negative_cash_balance_units

    # ---------------------------------------------------------------------------------------------------
    def evaluate_strategy(self, prices_df, signals_df):
        
        # Change signals df columns names (CNT: count of non-zero signals)
        signals_df.columns = ['SIG_'+i for i in signals_df.columns]
        signals_df['CNT'] = signals_df.sum(axis=1)
        signals_df = signals_df.div(signals_df['CNT'],axis=0).replace(_np.NaN,0)

        # Transaction prices df and columns names
        trp_df = prices_df.rolling(2).mean()
        trp_df.columns = ['TRP_'+i for i in trp_df.columns]

        # Units df and columns names
        units_names = ['UNT_'+i for i in prices_df.columns]

        # Units, Net_Purchases, Cash, Value
        labels = units_names + ['NET_PURCHASES','CASH','VALUE']

        # Concat prices and signals
        df = _pd.concat([prices_df, signals_df, trp_df],axis=1)
        df[labels] = _np.NaN

        # Lists of assets by category: weight, units, transaction price, value price
        weight_cols = [i for i in df.columns if 'SIG_' in i]
        units_cols = [i for i in df.columns if 'UNT_' in i]
        trp_cols = [i for i in df.columns if 'TRP_' in i]
        vlp_cols = list(prices_df.columns)

        # Find first date where signal is positive for at least one asset
        start_date = signals_df[signals_df['CNT']>0].index[0]
        df = df.loc[start_date:,:]


        first_valid_date = True
        for i in df.index:

            trp = list(df.loc[i,trp_cols].replace(_np.NaN,0))
            vp = list(df.loc[i,vlp_cols].replace(_np.NaN,0))
            wei = list(df.loc[i,weight_cols])
   
            if first_valid_date:
                
                df.loc[i, units_cols] = self._calc_units_based_on_weights(transaction_prices=trp,
                                                                        weights=wei,
                                                                        capital=self._cash)
                units_ls = list(df.loc[i,units_cols])
                
                df.loc[i,'NET_PURCHASES'] = self._calc_position_cost(transaction_prices=trp,
                                                                     assets_units=units_ls)
                
                df.loc[i,'CASH'] = self._calc_cash_in_the_portfolio(previous_cash=self._cash,
                                                                    cost=df.loc[i,'NET_PURCHASES'])
                
                df.loc[i,'VALUE'] = self._calc_total_value(valuation_prices=vp,
                                                           assets_units=units_ls,
                                                           current_cash=df.loc[i,'CASH'])
                
                first_valid_date = False

            else:
                if list(df.loc[previous_date,weight_cols]) == list(df.loc[i,weight_cols]):
            
                    df.loc[i,units_cols] = df.loc[previous_date,units_cols]
                    
                else:
                    initial_units = self._calc_units_based_on_weights(transaction_prices=trp,
                                                                    weights=wei,
                                                                    capital=df.loc[previous_date,'VALUE'])
                    
                    df.loc[i,units_cols] = self._check_cash_balance(transaction_prices=trp,
                                                                    cash=df.loc[previous_date,'CASH'],
                                                                    units_suggested = initial_units,
                                                                    units_old = df.loc[previous_date,units_cols])
        
        
                units_ls = list(df.loc[i,units_cols])
        
                diff_in_units = self._calc_target_units(units_t1=df.loc[i,units_cols],
                                                        units_t0=df.loc[previous_date,units_cols])

                df.loc[i,'NET_PURCHASES'] = self._calc_position_cost(transaction_prices=trp,
                                                                    assets_units=diff_in_units)

                df.loc[i,'CASH'] = self._calc_cash_in_the_portfolio(previous_cash=df.loc[previous_date,'CASH'],
                                                                    cost=df.loc[i,'NET_PURCHASES'])


                df.loc[i,'VALUE'] = self._calc_total_value(valuation_prices=vp,
                                                        assets_units=units_ls,
                                                        current_cash=df.loc[i,'CASH'])
            previous_date = i

        return df
    # ---------------------------------------------------------------------------------------------------

# ---------------------------------------------------------------------------------------------------
# class BackTest:
    
#     def __init__(self, initial_capital=10000):
#         self._cash = initial_capital    
    
#     # ---------------------------------------------------------------------------------------------------
#     def _get_units(self, transaction_price, capital):
#         """
#         Figure out how many units of the asset in question will be bought given a
#         transaction price and investment capital.
#         """
#         # How many units of the asset will be bought
#         units = round(capital/transaction_price)

#         # Asset value must be less than total investment
#         if units*transaction_price > capital:
#             return units-1
        
#         else:
#             return units
    
    
#     def _calc_position(self, value_p=None, trade_p=None, signal=None, action=None, cash=0, units=0):
#         """
#         Calculates what happens when the strategy enters a position, liquidates its holdings or
#         stands pat.
#         """

#         # ------------------------------------------------------
#         # ------ what happens when you enter a position -------
#         # ------------------------------------------------------
#         if (signal=='IN') and (action=='BUY'):

#             # Units purchased
#             units = self._get_units(trade_p, cash)

#             # Position initial cost
#             cost = round(units * trade_p,4)

#             # Cash value
#             cash = round(cash - cost,4)
        
#         # ------------------------------------------------------
#         # ------ what happens when you get out of a position ---
#         # ------------------------------------------------------
#         elif (signal=='OUT') and (action=='SELL'):

#             # Liquidate position to cash
#             cash = cash + trade_p * units

#             # Purchase Cost is considered to be 0 as there are no purchases made
#             cost = 0
            
#             # Also no assets are held so units = 0
#             units = 0
        
#         # ------------------------------------------------------  
#         # ------ what happens when you don't do anything -------
#         # ------------------------------------------------------
#         elif (action=='NO ACTION'):
#             # No actions were taken, cash is unchanged, units are unchanged, cost = 0
#             cash = cash
#             units = units
#             cost = 0
        
#         # Value of position
#         valuation = round(units * value_p,4)
            
#         # Value of position plus cash
#         total = valuation + cash

#         return units, cost, cash, valuation, total
    
    
#     def evaluate_single_asset_strat(self, df, name='Asset', signal='Signal'):
#         """
#         Expects a dataframe with two columns: name & signal.
        
#         Signal: a list of 'IN'/'OUT' strings indicating whether the asset should be long or not
#         Price: a list of asset prices (assumed to be end-of-day prices)
        
#         Derived columns:
#         Trade price: the mean price of a 2-day period that a transaction is assumed to take place
#         Action: the order the strategy issues, 'NO ACTION', 'SELL' or 'BUY' depending on whether the
#         asset is already held and on whether it should be long or not.
#         Units: units of the asset held/purchased at any given time
#         Cost: units * trade price (the invested capital)
#         Cash: cash in the portfolio
#         Valuation: units * value price (even for the same day valuation is different than the cost)
#         Total: sum of valuation and cash
#         """
        
#         # Add Trade and Signal columns as per above

#         df['Trade'] = df[name].rolling(2).mean()
#         df['Action'] = df[signal].replace(['OUT','IN'],[0,1]).diff().replace([0,-1,1],['NO ACTION','SELL','BUY'])
        
#         # Add the following columns that are handy for performance calculation
#         new_labels = ['Units', 'Cost', 'Cash', 'Valuation', 'Total']
#         df[new_labels] = _np.NaN

#         # Find the first time you enter the strategy as long ('BUY')
#         first_valid_buy = df[df['Action']=='BUY'].first_valid_index()
        
#         # Start from this first date
#         df = df.loc[first_valid_buy:,:]
        
#         # Iterate over the period
#         for i in df.index:

#             if i == first_valid_buy:
#                 capital = self._cash
#                 units_position = 0

#             else:
#                 capital = df.loc[previous_day,'Cash']
#                 units_position = df.loc[previous_day,'Units']
            
#             # Fill the ['Units', 'Cost', 'Cash', 'Valuation', 'Total'] columns
#             df.loc[i, new_labels] = self._calc_position(value_p=df.loc[i,name],
#                                                         trade_p=df.loc[i,'Trade'],
#                                                         signal=df.loc[i,signal],
#                                                         action=df.loc[i,'Action'],
#                                                         cash=capital,
#                                                         units=units_position)
            
#             # Keep track of the previous valid date to use in the else statement above
#             previous_day = i
        
#         # Calculate your benchmark - a buy and hold strategy!
#         df['Buy_Hold'] = df[name].pct_change().add(1).cumprod().fillna(1)*df['Total'].iloc[0]
        
#         return df
#     # ---------------------------------------------------------------------------------------------------
