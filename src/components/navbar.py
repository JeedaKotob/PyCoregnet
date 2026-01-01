import dash
from dash import Dash, dcc, html
import dash_bootstrap_components as dbc

def get_navbar(page_registry):
    """page_registry = dash.page_registry.values()"""

    dropdowns = {}
    for page in page_registry:
        path = page["path"]
        pc = path.split("/")[1:]
        if len(pc) > 1:
            parent,child = pc
            if parent not in dropdowns:
                dropdowns[parent] = []
            dropdowns[parent].append(child)


    ddowns = [    
        dbc.DropdownMenu(
            label=parent.capitalize(),
            children=[
                dbc.DropdownMenuItem(
                    c,
                    href=f"/{parent}/{c}"
                ) for c in child
            ],
            nav=True,
            in_navbar=True,
            className="text-white"
        ) for parent, child in dropdowns.items()
    ]

    return dbc.Navbar(
        children=[
            html.A("N", href="#",className="text-white text-decoration-none m-2 d-none",id="navbar-title-sm",n_clicks=0),
            html.A("PyCoregnet", href="#", className="text-white text-decoration-none m-2",id="navbar-title",n_clicks=0),
            dbc.Nav(
                children=[dbc.NavLink("Home", href="/")] + ddowns,
                navbar=True,
                id="navbar-content",
                className="",
            ),
        ],
        color="dark",
        dark=True,
        className="px-0 w-10 position-absolute z-3 shadow rounded-pill m-2 px-3",
        id="navbar"
    )


"""
@app.callback(
    Output("navbar","children"),
    Input("navbar-title","n_clicks"),
    State("navbar","children"),
    
)
def navbar_collapse(n_clicks,children):
    for e in children:
        if 'props' in e and 'className' in e['props']:
            e['props']['className'] = e['props']['className'] + ' d-none'
    return children
    
    return no_update

@callback(
    Output("navbar-dropdowns", "className"),
    Input("navbar-button", "n_clicks"),
    State("navbar-dropdowns", "className"),
)
def toggle_navbar_dropdowns(n_clicks, current_class):
    if not n_clicks:
        return "ms-auto"
    
    # Toggle between showing and hiding with no animation
    if current_class and "d-none" in current_class:
        # Show the dropdowns
        return "ms-auto"
    else:
        # Hide the dropdowns
        return "ms-auto d-none"

@callback(
    Output("navbar-dropdowns", "style"),
    Input("navbar-button", "n_clicks"),
    State("navbar-dropdowns", "style"),
)
def toggle_navbar_dropdowns(n_clicks, current_style):
    if not n_clicks:
        return {}
    
    # Toggle display between 'none' and default
    if current_style is None:
        current_style = {}
    
    if current_style.get("display") == "none":
        # Show the dropdowns
        return {**current_style, "display": "flex"}
    else:
        # Hide the dropdowns
        return {**current_style, "display": "none"}
"""