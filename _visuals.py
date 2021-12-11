import pandas as _pd
import numpy as _np
from datetime import date as _date
from datetime import datetime as _datetime
import plotly.figure_factory as _ff
from datetime import timedelta as _timedelta
import plotly.express as _px
from ._utilities import _calc_expected_shortfall

_cool_colors = ["#001219","#005f73","#0a9396","#94d2bd","#e9d8a6",
               "#ee9b00","#ca6702","#bb3e03","#ae2012","#9b2226"]

_cmx_colors = ["#e39774","#e5e5e5","#5c9ead"]

_chart_format_dict = {'Percent':   ["Date: %{x|%Y-%m-%d}<br>Value: %{y:.1%}",  ".0%"       ],
                      'Value':     ["Date: %{x|%Y-%m-%d}<br>Value: %{y}",      ".1f"       ],
                      'Value_2f':  ["Date: %{x|%Y-%m-%d}<br>Value: %{y:.2f}",  ".2f"       ],
                      'Density':   ["Return: %{x}<br>Count: %{y}",             ".0f", ".1%"]}

_charts_template='simple_white'


# --------------------------------------------------------------------------------------------
def plot_line(df=None, rebase=False, chart_title='Historical Performance', legend=False, to_return=False, width=720, height=360):
    """
    Plots asset prices time series.
    """

    if df is None: 
        return _plot_none(chart_title=chart_title, width=width, height=height)

    else:
        opacity = 0
        hover = _chart_format_dict['Value'][0]
        yformat = _chart_format_dict['Value'][1]

        # Rebase data if needed
        if rebase==True:
            # pct_change handles any missing values by setting the rate of change to 0
            df = df.pct_change().add(1).cumprod().fillna(1)-1
            opacity = 0.8
            hover = _chart_format_dict['Percent'][0]
            yformat = _chart_format_dict['Percent'][1]

        # Make the plot
        fig = _template_line(df, chart_title=chart_title, legend=legend, width=width, height=height, template=_charts_template)
        fig = fig.add_hline(y=0.0,line_width=1.5, line_dash="dot", line_color="red", opacity=opacity
                ).update_traces(hovertemplate=hover).update_yaxes(tickformat=yformat)

        # Show or return the plot
        if to_return==False:
            fig.show()
        
        else:
            return fig  

# --------------------------------------------------------------------------------------------
def plot_vol(df=None, window=21, freq=252, chart_title='Historical Volatility', legend=False, to_return=False, width=720, height=360):
    """
    Plots annualized volatility over the passed window.
    """
    if df is None: 
        return _plot_none(chart_title=chart_title, width=width, height=height)
    
    else:
        volatility = df.pct_change().rolling(window=window, min_periods=window).std()*_np.sqrt(freq)
        hover = _chart_format_dict['Percent'][0]
        yformat = _chart_format_dict['Percent'][1]

        fig = _template_line(volatility, chart_title=chart_title, legend=legend, width=width, height=height, template=_charts_template
                ).update_traces(hovertemplate=hover).update_yaxes(tickformat=yformat)

        # Show or return the plot
        if to_return==False:
            fig.show()
        
        else:
            return fig

# --------------------------------------------------------------------------------------------
def plot_ddown(df=None, chart_title='Drawdown', legend=False, to_return=False, width=720, height=360):
    """
    Plots price drawdown given the max price of the period in the dataframe.
    """
    if df is None: 
        return _plot_none(chart_title=chart_title, width=width, height=height)
    
    else:
        df = df.fillna(method="ffill")
        maxPrices = df.cummax()
        ddown = (df/maxPrices)-1

        hover = _chart_format_dict['Percent'][0]
        yformat = _chart_format_dict['Percent'][1]

        fig = _template_line(ddown, chart_title=chart_title, legend=legend, width=width, height=height, template=_charts_template
                ).update_traces(hovertemplate=hover).update_yaxes(tickformat=yformat)

        # Show or return the plot
        if to_return==False:
            fig.show()
        
        else:
            return fig

