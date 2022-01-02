import datetime
from re import S
import dash_bootstrap_components as dbc
from dash import html
import pandas as pd
from ..utils import navbar
from ..hconn import pdt, data_assets_cum_ret, data_assets_ann_ret, data_assets_ann_vol
from ..cards import cards_plots as cp
from ..cards import cards_tables as ct
from dash.dependencies import Input, Output, State
from ..app import app
from ..filters.filters_dropdowns import dropdown_time_period_assets_options
from datetime import datetime, timedelta


card_assets_treemap = cp.card_treemap(data_assets_cum_ret, sort_by='1-wk')
card_assets_barchart = cp.card_barchart(data_assets_cum_ret, sort_by='1-wk')

card_assets_performance = cp.card_performance(pdt['SWDA'],
                                              card_title='Assets Performance',
                                              dropna=True, legend=True)

card_assets_risk = cp.card_risk(pdt['SWDA'], card_title='Assets Risk Annualised',
                                window=63, dropna=True, legend=True)

# card_assets_beta = cp.card_beta(pdt['SWDA'], card_title='Assets Risk Annualised',
#                                 window=63, dropna=True, legend=True)

card_assets_kde = cp.card_histogram(pdt['SWDA'], normal=False, normal_label=None, card_title='Asset Returns KDE', legend=True)


card_assets_ddown = cp.card_drawdown(pdt['SWDA'], dropna=True, legend=True)

card_assets_info = ct.card_table_assets_stats(assets_list=['SWDA'])

def create_layout_2():

    return html.Div([
                html.Div([navbar,
                
                # Assets Treemap
                dbc.Row([dbc.Col([card_assets_treemap], width=12, id='assets_treemap')], class_name='p-4'),

                # Assets Barchart
                dbc.Row([dbc.Col([card_assets_barchart], width=12, id='assets_barchart')], class_name='p-4'),

                # Performance and risk
                dbc.Row([dbc.Col([card_assets_performance],width=6, id='assets_perf'),
                         dbc.Col([card_assets_risk],width=6, id='assets_risk')],class_name='p-4'),
                
                # Drawdown
                dbc.Row([dbc.Col([card_assets_ddown],width=12, id='assets_ddown')],class_name='p-4'),

                # Histogram
                dbc.Row([dbc.Col([card_assets_kde],width=6, id='assets_hist')],class_name='p-4'),

                # Asset stats table
                dbc.Row([dbc.Col([card_assets_info],width=12, id='assets_info')],class_name='p-4'),

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
def update_calc_method(value):
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



# ---------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------
# Update performance chart
@app.callback(
    [Output('assets_perf','children')],
    [Input("dropdown_securities_list", "value"),
     Input("date-picker-range", "end_date"),
     Input("date-picker-range", "start_date")]
)
def update_values(value, eop, sop):
    try:
        df = custom_dates(start=sop,end=eop,asset_list=value)
        out = [cp.card_performance(df, card_title='Assets Performance', legend=True)]
        return out
    except Exception as e:
        print('Failed attempt to update list (line plot)', e.args)
        out = [cp.card_performance(None, card_title='Assets Performance')]
        return out

# -------------------
# Update risk chart
@app.callback(
    [Output('assets_risk','children')],
    [Input("dropdown_securities_list", "value"),
     Input("date-picker-range", "end_date"),
     Input("date-picker-range", "start_date")]
)
def update_values(value, eop, sop):
    try:
        df = custom_dates(start=sop,end=eop,asset_list=value)
        out = [cp.card_risk(df, card_title='Assets Risk Annualised', window=63, legend=True)]
        return out
    except Exception as e:
        print('Failed attempt to update list (vol plot)', e.args)
        out = [cp.card_risk(None, card_title='Assets Risk Annualised')]
        return out

# -------------------
# Update hist chart
@app.callback(
    [Output('assets_hist','children')],
    [Input("dropdown_securities_list", "value"),
     Input("date-picker-range", "end_date"),
     Input("date-picker-range", "start_date")]
)
def update_values(value, eop, sop):
    try:
        df = custom_dates(start=sop,end=eop,asset_list=value)
        out = [cp.card_histogram(df, normal=False, normal_label=None, card_title='Asset Returns KDE', legend=True)]
        return out
    except Exception as e:
        print('Failed attempt to update list (histogram plot)', e.args)
        out = [cp.card_histogram(None, normal=False, normal_label=None, card_title='Asset Returns KDE')]
        return out

# -------------------
# Update drawdown chart
@app.callback(
    [Output('assets_ddown','children')],
    [Input("dropdown_securities_list", "value"),
     Input("date-picker-range", "end_date"),
     Input("date-picker-range", "start_date")]
)
def update_values(value, eop, sop):
    try:
        df = custom_dates(start=sop,end=eop,asset_list=value)
        out = [cp.card_drawdown(df, legend=True)]
        return out
    except Exception as e:
        print('Failed attempt to update list (drawdown plot)', e.args)
        out = [cp.card_drawdown(None)]
        return out

# -------------------
# Update assets info table
@app.callback(
    [Output('assets_info','children')],
    [Input("dropdown_securities_list", "value"),
     Input("date-picker-range", "end_date"),
     Input("date-picker-range", "start_date")]
)
def update_values(value, eop, sop):
    try:
        out = [ct.card_table_assets_stats(assets_list=value,start_date=sop,end_date=eop)]
        return out
    except Exception as e:
        print('Failed attempt to update list (assets table stats)', e.args)
        out = [ct.card_table_assets_stats(assets_list=None)]
        return out

# ---------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------
# Modal securities functionality
@app.callback(
    Output("modal-securities", "is_open"),
    [Input("modal-button-open", "n_clicks"),
     Input("modal-button-close", "n_clicks")],
    [State("modal-securities", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


# ---------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------
# Max min dates allowed for date picker
@app.callback(
    [Output("date-picker-range", "max_date_allowed"),
     Output("date-picker-range", "end_date"),
     Output("date-picker-range", "min_date_allowed"),
     Output("date-picker-range", "start_date")],
    [Input("dropdown_securities_list", "value")],
)
def set_date_range_for_securities(value):
    
    try:
        ind = pdt[value].dropna(how='all').index
        start_date = ind[0]
        end_date = ind[-1]
        # print('entered set date range - success', value)
        # return max allowed and end date + min allowed and start date
        return end_date, end_date, start_date, start_date
    except:
        start_date = datetime.today() - timedelta(days=21)
        end_date = datetime.today()
        # print('entered set date range - failure', value)
        return end_date, end_date, start_date, start_date



# ---------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------
def custom_dates(start, end, asset_list):
    try:
        
        df = pd.DataFrame(pdt[asset_list].dropna(how='all')).loc[start:end,:].copy()
        # print('entered custom date range - success')
        return df
    except Exception as e:
        # print('entered custom date range - failure')
        # print('Failed attempt to change date range', e.args, start, end, asset_list)
        return pdt[asset_list].dropna(how='all')