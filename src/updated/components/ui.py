import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, dash_table

def btn_grp(id: str, label: str, options: list, value: str):
    """Custome Button Group """
    return dbc.Row(
        [
            dbc.Col(
                dbc.Label(label, className="small text-cxenter "),width="auto"
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
                ),
                width=5
            ),
            dbc.Col(
                dbc.Button(
                    ["Update Threshold"],
                    id=btn_id,
                    size="sm",
                    color="outline-primary"
                ),
                width="auto"
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
    
    

    
    

if __name__ == "__main__":
    
    def render(content):
        return dbc.Container(
            fluid=True,
            className="p-0 m-0 h-100",
            children=[
                dbc.Row(
                    className="g-0 h-100",  # g-0 removes gutters, h-100 for full height
                    children=[
                        # Main content area
                        dbc.Col(
                            id={"type": "main-content", "uid":"uid"},
                            width=9,
                            className="bg-danger d-flex flex-column overflow-hidden p-2",
                            children=[                        
                                # html.Div(
                                #     className="d-flex justify-content-center align-items-center h-100",
                                #     children=dbc.Spinner(
                                #         size="lg",
                                #         color="primary",
                                #         fullscreen=True
                                #     )
                                # ),
                            ]
                        ),
                        # Sidebar area - 25% (width 3)
                        dbc.Col(
                            width=3,
                            className="bg-secondary text-white p-3 h-100 overflow-auto",
                            children=[
                                dbc.Card(
                                    className="mb-2",
                                    children=[
                                    dbc.CardHeader("Card"),
                                    dbc.CardBody(content) 
                                    ]
                                )
                            ]
                        )
                    ]
                )
            ]
        )
    
    
    
    
    
    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
    
    
    app.layout = render([
        tabs(
                id="tabs-demo",
                options=[
                    {"label": "Table", "tab_id": "table", "children": table(id="table")},
                    {"label": "Tab 2", "tab_id": "tab-2", "children": html.Div("Content 2")},
                ],
            )
    ])
    
    
    
    
    
    
    
    
    # app.layout = render([
    #     tabs(
    #             id="tabs-demo",
    #             options=[
    #                 {"label": "Tab 1", "tab_id": "tab-1", "children": html.Div("Content 1")},
    #                 {"label": "Tab 2", "tab_id": "tab-2", "children": html.Div("Content 2")},
    #             ],
    #         )
    # ])
    
    

    # app.layout = dbc.Container(
    #     [
    #         html.H2("PyCoregnet UI Components Demo"),
    #         tabs(
    #             id="tabs-demo",
    #             options=[
    #                 {"label": "Tab 1", "tab_id": "tab-1", "children": html.Div("Content 1")},
    #                 {"label": "Tab 2", "tab_id": "tab-2", "children": html.Div("Content 2")},
    #             ],
    #             value="tab-1"
    #         ),
    #         html.Hr(),
    #         html.H4("Demo Table"),
    #         table(
    #             id="demo-table",
    #             data=[
    #                 {"Name": "Alice", "Age": 30},
    #                 {"Name": "Bob", "Age": 25},
    #                 {"Name": "Charlie", "Age": 35}
    #             ],
    #             columns=[
    #                 {"name": "Name", "id": "Name"},
    #                 {"name": "Age", "id": "Age"}
    #             ]
    #         ),
    #     ],
    #     fluid=True,
    #     className="p-4"
    # )

    app.run(debug=True)