# --------------------------------------------------------------------------------------------
def plot_var(df=None, window=21, forward=21, conf=0.95, chart_title='Historical VaR', legend=False, to_return=False, width=720, height=360):
    """
    Plots the forward-N periods (e.g. 21-days) value at risk based on the window's hist distribution.
    """
    if df is None: 
        return _plot_none(chart_title=chart_title, width=width, height=height)
    
    else:
        var = df.pct_change().rolling(window=window, min_periods=window).quantile(1-conf)*_np.sqrt(forward)
        hover = _chart_format_dict['Percent'][0]
        yformat = _chart_format_dict['Percent'][1]

        fig = _template_line(var, chart_title=chart_title, legend=legend, width=width, height=height, template=_charts_template
                ).update_traces(hovertemplate=hover).update_yaxes(tickformat=yformat)

        # Show or return the plot
        if to_return==False:
            fig.show()
        
        else:
            return fig  

# --------------------------------------------------------------------------------------------
def plot_esfall(df=None, window=21, conf=0.95, chart_title='Expected Shortfall (E(Rt)<VaR)', legend=False, to_return=False, width=720, height=360):
    """
    Plots Historical Exp. Shortfall. Not an annualized metric, just looks at the past N periods and says this is the average of returns below VaR over this date range.
    """
    if df is None:
        return _plot_none(chart_title=chart_title, width=width, height=height)
    
    else:
        # Calculate Expected Shortfall for all assets
        es = _pd.DataFrame(df).apply(lambda x: _calc_expected_shortfall(x,window=window,conf=conf))

        hover = _chart_format_dict['Percent'][0]
        yformat = _chart_format_dict['Percent'][1]

        fig = _template_line(es, chart_title=chart_title, legend=legend, width=width, height=height, template=_charts_template
                ).update_traces(hovertemplate=hover).update_yaxes(tickformat=yformat)

        # Show or return the plot
        if to_return==False:
            fig.show()
        
        else:
            return fig  

# --------------------------------------------------------------------------------------------
def plot_correl(df=None, window=21, base=None, chart_title='Correlation', legend=False, to_return=False, width=720, height=360):
    """
    Plots the correlation of the base asset and every other asset on a rolling basis over the window period.
    """
    if (df is None) or (base is None): 
        return _plot_none(chart_title=chart_title, width=width, height=height)
    
    else:
        # Calculate correlation for base vs all other assets and then remove the base asset col
        cor = df.pct_change().rolling(window).corr()[base].unstack().drop([base],axis=1)

        hover = _chart_format_dict['Value_2f'][0]
        yformat = _chart_format_dict['Value_2f'][1]

        chart_title = chart_title + ' vs '+base
        fig = _template_line(cor, chart_title=chart_title, legend=legend, width=width, height=height, template=_charts_template
                ).update_traces(hovertemplate=hover).update_yaxes(tickformat=yformat)

        # Show or return the plot
        if to_return==False:
            fig.show()
        
        else:
            return fig  

# --------------------------------------------------------------------------------------------
def plot_hist(df=None, chart_title='Returns KDE', legend=False, to_return=False, width=720, height=360):
    
    if df is None: 
        return _plot_none(chart_title=chart_title, width=width, height=height)
    
    else:
        labels = list(df.columns)
        data = [df[i].dropna().pct_change().dropna() for i in labels]

        hover = _chart_format_dict['Density'][0]
        yformat = _chart_format_dict['Density'][1]
        xformat = _chart_format_dict['Density'][2]

        fig = _ff.create_distplot(data, group_labels=labels, show_curve='kde',
                                  show_hist=False, show_rug=False, colors=_cool_colors)
         
        fig = _time_layout(fig=fig, title=chart_title, legend=legend, width=width, height=height)
        
        fig = fig.update_layout(template=_charts_template).update_traces(hovertemplate=hover
                ).update_xaxes(tickformatstops = [dict(value=xformat)]).update_yaxes(tickformat=yformat)

        # Show or return the plot
        if to_return==False:
            fig.show()
        
        else:
            return fig 

# --------------------------------------------------------------------------------------------
def plot_scatter(df=None, chart_title='Returns-Volatility Plot', legend=False, to_return=False, width=720, height=360):
    if df is None: 
        return _plot_none(chart_title=chart_title, width=width, height=height)
    
    else:
        fig = ''

        # Show or return the plot
        if to_return==False:
            fig.show()
        
        else:
            return fig 

