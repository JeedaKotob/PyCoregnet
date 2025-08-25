import dash
from dash import Dash, dcc, html, Input, Output, State, callback, no_update, callback_context,ctx
import dash_cytoscape as cyto
import dash_bootstrap_components as dbc
import pandas as pd
import logging

# BaseNetworkGraph
from components import ui as UIC
from components import backend as BEC

from assets.stylesheet import full_network_stylesheet 
import utils

dash.register_page(__name__, path='/new')

layout = dbc.Container()

GRAPH = "fullbipartitenetwork"



graph_tabs = UIC.tabs(id="graph-tabs", value="fullbipartitenetwork",
    options=[
        {'label': 'Full Bipartite Network', 'tab_id': 'fullbipartitenetwork'},
        {'label': 'Coregulators Network', 'tab_id': 'coregulatorsnetwork'},
        {'label': 'Coregulated Graph', 'tab_id': 'coregulatedgraph'},
        {'label': 'Network Graph Layout', 'tab_id': 'networkgraphlayout'}
    ],
)


layout = dbc.Container( className="network-graph-layout dash-page-container-child", fluid=True,
    children=[
        dcc.Store(id="selected_nodes",data={"selected" : [], "node_mode" : "single", "node_type" : "both", "backtracking" : False}),
        # Network Graph View
        html.Div(
            className="cyto-graph-wrapper",
            id="cy-wrapper",
            children=[
                graph_tabs,
                html.Div(
                    dbc.Spinner(
                    size="lg",
                    color="primary",
                    ),
                    style={'flex': '1', 'display': 'flex', 'justify-content': 'center', 'alignItems': 'center'},
                )
            ],
        ),
        
        # Network Controls View
        dbc.Container(className="network-controls",
            children=[
                # Graph Controls
                dbc.Container( id="", className="network-controls-section",
                    children=[
                        
                        html.H4("Graph Controls"),
                        
                        UIC.button_group(id="node-mode-btns", label="Mode", value="single",
                            options=[
                                {'label': 'Single', 'value': 'single'},
                                {'label': 'off', 'value': 'off'},
                                {'label': 'Multiple', 'value': 'multiple'},
                            ],
                        ),
                        UIC.button_group(id="node-type-btns",label="Highlight Type", value="both",
                            options=[
                                {'label': 'Target', 'value': 'target'},
                                {'label': 'Both', 'value': 'both'},
                                {'label': 'TF', 'value': 'tf'},
                            ],
                        ),
                        UIC.button_group(id="backtracking-bool-btns", label="Backtracking", value="False",
                            options=[
                                {'label': 'On', 'value': 'True'},
                                {'label': 'Off', 'value': 'False'},
                            ],
                        ),
                ]),
                
                dbc.Container( id="", className="network-controls-section",
                    children=[
                        html.H4("Node Inspector"),
                        html.Label("Search for a Gene or Node"),
                        dcc.Dropdown(
                            id='graph-dropdown',
                            placeholder='Select a node...',
                            style={'fontFamily': 'monospace'},
                            options=[],
                            multi=True,
                        ),
                        UIC.tabs(id="info-content",value="regulation",
                            options=[
                            {'label': 'Regulation', 'tab_id': 'regulation'},
                            {'label': 'Gene Expression', 'tab_id': 'expression'}
                            ],
                        ),
                        html.Div(
                            id='content'
                        )         
                    ]
                ), 

                
                dbc.Button("Reset Graph", id="full-reset-button", outline=True, color="secondary", className="me-1 w-100 text-primary bg-white"),
            ]#network-controls children
        )#network-controls
    ]#network-graph-layout children
)#network-graph-layout



# NOTE: This is responsible for:
# 1- Cache the full_net data 
    # dcc.Store cant handle large data 
    # prevent constant running
# 2- loading icon -> cyto.Cytoscape
@callback(
    Output("cy-wrapper","children"),
    Input("cy-wrapper","children"),
    Input("graph-tabs", "active_tab"), 
)
def load_graph(children : list,active_tab :str):
    
    from dash import get_app
    app = get_app()
    cache = app.server.config["APP_CACHE"]

    graph_net = cache.get(GRAPH)
    
    if not graph_net :
        graph_net = utils.create_full_network(utils.grn)
        cache.set(GRAPH,graph_net)
         
    elements = graph_net['nodes'] + graph_net['edges']
        
    children[1] = cyto.Cytoscape(
        id='network-graph',
        layout={'name': 'preset', 'fit': True},
        style={'flex-grow': '1', 'box-sizing': 'border-box'},
        minZoom=0.1,
        maxZoom=2,
        elements=elements,
        stylesheet=full_network_stylesheet,
    )
    
    return children


