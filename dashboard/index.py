def run_this():

    from dash import dcc
    from dash import html
    from dash.dependencies import Input, Output

    from .app import app
    from .apps import app1, app2

    app.layout = html.Div([ dcc.Location(id='url', refresh=False), 
                            html.Div(id='page-content')
                          ])


    @app.callback(Output('page-content', 'children'),
                  Input('url', 'pathname')
                  )
    def display_page(pathname):
        
        if pathname == "/layout-2":
            print('going in 2')
            return app2.layout_2

        else:
            print('going in home')
            return app1.layout_home

    # if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False, threaded=False, port=8072)