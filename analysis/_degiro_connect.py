import requests as _requests
import pandas as _pd
import json as _json
from datetime import datetime as _datetime
import os

class DeGiro():

    def __init__(self, user, psw):
        self.user = user
        self.psw = psw
        self._BASE_TRADER_URL = 'https://trader.degiro.nl'
        self._CONFIG_URL = self._BASE_TRADER_URL + '/login/secure/config'
        self._LOGIN_URL = self._BASE_TRADER_URL+'/login/secure/login'
        self._SRCH_URL = 'v5/products/lookup?intAccount='
        self.credentials = None
        self.shortcuts = ['YTD', 'P1D', 'P1W', 'P1M', 'P3M', 'P6M', 'P1Y', 'P3Y', 'P5Y', 'P50Y']
        self.user_agent = os.environ.get("USER_AGENT")

    # --------------------------------------------------------------------------------------------------------------
    def login(self):
        
        product_search_url, account, userToken, config_data, secID = self._get_client_info()
        
        data_dct = {'product_search_url': product_search_url,
                    'account_id': account,
                    'user_token': userToken,
                    'config_data': config_data,
                    'session_id': secID}
        
        self.credentials = data_dct
        print('Logged in to DeGiro account')

    # --------------------------------------------------------------------------------------------------------------

    def _get_client_info(self):
        
        try:
            config_data, secID = self._get_config_data()
            # print(config_data , secID)
            
            pa_url = config_data['data']['paUrl']
            
            url_client = pa_url+'client?sessionId='+secID
            
            product_search_url = config_data['data']['productSearchUrl']
            
            try:
                client_info = _requests.get(url_client, headers = {'user-agent': self.user_agent})

                client_data =  _json.loads(client_info.content.decode("utf-8"))
                
                if client_info.status_code == 200:

                    account = str(client_data['data']['intAccount'])
                    userToken = str(client_data['data']['id'])
                    
                    return product_search_url, account, userToken, config_data, secID
                
                else:
                    print('Client data fetch failed')
            
            except Exception as e:
                print('2 - client info', e.args)
                print('Config data or session id fetch failed')

        except Exception as e:
            print('1 - client info', e.args)
    
    # --------------------------------------------------------------------------------------------------------------
    def _get_config_data(self):
        
        try:
            secID = self._get_session_id()
            
            if secID is not None:
                updConfig =  _requests.get(self._CONFIG_URL, headers = {'Cookie':'JSESSIONID='+secID+';','user-agent':self.user_agent})
                
                if updConfig.status_code ==  200:
                    config_data = _json.loads(updConfig.content.decode("utf-8"))
                    
                    return config_data, secID
                else:
                    print('Config data fetch failed')
        
        except Exception as e:
            print('3 - config data', e.args)


    # --------------------------------------------------------------------------------------------------------------
    def _get_session_id(self):
        
        try:
            de_giro = _requests.post(self._LOGIN_URL,
                                     headers = {
                                        'Content-Type': 'application/json',
                                        'user-agent': self.user_agent,
                                        },
                                     json= {'username': self.user, 'password': self.psw} )
            # secID = de_giro.headers['Set-Cookie'].split('JSESSIONID=')[1].split(';')[0]
            secID = de_giro.json()['sessionId']
            
            return secID
            
        except Exception as e:
            print('4 - session id', e.args)
            print('Session id fetch failed')
    
    # --------------------------------------------------------------------------------------------------------------
    def _securities_dict(self, df, assets=None):
        '''
        Returns a list of dictionaries from a two-column dataframe. They keys of each dictionary are the values of
        the first column and its values are the values of the second column.
        df: a two-column dataframe with no missing values
        '''
        ls = list(map(lambda x: {str(x[0]):str(x[1])}, df.dropna().values))
        if assets is None:
            return ls
        else:
            return list(filter(lambda x: list(x.values())[0] in assets, ls))
    # --------------------------------------------------------------------------------------------------------------
    
    def comp_series(self, securities, ts_type='price', date_range={'range':None,'auto':'P1Y'}):
        '''
        Returns price or volume data for multiple securities given a date range.
        range: e.g. '2019-01-01:2020-12-31'
        auto: e.g.  any of the shortcuts such as 'P1Y'
        ts_type: 'price' | 'volume'
        securities: list of dictionaries 'vwd_id':'security_name'}
        '''

        composite = _pd.DataFrame()

        for security_dict in securities:
            data = self.single_series(security=security_dict, ts_type=ts_type, date_range=date_range)
            composite = _pd.concat([composite,data],axis=1)

        return composite

    # --------------------------------------------------------------------------------------------------------------
    def single_series(self, security, ts_type='price', date_range={'range':None,'auto':'P1Y'}):
        '''
        Returns price or volume data for a single security given a date range.
        range: e.g. '2019-01-01:2020-12-31'
        auto: e.g.  any of the shortcuts such as 'P1Y'
        ts_type: 'price' | 'volume'
        security: {'vwd_id':'security_name'}
        '''

        try:
            user_token = self.credentials['user_token']
            time_period = self._get_time_period(date_range)

            # Unpack dictionary (single key-value pair)
            security_id = list(security.keys())[0]
            security_name = list(security.values())[0]

            url = 'https://charting.vwdservices.com/hchart/v1/deGiro/data.js?'+\
                'resolution=P1D&culture=en-US&'+time_period+'&series=issueid%3A'+security_id+\
                '&series='+ts_type+'%3Aissueid%3A'+security_id+'&format=json&userToken='+user_token
            

            data = _json.loads(_requests.get(url).content)['series']
            ts = self._transform_time_series_response(data=data, column_name=security_name)
            ts.index = _pd.to_datetime(ts.index)

            return ts
        
        except Exception as e:
            print(list(security.values())[0], e.args)
    
    # --------------------------------------------------------------------------------------------------------------
    def _get_time_period(self, date_range):
        '''Assumes start < end. So, don't be silly.'''
        
        if 'auto' not in date_range: date_range['auto'] = None
        if 'range' not in date_range: date_range['range'] = None

        if date_range['auto'] in self.shortcuts:
            time_period = 'period='+date_range['auto']
        else:
            start = date_range['range'].split(':')[0]
            end = date_range['range'].split(':')[1]
            time_period = 'start='+start+'&end='+end
        
        return time_period

    # --------------------------------------------------------------------------------------------------------------
    def _transform_time_series_response(self, data, column_name):
        ''' '''
        # Use isin if there's no column name
        # if column_name is None:
        #    column_name = data[0]['data']['isin']

        # first, last index -> get first and last index items to generate a series of time representation
        index_first = data[1]['data'][0][0]
        index_last = data[1]['data'][-1][0]
        time_index = [i for i in range(index_first, index_last+1)]

        # first, last date -> get first and last date to generate the date range
        date_first = _datetime.strptime(data[0]['data']['windowFirst'][:10],'%Y-%m-%d')
        date_last = _datetime.strptime(data[0]['data']['windowLast'][:10],'%Y-%m-%d')
        dates_series = _pd.date_range(date_first, date_last, freq='1D')

        # Construct df of dates and time
        df_time = _pd.DataFrame(index = time_index, data = dates_series, columns=['Dates'])

        # Construct df of price or volume data
        df_data = _pd.DataFrame(data[1]['data'], columns = ['demo_index',column_name]).set_index('demo_index')

        # Merge the stuff
        ts = _pd.concat([df_time, df_data], axis=1).set_index('Dates').dropna()

        return ts
    
    # --------------------------------------------------------------------------------------------------------------
    def search_degiro(self, searchTerm, search_limit=30, product_type='All'):
    
        try:
            product_search_url = self.credentials['product_search_url']+self._SRCH_URL
            account = self.credentials['account_id']
            secID = self.credentials['session_id']
            search_url_base = product_search_url+account+'&sessionId='+secID

            if product_type == 'All':
                search_url = search_url_base+'&limit='+str(search_limit)+'&searchText='+searchTerm

            else:
                product_mapping = {'ETFs':'131','Stocks':'1'}
            
                search_url = search_url_base+'&productTypeId='+product_mapping[product_type]+\
                            '&limit='+str(search_limit)+'&searchText='+searchTerm

            search_results = _requests.get(search_url)
            return _json.loads(search_results.content)
            
        except Exception as e:
            print('Product search failed - ', e.args)