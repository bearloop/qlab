from datetime import timedelta
import pandas as _pd
import numpy as _np
import cvxpy as cp
import math

class BackTest:

    def __init__(self, initial_capital=10000, flat_fee=2.2, percentage_fee=0.1/100):
        self._initial_capital = initial_capital 
        self._flat_fee = flat_fee
        self._percentage_fee = percentage_fee

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
    def _calc_net_purchases(self, transaction_prices, assets_units):
        """
        Calculate net purchases cost (if negative then this translates to net sales).
        """
        return round(sum(_np.array(transaction_prices) * _np.array(assets_units)),4)

    # ---------------------------------------------------------------------------------------------------
    def _calc_cash_balance(self, previous_cash, cost):
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
        """
        Calculate sum of cash and portfolio value
        """
        return current_cash +self._calc_portfolio_value(valuation_prices=valuation_prices, assets_units=assets_units)

    # ---------------------------------------------------------------------------------------------------
    def _check_cash_balance(self, transaction_prices, cash, units_suggested, units_prev=None):
        
        # If previous unit set is missing then the assets had not been held
        if units_prev is None:
            units_prev = [0 for i in units_suggested]
        
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
        exp = cash -cp.sum([transaction_prices[ind] * (units_new[ind] - units_prev[ind]) for ind in units_new.keys()])

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
    def _calc_strat(self, df, asset_names):
        """
        
        """
        # Lists of assets by category: weight, units, transaction price, value price
        weight_cols = [i for i in df.columns if 'SIG_' in i]
        units_cols = [i for i in df.columns if 'UNT_' in i]
        trp_cols = [i for i in df.columns if 'TRP_' in i]
        vlp_cols = asset_names
        
        # We begin from the first date the portfolio enters a long position, so the start date..
        # ..is the date before that
        previous_date = df.index[0]

        for current_date in df.index[1:]:
            
            # trp: transaction prices per asset on the current date
            trp = list(df.loc[current_date,trp_cols].replace(_np.NaN,0))

            # vp: valuation (end-of-day) prices per asset on the current date
            vp = list(df.loc[current_date,vlp_cols].replace(_np.NaN,0))

            # wei: signal translated into weights per asset on the current date..
            # ...if the signal says two assets must be held, then their weights are 50% each
            wei = list(df.loc[current_date,weight_cols])

            # Check if the weights / signals have changed (i.e. you shouldn't act if there aren't any signal changes)..
            # ..though the actual portfolio weights well vary of course
            if list(df.loc[previous_date, weight_cols]) == list(df.loc[current_date, weight_cols]):
        
                df.loc[current_date,units_cols] = df.loc[previous_date,units_cols]
            
            # Otherwise, since there's at least one asset signal that's changed (diff from previous date), recalculate all units
            else:
                units_proposed = self._calc_units_based_on_weights(transaction_prices=trp,
                                                                  weights=wei,
                                                                  capital=df.loc[previous_date,'VALUE'])
                
                df.loc[current_date,units_cols] = self._check_cash_balance(transaction_prices=trp,
                                                                           cash=df.loc[previous_date,'CASH'],
                                                                           units_suggested = units_proposed,
                                                                           units_prev = df.loc[previous_date,units_cols])
            
            # Auxiliery arguments: current date units, previous date units and previous date cash balance
            units_t1 = df.loc[current_date,units_cols]
            units_t0 = df.loc[previous_date,units_cols]
            starting_cash = df.loc[previous_date,'CASH']
                
            # Subtract previous date's units from current date's and use the diffence to calculate net purchases
            diff_in_units = self._calc_target_units(units_t1=units_t1, units_t0=units_t0)

            # Add current date's net purchases to the dataframe
            df.loc[current_date,'NET_PURCHASES'] = self._calc_net_purchases(transaction_prices=trp,
                                                                            assets_units=diff_in_units)

            # Add current date's cash value to the dataframe
            df.loc[current_date,'CASH'] = self._calc_cash_balance(previous_cash=starting_cash, 
                                                                  cost=df.loc[current_date,'NET_PURCHASES'])
            
            # Add the (current date's) sum of the portfolio and cash value to the dataframe
            df.loc[current_date,'VALUE'] = self._calc_total_value(valuation_prices=vp,
                                                                  assets_units=units_t1,
                                                                  current_cash=df.loc[current_date,'CASH'])
                
            # Keep previous date to use on the next iteration
            previous_date = current_date

        return df

    # ---------------------------------------------------------------------------------------------------
    def _calc_fees(self, df):
        """
        Calculate strategy fees based on the number and value of every transaction that has taken place
        over the course of the strategy.
        """
        df = df.copy()

        # Units held per asset df
        units_cols = [i for i in df.columns if 'UNT_' in i] 
        units_df = df[units_cols].diff().copy()
        units_df.columns = [i[4:] for i in units_df.columns]
        
        # Transaction prices df
        tpr_cols = [i for i in df.columns if 'TRP_' in i]
        tpr_df = df[tpr_cols].copy()
        tpr_df.columns = [i[4:] for i in tpr_df.columns]
        
        # Fees calculation considering every transaction (purchase or sale of assets)

        # Percentage fees calculation: absolute value of rebalancing * percentage fee
        df['PCT_FEES'] = abs(units_df.mul(tpr_df)*(self._percentage_fee)).sum(axis=1)
        
        # Flat fees calculation: purchase / sale of an asset * flat fee
        df['FLAT_FEES'] = ((units_df.mul(tpr_df).fillna(0)!=0)*self._flat_fee).sum(axis=1)
        
        # Sum of fees
        df['TOTAL_FEES'] = df[['PCT_FEES','FLAT_FEES']].sum(axis=1)
        
        return df

    # ---------------------------------------------------------------------------------------------------
    def evaluate_strategy(self, prices_df, signals_df, verbose=True):
        """
        Strategy evaluation based on asset prices and signals. Signal is translated to weight on the date
        the strategy rebalances but afterwards it behaves as a buy and hold strategy until the next rebalancing
        date (the SIG_ASSET columns instead show fixed weights but do not get confused by that).
        prices_df: a dataframe with asset prices.
        signals_df: a dataframe with boolean values indicating whether every asset is held or not at
                    any given time.
        """
        # Copy so as not to change the original df
        prices_df = prices_df.copy()
        signals_df = signals_df.copy()
        
        # Asset names
        assets_names = list(prices_df.columns)

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

        # Concat (actual and transaction) prices and signals/weights
        df = _pd.concat([prices_df, signals_df, trp_df],axis=1)
        df[labels] = _np.NaN

        # Find first date where signal is positive for at least one asset
        start_date = signals_df[signals_df['CNT']>0].index[0]
        df = df.loc[start_date:,:]
        
        # Drop rows that don't have at least one transaction price. this tries to fix the issue that appears..
        # ..when there's an imbalance between value and transaction prices as well as signals and transaction prices
        # df = df[df[trp_df.columns].notnull().any(axis=1)]

        # Add an origin date at the start of the df and set units, net purchases, cash and value
        origin = _pd.DataFrame(index=[df.index[0]-timedelta(1)],columns = df.columns, data=_np.NaN)
        origin[['VALUE','CASH']] = self._initial_capital
        origin[['NET_PURCHASES']] = 0
        origin[units_names] = 0

        # Concat origin with the rest of the dates
        df = _pd.concat([origin, df])

        # Calculate strategy returns
        df = self._calc_strat(df=df, asset_names=assets_names)
        
        # Calculate fees
        df = self._calc_fees(df=df)

        if verbose:
            return df.copy()
        else: 
            # Return only asset prices, asset units, net purchases, cash balance, fees and value
            columns = assets_names + labels + ['PCT_FEES','FLAT_FEES','TOTAL_FEES']
            return df[ columns ].copy()
    # ---------------------------------------------------------------------------------------------------