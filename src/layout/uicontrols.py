from dash import html
import dash_bootstrap_components as dbc
from typing import Literal
from components.ui import (
    btn_grp,
    thresh_input,
    dropdown,
    tabs,
    network_stats,
)

#  Network control options
_NC_CONFIG = [
    {
        "card": "Network Stats",
        "id": "network_stats",
        "func": network_stats,
        "parms": {},
    },
    {
        "card": "Graph Controls",
        "id": "selection_mode",
        "func": btn_grp,
        "parms": {
            "label": "Selection",
            "value": None,  # "single",
            "options": [
                {"label": "Single", "value": "single"},
                {"label": "Off", "value": "off"},
                {"label": "Multiple", "value": "multiple"},
            ],
        },
    },
    {
        "card": "Graph Controls",
        "id": "filter_mode",
        "func": btn_grp,
        "parms": {
            "label": "Filter By",
            "value": None,  # "both",
            "options": [
                {"label": "Target", "value": "target"},
                {"label": "Both", "value": "both"},
                {"label": "TF", "value": "tf"},
            ],
        },
    },
    {
        "card": "Graph Controls",
        "id": "backtracking_mode",
        "func": btn_grp,
        "parms": {
            "label": "Backtracking",
            "value": None,  # False,
            "options": [
                {"label": "On", "value": "True"},
                {"label": "Off", "value": "False"},
            ],
        },
    },
    {
        "card": "Graph Controls",
        "id": "threshold_input",
        "func": thresh_input,
        "parms": {
            "label": "Threshold",
        },
    },
    {
        "card": "Node Inspector",
        "id": "options_dropdown",
        "func": dropdown,
        "parms": {
            "label": "Highlight Node",
        },
    },
    {
        "card": "Insights",
        "id": "inspector_tabs",
        "func": tabs,
        "parms": {
            "options": None,
        },
    },
]

_DEFAULT_CARD_CLASS = "d-flex flex-column"

_CARD_CLASS_NAME = {
    "Network Stats": _DEFAULT_CARD_CLASS,
    "Graph Controls": _DEFAULT_CARD_CLASS,
    "Node Inspector": _DEFAULT_CARD_CLASS,
    "Insights": f"{_DEFAULT_CARD_CLASS} p-0 ",
}

_CARD_STYLE = {"Insights": {"height": "400px"}}


def modify_card(self, card: str):
    cardID = card.lower().replace(" ", "-")

    if card == "Insights":
        return cardID, dbc.Row(
            [
                dbc.Col("Insights", width="auto"),
                dbc.Col(
                    dbc.Button(
                        "Switch View",
                        id={"type": "insights_switch_view_btn", "uid": self.uid},
                        size="sm",
                    ),
                    width="auto",
                ),
            ],
            justify="between",
            align="center",
        )

    return cardID, card


class UIControls:
    def __init__(
        self,
        *,
        selection_mode: Literal["single", "off", "multiple"] = None,
        filter_mode: Literal["target", "both", "tf"] = None,
        backtracking_mode: bool = False,
        threshold_input: bool = False,
        options_dropdown: bool = False,
        inspector_tabs: list = None,
        network_stats: bool = False,
    ):

        # Will be assigned in the UILayout class
        self.uid = None

        # Get Defined parms
        defined_parms = {k: v for k, v in locals().items() if k != "self" and v}
        self.defined_parms = defined_parms
        self._store = self.defined_parms

        # Get the controls configs of the defined parms
        self._CONTROLS_CONFIG = [nc for nc in _NC_CONFIG if nc["id"] in defined_parms]

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
            card = nc["card"]

            # Unique ID dictionary for the component.
            comp_id = {"type": nc["id"], "uid": self.uid}

            # Get the function and its parameters.
            func = nc["func"]

            # Copy the parms of network controls
            parms = nc["parms"].copy()

            if "value" in parms:  # To assign the defined parameter
                parms["value"] = self.defined_parms[nc["id"]]

            if "options" in parms:
                if parms["options"] is None:
                    parms["options"] = self.defined_parms[nc["id"]]

            # Create the component
            new_component = func(id=comp_id, **parms)

            # Check if the 'card' key already exists in the dictionary.
            if card in staged_components:
                # If it exists, append the new component to the existing list.
                staged_components[card].append(new_component)
            else:
                # If it does not exist, initialize it
                staged_components[card] = [new_component]

        # Create the components list, which will include everything for the NC
        components = []
        for card, values in staged_components.items():
            #  An exception for Insights as we need the entire table
            className = _CARD_CLASS_NAME.get(card)
            style = _CARD_STYLE.get(card, None)

            cardId, card = modify_card(self, card)

            components.append(
                dbc.Card(
                    className="mb-2",
                    id={"type": f"{cardId}-card-container", "uid": self.uid},
                    children=[
                        dbc.CardHeader(
                            card, id={"type": f"{cardId}-card-header", "uid": self.uid}
                        ),
                        dbc.CardBody(
                            values,
                            className=className,
                            id={"type": f"{cardId}-card-body", "uid": self.uid},
                            style=style,
                        ),
                    ],
                )
            )

        # Empty Space for the user
        components.append(html.Div(style={"height": "50vh"}))

        return components
