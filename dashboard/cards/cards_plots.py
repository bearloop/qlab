from ...analysis import _visuals as vs
from .cards_templates import card_template, card_template_cmx, card_template_treemap, update_background, get_period


# --------------------------------------------------------------------------------------------------------------
def card_portfolio_alloc_hist(data):

    figure = vs.plot_alloc_hist(data, chart_title='', to_return=True)
    figure = update_background(figure)

    card = card_template(figure=figure, card_title='Historical Asset Allocation')

    return card

# --------------------------------------------------------------------------------------------------------------
def card_portfolio_alloc_last(data):

    figure = vs.plot_alloc(data, chart_title='', to_return=True)
    figure = update_background(figure)
    figure = figure.update_traces(domain={'x': [0,0.8], 'y': [0, 1]})

    card = card_template(figure=figure, card_title='Current Holdings')

    return card

# --------------------------------------------------------------------------------------------------------------
def card_performance(data, card_title='Portfolio Performance'):
    
    figure = vs.plot_line(data, rebase=True, chart_title='', legend=False, to_return=True)
    figure = update_background(figure)

    card = card_template(figure=figure, card_title=card_title)

    return card

# --------------------------------------------------------------------------------------------------------------
def card_port_returns(data, period='day', card_title='Portfolio Returns'):
    
    figure = vs.plot_ret(data, period=period, chart_title='', legend=False, to_return=True)
    figure = update_background(figure)

    card = card_template(figure=figure, card_title=card_title)

    return card

# --------------------------------------------------------------------------------------------------------------
def card_port_histogram(data, normal=True, normal_label='PORT', card_title='Portfolio Returns KDE'):
    
    figure = vs.plot_hist(data, normal=normal, normal_label=normal_label, chart_title='', legend=False, to_return=True)
    figure = update_background(figure)

    card = card_template(figure=figure, card_title=card_title)

    return card

# --------------------------------------------------------------------------------------------------------------
def card_risk(data, window=21, card_title='Portfolio Risk Annualised'):
    
    figure = vs.plot_vol(data, window=window, chart_title='', legend=False, to_return=True)
    figure = update_background(figure)

    card = card_template(figure=figure,
                         card_title=card_title,
                         card_sub_title='Lookback period = {} days'.format(str(window)))

    return card

# --------------------------------------------------------------------------------------------------------------
def card_var(data, window=21, forward=21, conf=0.95, card_title='Portfolio Value at Risk'):
    
    figure = vs.plot_var(data, window=window, forward=forward, conf=conf,
                         chart_title='', legend=False, to_return=True)
    figure = update_background(figure)

    subtitle = 'Lookback = {win} days, forward = {forw} days'.format(win=str(window), forw=str(forward))

    card_title = card_title + ' (@{conf}'.format(conf=str(round(conf*100,1))+'%)')

    card = card_template(figure=figure,
                         card_title=card_title,
                         card_sub_title=subtitle)

    return card

# --------------------------------------------------------------------------------------------------------------
def card_exp_shortfall(data, window=21, conf=0.95, card_title='Portfolio Exp. Shortfall'):
    
    figure = vs.plot_esfall(data, window=window, conf=conf, chart_title='', legend=False, to_return=True)
    figure = update_background(figure)

    subtitle = 'Mean Ret. < VaR in previous {win} days'.format(win=str(window))

    card_title = card_title + ' (@{conf}'.format(conf=str(round(conf*100,1))+'%)')

    card = card_template(figure=figure,
                         card_title=card_title,
                         card_sub_title=subtitle)

    return card

# --------------------------------------------------------------------------------------------------------------
def card_cmx(data):
    
    figure = vs.plot_cmx(data, chart_title='', colorbar=False, to_return=True, show_dates=False)
    figure = update_background(figure)
    subtitle = get_period(data)

    card = card_template_cmx(figure=figure,
                             card_title='Correlation Matrix',
                             card_sub_title='Period: ' + subtitle)
    
    return card

# --------------------------------------------------------------------------------------------------------------
def card_drawdown(data):

    figure = vs.plot_ddown(data, chart_title='', to_return=True)
    figure = update_background(figure)
    subtitle = get_period(data)
    card = card_template(figure=figure,
                         card_title='Historical Price Drawdown',
                         card_sub_title='Drawdown over: ' + subtitle)

    return card

# --------------------------------------------------------------------------------------------------------------
def card_correl(data, window=21, base='PORT', legend=True, card_title='Rolling Correlation'):
    
    figure = vs.plot_correl(data, window=window, base=base, chart_title='', legend=legend, to_return=True)
    figure = update_background(figure)

    subtitle = 'Lookback period = {win} days'.format(win=str(window))

    card = card_template(figure=figure,
                         card_title=card_title+' vs '+base,
                         card_sub_title=subtitle)

    return card


# --------------------------------------------------------------------------------------------------------------
def card_treemap(data, sort_by, card_title='Assets Heatmap', reverse=False):

    figure = vs.plot_treemap(data, sort_by=sort_by, frame=False, chart_title='', midpoint=0,
                             colorbar=False, reverse=reverse, to_return=True)
    figure = update_background(figure)

    card = card_template_treemap(figure=figure,
                                 card_title=card_title + ' (' + sort_by + ')',
                                 card_sub_title='')
    
    return card

# --------------------------------------------------------------------------------------------------------------
def card_barchart(data, sort_by, card_title='Assets Monitor'):

    figure = vs.plot_barchart(data, sort_by=sort_by, chart_title='', show_range=False, legend=True, to_return=True)
    figure = update_background(figure)

    card = card_template(figure=figure,
                         card_title=card_title + ' (' + sort_by + ')',
                         card_sub_title='')
    
    return card

# --------------------------------------------------------------------------------------------------------------
