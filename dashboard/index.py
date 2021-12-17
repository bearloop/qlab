
def main():
    from dotenv import load_dotenv
    import os
    from ..analysis import HerokuDB, Portfolio
    import dash
    import dash_bootstrap_components as dbc

    # Load dot env file
    load_dotenv(dotenv_path=os.getcwd()+'/testlab/.env')

    # Connect to Heroku PostgreSQL

    db = HerokuDB(os.environ.get("HERO_URI"))
    db.connect()

    pric = db.prices_table_read()
    pric['PORT'] = Portfolio(heroku_conn=db).fetch_data()['PORT']

    po = Portfolio(db)
    tr = po.fetch_transactions()

    tr['cap_paid'] = tr['transaction_price'].mul(tr['transaction_quantity'])
    tr2 = tr.groupby('symbol').sum()
    tr2 = tr2[tr2['transaction_quantity']>0]
    tr2['cap_paid_share'] = tr2['cap_paid'].div(tr2['transaction_quantity'])
    tr2['last_price'] = pric[tr2.index].iloc[-1]
    tr2['position'] = tr2['last_price'].mul(tr2['transaction_quantity'])
    tr2['pnl'] = tr2['position']-tr2['cap_paid']
    tr2['pnl_pct'] = tr2['pnl'].div(tr2['cap_paid'])
    tr2 = tr2.sort_values(by='cap_paid',ascending=False)
    tr2['weight'] = tr2['position'].div(tr2['position'].sum())

    app = dash.Dash(__name__,
                    external_stylesheets=[dbc.themes.QUARTZ],
                    suppress_callback_exceptions=True
                    )


    app.layout = dbc.Container([

        dbc.Table.from_dataframe(tr2, striped=True, bordered=True, hover=True)
    ])

    return app


def run_this():
    app = main()
    app.run_server(debug=True, use_reloader=False, threaded=False, port=8072)

# if __name__ == '__main__':
#     app.run_server(debug=True, use_reloader=False, threaded=False, port=8072)