"""

network_controls = NetworkControls(
    name = GRAPH,
    selection_mode = 'single',
    filter_mode = 'both',
    inspector_options = {
        "Regulation" : partial(fullbipartite.regulation,grn_path="./grn.json"),
        "Expression" : partial(fullbipartite.get_heat_map,filepath="./CIT_BLCA_EXP.csv"),
    },
    enable_stats_display = True   
)

graph_options = network_controls.store


graph = CytoGraphHandler(
    store = graph_options,
    network_creation_function = fullbipartite.create_network,
    network_stylesheet = stylesheet.full_network_stylesheet,
    graph_layout = fullbipartite.layout,
    dropdown_options = fullbipartite.options
)


NetworkLayout(
    graph,
    network_controls
)

"""

import dash
from dash import (
    Dash, dcc, html, Input, Output, State, callback, 
    no_update, callback_context, ctx, MATCH, ALL
)
import dash_cytoscape as cyto
import dash_bootstrap_components as dbc
from functools import partial
from typing import Literal

cyto.load_extra_layouts()

from components.ui import tabs, button_group, stat_box, threshold_input
import utils

class NetworkControls:

    _CONTROLS_CONFIG = [
        {
            "type": "selection-mode-btns",
            "component": button_group,
            "check_key": "selection_mode",
            "props": {
                "label": "Selection",
                "value": "single",
                "options": [
                    {'label': 'Single', 'value': 'single'},
                    {'label': 'off', 'value': 'off'},
                    {'label': 'Multiple', 'value': 'multiple'},
                ],
            }
        },
        {
            "type": "filter-mode-btns",
            "component": button_group,
            "check_key": "filter_mode",
            "props": {
                "label": "Filter By",
                "value": "both",
                "options": [
                    {'label': 'Target', 'value': 'target'},
                    {'label': 'Both', 'value': 'both'},
                    {'label': 'TF', 'value': 'tf'},
                ],
            }
        },
        {
            "type": "backtracking-mode-btns",
            "component": button_group,
            "check_key": "backtracking_mode",
            "props": {
                "label": "Backtracking",
                "value": "False",
                "options": [
                    {'label': 'On', 'value': 'True'},
                    {'label': 'Off', 'value': 'False'},
                ],
            }
        },
        {
            "type": "threshold",
            "component": threshold_input,
            "check_key": "threshold_input",
            "props": {
                "label": "Threshold",
            }
        },
    ]
    
    def __init__(
        self,
        *,
        name,
        selection_mode: Literal["single", "off", "multiple"] = None,
        filter_mode: Literal["target", "both", "tf"] = None,
        backtracking_mode : bool = None,
        dropdown_options : dict = None,
        threshold_input : bool = None,
        inspector_options : dict = None,
        enable_stats_display : bool = None
        ):
        
        #  Unique id (To handle callbacks for the specific graph)
        self.uid = name
        
        # Selected options (Defined parameters)
        params = {k: v for k, v in locals().items() if k != 'self' and v is not None and v is not False}
        
        for k, v in params.items():
            setattr(self, k, v)
            
        self._CONTROLS_CONFIG = [
            cfg for cfg in self._CONTROLS_CONFIG
            if cfg["check_key"] in params
        ]
        
        # Initialize the store with default values
        self.store = {
            'graph': name,
            'selected': [],
            'metadata': {
            'total_nodes': 0,
            'total_edges': 0,
            'selected_nodes': 0,
            'selected_edges': 0,
            }
        }
        
        # Update the store with selected options
        self.store.update(params)    
        
    
    def create_component_list(self): 
        
        component_list = []
        if self.enable_stats_display:
            component_list.append(self._stats_display())
                    
        component_list.append(self._controls())
        
        if self.inspector_options:
            component_list.append(self._content_inspector())

        
        return component_list
                
        
    def _stats_display(self):
        
        return dbc.Card(className="mb-2",children=[
            dbc.CardHeader("Network stats"),
            dbc.CardBody(stat_box(stats=[
            {"name" : "Total Nodes", "id" : {"type": "total_nodes", "uid": self.uid}},
            {"name" : "Total Edges", "id" : {"type": "total_edges", "uid": self.uid}}
            ])),
            dbc.CardBody(stat_box(stats=[
            {"name" : "Selected Nodes", "id" : {"type": "selected_nodes", "uid": self.uid}},
            {"name" : "Selected Edges", "id" : {"type": "selected_edges", "uid": self.uid}}
            ])),
        ])
    
    
    def _controls(self):
        # The components that will be present in the layout
        control_elements = []

        # Loop over all the possible options the graph can have
        for cfg in self._CONTROLS_CONFIG:
            # Set a unique id for the component specific to the current graph
            component_id = {"type": cfg["type"], "uid": self.uid}
            # The function ex: either button_group / threshold_input
            component_func = cfg["component"]
            
            control_elements.append(
                component_func(
                    id=component_id,
                    **cfg["props"]
                )
            )

        return dbc.Card(
            className="mb-2",
            children=[
                dbc.CardHeader("Graph controls"),
                dbc.CardBody(control_elements) 
            ]
        )
        
    
    def _content_inspector(self):
        
        #  Intiate list that will be present in the layout
        inspector_elements = [
            # Add Label
            dbc.Row(html.Label("Highlight Node"),className="mb-2"),
            # Add dropdown 
            dbc.Row(dcc.Dropdown(id={"type" : "dropdown", "uid" : self.uid},className="mb-2")),
            tabs(id={"type": "inspector-table", "uid": self.uid},
            options=[
                { "label":key, "tab_id" : key.lower()} for key in self.inspector_options.keys()
                ],value=None),
        ]
        
        return dbc.Card(
            className="mb-2",
            children=[
                dbc.CardHeader("Node Inspector"),
                dbc.CardBody(inspector_elements) 
            ]
        )
            
    



