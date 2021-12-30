import pandas as _pd
import numpy as _np
from datetime import date as _date
from datetime import datetime as _datetime
import plotly.figure_factory as _ff
from datetime import timedelta as _timedelta
import plotly.express as _px
from ._utilities import _calc_expected_shortfall

_cool_colors = ["#001219","#005f73","#0a9396","#94d2bd",
               "#ee9b00","#ca6702","#bb3e03","#ae2012","#9b2226","#7d8491"]

_cmx_colors = ["#961957","#d0d5db","#2c71c0"]#["#e39774","#e5e5e5","#5c9ead"]

_chart_format_dict = {'Percent':   ["Date: %{x|%Y-%m-%d}<br>Value: %{y:.1%}",  ".0%"       ],
                      'Value':     ["Date: %{x|%Y-%m-%d}<br>Value: %{y}",      ".1f"       ],
                      'Value_2f':  ["Date: %{x|%Y-%m-%d}<br>Value: %{y:.2f}",  ".2f"       ],
                      'Density':   ["Return: %{x:.2%}<br>Count: %{y}",         ".0f", ".1%"]}

_charts_template='simple_white'


# --------------------------------------------------------------------------------------------
def plot_line(df=None, rebase=False, chart_title='Historical Performance', legend=True, to_return=False, width=720, height=360):
    """
    Plots asset prices time series.
    """

    if df is None: 
        return _plot_none(chart_title=chart_title, width=width, height=height)

    else:
        df = _ffill(df)
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
def plot_ret(df=None, period=None, chart_title='Returns', legend=True, to_return=False, width=720, height=360):
    """
    Plots asset price time series returns.
    period: str, end of week, month or quarter 
    """

    if df is None: 
        return _plot_none(chart_title=chart_title, width=width, height=height)

    else:
        df = _ffill(df)
        hover = _chart_format_dict['Percent'][0]
        yformat = _chart_format_dict['Percent'][1]

        if period == 'week':
            df = df.resample('W-FRI').apply(lambda x: x[-1])
        elif period == 'month':
            df = df.resample('M').apply(lambda x: x[-1])
        elif period == 'quarter':
            df = df.resample('Q').apply(lambda x: x[-1])

        rt = _pd.DataFrame(df.pct_change().dropna())
        # Make the bar chart plot
        fig = _px.bar(rt, template=_charts_template, color_discrete_sequence=_cool_colors)

        # Update layout
        fig = _time_layout(fig, title=chart_title, legend=legend, width=width, height=height)

        # Add space to the right part of the graph
        if (period is None) or period =='day':
            fig = _add_space(rt, fig)
            fig = fig.update_traces(marker_line_width=0, selector=dict(type="bar"))

        # Update traces, y axis format
        fig = fig.update_traces(hovertemplate=hover).update_yaxes(tickformat=yformat)

        # Show or return the plot
        if to_return==False:
            fig.show()
        
        else:
            return fig

# --------------------------------------------------------------------------------------------
def plot_vol(df=None, window=21, freq=252, chart_title='Historical Volatility', legend=True, to_return=False, width=720, height=360):
    """
    Plots annualized volatility over the passed window.
    """
    if df is None: 
        return _plot_none(chart_title=chart_title, width=width, height=height)
    
    else:
        df = _ffill(df)
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
def plot_ddown(df=None, chart_title='Drawdown', legend=True, to_return=False, width=720, height=360):
    """
    Plots price drawdown given the max price of the period in the dataframe.
    """
    if df is None: 
        return _plot_none(chart_title=chart_title, width=width, height=height)
    
    else:
        df = _ffill(df)
        # df = df.fillna(method="ffill")
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
def plot_var(df=None, window=21, forward=21, conf=0.95, chart_title='Historical VaR', legend=True, to_return=False, width=720, height=360):
    """
    Plots the forward-N periods (e.g. 21-days) value at risk based on the window's hist distribution.
    """
    if df is None: 
        return _plot_none(chart_title=chart_title, width=width, height=height)
    
    else:
        df = _ffill(df)
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
def plot_esfall(df=None, window=21, conf=0.95, chart_title='Expected Shortfall (E(Rt)<VaR)', legend=True, to_return=False, width=720, height=360):
    """
    Plots Historical Exp. Shortfall. Not an annualized metric, just looks at the past N periods and says this is the average of returns below VaR over this date range.
    """
    if df is None:
        return _plot_none(chart_title=chart_title, width=width, height=height)
    
    else:
        df = _ffill(df)
        # Calculate Expected Shortfall for all assets
        es = df.apply(lambda x: _calc_expected_shortfall(x,window=window,conf=conf))

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
def plot_correl(df=None, window=21, base=None, chart_title='Correlation', legend=True, to_return=False, width=720, height=360):
    """
    Plots the correlation of the base asset and every other asset on a rolling basis over the window period.
    """
    if (df is None) or (base is None): 
        return _plot_none(chart_title=chart_title, width=width, height=height)
    
    else:
        df = _ffill(df)
        # Calculate correlation for base vs all other assets and then remove the base asset col
        cor = df.pct_change().rolling(window).corr()[base].unstack().drop([base],axis=1)

        hover = _chart_format_dict['Value_2f'][0]
        yformat = _chart_format_dict['Value_2f'][1]

        if chart_title!='':
            chart_title = chart_title + ' vs ' + base

        fig = _template_line(cor, chart_title=chart_title, legend=legend, width=width, height=height, template=_charts_template
                ).update_traces(hovertemplate=hover).update_yaxes(tickformat=yformat)

        # Show or return the plot
        if to_return==False:
            fig.show()
        
        else:
            return fig  

