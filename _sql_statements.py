# CREATE TABLES
sql_prices_table_create = """
                          CREATE TABLE IF NOT EXISTS prices (
                              symbol text NOT NULL PRIMARY KEY,
                              data text NOT NULL)
                           """

sql_transactions_table_create = """
                                CREATE TABLE IF NOT EXISTS transactions(
                                   id integer NOT NULL PRIMARY KEY,
                                   symbol varchar NOT NULL,
                                   transaction_price numeric NOT NULL,
                                   transaction_quantity integer NOT NULL,
                                   transaction_type varchar NOT NULL,
                                   transaction_date varchar NOT NULL)
                                """

sql_securities_table_create = """
                          CREATE TABLE IF NOT EXISTS securities(
                              dg_id varchar NOT NULL PRIMARY KEY,
                              name varchar NOT NULL,
                              isin varchar NOT NULL,
                              vwd_id varchar,
                              symbol varchar NOT NULL,
                              product_type varchar,
                              prod_type_id varchar,
                              currency varchar NOT NULL,
                              exchange_id varchar NOT NULL,
                              vwd_id_secondary varchar)
                           """


sql_exchanges_table_create = """
                         CREATE TABLE IF NOT EXISTS exchanges(
                              exchange_id varchar NOT NULL PRIMARY KEY,
                              exchange_code varchar NOT NULL,
                              exchange_country varchar,
                              exchange_city varchar,
                              exchange_name varchar)
                         """


sql_fin_times_table_create = """
                         CREATE TABLE IF NOT EXISTS ft_exchanges(
                              exchange_id varchar NOT NULL PRIMARY KEY,
                              exchange_code varchar NOT NULL,
                              ft_exch_code varchar NOT NULL)
                         """


sql_etfs_data_table_create = """
                         CREATE TABLE IF NOT EXISTS etfs_data (
                              ft_symbol varchar NOT NULL PRIMARY KEY,
                              isin varchar,
                              aum varchar,
                              exp_ratio varchar,
                              ft_currency varchar,
                              domicile varchar,
                              launch_date varchar,
                              sec_technology varchar,
                              sec_financials varchar,
                              sec_healthcare varchar,
                              sec_cyclicals varchar,
                              sec_industrials varchar,
                              sec_communications varchar,
                              sec_defensives varchar,
                              sec_materials varchar,
                              sec_energy varchar,
                              non_equities varchar,
                              sec_other varchar,
                              bottom_90 varchar,
                              top_10 varchar)
                         """


# ------------------------------------------------------------------------------------------
# DROP TABLES
sql_prices_table_drop = """DROP TABLE IF EXISTS prices"""

sql_transactions_table_drop = """DROP TABLE IF EXISTS transactions"""

sql_securities_table_drop = """DROP TABLE IF EXISTS securities"""

sql_exchanges_table_drop = """DROP TABLE IF EXISTS exchanges"""

sql_ft_exchanges_table_drop = """DROP TABLE IF EXISTS ft_exchanges"""

sql_etfs_data_table_drop = """DROP TABLE IF EXISTS etfs_data"""



# ------------------------------------------------------------------------------------------
# INSERT RECORDS
sql_prices_insert_query = """
                        INSERT INTO prices (
                             symbol,
                             data)
                             VALUES (%s, %s)
                             ON CONFLICT (symbol)
                                 DO UPDATE SET data = EXCLUDED.data
                        """

sql_transactions_insert_query = """
                        INSERT INTO transactions (
                                 id,
                                 symbol,
                                 transaction_price,
                                 transaction_quantity,
                                 transaction_type,
                                 transaction_date)
                                 VALUES (%s, %s, %s, %s, %s, %s)
                                 ON CONFLICT (id)
                                     DO UPDATE SET symbol = EXCLUDED.symbol,
                                                   transaction_price = EXCLUDED.transaction_price,
                                                   transaction_quantity = EXCLUDED.transaction_quantity,
                                                   transaction_type = EXCLUDED.transaction_quantity,
                                                   transaction_date = EXCLUDED.transaction_date
                        """

