import psycopg2 as _psycopg2
import pandas as _pd
import requests as _requests
from ._ft_market_data import ft_aggregate, ft_summary, ft_sectors, ft_securities
from ._sql_statements import *
from ._utilities import _convert_df_to_str, _convert_str_to_df
from ._portfolio import Portfolio

class HerokuDB:
    
    def __init__(self, uri, local_mode=False):
        self.uri = uri
        self._conn = None
        self._cur = None
        self.url = 'https://trader.degiro.nl/product_search/config/dictionary'
        self.local_mode = local_mode
    
    # --------------------------------------------------------------------------------------------
    def connect(self):
        '''
        Connect to herokuDB based on the provided uri. Return connection and cursor.
        '''
        try:
            if self.local_mode:
                self._conn = _psycopg2.connect(self.uri)

            else:
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
    def clean_degiro_search(self, search_results):
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
                self.execute_sql("""SELECT COUNT(*) FROM {}""".format(table[0]))
                print('Table: ', table[0], '--- rows:', str(self.fetch().iloc[0][0]))
        
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
    def prices_table_update_auto(self, period='P1M', dg=None, assets_list=None):
        """
        Retrieves time series data and adds them to the prices table. If there is an assets list, only these assets are updated.
        """

        if assets_list is None:
            # Retrieve vwd ids / symbols from securities tables
            self.execute_sql("SELECT vwd_id, symbol FROM securities WHERE product_type = 'ETF' ")
            
            # Pass the ids / symbols to get price time series
            data = dg.comp_series(securities=dg._securities_dict(self.fetch()),
                            ts_type='price',
                            date_range={'auto':period})
            
            # Update the prices table using the prices data from degiro
            self.prices_table_update_manual(df=data.copy())
        
        else:
            for asset in assets_list:
                # Retrieve vwd ids / symbols from securities tables
                self.execute_sql("SELECT vwd_id, symbol FROM securities WHERE symbol = '{}' ".format(asset))

                # Pass the ids / symbols to get price time series
                data = dg.comp_series(securities=dg._securities_dict(self.fetch()),
                                ts_type='price',
                                date_range={'auto':period})
                
                # Update the prices table using the prices data from degiro
                self.prices_table_update_manual(df=data.copy())

    # --------------------------------------------------------------------------------------------
    def prices_table_update_manual(self, df):
        """ """
        for asset in df.columns:

            # First read existing data:
            try:
                # if asset is in table you'll be able to read
                existing_data = self.prices_table_read(assets_list=[asset])
            except:
                # Otherwise pass an empty df back
                existing_data = _pd.DataFrame()

            # Then use combine_first to upsert data to existing df
            df_combined = _pd.DataFrame(df[asset]).combine_first(existing_data)

            # ..and convert the combined df to string
            prices_as_string = _convert_df_to_str(df_combined, column=asset)

            # Finally save the string to the table
            self.execute_sql(query = sql_prices_insert_query, data=(asset, prices_as_string))
    
    # --------------------------------------------------------------------------------------------
    def _read_price_time_series_data(self, assets_list=None, portfolio=True):
        """ """
        try:
            if assets_list is None:
                # Use all available symbols in the prices table
                query = 'SELECT * FROM prices'

            else:
                # Use the passed list to filter the prices table
                if len(assets_list) == 1:
                    query = "SELECT * FROM prices WHERE symbol = '{}'".format(assets_list[0])
                else:
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
    
    # --------------------------------------------------------------------------------------------
    def prices_table_read(self, assets_list=None, portfolio=True):

        results = self._read_price_time_series_data(assets_list=assets_list, portfolio=portfolio)

        if portfolio:
                port = Portfolio(heroku_conn=self).fetch_data()
                results = _pd.concat([results, port['PORT']],axis=1)
        
        return results.ffill()

    # --------------------------------------------------------------------------------------------
    def insert_new_asset(self, dg_search_result=None, asset=None, asset_segment=None, ft_suffix=None, dg=None):
        """Provide all 5 arguments to call this functions"""
        if all(i is not None for i in [dg_search_result, asset, asset_segment, ft_suffix, dg]):
            
            # Insert new security to <<securities>> table
            self.execute_sql(sql_security_insert_query,
                             self.clean_degiro_search(dg_search_result))

            # Insert segment for new security to <<market_segments>> table
            self.execute_sql(sql_market_segments_insert_query,(asset,asset_segment))

            # Insert price time series data to <<prices>> table
            self.prices_table_update_auto(period='P50Y',dg=dg, assets_list=[asset])

            # Scrap FT data and add to <<etfs_data>> table
            self.load_ft_funds_data(etfs_list=[asset+':'+ft_suffix])

        else:
            print('Insert every argument to proceed.')
    
    # --------------------------------------------------------------------------------------------
    def market_segments_info(self):

        self.execute_sql("""SELECT securities.symbol, name, segment
                            FROM securities
                            JOIN market_segments
                            ON securities.symbol=market_segments.symbol""")
        ms = self.fetch()
        ms.index = ms.symbol
        ms.loc['PORT',:] = ['PORT','Portfolio','Portfolio']

        return ms
    
    # --------------------------------------------------------------------------------------------