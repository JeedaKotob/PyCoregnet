import dash
import dash_bootstrap_components as dbc
from dash import html
from dash import dcc

def tabs(id: str, options: list, value: str):
    return dbc.Tabs(
        id=id,
        # active_tab=value,
        active_tab=options[0]['tab_id'], #The active tab is the first element of the options list
        className="justify-content-center text-black border-0",
        children=[
            dbc.Tab(
                label=option['label'],
                tab_id=option['tab_id'],
                labelClassName='text-black border-0',
                activeLabelClassName='text-black border-0 border-bottom border-primary border-3',
                activeTabClassName='text-black border-0'
            ) for option in options
        ]
    )
    
    

def button_group(id: str, label: str, options: list, value: str, visible = True):

    return dbc.Row(
        [
            dbc.Col(
                dbc.Label(label, className="small text-center "),width="auto"
            ),
            dbc.Col(
                dbc.RadioItems(
                    id=id,
                    className="btn-group btn-group-sm",
                    inputClassName="btn-check",
                    labelClassName="btn btn-outline-primary btn-sm text-center",
                    labelCheckedClassName="active btn-sm",
                    options=options,
                    value=value,
                ),
                width="auto"
            ),
        ],
        justify="between",
        align="center",
        className="mb-3" if visible else "d-none"
    )

def threshold_input(id: str, label: str, visible=True):
    btn_id = {}
    btn_id["type"]  = f"{id["type"]}-btn"
    btn_id['uid'] = id['uid']
    return dbc.Row([
        dbc.Col(dbc.Input(id=id, type='number', value=label, min=1,size="sm", placeholder=label), width=5),
        dbc.Col(dbc.Button(["Update Threshold"], id=btn_id, size="sm", color="outline-primary"), width="auto"),
    ], align="center", justify="between", className="mb-3" if visible else "d-none")


def stat_card():
    """
        @callback(
        [Output("total_nodes", "children"),
        Output("total_edges", "children"),
        Output("selected_nodes", "children"),
        Output("selected_edges", "children")],
        Input("node-mode-btns", "value"),  # Optional, if using selection
    )
    def update_stats(figure):
        return 930,7902,1,128000    
    """
    
    def box(label, num_id):
        return dbc.Card(
            dbc.CardBody([
                html.H6("0",id=num_id, className="text-center fw-bold"),
                html.Small(label, className="text-center text-muted d-block")
            ]),
            className="h-100"
        )

    return dbc.Card(className="mb-2",children=[
            dbc.CardHeader("Network stats"),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col(box("Total Nodes", "total_nodes"), width=6),
                    dbc.Col(box("Total Edges", "total_edges"), width=6),
                ], className="mb-2", align="stretch"),
                
                dbc.Row([
                    dbc.Col(box("Selected Nodes", "selected_nodes"), width=6),
                    dbc.Col(box("Selected Edges", "selected_edges"), width=6),
                ], align="stretch"),
            ])
            ])


    
def stat_box(stats: list):
    def cell(text,id):

        return dbc.Col([
            dbc.Row([
            dbc.Col([html.Small(text, className="text-center text-muted fw-bold")], width=6, className="d-flex justify-content-center align-items-center"),
            dbc.Col([html.Div(id=id, className="p-2 bg-secondary text-center text-white rounded fw-bold")], width=6, className="d-flex justify-content-center align-items-center"),
            ])
        ], width=6, className="d-flex justify-content-center align-items-center")
    
    return dbc.Row([
        cell(stat["name"], stat["id"]) for stat in stats
    ])
    