sql_security_insert_query = """
                        INSERT INTO securities (
                             dg_id,
                             name,
                             isin,
                             vwd_id,
                             symbol,
                             product_type,
                             prod_type_id,
                             currency,
                             exchange_id,
                             vwd_id_secondary)
                             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                             ON CONFLICT (dg_id)
                             DO NOTHING
                        """


sql_exchange_insert_query = """
                        INSERT INTO exchanges (
                             exchange_id,
                             exchange_code,
                             exchange_country,
                             exchange_city,
                             exchange_name)
                             VALUES (%s, %s, %s, %s, %s)
                             ON CONFLICT (exchange_id)
                                 DO UPDATE SET exchange_code = EXCLUDED.exchange_code,
                                               exchange_country = EXCLUDED.exchange_country,
                                               exchange_city = EXCLUDED.exchange_city,
                                               exchange_name = EXCLUDED.exchange_name
                        """


sql_ft_exchange_insert_query = """
                           INSERT INTO ft_exchanges (
                                 exchange_id,
                                 exchange_code,
                                 ft_exch_code)
                                 VALUES (%s, %s, %s)
                                 ON CONFLICT (exchange_id)
                                     DO UPDATE SET exchange_code = EXCLUDED.exchange_code,
                                                   ft_exch_code = EXCLUDED.ft_exch_code
                            """


sql_etfs_data_insert_query = """
                        INSERT INTO etfs_data (
                              ft_symbol,
                              isin,
                              aum,
                              exp_ratio,
                              ft_currency,
                              domicile,
                              launch_date,
                              sec_technology,
                              sec_financials,
                              sec_healthcare,
                              sec_cyclicals,
                              sec_industrials,
                              sec_communications,
                              sec_defensives,
                              sec_materials,
                              sec_energy,
                              non_equities,
                              sec_other,
                              bottom_90,
                              top_10)
                             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                             ON CONFLICT (ft_symbol)
                                 DO UPDATE SET isin = EXCLUDED.isin,
                                               aum = EXCLUDED.aum,
                                               exp_ratio = EXCLUDED.exp_ratio,
                                               ft_currency = EXCLUDED.ft_currency,
                                               domicile = EXCLUDED.domicile,
                                               launch_date = EXCLUDED.launch_date,
                                               sec_technology = EXCLUDED.sec_technology,
                                               sec_financials = EXCLUDED.sec_financials,
                                               sec_healthcare = EXCLUDED.sec_healthcare,
                                               sec_cyclicals = EXCLUDED.sec_cyclicals,
                                               sec_industrials = EXCLUDED.sec_industrials,
                                               sec_communications = EXCLUDED.sec_communications,
                                               sec_defensives = EXCLUDED.sec_defensives,
                                               sec_materials = EXCLUDED.sec_materials,
                                               sec_energy = EXCLUDED.sec_energy,
                                               non_equities = EXCLUDED.non_equities,
                                               sec_other = EXCLUDED.sec_other,
                                               bottom_90 = EXCLUDED.bottom_90,
                                               top_10 = EXCLUDED.top_10
                        """

# ------------------------------------------------------------------------------------------
# DELETE RECORDS
sql_prices_delete_query = """
                           DELETE FROM prices WHERE symbol = %s
                           """

sql_transactions_delete_query = """
                           DELETE FROM transactions WHERE id = %s
                           """

sql_ft_exchange_delete_query = """
                           DELETE FROM ft_exchanges WHERE exchange_id = %s
                           """

sql_exchange_delete_query = """
                        DELETE FROM exchanges WHERE exchange_id = %s
                        """

sql_security_delete_query = """
                        DELETE FROM securities WHERE dg_id = %s
                        """

sql_etf_data_delete_query = """
                        DELETE FROM etf_data WHERE ft_symbol = %s
                        """
# ------------------------------------------------------------------------------------------
# JOINS
sql_join_3 = """
        SELECT securities.exchange_id, isin, currency, symbol, product_type, ft_exchanges.exchange_code, ft_exch_code
        FROM ((securities
        INNER JOIN exchanges ON securities.exchange_id=exchanges.exchange_id)
        INNER JOIN ft_exchanges ON securities.exchange_id=ft_exchanges.exchange_id)
        WHERE product_type='ETF';
        """