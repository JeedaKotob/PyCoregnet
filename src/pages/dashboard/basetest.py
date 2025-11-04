from functools import partial
import dash

from layout.base import NetworkControls
from graph import fullbipartite
from assets import stylesheet

dash.register_page(__name__, path='/dashboard/basetest')

def h():...
nc = NetworkControls(
    name = 'fb2',
    selection_mode='single',
    filter_mode='both',
    enable_stats_display = True,
    inspector_options = {
        "t1" : h,
        "t2" : h,
    }
    )

cl = nc.create_component_list()

print(cl)


layout = dash.html.Div(children=cl)




