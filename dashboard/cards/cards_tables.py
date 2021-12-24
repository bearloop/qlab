from ...analysis import _tables as tab
from .cards_templates import card_table
from dash import dash_table
from dash.dash_table.Format import Format, Scheme
import pandas as _pd

# --------------------------------------------------------------------------------------------------------------
def card_table_portfolio_holdings_summary(db):

    df = tab.table_holdings_summary(db=db)
  
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
                "border": "0.0px solid #2a93cfc9",
            }]

    table = dash_table.DataTable(data=table,columns=cols,id='custom-table',
                                 style_data_conditional=format_data_conditional,
                                 style_table={},
                                 style_header=format_header,
                                 style_cell=format_cell)

    

    card = card_table(table=table, card_title='Portfolio Holdings Summary')

    return card
