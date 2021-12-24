import dash_bootstrap_components as dbc
from dash import html
from ..utils import navbar, check_period
from ..hconn import data_port, data_cmx, data_wei_hist, data_wei_last, db
from ..cards import cards_plots as cp
from ..cards import cards_tables as ct
from dash.dependencies import Input, Output
from ..app import app

card_port_performance = cp.card_performance(data_port)
card_port_alloc_hist = cp.card_portfolio_alloc_hist(data_wei_hist)
card_port_alloc_last = cp.card_portfolio_alloc_last(data_wei_last)
card_port_risk = cp.card_risk(data_port, window=42)
card_port_var = cp.card_var(data_port, window=42, forward=21, conf=0.95)
card_port_esfall = cp.card_exp_shortfall(data_port, window=42, conf=0.95)
card_correl_matrix = cp.card_cmx(data_cmx)
card_correl_rolling = cp.card_correl(data_cmx, window=42, base='PORT', legend=True)
card_port_holdings = ct.card_table_portfolio_holdings_summary(db)

def create_layout_home():

    return html.Div([
                html.Div([navbar,

                # Performance and holdings
                dbc.Row([dbc.Col([card_port_performance],width=6, id='port_perf'),
                         dbc.Col([card_port_holdings],width=6)],class_name='p-4'),
                
                # Allocation
                dbc.Row([dbc.Col([card_port_alloc_hist],width=8),
                            dbc.Col([card_port_alloc_last],width=4)],class_name='p-4'),
                
                # Risk metrics
                dbc.Row([dbc.Col([card_port_risk],width=4,id='port_risk'),
                         dbc.Col([card_port_var],width=4,id='port_var'),
                         dbc.Col([card_port_esfall],width=4,id='port_esfall')],class_name='p-4'),

                # Correlation
                dbc.Row([dbc.Col([card_correl_matrix],width=6, id='port_cmx'),
                         dbc.Col([card_correl_rolling],width=6,id='port_correl')],class_name='p-4')
                
            ],className='my-page-container')

    ], className="page",
    )

layout_home = create_layout_home()

# ---------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------
# Portfolio performance graph
@app.callback(
    [Output('port_perf','children')],
    [Input('dropdown_time_period_port','value')]
)
def update_values(value):
    
    df = check_period(data=data_port, value=value)
    
    out = [cp.card_performance(df)]
    return out

# ---------------------
# Portfolio CMX graph
@app.callback(
    [Output('port_cmx','children')],
    [Input('dropdown_time_period_port','value')]
)
def update_values(value):
    
    df = check_period(data=data_cmx, value=value)
    
    out = [cp.card_cmx(df)]
    return out


# ---------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------
# Portfolio risk graph
@app.callback(
    [Output('port_risk','children')],
    [Input('slider_lookback_days_port','value')]
)
def update_values(value):
    out = [cp.card_risk(data_port, window=value)]
    return out

# ---------------------
# Portfolio value at risk graph
@app.callback(
    [Output('port_var','children')],
    [Input('slider_lookback_days_port','value'),
     Input('slider_forward_days_port','value')]
)
def update_values(value_window, value_forward):
    out = [cp.card_var(data_port, window=value_window, forward=value_forward, conf=0.95)]
    return out

# ---------------------
# Portfolio expected shortfall graph
@app.callback(
    [Output('port_esfall','children')],
    [Input('slider_lookback_days_port','value')]
)
def update_values(value):
    out = [cp.card_exp_shortfall(data_port, window=value, conf=0.95)]
    return out

# ---------------------
# Portfolio assets rolling correlation
@app.callback(
    [Output('port_correl','children')],
    [Input('slider_lookback_days_port','value')]
)
def update_values(value):
    out = [cp.card_correl(data_cmx, window=value, base='PORT', legend=True)]
    return out

# ---------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------
# Update lookback period
@app.callback(
[Output('lookback-period','children')],
[Input('slider_lookback_days_port','value')]
)
def update_lookback_label(value):
    marks={5:'1wk',10:'2wk',21:'1mo',45:'45d',63:'3mo',126:'6mo'}

    out = ['Lookback period - '+marks[value]]
    return out

# ---------------------
# Update forward period
@app.callback(
[Output('forward-period','children')],
[Input('slider_forward_days_port','value')]
)
def update_forward_label(value):
    marks={1:'1d',5:'1wk',21:'1mo',63:'3mo'}
    out = ['Forward period - '+marks[value]]
    return out

# ---------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------
