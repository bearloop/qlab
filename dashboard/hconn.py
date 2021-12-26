import pandas as pd
from dotenv import load_dotenv
import os
from ..analysis import HerokuDB
from ..analysis import  Portfolio
from ..analysis import calc_cumulative_ret
# Load dot env file
load_dotenv(dotenv_path=os.getcwd()+'/qlab/.env')

# Connect to Heroku PostgreSQL
db = HerokuDB(os.environ.get("HERO_URI"))

db.connect()

# --------------------------------------------------------------------------------------------------------------
data_port = pd.DataFrame(Portfolio(db).fetch_data()['PORT'])

data_wei_hist = Portfolio(db).fetch_weights_history()
data_wei_last = Portfolio(db).fetch_weights_last()

assets = ['PORT'] + list(data_wei_last.index)
data_cmx = db.prices_table_read(assets_list=assets).loc['2020-03-25':]

pdt = db.prices_table_read()
data_assets = calc_cumulative_ret(pdt, db=db)