#  SET OPTIONS SYNCED FROM the centralized store (defualt)
@callback(
    [
        Output("graph-dropdown","options"),
        Output("graph-dropdown","multi"),
        Output('graph-dropdown', 'disabled'),
    ],
    Input("selected_nodes", "data"),
)
def set_dropdown(store):
    node_mode = store['node_mode'] # Either single,off,multiple

    if node_mode == "single":
        multi = False
    elif node_mode == "multiple":
        multi = True
    else:
        return no_update,no_update,True
        
    node_type = store['node_type'] # Either target,both,tf
    
    from dash import get_app
    app = get_app()
    cache = app.server.config["APP_CACHE"]
    graph_net = cache.get(GRAPH)
    
    # TODO IF Fail Refresh
    if not graph_net:
        import time 
        time.sleep(2)
        graph_net = cache.get(GRAPH)
    
    
    # TODO Optomize
    # make cache.set("dropdown",[dropdown_options = options['tf] + options['target] ])
    options = [{
        'label': f"{node['data']['id']}   ({node['data']['type']})",
        'value': node['data']['id'],
    } for node in graph_net['nodes']]
    
    if node_type == "tf":
        options =  [node for node in options if "(tf)" in node['label']]
    elif node_type == "target":
        options = [node for node in options if "(target)" in node['label']]
        
    return options,multi,False
            

# CENTRALIZED STORE SYNC ALL CALLBACKS
@callback(
    [
        Output("selected_nodes", "data"),
        Output("graph-dropdown", "value"),
    ],
    [
        Input("network-graph", "tapNodeData"),
        Input("graph-dropdown", "value"),
        Input("node-mode-btns","value"), # node mode (Single , Off ,Multiple)
        Input("node-type-btns","value"), # node type (Targets, both , Tfs)
        Input("backtracking-bool-btns","value"), # Allow Backtrack (True/False) 
    ],
    State("selected_nodes", "data"),
    prevent_initial_call=True,
)
def sync(tapNodeData, dropdown_value,node_mode,node_type,backtracking,store):
    trigger = ctx.triggered_id
    
    store['node_mode'] = node_mode
    store['node_type'] = node_type
    store['backtracking'] = backtracking
    
    # NOTE : Output of tapNodeData['id'] : str 
    # NOTE : Input of dropdown_value: str when node_mode == single
    # NOTE : Input of dropdown_value: list when node_mode == multiple
    # NOTE NOTE NOTE store['selected'] SHOUDL ALWAYS BE TYPE LIST
    
    
    if trigger == "network-graph" and tapNodeData:
        if store['node_mode'] == 'single':
            sel = tapNodeData['id']
            store["selected"] = [sel]
            return store, sel
        elif store['node_mode'] == 'multiple':
            temp = set(store["selected"])
            temp.add(tapNodeData['id'])
            store["selected"] = list(temp)
            return store , store["selected"]
            

    if trigger == "graph-dropdown":
        
        if not dropdown_value:
            store['selected'] = []
            return store , no_update
        
        
        if store['node_mode'] == 'single':
            store["selected"] = [dropdown_value]
            return store, dropdown_value
        elif store['node_mode'] == 'multiple':
            temp = set(store['selected'])
            temp.update(dropdown_value)
            
            if len(temp) > len(dropdown_value):
                temp = dropdown_value
            
            store['selected'] = list(temp)
        
            return store, dropdown_value
    
    return store, no_update


@callback(
    Output("network-graph","elements"),
    Input("network-graph","elements"), 
    Input("selected_nodes","data"),
    prevent_initial_call=True
)
def highlightor(elements ,store ):
    selected = set(store['selected'])


    if not selected:
        for d in elements:
            d['classes'] = ''
        return elements

    connected_nodes = set()
    
    nodes = [e.copy() for e in elements if 'source' not in e['data']]
    edges = [e.copy() for e in elements if 'source' in e['data']]
    # edge = {{'data': {'id': 'SPOCD1->A2ML1', 'source': 'SPOCD1', 'target': 'A2ML1', 'interaction_type': 'Repression'}}
    for edge in edges:
        src = edge['data']['source']
        tgt = edge['data']['target']        
        if selected & {src, tgt}:
            edge['classes'] = "highlighted-edge"
            connected_nodes.update([src, tgt])
        else:
            edge['classes'] = "faded"
            
    
    # node = {'data': {'id': 'A2ML1', 'type': 'target'}, 'position': {'x': 2735, 'y': 194}}
    for node in nodes:
        nid = node['data']['id']
        if nid in selected:
            node['classes'] = 'highlighted'
        elif nid in connected_nodes:
            node['classes'] = ''
        else:
            node['classes'] = 'faded'
    
    elements = nodes + edges    
    
    return elements


@callback(
    Output('content','children'),
    Input("selected_nodes","data"),
    Input('info-content','active_tab'),
)
def content(store,value):
    selected = store['selected']
    
    if not selected:
        return []
    
    if value == "regulation":
        return BEC.regulation_table(selected,utils.grn)
    else:
        return  dcc.Graph(figure=BEC.get_heat_map("./CIT_BLCA_EXP.csv",selected))
    
    