import dash_bootstrap_components as dbc
from dash import html
from .filters_dropdowns import dropdown_securities_list, checklist_securities_list


# --------------------------------------------------------------------------------------------------------------
# Securities selection modal
modal_header = dbc.ModalHeader(dbc.ModalTitle("Search & select securities"),close_button=False)


accordion = html.Div( dbc.Accordion(
                                    [
                                        dbc.AccordionItem(
                                            dropdown_securities_list,
                                            title="Select Securities 1"
                                        ),

                                        # dbc.AccordionItem(
                                        #     checklist_securities_list,
                                        #     title="Select Securities"
                                        # )
                                    ],
                                    flush=True,
                                ),
                            )

modal_body = dbc.ModalBody(children=[dbc.CardBody(dropdown_securities_list)])


modal_footer = dbc.ModalFooter(
                            dbc.Button("Close tab",
                                       id='modal-button-close',
                                       n_clicks=0)
                            )


modal = html.Div(children=[dbc.Modal(children=[modal_header,modal_body,modal_footer],
                            id='modal-securities',
                            is_open=False,
                            backdrop="static",
                            scrollable=True,
                            centered=True),
                            dbc.Button("Securities Search", id='modal-button-open', n_clicks=0)]
                            )
# --------------------------------------------------------------------------------------------------------------
