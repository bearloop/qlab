from ...analysis import _tables as tab
from .cards_templates import card_table, card_table_test
from dash import dash_table
from dash.dash_table.Format import Format, Scheme
import pandas as _pd

# --------------------------------------------------------------------------------------------------------------
# Constants: table formatting

format_header={
        'backgroundColor': 'transparent !important',
        'font_family': 'sans-serif',
        'text_align': 'left',
        'border': '0.0px',
        'border-top': '2.0px solid #272727',
        'border-bottom': '1.8px solid #272727'
    }

format_cell = {
        'font_family': 'sans-serif',
        'backgroundColor': 'transparent !important',
        'text_align': 'left',
        'border': '0.0px',
        'border-bottom': '0.1px solid #272727'
    }

format_data_conditional = [{
            "if": {"state": "selected"},
            "border": "0.0px solid transparent",
        }]

# --------------------------------------------------------------------------------------------------------------
# Portfolio view: transactions table
def table_portfolio_holdings_transactions(db):

    df = tab.table_holdings_summary(db=db)
    assets_list = df.index

    df = _pd.concat([_pd.DataFrame(df.index.values,index=df.index,columns=['Symbol']),df],axis=1)

    table = df.to_dict('records')
    cols = [dict(id='Symbol',name='Symbol'),
            dict(id='Units', name='Units', type='numeric', format=Format(precision=2, scheme=Scheme.decimal_integer)),
            dict(id='Cost/unit', name='Cost/unit', type='numeric', format=dict(specifier='.2f')),
            dict(id='Last Price', name='Last Price', type='numeric', format=dict(specifier='.2f')),
            dict(id='Position', name='Position', type='numeric', format=dict(specifier='.2f')),
            dict(id='PnL', name='PnL', type='numeric', format=dict(specifier='.2f')),
            dict(id='PnL %', name='PnL %', type='numeric', format=Format(precision=2,scheme=Scheme.percentage)),
            dict(id='Allocation', name='Allocation', type='numeric', format=Format(precision=2,scheme=Scheme.percentage))]

    table1 = dash_table.DataTable(data=table,columns=cols,id='custom-table-transactions',
                                 style_data_conditional=format_data_conditional,
                                 style_table={},
                                 style_header=format_header,
                                 style_cell=format_cell)
    
    return table1, assets_list

# --------------------------------------------------------------------------------------------------------------
# Portfolio view: fund details table
def table_portfolio_fund_details(assets_list, db):

    df = tab.table_fund_details(assets_list=assets_list, db=db)
    df = df.drop(['ISIN','Launch'],axis=1)
    df = _pd.concat([_pd.DataFrame(df.index.values,index=df.index,columns=['Symbol']),df],axis=1)
   
    # Fromat % columns in the dataframe
    pct_columns = [i for i in df.columns if '%' in i]
    df[pct_columns] = df[pct_columns]/100

    table = df.to_dict('records')

    cols = [dict(id='Symbol',name='Symbol'),
            # dict(id='ISIN', name='ISIN'),
            dict(id='Fund AUM', name='AUM'),
            dict(id='Expense %', name='Expense', type='numeric', format=Format(precision=2,scheme=Scheme.percentage) ),
            # dict(id='Launch', name='Launch'),
            dict(id='Top-10 %', name='Top-10', type='numeric', format=Format(precision=0,scheme=Scheme.percentage) ),
            dict(id='IT %', name='InfoTech', type='numeric', format=Format(precision=0,scheme=Scheme.percentage) ),
            dict(id='HC %', name='HCare', type='numeric', format=Format(precision=0,scheme=Scheme.percentage) ),
            dict(id='FIN %', name='Fin', type='numeric', format=Format(precision=0,scheme=Scheme.percentage) ),
            dict(id='TEL %', name='Telco', type='numeric', format=Format(precision=0,scheme=Scheme.percentage) ),
            dict(id='CYCL %', name='Cycl', type='numeric', format=Format(precision=0,scheme=Scheme.percentage) ),
            dict(id='DEF %', name='Def', type='numeric', format=Format(precision=0,scheme=Scheme.percentage) ),
            ]

    table = dash_table.DataTable(data=table,columns=cols,id='custom-table-fund-details',
                                 style_data_conditional=format_data_conditional,
                                 style_table={},
                                 style_header=format_header,
                                 style_cell=format_cell)

    return table

# --------------------------------------------------------------------------------------------------------------
# Portfolio view: holdings summary tabs
def card_table_portfolio_holdings_summary(db):

    table1, assets_list = table_portfolio_holdings_transactions(db)
    table2 = table_portfolio_fund_details(assets_list=assets_list, db=db)
    card = card_table_test(table1=table1,table2=table2, card_title='Portfolio Holdings Summary')

    return card
