from ...analysis import _tables as tab
from .cards_templates import  card_table
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
        'border-top': '1.8px solid #272727',
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
           
        }]


# --------------------------------------------------------------------------------------------------------------
# Portfolio view: transactions table
def table_portfolio_holdings_transactions(db):

    df = tab.table_holdings_summary(db=db)
    assets_list = df.index

    df = _pd.concat([_pd.DataFrame(df.index.values,index=df.index,columns=['Symbol']),df],axis=1)
    cols = [{'id':i,'name':i} for i in df.columns]

    table = df.to_dict('records')

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
    cols = [{'id':i,'name':i} for i in df.columns]

    table = df.to_dict('records')
    
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

    table = tab.table_securities_stats(df)
    table = _pd.concat([_pd.DataFrame(table.index.values,index=table.index,columns=['Symbol']),table],axis=1)
    cols = [{'id':i,'name':i} for i in table.columns]

    table = table.to_dict('records')
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
    card = card_table(table1=table1, table2=table2, table3=table3, card_title='Portfolio Holdings Summary')

    return card


# --------------------------------------------------------------------------------------------------------------
# Assets view: assets stats
def card_table_assets_stats(assets_list, start_date=None, end_date=None):

    if assets_list is not None:
    
        # assets_list.append('PORT')

        df = _pd.DataFrame(pdt[assets_list]).copy()
        
        if start_date is not None:
            df = df.loc[start_date:,:]
        
        if end_date is not None:
            df = df.loc[:end_date,:]

        table = tab.table_securities_stats(df)
        table = _pd.concat([_pd.DataFrame(table.index.values,index=table.index,columns=['Symbol']),table],axis=1)
        # format_cell['width']='50px'
        
        cols = [{'id':i,'name':i} for i in table.columns]

        table = table.to_dict('records')
        table_assets = dash_table.DataTable(data=table, columns=cols, id='custom-table-assets-view',
                                    style_data_conditional=format_data_conditional,
                                    style_table={},
                                    style_header=format_header,
                                    style_cell=format_cell,
                                    sort_action='native')
    
    else:
        table_assets = None
    
    card = card_table(table1=table_assets, table2=None, table3=None,
                      card_title='Assets Stats', card_sub_title='Return-risk profile of selected assets')

    return card
# --------------------------------------------------------------------------------------------------------------