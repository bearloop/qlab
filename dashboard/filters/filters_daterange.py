from datetime import datetime as dtt
from datetime import timedelta
from dash import dcc


dranged = dcc.DatePickerRange(  id='date-picker-range',
                                show_outside_days=False,
                                day_size=32,
                                number_of_months_shown=2,
                                display_format='DD/MM/YYYY',
                                clearable=False,
                                minimum_nights=7,
                                with_portal=True
                            )