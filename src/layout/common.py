"""
common.py

This file aswell as 'updates' module, includes improved
structures and function handling

There are three class, all of which help us create as much graphs as
we want with less code and being lightwieght


UIControls
    - Responsible for all Controls for graph/network/heatmap/and more
    - _NC_CONFIG is the available options we currenty have
    - _NC_CONFIG = {
        "card": "controls",             # Section
        "id" : "selection_mode_btn",    # ID
        "func" : btn_grp,               # function to create the component
        "parms" : {                    # parms to for the function
            "label" : "Selection",      # label (what ui see)
            "value" : single,           # DEFUALT VALUE of the options
            "options": [                # BTNS (label -> btn name, value -> btn vallue )
                {'label': 'Single', 'value': 'single'}, # 
                {'label': 'off', 'value': 'off'},
                {'label': 'Multiple', 'value': 'multiple'},
            ],            
        },
        ...
        }
    - Use the UIControls(...) class to define your paramters
    - UIControls.unpack() to get the entire component list
    
CytoGraph
    - Responsible for all data preprocess/process/cache for the graph
    - Add your params to the CytoGraph(...) class
    - The class obj will have all metadata aswell all data for the specific graph
    

"""

import dash
from dash import (
    Dash, dcc, html, Input, Output, State, callback, 
    no_update, callback_context, ctx, MATCH, ALL, Patch
)
import dash_cytoscape as cyto
import dash_bootstrap_components as dbc
from functools import partial
from typing import Literal

cyto.load_extra_layouts()

from updated.components.ui import btn_grp, thresh_input, dropdown, tabs, table, get_heat_map,network_stats
import utils


DUMMY = html.Div("DUMMY", className="d-flex flex-1 bg-danger")

_NC_CONFIG = [
    {
        "card": "Network Stats",
        "id": "network_stats",
        "func": network_stats,
        "parms": {
        }
    },
    {
        "card": "Graph controls",
        "id": "selection_mode",
        "func": btn_grp,
        "parms": {
            "label": "Selection",
            "value": None,#"single",  
            "options": [
                {"label": "Single", "value": "single"},
                {"label": "Off", "value": "off"},
                {"label": "Multiple", "value": "multiple"},
            ],
        }
    },
    {
        "card": "Graph controls",
        "id": "filter_mode",
        "func": btn_grp,
        "parms": {
            "label": "Filter By",
            "value": None,#"both",  
            "options": [
                {"label": "Target", "value": "target"},
                {"label": "Both", "value": "both"},
                {"label": "TF", "value": "tf"},
            ],
        }
    },
    {
        "card": "Graph controls",
        "id": "backtracking_mode",
        "func": btn_grp,
        "parms": {
            "label": "Backtracking",
            "value": None,#False,  
            "options": [
                {"label": "On", "value": "True"},
                {"label": "Off", "value": "False"},
            ],
        }
    },
    {
        "card": "Graph controls",
        "id": "threshold_input",
        "func": thresh_input,
        "parms": {
            "label": "Threshold",
        }
    },
    {
        "card": "Node Inspector",
        "id": "options_dropdown",
        "func": dropdown,
        "parms": {
            "label": "Highlight Node",
        }
    },
    {
        "card": "Node Inspector",
        "id": "inspector_tabs",
        "func": tabs,
        "parms": {
            "options" : [
                {"label": "Tab 1", "value": "1",  "tab_id":"" },
                {"label": "Tab 2", "value": "2",  "tab_id":"" },
            ],
            "value" : None
        }
    },        
]

