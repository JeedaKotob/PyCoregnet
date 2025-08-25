import dash
from layout.baselayout import BaseNetworkGraph
from graph import fullbipartite
from assets import stylesheet

dash.register_page(__name__, path='/dashboard/full')

store = {
    "graph" : "fullbipartite", # Either fullnetwork, coregnetwork, targetnetwork
    "selected" : [], 
    "selection_mode" : "single", # Either single, off, multiple, if None then not included in layout
    "filter_mode" : "both", # Either Target, Both, TF if None then not included in layout
    "backtracking" : False, # Either True, False if None then not included in layout
    "threshold" : 0, # Always 0 if None then not included in layout
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
)

layout = app_layout.get_layout()
app_layout.register_callbacks(dash.get_app())

