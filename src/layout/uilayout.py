from dash import dcc
import dash_bootstrap_components as dbc
from layout import CytoGraph, UIControls
from config.ui_config import (
    _UILAYOUT_CONTAINER_CLASS_NAME,
    _UILAYOUT_ROW_CLASS_NAME,
    _UILAYOUT_MAIN_CONTENT_CLASS_NAME,
    _UILAYOUT_SIDEBAR_CLASS_NAME,
)

# NOTE NEEDS TO BE REPLACED
import utils

# Run the callbacks
import callbacks.callbacks


class UILayout:
    def __init__(
        self,
        uid: str,
        cytograph: CytoGraph = None,
        controls: UIControls = None,
        content_width: int = 9,
        controls_width: int = 3,
    ):

        self.uid = uid

        # Assign the UID the layout
        cytograph.pack(uid)
        # Compute the graph
        cytograph.compute()

        # Assign the UID the layout & add extra info
        controls.pack(uid, cytograph.options)

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
            className=_UILAYOUT_CONTAINER_CLASS_NAME,
            children=[
                dcc.Store(id={"type": "store", "uid": self.uid}, data=self.store),
                dcc.Store(
                    id={"type": "backup-store", "uid": self.uid}, data=self.store
                ),
                dbc.Row(
                    className=_UILAYOUT_ROW_CLASS_NAME,  # g-0 removes gutters, h-100 for full height
                    children=[
                        # Main content area
                        dbc.Col(
                            id={"type": "main-content", "uid": self.uid},
                            width=self.content_width,
                            className=_UILAYOUT_MAIN_CONTENT_CLASS_NAME,
                            children=self.CONTENT.unpack(),
                        ),
                        # Sidebar area
                        dbc.Col(
                            width=self.controls_width,
                            className=_UILAYOUT_SIDEBAR_CLASS_NAME,
                            children=self.CONTROLS.unpack(),
                        ),
                    ],
                ),
            ],
        )