class UIControls:
        
    def __init__(
        self,
        *,
        selection_mode: Literal["single", "off", "multiple"] = None,
        filter_mode: Literal["target", "both", "tf"] = None,
        backtracking_mode : bool = False,
        threshold_input : bool = False,
        options_dropdown: bool = False,
        inspector_tabs : list = None,
        network_stats : bool = False,
        ): 
          
        # Will be assigned in the UILayout class
        self.uid = None  
        
        # Get Defined parms
        defined_parms = {k: v for k, v in locals().items() if k != 'self' and v}
        self.defined_parms = defined_parms
        self._store = self.defined_parms
        
        # Get the controls configs of the defined parms
        self._CONTROLS_CONFIG = [
            nc for nc in _NC_CONFIG
            if nc["id"] in defined_parms
        ]
        
    def pack(self, uid, options_dropdown):
        
        self.uid = uid
        
        # Update the options for 'options_dropdown' if present
        for nc in self._CONTROLS_CONFIG:
            if nc["id"] == "options_dropdown":
                nc["parms"]["options"] = options_dropdown
                
        return self
        
        
    
            
    def unpack(self):
        
        if self.uid is None:
            raise ValueError
        
        # Initialize the dictionary to store components, grouped by 'card'.
        staged_components = {}
        
        # Iterate through the configuration list.
        for nc in self._CONTROLS_CONFIG:
            card = nc['card']

            # Unique ID dictionary for the component.
            comp_id = {"type": nc["id"], "uid": self.uid}
            
            
            # Get the function and its parameters.
            func = nc['func']
            
            # Copy the parms of network controls
            parms = nc['parms'].copy() 

            if "value" in parms: # To assign the defined parameter 
                parms["value"] = self.defined_parms[nc["id"]]
            
            # Create the component
            new_component = func(
                id=comp_id,
                **parms
            )

            # Check if the 'card' key already exists in the dictionary.
            if card in staged_components:
                # If it exists, append the new component to the existing list.
                staged_components[card].append(new_component)
            else:
                # If it does not exist, initialize it
                staged_components[card] = [new_component]
                
        # Create the components list, which will include everything for the NC
        components = []
        for card, values  in staged_components.items():
            components.append(
                dbc.Card(
                    className="mb-2",
                    children=[
                    dbc.CardHeader(card),
                    dbc.CardBody(values) 
                    ]
                )   
            )       
        return components
         
    

class CytoGraph:
    def __init__(
        self,
        preprocess_function: callable = None,
        preprocess_role: str = Literal['bygene','bytf'],
        creation_function: callable = None,
        threshold_function : callable = None,
        threshold: float = None,
        threshold_ratio: float = None,
        stylesheet: dict = None,
        layout_config: dict = None,
        dropdown_options: callable = None,
        ): 
        self.preprocess_function = preprocess_function
        self.preprocess_role = preprocess_role
        self.creation_function = creation_function
        self.threshold_function = threshold_function
        self.threshold = threshold
        self.threshold_ratio = threshold_ratio
        self.stylesheet = stylesheet
        self.layout_config = layout_config
        self.dropdown_options = dropdown_options
        self.store = {
            "selected": [],
            "metadata": {
                "total_nodes": 0,
                "total_edges": 0,
                "selected_nodes": 0,
                "selected_edges": 0,
            },
        }
        
        
        # self._store = {
        #     "selected" : [], 
        #     "threshold" : self.threshold,
        #     "metadata" :{
        #         "total_nodes" : 0,
        #         "total_edges" : 0,
        #         "selected_nodes" : 0,
        #         "selected_edges" : 0,
        #     },
        # }
        #"threshold_ratio" : self.threshold_ratio,
        # "role" : self.preprocess_role,
    @property
    def _store(self):
        store = self.store
        store.update({"uid": self.uid})

        if self.threshold is not None:
            store.update({
                "threshold": self.threshold,
                "threshold_ratio": self.threshold_ratio,
                "preprocess_role": self.preprocess_role,
            })

        return store

        
    
    def pack(self,uid):
        self.uid = uid
        return self
                
    def compute(self):
        
        if self.preprocess_function:
            #NOTE we can cache this
            pre_data = self.preprocess_function(utils.grn,self.preprocess_role)    
            
            # NOTE NOT STABLE
            app = dash.get_app()
            cache = app.server.config['SERVER_CACHE']      
            cache.set(self.uid,pre_data)
    
            
            if not self.threshold:
                self.threshold = self.threshold_function(pre_data,self.threshold_ratio)
                
            data = self.creation_function(pre_data,self.threshold)
        else:
            data = self.creation_function(utils.grn)
            
        self.elements  = data['nodes'] + data['edges']     
        
        self._store['metadata']['total_nodes'] = len(data['nodes'])      
        self._store['metadata']['total_edges'] = len(data['edges'])    

        if self.dropdown_options:
            self.options = self.dropdown_options(data['nodes'])#TODO Remove hardcod
            
        return self
      
                

    def unpack(self):
        
        if self.uid is None:
            raise ValueError
        
        return [cyto.Cytoscape(
            id={"type": "network-graph", "uid": self.uid},
            style={'flex-grow': '1', 'box-sizing': 'border-box', 'border-radius': '8px', 'box-shadow': '0 4px 6px rgba(0, 0, 0, 0.1)'},
            minZoom=0.1,
            maxZoom=2,
            elements=self.elements,
            stylesheet=self.stylesheet,
            layout=self.layout_config,
            className="bg-light"
        )]






