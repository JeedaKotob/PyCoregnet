from functools import partial

import dash
from layout.baselayout import BaseNetworkGraph
from graph import fullbipartite
from assets import stylesheet

import utils

dash.register_page(__name__, path='/dashboard/full')

store = {
    "graph" : "fullbipartite", # Either fullnetwork, coregnetwork, targetnetwork
    "selected" : [], 
    "selection_mode" : "single", # Either single, off, multiple, if None then not included in layout
    "filter_mode" : "both", # Either Target, Both, TF if None then not included in layout
    "backtracking" : False, # Either True, False if None then not included in layout
    "threshold" : None, # Always 0 if None then not included in layout
    "metadata" :{
        "total_nodes" : 0,
        "total_edges" : 0,
        "selected_nodes" : 0,
        "selected_edges" : 0,
    },
}



app_layout = BaseNetworkGraph(
    store = store,
    create_network=fullbipartite.create_network,
    stylesheet=stylesheet.full_network_stylesheet,
    graph_layout=fullbipartite.layout,
    dropdown_options=fullbipartite.options,
    content={
        "Regulation" : partial(fullbipartite.regulation,grn_path="./grn.json"),
        "Expression" : partial(fullbipartite.get_heat_map,filepath="./CIT_BLCA_EXP.csv"),
    }
)

layout = app_layout.get_layout()
app_layout.register_callbacks(dash.get_app())

