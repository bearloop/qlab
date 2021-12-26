import dash_bootstrap_components as dbc
from dash import html
from ..utils import navbar
from ..hconn import data_assets
from ..cards import cards_plots as cp
from dash.dependencies import Input, Output
from ..app import app


card_assets_treemap = cp.card_treemap(data_assets, sort_by='1-wk')
card_assets_barchart = cp.card_barchart(data_assets, sort_by='1-wk')


def create_layout_2():

    return html.Div([
                html.Div([navbar,

                # Assets Treemap
                dbc.Row([dbc.Col([card_assets_treemap], width=12, id='assets_treemap')], class_name='p-4'),

                # Assets Barchart
                dbc.Row([dbc.Col([card_assets_barchart], width=12, id='assets_barchart')], class_name='p-4')

            ],className='my-page-container')

    ], className="page",
    )

layout_2 = create_layout_2()



# ---------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------
# Assets treemap
@app.callback(
    [Output('assets_treemap','children')],
    [Input('dropdown_time_period_assets','value')]
)
def update_values(value):
    
    out = [cp.card_treemap(data_assets, sort_by=value)]
    return out

# ---------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------
# Assets barchart
@app.callback(
    [Output('assets_barchart','children')],
    [Input('dropdown_time_period_assets','value')]
)
def update_values(value):
    
    out = [cp.card_barchart(data_assets, sort_by=value)]
    return out

# ---------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------