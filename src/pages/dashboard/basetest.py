from functools import partial
import dash

from layout.base import NetworkControls , NetworkLayout, CytoGraphHandler
from graph import fullbipartite
from assets import stylesheet

dash.register_page(__name__, path='/dashboard/basetest')

network_controls = NetworkControls(
    name = 'full',
    selection_mode='single',
    filter_mode='both',
    backtracking_mode = None,
    threshold_input = None,
    enable_stats_display = True,
    dropdown_options = fullbipartite.options,

    inspector_options = {
        "Regulation" : partial(fullbipartite.regulation,grn_path="./grn.json"),
        "Expression" : partial(fullbipartite.get_heat_map,filepath="./CIT_BLCA_EXP.csv"),
    }
)

cyto_graph_handler = CytoGraphHandler(
    network_preprocess_function = None,
    network_creation_function = fullbipartite.create_network,
    network_threshold = None,
    network_stylesheet = stylesheet.full_network_stylesheet,
    network_layout_config = fullbipartite.layout,
)



from pages.heatmap import hm

network_layout = NetworkLayout(
    network_controls=network_controls,
    cyto_graph_handler=cyto_graph_handler,
    heatmap=hm
)




layout = network_layout.render_layout()

network_layout._register()




