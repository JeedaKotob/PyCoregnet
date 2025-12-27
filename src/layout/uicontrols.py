"""
UI Controls Layout Module

Responsible for all Controls for graph/network/heatmap/and more
_NC_CONFIG is the available options we currenty have
_NC_CONFIG = [
    {
    "card": "controls",             # Section
    "id" : "selection_mode_btn",    # ID & UIControls parm name
    "func" : btn_grp,               # function to create the component
    "parms" : {                     # parms to for the function
        "label" : "Selection",      # label (what ui see)
        "value" : single,           # DEFUALT VALUE of the options / Defined 
        "options": [                # BTNS (label -> btn name, value -> btn vallue )
            {'label': 'Single', 'value': 'single'}, # 
            {'label': 'off', 'value': 'off'},
            {'label': 'Multiple', 'value': 'multiple'},
        ],            
    },
    ...
]
- Use the UIControls(...) class to define your paramters
- UIControls.unpack() to get the entire component list"""

import dash_bootstrap_components as dbc
from typing import Literal
from components.ui import btn_grp, thresh_input, dropdown, tabs, table, get_heat_map,network_stats

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
        """Add info from UILayout class before unpack()"""
        self.uid = uid
        
        # Update the options for 'options_dropdown' if present
        for nc in self._CONTROLS_CONFIG:
            if nc["id"] == "options_dropdown":
                nc["parms"]["options"] = options_dropdown
                
        return self
        
        
            
    def unpack(self):
        """Returns the entire layou"""
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
         
    
