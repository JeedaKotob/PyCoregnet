from typing import Literal
import dash
from dash import (
    html, Input, Output, State, callback, dcc,
    no_update, callback_context, ctx, MATCH, ALL, Patch, get_app
)
import dash_bootstrap_components as dbc
from layout import CytoGraph, UIControls
# NOTE NEEDS TO BE REPLACED
import utils
# Run the callbacks
import callbacks.cytocontrols

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
        
        # Assign the UID the layout
        cytograph.pack(uid)
        # Compute the graph 
        cytograph.compute()
        
        # Assign the UID the layout & add extra info
        controls.pack(uid,cytograph.options)     
        
        # Merge the store
        self.store = controls._store | cytograph._store
        
        # To unpack later
        self.CONTENT = cytograph
        self.CONTROLS = controls 
        
        # For layout
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
                        # Sidebar area
                        dbc.Col(
                            width=self.controls_width,
                            className="bg-secondary text-white p-3 h-100 overflow-auto",
                            children=self.CONTROLS.unpack()
                        )
                    ]
                )
            ]
        )


