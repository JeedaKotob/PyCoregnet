import os

import dash
from dash import dcc, html, Input, Output, State, callback, no_update, callback_context,ctx,MATCH
import dash_cytoscape as cyto
import dash_bootstrap_components as dbc
import pandas as pd


dash.register_page(__name__, path='/')


def scan_files(directory):
    csv_files = []
    json_files = []

    for file in os.listdir(directory):
        if file.endswith('.csv'):
            csv_files.append(file)
        elif file.endswith('.json'):
            json_files.append(file)

    return csv_files, json_files




layout = dbc.Container(fluid=True, className="min-vh-100 bg-light", children=[
    dcc.Store(id="data-manager"),
    dcc.Location(id="url"),
    
    # Header Section
    dbc.Row(className="py-5 text-center", children=[
        dbc.Col(className="mx-auto", width=8, children=[
            html.H1("PyCoregNet", className="display-4 fw-bold text-primary mb-3"),
            html.P("Gene Co-regulation Network Analysis Platform", 
                   className="lead text-muted mb-4"),
            html.P("Upload your expression data (CSV) and network structure (JSON) to begin analysis", 
                   className="text-secondary mb-0")
        ])
    ]),
    
    # Main Content Section
    dbc.Row(className="py-4", justify="center", children=[
        dbc.Col(width=10, children=[
            dbc.Row(className="g-4", children=[
                # CSV Upload Section
                dbc.Col(md=6, children=[
                    dbc.Card(className="h-100 border-0 shadow-sm", children=[
                        dbc.CardBody(className="p-4", children=[
                            html.H4("Expression Data", className="card-title text-primary mb-3"),
                            html.P("Select your gene expression CSV file", 
                                   className="card-text text-muted mb-3"),
                            dcc.Dropdown(
                                id="csv-dropdown",
                                placeholder="Choose CSV file...",
                                className="mb-3"
                            ),
                            # Metadata section for CSV
                            html.Div(id="csv-metadata", className="mt-3", children=[
                                html.H6("File Information", className="text-secondary mb-2"),
                                html.Div(className="p-3 bg-light rounded", id="csv-metadata",children=[
                                    html.Small("No file selected", className="text-muted")
                                ])
                            ])
                        ])
                    ])
                ]),
                
                # JSON Upload Section
                dbc.Col(md=6, children=[
                    dbc.Card(className="h-100 border-0 shadow-sm", children=[
                        dbc.CardBody(className="p-4", children=[
                            html.H4("Network Structure", className="card-title text-primary mb-3"),
                            html.P("Select your network topology JSON file", 
                                   className="card-text text-muted mb-3"),
                            dcc.Dropdown(
                                id="json-dropdown",
                                placeholder="Choose JSON file...",
                                className="mb-3"
                            ),
                            # Metadata section for JSON
                            html.Div(id="json-metadata", className="mt-3", children=[
                                html.H6("File Information", className="text-secondary mb-2"),
                                html.Div(className="p-3 bg-light rounded",id="json-metadata", children=[
                                    html.Small("No file selected", className="text-muted")
                                ])
                            ])
                        ])
                    ])
                ])
            ])
        ])
    ]),
    
    # Action Section
    dbc.Row(className="py-4 text-center", children=[
        dbc.Col(children=[
            dbc.Button(
                "Proceed to Analysis",
                color="primary",
                size="lg",
                className="px-5 py-2",
                disabled=True,
                id="proceed-btn"
            )
        ])
    ])
])

# directory = os.path.dirname(os.path.abspath(__file__))
# csv_files, json_files = scan_files(directory)


@callback(
    [
        Output("csv-dropdown", "options"),
        Output("json-dropdown", "options"),
    ],
    Input("url", "pathname")
)
def list_files(pathname):

    directory = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    csv_files, json_files = scan_files(directory)
    return csv_files, json_files
    
    


@callback(
    [
        Output("data-manager","data"),
        Output("csv-metadata","children"),
        Output("json-metadata","children"),
    ],
    Input("csv-dropdown","value"),
    Input("json-dropdown","value"),
    State("data-manager","data"),
)
def import_data(csv_value : str,json_value : str, data_store):
    
    
    csv_info=json_info = no_update
    
    if not data_store:
        data_store = {"grn": None, "ne" : None}
    
    if csv_value:
        csv_value = "./" + csv_value
        ne = pd.read_csv(csv_value)
        csv_info = str({"rows" : ne.shape[0], "columns" : ne.shape[1]})
    
    if json_value:
        json_value = "./" + json_value
        
        grn_obj = GRNHandler(json_value)
        if grn_obj.is_valid:
            data_store['grn'] = json_value
            json_info = str(grn_obj.meta_data)
        else:
            json_info = grn_obj.error_message
    
    

    

    
        
    
    
    return data_store,csv_info,json_info
    
    