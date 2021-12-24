from dash import dcc

# --------------------------------------------------------------------------------------------------------------
slider_lookback_days_port = dcc.Slider(id='slider_lookback_days_port',
        min=5,max=126,step=None,
        marks={5:'',10:'',21:'',45:'',63:'',126:''},
        value=45
    )
# --------------------------------------------------------------------------------------------------------------
slider_forward_days_port = dcc.Slider(id='slider_forward_days_port',
        min=1,max=63,step=None,
        marks={1:'',5:'',21:'',63:'',},
        value=21
    )