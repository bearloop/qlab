from datetime import datetime as _datetime
import dash_bootstrap_components as dbc
from dash import dcc, html

# --------------------------------------------------------------------------------------------------------------
def card_template(figure, card_title='Bla Bla', card_sub_title=''):

    return dbc.Card(
        [
            dbc.CardHeader(
                html.Div([html.H3(card_title,className="header-title"),
                html.P(card_sub_title,className="header-subtitle")])
                ),
            dbc.CardBody(
                [dcc.Graph(figure=figure, className='custom-chart',responsive=True)]
                )
        ], class_name="h-100"
    )

# --------------------------------------------------------------------------------------------------------------
def card_template_cmx(figure, card_title='Bla Bla', card_sub_title=''):

    return dbc.Card(
        [
            dbc.CardHeader(
                html.Div([html.H3(card_title,className="header-title"),
                html.P(card_sub_title,className="header-subtitle")])
                ),
            dbc.CardBody(
                [dcc.Graph(figure=figure, className='custom-chart-cmx',responsive=True)]
                )
        ], class_name="h-100"
    )

# --------------------------------------------------------------------------------------------------------------
def card_template_treemap(figure, card_title='Bla Bla', card_sub_title=''):

    return dbc.Card(
        [
            dbc.CardHeader(
                html.Div([html.H3(card_title,className="header-title"),
                html.P(card_sub_title,className="header-subtitle")])
                ),
            dbc.CardBody(
                [dcc.Graph(figure=figure, className='custom-chart-treemap',responsive=True)]
                )
        ]
    )
# --------------------------------------------------------------------------------------------------------------
def update_background(fig):

    return fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')

# --------------------------------------------------------------------------------------------------------------
def card_table(table, card_title='Bla Bla', card_sub_title=''):

    return dbc.Card(
        [
            dbc.CardHeader(
                html.Div([html.H3(card_title,className="header-title"),
                html.P(card_sub_title,className="header-subtitle")])
                ),
            dbc.CardBody(
                [table]
                )
        ], class_name="h-100"
    )

# --------------------------------------------------------------------------------------------------------------
def get_period(data):
     # Get period
    date1 = _datetime.strftime(data.dropna().index[0], '%Y-%m-%d')
    date2 = _datetime.strftime(data.dropna().index[-1], '%Y-%m-%d')
    period_range = str(date1)[:10] + ' - ' + str(date2)[:10]

    return period_range