from dash import dcc


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
