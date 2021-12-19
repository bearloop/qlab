# from dotenv import load_dotenv
# import os
from ...analysis import _visuals as vs
import dash_bootstrap_components as dbc
from dash import dcc, html
from ..utils import navbar, db

# # Load dot env file
# load_dotenv(dotenv_path=os.getcwd()+'/qlab/.env')

# # Connect to Heroku PostgreSQL
# db = HerokuDB(os.environ.get("HERO_URI"))
# db.connect()

db.connect()
print('Start', db)
pdt = db.prices_table_read(assets_list=['SWDA','EIMI','EXXT','RBOT','QDVG','QDVE'])
db.close()
print('End', db)

assets_ls = ['PORT'] + ['SWDA','EIMI','EXXT','RBOT','QDVG','QDVE']
data = pdt.loc['2020-03-25':,assets_ls].copy().ffill()

fig_line = vs.plot_line(data,rebase=True, chart_title='', legend=True, to_return=True
                    ).update_layout(paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)')

fig_ddown = vs.plot_ddown(data, chart_title='', legend=True, to_return=True
                    ).update_layout(paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)')


card = dbc.Card(
    [
         dbc.CardHeader(
            html.Div([html.H3('Historical Performance',className="header-title"),
            html.P('--I am a coder--',className="header-subtitle")])
            ),
        dbc.CardBody(
            [dcc.Graph(figure=fig_line,className='custom-chart',responsive=True)]
            )
       
    ],
)

card2 = dbc.Card(
    [
        dbc.CardFooter(
            html.Div([html.H3('Historical Performance',className="header-title"),
            html.P('--I am a coder--',className="header-subtitle")])
            ),
        dbc.CardBody(
            [dcc.Graph(figure=fig_ddown,className='custom-chart',responsive=True)]
            )
    ],
)

def create_layout_2():

    return html.Div([html.Div([navbar,
                dbc.Row([dbc.Col([card2],width=4),
                            dbc.Col([card],width=8)],class_name='p-4'),
                dbc.Row([dbc.Col([card],width=12)],class_name='p-4'),
                dbc.Row([dbc.Col([card2],width=8),
                            dbc.Col([card],width=4)],class_name='p-4'),
                dbc.Row([dbc.Col([card2],width=6),
                            dbc.Col([card2],width=6)],class_name='p-4')
            ],className='my-page-container')

    ], className="page",
    )

layout_2 = create_layout_2()