# --------------------------------------------------------------------------------------------
def plot_hist(df=None, normal=False, normal_label=None, chart_title='Returns KDE', legend=True, to_return=False, width=720, height=360):
    
    if df is None: 
        return _plot_none(chart_title=chart_title, width=width, height=height)
    
    else:
        df = _ffill(df)
        labels = list(df.columns)
        data = [df[i].dropna().pct_change().dropna() for i in labels]

        if normal:
            mu = df[normal_label].dropna().pct_change().mean()
            sd = df[normal_label].dropna().pct_change().std()
            norm_dist = _pd.Series([_np.random.normal(loc=mu, scale=sd) for k in range(2000)])
            labels.append('NORM (MU: ' + str(round(mu*100,1))+'% - SD:' + str(round(sd*100,1))+'%)')
            data.append(norm_dist)

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
def _plot_scatter(df=None, chart_title='Returns-Volatility Plot', legend=True, to_return=False, width=720, height=360):
    if df is None: 
        return _plot_none(chart_title=chart_title, width=width, height=height)
    
    else:
        df = _ffill(df)
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
        df = _ffill(df)

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
        # Add annotated text so that the heatmap does not show any NaN
        at = cor.values.round(2).astype(str)
        at[at=='nan'] = ''

        fig = _ff.create_annotated_heatmap(cor.values.round(2),
                                    x=list(cor.columns),y=list(cor.index),
                                    annotation_text=at,reversescale=True,
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
def plot_alloc_hist(df=None, chart_title='Portfolio Historical Allocation', legend=True, to_return=False, width=720, height=360):
    """
    """
    if df is None: 
        return _plot_none(chart_title=chart_title, width=width, height=height)
    
    else:
        
        yformat = _chart_format_dict['Percent'][1]

        fig = _px.area(df, template = _charts_template, color_discrete_sequence=_cool_colors)

        fig = fig.update_traces(line_width=0.0,
                                hovertemplate="Date: %{x|%Y-%m-%d}<br>Weight: %{y:0.3%}"
                                ).update_yaxes(tickformat=yformat).update_layout(yaxis_range=(0, 1))
        
        fig = _time_layout(fig, title=chart_title, legend=legend, width=width, height=height)
        fig = _add_space(df, fig)

        # Show or return the plot
        if to_return==False:
            fig.show()
        
        else:
            return fig 

# --------------------------------------------------------------------------------------------
def plot_alloc(df=None, chart_title='Portfolio Allocation', to_return=False, width=720, height=360):
    """
    Expects a pandas DataFrame with a single column, where the index holds the asset names.
    """
    if df is None: 
        return _plot_none(chart_title=chart_title, width=width, height=height)
    
    else:
        fig = _px.pie(df, values=df.columns[0], names=df.index, template=_charts_template, hole=0.3,
                     color_discrete_sequence=_cool_colors)

        fig = fig.update_traces(textposition='inside', textinfo='percent+label', pull=0.015,
                                hovertemplate="Asset: %{label}<br>Weight: %{percent:0.2%}")

        fig = fig.update_layout(width = width, height = height,
                                font = dict(color="#505050", size=10, family='sans-serif'),
                                showlegend = True, legend_title='Assets:', legend_x=0.85,
                                title={'text':chart_title,
                                       'xref':'paper', 'x':1, 'xanchor': 'right', 
                                       'font':{'size':15, 'family':'sans-serif'}})

        # Show or return the plot
        if to_return==False:
            fig.show()
        
        else:
            return fig 

# --------------------------------------------------------------------------------------------
def plot_treemap(df, sort_by='1-yr', frame=True, chart_title='Performance', midpoint=0, colorbar=False, 
                                      reverse=False, to_return=False, width=920, height=640):
    """
    Plots a treemap for performance or volatility (whichever the dataframe includes).
    Expects 3 descriptive columns: symbol, name, segment, and as many period columns as apply.
    sort_by: 1-yr, 1-mo YtD etc
    midpoint: 0 or None
    colorbar, reverse, to_return: boolean
    """
    if df is None: 
        return _plot_none(chart_title=chart_title, width=width, height=height)
    
    else:
        # Filter out rows for which the sort_by column is NaN
        df = df[df[sort_by].notnull()]

        # Full name
        name = "<br>%{customdata[0]}"
        
        # Data frame columns except symbol, name and segment
        cols = [i for i in df.columns if i not in ['symbol','name','segment']]
        
        # Map periods to customdata values 
        dd = {}
        for ind, per in enumerate(cols): dd[per] = ["<br>"+per+": ","%{customdata["+str(ind+1)+"]:.2%}"]
        
        # Construct hover template by flattening the dictionary values
        hover = "%{parent} - %{label}"+name+'<br>'+chart_title+':'+\
                        ''.join([str(k) for elem in dd for k in dd[elem]])
        
        # Configure colors order
        if reverse: colors = _cmx_colors[::-1]
        else: colors = _cmx_colors

        # Treemap figure
        if frame:
            frame = 'Assets Monitor: '+chart_title+ ' - '+sort_by
        else:
            frame = 'All Assets'

        fig = _px.treemap(df,
                    color=sort_by,hover_data=['name']+list(dd.keys()),
                    color_continuous_scale=colors,
                    color_continuous_midpoint=midpoint,
                    path=[_px.Constant(frame),'segment','symbol'],
                    width=width,height=height)
        
        # Configure hover and text templates
        fig.data[0].texttemplate = "%{label}<br>"+dd[sort_by][1]
        fig = fig.update_layout(coloraxis_showscale=colorbar).update_traces(hovertemplate=hover)
        
        # Show or return the plot
        if to_return==False:
            fig.show()
        
        else:
            return fig 

# --------------------------------------------------------------------------------------------
def plot_barchart(df, sort_by='1-yr', chart_title='Cum. Returns', show_range=True, legend=True, to_return=False, width=720, height=360):

    if df is None: 
        return _plot_none(chart_title=chart_title, width=width, height=height)
    
    else:
        opacity = 0.8

        # Filter data by the selected period
        df = df[df[sort_by].notnull()]

        # Plot bar chart
        fig = _px.bar(df, x=df.index, y=df[sort_by], template=_charts_template,
                     color='segment',  color_discrete_sequence=_cool_colors[1:], hover_data=['name','segment'])
        
        # Remove white border from bars
        fig = fig.update_traces(marker_line_width=0, selector=dict(type="bar"))
        
        # Adjust title if period is "custom"
        if show_range:
            if sort_by=='Custom':
                chart_title = chart_title + ' - custom date range'
            else:
                chart_title = chart_title+': '+sort_by
        
        # Make further format / layout modifications with _text_layout
        fig = _text_layout(fig=fig, title=chart_title, legend=legend, width=width, height=height)
        
        # If there's portfolio data, draw a horizontal line
        if 'PORT' in df[sort_by].index:
            fig = fig.add_hline(y=df[sort_by].loc['PORT'], line_width=1.5, line_dash="dot", line_color="black", opacity=opacity)
        
        # Axis format
        yformat = _chart_format_dict['Percent'][1]

        # Hover format
        very_custom_hover = "Segment: %{customdata[1]}<br>Asset: %{x}<br>Value: %{y:.1%}<br>Name: %{customdata[0]}<extra></extra>"

        # Update axis and hover formats
        fig = fig.update_yaxes(tickformat=yformat).update_traces(hovertemplate=very_custom_hover)
    
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
def _template_line(df=None, chart_title=None, legend=True, width=720, height=360, template=_charts_template):
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
            # xaxis = {"gridcolor": "#E1E5ED"},
            # yaxis = {"gridcolor": "#E1E5ED"},
            # plot_bgcolor='white',
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
def _text_layout(fig, title, legend, width, height):
    
    fig = fig.update_layout(font = dict(color="#505050", size=10, family='sans-serif'),
                            width = width, height = height,
                            showlegend = legend, legend_title = None,
                            margin = {'l':0, 't':25, 'r':10, 'b':0, 'pad':0},
                            title = {'text':title, 'xref':'paper', 'x':1, 'xanchor': 'right',
                                     'font':{'size':15, 'family':'sans-serif'}})
    
    fig = fig.update_xaxes(categoryorder='total descending',title_text='').update_yaxes(title_text='')
    
    return fig

# --------------------------------------------------------------------------------------------
def _add_space(df, fig):
    """ """
    x0 = df.index[-1]
    x1 = x0+_timedelta(days=21)
    fig = fig.add_vrect(x0=x0, x1=x1, col=1, opacity=0.05)

    return fig

# --------------------------------------------------------------------------------------------
def _ffill(df):
    """ """
    df = _pd.DataFrame(df).ffill().copy()
    return df