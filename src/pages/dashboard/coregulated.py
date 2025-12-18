from functools import partial

import dash
from layout.baselayout import BaseNetworkGraph
from assets import stylesheet
from graph import adj

dash.register_page(__name__, path='/dashboard/coregulated')



store = {
    "graph" : "targets", # Either fullnetwork, coregnetwork, targetnetwork
    "selected" : [], 
    "selection_mode" : "single",
    "filter_mode" : None,
    "backtracking" : None,
    "threshold" : 0,
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
    'nodeRepulsion': 1000000,
    'edgeElasticity': 100,
    'gravity': 50,
    'numIter': 1000
}

app_layout = BaseNetworkGraph(
    store=store,
    preprocess=partial(adj.get_entity_partners,key="bygene"),
    create_network=adj.create_network, 
    stylesheet=stylesheet.target_network_stylesheet,
    graph_layout=graph_layout,
    dropdown_options=adj.options,
    threshold=partial(adj.default_threshold,threshold = 0.5),
    content={
        "Regulation" : partial(adj.by_update_info_panel,columns=
                                                            [
                                                                {"name": "TG", "id": "Node"},
                                                                {"name": "TF", "id": "shared"},
                                                                {"name": "STFC", "id": "count"},
                                                            ]
        ),
        "GRN" : None,
    }
)

layout = app_layout.get_layout()
# app_layout.register_callbacks(dash.get_app())


{
    "Node" : "TG",
    "Shared" : "TF",
    "Count" : "STFC",
}
