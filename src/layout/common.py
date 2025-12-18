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

from updated.components.ui import btn_grp, thresh_input, dropdown, tabs, table, get_heat_map
import utils


DUMMY = html.Div("DUMMY", className="d-flex flex-1 bg-danger")

_NC_CONFIG = [
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
        inspector_tab : bool = False,
        # inspector_tab : dict = None,
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
        creation_function: callable = None,
        get_threshold : callable = None,
        threshold: float = None,
        stylesheet: dict = None,
        layout_config: dict = None,
        dropdown_options: callable = None,
        ): 
        self.preprocess_function = preprocess_function
        self.creation_function = creation_function
        self.get_threshold = get_threshold
        self.threshold = threshold
        self.stylesheet = stylesheet
        self.layout_config = layout_config
        self.dropdown_options = dropdown_options
        
        self._store = {
            "selected" : [], 
            "threshold" : self.threshold,
            "metadata" :{
                "total_nodes" : 0,
                "total_edges" : 0,
                "selected_nodes" : 0,
                "selected_edges" : 0,
            },
        }

    
    def pack(self,uid):
        self.uid = uid
        return self
        
    def compute(self):
        
        if self.preprocess_function:
            data = self.preprocess_function(utils.grn)
            
        else:
            data, _ = self.creation_function(utils.grn)
            
            
        if self.get_threshold:
            threshold = self.get_threshold(data)
            nodes_n_edges,_= self.creation_function(data,threshold)
            elements = nodes_n_edges['nodes'] + nodes_n_edges['edges']      
            total_nodes= len(nodes_n_edges['nodes'])
            total_edges = len(nodes_n_edges['edges'])  
            self.threshold = threshold    
            if self.dropdown_options:
                options = self.dropdown_options(nodes_n_edges['nodes'])
        else:
            elements = data['nodes'] + data['edges']     
            total_nodes=len(data['nodes'])      
            total_edges=len(data['edges'])      
            if self.dropdown_options:
                options = self.dropdown_options(data['nodes'],{"filter_mode" : ""})#TODO Remove hardcod
            
            
        self._store['metadata']['total_nodes'] = total_nodes
        self._store['metadata']['total_edges'] = total_edges
        if self.dropdown_options:
            self.options = options
        self.elements = elements
        
        
        return self
    
    
    def unpack(self):
        
        if self.uid is None:
            raise ValueError
        
        return [cyto.Cytoscape(
            id={"type": "network-graph", "uid": self.uid},
            style={'flex-grow': '1', 'box-sizing': 'border-box'},
            minZoom=0.1,
            maxZoom=2,
            elements=self.elements,
            stylesheet=self.stylesheet,
            layout=self.layout_config,
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
                            className=" d-flex flex-column overflow-hidden p-2",
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
            if not node_id:
                return store, no_update
            if sel_mode == 'single':
                store["selected"] = node_id
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
    # print(store['selected'])
    
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
    
        
    
