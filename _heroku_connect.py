import psycopg2 as _psycopg2
import pandas as _pd
import requests as _requests
from ._ft_market_data import ft_aggregate, ft_summary, ft_sectors, ft_securities
from ._sql_statements import *
from ._utilities import _convert_df_to_str, _convert_str_to_df
 
class HerokuDB:
    
    def __init__(self, uri):
        self.uri = uri
        self._conn = None
        self._cur = None
        self.url = 'https://trader.degiro.nl/product_search/config/dictionary'
    
    # --------------------------------------------------------------------------------------------
    def connect(self):
        '''
        Connect to herokuDB based on the provided uri. Return connection and cursor.
        '''
        try:
            self._conn = _psycopg2.connect(self.uri, sslmode='require')
            self._conn.set_session(autocommit=True)
            self._cur = self._conn.cursor()
            print('Connected to DB, cursor is created')
            
        except Exception as e:
            print(e.args)
    
    # --------------------------------------------------------------------------------------------
    def close(self):
        '''
        Close connection to herokuDB.
        '''
        try:
            if self._conn != None:
                self._conn.close()
                # Update conn and cur as connection is now closed
                self._conn, self._cur = None, None 
                print('Connection closed')
            else:
                print('No connection is available')
                
        except Exception as e:
            print(e.args)
            
    # --------------------------------------------------------------------------------------------
    def execute_sql(self,query,data=None):
        '''
        Execute an sql query. Data must be a tuple, e.g. (value,) or (value_1, value_2).
        '''
        try:
            if self._cur != None:
                self._cur.execute(query,data)
                print('Query executed', end = "\r")
            else:
                print('Cursor is not available')
            
        except Exception as e:
            print(e.args)
            
    # --------------------------------------------------------------------------------------------
    def clean_dgiro_dict(self, search_results):
        """
        Return a cleaned dictionary.
        """
        if 'vwdIdSecondary' not in search_results:
            search_results['vwdIdSecondary'] = -1

        if 'vwdId' not in search_results:
            search_results['vwdId'] = -1


        clean_data = (search_results['id'],search_results['name'],search_results['isin'],\
                      search_results['vwdId'],search_results['symbol'],search_results['productType'],\
                      search_results['productTypeId'],search_results['currency'],\
                      search_results['exchangeId'],search_results['vwdIdSecondary'])

        return clean_data
    
    # --------------------------------------------------------------------------------------------
    def fetch(self,index_name=None,limit=10000):
        """Fetch table data as Pandas DataFrame."""
        try:
            records = self._cur.fetchmany(limit)
            
            col_names = [elt[0] for elt in self._cur.description]
            
            if index_name is None:
                return _pd.DataFrame(records, columns = col_names)
            
            else:
                return _pd.DataFrame(records, columns = col_names).set_index(index_name)
        
        except Exception as e:
            print(e.args)
   
    # --------------------------------------------------------------------------------------------
    def print_tables(self):
        """Print database table names."""
        try:
            sql_print_tables_query = ("""
                                      SELECT table_name
                                      FROM information_schema.tables
                                      WHERE table_schema = 'public'
                                  """)
            self.execute_sql(query=sql_print_tables_query,data=None)
            
            for table in self._cur.fetchall():
                print('Table: ', table[0])
        
        except Exception as e:
            print(e.args)
     
    # --------------------------------------------------------------------------------------------
    def load_dg_exchange_ids(self):
        """
        Uses a url link to load exchanges details to a table. You should run this only once.
        """
        self.execute_sql(query=sql_exchanges_table_create,data=None)
        res = _requests.get(self.url).json()
        
        for e in res['exchanges']:
            d = {}
            for item in ['id','hiqAbbr','country','city','name']:
                try: d[item] = e[item]
                except: d[item] = '-1'

            exchange_details = (d['id'], d['hiqAbbr'], d['country'], d['city'], d['name'])
            self.execute_sql(query=sql_exchange_insert_query,data=exchange_details)
    
    # --------------------------------------------------------------------------------------------
    def load_ft_funds_data(self, etfs_list=None):
        """ """
        
        if etfs_list is None:
            
            # Join tables to read FT funds codes
            self.execute_sql(sql_join_3)
            joined_df = self.fetch(index_name='exchange_id')

            # Create list of funds to get FT data for
            etfs_list = list(map(lambda x: x[0]+':'+x[1]+':'+x[2], joined_df[['symbol','ft_exch_code','currency']].values))

        # Read data from FT site
        funds_data = ft_aggregate(etfs_list).T.fillna(0)
        
        # Index to column, erm in the right order
        funds_data['index'] = funds_data.index
        funds_data = _pd.concat([funds_data['index'],
                                 funds_data.drop(['index'],axis=1)] ,axis=1)
        
        # Create or update relevant DB TABLE (etfs_data)
        self.execute_sql(query=sql_etfs_data_table_create)
        
        # Add row to table (first convert all the data to type string)
        for etf in etfs_list:
            
            self.execute_sql(query=sql_etfs_data_insert_query,
                             data=tuple(funds_data.loc[etf].astype(str)) )
        
    # --------------------------------------------------------------------------------------------
    def prices_table_update(self, df):
        """ """
        for asset in df.columns:
            prices_as_string = _convert_df_to_str(df, column=asset)
            self.execute_sql(query = sql_prices_insert_query, data=(asset, prices_as_string))
    
    # --------------------------------------------------------------------------------------------
    def prices_table_read(self, assets_list=None):
        """ """
        try:
            if assets_list is None:
                # Use all available symbols in the prices table
                query = 'SELECT * FROM prices'

            else:
                # Use the passed list to filter the prices table
                query = "SELECT * FROM prices WHERE symbol IN {}".format(tuple(assets_list))
            
            # Fetch data and create a data frame
            self.execute_sql(query=query)
            df = self.fetch()
            df = df.set_index('symbol').T

            results = _pd.DataFrame()

            # Unpack data and move them to a dataframe
            for asset in df.columns:
                values = df.loc['data',asset]
                prices_as_df = _convert_str_to_df(values, asset)
                results = _pd.concat([results,prices_as_df],axis=1)

            return results
        except Exception as e:
            print(e.args)