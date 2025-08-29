import dash
from dash import Dash, dcc, html, Input, Output, State, callback, no_update, callback_context,ctx, MATCH, ALL
import dash_cytoscape as cyto
import dash_bootstrap_components as dbc
import pandas as pd
cyto.load_extra_layouts()

from components.ui import tabs, button_group,stat_box,threshold_input

total_nodes=total_edges=threshold=0


class BaseNetworkGraph:
    def __init__(
        self,
        store=None, 
        preprocess=None,
        create_network=None,
        stylesheet=None,
        graph_layout=None,
        dropdown_options = None,
        threshold = None,
        content = None,
        
        ):
        
        self.store = store
        self.uid = self.store['graph']
        
        self.preprocess = preprocess
        self.create_network = create_network
        self.stylesheet = stylesheet
        self.graph_layout = graph_layout
        
        self.dropdown_options = dropdown_options
        self.threshold = threshold
        self.content = content

        
        
    def get_layout(self):
        
        graph_tabs = tabs(id={"type": "graph-tabs", "uid": self.uid}, value="full",
            options=[
            {'label': 'Full Bipartite Network', 'tab_id': 'full'},
            {'label': 'Coregulators Network', 'tab_id': 'coregs'},
            {'label': 'Coregulated Network', 'tab_id': 'coregulated'},
            ],
        )

        def check(key, store = self.store):
            if store[key]:
                return True
            elif store[key] == 0:
                return True
            else: 
                return False
        
        


        layout = dbc.Container(
                fluid=True,
                className="p-0 m-0 h-100",
                children=[
                    dcc.Store(id={"type": "store", "uid": self.uid}, data=self.store),
                    dbc.Row(
                        className="g-0 h-100",  # g-0 removes gutters, h-100 for full height
                        children=[
                            # Main content area - 75%
                            dbc.Col(
                                id={"type" : "main-content", "uid" : self.uid},
                                width=9,  # 9/12 = 75%
                                className="bg-light d-flex flex-column overflow-hidden",
                                children=[
                                    graph_tabs,
                                    html.Div(
                                        className="d-flex justify-content-center align-items-center h-100",
                                        children=[
                                            dbc.Spinner(
                                                size="lg",
                                                color="primary",
                                            )
                                        ]
                                    ),
                                ]
                            ),
                            # Sidebar area - 25%
                            dbc.Col(
                                width=3,  # 3/12 = 25%
                                className="bg-secondary text-white p-3 h-100 overflow-auto",
                                children=[
                                    
                                    dbc.Card(className="mb-2",children=[
                                        dbc.CardHeader("Network stats"),
                                        dbc.CardBody(stat_box(stats=[
                                            {"name" : "Total Nodes", "id" : {"type": "total_nodes", "uid": self.uid}},
                                            {"name" : "Total Edges", "id" : {"type": "total_edges", "uid": self.uid}}
                                            ])),
                                        dbc.CardBody(stat_box(stats=[
                                            {"name" : "Selected Nodes", "id" : {"type": "selected_nodes", "uid": self.uid}},
                                            {"name" : "Selected Edges", "id" : {"type": "selected_edges", "uid": self.uid}}
                                            ])),
                                    ]),
                                    
                                    
                                    dbc.Card(className="mb-2",children=[
                                            dbc.CardHeader("Graph controls"),
                                            dbc.CardBody([
                                                button_group(id={"type" : "selection-mode-btns", "uid" : self.uid}, label="Selection", value="single",
                                                    options=[
                                                        {'label': 'Single', 'value': 'single'},
                                                        {'label': 'off', 'value': 'off'},
                                                        {'label': 'Multiple', 'value': 'multiple'},
                                                    ],visible=check("selection_mode")),
                                                button_group(id={"type" : "filter-mode-btns", "uid" : self.uid},label="Filter By", value="both",
                                                    options=[
                                                        {'label': 'Target', 'value': 'target'},
                                                        {'label': 'Both', 'value': 'both'},
                                                        {'label': 'TF', 'value': 'tf'},
                                                    ],visible=check("filter_mode")),
                                                button_group(id={"type" : "backtracking-mode-btns", "uid" : self.uid}, label="Backtracking", value="False",
                                                    options=[
                                                        {'label': 'On', 'value': 'True'},
                                                        {'label': 'Off', 'value': 'False'},
                                                    ],visible=check("backtracking")),
                                                threshold_input(id={"type" : "threshold", "uid" : self.uid},label="Threshold",visible=check("threshold")),                                        
                                                ])]),
                                    
                                    dbc.Card(className="mb-2",children=[
                                        dbc.CardHeader("Node Inspector"),
                                        dbc.CardBody([
                                            dbc.Row(html.Label("Highlight Node"),className="mb-2"),
                                            dbc.Row(dcc.Dropdown(id={"type" : "dropdown", "uid" : self.uid},className="mb-2")),
                                            tabs(id={"type": "inspector-table", "uid": self.uid},
                                                options=[
                                                    { "label":key, "tab_id" : key.lower()} for key in self.content.keys()
                                                    ],value=None),
                                            dbc.Row(id={"type": "content", "uid": self.uid},className="d-flex",style={'height': '50vh'})
                                        ]),
                                        # dbc.Row(html.H2("Please Select A Node"))
                                        
                                    ]),                        
                                    
                                    dbc.Row(className="mb-2",children=[
                                        dbc.Col(dbc.Button("Reset Graph", id={"type": "full-reset-button", "uid": self.uid}, outline=True, color="secondary", className="me-1 w-100 text-primary bg-white"),width=6),
                                        dbc.Col(dbc.Button("Reset All", id={"type": "full-reset-button-2", "uid": self.uid}, outline=True, color="secondary", className="me-1 w-100 text-primary bg-white"),width=6),
                                    ]),
                                    
                                    dbc.Row(style={'height': '50vh'})
                                    
                                ]
                            )
                        ]
                    )
                ]
        )
        return layout

    def register_callbacks(self, app):
        
        # CENTRALIZED STORE SYNC ALL CALLBACKS    
        @app.callback(
            [
                Output({"type": "main-content", "uid": self.uid}, "children"),
                Output({"type": "threshold", "uid": self.uid}, "value"),
            ],
            Input({"type": "main-content", "uid": self.uid}, "children"),
            Input({"type": "threshold-btn", "uid": self.uid},"n_clicks"), 
            State({"type": "threshold", "uid": self.uid},"value"), # Allow Backtrack (True/False) 
        )
        def load_graph(children : list, threshold_btn , n_threshold ):

            uid = self.uid
            global threshold, total_nodes, total_edges
            
            from dash import get_app
            app = get_app()
            cache = app.server.config["APP_CACHE"]
            
            # The graph_data is specific to the graph
            # If full then save graph_data {graph_net['nodes'] , graph_net['edges']}
            # If targets,tf then save targets,tfs not {graph_net['nodes'] , graph_net['edges']}
            graph_data = cache.get(uid)
            
            
            if not graph_data :
                import utils #TODO Change
                if self.preprocess:
                    graph_data = self.preprocess(utils.grn) # cache this not the elements 
                else:
                    graph_data = self.create_network(utils.grn)
                    
                cache.set(uid,graph_data)

            threshold = None
            if self.threshold:
                
                
                if threshold_btn is not None and threshold_btn > 0:
                    threshold = n_threshold
                else:
                    threshold = self.threshold(graph_data)
                
                nodes_n_edges = self.create_network(graph_data,threshold)          
                elements = nodes_n_edges['nodes'] + nodes_n_edges['edges']            
                total_nodes= len(nodes_n_edges['nodes'])
                total_edges = len(nodes_n_edges['edges'])
            else:
                elements = graph_data['nodes'] + graph_data['edges']     
                total_nodes=len(graph_data['nodes'])      
                total_edges=len(graph_data['edges'])      
                            
                            
                
                
            cytoscape_graph = cyto.Cytoscape(
                id={"type": "network-graph", "uid": uid},
                style={'flex-grow': '1', 'box-sizing': 'border-box'},
                minZoom=0.1,
                maxZoom=2,
                elements=elements,
                stylesheet=self.stylesheet,
                layout=self.graph_layout,
            )
            
            return [children[0], cytoscape_graph] , threshold
            
    
        #  SET OPTIONS SYNCED FROM the centralized store (defualt)
        @app.callback(
            [
                Output({"type": "dropdown", "uid": self.uid},"options"),
                Output({"type": "dropdown", "uid": self.uid},"multi"),
                Output({"type": "dropdown", "uid": self.uid}, 'disabled'),
            ],
            Input({"type": "store", "uid": self.uid}, "data"),
            Input({"type": "network-graph", "uid": self.uid}, "elements"),
            prevent_initial_call=True
        )
        def set_dropdown(store,elements):
            
            selection_mode = store['selection_mode'] # Either single,off,multiple

            if selection_mode == "single":
                multi = False
            elif selection_mode == "multiple":
                multi = True
            else:
                return no_update,no_update,True
           
                
            nodes = [e.copy() for e in elements if 'source' not in e['data']]
            if self.preprocess:
                options = self.dropdown_options(
                    nodes
                )
            else: # Basically Full Bipartite CHANGE if needed

                options = self.dropdown_options(
                    nodes,
                    store
                )
            
            return options,multi,False

        # CENTRALIZED STORE SYNC ALL CALLBACKS
        @app.callback(
            [
            Output({"type": "store", "uid": self.uid}, "data"),
            Output({"type": "dropdown", "uid": self.uid}, "value"),
            ],
            [
            Input({"type": "network-graph", "uid": self.uid}, "tapNodeData"),
            Input({"type": "dropdown", "uid": self.uid}, "value"),
            Input({"type": "selection-mode-btns", "uid": self.uid},"value"), # node mode (Single , Off ,Multiple)
            Input({"type": "filter-mode-btns", "uid": self.uid},"value"), # node type (Targets, both , Tfs)
            Input({"type": "backtracking-mode-btns", "uid": self.uid},"value"), # Allow Backtrack (True/False) 
            Input({"type": "threshold-btn", "uid": self.uid},"n_clicks"), 
            ],
            State({"type": "threshold", "uid": self.uid},"value"), # Allow Backtrack (True/False) 
            State({"type": "store", "uid": self.uid}, "data"),
            prevent_initial_call=True,
        )
        def sync(tapNodeData, dropdown_value,selection_mode,filter_mode,backtracking_mode,threshold_btn,threshold_value,store):

            trigger = ctx.triggered_id
            
            # NOTE : Output of tapNodeData['id'] : str 
            # NOTE : Input of dropdown_value: str when selection_mode == single
            # NOTE : Input of dropdown_value: list when filter_mode == multiple
            # NOTE NOTE NOTE store['selected'] SHOUDL ALWAYS BE TYPE LIST
            store['metadata']['total_nodes'] = total_nodes # Global
            store['metadata']['total_edges'] = total_edges # Global
            store['threshold'] = threshold # Global
            
            store['selection_mode'] = selection_mode
            store['filter_mode'] = filter_mode
            store['backtracking_mode'] = backtracking_mode
            
            if trigger == {"type": "network-graph", "uid": self.uid} and tapNodeData:
                if store['selection_mode'] == 'single':
                    sel = tapNodeData['id']
                    store["selected"] = [sel]
                    return store, sel
                elif store['selection_mode'] == 'multiple':
                    temp = set(store["selected"])
                    temp.add(tapNodeData['id'])
                    store["selected"] = list(temp)
                    return store , store["selected"]
            

            if trigger == {"type": "dropdown", "uid": self.uid}:
                if not dropdown_value:
                    store['selected'] = []
                    return store , no_update
                
                
                if store['selection_mode'] == 'single':
                    store["selected"] = [dropdown_value]
                    return store, dropdown_value
                elif store['selection_mode'] == 'multiple':
                    temp = set(store['selected'])
                    temp.update(dropdown_value)
                    
                    if len(temp) > len(dropdown_value):
                        temp = dropdown_value
                    
                    store['selected'] = list(temp)
                    
                
                    return store, dropdown_value
            
            
            #  The defualt threshold is never in the store (Dont need?)
            if trigger == {"type": "threshold-btn", "uid": self.uid}:
                store['threshold'] = threshold_value
                return store, no_update
                
            return store, no_update



        @app.callback(
            Output({"type": "network-graph", "uid": self.uid}, "elements"),
            Input({"type": "store", "uid": self.uid}, "data"),
            State({"type": "network-graph", "uid": self.uid}, "elements"),
            prevent_initial_call=True
        )
        def highlightor(store, elements):
            
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
              

        @app.callback(
            Output({"type": "content", "uid": self.uid}, "children"),
            Input({"type": "store", "uid": self.uid}, "data"),
            Input({"type": "inspector-table", "uid": self.uid}, "active_tab"),
            State({"type": "network-graph", "uid": self.uid}, "elements"),
            prevent_initial_call=True

        )
        def update_inspector(store, active_tab, elements):
            
            selected = store['selected']
            threshold = store['threshold']
            
            if not selected:
                return no_update
            
            if self.preprocess : 
                edges = [e.copy() for e in elements if 'source' in e['data']]
                
                uid = self.uid
                from dash import get_app
                app = get_app()
                cache = app.server.config["APP_CACHE"]
                graph_data = cache.get(uid)
                            
                return self.content[active_tab.capitalize()](graph_data, selected, edges,threshold)
                
            else:
                if active_tab and store['selected']:
                    return self.content[active_tab.capitalize()](store['selected'])
                
            return no_update
        
        
        @app.callback(
            [
                Output({"type": "total_nodes", "uid": self.uid}, "children"),
                Output({"type": "total_edges", "uid": self.uid}, "children"),
                Output({"type": "selected_nodes", "uid": self.uid}, "children"),
                Output({"type": "selected_edges", "uid": self.uid}, "children"),
            ],
            Input({"type": "store", "uid": self.uid}, "data"),
            State({"type": "network-graph", "uid": self.uid}, "elements"),
            prevent_initial_call=True
        )
        def network_stats(store, elements):
            selected = store['selected']
            metadata = store['metadata']    
            total_nodes = metadata['total_nodes']
            total_edges = metadata['total_edges']
            len_selected_nodes = len(selected)
            
            edges = [e.copy() for e in elements if 'source' in e['data']]

            selected_edges = []
            for e in edges:
                
                edge = e['data']['source']
                
                if edge in selected:
                    selected_edges.append(edge)
                            
            return total_nodes,total_edges,len_selected_nodes,len(selected_edges)
        
        

        
            
        
            