class UILayout:
    def __init__(
        self,
        uid : str,
        cytograph: CytoGraph = None,
        controls: UIControls = None,
        content_width : int = 9,
        controls_width : int = 3,
        ):
        
        self.uid = uid
        
        cytograph.pack(uid)
        cytograph.compute()
        controls.pack(uid,cytograph.options)     
        
        self.store = controls._store | cytograph._store
            
        self.CONTENT = cytograph
        self.CONTROLS = controls 
        
        self.content_width = content_width
        self.controls_width = controls_width
        
        
        
    def render(self):
        return dbc.Container(
            fluid=True,
            className="p-0 m-0 h-100",
            children=[
                dcc.Store(id={"type": "store", "uid": self.uid}, data=self.store),
                dcc.Store(id={"type": "backup-store", "uid": self.uid}, data=self.store),
                dbc.Row(
                    className="g-0 h-100",  # g-0 removes gutters, h-100 for full height
                    children=[
                        # Main content area
                        dbc.Col(
                            id={"type": "main-content", "uid": self.uid},
                            width=self.content_width,
                            className=" d-flex flex-column overflow-hidden p-2 bg-secondary",
                            children=self.CONTENT.unpack()
                        ) ,
                        # Sidebar area - 25% (width 3)
                        dbc.Col(
                            width=self.controls_width,
                            className="bg-secondary text-white p-3 h-100 overflow-auto",
                            children=self.CONTROLS.unpack()
                        )
                    ]
                )
            ]
        )
        
        
def get_first(val):
    if isinstance(val, list) and val:
        assert len(val) == 1
        return val[0]
    return val

# All UI Input goes to the store
@callback(
    [
        Output({"type": "store", "uid": MATCH}, "data"),
        Output({"type": "options_dropdown", "uid": MATCH}, "value"),
    ],
    
    [
        Input({"type": "network-graph", "uid": MATCH}, "tapNodeData"),
        Input({"type": "options_dropdown", "uid": MATCH}, "value"),
        Input({"type": "selection_mode", "uid": ALL}, "value"),
        Input({"type": "filter_mode", "uid": ALL}, "value"),
        Input({"type": "backtracking_mode", "uid": ALL}, "value"),
        Input({"type": "threshold_input_btn", "uid": ALL}, "n_clicks"),
    ],
    State({"type": "threshold_input", "uid": ALL}, "value"),
    State({"type": "store", "uid": MATCH}, "data"),
    prevent_initial_call=True,
)
def sync(
    tapNodeData, dropdown_value, selection_mode, filter_mode, backtracking_mode, threshold_btn, threshold_value, store
):
    trigger = ctx.triggered_id

    assert isinstance(store, dict) # Catch problems from ALL pattern-matched inputs

    # Helper to get first value from ALL pattern-matched inputs
    def get_first(val):
        if isinstance(val, list) and val:
            assert len(val) == 1
            return val[0]
        return val

    # Update store based on which control triggered the callback
    if trigger:
        t_type = trigger.get('type') if isinstance(trigger, dict) else trigger

        if t_type == "selection_mode":
            val = get_first(selection_mode)
            if val:
                store['selection_mode'] = val

        elif t_type == "filter_mode":
            val = get_first(filter_mode)
            if val:
                store['filter_mode'] = val

        elif t_type == "backtracking_mode":
            val = get_first(backtracking_mode)
            if val:
                store['backtracking_mode'] = val

        elif t_type == "threshold_input_btn":
            val = get_first(threshold_value)
            if val is not None:
                store['threshold'] = val
        elif t_type == "network-graph" and tapNodeData:
            sel_mode = store.get('selection_mode', 'single')
            
            if sel_mode=="off":
                return no_update,no_update
            
            node_id = tapNodeData.get('id')
            node_type = tapNodeData.get('type')
            if not node_id:
                return store, no_update
            
            # Check if node matches the current filter mode
            filt_mode = store.get('filter_mode')
            if node_type is not None:
                if filt_mode == 'target' and node_type != 'target':
                    return store, no_update
                elif filt_mode == 'tf' and node_type != 'tf':
                    return store, no_update
            # 'both' allows all node types, and None type passes through
            
            if sel_mode == 'single':
                store["selected"] = [node_id]
                return store, node_id
            elif sel_mode == 'multiple':
                
                selected = store.get("selected", [])
                if isinstance(selected,str):
                    selected = [selected]                
                temp = set(selected)
                temp.add(node_id)
                store["selected"] = list(temp)
                return store, store["selected"]

    
        elif t_type == "options_dropdown":
            val = dropdown_value
            sel_mode = store.get('selection_mode', 'single')
            if not val:
                store['selected'] = []
                return store, no_update
            if sel_mode == 'single':
                store["selected"] = [val]
                return store, no_update
            elif sel_mode == 'multiple':
                                
                temp = set(store.get('selected', []))
                # val could be a list or a single value
                if isinstance(val, list):
                    temp.update(val)
                    # If user deselected, keep only current dropdown values
                    if len(temp) > len(val):
                        temp = set(val)
                    store['selected'] = list(temp)
                    return store, no_update
                else:
                    temp.add(val)
                    store['selected'] = list(temp)
                    return store, no_update

    return store, no_update 



