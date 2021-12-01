import pandas as _pd
import numpy as _np
from datetime import date as _date
from datetime import datetime as _datetime
from datetime import timedelta as _timedelta
import plotly.express as _px


_cool_colors = ["#001219","#005f73","#0a9396","#94d2bd","#e9d8a6",
               "#ee9b00","#ca6702","#bb3e03","#ae2012","#9b2226"]

_chart_format_dict = {'Percent':["Date: %{x|%Y-%m-%d}<br>Value: %{y:.1%}", ".0%"],
                      'Value':  ["Date: %{x|%Y-%m-%d}<br>Value: %{y}",     ".1f"]}

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
def plot_var(df=None, window=21, forward=21, conf=0.05, chart_title='Historical VaR', legend=False, to_return=False, width=720, height=360):
    """
    Plots the forward-N periods (e.g. 21-days) value at risk based on the window's hist distribution.
    """
    if df is None: 
        return _plot_none(chart_title=chart_title, width=width, height=height)
    
    else:
        conf=0.95
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
def _plot_none(chart_title=None, width=720, height=360):
    """
    Makes sure that plots return an empty chart.
    """
    # Create a DF and assign some value
    df = _pd.DataFrame()
    df.loc[_date.today(), "data"] = 0 #.strftime("%d-%m-%Y")
    return _template_line(df, chart_title=chart_title, width=width, height=height, template=_charts_template)


# --------------------------------------------------------------------------------------------
def _template_line(df=None, chart_title=None, legend=False, width=720, height=360, template='simple_white'):
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

