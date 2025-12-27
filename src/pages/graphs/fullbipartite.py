import dash
import dash_cytoscape as cyto
import dash_bootstrap_components as dbc
from graph import fullbipartite
from assets import stylesheet
from layout import UIControls, CytoGraph, UILayout

dash.register_page(__name__, path='/graphs/fullbipartite')

layout = dbc.Spinner(size="lg",color="primary")

uicontrols = UIControls(
    selection_mode="single",
    filter_mode="both",
    options_dropdown=True,
    inspector_tabs=['table','heatmap'],
    network_stats=True
)

cytograph = CytoGraph(
    creation_function=fullbipartite.create_network,
    stylesheet=stylesheet.full_network_stylesheet,
    layout_config=fullbipartite.layout,
    dropdown_options=fullbipartite.options
)

uilayout = UILayout(
    uid='full',
    cytograph=cytograph,
    controls=uicontrols
)

layout = uilayout.render()
