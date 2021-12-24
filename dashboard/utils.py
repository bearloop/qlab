import dash_bootstrap_components as dbc
from dash import html
from .app import app
from dash.dependencies import Input, Output
from .filters.filters_aggregate import filters_tab_1, filters_tab_2
from ..analysis._utilities import _calc_ytd, _calc_mtd

# --------------------------------------------------------------------------------------------------------------
# Sidebar
sidebar = html.Div(
    filters_tab_1,
    style = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "1rem 1rem",
    "background-color": "#f8f9fa",
}, className='sidebar',id='sidebar-id'
)

# --------------------------------------------------------------------------------------------------------------

# Navbar
navbar = dbc.NavbarSimple(
    children=[sidebar],
    brand="Qlab Dashboard",
    brand_style={"font-size": "26px"},
    color="#495057",
    links_left=True,
    fixed="top",
    sticky="top",
    class_name="customNavBar")


# --------------------------------------------------------------------------------------------------------------

@app.callback(Output('sidebar-id', 'children'),
              Input('url', 'pathname')
            )
def display_page(pathname):

    if pathname == "/layout-2":
        return filters_tab_2
    else:
        return filters_tab_1


# --------------------------------------------------------------------------------------------------------------
def check_period(data, value):

    if value == 'inception':
        df = data.copy()
    elif value == 'ytd':
        ind = _calc_ytd(data.copy()).index[0]
        df = data.loc[ind:,:]
    elif value == 'mtd':
        ind = _calc_mtd(data.copy()).index[0]
        df = data.loc[ind:,:]
    elif value == '1yr':
        df = data.iloc[-252-1:,:]
    elif value == '6m':
        df = data.iloc[-126-1:,:]
    elif value == '3m':
        df = data.iloc[-63-1:,:]
    elif value == '1m':
        df = data.iloc[-21-1:,:]
    elif value == '1w':
        df = data.iloc[-5-1:,:]
    
    return df