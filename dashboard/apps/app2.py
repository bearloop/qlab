import dash_bootstrap_components as dbc
from dash import html
from ..utils import navbar
from ..hconn import data_port, data_cmx, data_wei_hist, data_wei_last
from ..cards import cards_plots as cp

# card_port_performance = cp.card_performance(data_port)
# card_port_alloc_hist = cp.card_portfolio_alloc_hist(data_wei_hist)
# card_port_alloc_last = cp.card_portfolio_alloc_last(data_wei_last)
# card_port_risk = cp.card_risk(data_port, window=21)
# card_port_var = cp.card_var(data_port, window=21, forward=21, conf=0.95)
# card_port_esfall = cp.card_exp_shortfall(data_port, window=21, conf=0.95)
# card_correl_matrix = cp.card_cmx(data_cmx)


def create_layout_2():

    return html.Div([
                html.Div([navbar,
                

            ],className='my-page-container')

    ], className="page",
    )

layout_2 = create_layout_2()