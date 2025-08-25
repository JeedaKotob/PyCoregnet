from functools import partial

import dash
from layout.baselayout import BaseNetworkGraph
from assets import stylesheet
from graph import adj

dash.register_page(__name__, path='/dashboard/coregs')

store = {
    "graph" : "coregulator", # Either fullnetwork, coregnetwork, targetnetwork
    "selected" : [], 
    "selection_mode" : "single",
    "filter_mode" : "both",
    "backtracking" : False,
    "threshold" : None,
    "metadata" :{
        "total_nodes" : 0,
        "total_edges" : 0,
        "selected_nodes" : 0,
        "selected_edges" : 0,
    },
}

graph_layout={
    'name': 'cose',
    'quality': 'default', # for fcose
    'fit': True,
    'padding': 40,
    'animate': False,
    'nodeRepulsion': 2500000,
    'edgeElasticity': 100,
    'gravity': 70,
    'numIter': 1000
}

app_layout = BaseNetworkGraph(
    store=store,
    preprocess=partial(adj.get_entity_partners,key="bytf"),
    create_network=adj.create_network, 
    stylesheet=stylesheet.coreg_network_stylesheet,
    graph_layout=graph_layout,
    dropdown_options=adj.options,
    threshold=partial(adj.default_threshold,threshold = 0.1)
)

layout = app_layout.get_layout()
app_layout.register_callbacks(dash.get_app())