@callback(
    [
        Output({"type": "options_dropdown", "uid": MATCH},"multi"),
        Output({"type": "options_dropdown", "uid": MATCH}, 'disabled'),
    ],
    Input({"type": "store", "uid": MATCH}, "data"),
    State({"type": "options_dropdown", "uid": MATCH}, "multi"),
    State({"type": "options_dropdown", "uid": MATCH}, "disabled"),
    prevent_initial_call=True,
)
def dropdown_selection_mode(store, multi, disabled):
    selection_mode = store.get('selection_mode')
    
    if selection_mode == "single":
        if multi is False and disabled is False:
            return no_update, no_update
        return False, False
    
    elif selection_mode == "multiple":
        if multi is True and disabled is False:
            return no_update, no_update
        return True, False
    
    elif selection_mode == "off":
        if disabled is True:
            return no_update, no_update
        return no_update, True
    
    return no_update, no_update
    
            
@callback(
    Output({"type": "network-graph", "uid": MATCH}, "elements"),
    Input({"type": "store", "uid": MATCH}, "data"),
    State({"type": "network-graph", "uid": MATCH}, "elements"),
    prevent_initial_call=True
)
def highlightor(store, elements):
    
    selected_val = store['selected']
    if isinstance(selected_val, str):
        selected = {selected_val}
    else:
        selected = set(selected_val) if selected_val else set()

    if not selected:
        patch = Patch()
        for i in range(len(elements)):
            patch[i] = elements[i].copy()
            patch[i]['classes'] = ''
        return patch
        
    connected_nodes = set()
    patch = Patch()
    
    # First pass: identify connected nodes
    for i, e in enumerate(elements):
        if 'source' in e['data']:
            src = e['data']['source']
            tgt = e['data']['target']        
            if selected & {src, tgt}:
                connected_nodes.update([src, tgt])
    
    # Second pass: apply classes using patch
    for i, e in enumerate(elements):
        elem_copy = e.copy()
        
        if 'source' in e['data']:  # Edge
            src = e['data']['source']
            tgt = e['data']['target']        
            if selected & {src, tgt}:
                elem_copy['classes'] = "highlighted-edge"
            else:
                elem_copy['classes'] = "faded"
        else:  # Node
            nid = e['data']['id']
            if nid in selected:
                elem_copy['classes'] = 'highlighted'
            elif nid in connected_nodes:
                elem_copy['classes'] = ''
            else:
                elem_copy['classes'] = 'faded'
        
        patch[i] = elem_copy
    
    return patch



@callback(
    Output({"type": "options_dropdown", "uid": MATCH}, "options"),
    Input({"type": "network-graph", "uid": MATCH}, "elements"),
    Input({"type": "filter_mode", "uid": ALL}, "value"),
    State({"type": "options_dropdown", "uid": MATCH}, "options"),
)
def create_dropdown_options(elements, filter_mode, current_options):
        
    # Extract filter_mode from ALL pattern-matched list
    if isinstance(filter_mode, list) and filter_mode:
        filter_mode = filter_mode[0]
    
    # Get nodes using GENERATOR better for memory 
    nodes = (ele['data'] for ele in elements if 'source' not in ele['data'])
    
    # Get the first node to check data type
    first_node = next(nodes, None)
    
    # Handle empty nodes case
    if first_node is None:
        return []
    
    # Is a bool True if full graph
    byreg = first_node.get('type') in ['tf', 'target']
    
    options = []
    
    # Add the first node since we consumed it using next()
    label = first_node.get('label', first_node.get('id'))
    if byreg:
        if first_node['type']==filter_mode or filter_mode =="both":
            label = f"{label} ({first_node['type']})"
            options.append({'label': label, 'value': first_node['id']})
    else:
        options.append({'label': label, 'value': first_node['id']})
        

    # Process the REST of the nodes
    for node in nodes:
        label = node.get('label', node.get('id'))
    
        if byreg:
            if node['type']==filter_mode or filter_mode =="both":
                label = f"{label} ({node['type']})"        
                options.append({
                    'label': label, 
                    'value': node['id']
                })
        else:
            options.append({
                'label': label, 
                'value': node['id']
            })
            
        
    options = sorted(options, key=lambda x: x['label'])
    
    return options


