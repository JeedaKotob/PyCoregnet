import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, dash_table

def btn_grp(id: str, label: str, options: list, value: str):
    """Custome Button Group """
    return dbc.Row(
        [
            dbc.Col(
                dbc.Label(label, className="small text-cxenter ")
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
                )
            ),
        ],
        justify="between",
        align="center",
        className="mb-3" 
    )

def thresh_input(id: dict, label: str):
    btn_id = id.copy()
    btn_id['type'] = btn_id['type'] + '_btn'
    return dbc.Row(
        [
            dbc.Col(
                dbc.Input(
                    id=id,
                    type='number',
                    min=1,
                    size="sm",
                    placeholder=label
                )
            ),
            dbc.Col(
                dbc.Button(
                    ["Update Threshold"],
                    id=btn_id,
                    size="sm",
                    color="outline-primary"
                )
            ),
        ],
        align="center",
        justify="between",
        className="mb-3"
    )

def dropdown(id : str, label : str, options = []):
    return dbc.Row([
        dbc.Row(html.Label(label), className="mb-2"),
        dbc.Row(dcc.Dropdown(id=id,className="mb-2",options=options))
        ])


def table(id):
    return dash_table.DataTable(
            id=id,
            page_size=10,
            style_cell={
                'textAlign': 'center',
                'fontFamily': "'Inter', sans-serif",
                'fontSize': '14px',
                'borderBottom': '1px solid #ccc',
                'borderLeft': 'none',
                'borderRight': 'none',
                'borderTop': 'none'
            },
            style_header={
                'fontWeight': 'bold',
                'backgroundColor': 'white',
                'borderBottom': '1px solid #ccc',
                'borderLeft': 'none',
                'borderRight': 'none',
                'borderTop': 'none'
            },
        )


def tabs(id: str, options: list ):#, value: str):
    return dbc.Tabs(
        id=id,
        className="justify-content-center text-black border-0",
        active_tab=None,
        # active_tab=value,
        children=[
            dbc.Tab(
                children=option['children'],
                label=option['label'],
                tab_id=option['tab_id'],
                # tab_id={"type": option['tab_id'], "uid": id['uid']},
                labelClassName='text-black border-0',
                activeLabelClassName='text-black border-0 border-bottom border-primary border-3',
                activeTabClassName='text-black border-0'
            ) for option in options
        ]
    )
    
# def tabs(id: str, options: list ):#, value: str):
def tabs(id: str, options: list, value: str):
    return dbc.Card([
            dbc.CardHeader([
                dbc.Tabs(
                id=id,
                className="d-flex justify-content-evenly text-black border-0",
                # active_tab=None,
                children=[
                    dbc.Tab(
                        label=option['label'],
                        # tab_id=option['tab_id'],
                        tab_id=valueId,
                        labelClassName='text-black border-0',
                        activeLabelClassName='text-black border-0 border-bottom border-primary border-3',
                        activeTabClassName='text-black border-0'
                    ) for option,valueId in zip(options,value)
                ]
            )
        ], style={"backgroundColor": "transparent"}),    
        dbc.CardBody(id={"type": f"{id['type']}_content", "uid": id['uid']}, style={"backgroundColor": "transparent", "height": "50vh"}),
    ], style={"backgroundColor": "transparent"}, className="d-flex flex-1")
    
    

def network_stats(id: str):
    uid = id['uid']
    return dbc.Container([
        dbc.Row([
            dbc.Col(dbc.Label("Total: ", className="small text-cxenter")),
            dbc.Col([
                html.Span(id={"type": "total_nodes", "uid": uid}, children="0"),
                " nodes | ",
                html.Span(id={"type": "total_edges", "uid": uid}, children="0"),
                " edges"
            ], className="small text-cxenter"),
        ], className="flex-nowrap text-nowrap"),
        dbc.Row([
            dbc.Col(dbc.Label("Selected: ", className="small text-cxenter")),
            dbc.Col([
                html.Span(id={"type": "selected_nodes", "uid": uid}, children="0"),
                " nodes | ",
                html.Span(id={"type": "selected_edges", "uid": uid}, children="0"),
                " edges"
            ], className="small text-cxenter"),
        ], className="flex-nowrap text-nowrap"),
    ])
    

# id={"type": "total_edges", "uid": id}
# id={"type": "selected_nodes", "uid": id}
# id={"type": "selected_edges", "uid": id}

def get_heat_map(genes,filepath):
    import pandas as pd
    import plotly.graph_objects as go
    ne=pd.read_csv(filepath,index_col=0)
    if isinstance(genes,str):
        genes=[genes]

    selected_df = ne.loc[genes].T
    global_mean=ne.values.mean()
    z_scores=selected_df-global_mean
    zmin = z_scores.min().min()
    zmax = z_scores.max().max()

    n_genes = len(z_scores.columns)
    n_samples = len(z_scores.index)
    
    heatmap_width = min(1000, max(300, 20 * n_genes))
    heatmap_height = min(900, max(300, 20 * n_samples))

    heatmap=go.Figure(data=go.Heatmap(
        z=z_scores.values,
        x=z_scores.columns,
        y=z_scores.index,
        zmin=zmin,
        zmax=zmax,
        colorscale=[
            [0, "red"],   
            [0.5, "black"], 
            [1, "green"]   
        ]
    ))
    heatmap.update_layout(
        xaxis=dict(showticklabels=False),
        yaxis=dict(showticklabels=False),
        xaxis_title="Genes",
        yaxis_title="Samples"
    
    )
    return dcc.Graph(figure=heatmap)
    
    

    
    
