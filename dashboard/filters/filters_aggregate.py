import dash_bootstrap_components as dbc
from dash import html
from .filters_dropdowns import dropdown_time_period_port
from .filters_sliders import slider_lookback_days_port, slider_forward_days_port
# --------------------------------------------------------------------------------------------------------------
# Links to new pages
pages_menu = html.Div([
          html.P('Dashboards',className="header-title-filters"),
          html.Hr(className='hr'),
          dbc.Nav(
            [
                dbc.NavLink("Portfolio View", href="/", active="exact"),
                dbc.NavLink("Assets Monitor", href="/layout-2", active="exact")
            ],
            vertical=True,
            pills=True,
        )],id='navigation-menu')

# --------------------------------------------------------------------------------------------------------------

port_view_filters= html.Div([
          html.P('Filters',className="header-title-filters"),
          html.Hr(className='hr'),
          dbc.CardBody([html.P('Date range',className="filters-p-class"),
                    dropdown_time_period_port],id='filters-card-body'),
          html.Hr(className='hr'),
          dbc.CardBody([html.P('Lookback period - ',className="filters-p-class", id='lookback-period'),
                    slider_lookback_days_port],id='filters-card-body-2'),
          html.Hr(className='hr'),
          dbc.CardBody([html.P('Forward period - ',className="filters-p-class", id='forward-period'),
                    slider_forward_days_port],id='filters-card-body-3'),
          html.Hr(className='hr'),          
],id='portfolio-view-filters')


# --------------------------------------------------------------------------------------------------------------


filters_tab_1 = [html.Div([pages_menu, port_view_filters],className='ko')]
filters_tab_2 = [html.Div([pages_menu],className='ko')]