@callback(
    Output({"type": "threshold_input", "uid": ALL}, "value"),
    Input({"type": "main-content", "uid": ALL}, "children"),
    State({"type": "store", "uid": ALL}, "data"),
)
def update_thresh(children,store):
    store = get_first(store)
    threshold = store.get("threshold",[])
    if threshold:
        return [threshold]
    else:
        return [no_update]


@callback(
    Output({"type": "network-graph", "uid": MATCH}, "elements",allow_duplicate=True),
    Input({"type": "threshold_input_btn", "uid": ALL}, "n_clicks"),
    State({"type": "threshold_input", "uid": ALL}, "value"),
    State({"type": "store", "uid": ALL}, "data"),
    prevent_initial_call=True    
)
def update_graph_thresh(n_clicks,value,store):
    value = get_first(value)
    store = get_first(store)

    from updated.graph import adj
    
    data = adj.create_network(
        adj.get_genes(utils.grn,store['preprocess_role']),
        value
    )
    
    
    return data['nodes'] + data['edges']

    
    
@callback(
    [
    Output({"type": "total_nodes", "uid": MATCH}, "children"),
    Output({"type": "total_edges", "uid": MATCH}, "children"),
    Output({"type": "selected_nodes", "uid": MATCH}, "children"),
    Output({"type": "selected_edges", "uid": MATCH}, "children"),
    ],
    Input({"type": "store", "uid": MATCH}, "data"),
    State({"type": "network-graph", "uid": MATCH}, "elements"),
)
def update_network_stats(store,elements):
    selected = store['selected']
    metadata = store['metadata']
    t=0
    tf = 0
    
    for e in elements:
        data = e['data']
        source = data.get("source",None)
        if not source:
            pass
        target = data.get("target",None)
        if source in selected:
            t=t+1
        elif target in selected:
            tf=tf+1
            
    total = t+tf        
        
    
    return metadata['total_nodes'],metadata['total_edges'],len(selected),total

    

@callback(
    Output({"type": "inspector_tabs_content", "uid": MATCH}, "children"),
    Input({"type": "inspector_tabs", "uid": MATCH}, "active_tab"),
    Input({"type": "store", "uid": MATCH}, "data"),
    State({"type": "network-graph", "uid": MATCH}, "elements"),
    prevent_initial_call=True
)
def update_inspector_tabs(active_tab, store,___):
    """Update inspector tabs based on active tab and store data"""
    print(active_tab)

    if not active_tab:
        return no_update
    
    selected = store.get("selected",None)
    
    if not selected:
        return html.Div(
            "Please select a node",
            className="d-flex align-items-center justify-content-center h-100"
        )

    
    if active_tab == "table":
        from graph.fullbipartite import regulation
        return regulation(selected,"./grn.json")
    elif active_tab == "heatmap":
        from graph.fullbipartite import get_heat_map
        return get_heat_map(selected,"./CIT_BLCA_EXP.csv")
    elif active_tab == "adj_table":
        from dash import get_app
        app = get_app()
        cache = app.server.config["SERVER_CACHE"]
        pre_data = cache.get(store['uid'])
        
        if not pre_data:
            raise NameError("Getting cache has failed")
        
        edges = [e.copy() for e in ___ if 'source' in e['data']]
        columns=[
            {"name": "TF", "id": "Node"},
            {"name": "CO", "id": "shared"},
            {"name": "STC", "id": "count"},
        ]

        from updated.graph.adj import by_update_info_panel
        
        # NOTE FULL CONNECTIONS OR CURRENT ?
        return by_update_info_panel(pre_data,selected,edges,store['threshold'],columns)
    





    return no_update
    
    


