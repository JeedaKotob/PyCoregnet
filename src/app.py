import uuid
from flask import Flask
import dash
from dash import Dash, dcc, html, callback, Input, Output, no_update, State, callback_context
import dash_cytoscape as cyto
import dash_bootstrap_components as dbc
from flask_caching import Cache
cyto.load_extra_layouts()

from components.navbar import get_navbar

server = Flask(__name__)

# Local-friendly cache (persists between runs). For Redis, swap config.
config = {
    "DEBUG": True,          # some Flask specific configs
    "CACHE_TYPE": "SimpleCache",  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 3600
}
# tell Flask to use the above defined config
server.config.from_mapping(config)
cache = Cache(server)
server.config['SERVER_CACHE']=cache

app = dash.Dash(
    __name__,
    server=server,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    use_pages=True,
    url_base_pathname="/"
)

# Responsible to make a desktop-app like structure
APP_STYLE = {
    "height": "100vh",
    "display": "flex",
    "flexDirection": "column",
    "padding": "0",
    "backgroundColor": "#f8f9fa"
}

navbar = get_navbar(dash.page_registry.values())

#  Main layout
app.layout = dbc.Container(
    fluid=True,
    style=APP_STYLE,
    children=[
        navbar,
        dbc.Container(
            dash.page_container,
            fluid=True,
            className="dash-page-container"
        )
    ],
)


# @callback(
#     Output("navbar-content", "className"),
#     Input("navbar-title", "n_clicks"),
#     State("navbar-content", "className"),
#     prevent_initial_call=True    
# )
# def toggle_navbar_dropdowns(title ,current_class):
    
#     if title:
#         if current_class and "d-none" in current_class:
#             # Show the dropdowns
#             return "ms-auto"
#         else:
#             # Hide the dropdowns
#             return "ms-auto d-none"

    
#     return no_update



@callback(
    Output("navbar", "children"),
    Input("navbar-title", "n_clicks"),
    Input("navbar-title-sm", "n_clicks"),
    State("navbar", "children"),
    prevent_initial_call=True    
)
def toggle_navbar_dropdowns(title, title_sm, children):
    ctx = callback_context
    
    if not ctx.triggered:
        return no_update
    
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if triggered_id == 'navbar-title':
        children[0]['props']['className'] = children[0]['props']['className'].replace("d-none", "")
        for e in children[1:]:
            e['props']['className'] = e['props']['className'] + " d-none"
        return children
    elif triggered_id == 'navbar-title-sm':
        children[0]['props']['className'] = children[0]['props']['className'] + " d-none"
        for e in children[1:]:
            e['props']['className'] = e['props']['className'].replace("d-none", "")
        return children
    
    return no_update




if __name__ == '__main__':
    app.run(debug=True,port=8050)
