def run_this():

    from dash import dcc
    from dash import html
    from dash.dependencies import Input, Output

    from .app import app
    from .apps import app1, app2

    app.layout = html.Div([ dcc.Location(id='url', refresh=False), 
                            html.Div(id='page-content'),
                            # dcc.Store(id="fetched_data", storage_type="session", data={}),
                        ])


    @app.callback(Output('page-content', 'children'),
                  Input('url', 'pathname')
                  )
    def display_page(pathname):

        if pathname == "" or pathname == "/" or pathname == "/home":
            print('going in')
            return app1.layout_home

        
        if pathname == "/layout2":
            print('going in')
            return app2.layout_2

        else:
            return app1.layout_home
    # return app

    # if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False, threaded=False, port=8072)


# def run_this():
#     app = main()
#     app.run_server(debug=True, use_reloader=False, threaded=False, port=8072)

# if __name__ == '__main__':
#     app.run_server(debug=True, use_reloader=False, threaded=False, port=8072)


    # from dotenv import load_dotenv
    # import os
    # from ..analysis import HerokuDB, plot_line
    # import dash
    # import dash_bootstrap_components as dbc
    # from dash import dcc, html

    # # Load dot env file
    # load_dotenv(dotenv_path=os.getcwd()+'/qlab/.env')

    # # Connect to Heroku PostgreSQL
    # db = HerokuDB(os.environ.get("HERO_URI"))
    # db.connect()

    # # tr2 = table_holdings_summary(db=db)

    # app = dash.Dash(__name__,
    #                 external_stylesheets=[dbc.themes.QUARTZ],
    #                 suppress_callback_exceptions=True
    #                 )

    # pdt = db.prices_table_read(assets_list=['SWDA','EIMI','EXXT','RBOT','QDVG','QDVE'])
    # assets_ls = ['PORT'] + ['SWDA','EIMI','EXXT','RBOT','QDVG','QDVE']
    # data = pdt.loc['2020-03-25':,assets_ls].copy().ffill()
    # fig_line = plot_line(data,rebase=True, chart_title='', legend=True, to_return=True)
    # fig_line = fig_line.update_layout(paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)')

    # card = dbc.Card(
    #     [
    #         dbc.CardHeader(
    #             html.Div([html.H3('Historical Performance',className="header-title"),
    #             html.P('--I am a coder--',className="header-subtitle")])
    #             ),
    #         dbc.CardBody(
    #             [dcc.Graph(figure=fig_line,className='custom-chart',responsive=True)]
    #             )
    #     ],
    # )

    # home_layout = html.Div([
    #                 dbc.Row([dbc.Col([card],width=4),
    #                          dbc.Col([card],width=8)],class_name='p-4'),
    #                 dbc.Row([dbc.Col([card],width=12)],class_name='p-4'),
    #                 dbc.Row([dbc.Col([card],width=8),
    #                          dbc.Col([card],width=4)],class_name='p-4'),
    #                 dbc.Row([dbc.Col([card],width=6),
    #                          dbc.Col([card],width=6)],class_name='p-4')
    #             ],className='my-page-container')

    
    # app.layout = html.Div([

    #     # dbc.Table.from_dataframe(tr2, striped=True, bordered=True, hover=True),
    #     home_layout
    # ])

    # CONTENT_STYLE = {
    # "margin-left": "18rem",
    # "margin-right": "2rem",
    # "padding": "2rem 1rem",
    # }
