from dash import dcc
import dash_bootstrap_components as dbc
from ..hconn import sec_list

# --------------------------------------------------------------------------------------------------------------
dropdown_time_period_port = dcc.Dropdown(options=[
                                {'label': 'Since inception', 'value': 'inception'},
                                {'label': 'Year-to-date', 'value': 'ytd'},
                                {'label': 'Month-to-date', 'value': 'mtd'},
                                {'label': '1 year', 'value': '1yr'},
                                {'label': '6 months', 'value': '6m'},
                                {'label': '3 months', 'value': '3m'},
                                {'label': '1 month', 'value': '1m'},
                                {'label': '1 week', 'value': '1w'}
                            ],value='inception',
                            multi=False,clearable=False,id='dropdown_time_period_port'
                        )

# --------------------------------------------------------------------------------------------------------------
dropdown_time_period_assets_options = [
                                {'label': 'Year-to-date', 'value': 'YtD'},
                                {'label': 'Month-to-date', 'value': 'MtD'},
                                {'label': '1 year', 'value': '1-yr'},
                                {'label': '3 months', 'value': '3-mo'},
                                {'label': '1 month', 'value': '1-mo'},
                                {'label': '1 week', 'value': '1-wk'},
                                {'label': '1 day', 'value': '1-day'}
                            ]
dropdown_time_period_assets = dcc.Dropdown(options=dropdown_time_period_assets_options,
                                           value='1-wk',multi=False,clearable=False,
                                           id='dropdown_time_period_assets'
                        )

# --------------------------------------------------------------------------------------------------------------

dropdown_securities_list_options = list(map(lambda x: {'label': x[1][0] + ': ' + x[1][1], 'value': x[1][0]}, 
                                            sec_list.sort_values(by='symbol').iterrows()))


dropdown_securities_list = dcc.Dropdown(options=dropdown_securities_list_options,value='SWDA',
                                        multi=True,clearable=True,searchable=True,id='dropdown_securities_list'
                                        )

checklist_securities_list = dbc.Checklist(options=dropdown_securities_list_options,
                                          value=['SWDA'],id='checklist_securities_list')