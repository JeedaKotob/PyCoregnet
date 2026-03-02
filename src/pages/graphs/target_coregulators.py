import dash
import dash_cytoscape as cyto
import dash_bootstrap_components as dbc
from assets import stylesheet
from layout import UIControls, CytoGraph, UILayout

from graph import adj 

dash.register_page(__name__, path='/graphs/TargetCoregulators')

layout = dbc.Spinner(size="lg",color="primary")

graph_layout={
    'name': 'cose',
    'quality': 'default', # for fcose
    'fit': True,
    'padding': 40,
    'animate': False,
    'nodeRepulsion': 1000000,
    'edgeElasticity': 100,
    'gravity': 50,
    'numIter': 1000
}

uicontrols = UIControls(
    selection_mode="single",
    threshold_input=True,
    options_dropdown=True,
    inspector_tabs = ['adj_table'],
    network_stats=True,   
)

cytograph = CytoGraph(
    preprocess_function=adj.get_genes,
    preprocess_role="bygene",
    creation_function=adj.create_network,
    threshold_function=adj.default_threshold,
    threshold = None,
    threshold_ratio = 0.5,
    stylesheet=stylesheet.coreg_network_stylesheet,
    layout_config=graph_layout,
    dropdown_options=adj.options
)


uilayout = UILayout(
    uid='coregulated',
    cytograph=cytograph,
    controls=uicontrols
)

layout = dash.html.Div()# uilayout.render() 


