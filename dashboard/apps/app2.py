import dash_bootstrap_components as dbc
from dash import html
from ..utils import navbar
from ..hconn import data_assets_cum_ret, data_assets_ann_ret, data_assets_ann_vol
from ..cards import cards_plots as cp
from dash.dependencies import Input, Output
from ..app import app
from ..filters.filters_dropdowns import dropdown_time_period_assets_options

card_assets_treemap = cp.card_treemap(data_assets_cum_ret, sort_by='1-wk')
card_assets_barchart = cp.card_barchart(data_assets_cum_ret, sort_by='1-wk')


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
    [Input('dropdown_time_period_assets','value'),
     Input('slider_monitor_type_port','value')]
)
def update_values(dropdown_value, slider_value):
    df = which_dataset(slider_value=slider_value)

    if slider_value == 30:
        # slider_value=30 -> vol calculation
        reverse=True
        midpoint=0.07 # set 7% as vol benchmark
    else:
        # slider_value=10 or 20 -> returns calculation
        reverse = False
        midpoint=0
    
    out = [cp.card_treemap(df, sort_by=dropdown_value, reverse=reverse, midpoint=midpoint)]
    return out


# ---------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------
# Assets barchart
@app.callback(
    [Output('assets_barchart','children')],
    [Input('dropdown_time_period_assets','value'),
     Input('slider_monitor_type_port','value')]
)
def update_values(dropdown_value, slider_value):
    df = which_dataset(slider_value=slider_value)
    out = [cp.card_barchart(df, sort_by=dropdown_value)]
    return out


# ---------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------
# Update Calculation type
@app.callback(
[Output('calculation-type','children')],
[Input('slider_monitor_type_port','value')]
)
def update_forward_label(value):
    marks={10:'Period Ret',20:'Ann. Ret',30:'Ann. Vol'}
    out = ['Method - '+marks[value]]
    return out

# ---------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------
# Adjust Dropdown filter according to Slider type of calculation
@app.callback(
    [Output('dropdown_time_period_assets','options'),
     Output('dropdown_time_period_assets','value')],
    [Input('slider_monitor_type_port','value'),
     Input('dropdown_time_period_assets','value')]
)
def update_values(slider_value, dropdown_value):
    if slider_value > 10:
        # exclude last two values representing 1-day and 1-week periods
        options=dropdown_time_period_assets_options[:-2]
        if dropdown_value in ['1-day','1-wk']:
            dropdown_value='1-mo'
    else:
        options=dropdown_time_period_assets_options

    return options, dropdown_value

# ---------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------
# Figure out which dataset to use
def which_dataset(slider_value):
    if slider_value == 10:
        df = data_assets_cum_ret.copy()
    elif slider_value == 20:
        df = data_assets_ann_ret.copy()
    elif slider_value == 30:
        df = data_assets_ann_vol.copy()
    return df