class CytoGraphHandler:
    def __init__(
        self,
        # uid,
        network_preprocess_function: callable,
        network_creation_function: callable,
        network_threshold : float,
        network_stylesheet : dict,
        network_layout_config : dict,
        ): 
        
        params = {k: v for k, v in locals().items() if k != 'self'}
        for k, v in params.items():
            setattr(self, k, v)
            
    
    def _perprocess():
        pass
    
    def _cache_hander():
        pass
        
    def create_compontent(self):
        
        graph_data , _= self.network_creation_function(utils.grn)
        elements = graph_data['nodes'] + graph_data['edges']     

        return cyto.Cytoscape(
            id={"type": "network-graph", "uid": "hardcoded"},
            style={'flex-grow': '1', 'box-sizing': 'border-box'},
            minZoom=0.1,
            maxZoom=2,
            elements=elements,
            stylesheet=self.network_stylesheet,
            layout=self.network_layout_config,
        ) 
    
        
    

def manual_tabs(uid,options: list):
    return dbc.Tabs(
        id={"type": "graph-tabs", "uid": uid},
        className="justify-content-center text-black border-0 bg-light h-0",
        children=[
            dbc.Tab(
                label = list(option.keys())[0],
                tab_id = list(option.keys())[0].replace(" ", "").lower(),
                labelClassName='text-black border-0 ',
                # activeLabelClassName='text-black ',
                # activeTabClassName='text-black border-0 '
            ) for option in options
        ]
    )    

graph_tabs = manual_tabs(
    uid="hardcoded",
    options=[
        {'Full Bipartite Network': html.Div("Graph")},
        {'Full Bipartite Heatmap': html.Div("Heatmap")}
    ],
)









class NetworkLayout:
    def __init__(
        self,
        network_controls : NetworkControls,
        cyto_graph_handler : CytoGraphHandler,
        heatmap
        ): 
        self.network_controls = network_controls
        self.cyto_graph_handler = cyto_graph_handler
        self.heatmap = heatmap
        
        self.uid = "hardcoded"
        
        
        
        
    def render_layout(self):
        
        return dbc.Container(
            fluid=True,
            className="p-0 m-0 h-100",
            children=[
            dbc.Row(
                className="g-0 h-100",  # g-0 removes gutters, h-100 for full height
                children=[
                # Main content area - 75% (width 9) nneds to be on the left
                dbc.Col(
                    id={"type" : "main-content", "uid" : self.uid},
                    width=9,
                    className="bg-danger d-flex flex-column overflow-hidden p-2",
                    children=[
                        graph_tabs,
                        html.Div(
                            className="d-flex justify-content-center align-items-center h-100",
                            children = dbc.Spinner(
                                    size="lg",
                                    color="primary",
                                    fullscreen=True
                            )
                    ),
                ]
                ),
                # Sidebar area - 25% (width 3)
                dbc.Col(
                    width=3,
                    className="bg-secondary text-white p-3 h-100 overflow-auto",
                    children=self.network_controls.create_component_list()
                )
                ]
            )
            ]
        )
      
      
    def _register(self):
        
            from dash import get_app
            app : dash = get_app()
            
            @app.callback(
                Output({"type": "main-content", "uid": self.uid}, "children"),
                Input({"type": "main-content", "uid": self.uid}, "children"),
                Input({"type" : "graph-tabs", "uid" :"hardcoded"}, "active_tab")
            )
            def _tabs(children,active_tab):
                
                print(active_tab)
                if active_tab == "fullbipartitenetwork":
                    return [children[0], self.cyto_graph_handler.create_compontent()]
                elif active_tab == "fullbipartiteheatmap":
                    return [children[0], self.heatmap]
                
                
            

                
                
                
  
        
        
        
    