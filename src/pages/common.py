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
    - 

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

from updated.components.ui import btn_grp
import utils

_NC_CONFIG = [
    {
        "card": "Graph controls",
        "id": "selection_mode_btn",
        "func": btn_grp,
        "parms": {
            "label": "Selection",
            "value": "single",  
            "options": [
                {"label": "Single", "value": "single"},
                {"label": "off", "value": "off"},
                {"label": "Multiple", "value": "multiple"},
            ],
        },
    },
    {
        "card": "Graph controls",
        "id": "filter_mode_btn",
        "func": btn_grp,
        "parms": {
            "label": "Filter By",
            "value": "both",  
            "options": [
                {"label": "Target", "value": "target"},
                {"label": "Both", "value": "both"},
                {"label": "TF", "value": "tf"},
            ],
        },
    },
    {
        "card": "Graph controls",
        "id": "backtracking_mode_btn",
        "func": btn_grp,
        "parms": {
            "label": "Backtracking",
            "value": False,  
            "options": [
                {"label": "On", "value": "True"},
                {"label": "Off", "value": "False"},
            ],
        },
    },
    # {
    #     "card": "controls",
    #     "id": "threshold_input",
    #     # "func": threshold_input,
    #     "parms": {
    #         "label": "Threshold",
    #         # add any threshold-specific parms you need (min/max/step/value)
    #         # "value": None,
    #     },
    # },
    # {
    #     "card": "inspector",
    #     "id": "options_dropdown",
    #     # "func": threshold_input,
    #     "parms": {
    #         "label": "Threshold",
    #         # add any threshold-specific parms you need (min/max/step/value)
    #         # "value": None,
    #     },
    # },
]

DUMMY = html.Div("DUMMY", className="d-flex flex-1 bg-danger")

class UIControls:
        
    def __init__(
        self,
        *,
        selection_mode_btn: Literal["single", "off", "multiple"] = None,
        filter_mode_btn: Literal["target", "both", "tf"] = None,
        backtracking_mode_btn : bool = False,
        threshold_input : bool = False,
        options_dropdown: bool = False,
        inspector_options : dict = None,
        enable_stats_display : bool = False
        ): 
          
        self.uid = None  
        
        # Get Defined parms
        defined_parms = {k: v for k, v in locals().items() if k != 'self' and v}
        
        # Get the controls configs of the defined parms
        self._CONTROLS_CONFIG = [
            nc for nc in _NC_CONFIG
            if nc["id"] in defined_parms
        ]
        
            
    def unpack(self, uid):
        
        # Initialize the dictionary to store components, grouped by 'card'.
        staged_components = {}
        
        # Iterate through the configuration list.
        for nc in self._CONTROLS_CONFIG:
            card = nc['card']
            
            # Unique ID dictionary for the component.
            comp_id = {"type": nc["id"], "uid": uid}
            
            # Get the function and its parameters.
            func = nc['func']
            parms = nc['parms']
            
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
        # uid,
        network_preprocess_function: callable,
        network_creation_function: callable,
        network_threshold : float,
        network_stylesheet : dict,
        network_layout_config : dict,
        ): ...
    


class UILayout:
    def __init__(
        self,
        uid : str,
        content: CytoGraph = None,
        controls: UIControls = None,
        content_width : int = 9,
        controls_width : int = 3,
        ):
        self.uid = uid
        self.content = content = DUMMY
        self.controls = controls
        self.content_width = content_width
        self.controls_width = controls_width
        
        
    def render(self):
        return dbc.Container(
            fluid=True,
            className="p-0 m-0 h-100",
            children=[
                dbc.Row(
                    className="g-0 h-100",  # g-0 removes gutters, h-100 for full height
                    children=[
                        # Main content area
                        dbc.Col(
                            id={"type": "main-content", "uid": self.uid},
                            width=self.content_width,
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
                            width=self.controls_width,
                            className="bg-secondary text-white p-3 h-100 overflow-auto",
                            children=self.controls.unpack(self.uid)
                        )
                    ]
                )
            ]
        )
    

dash.register_page(__name__, path='/dashboard/cmn')

uicontrols = UIControls(
    selection_mode_btn="single",
    filter_mode_btn="both",
    backtracking_mode_btn=True
)


uilayout = UILayout(
    uid='test',
    controls=uicontrols
)

layout = uilayout.render()
