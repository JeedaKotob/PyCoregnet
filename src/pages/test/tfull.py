import dash
import dash_cytoscape as cyto
import dash_bootstrap_components as dbc
from functools import partial
from typing import Literal

cyto.load_extra_layouts()

from updated.components.ui import btn_grp, thresh_input, dropdown, tabs, table, get_heat_map
import utils

dash.register_page(__name__, path='/dashboard/tfull')

from graph import fullbipartite
from assets import stylesheet

from layout.common import *


layout = dbc.Spinner(size="lg",color="primary")

uicontrols = UIControls(
    selection_mode="single",
    filter_mode="both",
    options_dropdown=True,
    
    # backtracking_mode=True,
    # threshold_input=True,
    
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
# uilayout.register_callbacks(dash.get_app())
