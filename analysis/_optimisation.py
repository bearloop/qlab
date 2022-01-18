import pandas as _pd
import numpy as _np
from math import exp
import scipy.optimize as _sco

class Optimise:

    def __init__(self, frequency=252, annualised_risk_free_rate=0, ef_points=25):
        self.expected_ret = None
        self.covariance = None
        self._constraints = None
        self.bounds = None
        self._assets = None
        self.asset_names = None
        self._initial_weights = None
        self._freq = frequency
        self.ef_points = ef_points
        self._frontier_return = None
        self.annualised_risk_free_rate = annualised_risk_free_rate
        pass
    
    # ---------------------------------------------------------------------------------------------------
    def _portfolio_return(self, weights, annualised_expected_returns):
        ''' Returns mean portfolio return given asset annualised expected returns and asset weights'''
        return _np.nansum(annualised_expected_returns * weights)
    
    # ---------------------------------------------------------------------------------------------------
    def _portfolio_variance(self, weights, annualised_covariance):
        ''' Returns portfolio variance given asset annualised returns covariance and asset weights'''
        return _np.nansum(weights * _np.nansum(annualised_covariance * weights, axis=1))

    # ---------------------------------------------------------------------------------------------------
    def shrunk_covariance(self, df):
        ''
        pass
    
    # ---------------------------------------------------------------------------------------------------
    def _max_return_portfolio(self, weights, annualised_expected_returns):
        ''' Find highest return portfolio returns '''
        return -self._portfolio_return(weights=weights, annualised_expected_returns=annualised_expected_returns)

    # ---------------------------------------------------------------------------------------------------
    def _min_variance_portfolio(self, weights, annualised_covariance):
        ''' Find minimum variance portfolio volatility'''
        ann_variance = self._portfolio_variance(weights=weights, annualised_covariance=annualised_covariance)
        return _np.sqrt(ann_variance)
    
    # ---------------------------------------------------------------------------------------------------
    def _max_sharpe_portfolio(self, weights, annualised_expected_returns, annualised_covariance):
        ''' Find maximum Sharpe ratio portfolio'''
        # Mean expected return annualised
        mu = self._portfolio_return(weights=weights, annualised_expected_returns=annualised_expected_returns)
        # Expected volatility annualised
        vol = _np.sqrt(self._portfolio_variance(weights=weights, annualised_covariance=annualised_covariance))
        # Annualised risk free rate
        rf = self.annualised_risk_free_rate
        # Sharpe ratio
        sharpe_ratio = (mu - rf) / vol

        return -sharpe_ratio
    
    # ---------------------------------------------------------------------------------------------------
    def _risk_parity_portfolio(self, weights, annualised_covariance):
        # Expected volatility annualised
        vol = _np.sqrt(self._portfolio_variance(weights=weights, annualised_covariance=annualised_covariance))
        # Marginal risk contribution
        marginal_risk_contribution = _np.nansum(annualised_covariance*weights, axis=1) / vol
        # Overall risk contribution
        total_risk_contribution = weights*marginal_risk_contribution
        # Risk parity: Set initial risk budget as 1/N (If 1/N then "risk parity", otherwise "risk budgeting")
        risk_budget = self._initial_weights
        risk_parity = _np.nansum((total_risk_contribution-(_np.array(risk_budget)*vol))**2)

        return risk_parity

    # ---------------------------------------------------------------------------------------------------
    def _set_constraints(self, con_type=None):
        ''' Set constraints '''
        if con_type is None:
            self._constraints = [{'type': 'eq', 'fun': lambda x: _np.sum(x) - 1}]

        elif con_type=='frontier':
            self._set_constraints() # clear existing constraints first, then add the default constraint Σw=1 before any other
            self._constraints.append({'type': 'eq', 'fun': lambda x: self._portfolio_return(x, self.expected_ret) - self._frontier_return})
            
    # ---------------------------------------------------------------------------------------------------
    def _set_bounds(self):
        ''' Set bounds '''
        self._assets = len(self.expected_ret)
        self._initial_weights = self._assets * [1./self._assets]
        self.bounds = tuple((0,1) for a in range(self._assets))

    # ---------------------------------------------------------------------------------------------------
    def clean_up_results(self, results_dictionary):
        ''' Cleans up optimisation results dictionary and converts key information to a dataframe'''
        # Create a dataframe
        clean_df = _pd.DataFrame(columns = results_dictionary.keys(),
                           index = ['Return', 'Volatility', 'Sharpe'] + self.asset_names,
                           data=_np.NaN)
        
        for port_type in clean_df.columns:
            # Print out optimisation message
            if 'Optimization terminated successfully' != results_dictionary[port_type]['message']:
                print('Something went wrong while performing portfolio optimisation for',port_type)
            
            # Return and volatility
            weights = list(results_dictionary[port_type]['x'].round(5))

            clean_df.loc['Return',port_type] = self._portfolio_return(weights=weights,
                                                                      annualised_expected_returns=self.expected_ret)
            
            clean_df.loc['Volatility',port_type] = _np.sqrt(self._portfolio_variance(weights=weights,
                                                                                     annualised_covariance=self.covariance))
            
            # Sharpe ratio
            sharpe = (clean_df.loc['Return',port_type] - self.annualised_risk_free_rate) / clean_df.loc['Volatility',port_type]
            clean_df.loc['Sharpe',port_type] = sharpe

            # Asset weights
            clean_df.loc[self.asset_names,port_type] = weights
            
        return clean_df
    
    # ---------------------------------------------------------------------------------------------------
    def _single_asset_portfolio(self, df):
        
        # Construct data frame
        output = _pd.DataFrame(columns=['MaxReturn','MinVariance','MaxSharpe','RiskParity'])
        
        # Set return to the asset's annualised return
        output.loc['Return',:] = df.pct_change().mean()[0]*self._freq

        # Set volatility to the asset's annualised standard deviation of returns
        output.loc['Volatility',:] = df.pct_change().std()[0]*(self._freq**(1/2))

        # Set Sharpe ratio
        output.loc['Sharpe',:] = (output.loc['Return','MaxReturn'] - self.annualised_risk_free_rate) / output.loc['Volatility','MaxReturn']
        
        #  Set weight to 1
        single_asset_name = df.columns[0]
        output.loc[single_asset_name,:] = 1

        return output
        
    # ---------------------------------------------------------------------------------------------------
    def optimal_portfolios(self, df, expected_ret=None, covariance=None, method='SLSQP', verbose=False):
        '''
        Returns results for 4 optimised by some criterion portfolios:
        (1) Highest Return, (2) Minimum variance, (3) Max Sharpe ratio, (4) Risk parity portfolio
        Arguments:
        ----------
        df: pd.DataFrame, asset prices time series
        expected_ret: None or pd.Series, asset names as its index and annualised returns as its values
        covariance: None or pd.DataFrame, asset returns covariance
        '''
        df = _pd.DataFrame(df).copy()

        if len(df.columns) <= 1:
            return self._single_asset_portfolio(df)

        else:
            # Set assets expected returns & covariance
            if expected_ret is None:
                self.expected_ret =  df.pct_change().dropna(how='all').mean()*self._freq
            else:
                self.expected_ret = expected_ret

            if covariance is None:
                self.covariance = df.pct_change().dropna(how='all').cov()*self._freq
            else:
                self.covariance = covariance
            
            # Asset names
            self.asset_names = list(self.expected_ret.index)

            # Set bounds and constraints
            self._set_bounds()
            self._set_constraints()

            # Optimisation by portfolio type
            results_dict = {}
            results_dict['MaxReturn'] = _sco.minimize(self._max_return_portfolio, x0=self._initial_weights,
                                                    args=(self.expected_ret), method=method,
                                                    bounds=self.bounds, constraints=self._constraints)

            results_dict['MinVariance'] = _sco.minimize(self._min_variance_portfolio, x0=self._initial_weights,
                                                        args=(self.covariance), method=method,
                                                        bounds=self.bounds, constraints=self._constraints)

            results_dict['MaxSharpe'] = _sco.minimize(self._max_sharpe_portfolio, x0=self._initial_weights,
                                                    args=(self.expected_ret, self.covariance), method=method,
                                                    bounds=self.bounds, constraints=self._constraints)

            results_dict['RiskParity'] = _sco.minimize(self._risk_parity_portfolio, x0=self._initial_weights,
                                                    args=(self.covariance), method=method,
                                                    bounds=self.bounds, constraints=self._constraints)
        
            if verbose:
                return results_dict
            else:
                return self.clean_up_results(results_dict)
            
    # ---------------------------------------------------------------------------------------------------
    def efficient_frontier(self, df, expected_ret=None, covariance=None, method='SLSQP'):
        '''
        '''
        optimal_portfolios_df = self.optimal_portfolios(df=df, expected_ret=expected_ret,
                                                        covariance=covariance, method=method,
                                                        verbose=False)
        
        # Returns of portfolios along the efficient frontier
        minimum_return = optimal_portfolios_df.loc['Return','MinVariance']
        maximum_return = optimal_portfolios_df.loc['Return','MaxReturn']
        target_range = _np.linspace(start=minimum_return, stop=maximum_return - 0.0001, num=self.ef_points)

        efrontier_dct = {}
        self._set_constraints(con_type='frontier')

        for ind, ret_level in enumerate(target_range):
            self._frontier_return = ret_level
            efrontier_dct['EF_'+str(ind+1)] = _sco.minimize(self._min_variance_portfolio, x0=self._initial_weights,
                                                             args=(self.covariance), method=method,
                                                             bounds=self.bounds, constraints=self._constraints)
        
        # "Reset" frontier return to None, otherwise the last ret_level value will be stored in self._frontier_return
        self._frontier_return = None    

        # Clean up eff frontier portfolios optimisation results and concat with the main 4 portfolios
        optimal_portfolios_df = _pd.concat([optimal_portfolios_df, self.clean_up_results(efrontier_dct)],axis=1)

        return optimal_portfolios_df
    
    # ---------------------------------------------------------------------------------------------------