import pandas as pd
from dotenv import load_dotenv
import os
from ..analysis import HerokuDB
from ..analysis import  Portfolio
from ..analysis import calc_cumulative_ret, calc_annualised_ret, calc_annualised_vol
# Load dot env file
load_dotenv(dotenv_path=os.getcwd()+'/qlab/.env')

# Connect to Heroku PostgreSQL
db = HerokuDB(os.environ.get("LOCAL_URI"), local_mode=True)

db.connect()

# --------------------------------------------------------------------------------------------------------------
# All time series
pdt = db.prices_table_read()

# Portfolio view: price time series and weights
data_port = pd.DataFrame(Portfolio(db).fetch_data()['PORT'])
data_wei_hist = Portfolio(db).fetch_weights_history()
data_wei_last = Portfolio(db).fetch_weights_last()

# Portfolio view: Correlation data
assets = ['PORT'] + list(data_wei_last.index)
data_cmx = pdt[assets].loc['2020-03-25':]
# data_cmx = db.prices_table_read(assets_list=assets).loc['2020-03-25':]

# Assets view: Monitor data
data_assets_cum_ret = calc_cumulative_ret(pdt, db=db)
data_assets_ann_ret = calc_annualised_ret(pdt, db=db)
data_assets_ann_vol = calc_annualised_vol(pdt, db=db)

# Assets view
def _sec_list(db):
    db.execute_sql("SELECT symbol, name FROM securities WHERE product_type='ETF' ORDER BY name ASC")
    df = db.fetch()
    return df

sec_list = _sec_list(db=db)