# --------------------------------------------------------------------------------------------
def plot_cmx(df=None, chart_title='Correlation matrix', colorbar=False, to_return=False, width=720, height=360, show_dates=True):

    if df is None: 
        return _plot_none(chart_title=chart_title, width=width, height=height)
    
    else:
        # This will hide the upper triangle of the table
        
        ret = df.pct_change().dropna()
        cor = ret.corr()
        cor = cor.mask(_np.tril(cor.values,-1)==0)
        cor = cor.dropna(how='all').dropna(how='all',axis=1)

        if show_dates:
            try:
                date1 = _datetime.strftime(ret.index[0], '%Y-%m-%d')
                date2 = _datetime.strftime(ret.index[-1], '%Y-%m-%d')
                chart_title = chart_title + ': ' + str(date1)[:10] + ' - ' + str(date2)[:10]
                
            except: ''
        
        fig = _ff.create_annotated_heatmap(cor.values.round(2),
                                    x=list(cor.columns),y=list(cor.index),reversescale=True,
                                    colorscale=_cmx_colors,hoverinfo='z',showscale=colorbar, xgap = 2, ygap = 2)

        fig = fig.update_layout(width = width, height = height, plot_bgcolor='white', 
                         font = dict(color="#505050", size=12, family='sans-serif'),
                         margin = {'l':0, 't':65, 'r':10, 'b':0, 'pad':0},
                         title={'text':chart_title, 'xref':'paper', 'x':1, 'xanchor': 'right',
                                'font':{'size':15, 'family':'sans-serif'}})

        fig = fig.update_xaxes(showline=True, linewidth=0.25, linecolor='black', showgrid=False,
                              ticks="outside", title_text=None
                              ).update_yaxes(showline=True, linewidth=0.25, linecolor='black', showgrid=False, 
                              ticks="outside", title_text=None, autorange='reversed')
        
        # Show or return the plot
        if to_return==False:
            fig.show()
        
        else:
            return fig 

# --------------------------------------------------------------------------------------------
def _plot_none(chart_title=None, width=720, height=360):
    """
    Makes sure that plots return an empty chart.
    """
    # Create a DF and assign some value
    df = _pd.DataFrame()
    df.loc[_date.today(), "data"] = 0 #.strftime("%d-%m-%Y")
    return _template_line(df, chart_title=chart_title, width=width, height=height, template=_charts_template)

# --------------------------------------------------------------------------------------------
def _template_line(df=None, chart_title=None, legend=False, width=720, height=360, template=_charts_template):
    """ """
    
    # Make the line plot
    fig = _px.line(df, template = template, color_discrete_sequence=_cool_colors, render_mode="svg")

    # Update layout
    fig = _time_layout(fig, title=chart_title, legend=legend, width=width, height=height)

    # Add space to the right part of the graph
    fig = _add_space(df, fig)
        
    return fig

# --------------------------------------------------------------------------------------------
def _time_layout(fig, title, legend, width, height):
    """ """

    xaxis_tickformatstops = [
        dict(dtickrange=[None, "M1"], value="%b %d"),
        dict(dtickrange=["M1", "M12"], value="%b '%y"),
        dict(dtickrange=["M12", None], value="%Y Y")
    ]

    fig = fig.update_layout(
            font = dict(color="#505050", size=10, family='sans-serif'),
            xaxis = {"gridcolor": "#E1E5ED"},
            yaxis = {"gridcolor": "#E1E5ED"},
            plot_bgcolor='white',
            showlegend = legend, legend_title='Assets:',
            autosize=False,
            width = width, height = height,
            margin = {'l':0, 't':25, 'r':10, 'b':0, 'pad':0},
            title={'text':title, 'xref':'paper', 'x':1, 'xanchor': 'right',
                   'font':{'size':15, 'family':'sans-serif'}}
        ).update_xaxes(tickformatstops=xaxis_tickformatstops, title_text='',
        ).update_yaxes(title_text='')

    return fig

# --------------------------------------------------------------------------------------------
def _add_space(df, fig):
    """ """
    x0 = df.index[-1]
    x1 = x0+_timedelta(days=21)
    fig = fig.add_vrect(x0=x0, x1=x1, col=1, opacity=0.05)

    return fig


# --------------------------------------------------------------------------------------------

