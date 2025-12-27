from functools import partial

import dash
import dash_cytoscape as cyto
import dash_bootstrap_components as dbc
from functools import partial
from typing import Literal

cyto.load_extra_layouts()

from updated.components.ui import btn_grp, thresh_input, dropdown, tabs, table, get_heat_map
import utils

dash.register_page(__name__, path='/dashboard/tcoregs')

from updated.graph import adj
from assets import stylesheet

from layout.common import *


layout = dbc.Spinner(size="lg",color="primary")


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

uicontrols = UIControls(
    selection_mode="single",
    threshold_input=True,
    options_dropdown=True,
    inspector_tabs = ['adj_table'],
    network_stats=True,
    
)


cytograph = CytoGraph(
    preprocess_function=adj.get_genes,
    preprocess_role="bytf",
    creation_function=adj.create_network,
    threshold_function=adj.default_threshold,
    threshold = None,
    threshold_ratio = 0.1,
    stylesheet=stylesheet.coreg_network_stylesheet,
    layout_config=graph_layout,
    dropdown_options=adj.options
)


uilayout = UILayout(
    uid='coregs',
    cytograph=cytograph,
    controls=uicontrols
)

layout = uilayout.render()
# uilayout.register_callbacks(dash.get_app())
