import requests as _requests
import json as _json

class DeGiro():

    def __init__(self, user, psw):
        self.user = user
        self.psw = psw
        self._BASE_TRADER_URL = 'https://trader.degiro.nl'
        self._CONFIG_URL = self._BASE_TRADER_URL + '/login/secure/config'
        self._LOGIN_URL = self._BASE_TRADER_URL+'/login/secure/login'

    # --------------------------------------------------------------------------------------------------------------
    def login(self):
        
        product_search_url, account, userToken, config_data, secID = self._get_client_info()
        
        data_dct = {'product_search_url': product_search_url,
                    'account_id': account,
                    'user_token': userToken,
                    'config_data': config_data,
                    'session_id': secID}
        
        return data_dct
    
    # --------------------------------------------------------------------------------------------------------------

    def _get_client_info(self):
        
        try:
            config_data, secID = self._get_config_data()
            
            pa_url = config_data['data']['paUrl']
            
            url_client = pa_url+'client?sessionId='+secID
            
            product_search_url = config_data['data']['productSearchUrl']
            
            try:
                client_info = _requests.get(url_client)

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
                updConfig =  _requests.get(self._CONFIG_URL, headers = {'Cookie':'JSESSIONID='+secID+';'})
                
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
                                     headers = {'Content-Type': 'application/json'},
                                     json= {'username': self.user, 'password': self.psw} )

            secID = de_giro.headers['Set-Cookie'].split('JSESSIONID=')[1].split(';')[0]
            
            return secID
            
        except Exception as e:
            print('4 - session id', e.args)
            print('Session id fetch failed')