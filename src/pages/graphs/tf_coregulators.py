import dash
import dash_cytoscape as cyto
import dash_bootstrap_components as dbc
from assets import stylesheet
from layout import UIControls, CytoGraph, UILayout

from graph import adj  # NOTE UPDATE
import callbacks.tf_coregulators

dash.register_page(__name__, path="/graphs/TFCoregulators")

layout = dbc.Spinner(size="lg", color="primary")

graph_layout = {
    "name": "cose",
    "quality": "default",  # for fcose
    "fit": True,
    "padding": 40,
    "animate": False,
    "nodeRepulsion": 2500000,
    "edgeElasticity": 100,
    "gravity": 70,
    "numIter": 1000,
}

uicontrols = UIControls(
    selection_mode="single",
    threshold_input=True,
    options_dropdown=True,
    inspector_tabs=[
        {"label": "Regulation", "tab_id": "table"},
        {"label": "TF Activity", "tab_id": "nn"},
        {"label": "GOE", "tab_id": "GO"},
    ],
    network_stats=True,
)

cytograph = CytoGraph(
    preprocess_function=adj.get_genes,
    preprocess_role="bytf",
    creation_function=adj.create_network,
    threshold_function=adj.default_threshold,
    threshold=None,
    threshold_ratio=0.1,
    stylesheet=stylesheet.coreg_network_stylesheet,
    layout_config=graph_layout,
    dropdown_options=adj.options,
)


uilayout = UILayout(uid="coregs", cytograph=cytograph, controls=uicontrols)

layout = uilayout.render()
