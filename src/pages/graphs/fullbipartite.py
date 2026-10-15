import dash
import dash_bootstrap_components as dbc

import callbacks.fullbipartite  # noqa: F401  (registers callbacks)
from assets import stylesheet
from graph import fullbipartite
from layout import CytoGraph, UIControls, UILayout

dash.register_page(__name__, path="/graphs/FullBipartite")

layout = dbc.Spinner(size="lg", color="primary")

uicontrols = UIControls(
    selection_mode="single",
    filter_mode="both",
    options_dropdown=True,
    inspector_tabs=[
        {"label": "Regulation", "tab_id": "table"},
        {"label": "Heatmap", "tab_id": "heatmap"},
    ],
    network_stats=True,
)

cytograph = CytoGraph(
    creation_function=fullbipartite.create_network,
    stylesheet=stylesheet.full_network_stylesheet,
    layout_config=fullbipartite.layout,
    dropdown_options=fullbipartite.options,
)

uilayout = UILayout(uid="full", cytograph=cytograph, controls=uicontrols)

layout = uilayout.render()
