from ...analysis import _tables as tab
from .cards_templates import card_table, card_table_test
from dash import dash_table
from dash.dash_table.Format import Format, Scheme
import pandas as _pd
from ..hconn import pdt
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
# Porfolio view: securities statistics table
def table_portfolio_stats(assets_list, start_date=None):

    df = pdt[list(assets_list)+['PORT']].copy()
    
    if start_date is not None:
        df = df.loc[start_date:,:]

    table = tab.table_securities_stats(df).T
    table = _pd.concat([_pd.DataFrame(table.index.values,index=table.index,columns=['Symbol']),table],axis=1)

    table = table.to_dict('records')

    cols = [dict(id='Symbol',name='Symbol'),dict(id='Start',name='Start'),dict(id='End',name='End'),
            dict(id='Periods',name='Periods'),
            dict(id='Ret: 1-d', name='Ret: 1-d', type='numeric', format=Format(precision=2, scheme=Scheme.percentage)),
            dict(id='Ret: 1-wk', name='Ret: 1-wk', type='numeric', format=Format(precision=2, scheme=Scheme.percentage)),
            dict(id='Ret: 1-mo', name='Ret: 1-mo', type='numeric', format=Format(precision=2, scheme=Scheme.percentage)),
            dict(id='Ret: 3-mo', name='Ret: 3-mo', type='numeric', format=Format(precision=2, scheme=Scheme.percentage)),
            dict(id='Ret: 1-yr', name='Ret: 1-yr', type='numeric', format=Format(precision=2, scheme=Scheme.percentage)),
            dict(id='CAGR', name='CAGR', type='numeric', format=Format(precision=2, scheme=Scheme.percentage)),
            dict(id='E(r) (1-yr, ann)', name='E(r) (1-yr, ann)', type='numeric', format=Format(precision=2, scheme=Scheme.percentage)),
            dict(id='Vol (1-yr, ann)', name='Vol (1-yr, ann)', type='numeric', format=Format(precision=2, scheme=Scheme.percentage)),
            dict(id='Drawdown', name='Drawdown', type='numeric', format=Format(precision=2, scheme=Scheme.percentage)),
            dict(id='Max Drawdown', name='Max Drawdown', type='numeric', format=Format(precision=2, scheme=Scheme.percentage)),
            dict(id='Mean ret', name='Mean ret', type='numeric', format=Format(precision=2, scheme=Scheme.percentage)),
            dict(id='Stand Dev', name='Stand Dev', type='numeric', format=Format(precision=2, scheme=Scheme.percentage)),
            dict(id='Skewness', name='Skewness', type='numeric', format=Format(precision=2, scheme=Scheme.percentage)),
            dict(id='Kurtosis', name='Kurtosis', type='numeric', format=Format(precision=2, scheme=Scheme.percentage))
       ]

    table3 = dash_table.DataTable(data=table,columns=cols,id='custom-table-stats',
                                 style_data_conditional=format_data_conditional,
                                 style_table={},
                                 style_header=format_header,
                                 style_cell=format_cell)
    return table3
# --------------------------------------------------------------------------------------------------------------
# Portfolio view: holdings summary tabs
def card_table_portfolio_holdings_summary(db):

    table1, assets_list = table_portfolio_holdings_transactions(db)
    table2 = table_portfolio_fund_details(assets_list=assets_list, db=db)
    table3 = table_portfolio_stats(assets_list=assets_list, start_date='25-03-2020')
    card = card_table_test(table1=table1, table2=table2, table3=table3, card_title='Portfolio Holdings Summary')

    return card
